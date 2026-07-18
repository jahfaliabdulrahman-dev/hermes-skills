# LLM Prompt Isolation — Battle Story (Azdal, July 2026)

## The Bug Class

When a Flutter app uses the same LLM (Gemini Flash) for multiple purposes — chat responses AND transaction classification — a single shared system prompt causes cascading failures across all call paths.

## Four Failed Attempts

| # | Approach | Why It Failed |
|---|----------|--------------|
| 1 | Remove `action_buttons` from system prompt; "express in plain text only" | Killed classification call — `_tryAutoClassify` returned null because prompt blocked ALL JSON |
| 2 | Narrow to "don't send action_buttons"; keep compound_split_card instruction | Main call still emitted compound_split_card with history-contaminated items |
| 3 | Remove compound_split_card instruction; add blanket prohibition | Prohibition killed `_tryAutoClassify` — compound splits never appeared even for genuine multi-item messages |
| 4 | Create dedicated `classifyTransaction()` with separate prompt; simplify main prompt to "express in plain text" | Main prompt still had widget-legitimizing language → Gemini inferred compound_split_card was OK |

## Root Cause 1: System Prompt Cascade

Adding a prohibition to the main `_systemPrompt` affects EVERY Gemini call because `sendMessage()` injects it into all requests. The classification call needs permissive JSON instructions; the main chat call needs restrictive "text only" instructions. One prompt cannot serve both.

**Fix:** Dedicated `classifyTransaction()` method with its own `_classifySystemPrompt`.

## Root Cause 2: History Contamination + Two Paths

`_buildContents` sends ALL user messages to the main chat call. When tx#1 is confirmed and tx#2 sent, Gemini sees BOTH amounts → emits `compound_split_card`. Path 1 fires → `_tryAutoClassify` (no history, clean) is never called.

**Fix Layer 1:** Filter history — exclude user messages whose transactions were confirmed.
**Fix Layer 2:** Gate Path 1 — block transaction widgets from main response.

## Working Architecture

```dart
// Separate prompts per purpose
const _systemPrompt = 'عبر عن التصنيف بنص عادي.';
const _classifyPrompt = 'أجب بصيغة JSON فقط. للمعاملة: {"amount":N,...}';

// Filtered history
final filtered = history.where((m) {
  if (!m.isUser) return true;
  return !_confirmedIds.contains(m.id);
}).toList();

// Widget gate
if (isTransactionWidget(widget)) { /* DROP — classify instead */ }
else { show(widget); return; }
final result = await classify(text);  // always reached for transactions
```

## Key Insight

The main chat response must NEVER be the authority on transaction classification. Classification is the gatekeeper; main chat is conversational only.

## MoA Protocol Used

- Light 2-Round Protocol (Destroyer + Meta-critic)
- Both judges converged independently
- Destroyer scored architecture: 2/10 before fix
- User's intuition ("filter history") matched both judges independently

## Refs

- Azdal: `6cd69d0` (defense-in-depth), `641b0f0` (dedicated classifyTransaction), `18d882f` (action_buttons prompt fix)
- Handoff: `app-spec/CLAUDE_HANDOFF_history_leak.md`
