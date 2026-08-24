#!/usr/bin/env python3
"""Rank OCR backends on the same pages, so the choice is evidence and not vibes.

Reading Bulgarian handwritten mathematics is the hardest thing this corpus
asks of a model, and the failure that matters is not a garbled word — it is a
model that invents a formula and returns it with the same confidence as a
correct one. Eyeballing one page per model does not catch that. So: run every
candidate over the same prepped pages, score each against a reference
transcription, and print a table.

Two numbers per model, because they fail differently:

  text    character-level similarity of the prose, which catches a model that
          is merely inaccurate
  math    similarity of the equations alone, which catches the dangerous case —
          gemma3:4b scored well on prose here and still invented every formula

`--ref` names the model whose output is treated as ground truth (the default is
whatever `codex` produced). Pages are read from run/ocr/<unit>__<tag>/, so a
model already benchmarked is not paid for twice unless `--force` says so.

    python3 scripts/ocr_bench.py --list-specs
    python3 scripts/ocr_bench.py --unit temi_01 --pages 2 \
        --spec zen:gemini-3.5-flash-lite --spec ollama:gemma3:4b
    python3 scripts/ocr_bench.py --unit temi_01 --report      # score what exists
"""
import argparse
import difflib
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "run", "ocr")
sys.path.insert(0, os.path.join(ROOT, "src"))

# A spec is "<provider>:<model>"; these are the ones worth trying on this corpus.
KNOWN = [
    "codex:gpt-5.6-luna", "codex:gpt-5.6-terra", "codex:",
    "opencode:x-preview-f-free", "opencode:big-pickle",
    "zen:gemini-3.5-flash-lite", "zen:gemini-3-flash", "zen:gemini-3.7-flash",
    "zen:nemotron-3.5-lightning-free", "zen:nemotron-3-ultra-free",
    "zen:hy3-free", "zen:mimo-v2.5-free", "zen:laguna-s-2.1-free",
    "zen:deepseek-v4-flash-free", "zen:x-preview-f-free",
    "zen:qwen3.6-plus", "zen:glm-5.2",
    "ollama:gemma3:4b", "ollama:qwen2.5vl:7b",
    "nvidia:nvidia/nemotron-nano-12b-v2-vl",
    "mlx:mlx-community/Qwen3-VL-8B-Instruct-3bit",
    "mlx:mlx-community/Qwen3.5-9B-8bit",
]


def tag_of(spec):
    prov, _, model = spec.partition(":")
    return (prov + "_" + model.replace("/", "_").replace(":", "_").replace(".", "")) \
        .strip("_").lower()


def run_spec(spec, unit, pages, timeout, force, deadline=None):
    """Invoke ocr_pages.py for one spec. Returns its output tag."""
    prov, _, model = spec.partition(":")
    tag = tag_of(spec)
    # -u: without it the child's progress is buffered and a long bench looks
    # indistinguishable from a hung one.
    cmd = [os.path.join(ROOT, ".venv", "bin", "python"), "-u",
           os.path.join(ROOT, "scripts", "ocr_pages.py"),
           "--unit", unit, "--out-tag", tag, "--timeout", str(timeout),
           # Fail fast: a model that cannot take an image 400s on every page,
           # and four retries with backoff turns a 5-second answer into two
           # minutes of waiting for a result already known.
           "--retries", "1"]
    if pages:
        cmd += ["--limit", str(pages)]
    if force:
        cmd += ["--force"]

    if prov == "codex":
        cmd += ["--mode", "cloud", "--provider", "codex"]
        if model:
            cmd += ["--model", model]
    elif prov == "opencode":
        cmd += ["--mode", "cloud", "--provider", "opencode", "--model", model]
    elif prov == "zen":
        cmd += ["--mode", "cloud", "--provider", "zen", "--model", model]
    elif prov == "ollama":
        cmd += ["--mode", "local", "--backend", "openai", "--model", model,
                "--base-url", "http://localhost:11434/v1"]
    elif prov == "mlx":
        cmd += ["--mode", "local", "--backend", "mlx-vlm", "--model", model]
    elif prov == "nvidia":
        key = json.load(open(os.path.expanduser(
            "~/.local/share/opencode/auth.json")))["nvidia"]["key"]
        cmd += ["--mode", "local", "--backend", "openai", "--model", model,
                "--base-url", "https://integrate.api.nvidia.com/v1",
                "--api-key", key]
    else:
        raise SystemExit("unknown provider in spec: " + spec)

    print("\n=== %s ===" % spec, flush=True)
    # Hard ceiling per spec, so one stalled backend cannot hold up the bench.
    cap = timeout * (pages or 1) + 60
    if deadline is not None:
        cap = min(cap, max(15, int(deadline - time.time())))
    try:
        r = subprocess.run(cmd, stdin=subprocess.DEVNULL, timeout=cap)
        return tag, r.returncode
    except subprocess.TimeoutExpired:
        print("  %s ABANDONED after %ds" % (spec, cap))
        return tag, -1


