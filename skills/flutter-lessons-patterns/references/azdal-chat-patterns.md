# Azdal Chat Integration Patterns — Supabase + Flutter (2026-07-12)

> **Source:** Azdal DEC-020 implementation session — cancel + undo features
> **Context:** TransactionService + ChatProvider + widget_catalog.dart
> **See also:** `flutter-lessons-patterns/SKILL.md` Patterns 33–36

---

## 1. Supabase Soft-Delete with `.or()` for Compound Groups

**Pattern:** When the first inserted row's id IS the group_id for its children (see `saveCompoundSplits`), soft-delete the whole group in one query using Supabase's `.or()` filter.

```dart
// Single transaction soft-delete
await _client
    .from('transactions')
    .update({'is_deleted': true, 'deleted_at': DateTime.now().toIso8601String()})
    .eq('id', id)
    .eq('user_id', uid);

// Compound group soft-delete (parent + ALL children)
await _client
    .from('transactions')
    .update({'is_deleted': true, 'deleted_at': DateTime.now().toIso8601String()})
    .or('id.eq.$groupId,group_id.eq.$groupId')  // ← one query covers both
    .eq('user_id', uid);
```

**Why `.or()` works:** Supabase's `.or()` accepts comma-separated filter expressions in the format `column.operator.value`. The expression `id.eq.X,group_id.eq.X` matches rows where either condition is true — the parent row (id = groupId) AND all children (group_id = groupId).

**Why NOT separate queries:** Two separate UPDATE queries for parent and children create a window where the parent is deleted but children still appear active. `.or()` is atomic for the entire group.

---

## 2. Cancel Before Confirm (No-Op Save Path)

**Pattern:** For any confirmation widget where the user might change their mind before committing, add a cancel button that does a no-op — no database write, no state rollback needed — just show an acknowledgment.

```dart
// Widget: "❌ إلغاء" button next to "✅ تأكيد"
OutlinedButton(
  onPressed: () => onAction?.call({
    'action': 'compound_split_cancel',
    'widget': 'compound_split_card',
    // No splits, no amounts — this just discards
  }),
  child: const Text('❌ إلغاء'),
)

// Handler: no Supabase, just acknowledge
if (actionType == 'compound_split_cancel') {
  chatNotifier.addBotMessage('تم الإلغاء.');
  break;
}
```

**When to use vs. undo:** Cancel is for PRE-confirm (nothing was saved yet). Undo is for POST-confirm (soft-delete what was saved). They are complementary, not alternatives. A pre-confirm cancel needs no database action at all — the data only exists in the widget's local `_splits` state.

---

## 3. action_buttons Passthrough Pattern

**Pattern:** Reuse the existing `action_buttons` widget for non-classification actions (undo, retry, share) by attaching metadata fields (`tx_id`, `tx_type`) to the widget JSON. Have the `_ActionButtonsWidget` forward those fields through `onAction` so the handler receives them.

```dart
// Widget JSON — tx_id + tx_type embedded alongside buttons
{
  'widget': 'action_buttons',
  'question': 'تم تسجيل المعاملة بنجاح ✅',
  'buttons': [
    {'label': '↩️ تراجع', 'value': 'undo_transaction', 'type': 'secondary'}
  ],
  'tx_id': txId,       // ← passthrough: transaction or group id
  'tx_type': 'simple', // ← passthrough: 'simple' or 'group'
}

// _ActionButtonsWidget forwarding
onPressed: () => onAction?.call({
  'action': 'button_tap',
  'widget': 'action_buttons',
  'value': btn['value'],
  'label': btn['label'],
  if (json.containsKey('tx_id')) 'tx_id': json['tx_id'],
  if (json.containsKey('tx_type')) 'tx_type': json['tx_type'],
})

// Handler: reads tx_id + tx_type, routes to soft-delete
} else if (value == 'undo_transaction') {
  await _undoTransaction(action, chatNotifier);
}

// _undoTransaction: dispatches based on tx_type
if (txType == 'group') {
  await txService.softDeleteTransactionGroup(txId);
} else {
  await txService.softDeleteTransaction(txId);
}
```

**Why not create a 7th widget type:** The action_buttons widget already handles button rendering, styles, and action dispatch. Adding metadata passthrough fields avoids widget catalog bloat and keeps the 6-widget limit. Any new action that fits the "question + buttons" form can reuse this.

**Detection pattern:** Before creating a new widget type for the catalog, ask: "Does this just need different metadata attached to existing action_buttons?" If yes, passthrough. Only create a new widget type when the visual structure or interaction pattern is fundamentally different.

---

## 4. Double-Tap Guards for Mutation Actions

**Pattern:** Every mutation action (confirm, undo, delete, save) needs an atomic guard flag at the handler level. The guard is set before the async call and cleared in `finally {}` so it always resets — even on exceptions.

```dart
// Guards in _ChatScreenState
bool _isConfirming = false;
bool _isUndoing = false;

// Confirm guard
if (_isConfirming) return;
_isConfirming = true;
try {
  await txService.saveTransaction(...);
} finally {
  _isConfirming = false;  // ← always resets
}

// Undo guard — separate flag, same pattern
if (_isUndoing) return;
_isUndoing = true;
try {
  await txService.softDeleteTransaction(id);
} finally {
  _isUndoing = false;
}
```

**Why separate flags:** Combining them into one `_isBusy` flag would make undo wait for confirm to finish and vice versa — they're independent operations. Separate flags allow confirm and undo to be used on different transactions simultaneously.

**Why `finally {}` not `catch {}`:** If the try block throws, the guard must still reset — otherwise the button stays locked forever. `finally {}` guarantees reset regardless of success or failure.
