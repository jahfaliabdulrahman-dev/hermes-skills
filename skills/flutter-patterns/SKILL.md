---
name: flutter-patterns
description: "Class-level Flutter patterns: ANR debugging, dialog localization, input hardening, widget wrapping, CI drift, image lifecycle, GoRouter routing. Covers general Flutter UI/UX, platform-integration, and navigation patterns that aren't Isar-specific. For Isar-specific Flutter patterns, see flutter-isar-clean-arch-setup."
tags: [flutter, patterns, anr, localization, input, widgets, ui, platform, genui, a2ui, gorouter, routing]
---
# Flutter General Patterns

Umbrella skill for general Flutter UI, platform-integration, debugging, and routing patterns. Covers all non-Isar-specific Flutter expertise accumulated across sessions.

## Absorbed Sub-Skills (use via labeled sections below)

| Sub-Skill | Content | Status |
|-----------|---------|--------|
| `flutter-anr-debugging` | Signal 3 ANR, Hero tag collisions, scrollbar assertion, Air-Lock pattern | Absorbed — see Section 1 |
| `flutter-dialog-localization` | Riverpod `_translations` map, zero hardcoded strings, ConsumerWidget conversion | Absorbed — see Section 2 |
| `flutter-dialog-transient-file-lifecycle` | `_didSave` flag pattern for orphan vs. saved file cleanup in dialogs | Absorbed — see Section 3 |
| `flutter-textfield-clipping` | Floating label clipping in RTL AlertDialogs, `isDense` + reduced `contentPadding` fix | Absorbed — see Section 4 |
| `flutter-widget-wrapping` | InkWell wrapping, bracket spiral rule, Dismissible wrapping, static method `t()` access | Absorbed — see Section 5 |
| `flutter-input-hardening` | `InputSanitizers` utility, Arabic-Indic digit sanitization, `detectTextDirection`, validators | Absorbed — see Section 6 |
| `flutter-image-lifecycle-atomic` | Normalized ref-counted InvoiceImage lifecycle, SHA-256 dedup, soft-delete GC | Absorbed — see Section 7 |
| `flutter-ci-environment-drift` | CI environment mismatch causing build failures, PATH/SDK resolution | Absorbed — see Section 8 |
| `ui-yield-protocol` | Yield main thread 500ms before heavy I/O to prevent InputMethodManager ANR | Absorbed — see Section 9 |
| `flutter-genui-a2ui` | Flutter GenUI SDK + A2UI protocol for agent-driven declarative UI (JSON, not eval) | Absorbed — see Section 10 |
| `riverpod-mutation-order` | Riverpod "Mutate Before Snapshot" TOCTOU anti-pattern — duplicate messages, API rejections | Absorbed — see Section 11 |
| `flutter-llm-integration` | Gemini prompt isolation, history filtering, two-paths collapse, defense-in-depth for LLM outputs | Absorbed — see Section 12 |
| `gorouter-stale-shellroute` | GoRouter `const NoTransitionPage` inside ShellRoute prevents rebuild on query change | Absorbed — see Section 13 |

---

## Section 1: ANR Debugging

**Full content** archived in `references/anr-debugging.md`

### Quick Reference

**Signal 3 ANR on Navigation** — Choreographer skips frames, process killed.
- **Root cause (90% of IndexedStack apps):** Hero tag collision — multiple FABs share default `<default FloatingActionButton tag>` → rendering pipeline crash
- **Fix:** Set `heroTag: null` on ALL FABs inside IndexedStack pages
- **Why null?** Disables Hero animation entirely — no tag lookup, no collision

**Scrollbar Assertion Crash in Dialogs:**
- `Scrollbar(thumbVisibility: true)` without explicit controller → crash in dialogs
- **Fix:** Remove `thumbVisibility` (platform default handles it) or provide explicit `ScrollController`

**Keyboard + I/O Thread Collision (Air-Lock Pattern):**
- Heavy Isar writes with active text fields cause InputMethodManager deadlock
- **Fix:** Navigate to a clean `LoadingScreen` before I/O — destroys widget tree, kills keyboard state
- Sequence: extract payload → `pushReplacement(LoadingScreen)` → `await Future.delayed(500ms)` → perform I/O

### When to Use Air-Lock
- First-launch setup wizards with Isar writes
- Batch imports triggered from forms
- Any I/O > 100ms from a screen with active `TextFormField`s

---

## Section 2: Dialog Localization

**Full content** archived in `references/dialog-localization.md`

### Quick Reference

