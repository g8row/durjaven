# Plan — turning the ДИ material into a book

Target: one compilable Bulgarian LaTeX book covering all 35 topics of the state
exam, built to the standard of `lec2tex`'s `probability-statistics-bg.pdf` —
numbered statement environments on a shared counter, a four-tier visual
hierarchy, cross-references that are checked mechanically, and a review pass
that treats fidelity to the sources as the thing being audited.

Read [CORPUS.md](CORPUS.md) first: it says what the sources are, how hard each
is to read, and where they contradict each other.

---

## 1. What carries over from `lec2tex`, and what does not

`lec2tex` had two layers: a video→draft pipeline, and the editorial machinery
that turned the draft into a book. **The pipeline does not apply here** — there
is no video, no audio, no whiteboard. The editorial machinery applies almost
entirely, because the hard problem is the same one: many imperfect sources that
disagree, and a book that must not quietly invent the difference away.

Copied and used as-is:

| File | Role |
|---|---|
| `src/backends.py` | per-stage local/cloud model switching; `agy` CLI, Gemini, MLX-VLM, Ollama, vLLM |
| `src/vlm_ocr.py` | the items-JSON schema and `_extract_json` |
| `src/verify_math.py` | SymPy + reasoning-LLM equation cross-check |
| `topics/preamble.tex` | the entire visual system — tiers, palette, theorem environments, TikZ styles |
| `docs/rubric_math.md`, `docs/rubric_fidelity.md` | the two-stage blind review protocol |
| `docs/REMEDIATION.md` | rules R1–R5: don't correct the source silently, don't strengthen a claim, footnote instead |

Copied and adapted:

| File | From | Change needed |
|---|---|---|
| `scripts/ocr_pages.py` | `ocr_pesho.py` | source is folders of JPEGs and scanned PDFs, not one PDF; per-tier preprocessing and prompts |
| `scripts/build_topics.py` | `build_lectures.py` | 35 chapters in 11 parts instead of 15 lectures; `listings` for the code chapters |
| `scripts/check_refs.py` | same | a rename — it imports `build_lectures` and expects `lectures/`; the two silent failures it catches are unchanged |

Deliberately not copied: `main.py`, `transcribe.py`, `board_detection.py`,
`board_tracking.py`, `temporal_alignment.py`, `ocr_pipeline.py`. All of them are
about getting text off a whiteboard in a video.

New, and specific to this corpus:

| File | Role | Status |
|---|---|---|
| `src/ttfcmap.py` | reverse a TrueType `cmap`; read a `.ttc` | **done** |
| `scripts/extract_math.py` | recover the deleted mathematics from the Word exports | **done, run over the corpus** |
| `scripts/glyph_table.py` | name the font variant glyphs once, keep the answer | **done, awaiting its model pass** |
| `scripts/map_topics.py` | build the content-derived topic↔source map | Phase 0 |
| `scripts/gen_appendices.py` | `AI.txt` / `FP.txt` / конспект sample problems → appendices | Phase 4 |
| `scripts/check_coverage.py` | each chapter against its official annotation | Phase 0 |

---

## 2. The finding that shapes everything

The 26 numbered PDFs carry 106 pages of well-organised notes whose prose
extracts perfectly and **whose mathematics extracts as blank space**. Word set
every equation in a subsetted Cambria Math whose `ToUnicode` CMap covers only
the Cyrillic runs; every math glyph therefore maps to U+0020. On screen the file
is perfect. A pipeline that trusted `get_text()` would produce a book with the
mathematics deleted and no error anywhere to show for it.

The subsets use `/Encoding /Identity-H` with `/CIDToGIDMap /Identity` and keep
the original glyph ids, so a CID in the content stream *is* a glyph id in the
full Cambria Math. Replacing the broken CMap with an identity one yields the raw
CIDs; one reversed `cmap` from the full font — present in any Office install —
decodes them. `scripts/extract_math.py` does this and has been run over the
whole corpus:

```
6,029 equation runs · 35,192 glyphs · 79.2% decoded to exact Unicode
6,443 math crops rendered at 400 dpi
```

The residue is font *variant* glyphs — reachable only through `GSUB`/`MATH`,
never from `cmap`. There are 175 distinct ones and **the fifty commonest cover
91% of occurrences**; rendered, they turn out to be overwhelmingly script-size
digits and letters (subscript indices) plus stretchy brackets. Naming them once
with `glyph_table.py --identify` and checking the result in should take
recovery past 97%, deterministically and offline, for good.

