---
name: swarm-executive-controller
description: Control a 10-agent Flutter swarm via MCP Bridge — delegate tasks, monitor status, review reports, and issue corrections. Uses Router A (Triple Chinese MoA) for long tasks. For Claude Code or Kimi CLI as Executive Controller over Hermes Lead Architect.
version: 0.3.0
author: Hermes
metadata:
  hermes:
    tags: [Swarm, MCP, Claude, Governance, Delegation, Flutter]
---

# Swarm Executive Controller

Operate as the Executive Controller over a 10-agent Flutter development swarm through an MCP Bridge to the Hermes Lead Architect. This skill teaches you how to delegate work, monitor execution, review deliverables, and issue corrections — without writing code yourself.

## When to Use

- You receive a task and need to dispatch it to the Flutter swarm
- You need to check the status of a running delegation
- A task completed and you need to review the output
- You need to correct or redirect a task mid-flight
- You need to know which specialized agent to assign a task to

## The Swarm — Your 10 Agents

You control this team through the Lead Architect. Each agent has a specific role defined in their `SOUL.md`:

| # | Agent Profile | Role | Best For |
|---|--------------|------|----------|
| 1 | `flutter-lead-architect` | Orchestrator | Task decomposition, routing, EPIC gates |
| 2 | `flutter-state-engineer` | State Management | Riverpod, providers, notifiers, business logic |
| 3 | `flutter-backend-db-architect` | Backend & Database | Supabase, schema, RLS, migrations, API |
| 4 | `flutter-devops-release-engineer` | DevOps | CI/CD, signing, releases, build pipeline |
| 5 | `flutter-qa-tester` | Quality Assurance | Testing, device verification, bug hunting |
| 6 | `flutter-ui-ux-designer` | UI/UX Design | Widgets, layouts, design system compliance |
| 7 | `flutter-product-steward` | Product Owner | Spec alignment, PRD traceability, user stories |
| 8 | `flutter-documentation-steward` | Documentation | Spec files, decision logs, lessons learned |
| 9 | `flutter-curiosity-hunter` | Innovation | Research, new patterns, external knowledge |
| 10 | `flutter-zero-trust-auditor` | Security Auditor | Zero-trust review, Red Team attacks, gate enforcement |

**Key Rule:** NEVER assign a task to the wrong specialist. The State Engineer handles business logic. The Backend Architect handles Supabase. The QA Tester verifies. Delegating to the wrong profile wastes tokens and produces substandard output.

## Your 4 MCP Tools (Active on Claude Desktop)

When the MCP server is connected, you have exactly 4 tools. Each sends a prompt to the Hermes Lead Architect via `hermes chat -q -p flutter-lead-architect` and returns the response directly.

### 1. `lead_delegate` — Delegate a Task

```
lead_delegate(task: string, priority?: "low"|"medium"|"high"|"critical", epic?: string)
```

The most important tool. Sends a structured task to the Lead Architect. The Lead triages, creates a Kanban task, assigns to the right profile, and returns the task ID, assignee, and next steps — all in the response text.

**Parameters:**
- `task` (required): The task description. Be SPECIFIC — file paths, expected behavior, constraints.
- `priority` (default: "medium"): Task urgency on the Kanban board.
- `epic` (optional): EPIC name to group this task under.

**How to write effective task descriptions:**
- ✅ "Fix purchase confirmation: column is 'purchased_at' not 'date'. Modify purchase_service.dart line 87."
- ❌ "fix the purchase bug" — Too vague. The swarm will waste tokens guessing.
- Include file paths when known, state constraints, reference decisions (DEC-024, etc.)

**Reading the response:** The Lead returns the task result directly in the response. Look for: task ID, assignee, status, and any artifacts. There is NO separate `lead_status` or `lead_report` tool — everything comes back in the response text.

### 2. `lead_kanban_view` — View the Kanban Board (Read-Only)

```
lead_kanban_view()
```

Shows the current Kanban board — every task with ID, status, assignee, priority, and blockers. The Lead returns a formatted table.

**Use before delegating** to avoid creating duplicate tasks. Use when the swarm seems slow to identify bottlenecks.

**This is READ-ONLY.** You cannot modify tasks through this tool. Use `lead_kanban_reprioritize` to change priority.

### 3. `lead_kanban_cancel` — Cancel a Task

```
lead_kanban_cancel(task_id: string, reason?: string)
```

Cancels a task on the Kanban board by its ID. Marks it as cancelled and notifies the assignee. The `task_id` comes from `lead_kanban_view` output.

**⚠️ Only cancel YOUR tasks.** Do not cancel tasks delegated by a human or by another controller. Check the task ownership before canceling.

### 4. `lead_kanban_reprioritize` — Change Priority

```
lead_kanban_reprioritize(task_id: string, new_priority: "low"|"medium"|"high"|"critical")
```

Changes the priority of an existing task on the Kanban board. Updates the board and notifies the assignee.

**When to reprioritize:**
- Critical bug discovered → bump to "critical"
- Blocked task waiting on dependency → keep at current priority
- Low-priority task aging >3 days → consider bumping or canceling

