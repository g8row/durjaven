#!/usr/bin/env python3
"""Recover the mathematics that Word threw away in sources/di/NN.pdf.

The numbered topic PDFs are Word documents exported to PDF. Their prose
extracts perfectly, but every OMML equation is set in a subsetted Cambria Math
whose `ToUnicode` CMap maps only the Cyrillic runs — so `page.get_text()`
renders each formula as a run of spaces. Roughly a third of the mathematical
content of the corpus is invisible to ordinary extraction while looking
perfectly fine on screen, which is the worst possible failure mode.

It is recoverable without a model. The subsets use `/Encoding /Identity-H`
with `/CIDToGIDMap /Identity` and keep the original glyph ids, so a CID in the
content stream *is* a glyph id in the full Cambria Math. Replacing the broken
`ToUnicode` with an identity CMap makes PyMuPDF hand back the raw CIDs, and one
reversed `cmap` from the full font (shipped inside any Microsoft Office
install) decodes all of them.

What comes back is the exact character sequence with per-glyph bounding boxes —
symbols with no guessing — but *not* the two-dimensional structure: a fraction,
a subscript and a limit are all just glyphs at positions. So this script emits
both halves of the evidence a later stage needs:

  run/di/NN/page_XXX.json   reading-order items; each math run carries its exact
                            character sequence, its bbox and per-glyph boxes
  run/di/NN/crops/*.png     the same math runs cropped from a 400-dpi render
  run/di/NN/page_XXX.txt    prose + math inline, for a fast human read

A VLM reads the crop for *structure*; the character sequence then validates what
it returned. A model that hallucinates a symbol disagrees with the glyph stream
and gets caught — which is what makes this corpus safe to automate at all.

Usage:
    python3 scripts/extract_math.py --report          # coverage over all PDFs
    python3 scripts/extract_math.py --pdf 2           # one topic
    python3 scripts/extract_math.py                   # every text-bearing PDF
"""
import argparse
import glob
import json
import os
import re
import sys
import unicodedata

import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from ttfcmap import gid_to_unicode, ttc_offset, font_name  # noqa: E402

DI = os.path.join(ROOT, "sources", "di")
OUT = os.path.join(ROOT, "run", "di")

# Cambria Math ships with every Office install; any one of them will do.
FONT_SEARCH = [
    "/Applications/Microsoft Excel.app/Contents/Resources/DFonts/Cambria.ttc",
    "/Applications/Microsoft Word.app/Contents/Resources/DFonts/Cambria.ttc",
    "/Applications/Microsoft PowerPoint.app/Contents/Resources/DFonts/Cambria.ttc",
    "/Applications/Microsoft OneNote.app/Contents/Resources/DFonts/Cambria.ttc",
    "/Library/Fonts/Cambria.ttc",
    os.path.expanduser("~/Library/Fonts/Cambria.ttc"),
    "C:/Windows/Fonts/cambria.ttc",
]

IDENTITY_CMAP = b"""/CIDInit /ProcSet findresource begin
12 dict begin begincmap
/CIDSystemInfo << /Registry (Adobe) /Ordering (Identity) /Supplement 0 >> def
/CMapName /Identity-UCS def /CMapType 2 def
1 begincodespacerange <0000> <FFFF> endcodespacerange
1 beginbfrange <0000> <FFFF> <0000> endbfrange
endcmap CMapName currentdict /CMap defineresource pop end end"""


def load_variant_table():
    """{glyph_id: "LaTeX"} for the variant glyphs `cmap` cannot name.

    Built once by scripts/glyph_table.py; absent on a fresh checkout, in which
    case those glyphs stay U+FFFD and the drafting stage falls back to the crop.
    """
    p = os.path.join(ROOT, "data", "glyph_map.json")
    if not os.path.exists(p):
        return {}
    return {int(k): v for k, v in json.load(open(p)).items()}


def load_math_map():
    """{glyph_id: codepoint} for the full Cambria Math."""
    for path in FONT_SEARCH:
        if not os.path.exists(path):
            continue
        b = open(path, "rb").read()
        # A .ttc holds Cambria and Cambria Math; pick the one with a MATH table.
        for idx in (1, 0):
            try:
                off = ttc_offset(b, idx)
            except IndexError:
                continue
            if "Math" in font_name(b, off):
                m = gid_to_unicode(b, off)
                if m:
                    return m, "%s#%d" % (path, idx)
    raise SystemExit(
        "Cambria Math not found. Looked in:\n  " + "\n  ".join(FONT_SEARCH) +
        "\nInstall any Microsoft Office app, or drop Cambria.ttc in ~/Library/Fonts."
    )


