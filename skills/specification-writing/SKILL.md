---
name: specification-writing
description: Write and maintain product specification files following the AI-Agent App Build Specification Pack framework. Covers the 18-file structure, iterative refinement process, depth requirements, and the NO PROCEDURAL REDUCTION rule. Use when creating or updating any app-spec file (00-19), writing PRDs, design systems, user flows, monetization specs, risk registers, or financial models.
tags: [specification, prd, product-discovery, design-system, user-flows, monetization, risks, financial-model, documentation]
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
- Creating or updating any file in `app-spec/` (00-19)
- Writing a PRD from product discovery
- Updating design systems, user flows, or monetization specs
- Building financial models or risk registers
- User asks to apply updates across multiple spec files
- User references the AI-Agent App Build Specification Pack

## Specification Pack Structure

The AI-Agent App Build Specification Pack defines 18 files. Not all apply to every project. For CarSah (local-first, no backend MVP):

| # | File | Purpose |
|---|---|---|
| 00 | Product Discovery | Problem, personas, value prop, MVP scope, feasibility, Go/No-Go |
| 01 | PRD | User stories with Gherkin, business rules, edge cases, glossary, traceability |
| 02 | Monetization & Entitlements | Feature matrix, pricing, trial mechanism, paywall architecture, abuse protection |
| 03 | User Flows & Navigation | Screen inventory, Mermaid navigation map, flow details, navigation rules |
| 04 | UI Design System | Color tokens, spacing, elevation, radius, typography, component specs, states, motion, accessibility, RTL/LTR |
| 05 | Data Model & ERD | Entities, relationships, field justifications |
| 07 | Flutter Architecture | Clean Architecture layers, provider graph, folder structure |
| 08 | Security & Privacy | Auth strategy, data sensitivity, permissions |
| 09 | Testing & Acceptance | Test pyramid, DoD, acceptance criteria |
| 10 | DevOps & Release | CI/CD, environments, release checklist |
| 11 | AI Agent Operating Contract | Agent rules, validation payload, traceability |
| 12 | Decision Log | Structured ADR format |
| 13 | Assumptions & Risks | Financial, data, UX, privacy, licensing, platform risks |
| 19 | Financial Model | Unit economics, LTV, break-even, founder targets, CAC, decision triggers |

## Depth Requirements Per File Type

### PRD (File 01)
Must include:
- User stories with Gherkin-style acceptance criteria (Given/When/Then)
- Business rules with unique IDs
- Edge cases with expected behavior
- Error messages (AR + EN where applicable)
- Glossary of domain terms
- Feature traceability matrix (Feature ID → User Story → Screen → Business Rule → Test Case)

### User Flows (File 03)
Must include:
- Screen inventory with IDs, tab/flow, MVP status, notes
- Single valid Mermaid navigation map inside ```mermaid fence
- Per-flow details with rules for each step
- Navigation rules with IDs

### UI Design System (File 04)
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

### Monetization (File 02)
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

### Risks (File 13)
Must include:
- Categorized risks with unique IDs
- Severity ratings
- Mitigation strategies
- References to governing files
- Product assumptions
- Technical assumptions
- Market assumptions

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
- **Losing detail on rewrite**: When writing a file from scratch, forgetting to include depth from prior versions. Always read the prior version first and preserve its structure.
- **Missing cross-references**: Spec files should link to each other. File 02 references File 19. File 13 references File 19. File 00 cross-references all others.
- **Stale contradictions**: When a decision changes (e.g., 2 vehicles → 5 vehicles), all references across all files must be updated. Use search to find stale mentions.
- **Mermaid syntax**: Always validate Mermaid blocks. One block per file. Inside ```mermaid fence. No orphan nodes.
