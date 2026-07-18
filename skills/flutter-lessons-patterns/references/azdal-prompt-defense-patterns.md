# Azdal — Prompt Architecture & Code-Level Defense Patterns

> Added: 2026-07-13. Source: Azdal conversational redesign session (16 commits, 7 prompt iterations).

## Pattern 1: Dedicated Classify Method with Isolated Prompt

**Problem:** When a single Gemini API key serves both chat conversation AND transaction classification, the system prompt for one call interferes with the other. Prohibitions added to the chat prompt ("never emit action_buttons") kill the classification call too — Gemini can't distinguish which call the prohibition applies to.

**Fix:** Add a dedicated classification method that uses its OWN system prompt, completely separate from the main chat prompt:

```dart
// Wrong: both calls share _systemPrompt
final response = await geminiService.sendMessage(classifyPrompt);

// Right: classification has its own prompt, no history
final response = await geminiService.classifyTransaction(text);
```

The dedicated method:
- Has its own `_classifySystemPrompt` with explicit JSON-formatting instructions
- Receives ZERO conversation history (prevents cross-message contamination)
- Returns structured data that the caller branches on

**Pitfall:** Don't add prohibitions to the main prompt that the classification prompt needs. Instead, separate them completely. If the main prompt says "never emit compound_split_card", the classification call must use a different prompt that explicitly allows it.

## Pattern 2: Code-Level Defense Over Prompt Rules

**Problem:** Prompt-based anti-merge rules ("don't merge with previous messages", "only handle the last one") are fragile, stochastic, and cause negative interference. Three separate attempts at this during the history leak fix proved counterproductive — each prompt rule created a new regression.

**Fix:** Use code-level defenses that are deterministic and reliable:

| Layer | Mechanism | What It Guards |
|-------|----------|---------------|
| 1 — History filter | Exclude classified messages from Gemini history via `_storedClassifications` map | Cross-message merging structurally impossible |
| 2 — Widget gate | Drop `action_buttons`/`compound_split_card` from main response in `_sendMessage` | Main chat never trusted for transaction UI |
| Classification | `classifyTransaction()` with own prompt, no history | Single-message classification only |

**Rule:** Never add anti-merge language to prompts. Merge safety comes from code structure (history isolation), never from prompt wording.

## Pattern 3: Immediate Mark-on-Send

**Problem:** Classification is async. The history filter runs before classification completes. If classification fails, the message's ID is never stored in the filter map → it leaks into the next `sendMessage`'s history.

**Fix:** Mark messages as "in-flight" IMMEDIATELY when they enter the send pipeline, BEFORE any Gemini call:

```dart
final userMsgId = chatNotifier.addUserMessage(text);
_storedClassifications[userMsgId] = <String, dynamic>{}; // immediate placeholder

// ... later, _tryAutoClassify overwrites with real data
_storedClassifications[lastUserMsgId] = txResult;
```

**Critical detail:** Compute the filter BEFORE marking the current message (or explicitly include `m.id == userMsgId` in the filter). Otherwise the current message gets filtered out too.

## Pattern 4: Router-First Design (Digit Gate)

**Problem:** Running both a chat call AND a classification call for every message is wasteful and produces incoherent responses when both calls' outputs are stitched together.

**Fix:** Gate on whether the message contains a digit:

```dart
final hasDigit = RegExp(r'[0-9٠-٩]').hasMatch(text);

if (!hasDigit) {
  // Conversational coach path only — one call, one response
  final response = await geminiService.sendMessage(text, history: filtered);
  chatNotifier.addBotMessage(response.text);
} else {
  // Router path — classifyTransaction returns kind + reply together
  final result = await geminiService.classifyTransaction(text);
  switch (result.kind) {
    case 'transaction': autoSave(...);
    case 'compound': showCompoundSplit(...);
    case 'clarify': askQuestion(...);
    case 'chat': fallThroughToCoach(...);
  }
}
```

This eliminates the incoherent dual-bubble bug where a conversational reply and a hardcoded confirm widget appeared in the same message.

## Pattern 5: Bounded Reply Pattern (BRP) for LLM-Authored Text

**Rule:** Any bot-facing text authored by an LLM must:
1. Be a single named JSON field (e.g. `"reply"`), never a whole free-form message
2. Have an explicit one-line purpose in its prompt
3. Be bounded by tone/length/don't-list constraints
4. Have 2-3 concrete few-shot examples written directly into the prompt
5. Have a deterministic Dart fallback for empty/malformed output

This prevents prompt drift — instructions added ad hoc under time pressure that cause new regressions.

## Pattern 6: Router Kind Taxonomy (4-Way Classification Dispatch)

**Context:** When the router (`classifyTransaction`) returns a single JSON with a `kind` field, the caller must branch cleanly on all 4 possible values. Each branch has different save behavior, widget requirements, and history-reentry rules.

**The 4 kinds and their dispatch:**

