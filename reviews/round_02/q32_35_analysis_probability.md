# Round 2 independent review — Questions 32–35

Scope: independent, read-only audit of the four generated chapter bodies against the authoritative question map in `topics/manifest.json` and the mapped local PDFs.  The shifted mapping is respected: Q32 → `sources/di/30.pdf`, Q33 → `sources/di/31.pdf`, Q34 → `sources/di/33.pdf`, Q35 → `sources/di/34.pdf`.

## Verdicts

| Question | Verdict | Source checked | Result |
|---|---|---|---|
| 32 — Fermat, Rolle, Lagrange, Cauchy, Taylor | PASS | `sources/di/30.pdf`, pp. 1–3 | The hypotheses and proofs cover every named result. The Cauchy form explicitly protects both denominators, and the Taylor remainder proof correctly invokes Cauchy on the auxiliary functions. |
| 33 — definite integral, Darboux sums, integrability, Newton–Leibniz | PASS | `sources/di/31.pdf`, pp. 1–4 | Definitions use the correct lower/upper Darboux conventions; the Darboux criterion, continuous-function integrability, and both fundamental-theorem directions are present and mathematically coherent. |
| 34 — iterative nonlinear solvers | P1 | `sources/di/33.pdf`, pp. 1–3 (especially p. 2) | The fixed-point/contraction material and the chord, secant, and Newton formulas are covered, but the stated definition of convergence order is nonstandard and overstrong for the later order claims. |
| 35 — binomial, geometric, Poisson | PASS | `sources/di/34.pdf`, pp. 1–4 | PMFs, normalisation, PGFs, means, and variances agree with the mapped material. The chapter consistently chooses the zero-based geometric convention that the source uses. |

## Findings

### P1 — “Order of convergence” is defined by a stronger global bound, not by the usual local/asymptotic error order

- **Chapter:** `topics/bodies/topic_34.tex`, lines **276–288**. It declares order \(p>1\) from \(|x_n-\xi|\le Cq^{p^n}\), then uses the terminology alongside the standard secant and Newton orders later in the chapter (lines 484–488 and 520–523).
- **Mapped source:** `sources/di/33.pdf`, **p. 2**. The corresponding source line is OCR-damaged in `run/di/33/page_002.txt`, but it is the source’s section headed “ред на сходимост”; the surrounding page gives the geometric estimate and introduces the chord/secant methods.
- **Impact:** \(Cq^{p^n}\) is at best a strong sufficient/R-order-style bound; it is not the standard definition of Q-order. Consequently the reader cannot correctly interpret the stated secant order \((1+\sqrt5)/2\) or Newton’s quadratic order from the definition supplied. A source extraction defect should not be preserved as a replacement definition that changes the concept.
- **Proposed correction:** define local order \(p\ge1\) using \(e_n=x_n-\xi\) and
  \[
  \lim_{n\to\infty}\frac{|e_{n+1}|}{|e_n|^p}=\mu,\qquad 0<\mu<\infty,
  \]
  or explicitly label an eventual inequality \(|e_{n+1}|\le C|e_n|^p\) as an upper-order estimate. Keep \(|e_n|\le Cq^n\) separately for linear/geometric convergence. Then retain the secant and Newton orders under that definition.

## No additional P0–P2 findings

I found no further source-fidelity omission or mathematical defect at P0–P2 severity in Q32, Q33, or Q35. In particular, Q32’s Taylor hypotheses support the differentiations used in its proof; Q33’s use of lower/upper integrals is directionally correct; and Q35’s zero-based geometric PMF \(q^kp\), PGF \(p/(1-qs)\), mean \(q/p\), and variance \(q/p^2\) are mutually consistent.
