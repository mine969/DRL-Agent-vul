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

Every answer below has two layers: **Simple** — say this first, always, even to a technical interviewer. **If they push for detail** — the technical follow-up, only if they ask "how exactly" or "show me the numbers." If you can't explain the Simple line in your own words without reading it, that's the gap — go back to the paper before the talk, not during it.

### "Why detection rate this low — isn't that a weak result?"
**Simple:** "It is low, and we say that upfront instead of hiding it. What we built isn't a tool that finds everything — it's a tool that only reports a bug when it's actually 100% sure. Most similar research tools just guess and report high numbers without double-checking themselves. Ours double-checks everything, so our number is smaller but it's a number you can trust."
**If they push for detail:** "Every number on that slide is independently confirmed, not just flagged — and we proved that with the 5x robustness check, which most DRL-scanner papers don't do at all."

### "Why only IDOR gets confirmed — what about XSS, SQLi, etc.?"
**Simple:** "The tool actually looks for all kinds of bugs, not just this one. But this particular type — where someone can access another user's data by just changing a number in a web address — is the one our strict double-checking system agreed on every time, in these five test apps. It's a real gap in how we currently check, not proof the tool can't find other bug types. Fixing that is next on our list."
**If they push for detail:** "Our confirmation criteria — ground-truth header plus independent validator agreement — consistently line up for IDOR specifically. It's on the future-work list to ablate that per vulnerability type."

### "Why these five specific apps?"
**Simple:** "We built five fake but realistic websites ourselves — an online shop, a social media site, a bank, a blog, and a file-sharing site — and we planted a known, counted number of bugs in each one, in the actual code. So we always know the exact right answer to grade against, instead of guessing."
**If they push for detail:** "Vuln counts (20/20/4/6/6) come from `run_ground_truth_scan`, not estimation — they're enumerated directly in source code."

### "Why D3QN and not a newer architecture (Rainbow full, PPO, etc.)?"
**Simple:** "There's a well-known upgrade path in this field with about six different improvements you can stack together. We used five of the six — leaving one out kept the problem manageable for a first proper study. Think of it as the sensible middle option between the basic version and the maximum-complexity version we haven't earned the right to claim works yet."
**If they push for detail:** "D3QN with PER, Noisy Nets, and multi-step returns covers five of Rainbow's six components — we deliberately excluded Distributional RL to keep the state/action space tractable."

### "Where's your statistical significance testing?"
**Simple:** "It's already done, in the paper. We tested six different versions of our agent, five separate times each, and ran a standard statistics test to check if the differences between them were real or just luck. The answer: yes, real differences exist between the six versions overall. What we couldn't yet prove is exactly which specific version beats which other one — that needs more test runs than we had time for, and we say so honestly instead of hiding it."
**If they push for detail:** "A Friedman test across all six variants — Random, vanilla DQN, full Extended D3QN, three leave-one-out ablations — five seeds each, came back significant on both reward and detection rate (χ²=18.83, p=0.0021 and χ²=17.60, p=0.0035). The pairwise Wilcoxon comparisons against the full model didn't clear p<0.05, and that's arithmetic, not a weak result: at n=5 seeds, Wilcoxon's p-value floor is 0.0625, so no pairwise comparison could hit significance even with a perfect sweep."

### "How do you know the confirmation step itself isn't buggy / trivially satisfied?"
**Simple:** "We require two separate, independent checks to both say 'yes, this is a real bug' before we count it — like needing two different witnesses to agree instead of trusting one. We also tested this by scanning much harder and much longer: if our checking system was too easy to fool, scanning harder should have found more 'confirmed' bugs. It didn't. That's good evidence the check is doing its job properly."
**If they push for detail:** "The target's own ground-truth response header and a separate local validator are deliberately decoupled so one can't rubber-stamp the other. The 5x scan test is an indirect proof: if confirmation was trivially satisfied, more scanning volume would have inflated the confirmed count too, and it didn't."

### "What's the real-world deployment story — would you run this against a live app?"
**Simple:** "Not yet, and that's on purpose. Right now we only test against our own fake websites, where we already know exactly what bugs exist. That's the only way to know for certain if the tool is right or wrong. Pointing it at a real website would mean we couldn't grade its answers anymore — we'd lose the thing that makes our results trustworthy."
**If they push for detail:** "Everything runs against mock apps with known ground truth specifically so we can measure recall honestly — that's a deliberate scope limitation, not an oversight."

### "What would you do differently if you restarted this project?"
**Simple:** "We'd build our 'how do we know it's telling the truth' checks first, and the expensive training runs second. We did it backwards — spent weeks on heavy training, then had to go back and bolt on the verification afterward. If we'd built the verification step first, we'd have caught problems earlier and wasted a lot less time."
**If they push for detail:** "Build the ground-truth confirmation pipeline and the ablation harness before scaling up training episodes — we built compute-heavy training first and retrofitted rigor second."

---

## Before you walk in
- Know cold: **20/20/4/6/6** ground truth, **25% / 16.7%** confirmed rates, **5x / 3x / 0** robustness numbers, **+1.0 / −0.1 / −0.01** rewards, **3,000** episode default.
- If a number doesn't come out smoothly under pressure, that's the one to drill before InCIT, not during.
