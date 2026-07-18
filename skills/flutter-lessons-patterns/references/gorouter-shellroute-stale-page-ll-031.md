# GoRouter ShellRoute — NoTransitionPage Session Switching (LL-031)

## Reproduction (Hermex Android, 2026-07-16)

### Setup
- `ShellRoute` with bottom navigation (Chat | Sessions | Tasks | Settings)
- Chat route: `/chat` with optional query param `?session=X`
- `ChatScreen` relies on `didChangeDependencies()` to detect session switches

### Bug
1. Open session A from session list → title and messages load correctly for A
2. Go back to sessions list, open session B (different ID, different message count)
3. **Actual:** AppBar shows session A's title, messages show session A's content or stale error
4. **Expected:** AppBar and messages update to session B's data

### Root Cause Trace
```
app_router.dart:52 → const NoTransitionPage(child: ChatScreen())
                         ↓
              Same const Page object for ALL /chat?session=X URLs
                         ↓
              GoRouter sees no widget change → reuses existing widget tree
                         ↓
              didChangeDependencies() never fires on ChatScreen
                         ↓
              _initChatIfNeeded() never runs → loadHistory() never called
                         ↓
              User sees stale data from first session
```

### Fix Applied
```dart
// lib/core/router/app_router.dart:50-55
GoRoute(
  path: RoutePaths.chat,
  pageBuilder: (context, state) => NoTransitionPage(
    key: ValueKey(state.uri.toString()),  // ← forces new widget per unique URI
    child: const ChatScreen(),
  ),
),
```

### Device Verification (Tecno LJ7, HiOS)
- Session 263 (17 messages): opened → correct title + messages
- Session 2 (3 messages): opened after 263 → correct title + messages (NOT 263's data)
- Session 17 (untitled): opened after 2 → correct title + messages
- Tab cycling (Chat→Sessions→Chat) without opening session: scroll state preserved ✓

### Key Insight
The `const` on `NoTransitionPage` is the smoking gun. In Dart/Flutter, `const` constructors produce canonicalized identical objects. GoRouter's page caching sees the identical object and assumes no rebuild is needed. Removing `const` and adding a unique `ValueKey` per URI forces Flutter to treat each session as a distinct page.

### Related Pattern
The `_lastSessionId` guard in `chat_screen.dart:39-76` was designed as the primary session-switch detection mechanism. With the key fix, it becomes a harmless safety net since the widget is torn down and rebuilt per session anyway.