| `kind` | Meaning | Save | Widget | History |
|--------|---------|------|--------|---------|
| `transaction` | Single clear expense | Auto-save immediately | `↩️ تراجع` undo button only | Stay excluded |
| `compound` | Multi-item split | Wait for confirm tap | `compound_split_card` with ❌/✅ | Stay excluded |
| `clarify` | Ambiguous, need info | Nothing saved | None (text only) | Re-enter history |
| `chat` / null | Not a transaction | Nothing saved | None | Re-enter history → fall through to coach prompt |

**Critical detail:** `clarify` and `chat` kinds must remove the message from the history filter (`_storedClassifications.remove(userMsgId)`) so they re-enter future conversation context. `transaction` and `compound` must keep the placeholder so they stay excluded.

**Pitfall:** Forgetting the re-entry rule means a `clarify` question gets excluded from Gemini's view of the conversation, causing Gemini to lose context of what it just asked about.

## Pattern 7: Auto-Save with Undo Safety Net

**Context:** When the user's message is unambiguously a single transaction, saving immediately (no confirm tap) is better UX — but requires a quick undo mechanism as the safety net.

**Implementation:**
```dart
// Immediate auto-save — no confirm tap
final saved = await txService.saveTransaction(amount: ..., category: ...);

// Undo button is the safety net — soft-delete only
chatNotifier.addBotMessage(
  replyText,
  widget: {
    'widget': 'action_buttons',
    'buttons': [{'label': '↩️ تراجع', 'value': 'undo_transaction'}],
    'tx_id': saved['id'],
    'tx_type': 'simple',
  },
);
```

**Why this beats confirm-tap:**
- The old "🔄 تعديل" button never did real inline editing — it just prompted a re-type
- Undo-then-retype is strictly cleaner than edit-then-retype
- Zero-tap reads as stronger AI confidence in a live demo
- The app's tagline is "بدون تعب" (effortless) — a mandatory confirm contradicts that

**Pitfall:** Never auto-save compound splits (multi-item messages). Those must keep the explicit ❌ إلغاء / ✅ تأكيد step because the user can genuinely adjust amounts in the split card before confirming.

## Pattern 8: Full-File Rewrite Callback Verification

**Context:** When rewriting an entire widget file (using `write_file` instead of targeted `patch`), callbacks wired in the `build()` method are easy to accidentally replace with empty lambdas. The camera button in `_InputBar` was replaced with `onCamera: () { // NOT IMPLEMENTED }` during a chat_screen.dart rewrite — the original `onCamera: _pickReceiptImage` was lost.

**Prevention checklist after any full-file Flutter rewrite:**
1. Search for `NOT IMPLEMENTED` or empty `() {}` lambdas in widget constructors
2. Verify every `on*` callback in the `build()` method matches the original
3. Specifically check: `onSend`, `onMic`, `onCamera`, `onTap`, `onChanged`, `onSubmitted`
4. Run `git diff --stat` to confirm only intended sections changed
5. Deploy to device and physically tap every interactive element

**This is not a prompt/interaction bug — it's a code-rewrite regression.** The analyzer won't catch it (empty lambdas are valid Dart). Only live device testing catches it.

## Pattern 9: Pre-Filter Heuristic — Local Regex Before LLM Call

**Context:** When adding a new conversational feature that must not interfere with an existing stabilized router, a cheap local keyword heuristic gate prevents unnecessary LLM round-trips. On match, a dedicated isolated call runs; on no-match (or failure), the message falls through to the unmodified existing router/coach path.

**Why not extend the existing router's `kind` enum:** The router's prompt was stabilized over 3 MoA rounds + device verification. Touching it risks regression. A pre-filter is additive and cannot break the existing flow — worst case, the heuristic returns `kind:"none"` and the message goes through exactly as before.

**Implementation:**
```dart
// Top-level constants — cheap, deterministic, zero API cost
final RegExp _commitmentKeywords = RegExp('قسط|التزام|تمارا|إيجار|قرض...');
final RegExp _goalKeywords = RegExp('هدف|ادخار|أوفر|صندوق الطوارئ...');

bool _looksLikeSetupIntent(String text) =>
    _commitmentKeywords.hasMatch(text) || _goalKeywords.hasMatch(text);

// In _sendMessage, BEFORE the existing router:
if (_looksLikeSetupIntent(text)) {
  final result = await geminiService.classifySetupIntent(text);
  if (result.kind != 'none') {
    await _handleSetupIntent(result.kind, result.data, chatNotifier);
    return; // stays excluded from coach history
  }
  // "none" → fall through to existing router, unmodified
}
```

**Safety properties:**
- False positives cost one extra "none" LLM call and fall through harmlessly
- False negatives mean the message behaves exactly as before the feature existed
- The feature can never be the reason an ordinary message fails — any exception in `classifySetupIntent` resolves to `{"kind":"none"}`
- The new prompt is completely isolated from the existing router/coach prompts

**When to use this pattern:** Any new conversational intent that maps to features outside the existing transaction router. The rule: never extend a stabilized prompt; add a pre-filter with its own isolated prompt instead.

## Pattern 10: Widget Payload Forwarding — Spread Instead of Whitelist

**Problem:** `_ActionButtonsWidget` and `_QuickInputFormWidgetState` used manual per-field whitelists to forward widget JSON keys into the emitted action payload:

