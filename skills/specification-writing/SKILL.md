---
name: specification-writing
description: Write and maintain product specification files following the AI-Agent App Build Specification Pack framework. Covers the 25-file, 6-stage sequential structure (00–25), mandatory file header template with Cross-Reference traceability, depth requirements, and the NO PROCEDURAL REDUCTION rule. Use when creating or updating any app-spec file, writing PRDs, design systems, user flows, monetization specs, risk registers, financial models, swarm playbooks.
tags: [specification, prd, product-discovery, design-system, user-flows, monetization, risks, financial-model, documentation, swarm, zero-trust]
version: "3.4.0"
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

## Governing Rule — SKILL CONTENT SEPARATION

> **Hard-learned:** 2026-07-26. The user rejected newly-created skills because their SKILL.md files mixed general patterns with project-specific audit data (mentioning Hermex, CarSah, Azdal by name). A skill that references specific projects cannot be reused by future projects.

**ABSOLUTE RULE:** SKILL.md is the universal pattern — it MUST remain project-agnostic. Project-specific context belongs ONLY in reference files, never in the skill body.

**Separation contract:**

| File | Contains | Must NOT contain |
|------|----------|-----------------|
| `SKILL.md` | Universal patterns, contracts, templates, anti-patterns | Project names, file paths to specific repos, line numbers, DEC numbers from specific projects |
| `references/project-landscape.md` | Snapshot of current project state: exact file paths, line numbers, DEC entries, migration priorities | Universal pattern definitions (those belong in SKILL.md) |
| `references/authoritative-sources.md` | Curated excerpts from Flutter/Dart official docs, library APIs, versioned references | Project-specific observations |

**When writing SKILL.md:**
- Use "typical Flutter project" not "Hermex Android"
- Use "API-heavy app" not "Hermex pattern"
- Use "hundreds of debugPrint calls" not "483 debugPrint calls"
- Templates, examples, and code snippets must use generic class names

**When a new project is audited:**
1. The universal pattern (SKILL.md) remains UNCHANGED
2. Append a new section to `references/project-landscape.md`
3. If a pattern deficiency is found that applies universally, update SKILL.md generically

## Governing Rule — EXTERNAL SOURCE GROUNDING

> **Established:** 2026-07-26. Before finalizing any architectural skill, ground it in official Flutter/Dart documentation using `find-docs` (Context7 CLI).

**Workflow:**
1. Use `npx ctx7@latest library` to resolve relevant library IDs (dio, riverpod, go_router, logger, dart, flutter)
2. Use `npx ctx7@latest docs` to query official documentation for canonical patterns
3. Curate findings into `references/authoritative-sources.md` with library IDs, key evidence, and relevance summaries
4. Cross-reference SKILL.md patterns against sources — flag any divergence
5. If sources reveal a pattern is wrong or incomplete, fix SKILL.md BEFORE saving

## Governing Rule — THE TWO-REIN RULE (Creativity vs Quality)

> **Established:** 2026-07-30. Adopted from YC/Anthropic insights (Boris Cherny, Claude Code) and adapted through founder-led strategic discussion. The core insight: frontier models perform best with minimal scaffolding in creative domains, but still require strict guardrails in domains where errors are costly. The wisdom is knowing when to loosen and when to tighten.

**The principle:** Not all specification files are equal. Some require creative freedom; others require deterministic correctness. Applying the same governance level everywhere either suffocates innovation (all reins tight) or burns tokens on unverified output (all reins loose).

### Three-Zone Classification

Every file in the Spec Pack falls into one of three zones:

| Zone | Files | Reins | Governance |
|:----:|:-----:|:-----:|------------|
| **🎨 Creative** | 07 (User Flows), 08 (Design) | **Loose** | Human aesthetic judgment; minimal automated gates |
| **⚖️ Mixed**    | 09 (PRD), 12 (Architecture) | **Tight on logic, loose on UI** | Lint + review; template required |
| **🔒 Quality**  | 10 (Data), 11 (API), 13 (Security), 15 (DevOps), 17 (ACID), 18 (Backlog) | **Tight** | Automated verification gates (tests, lint, schema validation); skills enforced |

### Stage 3: Dual Paths

Stage 3 is the ONLY stage with two execution paths. The founder chooses based on whether the design direction is already known:

| Path | When | Model Role | Founder Role |
|:----:|------|------------|--------------|
| **🐢 Normal** | App Mark exists (Canva), colors defined | Claude generates derivative assets from App Mark | Active: reviews, adjusts incrementally |
| **⚡ Fast** | No constraints — "surprise me" | Claude reads Stage 1+2, autonomously produces BOTH 07+08 | Passive: receives, judges (accept/reject/modify) |

**Both paths produce files 07+08. The Normal Path is unchanged. Stage 3.5 is MANDATORY for both.**

### Governance Gradient

