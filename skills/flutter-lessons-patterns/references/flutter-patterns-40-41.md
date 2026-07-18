# Pattern 40: GoRouter ShellRoute PageKey for Session Switching

> Added: 2026-07-16. Source: hermex_android chat screen stale session bug.

**Problem:** In a `ShellRoute` with a bottom navigation bar, switching between `/chat?session=A` and `/chat?session=B` showed stale data from session A. The app bar title and messages never updated after the first session load.

**Root cause:** The `GoRoute` used `const NoTransitionPage(child: ChatScreen())`. Because the `Page` object was `const`, every navigation to `/chat` — regardless of query parameters — returned the identical widget instance. GoRouter/Flutter saw "same Page object = nothing changed" and never rebuilt the widget tree. `didChangeDependencies()` in `ChatScreen` (which was designed to detect session switches via route param changes) never fired after the initial load.

**Fix:** Remove `const` from `NoTransitionPage` and add a `ValueKey` based on the full URI:

```dart
// ❌ BROKEN — const Page, same instance regardless of params
GoRoute(
  path: RoutePaths.chat,
  pageBuilder: (context, state) => const NoTransitionPage(
    child: ChatScreen(),
  ),
),

// ✅ FIXED — unique key per URI, Flutter rebuilds on param change
GoRoute(
  path: RoutePaths.chat,
  pageBuilder: (context, state) => NoTransitionPage(
    key: ValueKey(state.uri.toString()),
    child: const ChatScreen(),
  ),
),
```

**Why this works:** `state.uri.toString()` includes query params (`/chat?session=263` vs `/chat?session=2`). Different URIs → different keys → Flutter destroys the old `ChatScreen` widget and creates a new one → `initState()` and `didChangeDependencies()` fire fresh.

**ShellRoute state preservation:** The `key` only triggers when the URI actually changes. Navigating between tabs (Chat → Sessions → Chat without opening a new session) preserves the scroll position and text input state — the URI hasn't changed, so the key is the same, so Flutter reuses the existing widget.

**Verification:** This bug only manifests at runtime. `flutter test` won't catch it because tests typically navigate directly, not via ShellRoute. Always verify with `adb` on a real device: open session A → go back → open session B → verify title and messages update.

---

# Pattern 41: Riverpod copyWith Null-Fallback Trap

> Added: 2026-07-16. Source: hermex_android stale AppBar title on untitled sessions.

**Problem:** Opening an untitled session kept showing the previous session's title ("Session 263") in the AppBar, even though the messages loaded correctly for the new session.

**Root cause:** `ChatState.copyWith()` uses the standard Riverpod pattern where `null` means "don't change this field":

```dart
sessionTitle: clearSessionTitle
    ? null
    : (sessionTitle ?? this.sessionTitle),
```

When `clearSessionTitle` is `false` (the default) and `sessionTitle` is `null`, the expression falls through to `this.sessionTitle` — preserving the OLD value. Untitled sessions return `title: null` from the API. So `loadHistory(sessionId, title: null)` silently kept the previous session's title.

**Fix:** Pass `clearSessionTitle: true` when the incoming value is null or empty:

```dart
// ❌ BROKEN — null silently falls back to old value
state = state.copyWith(
  sessionTitle: title,        // null → keeps old title!
  sessionModelName: modelName, // null → keeps old model!
);

// ✅ FIXED — explicit clear when value is null/empty
state = state.copyWith(
  sessionTitle: title,
  clearSessionTitle: title == null || title.isEmpty,
  sessionModelName: modelName,
  clearSessionModelName: modelName == null || modelName.isEmpty,
);
```

**The pattern:** Any `copyWith` that has `clear*` flags follows this contract:
- `field: null` + `clearField: false` → **keep old value** (no-op)
- `field: null` + `clearField: true` → **clear to null** (explicit reset)
- `field: value` + `clearField: false` → **set to new value** (normal update)

**The trap:** When loading data from an API/external source that may return null, the default `clearField: false` combined with `null` silently preserves stale data. Always pair null values with `clearField: true` when the intent is to reset.

**Prevention:** Add a unit test that verifies:
1. Set state with `sessionTitle: 'Session A'`
2. Call `loadHistory` with `title: null`
3. Assert `state.sessionTitle == null` (not 'Session A')

This class of bug only manifests when switching between sessions where one has a title and the other doesn't — a test with two sequential `loadHistory` calls would catch it.
