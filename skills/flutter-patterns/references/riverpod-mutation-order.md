# Riverpod State Mutation Before Snapshot — Full Reference

> Source: Hermex Android LL-029 analysis — 2026-07-06

## Bug Anatomy

### The Pattern

```
state.copyWith(messages: [...state.messages, newItem])  // 1. Mutate state
final snapshot = buildSnapshot(state)                    // 2. Read derived view
api.send(snapshot + explicitAddition)                    // 3. Double-counted
```

The snapshot captured at step 2 includes `newItem` because step 1 already mutated `state.messages`. If step 3 also adds `newItem` explicitly, the API receives it twice.

### Hermex Android Case

**File:** `lib/features/chat/providers/chat_provider.dart` — `ChatNotifier.sendMessage()`

**Pre-fix order (broken):**
1. Line 254: `state = state.copyWith(messages: [...state.messages, userMessage, agentMessage])` — user message added to state
2. Line 260: `final history = _buildHistory()` — reads `state.messages` which now INCLUDES the just-added user message
3. Line 266: `_repository.streamChatCompletion(message: trimmed, history: history)` — repository adds user message AGAIN (line 122 of chat_repository.dart)
4. API receives: `[..., {role: user, content: "السلام عليكم"}, {role: user, content: "السلام عليكم"}]` — two consecutive same-role messages
5. Hermes API enforces strict user/assistant alternation → rejects with 400

**Post-fix order (correct):**
1. Line 241: `final history = _buildHistory()` — snapshot of PREVIOUS state
2. Line 258: `state = state.copyWith(messages: [...state.messages, userMessage, agentMessage])` — mutation
3. Line 266: `_repository.streamChatCompletion(message: trimmed, history: history)` — history clean, repository adds one user message
4. API receives: `[..., {role: assistant, content: "..."}, {role: user, content: "السلام عليكم"}]` — proper alternation

### Dual-Source Architecture (Why This Is Fragile)

Two layers independently add the user message to the API request:

| Layer | File | What It Adds |
|-------|------|-------------|
| Notifier | `chat_provider.dart:244-248` | `userMessage` via `state.copyWith(messages: [...])` |
| Notifier | `chat_provider.dart:484-493` | `_buildHistory()` → `state.messages` → extracted into history list |
| Repository | `chat_repository.dart:122-125` | `{'role': 'user', 'content': message}` added to `messages` body |

The notifier builds history from `state.messages`, and the repository adds the current message explicitly. If history already contains the current message (because `state` was mutated before the snapshot), the repository's explicit addition creates a duplicate.

## Edge Case Analysis

| Edge Case | Safe? | Why |
|-----------|-------|-----|
| Rapid successive sends (double-tap) | ✅ | `isStreaming` guard at line 225 blocks second call before any mutation. `isStreaming` is set `true` in same `state.copyWith()` that adds messages |
| First message in fresh session | ✅ | `_buildHistory()` returns `[]` when `state.messages` is empty. Repository adds single `{role: user}` — no duplication |
| Subsequent messages in conversation | ✅ | History captures `[u₁, a₁, u₂, a₂, ...]`. Repository appends `uₙ₊₁` → proper alternation |
| Tool messages in history | ✅ | `_buildHistory()` filters `role != 'tool' && role != 'system'` |
| Partially streamed messages | ✅ | `_buildHistory()` filters `!m.isStreaming` |
| Non-streaming fallback path | ⚠️ Separate issue | `sendChatCompletion()` sends NO history at all — just the current message. Not a duplicate bug, but conversation context is silently lost on SSE failure fallback |

## Systemic Prevention

### 1. Unit Test (Highest ROI)

Add to provider tests — verify API request body integrity:

```dart
test('sendMessage API request body has exactly one user message per send', () {
  // Verify: messages list has role:user count == 1 more than history had
  // Assert: no two consecutive messages have same role
});
```

Add Gherkin scenario: **AC-F002-14: "API request alternation integrity"**

### 2. PR Checklist Item

> "Does any `state.copyWith()` precede a `_buildHistory()`-style snapshot call in the same method? If so, move the snapshot BEFORE the mutation."

### 3. Architectural Safeguard

Add assertion in `_buildHistory()`:
```dart
List<Map<String, dynamic>> _buildHistory() {
  assert(
    !state.isStreaming,
    '_buildHistory() called while streaming — history may include partial message',
  );
  // ... existing logic
}
```

Add defensive dedup in repository:
```dart
// If two consecutive messages have same role, log warning, skip duplicate
if (messages.isNotEmpty && messages.last['role'] == role) {
  debugPrint('WARNING: Skipping duplicate role=$role message');
  return;
}
```

### 4. What Does NOT Work

- **Android preflight gates** — this is a pure Dart/Riverpod bug, no Android config involved
- **Existing Dart lint rules** — no lint catches "mutation order before snapshot," it's semantic
- **Regex-based scanning** — fragile, false positives likely. Better as code review convention.

## Bug Class Taxonomy

| LL | Class | Layer |
|----|-------|-------|
| LL-024 | Namespace mismatch | Android build config |
| LL-025 | Isar + ProGuard/R8 | Android build config |
| LL-027 | Cleartext HTTP blocked | Android network policy |
| **LL-029** | **Mutate Before Snapshot** | **Flutter/Riverpod state** |

LL-029 is a NEW class — the first state-management ordering bug documented for this project. It's not an Android gap; it's a Dart/Riverpod TOCTOU anti-pattern.

### Related Patterns (Same Family)

- **LL-004:** `isBusy` guard — same "prevent duplicates at provider level" philosophy
- **LL-007:** Provider invalidation ordering — same "mutation order matters in Riverpod" class
- **LL-021:** `write_file` overwrite — same "capture snapshot before mutation" pattern, different layer (file I/O instead of state management)
