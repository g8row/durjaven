# Round 2 — P1 validation: formal/algorithms

Independent check of the five specified reports against the chapter bodies and
the mapped local sources. No chapters were changed.

## Q2 — non-homogeneous recurrences: **CORROBORATED**

- **Chapter:** `topics/bodies/topic_02.tex:394-415`.  It gives the form and
  identifies `b^nP(n)`, but line 414 expressly declines to state how a
  forcing base that is a homogeneous root is handled.
- **Mapped source:** `run/ocr/temi_02__production/page_005.json` (source p. 5,
  `2ра тема`): after finding the homogeneous roots, it forms a multiset of
  forcing bases with multiplicity `deg p_i+1`, unions it with the homogeneous
  root multiset, and solves the resulting `k+l`-parameter form from initial
  conditions.  `topics/manifest.json:26` identifies these photographs as the
  required recurrence source.
- **Minimal correction:** State the equivalent rule: for `b^nP_d(n)`, use a
  particular trial `n^s b^nQ_d(n)`, where `s` is the multiplicity of `b` in
  the homogeneous characteristic polynomial; then add the homogeneous
  solution and determine constants from the initial conditions.

## Q4 — regular-language pumping lemma: **CORROBORATED**

- **Chapter:** no pumping/`uvw` lemma occurs in `topics/bodies/topic_04.tex`;
  the final coverage list is `:492-512` and proceeds from Kleene directly to
  Myhill--Nerode/minimisation.
- **Mapped source:** `run/ocr/di_4__production/page_006.json` (source p. 6,
  item 5) explicitly requires the formulation and proof of the regular
  language pumping (`uvw`) lemma.  Its statement gives `alpha=uvw`,
  `|v|>=1`, `|uv|<=p`, and `uv^n w in L` for every natural `n`.
- **Minimal correction:** Add the lemma, the DFA/pigeonhole proof, and one
  short non-regularity application; include it in the exam-focus list.

## Q7 — Prim theorem connectedness: **CORROBORATED**

- **Chapter:** `topics/bodies/topic_07.tex:176-208` states unconditionally
  that Prim returns an MST.  Although the chapter introduces the MST problem
  for a connected graph at `:13, 36-42`, neither the theorem nor its proof
  carries that input condition.  In particular, `:189-207` assumes every
  non-root extracted vertex has a predecessor and concludes all vertices are
  connected; this fails after the starting component is exhausted.
- **Mapped source:** `run/ocr/temi_07__production/page_003.json` (source p. 3,
  `7ма тема`) declares Prim's input a non-oriented connected graph; the MST
  theorem is for a weighted connected graph at `page_002.json` (source p. 2).
- **Minimal correction:** Qualify the theorem as applying to a connected
  undirected weighted graph, or separately state/prove that the same code
  returns a minimum spanning forest on a disconnected graph.

## Q22 — first-order resolution completeness with equality: **CORROBORATED**

- **Chapter:** `topics/bodies/topic_22.tex:333-340` asserts the equivalence
  for every set of predicate clauses; `:366` justifies the predicate case via
  Herbrand instances.  The book permits formal equality in the underlying
  language at `topics/bodies/topic_21.tex:8-15, 66-74`.
- **Mapped source:** the Herbrand bridge used here is restricted to a language
  without formal equality in `run/ocr/di_logichesko1__production/page_005.json`
  (source p. 5) and `page_006.json` (p. 6); the same restriction is repeated
  by the Herbrand theorem in `run/ocr/di_Logichesko__production/page_150.json`
  (p. 150) and `page_152.json` (p. 152).
- **Minimal correction:** Restrict the predicate-resolution completeness
  theorem and its Herbrand proof sketch to languages without formal equality
  (with the usual clausification hypotheses), or introduce an equality-aware
  calculus such as paramodulation/superposition before claiming completeness.
