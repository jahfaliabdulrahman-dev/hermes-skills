---
name: swarm-governance
description: System-wide Flutter swarm governance constitution — 8-article constitution.yaml, Process Governance model, Constitutional Court, Binding Review Contracts, Governance Lessons (GL) tracking, orchestrator turn budgets. Deploy once, all projects inherit via symlinks. Use when setting up or troubleshooting multi-agent Flutter swarm governance.
version: 1.0.0
---

# Swarm Governance — System-Wide Constitution

## What Is It

A permanent, system-wide governance constitution for ALL Flutter swarm projects. Deployed once at `~/.hermes/swarm/`. Every new project inherits automatically via symlinks.

## Architecture — 3 Layers

```
DEFENSE → DETECTION → ESCALATION
(Symlinked  (SCSI+Cron)  (Council+Human)
Constitution)
```

## Key Files

| File | Purpose |
|------|---------|
| `~/.hermes/swarm/constitution.yaml` | SINGLE SOURCE OF TRUTH — 8 articles |
| `~/.hermes/profiles/flutter-*/constitution.yaml` | Symlinks → swarm/constitution.yaml |
| `~/.hermes/swarm/00_governance_lessons.md` | GL tracking (separate from LL-NNN) |
| `~/.hermes/swarm/ledger/` | Immutable event log |
| `~/.hermes/swarm/reputation/` | Reputation scores |

## 8 Articles

| Article | Content |
|---------|---------|
| I | Profile Identities & Boundaries |
| II | EPIC Lifecycle & 6 Completion Gates |
| III | Binding Review Contracts (staked, bidirectional) |
| IV | Detection & Escalation (L0–L4) |
| V | Governance Council (3 seats, 2/3 majority) |
| VI | Constitutional Court (non-AI cron, 60s heartbeat) |
| VII | Project Lifecycle (Plan→Design→Dev→Test→Deploy→Monitor) |
| VIII | Amendment Procedure |

## Core Mechanisms

1. **Process Governance (not State):** Governs HOW agents reason and interact, not just task completion
2. **Binding Review Contracts:** Architect stakes reputation. No silent abandonment.
3. **Constitutional Court:** Non-AI cron watching watchers. 60-second heartbeat.
4. **Rotating Governance Council:** 3 seats, 2/3 majority. No single failure point.

## Governance Lessons (GL) System

Separate from code lessons (LL-NNN). Symlinked to all 10 profiles at `00_governance_lessons.md`.

| GL | Lesson |
|----|--------|
| GL-001 | Decomposition ≠ Completion — Lead abandons EPICs |
| GL-002 | Hunter findings ignored — no escalation chain |
| GL-003 | Context window exhaustion — orchestrator crash before closure |
| GL-004 | Old pipeline tasks don't auto-unblock when conditions met |
| GL-005 | First successful constitution-governed EPIC |
| GL-006 | No governance lessons tracking existed |
| GL-007 | Orchestrator vs worker turn budget asymmetry |
| GL-008 | CI secret name mismatch — workflow vs repository |
| GL-009 | PKCS12 vs JKS keystore format incompatibility |
| GL-010 | Keystore password exposure in shell commands |
| GL-011 | Analysis paralysis — Triple-Chinese MoA consultation loop |
| GL-012 | Self-correction — chronological contradiction detected |
| GL-013 | Phantom bug fix — 30-minute hunt for non-existent error |

## Competitive Benchmark Findings (2026-07-11)

Two rounds of competitive benchmarking compared our constitutional swarm against 8 frontier models:

**Round 1 (Standalone):** All 2025-2026 models (GPT-4.1, Gemini 2.5 Pro, DeepSeek-v4-pro, Claude Opus 4) hit 4/4. All 2024 models (GPT-4o, Claude Sonnet 4) scored 0/4. **Finding: frontier model convergence — raw capability is commoditizing. The differentiator is governance, not coding skill.**

**Round 2 (Orchestration):** 3 of 4 frontier orchestrators (MiniMax M3, Qwen 3.7 Plus, GLM-5.2) completed 4/4 when acting as Lead Architect for a 9-agent team WITHOUT constitution. Claude Sonnet 5 scored 0/4 due to analysis paralysis. **Finding: 25% ungoverned failure rate. Governance overhead (3h 16m for 6 gates) IS the product — each gate maps to a documented failure mode.**

**Key insight:** Frontier models can all fix bugs. Governance provides: audit trail, gate enforcement, regression prevention, and silent-failure detection. The 6 gates (§II) are not overhead — they are the machine-enforceable response to empirically observed violations (GL-001 through GL-013).

