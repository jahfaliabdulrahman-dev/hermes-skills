# Patterns 31-44 — Flutter Cross-Project Lessons

> Extracted from flutter-lessons-patterns SKILL.md (v2.24) — split for size. Read the index in SKILL.md for the classification map.

## Pattern 31 — Lessons Flow to Shared Knowledge Base (LL-045)
**Level:** 📏 RULE · SHOULD — Docs-flow gate — kanban can enforce but it's process


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
**Level:** 📏 RULE · SHOULD — Impact analysis — mental discipline, no tool


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

**Why:** Single-minded task execution is the #1 cause of regression bugs. Every regression in these codebases (LL-029 duplicate messages, LL-023 fake connection, LL-022 redaction artifact, LL-042 disabled jobs filter) shares a common root cause: the implementer focused on what they were adding without checking what they would break. A 30-second impact analysis before coding prevents hours of debugging.

---

<details>
<summary>📋 Full Original: LL-046</summary>

**LL-046: Impact Analysis Before Implementation — Never code without downstream analysis
- **Date:** 2026-07-12
- **Stage:** HERMEX-007 (EPIC Closure — Post-Mortem)
- **Files Affected:** Multiple — cross-cutting pattern observed across all project lessons
- **Lesson:** Every regression bug in these codebases (duplicate messages LL-029, fake connection LL-023, API key redaction LL-022, disabled jobs filter LL-042, build namespace LL-024, Isar+ProGuard LL-025, cleartext blocking LL-027) shares a common pattern: the implementer coded the immediate fix without analyzing what else their change would affect. A 30-second downstream impact analysis before implementation would have caught every single one.
- **Root Cause:** No meta-pattern exists that requires "impact analysis" as a pre-implementation step. Developers focus on the specific bug/feature without tracing the full data flow from trigger → mutation → API call → state change → UI update.
- **Prevention Rule:** Before any implementation, trace the full impact chain: Which providers read this state? Which widgets listen to these providers? Which API calls consume this data? What test expectations would this change invalidate?
- **Linked Decision ID:** N/A (meta-pattern — applies across all lessons)

</details>

## Pattern 33 — Stored First Decision: Never Re-Call Non-Deterministic APIs
**Level:** 📏 RULE · MUST NOT — Stored-first decision — no lint; test possible but no standing gate


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

## Pattern 34 — Riverpod Reactive Service: Bridge Platform SDK Callbacks to StateNotifier
**Level:** 📏 RULE · SHOULD — Reactive service pattern — design pattern


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

## Pattern 35 — Compute Derived Values Locally: Never Trust LLM Math
**Level:** 📏 RULE · MUST NOT — Compute locally — no lint distinguishes LLM-derived values


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

## Pattern 36 — Ephemeral Message Lifecycle: Track Id, Remove, Replace
**Level:** 📏 RULE · SHOULD — Ephemeral message lifecycle — implementation pattern


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

## Pattern 37 — LLM Must Not Emit Actionable UI: App Constructs UI From Verified Data
**Level:** 📏 RULE · MUST NOT — LLM prompt discipline — manual review


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

## Pattern 38 — Android INTERNET Permission on Custom OEM ROMs
**Level:** 🚪 GATE · MUST — AndroidManifest INTERNET permission — preflight/CI grep can verify; all network fails


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

## Pattern 39 — Widget "Answered Once": Buttons Disabled After First Action
**Level:** 📏 RULE · SHOULD — Answered-once widget — widget-testable but no standing gate


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

## Pattern 40 — Full-File Rewrite Callback Verification
**Level:** 📏 RULE · SHOULD — Rewrite callback checklist — manual verification


**Source:** Azdal (2026-07-13) — camera button grayed out after conversational redesign rewrite

**Rule:** When rewriting an entire widget file (using `write_file` instead of targeted `patch`), callbacks wired in the `build()` method are easy to accidentally replace with empty lambdas. After any full-file Flutter rewrite, run this checklist:

1. Search for `NOT IMPLEMENTED` or empty `() {}` lambdas in widget constructors
2. Verify every `on*` callback in the `build()` method matches the original
3. Specifically check: `onSend`, `onMic`, `onCamera`, `onTap`, `onChanged`, `onSubmitted`
4. Run `git diff --stat` to confirm only intended sections changed
5. Deploy to device and physically tap every interactive element

**Example bug:** During one project's conversational redesign, `chat_screen.dart` was completely rewritten. The `_InputBar` widget wiring inadvertently replaced `onCamera: _pickReceiptImage` with an empty lambda `onCamera: () { // NOT IMPLEMENTED }`. The analyzer didn't catch it (empty lambdas are valid Dart). Only live device testing caught it when the camera button appeared grayed out.

**Prevention:** Prefer targeted `patch` edits over full-file `write_file` for widget classes. When `write_file` is necessary (too many changes for patches), run the callback verification checklist immediately after.

**Detection:** `flutter analyze` will NOT catch empty callbacks. `flutter test` will NOT catch missing camera functionality. Only device testing catches this.

---

## Pattern 41 — Error-Handling Architecture: validateStatus + interceptor + sanitizeError (LL-047)
**Level:** 🚪 GATE · SHOULD — Integration test triggering every error class is mandated (LL-047); raw leakage = high


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
**Level:** 🚪 GATE · MUST — CI grep rule exists (LL-048); TLS pinning bypass = max severity


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
**Level:** 📏 RULE · SHOULD — Reactive watch — no lint


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
**Level:** 📏 RULE · SHOULD — Gate rescan integrity — audit process, manual


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