---
name: flutter-lessons-patterns
description: Cross-project Flutter patterns distilled from CarSah + Hermex_Android + Azdal — 39 programming patterns. Single source of truth for all Flutter/Dart/Android coding lessons. Load before every implementation task.
version: 2.16.0
triggers:
  - Starting any Flutter implementation task
  - Creating a new BL (backlog item) or Kanban card
  - Reviewing code before merge
  - User mentions "lessons learned" or "patterns"
  - User asks "what went wrong last time"
  - Prompt engineering or LLM integration architecture decisions
  - History leak / cross-message contamination debugging in chat pipelines
  - Adding or modifying widget action payload forwarding
  - Interactive widget lifecycle (answered-once, form disable after submit)
  - Arabic-indic numeral normalization in form parsing
  - Duplicate bubble text from addBotMessage + widget question field
references:
  - Azdal Prompt Architecture → references/azdal-prompt-defense-patterns.md (12 patterns)
  - Full-File Rewrite Callback Verification → covered by Pattern 8 in references
  - Azdal Stage 4 Patterns → references/azdal-stage4-patterns.md (5 patterns)
related_skills:
  - flutter-design-anti-patterns
  - flutter-android-build-system
  - android-preflight-verification
  - flutter-isar-clean-arch-setup
---

# Flutter Cross-Project Patterns — Unified Programming Lessons

> **Sources:** CarSah (LL-001–LL-020) + Hermex_Android (LL-001–LL-042)
> **Patterns: 40** (1–8: CarSah core, 9–12: Android build, 13–17: Hermex core, 18–28: Hermex extended, 29–30: Hermex HERMEX-007, 31: Swarm governance, 32: Hermex meta-pattern, 33: Azdal stored-first-decision, 34: Azdal reactive-service, 35: Azdal compute-locally, 36: Azdal ephemeral-message-lifecycle, 37: Azdal LLM-no-actionable-UI, 38: Android-Tecno-INTERNET, 39: Azdal widget-answered-once, 40: Azdal full-rewrite-callback-verification)
> **Purpose:** This is the SINGLE source of truth for ALL Flutter/Dart/Android programming lessons. Load before every implementation task. Governance/process lessons belong in `~/.hermes/swarm/00_governance_lessons.md`.

---

## Pattern 1 — Provider Invalidation Rule (LL-003)

**Rule:** Every data mutation (create, update, delete) MUST call `ref.invalidate()` on EVERY provider that holds stale data after the mutation.

```dart
// ❌ BROKEN — saved record invisible until restart
await isar.writeTxn(() => isar.serviceRecords.put(record));

// ✅ CORRECT
await isar.writeTxn(() => isar.serviceRecords.put(record));
ref.invalidate(serviceRecordListProvider);
ref.invalidate(dashboardStatsProvider);
```

**Check:** If you can't list every provider affected, ask the Lead Architect before committing.

---

<details>
<summary>📋 Full Original: LL-003</summary>

**LL-003: Riverpod Provider Hygiene — Notifier vs AutoDisposeNotifier
- **Date:** 2026-07-05
- **Stage:** Implementation (Phase 2)
- **Files Affected:** lib/features/tasks/providers/task_provider.dart
- **Lesson:** `TaskListNotifier` extends `Notifier` (not `AutoDisposeNotifier`) per DEC-034 rule 2 — providers that hold server-fetched data must survive tab switches and should not auto-dispose.
- **Root Cause:** AutoDisposeNotifier discards state when the listening widget is removed from the tree; tab navigation causes rebuilds that would lose cached task/session data.
- **Prevention Rule:** Only use `AutoDisposeNotifier` for transient UI state (form data, search queries). Use `Notifier` for data fetched from the server.
- **Linked Decision ID:** DEC-034

</details>

## Pattern 2 — Device Verification Gate (LL-002 + LL-013)

**Rule:** CI green ≠ working. Every BL/feature requires:
1. Cross-tab device testing (not single-tab)
2. Navigation architecture changes require device testing across ALL tabs
3. Physical device run before marking any BL "done"

```yaml
# In BL definition:
verification:
  - flutter analyze: pass
  - flutter test: all green
  - device_test: cross-tab navigation verified ← MANDATORY
```

---

<details>
<summary>📋 Full Original: LL-002</summary>

**LL-002: SSE Streaming — Raw HttpClient over third-party SSE libraries
- **Date:** 2026-07-05
- **Stage:** Implementation (Phase 2)
- **Files Affected:** lib/core/api/sse_client.dart, lib/features/chat/
- **Lesson:** Custom SSE parser using `dart:io HttpClient` proved more reliable than immature Flutter SSE packages; manual SSE parsing (`data: {...}\n\n`) is straightforward.
- **Root Cause:** Flutter SSE library ecosystem immature — no production-ready package for raw SSE streaming.
- **Prevention Rule:** For non-mainstream protocols, prefer custom `dart:io` implementations over unproven third-party packages. Validate with integration tests.
- **Linked Decision ID:** ADR-001 (consequence noted)

</details>


<details>
<summary>📋 Full Original: LL-013</summary>

**LL-013: Big Bang QA — QA must be phased alongside feature delivery
- **Date:** 2026-07-05
- **Stage:** Post-Mortem (Post-Implementation)
- **Source:** Sulaiman + Abdulrahman review
- **Issue:** Lead Architect decomposed project as: all 8 features → single QA phase at end. This "Big Bang Testing" pattern means defects discovered late have exponentially higher fix costs and risk cascading rework across already-completed features.
- **Root Cause:** Decomposition strategy treated QA as a final gate rather than a continuous phased gate. No rule in the Global Contract or Lead Architect's SOUL enforces phased testing.
- **Impact:** If QA found a fundamental issue (e.g., SSE streaming breaks on certain responses), ALL features depending on Chat would need rework — potentially F-003, F-004, F-005, F-006, F-007.
- **Severity:** 🔴 High — applies to ALL future projects, not just Hermex Android
- **Prevention Rule:** QA must be decomposed into phases matching feature delivery groups. Each phase must pass its QA gate before the next phase begins implementation. The sequence should follow: F-001 build → QA → ✅ → F-002+F-003 build → QA integration → ✅ → F-004+F-005+F-006 build → QA → ✅ → F-007+F-008 build → QA → ✅ → Final integration QA → Zero-Trust Audit → Release.
- **Governance Impact:** This rule must be added to `FLUTTER_GLOBAL_CONTRACT.md` (new rule: "No Big Bang QA — Phased Testing Mandatory") and `flutter-lead-architect/SOUL.md` (decomposition constraint).
- **Linked Decision ID:** N/A (process gap — discovered in post-mortem)

</details>

## Pattern 3 — Zero Hardcoded Strings (LL-001 + LL-006 + LL-018)

**Rule:** No user-facing string anywhere — not in widgets, not in use cases, not in validators, not in domain/data layers. ALL strings via `AppLocalizations`.

```dart
// ❌ BROKEN
validator: (value) => value.isEmpty ? 'Odometer is required' : null

// ✅ CORRECT
validator: (value) => value.isEmpty ? AppLocalizations.of(context)!.odometerRequired : null
```

**Check:** Every new validation message MUST include BOTH AR and EN entries in the same PR.

---

<details>
<summary>📋 Full Original: LL-001</summary>

**LL-001: Server Connection — Static utility methods enable testability
- **Date:** 2026-07-05
- **Stage:** Implementation (Phase 2)
- **Files Affected:** lib/features/connection/
- **Lesson:** Static `isLocalNetwork()` on ServerRepository and ConnectionState renamed to ServerConnectionState to avoid Flutter SDK naming conflict.
- **Root Cause:** Flutter framework exports a `ConnectionState` enum; using the same name in app code caused ambiguous imports.
- **Prevention Rule:** Always search for existing Flutter/Dart symbols before naming classes. Prefer domain-specific prefixes.
- **Linked Decision ID:** N/A (implementation-level pattern)

</details>


<details>
<summary>📋 Full Original: LL-018</summary>

**LL-018: Missing ProviderScope in Widget Test — App renders without crashing FAILED
- **Date:** 2026-07-06
- **Stage:** Post-Mortem (MoA Audit)
- **Source:** Triple Chinese MoA analysis of Hermex Android
- **Issue:** `widget_test.dart` called `HermexApp()` directly without wrapping it in `ProviderScope`. The main `runApp()` in `main.dart` does wrap with `ProviderScope`, but the test did not. This caused the most basic smoke test to fail: "HermexApp renders without crashing — FAILED."
- **Root Cause:** No rule mandated that the smoke test be written FIRST (before feature implementation) or that it must mirror the exact widget tree from `main.dart`. Smoke test was likely written after features were complete, and the ProviderScope dependency was missed.
- **Impact:** 402 tests passed but the single most important test — "does the app even load?" — failed. This means no one could verify end-to-end functionality through automated tests.
- **Prevention Rule:** Smoke Test First. Every Flutter project MUST have `App renders without crashing` as the FIRST test, mirroring `main.dart`'s widget tree exactly (including ProviderScope). This test must pass before any feature implementation begins.
- **Linked Decision ID:** N/A (governance gap)

</details>


<details>
<summary>📋 Full Original: LL-006</summary>

**LL-006: Repository Null-Safety — Accept nullable ApiClient with safe defaults
- **Date:** 2026-07-05
- **Stage:** Implementation (Phase 2)
- **Files Affected:** lib/features/skills/data/skills_repository.dart, lib/features/workspace/data/workspace_repository.dart
- **Lesson:** Repositories that accept nullable `ApiClient` and return safe defaults (empty list) when no server is connected prevent null-check proliferation in providers.
- **Root Cause:** Providers may be read before a server connection is established; nullable ApiClient with graceful degradation avoids runtime null errors.
- **Prevention Rule:** All repositories should accept nullable dependencies and return safe defaults (empty list, null, cached data) when dependencies are unavailable.
- **Linked Decision ID:** N/A (pattern)

</details>

## Pattern 4 — Save-Gating Validators (LL-005 + LL-017)

**Rule:** Required fields must disable the Save button when invalid. Data integrity decisions MUST list every affected field explicitly — never reference a "pipeline" without enumerating fields.

```yaml
# ❌ BROKEN — "invoke recalculation pipeline"
# ✅ CORRECT — list every field:
#   - performedAtKm (ServiceRecordTaskLink)
#   - completedAtKm (ServiceRecordTaskLink)
#   - completedAt (ServiceRecordTaskLink)
```

---

<details>
<summary>📋 Full Original: LL-017</summary>

**LL-017: Router Wiring Gap — Code exists but screens not wired
- **Date:** 2026-07-06
- **Stage:** Post-Mortem (MoA Audit)
- **Source:** Triple Chinese MoA analysis of Hermex Android
- **Issue:** `chat_screen.dart`, `workspace_screen.dart`, and `skills_screen.dart` were fully implemented with passing tests, but `app_router.dart` used `_placeholderScreen()` stubs instead of importing and wiring the real screens. The Traceability Matrix marked F-002, F-005, F-006 as "✅ Implemented" — but users could never reach these screens because they weren't connected to the router.
- **Root Cause:** No governance rule required Router Wiring as an acceptance gate. The Lead Architect wrote the router with stubs during early development and never updated them after State Engineer completed the implementations. No smoke test verified that each feature route renders the real screen.
- **Impact:** 3 of 8 features (37.5%) were effectively dead code — implemented but unreachable. The project's real completion rate was ~50%, not 100% as the Traceability Matrix claimed.
- **Prevention Rule:** Router Wiring = Acceptance Gate. No feature is DONE until its screen is imported and wired in `app_router.dart`. The Traceability Matrix must include a "Router Wired" column.
- **Linked Decision ID:** N/A (governance gap — discovered in MoA audit)

</details>


<details>
<summary>📋 Full Original: LL-005</summary>

**LL-005: GoRouter Route Ordering — Static paths before parameterized
- **Date:** 2026-07-05
- **Stage:** Implementation (Phase 2)
- **Files Affected:** lib/core/router/app_router.dart
- **Lesson:** GoRouter evaluates routes in order; `/tasks/new` must be declared BEFORE `/tasks/:id` to prevent "new" being captured as an ID parameter.
- **Root Cause:** GoRouter matches the first route whose pattern fits; `:id` matches any segment including "new".
- **Prevention Rule:** Always define static sub-routes before parameterized ones. Document this ordering constraint in router comments.
- **Linked Decision ID:** N/A (pattern)

</details>

## Pattern 5 — Tests in Same PR (LL-007)

**Rule:** No "tests in a follow-up PR." UI changes, i18n changes, and new validators MUST include tests in the SAME PR.

```yaml
# PR template checkbox:
□ Tests included for all new/modified widgets
□ Tests included for all new validators
□ i18n coverage verified for all new strings
```

---

<details>
<summary>📋 Full Original: LL-007</summary>

**LL-007: Provider Invalidation — Widget layer, not provider internals
- **Date:** 2026-07-05
- **Stage:** Implementation (Phase 2)
- **Files Affected:** lib/features/workspace/providers/workspace_provider.dart
- **Lesson:** `WorkspaceBrowserNotifier` does NOT call `ref.invalidate` internally — widget layer handles provider invalidation. Internal invalidation causes circular dependency chains in tests.
- **Root Cause:** Calling `ref.invalidate` from within a provider's own method creates a circular dependency that breaks Riverpod's dependency graph.
- **Prevention Rule:** Providers should never invalidate themselves or their parent providers. Invalidation belongs in the widget layer or in dedicated controller providers.
- **Linked Decision ID:** N/A (pattern)

</details>

## Pattern 6 — Spec Sync Gate (LL-008)

**Rule:** No stage closes until spec sync PR is merged. Lessons from implementation MUST flow back to app-spec files before the stage is considered complete.

---

<details>
<summary>📋 Full Original: LL-008</summary>

**LL-008: Optimistic UI for Read-Only Toggle — Skills enable/disable
- **Date:** 2026-07-05
- **Stage:** Implementation (Phase 2)
- **Files Affected:** lib/features/skills/providers/skills_provider.dart
- **Lesson:** Skills toggle is optimistic local-only — no server-side mutation API defined. Toggle updates UI state immediately without waiting for server confirmation.
- **Root Cause:** Hermes Agent API Server `GET /v1/skills` returns skill data but no `PATCH /v1/skills/{name}` endpoint exists for toggling.
- **Prevention Rule:** When the backend lacks a mutation endpoint, implement optimistic local UI only and document the limitation clearly in code comments and spec.
- **Linked Decision ID:** N/A (API limitation)

</details>

## Pattern 7 — Design Before Implementation (LL-016 + LL-019)

