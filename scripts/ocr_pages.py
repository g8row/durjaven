#!/usr/bin/env python3
"""OCR everything in the corpus that has no text layer.

Two kinds of input, handled uniformly:

  sources/temi/<N>та тема/*.jpg   157 phone photographs of loose A4 sheets
  sources/di/<name>.pdf           202 pages of scanned or photographed notebooks

They differ enormously in how hard they are to read, and a single preprocessing
recipe would either destroy the easy ones or fail on the hard ones. So each unit
is assigned a *tier* (see docs/CORPUS.md §2), and the tier picks both the
preprocessing and the prompt:

  photo-clean       sheet on white or pale ground — crop, flatten, stretch
  photo-desk        sheet on a dark desk, reverse side showing through —
                    the same, plus a harder background division
  scan-ruled        Logichesko: grayscale scan, thin strokes, ruled paper
  notebook-hostile  SA/ST: squared paper, perspective, facing page, a thumb
  code              oop2: C++ that must come back verbatim, not as prose
  typeset           4.pdf / 32.pdf: pristine rendering, flattened to images —
                    no cleanup wanted, only a different prompt

Tiers are assigned by name where that is known and otherwise detected from the
image (a dark border means a desk shot). `--list` shows the assignment without
doing any work.

Output mirrors the video pipeline's items-JSON so everything downstream reads
one schema:

  run/ocr/<unit>/page_NNN.json    {"items":[{"type":"text"|"equation"|"code",...}]}
  run/ocr/<unit>/prep/*.png       what the model was actually shown

Resumable: a page that already has output is skipped, so a dropped connection
or an interrupted run costs only the page in flight. `--force` re-reads.

Usage:
    python3 scripts/ocr_pages.py --list
    python3 scripts/ocr_pages.py --unit "1ва тема" --prep-only
    python3 scripts/ocr_pages.py --tier photo-clean --limit 2
    python3 scripts/ocr_pages.py                       # everything

Backends (src/backends.py — every stage can run local or cloud):
    --mode local --backend openai --base-url http://localhost:11434/v1 \
        --model gemma3:4b                              # Ollama, any vision model
    --mode local --backend mlx-vlm \
        --model mlx-community/Qwen2.5-VL-7B-Instruct-4bit
    --mode cloud --provider gemini                     # needs GEMINI_API_KEY
"""
import argparse
import json
import os
import re
import sys
import time
import unicodedata

import cv2
import numpy as np
import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

TEMI = os.path.join(ROOT, "sources", "temi")
DI = os.path.join(ROOT, "sources", "di")
OUT = os.path.join(ROOT, "run", "ocr")

# --------------------------------------------------------------------------- #
# Prompts
# --------------------------------------------------------------------------- #

_SCHEMA = """Върни САМО JSON обект със следната форма, без коментар и без markdown:
{
  "items": [
    {"type": "text", "content": "<българският текст както е написан>"},
    {"type": "equation", "content": "<математиката като валиден LaTeX, без $ разделители>"}
  ]
}"""

_RULES = """Правила:
- "equation" за всичко математическо (формули, изрази, отделни означения като \\Omega, A^c, \\bigcup_{i=1}^n A_i).
- "text" за проза и заглавия; запази българския, не превеждай.
- Спазвай реда отгоре-надолу.
- Ако нещо е нечетливо, постави [?] на негово място. НЕ измисляй съдържание.
Върни само JSON обекта."""

PROMPT_HAND = f"""Транскрибирай тази снимка на ръкописни студентски записки за държавен изпит по информатика. Текстът е на български, писан на ръка.

{_SCHEMA}

{_RULES}"""

PROMPT_CODE = f"""Транскрибирай тази снимка на ръкописни записки по обектно-ориентирано програмиране. Съдържа български текст и код на C++.

Върни САМО JSON обект със следната форма, без коментар и без markdown:
{{
  "items": [
    {{"type": "text", "content": "<българският текст>"}},
    {{"type": "code", "content": "<кодът ТОЧНО както е написан>"}}
  ]
}}

Правила:
- "code" за всеки ред код. Запази го БУКВАЛНО: имена, ->, ::, {{}}, ;, интервали.
  НЕ поправяй синтаксис, НЕ форматирай наново, НЕ превеждай идентификатори.
- "text" за прозата на български.
- Ако нещо е нечетливо, постави [?]. НЕ измисляй съдържание.
Върни само JSON обекта."""

PROMPT_TYPESET = f"""Транскрибирай тази страница от печатни записки на български за държавен изпит по информатика. Текстът е набран (не е ръкопис).

{_SCHEMA}

{_RULES}"""

# --------------------------------------------------------------------------- #
# Tiers
# --------------------------------------------------------------------------- #
# `flatten` is the sigma of the background blur that gets divided out; larger
# keeps more of the low-frequency detail. `clahe` is the local contrast limit.
# `dpi` only applies to PDF sources.

