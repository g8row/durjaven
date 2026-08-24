#!/usr/bin/env python3
"""Check photograph-OCR formulas against the PDFs' exact glyph stream.

Reading a formula off a phone photograph is a guess, however good the model.
Measured against a paid reference, ox-alpha's mathematics scores 61-83%
similarity, and reading the diff shows the gap is not all notation: it returned
`E ⊆ {X ∈ V : |X| = 2}` where the source has `X ⊆ V`, which is a false
statement rather than a formatting choice. Nothing in the prose reveals it and
no error is raised.

For 24 of the 35 questions there is a second, *exact* account of the same
mathematics. `scripts/extract_math.py` recovers the true character sequence of
every equation in the Word-export PDFs with no model involved — that is what
the CID recovery buys. So an equation from the photographs can be checked
rather than trusted: reduce both sides to a bag of mathematical atoms and ask
whether the photograph's formula appears anywhere in the PDF's glyph stream.

Matching is deliberately loose about presentation and strict about content.
Whitespace, `\\left`/`\\right`, `\\,` and font commands are dropped; `\\subseteq`
and `⊆` are the same atom; but ∈ and ⊆ are different atoms, so the graph-theory
error above cannot match. A photograph equation with no counterpart is not
necessarily wrong — the notes and the PDF do differ in coverage — so the output
is a queue to look at, not a list of errors.

    python3 scripts/crosscheck_math.py                # every mapped question
    python3 scripts/crosscheck_math.py --topic 3      # one
    python3 scripts/crosscheck_math.py --topic 3 -v   # show the misses
"""
import argparse
import collections
import glob
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "topics", "manifest.json")
DI_RUN = os.path.join(ROOT, "run", "di")
OCR_RUN = os.path.join(ROOT, "run", "ocr")

# LaTeX spellings of the characters the glyph stream returns as Unicode. Only
# symbols that actually carry meaning: anything purely presentational is
# dropped instead (see DROP).
LATEX_TO_CHAR = {
    r"\subseteq": "⊆", r"\subset": "⊂", r"\supseteq": "⊇", r"\supset": "⊃",
    r"\in": "∈", r"\notin": "∉", r"\ni": "∋",
    r"\cup": "∪", r"\cap": "∩", r"\setminus": "\\", r"\emptyset": "∅",
    r"\varnothing": "∅", r"\triangle": "△", r"\oplus": "⊕",
    r"\forall": "∀", r"\exists": "∃", r"\neg": "¬", r"\lnot": "¬",
    r"\land": "∧", r"\wedge": "∧", r"\lor": "∨", r"\vee": "∨",
    r"\rightarrow": "→", r"\to": "→", r"\Rightarrow": "⇒",
    r"\leftrightarrow": "↔", r"\Leftrightarrow": "⇔", r"\iff": "⇔",
    r"\mapsto": "↦", r"\leftarrow": "←", r"\gets": "←",
    r"\le": "≤", r"\leq": "≤", r"\ge": "≥", r"\geq": "≥",
    r"\ne": "≠", r"\neq": "≠", r"\equiv": "≡", r"\approx": "≈",
    r"\times": "×", r"\cdot": "·", r"\div": "÷", r"\pm": "±",
    r"\sum": "∑", r"\prod": "∏", r"\int": "∫", r"\infty": "∞",
    r"\bigcup": "⋃", r"\bigcap": "⋂", r"\sqrt": "√", r"\partial": "∂",
    r"\alpha": "α", r"\beta": "β", r"\gamma": "γ", r"\delta": "δ",
    r"\epsilon": "ε", r"\varepsilon": "ε", r"\zeta": "ζ", r"\eta": "η",
    r"\theta": "θ", r"\lambda": "λ", r"\mu": "μ", r"\nu": "ν", r"\xi": "ξ",
    r"\pi": "π", r"\rho": "ρ", r"\sigma": "σ", r"\tau": "τ", r"\phi": "φ",
    r"\varphi": "φ", r"\chi": "χ", r"\psi": "ψ", r"\omega": "ω",
    r"\Gamma": "Γ", r"\Delta": "Δ", r"\Theta": "Θ", r"\Lambda": "Λ",
    r"\Pi": "Π", r"\Sigma": "Σ", r"\Phi": "Φ", r"\Omega": "Ω",
    r"\mid": "|", r"\vert": "|", r"\lVert": "|", r"\rVert": "|",
    r"\ldots": "…", r"\dots": "…", r"\cdots": "…",
    r"\langle": "⟨", r"\rangle": "⟩", r"\lfloor": "⌊", r"\rfloor": "⌋",
    r"\perp": "⊥", r"\circ": "∘", r"\prime": "'", r"\ast": "*",
}

# Presentation only — these change nothing about what the formula says.
DROP = re.compile(
    r"\\(?:left|right|big|Big|bigg|Bigg|displaystyle|text|mathrm|mathbf|mathcal"
    r"|mathbb|mathit|operatorname|limits|nolimits|quad|qquad|;|:|!|,|\s)")


