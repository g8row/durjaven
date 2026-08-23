# The corpus — what is here and what the book will contain

Source material for the **Държавен изпит** notes — the ФМИ bachelor's state
exam in Компютърни науки: 365 PDF pages and 165 photographs against a 35-question
syllabus that runs from axiomatic set theory to Poisson distributions by way of
OSI layers, Dijkstra, C++ polymorphism and Scheme streams.

Everything below was measured from the files, not assumed. The official
конспект (`sources/konspekt/`, ФС протокол № 6/30.06.2025) is the authority on
what the book must contain; where a source disagrees with it, or the sources
disagree with each other, that is recorded rather than resolved.

---

## 1. Inventory

### `sources/di/` — 39 PDFs, 365 pages

| Class | Files | Pages | Text layer | What it is |
|---|---|---|---|---|
| **A** Word export | 26 numbered PDFs | 106 | prose yes, **maths broken** | the main body of notes |
| **A′** Word export, no maths | `SA-SI.pdf` | 12 | full | software-architecture prose |
| **B** Word export, flattened | `4.pdf`, `32.pdf` | 12 | none | same typesetting, saved as page images |
| **D** LaTeX, cp1251 | `Задачи/1`, `Задачи/2` | 33 | mojibake, trivially fixed | the only professionally typeset sources |
| **E** handwritten scans | `Logichesko`, `logichesko1/2`, `SA`, `ST`, `oop2` | 202 | none | notebooks, photographed or scanned |

### `sources/temi/` — 157 photographs, 30 folders

Loose A4 sheets, one folder per topic, 2–11 shots each, 4624×2604 or
2604×3646. Blue ballpoint in a small, consistent, very legible hand. Each
topic's first sheet carries its number in a circle — ①, ⑭, ㉟ — which is what
makes the numbering audit in §3 possible at all.

### `sources/konspekt/` — the syllabus, 19 pages

The official конспект: 35 questions in three sections, and for each an
annotation naming the required definitions, theorems and proofs, sample
problems, and literature references. Parsed to `docs/konspekt_annotations.json`.
This is the spine of the book and the checklist every chapter is audited
against — it is the difference between "covers the topic" and "covers the
question as set".

### Loose files

`Задачи/AI.txt` (6.2 KB) tabulates the search algorithms — DFS, BFS, UCS, A\*,
with node-selection rule, evaluation function and the path each finds.
`Задачи/FP.txt` (9.1 KB) is a reference of the R5RS Scheme functions the course
uses, with worked examples of `eq?` / `eqv?` / `equal?` and the higher-order
functions. Both are clean prose and belong in appendices, not chapters.
Eight further loose images (`oop2/*.jfif`, `Задачи/*.webp`) are photographs
duplicating material already in the PDFs.

---

## 2. The four difficulty tiers

The tiers are not editorial judgements — they are how the text has to be got
off the page, and they drive the whole extraction plan.

### Tier A — the maths is there but invisible (106 pages, easiest)

The numbered PDFs are Word documents exported to PDF. Prose extracts perfectly.
Every OMML equation, however, is set in a subsetted Cambria Math whose
`ToUnicode` CMap covers only the Cyrillic runs, so **every formula extracts as a
run of spaces** while looking perfect on screen. A naive pipeline would produce
a book with the mathematics silently deleted.

It is recoverable without a model, and `scripts/extract_math.py` does it — see
[PLAN.md](PLAN.md) §2. Measured across the corpus: **6,029 equation runs,
35,192 glyphs, 79% decoded to exact Unicode**, the remainder being font variant
glyphs handled by a one-off lookup table.

### Tier B — clean but flattened (12 pages, easy)

`4.pdf` (Крайни автомати, 8 pp) and `32.pdf` (Уравнения за права и равнина,
4 pp) are the same Word typesetting saved as page images. No text layer at all,
but the rendering is pristine, so a vision model reads them at near-typeset
accuracy. `32.pdf` overlaps the LaTeX `Задачи` documents, which gives a free
cross-check.

### Tier C — handwritten, good conditions (183 pages + 157 photos, moderate)

The `sources/temi/` photographs and `Logichesko.pdf` (158 pp). Neat hand, good
contrast, mostly even lighting. `Logichesko` is a grayscale scan of ruled paper
— thin strokes, faint ruling that competes with the ink, and it is by a wide
margin the largest single source in the corpus. The photographs split further:
roughly half are shot on white or pale backgrounds and are genuinely easy; the
rest sit on a dark wooden desk with the reverse side of the sheet showing
through, and need the divide-out-the-background preprocessing that
`scripts/ocr_pages.py` already implements.

### Tier D — handwritten, hostile conditions (24 pages, hard)