TIERS = {
    "photo-clean":      {"prompt": PROMPT_HAND,    "flatten": 25, "clahe": 2.0, "crop": True,  "degrid": 0,  "dpi": 220},
    "photo-desk":       {"prompt": PROMPT_HAND,    "flatten": 15, "clahe": 3.0, "crop": True,  "degrid": 0,  "dpi": 220},
    "scan-ruled":       {"prompt": PROMPT_HAND,    "flatten": 18, "clahe": 2.5, "crop": False, "degrid": 0,  "dpi": 200},
    "notebook-hostile": {"prompt": PROMPT_HAND,    "flatten": 35, "clahe": 1.8, "crop": True,  "degrid": 40, "dpi": 300},
    "code":             {"prompt": PROMPT_CODE,    "flatten": 20, "clahe": 2.5, "crop": True,  "degrid": 0,  "dpi": 260},
    "typeset":          {"prompt": PROMPT_TYPESET, "flatten": 0,  "clahe": 0,   "crop": False, "degrid": 0,  "dpi": 300},
}

# PDFs whose tier is known from what they are.
PDF_TIERS = {
    "Logichesko.pdf": "scan-ruled",
    "logichesko1.pdf": "scan-ruled",
    "logichesko2.pdf": "scan-ruled",
    "SA.pdf": "notebook-hostile",
    "ST.pdf": "notebook-hostile",
    "oop2/oop2.pdf": "code",
    "4.pdf": "typeset",
    "32.pdf": "typeset",
}