**Why this matters beyond convenience.** What comes back is the exact character
sequence, with per-glyph boxes, but not the two-dimensional structure — a
fraction, a subscript and a limit are all just glyphs at coordinates. So the
division of labour is:

- the **glyph stream** supplies the symbols, exactly, with no model involved;
- a **vision model** reads the crop for structure — where the fraction bar is,
  what the limits of the sum are;
- and the glyph stream then **validates** the model's LaTeX. Character multisets
  that disagree mean a hallucination, and it gets caught.

That is the whole reason this corpus is safe to automate. Vision models are
weak exactly where the glyph stream is strong (naming a symbol) and strong
exactly where it is weak (2-D layout). Nothing else in the plan gets to skip
this check.

---

## 3. Phases

### Phase 0 — Topic map *(largely done; verification remains)*

The official конспект settles this. `topics/manifest.json` now maps all 35
questions to their sources, with a confidence field per topic. The headline
findings (CORPUS.md §3): the sources predate the June 2025 revision, which
rotated the mathematics block, so **topics 28–35 are systematically offset in
both source sets**; and the PDFs are additionally stale on topics 6 and 8, where
the photographs are correct.

What remains is verification, not discovery:

1. **Topic 32** is the weakest link — `30.pdf` opens on Вайерщрас, which the
   annotation does not name. Read it before drafting.
2. **Topics 2, 31, 35** have sources that only partly satisfy their annotations
   (recurrence relations; alternating group / Cayley / homomorphism theorem;
   the three discrete distributions and generating functions). Confirm from the
   photographs, else declare the gap.
3. **Topics 11 and 12** have no source at all. Decide: source separately, or
   ship as declared gaps.
4. **Topics 15, 16** are marked `derived` — mapped by position rather than read.
   Spot-check.

An annotation-coverage pass belongs here too, and it is cheap: for each topic,
compare the terms the annotation names against the extracted text, and report
what is missing. That turns "does the book answer the question?" from a
judgement call into a checklist, and it is worth doing *before* drafting rather
than discovering it in review.

**TODO — check against the published exam material.**
<https://www.fmi.uni-sofia.bg/bg/node/7349> is the faculty's ДИ page. Confirm
that the конспект in `sources/konspekt/` is the current one, and pull whatever
past papers or sample solutions it links; those are the real test of whether a
chapter is sufficient, and they may also fill topics 11 and 12.

### Phase 1 — Deterministic extraction *(scripts only, no models)*

```bash
python3 scripts/extract_math.py                 # done — 26 PDFs
python3 scripts/glyph_table.py --render         # done — 175 glyph PNGs
python3 scripts/glyph_table.py --identify       # then review data/glyph_map.json
python3 scripts/extract_math.py                 # re-run, now ≥97%
```

Also here: decode the two `Задачи` PDFs (a one-line cp1251 fix — they are the
only professionally typeset sources and are worth trusting over the notes where
they overlap), and render every Tier B/C/D page to prepped PNGs.

Nothing in this phase costs a model call, and it produces the ground truth
everything later is checked against. It runs in minutes.

### Phase 2 — OCR *(bulk model calls, still no agents)*

Two independent jobs, both through `backends.py` so either can run local or
cloud:

**2a — page OCR** over the 157 photographs and 202 scanned pages, via
`ocr_pages.py`, resumable, with retry and backoff. Preprocessing and prompt are
selected per tier (CORPUS.md §2): the desk-background photographs get the
divide-out-the-background treatment inherited from `ocr_pesho.py`; `SA`/`ST` get
the most aggressive preprocessing and the strongest model; `oop2` gets a prompt
that emits verbatim code rather than LaTeX.

**2b — math structure** over the 6,443 crops. Each call gets the crop *and* its
exact glyph stream, and returns LaTeX. Every result is validated against the
glyph multiset; disagreements are queued, not silently accepted.

Both are embarrassingly parallel and neither belongs in an agent — see §4.

### Phase 3 — Drafting *(agents; §4 in detail)*

One agent per topic writes `topics/bodies/topic_NN.tex` against the extracted
prose, the validated LaTeX, the photograph OCR and the style rules.

### Phase 4 — Build *(scripts)*

```bash
python3 scripts/gen_appendices.py     # AI.txt + FP.txt → appendices А, Б
python3 scripts/build_topics.py       # drivers + the book
python3 scripts/check_refs.py         # after ANY substantial edit
```

