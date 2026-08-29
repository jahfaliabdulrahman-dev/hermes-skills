# Azdal Specification Pack — Full Structure (2026-07-18)

Ground truth from `~/Projects/<project>/app-spec/` (example: Azdal). 27 files across 22 slots.

## Slot 00 — Foundation Layer (6 files)

```
00_product_discovery.md          — Problem, personas, value prop, MVP scope
00_project_context.md             — Stack, dependencies, environment, conventions
00_project_overrides.md           — Deviations from standard spec pack
00_lessons_learned.md             — LL-001 through LL-011, DEC-001 through DEC-037
00_active_capabilities.md         — Current feature status inventory
00_agent_operating_playbook.md    — Profile-to-Kanban mappings, task templates
```

## Slots 01-19 — Core Specification

```
01_prd.md                          — User stories (Gherkin), business rules, glossary
02_monetization_entitlements.md    — Feature access matrix, pricing, paywall
03_user_flows_navigation.md        — Screen inventory, Mermaid navigation map
04_ui_design_system.md             — Color tokens, spacing, elevation, typography
05_data_model_erd.md               — Entities, relationships, field justifications
06_api_contract_openapi.yaml       — OpenAPI specification (YAML)
07_flutter_architecture.md         — Clean Architecture layers, provider graph
08_security_privacy.md             — Auth strategy, data sensitivity, permissions
09_testing_acceptance.md           — Test pyramid, DoD, acceptance criteria
10_devops_release_observability.md — CI/CD, environments, signing, observability
11_ai_agent_operating_contract.md  — Agent rules, validation payload, traceability
12_decision_log.md                 — Structured ADR (DEC-001 → DEC-050+)
13_assumptions_risks.md            — Categorized risks with IDs and mitigation
14_admin_panel_specification.md    — Admin dashboard, moderation, RBAC
15_support_operations_playbook.md  — On-call, incident response, escalation
16_implementation_backlog.md       — Prioritized queue, dependency chains
17_data_architecture_acid_constraints.md — Transaction boundaries, consistency
18_zero_trust_red_team_audit.md    — Attack vectors, penetration test results
19_financial_model_unit_economics.md — LTV, CAC, break-even, founder targets
```

## Slots 20-21 — Personal Build Extensions

```
20_personal_vision_and_goals.md    — Founder's reasons, coach tone, metrics
21_personal_build_plan.md          — Phased roadmap, account durability
```

## Slot Differences Between Projects

| Slot | Azdal | Hermex Android |
|------|-------|---------------|
| 06 | OpenAPI `.yaml` | Markdown `.md` |
| 14 | Admin Panel | Not used |
| 15 | Support Ops | Not used |
| 19 | Financial Model | Traceability Matrix |
| 20-21 | Personal Build | Not used |

## When to Use Which Structure

- **Full 22-slot (Azdal):** Consumer-facing app with monetization, admin panel, support ops, and personal vision
- **19-slot (Hermex):** Technical tool/app without monetization or personal build
- **14-slot (CarSah):** Local-first MVP without backend