def identity_pdf(src, tmp):
    """Copy `src` with every CambriaMath ToUnicode replaced by an identity CMap.

    Only the math font is touched: Cambria and Calibri carry working CMaps and
    must keep them, or the prose would come back as CIDs too.
    """
    d = pymupdf.open(src)
    patched = 0
    for xref in range(1, d.xref_length()):
        bf = d.xref_get_key(xref, "BaseFont")
        if bf[0] == "null" or "CambriaMath" not in str(bf[1]):
            continue
        if d.xref_get_key(xref, "Subtype")[1] != "/Type0":
            continue
        tu = d.xref_get_key(xref, "ToUnicode")
        if tu[0] != "xref":
            continue
        d.update_stream(int(tu[1].split()[0]), IDENTITY_CMAP, new=True)
        patched += 1
    d.save(tmp)
    d.close()
    return patched


# Everything outside these blocks that a maths run can contain is prose the
# equation editor happened to swallow (Word puts \text{} runs in the math font).
_MATH_RANGES = [
    (0x1D400, 0x1D7FF),  # Mathematical Alphanumeric Symbols
    (0x2100, 0x214F), (0x2190, 0x21FF), (0x2200, 0x22FF),
    (0x2A00, 0x2AFF), (0x27C0, 0x27EF), (0x2980, 0x29FF),
    (0x0370, 0x03FF),   # Greek
    (0xE000, 0xF8FF),   # private use — Cambria Math's stretchy variants
]


def is_mathy(ch):
    o = ord(ch)
    return any(a <= o <= b for a, b in _MATH_RANGES)


def _char_key(c):
    """A glyph's position on the page, stable across the patched/original pair."""
    return (round(c["bbox"][0], 1), round(c["bbox"][1], 1))


