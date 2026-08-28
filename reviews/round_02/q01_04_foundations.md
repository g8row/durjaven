# Round 2 — independent focused review: questions 1–4

Scope: `topics/bodies/topic_01.tex` through `topic_04.tex`, checked against
`topics/manifest.json`, the mapped DI material, and the production OCR. This
is an independent review; no Round 1 findings were used. Severity reflects
exam-facing correctness and fidelity. No chapter was edited.

## Q1 — Множества. Декартово произведение. Релации. Функции.

**Verdict: PASS (no P0–P2 finding).** The chapter covers the manifest topic
and its mapped `1.pdf` / `1ва тема` material: construction axioms, induction,
set operations, products, relations and functions. The formulas and the
finite-poset statements checked in this pass are mathematically sound.

## Q2 — Основни комбинаторни принципи и конфигурации. Рекурентни уравнения.

**Verdict: NEEDS CORRECTION.**

### P1 — The non-homogeneous recurrence section omits the solution rule

- **Chapter:** `topics/bodies/topic_02.tex:394-415`.
- **Evidence:** `sources/temi/2ра тема` / production transcription
  `run/ocr/temi_02__production/page_005.json` (page 5, “2ра тема”) gives the
  non-homogeneous form and then the required construction: form the multiset
  from the homogeneous characteristic roots and each forcing base `b_i`, with
  multiplicity `deg p_i + 1`, then use the resulting general form and initial
  conditions. `topics/manifest.json`, topic 2, explicitly flags the
  recurrence material as requiring the photographs because `sources/di/2.pdf`
  covers only counting principles.
- **Impact:** The chapter stops at recognizing `b^nP(n)` and calls the crucial
  collision case under-specified. An examinee therefore cannot actually solve
  the mapped non-homogeneous recurrences, especially when a forcing base is a
  characteristic root.
- **Correction:** Replace the caveat with the standard undetermined-
  coefficients rule. For a forcing term `b^nP_d(n)`, try
  `n^s b^n Q_d(n)`, where `s` is the multiplicity of `b` as a root of the
  homogeneous characteristic polynomial (zero if absent), determine the
  coefficients by substitution, then add the homogeneous solution and impose
  the initial conditions. State the equivalent augmented-root/multiset method
  used by the source.

## Q3 — Графи. Дървета. Обхождания на графи.

**Verdict: NEEDS CORRECTION.**

### P2 — “Weakly connected” is defined as semiconnected, not weakly connected

- **Chapter:** `topics/bodies/topic_03.tex:198-200`.
- **Evidence:** The mapped source records this wording at
  `sources/di/3.pdf`, p. 1; its transcription is
  `run/di/3/page_001.txt` under “Деф: Слабо свързан граф”. The corroborating
  photo transcription is `run/ocr/temi_03__production/page_001.json` (p. 1,
  “3та тема”).
- **Impact:** “For every pair there is a directed path in at least one
  direction” is the standard notion *semiconnected*, not weakly connected.
  For example, `a <- b -> c` is weakly connected after directions are ignored,
  but neither `a` reaches `c` nor `c` reaches `a`. The present text teaches a
  wrong standard term.
- **Correction:** Define weak connectivity as connectivity of the underlying
  undirected graph. If the source’s stronger condition is retained, name it
  “semiconnected” and distinguish it from weak connectivity.

### P2 — The definition of a simple cycle does not forbid reusing an edge

- **Chapter:** `topics/bodies/topic_03.tex:184-190`.
- **Evidence:** `sources/di/3.pdf`, p. 1, transcribed at
  `run/di/3/page_001.txt`, defines a simple oriented cycle with all elements
  other than the coincident endpoints unique; the photo corpus for the topic
  is `run/ocr/temi_03__production/page_001.json` (p. 1). In contrast, the
  chapter requires only distinct internal vertices.
- **Impact:** In a graph containing one edge `e={u,v}`, the closed walk
  `(u,e,v,e,u)` satisfies the chapter’s stated condition (one distinct internal
  vertex) but is not a simple cycle because it traverses `e` twice. This
  corrupts the definitions used by the tree/acyclicity material.
- **Correction:** Require that the edges are pairwise distinct as well as
  that the internal vertices are pairwise distinct (equivalently, all vertices
  are distinct except the equal first/last vertex).

## Q4 — Характеризация на регулярните езици. Теорема на Майхил–Нероуд.

**Verdict: NEEDS CORRECTION.**

### P1 — The mapped pumping lemma is absent

- **Chapter:** `topics/bodies/topic_04.tex:492-512` (the final exam-focus
  list has no pumping lemma), and no earlier chapter lines formulate it.
- **Evidence:** The exact mapped PDF source, `sources/di/4.pdf`, p. 6,
  contains “Формулировка и доказателство на лемата разрастване за регулярни
  езици (uvw-лема)”; see the typeset production transcription
  `run/ocr/di_4__production/page_006.json` (page 6, section 5). It precedes
  the Myhill–Nerode material on page 7.
- **Impact:** This removes one of the source’s two supplied methods for
  establishing non-regularity and makes the chapter materially less faithful
  to the mapped teaching material.
- **Correction:** Add the regular-language pumping lemma with all three
  conditions (`|uv|<=p`, `|v|>=1`, `uv^iw in L` for every `i>=0`), its
  pigeonhole-principle proof from a DFA with `p` states, and one short
  counterexample application. Add it to the exam-focus list.

### P2 — The minimality proof uses an imprecise and unjustified counting step

- **Chapter:** `topics/bodies/topic_04.tex:408-416`.
- **Evidence:** The mapped source states the Myhill–Nerode theorem and the
  minimal-automaton conclusion in `sources/di/4.pdf`, p. 7; see
  `run/ocr/di_4__production/page_007.json` (page 7, sections 7–8). The
  chapter’s proof needs that conclusion but says “each state ... can
  correspond to at most one class,” which is not the established direction of
  the preceding implication.
- **Impact:** The conclusion is true, but this proof does not show it cleanly:
  one must map each Myhill–Nerode class represented by `u` to the state reached
  after `u` and prove that different classes map to different states. The
  current wording is especially misleading in the presence of unreachable or
  equivalent DFA states.
- **Correction:** For every class choose a representative `u` and map
  `[u]_L` to `delta*(q0,u)`. If two representatives reach the same state, the
  earlier displayed calculation proves they are Myhill–Nerode equivalent;
  hence the map is injective. Therefore the number of classes is at most the
  number of reachable states, and hence at most `|Q|`. This proves minimality
  of `M_L` after restricting arbitrary DFAs to reachable states (or directly
  using the inequality).

## Audit notes

- No P0 issue was found in Q1–Q4.
- Q1’s extra exposition beyond the source was not treated as an error where it
  remained correct and supported the announced syllabus.
- Q2’s stated gap about arbitrary binary-relation properties matches the
  source-map limitation and was not elevated as a chapter defect.
