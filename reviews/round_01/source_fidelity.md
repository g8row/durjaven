# Round 01 — source-fidelity review

Scope: independent comparison of the 35 chapter bodies with the authoritative local notes.  The numbering follows `topics/manifest.json`; in particular, topics 28–29 use source 32, 30 uses 28, 31 uses 29, 32 uses 30, 33 uses 31, 34 uses 33, and 35 uses 34.  Source citations below are local paths and page numbers (the `run/di` text is page-separated; OCR production paths are cited where the source is photographic).  This review does not use web sources and does not modify chapters.

## Findings

### P1 — invalid pointer-arithmetic example is presented as valid C++

`topics/bodies/topic_15.tex:82-89` defines `int x`, `int* p = &x`, then shows `int* const q = p; q = p + 2; // грешка`.  Pointer arithmetic on a pointer to a standalone scalar is not a valid array object/one-past calculation; `p+2` has undefined behavior even before any dereference.  The mapped source discusses pointer/constant forms but does not supply this example (`run/di/15/page_001.txt`, source section “Указатели и константи”; corroborating photographic OCR: `run/ocr/temi_15__production/page_*.json`).  Replace with an actual array example (or only demonstrate that reassignment of `q` is ill-formed).  This is a book-level code error, although the surrounding conceptual coverage is faithful.

### P2 — Fibonacci base case silently changes the supplied example

`topics/bodies/topic_15.tex:434-440` uses `fib(0)==1` and `fib(1)==1`.  The mapped source's standard Fibonacci example is present in `run/di/15/page_005.txt` (and the corresponding `temi_15` production OCR); the source convention should be checked and stated explicitly because the chapter's recurrence then has a shifted sequence relative to the usual `F(0)=0,F(1)=1`.  This is not necessarily mathematically wrong, but it is an unmarked strengthening/variant of the notes.  Add the convention or use the source's bases.

### P2 — topic 13 narrows a source claim without flagging the omission

The source's OSI transport description includes “broadcasting” among possible services (`run/di/13/page_001.txt`, p. 1).  The chapter's transport section (`topics/bodies/topic_13.tex:43-64`) covers segmentation, reliability and end-to-end operation but omits that source example.  This is a minor fidelity omission, not a contradiction: the later IPv6 statement that there is no IPv6 broadcast (`:206`) concerns IPv6 addressing, not the generic OSI transport note.  Add a short qualification if complete note fidelity is required.

### P2 — source-derived complexity contradictions are disclosed but remain exam-facing

