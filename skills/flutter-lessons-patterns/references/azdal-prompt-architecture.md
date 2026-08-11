# Azdal — Prompt Architecture Lessons

> **Session:** 2026-07-12  
> **Source:** Three cycles of debugging prompt interference between main chat and classification calls.

## Core Lesson: System Prompt Isolation

When a single Gemini API key serves TWO roles (chat response + transaction classification), the chat system prompt MUST NOT include instructions that block the classification call's needs.

### The Pattern (3 incarnations, same bug class)

| Incident | System Prompt Said | Classification Needed | Result |
|----------|-------------------|----------------------|--------|
| Action_buttons | "أرسل action_buttons JSON" | Don't emit action_buttons | Gemini emitted them → bypassed classification storage |
| Fix attempt 1 | "لا ترسل أبداً action_buttons" | Classification needs structured JSON | Classification call also blocked → no confirm buttons |
| Compound_split_card | "استخدم compound_split_card" | Don't emit from main chat | History leaked → stale items bundled |
| Fix attempt 2 | "لا ترسل compound_split_card" | Classification needs compound_split_card | Classification call also blocked → compound never appears |

### The Solution

Add a **dedicated classification method** with its OWN system prompt:

```
GeminiService.sendMessage()      → _systemPrompt (chat)
GeminiService.classifyTransaction() → _classifySystemPrompt (classification only)

No overlap. No conflict. No history in classification call.
```

### Why This Works

1. **Separate system prompts** — main chat never sees classification instructions, classification never sees chat instructions
2. **No history** — `classifyTransaction` receives ONLY the current user text
3. **Single responsibility** — classification call does one thing

### When to Use

Any time a single LLM serves multiple roles in the same app with conflicting prompt requirements.

### Related Commits

- `18d882f`: Action_buttons removed from system prompt
- `75935c5`: Compound_split_card removed from system prompt (broke classification)
- `641b0f0`: Dedicated `classifyTransaction` method (final fix)
