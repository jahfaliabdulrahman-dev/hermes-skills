# Widget "Answered Once" Pattern

> **Session:** 2026-07-12  
> **Pattern type:** Flutter/Dart — Riverpod StateNotifier + widget rendering

## Problem

Actionable widgets stay fully interactive forever after rendering — even after their action has been handled. Tapping confirm twice produces duplicate saves.

## Solution

### 1. Data Layer — ChatProvider.markWidgetAnswered

```dart
void markWidgetAnswered(String messageId, String selectedValue) {
  final message = state.messages[...];
  final updatedWidget = {
    ...?message.widget,
    '_answered': true,
    '_selectedValue': selectedValue,
  };
  // Replace in-place via copyWith
}
```

Merges into existing widget map — no new ChatMessage fields needed.

### 2. Injection — MessageBubble wraps onAction

```dart
onAction: (action) => onWidgetAction!({
  ...action,
  'message_id': message.id,
})
```

Single change, covers ALL widget types. No widget code modified.

### 3. Consumption — Handler calls markWidgetAnswered FIRST

```dart
chatNotifier.markWidgetAnswered(msgId, value);  // synchronous
await someAsyncWork();  // widget already shows answered state
```

### 4. Rendering — Widgets read _answered

Read `json['_answered']` + `json['_selectedValue']`:
- All buttons: `onPressed: null`
- Container: `Opacity(0.55)`
- Selected button: distinct highlight

## Edge Cases

- Double-tap ms apart: `_isConfirming` guard
- Tap minutes later: `_answered` persists → `onPressed: null`
- Scroll away/back: state in ChatMessage → Riverpod rebuild preserves
- Network failure: widget stays answered, retry via ErrorBubble