## Orchestrator Turn Budget Rule

**Born from GL-003/GL-007:** Lead Architect crashed at 200 turns (max_turns default) after 50 minutes of monitoring during first constitution-governed EPIC. Monitoring cycles consume turns without producing output.

**Rule:** Orchestrators (Lead Architect) must have `max_turns: 1000`. Workers stay at 200. Adjust in `~/.hermes/profiles/flutter-lead-architect/config.yaml`:

```yaml
agent:
  max_turns: 1000  # Was: 200
goals:
  max_turns: 1000  # Was: 200
```

**Why 500-1000:** Decomposition (50 turns) + architecture analysis (100 turns) + monitoring cycles every 30min × 5 hours (100 turns) + gate verification (50 turns) + status reports (50 turns) + buffer.

## Pitfalls

- **Never save governance to project app-spec/.** 0/10 failure. System-wide only.
- **Decomposition ≠ Completion.** Lead used to mark EPICs DONE in 27min. Constitution §II requires 6 gates before closure. GL-001.
- **Orchestrator turn budgets > workers.** Lead crashed at 200 turns (50min monitoring). Orchestrators need 3-5× more turns (500-1000) because monitoring cycles consume turns without output. GL-003, GL-007.
- **Governance lessons need separate tracking.** Code bugs → LL-NNN. Governance failures → GL-NNN. GL-006.
- **Symlinks must be verified after profile re-creation.**
- **Constitution amendments require Governance Council 2/3 vote.**
- **Text in SOUL files is not enforcement.** Use: hooks, cron, symlinks, Constitutional Court.
- **Transition Period: Old pipeline tasks don't auto-unblock.** Pre-constitution tasks may remain BLOCKED even when all CRITICALs are resolved. Requires manual unblocking during transition. GL-004. The Constitutional Court auto-handles this once deployed.
- **GitHub Secrets are human-only.** CI/CD signing keys require manual entry into GitHub Secrets. No agent can bypass this. C-4 (Debug Keystore) pattern: DevOps creates keystore locally, human adds to Secrets. Flag as human-dependency in EPIC comments.
- **Triple-Chinese analysis paralysis.** When 3 MoA models disagree on a technical point (e.g., font support, keystore format), Lead Architect may loop indefinitely consulting references. Break the loop with a direct instruction: "STOP ANALYSIS. EXECUTE." Explicitly state that all gates are met and closure is the only remaining action. GL-008.
- **`echo` adds trailing newlines.** When setting GitHub Secrets via CLI, use `printf '%s' 'value' | gh secret set NAME` — NOT `echo 'value' | gh secret set NAME`. Trailing newlines silently corrupt secrets and cause CI failures. Discovered during C-4 keystore deployment.
- **Keystore format matters for CI.** Local builds may succeed with PKCS12 but CI/JDK may require JKS. If CI fails with "Tag number over 30" or keystore format errors, regenerate with `-storetype JKS`. DevOps must verify CI build after secret updates.
- **macOS `base64` needs `-i` flag.** `base64 -i file.keystore` — NOT `base64 file.keystore`. The latter fails silently or produces wrong output.
- **"STOP ANALYSIS. EXECUTE." — break the loop.** When Lead Architect's Triple-Chinese MoA loops indefinitely consulting references, post a comment on the EPIC: "⛔ STOP ANALYSIS. EXECUTE. All gates met. Close EPIC. NOW." Be direct. Be commanding. The plural models can deadlock each other.
- **Self-correction is a feature, not a bug.** Lead Architect discovered a chronological contradiction (Ruling #497 at 01:28 vs WONTFIX at 01:39). He self-corrected without human prompting. This is the constitution working — not a failure. Let it self-correct.
- **CI polling is the final wait.** After all code is pushed and secrets updated, Lead Architect legitimately waits for `gh run view` to confirm CI passes. This is not analysis paralysis — this is the final gate. Do not interrupt this phase.
- **Never save governance artifacts to project `app-spec/`.** Constitution, lessons, scripts all go to `~/.hermes/swarm/`. The first 9-round assembly made this mistake — saved to hermex_android project path. This was a 0/10 governance failure corrected by the user. System-wide means system-wide.

## References

- `references/constitution.yaml` — Full ratified governance constitution (8 articles)
- `references/multi-model-assembly.md` — 9-round constitutional assembly method
- `references/benchmark-pitfalls.md` — Benchmark design: model generation gap, workspace contamination, self-report hallucination