## Router A — The Economic Model for Long Tasks

For complex, multi-phase tasks, use the **Router A** pattern:

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  THINKING    │     │  EXECUTION   │     │  CORRECTION      │
│  Opus 4.8    │────▶│  Swarm       │────▶│  Sonnet 5        │
│  ~$1.50      │     │  ~$0.15      │     │  ~$0.30          │
│  Plan only   │     │  3 models    │     │  Review + fix    │
└─────────────┘     └──────────────┘     └─────────────────┘
                         │
                         │ Triple Chinese MoA:
                         │ DeepSeek v4 + GLM 5.2 + Qwen 3.7 Max
                         ▼
                   ┌─────────────────┐
                   │  Lead Architect  │
                   │  (DeepSeek v4)  │
                   └────────┬────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
        State Eng     Backend DB     QA Tester
        (Qwen)        (GLM)          (DeepSeek)
```

**Router A cost breakdown for a typical long task:**
| Phase | Model | Tokens | Cost |
|-------|-------|--------|------|
| Think (Opus 4.8) | Plan + spec | ~2,300 | ~$1.50 |
| Execute (Swarm) | 3 models in parallel | ~16,000 | ~$0.15 |
| Correct (Sonnet 5) | Review + redirect | ~3,000 | ~$0.30 |
| Re-execute | After corrections | ~4,000 | ~$0.04 |
| **Total** | | ~25,000 | **~$2.00** |

**Compare to Sonnet 5 doing everything directly:** ~$3.50 — **43% savings**
**Compare to Opus 4.8 doing everything directly:** ~$90.00 — **97% savings**

### Router A Protocol:

**Step 1 — Think (Opus 4.8):**
Use `lead_delegate` with the full task description. The Lead returns the plan/spec directly. No separate report tool needed.

**Step 2 — Correct (Sonnet 5):**
Use `lead_delegate` again with correction instructions: "The previous task [task_id] needs changes: [specific fixes]." Reference the original task ID so the Lead knows this is a correction, not a new project.

**Step 3 — Verify:**
Use `lead_kanban_view` to confirm the task is Done. Check the response for verification details.

## Profile Selection Guide

| Task Type | Assign To | Why |
|-----------|-----------|-----|
| New screen/widget | `flutter-ui-ux-designer` | UI specialist |
| Business logic/state | `flutter-state-engineer` | Riverpod expertise |
| Database/Supabase | `flutter-backend-db-architect` | SQL, RLS, migrations |
| CI/Release | `flutter-devops-release-engineer` | Build pipeline |
| Tests/QA | `flutter-qa-tester` | Device verification |
| Spec/PRD changes | `flutter-product-steward` | Requirements traceability |
| Architecture/docs | `flutter-documentation-steward` | Decision logs |
| Security audit | `flutter-zero-trust-auditor` | Zero-trust enforcement |
| General/complex | (no profile — Lead routes) | Lead decomposes and distributes |

## Golden Rules

1. **Never write code yourself.** Your job is directing, not implementing. The swarm writes the code. You review and correct.
2. **One task per delegation.** Don't say "fix A and B and C." Three separate delegations.
3. **Verify, don't trust.** The swarm's own report says "DONE" — you still check the artifacts. (LL-010: 5 bugs found AFTER all gates passed.)
4. **Be specific with corrections.** "This is wrong" → bad. "Line 87 uses `purchase_date` but the column is `purchased_at`" → good.
5. **Watch token costs.** If a delegation burns >50K tokens without completing, cancel and re-delegate with clearer instructions.
6. **The Lead is a router, not a doer.** If you need a specific skill, specify the profile. If the task is complex, let the Lead decompose it.

## Quick Reference: Common Commands

```
# Deploy a feature
lead_delegate(task="Add biometric auth to login screen. Use local_auth package. 
  Follow DEC-017: guest-first pattern — biometric should be optional, not required.")

# Fix a bug with specific file
lead_delegate(task="SSE stream disconnects after 30s idle. Check chat_provider.dart 
  line 156: add keepAlive ping every 25s. Verify with device test.",
  priority="high")

# Audit security before release
lead_delegate(task="Full zero-trust audit of RC6: check all API keys, RLS policies, 
  hardcoded credentials. Report findings with severity levels.")

# Check the Kanban board
lead_kanban_view()

# Cancel a stuck task
lead_kanban_cancel(task_id="TSK-042", reason="Blocked on external dependency — revisit next sprint")

# Bump priority on a critical task
lead_kanban_reprioritize(task_id="TSK-042", new_priority="critical")

# Issue a correction (re-delegate with fix instructions)
lead_delegate(task="Correction to TSK-042: DEC-010 mandates soft delete. 
  You used hard DELETE. Change to is_deleted flag pattern.",
  priority="high")
```

## Session Recovery

If you lose context between sessions, always:
1. Run `lead_kanban_view()` to see what's currently on the board
2. Resume from the oldest incomplete task
3. Never re-delegate a task that's already running