def detect_photo_tier(img):
    """photo-clean or photo-desk, from how dark the border is.

    A sheet shot on a desk leaves a dark frame around a bright page; one shot on
    a pale ground does not. Comparing the border's median to the centre's
    separates them cleanly and needs no per-folder labelling.
    """
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = g.shape
    b = max(2, min(h, w) // 20)
    border = np.concatenate([
        g[:b].ravel(), g[-b:].ravel(), g[:, :b].ravel(), g[:, -b:].ravel()])
    centre = g[h // 3:2 * h // 3, w // 3:2 * w // 3]
    return "photo-desk" if np.median(border) < 0.72 * np.median(centre) else "photo-clean"


# --------------------------------------------------------------------------- #
# Preprocessing
# --------------------------------------------------------------------------- #

def prep(img, tier):
    """Crop to the written page, kill the ruling and the tint, boost the ink."""
    cfg = TIERS[tier]
    if not cfg["flatten"]:
        return img                      # typeset: hand it over untouched

    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if cfg["crop"]:
        # --- locate the page: the paper is much brighter than the desk -------
        blur = cv2.GaussianBlur(g, (9, 9), 0)
        _, m = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
        cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if cnts:
            c = max(cnts, key=cv2.contourArea)
            # Guard against the crop swallowing the page: on a pale ground the
            # largest bright region can be the background itself.
            if cv2.contourArea(c) > 0.12 * g.size:
                x, y, w, h = cv2.boundingRect(c)
                pad = int(0.012 * max(w, h))
                x, y = x + pad, y + pad
                w, h = max(w - 2 * pad, 1), max(h - 2 * pad, 1)
                g = g[y:y + h, x:x + w]

    # --- flatten the paper: divide out a heavy blur of itself ----------------
    # Ruling, tint and the shadow of the reverse side are all low-frequency next
    # to pen strokes, so dividing by a large-kernel blur removes them and leaves
    # the ink. A smaller sigma is more aggressive, which is what the bad shots
    # need and what would eat the faint strokes on a clean one.
    s = cfg["flatten"]
    bg = cv2.GaussianBlur(g, (0, 0), sigmaX=s, sigmaY=s)
    flat = cv2.divide(g, bg, scale=255)

    # --- suppress the printed grid -------------------------------------------
    # Squared paper defeats the division above: the squares are the same spatial
    # frequency as the writing, so flattening amplifies them into black speckle
    # rather than removing them. They are, however, the only *long straight
    # runs* on the page — handwriting never produces a 40px unbroken horizontal
    # or vertical stroke — so a morphological opening isolates the grid alone,
    # and subtracting it leaves the ink standing.
    if cfg.get("degrid"):
        k = cfg["degrid"]
        inv = 255 - flat
        hor = cv2.morphologyEx(inv, cv2.MORPH_OPEN,
                               cv2.getStructuringElement(cv2.MORPH_RECT, (k, 1)))
        ver = cv2.morphologyEx(inv, cv2.MORPH_OPEN,
                               cv2.getStructuringElement(cv2.MORPH_RECT, (1, k)))
        grid = cv2.GaussianBlur(cv2.max(hor, ver), (3, 3), 0)
        flat = 255 - cv2.subtract(inv, grid)

    # --- stretch what is left ------------------------------------------------
    flat = cv2.createCLAHE(clipLimit=cfg["clahe"], tileGridSize=(8, 8)).apply(flat)
    lo, hi = np.percentile(flat, [2, 98])
    flat = np.clip((flat.astype(np.float32) - lo) * 255.0 / max(hi - lo, 1), 0, 255)
    return flat.astype(np.uint8)


def cap_size(img, max_px=1600):
    """Keep the long edge sane — a 4624px photo is downscaled by the model
    anyway, and sending it whole only slows the request down."""
    h, w = img.shape[:2]
    if max(h, w) <= max_px:
        return img
    s = max_px / max(h, w)
    return cv2.resize(img, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)


# --------------------------------------------------------------------------- #
# Units
# --------------------------------------------------------------------------- #

def repair_json(raw):
    """Parse model JSON that is merely truncated rather than malformed.

    A long page can end a brace short of complete — one observed result carried
    2,410 characters of correct transcription and failed to parse because the
    final `}` was missing. Throwing that away and calling the page empty is the
    worst outcome: the page still counts as read, and the loss is silent.

    So: find the outermost object, trim any half-written trailing item, and
    close whatever brackets are still open. Returns None if there is nothing
    recoverable, which is the honest answer for an empty response.
    """
    if not raw or not raw.strip():
        return None
    t = raw.strip()
    i = t.find("{")
    if i < 0:
        return None
    t = t[i:]
    try:
        return json.loads(t)
    except Exception:
        pass
    # Drop a trailing fragment, then close what is open.
    for cut in (t.rfind("},"), t.rfind("}"), len(t)):
        if cut <= 0:
            continue
        head = t[:cut + 1] if cut < len(t) else t
        for closing in ("", "]}", "}", "]", '"}]}', '"}]'):
            try:
                return json.loads(head + closing)
            except Exception:
                continue
    return None


def slug(name):
    """A filesystem- and git-friendly id for a Cyrillic folder name."""
    n = unicodedata.normalize("NFC", name)
    m = re.match(r"^(\d+)", n)
    return "temi_%02d" % int(m.group(1)) if m else re.sub(r"\W+", "_", n)


def photo_units():
    if not os.path.isdir(TEMI):
        return
    for d in sorted(os.listdir(TEMI), key=lambda x: (int(re.match(r"^(\d+)", x).group(1))
                                                     if re.match(r"^(\d+)", x) else 999)):
        p = os.path.join(TEMI, d)
        if not os.path.isdir(p):
            continue
        imgs = sorted(f for f in os.listdir(p) if f.lower().endswith((".jpg", ".jpeg")))
        if imgs:
            yield {"id": slug(d), "label": d, "kind": "photos",
                   "paths": [os.path.join(p, f) for f in imgs]}


def pdf_units():
    for rel, tier in PDF_TIERS.items():
        p = os.path.join(DI, rel)
        if os.path.exists(p):
            yield {"id": "di_" + re.sub(r"\W+", "_", os.path.splitext(rel)[0]),
                   "label": rel, "kind": "pdf", "path": p, "tier": tier}


def units():
    return list(photo_units()) + list(pdf_units())


def load_page(unit, i):
    """(image, tier) for page/photo `i` of `unit`."""
    if unit["kind"] == "photos":
        img = cv2.imread(unit["paths"][i])
        return img, unit.get("tier") or detect_photo_tier(img)
    tier = unit["tier"]
    d = pymupdf.open(unit["path"])
    pm = d[i].get_pixmap(dpi=TIERS[tier]["dpi"])
    a = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width, pm.n)
    d.close()
    return cv2.cvtColor(a[:, :, :3], cv2.COLOR_RGB2BGR), tier


def page_count(unit):
    if unit["kind"] == "photos":
        return len(unit["paths"])
    d = pymupdf.open(unit["path"])
    n = len(d)
    d.close()
    return n


# --------------------------------------------------------------------------- #

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--unit", help="one unit id or folder name, e.g. temi_01")
    ap.add_argument("--tier", help="only units/pages of this tier")
    ap.add_argument("--limit", type=int, help="at most N pages per unit (sampling)")
    ap.add_argument("--list", action="store_true", help="show the plan, do nothing")
    ap.add_argument("--prep-only", action="store_true", help="write prepped PNGs only")
    ap.add_argument("--max-px", type=int, default=1600)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--out-tag", default=None,
                    help="write under run/ocr/<unit>__<tag>/ so two models' runs "
                         "can sit side by side for comparison")
    ap.add_argument("--retries", type=int, default=4)
    ap.add_argument("--workers", type=int, default=1,
                    help="pages read concurrently; each call is an independent "
                         "subprocess or request, so this scales close to linearly")
    ap.add_argument("--timeout", type=int, default=300,
                    help="seconds per page before the call is abandoned; a local "
                         "model that stalls must not hold up 371 pages")
    ap.add_argument("--schema", default=os.path.join(ROOT, "data", "ocr_schema.json"),
                    help="JSON schema handed to providers that can enforce one "
                         "(codex --output-schema)")
    ap.add_argument("--mode", default="local")
    ap.add_argument("--backend", default=None,
                    help="local backend: mlx-vlm | openai")
    ap.add_argument("--model", default=None)
    ap.add_argument("--provider", default="gemini")
    ap.add_argument("--base-url", default=None)
    ap.add_argument("--api-key", default=None,
                    help="bearer token for an OpenAI-compatible endpoint; also "
                         "read from OCR_API_KEY")
    args = ap.parse_args()

    us = units()
    if args.unit:
        want = args.unit
        us = [u for u in us if u["id"] == want or u["label"] == want
              or slug(u["label"]) == want]
        if not us:
            raise SystemExit("no such unit: %s" % want)

    if args.list:
        print("%-14s %-26s %-6s %-18s %s" % ("id", "label", "pages", "tier", "kind"))
        print("-" * 80)
        tot = 0
        for u in us:
            n = page_count(u)
            tot += n
            if u["kind"] == "photos":
                img = cv2.imread(u["paths"][0])
                tier = detect_photo_tier(img)
            else:
                tier = u["tier"]
            print("%-14s %-26s %-6d %-18s %s" % (u["id"], u["label"], n, tier, u["kind"]))
        print("-" * 80)
        print("%d units, %d pages" % (len(us), tot))
        return

    client = None
    if not args.prep_only:
        from backends import VLMClient
        client = VLMClient(mode=args.mode, model=args.model, backend=args.backend,
                           provider=args.provider, base_url=args.base_url,
                           api_key=args.api_key or os.environ.get("OCR_API_KEY"),
                           timeout=args.timeout,
                           output_schema=args.schema if os.path.exists(args.schema) else None)
        print("backend:", client.describe())

    from vlm_ocr import _extract_json
    from concurrent.futures import ThreadPoolExecutor

    # (unit, page-index, tier, prep_path, dest) for everything still to do.
    jobs = []
    for u in us:
        n = page_count(u)
        pages = range(min(n, args.limit) if args.limit else n)
        outdir = os.path.join(OUT, u["id"] + ("__" + args.out_tag if args.out_tag else ""))
        os.makedirs(os.path.join(outdir, "prep"), exist_ok=True)
        for i in pages:
            img, tier = load_page(u, i)
            if args.tier and tier != args.tier:
                continue
            dest = os.path.join(outdir, "page_%03d.json" % (i + 1))
            prep_path = os.path.join(outdir, "prep", "page_%03d.png" % (i + 1))
            if os.path.exists(dest) and not args.force and not args.prep_only:
                print("skip %s p%d (done)" % (u["id"], i + 1))
                continue
            # Preprocessing is cheap and CPU-bound; do it up front so the
            # workers only ever wait on the model.
            cv2.imwrite(prep_path, cap_size(prep(img, tier), args.max_px))
            if args.prep_only:
                print("prepped %s" % prep_path)
                continue
            jobs.append((u, i, tier, prep_path, dest))

    if args.prep_only or not jobs:
        return

    failed = []
    done = [0]

    def run(job):
        u, i, tier, prep_path, dest = job
        for attempt in range(1, args.retries + 1):
            try:
                raw = client.read_image(prep_path, TIERS[tier]["prompt"])
                try:
                    data = _extract_json(raw)
                except Exception:
                    data = repair_json(raw)
                if not data or not data.get("items"):
                    # An empty result must NOT be written: the file would make
                    # the page look done and a resume would skip it forever.
                    raise RuntimeError(
                        "no items recovered (%d chars raw)" % len(raw or ""))
                data.update({"unit": u["id"], "label": u["label"],
                             "page": i + 1, "tier": tier})
                json.dump(data, open(dest, "w"), ensure_ascii=False, indent=1)
                done[0] += 1
                print("[%d/%d] %s p%d [%s] -> %d items"
                      % (done[0], len(jobs), u["id"], i + 1, tier,
                         len(data.get("items", []))))
                return
            except Exception as e:
                print("  %s p%d attempt %d/%d failed (%s)"
                      % (u["id"], i + 1, attempt, args.retries, str(e)[:90]))
                if attempt < args.retries:
                    time.sleep(min(60, 5 * 2 ** (attempt - 1)))
        failed.append("%s:%d" % (u["id"], i + 1))

    print("%d pages to read, %d workers" % (len(jobs), args.workers))
    if args.workers > 1:
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            list(ex.map(run, jobs))
    else:
        for j in jobs:
            run(j)

    if failed:
        print("FAILED (re-run to retry): %s" % ", ".join(failed))


if __name__ == "__main__":
    main()
