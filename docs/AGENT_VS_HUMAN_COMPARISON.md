# Agent vs Human Tester

This project is best treated as an AI-assisted web testing system, not a full replacement for an experienced human penetration tester.

## What the Agent Does Well

- Runs long, repeatable test loops without fatigue.
- Applies learned attack patterns quickly across discovered endpoints.
- Produces structured findings and reports for triage.
- Works consistently on the 5 local mock targets used for training.

## Where Humans Still Lead

- Business logic abuse that depends on domain context and intent.
- Creative exploit chaining across systems, trust boundaries, and workflows.
- Threat modeling and deciding what to test first under time constraints.
- Report judgment, risk communication, and remediation prioritization.

## Practical Positioning

- Use the scanner to automate baseline recon and vulnerability probing.
- Use human review for high-impact validation, exploit chain design, and final conclusions.
- Treat findings as security signals that still require analyst verification.

## Bottom Line

The current agent is a strong force multiplier for authorized testing workflows, especially on known app patterns. It improves speed and coverage, while human expertise remains essential for advanced reasoning and final security decisions.