**Rule:** Complex UI decisions (changing screen structure, audience, or data integrity) REQUIRE:
1. Designer-produced mockup BEFORE implementation card opens
2. Device validation of structural decisions BEFORE coding begins
3. Specs that survive device reality, not just paper review

---

<details>
<summary>📋 Full Original: LL-019</summary>

**LL-019: Empty Catch Blocks in Auth Path — Silent security failures
- **Date:** 2026-07-06
- **Stage:** Post-Mortem (MoA Audit)
- **Source:** Triple Chinese MoA analysis of Hermex Android
- **Issue:** `auth_manager.dart` contains two `catch (_) {}` blocks that silently swallow all exceptions from `flutter_secure_storage`. Combined with null assertions (`!`) in `certificate_pinner.dart`, this creates a compound risk: TLS pinning silently disabled + no auth error surfaced = potential MITM attack vector.
- **Root Cause:** Developer used empty catch blocks as a "quick fix" during development, intended to add proper error handling later. No linting rule or code review gate flagged them.
- **Impact:** Security-critical operations (auth, TLS) can fail silently with zero visibility. Combined failure scenario: secure storage fails → TLS pinning disabled → MITM attack on public WiFi → API token theft.
- **Prevention Rule:** Empty catch blocks are FORBIDDEN in security-critical paths (auth, TLS, storage, network). Minimum: log the error. Preferred: surface to user or fallback to safe state. Add linting rule: `avoid_empty_catch`.
- **Linked Decision ID:** N/A (code quality — discovered in MoA audit)

</details>


<details>
<summary>📋 Full Original: LL-016</summary>

**LL-016 — 7-round review loop signals spec-implementation gap
- **Date:** 2026-06-21
- **Stage:** 5.7 (Phase 2)
- **Files Affected:** 12_decision_log.md DEC-051/DEC-052, 04_ui_design_system.md §7.7/§7.8, 16_implementation_backlog.md BL-089/090/091
- **Lesson:** DEC-051 nested tree form and DEC-052 mechanic card required 7 review rounds (t_a85dd03e), exposing that architecture-level decisions without designer-produced mockups force discovery during implementation.
- **Root Cause:** DEC-051 and DEC-052 were written at decision-log level without accompanying UI mockups; the State Engineer had to iterate design details that should have been resolved before implementation.
- **Prevention:** Complex UI decisions (DECs that change screen structure or audience) MUST include a designer-produced spec mockup BEFORE the implementation card opens.
- **Linked Decision:** DEC-051, DEC-052.

</details>

## Pattern 8 — 1-Day BL Maximum (LL-020)

**Rule:** Every backlog item must be completable in ≤1 working day. BLs exceeding 1 day must be split. Any BL running >1 day is auto-blocked for architect review.

**Why:** Large BLs mask individual mismatches that compound into multi-round rework (CarSah Stage 5 took 11 days because BLs spanned 3+ days).

---

<details>
<summary>📋 Full Original: LL-020</summary>

**LL-020: Stale Router After Feature Completion — No wiring verification gate
- **Date:** 2026-07-06
- **Stage:** Post-Mortem (MoA Audit)
- **Source:** Triple Chinese MoA analysis of Hermex Android
- **Issue:** The Kanban workflow treated "Feature Implementation" and "Router Wiring" as a single implicit task. The State Engineer implemented features in `lib/features/` but the router in `lib/core/router/` was never updated. No Kanban task existed for "Wire Feature X to Router."
- **Root Cause:** The Kanban decomposition model assumed that creating feature files automatically meant they were wired. Router wiring was not a separate, explicit task in the workflow.
- **Impact:** Systematic risk — any future project using this workflow would have the same gap. Features get built but never connected.
- **Prevention Rule:** Every Feature implementation task MUST have a paired "Router Wiring" subtask. The Kanban board must include a "ROUTER_WIRING" verification column or the Definition of Done must explicitly include "Screen is reachable via router navigation."
- **Linked Decision ID:** N/A (process gap)

---

## 2026-07-06 — Android Build Failures & Skill Remediation

</details>

## Pattern 9 — Android Namespace = MainActivity Package (LL-024)

**Source:** hermex_android (2026-07-06) → `~/Projects/hermex_android/app-spec/00_lessons_learned.md`

**Rule:** Before any Flutter release build, verify that `namespace` in `build.gradle.kts` matches the Kotlin `package` in `MainActivity.kt`.

```bash
# Verification:
NS=$(grep -oP 'namespace\s*=\s*"\K[^"]+' android/app/build.gradle.kts)
PKG=$(grep -oP '^package\s+\K\S+' android/app/src/main/kotlin/**/MainActivity.kt)
# MUST MATCH — mismatch = ClassNotFoundException → crash on launch
```

**Why:** AndroidManifest's `android:name=".MainActivity"` resolves relative to Gradle `namespace`. If `namespace` ≠ Kotlin package, Android can't find the activity.

**Prevention:** Load `android-preflight-verification` skill. Run `bash scripts/android-preflight.sh` — machine-enforceable gate before every build.

---

<details>
<summary>📋 Full Original: LL-024</summary>

**LL-024: Namespace Mismatch — AndroidManifest resolves to wrong class
- **Date:** 2026-07-06
- **Stage:** Release (first device install)
- **Source:** Physical Android device install test
- **Issue:** `namespace = "com.hermex.android"` in `build.gradle.kts` but `MainActivity.kt` declared `package com.jahfali.hermex_android`. Android resolved `android:name=".MainActivity"` relative to namespace → `com.hermex.android.MainActivity` → `ClassNotFoundException` → crash before splash screen.
- **Root Cause:** 9-profile swarm generated code without coordination. DevOps Engineer set namespace, State Engineer set Kotlin package — no profile owned the end-to-end Android build correctness.
- **Impact:** App "لم يفتح نهائيا" (never opened). User saw nothing. Critical first-impression failure.
- **Prevention Rule:** Android Verification Gate §1 — namespace in build.gradle.kts MUST equal MainActivity.kt package. Automated script verifies before every release.
- **Linked Decision ID:** N/A (build configuration gap)

</details>

## Pattern 10 — Isar + ProGuard = Crash (LL-025)

**Source:** hermex_android (2026-07-06) → `~/Projects/hermex_android/app-spec/00_lessons_learned.md`

**Rule:** If `isar:` appears in `pubspec.yaml`, `isMinifyEnabled` MUST be `false` in the release build type.

```kotlin
// android/app/build.gradle.kts
release {
    isMinifyEnabled = false  // REQUIRED when using Isar
    // R8 strips Isar adapter classes loaded reflectively
}
```

**Why:** Isar generates adapter classes (CachedSessionAdapter, etc.) loaded via reflection. R8/ProGuard strips classes not directly referenced in Java/Kotlin → native crash on `Isar.open()`.

**Prevention:** Load `flutter-android-build-system` skill before configuring build types.

---

<details>
<summary>📋 Full Original: LL-025</summary>

**LL-025: Isar + ProGuard/R8 Incompatibility
- **Date:** 2026-07-06
- **Stage:** Release (discovered during LL-024 investigation)
- **Source:** Code audit
- **Issue:** `isMinifyEnabled = true` in release build type strips Isar adapter classes (CachedSessionAdapter, etc.) because they are loaded reflectively, not directly referenced in Java/Kotlin code. Even if the namespace was correct, the app would crash on `Isar.open()`.
- **Root Cause:** No profile SOUL or spec file documented the Isar + ProGuard incompatibility. `android/skills` official docs confirm this pattern.
- **Impact:** Compound failure — two independent crashes, either one fatal.
- **Prevention Rule:** Android Verification Gate §2 — if `isar:` in `pubspec.yaml`, `isMinifyEnabled` MUST be `false`. Automated script verifies before every release.
- **Linked Decision ID:** N/A (build configuration gap)

</details>

## Pattern 11 — Official Android Sources Mandatory (LL-026)

**Source:** hermex_android (2026-07-06) — MoA-audited 2026-07-06 → `~/Projects/hermex_android/app-spec/00_lessons_learned.md`

**Rule:** No Flutter swarm profile may work on Android build configuration without loading the official Android skills.

**Mandatory skills (MoA-corrected):**
- `flutter-android-build-system` ← developer.android.com/build + isar.dev
- `android-preflight-verification` ← LL-024 + LL-025 enforcement (executable bash gate)

**Dropped:** `github.com/android/skills` — MoA audit found it covers app code (Camera, Compose, Navigation) NOT build config (namespace, ProGuard, AGP).

**Why:** Flutter profiles have deep Dart knowledge but zero Android build knowledge (namespace, ProGuard, AGP, applicationId). Official Google sources are non-negotiable. The preflight script provides machine-enforceable gating — not just documentation.

---

<details>
<summary>📋 Full Original: LL-024</summary>

**LL-024: Namespace Mismatch — AndroidManifest resolves to wrong class
- **Date:** 2026-07-06
- **Stage:** Release (first device install)
- **Source:** Physical Android device install test
- **Issue:** `namespace = "com.hermex.android"` in `build.gradle.kts` but `MainActivity.kt` declared `package com.jahfali.hermex_android`. Android resolved `android:name=".MainActivity"` relative to namespace → `com.hermex.android.MainActivity` → `ClassNotFoundException` → crash before splash screen.
- **Root Cause:** 9-profile swarm generated code without coordination. DevOps Engineer set namespace, State Engineer set Kotlin package — no profile owned the end-to-end Android build correctness.
- **Impact:** App "لم يفتح نهائيا" (never opened). User saw nothing. Critical first-impression failure.
- **Prevention Rule:** Android Verification Gate §1 — namespace in build.gradle.kts MUST equal MainActivity.kt package. Automated script verifies before every release.
- **Linked Decision ID:** N/A (build configuration gap)

</details>


<details>
<summary>📋 Full Original: LL-026</summary>

**LL-026: Android Build Knowledge Gap — No official sources in swarm
- **Date:** 2026-07-06
- **Stage:** Post-Mortem (Root Cause Analysis)
- **Source:** Comprehensive audit of all 9 Flutter profiles + Spec Pack
- **Issue:** Zero profiles had Android build knowledge. Words `namespace`, `ProGuard`, `applicationId` appeared NOWHERE in any SOUL file. Spec File 10 (DevOps) was 19 lines — no Android build configuration checklist.
- **Root Cause:** Swarm was designed for Dart/Flutter expertise only. Android native build system was an implicit blind spot — everyone assumed "someone else handles it."
- **Impact:** Systemic risk for ALL future Flutter projects.
- **Prevention Rule — 3 New Skills Created from Official Sources:**
  1. `android-build-system` ← github.com/android/skills (Google AI-optimized) + developer.android.com
  2. `flutter-android-deployment` ← docs.flutter.dev/deployment/android
  3. `android-verification-gate` ← custom (LL-024 enforcement)
  
  These skills are MANDATORY for flutter-devops-release-engineer and flutter-lead-architect. Updated SOULs to enforce loading.
- **Linked Decision ID:** N/A (competency gap remediation)

</details>


<details>
<summary>📋 Full Original: LL-025</summary>

**LL-025: Isar + ProGuard/R8 Incompatibility
- **Date:** 2026-07-06
- **Stage:** Release (discovered during LL-024 investigation)
- **Source:** Code audit
- **Issue:** `isMinifyEnabled = true` in release build type strips Isar adapter classes (CachedSessionAdapter, etc.) because they are loaded reflectively, not directly referenced in Java/Kotlin code. Even if the namespace was correct, the app would crash on `Isar.open()`.
- **Root Cause:** No profile SOUL or spec file documented the Isar + ProGuard incompatibility. `android/skills` official docs confirm this pattern.
- **Impact:** Compound failure — two independent crashes, either one fatal.
- **Prevention Rule:** Android Verification Gate §2 — if `isar:` in `pubspec.yaml`, `isMinifyEnabled` MUST be `false`. Automated script verifies before every release.
- **Linked Decision ID:** N/A (build configuration gap)

</details>

## Pattern 12 — Design Quality Anti-Patterns (LL-027 — Cross-Reference)

**Source:** Impeccable-inspired gap analysis (2026-07-11)

**Rule:** Before any UI-facing Flutter task, also load `flutter-design-anti-patterns` — 31 deterministic design quality rules across 10 categories (color, typography, layout, states, a11y, i18n/RTL, components, performance, navigation, general).

**Why:** This skill covers logic/infrastructure patterns (providers, build config, i18n discipline). It does NOT cover visual design quality (hardcoded colors, container nesting, missing empty states, RTL padding, contrast). Both are needed for a complete pre-commit gate.

**Detection:** `python3 <skill-dir>/scripts/detect.dart.py lib/ --severity P0 --json`

**CarSah baseline** (92 files, 2026-07-11): 15 hardcoded colors, 1 fixed-dimension widget, 2 missing text-scaling hits.

---

<details>
<summary>📋 Full Original: LL-027</summary>

**LL-027: Android Cleartext HTTP Blocked — network_security_config whitelist too narrow
- **Date:** 2026-07-06
- **Stage:** Release (first real-device connection test)
- **Source:** User tested app with real Hermes Agent server on LAN
- **Issue:** `network_security_config.xml` allowed cleartext HTTP only for hardcoded IPs (192.168.1.1, 192.168.0.1, etc.). User's server at `192.168.8.80` was NOT on the list. Android silently dropped all HTTP connections to any IP not in the domain-config whitelist. The server returned HTTP 200 via curl from Mac — proving server/firewall/port were all correct. The app timed out after exactly 10 seconds (matching the Dart `connectTimeout`) with zero network activity reaching the server.
- **Root Cause:** The domain-config whitelist in `network_security_config.xml` was designed during development with hardcoded common IPs (192.168.1.1, 192.168.0.1, 192.168.1.100, 10.0.0.1, etc.). Android's `<domain>` element does NOT support CIDR notation, so the list had to be exhaustive. Any IP not explicitly listed was blocked at the OS level before Dio/Dart ever saw the request.
- **Impact:** 2+ hours of debugging across macOS firewall, Hermes config paths, port binding, proxy attempts, and gateway restarts — none of which were the actual problem. The bug was in the app's Android configuration, 4 layers removed from where we were debugging.
- **Fix:** Changed `<base-config cleartextTrafficPermitted="false">` to `true`. Dart-level validation (`_validateUrl()` → `isLocalNetwork()`) already restricts HTTP to RFC 1918 private IPs, so this doesn't weaken security — it just removes an overly restrictive OS-level duplicate check.
- **Prevention Rule:** 1) `network_security_config.xml` MUST use `cleartextTrafficPermitted="true"` in base-config for local-server apps. 2) The `android-preflight.sh` script MUST verify the base-config allows cleartext. 3) If domain-config whitelist is used, it MUST include a comment warning that any IP not listed will be silently blocked by Android.
- **Linked Decision ID:** N/A (Android network policy gap)