| Stage | Writes | Judges | Reins |
|:-----:|--------|--------|:-----:|
| 1–2 (Idea & Feasibility) | Founder + Model | Founder | Tight |
| 3 (Design) | Model | Founder (taste) | **Loose** |
| 3.5 (Build Readiness) | Model (founder's intent) | **Third party** | **Tightest** |
| 4+ (MVP & Production) | Model (skills enforced) | Auto tests + Founder | Tight |

**Key insight:** Stage 3.5 is the governance bottleneck — model writes the build plan, third party reviews it adversarially, founder receives the verdict. Mirrors Bun (YC 2026): autonomous agents ran 11 days, adversarial review caught 3 critical bugs before merge.

## Tooling — Premium Generator & Verifier

A paid/companion tooling suite exists for this skill (Spec Pack Premium, built 2026-08-03). Two scripts, both tested:

- `scripts/generate_spec_pack.py` — generates the full 26-file pack (00–25) with mandatory headers + section skeletons into `<project>/app-spec/`. Usage: `python3 scripts/generate_spec_pack.py /path/to/project PROJECT_NAME`
- `scripts/verify_spec_pack.py` — compliance gate (exit-code): checks file presence, header integrity, content markers, per-stage readiness. Usage: `python3 scripts/verify_spec_pack.py /path/to/project` (exit 0 = compliant, 1 = gaps).

The generator embeds the 4 mandatory architecture patterns (Hook System, Screen State Machine, Error Handler, Logger) with their verification checklists directly into File 12. The verifier is CI-usable. These were validated against a real project (correctly detected Azdal's legacy 22-slot structure as non-compliant with the 25-file system).

## Trigger

Use this skill when:

---

## Project Stages — Six Gates

Every project MUST pass through these 6 stages in order. A flaw in any stage affects all subsequent stages. No stage begins until the previous stage is fully complete.

| Stage | Name | Gate | Rule |
|:-----:|------|:----:|------|
| 1 🟢 | **الفكرة (Idea)** | IDEA_GATE | Problem, personas, value prop, context. No code. |
| 2 🟡 | **دراسة الجدوى (Feasibility)** | FEASIBILITY_GATE | Monetization, financials, risks. Prove viability before design. |
| 3 🟠 | **التصميم والهوية (Design)** | DESIGN_GATE | User flows, design system, wireframes, prototype. **No code before this closes.** |
| 3.5 🟤 | **جاهزية البناء (Build Readiness)** | BUILD_READINESS_GATE | Lock dependency graph + one build sequence (18) + technical-debt-vs-feature policy (16). **No code until this closes.** Deliberately lightweight — a dependency graph + one sequence + one policy, not Gantt/CPM. |
| 4 🔵 | **MVP** | MVP_GATE | PRD, data model, architecture, security, testing, backlog. Build minimum. **Requires DESIGN_GATE AND BUILD_READINESS_GATE both closed.** |
| 5 🟣 | **التطوير والتحسين (Iteration)** | ITERATE_GATE | Decision log, lessons learned, red team audit. Improve from real feedback. |
| 6 ⚫ | **النشر والإنتاج (Production)** | PRODUCTION_GATE | Admin panel, support ops, capabilities inventory, swarm playbook. Go live. |

Each stage has a status: ✅ Complete | 🔄 In Progress | ⏳ Blocked (waiting on previous stage) | 🚨 Missing (gap!)

---

## Specification Pack Structure — 25 Files (Sequential 00–25)

Evolved from the 22-slot v2.0 system into a 6-stage, 25-file sequential structure. Every file is numbered by its position in the project lifecycle — open `00`, read the index, follow the numbers.

### 🗺️ File 00 — The Map

`00_project_stages.md` is the FIRST file created and the FIRST file read by any agent. It contains:

1. **📋 FILE INDEX** — Complete table of all 25 files: number, filename, stage, purpose
2. **🚦 STAGE STATUS** — Which stages are complete, in progress, blocked, or missing
3. **Gates** — What must be true before each stage can begin

### Stage 1: الفكرة 🟢 — Files 01–03

| # | File | Purpose |
|---|------|---------|
| 01 | `01_product_discovery.md` | Problem, personas, value proposition, MVP scope, feasibility, Go/No-Go decision |
| 02 | `02_project_context.md` | Tech stack, dependencies, environment, constraints, conventions, **which persistence/backend stack this project uses** |
| 03 | `03_project_overrides.md` | Deviations from standard spec pack, project-specific rules |

### Stage 2: دراسة الجدوى 🟡 — Files 04–06

| # | File | Purpose |
|---|------|---------|
| 04 | `04_monetization_entitlements.md` | Feature access matrix per tier, pricing, trial mechanism, paywall architecture, abuse protection |
| 05 | `05_financial_model.md` | Unit economics, LTV, CAC, break-even, founder targets, decision triggers |
| 06 | `06_assumptions_risks.md` | Categorized risks with IDs, severity, mitigation, product/technical/market assumptions |

### Stage 3: التصميم والهوية 🟠 — Files 07–08

| # | File | Purpose |
|---|------|---------|
| 07 | `07_user_flows_navigation.md` | Screen inventory with IDs, Mermaid navigation map, flow details, navigation rules |
| 08 | `08_design_prototype.md` ✨ | **Everything design:** Color tokens (hex), spacing (4dp MD3), elevation, radius, typography, component specs, states, motion, accessibility, RTL/LTR, wireframes, interactive prototype, user journey walkthrough, design testing notes |

### Stage 3.5: جاهزية البناء 🟤 — Build Readiness (no new file numbers)

> **⚠️ MANDATORY for BOTH Stage 3 paths (Normal and Fast).** This stage has NO standalone file. Its content lives inside two existing Stage 4 files — `16_ai_agent_contract.md` and `18_implementation_backlog.md` — but MUST be written and locked BEFORE any Stage 4 code begins. It cannot be completed before the design settles (Stage 3 must close first).

**Governance for Stage 3.5:**
- **Who writes:** The model — based on the founder's stated intent and the completed Stage 1-3 files
- **Who judges:** A **third party** (independent adversarial reviewer) — NOT the founder alone
- **Why third party:** This is the single highest-leverage quality gate. After creative freedom in Stage 3, the build plan must be challenged by an external reviewer. This mirrors the Bun case study (YC 2026): 64 agents ran autonomously for 11 days, but adversarial human review caught 3 critical bugs before merge
- **Reins:** Tightest in the entire governance gradient — external validation before any code

| Location | Content |
|----------|---------|
| `18_implementation_backlog.md` (new section) | Dependency graph across all backlog items + **one locked build sequence** — deliberately one, not multi-variant. Once locked, the build order is NOT renegotiated feature-by-feature. |
| `16_ai_agent_contract.md` (new section) | Explicit technical-debt-vs-feature policy — when a mid-build choice arises between fixing debt or shipping a feature, the policy (not a live debate) decides. |

**Why this exists:** Past build attempts hit repeated mid-build negotiation ("which feature first?", "fix this debt now or later?") despite having a spec pack — because the pack had priorities but no locked order and no debt policy. Stage 3.5 closes that gap once, before coding, instead of re-litigating it feature by feature. Deliberately lightweight (a dependency graph + one sequence + one policy) rather than formal construction-style scheduling (Gantt/CPM), which would reintroduce the process-overhead trap.

### Stage 4: MVP 🔵 — Files 09–18

| # | File | Purpose |
|---|------|---------|
| 09 | `09_prd.md` | User stories with Gherkin (Given/When/Then), business rules, edge cases, error messages (AR+EN), glossary, traceability matrix |
| 10 | `10_data_model_erd.md` | Entities, relationships, field justifications, schema |
| 11 | `11_api_contract.md` | OpenAPI/GraphQL spec, endpoints, request/response schemas, auth headers |
| 12 | `12_flutter_architecture.md` | Clean Architecture layers, provider/notifier graph, folder structure, routing, **Hook System Architecture** (§ mandatory), **Screen State Machine** (§ mandatory), **Unified Error Handler** (§ mandatory), **Structured Logger** (§ mandatory) |

### Structured Logger — Depth Requirement (File 12)

> **Effective:** 2026-07-26
> **Source:** `flutter-app-logger` skill
> **Governance Rule:** Every Flutter project MUST use `AppLogger` with at least 4 levels (debug, info, warn, error). Raw `debugPrint` for application logging is prohibited. `LogBuffer` must be accessible at runtime for debugging. Error/fatal levels must persist to file via `LogPersister`.

**Verification Gate:**
- [ ] `AppLogger` replaces all `debugPrint` calls (483 total across projects)
- [ ] Every class uses `AppLogger.of('Category')` — no manual prefixes
- [ ] At least 4 log levels in use: debug, info, warn, error
- [ ] `LogBuffer.query()` works at runtime — filterable by level and category
- [ ] `LogPersister` writes error+ entries to `app_log.txt`

Cross-reference:
- `flutter-app-logger` skill
- `flutter-error-handler` skill — `ErrorLogger.log()` uses `AppLogger.error()` internally

### Unified Error Handler — Depth Requirement (File 12)

> **Effective:** 2026-07-26
> **Source:** `flutter-error-handler` skill
> **Governance Rule:** Every Flutter project MUST use `ErrorHandler.show(context, error)` as the single entry point for all user-facing errors. Raw `ScaffoldMessenger.of(context).showSnackBar(SnackBar(...))` scattered across screens is prohibited. All errors must be classified through `ErrorClassifier.classify()` before display.

**Verification Gate:**
- [ ] `ErrorHandler.show()` is the ONLY way errors reach the user
- [ ] No raw `ScaffoldMessenger.of(context).showSnackBar()` for error display
- [ ] All 10 `ErrorType` values have AR + EN user messages in `ErrorMessageMapper`
- [ ] `ErrorLogger.log()` called on every error with stack trace
- [ ] `ErrorSeverity` matches display mechanism (success→green, error→red+retry, critical→dialog)

Cross-reference:
- `flutter-error-handler` skill — the authoritative implementation reference
- `flutter-screen-state-machine` skill — `AppError` widget pairs with `ErrorHandler` for full-screen errors

### Screen State Machine — Depth Requirement (File 12)

> **Effective:** 2026-07-26
> **Source:** `flutter-screen-state-machine` skill
> **Governance Rule:** Every Flutter project MUST use the unified `ScreenState<T>` widget pattern. Per-screen `_buildLoadingState` / `_buildErrorState` / `_buildEmptyState` methods are prohibited. The 5 standard widgets (`AppLoading`, `AppError`, `AppEmpty`, `AppOffline`, `AppEmptySearch`) must live in `lib/core/ui/screen_states/`.

**Verification Gate:**
- [ ] `ScreenState<T>` used in every screen that consumes `AsyncValue<T>`
- [ ] No per-screen `_buildLoadingState()` / `_buildErrorState()` / `_buildEmptyState()` methods exist
- [ ] All 5 standard widgets present in `lib/core/ui/screen_states/`
- [ ] `AppError` always has `onRetry` callback (no dead-end errors)
- [ ] `AppLoading` uses `skipLoadingOnRefresh` for pull-to-refresh screens

Cross-reference:
- `flutter-screen-state-machine` skill — the authoritative implementation reference
- `flutter-hook-architect` skill — PostMutationInvalidationHook pairs with ScreenState for refresh

### Hook System Architecture — Depth Requirement (File 12)

> **Effective:** 2026-07-26
> **Source:** `flutter-hook-architect` skill
> **Governance Rule:** Every Flutter project MUST include a Hook System Architecture section in its architecture file (12 or project-overridden equivalent). Level 1 (Safety) hooks are non-negotiable before any code ships.

The Hook System Architecture section must address:

1. **11 Hook Types** — Which of the 11 hook types apply to this project (PreRequest, PostResponse, OnRequestError, RouteGuard, PreMutation, PostMutation, WidgetLifecycle, StreamTransform, InputSanitize, FileGuard, SessionGate)
2. **4 Progression Levels** — Current level for each hook type (Safety → Productivity → Intelligence → Orchestration)
3. **Configuration Structure** — `hooks.yaml` or equivalent configuration, registered with the HookChain orchestrator
4. **Security Chain** — Veto order, injection patterns (14 patterns minimum), trusted tools skiplist
5. **Self-Healing Audit** — Hook grading report (A-F) with auto-fix recommendations
6. **Project-Specific Template** — Which of the 3 templates applies (API-heavy, Local-DB, LLM-powered) and any deviations

**Verification Gate (Level 1 — Safety):**
- [ ] Every user input passes through `InputSanitize` before any operation
- [ ] Every file path validated against `FileGuard.allowedPaths`
- [ ] Every HTTP request has Bearer token (for authenticated endpoints)
- [ ] Every 401 triggers token refresh + retry exactly once
- [ ] Every protected route has auth check via `RouteGuard`

Cross-reference:
- `flutter-hook-architect` skill — the authoritative implementation reference
- `hook-veto-protocol` skill — security chain origin
- `19_decision_log.md` — DEC entries for hook-related decisions
| 13 | `13_security_privacy.md` | Auth strategy, data sensitivity classification, permissions, encryption, threat model |
| 14 | `14_testing_acceptance.md` | Test pyramid, DoD, acceptance criteria, device targets |
| 15 | `15_devops_release.md` | CI/CD pipelines, environments, signing, release checklist, observability |
| 16 | `16_ai_agent_contract.md` | Agent rules, validation payload format, traceability, handoff protocols, boundaries |
| 17 | `17_data_architecture_acid.md` | Transaction boundaries, consistency guarantees, migration strategy |
| 18 | `18_implementation_backlog.md` | Prioritized feature queue, dependency chains, effort estimates |

### Stage 5: التطوير والتحسين 🟣 — Files 19–21

| # | File | Purpose |
|---|------|---------|
| 19 | `19_decision_log.md` | Structured ADR format (DEC-NNN), rationale, date, linked files, rejection reasons |
| 20 | `20_lessons_learned.md` | Sequential LL-NNN numbering, date discovered, stage, root cause, prevention rule, cross-reference to DEC |
| 21 | `21_zero_trust_red_team.md` | Attack vectors, penetration test results, security assumptions challenged |

### Stage 6: النشر والإنتاج ⚫ — Files 22–25

| # | File | Purpose |
|---|------|---------|
| 22 | `22_admin_panel.md` | Admin dashboard, moderation tools, analytics views, role-based access |
| 23 | `23_support_operations.md` | On-call procedures, incident response, escalation paths, FAQ maintenance |
| 24 | `24_active_capabilities.md` | Current feature status — the accurate, living inventory of what works |
| 25 | `25_swarm_operating_playbook.md` | Profile-to-Kanban mappings, task dispatch templates (Lite/Full), orchestrator rules, EPIC lifecycle gates, SCSI Guardian protocol |

---

## Stage Gate Rules

### Gate 3 (DESIGN_GATE) — The Critical One

This is the stage the user discovered was missing in CarSah. The rule:

> **No executable code is written before DESIGN_GATE closes.**
> The design prototype (`08_design_prototype.md`) must exist and be approved. Colors, wireframes, user journey — all decided and documented. Code without design = rework.

**PRECISION — what "no code" means (hard-learned):** the gate forbids
APP SOURCE CODE (lib/, src/, app logic, behavior tests). It does NOT forbid
— and in fact REQUIRES — the design agent to write spec artifacts: reflecting
the design artifact onto `07_user_flows_navigation.md` and
`08_design_prototype.md`, exporting visual references, element checklists,
and tokens into the repo. Refusing to touch spec files in the design phase on
the grounds of "stage 3.5 not complete" is a MISAPPLICATION of this gate: it
forces the founder to hand-copy design output, and every manual transfer loses
fidelity. The deciding question is only: does the change touch app source
code? No → design-stage artifact, write it. Yes → wait for the gates.
See File 08 §6 (Operational Pipeline) below for the full stage-3 execution
rules.

### Gate 3.5 (BUILD_READINESS_GATE) — The Build Lock

This gate prevents the "which feature first?" negotiation that plagued past builds. **It is MANDATORY for BOTH Stage 3 Normal and Fast paths.**

> **No executable code is written before BUILD_READINESS_GATE closes.**
> After DESIGN_GATE closes, the next step is NOT writing code — it's locking the build order. The dependency graph + one build sequence (18) and the technical-debt-vs-feature policy (16) must be written by the model, then reviewed and approved by a third party (independent adversarial reviewer). The founder receives the reviewer's verdict and makes the final approval. Only then does MVP coding begin.

**Why DESIGN_GATE alone isn't enough:** A spec pack with priorities but no locked order still forces live mid-build negotiation on every feature boundary. Stage 3.5 eliminates that by making the build sequence a one-time decision (locked, not debated feature-by-feature) and the debt policy an explicit rule (not a recurring argument).

**Why third-party review:** The founder should not be the sole judge of the build plan. After creative freedom in Stage 3, an independent adversarial reviewer challenges the model's build plan — catching blind spots the founder and model both missed. This mirrors the Bun case study (YC 2026): autonomous agents produced code, but adversarial human review caught 3 critical bugs before merge.

**Deliberately lightweight:** This is a dependency graph + one sequence + one policy — NOT formal construction scheduling (Gantt charts, CPM, FF/FS/SF/SS dependencies). Heavy scheduling would reintroduce the governance-overhead trap.

### Gate Rules for All Stages

1. Each stage's files MUST exist in `app-spec/` before the stage begins — empty if not yet populated
2. A stage CANNOT start until the previous stage's files are complete (not empty placeholders)
3. `00_project_stages.md` MUST be updated to reflect current stage status
4. **Create empty > Leave absent** — an empty file signals intent; an absent file is a hidden assumption

### Mid-Project Stage Audit

When receiving a project already in progress:

1. Read `00_project_stages.md` — if missing, create it and run a full audit
2. Check each stage's files: present? populated?
3. Flag any 🚨 gaps — especially missing DESIGN_GATE (Stage 3)
4. **Stop and fill gaps before writing new code** — a mid-project design gap is still a gap

### Pre-Proposal Code Audit (Fatabayyanu Gate)

**Mandatory before adding any new architectural pattern, capability, or system design to app-spec.** This gate prevents proposing something that already exists, and establishes an accurate baseline for the spec addition.

**Workflow:**

1. **Read spec files first** — check ALL relevant spec files across the project for existing mentions of the pattern (architecture, capabilities, decision log)
2. **Search actual codebase** — scan `lib/` and all source directories for:
   - The pattern name (e.g. `hook`, `interceptor`, `middleware`, `guard`)
   - Related class names, file names, and imports
   - Any partial/primitive implementations that might be an informal version of the pattern
3. **Cross-reference ALL projects the user maintains** — the pattern may exist in one project but not others. Establish the full landscape:
   - Which projects have it in spec? Which have it in code?
   - Where is it partially implemented vs fully absent?
4. **Report current state clearly** before proposing changes — use a table format:

   ```
   | Project | Spec | Code | Status |
   |---------|------|------|--------|
   | Hermex Android | ❌ Absent | ✅ Partial (Dio interceptors only) | ❌ No formal pattern |
   | CarSah | ❌ Absent | ❌ Absent | ❌ Not implemented |
   | Azdal | ❌ Absent | ❌ Absent | ❌ Not implemented |
   ```

5. **Only then propose spec additions** — grounded in the real gap, not an assumption

**Rationale:** This pattern was hard-learned when the user asked "تأكد اولا من الملفات كقراءة فقط هل هي منفذة ام لا" before agreeing to add Hook System architecture to app-spec. Proposing spec changes without code verification = proposing solutions to non-existent problems. Always verify the gap before filling it.

---

## Depth Requirements Per File Type

### PRD (File 09)
Must include:
- User stories with Gherkin-style acceptance criteria (Given/When/Then)
- Business rules with unique IDs
- Edge cases with expected behavior
- Error messages (AR + EN where applicable)
- Glossary of domain terms
- Feature traceability matrix (Feature ID → User Story → Screen → Business Rule → Test Case)

### User Flows (File 07)
Must include:
- Screen inventory with IDs, tab/flow, MVP status, notes
- Single valid Mermaid navigation map inside ```mermaid fence
- Per-flow details with rules for each step
- Navigation rules with IDs

### Design Prototype (File 08) ✨ — Unified Design File

This is the single most important file in Stage 3. It contains EVERYTHING design-related — no separate brand guide, no separate prototype spec. One file, one source of truth.

#### §1 Logo Architecture — Full Logo vs App Mark

A common pitfall is placing text-heavy full logos inside small app icon containers. The distinction:

| Asset | Dimensions | Usage |
|-------|-----------|-------|
| **Full Combination Logo** | Horizontal/vertical lockup (variable) | Landing pages, store listings, headers, invoices, PDF reports |
| **App Mark (Standalone Symbol)** | 1024×1024 px square canvas | Master source for all system-generated icons |

**App Mark Types (choose one):**
1. **Symbol/Icon Mark** — stylized graphic (e.g., car silhouette + checkmark for automotive apps)
2. **Monogram/Lettermark** — abstracted letter from brand name (e.g., styled 'C' or 'S')
3. **Wordmark/Logotype** — custom typographic logo. Note: full wordmarks are NEVER used directly as app icons; an extracted lettermark is used instead

**§1.1 App Mark Generation Workflow (Canva → Claude)**

The recommended non-designer workflow:

```
Step A: Generate App Mark in Canva
  → Use Canva's AI logo generator or manual design tools
  → Output: ONE 1024×1024 px App Mark (transparent PNG preferred)

Step B: Feed App Mark to Claude
  → Give Claude the App Mark + context about the brand
  → Claude produces derivative assets for all screen contexts:
    • Full Combination Logo (for Auth, About, PDF headers)
    • Splash screen variant (centered mark on brand background)
    • Notification icons (monochrome white, per Android spec)
    • Store listing feature graphics

Step C: Validate Platform Compliance
  → iOS: no transparency in final icon (system adds rounded corners)
  → Android: adaptive icon layers (foreground + background)
  → Notification icons: white/semi-transparent on transparent background
```

#### §2 Color Architecture (The 60-30-10 Rule)

Apply the standard color distribution rule to avoid visual clutter:

| Proportion | Role | Light Mode | Dark Mode |
|:----------:|------|------------|-----------|
| **60%** | Neutral Surface/Background | White or light off-grey | Deep navy/slate |
| **30%** | Primary Brand Color | Cards, headers, secondary navigation | Same brand color, adjusted luminance |
| **10%** | Accent/CTA Color | Primary action triggers (Save, Confirm, Inspect) | Brighter accent for dark contrast |

**System Status Colors** (separate from brand): Green (success), Red (errors), Amber (warnings).

**Color Exploration Tools:**
| Tool | Purpose |
|------|---------|
| Realtime Colors (realtimecolors.com) | Preview palettes on real mobile UI layouts, adjust distribution ratios |
| Coolors (coolors.co) | Generate cohesive schemes, explore automotive-grade palettes |
| Adobe Color (color.adobe.com) | Verify contrast ratios against WCAG accessibility standards |
| Material Theme Builder (material-foundation.github.io) | Generate MD3 tonal palettes with 13 values per color, export as JSON |

#### §3 Platform-Specific System Asset Requirements

Modern mobile operating systems enforce strict guidelines for icons and splash screens:

**App Launcher Icons:**
| Platform | Master Size | Output Format | Key Rule |
|----------|:----------:|---------------|----------|
| iOS | 1024×1024 px | PNG (no transparency) | System applies rounded corners — do NOT pre-round |
| Android | 1024×1024 px | Adaptive Icon (foreground + background layers) | Foreground: 108dp safe zone inside 108dp; Background: fills 108dp |

**Splash Screens:**
| Platform | Approach | Implementation |
|----------|----------|---------------|
| iOS | Storyboard-based | Single centered image + solid background color |
| Android | Native splash API (Android 12+) | Window background + icon centered, no branding text |

**Flutter Automation (eliminate manual resizing):**
| Package | Version | Purpose |
|---------|:-------:|---------|
| `flutter_launcher_icons` | ^0.14.4 | Ingest 1024×1024 master → generate all iOS + Android icon assets |
| `flutter_native_splash` | ^2.4.8 | Generate splash screens across all densities from config |
| IconKitchen (web) | — | Adaptive icon generation for Android |
| Android Asset Studio (web) | — | Monochrome notification icons |

**Configuration snippet (`pubspec.yaml`):**
```yaml
dev_dependencies:
  flutter_launcher_icons: ^0.14.4
  flutter_native_splash: ^2.4.8

flutter_launcher_icons:
  image_path: "assets/app_mark_1024.png"
  android: true
  ios: true
  adaptive_icon_background: "#FFFFFF"
  adaptive_icon_foreground: "assets/app_mark_foreground_1024.png"

flutter_native_splash:
  color: "#1A73E8"  # Primary brand color
  image: "assets/splash_app_mark.png"
  android: true
  ios: true
```

#### §4 Screen-by-Screen Asset Placement Guide

To ensure consistent visual hierarchy throughout the user journey:

| Screen | Asset | Notes |
|--------|-------|-------|
| **Splash Screen** | Transparent App Mark centered on solid brand background | No text, no slogan — mark only |
| **Onboarding (3-4 screens)** | Vector illustrations + short benefit headlines + CTA buttons | Brand colors in illustrations, not UI chrome |
| **Authentication/Login** | Full Combination Logo (Symbol + Name + Slogan) at top header | Maximum brand recognition at trust moment |
| **Dashboard (Home)** | Clean header: user avatar, notifications, service cards, search | App Mark small in header or nav bar only |
| **About App Screen** | Full Combination Logo + build version + legal + support | Official identity, not decorative |
| **Exported PDF Reports** | Full Combination Logo in document header | For vehicle inspection/maintenance reports or similar |

#### §5 Core Design Requirements (in addition to Stage 3 defaults)

Beyond the standard MD3 tokens, File 08 MUST include:
- **Brand identity** — color tokens with hex values and usage (light AND dark where defined)
- **Spacing** — based on 4dp MD3 grid
- **Elevation** — levels
- **Border radius** — tokens
- **Typography** — scale with all properties (include Arabic-first font choices like Cairo)
- **Component specs** — buttons, text fields, cards, state-specific layouts
- **Empty/error state designs**
- **Motion specifications**
- **Accessibility requirements** (WCAG contrast minimums)
- **RTL/LTR rules** — validate both states for every screen
- **Wireframes** — at minimum low-fidelity for every screen in the user journey
- **Interactive prototype** — Figma link or equivalent, showing full user journey
- **User journey walkthrough** — every tap, every transition, documented step by step
- **Design testing notes** — was it tested on someone? their feedback?
- **Source/provenance labeling rules** — which assets came from Canva, which from Claude, which are stock

#### §6 Operational Pipeline for Stage 3 (design agent behavior)

The design phase is not just content — it is an operational pipeline. These
rules prevent the two failure classes that cost real projects rework:
misclassification (refusing to write spec files) and shape loss (prose that
ten different implementations can all satisfy).

**Visual references are the binding shape source:**
- Export one screenshot per screen and COMMIT it into the repo next to the
  spec. The spec stays the source of RULES (flows, data, logic); the reference
  is the source of SHAPE (look, spacing, position).
- Write the conflict rule in the spec text: "on shape conflict, the reference
  wins."
- Export state variants per screen (at least default + empty + error) — a
  single happy-path screenshot leaves the other states to prose.
- No-build-without-reference: a screen is not buildable until its reference
  exists; check completeness at Stage 3.5, not during build.
- The reference is the EXPORTED FILE (versioned artifact), never the agent's
  memory or its re-description.

**Element checklists, not paragraphs:** for each screen provide a checkbox
list (brand icon present, back control at declared edge, empty/error/loading
states defined, fields match the data model). A gate can check a list; it
cannot audit a paragraph. Missing elements surface as unchecked boxes.

**RTL-safe vocabulary:** default to start/end (logical). "Left" is ambiguous
in RTL — physical left vs line start are different edges. If physical
left/right is truly intended, say "physical left, even in RTL" explicitly.
In Flutter mirror the vocabulary: `AlignmentDirectional`,
`EdgeInsetsDirectional`, never raw left/right for layout.

**Declared tokens, never derived:** every color/radius/spacing/typography
value is written explicitly; no seed-based generation (`ColorScheme.fromSeed`)
for final values — the seed silently produced a near-white tint where the spec
said white; all tests green, the eye can't tell. Stage 4 pins the declared
values with a theme/token test so drift fails CI, not the founder's eye.

**Visual acceptance gate (mandatory):** no screen is accepted on code review
alone. 1) device screenshot of the built screen; 2) the spec reference beside
it; 3) a numbered diff list; 4) the founder decides fix vs amend the spec —
never silently. Required step in the build pipeline, not a reviewer's favor.

**Anti-patterns (all hit in the field):**
| Anti-pattern | Failure | Fix |
|---|---|---|
| Design agent refuses spec-file writes before Stage 4 | Founder hand-copies → fidelity loss | Gate 3 precision: spec artifacts ARE stage 3 |
| Prose-only shape ("center the selector") | Compliant but wrong layout (blank space, floating button) | Visual references + no-build-without-reference |
| "left" in an RTL app | Back control on wrong edge; lying comment | start/end vocabulary |
| Derived palette from a seed | Silent spec violation, invisible to tests | Declared tokens + pinned test |
| "no deviations" without visual comparison | Real deviations found later on device | Visual acceptance gate + honest diff list |
| Manual re-transfer of design output | Every transfer loses something | Agent reflects its own artifact onto files |

### Monetization (File 04)
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

### Financial Model (File 05)
Must include:
- Unit economics per customer/transaction
- LTV calculation with assumptions
- CAC by channel
- Break-even analysis
- Revenue projections
- Decision triggers (when to pivot/kill/scale)

### Risks (File 06)
Must include:
- Categorized risks with unique IDs
- Severity ratings
- Mitigation strategies
- References to governing files
- Product assumptions
- Technical assumptions
- Market assumptions

### Lessons Learned (File 20)
Must include:
- Sequential LL-NNN numbering
- Date discovered, stage, files affected
- Root cause analysis
- Prevention rule (machine-enforceable where possible)
- Cross-reference to DEC-NNN entries
- Source file path

### Decision Log (File 19)
Must include:
- Sequential DEC-NNN numbering
- Date, context, decision
- Rationale with trade-offs considered
- Linked files and LL-NNN references
- Rejection reasons when applicable

### Swarm Operating Playbook (File 25)
Must include:
- Profile-to-responsibility matrix
- Task dispatch templates (Lite/Full)
- Orchestrator anti-temptation rules
- EPIC lifecycle gates
- Guardian protocol (SCSI integration)

### Project Stages (File 00)
Must include:
- **FILE INDEX** — complete table: #, filename, stage, purpose — same structure as this skill's tables
- **STAGE STATUS** — table with stage name, status emoji, files included (include Stage 3.5 between 3 and 4)
- **CURRENT STATE** — which stage is active, which are blocked, which are complete. Must explicitly state that BUILD_READINESS_GATE (3.5) gates MVP: no code until both DESIGN_GATE AND BUILD_READINESS_GATE close.

---

## `00_project_stages.md` Template

When creating this file for a new project, use this structure:

```markdown
# Project Stages & File Index — [Project Name]

## 📋 File Index

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

## 🚦 Stage Status

| Stage | Status | Files | Notes |
|-------|:------:|-------|-------|
| 1-الفكرة | ⬜ | 01, 02, 03 | |
| 2-الجدوى | ⬜ | 04, 05, 06 | Blocked until Stage 1 ✅ |
| 3-التصميم | ⬜ | 07, 08 | Blocked until Stage 2 ✅ |
| 3.5-جاهزية البناء | ⏳ | (inside 16 & 18) | Blocked until Stage 3 ✅ — no standalone file |
| 4-MVP | ⬜ | 09–18 | Blocked until Stage 3 ✅ AND Stage 3.5 ✅ |
| 5-التطوير | ⬜ | 19–21 | Blocked until Stage 4 ✅ |
| 6-الإنتاج | ⬜ | 22–25 | Blocked until Stage 5 ✅ |

Status legend: ⬜ Not started | 🔄 In Progress | ✅ Complete | ⏳ Blocked | 🚨 Missing (gap!)
```

### `00_project_stages.md` — Gates Table Template

```markdown
## 🧭 Gates

| Gate | Opens when | Guards |
|------|-----------|--------|
| IDEA_GATE | 01–03 complete | |
| FEASIBILITY_GATE | 04–06 complete | |
| **DESIGN_GATE** | **07–08 complete + prototype approved** | **no code before this closes** |
| **BUILD_READINESS_GATE (3.5)** | DESIGN_GATE closed + dependency graph (18) + build sequence locked (18) + debt-vs-feature policy defined (16) | |
| MVP_GATE | 09–18 complete + DESIGN_GATE **and** BUILD_READINESS_GATE both closed | |
| ITERATE_GATE | MVP shipped + real feedback | |
| PRODUCTION_GATE | 22–25 ready + launch checklist | |
```

---

## Iterative Refinement Process

Specification files evolve through versions:
1. Initial draft — capture all known decisions
2. User review — feedback, corrections, new ideas
3. Apply updates — add depth, fix contradictions
4. Repeat 2-3 until user approves
5. Version bump and status change

Each version bump must preserve all prior content. Only remove content when explicitly directed by user or when contradictions require replacement (and even then, document the change).

---

## Changelog

### v3.3.0 → v3.4.0

| Change | v3.3.0 | v3.4.0 |
|--------|--------|--------|
| Two-Rein Rule | Not defined | **New Governing Rule** — Creativity vs Quality gradient across all stages. Neither uniform strictness nor uniform freedom is correct. Wisdom = knowing when to loosen and when to tighten. |
| Stage 3 Dual Paths | Only Canva→Claude Normal Path | **Two Paths:** 🐢 Normal Path (unchanged, Canva→Claude as before) and ⚡ Fast Path (full delegation — model reads Stage 1+2, autonomously produces 07+08 — "surprise me") |
| Governance Gradient | Not defined | Authority distribution across stages: Founder leads 1-2, Model leads 3, Third Party judges 3.5, Automated tests + Founder judge 4+ |
| Stage 3.5 Governance | Model writes, founder approves | **Model writes, third party reviews independently, founder receives verdict** — adversarial review mirroring Bun case study (YC 2026). Mandatory for BOTH Normal and Fast paths |
| Three-Zone Classification | Not defined | **3 Zones:** 🎨 Creative (07-08, loose), ⚖️ Mixed (09,12, tight/flexible), 🔒 Quality (10-11-13-15-17-18, tight) |
| Pitfalls | 15 pitfalls | **17 pitfalls** — added: Uniform governance, Skipping third-party review in Stage 3.5 |
| File size | 766 lines (v3.2.0) | ~908 lines |
| Rationale | — | Founder-led strategic discussion synthesizing Anthropic YC report (Boris Cherny: 80% prompt deletion, verification-driven execution) with existing Spec Pack governance. The Two-Rein Rule emerged from the founder's own framing: "الحكمة أن تعرف متى ترخي له الحبل ومتى تشد عليه." Normal Path preserved unchanged. Fast Path added as a new option for Stage 3. Stage 3.5 elevated to mandatory governance bottleneck with third-party adversarial review for both paths. |

### v3.2.0 → v3.3.0

| Change | v3.2.0 | v3.3.0 |
|--------|--------|--------|
| File 08 Design Depth | Basic checklist (Brand identity, Spacing, Typography, etc.) | **4 subsections added:** §1 Logo Architecture (Full Logo vs App Mark + Canva→Claude workflow), §2 Color Architecture (60-30-10 rule + tools), §3 Platform-Specific System Asset Requirements (iOS/Android specs + Flutter automation stack), §4 Screen-by-Screen Asset Placement Guide, §5 Core Design Requirements |
| Design Workflow | Not defined | **Canva → Claude pattern:** App Mark from Canva (1024×1024 px) → Claude generates derivative assets for all screen contexts (Full Logo, Splash, Notification icons, Store graphics) |
| Flutter Automation | Not mentioned | **4 tools documented:** flutter_launcher_icons (^0.14.4), flutter_native_splash (^2.4.8), IconKitchen, Android Asset Studio — with ready-to-paste pubspec.yaml config |
| 60-30-10 Rule | Not mentioned | Color distribution rule documented with Light/Dark mode specifics + 4 color exploration tools |
| Pitfalls | 11 pitfalls | **15 pitfalls** — added: Full logo as app icon, Skipping color distribution, Platform asset ignorance, Manual asset resizing |
| Rationale | — | User provided comprehensive Car Sah Design Guide (2026-07-30) with end-to-end mobile design blueprint. Updated File 08 to be the authoritative design reference in the spec pack. Canva→Claude workflow reflects the user's actual preferred design process. |

### v3.1.0 → v3.2.0

| Change | v3.1.0 | v3.2.0 |
|--------|--------|--------|
| Skill Content Separation | Not defined — skills could freely mix patterns with project data | **Governing Rule added** — SKILL.md must be project-agnostic; project context in `references/project-landscape.md` |
| External Source Grounding | Not defined — skills created from internal knowledge only | **Governing Rule added** — skills must ground patterns in official Flutter/Dart docs via `find-docs` (Context7) |
| Reference file contract | Implicit only | **Explicit 3-file contract** — SKILL.md (universal) + project-landscape.md (snapshot) + authoritative-sources.md (grounding) |
| Pitfalls | 9 pitfalls | **11 pitfalls** — added "skill content contamination" and "untethered skills" |
| Rationale | — | User rejected 4 skills for mixing project names into SKILL.md. Pattern established: audit projects → research sources → write generic pattern → add project snapshot as reference. |

### v3.0.0 → v3.1.0

| Change | v3.0.0 | v3.1.0 |
|--------|--------|--------|
| Build Readiness Gate | Not defined — DESIGN_GATE → MVP_GATE directly | **Stage 3.5 🟤 added** — locks dependency graph + build sequence (18) + debt policy (16) before any code |
| Gate count | 6 gates | **7 gates** (BUILD_READINESS_GATE between DESIGN and MVP) |
| MVP_GATE prerequisite | DESIGN_GATE only | DESIGN_GATE **and** BUILD_READINESS_GATE both closed |
| New file numbers? | — | **None** — Stage 3.5 content lives in existing files 16 & 18 |
| Rationale | — | Founder-observed pattern: mid-build negotiation despite having a spec pack. Lightweight lock (graph + sequence + policy) vs heavy scheduling. |

### v2.0.0 → v3.0.0

| Change | v2.0.0 | v3.0.0 |
|--------|--------|--------|
| Structure | 22 slots (grouped) | **6 stages × 25 files (sequential)** |
| Numbering | Slot-based (00, 00, 00…) | **Sequential 00→25** |
| Design | Separate: `04_ui_design_system.md` + missing prototype | **Unified: `08_design_prototype.md`** |
| Personal files | Slots 20–21 (Personal Vision, Personal Build Plan) | **Removed** — roadmap replaces them |
| Index | None | **`00_project_stages.md` — index + stage map** |
| Stages | Implicit | **Explicit 6-stage gate system** |
| DESIGN_GATE | Missing entirely | **Stage 3 — mandatory before any code** |

---

---

## File Header Template — MANDATORY

Every file in `app-spec/` MUST start with this header. The Cross-Reference (traceability) field is the most valuable — it tells any agent or human exactly which files are related without searching.

### Template

```markdown
# NN — File Title

> **Document ID:** SPEC-NN-{PROJECT}
> **Version:** 1.0.0
> **Status:** Draft
> **Stage:** N 🟢🟡🟠🔵🟣⚫ — Stage Name (Arabic)
> **Owner:** Eng. Abdulrahman Jahfali
> **Last Updated:** YYYY-MM-DD
> **Cross-Reference:** [00_project_stages.md](00_project_stages.md), [XX_related_file.md](XX_related_file.md)

---
```

### Field Rules

| Field | Rule |
|-------|------|
| `# NN — File Title` | `NN` = two-digit file number (00–25). Title = Arabic where natural, English for technical terms. |
| `Document ID` | `SPEC-NN-{PROJECT}` — project short name (e.g., CARSAH, AZDAL, HERMEX) |
| `Version` | Semantic versioning. Start at `1.0.0`. Bump major on structural change, minor on new sections, patch on fixes. |
| `Status` | `Draft` → `Review` → `Approved` → `Living` (updated continuously after approval) |
| `Stage` | Emoji + stage number + Arabic name — links every file to its gate |
| `Owner` | Always `Eng. Abdulrahman Jahfali` — founder and final decision-maker |
| `Last Updated` | ISO date format `YYYY-MM-DD` |
| `Cross-Reference` | **The traceability link.** List every file this spec depends on or relates to. Never leave empty. Minimum: `00_project_stages.md`. |

### Stage-to-Emoji Mapping

| Stage | Emoji | Name |
|:-----:|:-----:|------|
| 1 | 🟢 | الفكرة |
| 2 | 🟡 | دراسة الجدوى |
| 3 | 🟠 | التصميم والهوية |
| 3.5 | 🟤 | جاهزية البناء |
| 4 | 🔵 | MVP |
| 5 | 🟣 | التطوير والتحسين |
| 6 | ⚫ | النشر والإنتاج |

### Example — File 08 (Design Prototype)

```markdown
# 08 — Design Prototype

> **Document ID:** SPEC-08-CARSAH
> **Version:** 1.0.0
> **Status:** Draft
> **Stage:** 3 🟠 — التصميم والهوية
> **Owner:** Eng. Abdulrahman Jahfali
> **Last Updated:** 2026-07-22
> **Cross-Reference:** [07_user_flows_navigation.md](07_user_flows_navigation.md), [00_project_stages.md](00_project_stages.md)

---
```

### Cross-Reference Defaults Per File

Each file type has expected linked files. When creating a new file, these are the minimum cross-references:

| File | Always Linked To |
|------|------------------|
| Any file | `00_project_stages.md` |
| Stage 1 files (01–03) | Each other + `00` |
| Stage 2 files (04–06) | Each other + `00` |
| Stage 3 files (07–08) | Each other + `00` |
| Stage 4 files (09–18) | `09_prd.md` (hub) + `00` |
| Stage 5 files (19–21) | `19_decision_log.md` (hub) + `00` |
| Stage 6 files (22–25) | `25_swarm_operating_playbook.md` (hub) + `00` |

### Updating the Header

When a file is modified:
1. Bump `Version` according to semantic rules
2. Update `Last Updated` to today
3. If status changes (Draft → Review → Approved), update `Status`
4. If new files are linked, add them to `Cross-Reference`
5. If the project moves to a new stage, update the file's `Stage` field to reflect where it currently lives

---

## Pitfalls

- **Procedural reduction**: The most common and most serious error. Creating condensed summaries when asked to update specs. The user will reject these immediately.
- **Full logo as app icon**: Placing a text-heavy full combination logo inside a small app icon container. The App Mark (1024×1024 px standalone symbol) is for icons; the Full Combination Logo is for wide surfaces (headers, PDFs, store listings).
- **Skipping color distribution**: Designing without applying the 60-30-10 rule → every screen feels visually cluttered or disconnected. 60% neutral surface, 30% primary brand, 10% accent/CTA.
- **Platform asset ignorance**: Assuming iOS and Android icons work the same way. iOS uses a single PNG (system rounds corners). Android uses adaptive icons (foreground + background layers). Notification icons have their own spec (monochrome white).
- **Manual asset resizing**: Resizing icons by hand for every density instead of using `flutter_launcher_icons` + `flutter_native_splash`. These packages should be in every project's dev_dependencies from Stage 3 onward.
- **Uniform governance**: Applying the same strictness to all stages equally — suffocates creativity in Stage 3, loosens critical controls in Stage 4. Use the Two-Rein Rule: classify each file into Creative, Mixed, or Quality Zone before delegating.
- **Skipping third-party review in Stage 3.5**: The founder reviewing the build plan alone creates a single point of failure. Stage 3.5 requires an independent adversarial reviewer — the founder receives their verdict but is not the sole judge.
- **Skill content contamination**: Writing project-specific audit data (repo paths, line numbers, DEC entries, project names) into SKILL.md instead of `references/project-landscape.md`. A skill must be reusable by any project. The user rejected 4 skills on 2026-07-26 for this violation.
- **Untethered skills**: Creating architectural patterns without grounding in official Flutter/Dart documentation. Always run `find-docs` (Context7) and save findings to `references/authoritative-sources.md`.
- **Skipping DESIGN_GATE**: Writing code before Stage 3 is complete. This caused CarSah to be rebuilt twice. Never again.
- **Losing detail on rewrite**: When writing a file from scratch, forgetting to include depth from prior versions. Always read the prior version first and preserve its structure.
- **Missing cross-references**: Spec files should link to each other. File 04 references File 05. File 06 references File 05. File 00 cross-references all others.
- **Stale contradictions**: When a decision changes, all references across all files must be updated. Use search to find stale mentions.
- **Mermaid syntax**: Always validate Mermaid blocks. One block per file. Inside ```mermaid fence. No orphan nodes.
- **LL vs DEC separation**: Lessons (LL) go in `20_lessons_learned.md`. Decisions (DEC) go in `19_decision_log.md`. Never mix them.
- **Stage jumping**: Creating Stage 4 files before Stage 2 is complete. Each stage gates the next — no exceptions.
- **Empty ≠ Absent**: An empty file is a placeholder with intent. An absent file is a hidden assumption. Create empty, never leave absent.
