# Multi-Model Constitutional Assembly — 5-Phase Process

Born from 2026-07-09: 9-round dialogue between Triple-Chinese MoA and DeepSeek-v4-pro to design swarm governance constitution. Eng. Abdulrahman's principle: "عدة عقول تنتج إجابات عظيمة."

## When to Use
- Designing or amending governance structures
- Making constitutional-level decisions for the swarm
- Resolving systemic governance failures that recur across projects
- NOT for: feature implementation, bug fixes, task routing, code review

## The 5 Phases

| Phase | Actor | Role | Input | Output |
|-------|-------|------|-------|--------|
| 0 | Sulaiman | Preparation | System state | Unified brief (one question) |
| 1 | DeepSeek-v4-pro | Ground-level practical analysis | Brief | Answer + quantitative self-assessment |
| 2 | Triple-Chinese MoA | Destruction by logic | Brief + Phase 1 | Critique + superior architecture + self-assessment |
| 3 | DeepSeek-v4-pro (Systems lens) | Synthesis | Brief + Phases 1+2 | Definitive architecture |
| 4 | Sulaiman | Summary & comparison | All phases | Agreement/disagreement map + voting question |
| 5 | All 3 models (parallel) | Vote | Synthesis + Phase 4 | APPROVE/REJECT/APPROVE WITH RESERVATIONS + justification |

## Critical Rules

1. **ALL models receive the SAME question** — never vary
2. **Cumulative context** — each phase reads everything before it
3. **"Destroy with logic, not for argument"** — cite evidence, concede what's right
4. **Self-assessment must be QUANTITATIVE**: "X/10 because I covered A, B, C — but missed D, E"
5. **Solutions must be SYSTEM-WIDE** — never project-specific (0/10 failure if saved to app-spec/)
6. **Separate models** — each queried independently for genuinely different perspectives
7. **Text is not enforcement** — every rule needs a mechanism (hook, cron, symlink, Court)
8. **If not convincing to BOTH Sulaiman and Abdulrahman, do NOT implement.** Save for later.

## 2026-07-09 Assembly Results

**Question:** "Design permanent governance constitution for 10-profile Flutter swarm. Must be system-wide, machine-enforceable, survive restarts. Cover: Prevention, Detection, Escalation. Additionally: what's missing for professional Flutter dev end-to-end?"

### Scores & Votes

| Phase | Model | Score | Key Contribution |
|-------|-------|-------|-----------------|
| 1 | DeepSeek-v4-pro | 7/10 | SOUL files are text, not enforcement. 3 pillars: hooks, cron, kernel. |
| 2 | Triple-Chinese MoA | 4/10 (of P1) | Category error: treating agent behavior as database problem. 6 fundamental errors. |
| 3 | DeepSeek Systems | 8.5/10 | Process Governance, Binding Contracts, Constitutional Court, Event Bus. |
| Vote 1 | DeepSeek (P1 author) | APPROVE WITH RESERVATIONS | 5 reservations: reputation untested, behavioral signals fragile, minimum viable = Phase 1, Court single failure point, no startup compliance check. |
| Vote 2 | Triple-Chinese | APPROVE WITH RESERVATIONS | 6.5/10 real score (not 8.5). Contracts still aspirational, context window unaddressed, Court unguarded. |
| Vote 3 | Neutral Arbitrator | APPROVE WITH RESERVATIONS | 7/10. Hunter needs compulsory action, QA needs PULL model, reputation must be validated. |

**Final Outcome:** Unanimous APPROVE WITH RESERVATIONS. Constitution deployed at `~/.hermes/swarm/`. Reservations documented as Phase 4 work items.

## Key Lessons from This Assembly

1. **Separate models produce genuinely different insights** — don't bundle them
2. **The destruction phase is essential** — adversarial review catches what self-assessment misses
3. **Self-assessment must be quantitative and honest** — self-grading 8.5/10 when consensus is 7/10 reveals blind spots
4. **Voting without justification is worthless** — every vote must cite evidence from the proposal
5. **0/10: System-wide means system-wide** — saved first draft to `hermex_android/app-spec/`. User correctly rejected this as "حكم فاشل" (failed governance). Governance artifacts go to `~/.hermes/swarm/` ONLY.
6. **"ممنوع الاختزال الاجرائي"** — no procedural shortcuts. Every phase must complete fully.
7. **Adversarial ≠ hostile** — the destruction phase attacks IDEAS, not the model that produced them
