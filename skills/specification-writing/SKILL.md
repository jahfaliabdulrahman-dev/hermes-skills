---
name: specification-writing
description: Write and maintain product specification files following the AI-Agent App Build Specification Pack framework. Covers the 22-slot structure (00–21), 27+ files including the 6-file Slot-00 foundation, depth requirements, and the NO PROCEDURAL REDUCTION rule. Use when creating or updating any app-spec file, writing PRDs, design systems, user flows, monetization specs, risk registers, financial models, swarm playbooks, or personal build plans.
tags: [specification, prd, product-discovery, design-system, user-flows, monetization, risks, financial-model, documentation, swarm, zero-trust]
version: "2.0.0"
---

# Specification Writing

## Governing Rule — NO PROCEDURAL REDUCTION

**ABSOLUTE RULE:** Never condense, summarize, shortcut, or skip detail when creating or updating specification files, PRDs, architecture docs, or any project artifact. Every rewrite must preserve ALL prior depth. Procedural reduction = loss of engineering knowledge = unacceptable.

When updating a spec file:
- Never replace detailed content with summaries
- Never collapse user stories into bullet-point descriptions
- Never remove Gherkin scenarios, edge cases, or error messages
- Never strip UI design system detail (spacing, elevation, radius, states, motion, accessibility)
- Never remove business rules, glossaries, or traceability matrices
- Add new decisions ON TOP of existing depth, not replacing it

## Trigger

Use this skill when:
- Creating or updating any file in `app-spec/` (slots 00–21)
- Writing a PRD from product discovery
- Updating design systems, user flows, or monetization specs
- Building financial models or risk registers
- User asks to apply updates across multiple spec files
- User references the AI-Agent App Build Specification Pack

## Specification Pack Structure — 22 Slots, 27+ Files

Evolved from 18 files to 22 slots across 3 production projects (Azdal, Hermex Android, CarSah). Slot 00 is the foundation layer with 6 files. Slots 20–21 are personal-build extensions.

### 🧭 Slot 00 — Foundation Layer (6 files)

| File | Purpose |
|------|---------|
| `00_product_discovery.md` | Problem, personas, value prop, MVP scope, feasibility, Go/No-Go |
| `00_project_context.md` | Stack, dependencies, environment, constraints, conventions |
| `00_project_overrides.md` | Deviations from standard spec pack, project-specific rules |
| `00_lessons_learned.md` | All LL-NNN and DEC-NNN entries, cross-project patterns |
| `00_active_capabilities.md` | Current feature status — the accurate, living inventory of what works |
| `00_swarm_operating_playbook.md` | Profile-to-Kanban mappings, task templates, orchestrator rules |

### 🏗️ Slots 01–19 — Core Specification

| Slot | File | Purpose |
|------|------|---------|
| 01 | PRD | User stories with Gherkin (Given/When/Then), business rules, edge cases, error messages (AR+EN), glossary, traceability matrix |
| 02 | Monetization & Entitlements | Feature matrix per tier, pricing, trial mechanism, paywall architecture, abuse protection |
| 03 | User Flows & Navigation | Screen inventory with IDs, Mermaid navigation map, flow details, navigation rules |
| 04 | UI Design System | Color tokens (hex), spacing (4dp MD3), elevation, radius, typography, component specs, states, motion, accessibility, RTL/LTR |
| 05 | Data Model & ERD | Entities, relationships, field justifications, schema |
| 06 | API Contract | OpenAPI/GraphQL spec, endpoints, request/response schemas, auth headers |
| 07 | Flutter Architecture | Clean Architecture layers, provider/notifier graph, folder structure, routing |
| 08 | Security & Privacy | Auth strategy, data sensitivity classification, permissions, encryption |
| 09 | Testing & Acceptance | Test pyramid, DoD, acceptance criteria, device targets |
| 10 | DevOps & Release | CI/CD pipelines, environments, signing, release checklist, observability |
| 11 | AI Agent Operating Contract | Agent rules, validation payload format, traceability, handoff protocols |
| 12 | Decision Log | Structured ADR format (DEC-NNN), rationale, date, linked files |
| 13 | Assumptions & Risks | Categorized risks with IDs, severity, mitigation, product/technical/market assumptions |
| 14 | Admin Panel Specification | Admin dashboard, moderation tools, analytics views, role-based access |
| 15 | Support Operations Playbook | On-call procedures, incident response, escalation paths, FAQ maintenance |
| 16 | Implementation Backlog | Prioritized feature queue, dependency chains, effort estimates |
| 17 | Data Architecture & ACID Constraints | Transaction boundaries, consistency guarantees, migration strategy |
| 18 | Zero Trust Red Team Audit | Attack vectors, penetration test results, security assumptions challenged |
| 19 | Financial Model | Unit economics, LTV, CAC, break-even, founder targets, decision triggers |

