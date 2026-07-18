---
name: swarm-executive-controller
description: Control a 10-agent Flutter swarm via MCP Bridge — delegate tasks, monitor status, review reports, and issue corrections. Uses Router A (Triple Chinese MoA) for long tasks. For Claude Code or Kimi CLI as Executive Controller over Hermes Lead Architect.
version: 0.2.0
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

## Your 5 MCP Tools

When connected via the MCP Bridge to the Hermes Lead Architect, you have exactly 5 tools (4 delegation + 1 Kanban):

### 1. `lead_delegate` — Start a Task

```
lead_delegate(
  task: string,          # Clear task description in English
  profile?: string,      # Optional: target a specific profile
  priority?: "low" | "normal" | "high",
  callback?: string      # Optional: task ID to chain after completion
) → { delegation_id: string, estimated_tokens: number }
```

**How to write task descriptions:**
- Be specific about the deliverable — not "fix the app" but "Fix the subscription screen: the Cancel button does not call the API; check `subscription_provider.dart` line 142."
- Include file paths when known: "Modify `lib/features/chat/providers/chat_provider.dart` to add error retry logic for failed SSE streams."
- State constraints: "Must use existing `Platform.environment` pattern for credentials. Do NOT hardcode URLs."
- Reference decisions: "Follow DEC-024: LLM never computes. All math must be pure Dart."

**Example — Correct:**
```
lead_delegate(
  task: "Fix purchase confirmation insert: the 'purchases' table column is 'purchase_date' 
         (not 'date'). Modify lib/features/purchase/services/purchase_service.dart line 87 
         to use the correct column name. Verify with direct Supabase query after fix.",
  profile: "flutter-backend-db-architect"
)
```

**Example — Wrong:**
```
lead_delegate(task: "fix the purchase bug")
// Too vague. Which bug? Which file? The swarm will waste tokens guessing.
```

### 2. `lead_status` — Check Progress

```
lead_status(delegation_id: string) → {
  status: "pending" | "running" | "completed" | "failed",
  started_at: string?,
  completed_at: string?,
  current_phase: string?,
  tokens_used: number
}
```

**When to use:**
- After delegating, don't immediately check status — wait 30-60 seconds first
- Long tasks (>5 minutes): check every 2-3 minutes
- If status is "running" for >10 minutes, it may be stuck — use `lead_correct` to redirect

**Interpreting statuses:**
- `pending`: Lead hasn't started yet — Kanban queue, wait
- `running`: Active execution — swarm is working
- `completed`: Done — ready for `lead_report`
- `failed`: Error occurred — request report for error details

### 3. `lead_report` — Get Results

```
lead_report(delegation_id: string) → {
  summary: string,
  artifacts: [{ path: string, type: string }],
  decisions: [{ id: string, summary: string }],
  tests: { passed: number, failed: number, coverage?: number },
  verification: string,  // How the swarm verified this
  token_cost: { input: number, output: number, model: string }
}
```

**Review checklist:**
1. Read the summary first — does it match what you asked?
2. Check decisions — new DEC entries mean architecture changes
3. Check tests — zero tests is a red flag for the QA profile
4. Check verification — did they test on real device? (LL-010 rule)
5. Check token cost — unusually high cost means the task was poorly specified

### 4. `lead_correct` — Issue Corrections

```
lead_correct(
  delegation_id: string,
  feedback: string,
  mode: "append" | "replace" | "new_task"
) → { correction_id: string }
```

**Modes explained:**
- `append`: Add to existing work. "Add Arabic RTL validation to the form fields you just created."
- `replace`: The work is wrong. "You used `purchase_date` but the column is `purchased_at`. Redo the insert logic."
- `new_task`: The task is too big — split off a new delegation. "The error handling is correct. Now open a new task for the loading state animation."

**Correction best practices:**
- Always reference the original `delegation_id`
- Be specific about what's wrong and what's expected
- If the swarm made the same mistake twice, check your task description — it may be ambiguous
- One correction per issue — don't bundle 5 fixes in one `lead_correct`

### 5. Kanban Board (Read-Only)

These tools give you visibility into the swarm's workload WITHOUT interfering with the Lead Architect's distribution authority. You can SEE everything but you cannot MOVE, DELETE, or REPRIORITIZE tasks that aren't yours.

