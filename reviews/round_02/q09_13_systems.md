# Round 2 independent review — questions 9–13 (systems)

Scope: independent review of `topics/bodies/topic_09.tex`–`topic_13.tex`, checked against `topics/manifest.json` and the mapped OCR/DI evidence. No chapter edits made.

## Verdicts

| Question | Verdict |
|---|---|
| 9 | **Accept with minor correction.** Broad coverage and ordering match `sources/di/9.pdf` / `run/di/9/page_001.txt`–`page_004.txt`; one architecture wording issue below. |
| 10 | **Accept with correction.** Coverage is faithful to `sources/di/10.pdf` / `run/di/10/page_001.txt`–`page_004.txt`; the segment-boundary test should be corrected. |
| 11 | **GAP (correctly declared).** `topics/manifest.json` marks topic 11 `confidence: "gap"`; chapter lines 4–11 explicitly state there is no supplied source. Do not fill from inference. |
| 12 | **GAP (correctly declared).** `topics/manifest.json` marks topic 12 `confidence: "gap"`; chapter lines 4–11 explicitly state there is no supplied source. Do not fill from inference. |
| 13 | **Accept with correction.** Strong, mostly faithful coverage of `sources/di/13.pdf` / `run/di/13/page_001.txt`–`page_005.txt`; global-unicast wording is materially overbroad. |

## Findings (severity-ranked)

### P1 — Q13: IPv6 global-unicast range is incorrectly defined

- **Chapter:** `topics/bodies/topic_13.tex:213-220`, especially line 220: “global unicast addresses -- the remaining addresses from the corresponding global range.”
- **Evidence:** `sources/di/13.pdf`, p. 4; OCR `run/di/13/page_004.txt` (the source itself says “Global Unicast - всички останали”).
- **Impact:** “all remaining” can classify reserved, documentation, unique-local, multicast/other special space as global unicast; it gives an incorrect address taxonomy despite the source’s shorthand.
- **Correction:** Say global unicast uses the globally routable unicast range (normally `2000::/3` in the standard IPv6 unicast allocation), and retain the explicitly listed special ranges. If strict source fidelity is required, label the source’s “all remaining” phrase as an oversimplification rather than reproducing it as a definition.

### P1 — Q10: Segment offset boundary test is off by one

- **Chapter:** `topics/bodies/topic_10.tex:190-197`, especially line 194: “If the offset is greater than the segment length…”.
- **Evidence:** `sources/di/10.pdf`, p. 2; OCR `run/di/10/page_002.txt` (source uses the same loose wording).
- **Impact:** With zero-based offsets and a segment length `L`, valid offsets are `0..L-1`; offset `L` is already out of bounds. The current sentence permits one invalid byte.
- **Correction:** State that the offset must satisfy `0 <= offset < length` (or that an offset greater than or equal to the segment length raises a protection fault). Note this is a technical normalization of the source wording.

### P2 — Q9: Instruction format presents a next-instruction pointer as usual

- **Chapter:** `topics/bodies/topic_09.tex:290-299`, line 298 lists “pointer to the next instruction” as an ordinary instruction field.
- **Evidence:** `sources/di/9.pdf`, p. 3; OCR `run/di/9/page_003.txt` (source lists this as a possible instruction component).
- **Impact:** In most stored-program ISAs the next-instruction address is held/updated implicitly by the program counter and is not encoded as a field in every instruction. The wording can misteach the distinction between the source’s conceptual format and real ISA encodings.
- **Correction:** Qualify it as a source-level/conceptual possibility: an instruction *may* encode a branch/target or next-address information; normally the PC supplies the sequential next address implicitly.

### P2 — Q13: TLD management is attributed to registrars

- **Chapter:** `topics/bodies/topic_13.tex:243-249`, line 247: “Top-level domains are managed by registrars.”
- **Evidence:** `sources/di/13.pdf`, p. 5; OCR `run/di/13/page_005.txt` (same attribution).
- **Impact:** This conflates registries (which operate TLD registries) with registrars (which register names for customers). It is a terminology error in the DNS hierarchy section.
- **Correction:** Say TLD registries/registry operators maintain the TLD; registrars provide registration services for second-level names. If preserving the supplied lecture wording, add a brief terminology caveat.

## Gap handling

Questions 11 and 12 are not underwritten by any `run/di`, `run/ocr/*__production`, `run/math`, or source PDF. The placeholders accurately reproduce the syllabus annotation and explicitly identify the absence (`topics/bodies/topic_11.tex:4-11`, `topic_12.tex:4-11`; `topics/manifest.json` entries 11–12). No technical verdict beyond **GAP** is possible without introducing outside material.
