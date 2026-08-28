# Round 02 — Questions 19–22: independent review

Scope: `topics/bodies/topic_19.tex` through `topic_22.tex`, checked against the mapped entries in `topics/manifest.json`, `run/di/19`, `run/di/20`, `sources/di/Задачи/FP.txt`, and the canonical logical-material OCR (`run/ocr/di_logichesko1__production`, `run/ocr/di_logichesko2__production`, and `run/ocr/di_Logichesko__production`).  No prior-round findings were used as authority.

## Verdicts

| Question | Verdict | Summary |
|---|---|---|
| 19 | Needs correction | The Scheme/Racket `foldl` example uses the Haskell argument convention. |
| 20 | Needs correction | The presented stream implementation redefines `delay` as a thunk but still applies the native `force`; it cannot run as shown. |
| 21 | Pass | The first-order syntax, valuation semantics, quantifiers, capture warning, and substitution lemma are technically sound and match the mapped logic material. |
| 22 | Needs correction | The resolution-completeness theorem is stated without the source's exclusion of formal equality; the substitution definition also omits a source condition. |

## Findings

### Q19 — P1: `foldl` has the wrong argument order for the displayed Scheme/Racket call

- **Chapter:** `topics/bodies/topic_19.tex:375-385` states that `(foldl - 0 '(1 2 3))` means `((0-1)-2)-3`.
- **Evidence:** `sources/di/Задачи/FP.txt`, section **3. ФУНКЦИИ ОТ ПО-ВИСОК РЕД**, defines the Racket-style call as `foldl - 0 '(1 2 3)` = `(- 3 (- 2 (- 1 0)))` = `2`; the mapped lecture source likewise gives the Haskell and Scheme conventions separately (`run/di/20/page_003.txt`, PDF p. 3).
- **Impact:** In Racket's `foldl`, the combining procedure receives *element, accumulator*, not accumulator, element.  For a noncommutative operation the chapter's expansion is false: the shown Scheme/Racket expression evaluates to `2`, whereas `((0-1)-2)-3` is the Haskell `foldl (-) 0 [1,2,3]` expansion and evaluates to `-6`.
- **Correction:** Either label the discussion as Haskell and use `[1,2,3]`, or retain Scheme/Racket syntax and write the Racket expansion `(- 3 (- 2 (- 1 0)))`.  Do not present the Haskell accumulator-first law as the semantics of a Scheme/Racket call.

### Q20 — P1: the stream code mixes a homemade thunk with the primitive promise API

- **Chapter:** `topics/bodies/topic_20.tex:594-615` defines `(delay x)` to expand to `(lambda () x)`, while `tail` subsequently calls `(force (cdr s))`; the later stream examples rely on this pair (`:621-688`).
- **Evidence:** The mapped source identifies `delay` and `force` as a matched pair of **primitive operations**: `delay` returns a promise and `force` forces that promise (`run/di/20/page_004.txt`, PDF p. 4).  The same source explicitly says that Scheme promises memoize their computed value.
- **Impact:** In Scheme/Racket, native `force` expects a promise, not a zero-argument procedure.  With the chapter's macro, `(cdr s)` is a procedure, so `tail` raises a contract/type error rather than returning the next stream.  Replacing `force` with direct procedure application would make it run but would still lose the promised memoization.
- **Correction:** Remove the redefinition of `delay` and use the language's native `delay`/`force` pair in `cons-stream`; alternatively provide a complete, internally consistent thunk-plus-memoization implementation (including its own `force`).

### Q22 — P1: first-order resolution completeness is asserted for a language that may contain formal equality

- **Chapter:** `topics/bodies/topic_22.tex:333-340` asserts `Γ` is unsatisfiable iff `Γ ⊢_r □` for an unqualified set of predicate clauses; `:366` then appeals to Herbrand instances.  This follows a book definition that permits formal equality in the language (`topics/bodies/topic_21.tex:8-14,66-74`).
- **Evidence:** The canonical source's equivalence between the Herbrand/deductive treatment and models is expressly for a language **without formal equality** (`run/ocr/di_logichesko1__production/page_005.json`, PDF p. 5, “език L е без формално равенство”; `page_006.json`, PDF p. 6).  Its Herbrand theorem repeats the same restriction (`run/ocr/di_Logichesko__production/page_152.json`, PDF p. 152).
- **Impact:** Ordinary resolution without equality axioms or a dedicated equality calculus is not complete for first-order logic with built-in equality.  The theorem as printed overclaims the method and conflicts with the stated source hypotheses.
- **Correction:** State the theorem for clause sets in a language without formal equality (and make the Herbrand/scoping hypotheses explicit), or add an equality extension such as paramodulation/superposition or appropriate equality axioms before claiming completeness.

### Q22 — P2: substitution definition drops the source's non-identity condition

- **Chapter:** `topics/bodies/topic_22.tex:223-232` calls any finite set of mappings from distinct variables to terms a substitution.
- **Evidence:** The mapped source requires, in addition, `x_i ≠ τ_i` for every displayed mapping (`run/ocr/di_logichesko1__production/page_002.json`, PDF p. 2).
- **Impact:** Allowing identity mappings is harmless mathematically if substitutions are treated extensionally, but it is not the course source's definition and weakens fidelity just before unification is introduced.
- **Correction:** Add `x_i\ne t_i` to the definition, or explicitly state that identity mappings are admitted but discarded without changing a substitution's action.

## Checks with no P0–P2 finding

- **Q19:** The distinction between applicative/call-by-value and normal/call-by-name is correctly qualified at `topic_19.tex:292-318`; it does not conflate call-by-name with memoizing call-by-need.  Higher-order functions, lambda expressions, and currying are appropriately represented.
- **Q20:** The Haskell `foldr` and `foldl` definitions and their noncommutative examples (`topic_20.tex:455-535`) are correct; the chapter correctly repairs the inconsistent source/Racket `foldl` example in the Haskell section.  List representation, `eq?`/`equal?`, `memq`/`member`, and the intended lazy-list account are sound subject to the stream-code correction above.
- **Q21:** Inductive syntax, scope/free-variable definitions, nonempty structures, term/formula valuation, equality semantics when present, quantifier clauses, and capture-avoiding substitution agree with `run/ocr/di_logichesko1__production/page_001.json` (PDF p. 1), `page_004.json` (PDF p. 4), and `page_005.json` (PDF p. 5).
- **Q22:** Propositional resolvents, standardizing variables apart before predicate resolution, occurs check, Horn-clause reading, and the SLD/Prolog explanation are technically appropriate.  Propositional-resolution completeness itself is supported by `run/ocr/di_logichesko2__production/page_011.json` (PDF p. 11) and `page_013.json` (PDF p. 13).