Add translation key to `_translations` map in `settings_provider.dart`:
```dart
'key_name': {'en': 'English', 'ar': 'العربية'},
```

For standalone widgets needing `t()` (no `ref` in scope):
- `StatefulWidget` → `ConsumerStatefulWidget`
- `StatelessWidget` → `ConsumerWidget`
- Pull `t` via `final t = ref.watch(settingsProvider).t` in `build()`

**Key pitfalls:**
- Remove `const` from any widget calling `t()` at runtime
- Static methods can't access `ref` — pass `WidgetRef` as parameter
- Don't compose: `'${t('notes')} (${t('cancel')})'` — create dedicated key instead

---

## Section 3: Dialog Transient File Lifecycle

**Full content** archived in `references/dialog-transient-file-lifecycle.md`

### Quick Reference — The `_didSave` Flag Pattern

`dispose()` cannot distinguish "dialog cancelled" from "dialog saved then disposed." Both have `transientPath != null`. Without a flag, `dispose()` deletes files that were just saved.

```dart
mixin FileDialogLifecycle<T extends StatefulWidget> on State<T> {
  bool _didSave = false;  // THE CRITICAL FLAG

  void disposeFileLifecycle() {
    if (_didSave) return;  // Saved — skip orphan cleanup
    if (transientPath != null && transientPath != _originalPath) {
      _storage.deleteFile(transientPath!);  // Deletes orphan
    }
  }

  String? finalizeFilePath() {
    _didSave = true;  // BLOCKS dispose cleanup
    return transientPath;
  }

  void revertSaveConfirmation() {
    _didSave = false;  // On DB write failure
  }
}
```

**Critical:** Never use `flutter_image_compress` for local file persistence on Android 14+ — OS temp paths get GC'd during activity transitions. Use `dart:io File.copy()` instead.

---

## Section 4: TextField Clipping in RTL AlertDialogs

**Full content** archived in `references/textfield-clipping.md`

### Quick Reference

Floating label clips entered text in narrow RTL AlertDialogs (especially `OutlineInputBorder`).

```dart
TextFormField(
  decoration: InputDecoration(
    isDense: true,                          // ← Key fix
    contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 14),
  ),
)
```

`isDense: true` reduces internal height so the floating label doesn't overlap the entered text.

---

## Section 5: Widget Wrapping Patterns

**Full content** archived in `references/widget-wrapping.md`

### Quick Reference

**The Bracket Spiral Rule:**
When `patch` edits to a Flutter widget tree cause persistent bracket/indentation errors after 2-3 attempts — **STOP patching, rewrite the file entirely**. Symptoms: "Too many positional arguments," unexpected `)` errors, `balance += line.count('(') - line.count(')')` tracking shows +1 overall.

**InkWell Wrapping:**
```dart
// WRONG — Container clips ripple
Container(child: InkWell(onTap: onTap, child: ...))

// CORRECT — InkWell wraps Container
InkWell(
  onTap: onTap,
  borderRadius: BorderRadius.circular(12),
  child: Container(...)
)
```

**Dismissible Wrapping:** Always add the extra closing paren for the outer `Dismissible`:
```dart
child: Dismissible(
  key: ValueKey(record.id),
  onDismissed: (_) => _delete(record),
  child: _MyCard(record: record),
),  // ← DON'T FORGET
```

---

## Section 6: Input Hardening

**Full content** archived in `references/input-hardening.md`

### Quick Reference — `InputSanitizers` Utility

```dart
class InputSanitizers {
  // Cost regex: requires digit before optional dot (not \d* which allows leading dot)
  static final costFormatter = FilteringTextInputFormatter.allow(
    RegExp(r'^\d+\.?\d{0,2}'),
  );

  // Arabic-Indic digit sanitization (٠-٩ → 0-9)
  static String sanitizeDigits(String input) {
    for (final e in _arabicDigits.entries) {
      input = input.replaceAll(e.key, e.value);
    }
    return input.replaceAll(',', '');
  }

  static TextDirection detectTextDirection(String text) {
    for (final rune in text.runes) {
      if (rune >= 0x0600 && rune <= 0x06FF) return TextDirection.rtl;
    }
    return TextDirection.ltr;
  }
}
```

**Pitfalls:**
- `\d*\.?\d{2}` allows leading dot → `double.tryParse(".5")` returns null
- `detectTextDirection` needs `onChanged: (_) => setState(() {})` to trigger rebuild
- `textDirection` on TextField must be set at build time — requires state trigger

---

## Section 7: Image Lifecycle (Ref-Counted)

