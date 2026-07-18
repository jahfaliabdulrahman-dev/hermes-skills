# CarSah Specification Pack Structure

Reference for creating/updating specification files in the CarSah project.

## File Inventory

| # | File | Status | Notes |
|---|---|---|---|
| 00 | product_discovery.md | Approved for PRD (v3.0) | 2 plan levels, 6-step setup, 5 vehicles, iOS TestFlight gate |
| 01 | prd.md | Draft (v3.0) | 7 user stories, Gherkin, 13 business rules, glossary, traceability |
| 02 | monetization_entitlements.md | Draft (v3.0) | Trial, grace period, paywall, analytics, abuse protection |
| 03 | user_flows_navigation.md | Draft (v3.0) | 20 screens, Mermaid map, optional audit |
| 04 | ui_design_system.md | Draft (v3.0) | Full MD3 tokens, component specs, states, motion, accessibility |
| 05 | data_model_erd.md | Not created | Pending |
| 07 | flutter_architecture.md | Not created | Pending |
| 08 | security_privacy.md | Not created | Pending |
| 09 | testing_acceptance.md | Not created | Pending |
| 10 | devops_release_observability.md | Not created | Pending |
| 11 | ai_agent_operating_contract.md | Not created | Pending |
| 12 | decision_log.md | Not created | Pending |
| 13 | assumptions_risks.md | Draft (v3.0) | 22 risks across 6 categories |
| 19 | financial_model_unit_economics.md | Approved for PRD (v2.4 extend to v3.0) | 19 sections, API policy, shared cache |

## Key v3.0 Decisions (Applied Across All Files)

1. 2 plan confidence levels: Smart Standard Plan (MVP/Free) + Vehicle-specific Precision Plan (V2 Pro)
2. User Custom is NOT a confidence level — it's Custom Plan Editing, V2 Pro Precision feature
3. 6-step setup: Brand → Model → Year → Energy → Transmission (Auto/Manual only) → Odometer (optional)
4. Audit is optional, never blocks Dashboard
5. 5 vehicles free, 6th blocked with neutral message, no paywall
6. iOS TestFlight mandatory before public MVP launch
7. Saudi workshop terms first, formal in explanations
8. Oil display: brand + viscosity + liters + "مع السيفون" + source label
9. Every technical value must label its source
10. No VIN/API/license scan in MVP or V2 Free
11. Smart Standard Plan engine oil: 7,500 km (conservative, not OEM)
12. Pro primary value drivers: Precision Plan, Custom Plan Editing, QR, Cloud, Passport/Transfer
13. API financial policy: V2 Pro only, ≤150 SAR/month target, shared config cache
14. Total-first cost: totalCostSar required, knownCostItems optional, unallocatedCostSar computed

## Cross-Reference Rules

- File 00 cross-references: 02, 03, 04, 13, 19
- File 01 cross-references: 00, 02, 03, 04, 19
- File 02 cross-references: 19, 00, 01
- File 03 cross-references: 01, 04
- File 04 cross-references: 00, 01, 03
- File 13 cross-references: 19, 00
- File 19 cross-references: 00, 02
