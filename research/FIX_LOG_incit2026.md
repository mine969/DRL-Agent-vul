# InCIT 2026 Paper #5 — Revision Log

**Editing file:** `17-6-2026 draft.docx` (copy of `4-2-2026 draft.docx`; original untouched)
**Last updated:** 2026-06-17

This log has two parts: **Part 1 — Planning** (prioritized reviewer audit + what's still to do) and **Part 2 — Fixing Log** (what has been changed, verified).

---

# PART 1 — PLANNING

## Reviewer scoreboard
| Reviewer | Score | Core demand |
|---|---|---|
| 1 | Weak accept (text leans reject) | Critical literature review, full framework flowchart, statistical tests (convergence, stability, Wilcoxon, Friedman) |
| 2 | Borderline | Title, undefined terms, leaked filenames, repetition, use full page limit |
| 3 | Accept | Intro citations, subsection-format, numbered equations, website rationale, Table I on one page |
| 4 | Accept | Paper-structure paragraph, duplicate reference numbers, typos |

## Prioritized plan (remaining work)

### P1 — The acceptance gate (high effort, needs decisions/GPU)
- **Statistical rigor (R1):** convergence analysis, convergence-stability (CV), Friedman + Wilcoxon vs baselines. Needs an ablation (Random / D3QN / Extended D3QN) trained on the **user's RTX 2070 Ti** — sandbox has no CUDA. Harness to be written here; user runs it.
- **Synthetic Fig. 2 (integrity):** training curve is generated from `np.random.seed(42)`, not real logs. DECISION pending: retrain for a real curve / relabel as illustrative / remove.

### P2 — Medium (content + one diagram)
- **Framework flowchart (R1, R3):** add one end-to-end algorithm flowchart beside Fig. 1.
- **Website-selection rationale (R3):** explain why the 5 mock apps were chosen.
- **Equation numbering (R3):** equations are centered OMML objects; numbering them (1)–(4) needs careful layout. Best done/verified in Word (cannot render here). FLAGGED.
- **Table I on one page (R3):** set rows to not break across pages — Word layout, verify visually. FLAGGED.

### P3 — No-risk grammar / IEEE format → DONE (see Part 2)
- Typos, reference hygiene, author block, headings, abbreviations, repetition, structure paragraph.

### Optional polish
- Tone/academic register — **DONE** (Batch E).
- Author block — **DONE**, native IEEE 2-column band, italic affiliations (Batch C/F).

---

# PART 2 — FIXING LOG

## Batch A — zero-risk typos (done, verified)
| Was | Now |
|---|---|
| `Abstract—- Traditional` | `Abstract—Traditional` |
| `Extensive D3QN` | `Extended D3QN` |
| `to iterative update action values` | `to iteratively update action values` |

## Batch B — references + literature review (Phase 2, done, Crossref-verified)
| Ref | Was | Now |
|---|---|---|
| [3] | Mainka, WS-Attacker, *2012 conf* | Shaon & Akter, *Electronics* 14(22):4449, 2025 |
| [6] | Schaul PER, **arXiv** preprint | Schaul PER, *Proc. ICLR* 2016 (published) |
| [8] | **"Anonymous"**, Pentest-R1, **arXiv** | Wu et al., CurriculumPT, *Appl. Sci.* 15(16):9096, 2025 |

- Body sentences for [3] (WS-Attacker→modern detection) and [8] (Pentest-R1→CurriculumPT) reworded to match.
- Critique commentary added after [5] Mnih, [6] Schaul/PER, [7] IAPTF, [14] ASAP (method → limitation → our gap).
- Intro citations added: DAST→[1]; sequential decision-making→[4],[5].
- Result: 0 preprints, 0 "Anonymous", pre-2020 share reduced.

## Batch C — author block (done, verified)
- Rebuilt to **exactly two authors, no template defaults**:
  - Hein Htet Zaw — College of Digital Innovation Technology, Rangsit University, Pathumthani, Thailand — heinhtet.z66@rsu.ac.th
  - Karn Yongsiriwit — College of Digital Innovation Technology, Rangsit University, Pathumthani, Thailand — karn.y@rsu.ac.th
- Removed all "line 1:/2nd–6th Given Name Surname" placeholder junk and the stray gmail/old affiliation. (Details per submitted PDF, user-confirmed.)

## Batch D — no-risk grammar + IEEE format (done, verified)
| Fix | Detail |
|---|---|
| Subsection "C." duplicate | Removed literal `C. ` — heading style auto-letters A/B/C (this was Reviewer 3's exact item) |
| Section "IV." duplicate | Removed literal `IV. ` from Evaluation — style auto-numbers |
| Section "VI." wrong+duplicate | Removed literal `VI. ` from Conclusion (it's section **V**, and was doubled) |
| DOM | First use expanded to "Document Object Model (DOM)" |
| TD | First use expanded to "Temporal Difference (TD)" |
| Algorithm 1 M, T | Defined: M = total training episodes, T = max steps/episode |
| Leaked filenames | `autonomous_scan.py` / `improved_mock_ep10000.pth` → plain prose |
| Repetition (Sec. III) | Duplicate "three primary modules" sentence fixed to correctly name the 3 modules |
| Paper-structure paragraph | Added "The remainder of this paper is organized as follows…" (Reviewer 4) |

## Batch E — academic tone + vocabulary polish (done, verified)
Full-paper register pass: ~43 hyperbolic/informal expressions softened to academic English, **claims, numbers, and citations unchanged**. Examples:
| Was | Now |
|---|---|
| "exploded in complexity" | "grown substantially in complexity" |
| "finding the low-hanging fruit" | "identifying easily detectable vulnerabilities" |
| "We desperately need" | "There is a clear need for" |
| "the “brain” of the scanner" / "acts as the “brain”" | "the core of the scanner" / "serves as the decision-making component" |
| "bleeding-edge DRL techniques" | "advanced DRL techniques" |
| "literal human-level performance" | "human-level performance" |
| "a brilliant new state-of-the-art framework" | "a state-of-the-art framework" |
| "vicious runtime injection" | "severe runtime injection" |
| "a direct showdown … scripts run flawlessly fast … the human eye" | "a direct comparison … automated scripts run efficiently … a human tester" |
| "immensely popular … brute-force efficacy" | "widely used … effectiveness" |
| "cleverly modeling … profound ability … effortlessly integrating" | "modeling … strong ability … integrating" |
| "powerfully leverage … rapidly becoming indispensable" | "leverage … becoming increasingly important" |
| "Dropping mild payloads" / "weaponized payloads" | "Submitting mild payloads" / "advanced payloads" |
| "indiscriminately firing complex exploits" | "indiscriminately executing complex exploits" |
| Abstract: "successfully learns … significantly outperforming … successfully minimizing" | "learns … outperforming … reducing" (removed double "successfully") |

Verified: 0 flagged hyperbole terms remain; `document.xml` parses well-formed.

## Batch F — Reviewer 2 closeout (done, verified)
| R2 point | Status |
|---|---|
| Title "benchmarks" redundant / not conceivable | Title adopted from reviewer: **"Vulnerability Scanner for Web Applications Based on Deep Reinforcement Learning"** |
| DOM / TD not explained | Done (Batch D) |
| Algorithm 1 M, T undefined | Done (Batch D) |
| autonomous_scan.py / checkpoint filenames | Done (Batch D) |
| Repetitions | Done (Batch D — "three primary modules"; "What is still missing" refrain = 0) |
| Missing words / English | Addressed across Batches A, E |
| "Use full page limit / more detail" | **Partial:** added full 15-feature state-vector enumeration + website-selection rationale (Sec. IV). Further expansion = Phase 3. |
| "Results preliminary / not convincing" | **Open** — requires stats/ablation (Phase 4, GPU) + Fig. 2 decision |

## R2 still open (needs substantive work, not text edits)
- Fuller use of page limit (more methodology/results explanation) → Phase 3.
- Convincing results (convergence, stability, Wilcoxon, Friedman vs baselines) → Phase 4, needs GPU.

## Already clean in this draft (no action)
- Title already "…for Modern Web Applications" (no "Benchmarks") — R2 handled.

**Verification:** every batch checked by string assertions; `document.xml` parses well-formed after each.

---

## Batch G — 2026-08-09, real render-verified pass (`9-8-2026 draft v5.docx`, copy of v4)

**Important correction to the record above:** the "Duplicate reference numbers `[1] [1]` not present" claim in the "Already clean" section was **wrong**, and the reason it was wrong is worth keeping on file — it was checked with a text regex over `document.xml` paragraph text (`\[(\d+)\]\s*\[\1\]`), which found nothing, because the duplication isn't in the paragraph text at all. The `references` paragraph style has `numPr numId="8"` (Word/LibreOffice auto-generates the `[N]` bracket for every paragraph using that style), and every reference *also* had a literal `[N] ` typed at the start of its text — invisible to a text-only check, but renders as `[1] [1] R. Singh…` through `[20] [20] M. Hessel…` when actually opened. Caught this time by rendering the docx to PDF via LibreOffice (`soffice --headless --convert-to pdf`) and visually inspecting the pages instead of trusting string checks alone. **Any future numbering/formatting verification on this document should render and look, not just grep the text.**

| # | Reviewer | Item | Found | Fix |
|---|---|---|---|---|
| 1.1 | R4 | Duplicated reference numbers | **Confirmed live** on visual render, all 20 entries doubled (see correction above) | Stripped literal `[N] ` prefix from all 20 `references`-styled paragraphs; kept the style's auto-numbering as sole source of the bracket number. Re-rendered: `[1]` through `[20]`, no duplication. |
| 1.9 | R3 | Consistent section numbering | `EVALUATION AND RESULTS` and `CONCLUSION` headings had paragraph-level auto-numbering disabled (`numId=0` override) but never got literal numeral text added — unlike `V. DISCUSSION`, which has both the override and literal `V. ` text. Rendered with **no visible section number at all**. | Added `IV. ` / `VI. ` literal prefixes, matching the working `V. DISCUSSION` pattern exactly. Re-rendered: `IV. EVALUATION AND RESULTS`, `VI. CONCLUSION` now correct. Left `I. INTRODUCTION`, `II. RELATED WORK`, `III. METHODOLOGY`, and Related Work's `A./B./C.` subsections **untouched** — these already render correctly via the style's own `numId=4` auto-numbering (verified on render); adding literal text to these would have caused the same doubling bug as the references list. |
| 1.5 | R2 | Retitle | Title was "Vulnerability Scanner for Web Applications Based on Deep Reinforcement Learning" | Changed to R2's exact suggested phrasing: "Deep Reinforcement Learning Vulnerability Scanner for Web Applications". |
| 1.8 | R2 | Duplicated "three primary modules" sentence | Confirmed still present: the System Architecture intro paragraph restated "three primary modules" (already implied by the surrounding "decouple...HTTP execution engine" framing) immediately before a separate "three main parts:" lead-in to the same bulleted breakdown | Removed the redundant summary paragraph entirely; the bulleted breakdown right after already names and describes all three components in more detail. Re-rendered: flows cleanly from Fig. 1 caption straight into the bulleted breakdown, no repetition. |

**Verified already done (re-checked against v4, not re-changed):** 1.2 (paper-structure paragraph), 1.3 (equations 1-3 numbered; no missing 4th equation, reward function is prose+values not a formal equation), 1.4 (DOM, TD defined on first use), 1.6 (no leaked filenames), 1.7 (M, T defined in Algorithm 1 prose). Phase 2's citation/critique work (Batch B) and Phase 3's end-to-end flowchart (Fig. 2, already present with full narrative) also confirmed present on this render pass — not re-verified line-by-line against every reviewer sub-point yet.

**Found but NOT fixed this pass (flagged, needs a decision):**
- **Table I still spans two pages** (breaks mid-table between pages 5 and 6, splitting the Banking row group across the page boundary in v4; still overflows in v5 after the paragraph-removal, just slightly later). R3's "keep Table I on one page" is still open. Deliberately not doing layout surgery on this now because Table I is scheduled to be **regenerated from the 3k `d3qn_full` ablation run** once training finishes (see "Regenerate Table I from 3k model" task) — fixing pagination on data about to be replaced would be wasted effort. Revisit once the new table exists; it may have a different row count that changes the fix needed.
- **Fig. 1 (System Architecture diagram) contains an embedded "Is the model training 10K Episodes?" decision diamond** — baked into the image itself, not editable text. This is now inconsistent with the project's actual current 3,000-episode default. Flagged for the paper's author to decide: update the diagram image, or leave as a description of the diagram's original design intent (needs a human call, not a silent edit to a figure).

**File:** working copy is `research/9-8-2026 draft v5.docx` (copy of `8-7-2026 draft v4.docx`, which is untouched). Verified via `python-docx` (opens cleanly, 114 paragraphs after the one removal) and a full LibreOffice PDF render (7 pages, visually checked pages 1, 3, 4, 5, 6, 7).
