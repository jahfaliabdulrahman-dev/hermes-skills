# Patterns 19-30 — Flutter Cross-Project Lessons

> Extracted from flutter-lessons-patterns SKILL.md (v2.24) — split for size. Read the index in SKILL.md for the classification map.

## Pattern 19 — Empty Catch Blocks FORBIDDEN in Security Paths (LL-019)
**Level:** 🚪 GATE · MUST NOT — avoid_empty_catch lint available; max severity (MITM/security)


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
**Level:** 📏 RULE · SHOULD — Route ordering — cheap to fix, low severity; no lint


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
**Level:** 📏 RULE · SHOULD — Provider auto-dispose intent — no lint can judge intent


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
**Level:** 📏 RULE · SHOULD — Nullable repository pattern — design pattern, no gate


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
**Level:** 📏 RULE · SHOULD — isBusy guard — implementation pattern, no lint


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
**Level:** 🚪 GATE · MUST — Router wiring verified by smoke-test-reaching-screen (LL-017 mandate); 37.5% dead code


**Source:** hermex_android (2026-07-06) → `~/Projects/hermex_android/app-spec/00_lessons_learned.md`

**Rule:** No feature is DONE until its screen is imported and wired in `app_router.dart`. The Traceability Matrix MUST include a "Router Wired" column.

```yaml
# Definition of Done for every feature:
  - Screen implemented: ✅
  - Tests passing: ✅
  - Router wired: ← MANDATORY column in traceability matrix
  - Smoke test reaches screen: ← MANDATORY
```

**Why:** 3 of 8 features in one project (37.5%) were fully implemented with passing tests but unreachable because the router used placeholder stubs. The project's real completion rate was ~50%, not 100%.

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
**Level:** 📏 RULE · MUST NOT — Invalidation ownership — no lint


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
**Level:** 📏 RULE · SHOULD — Verify actual SSE format with curl — behavioral


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
**Level:** 📏 RULE · SHOULD — Branch hygiene — work-start behavior, no gate


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
**Level:** 📏 RULE · MUST NOT — Duplicate of Pattern 13 — inherits RULE


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
**Level:** 📏 RULE · SHOULD — Verify API response key with curl — behavioral


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
**Level:** 🧭 JUDGMENT · MAY — Role separation depends on team structure — solo dev doesn't need it


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