**Full content** archived in `references/image-lifecycle-atomic.md`

### Quick Reference

Normalized `InvoiceImage` entity with reference counting — prevents phantom files, refCount leaks, nested transaction deadlocks:

```dart
@collection
class InvoiceImage {
  Id id = Isar.autoIncrement;
  late String relativePath;    // "invoices/invoice_xxx.jpg"
  late String contentHash;     // SHA-256, unique index → dedup
  late int refCount;           // shared reference count
  DateTime? deletedAt;          // soft delete
}
```

**Critical rules:**
1. Never use `!` on nullable fields — local variable + null check always
2. Never nest `writeTxn` — inline refCount logic directly
3. Soft delete BEFORE physical delete — entity persists for GC
4. Dedup via SHA-256 hash, not path

---

## Section 8: CI Environment Drift

**Full content** archived in `references/ci-environment-drift.md`

### Quick Reference

Flutter CI builds fail due to environment mismatch (Flutter SDK version, Dart SDK, platform tools). Key symptoms:
- `flutter analyze` passes locally but fails on CI
- `dart run build_runner build` fails with version conflicts
- Missing platform folders (`ios/`, `android/`) in CI container

**Pre-flight verification in CI:**
```bash
flutter doctor
flutter --version
dart --version
# Check .dart_tool/package_config.json exists
```

---

## Section 9: UI-Yield Protocol

**Full content** archived in `references/ui-yield-protocol.md`

### Quick Reference

ANR (Signal 3) when user action triggers heavy I/O while keyboard or animation is still active.

```dart
Future<void> _onSave() async {
  setState(() => _isLoading = true);           // 1. Lock UI first
  FocusScope.of(context).unfocus();            // 2. Dismiss keyboard
  await Future.delayed(Duration(milliseconds: 500));  // 3. YIELD
  await _executeDatabaseOperations();         // 4. Safe I/O
  if (mounted) Navigator.of(context).pop();    // 5. Navigate
}
```

**Timing:**
| Scenario | Minimum Delay |
|----------|--------------|
| Release build, warm start | 150ms |
| Debug build, warm start | 300ms |
| Debug build, first launch | 500ms |

Use 500ms as default. `await Future.delayed` (not `Timer`) ensures main thread yields.

---

## Section 10: GenUI & A2UI — Agent-Driven Dynamic UI

**Full content** archived in `references/genui-a2ui.md`

### Quick Reference

**What it is:** Google's official Flutter GenUI SDK (beta, Dec 2025) + A2UI protocol. AI agents describe UIs via declarative JSON, Flutter renders from a pre-built widget catalog. No runtime code execution — app-store-safe.

**Package:** `genui_a2ui` on pub.dev

**Key facts:**
- Agent sends JSON UI schema → Flutter renders from widget catalog
- Declarative only — NO `eval()`, NO code generation
- Widget catalog: `summary_card`, `bar_chart`, `pie_chart`, `line_chart`, `action_buttons`, `quick_input_form`
- RTL/Arabic support via Flutter's built-in `Directionality`

**When to use:**
- AI agent apps needing dynamic UI (not hardcoded screens)
- Conversational interfaces with data visualization
- Fintech dashboards composed by LLM based on user questions

**When NOT to use:**
- Standard apps with fixed screens — use regular Flutter widgets
- If you need runtime code execution — this is NOT that

**Difficulty calibration:** 5/10 for MVP dynamic UI (not 9/10). Prior assessment of "near impossible" was wrong — the JSON widget catalog approach is well-defined. The hard part is the agent prompt engineering (getting the LLM to output valid schema JSON), not the Flutter rendering.

**Pitfalls:**
- Agent CANNOT invent new widget types — catalog must be pre-built
- Each interaction round-trips: user tap → agent → new JSON. Manage latency.
- Beta status — test thoroughly before production
- **Gemini CLAIMS "agent writes Flutter code at runtime" — this is FALSE and dangerous. Reality: agent outputs declarative JSON against a fixed widget catalog. No eval(). No code generation. Correct this misconception immediately if any AI claims otherwise.**
- Claude accurately identified GenUI/A2UI existence via official Google sources (developers.googleblog.com, docs.flutter.dev, pub.dev), while Hermes originally rated it 9/10 "impossible" — the correction is: it's 5/10 difficulty, JSON widget catalog, and app-store-safe by design.
- **ISSUE RESOLVED 2026-05-16:** The 3-agent cross-validation (Gemini → Hermes → Claude) converged: GenUI/A2UI is viable. Gemini overstated it (code generation claim). Hermes understated it (near-impossible claim). Claude hit the accurate middle: declarative JSON from widget catalog.