```
lead_kanban_view() → {
  columns: [
    { name: "Backlog", tasks: [{ id, title, assigned_to, priority, age }] },
    { name: "In Progress", tasks: [...] },
    { name: "Review", tasks: [...] },
    { name: "Done", tasks: [...] }
  ],
  bottlenecks: [{ profile: "flutter-qa-tester", queued: 5, warning: true }],
  swarm_health: "healthy" | "overloaded" | "idle"
}

lead_kanban_status(task_id?: string) → {
  task: { id, title, status, assigned_to, started_at, dependencies, blocks },
  chain: [{ task_id, status }]  // if part of a dependency chain
}
```

**When to use Kanban tools:**

| Situation | Tool | Action |
|-----------|------|--------|
| Before delegating | `lead_kanban_view` | Check if task already exists or related task is running |
| Swarm seems slow | `lead_kanban_view` | Check bottlenecks — is QA overwhelmed? |
| Delegation weird result | `lead_kanban_status` | Trace dependency chain — what blocked it? |
| Before canceling | `lead_kanban_status` | Check if task has dependent tasks that would break |

**Why Read-Only:**

| Operation | Allowed? | Reason |
|-----------|----------|--------|
| View board | ✅ | Situational awareness |
| View task status | ✅ | Trace dependencies |
| Cancel your own task | ✅ | Via `lead_correct(mode="new_task")` — not direct Kanban cancel |
| Reassign a task | ❌ | Lead Architect owns distribution |
| Reprioritize | ❌ | Lead decides what's urgent |
| Delete a task | ❌ | Audit trail — irreversible |
| Decompose a task | ❌ | Lead's core job — do not undermine SOUL |

**Bottleneck response protocol:**
1. If `swarm_health: "overloaded"` — do NOT delegate new tasks. Wait or check bottlenecks.
2. If a profile has 3+ queued tasks — consider delegating the NEW task to a different profile.
3. If all profiles are busy — batch your corrections instead of sending them one by one.
4. NEVER "clear the queue" — Kanban tasks exist for a reason. Only cancel your own.

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
```
lead_delegate(
  task: "[FULL TASK DESCRIPTION WITH CONSTRAINTS]",
  priority: "high"
)
→ Get delegation_id
→ Wait for status: "completed"
→ lead_report() 
→ Read the plan/spec the Lead generated
```

**Step 2 — Execute (Swarm):**
The Lead architect automatically decomposes the plan into parallel tasks, dispatches them to the 3-model MoA (DeepSeek + GLM + Qwen), and collects results.

**Step 3 — Correct (Sonnet 5):**
```
lead_correct(
  delegation_id: "<id>",
  feedback: "[SPECIFIC ISSUES FOUND]",
  mode: "replace"  // or "append" if minor
)
```

**Step 4 — Loop:**
Steps 2-3 repeat until the report passes review. Maximum 3 correction cycles — if still failing after 3 rounds, the task specification is likely flawed.

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

```bash
# Deploy a feature
lead_delegate(task="Add biometric auth to login screen. Use local_auth package. 
  Follow DEC-017: guest-first pattern — biometric should be optional, not required.")

# Fix a bug with specific file
lead_delegate(task="SSE stream disconnects after 30s idle. Check chat_provider.dart 
  line 156: add keepAlive ping every 25s. Verify with device test.",
  profile="flutter-state-engineer")

# Audit security before release
lead_delegate(task="Full zero-trust audit of RC6: check all API keys, RLS policies, 
  hardcoded credentials. Report findings with severity levels.",
  profile="flutter-zero-trust-auditor")

# Check what's happening
lead_status(id="del_abc123")

# Get the full report
lead_report(id="del_abc123")

# Redirect work
lead_correct(id="del_abc123", feedback="DEC-010 mandates soft delete. 
  You used hard DELETE. Change to is_deleted flag pattern.",
  mode="replace")
```

## Session Recovery

If you lose context between sessions, always:
1. Run `lead_swarm_status()` to see what's currently running
2. Check the Kanban board for pending tasks
3. Resume from the oldest incomplete delegation
4. Never re-delegate a task that's already running
