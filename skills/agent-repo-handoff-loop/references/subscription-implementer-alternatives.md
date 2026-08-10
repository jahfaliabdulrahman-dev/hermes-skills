# Subscription Implementer Alternatives (the implementer is a commodity)

General reference — the CLASS of tools that can fill the implementer slot of a
repo-mailbox loop at a FLAT monthly cost, replacing a metered-API implementer
with a one-line change in the coordinator. Nothing here is tool-specific; the
verified case study at the end is EVIDENCE for the class, not the subject.

## The class definition

Any tool that satisfies the five applicability conditions (see the main
SKILL.md "The implementer is a commodity" section):

1. **Shared repo access** — reads/writes git + files.
2. **Automatable** — a headless/CLI mode the coordinator can invoke
   (`-p`, `-q`, `--print`); a chat-only app breaks the loop. **This is the
   hard gate: no CLI, no seat at the table.**
3. **Follows a written protocol** — the mailbox message format.
4. **Verification from at least one side** — CI/tests per delivery.
5. **Human-readable state** — STATE.md stays readable by the founder.

Optional-but-valuable: a stateless invocation model (fresh context per wake,
truth read from the repo) — eliminates the session-corruption class entirely.

## The economic argument

- Metered API implementer: ~$25/mo, scales with usage, subject to provider
  outages (502/503 windows observed).
- Subscription implementer: flat monthly, top-tier model, same mailbox.
- The punchline: the same mailbox, a cheaper and stronger postman. The
  cost-per-capability curve collapses because the transport never changes.

## Verified case study (2026-08-10 — Moonshot Kimi Code CLI)

Facts verified from the official repo and docs at the time:

- Official GitHub `MoonshotAI/kimi-code` (MIT, ~6.2k stars): "Kimi Code CLI —
  The Starting Point for Next-Gen Agents"; installs via one curl command.
- Login: **Kimi Code OAuth (subscription) OR a Moonshot API key** — both paths
  supported; the CLI binary itself is free.
- **Non-interactive mode confirmed in the command reference:** `kimi -p
  "<prompt>"` runs a single prompt headless, streams to stdout, uses the auto
  permission policy (no human approval); `--output-format stream-json` for
  machine parsing; `--session/--continue` for resume; `--skills-dir` for
  custom skill directories; `--agent/--agent-file` for custom agents;
  `-m <model>` to pick the coding model alias.
- Subscription tiers (official kimi.com membership pricing): Moderato $19/mo
  (60 agent tasks/mo, 2 concurrent) · Allegretto $39/mo (150 tasks, 2
  concurrent) — **all paid tiers include "Kimi Code available"**; Allegro
  $99/mo · Vivace $199/mo scale credits up.
- Model: Kimi K3 — 2.8T-parameter open-weight multimodal reasoning model,
  1M context; Moonshot positions it for autonomous programming agents
  (platform.kimi.ai). API pricing (if metered instead): ~$3/M fresh input,
  $0.30/M cached input, $15/M output.
- Caveats to verify at purchase time: plans were in a transition ("Kimi and
  Kimi Code benefits will be separated" — new membership plans coming),
  current tiers showed "Join Waitlist"; usage is a monthly credit pool + a
  separate Kimi Code pool with WEEKLY quotas — a 24/7 loop must fit the
  weekly budget or stall mid-week.

## The standard experiment (do this BEFORE switching)

Run ONE small step on a side lane with the candidate implementer, the SAME
auditor, the same mailbox. Compare: rounds to APPROVE, number of STOPs,
evidence quality, real monthly cost. If it wins — switch with a founder DEC.
If it hits the subscription cap or fails the audit bar — keep the current
implementer, no loss. Two days answers the question.