```dart
// ❌ WHITELIST — every new field is a future bug
onPressed: () => onAction?.call({
  'action': 'button_tap',
  'widget': 'action_buttons',
  'value': value,
  'label': btn['label'],
  if (json.containsKey('tx_id')) 'tx_id': json['tx_id'],
  if (json.containsKey('tx_type')) 'tx_type': json['tx_type'],
  if (json.containsKey('commitment_id')) 'commitment_id': json['commitment_id'],
  if (json.containsKey('goal_id')) 'goal_id': json['goal_id'],
}),
```

Every new call site that added a new forwarded key (e.g. `purchase_item`/`purchase_amount` for the purchase-confirmation flow) broke silently because the whitelist wasn't updated. This bug class recurred 3 times: `commitment_id`/`goal_id` (commit `6110bef`), `purchase_item`/`purchase_amount` (commit `9497c82`), and `_form_kind`/`commitment_id`/`goal_id` in `quick_input_form` (this session).

**Fix:** Use Dart's spread operator (`...json`) to forward ALL widget JSON keys, then override the rendering-specific keys:

```dart
// ✅ SPREAD — every future field propagates automatically
onPressed: answered
    ? null
    : () => onAction?.call({
        ...json,           // forward everything
        'action': 'button_tap',  // override rendering-specific keys
        'widget': 'action_buttons',
        'value': value,
        'label': btn['label'],
      }),
```

**Why this works:** Later keys in a Dart map literal win — `action`/`widget`/`value`/`label` are always correct regardless of what's in `json`. All other keys (`tx_id`, `commitment_id`, `goal_id`, `purchase_item`, `purchase_amount`, any future field) propagate automatically.

**Rule:** Every widget that forwards JSON data to an action handler MUST use the spread pattern. Never add a new `if (json.containsKey(...))` entry — that's adding to the whitelist, which is the broken pattern.

## Pattern 11: Widget State Machine — Answered-Once for ALL Interactive Widgets

**Problem:** `_handleWidgetAction` called `markWidgetAnswered` for `action_buttons` and `compound_split_card`, but NOT for `quick_input_form`. The form's submit button stayed tappable indefinitely — 3 taps created 3 commitment/goal rows. The widget itself never checked `_answered` either.

**Fix:** Every interactive widget type needs three coordinated changes to make the "answered once" pattern complete:

1. **Handler marks on submit:** `_handleWidgetAction` must call `markWidgetAnswered(msgId, value)` for EVERY widget type that produces a submit action — not just `action_buttons`:

```dart
case 'quick_input_form':
  final msgId = action['message_id'] as String?;
  if (values == null) break;
  if (msgId != null) chatNotifier.markWidgetAnswered(msgId, 'form_submitted');
  // ... dispatch on formKind
```

2. **Widget reads `_answered`:** The widget's `build()` checks `widget.json['_answered']` and applies:
   - `Opacity(opacity: answered ? 0.55 : 1.0)` around the entire widget
   - `TextField(enabled: !answered)` on every input
   - `onPressed: answered ? null : ...` on the submit button

3. **Spread pattern for payload:** Combine with Pattern 10 — use `...widget.json` spread so `_answered` and any embedded IDs propagate automatically.

**The three-widget invariant:** `action_buttons` ✅ | `compound_split_card` ✅ | `quick_input_form` ✅ — all three must follow this pattern. Add to this checklist when introducing a new interactive widget type.

## Pattern 12: Duplicate Text Detection — Widget Question vs Bubble Text

**Problem:** 8 call sites passed the SAME string as both `addBotMessage`'s `text` parameter (rendered as a bubble) AND the attached widget's `question` field (rendered as a heading inside the button card). The result: the exact same sentence appears twice, stacked, with the button only under the second copy.

**Root cause:** The codebase had two correct examples (`_runPurchaseDecision`'s `yes`/`wait` cases already passed `''` as bubble text and let the widget's `question` carry the sentence), but this pattern wasn't applied consistently.

**Fix:** When a widget carries its own text via a `question` or `title` field, the `addBotMessage` text argument MUST be `''`:

```dart
// ❌ DUPLICATE — same string in both places
chatNotifier.addBotMessage(
  'تم تسجيل 50 ريال ✅',
  widget: {'widget': 'action_buttons', 'question': 'تم تسجيل 50 ريال ✅', ...},
);

// ✅ SINGLE — widget carries the text, bubble text is empty
chatNotifier.addBotMessage(
  '',  // empty — the widget's 'question' field carries the sentence
  widget: {'widget': 'action_buttons', 'question': 'تم تسجيل 50 ريال ✅', ...},
);
```

**When this does NOT apply:** `_submitCommitmentAdd`/`_submitGoalAdd` have two GENUINELY DIFFERENT sentences (save confirmation + follow-up question) — these are correct to leave as-is. Only fix sites where both strings are identical.

**Pre-commit check:** After adding any new `addBotMessage` call with an `action_buttons` widget, verify that `text != question`. If they're identical, change `text` to `''`.