def _char_index(page):
    """{position: character} for the file as received.

    Keyed per *glyph*, not per span: patching the CMap changes how PyMuPDF
    groups characters into spans (a run of identical spaces coalesces where
    distinct CIDs do not), so span-level correspondence does not survive. Glyph
    boxes are untouched by the patch and line up exactly.
    """
    idx = {}
    for b in page.get_text("rawdict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                for c in s["chars"]:
                    idx[_char_key(c)] = c["c"]
    return idx


def decode_span(span, mathmap, variants, orig_chars):
    """Decode one Cambria Math span, keeping per-glyph geometry.

    A PDF here mixes two kinds of Cambria Math subset under one base name: the
    Type0/Identity-H ones carrying the equations, whose glyphs the patch turns
    into raw CIDs, and simple `/WinAnsiEncoding` ones Word uses for stray
    punctuation, which were never broken. Word also sets ordinary Cyrillic prose
    in the math font. The defect itself separates them: a glyph the original
    rendered as a space, and which is not the subset's own space, is an equation
    glyph and gets decoded; everything else is already correct as received.
    """
    chars, missing, decoded_any = [], 0, 0
    for c in span["chars"]:
        cid = ord(c["c"])
        was = orig_chars.get(_char_key(c))
        # A space is the ambiguous case, because it is also what PyMuPDF
        # substitutes for a CID the CMap does not cover. Two codes are genuine
        # spaces and must not be decoded: 3, the Type0 subsets' own space, and
        # 32, which is a literal space in the simple /WinAnsiEncoding subsets
        # (whose codes are bytes, not CIDs, and which the patch leaves alone).
        # No equation draws Cambria Math's glyph 32 \u2014 it is "\u00c2" \u2014 so treating
        # code 32 as a space costs nothing.
        if cid in (3, 32):
            ch = " "
        elif was is not None and was != " ":
            ch = was                # this glyph's own CMap works \u2014 trust it
        elif cid in mathmap:
            ch = chr(mathmap[cid])
            decoded_any += 1
        elif cid in variants:
            ch = variants[cid]      # named once, in data/glyph_map.json
            decoded_any += 1
        else:
            ch = "\uFFFD"           # a variant glyph not yet in the table
            missing += 1
            decoded_any += 1
        chars.append({"ch": ch, "cid": cid,
                      "bbox": [round(x, 2) for x in c["bbox"]]})
    return chars, missing, decoded_any


def page_items(page, mathmap, variants, orig_page):
    """Reading-order items for one page: prose runs and decoded math runs.

    `page` comes from the identity-patched copy and `orig_page` from the file as
    received; the two have identical structure because only a CMap changed.
    Both are needed because a PDF mixes two kinds of Cambria Math subset: the
    Type0/Identity-H ones that carry the equations and decode to spaces, and
    simple `/WinAnsiEncoding` ones that Word uses for stray punctuation and
    decode perfectly already. They are indistinguishable by font name — PyMuPDF
    strips the subset tag — so the defect itself is the discriminator: a span
    that came back blank from the original is a broken equation span and is
    read from the patched CIDs; anything else is taken as it was.
    """
    items = []
    stats = {"math_glyphs": 0, "unmapped": 0, "math_runs": 0}
    orig_chars = _char_index(orig_page)
    for block in page.get_text("rawdict")["blocks"]:
        for line in block.get("lines", []):
            buf_text, buf_math = [], []

            def flush_text():
                if buf_text:
                    s = "".join(buf_text)
                    if s.strip():
                        items.append({"type": "text", "content": s})
                    buf_text.clear()

            def flush_math():
                if not buf_math:
                    return
                seq = "".join(c["ch"] for c in buf_math)
                if not seq.strip():
                    buf_math.clear()
                    return
                xs = [c["bbox"] for c in buf_math]
                bbox = [min(b[0] for b in xs), min(b[1] for b in xs),
                        max(b[2] for b in xs), max(b[3] for b in xs)]
                stats["math_runs"] += 1
                items.append({
                    "type": "math",
                    "chars": seq,
                    "bbox": [round(v, 2) for v in bbox],
                    "glyphs": buf_math.copy(),
                })
                buf_math.clear()

            for span in line["spans"]:
                text = "".join(c["c"] for c in span["chars"])
                is_math_font = "CambriaMath" in span["font"].replace(" ", "")
                if not is_math_font:
                    flush_math()
                    buf_text.append(text)
                    continue
                decoded, missing, n_dec = decode_span(span, mathmap, variants, orig_chars)
                stats["unmapped"] += missing
                stats["math_glyphs"] += n_dec
                # Word routes ordinary Cyrillic prose through the math font
                # too; split it back out so the crops stay tight.
                for c in decoded:
                    if is_mathy(c["ch"]) or c["ch"] == "\uFFFD":
                        flush_text()
                        buf_math.append(c)
                    elif buf_math and c["ch"] in " ,.;:()[]{}=+-/|<>!*0123456789'":
                        buf_math.append(c)   # glue inside a formula
                    else:
                        flush_math()
                        buf_text.append(c["ch"])
            flush_math()
            flush_text()
    return items, stats


def merge_runs(items, gap=6.0):
    """Join math runs split across spans but visually contiguous."""
    out = []
    for it in items:
        if (it["type"] == "math" and out and out[-1]["type"] == "math"
                and abs(it["bbox"][1] - out[-1]["bbox"][1]) < 4
                and it["bbox"][0] - out[-1]["bbox"][2] < gap):
            p = out[-1]
            p["chars"] += it["chars"]
            p["glyphs"] += it["glyphs"]
            p["bbox"] = [min(p["bbox"][0], it["bbox"][0]),
                         min(p["bbox"][1], it["bbox"][1]),
                         max(p["bbox"][2], it["bbox"][2]),
                         max(p["bbox"][3], it["bbox"][3])]
        else:
            out.append(it)
    return out


def crop_math(page, items, outdir, pageno, dpi=400, pad=3.0):
    """Write one PNG per math run — the structural evidence a VLM reads."""
    os.makedirs(outdir, exist_ok=True)
    zoom = dpi / 72.0
    n = 0
    for i, it in enumerate(items):
        if it["type"] != "math":
            continue
        x0, y0, x1, y1 = it["bbox"]
        # A tall construction (fraction, sum with limits) overflows the span
        # box; pad generously in y so the crop keeps its numerator and limits.
        r = pymupdf.Rect(x0 - pad, y0 - pad * 2.5, x1 + pad, y1 + pad * 2.5)
        r = r & page.rect
        if r.is_empty:
            continue
        name = "p%03d_m%03d.png" % (pageno, i)
        page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=r).save(
            os.path.join(outdir, name))
        it["crop"] = name
        n += 1
    return n


def flat_text(items):
    parts = []
    for it in items:
        if it["type"] == "text":
            parts.append(it["content"])
        else:
            parts.append("  ⟦" + it["chars"] + "⟧  ")
    return re.sub(r"[ \t]{3,}", "  ", "".join(parts))