def atoms(latex):
    """Reduce a formula to the bag of characters that carry its meaning.

    Both sides go through this, so it does not matter whether the source wrote
    \\varnothing or \\emptyset — what matters is that ∈ and ⊆ stay distinct.
    """
    if not latex:
        return collections.Counter()
    s = latex
    for k in sorted(LATEX_TO_CHAR, key=len, reverse=True):
        s = s.replace(k, LATEX_TO_CHAR[k])
    s = DROP.sub("", s)
    s = re.sub(r"\\[a-zA-Z]+", "", s)          # any command left over
    s = re.sub(r"[\s{}$\\]", "", s)            # grouping and whitespace
    # Sub/superscript markers carry structure, not content; the glyph stream
    # encodes that as position instead, so they cannot be compared here.
    s = s.replace("^", "").replace("_", "")
    # Word sets variables in Mathematical Italic — the glyph stream returns
    # U+1D449 for V, not "V" — while a model writes plain ASCII. NFKC folds the
    # Mathematical Alphanumeric Symbols block onto its Latin base letters so
    # the two accounts are comparable at all.
    s = unicodedata.normalize("NFKC", s)
    return collections.Counter(s)


def containment(small, big):
    """How much of `small` is present in `big`, 0..1."""
    if not small:
        return 1.0
    hit = sum(min(c, big.get(ch, 0)) for ch, c in small.items())
    return hit / sum(small.values())


def glyph_runs(pdf_stem, window=4):
    """The PDF's equations as atom bags — exact, no model.

    Word splits one formula across several spans: `⊆𝐸{𝑋⊆𝑉` and `𝑋| =2}` are two
    halves of the same edge-set definition, so a photograph's complete formula
    is contained in no single run. The fix is to also match against windows of
    consecutive runs — but only short ones.

    Pooling a whole page instead does not work, and fails in the worst
    direction: with every character on the page in one bag, both
    `{X ⊆ V : |X| = 2}` and the false `{X ∈ V : |X| = 2}` score 100%, because ∈
    occurs somewhere else on the page. A check that corroborates the error it
    was built to catch is worse than no check. Short windows keep locality, so
    the wrong symbol has to appear *next to* the rest of the formula to match.
    """
    out = []
    for f in sorted(glob.glob(os.path.join(DI_RUN, pdf_stem, "page_*.json"))):
        runs = [it["chars"] for it in json.load(open(f)).get("items", [])
                if it.get("type") == "math"]
        for i in range(len(runs)):
            for w in range(1, window + 1):
                if i + w > len(runs):
                    break
                joined = "".join(runs[i:i + w])
                out.append((joined, atoms(joined)))
    return out


def photo_equations(unit_tag):
    out = []
    for f in sorted(glob.glob(os.path.join(OCR_RUN, unit_tag, "page_*.json"))):
        d = json.load(open(f))
        for it in d.get("items", []):
            if it.get("type") == "equation":
                out.append((d.get("page"), it["content"], atoms(it["content"])))
    return out


def check(topic, meta, tag, threshold, verbose):
    pdf = meta.get("pdf")
    photos = meta.get("photos")
    if not pdf or not photos:
        return None
    stem = os.path.splitext(os.path.basename(pdf))[0]
    runs = glyph_runs(stem)
    m = re.match(r"^(\d+)", photos)
    unit = "temi_%02d__%s" % (int(m.group(1)), tag) if m else None
    if not runs or not unit:
        return None
    eqs = photo_equations(unit)
    if not eqs:
        return None

    matched, misses = 0, []
    for page, latex, bag in eqs:
        if not bag:
            continue
        best, best_src = 0.0, ""
        for src, rbag in runs:
            c = containment(bag, rbag)
            if c > best:
                best, best_src = c, src
            if best >= 0.999:
                break
        if best >= threshold:
            matched += 1
        else:
            misses.append((page, latex, best, best_src))
    total = matched + len(misses)
    if verbose and misses:
        # Worst first: that is the reading order that finds errors soonest.
        misses.sort(key=lambda m: m[2])
        print("    queue, least corroborated first:")
        for page, latex, sc, src in misses[:12]:
            print("      p%-3s %.0f%%  %s" % (page, 100 * sc, latex[:62]))
            print("             vs  %s" % src[:62])
    return {"topic": topic, "pdf": pdf, "unit": unit,
            "total": total, "matched": matched, "misses": len(misses)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic")
    ap.add_argument("--tag", default="oxalpha")
    ap.add_argument("--threshold", type=float, default=0.80,
                    help="containment above which a formula counts as "
                         "corroborated. One wrong symbol in a fourteen-symbol "
                         "formula moves the score by under ten points, so treat "
                         "the queue as a ranking and read from the bottom up "
                         "rather than as a verdict")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    man = json.load(open(MANIFEST))["topics"]
    rows = []
    for topic, meta in sorted(man.items(), key=lambda kv: int(kv[0])):
        if args.topic and topic != args.topic:
            continue
        if args.verbose:
            print("\n=== question %s: %s" % (topic, meta["title"][:60]))
        r = check(topic, meta, args.tag, args.threshold, args.verbose)
        if r:
            rows.append(r)

    if not rows:
        raise SystemExit("nothing to check yet — needs both extract_math.py "
                         "output and photograph OCR for the same question")
    print("\n%-6s %-12s %7s %9s %8s" % ("q", "pdf", "eqs", "corrob.", "queue"))
    print("-" * 48)
    tm = tt = 0
    for r in rows:
        tm += r["matched"]; tt += r["total"]
        print("%-6s %-12s %7d %8.0f%% %8d"
              % (r["topic"], r["pdf"], r["total"],
                 100.0 * r["matched"] / max(r["total"], 1), r["misses"]))
    print("-" * 48)
    print("%-6s %-12s %7d %8.0f%% %8d"
          % ("all", "", tt, 100.0 * tm / max(tt, 1), tt - tm))
    print("\nCorroborated means the formula's characters occur in the PDF's "
          "glyph stream,\nwhich is exact. The queue is for review, not a list "
          "of errors — the two\nsources genuinely differ in what they cover.")


if __name__ == "__main__":
    main()
