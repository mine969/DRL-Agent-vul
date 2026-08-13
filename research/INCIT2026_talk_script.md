# Talk Script — INCIT 2026 (10 min + 5 min Q&A)

Read this once, then talk from the slide titles, not this page. Numbers in **bold** are the ones you cannot fumble.

---

## Slide 1 — Title (20s)
"Good [morning/afternoon]. I'm presenting our work on a deep reinforcement learning vulnerability scanner for web applications — an agent that learns to find what static scanners miss, not just replay a signature list."

## Slide 2 — The Problem (40s)
"Three things drove this. Manual pentesting doesn't scale — skilled testers are expensive, release cycles are days not quarters. Static scanners plateau on signature-shaped bugs. And the blind spot is IDOR-class bugs — broken object-level authorization — because catching those needs context across multiple requests, not a single stateless check."

## Slide 3 — Research Gap (35s)
"Prior DRL scanners solve one vulnerability class at a time, use narrow state representations like raw HTTP text, and — this is the important one — don't systematically confirm their detections against ground truth. That last gap is what let earlier work overstate results. We built the confirmation step in from day one."

## Slide 4 — Our Approach (40s)
"Our agent is an Extended D3QN — Double DQN to stop Q-value overestimation, Dueling networks to separate state value from action advantage, Prioritized Experience Replay so rare confirmed hits get replayed more, and Noisy Nets for learned exploration instead of hand-tuned epsilon decay. Plus multi-step returns for credit assignment across multi-request attack chains."

## Slide 5 — System Architecture / Fig 1 (35s)
"Five mock targets — e-commerce, social media, banking, blog, file share — feed a 15-dimensional state vector into the agent. Training runs to **3,000 episodes**, then the vulnerability detection model generates the report. Only confirmed findings make it to the report — unconfirmed activity is logged separately, not counted."

## Slide 6 — End-to-End Pipeline / Fig 2 (30s)
"This is the loop: HTTP response → state encoder → the Double-Dueling network → PER for replay → reward and detection logic → phase controller → action back out as an HTTP request. Every arrow here is a real code path, not a simplification."

## Slide 7 — MDP Formulation (40s)
"15-dimensional state, 50 discrete actions, 4 curriculum phases. Reward shaping is simple and interpretable: **+1.0** for a confirmed vulnerability flag, **−0.1** for triggering a WAF, **−0.01** for a wasted request. Bellman target uses the Double-DQN correction — decouple action selection from evaluation to stop overestimation."

## Slide 8 — Phase Curriculum (30s)
"Recon, Assess, Exploit, Post-Exploit — phases are earned, not scripted. The agent has to demonstrate signal in one phase before the next unlocks, mirroring how a real pentest engagement actually escalates."

## Slide 9 — Experimental Setup (30s)
"Ground truth isn't estimated — it's enumerated in code, per target: **20 / 20 / 4 / 6 / 6** planted vulnerabilities across the five apps. A finding only counts as confirmed when both the ground-truth response header and an independent local validator agree."

## Slide 10 — Results (45s)
"Here's where we're honest. Confirmed detection: E-Commerce **25%** (1 of 4 IDOR), Social Media **16.7%** (1 of 6 IDOR). Banking, Blog, File Share: **zero**. Every other planted vulnerability class: zero across all five targets. We're reporting this as-is. The contribution here isn't a win rate — it's a measurement pipeline you can trust."

## Slide 11 — Robustness Check (45s) — your strongest slide, slow down here
"We asked: is this weak detection just under-scanning? So we reran everything with **5x** the crawl depth and attack intensity — depth 150 vs 20, intensity 100 vs 5. Unconfirmed activity flagged went up roughly **3x**. Confirmed detections: **zero change**. Same single IDOR finding on the same two targets, everything else still zero. That tells us the gap is structural, not a symptom of insufficient scanning — and it tells us the ground-truth confirmation step actually resists false-positive inflation when you scan harder."