</details>

## Pattern 13 — State Mutation Order: Snapshot BEFORE Mutating (LL-029)

**Source:** hermex_android (2026-07-06) → `~/Projects/hermex_android/app-spec/00_lessons_learned.md`

**Rule:** Never call a history/snapshot builder AFTER mutating the state it reads from. Take the snapshot first, then mutate.

```dart
// ❌ BROKEN — history includes the just-added message (duplicate in API request)
state = state.copyWith(messages: [...state.messages, userMsg]);
final history = _buildHistory(); // ← userMsg is already in state.messages!

// ✅ CORRECT
final history = _buildHistory(); // ← snapshot of previous messages only
state = state.copyWith(messages: [...state.messages, userMsg]);
```

**Why:** If the API requires strict user/assistant alternation, a duplicate user message in the request body will be rejected. Add a unit test that verifies exactly one user message in the API request body.

---

<details>
<summary>📋 Full Original: LL-029</summary>

**LL-029: Duplicate User Messages — State Mutation Before History Capture
- **Date:** 2026-07-06
- **Stage:** First chat test after successful connection
- **Source:** User sent first message "السلام عليكم" — app crashed with API error
- **Issue:** `ChatNotifier.sendMessage()` added the user message to `state.messages` (line 254) BEFORE calling `_buildHistory()` (line 260). Since `_buildHistory()` reads from `state.messages`, the history included the just-added user message. Then `chat_repository.dart` added the same message AGAIN explicitly: `messages.add({'role': 'user', 'content': message})`. Result: two consecutive `role: user` messages in the API request. Hermes API enforces strict user/assistant alternation and rejected with "Invalid argument (string): Contains invalid characters."
- **Root Cause:** Mutation order bug — mutable state (`state.messages`) was updated before the snapshot (`_buildHistory()`) was taken. This is a classic React/Riverpod anti-pattern: reading derived state after mutating the source.
- **Fix:** Moved `final history = _buildHistory()` to BEFORE `state = state.copyWith(messages: [...state.messages, userMessage, agentMessage])`. History now contains only previous messages.
- **Prevention Rule:** 1) Never call a history/snapshot builder AFTER mutating the state it reads from. 2) Add a unit test for `sendMessage` that verifies exactly one user message appears in the API request body. 3) Consider a lint rule or PR checklist item: "Does any state.copyWith() precede a _buildHistory()-style snapshot?"
- **Bug Class:** NEW — this is a Flutter/Riverpod state management bug, NOT an Android knowledge gap. Different from LL-024/025/027 (which were Android build/config issues). Requires Dart-level testing, not Android-level gates.
- **Linked Decision ID:** N/A (state management pattern)

---

## 2026-07-07 — Operational Bug Recovery Session

</details>

## Pattern 14 — Silent API Key Redaction: `***` Literal (LL-022)

**Source:** hermex_android (2026-07-07) → `~/Projects/hermex_android/app-spec/00_lessons_learned.md`

**Rule:** Before any commit, verify no SOUL-redaction artifacts remain:
```bash
grep -rn "apiKey: \*\*\*" lib/ || true
grep -rn 'api_key: \*\*\*' lib/ || true
```

**Why:** Swarm SOUL-level security sanitization replaces API keys with `***` in output. These redacted outputs can be committed as literal source code (`apiKey: '***'`), silently breaking ALL authenticated API calls. The compiler does not catch this — `***` is valid Dart.

---

<details>
<summary>📋 Full Original: LL-022</summary>

**LL-022: Silent API Key Redaction — `***` literal replaced variable
- **Date:** 2026-07-07
- **Stage:** Production Bug Recovery
- **Source:** Abdulrahman report — "Agent Data (Skills, Memory, Insight) لا تعمل"
- **Issue:** Two files (`api_client_provider.dart:73`, `connection_screen.dart:226`) contained `apiKey: ***` as a literal string instead of the `apiKey` variable. This redaction artifact — likely from the swarm's SOUL-level security sanitization — silently broke ALL API-dependent features. Every request carried the literal HTTP header `Authorization: Bearer ***`.
- **Root Cause:** The MoA swarm's security layer replaced actual API key values with `***` during output redaction. These redacted outputs were then treated as source code and committed. No human or automated gate detected that `***` is not valid Dart syntax referencing a variable named `apiKey`. The compiler does not flag this — `***` is valid Dart (three `*` operators).
- **Impact:** Skills, Memory, Insights, Chat streaming, and any feature relying on `ApiClient` failed silently. Health endpoint returned 401 but error messages were not surfaced properly. The app appeared functional but every API call received "Unauthorized."
- **Prevention Rule (PERMANENT — GOV-005):** No commit may pass if `grep -rn "apiKey: \*\*\*" lib/` or `grep -rn "api_key: \*\*\*" lib/` returns matches. These are SOUL-redaction artifacts that MUST be reverted to actual variable names before commit. Add to CI pre-commit hook and governance rules.
- **Governance Impact:** Added to `00_swarm_operating_playbook.md` as permanent rule under §Governance.
- **Linked Decision ID:** N/A (security sanitization defect)

</details>

## Pattern 15 — Fake Connection State: Never Set 'connected' Without Health Check (LL-023)

**Source:** hermex_android (2026-07-07) → `~/Projects/hermex_android/app-spec/00_lessons_learned.md`

**Rule:** Any method that transitions status to `ConnectionStatus.connected` MUST: (a) retrieve the API key, (b) perform a health check against the server, (c) only transition on success. Never use `connected` as a local-only state — it MUST represent verified server reachability.

```dart
// ❌ BROKEN — declares connected without verification
void selectServer(Server s) {
  state = state.copyWith(status: ConnectionStatus.connected);
}

// ✅ CORRECT
Future<void> selectServer(Server s) async {
  final key = await _storage.read(s.id);
  final healthy = await _api.healthCheck(s.url, key);
  state = state.copyWith(status: healthy ? ConnectionStatus.connected : ConnectionStatus.error);
}
```

---

<details>
<summary>📋 Full Original: LL-023</summary>

**LL-023: Fake Connection State — selectServer declared connected without health check
- **Date:** 2026-07-07
- **Stage:** Production Bug Recovery
- **Source:** Abdulrahman report — "السيرفرات المحفوظة لا تدخلني على السيرفر"
- **Issue:** `ConnectionNotifier.selectServer()` set `status: ConnectionStatus.connected` immediately after `setActive(serverId)` — without retrieving the stored API key or performing a health check against the server. ConnectionScreen's listener used a flag `_hasAttemptedConnection` that only triggered after manual `_handleConnect()`, so saved server selection never auto-navigated to chat.
- **Root Cause:** `selectServer` was designed as a state-local operation ("mark this server as active") but its name (`selectServer`) and state flag (`connected`) implied full connection functionality. No health check, no key retrieval, no auto-navigation. Two separate bugs compounded: (1) the fake connection, (2) the auto-nav gate.
- **Prevention Rule (PERMANENT):** Any method that transitions status to `ConnectionStatus.connected` MUST: (a) retrieve the API key, (b) perform a health check, (c) only transition on success. Never use `connected` as a local-only state — it MUST represent verified server reachability.
- **Governance Impact:** Connection lifecycle is a security boundary. Mark as invariant in architecture spec.
- **Linked Decision ID:** N/A

</details>

## Pattern 16 — API Query Parameters: Always Pass `include_disabled=true` (LL-042)

**Source:** hermex_android (2026-07-12) → `~/Projects/hermex_android/app-spec/00_lessons_learned.md`

**Rule:** When fetching entity lists that include paused/disabled items (cron jobs, tasks, skills), ALWAYS pass `include_disabled=true` in query parameters. The default API behavior silently excludes disabled entities.

```dart
// ❌ BROKEN — returns only active jobs
final response = await _dio.get('/api/jobs');

// ✅ CORRECT
final response = await _dio.get('/api/jobs', queryParameters: {'include_disabled': 'true'});
```

**Why:** The Hermes API defaults `include_disabled` to `false`. Paused jobs appear to "not exist" in the app even though they exist on disk. Always test API endpoints with and without the flag.

---

<details>
<summary>📋 Full Original: LL-042</summary>

**LL-042: GET /api/jobs excludes disabled/paused jobs by default — requires ?include_disabled=true
- **Date:** 2026-07-12
- **Stage:** T3-3 Investigation (API mismatch)
- **Files Affected:** lib/features/tasks/data/task_repository.dart, app-spec/06_api_contract.md
- **Lesson:** The Hermes API Server's `GET /api/jobs` endpoint defaults `include_disabled` to `false`, returning only enabled/active jobs. Paused jobs (`enabled: false`, `state: "paused"`) are silently excluded. The Hermex Flutter client's `TaskRepository.getAll()` was not passing `include_disabled=true`, so the Tasks page showed zero jobs despite 4 paused jobs existing in `~/.hermes/cron/jobs.json`.
- **Root Cause:** API contract spec (`06_api_contract.md` line 302) incorrectly stated "Returns all jobs regardless of status (active, paused, scheduled, etc.)" The actual default behavior excludes disabled jobs. The `include_disabled` query parameter was not documented in the spec, and the Flutter client did not pass it.
- **Verification:** `curl "http://localhost:8642/api/jobs"` → `{"jobs": []}`; `curl "http://localhost:8642/api/jobs?include_disabled=true"` → returns all 4 paused jobs. `hermes cron list` (CLI) also defaults to `include_disabled=False`.
- **Prevention Rule:** Always test API endpoints with `?include_disabled=true` when paused/disabled entities are expected. Document ALL query parameters in `06_api_contract.md`. For Flutter clients fetching entity lists that include paused items, always pass `include_disabled=true`.
- **Fix (Hermex):** Add `'include_disabled': 'true'` to `queryParameters` in `TaskRepository.getAll()` (line 31 of `task_repository.dart`).
- **Linked Decision ID:** DEC-T3-JOBSFILTER

</details>

## Pattern 17 — Verify On Disk Before Claiming (Meta-Pattern — Sulaiman Session 2026-07-11)

**Source:** 6 rounds of governance evaluation where claimed fixes did not exist on disk

**Rule:** Before dispatching any task for independent evaluation or marking it "complete," ALWAYS:
1. Read the actual file(s) that should contain the fix
2. Run the verification command in the terminal
3. Confirm the output matches the claim
4. THEN report the result

```bash
# BEFORE claiming "Dedup is fixed":
python3 ~/.hermes/swarm/violation_detector.py  # ← must show 0 violations
ls -la ~/.hermes/swarm/processed_violations.json  # ← must exist
```

**Never:** describe what SHOULD exist without verifying it DOES exist. The gap between "designed in my head" and "written to disk" has caused 5 rounds of failed evaluations.

---

## Pattern 18 — ProviderScope in Widget Tests: Mirror main.dart Exactly (LL-018)

**Source:** hermex_android (2026-07-06) → `~/Projects/hermex_android/app-spec/00_lessons_learned.md`

**Rule:** Every Flutter widget test that renders the app must wrap it in `ProviderScope`, exactly as `main.dart` does. The smoke test ("App renders without crashing") must pass BEFORE any feature implementation begins.

```dart
// ❌ BROKEN — test calls HermexApp() without ProviderScope
testWidgets('App renders', (tester) async {
  await tester.pumpWidget(const HermexApp()); // CRASH — no ProviderScope
});

// ✅ CORRECT
testWidgets('App renders', (tester) async {
  await tester.pumpWidget(
    const ProviderScope(child: HermexApp()),
  );
});
```

**Why:** 402 tests passed but the single most important test — "does the app even load?" — failed because ProviderScope was missing. Features can't render without Riverpod providers.

---

<details>
<summary>📋 Full Original: LL-018</summary>

**LL-018: Missing ProviderScope in Widget Test — App renders without crashing FAILED
- **Date:** 2026-07-06
- **Stage:** Post-Mortem (MoA Audit)
- **Source:** Triple Chinese MoA analysis of Hermex Android
- **Issue:** `widget_test.dart` called `HermexApp()` directly without wrapping it in `ProviderScope`. The main `runApp()` in `main.dart` does wrap with `ProviderScope`, but the test did not. This caused the most basic smoke test to fail: "HermexApp renders without crashing — FAILED."
- **Root Cause:** No rule mandated that the smoke test be written FIRST (before feature implementation) or that it must mirror the exact widget tree from `main.dart`. Smoke test was likely written after features were complete, and the ProviderScope dependency was missed.
- **Impact:** 402 tests passed but the single most important test — "does the app even load?" — failed. This means no one could verify end-to-end functionality through automated tests.
- **Prevention Rule:** Smoke Test First. Every Flutter project MUST have `App renders without crashing` as the FIRST test, mirroring `main.dart`'s widget tree exactly (including ProviderScope). This test must pass before any feature implementation begins.
- **Linked Decision ID:** N/A (governance gap)

</details>

## Pattern 19 — Empty Catch Blocks FORBIDDEN in Security Paths (LL-019)

**Source:** hermex_android (2026-07-06) → `~/Projects/hermex_android/app-spec/00_lessons_learned.md`

**Rule:** `catch (_) {}` is FORBIDDEN in: auth, TLS, encryption, storage, network, API key handling. Minimum: log the error. Preferred: surface to user or fallback to safe state.

```dart
// ❌ BROKEN — TLS failure silenced, app proceeds without pinning
try {
  await _secureStorage.read(key: 'api_key');
} catch (_) {} // SILENT FAILURE — MITM risk

// ✅ CORRECT
try {
  await _secureStorage.read(key: 'api_key');
} catch (e, st) {
  _logger.severe('SecureStorage read failed', e, st);
  throw AuthException('Cannot retrieve credentials');
}
```

**Why:** Combined with null assertions (`!`), silent failures in security paths create compound attack vectors: secure storage fails → TLS disabled → API token stolen.

---

<details>
<summary>📋 Full Original: LL-019</summary>

