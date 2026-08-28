# Round 02 — independent review: questions 23–27

Scope: independent review of `topics/bodies/topic_23.tex` through
`topic_27.tex` against `topics/manifest.json` and the mapped local evidence.
The mapped primary evidence is `run/ocr/temi_23__production` through
`run/ocr/temi_27__production`; Q25 also maps `sources/di/Задачи/AI.txt`, Q26
maps `sources/di/ST.pdf`, and Q27 maps `sources/di/SA.pdf` and
`sources/di/SA-SI.pdf`. No chapter files were edited.

## Q23 — Relational databases and the relational model

**Verdict: P2 — essentially correct, with one algebraic-notation clarification needed.**

### P2 — Cartesian-product commutativity is qualified too vaguely

- **Chapter:** `topics/bodies/topic_23.tex:337-355`, especially line 355.
- **Evidence:** The mapped note calls Cartesian product “бинарна, асоц, комут” and says its result schema is the union of the schemas in `sources/di/23.pdf`, p. 4 (OCR: `run/ocr/temi_23__production/page_004.json`).
- **Impact:** With ordered tuple/schema conventions, `R×S` and `S×R` have components in different positions (and potentially different qualified attribute order), so literal equality is not true without an explicit isomorphism/reordering. “According to the ordering” is not a definition of that equivalence and can confuse an examinee about typed relational expressions.
- **Correction:** Say that Cartesian product is commutative up to the canonical reordering/isomorphism of attributes (or state the convention that schemas are treated as unordered for this property), and distinguish that from literal equality of ordered tuples.

The definitions of relation/schema/instance, DDL and DML, core algebra operators, selection/projection, joins, renaming, and operator priority are otherwise faithful and technically sound. The source’s `COMMIT` wording is reproduced as mapped material, with no separate finding here.

## Q24 — Normal forms

**Verdict: P2 — the normalization treatment is strong, but one source label remains misleading despite an ensuing correction note.**

### P2 — “lossless join” is initially defined as dependency preservation

- **Chapter:** `topics/bodies/topic_24.tex:445-465`, especially lines 451-454.
- **Evidence:** The mapped source itself labels the condition `F_1 ∪ F_2 = F` as “без загуба на функ. зависимости” in `sources/di/24.pdf`, p. 5 (`run/ocr/temi_24__production/page_005.json`).
- **Impact:** The chapter introduces this under the heading “Съединение без загуба” and says “съединението ... е без загуба на функционални зависимости,” which can still be read as defining lossless join. Dependency preservation (`F_1∪F_2=F`) is not the lossless-join condition; lossless join concerns equality of the natural join of projections with the original relation. The subsequent `supp` note correctly distinguishes them, but the preceding claim remains internally misleading for an oral answer.
- **Correction:** Rename the subsection/claim at lines 451-454 to “запазване на функционалните зависимости,” reserve “съединение без загуба” for the projection/join property, and retain the explanatory note.

The definitions and examples for anomalies, keys/superkeys, FD/Armstrong rules, 1NF–BCNF, MVD/4NF, and the normalization example are otherwise correct and cover the mapped material.

## Q25 — State-space search, genetic algorithms, CSP and games

**Verdict: Pass.**

The state/operator/goal definitions, graph-versus-search-tree distinction, completeness/complexity/optimality criteria, uninformed and informed search, beam search and hill climbing, genetic-algorithm stages/operators, CSP backtracking/propagation/min-conflicts, and minimax/alpha–beta material are consistent with `sources/di/25.pdf` (pp. 1–5), `run/ocr/temi_25__production/page_001.json` through `page_005.json`, and the mapped `sources/di/Задачи/AI.txt`. No independent P0–P2 finding.

## Q26 — Contemporary software technologies

**Verdict: Pass.**

The software product/process definitions, lifecycle models, agile/XP/SCRUM distinctions, requirements, UML, verification/validation, testing categories, and quality-management coverage are faithful to `sources/di/26.pdf` and `sources/di/ST.pdf`, including the mapped production OCR (`run/ocr/temi_26__production/page_001.json` through `page_004.json` and `run/ocr/di_ST__production`). No independent P0–P2 finding.

## Q27 — Software-system architectures

**Verdict: P1 — one terminology error in the event/connector styles; otherwise broadly faithful.**

### P1 — producer–consumer is incorrectly presented as a synonym of implicit invocation

- **Chapter:** `topics/bodies/topic_27.tex:250-256`, especially line 254.
- **Evidence:** The mapped architecture note describes implicit invocation through events and event notification, but does not equate it with producer–consumer; see `sources/di/SA.pdf`, p. 2 (`run/ocr/temi_27__production/page_002.json`).
- **Impact:** Publish–subscribe and producer–consumer are distinct messaging patterns: publish–subscribe commonly broadcasts an event to multiple subscribers, whereas producer–consumer coordinates producers and consumers through a queue/buffer, usually with each item consumed by one consumer. Calling both synonyms of implicit invocation erases this distinction and can produce a materially wrong architecture-style answer.
- **Correction:** Retain implicit invocation/event-based architecture as the general style; mention publish–subscribe as one event-notification variant and producer–consumer as a separate queue-based coordination pattern (which may be implemented using implicit invocation), not as a synonym.

The architecture definition and views/structures, components/connectors, layered/MVC/Pipe-and-Filter/client–server/shared-data styles, service/microservice discussion, ADD, ATAM/CBAM, quality tactics, and documentation elements otherwise align with `sources/di/SA.pdf`, `sources/di/SA-SI.pdf`, and `run/ocr/temi_27__production/page_001.json` through `page_004.json`.
