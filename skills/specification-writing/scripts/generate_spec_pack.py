#!/usr/bin/env python3
"""Spec Pack Generator — creates the full 25-file structure with headers.

Usage:
    python3 generate_spec_pack.py /path/to/project PROJECT_NAME

Creates app-spec/ with all 25 files, each with the mandatory header and
core section skeleton. Fill in the content per the specification-writing
skill. This is the PREMIUM template suite (not the free SKILL.md).
Built 2026-08-03 as part of Spec Pack Premium; validated by generating a
fresh pack and verifying it with verify_spec_pack.py.
"""
import os
import sys
from datetime import date

HEADER = """# {num} — {title}

> **Document ID:** SPEC-{num}-{project}
> **Version:** 1.0.0
> **Status:** Draft
> **Stage:** {stage_emoji} — {stage_name}
> **Owner:** {owner}
> **Last Updated:** {today}
> **Cross-Reference:** [00_project_stages.md](00_project_stages.md){xref}

---

"""

FILES = [
    # (num, title, stage_emoji, stage_name, xref, body)
    ("00", "Project Stages & File Index", "🗺️", "الخريطة", "", """
## 📋 FILE INDEX

| # | File | Stage | Purpose |
|---|------|:-----:|---------|
| 00 | `00_project_stages.md` | 🗺️ | Project roadmap + this index |
| 01 | `01_product_discovery.md` | 1 🟢 | Problem, personas, value, Go/No-Go |
| 02 | `02_project_context.md` | 1 🟢 | Stack, environment, constraints |
| 03 | `03_project_overrides.md` | 1 🟢 | Deviations from standard template |
| 04 | `04_monetization_entitlements.md` | 2 🟡 | Pricing, tiers, paywall |
| 05 | `05_financial_model.md` | 2 🟡 | Unit economics, LTV, CAC, break-even |
| 06 | `06_assumptions_risks.md` | 2 🟡 | Risk register, assumptions |
| 07 | `07_user_flows_navigation.md` | 3 🟠 | Screen map, navigation, Mermaid |
| 08 | `08_design_prototype.md` | 3 🟠 | Colors, fonts, wireframes, prototype, RTL |
| 09 | `09_prd.md` | 4 🔵 | User stories, Gherkin, business rules |
| 10 | `10_data_model_erd.md` | 4 🔵 | Entities, relationships, schema |
| 11 | `11_api_contract.md` | 4 🔵 | OpenAPI/GraphQL endpoints |
| 12 | `12_flutter_architecture.md` | 4 🔵 | Clean Architecture, Riverpod, folders |
| 13 | `13_security_privacy.md` | 4 🔵 | Auth, encryption, threat model |
| 14 | `14_testing_acceptance.md` | 4 🔵 | Test strategy, DoD |
| 15 | `15_devops_release.md` | 4 🔵 | CI/CD, signing, observability |
| 16 | `16_ai_agent_contract.md` | 4 🔵 | Agent rules, boundaries, handoffs |
| 17 | `17_data_architecture_acid.md` | 4 🔵 | Transactions, consistency, migrations |
| 18 | `18_implementation_backlog.md` | 4 🔵 | Prioritized features, estimates |
| 19 | `19_decision_log.md` | 5 🟣 | ADR (DEC-NNN), rationale |
| 20 | `20_lessons_learned.md` | 5 🟣 | LL-NNN, root cause, prevention |
| 21 | `21_zero_trust_red_team.md` | 5 🟣 | Attack vectors, penetration results |
| 22 | `22_admin_panel.md` | 6 ⚫ | Admin dashboard, moderation |
| 23 | `23_support_operations.md` | 6 ⚫ | On-call, incident response |
| 24 | `24_active_capabilities.md` | 6 ⚫ | Living inventory of what works |
| 25 | `25_swarm_operating_playbook.md` | 6 ⚫ | Profiles, Kanban, EPIC gates |

## 🚦 STAGE STATUS

| Stage | Status | Files | Notes |
|-------|:------:|-------|-------|
| 1-الفكرة | ⬜ | 01, 02, 03 | |
| 2-الجدوى | ⬜ | 04, 05, 06 | Blocked until Stage 1 ✅ |
| 3-التصميم | ⬜ | 07, 08 | Blocked until Stage 2 ✅ |
| 3.5-جاهزية البناء | ⏳ | (inside 16 & 18) | Blocked until Stage 3 ✅ — no standalone file |
| 4-MVP | ⬜ | 09–18 | Blocked until Stage 3 ✅ AND Stage 3.5 ✅ |
| 5-التطوير | ⬜ | 19–21 | Blocked until Stage 4 ✅ |
| 6-الإنتاج | ⬜ | 22–25 | Blocked until Stage 5 ✅ |

## 🧭 GATES

| Gate | Opens when | Guards |
|------|-----------|--------|
| IDEA_GATE | 01–03 complete | |
| FEASIBILITY_GATE | 04–06 complete | |
| **DESIGN_GATE** | **07–08 complete + prototype approved** | **no code before this closes** |
| **BUILD_READINESS_GATE (3.5)** | DESIGN_GATE closed + dependency graph (18) + build sequence locked (18) + debt-vs-feature policy defined (16) | |
| MVP_GATE | 09–18 complete + DESIGN_GATE **and** BUILD_READINESS_GATE both closed | |
| ITERATE_GATE | MVP shipped + real feedback | |
| PRODUCTION_GATE | 22–25 ready + launch checklist | |

Status legend: ⬜ Not started | 🔄 In Progress | ✅ Complete | ⏳ Blocked | 🚨 Missing (gap!)
"""),
    ("01", "Product Discovery", "1 🟢", "الفكرة", ", [02_project_context.md](02_project_context.md), [03_project_overrides.md](03_project_overrides.md)", """
## Problem Statement

<!-- What real problem does this solve? Who feels it? How bad is it? -->

## Personas

### Persona 1 — [Name]
- **Background:**
- **Pain points:**
- **Goals:**
- **Current workaround:**

## Value Proposition

<!-- One sentence: for WHO, WHAT, so THAT. -->

## MVP Scope

- **In scope:**
- **Out of scope (explicitly):**

## Feasibility & Go/No-Go

- [ ] Problem validated with real users
- [ ] Solution technically feasible with chosen stack
- [ ] Decision: **GO / NO-GO** (date)
"""),
    ("02", "Project Context", "1 🟢", "الفكرة", ", [01_product_discovery.md](01_product_discovery.md), [03_project_overrides.md](03_project_overrides.md)", """
## Tech Stack

| Layer | Choice | Version | Rationale |
|-------|--------|:-------:|-----------|
| Frontend | | | |
| State | | | |
| Persistence | | | |
| Backend | | | |
| Auth | | | |

## Dependencies

<!-- Locked versions, upgrade policy, known breaking changes -->

## Environment & Constraints

- **Target platforms:**
- **Min OS versions:**
- **Offline requirements:**
- **RTL/bilingual requirements:**

## Conventions

- Naming, folder structure, commit style, code review rules
"""),
    ("03", "Project Overrides", "1 🟢", "الفكرة", ", [01_product_discovery.md](01_product_discovery.md), [02_project_context.md](02_project_context.md)", """
## Deviations from Standard Spec Pack

| # | Standard Rule | Override | Rationale |
|---|---------------|----------|-----------|
| 1 | | | |

## Project-Specific Rules

<!-- Rules that apply ONLY to this project -->
"""),
    ("04", "Monetization & Entitlements", "2 🟡", "دراسة الجدوى", ", [05_financial_model.md](05_financial_model.md), [06_assumptions_risks.md](06_assumptions_risks.md)", """
## Feature Access Matrix

| Feature | Free | Pro | Enterprise |
|---------|:----:|:---:|:----------:|
| | ✅ | ✅ | ✅ |

## Pricing & Tiers

- **Free tier:**
- **Pro tier:** price, billing cycle
- **Trial mechanism:** length, grace period

## Entitlement Source of Truth

<!-- Where does the client check what a user can access? Server-side? Cached? -->

## Paywall Architecture

- Triggers, upgrade prompts, paywall screens
- **Abuse protection:** device limits, account sharing detection
"""),
    ("05", "Financial Model", "2 🟡", "دراسة الجدوى", ", [04_monetization_entitlements.md](04_monetization_entitlements.md), [06_assumptions_risks.md](06_assumptions_risks.md)", """
## Unit Economics

| Metric | Value | Assumption |
|--------|:-----:|------------|
| ARPU | | |
| Monthly churn | | |
| Gross margin | | |
| CAC by channel | | |

## LTV Calculation

<!-- LTV = ARPU × gross margin × (1/churn). Show the math with assumptions. -->

## Break-Even Analysis

- Fixed costs, variable costs, break-even users

## Decision Triggers

<!-- When to pivot / kill / scale. Concrete numbers, not vibes. -->
"""),
    ("06", "Assumptions & Risks", "2 🟡", "دراسة الجدوى", ", [04_monetization_entitlements.md](04_monetization_entitlements.md), [05_financial_model.md](05_financial_model.md)", """
## Risk Register

| ID | Category | Risk | Severity | Likelihood | Mitigation |
|----|----------|------|:--------:|:----------:|------------|
| R-001 | Product | | | | |

## Assumptions

### Product Assumptions
### Technical Assumptions
### Market Assumptions
"""),
    ("07", "User Flows & Navigation", "3 🟠", "التصميم والهوية", ", [08_design_prototype.md](08_design_prototype.md)", """
## Screen Inventory

| ID | Screen | Tab/Flow | MVP? | Notes |
|----|--------|----------|:----:|-------|
| S-001 | | | ✅ | |

## Navigation Map

```mermaid
graph TD
    A[Home] --> B[Screen B]
```

## Flow Details

### Flow: [Name]
1. Entry point:
2. Steps:
3. Exit points:
4. Rules:

## Navigation Rules

- NR-001: ...
"""),
    ("08", "Design Prototype", "3 🟠", "التصميم والهوية", ", [07_user_flows_navigation.md](07_user_flows_navigation.md)", """
## §1 Logo Architecture

- **App Mark (1024×1024):** <!-- Canva → Claude workflow -->
- **Full Combination Logo:** <!-- Auth, About, PDF headers -->

## §2 Color Architecture (60-30-10)

| Proportion | Role | Light | Dark |
|:----------:|------|-------|------|
| 60% | Surface | | |
| 30% | Primary | | |
| 10% | Accent/CTA | | |

**Status colors:** Success / Error / Warning (separate from brand)

## §3 Platform Assets

- flutter_launcher_icons: ^0.14.4
- flutter_native_splash: ^2.4.8
- Adaptive icon config + notification icons

## §4 Screen-by-Screen Assets

| Screen | Asset | Notes |
|--------|-------|-------|
| Splash | App Mark only | No text |
| Onboarding | Vector illustrations | |
| Auth | Full logo | Trust moment |

## §5 Core Design Requirements

- Spacing (4dp MD3), elevation, radius, typography (Arabic-first: Cairo)
- Component specs, empty/error states, motion, accessibility (WCAG)
- RTL/LTR validation for every screen
- Wireframes (low-fi minimum) + interactive prototype link
- User journey walkthrough + design testing notes
"""),
    ("09", "PRD", "4 🔵", "MVP", ", [10_data_model_erd.md](10_data_model_erd.md), [11_api_contract.md](11_api_contract.md), [12_flutter_architecture.md](12_flutter_architecture.md), [00_project_stages.md](00_project_stages.md)", """
## User Stories (Gherkin)

### US-001: [Story title]
```gherkin
Feature: [Feature]
  Scenario: [Happy path]
    Given [context]
    When [action]
    Then [expected result]

  Scenario: [Edge case]
    Given [context]
    When [action]
    Then [expected result]
```

## Business Rules

| ID | Rule | Enforcement |
|----|------|-------------|
| BR-001 | | |

## Edge Cases & Error Messages

| Case | Behavior | Message (AR / EN) |
|------|----------|-------------------|
| | | |

## Glossary

| Term | Definition |
|------|------------|
| | |

## Traceability Matrix

| Feature | User Story | Screen | Business Rule | Test Case |
|---------|-----------|--------|---------------|-----------|
| | | | | |
"""),
    ("10", "Data Model ERD", "4 🔵", "MVP", ", [09_prd.md](09_prd.md), [17_data_architecture_acid.md](17_data_architecture_acid.md)", """
## Entities

### Entity: [Name]
| Field | Type | Constraints | Justification |
|-------|------|-------------|---------------|
| id | | PK | |

## Relationships

```mermaid
erDiagram
    ENTITY1 ||--o{ ENTITY2 : has
```

## Schema

<!-- SQL / Isar / Supabase DDL -->
"""),
    ("11", "API Contract", "4 🔵", "MVP", ", [09_prd.md](09_prd.md), [13_security_privacy.md](13_security_privacy.md)", """
## Endpoints

### `METHOD /path`
- **Auth:** Bearer token
- **Request:**
```json
{}
```
- **Response 200:**
```json
{}
```
- **Errors:** 400, 401, 403, 404, 429, 500

## Auth Headers & Refresh Flow

## Rate Limits
"""),
    ("12", "Flutter Architecture", "4 🔵", "MVP", ", [09_prd.md](09_prd.md), [10_data_model_erd.md](10_data_model_erd.md), [16_ai_agent_contract.md](16_ai_agent_contract.md)", """
## Clean Architecture Layers

- **Core:** models, services, utils
- **Features:** feature modules with data/domain/presentation
- **App:** routing, theme, DI

## Provider/Notifier Graph

## Hook System Architecture (MANDATORY)

1. **11 Hook Types** — which apply (PreRequest, PostResponse, RouteGuard, InputSanitize, FileGuard, SessionGate...)
2. **4 Progression Levels** — current level per type
3. **Configuration** — hooks.yaml, HookChain orchestrator
4. **Security Chain** — veto order, 14 injection patterns, skiplist
5. **Self-Healing Audit** — hook grading report (A-F)

**Verification (Level 1 Safety):**
- [ ] Every user input passes InputSanitize
- [ ] Every file path validated against FileGuard
- [ ] Every HTTP request has Bearer token
- [ ] Every 401 triggers refresh + retry exactly once
- [ ] Every protected route has RouteGuard

## Screen State Machine (MANDATORY)

- [ ] `ScreenState<T>` in every AsyncValue<T> screen
- [ ] No per-screen _buildLoadingState/_buildErrorState/_buildEmptyState
- [ ] 5 widgets in lib/core/ui/screen_states/: AppLoading, AppError, AppEmpty, AppOffline, AppEmptySearch
- [ ] AppError always has onRetry
- [ ] AppLoading uses skipLoadingOnRefresh

## Unified Error Handler (MANDATORY)

- [ ] ErrorHandler.show() is the ONLY error path
- [ ] No raw ScaffoldMessenger.showSnackBar for errors
- [ ] All 10 ErrorType values have AR+EN messages
- [ ] ErrorLogger.log() on every error
- [ ] ErrorSeverity matches display mechanism

## Structured Logger (MANDATORY)

- [ ] AppLogger replaces ALL debugPrint
- [ ] AppLogger.of('Category') — no manual prefixes
- [ ] 4 levels: debug, info, warn, error
- [ ] LogBuffer.query() runtime filterable
- [ ] LogPersister writes error+ to file

## Folder Structure

```
lib/
├── core/
│   ├── services/
│   ├── ui/
│   │   └── screen_states/
│   └── utils/
├── features/
│   └── <feature>/
│       ├── data/
│       ├── domain/
│       └── presentation/
└── app/
```

## Routing
"""),
    ("13", "Security & Privacy", "4 🔵", "MVP", ", [11_api_contract.md](11_api_contract.md), [21_zero_trust_red_team.md](21_zero_trust_red_team.md)", """
## Auth Strategy

## Data Sensitivity Classification

| Data | Classification | Protection |
|------|:-------------:|------------|
| | | |

## Permissions & Encryption

## Threat Model

| Threat | Vector | Mitigation |
|--------|--------|------------|
| | | |
"""),
    ("14", "Testing & Acceptance", "4 🔵", "MVP", ", [09_prd.md](09_prd.md), [12_flutter_architecture.md](12_flutter_architecture.md)", """
## Test Pyramid

| Layer | Tools | Coverage Target |
|-------|-------|:---------------:|
| Unit | | |
| Widget | | |
| Integration | | |
| E2E/Device | | |

## Definition of Done

- [ ] Code compiles, analyze clean
- [ ] Tests pass (count ≥ baseline)
- [ ] Device-verified on real hardware
- [ ] Git committed + pushed

## Acceptance Criteria per Epic

## Device Targets
"""),
    ("15", "DevOps & Release", "4 🔵", "MVP", ", [14_testing_acceptance.md](14_testing_acceptance.md), [25_swarm_operating_playbook.md](25_swarm_operating_playbook.md)", """
## CI/CD Pipelines

| Pipeline | Trigger | Jobs | Artifacts |
|----------|---------|------|-----------|
| | push/PR | | |

## Environments

- dev / staging / prod — URLs, credentials ownership

## Signing & Release Checklist

## Observability

- Logs, crash reporting, analytics, alerts
"""),
    ("16", "AI Agent Contract", "4 🔵", "MVP", ", [12_flutter_architecture.md](12_flutter_architecture.md), [18_implementation_backlog.md](18_implementation_backlog.md), [25_swarm_operating_playbook.md](25_swarm_operating_playbook.md)", """
## Agent Rules

- Rule 1: ...
- Rule 2: ...

## Validation Payload Format

```json
{
  "project": "",
  "task": "",
  "files": [],
  "exit_criteria": []
}
```

## Traceability & Handoff Protocols

## Boundaries

<!-- What agents must NEVER do -->

## Technical-Debt-vs-Feature Policy (Stage 3.5)

<!-- LOCKED once. When mid-build choice arises: fix debt or ship feature? The policy decides, not a live debate. -->
"""),
    ("17", "Data Architecture & ACID", "4 🔵", "MVP", ", [10_data_model_erd.md](10_data_model_erd.md)", """
## Transaction Boundaries

## Consistency Guarantees

## Migration Strategy

- Isar schema migrations / Supabase migrations — silent where possible
"""),
    ("18", "Implementation Backlog", "4 🔵", "MVP", ", [09_prd.md](09_prd.md), [16_ai_agent_contract.md](16_ai_agent_contract.md)", """
## Prioritized Backlog

| ID | Item | Priority | Effort | Depends On |
|----|------|:--------:|:------:|------------|
| B-001 | | | | |

## Dependency Graph (Stage 3.5 — LOCKED)

<!-- Graph across ALL backlog items. Once locked, build order is NOT renegotiated feature-by-feature. -->

## Build Sequence (ONE, locked)

```mermaid
graph LR
    A[B-001] --> B[B-002]
```
"""),
    ("19", "Decision Log", "5 🟣", "التطوير والتحسين", ", [20_lessons_learned.md](20_lessons_learned.md), [00_project_stages.md](00_project_stages.md)", """
## ADR Format

### DEC-001: [Decision title]
- **Date:** YYYY-MM-DD
- **Context:** Why now, what problem
- **Decision:** What was chosen
- **Rationale:** Trade-offs considered
- **Linked files:** [file](file)
- **Rejection reasons (if applicable):**
"""),
    ("20", "Lessons Learned", "5 🟣", "التطوير والتحسين", ", [19_decision_log.md](19_decision_log.md)", """
## Lesson Format

### LL-001: [Lesson title]
- **Date discovered:** YYYY-MM-DD
- **Stage:** N
- **Root cause:**
- **Prevention rule (machine-enforceable where possible):**
- **Cross-reference:** DEC-NNN
- **Source file path:**
"""),
    ("21", "Zero Trust Red Team", "5 🟣", "التطوير والتحسين", ", [13_security_privacy.md](13_security_privacy.md)", """
## Attack Vectors

| ID | Vector | Result | Severity | Status |
|----|--------|--------|:--------:|:------:|
| AT-001 | | | | |

## Penetration Test Results

## Security Assumptions Challenged

<!-- Every assumption in File 13 gets challenged here. -->
"""),
    ("22", "Admin Panel", "6 ⚫", "النشر والإنتاج", ", [23_support_operations.md](23_support_operations.md)", """
## Admin Dashboard

## Moderation Tools

## Analytics Views

## Role-Based Access
"""),
    ("23", "Support Operations", "6 ⚫", "النشر والإنتاج", ", [22_admin_panel.md](22_admin_panel.md)", """
## On-Call Procedures

## Incident Response

## Escalation Paths

## FAQ Maintenance
"""),
    ("24", "Active Capabilities", "6 ⚫", "النشر والإنتاج", ", [00_project_stages.md](00_project_stages.md)", """
## Feature Status — Living Inventory

| Feature | Status | Verified On | Notes |
|---------|:------:|:-----------:|-------|
| | ✅/🔄/🚨 | | |

> Update continuously. This is the ACCURATE current state — not aspirational.
"""),
    ("25", "Swarm Operating Playbook", "6 ⚫", "النشر والإنتاج", ", [16_ai_agent_contract.md](16_ai_agent_contract.md), [18_implementation_backlog.md](18_implementation_backlog.md)", """
## Profile-to-Responsibility Matrix

| Profile | Responsibility | Never |
|---------|---------------|-------|
| Lead Architect | Orchestrator, decomposes EPICs | Writes app code |
| | | |

## Task Dispatch Templates

### Lite (≤2 files, Route A)
```
quick_task(task="...", files="path1,path2")
```

### Full (EPIC, Route B)
```
/goal
## Objective
## Context
## Exit Criteria
```

## Orchestrator Anti-Temptation Rules

1. No "Phases & Worker Assignments" in prompts
2. Lead Architect decomposes — you don't
3. project_path mandatory for Route B

## EPIC Lifecycle Gates

## Guardian Protocol (SCSI)
"""),
]

