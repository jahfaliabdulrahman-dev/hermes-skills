---
name: swarm-executive-controller
description: Control a 10-agent Flutter swarm via MCP Bridge using Route A (direct) and Route B (EPIC). For Claude Code as Executive Controller over Hermes Lead Architect.
version: 1.0.0
author: Hermes
metadata:
  hermes:
    tags: [Swarm, MCP, Claude, Governance, Delegation, Flutter, Route-A, Route-B]
---

# Swarm Executive Controller

Operate as the Executive Controller over a 10-agent Flutter development swarm through an MCP Bridge to the Hermes Lead Architect. Covers the two-route decision tree: Route A (small tasks → direct execution) and Route B (EPICs → Lead Architect → Kanban → Swarm). Includes pre-flight Ultra verification protocol.

## When to Use

- You receive a task and need to decide: Route A (direct) or Route B (swarm)?
- You need to delegate an EPIC to the Lead Architect
- You need to check the Kanban board before delegating
- A task completed and you need to issue corrections
- You need to verify all profiles are on Ultra reasoning before an EPIC

## 🔀 DECISION TREE — READ FIRST

**BEFORE calling any tool, ask:**

```
Is this task SMALL?
  ≤2 files, same folder, bug fix, config change, simple method addition

  ├── YES → ROUTE A: quick_task
  │         Send directly to Sulaiman (default profile).
  │         NO Kanban. NO swarm. NO orchestration.
  │
  └── NO  → ROUTE B: lead_delegate
            This is an EPIC: 3+ files, new feature, new screen,
            architecture change, data model change.
            Goes to Lead Architect → Kanban → 10-agent Swarm.
```

---

## 🟢 ROUTE A — Direct Execution (small tasks)

**When:** Bug fix ≤2 files, config change, simple method, search/analyze, typo fix, color change.

**Tool:** `quick_task`

```
quick_task(task: string, files?: string)
```

**Format:**
```
Task: [one-line description]
File(s): [exact file paths, comma-separated]
What to change: [specific change]
Acceptance: flutter analyze clean + flutter test pass
```

**Examples:**
✅ `quick_task(task="Fix typo 'recieve' → 'receive' in chat_screen.dart line 45", files="lib/features/chat/chat_screen.dart")`
✅ `quick_task(task="Change primary button color token to match brand navy #001F5E", files="lib/app/theme.dart")`
✅ `quick_task(task="Add null check for user.name in profile_header.dart line 32")`

**❌ NOT Route A (send to Route B instead):**
- Adding a new screen
- Modifying 3+ files across different folders
- Changing the data model
- New feature that needs design + backend + state

---

## 🔴 ROUTE B — EPIC via Lead Architect + Kanban Swarm

**When:** EPIC — 3+ files, multi-domain, new feature, new screen, data model change.

**Tool:** `lead_delegate`

```
lead_delegate(task: string, priority?: "low"|"medium"|"high"|"critical", epic?: string)
```

**Pre-flight (ALWAYS before Route B):**

Sonnet MUST verify profiles are on Ultra reasoning before any EPIC:
```
lead_ultra_check()
```
This checks all 10 profiles. If any are NOT on Ultra, the Lead will set them. Only proceed to Route B AFTER all profiles confirm Ultra.

### /goal Template for Route B

Use this EXACT format in the `task` parameter of `lead_delegate`:

```
/goal

## Objective
[One line: what to build/fix/deploy]

## Context
- Project: [name] — [absolute path]
- Spec pack: app-spec/
- What exists: [brief]
- What doesn't work: [brief]

## Specific Defects (if bugfix)
1. [File:line — exact issue]

## Phases & Worker Assignments
- Phase 1: Product Steward — verify scope against PRD
- Phase 2: UI/UX Designer — screen specs (parallel with Backend)
- Phase 2: Backend DB Architect — data model (parallel with Designer)
- Phase 3: State Engineer — implement (after Phase 2)
- Phase 4: QA Tester — validate (after Phase 3)
- Phase 5: Zero-Trust Auditor — hostile audit (on-demand, critical features)
- Phase 6: DevOps Engineer — build + release (after QA PASS)
- Guardian: SCSI Hunter — continuous scan throughout

## Workers to SKIP
- [List any profiles NOT needed]

## Exit Criteria (Machine-Checkable)
- [ ] flutter analyze: 0 errors
- [ ] flutter test: all pass, count ≥ baseline
- [ ] Git pushed to remote
- [ ] APK built and smoke-tested on real Android device
- [ ] GitHub Release published with 'latest' tag
- [ ] SCSI Guardian: APPROVED

## File Paths
- Spec pack: [absolute-path]/app-spec/
- Source: [absolute-path]/lib/
- Tests: [absolute-path]/test/
```

