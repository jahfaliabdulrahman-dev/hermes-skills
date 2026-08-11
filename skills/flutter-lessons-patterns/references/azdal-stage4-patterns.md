# Azdal Stage 4 Patterns — July 2026 Session

## Pattern: Arabic-Indic Numeral Normalization Trap

**Bug class:** Form field `double.tryParse()` silently returns `null` for Arabic-Indic digits (٠-٩).

**Root cause:** `_arabicToWestern` helper was correctly removed during the router redesign (classifyTransaction returns JSON numbers, no client-side parsing needed). But the removal left EVERY form-submitted field (`values['key'] as String?`) with a bare `double.tryParse()` and no normalization. Arabic keyboard emits ٠١٢٣٤٥٦٧٨٩ by default on many devices.

**Fix:** Always wrap form-field string values in `_arabicToWestern()` before `double.tryParse()`:
```dart
double.tryParse(_arabicToWestern(values['amount'] as String? ?? ''))
```

**Rule:** Before removing a normalization helper, grep every call site that parses user input. If ANY of them would break without normalization, either keep the helper or add it back with proper scope comments.

**Affected sites in Azdal (all form-submitted fields):**
- Cold Start: income, commitments, weekly-spend
- Commitment add: monthly_amount, total_amount
- Commitment adjust: remaining
- Goal add: target_amount, monthly_contribution
- Goal adjust: current_amount
- Buy verdict clarification: income
- OCR failure manual entry: amount

## Pattern: Action Widget Payload Forwarding — Spread over Whitelist

**Bug class:** `_ActionButtonsWidget` manually whitelists forwarded JSON fields (`tx_id`, `tx_type`, `commitment_id`, `goal_id`, `purchase_item`, `purchase_amount`...). Every new field added to a widget requires a matching whitelist entry — missing one causes silent null on the handler side.

**Fix (general):** Use `...json` spread instead of per-field `if (json.containsKey(...))`:
```dart
// BEFORE — fragile per-field whitelist:
onPressed: () => onAction?.call({
  'action': 'button_tap',
  'widget': 'action_buttons',
  'value': value,
  'label': btn['label'],
  if (json.containsKey('tx_id')) 'tx_id': json['tx_id'],
  if (json.containsKey('tx_type')) 'tx_type': json['tx_type'],
  // ... every new field needs an entry here
}),

// AFTER — spread, later keys win:
onPressed: () => onAction?.call({
  ...json,
  'action': 'button_tap',
  'widget': 'action_buttons',
  'value': value,
  'label': btn['label'],
}),
```

**Applied to:** `_ActionButtonsWidget` (commit 9497c82), `_QuickInputFormWidgetState` (commit 428006f).

**Same pattern works for quick_input_form's submit button payload too.**

## Pattern: Duplicate Bubble Text — `addBotMessage` + `question`

**Bug:** Passing the same string as both `addBotMessage`'s `text` argument AND the widget's `question` field renders the sentence twice in one bubble — as bubble content text, then again as the widget heading.

**Fix:** Change the bubble text to `''` and let the widget's `question` carry the text alone:
```dart
// BEFORE — duplicate:
chatNotifier.addBotMessage(replyText, widget: {
  'widget': 'action_buttons', 'question': replyText, ...
});

// AFTER — single:
chatNotifier.addBotMessage('', widget: {
  'widget': 'action_buttons', 'question': replyText, ...
});
```

**Pattern already used correctly in the codebase:** `_runPurchaseDecision`'s `yes`/`wait` cases pass `''` as bubble text and let the widget carry the sentence.

**Call sites fixed (8 total):** `_saveAndAnnounceTransaction`, `_confirmPurchase`, `_handleCompoundSplit`, `_handleOcrFailureSubmit`, `_showCommitmentCompletePrompt`, `_showCommitmentEditPicker`, `_showGoalAchievedPrompt`, `_showGoalEditPicker`.

**Do NOT touch:** `_submitCommitmentAdd`/`_submitGoalAdd` — their bubble text (`'تم حفظ التزام...'`) and their `question` (`'في التزامات ثانية؟'`) are genuinely different sentences.

## Pattern: Interactive Widget Lifecycle — markWidgetAnswered + _answered

**Every interactive widget type needs TWO things:**
1. A `chatNotifier.markWidgetAnswered(msgId, value)` call at the TOP of its handler (before any async work)
2. An `_answered` check in the widget renderer (Opacity dim, buttons disabled, fields readonly)

**Missing either = unlimited duplicate submissions.**

**Widgets that already have this:** `action_buttons`, `compound_split_card`.

**Widget added in this session:** `quick_input_form` — was missing both. Fixed:
- Handler: `if (msgId != null) chatNotifier.markWidgetAnswered(msgId, 'form_submitted');`
- Renderer: `Opacity(opacity: answered ? 0.55 : 1.0)`, `TextField(enabled: !answered)`, `onPressed: answered ? null : ...`

**Rule:** When adding a new interactive widget type, check both sides immediately — don't wait for device testing to find the missing guard.

## Pattern: Full-File Rewrite Callback Loss

**Bug:** When rewriting a full file with `write_file`, callback wiring in the `build()` method was lost: `onCamera: _pickReceiptImage` became an empty lambda `onCamera: () { // NOT IMPLEMENTED }`.

**Fix:** After any `write_file` for a UI file, verify every `on*` callback in the build method is wired to a real handler. Camera, mic, send, form submit — check each one.
