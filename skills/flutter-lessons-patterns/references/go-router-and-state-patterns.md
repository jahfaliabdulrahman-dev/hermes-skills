# GoRouter & Riverpod State Patterns — Hermex Android

> Added: 2026-07-16. Source: RC6 polish session — two runtime-only bugs caught on real device.

## Pattern: GoRouter NoTransitionPage + ShellRoute Stale Widget

### Problem
When using `const NoTransitionPage` inside a `ShellRoute`, navigating to different query params (`/chat?session=A` → `/chat?session=B`) returns the IDENTICAL Page object because of `const`. Flutter's widget tree doesn't detect a change, so `didChangeDependencies()` never fires. The chat screen shows stale data from the first session.

### Symptom
- Opening session B shows session A's messages and title
- Only happens after the first navigation — first session loads correctly
- Data is fine (verified via curl directly to server)
- `didChangeDependencies()` prints show it fires only once

### Fix
Remove `const` from the Page and add a `ValueKey` based on the URI:

```dart
// ❌ BROKEN: same Page object for all query params
GoRoute(
  path: RoutePaths.chat,
  pageBuilder: (context, state) => const NoTransitionPage(
    child: ChatScreen(),
  ),
),

// ✅ FIXED: unique key per URI forces widget rebuild
GoRoute(
  path: RoutePaths.chat,
  pageBuilder: (context, state) => NoTransitionPage(
    key: ValueKey(state.uri.toString()),
    child: const ChatScreen(),
  ),
),
```

### Why This Works
- `state.uri.toString()` produces `/chat?session=X` for each session
- `ValueKey(...)` makes Flutter see a different widget for different URIs
- Flutter unmounts the old widget and creates a new one → `initState()` and `didChangeDependencies()` fire
- The child `ChatScreen` stays `const` — only the wrapper Page is dynamic

### Verification
- This bug ONLY manifests at runtime on a real device — `flutter analyze` and `flutter test` won't catch it
- Manual test: open 3 different sessions in sequence, verify each shows correct title + messages
- Tab switching (Chat → Sessions → Chat) without opening a new session should preserve scroll position

### Related Pattern
The `_lastSessionId` guard in `chat_screen.dart:39-76` is now a harmless safety net, not the primary mechanism. With the `ValueKey` fix, the screen is rebuilt for each session change, so `_lastSessionId` becomes a redundant backup.

---

## Pattern: Riverpod copyWith — null vs clear Flags

### Problem
A `copyWith` method that uses `field ?? this.field` as a fallback cannot distinguish "set to null" from "not provided":

```dart
ChatState copyWith({
  String? sessionTitle,
  bool clearSessionTitle = false,
}) =>
    ChatState(
      sessionTitle: clearSessionTitle
          ? null
          : (sessionTitle ?? this.sessionTitle), // ← BUG: null falls back to old value
    );
```

When the caller passes `sessionTitle: null` (e.g., an untitled session from the API), the `??` operator falls back to `this.sessionTitle` — the PREVIOUS session's title.

### Symptom
- Opening "Untitled" session shows previous session's title in AppBar
- Messages load correctly (they come from a separate API call)
- Only the title/model-name in state is stale

### Fix
Always set the clear flag when the value is null or empty:

```dart
// ❌ BROKEN: null falls through to old value
state = state.copyWith(
  sessionTitle: title,          // null from API
  sessionModelName: modelName,  // null from API
);

// ✅ FIXED: clear the field when value is null/empty
state = state.copyWith(
  sessionTitle: title,
  clearSessionTitle: title == null || title.isEmpty,
  sessionModelName: modelName,
  clearSessionModelName: modelName == null || modelName.isEmpty,
);
```

### Rule
**When a `copyWith` method uses `clearX` flags with `??` fallback semantics, EVERY call site that might pass a null/empty value MUST also set `clearX: true`.** Never rely on `null` to clear — it won't.

### Detection Checklist
When reviewing any `copyWith` call that passes nullable values:
1. Check if the target `copyWith` uses `clearX ? null : (value ?? this.value)` pattern
2. If yes, verify that null/empty inputs are paired with `clearX: true`
3. If the caller receives data from an external source (API, DB, user input), assume null is possible

### Example: Correct clearSession method
```dart
void clearSession() {
  state = state.copyWith(
    clearSession: true,       // explicitly clear
    clearSessionTitle: true,  // explicitly clear
    clearSessionModelName: true, // explicitly clear
  );
}
```
This correctly uses `clearX: true` without passing any value — the clean pattern.