`check_refs.py` earns its place here for the same reason it did in `lec2tex`: a
`\label` inside a `tcolorbox` can fail to reach the `.aux` depending on how the
box breaks across pages, so an unrelated edit in the same chapter can silently
knock out a cross-reference with no `??` and no build error.

### Phase 5 — Review *(agents; §4)*

The two-stage blind protocol from `lec2tex`: a mathematical review that never
sees the sources, a fidelity review that compares the chapter against them, and
an adjudicator that reconciles the two.

---

## 4. The subagent plan

### The governing rule

**Agents exercise judgement; scripts and bulk model calls do extraction.** No
agent ever iterates over formulas or pages one at a time. The numbers force
this:

| Artefact | Size | Consequence |
|---|---|---|
| `run/di/NN/page_*.json` | **1.4–5.6 MB per topic** | never enters an agent context |
| `run/di/NN/crops/` | up to **919 images** for one topic | ~500k tokens if viewed; a bulk pass instead |
| `run/di/NN/page_*.txt` | **8–27 KB per topic** | this is what an agent reads |

A single topic's crops, viewed naively by a drafting agent, would cost more
context than the entire rest of the book. Phase 2b exists to collapse those 919
images into ~20 KB of validated LaTeX before any agent starts.

### Wave 0 — Annotation coverage audit · 1 agent

The topic map is already built (`topics/manifest.json`); what this agent does
instead is compare each question's official annotation against the extracted
text of its sources, and report per topic what the annotation demands and the
sources do not appear to supply. Input is the 35 annotations (~25 KB) plus the
flat extracted text (~600 KB total — so it reads them a section at a time and
checkpoints, rather than holding all of it). **Opus 5**, run in three passes of
twelve topics. Output `docs/COVERAGE.md`, and it is what decides whether a
chapter is written from the sources or flagged short.

Blocking for the four `derived`/partial topics only; the rest can draft in
parallel with it.

### Wave 1 — OCR quality audit · 1 agent

After Phase 2a, samples ~20 pages across the tiers, compares OCR against the
image, and reports per-tier accuracy. The point is to find out *before* drafting
whether `SA`/`ST` came out usable, because if they did not, topics 26–27 need a
different source and that is a planning decision, not a drafting one.
**Opus 5**, ~60k tokens.

### Wave 2 — `Logichesko` distillation · 8 + 1 agents

158 pages of handwritten predicate logic and resolution — at ~4 KB of OCR per
page that is ~630 KB, well past what one agent should hold, and it backs only
two chapters. So:

- **8 chunk agents**, ~20 pages each (~80 KB, ~30k tokens). Each returns a
  structured inventory — definitions, theorems, proofs, worked examples, with
  page references — *not* prose. Target 3–4 KB out each. **Sonnet 5**;
  the task is summarisation against a fixed schema.
- **1 synthesis agent** reads the eight inventories (~30 KB total), maps them
  onto topics 21 and 22, and marks what is out of scope. **Opus 5**.

This is the only source that needs the chunk-and-synthesise treatment; every
other source fits a single agent.

### Wave 3 — Drafting · 35 agents, one per topic

Each agent receives, and nothing more:

```
run/di/NN/page_*.txt              8–27 KB   prose with math inline
run/math/NN.json                  ~20 KB    validated LaTeX per run
run/temi/NN/*.json                ~20 KB    photograph OCR (the second source)
docs/STYLE.md + preamble excerpt  ~10 KB    conventions
```

≈ 70 KB in, ≈ 25–30k tokens. Comfortable for any current model, which is the
point of Phase 2.

Model assignment follows the mathematical load, not the page count:

| Group | Questions | Agents | Model | Why |
|---|---|---|---|---|
| Mathematical | 1, 2, 3, 5, 7, 28–35 | 13 | **Opus 5** | numbered statements and proofs, two sources to reconcile |
| Logic | 21, 22 | 2 | **Opus 5** | third source (`Logichesko`), formal notation |
| Photograph-only | 6, 8, 17, 18 | 4 | **Opus 5** | one handwritten source, no PDF to cross-check — every claim rests on a single OCR pass |
| Prose + code | 14–16, 19, 20, 23–27 | 10 | **Sonnet 5** | definitions and enumerated properties; code must survive verbatim |
| Prose | 4, 9, 10, 13 | 4 | **Sonnet 5** | single source, no reconciliation |
| Absent | 11, 12 | — | — | not drafted until material is found |

Thirty-three chapters drafted, 19 on Opus and 14 on Sonnet.

