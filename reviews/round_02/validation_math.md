# Round 02 — independent mathematical validation

Scope: second opinion on the four designated findings only.  Classifications address mathematical correctness, with the mapped source retained as a fidelity check; they do not propose edits to the book.

## Q34 — convergence-order definition (P1)

**CORROBORATED.**

- **Chapter citation:** `topics/bodies/topic_34.tex:276-288`, especially the definition `|x_n-\xi|\le Cq^{p^n}` at 277–281, followed by the secant and Newton order claims at 484–488 and 520–524.
- **Mapped-source citation:** `sources/di/33.pdf`, pp. 1–3; the current photo transcription explicitly records Newton’s `p=2` at `run/ocr/temi_34__production/page_004.json:41-45`.  It does not supply a sound alternative definition.
- **Impact:** The displayed bound is a sufficient, substantially stronger rate estimate, not the usual definition of order.  In particular it is not the definition under which the standard secant order \(\varphi=(1+\sqrt5)/2\) and Newton’s quadratic order are stated.  The later claims therefore do not follow from the chapter’s definition.
- **Minimal correction:** Define order \(p\ge1\) locally by \(\lim_{n\to\infty}|e_{n+1}|/|e_n|^p=\mu\), with \(0<\mu<\infty\) (or state the corresponding eventual local inequality); describe \(p=1\) separately as linear/geometric convergence.

## Q5 — CFL pumping proof: nonempty pump (P2)

**CORROBORATED.**

- **Chapter citation:** `topics/bodies/topic_05.tex:88` chooses only the repeated pair nearest the leaf; `:115-117` infers \(|yv|\ge1\) because deleting a zero-yield section would give a smaller derivation tree.
- **Mapped-source citation:** `sources/di/5.pdf`, pp. 2–3; more legibly, `run/ocr/temi_05__production/page_002.json` chooses a derivation tree with a *minimum number of nodes*, and `page_003.json:43-93` uses that minimality when it deletes the middle portion.
- **Impact:** A smaller tree for the same word does not contradict nearest-to-the-leaf selection in the already chosen tree.  Thus the stated proof has not justified the required \(|yv|\ge1\) condition, even though the pumping lemma itself is true.
- **Minimal correction:** First choose, among derivation trees for the word, one of minimum size, then select the repeated nonterminal; the deletion is then a contradiction.  Alternatively add the direct CNF argument that a proper nonterminal-to-itself derivation has a terminal-producing sibling, so \(y\) or \(v\) is nonempty.

## Q8 — Bellman–Ford reachability mismatch (P2)

**CORROBORATED.**

- **Chapter citation:** the intermediate lemmas assume no negative cycle anywhere at `topics/bodies/topic_08.tex:365-370` and `392-401`, while the theorem assumes only none *reachable from* \(s\) at `403-408`; its proof invokes the preceding lemma at `410-412`.
- **Mapped-source citation:** the designated current source is the Q8 photograph set.  Its proof makes the stronger simplifying assumption that every graph vertex is reachable from \(s\): `run/ocr/temi_08__production/page_008.json:149`; its negative-cycle argument is explicitly about reachable vertices: `page_009.json:25-73`.  This confirms that reachability must be handled, not silently dropped.
- **Impact:** An unreachable negative cycle leaves the theorem true but makes neither cited lemma applicable as written, so line 411 does not prove the theorem’s stated case.
- **Minimal correction:** State the lemmas with “no negative cycle reachable from \(s\).”  Prove exact distances for reachable vertices and retain \(+\infty\) for the rest; in the final edge check, an improving edge with finite tail is reachable, so the usual edge inequality applies.

## Q30 — real-eigenvalue proof identity (P2)

**CORROBORATED.**

- **Chapter citation:** `topics/bodies/topic_30.tex:163-177`.  After obtaining \(A\bar z=\bar\lambda\bar z\) at 169–172, line 175 directly asserts \(\bar z^tAz=\bar\lambda\sum_i|z_i|^2\).
- **Mapped-source citation:** `sources/di/28.pdf`, pp. 1–2 (Q30’s mapped source); the relevant intended result is the reality of characteristic roots for a real symmetric operator.  The chapter’s own displayed formulas are enough to locate the gap precisely.
- **Impact:** The conjugated eigenvector equation has right-hand vector \(\bar z\), so it cannot be substituted directly into \(\bar z^t A z\).  The result is true, but the omitted equality prevents the displayed inference from following.
- **Minimal correction:** Insert
  \[
  \overline{\bar z^tAz}=z^tA\bar z
  =\bar\lambda\,z^t\bar z
  =\bar\lambda\sum_i|z_i|^2,
  \]
  where the first equality uses that \(A\) is real and symmetric.  Combined with the previous reality identity, this yields the desired comparison with \(\lambda\sum_i|z_i|^2\).
