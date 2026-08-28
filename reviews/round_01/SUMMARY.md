# Round 01 — consolidated findings

Baseline: commit `9830596`. No chapter text was changed during this review.

## Accepted correction queue

| Priority | Topic | Finding | Planned correction |
|---|---:|---|---|
| P1 | 7 | Prim's correctness theorem omits the connectedness hypothesis, although its proof assumes an MST exists and every non-root vertex receives a predecessor. | State that the weighted undirected graph is connected in the theorem and proof setup. |
| P1 | 22 | Predicate-resolution completeness is stated for arbitrary clauses even though the book admits formal equality and gives no equality inference rule. The mapped source explicitly restricts the theorem to a language without formal equality. | Restrict the completeness theorem to first-order clauses without equality, or add a separate equality calculus; the narrow correction is preferred. |
| P1 | 34 | The definition `|e_n| <= C q^(p^n)` is a strong bound, not the standard definition of convergence order used by the later Newton/secant claims. | Define order by `lim |e_(n+1)|/|e_n|^p = mu` (or an eventual local error inequality) and keep geometric convergence as the separate `p=1` case. |
| P2 | 15 | The constant-pointer example uses `p + 2` where `p` points to a scalar. The assignment is intentionally ill-formed because `q` is const, but the right-hand side also distracts with out-of-range pointer arithmetic. | Use two scalar variables and `q = &y`, or use an actual array, so the example isolates the const-assignment error. |
| P2 | 15, 18, 20 | The chapters correctly disclose erroneous or conditional complexity/arithmetic statements inherited from the notes, but the exam-focus summaries could make the caveats more explicit. | Add short source-error warnings to the corresponding exam-focus lists. |
| P3 | 23, 27 and similar | Useful explanatory material added beyond the terse notes is not always labelled as enrichment. | Mark substantial additions as explanatory examples during the editorial pass. |

## Reviewed but not queued

- **Topic 13 transport “broadcasting”:** the chapter omits a phrase present in
  the notes. Copying it verbatim would introduce a questionable layering claim,
  so this needs subject-matter adjudication rather than a fidelity-only edit.
- **Topic 15 Fibonacci bases:** the photographic source explicitly uses
  `fib(0) = fib(1) = 1`; the chapter follows it. This is a shifted convention,
  not a source-fidelity defect. An optional sentence may name the convention.
- **Topics 11–12:** correctly remain explicit gaps; no source exists in the
  corpus and no content was fabricated.

## Coverage result

- Formal foundations: questions 1–8 and 21–22 reviewed; two P1 findings.
- Applied mathematics: questions 28–35 reviewed; one P1 finding.
- Source fidelity: all 35 questions reviewed, with closer inspection of
  questions 9–20 and 23–27; the shifted mapping for questions 28–35 was
  confirmed.

The next pass should correct the three accepted P1 findings first, rebuild and
render the affected chapters, then address P2/P3 items in a separate editorial
commit.