Concurrency 4–6. Agents write only their own `topics/bodies/topic_NN.tex` —
no shared file is writable by two agents, so the wave needs no coordination.

### Wave 4 — Review · ~53 agents

Tiered, because a chapter of prose about the OSI model does not need the same
scrutiny as a chapter of proofs.

- **Mathematical chapters** (the 19 above — mathematical, logic and
  photograph-only): blind math review **and** fidelity review, fresh context each, per
  `docs/rubric_math.md` and `docs/rubric_fidelity.md`. The math reviewer does
  not see the sources; the fidelity reviewer does and checks the chapter against
  them. 38 agents, **Opus 5** for math, **Sonnet 5** for fidelity.
- **Prose chapters** (14): a single fidelity pass. **Sonnet 5**.
- **Adjudication**: 1 agent reconciles the two verdict streams into a
  remediation queue, per the `lec2tex` adjudication phase. **Opus 5**.
- Findings land as JSONL under `peer_review/runs/<date>/`; the book is **not**
  edited by reviewers. Remediation is a separate, later pass.

### Totals

| Wave | Agents | Model mix |
|---|---|---|
| 0 annotation coverage | 1 | Opus |
| 1 OCR audit | 1 | Opus |
| 2 `Logichesko` | 9 | 8 Sonnet + 1 Opus |
| 3 drafting | 33 | 19 Opus + 14 Sonnet |
| 4 review | 53 | 20 Opus + 33 Sonnet |
| **Total** | **97** | **42 Opus, 55 Sonnet** |

Wave 4 breaks down as 19 chapters reviewed twice (38), 14 reviewed once, and
one adjudicator.

At concurrency 5, Waves 3 and 4 are each a few hours of wall clock. Phases 1–2
are dominated by the 359 OCR calls and the 6,443 structure calls, which is an
overnight cloud run or a longer local one.

---

## 5. Guardrails

Carried from `docs/REMEDIATION.md`, and the reason the statistics book came out
trustworthy:

- **Don't correct the source silently.** These are a student's exam notes. Where
  they are wrong or non-standard, footnote it — never rewrite the claim.
- **Don't strengthen.** A hedge in the source stays a hedge in the book.
- **Don't invent.** Expansion must recover what the source said. Topics 11 and
  12 have no source; they ship as declared gaps unless material is found.
- **Two sources agreeing is the evidence worth having.** Most topics have both a
  PDF and photographs. Where they agree, confidence is high; where they diverge,
  the divergence is recorded in the chapter's audit file, not smoothed over.
- **Validate every model-produced formula** against the glyph stream. This is
  the one check that makes the Tier A mathematics safe, and it is free.
- **Run `check_refs.py` after any substantial edit**, not just after adding
  labels.

## 6. Known risks

| Risk | Handling |
|---|---|
| Sources predate the конспект | settled: `topics/manifest.json` maps by question, not filename; `6.pdf`/`8.pdf` retired to an appendix |
| Topic 32 mapping unconfirmed | read `30.pdf` against annotation 32 before drafting — flagged `derived` in the manifest |
| Topics 11, 12 have no source | ship as declared gaps, or source separately — check the faculty ДИ page first |
| A chapter covers the topic but not the *question* | the annotation-coverage audit (Wave 0) is the check; findings go in `docs/COVERAGE.md` |
| `SA`/`ST` may be too degraded to OCR | Wave 1 finds out early; fallback is `SA-SI.pdf` (12 clean pages) for topic 27 |
| Photo↔PDF pairing by filename | forbidden; `topics/manifest.json` is the only authority |
| Code chapters mangled into prose | separate prompt and `listings`, not math mode; verbatim fidelity checked in review |
| Variant glyphs left as U+FFFD | `data/glyph_map.json` is reviewed by hand; anything unresolved falls back to its crop |

---

## 7. What to do next

1. `glyph_table.py --identify`, then read `data/glyph_map.json` and re-run
   `extract_math.py`. Cheap, and it settles the last 21% of the mathematics.
2. Check <https://www.fmi.uni-sofia.bg/bg/node/7349> — confirm the конспект is
   current, and pull any past papers. They are the real test of sufficiency, and
   may cover topics 11 and 12.
3. Verify the four unconfirmed mappings (32 especially) and read `30.pdf`.
4. Phase 2a OCR on one folder from each photo tier, to calibrate preprocessing
   before committing to all 359 pages.
5. Wave 0 — the annotation-coverage audit, which tells you which chapters can
   actually be written from what is here.
