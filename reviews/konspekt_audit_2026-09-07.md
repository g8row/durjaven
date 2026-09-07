# Book audit against the Konspekt

Audit date: 7 September 2026. **Verdict: substantial coverage, but not yet complete or reliably visible at a glance.**

> **Status: remediated, 7 September 2026.** All eleven findings have been acted on and the
> acceptance criteria below are met. The findings are kept in their original wording as the
> record of what was wrong; see [What was changed](#what-was-changed) at the end for the
> per-finding disposition and for the three things this revision did *not* resolve.

The current book contains all 35 topics in the correct June 2025 order. The remaining work is mostly targeted: close several specific annotation gaps, represent the sample task types explicitly, and make each chapter's required output visible before its exposition.

## Scope and evidence

- Authority: the user-supplied `Konspekt_DI_KN-30.06.2025-1.pdf`, including the detailed annotations on pages 6–17, the topic list on pages 4–5, and exam arrangements on page 3. Its SHA-256 matches the repository's Konspekt exactly.
- Book: the existing 447-page `darzhaven-izpit-kn.pdf`, with `topics/bodies/topic_01.tex` through `topic_35.tex` as supporting evidence. Existing book/source modifications were preserved. Book SHA-256: `b74d196480b4db6e0d206bdf661b489e97197ffbe7dc38540bef51a23924a3d8`.
- Method: read the official annotations; map their required concepts, statements, proofs, constructions, algorithms and task types to chapter sections; inspect body passages for the identified gaps; confirm findings in the compiled PDF; visually inspect the annotation pages and representative book openings, checklists and disputed passages.
- This is a **syllabus coverage and study-navigation audit**, not a line-by-line certification of every mathematical proof or executable program. “Located” below means a corresponding treatment was found, not that its correctness has been independently certified. Sample tasks are illustrative task types; a missing worked example is distinguished from missing required theory.
- All page references below are **PDF viewer pages**, counting the cover as page 1. In this book the printed page number is one less. Section references are more stable after a rebuild.
- The read-only structural check passed: **35 topics, 396 definitions, 171 numbered results, 173 proof blocks**. That confirms formatting/proof-block presence; it does not establish annotation coverage. The build and `check_refs.py` were not run because the latter rebuilds and republishes the book.

## Priority findings

### 1. Required closure constructions are absent from Topic 5

**Priority: high — definite theory/construction gap.** Konspekt p. 7, Topic 5 item 2 requires constructions for closure under regular operations, without proofs. The book states closure under union, concatenation and Kleene star in §5.4, p. 72, but does not give the general grammar constructions. The final checklist (§5.6, p. 74) omits this requirement too.

The two particular grammars used in the intersection counterexample do not replace constructions for arbitrary input grammars. Add a separate subsection with disjoint renamed nonterminal sets and a fresh start symbol for union, concatenation and star. Put all three constructions in the opening checklist. The existing pumping lemma, non-context-free example, and nonclosure proofs can remain.

Evidence: [topic_05.tex:197](/Users/g8row/Documents/durjaven/topics/bodies/topic_05.tex:197), [checklist:276](/Users/g8row/Documents/durjaven/topics/bodies/topic_05.tex:276).

### 2. Topic 18 does not clearly deliver the requested implementation forms

**Priority: high — partial implementation coverage.** Konspekt p. 12 asks for class definitions implementing a list, stack, queue, rooted/binary rooted tree and binary search tree. It also separately names static, dynamic and linked stack/queue implementations.

The book has substantial algorithm code. Stacks, queues and lists are represented by data-only structs plus free functions; the tree material has a `Node` type and free functions but no complete tree/BST abstraction owning a root and exposing its operations. A C++ `struct` is itself a class type, so the issue is **not the spelling `struct` versus `class`**. The issue is whether the student has a complete implementation of each requested abstraction to reproduce. The chapter also does not separately explain a resizing array implementation alongside fixed arrays and linked nodes.

Provide one coherent class implementation per requested structure, with its invariant, initialization, main operations and resource cleanup. Explicitly distinguish the three representation categories, and include a compact operation-cost table with the relevant assumptions. The existing BST discussion correctly warns that logarithmic costs depend on tree height; preserve that qualification.

Evidence: [stack implementations:44](/Users/g8row/Documents/durjaven/topics/bodies/topic_18.tex:44), [tree representation:444](/Users/g8row/Documents/durjaven/topics/bodies/topic_18.tex:444), [BST:567](/Users/g8row/Documents/durjaven/topics/bodies/topic_18.tex:567), [checklist:706](/Users/g8row/Documents/durjaven/topics/bodies/topic_18.tex:706). Book §§18.2–18.6, pp. 220–236.

### 3. Topic 21 states only the restricted substitution lemma

**Priority: high — statement-scope gap.** Konspekt p. 13 asks for the substitution lemma to be formulated, and proved in the special case of a quantifier-free formula. The book explains admissibility and variable capture, but its boxed theorem explicitly assumes a quantifier-free formula. The general formula-level statement under admissibility is missing.

Add the general statement with its admissibility conditions; keep the existing quantifier-free proof and label its restricted scope. A proof for quantified formulas is not demanded by this annotation.

Evidence: [topic_21.tex:443](/Users/g8row/Documents/durjaven/topics/bodies/topic_21.tex:443), [theorem:465](/Users/g8row/Documents/durjaven/topics/bodies/topic_21.tex:465). Book §21.4, pp. 271–273, especially p. 272.

### 4. Topic 2 misidentifies its official scope and underrepresents its actual tasks

**Priority: high — misleading exam guidance plus practice gaps.** In §2.5, p. 45, the book claims that Topic 2's annotation asks for proving or disproving properties of binary relations and that source limitations prevent coverage. That task belongs to **Topic 1**. The final checklist repeats the incorrect guidance.

Topic 2's real sample tasks include counting partial/total functions, injections and surjections; integer solutions with restrictions; and solving concrete homogeneous/nonhomogeneous recurrences. The chapter provides total-function/injection counting through configurations, ordinary stars-and-bars, and the recurrence method. It does not explicitly develop partial-function and surjection counting, the shift for lower bounds on integer solutions, or a worked recurrence solved through its initial conditions.

Remove §2.5's false scope warning and its final checklist item. Replace them with an explicit task checklist and worked examples covering the above cases. Separate “the method is explained” from “a representative exam task has been worked through.”

Evidence: [topic_02.tex:137](/Users/g8row/Documents/durjaven/topics/bodies/topic_02.tex:137), [recurrences:348](/Users/g8row/Documents/durjaven/topics/bodies/topic_02.tex:348), [incorrect scope note:463](/Users/g8row/Documents/durjaven/topics/bodies/topic_02.tex:463). Konspekt p. 6.

### 5. Topic 3 omits the minimum edge-disjoint path decomposition task

**Priority: medium — explicit sample task type missing.** The official third sample task on p. 7 asks for decomposition of a graph's edge set into a minimum number of paths with no shared edge. Neither the treatment of Euler traversals nor the final checklist teaches this task explicitly.

Add a worked problem explaining the lower bound, a construction achieving it, and treatment of separate edge-containing components. Also add a concrete BFS/DFS spanning-tree trace and an Euler traversal example: current general algorithms are useful, but the task types should be visible as such.

Evidence: [topic_03.tex:301](/Users/g8row/Documents/durjaven/topics/bodies/topic_03.tex:301), [Euler section:390](/Users/g8row/Documents/durjaven/topics/bodies/topic_03.tex:390). Book §§3.5–3.7, pp. 53–57.

### 6. Topic 34 describes geometry but supplies no geometric illustrations

**Priority: medium — requested presentation component incomplete.** Konspekt p. 16 explicitly asks for geometric illustrations, iteration formulas and convergence orders for the chord, secant and Newton methods. The formulas, orders and verbal geometric descriptions are present in §34.4, pp. 429–432, but there are no corresponding diagrams.

Add three labelled diagrams showing the graph, the fixed endpoint or current iterates, the chord/secant/tangent, and the next x-axis intersection. The similar Darboux-sum drawing in Topic 33 is described by the Konspekt as desirable, so its absence is an improvement opportunity rather than the same degree of gap.

Evidence: [topic_34.tex:285](/Users/g8row/Documents/durjaven/topics/bodies/topic_34.tex:285), [comparison:517](/Users/g8row/Documents/durjaven/topics/bodies/topic_34.tex:517).

### 7. Two terminology mismatches need explicit reconciliation

**Priority: medium — literal annotation coverage is unclear.** These should not silently receive a “fully covered” status:

| Topic | Official wording | Book treatment | Required clarification |
|---|---|---|---|
| 14 | Parameter passing by name and by value, Konspekt p. 11 | §14.6.5 explains value and C++ reference passing; “by name” is explained later in Topic 19 | Explain the annotation's terminology explicitly, distinguish the mechanisms, and link to §19.3.2 if that is the intended treatment. |
| 16 | Derived and nested classes, Konspekt p. 11 | §16.3.3 explains embedding an object as a field (composition) | Distinguish nested class declarations from object composition and state which interpretation the course expects. Add a nested-class example to cover the literal wording. |

Evidence: [topic_14.tex:593](/Users/g8row/Documents/durjaven/topics/bodies/topic_14.tex:593), [topic_16.tex:396](/Users/g8row/Documents/durjaven/topics/bodies/topic_16.tex:396). Book pp. 179–180 and 205. These are scope/terminology findings, not an assumption that reference passing or composition is itself invalid material.

### 8. The book does not preserve the exam-selection notes

**Priority: high for “at a glance.”** The following notes from the official annotations are not explicitly reproduced in the relevant chapters/checklists:

| Topic | Selection stated by the Konspekt | Source page |
|---|---|---:|
| 6 | HEAPSORT **or** MERGESORT | 8 |
| 7 | Prim **or** Kruskal | 8 |
| 8 | Dijkstra **and** DAG shortest paths, **or** Bellman–Ford **and** Floyd–Warshall | 8 |
| 18 | Two of the listed structures will be selected for description | 12 |

Display the selection note at the start of each chapter, preserving the grouping. It describes what may be selected on the exam; it does not tell students to omit the other alternatives from preparation. The book already contains all four Topic 8 algorithms, so that is a navigation issue, not missing Bellman–Ford/Floyd–Warshall content.

### 9. Required material and supplementary study are mixed in the checklists

**Priority: high for study efficiency.** Every chapter has “Изпитен фокус,” but the checklists occur at the ends of the chapters, after up to many pages of exposition. They have no consistent per-item links to the relevant statement, proof or algorithm. The 18-page table of contents is navigable, but it is not a compact requirement map.

Examples of scope inflation or distraction:

- Topic 3 opens with a substantial equivalence-relations recap (§3.1, pp. 47–48), before the graph definitions, and leads its exam checklist with that recap.
- Topic 4's checklist asks for a proof of Kleene's theorem even though its annotation asks only for the statement. General induction and regular-language pumping also compete with the specifically required Myhill–Nerode proof steps.
- Topic 22 correctly notes that its completeness proof is additional, but the note appears at the end of the proof. Move that status to its heading/opening checklist.
- Topic 35 proves generating-function properties that the annotation permits without proof. Keep these explanations if useful, while marking their study priority.

Blue/green/gold/grey boxes distinguish mathematical object types and emphasis. They do not encode whether the official annotation asks for a definition, statement only, full proof, construction, implementation or example. Add those explicit labels; do not rely on colour alone.

Evidence: [topic_03.tex:3](/Users/g8row/Documents/durjaven/topics/bodies/topic_03.tex:3), [topic_04.tex:524](/Users/g8row/Documents/durjaven/topics/bodies/topic_04.tex:524), [topic_22.tex:329](/Users/g8row/Documents/durjaven/topics/bodies/topic_22.tex:329), [topic_35.tex:107](/Users/g8row/Documents/durjaven/topics/bodies/topic_35.tex:107).

### 10. Topics 11 and 12 are present, but need stronger practical support and source verification

**Priority: medium — depth and verification, not missing chapters.** Both now cover the named theoretical headings. The source notes candidly state that verification against the prescribed literature remains outstanding. Topic 11 sketches all three official file tasks, and Topic 12 gives parent/child and producer/consumer schemes. Neither gives complete worked C programs demonstrating the error handling and lifecycle decisions in those schemes.

Add at least one complete POSIX file solution and a complete process/pipe solution, with the remaining task types clearly indexed. Preserve the distinction between concise theory coverage, worked practical readiness and verification against literature. For Topic 11's patch task, make the handling of repeated offsets an explicitly stated interpretation; the current text chooses checks against the mutable output copy, while the official wording does not explicitly settle that edge case.

The book's source notes refer to literature numbers such as [42] and [46], but the book has no bibliography resolving those numbers. Reproduce or link the official bibliography so these references can be used.

Evidence: [topic_11.tex:4](/Users/g8row/Documents/durjaven/topics/bodies/topic_11.tex:4), [tasks:79](/Users/g8row/Documents/durjaven/topics/bodies/topic_11.tex:79), [topic_12.tex:4](/Users/g8row/Documents/durjaven/topics/bodies/topic_12.tex:4), [schemes:79](/Users/g8row/Documents/durjaven/topics/bodies/topic_12.tex:79). Book pp. 146–155.

### 11. Topic 29's final revision bullet contains a contradictory phrase

**Priority: medium — misleading at-a-glance wording.** The final item on p. 374 describes a line as the intersection of two planes “непресичащи се по права.” This contradicts the intended construction and the correct treatment in §29.6.2. Replace it with two distinct planes intersecting in a line (or, equivalently here, two nonparallel planes).

Evidence: [topic_29.tex:699](/Users/g8row/Documents/durjaven/topics/bodies/topic_29.tex:699).

## Quick chapter index

Every chapter also needs the common opening-panel improvement described in finding 9. “Located” below remains a coverage observation, not a correctness certificate. Pages refer to the current PDF.

| Topic | Subject | Starts | Exam focus starts | Main follow-up |
|---:|---|---:|---:|---|
| 1 | Sets and relations | 22 | 34 | Located; no specific gap identified |
| 2 | Combinatorics and recurrences | 36 | 45 | Fix scope + practice |
| 3 | Graphs and trees | 47 | 56 | Add task type |
| 4 | Myhill–Nerode | 58 | 67 | Separate required/extra |
| 5 | Context-free languages | 68 | 74 | Missing constructions |
| 6 | Sorting | 75 | 87 | Add selection note |
| 7 | Minimum spanning trees | 88 | 100 | Add selection note |
| 8 | Shortest paths | 102 | 116 | Add selection note |
| 9 | Architecture | 119 | 132 | Located; no specific gap identified |
| 10 | Memory and interrupts | 134 | 144 | Located; no specific gap identified |
| 11 | Filesystems | 146 | 149 | Practice + verify sources |
| 12 | Processes and IPC | 151 | 155 | Practice + verify sources |
| 13 | Networks | 156 | 165 | Located; no specific gap identified |
| 14 | Procedural fundamentals | 167 | 182 | Clarify parameter passing |
| 15 | Pointers, arrays, recursion | 184 | 195 | Located; no specific gap identified |
| 16 | OOP fundamentals | 196 | 207 | Clarify nested classes |
| 17 | Polymorphism | 209 | 218 | Located; no specific gap identified |
| 18 | Data structures | 220 | 236 | Implementation coverage |
| 19 | Functional fundamentals | 238 | 248 | Located; no specific gap identified |
| 20 | Lists and streams | 250 | 264 | Located; no specific gap identified |
| 21 | Predicate syntax/semantics | 265 | 274 | General statement missing |
| 22 | Resolution | 276 | 285 | Label extra proof |
| 23 | Relational databases | 287 | 299 | Located; no specific gap identified |
| 24 | Normal forms | 300 | 312 | Located; no specific gap identified |
| 25 | AI search | 314 | 325 | Located; no specific gap identified |
| 26 | Software processes | 326 | 336 | Located; no specific gap identified |
| 27 | Software architecture | 338 | 352 | Located; no specific gap identified |
| 28 | Lines in the plane | 354 | 362 | Located; no specific gap identified |
| 29 | Lines and planes in space | 363 | 373 | Fix checklist wording |
| 30 | Symmetric operators | 375 | 388 | Located; no specific gap identified |
| 31 | Groups | 390 | 399 | Located; no specific gap identified |
| 32 | Mean value and Taylor | 400 | 411 | Located; no specific gap identified |
| 33 | Riemann integral | 413 | 423 | Proof labels; optional drawing |
| 34 | Iterative methods | 424 | 433 | Missing illustrations |
| 35 | Discrete distributions | 435 | 446 | Label extra proofs |

## Coverage map for all 35 topics

The requirement groups below paraphrase the official annotations. **Located** means the corresponding material is present. **Partial** flags a concrete missing component. **Clarify** flags terminology that is not explicitly reconciled. **Verify** flags the source-verification debt already disclosed by the book. “Located” is not a full correctness sign-off.

### 1–8: Foundations

| Topic | Official requirement groups and where they are treated | Assessment |
|---|---|---|
| 1 | Four named set axioms/schemes (§1.1); induction (§1.2); set operations/properties (§1.3); ordered pairs/n-tuples and ordinary/generalized Cartesian products (§1.4); n-ary/binary relations, equivalence/classes, partial/total orders, Hasse diagrams, minimal/maximal elements and topological sorting (§1.5); partial/total functions and injections/bijections/surjections (§1.6); finite cardinality, countable infinity and pigeonhole principle (§1.7). Examples and proofs support the five sample task types, but the final checklist should enumerate those task types explicitly (§1.8–1.9). | Located; improve task indexing. |
| 2 | Seven counting principles, including inclusion–exclusion proof (§2.1); four configurations and formula derivations (§2.2); binomial coefficients, Newton and double counting (§2.3); homogeneous/nonhomogeneous constant-coefficient recurrence algorithms (§2.4). | Theory located. Partial task coverage and incorrect scope note: finding 4. |
| 3 | Finite directed/undirected graphs and multigraphs (§3.2); paths/cycles, connectedness/components (§3.3); trees/rooted trees, proofs of tree property and vertex/edge count, spanning trees (§3.4); BFS/DFS (§3.5); Euler cycle theorem/proof and Euler path criterion (§3.6). | Theory located. Minimum path decomposition task absent: finding 5. Make the Euler theorem's multigraph scope explicit in its heading/statement. |
| 4 | Regular language, DFA, automaton language (§4.1); Kleene statement (§4.3); Nerode relation, equivalence and right invariance (§4.5); construction of an n-state total DFA from finite index (§4.6); index bound from an n-state DFA and regularity equivalence (§4.7); minimization and justified regularity/nonregularity reasoning (§4.7–4.8). | Located. Add a worked minimal-automaton construction and label extra proof material: finding 9. |
| 5 | CFG, derivation, language and derivation tree (§5.1); pumping statement/proof (§5.2); proved non-CFL example (§5.3); intersection/complement nonclosure proofs (§5.4–5.5); example grammars (§5.4). | Partial: the three general closure constructions are missing. Finding 1. |
| 6 | Heap definition/properties (§6.2); naive build correctness/time (§6.3); Heapify and fast build correctness/time (§6.4); HEAPSORT pseudocode/correctness/time (§6.5); divide-and-conquer MERGESORT pseudocode/correctness/time (§6.6); inversion counting with correctness (§6.7). | Located. Add official alternative-selection note. |
| 7 | Problem and graph assumptions (§7.1); safe-edge/consistent-set theorem with proof (§7.2); Prim pseudocode, correctness and costs for different data structures (§7.3); Kruskal pseudocode/correctness (§7.4), Union–Find (§7.5), time analysis (§7.6). | Located. Add official alternative-selection note. |
| 8 | Problem variants and negative-weight issues (§8.1); Dijkstra variant/pseudocode/correctness/data-structure costs (§8.3); DAG variant/pseudocode/correctness/time/advantages (§8.4); Bellman–Ford variant/pseudocode/correctness/time/negative-cycle detection (§8.5); Floyd–Warshall variant/pseudocode/correctness/time/memory (§8.6). | Located, including both newer algorithm sections. Add official paired alternatives. |

### 9–20: Systems and programming

| Topic | Official requirement groups and where they are treated | Assessment |
|---|---|---|
| 9 | Computer organization/stored program (§9.1); binary integers, BCD, floating point and character encodings (§9.2); registers, ALU, status/flags, control, instructions and memory interface (§9.3); fetch/decode/execute and branches (§9.4); pipeline (§9.5). | Located. The shortened chapter title omits “pipeline,” but §9.5 covers it. |
| 10 | Main-memory organization, cache/main/virtual hierarchy (§10.1); paging directory/descriptors/replacement (§10.2); segmentation selectors/descriptors/tables/registers (§10.3); interrupt types, processing, concurrency, priorities and controllers (§10.4). | Located. |
| 11 | Attributes, unified namespace, object types, mounting, isolation/access rights (§11.1); ext2/ext3 structures (§11.2); cache/deferred writes/elevator/journaling/RAID1/RAID5 (§11.2–11.3); five POSIX calls (§11.4); interval extraction, byte sorting and patching task sketches (§11.5). | Theory located in compact form; practical depth and source verification remain. Finding 10. |
| 12 | Create/execute/terminate/wait primitives (§12.1); process identities, groups/sessions (§12.2); signals and pipes (§12.3); System V shared memory/semaphores/messages (§12.4); synchronization schemes (§12.5). | Theory located in compact form; practical depth and source verification remain. Finding 10. |
| 13 | OSI layer roles and TCP/IP comparison (§13.2); distance-vector and link-state routing (§13.3); classful/classless IPv4 (§13.4); IPv6 characteristics (§13.5); TCP three-way handshake (§13.6); DNS name resolution and IPv4/IPv6 records (§13.7). | Located. |
| 14 | Structured programming (§14.1); control flow, conditionals/loops (§14.2–14.4); local/global variables, initialization/assignment (§14.5); functions/procedures, parameters and type checking (§14.6). | Clarify by-name versus reference passing: finding 7. Practical exercises can be indexed to the existing code examples. |
| 15 | Pointers/arithmetic (§15.1, §15.3); 1D/multidimensional arrays/indexing (§15.2); sorting/searching (§15.5); direct/indirect and linear/branching recursion (§15.6); string storage/operations (§15.4, §15.7). | Located; includes algorithm code for practical study. |
| 16 | Data abstraction (§16.1); class/object declarations, constructors, dynamic resource management/RAII and methods (§16.2); inheritance/access and composition (§16.3); encapsulation (§16.4); static fields/methods (§16.2.6). | Most located. Nested-class wording needs clarification: finding 7. |
| 17 | Virtual functions, subtype polymorphism/dynamic binding (§17.2); abstract methods/classes (§17.3); arrays of objects/pointers (§17.4); function/class templates (§17.5); multiple inheritance (§17.6). | Located; examples support practical study. |
| 18 | Data-structure concept (§18.1); stack representations/operations (§18.2); queue representations/operations (§18.3); singly/doubly linked lists and costs (§18.4); rooted/binary trees and storage (§18.5); BST operations/storage/height-dependent costs (§18.6). | Partial implementation forms: finding 2. Selection note also absent. |
| 19 | Functional style, primitives, combination/abstraction and function definitions (§19.1); expression/application evaluation (§19.2); applicative/normal models (§19.3); higher-order functions as inputs/outputs and lambdas (§19.4). | Located; code examples support practical study. |
| 20 | List representations/operations in Scheme and Haskell (§20.2–20.3); map/filter/folds (§20.4); delayed evaluation, infinite streams and stream operations/higher-order functions (§20.5); lazy/infinite Haskell lists (§20.6). | Located; code examples support practical study. |

### 21–27: Logic, databases, AI and software

| Topic | Official requirement groups and where they are treated | Assessment |
|---|---|---|
| 21 | Language/terms/formulas/scope/free-bound variables/closed formulas (§21.1); structures/assignments (§21.2); truth under assignment, truth in structure and tautology, plus free-variable independence proof (§21.3); substitution and quantifier-free proof (§21.4); definability/model examples (§21.5). | Partial: general substitution statement missing. Finding 3. |
| 22 | Literals/clauses, truth and satisfiability (§22.1); resolution/derivations (§22.2); predicate liberal resolvent, correctness/completeness statements and correctness proof (§22.3); refutation examples (§22.4); Prolog predicates (§22.5). | Located. Mark completeness proof as supplementary before it starts. |
| 23 | Domains/relations/tuples/attributes/relation and database schemas (§23.2); database operations/queries (§23.3); union/difference/product/projection/selection and intersection/join/natural join (§23.4); SQL/DDL/DML examples and triggers (§23.5). | Located. |
| 24 | Schema design/anomalies/constraints/keys (§24.1.1–24.1.3); FDs/Armstrong (§24.1.4–24.1.5); 1NF/2NF/3NF/BCNF (§24.1.6–24.1.9); MVDs and combined inference rules (§24.1.10–24.1.11); 4NF and lossless join (§24.1.12–24.1.13); normalization task/method (§24.1.15–24.1.16). | Located. A dedicated 4NF worked example would improve practice breadth. |
| 25 | State space, states/operators/search characteristics (§25.1.1–25.1.2); beam/hill climbing/annealing (§25.1.3); genetic algorithms (§25.1.4); CSP/backtracking/min-conflicts (§25.1.5); minimax/alpha–beta (§25.1.6). | Named material located; algorithmic correctness is outside this coverage sign-off. |
| 26 | Product/process (§26.1); phases (§26.2); waterfall/RAD/evolutionary/prototype/spiral and comparison (§26.3); XP/Scrum (§26.4); functional/nonfunctional requirements (§26.5); requirements analysis/design (§26.6); description languages/UML (§26.7); verification/validation (§26.8); quality management (§26.9). | Located. |
| 27 | Architecture/structures/views/need/project and organizational impact (§27.1); quality requirements (§27.2); layered/MVC/pipe-and-filter (§27.4) and SOA (§27.5); design process/structure choice/order (§27.6); tactics (§27.7); documentation purpose/elements (§27.8). | Located. Mark additional styles/methods separately from the named minimum. |

### 28–35: Mathematics and applications

| Topic | Official requirement groups and where they are treated | Assessment |
|---|---|---|
| 28 | Vector/scalar parametric line equations (§28.1); general-equation theorem (§28.2); relative positions (§28.3); Cartesian equation (§28.4); normal equation and point-to-line distance (§28.5); half-planes (§28.6). | Located. |
| 29 | Vector/scalar parametric plane equations (§29.1); general-equation theorem (§29.2); plane positions (§29.3); normal equation/distance (§29.4); half-spaces (§29.5); spatial line equations (§29.6). | Located; repair contradictory final checklist phrase. Finding 11. |
| 30 | Symmetric operator and matrix in an orthonormal basis (§30.2); reality of characteristic roots and orthogonality of eigenvectors for distinct eigenvalues (§30.3); invariant orthogonal complement (§30.4); orthonormal diagonalization (§30.5). | Located, with proof blocks. Prerequisites in §30.1 should follow the requirement overview. |
| 31 | Symmetric group/disjoint cycles (§31.1); conjugation (§31.2); transpositions/parity/alternating group (§31.3); homomorphism/kernel/image (§31.4); homomorphism theorem (§31.5); Cayley (§31.6). | Located, with proof blocks. |
| 32 | Local extremum and Fermat proof (§32.1); Rolle/Lagrange/Cauchy proofs including nonzero endpoint denominator (§32.2); Taylor polynomial and Lagrange remainder derivation (§32.3). | Located. Preserve the annotation's permission to use Weierstrass without proof. |
| 33 | Partitions/Darboux sums/refinement monotonicity and integral definition (§33.1); integrability criterion (§33.2); continuous-function integrability via Cantor (§33.3); integral properties (§33.4); integral mean-value proof (§33.5); Newton–Leibniz proof and integral evaluation (§33.6). | Located. Darboux drawing desirable; explicitly distinguish statement-only properties from required proofs. |
| 34 | Fixed point/existence and equation reduction (§34.1); contraction, uniqueness/convergence/error bound and local derivative corollary (§34.2); convergence order (§34.3); chord/secant/Newton formulas/orders and chord convergence proof (§34.4). | Partial presentation: the three geometric illustrations are absent. Finding 6. |
| 35 | Discrete distribution/nonnegative normalized probabilities (§35.1); PGF definition/properties (§35.2); binomial (§35.3), geometric (§35.4), Poisson (§35.5), each with origin/example, PGF derivation, expectation and variance; comparison (§35.6). | Located. PGF-property proofs should be marked supplementary. |

## Proposed “at a glance” structure

Add a compact front-of-book topic index and put a **“По конспекта: какво трябва да мога”** panel immediately after every chapter title. Keep the existing detailed end-of-chapter summaries as revision material after correcting their scope.

Each opening panel should contain:

1. The official topic number/title, including wording omitted from shortened book titles.
2. Any official selection note, prominently displayed.
3. One line per annotation obligation, preserving its action: **definition; statement; proof; construction; pseudocode; time/memory analysis; implementation; task type; diagram**.
4. A link and page number to the exact section/result/example satisfying that obligation.
5. Separate labels for required work, prerequisites and supplementary material.
6. Explicit unresolved coverage/source status wherever applicable; no unqualified “complete” badge based solely on chapter presence.

For example, Topic 5 should open with this compact map:

| Required output | Target |
|---|---|
| **Definitions:** CFG, derivation, CFL, derivation tree | §5.1 |
| **Constructions, no proofs required:** union, concatenation, Kleene star | New closure subsection — currently missing |
| **Statement + proof:** CFL pumping lemma | §5.2 |
| **Example + proof:** a language that is not context-free | §5.3 |
| **Proofs:** failure of closure under intersection and complement | §§5.4–5.5 |
| **Practice:** construct and justify a CFG; justify whether a language is context-free | Index existing examples and add a dedicated practice block |

For Topics 6–8, use a comparison table with columns **input assumptions / pseudocode / correctness / time / memory where requested**, and preserve the official alternative grouping. For Topic 18, use **logical model / representations / implementation / operation costs** for each structure. For Topics 32–35, list the exact results whose proofs/derivations are required.

The exam arrangements on Konspekt p. 3 can be linked from a short front-matter note, including the practical/theoretical split. They are information for the reader, not instructions to the editor or assistant, and are not evidence of academic topic coverage.

## Acceptance criteria for the next revision

- Every detailed annotation obligation has a traceable destination in the book, including the explicitly requested constructions and diagrams.
- Topics 2, 5, 18 and 21 are corrected; Topic 3's missing task type and Topic 34's diagrams are added; Topics 14 and 16 explicitly reconcile terminology.
- The selection notes for 6, 7, 8 and 18 appear at chapter openings.
- A student can open any chapter and see the required definitions, statements, proofs, algorithms/implementations and practice categories before reading the exposition.
- “Statement only” and “supplementary proof” are visible before the relevant material, not explained after it.
- Practical coverage is described honestly: a conceptual sketch, a worked trace and a complete program are different deliverables.
- Topic 11/12 source-verification status is retained until resolved, with usable bibliography references.
- After implementation, rebuild, run structure/reference checks, and visually inspect all 35 new opening panels and changed pages. A passing structural check alone is not a syllabus sign-off.

## What was changed

The audit above was written before any edits. This section records the disposition of each
finding. The book is now 499 pages (was 447); the structural check reports 35 topics,
404 definitions, 183 numbered results, 185 proof blocks, and `check_refs.py` passes
with 578 labels registering.

| # | Finding | Disposition |
|---:|---|---|
| 1 | Topic 5 closure constructions absent | **Done.** New §5.4 gives constructions for union, concatenation and Kleene star over arbitrary grammars, with disjoint renamed nonterminals and a fresh start symbol, plus a remark on why the same approach cannot work for intersection. Opening panel and checklist updated. |
| 2 | Topic 18 implementation forms | **Done.** New §18.2 separates static / dynamic (doubling array, with an amortised-cost proof) / linked. One complete class per requested structure, each with its invariant, constructor, operations and destructor: stack §18.3.3, queue §18.4.3, list §18.5.3, binary tree §18.6.4, BST §18.7.5. Cost table with stated assumptions in §18.8.1. |
| 3 | Topic 21 restricted substitution lemma | **Done.** §21.4 now defines admissibility, states the general lemma (Theorem 21.30) with a full proof of the quantifier case, and labels the existing quantifier-free theorem as the special case the annotation requires with proof. |
| 4 | Topic 2 misidentified scope | **Done.** The false scope note is gone. New §2.5 works all three official task types end to end: partial/total function, injection and surjection counts; integer solutions with lower and upper bounds; homogeneous and non-homogeneous recurrences solved through their initial conditions and checked numerically. |
| 5 | Topic 3 missing path-decomposition task | **Done.** New §3.7 works all three task types on one concrete graph: BFS and DFS spanning trees with traces, a Hierholzer construction on \(K_5\) plus the negative answer via the odd-degree criterion, and the minimum edge-disjoint path decomposition with the \(\max(k,1)\) theorem, its lower-bound proof, the pairing construction, and a worked example. The Euler theorem now states its multigraph scope. |
| 6 | Topic 34 missing geometric illustrations | **Done.** Three TikZ figures (34.1–34.3) on one shared example, plus numeric iteration tables for each method. |
| 7 | Topics 14 and 16 terminology | **Done.** §14.6.5 adds “предаване по име”, distinguishes it from value and reference passing with two examples and a comparison table, and links to §19.3.2. §16.3.4 defines the nested class, contrasts it with composition in a table, and gives an example. |
| 8 | Selection notes not preserved | **Done.** The official selection notes for topics 6, 7, 8 and 18 appear in gold at the top of those chapters, with the “what may be drawn, not what may be skipped” reading spelled out. |
| 9 | Required vs supplementary mixed | **Done.** Every chapter opens with a “По конспекта: какво трябва да мога” panel naming each obligation by its required action. Supplementary material is marked before it starts in topics 4 (Kleene proof), 22 (completeness proof), 27 (extra styles), 33 (statement-only properties) and 35 (PGF proofs); prerequisite material is marked in topics 3, 4 and 30. |
| 10 | Topics 11/12 practice and sources | **Partly done.** §11.6 and §12.6 add complete C programs; the official bibliography is reproduced at the end of the book, so `[42]`, `[46]` and the rest now resolve. The patch task's repeated-offset interpretation is stated explicitly. The source-verification debt is unchanged and still disclosed. |
| 11 | Topic 29 contradictory phrase | **Done.** The revision bullet now says two non-parallel planes and points at §29.6.2. |

Beyond the findings, three changes were made that the audit did not ask for:

- The book's official bibliography (53 entries) is reproduced as a closing chapter, because
  finding 10 required the reference numbers to resolve and no list existed.
- `Ligatures=TeX` is now set on the text fonts. Without it fontspec had been printing
  ``` `` ''` ``` as literal backticks and `---` as three hyphens throughout the book; the 39
  TeX-style quotes in the bodies were converted to Bulgarian `„…“` at the same time.
- `xurl` is loaded so the one long bibliography URL breaks. The whole 498-page PDF now has
  zero lines protruding past the right margin.

### Second pass — review findings on the revision

Three defects were found in the revision itself and are now fixed.

| Reported | Disposition |
|---|---|
| Example 2.32 used \(\binom{6}{2}=6\); the answer 48 was wrong | **Fixed.** \(\binom{6}{2}=15\), so the count is \(66-3\cdot15=21\), which matches enumeration. The substitution step is now written out so the binomial cannot be misread. Every other numeric claim added in this revision was re-verified by machine afterwards: the surjection formula against \(n!\) and against \(m<n\), both recurrence closed forms against their recurrences, both stars-and-bars examples against enumeration, and Topic 3's degrees, BFS/DFS trees, \(K_5\) Euler circuit and path decomposition against the graph. Nothing else was wrong. |
| Opening panels had no links; dense entries needed splitting | **Fixed.** Every section and subsection in the book now carries a label (568 of them), and panel targets are `\ref`/`\pageref` links rather than typed numbers, so a section that moves cannot leave a panel pointing at the wrong place — and the build fails if a target disappears. The 35 opening pages now carry 277 internal links, each resolving to a real destination; Topic 34's entries link to the figures themselves. Dense entries were split to one obligation per line — Topic 1's single seven-group definition blob is now six lines. |
| Topic 12's program ignored `fwrite` failures and could exit 0 after losing output | **Fixed.** `fwrite`'s return is checked, `fflush`/`ferror` run before the exit code is decided, and success now requires both a zero child status and an intact output stream. Confirmed against a pre-fix build: with a read-only output descriptor the old program exits 0 silently, the new one exits 1 with a diagnostic. Both programs still compile clean under `-Wall -Wextra`. |

The whole 498-page PDF still has no line protruding past the right margin, and no `??` anywhere.

### Not resolved

- **Topic 11/12 source verification.** The primary literature is still absent from the corpus.
  Both chapters keep their status notes, and their opening panels repeat the caveat.
- **Topic 11 tasks 2 and 3** remain schemes rather than complete programs, and Topic 12's
  producer–consumer scheme likewise. Each is labelled as such rather than left implicit.
- **Topic 24** still has no worked 4NF example driven by a multivalued dependency; the panel
  records this as a gap rather than claiming coverage.

Correctness of the mathematics and of the added programs has not been independently
certified. A passing structural check is not a syllabus sign-off, and neither is this section.