**LL-019: Empty Catch Blocks in Auth Path — Silent security failures
- **Date:** 2026-07-06
- **Stage:** Post-Mortem (MoA Audit)
- **Source:** Triple Chinese MoA analysis of Hermex Android
- **Issue:** `auth_manager.dart` contains two `catch (_) {}` blocks that silently swallow all exceptions from `flutter_secure_storage`. Combined with null assertions (`!`) in `certificate_pinner.dart`, this creates a compound risk: TLS pinning silently disabled + no auth error surfaced = potential MITM attack vector.
- **Root Cause:** Developer used empty catch blocks as a "quick fix" during development, intended to add proper error handling later. No linting rule or code review gate flagged them.
- **Impact:** Security-critical operations (auth, TLS) can fail silently with zero visibility. Combined failure scenario: secure storage fails → TLS pinning disabled → MITM attack on public WiFi → API token theft.
- **Prevention Rule:** Empty catch blocks are FORBIDDEN in security-critical paths (auth, TLS, storage, network). Minimum: log the error. Preferred: surface to user or fallback to safe state. Add linting rule: `avoid_empty_catch`.
- **Linked Decision ID:** N/A (code quality — discovered in MoA audit)

</details>

## Pattern 20 — GoRouter: Static Routes BEFORE Parameterized (LL-005)

**Source:** hermex_android (2026-07-05) → `~/Projects/hermex_android/app-spec/00_lessons_learned.md`

**Rule:** In `app_router.dart`, define ALL static sub-routes BEFORE their parameterized siblings. GoRouter matches the FIRST route whose pattern fits — `:id` captures any segment including "new".

```dart
// ✅ CORRECT ORDER
GoRoute(path: '/tasks/new', ...),    // static — matched first
GoRoute(path: '/tasks/:id', ...),    // parameterized — fallback

// ❌ WRONG ORDER — "new" would be captured as :id
GoRoute(path: '/tasks/:id', ...),    // matches "new"!
GoRoute(path: '/tasks/new', ...),    // never reached
```

---

<details>
<summary>📋 Full Original: LL-005</summary>

**LL-005: GoRouter Route Ordering — Static paths before parameterized
- **Date:** 2026-07-05
- **Stage:** Implementation (Phase 2)
- **Files Affected:** lib/core/router/app_router.dart
- **Lesson:** GoRouter evaluates routes in order; `/tasks/new` must be declared BEFORE `/tasks/:id` to prevent "new" being captured as an ID parameter.
- **Root Cause:** GoRouter matches the first route whose pattern fits; `:id` matches any segment including "new".
- **Prevention Rule:** Always define static sub-routes before parameterized ones. Document this ordering constraint in router comments.
- **Linked Decision ID:** N/A (pattern)

</details>

## Pattern 21 — Provider Hygiene: NotifierProvider vs NotifierProvider.autoDispose (LL-003)

**Source:** hermex_android (2026-07-05) → `~/Projects/hermex_android/app-spec/00_lessons_learned.md`

**⚠️ UPDATED for Riverpod 3.0 (2026-07-12):** In Riverpod 3.0, `AutoDisposeNotifier` class was **removed** and unified into `Notifier`. The auto-dispose decision is now on the **provider declaration**, not the class hierarchy. Always extend `Notifier`; control disposal with the provider type.

**Rule:** Use `NotifierProvider.autoDispose<>()` for transient UI state (form data, search queries). Use plain `NotifierProvider<>()` for data that must survive tab switches (server-fetched data, cached lists).

```dart
// ✅ Server data — survives tab switches (NO auto-dispose)
class TaskListNotifier extends Notifier<TaskListState> {
  @override
  TaskListState build() => TaskListState.initial();
  // ... methods
}
final taskListProvider = NotifierProvider<TaskListNotifier, TaskListState>(
  TaskListNotifier.new,
);

// ✅ Transient UI state — discarded when widget leaves tree (auto-dispose)
class SearchQueryNotifier extends Notifier<String> {
  @override
  String build() => '';
  // ... methods
}
final searchQueryProvider = NotifierProvider.autoDispose<SearchQueryNotifier, String>(
  SearchQueryNotifier.new,
);
```

**Why:** In Riverpod 3.0, `AutoDisposeNotifier`, `FamilyNotifier`, and `AutoDisposeFamilyNotifier` were all unified into `Notifier`. The `NotifierProvider.autoDispose<>()` constructor controls when state is discarded. Tab navigation causes rebuilds — auto-disposed providers lose cached data, so avoid `autoDispose` for server-fetched state.

---

<details>
<summary>📋 Full Original: LL-003</summary>

**LL-003: Riverpod Provider Hygiene — Notifier vs AutoDisposeNotifier
- **Date:** 2026-07-05
- **Stage:** Implementation (Phase 2)
- **Files Affected:** lib/features/tasks/providers/task_provider.dart
- **Lesson:** `TaskListNotifier` extends `Notifier` (not `AutoDisposeNotifier`) per DEC-034 rule 2 — providers that hold server-fetched data must survive tab switches and should not auto-dispose.
- **Root Cause:** AutoDisposeNotifier discards state when the listening widget is removed from the tree; tab navigation causes rebuilds that would lose cached task/session data.
- **Prevention Rule:** Only use `AutoDisposeNotifier` for transient UI state (form data, search queries). Use `Notifier` for data fetched from the server.
- **Linked Decision ID:** DEC-034

</details>

## Pattern 22 — Repository Null-Safety: Accept Nullable Dependencies (LL-006)

**Source:** hermex_android (2026-07-05) → `~/Projects/hermex_android/app-spec/00_lessons_learned.md`

**Rule:** All repositories MUST accept nullable `ApiClient` (or equivalent) and return safe defaults when the dependency is unavailable. Never assume the server is connected.

```dart
// ✅ CORRECT
class SkillsRepository {
  final ApiClient? _api;
  SkillsRepository(this._api); // nullable

  Future<List<Skill>> getAll() async {
    if (_api == null) return []; // safe default
    // ...
  }
}
```

**Why:** Providers may be read before server connection is established. Graceful degradation prevents runtime null errors cascading through the widget tree.

---

<details>
<summary>📋 Full Original: LL-006</summary>

**LL-006: Repository Null-Safety — Accept nullable ApiClient with safe defaults
- **Date:** 2026-07-05
- **Stage:** Implementation (Phase 2)
- **Files Affected:** lib/features/skills/data/skills_repository.dart, lib/features/workspace/data/workspace_repository.dart
- **Lesson:** Repositories that accept nullable `ApiClient` and return safe defaults (empty list) when no server is connected prevent null-check proliferation in providers.
- **Root Cause:** Providers may be read before a server connection is established; nullable ApiClient with graceful degradation avoids runtime null errors.
- **Prevention Rule:** All repositories should accept nullable dependencies and return safe defaults (empty list, null, cached data) when dependencies are unavailable.
- **Linked Decision ID:** N/A (pattern)

</details>

## Pattern 23 — isBusy Guard: Provider-Level Atomicity (LL-004)

**Source:** hermex_android (2026-07-05) → `~/Projects/hermex_android/app-spec/00_lessons_learned.md`

**Rule:** Guard all mutation actions (send, delete, pause, run-now) with an atomic `isBusy` check at the provider/notifier level — not widget-level debouncing.

```dart
Future<void> sendMessage(String text) async {
  if (state.isBusy) return; // ← atomic guard
  state = state.copyWith(isBusy: true);
  try {
    await _repo.send(text);
  } finally {
    state = state.copyWith(isBusy: false);
  }
}
```

**Why:** Widget-level debounce timers can be bypassed by rapid state changes. Provider-level `isBusy` is atomic and shared across ALL listeners.

---

<details>
<summary>📋 Full Original: LL-004</summary>

**LL-004: Duplicate Tap Prevention — isBusy state flag
- **Date:** 2026-07-05
- **Stage:** Implementation (Phase 2)
- **Files Affected:** lib/features/tasks/providers/task_provider.dart, lib/features/chat/providers/chat_provider.dart
- **Lesson:** A simple `isBusy` boolean flag in provider state prevents duplicate network requests from rapid double-taps more reliably than widget-level debouncing.
- **Root Cause:** Widget-level debounce timers can be bypassed by rapid state changes; provider-level `isBusy` flag is atomic and shared across all listeners.
- **Prevention Rule:** Always guard mutation actions (send, delete, run-now) with an atomic `isBusy` check at the provider/notifier level.
- **Linked Decision ID:** N/A (implementation pattern)

</details>

## Pattern 24 — Router Wiring Gate: Feature NOT Done Until Wired (LL-017)

**Source:** hermex_android (2026-07-06) → `~/Projects/hermex_android/app-spec/00_lessons_learned.md`

**Rule:** No feature is DONE until its screen is imported and wired in `app_router.dart`. The Traceability Matrix MUST include a "Router Wired" column.

```yaml
# Definition of Done for every feature:
  - Screen implemented: ✅
  - Tests passing: ✅
  - Router wired: ← MANDATORY column in traceability matrix
  - Smoke test reaches screen: ← MANDATORY
```

**Why:** 3 of 8 Hermex features (37.5%) were fully implemented with passing tests but unreachable because the router used placeholder stubs. The project's real completion rate was ~50%, not 100%.

---

<details>
<summary>📋 Full Original: LL-017</summary>

**LL-017: Router Wiring Gap — Code exists but screens not wired
- **Date:** 2026-07-06
- **Stage:** Post-Mortem (MoA Audit)
- **Source:** Triple Chinese MoA analysis of Hermex Android
- **Issue:** `chat_screen.dart`, `workspace_screen.dart`, and `skills_screen.dart` were fully implemented with passing tests, but `app_router.dart` used `_placeholderScreen()` stubs instead of importing and wiring the real screens. The Traceability Matrix marked F-002, F-005, F-006 as "✅ Implemented" — but users could never reach these screens because they weren't connected to the router.
- **Root Cause:** No governance rule required Router Wiring as an acceptance gate. The Lead Architect wrote the router with stubs during early development and never updated them after State Engineer completed the implementations. No smoke test verified that each feature route renders the real screen.
- **Impact:** 3 of 8 features (37.5%) were effectively dead code — implemented but unreachable. The project's real completion rate was ~50%, not 100% as the Traceability Matrix claimed.
- **Prevention Rule:** Router Wiring = Acceptance Gate. No feature is DONE until its screen is imported and wired in `app_router.dart`. The Traceability Matrix must include a "Router Wired" column.
- **Linked Decision ID:** N/A (governance gap — discovered in MoA audit)

</details>

## Pattern 25 — Provider Invalidation: Widget Layer, Not Provider Internals (LL-007)

**Source:** hermex_android (2026-07-05) → `~/Projects/hermex_android/app-spec/00_lessons_learned.md`

**Rule:** Providers MUST NEVER call `ref.invalidate` on themselves or their parent providers. Invalidation belongs in widget layer or dedicated controller providers.

**Why:** Calling `ref.invalidate` from within a provider's own method creates a circular dependency that breaks Riverpod's dependency graph.

---

<details>
<summary>📋 Full Original: LL-007</summary>

**LL-007: Provider Invalidation — Widget layer, not provider internals
- **Date:** 2026-07-05
- **Stage:** Implementation (Phase 2)
- **Files Affected:** lib/features/workspace/providers/workspace_provider.dart
- **Lesson:** `WorkspaceBrowserNotifier` does NOT call `ref.invalidate` internally — widget layer handles provider invalidation. Internal invalidation causes circular dependency chains in tests.
- **Root Cause:** Calling `ref.invalidate` from within a provider's own method creates a circular dependency that breaks Riverpod's dependency graph.
- **Prevention Rule:** Providers should never invalidate themselves or their parent providers. Invalidation belongs in the widget layer or in dedicated controller providers.
- **Linked Decision ID:** N/A (pattern)

</details>

## Pattern 26 — SSE Parser: Custom Format Handling (LL-002 + HERMEX-007)

**Source:** hermex_android (2026-07-05, 2026-07-12) → `~/Projects/hermex_android/app-spec/00_lessons_learned.md`

**Rule:** Always verify the ACTUAL SSE event format returned by the server. The Hermes Agent API uses a custom `assistant.delta` structure — NOT OpenAI's format. Build a custom parser using `dart:io HttpClient` instead of relying on third-party SSE libraries.

```dart
// Hermes Agent SSE event structure (custom):
// event: assistant.delta
// data: {"content": "...", "session_id": "..."}

// NOT OpenAI format:
// data: {"choices": [{"delta": {"content": "..."}}]}

// ✅ Parse against actual API response, not documentation
```

**Why:** Flutter SSE library ecosystem is immature. The Hermes API returns a custom event format different from standard OpenAI SSE. Never assume the format — verify with `curl` against the live server, then build the parser.

---

<details>
<summary>📋 Full Original: LL-002</summary>

**LL-002: SSE Streaming — Raw HttpClient over third-party SSE libraries
- **Date:** 2026-07-05
- **Stage:** Implementation (Phase 2)
- **Files Affected:** lib/core/api/sse_client.dart, lib/features/chat/
- **Lesson:** Custom SSE parser using `dart:io HttpClient` proved more reliable than immature Flutter SSE packages; manual SSE parsing (`data: {...}\n\n`) is straightforward.
- **Root Cause:** Flutter SSE library ecosystem immature — no production-ready package for raw SSE streaming.
- **Prevention Rule:** For non-mainstream protocols, prefer custom `dart:io` implementations over unproven third-party packages. Validate with integration tests.
- **Linked Decision ID:** ADR-001 (consequence noted)

</details>

<details>
<summary>📋 Full Original: LL-043</summary>

**LL-043: Hermes SSE Event Types — assistant.delta with delta:text format
- **Date:** 2026-07-12
- **Stage:** HERMEX-007 (SSE Streaming Fix)
- **Files Affected:** lib/core/api/sse_client.dart, lib/features/chat/providers/chat_provider.dart
- **Lesson:** The Hermes Agent API uses a custom SSE event type system: `event: assistant.delta` with `data: {"delta": "text"}` — completely different from OpenAI's `data: {"choices": [{"delta": {"content": "..."}}]}`. The parser must handle multiple event types: `assistant.delta`, `tool.progress`, `run.started`, `message.started`.
- **Root Cause:** The SSE parser was written assuming OpenAI-compatible format. Hermes Agent uses a custom event protocol where text arrives in `{"delta": "text"}` not `choices[0].delta.content`.
- **Prevention Rule:** Always capture and log the raw SSE `event:` type and `data:` structure before writing the parser. Handle at minimum: `assistant.delta` (streaming text), `tool.progress` (tool execution status), `run.started` (session start), `message.started` (message boundary). Fall through unknown event types with a warning log.
- **Linked Decision ID:** DEC-HERMEX-007-SSE

</details>

## Pattern 27 — Branch Hygiene: Verify Baseline Before Starting Work (LL-033)

**Source:** hermex_android (2026-07-11) → `~/Projects/hermex_android/app-spec/00_lessons_learned.md`

