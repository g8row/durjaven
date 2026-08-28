# Round 01 — formal/mathematical review (Q1–8, Q21–22)

Scope: independent check of the mapped chapters against the local corpus. Findings below are limited to high-confidence correctness issues; an unlisted topic is not a claim of exhaustive proof verification.

## Findings

### Q7 — Prim theorem is missing a necessary hypothesis (P1)

- **Chapter:** `topics/bodies/topic_07.tex:176–178` states “Алгоритъмът на Прим връща минимално покриващо дърво” without assuming that `G` is connected.
- **Chapter evidence:** the proof immediately uses “графът има минимално покриващо дърво” at `:181–184`, and later claims all vertices get a predecessor and the output has `|V|-1` edges at `:207`. The pseudocode (`:156–169`) with an arbitrary disconnected input leaves every vertex outside the root component at key `∞`, with `π=NIL`; it therefore returns a spanning tree only for the root component (a spanning forest of that component, not an MST of all `V`).
- **Mapped evidence:** `run/di/7/page_*.txt` / corresponding production OCR for source `sources/di/7.pdf` (the source’s Prim statement is the standard connected-graph version; manifest maps Q7 to `7.pdf`).
- **Correction:** state “For a **connected**, weighted, undirected graph (and chosen root `r`), Prim returns an MST.” Alternatively specify the disconnected-graph behavior as a minimum spanning forest and repair the proof/output claim.

### Q22 — unrestricted completeness claim is false in the presence of equality (P1)

- **Chapter:** `topics/bodies/topic_22.tex:333–340` asserts `Γ` unsatisfiable iff `Γ ⊢r □` for an arbitrary set of predicate clauses. The chapter’s Q21 language explicitly allows formal equality as an atomic formula (`topics/bodies/topic_21.tex:65–74`), while Q22’s resolution rule (`:273–288`) only unifies predicate literals and has no equality rule (paramodulation/superposition) or equality axioms.
- **Why:** treating `=` as an ordinary predicate makes resolution incomplete for first-order logic with equality. For example, equality’s substitution consequences cannot in general be derived by the stated rule. The completeness theorem must either exclude equality from the clause language or add a complete equality treatment.
- **Mapped evidence:** `run/ocr/di_logichesko1__production/page_*.json` and `run/ocr/di_logichesko2__production/page_*.json` (mapped extras `sources/di/logichesko1.pdf`, `sources/di/logichesko2.pdf`; manifest maps these to Q22). The local source material distinguishes predicate resolution from equality handling; no equality inference rule appears in the chapter’s stated calculus.
- **Correction:** qualify the theorem as “for first-order clauses **without equality**” (with standardization-apart and the usual finite-clause assumptions), or extend the calculus and theorem to include equality inference.

## Per-topic verdict

| Topic | Verdict |
|---|---|
| Q1 | No high-confidence P0–P2 issue found in bounded pass. |
| Q2 | No high-confidence P0–P2 issue found in bounded pass. |
| Q3 | No high-confidence P0–P2 issue found in bounded pass. |
| Q4 | No high-confidence P0–P2 issue found in bounded pass. |
| Q5 | No high-confidence P0–P2 issue found in bounded pass. |
| Q6 | No high-confidence P0–P2 issue found in bounded pass. |
| Q7 | **P1:** missing connectedness hypothesis in Prim correctness theorem. |
| Q8 | No high-confidence P0–P2 issue found in bounded pass. |
| Q21 | No high-confidence P0–P2 issue found in bounded pass. Equality syntax is relevant to Q22’s qualification. |
| Q22 | **P1:** completeness theorem needs an explicit no-equality restriction or equality inference. |

## Limitations

This was a bounded textual/formal pass, not a line-by-line reconstruction of every proof or a fresh OCR transcription. Source-page citations are given at the mapped corpus level where the evidence is distributed across OCR page files; page-local OCR can be incomplete or image-derived. No chapter files were edited.
