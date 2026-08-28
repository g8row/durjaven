# Round 02 — focused independent review: questions 28–31

Scope: `topics/topic_28.tex` through `topics/topic_31.tex`, reviewed through
their included body files.  I used the current, deliberately rotated map in
`topics/manifest.json`: Q28 and Q29 -> `sources/di/32.pdf`; Q30 ->
`sources/di/28.pdf`; Q31 -> `sources/di/29.pdf`.  The official spine and
topic requirements were checked against `sources/konspekt/Konspekt_DI_KN-30.06.2025.pdf`,
pp. 15–16 (questions 28–31).

`sources/di/32.pdf` is image-only in this workspace (four PDF pages), so its
page-level fidelity check used its page range and the official annotation;
the formula audit below is independent of its OCR.  `sources/di/28.pdf` is
pp. 1–2 and `sources/di/29.pdf` is pp. 1–5.

## Findings requiring correction

### P2 — Q30: the proof that the quadratic scalar is real skips its essential identity

- **Chapter location:** `topics/bodies/topic_30.tex:163-177`.
- **Claim/step:** after obtaining
  `\overline z^{\,t}Az=\lambda\sum_i|z_i|^2`, the text states merely from
  real symmetry that this scalar equals its complex conjugate (lines 163–168),
  then states that it equals
  `\overline\lambda\sum_i|z_i|^2` (lines 169–177).
- **Source:** `sources/di/28.pdf`, p. 1 (the source’s proof explicitly works
  through transposition and complex conjugation before reaching the real-root
  conclusion).
- **Why this is a gap:** both displayed conclusions are true, but the second
  does not follow directly just by conjugating `Az=\lambda z` as written.
  One must use `A^t=A`, for example
  In detail, if `q=\overline z^{\,t}Az`, then symmetry and real entries give
  `\overline q=z^tA\overline z`; transposing
  `A\overline z=\overline\lambda\overline z` gives
  \[
    \overline q=\overline\lambda\,z^t\overline z
    =\overline\lambda\sum_i|z_i|^2.
  \]
  Together with `q=\lambda\sum_i|z_i|^2` and `q=\overline q`, this proves
  the conclusion. A cleaner proof
  is to state that `A=A^*`, hence `z^*Az` is real, and then compare
  `z^*Az=\lambda z^*z` with its conjugate.  The current prose leaves the
  key Hermitian/symmetry calculation unjustified.
- **Impact:** the theorem is correct and the later diagonalization proof uses
  it correctly, but this is a proof gap in one of the explicitly required
  spectral results.
- **Correction:** insert the missing transpose/conjugation calculation (or
  replace lines 163–177 with the short `A=A^*` argument), explicitly noting
  that `z^*z>0` for `z\ne0`.
- **Confidence:** high.

## Per-question verdicts and coverage

| Question | Verdict | Coverage and source-fidelity result |
|---|---|---|
| 28 — lines in the plane | **Pass** | Reviewed parameter/vector equations (body lines 3–71), general equation and its two directions (73–197), determinant/proportionality criteria (199–301), Cartesian form (303–371), normal form and point-to-line distance (373–477), and half-planes including the sign proof (479–577). All stated nonzero and orthonormal-coordinate conditions are present; formulas, determinants, examples, and signs check out. It covers the official requirements and the mapped `sources/di/32.pdf`, pp. 1–4. |
| 29 — planes and lines in space | **Pass** | Reviewed plane parameterizations (3–68), determinant/general-plane theorem and the three-point construction (70–235), complete rank/proportionality classification of two planes (237–336), normal equations and distance (338–427), half-spaces (429–485), and spatial-line equations/intersection of two nonparallel planes (487–610). The rank conditions, determinants, distance formulas, and examples are correct; all required themes are present. The richer rank treatment is compatible enrichment over mapped `sources/di/32.pdf`, pp. 1–4, not a fidelity omission. |
| 30 — symmetric operators | **P2 above; otherwise pass** | Reviewed definition and orthonormal-basis matrix equivalence (3–121), real spectrum (123–206), orthogonality (208–259), invariant orthogonal complement (261–320), induction diagonalization proof (322–418), matrix example (424–513), and recap (515–582). The theorem statements, hypotheses, induction, and example are correct and cover `sources/di/28.pdf`, pp. 1–2; only the proof step identified above needs repair. |
| 31 — symmetric/alternating groups, Cayley, homomorphisms | **Pass** | Reviewed cycle decomposition and conjugacy (3–169), transpositions/parity/`A_n` (171–278), homomorphism/kernel/image and quotient construction (280–407), first isomorphism theorem (408–511), and Cayley’s theorem (513–574). Composition order, cycle-to-transposition formula, normality/index argument, coset equivalence, induced map, and left-regular representation all check out. It covers every official topic and the mapped `sources/di/29.pdf`, pp. 1–4; additions are mathematically correct explanatory strengthening. |

No P0 or P1 findings were identified in this assigned scope.  No chapter files
were edited.