**Plan B — If GenUI SDK Fails:**
If the beta Flutter GenUI SDK has bugs (RTL, component failures, pub.dev issues):
- Keep the SAME JSON schemas — don't throw away the work
- Swap only the renderer to native Flutter widgets:
  - `action_buttons` → `Wrap` of `ElevatedButton`/`OutlinedButton`
  - `summary_card` → Flutter `Card` widget
  - `quick_input_form` → `TextField` with `InputDecoration`
  - `bar_chart` / `pie_chart` → `fl_chart` package
- The JSON schema becomes a pure logic/config layer; rendering is native
- This is architecturally clean because A2UI separates "describe UI" from "render UI"

---

## Section 11: Riverpod State Mutation Before Snapshot (TOCTOU)

**Full analysis** archived in `references/riverpod-mutation-order.md`

### Quick Reference — The Anti-Pattern

Calling a snapshot/history builder AFTER mutating `state` via `state.copyWith()` causes the snapshot to include the just-added mutation. If a downstream layer also adds the same data, you get duplicates.

```dart
// WRONG — history includes the just-added user message
state = state.copyWith(
  messages: [...state.messages, userMessage, agentMessage],  // 1. MUTATE
  isStreaming: true,
);
final history = _buildHistory();  // 2. SNAPSHOT — too late! Includes userMessage
_repository.streamChatCompletion(message: msg, history: history);  // 3. Adds userMessage AGAIN
// → API receives two consecutive role:user → API rejection

// CORRECT — snapshot BEFORE mutation
final history = _buildHistory();  // 1. SNAPSHOT — immutable view of previous state
state = state.copyWith(
  messages: [...state.messages, userMessage, agentMessage],  // 2. MUTATE
  isStreaming: true,
);
_repository.streamChatCompletion(message: msg, history: history);  // 3. Clean
// → API receives one role:user → proper alternation
```

### Detection Rule

> Does any `state.copyWith()` precede a `_buildHistory()`-style snapshot call in the same method? If so, move the snapshot BEFORE the mutation.

### Common Locations

- `ChatNotifier.sendMessage()` — history builder for SSE API requests
- Any notifier that builds API request context from `state` before mutating it
- Task providers that snapshot filter state before adding a new item

### Sister Patterns

- **LL-004:** `isBusy` guard in provider prevents duplicate network requests from rapid double-taps — same "prevent duplicates at provider level" philosophy
- **LL-007:** Provider invalidation ordering — calling `ref.invalidate` from within a provider creates circular dependencies — same class of "mutation order matters in Riverpod"

### When to Suspect This Bug

- API rejects with "Invalid argument" or 400 on message alternation
- Duplicate user messages appear in chat UI but only one was typed
- Debug logs show two consecutive `role: user` in the request body
- The bug appeared after a `_buildHistory()` call was added to include conversation context

---

## Section 12: LLM/Prompt Integration Patterns

**Full analysis** archived in `references/llm-prompt-isolation.md`

### Quick Reference — Four Patterns

#### Pattern 1: System Prompt Isolation (Separate Prompts Per Purpose)

When a Flutter app uses the same LLM for multiple purposes (chat + classification + OCR), a SINGLE system prompt causes cascading failures. Adding a prohibition like "don't emit widgets" blocks the CLASSIFICATION call too.

```dart
// WRONG — one prompt controls everything
const _systemPrompt = 'لا ترسل أبداً compound_split_card.';  // kills classification!

// CORRECT — separate prompts per purpose
const _systemPrompt = 'عبر عن التصنيف بنص عادي.';  // chat only
const _classifyPrompt = '"{"widget": "compound_split_card", ...}"';  // classification only

// Dedicated method with its own prompt
Future<GeminiResponse> classifyTransaction(String text) async {
  final model = GenerativeModel(
    systemInstruction: Content.system(_classifyPrompt),  // ← DIFFERENT prompt
  );
  return model.generateContent([Content.text(text)]);
}
```

**Rule:** Every distinct LLM purpose (chat, classification, OCR, summarization) gets its OWN system prompt. Never share.

#### Pattern 2: Two-Paths Collapse (Single Authoritative Code Path)

When an LLM's main response can produce the same UI widget as a separate classification call, one path bypasses critical logic.

