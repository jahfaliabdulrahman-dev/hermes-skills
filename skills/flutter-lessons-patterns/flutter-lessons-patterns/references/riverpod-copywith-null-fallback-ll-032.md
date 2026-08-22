# Riverpod copyWith — Null Fallback Stale State Bug (LL-032)

## Reproduction (Hermex Android, 2026-07-16)

### Setup
- `ChatNotifier` (Riverpod StateNotifier) manages chat UI state
- `ChatState.copyWith()` has pattern: `sessionTitle: clearSessionTitle ? null : (sessionTitle ?? this.sessionTitle)`
- `loadHistory()` called when user taps a session from the list

### Bug
1. Open session titled "Test Session" → AppBar shows "Test Session" ✓
2. Go back, open "Untitled" session (API returns `title: null`) → AppBar STILL shows "Test Session" ✗
3. Messages load correctly for the untitled session (data is fine — only UI is stale)

### Root Cause Trace
```
chat_provider.dart:497 → sessionTitle: title   (title = null for untitled sessions)
                         ↓
              copyWith(clearSessionTitle: false, sessionTitle: null)
                         ↓
              clearSessionTitle == false → don't set null
              sessionTitle ?? this.sessionTitle → null ?? "Test Session" → "Test Session"
                         ↓
              Old title persists — AppBar never updates
```

### Fix Applied
```dart
// lib/features/chat/providers/chat_provider.dart:493-500
state = state.copyWith(
  messages: [],
  isLoadingHistory: true,
  sessionId: sessionId,
  sessionTitle: title,
  clearSessionTitle: title == null || title.isEmpty,      // ← ADDED
  sessionModelName: modelName,
  clearSessionModelName: modelName == null || modelName.isEmpty,  // ← ADDED
  clearError: true,
);
```

### Why Both title AND modelName
The `copyWith()` pattern applies to ALL nullable fields with a `clearX` flag. `sessionModelName` has the identical structure:
```dart
sessionModelName: clearSessionModelName
    ? null
    : (sessionModelName ?? this.sessionModelName),
```
Even if the model name wasn't visibly bugged in this session, the same class of bug exists — fix both to prevent a future regression.

### Prevention Checklist
Every `copyWith()` call site that passes a nullable value MUST answer: "Does null mean 'keep the old value' or 'clear it'?"
- If "clear it" → MUST set `clearX: true`
- This should be a code review gate, not discovered at runtime

### Detection Difficulty
- Unit tests: EASY to miss — mock APIs return titles, null-title sessions are edge cases
- Manual testing: MUST explicitly test untitled/empty sessions
- The bug is silent: no crash, no error, just subtly wrong UI
