# InCIT 2026 — Paper #5 Revision Plan

**Paper:** Deep Reinforcement Learning Vulnerability Scanner for Multi‑Vulnerability Web Application Benchmarks
**Authors:** Hein Htet Zaw, Karn Yongsiriwit (Rangsit University)
**Plan date:** 2026‑06‑17
**Source file to edit:** copy `4-2-2026 draft.docx` → `17-6-2026 draft.docx` (original untouched)
**Status:** PLAN ONLY — no edits made yet. Awaiting approval + 2 decisions (see end).

---

## Review scoreboard

| Reviewer | Score | Stance |
|---|---|---|
| 1 | Weak accept (text says reject) | Harsh; wants critical lit review, full flowchart, statistical tests |
| 2 | Borderline | Title/grammar, undefined terms, leaked filenames, repetition, use full page limit |
| 3 | Accept | Citations in Intro, formatting, numbered equations, website rationale, table layout |
| 4 | Accept | Paper-structure paragraph, duplicated reference numbers, typos |

Net: salvageable. Three accept/borderline, one harsh. The gate is Reviewer 1's statistical-rigor demand.

---

## Integrity issues found (must resolve honestly)

1. **Fig. 2 training curve is synthetic.** `research/generate_training_curve.py` builds the reward/loss curves from `np.random.seed(42)` formulas, not real training logs. Cannot be presented as measured convergence data, especially while Reviewer 1 asks for convergence analysis. → DECISION 1.
2. **Detection results (Table I) are real.** Sourced from `research/results/autonomous_scan_average_findings.json` (genuine 5‑run eval). Keep.
3. **Results are modestly weak** (many 0.0% rows). Reviewers 1 & 2 note this. We will NOT overclaim superiority; reframe contribution as a component‑wise ablation (each Rainbow piece adds value) — defensible with honest numbers.

---

## Phase 0 — Setup (no risk)
- Copy `4-2-2026 draft.docx` → `17-6-2026 draft.docx`.
- Repair the document's root `.rels` (currently malformed; Word tolerates it, tooling does not) so edits are clean.

## Phase 1 — Trivial fixes (fast; satisfies Reviewers 2, 3, 4)
| # | Fix | Source review |
|---|---|---|
| 1.1 | Remove duplicated reference numbers `[1] [1]` → `[1]` (all 15) | R4 |
| 1.2 | Add "The remainder of the paper is organized as follows…" paragraph at end of Intro | R4 |
| 1.3 | Number all equations (1)–(4) | R3 |
| 1.4 | Define DOM and TD on first use | R2 |
| 1.5 | Retitle → "Deep Reinforcement Learning Vulnerability Scanner for Web Applications" (drop "Benchmarks", fix grammar) | R2 |
| 1.6 | Replace leaked filenames (`autonomous_scan.py`, `checkpoints/improved_mock_ep10000.pth`) with prose | R2 |
| 1.7 | Define `M` (total episodes) and `T` (steps/episode) in Algorithm 1 | R2 |
| 1.8 | Remove duplicated "three primary modules" sentence in Methodology; trim repeated "What is still missing" refrains | R2 |
| 1.9 | Fix Section 2‑C subsection title format; make Section 3 headings consistent; keep Table I on one page | R3 |

## Phase 2 — Literature review rewrite (Reviewers 1 & 3)
- Add citations to the Introduction (currently none).
- After each cited work in Section 2, add a critique sentence: what it did → method → limitation → the gap it leaves.
- Restructure Section 2 into a clear arc: state‑of‑the‑art → drawbacks of existing approaches → open problem → why Extended D3QN is suited.
- **Reference hygiene** (Reviewer 1 flagged pre‑2020 / preprints / conferences):
  - Keep [5] Mnih 2015 and [6] Schaul 2015 but add one justification line each (seminal/foundational).
  - Replace [8] "Pentest‑R1" (arXiv, author = "Anonymous" — bad) with a citable published source, or cut.
  - Swap weakest conference papers ([1][2][12][13][14]) for journal equivalents where available; justify any retained.
  - Target: reduce pre‑2020 and preprint/conference share; document each retained exception in text.

## Phase 3 — Framework flowchart + Methodology clarity (Reviewers 1 & 3)
- Create ONE new end‑to‑end flowchart: env → 15‑D state vector → Extended D3QN → action → HTTP request → reward → phase unlock → reporting. Sits alongside existing architecture figure (Fig. 1).
- Add step‑by‑step narrative tying the figure to the algorithm.
- Add website‑selection rationale to Section 4 (why these 6 mock apps; what vuln classes each covers).

## Phase 4 — Statistical rigor (Reviewer 1 — the gate) — needs GPU + DECISION 2
Codebase readiness: `agent/dqn_agent.py` = D3QN baseline; `agent/improved_dqn_agent.py` = Extended D3QN (PER + Noisy + multi‑step, with toggle flags). Only one trained checkpoint exists; baselines must be trained.

Deliverables I will build (scripts run on YOUR RTX 2070 Ti; I process the CSV outputs):
1. **Ablation harness** — Random → D3QN → Extended D3QN (+ component‑drop variants: −PER, −Noisy, −multi‑step), consistent episode budget, multiple seeds.
2. **Seeded eval** across all 6 targets → per‑target detection‑rate matrix.
3. **Stats script:**
   - Convergence analysis (from *real* training logs).
   - Convergence stability (coefficient of variation across seeds).
   - Friedman test across methods.
   - Wilcoxon signed‑rank, pairwise vs Extended D3QN.
4. New results tables/figures + analysis text, framed as ablation (not "beats all others").

If no GPU runs: limit Phase 4 to stability/CV on existing 5‑run data; frame Friedman/Wilcoxon as future work (weaker, but honest).

## Phase 5 — Verification
- Old↔new diff; reviewer‑point checklist (every comment mapped to a change).
- Verify reference count, years, no duplicate numbers, all equations numbered, all abbreviations defined.
- Confirm figures render; confirm NO synthetic data presented as empirical.
- Confirm page‑limit usage (Reviewer 2: fill available space, remove repetition).

---

## Open decisions (need your answer before Phase 4 / Fig. 2)

**DECISION 1 — Synthetic Fig. 2 training curve:**
(a) Re‑train on your GPU for a real curve · (b) relabel as illustrative schematic · (c) remove entirely.

**DECISION 2 — GPU ablation runs:**
(a) You can run training jobs (enables real Friedman/Wilcoxon vs baselines) · (b) existing data only (stats limited to current model).

---

## Effort / sequencing
- Phases 0–1: quick, no dependencies — can start immediately on approval.
- Phase 2–3: medium; content writing + one diagram.
- Phase 4: gated on Decisions 1 & 2 and your GPU.
- Phase 5: final.

Recommendation: approve Phases 0–3 now (they're pure wins and unblock a cleaner manuscript), and decide 1 & 2 in parallel so Phase 4 is ready when those runs finish.
