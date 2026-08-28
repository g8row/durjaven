# Round 2 focused independent review: questions 14–18

Scope: questions 14–18 only. I checked the chapter bodies against the mapped manifest and the local OCR/source material, with emphasis on C/C++ semantics, code behavior, complexity, recursion, OOP, and structure invariants. This is an independent pass; no prior review findings were used.

## Summary

| Question | Verdict |
|---|---|
| 14 | **Needs correction (P1)**: one materially false C++ language rule. Otherwise the control-flow, functions, parameters, and strings treatment is coherent. |
| 15 | **Needs correction (P2)**: pointer comparison is stated too broadly. Sorting/search code and recursion examples are otherwise correct under their stated preconditions. |
| 16 | **Pass**: class/object, construction/destruction, access, operators, RAII, and static members are presented accurately. |
| 17 | **Pass with a minor example hygiene issue (P2)**: polymorphism and virtual destruction are correctly explained; one allocation example leaks. |
| 18 | **Needs correction (P1)**: the doubly-linked-list insertion example can break the list's `last` invariant. The stack, queue, singly-linked-list, and BST algorithms otherwise preserve their stated invariants (subject to initialized inputs). |

## Findings

### Q14 — P1: omitted return type is not implicitly `int` in C++

Chapter lines [498–499](/Users/g8row/Documents/durjaven/topics/bodies/topic_14.tex:498) state that if a function's result type is omitted, C++ defaults it to `int`. A function declaration/definition in modern C++ requires an explicit decl-specifier (for example `int f()` or `void f()`); omitting it is ill-formed. The mapped source does contain the same legacy rule at `run/di/14/page_004.txt` (source page 4), but that does not make it valid C++.

Impact: a learner following the chapter will write code that fails to compile, and the chapter mischaracterizes a C-era implicit-int convention as C++ syntax.

Correction: replace the sentence with “В C++ резултатният тип трябва да бъде указан; при функция без резултат се използва `void`.” If historical context is desired, explicitly label implicit `int` as obsolete/ non-C++ legacy behavior.

### Q15 — P2: relational pointer comparisons are qualified incorrectly

Chapter lines [53–60](/Users/g8row/Documents/durjaven/topics/bodies/topic_15.tex:53) list `<`, `>`, `<=`, and `>=` as generally available pointer comparison operations, with no qualification. The mapped source gives the same unqualified list at `run/di/15/page_001.txt` (source page 1), but in C++ relational comparison is meaningfully defined for pointers into the same array object (and the relevant one-past position); for unrelated objects the result is unspecified/implementation-dependent, not a portable ordering. Equality has different rules.

Impact: readers may sort or order unrelated object pointers and assume a portable result, producing non-portable code. This is a correctness/documentation defect, not an issue with the array-indexing equivalences in lines 176–194.

Correction: say that `==`/`!=` test pointer equality, while relational comparisons are portable for positions within the same array (including one-past); do not use `<`/`>` to order pointers to unrelated objects (use `std::less<T*>` when an implementation-provided strict ordering is required).

### Q17 — P2: polymorphism example leaks three dynamic objects

Chapter lines [81–89](/Users/g8row/Documents/durjaven/topics/bodies/topic_17.tex:81) allocate `new Dog`, `new Cat`, and `new Animal` into `a1`, `a2`, and `a3`, then only demonstrate calls; no corresponding `delete` is shown. The mapped source shows the same allocation example at `run/ocr/temi_17__oxalpha/page_001.json` (source page 1). The chapter correctly explains the need for cleanup and a virtual base destructor at lines [132–154](/Users/g8row/Documents/durjaven/topics/bodies/topic_17.tex:132), but that later warning does not make this complete example leak-free.

Impact: running the snippet leaks all three allocations. It is a minor teaching-code defect because the example is explicitly about dispatch, but learners may copy it.

Correction: either use automatic objects plus pointers/references where possible, or add `delete a1; delete a2; delete a3;` after the calls (with a virtual destructor in `Animal`), preferably demonstrate `std::unique_ptr<Animal>`.

### Q18 — P1: `insertAfter` does not maintain the list's `last` pointer

Chapter lines [398–418](/Users/g8row/Documents/durjaven/topics/bodies/topic_18.tex:398) describe a doubly-linked list that “usually” keeps both beginning and end pointers, then provide `insertAfter(DLListItem* current, int value)`. When `current` is the tail (`current->next == nullptr`), lines [408–417] correctly link the new node but have no access to, or update of, the owning list's `last` field. The mapped source identifies the current-element pointer as assisting insertion/deletion/search at `run/ocr/temi_18__oxalpha/page_003.json` (source page 3); the chapter's own list invariant/representation is in lines [386–400].

Impact: after inserting after the tail, `last` still points to the old tail. A subsequent `insertLast`, tail deletion, or traversal starting from `last` can lose the new node or corrupt links. This is a concrete data-structure invariant failure.

Correction: pass `List& list` (and `current`) to `insertAfter`, and set `list.last = item` when `current->next` was null; alternatively explicitly state that the routine is for a node-only representation and provide a separate owner-aware tail update. Add a postcondition that `first`/`last` and both `next`/`prev` links remain consistent.

## Additional checks

- Q14 `if`/`switch`, loop ordering, `break`/`continue`, function calls/returns, references, and string-buffer preconditions are internally consistent; no additional P0–P2 issue found.
- Q15 selection, bubble, insertion, quick, merge, linear, and binary-search code is correct for valid non-null buffers and valid ranges. `merge` assumes `tmp` has room for the merged interval; that precondition should be understood but is conventional for the shown helper.
- Q16 constructor syntax, copy construction, destructor/resource discussion, operator restrictions, and static members are sound. The constructor correction already present in lines [150–152] is technically right.
- Q17 the `virtual`/`override`, abstract-class, slicing, template, multiple-inheritance, and virtual-inheritance explanations are sound. The chapter correctly limits the “virtual destructor” requirement to deletion through a base pointer.
- Q18 array-stack bounds checks, linked-stack cleanup, circular-array queue indices, linked-queue empty-state updates, singly-linked-list first/last updates, tree traversals, and BST deletion (including successor removal) are correct for initialized valid structures. BST `O(log n)` claims are appropriately conditioned on logarithmic height.