## Slide 12 — Limitations & Future Work (35s)
"Limitations, stated plainly: confirmed detection is narrow, IDOR-only, on two of five targets; it's a single-agent architecture with no transfer study yet; reward shaping is hand-tuned, not ablated per term. Future work: Friedman and Wilcoxon tests across seeds for statistical rigor, expanding the curriculum to auth-bypass and SSRF-style chains, and a component-wise ablation of the Rainbow additions."

## Slide 13 — Thank You (10s)
"Thank you — happy to take questions."

---

# Q&A / Interview Prep

Answer these like you're explaining to a beginner first, then add the technical layer. If you can't do that split from memory, that's the gap — go back to the paper before the talk, not during it.

### "Why detection rate this low — isn't that a weak result?"
Don't get defensive. Say: "It is low, and we say so directly. The contribution isn't the win rate, it's that every number on that slide is independently confirmed, not just flagged — and we proved that with the 5x robustness check, which most DRL-scanner papers don't do at all. A lot of prior work reports higher numbers precisely because they don't have that confirmation step."

### "Why only IDOR gets confirmed — what about XSS, SQLi, etc.?"
"The agent explores all action classes, but IDOR is the one where our confirmation criteria — ground-truth header plus independent validator agreement — consistently line up in these five targets. That's a real limitation of the current reward/confirmation design, not a claim that the agent can't detect other classes. It's on the future-work list to ablate that per vulnerability type."

### "Why these five specific apps?"
"They give deliberate, code-enumerated ground truth across different domains — e-commerce, social, banking, blog, file-share — so we're not testing on one narrow app type. Vuln counts (20/20/4/6/6) come from `run_ground_truth_scan`, not estimation."

### "Why D3QN and not a newer architecture (Rainbow full, PPO, etc.)?"
"D3QN with PER, Noisy Nets, and multi-step returns covers five of Rainbow's six components — we deliberately excluded Distributional RL to keep the state/action space tractable for a first systematic study. It's a reasonable middle ground between a vanilla DQN baseline and full Rainbow complexity we haven't yet justified with ablation data."

### "Where's your statistical significance testing?"
It's already in the paper, Section V-E — don't undersell this one. "We ran a Friedman test across all six variants — Random, vanilla DQN, full Extended D3QN, and three leave-one-out ablations — five seeds each. It came back significant on both reward and detection rate (χ²=18.83, p=0.0021 and χ²=17.60, p=0.0035). What didn't clear significance were the individual pairwise Wilcoxon comparisons against the full model — and that's not us hiding a weak result, it's arithmetic: at n=5 seeds, Wilcoxon's p-value floor is 0.0625, so no pairwise comparison could hit p<0.05 even with a perfect sweep. We report the honest limitation and flag more seeds as the fix."

### "How do you know the confirmation step itself isn't buggy / trivially satisfied?"
"Two independent signals have to agree — the target's own ground-truth response header and a separate local validator that doesn't read that header. They're deliberately decoupled so one can't rubber-stamp the other. The 5x scan test is really an indirect proof of this: if confirmation was trivially satisfied, more scanning volume would have inflated the confirmed count too, and it didn't."

### "What's the real-world deployment story — would you run this against a live app?"
"Not yet, and we're upfront about that boundary. Everything here runs against mock apps with known ground truth specifically so we can measure recall honestly. Deploying against a real target without ground truth removes exactly the thing that makes our numbers trustworthy — that's a deliberate scope limitation, not an oversight."

### "What would you do differently if you restarted this project?"
Have a real answer, not a hedge: "Build the ground-truth confirmation pipeline and the ablation harness before scaling up training episodes — we built compute-heavy training first and retrofitted rigor second. Doing it in the other order would have saved a lot of rework."

---

## Before you walk in
- Know cold: **20/20/4/6/6** ground truth, **25% / 16.7%** confirmed rates, **5x / 3x / 0** robustness numbers, **+1.0 / −0.1 / −0.01** rewards, **3,000** episode default.
- If a number doesn't come out smoothly under pressure, that's the one to drill before InCIT, not during.