def process(pdf_path, mathmap, variants, do_crops=True, dpi=400):
    stem = os.path.splitext(os.path.basename(pdf_path))[0]
    outdir = os.path.join(OUT, stem)
    os.makedirs(outdir, exist_ok=True)
    tmp = os.path.join(outdir, "_identity.pdf")
    patched = identity_pdf(pdf_path, tmp)
    doc = pymupdf.open(tmp)
    orig = pymupdf.open(pdf_path)
    total = {"math_glyphs": 0, "unmapped": 0, "math_runs": 0}
    for pno in range(len(doc)):
        page = doc[pno]
        items, st = page_items(page, mathmap, variants, orig[pno])
        items = merge_runs(items)
        for k in total:
            total[k] += st[k]
        if do_crops:
            crop_math(page, items, os.path.join(outdir, "crops"), pno + 1, dpi)
        # `glyphs` is bulky; keep it, it is the validation evidence.
        json.dump({"source": os.path.relpath(pdf_path, ROOT),
                   "page": pno + 1, "items": items},
                  open(os.path.join(outdir, "page_%03d.json" % (pno + 1)), "w"),
                  ensure_ascii=False, indent=1)
        open(os.path.join(outdir, "page_%03d.txt" % (pno + 1)), "w").write(
            flat_text(items))
    doc.close()
    orig.close()
    os.remove(tmp)
    return stem, len(pymupdf.open(pdf_path)), patched, total


def report(mathmap, variants, src):
    print("Cambria Math map: %d glyphs  (%s)\n" % (len(mathmap), src))
    print("%-14s %5s %6s %8s %8s %7s" %
          ("pdf", "pages", "fonts", "runs", "glyphs", "unmapped"))
    print("-" * 56)
    grand = {"math_glyphs": 0, "unmapped": 0, "math_runs": 0}
    for p in sorted(glob.glob(os.path.join(DI, "*.pdf")), key=_key):
        d = pymupdf.open(p)
        has_text = any(len(pg.get_text().strip()) > 200 for pg in d)
        d.close()
        if not has_text:
            continue
        stem, pages, patched, tot = process(p, mathmap, variants, do_crops=False)
        for k in grand:
            grand[k] += tot[k]
        pct = 100.0 * tot["unmapped"] / max(tot["math_glyphs"], 1)
        print("%-14s %5d %6d %8d %8d %6.2f%%" %
              (stem, pages, patched, tot["math_runs"], tot["math_glyphs"], pct))
    print("-" * 56)
    pct = 100.0 * grand["unmapped"] / max(grand["math_glyphs"], 1)
    print("%-14s %5s %6s %8d %8d %6.2f%%" %
          ("TOTAL", "", "", grand["math_runs"], grand["math_glyphs"], pct))


def _key(p):
    m = re.match(r"^(\d+)$", os.path.splitext(os.path.basename(p))[0])
    return (0, int(m.group(1))) if m else (1, p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", help="topic number or filename, e.g. 2 or SA-SI.pdf")
    ap.add_argument("--report", action="store_true",
                    help="glyph-recovery coverage over the corpus, no crops")
    ap.add_argument("--dpi", type=int, default=400)
    ap.add_argument("--no-crops", action="store_true")
    args = ap.parse_args()

    mathmap, src = load_math_map()
    variants = load_variant_table()
    if args.report:
        report(mathmap, variants, src)
        return

    if args.pdf:
        name = args.pdf if args.pdf.endswith(".pdf") else args.pdf + ".pdf"
        targets = [os.path.join(DI, name)]
    else:
        targets = sorted(glob.glob(os.path.join(DI, "*.pdf")), key=_key)

    for p in targets:
        d = pymupdf.open(p)
        if not any(len(pg.get_text().strip()) > 200 for pg in d):
            print("skip %s — no text layer (scanned; use scripts/ocr_pages.py)"
                  % os.path.basename(p))
            d.close()
            continue
        d.close()
        stem, pages, patched, tot = process(
            p, mathmap, variants, do_crops=not args.no_crops, dpi=args.dpi)
        print("%-12s %2d pp  %3d math fonts  %4d runs  %5d glyphs  %d unmapped"
              % (stem, pages, patched, tot["math_runs"],
                 tot["math_glyphs"], tot["unmapped"]))


if __name__ == "__main__":
    main()
