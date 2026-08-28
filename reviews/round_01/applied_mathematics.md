# Applied mathematics review — topics 28–35

Independent bounded review of the chapter bodies against the manifest mapping and the corresponding `sources/di` PDFs (with OCR/math artifacts where available). Findings are limited to high-confidence issues.

## Verdicts

| Topic | Verdict | Evidence checked |
|---|---|---|
| 28 | PASS | [topic_28.tex](/Users/g8row/Documents/durjaven/topics/bodies/topic_28.tex); `sources/di/32.pdf`, pp. 1–4; mapped line/plane formulas and distance/sign criteria checked |
| 29 | PASS | [topic_29.tex](/Users/g8row/Documents/durjaven/topics/bodies/topic_29.tex); `sources/di/32.pdf`, pp. 1–4; plane determinants, rank criteria, distance and half-space signs checked |
| 30 | PASS | [topic_30.tex](/Users/g8row/Documents/durjaven/topics/bodies/topic_30.tex); `sources/di/28.pdf`, pp. 1–2; symmetry and spectral/diagonalisation statements checked |
| 31 | PASS | [topic_31.tex](/Users/g8row/Documents/durjaven/topics/bodies/topic_31.tex); `sources/di/29.pdf`, pp. 1–5; cycle, conjugacy, alternating-group and homomorphism material checked |
| 32 | PASS | [topic_32.tex](/Users/g8row/Documents/durjaven/topics/bodies/topic_32.tex); `sources/di/30.pdf`, pp. 1–3; Fermat/Rolle/Lagrange/Cauchy/Taylor hypotheses and derivation checked |
| 33 | PASS | [topic_33.tex](/Users/g8row/Documents/durjaven/topics/bodies/topic_33.tex); `sources/di/31.pdf`, pp. 1–4; Darboux sums, criterion, Newton–Leibniz statements checked |
| 34 | **P1** | [topic_34.tex](/Users/g8row/Documents/durjaven/topics/bodies/topic_34.tex); `sources/di/33.pdf`, pp. 1–3; convergence-order definition needs correction (below) |
| 35 | PASS | [topic_35.tex](/Users/g8row/Documents/durjaven/topics/bodies/topic_35.tex); `sources/di/34.pdf`, pp. 1–4; binomial/geometric/Poisson pmfs, PGFs, moments checked |

## Finding

### P1 — Topic 34 defines “order of convergence” incorrectly/nonstandardly

At [topic_34.tex:276–288](/Users/g8row/Documents/durjaven/topics/bodies/topic_34.tex:276), order (p>1) is defined by the global bound

\[
|x_n-\xi|\le Cq^{p^n}.
\]

This is a super-exponential bound and is not the standard definition of order (p), which is an asymptotic relation such as

\[
\lim_{n\to\infty}\frac{|e_{n+1}|}{|e_n|^p}=\mu\in(0,\infty),
\qquad e_n=x_n-\xi,
\]

or (for an upper-order statement) (|e_{n+1}|\le C|e_n|^p) eventually. The displayed (q^{p^n}) bound is generally much stronger and does not justify the later claims that the secant and Newton methods have orders ((1+\sqrt5)/2) and (2). Replace the definition with the asymptotic/local error recurrence and retain (Cq^n) only as the separate linear/geometric case. The chapter’s own note at lines 290–292 acknowledges a damaged source formulation, but the replacement currently remains mathematically misleading. Mapped source: `sources/di/33.pdf`, p. 3 (the OCR extraction is visibly damaged; `run/ocr/temi_34__oxalpha/page_004.json`).

## Limitations

The source PDFs for this block are short scanned/typed lecture notes and do not provide stable printed equation numbering. Page references above are PDF page numbers. I did not edit chapter bodies or infer defects from stylistic differences; no other high-confidence P0/P1/P2 mathematical errors were found in this pass.
