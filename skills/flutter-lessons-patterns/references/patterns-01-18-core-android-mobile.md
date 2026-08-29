# Patterns 1-18 — Flutter Cross-Project Lessons

> Extracted from flutter-lessons-patterns SKILL.md (v2.24) — split for size. Read the index in SKILL.md for the classification map.

## Pattern 1 — Provider Invalidation Rule (LL-003)
**Level:** 📏 RULE · SHOULD — Provider hygiene — no lint exists; review catches it


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
**Level:** 📏 RULE · SHOULD — Device verification — requires a human/physical device; can't be automated


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
- **Severity:** 🔴 High — applies to ALL future projects, not just the project that surfaced it
- **Prevention Rule:** QA must be decomposed into phases matching feature delivery groups. Each phase must pass its QA gate before the next phase begins implementation. The sequence should follow: F-001 build → QA → ✅ → F-002+F-003 build → QA integration → ✅ → F-004+F-005+F-006 build → QA → ✅ → F-007+F-008 build → QA → ✅ → Final integration QA → Zero-Trust Audit → Release.
- **Governance Impact:** This rule must be added to `FLUTTER_GLOBAL_CONTRACT.md` (new rule: "No Big Bang QA — Phased Testing Mandatory") and `flutter-lead-architect/SOUL.md` (decomposition constraint).
- **Linked Decision ID:** N/A (process gap — discovered in post-mortem)

</details>

## Pattern 3 — Zero Hardcoded Strings (LL-001 + LL-006 + LL-018)
**Level:** 🚪 GATE · MUST NOT — lint hardcoded_color exists (flutter-design-anti-patterns); retrofit costly


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
- **Issue:** `widget_test.dart` called `TheApp()` directly without wrapping it in `ProviderScope`. The main `runApp()` in `main.dart` does wrap with `ProviderScope`, but the test did not. This caused the most basic smoke test to fail: "TheApp renders without crashing — FAILED."
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
**Level:** 📏 RULE · SHOULD — Validator gating — widget tests can cover but no standing gate


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
**Level:** 📏 RULE · SHOULD — PR hygiene — process rule, review-enforced


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
**Level:** 📏 RULE · SHOULD — Spec sync — manual docs flow, no machine check


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
**Level:** 📏 RULE · SHOULD — Design before implementation — no tool can detect


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
**Level:** 🧭 JUDGMENT · MAY — BL size depends on team speed/project complexity — not universal


**Rule:** Every backlog item must be completable in ≤1 working day. BLs exceeding 1 day must be split. Any BL running >1 day is auto-blocked for architect review.

