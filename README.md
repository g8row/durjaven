# ДИ — държавен изпит notes

Turning a pile of exam material — 365 PDF pages and 165 photographs, in three
different states of legibility — into one compilable Bulgarian LaTeX book
covering all 35 topics of the state exam.

Same treatment as `lec2tex`'s `probability-statistics-bg.pdf`: numbered
statement environments on one shared counter, a four-tier visual hierarchy so
the book can be skimmed rather than only read, mechanically checked
cross-references, and a blind two-stage review that audits fidelity to the
sources rather than prose quality. This repository is standalone — the tools it
needs from `lec2tex` are vendored here.

```
docs/PLAN.md      the plan: tools, phases, and the 97-agent breakdown
docs/CORPUS.md    what the sources are, how hard each is, where they conflict
topics/manifest.json  конспект question N -> its sources, with confidence
sources/konspekt/ the official syllabus — the spine of the book
sources/          the material as received
scripts/          extraction, OCR, build, checking
src/              model backends and the font machinery
topics/           the book's LaTeX — bodies/ is the source of truth
run/              extraction artefacts: the evidence
```

## The thing worth knowing

The 26 numbered PDFs are Word exports whose prose extracts perfectly and **whose
mathematics extracts as blank space** — Word subsets Cambria Math with a
`ToUnicode` CMap that covers only the Cyrillic, so every formula comes back as a
run of spaces while the file looks perfect on screen. A pipeline that trusted
`get_text()` would produce a book with the mathematics silently deleted.

`scripts/extract_math.py` gets it back without a model: the subsets are
`Identity-H` with `/CIDToGIDMap /Identity` and keep the original glyph ids, so a
CID in the content stream is a glyph id in the full Cambria Math, and one
reversed `cmap` decodes the lot.

```
6,029 equation runs · 35,192 glyphs · 79.2% decoded exactly · 6,443 crops
```

What that yields is the exact character sequence but not the two-dimensional
structure. So a vision model reads the crop for layout, and the glyph stream
then *validates* what it returned — a hallucinated symbol disagrees with the
glyphs and gets caught. That check is what makes this corpus safe to automate.

## Setup

```bash
python3.11 -m venv --system-site-packages .venv
.venv/bin/pip install pymupdf opencv-python-headless numpy requests sympy
brew install tectonic          # macOS; see tectonic docs on Linux
```

`extract_math.py` also needs Cambria Math, which ships inside any Microsoft
Office install; it looks there automatically, or drop `Cambria.ttc` in
`~/Library/Fonts`.

## Running

```bash
# recover the maths (deterministic, no model calls)
.venv/bin/python scripts/extract_math.py --report     # coverage over the corpus
.venv/bin/python scripts/extract_math.py              # extract + crop

# name the font variant glyphs once, then re-extract at ≥97%
.venv/bin/python scripts/glyph_table.py --render
.venv/bin/python scripts/glyph_table.py --identify

# OCR the handwriting (resumable; --prep-only to inspect preprocessing first)
.venv/bin/python scripts/ocr_pages.py --prep-only
.venv/bin/python scripts/ocr_pages.py

# build, then always check
.venv/bin/python scripts/build_topics.py
.venv/bin/python scripts/check_refs.py
```

Both commands publish the current collected book to
`darzhaven-izpit-kn.pdf` at the repository root. The root file is the single
canonical PDF deliverable; `topics/book.pdf` is only a transient compiler output.

Every model-using stage goes through `src/backends.py`, so each can run locally
(MLX-VLM, Ollama, vLLM) or in the cloud (`agy`, Gemini) independently of the
others — `--mode`, `--provider`, `--model`, `--base-url`.

## Status

Phase 1 extraction is done and has been run over the whole corpus. The topic
map is built: `topics/manifest.json` maps all 35 questions of the official
конспект to their sources.

Phase 2 page OCR is also complete: `run/ocr/*__production/` contains all 371
pages, preserving the completed Sol/ox-alpha evidence and filling the interrupted
run with GPT-5.6 Luna on easy pages and GPT-5.6 Terra on hard pages. The model
choice and benchmark results are recorded in `docs/PLAN.md`.

Phase 3 drafting is complete for every source-backed question: 33 chapter bodies
were produced with GPT-5.6 Luna and Terra. Questions 11 and 12 now contain compact
supplemental chapters based on the official detailed annotation and the comparison
document supplied later. Their source notes remain explicit because the original
listed literature is still absent from the corpus and requires future verification.

The thing to know before drafting anything: **neither source set follows the
current syllabus numbering.** Both predate the June 2025 revision, which rotated
the mathematics block, so questions 28–35 are systematically offset in the
filenames — and the PDFs are additionally stale on questions 6 and 8, where the
photographs are the correct source. Questions 11 and 12 still have no primary source
in the corpus; their supplemental chapters are therefore marked separately.
See [CORPUS.md](docs/CORPUS.md) §3–4.