---

## Your 6 MCP Tools (v1.1)

### Route A — Direct

| Tool | Profile | Purpose |
|------|---------|---------|
| `quick_task` | `default` (Sulaiman) | Small task ≤2 files — no Kanban, no swarm |

### Route B — Swarm

| Tool | Profile | Purpose |
|------|---------|---------|
| `lead_delegate` | `flutter-lead-architect` | EPIC → Kanban → 10-agent swarm |
| `lead_kanban_view` | `flutter-lead-architect` | Read-only Kanban board view |
| `lead_kanban_cancel` | `flutter-lead-architect` | Cancel your task on the board |
| `lead_kanban_reprioritize` | `flutter-lead-architect` | Change task priority |

### Pre-flight

| Tool | Purpose |
|------|---------|
| `lead_ultra_check` | Verify all 10 profiles on Ultra reasoning before EPIC |

---

## The 10 Swarm Agents

| # | Profile | Role | Best For |
|---|---------|------|----------|
| 1 | `flutter-lead-architect` | Orchestrator | Route B only — decomposes EPICs, routes tasks, enforces gates |
| 2 | `flutter-product-steward` | Product | SPEC, GATE, PRD, acceptance, scope |
| 3 | `flutter-ui-ux-designer` | Design | DESIGN, UX, UI, theme, layout, component, screen |
| 4 | `flutter-backend-db-architect` | Backend | DATA, SCHEMA, API, model, contract, endpoint, migration |
| 5 | `flutter-state-engineer` | Developer | FIX, FEAT, BUG, implement, change, refactor |
| 6 | `flutter-qa-tester` | QA | QA, TEST, VERIFY, validate, smoke, acceptance |
| 7 | `flutter-zero-trust-auditor` | Security | AUDIT, SECURITY, zero-trust, attack, vulnerability |
| 8 | `flutter-devops-release-engineer` | DevOps | BUILD, RELEASE, APK, CI/CD, deploy, publish |
| 9 | `flutter-documentation-steward` | Documentation | DOCS, DOCUMENTATION, lessons, README, spec, traceability |
| 10 | `flutter-curiosity-hunter` | SCSI Guardian | GUARDIAN, SCSI, HUNT, HUNTER, scan — continuous, closes with epic |

**⛔ Key Rule:** The Lead Architect is an ORCHESTRATOR, not a coder. Never give him a small task (Route A material) — he will either over-engineer it with Kanban cards or write code himself, violating his boundaries.

---

## Writing Corrections (Route B follow-up)

To correct a completed task, use `lead_delegate` again with the correction instructions:

```
lead_delegate(task="Correction to [task_id]: [specific fix needed]. 
  File: [path]. Change: [exact change].", priority="high")
```

The Lead recognizes this as a correction when you reference the original task ID.

---

## Profile Selection Table

| Keywords in Title | Assignee |
|------------------|----------|
| BUILD, RELEASE, APK, deploy, publish | `flutter-devops-release-engineer` |
| FIX, FEAT, BUG, implement, change, refactor | `flutter-state-engineer` |
| QA, TEST, VERIFY, validate, smoke | `flutter-qa-tester` |
| DESIGN, UX, UI, theme, layout, component, screen | `flutter-ui-ux-designer` |
| DATA, SCHEMA, API, model, contract, endpoint, migration | `flutter-backend-db-architect` |
| AUDIT, SECURITY, zero-trust, attack, vulnerability | `flutter-zero-trust-auditor` |
| DOCS, DOCUMENTATION, lessons, README, spec, traceability | `flutter-documentation-steward` |
| SPEC, GATE, PRD, acceptance, scope | `flutter-product-steward` |
| GUARDIAN, SCSI, HUNT, HUNTER, scan | `flutter-curiosity-hunter` |
| EPIC, DECOMPOSE, ORCHESTRATE, DECISION | `flutter-lead-architect` |

---

## Golden Rules

1. **Decide BEFORE delegating.** Route A (≤2 files) or Route B (EPIC)? Wrong route = wasted tokens.
2. **Ultra before EPIC.** Always `lead_ultra_check` before any `lead_delegate`.
3. **Never write code yourself.** You direct. The swarm executes. You verify.
4. **One EPIC per delegation.** Don't combine unrelated features.
5. **Verify, don't trust.** Swarm says DONE — you check anyway (LL-010).
6. **Route A is NOT for the Lead Architect.** Small tasks go to `quick_task` (default profile). Never send a 2-file bug fix to the Lead.
7. **The Lead is a router, not a doer.** If you need implementation, that's State Engineer. If you need orchestration, that's Lead.

## Session Recovery

1. Run `lead_kanban_view()` to see current board state
2. Resume from oldest incomplete task
3. Never re-delegate a task that's already running