The chapter correctly identifies the supplied notes' inconsistent claims: factorial is labelled `n log n` in the notes while the shown recursion is linear (`topics/bodies/topic_15.tex:412-428`; `run/di/15/page_005.txt`, p. 5), and the notes give `foldl (-) 0 '(1 2 3)` as 2 while the displayed left fold evaluates to −6 (`topics/bodies/topic_20.tex:520-533`; `run/di/20/page_003.txt`, p. 3).  Likewise, topic 18 preserves and qualifies the notes' `O(n)`/`O(log n)` tree-operation mismatch (`topics/bodies/topic_18.tex:534-536,571,597,661`; `run/di/18/page_*.txt`).  These are faithful caveats, not new errors, but the exam-focus lists should explicitly say “source contains an erroneous/conditional complexity value” so a reader cannot memorize the unqualified source value.

### P3 — added implementation detail is not always source-labelled

The chapters add useful textbook material beyond the terse notes (for example, `topics/bodies/topic_23.tex:121-180` gives concrete SQL DDL/DML and `:539-541` deliberately declines to invent trigger syntax; `topics/bodies/topic_27.tex:320-376` expands quality tactics).  This is acceptable enrichment, but because the project asks for fidelity, additions should be marked as explanatory examples rather than implied quotations from the notes.  No fabricated trigger syntax or misattributed external source was found.

## Focused audit: programming and systems (9–20, 23–27)

* **9:** All source pillars are represented: von Neumann components, signed/two's-complement and BCD formats, floating-point sign/exponent/mantissa, coding tables, registers/ALU/control/instructions, instruction cycle, interrupts and pipeline (`topics/bodies/topic_09.tex:3-410`; `run/di/9/page_001.txt`–`page_004.txt`).  The 32-bit layout and FPU wording are explanatory elaborations of the source's float page (`run/di/9/page_002.txt`), not misattributed claims.
* **10:** Cache hierarchy/locality, RAM, paging and FIFO, segmentation/GDT/LDT, interrupt vectors/priorities/controller and their composition are covered (`topics/bodies/topic_10.tex:1-344`; `run/di/10/page_001.txt`–`page_004.txt`).  The chapter explicitly flags the source's “статична” heading as contentually paging (`:134-136`), which is the correct fidelity treatment.
* **11–12:** Explicit, intentional gaps are preserved.  Both placeholders state no source exists and reproduce only the syllabus annotation (`topics/bodies/topic_11.tex:3-11`, `topic_12.tex:3-11`; `topics/manifest.json` confidence `gap`).
* **13:** OSI seven layers, TCP/IP comparison, distance-vector/link-state routing, IPv4 class/CIDR, IPv6, TCP handshake, DNS resolver/cache/A and AAAA are covered (`topics/bodies/topic_13.tex:3-289`; `run/di/13/page_001.txt`–`page_005.txt`).  One minor omission is the generic transport “broadcasting” example noted above.
* **14:** Control flow, `main`, conditionals, loops, variables/scope, functions/stack/parameters and C strings/cstring are all present (`topics/bodies/topic_14.tex:1-769`; `run/di/14/page_001.txt`–`page_005.txt`).  No source-number mix-up found.
* **15:** Pointers, arrays, pointer arithmetic, string literals, five sorts, searches and linear/branching recursion are all covered (`topics/bodies/topic_15.tex:3-519`; `run/di/15/page_001.txt`–`page_006.txt`).  The invalid scalar `p+2` example and unmarked Fibonacci convention are the only material concerns.
* **16:** Classes/objects, access, constructors/destructors/resources, methods/`this`, operators/static members, inheritance, subtype relation, encapsulation and polymorphism are covered (`topics/bodies/topic_16.tex:3-491`; `run/di/16/page_001.txt`–`page_005.txt`; extra `run/ocr/di_oop2_oop2__production/page_*.json`).
* **17:** Subtype/dynamic dispatch, virtual functions/vtable, abstract classes, object arrays/pointers, templates, multiple inheritance, diamond and virtual inheritance are covered (`topics/bodies/topic_17.tex:3-425`; photographic `run/ocr/temi_17__production/page_*.json`; extra `run/ocr/di_oop2_oop2__production/page_*.json`).  The non-virtual dispatch example is faithful to the note's teaching point; its allocated `new Derived()` is a pedagogical leak, not a source-fidelity omission.
* **18:** Stack, queue, singly/doubly linked lists, binary trees and BST operations/representations are covered (`topics/bodies/topic_18.tex:1-695`; `run/ocr/temi_18__production/page_*.json`).  Complexity caveats are unusually careful and preserve source ambiguity.
* **19:** Scheme expressions/evaluation, applicative vs normal evaluation, higher-order functions, currying, lambdas and returned functions are covered (`topics/bodies/topic_19.tex:1-526`; `run/di/19/page_001.txt`–`page_004.txt`; extra `sources/di/Задачи/FP.txt`).  The `1+` result discrepancy is explicitly called out (`:500-510`), so no misattribution remains.
* **20:** Scheme/Haskell lists, `cons/car/cdr`, map/filter/folds, streams, delay/force, infinite streams and Haskell laziness are covered (`topics/bodies/topic_20.tex:1-787`; `run/di/20/page_001.txt`–`page_005.txt`; `sources/di/Задачи/FP.txt`).  The foldl arithmetic correction is explicitly disclosed.
* **23:** Relational model, schema/instance, DDL/DML, SQL, all listed relational-algebra operators, priorities, examples and triggers are covered (`topics/bodies/topic_23.tex:1-571`; `run/di/23/page_001.txt`–`page_004.txt`).  Trigger syntax is correctly withheld because the source gives no concrete syntax (`:539-541`).
* **24:** Anomalies, keys/constraints, FDs, Armstrong axioms, 1NF/2NF/3NF/BCNF, MVD/4NF, lossless join and normalization procedure/example are covered (`topics/bodies/topic_24.tex:1-567`; `run/di/24/page_001.txt`–`page_003.txt`).
* **25:** State-space definitions, strategy metrics, blind/informed/local search, two-player minimax-style choice, genetic algorithms and CSP material are covered (`topics/bodies/topic_25.tex:1-411`; `run/di/25/page_001.txt`–`page_004.txt`; extra `sources/di/Задачи/AI.txt`).
* **26:** Product/process, project/resources, lifecycle models, XP/Scrum, requirements, analysis/design, UML, V&V, testing and quality management are covered (`topics/bodies/topic_26.tex:1-322`; `run/di/26/page_001.txt`–`page_004.txt`; extra `run/ocr/di_ST__production/page_*.json`).
* **27:** Architecture definition/structures, quality scenarios, components/connectors, styles, service architecture, design process, quality tactics and documentation are covered (`topics/bodies/topic_27.tex:1-446`; `run/di/27/page_001.txt`–`page_003.txt`; extra `run/ocr/di_SA__production/page_*.json`, `run/di/SA-SI/page_*.txt`).

## 35-topic coverage matrix

Status means coverage of the manifest title and supplied notes: **Full** = core points present; **Full*** = full with a documented source ambiguity/qualification; **Gap** = intentionally no source/chapter content; **Minor** = small omission or variant recorded above.

| # | Manifest topic (short) | Source anchor | Status |
|---:|---|---|---|
| 1 | Sets, products, relations, functions | `run/ocr/temi_01__production/page_*.json` | Full |
| 2 | Combinatorics, configurations, recurrences | `run/di/2/page_001.txt`–`005.txt` | Full |
| 3 | Graphs, trees, traversals | `run/di/3/page_001.txt`–`004.txt` | Full |
| 4 | Regular languages, Myhill–Nerode | `run/ocr/di_4__production/page_*.json` | Full |
| 5 | CFL pumping/non-closure | `run/di/5/page_001.txt`–`005.txt` | Full |
| 6 | Comparison sorting, heapsort | `run/ocr/temi_06__production/page_006.json`–`007.json` | Full |
| 7 | Minimum spanning trees | `run/di/7/page_001.txt`–`004.txt` | Full |
| 8 | Weighted shortest paths | `run/ocr/temi_08__production/page_*.json` | Full |
| 9 | Architecture, data formats, CPU | `run/di/9/page_001.txt`–`004.txt` | Full |
| 10 | Memory, paging/segmentation, interrupts | `run/di/10/page_001.txt`–`004.txt` | Full* |
| 11 | File system | manifest gap; `topic_11.tex:3-11` | Gap |
| 12 | Processes and IPC | manifest gap; `topic_12.tex:3-11` | Gap |
| 13 | Networks and protocols | `run/di/13/page_001.txt`–`005.txt` | Minor |
| 14 | Procedural constructs | `run/di/14/page_001.txt`–`005.txt` | Full |
| 15 | Pointers, arrays, recursion | `run/di/15/page_001.txt`–`006.txt` | Minor |
| 16 | OOP basics/inheritance | `run/di/16/page_001.txt`–`005.txt`; oop2 | Full |
| 17 | Polymorphism/multiple inheritance | temi17 production; oop2 | Full |
| 18 | Stack, queue, list, tree | temi18 production | Full* |
| 19 | FP evaluation/higher-order functions | `run/di/19/page_001.txt`–`004.txt`; FP.txt | Full* |
| 20 | FP lists/streams/laziness | `run/di/20/page_001.txt`–`005.txt`; FP.txt | Full* |
| 21 | First-order predicate syntax/semantics | temi21 production; logic extras | Full |
| 22 | Derivability/proof generation | temi22 production; logic extras | Full |
| 23 | Relational model/operations | `run/di/23/page_001.txt`–`004.txt` | Full |
| 24 | Normal forms | `run/di/24/page_001.txt`–`003.txt` | Full |
| 25 | State-space AI/genetic algorithms | `run/di/25/page_001.txt`–`004.txt`; AI.txt | Full |
| 26 | Modern software technologies | `run/di/26/page_001.txt`–`004.txt`; ST | Full |
| 27 | Software architectures | `run/di/27/page_001.txt`–`003.txt`; SA/SA-SI | Full |
| 28 | Lines in the plane | `run/ocr/di_32__production/page_*.json`; line exercise PDF | Full |
| 29 | Lines/planes in space | same source 32; plane exercise PDF | Full |
| 30 | Symmetric operators/diagonalization | `run/di/28/page_001.txt`–`002.txt` | Full |
| 31 | Symmetric/alternating groups, Cayley, homomorphisms | `run/di/29/page_001.txt`–`005.txt` | Full |
| 32 | Fermat/MVT/Taylor | `run/di/30/page_001.txt`–`003.txt` | Full |
| 33 | Darboux/Riemann/Newton–Leibniz | `run/di/31/page_001.txt`–`004.txt` | Full |
| 34 | Nonlinear iteration methods | `run/di/33/page_001.txt`–`003.txt` | Full |
| 35 | Discrete binomial/geometric/Poisson | `run/di/34/page_001.txt`–`004.txt` | Full |

## Limitations

The supplied PDF transcripts are noisy OCR (especially formulas and photographed topics), so page-level text is authoritative for prose but not always for glyph-level equations.  I did not treat general mathematical correctness as a separate external review; where the chapter itself identifies a corrupted source formula, I checked the displayed derivation and recorded the discrepancy.  Photographic topics without a `run/di` transcript were checked against available `__production` OCR paths and the chapter's explicit source notes.  No source exists for 11 or 12, so fidelity there can only be assessed against the manifest annotation, which the placeholders preserve.
