# Round 2 — consolidated findings

Baseline: book commit `9830596`. Eleven focused agents participated: eight
theme reviewers and three independent second-opinion validators. No chapter
body was edited during the review.

## Result

- No P0 defect was reported.
- Twelve P1 defects were reported and independently corroborated.
- Nine of those P1 defects were not present in the round 1 correction queue.
- Fourteen P2 defects or proof/terminology gaps were reported; three received
  a targeted second-opinion check and were corroborated.

## Corroborated P1 queue

| Q | Finding | Round 1 relationship |
|---:|---|---|
| 2 | The non-homogeneous recurrence section stops before the root-multiplicity/particular-solution rule required by the mapped notes. | New |
| 4 | The mapped regular-language pumping lemma, proof and application are absent. | New |
| 7 | Prim's correctness theorem omits the connectedness hypothesis used by its proof. | Confirms round 1 |
| 10 | Segment validation accepts `offset == length` unless “length” is redefined as an inclusive architectural limit. | New |
| 13 | IPv6 global unicast is incorrectly described as all addresses outside the listed special categories. | New |
| 14 | The chapter falsely says that an omitted C++ return type defaults to `int`. | New |
| 18 | `insertAfter` can append a node without updating the owning doubly linked list's `last` pointer. | New |
| 19 | The displayed Scheme/Racket `foldl` expansion uses Haskell's accumulator/element argument order. | New |
| 20 | The stream example redefines `delay` as an ordinary thunk but passes it to native `force`, and also loses promise memoization. | New |
| 22 | Resolution completeness is claimed for languages that may contain formal equality, without an equality inference calculus. | Confirms round 1 |
| 27 | Producer–consumer is presented as a synonym for implicit invocation/publish–subscribe. | New |
| 34 | The convergence-order definition uses a strong `C q^(p^n)` bound instead of the local/asymptotic error relation used by the later method-order claims. | Confirms round 1 |

The exact evidence and minimal edits are recorded in
`validation_formal_p1.md`, `validation_cs_p1.md`, and `validation_math.md`.

## P2 queue

| Q | Finding | Validation |
|---:|---|---|
| 3 | “Weakly connected” is defined as semiconnected. | Primary reviewer |
| 3 | The simple-cycle definition does not explicitly forbid edge reuse. | Primary reviewer |
| 4 | The Myhill–Nerode minimality proof uses an imprecise counting step. | Primary reviewer |
| 5 | The CFL pumping proof has not established that the pumped portion is nonempty. | **Second opinion corroborated** |
| 7 | The union-by-rank height proof omits the invariant connecting rank and height. | Primary reviewer |
| 8 | Bellman–Ford's lemmas exclude every negative cycle while the theorem excludes only reachable negative cycles. | **Second opinion corroborated** |
| 9 | The instruction-format discussion presents a next-instruction pointer as a usual instruction field. | Primary reviewer |
| 13 | TLD management is attributed too broadly to registrars. | Primary reviewer |
| 15 | Relational pointer comparisons are stated without their same-array/object-domain qualification. | Primary reviewer |
| 17 | A polymorphism example leaks three dynamically allocated objects. | Primary reviewer |
| 22 | The substitution definition omits the source's non-identity condition. | Primary reviewer |
| 23 | Cartesian-product commutativity needs an explicit schema/renaming qualification. | Primary reviewer |
| 24 | Lossless join is initially conflated with dependency preservation. | Primary reviewer |
| 30 | The proof that a symmetric real operator's eigenvalue is real skips the essential conjugation identity. | **Second opinion corroborated** |

## Clean focused passes

No P0–P2 defect was found in questions 1, 6, 16, 21, 25, 26, 28, 29, 31,
32, 33 or 35. Questions 11 and 12 were correctly preserved as explicit source
gaps and were not treated as completed chapters.

## Recommended correction order

1. Repair executable/code-semantic defects in questions 14, 18, 19 and 20.
2. Repair theorem coverage and hypotheses in questions 2, 4, 7, 22 and 34.
3. Correct architectural/taxonomy claims in questions 10, 13 and 27.
4. Apply the P2 proof, terminology and example-hygiene corrections.
5. Rebuild, run reference checks, and visually inspect every affected chapter.