**Rule:** Before starting work on any shared branch, run `git log --oneline -5` and verify the HEAD commit matches the expected baseline. If stale WIP commits exist, `git reset --hard` to the last clean commit.

```bash
# BEFORE starting work:
git log --oneline -5          # Verify HEAD
flutter test --reporter compact # Establish true test baseline
flutter analyze                 # Establish true analyze baseline
```

**Why:** Stale WIP commits from prior sessions accumulate on shared branches. Workers inspecting the branch see artifact errors (32 analyzer issues, 9 test failures) and raise false alarms. Document the baseline commit ID in the task body.

---

<details>
<summary>📋 Full Original: LL-033</summary>

**LL-033: Theme Crisis False Alarm — Stale Workspace Artifacts
- **Date:** 2026-07-11
- **Stage:** RC4 Theme Verification
- **Files Affected:** `lib/core/theme/`
- **Lesson:** A WIP commit (`0a2c5e6`) on the `epic/rc4-polish` branch contained 32 analyzer errors and 9 test failures from a failed theme migration attempt. A worker inspecting the branch saw these artifact errors and raised a "theme crisis" alarm. The actual clean state was at `8aec1db` (0 errors, 484/484 pass) — the WIP commit was an abandoned save point from a different agent session, not the current working state.
- **Root Cause:** The branch contained orphaned WIP commits from a prior worker that did a force-push or rebase cleanup without removing the stale commit. No branch hygiene rule prevented stale/incomplete commits from accumulating on shared branches.
- **Prevention Rule:** Before starting work on a shared branch, run `git log --oneline -5` and verify the HEAD commit matches the expected baseline. If stale WIP commits are present, either (a) `git reset --hard` to the last clean commit, or (b) cherry-pick only completed fixes and abandon the WIP commit. Document the baseline commit ID in the task body.
- **Linked Decision ID:** N/A (branch hygiene)

---

## 2026-07-11 — RC5 Regression Fixes & Governance

</details>

## Pattern 28 — [DUPLICATE — See Pattern 13] SSE Duplicate Message Prevention: Snapshot BEFORE Streaming (LL-029 — Extended)

> ⚠️ **This pattern is a duplicate of Pattern 13** ("State Mutation Order: Snapshot BEFORE Mutating"). Both cover the same rule: take a snapshot/read derived state BEFORE mutating source state. Pattern 13 is the canonical reference. This section is retained only for the SSE-specific 4-step sequence example.

**Source:** hermex_android (2026-07-06, 2026-07-12) → `~/Projects/hermex_android/app-spec/00_lessons_learned.md`

**Rule:** When streaming responses, the history sent to the API must NEVER include the message that triggered the stream. Build history BEFORE appending the user message to state, and also BEFORE the stream delivers the agent response.

```dart
// Full correct sequence:
// 1. Build history (previous messages only)
final history = _buildHistory();
// 2. Add user message to local state
state = state.copyWith(messages: [...state.messages, userMsg]);
// 3. Stream with history (userMsg NOT in history)
await _repo.streamChat(history, userMsg);
// 4. Agent response arrives via SSE — append to local state
```

**Why:** If the API enforces strict user/assistant alternation, including the current user message in the history causes "two consecutive user messages" → API rejection.

<details>
<summary>📋 Full Original: LL-029</summary>

**LL-029: Duplicate User Messages — State Mutation Before History Capture
- **Date:** 2026-07-06
- **Stage:** First chat test after successful connection
- **Source:** User sent first message "السلام عليكم" — app crashed with API error
- **Issue:** `ChatNotifier.sendMessage()` added the user message to `state.messages` (line 254) BEFORE calling `_buildHistory()` (line 260). Since `_buildHistory()` reads from `state.messages`, the history included the just-added user message. Then `chat_repository.dart` added the same message AGAIN explicitly: `messages.add({'role': 'user', 'content': message})`. Result: two consecutive `role: user` messages in the API request. Hermes API enforces strict user/assistant alternation and rejected with "Invalid argument (string): Contains invalid characters."
- **Root Cause:** Mutation order bug — mutable state (`state.messages`) was updated before the snapshot (`_buildHistory()`) was taken. This is a classic React/Riverpod anti-pattern: reading derived state after mutating the source.
- **Fix:** Moved `final history = _buildHistory()` to BEFORE `state = state.copyWith(messages: [...state.messages, userMessage, agentMessage])`. History now contains only previous messages.
- **Prevention Rule:** 1) Never call a history/snapshot builder AFTER mutating the state it reads from. 2) Add a unit test for `sendMessage` that verifies exactly one user message appears in the API request body. 3) Consider a lint rule or PR checklist item: "Does any state.copyWith() precede a _buildHistory()-style snapshot?"
- **Bug Class:** NEW — this is a Flutter/Riverpod state management bug, NOT an Android knowledge gap. Different from LL-024/025/027 (which were Android build/config issues). Requires Dart-level testing, not Android-level gates.
- **Linked Decision ID:** N/A (state management pattern)

---

## 2026-07-07 — Operational Bug Recovery Session

</details>

## Pattern 29 — API Response Key Format: Use `data`, Not `messages` (LL-041)

**Source:** hermex_android (2026-07-12) → `~/Projects/hermex_android/app-spec/00_lessons_learned.md`

**Rule:** When parsing Hermes API responses, ALWAYS verify the actual response JSON key with `curl` against the live server before writing parser code. The Hermes API v0.18.2+ returns session messages under `data`, not `messages`. Debug-log the response keys during initial integration.

```dart
// ❌ BROKEN — looking for wrong key; silently returns empty list
final data = response.data['messages'] as List<dynamic>? ?? [];

// ✅ CORRECT — uses the actual API response key
final data = response.data['data'] as List<dynamic>? ?? [];
// Always debug-log response keys during integration:
Logger('ChatRepo').fine('Response keys: ${response.data?.keys}');
```

**Why:** API response structure changes silently between versions. An empty list propagates through the widget tree as "no data" instead of "API format mismatch." Debug-logging catches the mismatch immediately.

---

<details>
<summary>📋 Full Original: LL-041 (Session API Key Format)</summary>

**LL-041: Session API key format — Hermes API returns `data` not `messages`
- **Date:** 2026-07-12
- **Stage:** HERMEX-007 (Session-to-Chat Routing)
- **Files Affected:** lib/features/chat/data/chat_repository.dart
- **Lesson:** Hermes API v0.18.2 returns session messages under `{"data": [...]}` while ChatRepository.getSessionMessages() was searching for `json['messages']`. The API response key changed between versions — always verify with `curl` instead of relying on documentation.
- **Root Cause:** Assumed the API response key was `messages` based on earlier spec documentation; actual Hermes API v0.18.2 returns `data` as the root key for session message lists.
- **Prevention Rule:** Always log the API response keys during initial integration (`Logger('ChatRepo').fine('Response keys: ${response.data?.keys}')`). Verify the actual wire format with `curl` before writing parser code.
- **Linked Decision ID:** DEC-HERMEX-007-SESSION

</details>

## Pattern 30 — Build Responsibility: Lead Architect Coordinates, DevOps Builds (LL-044)

**Source:** hermex_android (2026-07-12) → `~/Projects/hermex_android/app-spec/00_lessons_learned.md`

**Rule:** The Lead Architect NEVER builds APK artifacts directly. BUILD execution belongs exclusively to `flutter-devops-release-engineer`. If a BUILD task completes without producing a verifiable APK artifact, it must be reassigned to the DevOps specialist.

```yaml
# BUILD task definition — always assign to DevOps:
  - assignee: flutter-devops-release-engineer    # ← NOT Lead Architect
  - actions:
      - flutter build apk --release
      - verify APK exists on disk
      - sign, version, and distribute
```

**Why:** BUILD responsibility separation prevents architectural blind spots from colliding with build configuration details. The DevOps specialist owns Android build configuration (namespace, ProGuard, signing, AGP version), while the Architect owns system design. This separation was codified after HERMEX-007 build coordination issues.

---

<details>
<summary>📋 Full Original: LL-044</summary>

**LL-044: Build Responsibility Boundary — Lead Architect does not build APKs
- **Date:** 2026-07-12
- **Stage:** HERMEX-007 (RC5 Coordination)
- **Files Affected:** Kanban task definitions, SOUL.md (Lead Architect), flutter-devops-release-engineer profile
- **Lesson:** The Lead Architect attempted to directly close BUILD tasks during HERMEX-007 coordination, bypassing the DevOps Release Engineer's build pipeline. BUILD tasks were marked "done" without producing a verifiable APK artifact.
- **Root Cause:** No explicit boundary in profiles prevented the Lead Architect from executing BUILD tasks. The Lead Architect's SOUL did not explicitly forbid direct build execution.
- **Prevention Rule:** All BUILD tasks must be assigned exclusively to flutter-devops-release-engineer. The Lead Architect may create and coordinate BUILD tasks but may not close them without verifiable APK output and DevOps approval.
- **Linked Decision ID:** DEC-HERMEX-007-BUILD

</details>

---

## Pattern 31 — Lessons Flow to Shared Knowledge Base (LL-045)

**Source:** hermex_android (2026-07-12) → `~/Projects/hermex_android/app-spec/00_lessons_learned.md`

**Rule:** Every EPIC's final task MUST be a DOCS task assigned to `flutter-documentation-steward`, whose job is to:
1. Read `~/.hermes/skills/flutter-lessons-patterns/SKILL.md`
2. Identify new lessons from this EPIC's `00_lessons_learned.md` entries
3. Check if they're already recorded as Patterns (dedup)
4. Add new Patterns (following the numbered format)
5. Source every pattern with project name and LL-ID

Never leave lessons only in project-level `00_lessons_learned.md` — they must be elevated to the shared knowledge base.

```bash
# EPIC close checklist — final task:
kanban_create \
  title="DOCS — Elevate lessons to shared knowledge base" \
  assignee=flutter-documentation-steward
```

**Anti-pattern:**
- Closing an EPIC without a documentation task
- Leaving lessons stranded in per-project `00_lessons_learned.md` only
- Duplicating patterns already recorded in the shared knowledge base
- A human having to manually compare project lessons with patterns

**Why:** Lessons learned are cross-project assets. Without elevation, each new project repeats the same failures. The documentation steward owns this gate as the final EPIC task.

---

<details>
<summary>📋 Full Original: LL-045</summary>

**LL-045: Lessons Flow to Shared Knowledge Base — EPIC final task gate
- **Date:** 2026-07-12
- **Stage:** HERMEX-007 (EPIC Closure)
- **Files Affected:** `~/.hermes/skills/flutter-lessons-patterns/SKILL.md`, EPIC task definitions
- **Lesson:** During HERMEX-007 closure, lessons were elevated to the shared knowledge base only if a dedicated DOCS task existed. Without this gate, LL-045 itself — the meta-pattern about elevating lessons — would have been left only in the project-level 00_lessons_learned.md.
- **Root Cause:** No governance rule required an EPIC's final task to be a DOCS handoff to the shared knowledge base. The documentation steward can only elevate lessons if a task exists.
- **Prevention Rule:** Every EPIC must end with a DOCS task assigned to flutter-documentation-steward. The task body must explicitly list which LL-IDs need elevation. The kanban board should enforce this as a gate (EPIC not closed until steward completes).
- **Linked Decision ID:** DEC-HERMEX-007-LESSONS

</details>

---

## Pattern 32 — Impact Analysis Before Implementation (LL-046)

**Source:** hermex_android (2026-07-12)

**Rule:** Before writing ANY code, ask: "what effect will this have?" Never implement without first analyzing the downstream impact on:
1. Other providers/notifiers that depend on the same state
2. Widgets that listen to state changes
3. API call order and response handling
4. Tests — will existing tests break?
5. Other features sharing the same data flow

```dart
// ❌ BROKEN — focused only on the immediate task, broke downstream features
void sendMessage(String text) {
  state = state.copyWith(messages: [...state.messages, userMessage]);
  // ← downstream ChatScreen broke because state mutated before history snapshot
}

// ✅ CORRECT — analyzed impact on all downstream consumers first
// 1. Check: who reads state.messages? → ChatScreen, _buildHistory()
// 2. Check: what order? → history must be taken BEFORE mutation
// 3. Plan: snapshot first, then mutate
final history = _buildHistory();
state = state.copyWith(messages: [...state.messages, userMessage]);
```

**Checklist before every implementation:**
- [ ] Which providers read this state?
- [ ] Which widgets listen to these providers?
- [ ] Does any API call depend on unchanged state?
- [ ] What test expectations would this change invalidate?
- [ ] Have I traced the full data flow from trigger → mutation → UI?

**Why:** Single-minded task execution is the #1 cause of regression bugs. Every Hermex Android regression (LL-029 duplicate messages, LL-023 fake connection, LL-022 redaction artifact, LL-042 disabled jobs filter) shares a common root cause: the implementer focused on what they were adding without checking what they would break. A 30-second impact analysis before coding prevents hours of debugging.

---

<details>
<summary>📋 Full Original: LL-046</summary>

**LL-046: Impact Analysis Before Implementation — Never code without downstream analysis
- **Date:** 2026-07-12
- **Stage:** HERMEX-007 (EPIC Closure — Post-Mortem)
- **Files Affected:** Multiple — cross-cutting pattern observed across all Hermex Android lessons
- **Lesson:** Every regression bug in Hermex Android (duplicate messages LL-029, fake connection LL-023, API key redaction LL-022, disabled jobs filter LL-042, build namespace LL-024, Isar+ProGuard LL-025, cleartext blocking LL-027) shares a common pattern: the implementer coded the immediate fix without analyzing what else their change would affect. A 30-second downstream impact analysis before implementation would have caught every single one.
- **Root Cause:** No meta-pattern exists that requires "impact analysis" as a pre-implementation step. Developers focus on the specific bug/feature without tracing the full data flow from trigger → mutation → API call → state change → UI update.
- **Prevention Rule:** Before any implementation, trace the full impact chain: Which providers read this state? Which widgets listen to these providers? Which API calls consume this data? What test expectations would this change invalidate?
- **Linked Decision ID:** N/A (meta-pattern — applies across all lessons)

</details>

## Pattern 33 — Stored First Decision: Never Re-Call Non-Deterministic APIs (Azdal Bug 2)

**Source:** Azdal (2026-07-12) — device-surfaced bug, not caught by any test suite

**Rule:** When a non-deterministic API call (LLM, timestamp-based, random) produces a decision that the UI acts on (showing confirm/edit buttons, routing to a screen, computing a threshold), **store that first result** keyed by the entity identifier. Never re-call the same API in a confirmation handler, save handler, or retry path.

