---
name: mcp-bridge-patterns
description: Build MCP stdio bridges that connect an external LLM client (Claude Desktop, Kimi, any MCP host) to an agent runtime over HTTP. Zero-dependency server template, non-blocking dispatch with file persistence, and the PATH/environment traps that make subprocess-based bridges fail in production.
sources:
  - https://modelcontextprotocol.io/docs/concepts/transports (stdio transport + limited environment inheritance)
  - Production bridge shipped as a Claude Desktop .mcpb extension (2026-07-19) — every pitfall below was paid for in a real failure
---

# MCP Bridge Patterns

Patterns for a bridge process that speaks **MCP stdio** to an LLM client on one side and **HTTP** to an
agent runtime on the other. Written after shipping one and breaking it several times.

## When to Use

- Building an MCP bridge in Node.js with the stdio transport
- Debugging `MCP error -32001`, `socket hang up`, or a tool that hangs the host UI
- A bridge that works in your shell but fails inside the LLM client
- Long-running agent work that must not block the client's tool call

---

## Pattern 1: HTTP, never a subprocess

**Problem:** `spawn("<agent-cli> chat -q ...")` looks obvious and fails in production. MCP stdio servers
inherit only a **limited subset** of the environment, so your CLI is usually not on `PATH` at all — and even
when it is, process startup dominates latency.

**Solution:** POST to the runtime's HTTP API. No subprocess anywhere in the hot path.

```javascript
function agentApi(messages, profile, timeoutMs, retries = 2) {
  return new Promise((resolve, reject) => {
    const attempt = (n) => {
      const req = request(`${API_URL}/v1/chat/completions`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${API_KEY}`, "Content-Type": "application/json" },
        timeout: timeoutMs,
      }, (res) => { /* accumulate, parse, resolve */ });
      req.on("error", (e) => {
        if (n > 0 && isTransient(e)) setTimeout(() => attempt(n - 1), backoff(n));
        else reject(e);
      });
      req.write(body); req.end();
    };
    attempt(retries);
  });
}
```

**Retry only transients:** `socket hang up`, `ECONNRESET`, timeout. Backoff 2s → 4s, max 3 attempts.
Retrying a 4xx just multiplies a bad request.

**Credentials:** read the API key from the runtime's env file **once at startup**, then set the
`Authorization` header on every request. Never inline a key in the manifest — clients ship manifests around.

---

## Pattern 2: Non-blocking dispatch with file persistence

Any tool whose work can exceed a few seconds must return a `task_id` immediately and let the client poll a
`task_status` tool. A blocking tool call freezes the host UI and eventually times out on the client side,
which is indistinguishable from a crash to the user.

Make the dispatcher:
- **persist to disk** — the bridge is restarted by the client at will; in-memory state is a lie
- **dedup by content hash** — the same request re-sent gets the same `task_id` instead of a second run
- **cap concurrency** (2 is a sane default) and **auto-clean** finished records after ~1h

---

## Pattern 3: Two ID namespaces in one status tool

A status tool usually has to resolve more than one kind of identifier:

| ID shape | Origin | Resolution |
| --- | --- | --- |
| `task-…` | dispatched by this bridge | local file persistence |
| `t_…` | a work item in the runtime's own board/queue | HTTP API — **never** `exec()` |

Detect the shape, then resolve. Do not make the client remember which tool to call.

---

## Pattern 4: Route by explicit workspace path

If the runtime keeps separate boards/queues per project, map an explicit `project_path` argument to the
target, and inject it into the request:

```javascript
const boardMap = { "/abs/path/project-one": "project-one", "/abs/path/project-two": "project-two" };
const board = boardMap[projectPath] || "default";
```

## Pattern 5: Make `project_path` mandatory

A delegation tool must **require** the workspace path and validate it with `fs.existsSync()`. No path → hard
refusal. This single rule kills the most expensive failure class in bridge operation: work dispatched to the
wrong project because the model inferred the target from stale context instead of being told.

---

## Pattern 6: The environment trap, stated plainly

Per the MCP spec, stdio servers inherit a limited subset of environment variables. Therefore:
`exec()`, `spawn()`, and anything that resolves a binary from `PATH` are all unreliable inside the bridge.
Route every capability through the HTTP API, which runs in the full user environment.

---

## Zero-dependency server

Bridges are shipped as client extensions, and the host's bundled Node runtime does **not** include the MCP
SDK. Implementing the protocol by hand is ~30 lines and produces a ~5KB artifact that cannot fail on a
missing native module. The complete template, plus the packaging notes, lives in
[`references/zero-dependency-server-template.md`](references/zero-dependency-server-template.md).

```javascript
#!/usr/bin/env node
// stdio JSON-RPC — no dependencies
process.stdin.on("data", data => {
  for (const line of data.toString().trim().split("\n")) {
    if (!line) continue;
    try { handleMessage(JSON.parse(line)); } catch (e) { /* log to stderr, never stdout */ }
  }
});

function send(msg) { process.stdout.write(JSON.stringify(msg) + "\n"); }

function handleMessage(msg) {
  if (msg.method === "initialize") {
    send({ jsonrpc: "2.0", id: msg.id, result: {
      protocolVersion: "2024-11-05",
      capabilities: { tools: {} },
      serverInfo: { name: "bridge", version: "1.0.0" },
    }});
  } else if (msg.method === "tools/list") {
    send({ jsonrpc: "2.0", id: msg.id, result: { tools: [ /* … */ ] }});
  } else if (msg.method === "tools/call") {
    runTool(msg.params.name, msg.params.arguments)
      .then(r => send({ jsonrpc: "2.0", id: msg.id, result: r }))
      .catch(e => send({ jsonrpc: "2.0", id: msg.id, result: {
        content: [{ type: "text", text: e.message }], isError: true }}));
  }
}

setTimeout(() => {}, 86400000); // an MCP stdio server must never exit on its own
```

`package.json` needs `{ "type": "module", "main": "server/index.js" }`.

**stdout is the protocol channel.** Every log line, warning, or stray `console.log` corrupts the JSON-RPC
stream — send diagnostics to stderr only. This is the single most common cause of a bridge that "connects
and then dies".
