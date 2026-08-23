#!/usr/bin/env python3
"""Close the last gap in scripts/extract_math.py: the variant glyphs.

About a fifth of the equation glyphs in sources/di come back as U+FFFD. They
are Cambria Math's *variant* glyphs — the grown ∑ and ⋃ of a display operator,
the stretched brackets of a tall fraction, the small forms used in a subscript.
A variant is reachable only through the font's GSUB/MATH tables, never from
`cmap`, so reversing `cmap` cannot name it.

The saving grace is that the tail is short: across the corpus these are 175
distinct glyph ids, and the fifty commonest account for 91% of occurrences. So
rather than implement GSUB and MATH variant resolution, identify each glyph
once and keep the answer. This script renders every unmapped glyph to a small
PNG and, with `--identify`, asks a VLM to name it; the result is a checked-in
table that makes every later extraction deterministic and offline.

    python3 scripts/glyph_table.py --render            # PNGs + a contact sheet
    python3 scripts/glyph_table.py --identify          # VLM pass over the PNGs
    python3 scripts/glyph_table.py --identify --top 50 # just the head

The table lands in data/glyph_map.json as {glyph_id: "LaTeX or character"} and
is picked up automatically by extract_math.py. Entries are meant to be reviewed
by hand — it is a small file and a wrong entry is silent, so it is worth the
read. Anything still unidentified stays U+FFFD, which the drafting stage treats
as "look at the crop".
"""
import argparse
import collections
import glob
import json
import os
import sys

import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

RUN = os.path.join(ROOT, "run", "di")
DATA = os.path.join(ROOT, "data")
TABLE = os.path.join(DATA, "glyph_map.json")
GLYPHS = os.path.join(ROOT, "run", "glyphs")

PROMPT = """This image shows a single glyph cut from a Bulgarian university
mathematics document typeset in Cambria Math. Identify it.

Reply with ONLY a JSON object, no commentary and no markdown:
{"latex": "<the LaTeX command or character>", "confidence": "high|medium|low"}

Notes:
- Use the plain LaTeX form: "\\sum", "\\bigcup", "\\int", "\\sqrt", "(", "=".
- Large operators and their normal-size forms are the SAME command; a display
  \\sum and an inline \\sum both answer "\\sum".
- Stretched brackets answer as the plain bracket: "(", ")", "[", "|".
- A fraction bar answers "\\frac"; a horizontal overbar answers "\\overline".
- If the glyph is a fragment of a larger built-up symbol (the middle piece of a
  tall brace, say), answer {"latex": "", "confidence": "low"}.
"""


def census():
    """{glyph_id: occurrences} over every extracted page."""
    c = collections.Counter()
    for f in glob.glob(os.path.join(RUN, "*", "page_*.json")):
        for it in json.load(open(f))["items"]:
            if it["type"] != "math":
                continue
            for g in it["glyphs"]:
                if g["ch"] == "�":
                    c[g["cid"]] += 1
    if not c:
        raise SystemExit("no unmapped glyphs found — run scripts/extract_math.py first")
    return c


def locate(gid):
    """First page and box where `gid` occurs, so it can be re-rendered."""
    for f in sorted(glob.glob(os.path.join(RUN, "*", "page_*.json"))):
        d = json.load(open(f))
        for it in d["items"]:
            if it["type"] != "math":
                continue
            for g in it["glyphs"]:
                if g["cid"] == gid:
                    return d["source"], d["page"], g["bbox"]
    return None


def render(counter, dpi=600, pad=1.5):
    os.makedirs(GLYPHS, exist_ok=True)
    index = {}
    for gid, n in counter.most_common():
        hit = locate(gid)
        if not hit:
            continue
        src, pno, bbox = hit
        doc = pymupdf.open(os.path.join(ROOT, src))
        page = doc[pno - 1]
        r = pymupdf.Rect(bbox[0] - pad, bbox[1] - pad,
                         bbox[2] + pad, bbox[3] + pad) & page.rect
        if not r.is_empty:
            zoom = dpi / 72.0
            name = "gid_%05d.png" % gid
            page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=r).save(
                os.path.join(GLYPHS, name))
            index[gid] = {"png": name, "count": n, "source": src, "page": pno}
        doc.close()
    json.dump(index, open(os.path.join(GLYPHS, "index.json"), "w"), indent=1)
    print("rendered %d glyphs to %s" % (len(index), GLYPHS))
    return index


def identify(index, top, args):
    from backends import VLMClient
    from vlm_ocr import _extract_json
    client = VLMClient(mode=args.mode, model=args.model,
                       provider=args.provider, base_url=args.base_url)
    os.makedirs(DATA, exist_ok=True)
    table = json.load(open(TABLE)) if os.path.exists(TABLE) else {}
    ranked = sorted(index.items(), key=lambda kv: -kv[1]["count"])
    if top:
        ranked = ranked[:top]
    for gid, meta in ranked:
        if str(gid) in table and not args.force:
            continue
        path = os.path.join(GLYPHS, meta["png"])
        try:
            data = _extract_json(client.read_image(path, PROMPT))
        except Exception as e:
            print("gid %s failed: %s" % (gid, str(e)[:80]))
            continue
        latex = (data.get("latex") or "").strip()
        conf = data.get("confidence", "low")
        if latex and conf != "low":
            table[str(gid)] = latex
            print("gid %-6s x%-5d -> %-14s (%s)" % (gid, meta["count"], latex, conf))
        else:
            print("gid %-6s x%-5d -> unresolved (%s)" % (gid, meta["count"], conf))
        json.dump(table, open(TABLE, "w"), ensure_ascii=False, indent=1,
                  sort_keys=True)
    covered = sum(index[g]["count"] for g in index if str(g) in table)
    total = sum(m["count"] for m in index.values())
    print("\ntable covers %d/%d occurrences (%.1f%%)"
          % (covered, total, 100.0 * covered / max(total, 1)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--identify", action="store_true")
    ap.add_argument("--top", type=int, default=None,
                    help="only the N commonest glyphs")
    ap.add_argument("--dpi", type=int, default=600)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--mode", default="cloud")
    ap.add_argument("--model", default=None)
    ap.add_argument("--provider", default="agy")
    ap.add_argument("--base-url", default=None)
    args = ap.parse_args()

    idx_path = os.path.join(GLYPHS, "index.json")
    if args.render or not os.path.exists(idx_path):
        index = render(census(), args.dpi)
    else:
        index = {int(k): v for k, v in json.load(open(idx_path)).items()}

    if args.identify:
        identify(index, args.top, args)
    else:
        c = census()
        tot = sum(c.values())
        print("%d distinct unmapped glyphs, %d occurrences" % (len(c), tot))
        run = 0
        for i, (gid, n) in enumerate(c.most_common(20), 1):
            run += n
            print("  %2d. gid %-6d %5d   cumulative %5.1f%%"
                  % (i, gid, n, 100.0 * run / tot))


if __name__ == "__main__":
    main()