```dart
// ❌ BROKEN — second Gemini call can return different (or null) result
Future<void> _sendMessage(String text) async {
  final txResult = await _tryAutoClassify(text);  // FIRST call
  if (txResult != null) {
    _showConfirmButtons(txResult);  // user sees "✅ Confirm"
  }
}

Future<void> _confirmTransaction() async {
  final txResult = await _tryAutoClassify(text);  // SECOND call — WRONG!
  if (txResult == null) {
    showSuccess();  // ← BUG: fake success when second call diverged
    return;
  }
  await saveTransaction(txResult);
}

// ✅ CORRECT — store first result, reuse on confirm
final Map<String, Map<String, dynamic>> _storedClassifications = {};

Future<void> _sendMessage(String text) async {
  final txResult = await _tryAutoClassify(text);  // ONLY call
  if (txResult != null) {
    final msgId = _latestUserMessageId();
    _storedClassifications[msgId] = txResult;      // STORE
    _showConfirmButtons(txResult);
  }
}

Future<void> _confirmTransaction() async {
  final txResult = _storedClassifications[_latestUserMessageId()];
  if (txResult == null) {
    showError('التصنيف غير متوفر');  // real error, not fake success
    return;
  }
  await saveTransaction(txResult);
  showSuccess();  // ← only after saveTransaction actually returns
}
```

**Why:** LLM output isn't deterministic — the same prompt can return different JSON structures on successive calls. The second call in `_confirmTransaction` can return `null` or a different `type`, and the code that follows shows a success message WITHOUT actually saving. The user is told "تم التسجيل ✅" when nothing landed in the database.

**Detection pattern:** Any `Future<void> _confirm*()` or `_save*()` method that calls an LLM/API function that was already called in the `_send*()` or `_show*()` method. Trace: was the first result stored? Is the second call using the stored result or re-calling?

**Prevention checklist:**
- [ ] Does `_confirm*()` call the same API as `_send*()`?
- [ ] Is the first call's result stored somewhere (map, state, message field)?
- [ ] Does the confirm path use the stored result, not re-call?
- [ ] Is success only shown AFTER the persistence call returns?
- [ ] On any failure (null result, save error), is a real error shown, not a fake success?

**Related:** Pattern 13 (snapshot before mutating — same class: "read the state you need BEFORE you change what you're reading from"), Pattern 32 (impact analysis — "what happens if the second call returns differently?").

---

## Pattern 34 — Riverpod Reactive Service: Bridge Platform SDK Callbacks to StateNotifier (Azdal Voice Refactor)

**Source:** Azdal (2026-07-12) — VoiceService refactor from manual `setState()` to Riverpod-reactive

**Rule:** When a service wraps a platform SDK that delivers state changes via callbacks (speech recognizer status, OCR scanning state, location updates, permission results), do NOT rely on the widget layer calling `setState()` to reflect those changes. The service MUST push state into a dedicated `StateNotifier` from inside its own callbacks — making the state Riverpod-reactive so ANY widget watching it rebuilds automatically, from ANY cause (user tap, internal timeout, platform event).

```dart
// ── The State (immutable) ──
final class VoiceListeningState {
  const VoiceListeningState({this.isListening = false, this.error});
  final bool isListening;
  final String? error;
  VoiceListeningState copyWith({bool? isListening, String? error, bool clearError = false}) {
    return VoiceListeningState(
      isListening: isListening ?? this.isListening,
      error: clearError ? null : (error ?? this.error),
    );
  }
}

// ── The Notifier ──
final class VoiceListeningNotifier extends StateNotifier<VoiceListeningState> {
  VoiceListeningNotifier() : super(const VoiceListeningState());
  
  void setListening(bool value) {
    if (state.isListening != value) {
      state = state.copyWith(isListening: value, clearError: true);
    }
  }
  
  void setError(String message) {
    state = state.copyWith(isListening: false, error: message);
  }
}

// ── The Service (takes notifier, updates from internal callbacks) ──
final class VoiceService {
  VoiceService(this._notifier);
  final VoiceListeningNotifier _notifier;
  
  Future<bool> initialize() async {
    return await _speech.initialize(
      onStatus: (status) {
        // ← Platform callback → Riverpod state: no setState() needed
        _notifier.setListening(status == 'listening');
      },
      onError: (error) => _notifier.setError(error.errorMsg),
    );
  }
}

// ── The Providers ──
final voiceListeningProvider = StateNotifierProvider<VoiceListeningNotifier, VoiceListeningState>(
  (ref) => VoiceListeningNotifier(),
);
final voiceServiceProvider = Provider<VoiceService>(
  (ref) => VoiceService(ref.read(voiceListeningProvider.notifier)),
);

// ── The Widget (reacts to any state change, not just taps) ──
Widget build(BuildContext context) {
  final listening = ref.watch(voiceListeningProvider);  // ← watches notifier
  return _InputBar(isListening: listening.isListening, ...);
}

Future<void> _toggleVoice() async {
  final service = ref.read(voiceServiceProvider);
  final listening = ref.read(voiceListeningProvider);
  if (listening.isListening) {
    await service.stopListening();
  } else {
    await service.startListening(...);
  }
  // No setState() — onStatus callback → notifier → Riverpod → rebuild
}
```

**Before (broken):**
- Service had `bool get isListening => _speech.isListening` — a plain getter
- Widget read `ref.watch(voiceServiceProvider)` but Riverpod couldn't track the getter
- Widget called `setState(() {})` manually after tap-initiated start/stop
- Internal timeout/auto-stop transitions were invisible → icon stuck in "active" state
- Required two extra taps to turn mic off

**After (fixed):**
- `onStatus` callback → `VoiceListeningNotifier.setListening()` → Riverpod detects change → widget rebuilds
- Works for ALL transitions: user tap, `pauseFor` auto-stop, internal recognizer events
- Same pattern ready for Stage 3 (OCR scanning state) and Stage 4 (goals/integrity updates)

**Why this over `ChangeNotifier` or `ValueNotifier`:**
- `StateNotifier` is immutable — `state = state.copyWith(...)` — no mutation bugs
- Riverpod's `ref.watch()` tracks it natively
- No `dispose()` footguns (unlike `ChangeNotifier`)
- Same pattern as `ChatProvider` — consistency across codebase

**When to use this pattern:**
- Any platform SDK with callback-based state (speech, camera, location, biometrics, BLE)
- Any service whose state can change from causes OTHER than direct widget-layer calls
- Stage 3 OCR: `OcrScanningState` (scanning, processing, done, error)
- Stage 4 goals: `GoalSyncState` (idle, syncing, synced, error)

**When NOT to use:**
- Pure widget-local state (use `StatefulWidget` with `setState`)
- One-shot operations with no intermediate state (just return `Future<T>`)
- Simple derived data (use `Provider` with computation)

**Related:** Pattern 1 (Provider Invalidation — same immutable state discipline), Pattern 21 (Provider Hygiene — auto-dispose decisions).

---

## Pattern 35 — Compute Derived Values Locally: Never Trust LLM Math (Azdal Compound Split)

**Source:** Azdal (2026-07-12) — device-surfaced bug, compound_split_card showing "الإجمالي: 0 ريال"

**Rule:** Any numeric value displayed to the user that is derived from multiple items (total, average, percentage, difference) MUST be computed by Dart/SQL code — never read from LLM JSON output. This applies regardless of whether the LLM was instructed to calculate it or not.

```dart
// ❌ BROKEN — reads total from Gemini JSON, defaults to 0 when absent
// AND goes stale the moment the user taps +/- adjusters
final total = (widget.json['total'] as num?)?.toInt() ?? 0;

// ✅ CORRECT — compute from mutable state, recalculates on every build
final total = _splits.fold<int>(
  0,
  (sum, s) => sum + ((s['amount'] as num?)?.toInt() ?? 0),
);
```

**Why this is NOT the same as Pattern 33:** Pattern 33 covers "don't re-call the LLM on confirm." This pattern covers "don't trust LLM-computed values in widget rendering." The LLM correctly follows DEC-003 ("لا تحسب أبداً") and does NOT compute the total — so `widget.json['total']` is absent → defaults to 0. The widget then shows a wrong value because it was designed to trust the very thing the architecture forbade.

**The system prompt is correct — the widget is wrong:** The architecture principle (DEC-003) says the LLM must never calculate. The system prompt enforces this. The widget was written as if the LLM would send a `total` field — it didn't, and shouldn't. Fix the widget, not the prompt (though a prompt hint helps).

**Detection checklist:**
- [ ] Does any widget read `widget.json['someNumber']` and display it?
- [ ] Is that number a derived value (sum, average, difference, percentage)?
- [ ] Is it computed locally from mutable state, or read once from static JSON?
- [ ] If the user adjusts sub-values (e.g. +/- buttons), does the total recalculate?
- [ ] If the LLM omits the field entirely, does it default to a correct value?

**Related:** Pattern 33 (Stored First Decision — same class: never trust LLM output as deterministic), `references/gemini-pitfalls.md` (system prompt must match widget expectations).

---

- Update this skill after every significant project milestone (CarSah, Hermex_Android, Azdal, RQS, etc.)
- Every new project MUST feed its programming lessons here — no more per-project lesson silos
- Patterns that become obsolete should be marked `[SUPERSEDED]` with reference to the replacing pattern
- Source every pattern with the project and lesson ID it came from
- Non-programming lessons (governance, process, swarm) → save to `~/.hermes/swarm/00_governance_lessons.md`
| HERMEX-007 lessons (LL-041 through LL-046) recorded by flutter-documentation-steward as the final kanban task of each EPIC — this file is the single source of truth for all cross-project Flutter lessons

## Pattern 36 — Ephemeral Message Lifecycle: Track Id, Remove, Replace (Azdal Chat)

**Source:** Azdal (2026-07-12) — OCR processing bubble fix + undo button replacement

**Rule:** When a bot message is a temporary/placeholder that will be replaced by a final result, the `ChatProvider` MUST support `removeMessage(String id)` and `addBotMessage`/`addUserMessage` MUST return the generated message id. The caller captures the id, and when the final state arrives, removes the placeholder and adds the replacement.

```dart
// ── Provider: addBotMessage returns id, removeMessage supported ──
String addBotMessage(String text, {Map<String, dynamic>? widget}) {
  final message = ChatMessage(id: _uuid(), ...);
  state = state.copyWith(messages: [...state.messages, message], ...);
  return message.id;  // ← caller captures this
}

void removeMessage(String id) {
  final updated = <ChatMessage>[...state.messages];
  updated.removeWhere((m) => m.id == id);
  state = state.copyWith(messages: updated);
}

// ── Caller: capture id, remove + replace when done ──
final processingId = chatNotifier.addBotMessage(
  '', widget: const {'widget': 'ocr_processing'},
);
// ... OCR runs ...
chatNotifier.removeMessage(processingId);          // 1. REMOVE placeholder
chatNotifier.addBotMessage('تم استخراج 3 بنود',   // 2. ADD final result
  widget: {'widget': 'compound_split_card', ...});
```

**Use cases from this session:**
1. OCR processing bubble ("جاري تحليل...") → removed when result/failure arrives
2. Undo button ("↩️ تراجع") → removed and replaced with plain "تم التراجع ✅" after use

**Without this pattern:** Three bubbles pile up (image, processing, result/failure) because neither success nor failure paths remove the placeholder. The undo button stays actionable after use.

**Why `removeMessage` + re-add instead of mutating in-place:** ChatState.messages is an immutable list. Riverpod detects the replacement as a new state. The UI rebuilds with the correct number of bubbles. In-place mutation would skip Riverpod's change detection.

**Related:** Pattern 13 (snapshot before mutating — same class: read before you write), Pattern 33 (stored-first decision — capture once, reuse). See also `references/azdal-chat-patterns.md` for the full Supabase soft-delete and cancel/undo integration patterns.

---

## Pattern 37 — LLM Must Not Emit Actionable UI: App Constructs UI From Verified Data (Azdal System Prompt Fix)

**Source:** Azdal (2026-07-12) — bug where "confirm" failed with "classification not available" on real transaction messages, confirmed via device logcat

**Rule:** When an LLM's output triggers UI that the user can ACT on (confirm, save, delete, approve), the LLM MUST describe data in plain text, and the app MUST construct the actionable UI from code. Never instruct the LLM to emit the actionable UI JSON directly — the app owns UI construction because only the app can verify and store the data the UI needs before showing it.

```dart
// ❌ BROKEN — system prompt tells Gemini to emit action_buttons JSON
const _systemPrompt = '''
عند تصنيف معاملة، أرسل رداً يحتوي على JSON widget بالصيغة التالية:
```json
{
  "widget": "action_buttons",
  "question": "هل التصنيف صحيح؟",
  "buttons": [
    {"label": "✅ صحيح", "value": "confirm", "type": "primary"},
    {"label": "🔄 تعديل", "value": "edit", "type": "secondary"}
  ]
}
```
''';

// Result: Gemini emits action_buttons → _sendMessage Path 1 (widget != null)
// shows it directly → _tryAutoClassify never called → _storedClassifications
// never populated → confirm taps fail with "classification not available"
```

```dart
// ✅ CORRECT — Gemini classifies in plain text; app builds UI from code
const _systemPrompt = '''
أنت أزدل — مساعد مالي ذكي سعودي.
تصنف المعاملات (فئة/فئة فرعية/نبرة: أخضر/رمادي/أحمر).
عبر عن التصنيف بنص عادي فقط — لا ترسل أزرار (action_buttons).
التطبيق هو المسؤول عن بناء أزرار التأكيد والتعديل بنفسه.
لا تحسب أبداً — الحسابات على Supabase.
''';

// Result: Gemini returns plain text → _sendMessage Path 2 (widget == null)
// → _tryAutoClassify runs → populates _storedClassifications →
// Dart code constructs action_buttons from verified data → confirm works
```

**The two incompatible code paths that created this bug:**

```
Path 1 (widget != null from main response):
  Gemini → action_buttons JSON → shown directly → _storedClassifications empty → CONFIRM FAILS

Path 2 (widget == null, _tryAutoClassify called):
  Gemini → plain text → _tryAutoClassify parses → _storedClassifications populated → CONFIRM WORKS
```

The system prompt actively pushed Gemini toward Path 1. Path 2 was the fallback that only triggered when Gemini chose NOT to emit a widget — but the prompt told it to emit one for every classification.

**Why this is NOT the same as Pattern 33:** Pattern 33 covers "don't re-call the LLM on confirm — use stored result." This pattern covers "don't let the LLM be the source of actionable UI — the app must construct UI from data it can store and verify." Pattern 33 is the storage mechanism; Pattern 37 is the system prompt discipline that ensures the storage mechanism is actually used.

