# GoRouter — Stale Page Inside ShellRoute (const NoTransitionPage)

## Discovery Session
**Date:** 2026-07-16
**Project:** Hermex Android (epic/rc4-polish)
**Bug:** Chat screen stuck showing first session's data when switching between sessions

## Reproduction

1. Open app → navigate to `/chat?session=A` → ChatScreen loads session A (correct)
2. Navigate back to sessions list → tap session B → navigate to `/chat?session=B`
3. **BUG:** ChatScreen shows session A's title and messages
4. **Confirmed:** Server returns correct data for session B via `curl` — bug is purely Flutter-side

## Root Cause

`GoRoute.pageBuilder` inside a `ShellRoute` returned `const NoTransitionPage`:

```dart
GoRoute(
  path: RoutePaths.chat,
  pageBuilder: (context, state) => const NoTransitionPage(
    child: ChatScreen(),
  ),
),
```

**Mechanics:**
1. `/chat?session=A` → `pageBuilder` returns `const NoTransitionPage(ChatScreen())` — the const object
2. `/chat?session=B` → `pageBuilder` returns the **same** const object (same memory address)
3. GoRouter compares old Page == new Page → identical → skips rebuild
4. Flutter widget tree persists → `didChangeDependencies()` never fires
5. `ChatScreen._initChatIfNeeded()` (lines 39-76) which watches route params → never called

## Fix

```dart
GoRoute(
  path: RoutePaths.chat,
  pageBuilder: (context, state) => NoTransitionPage(
    key: ValueKey(state.uri.toString()),
    child: const ChatScreen(),
  ),
),
```

**Changes:**
- Remove `const` from `NoTransitionPage` — each call now returns a new object
- Add `key: ValueKey(state.uri.toString())` — different session URIs → different keys → Flutter treats as different widget → full rebuild

**What stays the same:**
- `ChatScreen` remains `const` — once created per key, it's efficient
- `_lastSessionId` guard inside `chat_screen.dart` — becomes harmless redundancy

## Verification

| Gate | Result |
|------|--------|
| `flutter analyze` | 0 errors |
| `flutter test` (526 tests) | All passed |
| Device: Tecno LJ7 (HiOS) | Manual smoke test required |

### Device Smoke Test Steps (mandatory — this bug only manifests at runtime)
1. Open session A → title + messages match A
2. Go back, open session B → title + messages update to B (NOT repeat A)
3. Repeat with session C to confirm it's consistent
4. Tab switch (Chat ↔ Sessions) without opening a new session → scroll/text state preserved

## Why Widget Tests Don't Catch This

Widget tests use `pumpWidget()` which directly builds widget trees — GoRouter navigation machinery is bypassed. Integration tests with `flutter_driver` or a full `WidgetTester.pumpAndSettle()` with GoRouter navigation would catch it, but unit-level widget tests do not.

## Detection Rule

> Does a `ShellRoute` pageBuilder use `const NoTransitionPage`? If so, does the target screen read query/path parameters in `didChangeDependencies()`? Add `key: ValueKey(state.uri.toString())`.

## Cross-Reference

- `LL-029` (Riverpod state mutation order) — similar class of "same object identity prevents expected updates"
- `flutter-lessons-patterns` Pattern LL-042 (`include_disabled`) — another runtime-only issue caught on device