def load(unit, tag, page):
    p = os.path.join(OUT, unit + ("__" + tag if tag else ""), "page_%03d.json" % page)
    if not os.path.exists(p):
        return None
    return json.load(open(p))


def parts(doc):
    """(prose, maths) as two normalised strings."""
    if not doc:
        return "", ""
    t, m = [], []
    for it in doc.get("items", []):
        (m if it.get("type") == "equation" else t).append(it.get("content", ""))
    norm = lambda xs: " ".join(" ".join(xs).split()).lower()
    return norm(t), norm(m)


def sim(a, b):
    """Similarity of two transcriptions, 0..1.

    autojunk MUST be off. SequenceMatcher's heuristic treats any element
    appearing in more than 1% of a sequence longer than 200 as junk and skips
    it — on a page of prose that is every space and every common letter, and
    two nearly identical transcriptions score 0.15 instead of 0.97. It made a
    perfectly good model look like the worst in the table.
    """
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


def report(unit, ref_tag, pages):
    tags = sorted({d.split("__", 1)[1] for d in os.listdir(OUT)
                   if d.startswith(unit + "__")})
    rows = []
    for tag in tags:
        ts, ms, n = [], [], 0
        for pg in range(1, pages + 1):
            ref, got = load(unit, ref_tag, pg), load(unit, tag, pg)
            if not ref or not got:
                continue
            rt, rm = parts(ref)
            gt, gm = parts(got)
            ts.append(sim(rt, gt))
            ms.append(sim(rm, gm))
            n += 1
        if n:
            rows.append((tag, sum(ts) / n, sum(ms) / n, n))
    rows.sort(key=lambda r: -(r[1] + 2 * r[2]))     # maths is what matters
    print("\n%-34s %7s %7s %6s" % ("spec", "text", "math", "pages"))
    print("-" * 58)
    for tag, t, m, n in rows:
        flag = "  <- reference" if tag == ref_tag else ""
        print("%-34s %6.1f%% %6.1f%% %6d%s" % (tag, 100 * t, 100 * m, n, flag))
    print("-" * 58)
    print("reference: %s   (math weighted double — an invented formula is the "
          "failure that matters)" % ref_tag)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--unit", default="temi_01")
    ap.add_argument("--pages", type=int, default=1)
    ap.add_argument("--spec", action="append", default=[])
    ap.add_argument("--all-known", action="store_true")
    ap.add_argument("--ref", default="codex")
    # A model that cannot transcribe one page in two minutes is not a
    # candidate for 371 of them, so the bench does not wait around to find out.
    ap.add_argument("--timeout", type=int, default=120,
                    help="seconds per page for one spec")
    ap.add_argument("--budget", type=int, default=900,
                    help="hard ceiling in seconds for the WHOLE bench; without "
                         "it, N specs times a generous per-page timeout quietly "
                         "becomes hours")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--report", action="store_true", help="score what already exists")
    ap.add_argument("--list-specs", action="store_true")
    args = ap.parse_args()

    if args.list_specs:
        for s in KNOWN:
            print("  %-40s -> run/ocr/<unit>__%s" % (s, tag_of(s)))
        return

    if not args.report:
        deadline = time.time() + args.budget
        for spec in (KNOWN if args.all_known else args.spec):
            if time.time() >= deadline:
                print("\n[budget of %ds spent — skipping the rest]" % args.budget)
                break
            try:
                run_spec(spec, args.unit, args.pages, args.timeout, args.force,
                         deadline)
            except Exception as e:
                print("  %s FAILED: %s" % (spec, str(e)[:160]))

    report(args.unit, args.ref, args.pages)


if __name__ == "__main__":
    main()