**Compound split audit (same session):** `compound_split_card` was checked for the same bug class. Not affected — `_handleCompoundSplit` reads `splits` from the action callback payload, never from `_storedClassifications`. The splits travel through the action, not through stored state. Only `action_buttons` (simple transaction confirm) was broken by this pattern.

**Detection checklist before any LLM prompt design:**
- [ ] Does the prompt instruct the LLM to emit JSON that triggers a user action (confirm, save, delete, approve)?
- [ ] If yes: does the code path that receives this JSON populate the same storage that the action handler reads from?
- [ ] Is there a SECOND code path that constructs the same UI from Dart code? If so, which one fires more often?
- [ ] Would removing the JSON instruction from the prompt collapse to a single verified code path?

**Related:** Pattern 33 (Stored First Decision), Pattern 35 (Compute Derived Values Locally — same class: never trust LLM output as authoritative), `references/gemini-pitfalls.md` Pitfall 3 (same bug documented from system prompt perspective).

---

## Pattern 38 — Android INTERNET Permission on Custom OEM ROMs (Azdal Tecno HiOS)

**Source:** Azdal (2026-07-12) — device-surfaced DNS failure on Tecno LJ7 (HiOS), confirmed via logcat

**Rule:** Always declare `<uses-permission android:name="android.permission.INTERNET"/>` explicitly in `AndroidManifest.xml` — even though it's a "normal" permission that should be auto-granted on Android 6+. Certain OEM ROMs (Transsion HiOS/Tecno/Infinix/Itel) enforce normal permissions strictly, and apps without INTERNET permission fail ALL network calls with DNS `errno = 7` ("No address associated with hostname").

```xml
<!-- REQUIRED — do not rely on Android auto-granting "normal" permissions -->
<!-- Missing this on Tecno HiOS → every HTTP call fails with DNS errno 7 -->
<uses-permission android:name="android.permission.INTERNET"/>
```

**Symptoms (logcat):**
```
=== AZDAL DEBUG: Gemini sendMessage FAILED (unexpected) —
ClientException with SocketException: Failed host lookup:
'generativelanguage.googleapis.com' (OS Error: No address associated
with hostname, errno = 7)
```

**Why this is deceptive:**
- `errno = 7` (ENONET) looks like a network connectivity issue — Wi-Fi off, no data, airplane mode
- The user confirms Wi-Fi is on, mobile data is on, browser works fine
- But the app CANNOT resolve DNS because the OS-level INTERNET permission was never granted
- Both Gemini AND Supabase fail identically — the common factor isn't either API, it's the OS permission

**Detection:** Two or more unrelated hostnames failing with identical `errno = 7` in the same logcat section → OS-level denial, not API-specific failure.

**Related:** Pattern 11 (Official Android Sources Mandatory), `references/tecno-hios-permissions.md` (full reproduction recipe).

---

## Pattern 39 — Widget "Answered Once": Buttons Disabled After First Action (Azdal Widget Lifecycle)

**Source:** Azdal (2026-07-12) — duplicate-actions bug: cancelled a compound_split_card, and "✅ تأكيد" was still tappable afterward

**Rule:** Any message with actionable buttons (confirm, cancel, edit, undo) must become non-interactive after the first action. The provider stores `_answered: true` and `_selectedValue` in the message's widget map; renderers read these to disable all buttons and highlight the selected one. The provider call (`markWidgetAnswered`) happens FIRST in the action handler, BEFORE any async work — so the UI locks immediately even if the async operation takes seconds.

```dart
// ── 1. Provider: markWidgetAnswered merges into widget map ──
void markWidgetAnswered(String messageId, String selectedValue) {
  final index = state.messages.indexWhere((m) => m.id == messageId);
  if (index == -1) return;
  final updatedWidget = <String, dynamic>{
    ...?state.messages[index].widget,
    '_answered': true,
    '_selectedValue': selectedValue,
  };
  final updated = <ChatMessage>[...state.messages];
  updated[index] = state.messages[index].copyWith(widget: updatedWidget);
  state = state.copyWith(messages: updated);
}

// ── 2. Renderer: reads _answered, disables all buttons ──
Widget build(BuildContext context) {
  final answered = json['_answered'] == true;
  final selectedValue = json['_selectedValue'] as String?;
  return Opacity(
    opacity: answered ? 0.55 : 1.0,  // dim when answered
    child: Column(children: [
      for (final btn in buttons)
        ElevatedButton(
          style: answered && btn['value'] == selectedValue
              ? _selectedStyle
              : _normalStyle,
          onPressed: answered ? null : () => onAction?.call({...}),
        ),
    ]),
  );
}

// ── 3. Handler: mark FIRST, then do async work ──
case 'action_buttons':
  final msgId = action['message_id'] as String?;
  final value = action['value'] as String?;
  if (msgId == null || value == null) break;
  chatNotifier.markWidgetAnswered(msgId, value); // SYNC, before await
  if (value == 'confirm') {
    await _confirmTransaction(...);  // async after UI locks
  }
  break;
```

**The `message_id` injection pattern:** Instead of modifying each widget renderer, inject `message_id` at the `_MessageBubble` layer by wrapping the `onAction` callback:

```dart
renderCatalogWidget(
  message.widget!,
  onAction: onWidgetAction != null
      ? (action) => onWidgetAction!({
          ...action,
          'message_id': message.id,  // injects for ALL widgets
        })
      : null,
);
```

**Which actions use which consumption pattern:**

| Action | Pattern | After first tap |
|--------|---------|----------------|
| Confirm (✅ صحيح) | `markWidgetAnswered` | Buttons dimmed, selected highlighted, all disabled |
| Cancel (❌ إلغاء) | `markWidgetAnswered` | Card dimmed, both buttons disabled |
| Edit (🔄 تعديل) | `markWidgetAnswered` | Buttons disabled, editor in NEW message |
| Undo (↩️ تراجع) | `removeMessage` + replace | Button replaced with plain text |

**Do NOT use `markWidgetAnswered` for undo** — undo already consumes itself via `removeMessage` → replacement (Pattern 36). Both on the same action would double-consume.

**Detection checklist:**
- [ ] Does the handler call `markWidgetAnswered` BEFORE any `await`?
- [ ] Does the widget renderer check `_answered` and set `onPressed: null`?
- [ ] Does `_MessageBubble` inject `message_id` into every action?
- [ ] Are both `action_buttons` AND `compound_split_card` handled?
- [ ] Do answered messages stay answered after scroll rebuilds?
- [ ] Is undo NOT going through `markWidgetAnswered`?

**Related:** Pattern 36 (Ephemeral Message Lifecycle), Pattern 23 (isBusy Guard — provider-level atomicity against double-tap).

### Pitfall — Compound Split Button Conditional (fixed 2026-07-12)

A bug was introduced in the initial implementation of this pattern for `compound_split_card`. The `onPressed` conditions were:

```dart
// ❌ BROKEN — each button only disabled when the OTHER was selected
onPressed: (answered && !isCancelled) ? null : ...   // cancel button
onPressed: (answered && !isConfirmed) ? null : ...    // confirm button
```

The confirm button's condition `(answered && !isConfirmed)` evaluates to `false` when confirm was the selected action → the button stays LIVE → re-tapping re-runs the save (real duplicate). The cancel button had the same asymmetry but was harmless since re-cancelling is a no-op.

**Fix:** Both must use the unconditional pattern:
```dart
onPressed: answered ? null : ...  // ← same for ALL buttons
```

The highlighting logic (`isConfirmed ? _success : _cyan`) correctly shows which button was selected — only `onPressed` needs to be unconditional. This matches `_ActionButtonsWidget` which already used unconditional `answered ? null : ...` from the start.

---

---

## Pattern 40 — Full-File Rewrite Callback Verification (Azdal Camera Regression)

**Source:** Azdal (2026-07-13) — camera button grayed out after conversational redesign rewrite

**Rule:** When rewriting an entire widget file (using `write_file` instead of targeted `patch`), callbacks wired in the `build()` method are easy to accidentally replace with empty lambdas. After any full-file Flutter rewrite, run this checklist:

1. Search for `NOT IMPLEMENTED` or empty `() {}` lambdas in widget constructors
2. Verify every `on*` callback in the `build()` method matches the original
3. Specifically check: `onSend`, `onMic`, `onCamera`, `onTap`, `onChanged`, `onSubmitted`
4. Run `git diff --stat` to confirm only intended sections changed
5. Deploy to device and physically tap every interactive element

**Example bug:** During Azdal's conversational redesign, `chat_screen.dart` was completely rewritten. The `_InputBar` widget wiring inadvertently replaced `onCamera: _pickReceiptImage` with an empty lambda `onCamera: () { // NOT IMPLEMENTED }`. The analyzer didn't catch it (empty lambdas are valid Dart). Only live device testing caught it when the camera button appeared grayed out.

**Prevention:** Prefer targeted `patch` edits over full-file `write_file` for widget classes. When `write_file` is necessary (too many changes for patches), run the callback verification checklist immediately after.

**Detection:** `flutter analyze` will NOT catch empty callbacks. `flutter test` will NOT catch missing camera functionality. Only device testing catches this.

---

## Pattern 41 — Error-Handling Architecture: validateStatus + interceptor + sanitizeError (LL-047)

**Source:** hermex_android (2026-07-16) — RC6 Comprehensive Remediation

**Rule:** When designing Dio interceptors/middleware, trace the full object lifecycle from entry → processing → exit. Three errors compound fatally: (1) loose `validateStatus` that never throws on 4xx, (2) `onError` that classifies but calls `handler.next(error)` with the original DioException — discarding the classification, (3) duplicate `_classifyError` across files. Every error path MUST end with `_sanitizeError()` applied uniformly.

```dart
// ❌ BROKEN — three architectural flaws compound
validateStatus: (status) => status! < 500,  // 4xx never throws → interceptor never runs
// In onError:
final classified = _classifyError(response, error);
handler.next(error);  // ← DISCARDS classification — AuthException/ClientException are dead code

// ✅ CORRECT — tight validateStatus + reject with classified + sanitize uniformly
validateStatus: (status) => status! < 400,  // throws on all errors
// In onError:
final classified = _classifyError(response, error);
handler.reject(DioException(  // ← uses the CLASSIFIED exception
  requestOptions: error.requestOptions,
  error: classified,
));
// At every provider catch site:
try { ... } catch (e) {
  state = state.copyWith(errorMessage: _sanitizeError(e)); // uniform sanitization
}
```

**Check:** Write an integration test that triggers each error category (401, 403, 404, 500, connection-refused) and asserts the exact exception type and sanitized message reaches the provider. Never define exception classes without a test proving they are actually thrown.

**Why:** `AuthException` and `ClientException` were defined as classes but unreachable because `handler.next` bypassed the interceptor's classification entirely. Raw server body leaked to UI at 8+ catch sites in session_provider, chat_provider, and stream_provider because `_sanitizeError()` wasn't uniformly applied. The interceptor was designed incrementally — each piece added without tracing the full error flow from Dio → interceptor → provider → UI.

---

<details>
<summary>📋 Full Original: LL-047</summary>

**LL-047: Error-Handling Architecture — validateStatus + interceptor + sanitizeError
- **Date:** 2026-07-15
- **Stage:** RC6 Phase 2 Implementation
- **Files Affected:** lib/core/api/api_client.dart, lib/features/chat/providers/chat_provider.dart, lib/features/sessions/providers/session_provider.dart, lib/features/chat/providers/stream_provider.dart, lib/features/tasks/data/task_repository.dart
- **Lesson:** The Dio interceptor chain had three architectural flaws that compounded into a complete error-handling bypass. The fix rebuilt the chain: tight validateStatus, onError using classified exceptions via handler.reject(), and a single _sanitizeError() helper applied uniformly at 8+ error catch sites.
- **Root Cause:** The interceptor was designed incrementally — each piece added without tracing the full error flow. AuthException and ClientException were defined but unreachable because handler.next bypassed them.
- **Prevention Rule:** When designing interceptors/middleware, trace the full object lifecycle from entry → processing → exit. Write an integration test that triggers each error category and asserts the exact exception type and sanitized message reaches the provider.
- **Linked Decision ID:** ADR-010

</details>

## Pattern 42 — Certificate Pinning Uniform Wiring: Single ApiClient Provider (LL-048)

**Source:** hermex_android (2026-07-16) — RC6 Comprehensive Remediation

**Rule:** Exactly ONE provider must construct `ApiClient` instances in the entire app. All features consume it. Add a CI grep rule to verify no direct `ApiClient()` calls outside the provider.

```dart
// ❌ BROKEN — Chat/Tasks constructed ApiClient directly WITHOUT certificate pinner
final api = ApiClient(baseUrl: server.url, apiKey: key);  // NO pinner!

// ✅ CORRECT — single provider with pinner, all features consume it
final api = ref.watch(resolvedApiClientProvider);  // always wired with certificatePinner
```

```bash
# CI enforcement:
grep -rn "ApiClient(" lib/ --include="*.dart" | grep -v "api_client_provider.dart"
# MUST return zero matches. Any match = bypassed certificate pinning.
```

**Why:** Chat and Tasks providers bypassed TLS pinning entirely by constructing `ApiClient` directly without `certificatePinner`. Sessions/Insights/Memory/Workspace/Skills correctly went through `resolvedApiClientProvider`. Certificate pinning is security-critical — a single bypass path defeats the entire mechanism. The `apiClientProvider` itself was a dead stub always returning null, adding to the confusion. The fix unified all construction through one provider and removed the dead stub.

---

<details>
<summary>📋 Full Original: LL-048</summary>

**LL-048: Certificate Pinning Gap — Uniform wiring through single provider
- **Date:** 2026-07-15
- **Stage:** RC6 Phase 2 Implementation
- **Files Affected:** lib/features/chat/providers/chat_provider.dart, lib/features/tasks/providers/task_provider.dart, lib/core/providers/api_client_provider.dart
- **Lesson:** Chat and Tasks providers constructed ApiClient directly without certificatePinner, bypassing TLS pinning entirely. The fix unified ALL ApiClient construction through the single resolvedApiClientProvider.
- **Root Cause:** Multiple ApiClient construction paths evolved without a single gate. No audit verified uniform pinning across all instances.
- **Prevention Rule:** Exactly ONE provider must construct ApiClient instances. Add a CI grep rule. Certificate pinning is security-critical — a single bypass path defeats the entire mechanism.
- **Linked Decision ID:** B.7–B.10

</details>

## Pattern 43 — Reactive Profile Switching: Watch connectionProvider (LL-049)

