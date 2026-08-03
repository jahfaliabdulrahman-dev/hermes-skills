# MCP Bridge Architecture — Lessons Learned

> 2026-07-19/20. Evolution v1.0 → v2.0. Source: Claude Desktop → Hermes Lead Architect integration.

## Key Lessons

### 1. NEVER use exec() or spawn() in MCP stdio servers
MCP servers launched over stdio inherit a **limited subset** of environment variables from Claude Desktop. The user's full PATH is not available. `exec("hermes kanban show")` fails silently. All tool implementations must use HTTP API to the Hermes Gateway at `:8642`.

### 2. Blocking subprocess calls exceed Claude Desktop's MCP timeout
`hermes chat -q` for large EPICs (9KB+) takes 60-120 seconds. Claude Desktop MCP timeout is ~60 seconds. Result: `-32001: Request timed out`. Fix: non-blocking HTTP API with task_id polling.

### 3. File-persisted tasks survive crashes
In-memory `Map<string, Task>` is lost on server restart. Use filesystem: `~/.hermes/bridge/tasks/{taskId}.json`. Content-hash dedup prevents duplicate EPICs.

### 4. Adaptive race is fragile
`Promise.race([hermesApiBg(), hermesApi()])` creates two simultaneous HTTP requests, leaking connections. Simpler: always return task_id immediately, let Claude poll.

### 5. Mandatory project_path prevents cross-project contamination
`lead_delegate` must require `project_path`. Validate with `fs.existsSync()`. Refuse if missing or invalid. No defaults. No implicit routing from profile memory.