### 👤 Slots 20–21 — Personal Build Extensions

| Slot | File | Purpose |
|------|------|---------|
| 20 | Personal Vision & Goals | Founder's real reasons, emotional truth, coach tone philosophy, metrics that matter |
| 21 | Personal Build Plan | Phased roadmap, hackathon-independent priorities, account durability, tool-calling router |

## Slot Order & Dependencies

```
00 (Foundation: 6 files)
    ↓
01 PRD  ←  02 Monetization  ←  19 Financial Model
    ↓
03 User Flows  ←  04 UI Design System
    ↓
05 Data Model  ←  06 API Contract
    ↓
07 Architecture  ←  08 Security  ←  09 Testing
    ↓
10 DevOps  ←  11 Agent Contract  ←  12 Decision Log
    ↓
13 Risks  ←  14 Admin  ←  15 Support
    ↓
16 Backlog  ←  17 Data ACID  ←  18 Zero Trust
    ↓
20 Personal Vision  ←  21 Personal Build Plan
```

## Depth Requirements Per File Type

### PRD (Slot 01)
Must include:
- User stories with Gherkin-style acceptance criteria (Given/When/Then)
- Business rules with unique IDs
- Edge cases with expected behavior
- Error messages (AR + EN where applicable)
- Glossary of domain terms
- Feature traceability matrix (Feature ID → User Story → Screen → Business Rule → Test Case)

### User Flows (Slot 03)
Must include:
- Screen inventory with IDs, tab/flow, MVP status, notes
- Single valid Mermaid navigation map inside ```mermaid fence
- Per-flow details with rules for each step
- Navigation rules with IDs

### UI Design System (Slot 04)
Must include:
- Color tokens with hex values and usage (light AND dark where defined)
- Spacing scale (based on 4dp MD3 grid)
- Elevation levels
- Border radius tokens
- Typography scale with all properties
- Component specs: buttons, text fields, cards, state-specific layouts
- Empty/error state designs
- Motion specifications
- Accessibility requirements
- RTL/LTR rules
- Source/provenance labeling rules

### Monetization (Slot 02)
Must include:
- Feature access matrix per tier
- Trial mechanism details
- Grace period rules
- Entitlement source of truth
- Paywall architecture with triggers
- Backend validation rules (if applicable)
- Analytics events
- Abuse protection
- Forward compatibility rules

### Risks (Slot 13)
Must include:
- Categorized risks with unique IDs
- Severity ratings
- Mitigation strategies
- References to governing files
- Product assumptions
- Technical assumptions
- Market assumptions

### Lessons Learned (Slot 00)
Must include:
- Sequential LL-NNN numbering
- Date discovered, stage, files affected
- Root cause analysis
- Prevention rule (machine-enforceable where possible)
- Cross-reference to DEC-NNN entries
- Source file path

### Decision Log (Slot 12)
Must include:
- Sequential DEC-NNN numbering
- Date, context, decision
- Rationale with trade-offs considered
- Linked files and LL-NNN references
- Rejection reasons when applicable

### Swarm Operating Playbook (Slot 00)
Must include:
- Profile-to-responsibility matrix
- Task dispatch templates (Lite/Full)
- Orchestrator anti-temptation rules
- EPIC lifecycle gates
- Guardian protocol (SCSI integration)

## Iterative Refinement Process

Specification files evolve through versions:
1. Initial draft — capture all known decisions
2. User review — feedback, corrections, new ideas
3. Apply updates — add depth, fix contradictions
4. Repeat 2-3 until user approves
5. Version bump and status change

Each version bump must preserve all prior content. Only remove content when explicitly directed by user or when contradictions require replacement (and even then, document the change).

## Pitfalls

- **Procedural reduction**: The most common and most serious error. Creating condensed summaries when asked to update specs. The user will reject these immediately.
- **Slot-00 sprawl**: Slot 00 has 6 files — never merge them. Each has a distinct role. Lessons ≠ Capabilities ≠ Context.
- **Losing detail on rewrite**: When writing a file from scratch, forgetting to include depth from prior versions. Always read the prior version first and preserve its structure.
- **Missing cross-references**: Spec files should link to each other. Slot 02 references Slot 19. Slot 13 references Slot 19. Slot 00 cross-references all others.
- **Stale contradictions**: When a decision changes (e.g., 2 vehicles → 5 vehicles), all references across all files must be updated. Use search to find stale mentions.
- **Mermaid syntax**: Always validate Mermaid blocks. One block per file. Inside ```mermaid fence. No orphan nodes.
- **LL vs DEC separation**: Lessons (LL) go in `00_lessons_learned.md`. Decisions (DEC) go in `12_decision_log.md`. Never mix them.
- **Personal build leakage**: Slots 20–21 contain personal/private content. These are project-specific and not part of the public spec pack template.