`SA.pdf` and `ST.pdf` (6 pp each) are phone photographs of a squared-paper
notebook held open on a sofa: dense small cursive filling every line, keystone
perspective, the facing page intruding, ink from the reverse showing through,
and a thumb in frame. `oop2.pdf` (6 pp) is easier writing but contains C++ that
must come out as verbatim code, not as prose — a different failure mode, since a
model that "tidies" `a1->talk()` has destroyed the content.

---

## 3. Topic numbering — the конспект is the spine

`sources/konspekt/Konspekt_DI_KN-30.06.2025.pdf` is the official syllabus
(ФС протокол № 6/30.06.2025): 35 questions in three sections, each with a
detailed annotation naming the definitions, theorems and proofs required, plus
sample problems and literature references. **Chapter N of the book is question N
of that document.** No source file's own numbering is authoritative.

That matters, because **neither source set follows the current numbering**. Both
appear to follow the previous revision (протокол № 2/24.02.2025), in which the
analytic-geometry questions sat at the end of the mathematics block rather than
the front. The June 2025 revision rotated that block:

| Old | New | Question |
|---|---|---|
| 32, 33 | **28, 29** | права в равнината / права и равнина в пространството |
| 28, 29, 30, 31 | **30, 31, 32, 33** | симетрични оператори / симетрична група / средни стойности / определен интеграл |
| 34, 35 | 34, 35 | unchanged |

That one rotation accounts for every discrepancy in topics 28–35, including the
"off by one at 33" that a filename-only comparison appears to show, and the fact
that `32.pdf` contains two of the current questions in a single file.

The PDFs additionally **lag on topics 6 and 8**, where they still carry the
questions those numbers held before February 2025:

- Question 6 is now *Сортиране чрез сравнения във време O(n lg n)* — binary
  heap, Heapify, HEAPSORT, MERGESORT. The photographs (⑥ двоична пирамида) are
  correct; `6.pdf` holds *модели на изчисленията* and is **stale**.
- Question 8 is now *Най-къси пътища в тегловни графи* — Дийкстра and the DAG
  algorithm. `8.pdf` holds *динамично програмиране* and does not match; the
  eleven photographs in ⑧ are the source.

So neither set is uniformly newer, and the mapping has to be made per topic. It
is recorded in `topics/manifest.json` with a confidence field and, where a
source only partly satisfies its annotation, a note saying so. **No stage may
pair a photograph with a PDF by filename.**

---

## 4. Coverage against the official annotations

| Coverage | Questions | Count |
|---|---|---|
| PDF **and** photographs | 1–5, 7, 14–16, 19, 20, 23–35 | 24 |
| PDF only (no photographs exist for 9–13) | 9, 10, 13 | 3 |
| Photographs only | 6, 8, 17, 18, 21, 22 | 6 |
| Backed additionally by a named PDF | 21, 22 (`Logichesko`), 26 (`ST`), 27 (`SA`, `SA-SI`), 16–17 (`oop2`) | — |
| **No source at all** | **11, 12** | **2** |

**Questions 11 and 12 — файлова система, and управление на процеси и
междупроцесни комуникации — have no source in this material at all.** Their
annotations are substantial (Linux file-system internals: mount points, inodes,
i-node tables; process primitives, fork/exec/wait, process groups, sessions,
IPC). No numbered PDF, no photograph folder, no named PDF covers them. They must
be sourced separately or shipped as a declared gap; the book must not invent
them.

Four further topics have a source that only *partly* satisfies its annotation,
which is a coverage gap rather than a sourcing one, and is flagged in the
manifest: question 2 (the sources cover the counting principles but recurrence
relations are not evident), 31 (Sn and cycles present; alternating group, Cayley
and the homomorphism theorem to be confirmed), 32 (`30.pdf` opens on Вайерщрас,
which the annotation does not name — the weakest link in the map) and 35 (the
source defines random variables generally; the annotation is specifically about
the three discrete distributions and generating functions).

Two PDFs are left over: `6.pdf` and `8.pdf`, both superseded questions. They are
good material about real topics and can be kept as appendices, but they answer
nothing on the current exam.

---

## 5. What the book will contain

Thirty-five chapters in the конспект's own three sections, plus appendices.
Titles are the official ones. Sources are as mapped in `topics/manifest.json`.

### ОСНОВИ НА КОМПЮТЪРНИТЕ НАУКИ

| # | Question | Sources |
|---|---|---|
| 1 | Множества. Декартово произведение. Релации. Функции | `1.pdf` + ① |
| 2 | Основни комбинаторни принципи и конфигурации. Рекурентни уравнения | `2.pdf` + ② ⚠ recurrences |
| 3 | Графи. Дървета. Обхождания на графи | `3.pdf` + ③ |
| 4 | Характеризация на регулярните езици. Теорема на Майхил-Нероуд | `4.pdf` + ④ |
| 5 | Лема за разрастването за КС езици. Незатвореност | `5.pdf` + ⑤ |
| 6 | Сортиране чрез сравнения във време O(n lg n) | ⑥ only — `6.pdf` is stale |
| 7 | Минимални покриващи дървета | `7.pdf` + ⑦ |
| 8 | Най-къси пътища в тегловни графи | ⑧ only — `8.pdf` is stale |

