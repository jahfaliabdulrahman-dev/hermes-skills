# Benchmark Design Pitfalls — Lessons from Hermex Governance Paper

## Fatal Confound: Model Generation Gap

**What happened:** We compared DeepSeek-v4-pro (2026) against GPT-4o (2024), Claude Sonnet 4 (2025), and Gemini 2.5 Pro (2025). DeepSeek "won" 4/4 vs 0/4 — but the older models failed because they were OLD, not because governance was better.

**Fix:** Compare models from the SAME generation. The SAME-MODEL comparison (DeepSeek-v4-pro standalone vs DeepSeek-v4-pro in swarm) is the strongest because it controls for model capability perfectly.

## Workspace Contamination

**What happened:** All models shared one workspace. Later git resets wiped earlier models' commits.

**Fix:** Separate workspaces per model. Truth-check immediately after each run. Save results per-model JSON.

## Self-Report Hallucination

**What happened:** Models claimed "4/4 fixed" but truth-check showed 0/4. Self-reports are unreliable.

**Fix:** Always use grep-based truth-checks. Record pre/post state. Publish truth-check script alongside results.