**Why:** Large BLs mask individual mismatches that compound into multi-round rework (one project's Stage 5 took 11 days because BLs spanned 3+ days).

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
**Level:** 🚪 GATE · MUST — android-preflight.sh exists and runs (LL-024 enforcement); crash = max severity


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
- **Root Cause:** 9-profile agent fleet generated code without coordination. DevOps Engineer set namespace, State Engineer set Kotlin package — no profile owned the end-to-end Android build correctness.
- **Impact:** App "لم يفتح نهائيا" (never opened). User saw nothing. Critical first-impression failure.
- **Prevention Rule:** Android Verification Gate §1 — namespace in build.gradle.kts MUST equal MainActivity.kt package. Automated script verifies before every release.
- **Linked Decision ID:** N/A (build configuration gap)

</details>

## Pattern 10 — Isar + ProGuard = Crash (LL-025)
**Level:** 🚪 GATE · MUST NOT — android-preflight.sh verifies isMinifyEnabled (LL-025); crash = max severity


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
**Level:** 📏 RULE · SHOULD — Skill-loading discipline — no automated check for a practice


**Source:** hermex_android (2026-07-06) — MoA-audited 2026-07-06 → `~/Projects/hermex_android/app-spec/00_lessons_learned.md`

**Rule:** No Flutter worker profile may work on Android build configuration without loading the official Android skills.

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
- **Root Cause:** 9-profile agent fleet generated code without coordination. DevOps Engineer set namespace, State Engineer set Kotlin package — no profile owned the end-to-end Android build correctness.
- **Impact:** App "لم يفتح نهائيا" (never opened). User saw nothing. Critical first-impression failure.
- **Prevention Rule:** Android Verification Gate §1 — namespace in build.gradle.kts MUST equal MainActivity.kt package. Automated script verifies before every release.
- **Linked Decision ID:** N/A (build configuration gap)

</details>


<details>
<summary>📋 Full Original: LL-026</summary>

**LL-026: Android Build Knowledge Gap — No official sources in the agent fleet
- **Date:** 2026-07-06
- **Stage:** Post-Mortem (Root Cause Analysis)
- **Source:** Comprehensive audit of all 9 Flutter profiles + Spec Pack
- **Issue:** Zero profiles had Android build knowledge. Words `namespace`, `ProGuard`, `applicationId` appeared NOWHERE in any SOUL file. Spec File 10 (DevOps) was 19 lines — no Android build configuration checklist.
- **Root Cause:** The agent fleet was designed for Dart/Flutter expertise only. Android native build system was an implicit blind spot — everyone assumed "someone else handles it."
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
**Level:** 🚪 GATE · SHOULD — detect.dart.py script exists (P0 severity scan)


**Source:** Impeccable-inspired gap analysis (2026-07-11)

**Rule:** Before any UI-facing Flutter task, also load `flutter-design-anti-patterns` — 31 deterministic design quality rules across 10 categories (color, typography, layout, states, a11y, i18n/RTL, components, performance, navigation, general).

**Why:** This skill covers logic/infrastructure patterns (providers, build config, i18n discipline). It does NOT cover visual design quality (hardcoded colors, container nesting, missing empty states, RTL padding, contrast). Both are needed for a complete pre-commit gate.

**Detection:** `python3 <skill-dir>/scripts/detect.dart.py lib/ --severity P0 --json`

**Baseline** (92 files): 15 hardcoded colors, 1 fixed-dimension widget, 2 missing text-scaling hits.

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
**Level:** 📏 RULE · MUST NOT — State mutation order — no lint; unit test can cover but no standing gate


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
**Level:** 🚪 GATE · MUST NOT — grep rule in CI (GOV-005); max severity — every API call fails silently


**Source:** hermex_android (2026-07-07) → `~/Projects/hermex_android/app-spec/00_lessons_learned.md`

**Rule:** Before any commit, verify no SOUL-redaction artifacts remain:
```bash
grep -rn "apiKey: \*\*\*" lib/ || true
grep -rn 'api_key: \*\*\*' lib/ || true
```

**Why:** SOUL-level security sanitization replaces API keys with `***` in output. These redacted outputs can be committed as literal source code (`apiKey: '***'`), silently breaking ALL authenticated API calls. The compiler does not catch this — `***` is valid Dart.

---

<details>
<summary>📋 Full Original: LL-022</summary>

**LL-022: Silent API Key Redaction — `***` literal replaced variable
- **Date:** 2026-07-07
- **Stage:** Production Bug Recovery
- **Source:** Abdulrahman report — "Agent Data (Skills, Memory, Insight) لا تعمل"
- **Issue:** Two files (`api_client_provider.dart:73`, `connection_screen.dart:226`) contained `apiKey: ***` as a literal string instead of the `apiKey` variable. This redaction artifact — likely from the fleet's SOUL-level security sanitization — silently broke ALL API-dependent features. Every request carried the literal HTTP header `Authorization: Bearer ***`.
- **Root Cause:** The agent fleet's security layer replaced actual API key values with `***` during output redaction. These redacted outputs were then treated as source code and committed. No human or automated gate detected that `***` is not valid Dart syntax referencing a variable named `apiKey`. The compiler does not flag this — `***` is valid Dart (three `*` operators).
- **Impact:** Skills, Memory, Insights, Chat streaming, and any feature relying on `ApiClient` failed silently. Health endpoint returned 401 but error messages were not surfaced properly. The app appeared functional but every API call received "Unauthorized."
- **Prevention Rule (PERMANENT — GOV-005):** No commit may pass if `grep -rn "apiKey: \*\*\*" lib/` or `grep -rn "api_key: \*\*\*" lib/` returns matches. These are SOUL-redaction artifacts that MUST be reverted to actual variable names before commit. Add to CI pre-commit hook and governance rules.
- **Process Impact:** Added to the agent operating playbook as a permanent pre-commit rule.
- **Linked Decision ID:** N/A (security sanitization defect)

</details>

## Pattern 15 — Fake Connection State: Never Set 'connected' Without Health Check (LL-023)
**Level:** 📏 RULE · MUST NOT — Health-check discipline — no automated detector; security-adjacent but manual


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
**Level:** 📏 RULE · SHOULD — Verify API params with curl — behavioral rule, no gate


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
- **Lesson:** A backend API's list endpoint defaults a flag to `false`, returning only enabled/active jobs. Paused jobs (`enabled: false`, `state: "paused"`) are silently excluded. The client's repository method was not passing `include_disabled=true`, so the page showed zero items despite 4 paused items existing in the backend.
- **Root Cause:** API contract spec (`06_api_contract.md` line 302) incorrectly stated "Returns all jobs regardless of status (active, paused, scheduled, etc.)" The actual default behavior excludes disabled jobs. The `include_disabled` query parameter was not documented in the spec, and the Flutter client did not pass it.
- **Verification:** `curl "http://localhost:8642/api/jobs"` → `{"jobs": []}`; `curl "http://localhost:8642/api/jobs?include_disabled=true"` → returns all 4 paused jobs. `hermes cron list` (CLI) also defaults to `include_disabled=False`.
- **Prevention Rule:** Always test API endpoints with `?include_disabled=true` when paused/disabled entities are expected. Document ALL query parameters in `06_api_contract.md`. For Flutter clients fetching entity lists that include paused items, always pass `include_disabled=true`.
- **Fix:** Add `'include_disabled': 'true'` to `queryParameters` in `TaskRepository.getAll()` (line 31 of `task_repository.dart`).
- **Linked Decision ID:** DEC-T3-JOBSFILTER

</details>

## Pattern 17 — Verify On Disk Before Claiming (Meta-Pattern — Sulaiman Session 2026-07-11)
**Level:** 📏 RULE · SHOULD — Meta-pattern: verify on disk before claiming — human/agent behavior


**Source:** 6 rounds of governance evaluation where claimed fixes did not exist on disk

**Rule:** Before dispatching any task for independent evaluation or marking it "complete," ALWAYS:
1. Read the actual file(s) that should contain the fix
2. Run the verification command in the terminal
3. Confirm the output matches the claim
4. THEN report the result

```bash
# BEFORE claiming "Dedup is fixed":
python3 <your>/violation_detector.py       # ← must show 0 violations
ls -la <your>/processed_violations.json    # ← must exist
```

**Never:** describe what SHOULD exist without verifying it DOES exist. The gap between "designed in my head" and "written to disk" has caused 5 rounds of failed evaluations.

---

## Pattern 18 — ProviderScope in Widget Tests: Mirror main.dart Exactly (LL-018)
**Level:** 🚪 GATE · MUST — Smoke test itself fails without ProviderScope — the test IS the gate


**Source:** hermex_android (2026-07-06) → `~/Projects/hermex_android/app-spec/00_lessons_learned.md`

**Rule:** Every Flutter widget test that renders the app must wrap it in `ProviderScope`, exactly as `main.dart` does. The smoke test ("App renders without crashing") must pass BEFORE any feature implementation begins.

```dart
// ❌ BROKEN — test calls TheApp() without ProviderScope
testWidgets('App renders', (tester) async {
  await tester.pumpWidget(const TheApp()); // CRASH — no ProviderScope
});

// ✅ CORRECT
testWidgets('App renders', (tester) async {
  await tester.pumpWidget(
    const ProviderScope(child: TheApp()),
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
- **Issue:** `widget_test.dart` called `TheApp()` directly without wrapping it in `ProviderScope`. The main `runApp()` in `main.dart` does wrap with `ProviderScope`, but the test did not. This caused the most basic smoke test to fail: "TheApp renders without crashing — FAILED."
- **Root Cause:** No rule mandated that the smoke test be written FIRST (before feature implementation) or that it must mirror the exact widget tree from `main.dart`. Smoke test was likely written after features were complete, and the ProviderScope dependency was missed.
- **Impact:** 402 tests passed but the single most important test — "does the app even load?" — failed. This means no one could verify end-to-end functionality through automated tests.
- **Prevention Rule:** Smoke Test First. Every Flutter project MUST have `App renders without crashing` as the FIRST test, mirroring `main.dart`'s widget tree exactly (including ProviderScope). This test must pass before any feature implementation begins.
- **Linked Decision ID:** N/A (governance gap)

</details>