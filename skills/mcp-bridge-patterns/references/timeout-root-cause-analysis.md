# Root Cause Analysis: lead_delegate Timeout (-32001)

> Real-world debugging session from 2026-07-19. Azdal project EPIC delegation failing
> 3/3 attempts with identical MCP error -32001. Full investigation below.

## Symptom Summary

| Attempt | Payload Size | Result | Kanban After |
|---------|-------------|--------|-------------|
| 1 | ~8.5 KB | -32001 timeout | 0 active tasks |
| 2 | ~9 KB | -32001 timeout | 0 active tasks |
| 3 | ~7.8 KB | -32001 timeout | 0 active tasks |

Other tools worked: `lead_ultra_check` (10/10), `lead_kanban_view` (with 1 transient timeout).

## Root Cause Chain

```
1. Claude sends tools/call(lead_delegate) with 9KB /goal brief
2. MCP server spawns: hermes chat -q [9KB prompt] -p flutter-lead-architect
3. Hermes needs 60-90+ seconds to:
   - Parse the complex EPIC brief (6 phases, 7 workers, 14 exit criteria)
   - Find project files (stale path ~/Azdal/ → wastes turns → adds latency)
   - Decompose into Kanban tasks
   - Respond with task IDs
4. Claude Desktop's MCP timeout fires at ~60 seconds
5. MCP server still waiting for hermes → no response sent → -32001
6. Hermes eventually finishes at ~90s but nobody is listening
```

## Contributing Factor: Stale Project Path

MEMORY.md had `Azdal ~/Azdal/` but the real path is `~/Projects/Azdal/`.
Hermes wasted turns trying to access a nonexistent directory before failing.
This added ~10-20 seconds of wasted latency per attempt.

## Fix Applied

1. **Non-blocking architecture** (v1.3): `lead_delegate` returns task_id immediately,
   `lead_task_status(task_id)` polls for results. Eliminates the timeout race entirely.

2. **Stale path fixed**: MEMORY.md updated to `Azdal ~/Projects/Azdal/`.

## Lesson

Any MCP tool that spawns a subprocess lasting >10 seconds MUST be non-blocking.
Claude Desktop's ~60s timeout is shorter than typical LLM processing time for
complex prompts. Blocking tools will always race the timeout.

## Reproduction

- MCP server: Flutter Lead Architect Controller v1.0 (old blocking architecture)
- Payload: `/goal` brief with 6 phases, 7 workers, 14 exit criteria (~8-9KB markdown)
- Hermes profile: flutter-lead-architect (deepseek-v4-pro, reasoning_effort: ultra)
- Claude Desktop MCP client