### ЯДРО НА КОМПЮТЪРНИТЕ НАУКИ

| # | Question | Sources |
|---|---|---|
| 9 | Компютърни архитектури. Централен процесор | `9.pdf` |
| 10 | Структура и йерархия на паметта. Преадресация. Прекъсвания | `10.pdf` |
| 11 | Файлова система. Функции, структура и реализация | **— none —** |
| 12 | Управление на процеси и междупроцесни комуникации | **— none —** |
| 13 | Компютърни мрежи и протоколи. OSI. IPv4, IPv6, TCP, DNS | `13.pdf` |
| 14 | Процедурно програмиране – основни конструкции | `14.pdf` + ⑭ |
| 15 | Процедурно програмиране – указатели, масиви, рекурсия | `15.pdf` + ⑮ |
| 16 | ООП. Класове и обекти. Наследяване и капсулация | `16.pdf` + ⑯ + `oop2` |
| 17 | ООП. Подтипов и параметричен полиморфизъм | ⑰ + `oop2` |
| 18 | Структури от данни. Стек, опашка, списък, дърво | ⑱ |
| 19 | ФП. Модели на оценяване. Функции от по-висок ред | `19.pdf` + ⑲ + `FP.txt` |
| 20 | ФП. Списъци. Потоци и отложено оценяване | `20.pdf` + ⑳ + `FP.txt` |
| 21 | Синтаксис и семантика на предикатното смятане от първи ред | ㉑ + `Logichesko` |
| 22 | Изводимост и компютърно генериране на доказателства | ㉒ + `Logichesko` |
| 23 | Бази от данни. Релационен модел | `23.pdf` + ㉓ |
| 24 | Бази от данни. Нормални форми | `24.pdf` + ㉔ |
| 25 | Изкуствен интелект. Пространство на състоянията | `25.pdf` + ㉕ + `AI.txt` |
| 26 | Съвременни софтуерни технологии | `26.pdf` + ㉖ + `ST.pdf` |
| 27 | Архитектури на софтуерни системи | `27.pdf` + ㉗ + `SA`, `SA-SI` |

### МАТЕМАТИКА И ПРИЛОЖЕНИЯ

The block whose numbering the sources predate — see §3.

| # | Question | Sources |
|---|---|---|
| 28 | Уравнения на права в равнината | `32.pdf` (½) + ㉜ + `Задачи/1` |
| 29 | Уравнения на права и равнина в пространството | `32.pdf` (½) + ㉝ + `Задачи/2` |
| 30 | Симетрични оператори. Теорема за диагонализация | `28.pdf` + ㉘ |
| 31 | Симетрична и алтернативна група. Теорема на Кейли | `29.pdf` + ㉙ ⚠ partial |
| 32 | Теорема на Ферма. Рол, Лагранж, Коши. Формула на Тейлър | `30.pdf` + ㉚ ⚠ verify |
| 33 | Определен интеграл. Дарбу. Нютон-Лайбниц | `31.pdf` + ㉛ |
| 34 | Итерационни методи за нелинейни уравнения | `33.pdf` + ㉞ |
| 35 | Случайни величини с дискретни разпределения | `34.pdf` + ㉟ ⚠ partial |

⚠ marks a source that only partly satisfies its annotation.

### Appendices

**А — Функции от курса по ФП.** The Scheme reference from `FP.txt`: type
predicates, the three equality relations, higher-order functions, with the
worked examples that make `eq?` versus `eqv?` versus `equal?` stick.

**Б — Алгоритми за търсене.** The comparison table from `AI.txt`: DFS, BFS,
UCS, A\* and the rest, each with its data structure, evaluation function and
the path it finds on the shared worked example.

**В — Примерни задачи.** The конспект gives sample problems under most
questions; collected, they make a practice set that maps one-to-one onto the
chapters.

**Г — Извън конспекта.** `6.pdf` (модели на изчисленията) and `8.pdf`
(динамично програмиране), superseded questions kept because they are good
material — clearly marked as not examinable.

---

## 6. Expected shape of the finished book

Extrapolating from the source density and from what the same treatment produced
for the statistics book (172 pages from 15 lectures):

- **220–280 pages**, 35 chapters, two appendices
- heavily front-loaded toward Parts I–III and X, which carry nearly all the
  numbered mathematical statements
- Parts IV, VI–IX are prose and diagrams — definitions and enumerated
  properties rather than theorems and proofs, so they need the same numbered
  environments but far fewer of them
- roughly 25–40 TikZ figures: automata, graphs, heaps, OSI layers, the geometry
  of Part XI, and the search trees of Приложение Б
- code listings in Parts V and VI need `listings`, not maths mode — an addition
  to the inherited preamble
