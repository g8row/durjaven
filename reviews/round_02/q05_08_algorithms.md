# Round 02 — independent review: questions 5–8

Scope: independent fidelity and correctness review of `topics/bodies/topic_05.tex` through `topic_08.tex`, against the per-topic mapping in `topics/manifest.json`.  The applicable sources are the current photograph OCR sets `run/ocr/temi_05__production`, `temi_06__production`, `temi_07__production`, and `temi_08__production`; the map explicitly marks `6.pdf` and `8.pdf` as stale.  The PDFs `sources/di/5.pdf` and `sources/di/7.pdf` were used only as corroboration where mapped.

## Q5 — CFL pumping; non-closure under intersection and complement

**Verdict: P2 — proof gap; otherwise faithful.**

### P2 — the proof has not established the nonempty pumping portion

- **Chapter:** `topics/bodies/topic_05.tex:115-117`.
- **Evidence:** `run/ocr/temi_05__production/page_003.json` explicitly obtains `|yv| >= 1` by choosing a *minimal* derivation tree and then replacing the middle portion with a smaller tree.  The book chooses only a repeated pair “closest to the leaf” at `topic_05.tex:88`, not a minimal derivation tree.
- **Impact:** The sentence “This contradicts the choice” at line 115 does not follow from the stated choice: deleting a zero-yield middle subtree makes a smaller tree, but need not contradict being the closest repeated pair in the original tree.  Thus a required hypothesis of the pumping lemma is left unsupported in its proof.
- **Correction:** Either choose a derivation tree of minimum size before selecting the repeated nonterminal (and say why the deletion contradicts that choice), as in the source, or use the CNF structure directly to prove that a nontrivial derivation `A =>* yAv` cannot have `y=v=epsilon`.

The lemma statement (`topic_05.tex:46-61`), the `a^n b^n c^n` application (`131-182`), and both non-closure arguments (`184-258`) match the mapped topic and source pages 2–4.

## Q6 — comparison sorting in O(n log n)

**Verdict: Pass.**

The heap definitions and properties, bottom-up `BuildHeap` proof and linear bound, `Heapsort`, merge sort, and inversion counting are consistent with `run/ocr/temi_06__production/page_001.json` through `page_011.json`.  In particular, the `Heapify` bounds checks, the `Heapsort` suffix invariant, and the cross-inversion increment `n1-i+1` are correct.  No P0–P2 finding.

## Q7 — minimum spanning trees

**Verdict: P1 and P2 — a theorem lacks a necessary hypothesis, and a Union--Find proof omits its key invariant.**

### P1 — Prim correctness theorem omits connectedness

- **Chapter:** `topics/bodies/topic_07.tex:176-208` (especially the unconditional statement at 176–178 and the conclusion at 207).
- **Evidence:** The topic map defines Q7 as MSTs; the mapped source states the Prim input is a “неор. свързан граф” in `run/ocr/temi_07__production/page_003.json`, and its MST theorem requires a weighted connected graph in `run/ocr/temi_07__production/page_002.json`.  The chapter correctly states this global problem hypothesis at `topic_07.tex:13` and `36-42`, but drops it from the theorem it proves.
- **Impact:** On a disconnected graph, after its component is exhausted, `Extract-Min` returns vertices with infinite keys and `pi = NIL`; the return set is a forest, not a spanning tree.  Therefore the theorem as written is false.
- **Correction:** State “Let `G` be a connected undirected weighted graph” in the theorem (or explicitly formulate the disconnected variant as a minimum spanning forest), and retain that hypothesis in the proof.

### P2 — union-by-rank height bound is asserted without the invariant that connects height to rank

- **Chapter:** `topics/bodies/topic_07.tex:353-375`, especially 358 and 366–374.
- **Evidence:** The source’s union-by-rank material is `run/ocr/temi_07__production/page_006.json`, which treats the height claim as the theorem to be justified.  The chapter proves only that a root of rank `h` has at least `2^h` vertices (360–364), then concludes that a tree’s “height or rank” is `h` (366), although no invariant `height(tree) <= rank(root)` has been stated or proved.
- **Impact:** The displayed counting argument bounds rank, not height by itself; hence it does not establish the claimed `Find-Set` logarithmic worst-case bound as written.
- **Correction:** Add the simultaneous induction invariant: every tree has height at most its root rank.  On a union, attaching a lower-rank root increases that subtree’s height by at most one and keeps it at most the higher rank; for equal ranks, the selected root’s rank increases by one.  Combine it with `size >= 2^rank` to obtain height `O(log n)`.

The cut-safe-edge theorem, Prim/Kruskal algorithms, and stated complexity formulas are otherwise correct under the chapter’s stated simple/connected graph assumptions.

## Q8 — shortest paths in weighted graphs

**Verdict: P2 — Bellman--Ford proof uses a stronger condition than its theorem and does not prove the stated case.**

### P2 — Bellman--Ford’s intermediate lemmas exclude unreachable negative cycles, but the theorem allows them

- **Chapter:** `topics/bodies/topic_08.tex:365-411`; compare the lemma hypotheses at 365–370 and 392–401 with the theorem at 403–408.
- **Evidence:** The mapped source introduces Bellman--Ford as detecting negative cycles relevant to the source and explains the reachable-cycle condition in `run/ocr/temi_08__production/page_007.json` through `page_009.json`.  The chapter itself correctly says the algorithm detects a cycle “достижим от началния връх” at `topic_08.tex:347` and gives the correct theorem hypothesis “няма отрицателен цикъл, достижим от s” at 403–404.
- **Impact:** A graph can contain a negative cycle unreachable from `s`.  The theorem is true for that graph, but neither preceding lemma applies because each says that the graph has *no* negative cycle anywhere; line 411 therefore cannot derive the theorem from “the previous lemma.”  This is a logical proof gap in a core correctness result.
- **Correction:** State both lemmas with “no negative cycle reachable from `s`.”  In the proof, construct shortest-path predecessors only for reachable vertices and separately preserve `d=+infinity` for unreachable vertices.  In the final edge check, if `x.d=+infinity`, relaxation cannot improve `y`; otherwise both endpoints relevant to an improvement are reachable, so the edge inequality follows.

The Dijkstra nonnegative-weight condition and first-unsettled-vertex proof (`178-270`), DAG-SSSP including negative edges (`273-341`), reachable-negative-cycle detection (`414-458`), and Floyd--Warshall recurrence/in-place space argument (`471-576`) are otherwise correct and consistent with `run/ocr/temi_08__production/page_001.json` through `page_011.json`.
