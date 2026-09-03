---
name: mcp-bridge-patterns
description: Zero-dependency MCP stdio server patterns — non-blocking dispatch, manifest desync fixes, shell-vs-LLM verification. For building MCP bridges that connect external LLM clients (Claude Desktop, Kimi) to Hermes Agent.
version: 1.0.0
author: Sulaiman (agent-authored)
metadata:
  hermes:
    tags: [MCP, stdio, architecture, non-blocking, claude-desktop, hermes]
---

# MCP Bridge Patterns

Recurring patterns for building MCP servers that bridge Claude Desktop to Hermes Agent. **v2.0: HTTP Bridge replaces subprocess spawning.**

## When to Use

- Building a new MCP bridge (Node.js, stdio transport)
- Debugging "MCP error -32001" or `socket hang up` from Hermes Gateway API
- Adding tools to an existing MCP server
- Routing tasks to Kanban boards based on project path

---

## Pattern 1: HTTP Bridge (v2.0)

**Problem:** `spawn("hermes chat -q")` is slow, fragile, and fails in Claude Desktop because **MCP stdio servers inherit a limited subset of PATH**. `hermes` binary is not available.

**Solution:** HTTP POST to Hermes Gateway API. Zero subprocess. Retry logic handles transient failures.

```javascript
function hermesApi(messages, profile, timeoutMs, retries = 2) {
  return new Promise((resolve, reject) => {
    const attempt = (n) => {
      const req = request(`${API_URL}/v1/chat/completions`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${API_KEY}`, "Content-Type": "application/json" },
        timeout: timeoutMs,
      }, (res) => { /* accumulate data, parse, resolve */ });
      req.on("error", (e) => {
        if (n > 0 && isTransient(e)) setTimeout(() => attempt(n-1), backoff(n));
        else reject(e);
      });
      req.write(body); req.end();
    };
    attempt(retries);
  });
}
```

**Retry:** Only `socket hang up`, `ECONNRESET`, timeout. Backoff 2s→4s. Max 3 attempts.

**API key source:** Read from the Hermes environment file at server startup. Set the `Authorization` header on every request.

---

## Pattern 2: Non-blocking Dispatch with File Persistence

All tools (`quick_task`, `lead_delegate`, kanban views) should be non-blocking. Return `task_id` immediately. Background HTTP requests persist state to disk. Client polls via `lead_task_status`.

Key features: file persistence (survives restarts), content-hash dedup (duplicate EPICs get same ID), max 2 concurrent, auto-cleanup after 1h.

---

## Pattern 3: Kanban-Aware lead_task_status

`lead_task_status` accepts two ID formats:

| ID | Source | Resolution |
|----|--------|-----------|
| `task-xxx` | bridge dispatch | File persistence |
| `t_xxx` | Kanban card | HTTP API to Lead Architect profile — NEVER `exec()` |

**Never use `exec()`** to query Kanban. MCP servers don't inherit the user's PATH. Always route through the Gateway API with the Lead Architect profile.

---

## Pattern 4: Board Routing via project_path

Map `project_path` to board slug. Inject into Lead Architect prompt:

```javascript
const boardMap = { "Azdal": "azdal", "CarSah": "carsah" }; // key = project folder basename
const board = boardMap[projectPath] || "default";
```

Boards created with `hermes kanban boards create <slug>`. Isolated per-project history.

---

## Pattern 5: project_path Enforcement

`lead_delegate` MUST require `project_path`. Validate with `fs.existsSync()`. No path → hard refusal. Prevents the #1 contamination class: EPICs routed to wrong project via stale memory.

---

## Pattern 6: MCP PATH Limitations

Per MCP spec: stdio servers inherit a **limited subset** of environment variables. Never use `exec()`, `spawn()`, or any subprocess that depends on the user's PATH. Route everything through the Gateway API — it runs in the full user environment.

---

## Zero-Dependency MCP Server Boilerplate (Node.js)

```javascript
#!/usr/bin/env node
import { spawn, exec } from "child_process";

// Stdio JSON-RPC transport
process.stdin.on("data", data => {
  for (const line of data.toString().trim().split("\n")) {
    if (!line) continue;
    try { handleMessage(JSON.parse(line)); } catch(e) { /* log to stderr */ }
  }
});

function send(msg) { process.stdout.write(JSON.stringify(msg) + "\n"); }

function handleMessage(msg) {
  if (msg.method === "initialize") {
    send({ jsonrpc: "2.0", id: msg.id, result: {
      protocolVersion: "2024-11-05",
      capabilities: { tools: {} },
      serverInfo: { name: "...", version: "1.0.0" }
    }});
  } else if (msg.method === "tools/list") {
    send({ jsonrpc: "2.0", id: msg.id, result: { tools: [...] }});
  } else if (msg.method === "tools/call") {
    runTool(msg.params.name, msg.params.arguments)
      .then(r => send({ jsonrpc: "2.0", id: msg.id, result: r }))
      .catch(e => send({ jsonrpc: "2.0", id: msg.id, result: { content: [{ type: "text", text: e.message }], isError: true }}));
  }
}

// Keep process alive (MCP stdio server must never exit)
setTimeout(() => {}, 86400000);
```

**package.json requirements:**
```json
{ "type": "module", "main": "server/index.js" }
```