CANONICAL = {
    "00": "00_project_stages.md",
    "01": "01_product_discovery.md",
    "02": "02_project_context.md",
    "03": "03_project_overrides.md",
    "04": "04_monetization_entitlements.md",
    "05": "05_financial_model.md",
    "06": "06_assumptions_risks.md",
    "07": "07_user_flows_navigation.md",
    "08": "08_design_prototype.md",
    "09": "09_prd.md",
    "10": "10_data_model_erd.md",
    "11": "11_api_contract.md",
    "12": "12_flutter_architecture.md",
    "13": "13_security_privacy.md",
    "14": "14_testing_acceptance.md",
    "15": "15_devops_release.md",
    "16": "16_ai_agent_contract.md",
    "17": "17_data_architecture_acid.md",
    "18": "18_implementation_backlog.md",
    "19": "19_decision_log.md",
    "20": "20_lessons_learned.md",
    "21": "21_zero_trust_red_team.md",
    "22": "22_admin_panel.md",
    "23": "23_support_operations.md",
    "24": "24_active_capabilities.md",
    "25": "25_swarm_operating_playbook.md",
}


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 generate_spec_pack.py /path/to/project PROJECT_NAME")
        sys.exit(1)

    project_path = sys.argv[1]
    project = sys.argv[2].upper()
    app_spec = os.path.join(project_path, "app-spec")
    os.makedirs(app_spec, exist_ok=True)

    today = date.today().isoformat()
    owner = os.environ.get("SPEC_OWNER", "Product Owner")

    for num, title, emoji, stage, xref, body in FILES:
        header = HEADER.format(
            num=num, title=title, project=project,
            stage_emoji=emoji, stage_name=stage,
            owner=owner, today=today, xref=xref,
        )
        filename = CANONICAL[num]
        with open(os.path.join(app_spec, filename), "w", encoding="utf-8") as f:
            f.write(header + body.strip() + "\n")
        print(f"  ✓ {filename}")

    print(f"\n✅ Spec Pack created in {app_spec} — {len(FILES)} files")
    print("Fill each file per the specification-writing skill. Do NOT reduce depth.")


if __name__ == "__main__":
    main()