**Source:** hermex_android (2026-07-16) — RC6 Comprehensive Remediation

**Rule:** Any provider that constructs a server-dependent resource (ApiClient, repository, SSE stream) MUST reactively watch the connection/session provider that owns server identity. Use `ref.watch(connectionProvider)` and rebuild the resource when the watched provider's server identity changes. Never guard with `isInitialized` when server identity is mutable.

```dart
// ❌ BROKEN — initialize-once pattern assumes immutable server identity
void initialize() {
  if (state.isInitialized && _repository != null) return;  // ← NEVER re-inits
  final server = await AuthManager.getActiveServerConfig(); // ← static snapshot
  _repository = ChatRepository(server.url, server.apiKey);
  state = state.copyWith(isInitialized: true);
}

// ✅ CORRECT — reactively watches, rebuilds on profile switch
@override
ChatState build() {
  final connection = ref.watch(connectionProvider);  // ← reactive
  final server = connection.activeServer;
  if (server == null) return ChatState.disconnected();

  _repository = ChatRepository(server.url, server.apiKey);
  return ChatState.ready(repository: _repository);
}
```

**Why:** `ChatNotifier.initialize()` read the active server once and guarded with `isInitialized` flag, making it blind to profile switches. Switching servers/profiles while the chat screen was alive left chat silently talking to the old server until the user manually tapped "New Chat." With multi-profile support (ADR-010), server identity can change at any moment — the provider must reactively watch, not cache.

---

<details>
<summary>📋 Full Original: LL-049</summary>

**LL-049: Reactive Profile Switching — Watch connectionProvider, don't cache once
- **Date:** 2026-07-15
- **Stage:** RC6 Phase 2 Implementation
- **Files Affected:** lib/features/chat/providers/chat_provider.dart
- **Lesson:** ChatNotifier.initialize read the active server once and guarded with isInitialized, making it blind to profile switches. The fix made it reactively watch connectionProvider.
- **Root Cause:** The initialize-once pattern assumes server identity is immutable during a screen's lifetime. With multi-profile support, it's not.
- **Prevention Rule:** Any provider that constructs a server-dependent resource MUST reactively watch the connection provider. Never guard with isInitialized when server identity is mutable.
- **Linked Decision ID:** ADR-010

</details>

## Pattern 44 — Gate Rescan Integrity: Re-test SPECIFIC Rejected Findings (LL-050 / ADR-012)

**Source:** hermex_android (2026-07-16) — RC6 Post-Mortem

**Rule:** Any security/QA gate that was previously REJECTED must, when re-scanned for PASS, explicitly re-test the SPECIFIC findings that caused the prior REJECT — with verifiable evidence attached. Re-verifying unrelated already-passing items does NOT constitute a valid re-scan.

```yaml
# Gate report template — REQUIRED section after any prior REJECT:
## Prior REJECT Findings
| Finding ID | Description | Status | Evidence |
|------------|-------------|--------|----------|
| AUD-RC5-001 | Raw exception leakage to UI | ✅ FIXED | grep shows 0 raw $e in catch blocks |
| AUD-RC5-002 | Missing auth error surfacing | ✅ FIXED | test_auth_exception_surfaced.dart passes |
```

**Why:** RC5 Gate2 REJECTED over AUD-RC5-001/002. A same-day "Gate4 rescan" declared PASS by re-verifying FLAG_SECURE, keystore, cleartext, and fonts — items that had never failed. The report never mentioned AUD-RC5-001/002. RC6 proved AUD-RC5-001 was still live in 8+ code sites. This mirrors LL-038 (theme tokens defined but not wired), LL-039 (release published before gates), and LL-040 (gate tasks done without validation) — all share the root cause of checking surface-level readiness without verifying the deep condition.

**Prevention:** Gate tasks MUST include a "Results / Evidence" field populated with verifiable output before transitioning to "done." The Lead Architect MUST independently verify gate evidence before closing any EPIC that had a prior REJECT. Codified as ADR-012.

---

<details>
<summary>📋 Full Original: LL-050</summary>

**LL-050: Gate Rescan Integrity — Re-test SPECIFIC rejected findings (H.26)
- **Date:** 2026-07-16
- **Stage:** RC6 Post-Mortem
- **Files Affected:** app-spec/12_decision_log.md (ADR-012)
- **Lesson:** RC5 Gate2 REJECTED over AUD-RC5-001/002. Same-day "Gate4 rescan" PASS never retested those findings. RC6 proved AUD-RC5-001 still live in 8+ code sites.
- **Root Cause:** The gate re-scan process had no rule requiring re-test of specific rejected findings. The auditor re-ran a standard checklist, not a targeted re-audit.
- **Prevention Rule:** Any gate PASS after REJECT MUST include a "Prior REJECT Findings" section with evidence for each. Codified as ADR-012.
- **Linked Decision ID:** ADR-012

</details>

## Pattern 45 — Bundled-Task Pattern for Shared-File Conflicts (LL-051)

**Source:** hermex_android (2026-07-16) — RC6 Coordination

**Rule:** During EPIC decomposition, run a file-affinity analysis: for each target file, count how many planned tasks would modify it. Files with ≥3 modifying tasks should either: (a) be bundled into a single assignee task, or (b) have tasks sequenced (not parallel) with explicit merge checkpoints.

```bash
# File-affinity analysis (run during EPIC decomposition):
# For each file in the planned changeset, count task assignments:
for file in $(git diff --name-only main...HEAD); do
  count=$(grep -l "$file" <task-specs> | wc -l)
  if [ $count -ge 3 ]; then
    echo "⚠️  $file — $count tasks → BUNDLE or SEQUENCE"
  fi
done
```

**Why:** `chat_provider.dart` was the nexus for 5+ RC6 defects (error handling, profile switching, model selection, message rendering, stream handling). Multiple specialist agents working on parallel tasks all modified the same file, creating a merge-conflict storm. Bundling all `chat_provider.dart`-touching work into a single Phase 2 task with a single assignee eliminated the conflicts. Parallel task decomposition had assumed file-level isolation that didn't hold.

**Prevention:** Add file-affinity analysis to the Lead Architect's EPIC decomposition checklist. When a file has ≥3 modifying tasks, prefer bundling over sequencing — merge conflicts are harder to resolve than a single large PR.

---

<details>
<summary>📋 Full Original: LL-051</summary>

**LL-051: Bundled-Task Pattern for Shared-File Conflicts (chat_provider.dart nexus)
- **Date:** 2026-07-16
- **Stage:** RC6 Coordination
- **Files Affected:** lib/features/chat/providers/chat_provider.dart
- **Lesson:** chat_provider.dart was the nexus for 5+ RC6 defects. Multiple parallel tasks all modified the same file creating a merge-conflict storm. Bundling into a single task eliminated conflicts.
- **Root Cause:** Parallel task decomposition assumed file-level isolation. No "shared file conflict" detection in Kanban pipeline.
- **Prevention Rule:** During EPIC decomposition, run file-affinity analysis. Files with ≥3 modifying tasks should be bundled or sequenced.
- **Linked Decision ID:** N/A (process pattern)

</details>

---

- **Last Updated:** 2026-07-18 — v2.15.0 — New Patterns 46–48 (Azdal Stage 4 cross-project): Never-Say-No-Data (cold-start UX), Live-Device Verification Supremacy (tests pass ≠ works), Regex-Gate Fallback + Disabled-Button Colors (LL-010, LL-011). Patterns count: 48.

---

## Pattern 46 — Never Say "No Data": Cold Start Intelligence (LL-009)

**Source:** Azdal (2026-05-16) → `~/Projects/Azdal/app-spec/00_lessons_learned.md`

**Rule:** Apps that say "add more transactions to see insights" lose users. The first experience MUST deliver value using whatever context is available — income brackets, general estimates, confidence levels. Give value first, then ask minimal questions (3 max).

```dart
// ❌ BROKEN — user sees "no data" on first open
if (transactions.isEmpty) {
  return Text("Add transactions to see your financial health");
}

// ✅ CORRECT — use estimates with confidence levels
final estimate = IncomeBracketEstimate.forRegion('SA');
return FinancialHealthCard(
  score: estimate.medianScore,
  confidence: ConfidenceLevel.low, // honest about uncertainty
  prompt: "Connect your bank for a personalized score →",
);
```

**Why:** Onboarding delivers insight before asking for input. 77% of finance app users quit in 3 days due to empty-state friction. Every additional tap required before the user sees value reduces retention.

---

<details>
<summary>📋 Full Original: LL-009</summary>

**LL-009: Never Say "No Data"**
- **Date:** 2026-05-16
- **Stage:** Triple-agent brainstorming
- **Lesson:** Apps that say "add more transactions to see insights" lose users. The first experience must deliver value.
- **Impact:** Designed Cold Start Intelligence: use income brackets, general estimates, confidence levels. Give value first, then ask minimal questions (3 max).
- **Rule:** Onboarding delivers insight before asking for input.
- **Source:** Azdal `01_prd.md`

</details>

---

## Pattern 47 — Live-Device Verification Supremacy (LL-010)

**Source:** Azdal (2026-07-14) → `~/Projects/Azdal/app-spec/00_lessons_learned.md`

**Rule:** "Tests pass" and "agent/auditor approved it" are necessary but NEVER sufficient. Before accepting any "done" report, reproduce the flow on a real device and query the live database directly — do NOT trust the app's own "success" message.

```bash
# ✅ Verification pipeline for any database-write feature:
# 1. Reproduce the exact user flow on a real device
# 2. Query the live database independently (do NOT trust app's success message)
# 3. Confirm: row exists + right values + right timestamp
PGPASSWORD='<pwd>' psql "postgresql://postgres:***@db.<ref>.supabase.co:5432/postgres" \
  -c "SELECT * FROM purchases WHERE user_id = '<uuid>' ORDER BY created_at DESC LIMIT 5;"
```

**Why (from Azdal Stage 4):** 5 critical bugs found AFTER `flutter analyze` clean, `flutter test` 34/34 passing, Zero-Trust Auditor APPROVE with 0 CRITICAL, and SCSI Guardian ALL CLEAR:
1. Purchase-confirmation insert against columns that don't exist on live table (100% failure rate)
2. Submit button never disabled (unlimited duplicate writes)
3. Success messages showing same sentence twice
4. Arabic-Indic numerals silently failing every form-field parse
5. A regression introduced BY the fix for #2 — key rename (`_form_kind` → `form_kind`) silently dropped

None were reachable by static analysis or unit tests. Every one found by: real device + direct database query.

---

<details>
<summary>📋 Full Original: LL-010</summary>

**LL-010: Passing Tests and Agent Self-Approval Are Not Verification**
- **Date:** 2026-07-14
- **Stage:** Stage 4 (BUY+INTG) live device testing
- **Lesson:** 5 critical bugs found on live device AFTER all gates passed. Unit tests re-derived target formulas as local constants instead of instantiating the actual service — they would pass unchanged against a broken implementation.
- **Rule:** Reproduce the flow live and check the live data source directly. Route B's own audit/guardian layer missed all 5 bugs.
- **Source:** Azdal `12_decision_log.md` DEC-036

</details>

---

## Pattern 48 — Regex Pre-Filter Gates + Disabled Button Colors (LL-011)

**Source:** Azdal (2026-07-15) → `~/Projects/Azdal/app-spec/00_lessons_learned.md`

**Rule A — Regex pre-filter fallback:** Any local keyword/regex gate standing in front of an LLM classifier for a correctness-critical feature MUST have a fallback path. A miss degrades to confidently-wrong-and-silent, not "slower but correct."

```dart
// ❌ regex-only gate — miss = silently falls through to generic chat
if (_looksLikeBuyIntent(message)) {
  return await purchaseService.evaluate(message);
}
// Falls through — user gets generic coach reply, purchase is silently ignored

// ✅ regex gate with safety-net classifier fallback
if (_looksLikeBuyIntent(message)) {
  return await purchaseService.evaluate(message);
}
// Fallback: if message is substantial (>20 chars, contains Arabic), 
// call classifier anyway as safety net
if (message.length > 20 && containsArabic(message)) {
  final intent = await classifier.classify(message);
  if (intent == Intent.buy) {
    return await purchaseService.evaluate(message);
  }
}
```

**Rule B — Disabled button colors:** `ElevatedButton.styleFrom(backgroundColor:, foregroundColor:)` only styles the ENABLED state. Once `onPressed: null`, Material silently substitutes its default disabled palette. Always set `disabledBackgroundColor`/`disabledForegroundColor` explicitly.

```dart
// ❌ custom colors silently lost when button is disabled
ElevatedButton(
  style: ElevatedButton.styleFrom(
    backgroundColor: Color(0xFF001F5E),
    foregroundColor: Colors.white,
  ),
  onPressed: isAnswered ? null : () => submit(),  // ← colors LOST when null
  child: Text("Submit"),
)

// ✅ explicit disabled colors
ElevatedButton(
  style: ElevatedButton.styleFrom(
    backgroundColor: Color(0xFF001F5E),
    foregroundColor: Colors.white,
    disabledBackgroundColor: Color(0xFF001F5E).withOpacity(0.5),
    disabledForegroundColor: Colors.white70,
  ),
  onPressed: isAnswered ? null : () => submit(),
  child: Text("Submit"),
)
```

**Verification:** When debugging button colors, measure actual RGB pixel values from a live screenshot — opacity-wrapper fixes treat the wrong layer and look plausible without fixing anything.

---

<details>
<summary>📋 Full Original: LL-011</summary>

**LL-011: A Local Regex Gate May Decide Cost, Never Correctness — And a "Disabled" Style Isn't Automatically Your Style**
- **Date:** 2026-07-15
- **Stage:** Second live-device retest of Stage 4, escalated to Opus 4.8
- **Lesson:** Two traps: (1) Regex pre-filters required exact hamza spelling, dropping common dialect typing silently. (2) ElevatedButton colors silently lost when disabled — only pixel-sampling a live screenshot revealed the real mechanism.
- **Rule:** Regex gates need fallback paths. Disabled button styles must be explicit.
- **Source:** Azdal DEC-037, DEC-037-B

</details>

## Related Skills

- **flutter-design-anti-patterns** — 31 Flutter design anti-patterns across 14 categories. Includes custom_lint plugin (3 core rules) and SPIKE regex detector. Load for any UI-related task. 🔗 `~/.hermes/skills/flutter/flutter-design-anti-patterns/`
- **flutter-input-hardening** — Centralized input sanitization and validation for Flutter
- **flutter-isar-clean-arch-setup** — Clean Architecture project structure with Isar + Riverpod