```dart
// WRONG — two paths produce identical confirm UI
if (response.widget != null) {
  showWidget(response.widget);           // Path 1: Gemini's widget (no classification data)
} else {
  final txResult = await classify(text);  // Path 2: App's classification (has data)
  showWidget(buildConfirmUI(txResult));   // ← Path 1 shows SAME UI without data!
}

// CORRECT — collapse to one authoritative path
// Main response: text only. Classification: the SOLE source of actionable widgets.
if (response.widget != null) {
  if (isTransactionWidget(response.widget)) { /* DROP — fall through */ }
  else { showWidget(response.widget); return; }
}
final txResult = await classify(text);  // ← ALWAYS reached for transactions
showWidget(buildConfirmUI(txResult));
```

**Rule:** If Gemini can produce the same UI through two different routes, delete one. Classification is the gatekeeper.

#### Pattern 3: History Filtering (Don't Feed Processed Items to the LLM)

LLMs see conversation history as unprocessed data. A confirmed/saved transaction from message #1 looks identical to a new transaction in message #2. The LLM has no way to know #1 was handled.

```dart
// WRONG — sends ALL user messages
final history = allMessages.where((m) => m.isUser).toList();

// CORRECT — filter out processed messages
final filtered = allMessages.where((m) {
  if (!m.isUser) return true;
  return !_confirmedMessageIds.contains(m.id);  // skip handled transactions
}).toList();
```

**Rule:** Before sending history to an LLM, strip user messages whose content has already been classified and acted upon.

#### Pattern 4: Defense-in-Depth (Prompt + Code Gate)

Never trust a single prompt constraint. Add a code-level gate that blocks LLM output even if the prompt fails.

```dart
// Layer 1: Prompt says "don't emit compound_split_card"
// Layer 2: Code gate — even if Layer 1 fails, this catches it
if (widgetType == 'compound_split_card' || widgetType == 'action_buttons') {
  // DROP — fall through to classification path
}
```

**Rule:** For every prompt-level constraint, add a code-level gate. Two layers > one.

### When to Suspect These Bugs

- Transaction confirmation fails with "classification not available" (Pattern 2)
- Second transaction merges with first into compound split (Pattern 3)
- Prompt fix X breaks feature Y (Pattern 1)
- Same widget appears correctly sometimes but not others (Pattern 2)

---

## Section 13: GoRouter — Stale Page Inside ShellRoute

**Full analysis** archived in `references/gorouter-stale-shellroute.md`

### Quick Reference — The `const NoTransitionPage` Trap

When using `pageBuilder` with `const NoTransitionPage` inside a GoRouter `ShellRoute`, the SAME Page object is returned for every navigation regardless of query parameters. GoRouter compares old and new Page references — finding them identical, it never rebuilds the widget tree, so `didChangeDependencies()` never fires.

```dart
// ❌ WRONG — Same Page object always. Stale UI on session switch.
GoRoute(
  path: '/chat',
  pageBuilder: (context, state) => const NoTransitionPage(
    child: ChatScreen(),
  ),
),

// ✅ RIGHT — Unique key per URI forces rebuild on query change.
GoRoute(
  path: '/chat',
  pageBuilder: (context, state) => NoTransitionPage(
    key: ValueKey(state.uri.toString()),
    child: const ChatScreen(),
  ),
),
```

### The Mechanics

1. Navigate to `/chat?session=A` → key `ValueKey('/chat?session=A')`
2. Navigate to `/chat?session=B` → key `ValueKey('/chat?session=B')`
3. Flutter: different keys → different widgets → tree rebuild → `didChangeDependencies()` fires → `_initChatIfNeeded()` detects new session

### Symptoms

- Opening any session after the first shows the FIRST session's title and messages
- `didChangeDependencies()` breakpoint never hits after first navigation
- Data from server is correct (verified via curl) — pure Flutter routing issue

### Detection Rule

> Does a `ShellRoute` pageBuilder use `const NoTransitionPage`? And does the target screen read query/path parameters in `didChangeDependencies()`? Add `key: ValueKey(state.uri.toString())`.

### What NOT to Touch

Leave any `_lastSessionId` guard in the target screen as defensive fallback — with the key fix, the screen rebuilds fresh per session, so the guard becomes harmless redundancy.

### Verification (Mandatory)

- `flutter analyze`: 0 new errors
- `flutter test`: no regressions (widget tests don't exercise ShellRoute navigation)
- **Device smoke test:** Open session A → back → open session B → verify B's title/messages appear (not A's). Repeat with session C. Tab switching (Chat ↔ Sessions) without opening a new session should preserve scroll/text state.