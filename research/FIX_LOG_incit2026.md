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
- **Website-selection rationale (R3):** explain why the 6 mock apps were chosen.
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

## Batch G — expansion + framework flowchart (done, verified)
**#1 Methodology/results expansion (R2 "more detail"):** added two grounded paragraphs (no new/contradicting numbers):
- Phase-based curriculum mechanics — the three phases (Recon 0-29 → Assessment 30-69 → Exploitation 70-149), action gating, WAF-evasion action family, and reward shaping (grounded in `env/web_sec_env.py`).
- Results analysis — why input-driven flaws (SQLi/XSS) are detected reliably while authorization/workflow flaws (IDOR, mass assignment, JWT) are harder (credit-assignment across authenticated requests); ties strong E-Commerce/Social Media vs weak Blog/File Share to the state/action design.

**#2 Framework flowchart (R1 + R3):** built and embedded as **Fig. 2** (`image3.png`) at the end of Methodology — end-to-end pipeline: Environment → State Encoder (15-D) → Extended D3QN → Phase Controller → Action/Payload → HTTP → loop, plus the training sub-loop (Reward & Detection → Replay Buffer → Agent) and the Report output. Caption auto-numbers via the `figurecaption` style (training curve becomes Fig. 3). Added an in-text pointer to Fig. 2 in the Methodology intro. Diagram visually verified before embedding.

Plan status: Phase-3 flowchart + R2 "more detail" now **done**. Remaining: equation numbering (R3, best in Word), and the statistics/synthetic-Fig. decision (Phase 4, GPU).

## Already clean in this draft (no action)
- Title already "…for Modern Web Applications" (no "Benchmarks") — R2 handled.
- Duplicate reference numbers `[1] [1]` not present.

**Verification:** every batch checked by string assertions; `document.xml` parses well-formed after each.
