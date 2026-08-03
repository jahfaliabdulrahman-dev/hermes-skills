# Zero-Dependency MCP Server Template

Complete working Node.js MCP server with zero external dependencies. Implements the MCP stdio protocol manually (JSON-RPC over stdin/stdout). Proven in production with the lead-controller MCP (2026-07-19).

## Why Zero-Dependency

Claude Desktop's built-in Node.js runtime does NOT include `@modelcontextprotocol/sdk`. Two options:
1. **Bundled SDK**: 20MB+ `.mcpb` file, may still crash on missing native modules
2. **Manual protocol**: ~5KB `.mcpb`, never crashes on missing deps, faster startup

The MCP protocol is simple enough that a manual implementation is ~30 lines.

## Template

```js
#!/usr/bin/env node
// Zero-dependency MCP server — stdio JSON-RPC
import { spawn } from "child_process";

// ── MCP Protocol (barebones) ──
process.stdin.on("data", data => {
  for (const line of data.toString().trim().split("\n")) {
    if (!line) continue;
    const msg = JSON.parse(line);
    handle(msg);
  }
});

function send(obj) {
  process.stdout.write(JSON.stringify(obj) + "\n");
}

function handle(msg) {
  if (msg.method === "initialize") {
    send({ jsonrpc: "2.0", id: msg.id, result: {
      protocolVersion: "2024-11-05",
      capabilities: { tools: {} },
      serverInfo: { name: "my-server", version: "1.0.0" }
    }});
  }
  else if (msg.method === "tools/list") {
    send({ jsonrpc: "2.0", id: msg.id, result: { tools: [
      { name: "my_tool", description: "What this tool does.",
        inputSchema: { type: "object", properties: {
          param: { type: "string", description: "Parameter description" }
        }, required: ["param"] } }
    ]}});
  }
  else if (msg.method === "tools/call") {
    const { name, arguments: args } = msg.params;
    const result = `Executed ${name} with ${JSON.stringify(args)}`;
    send({ jsonrpc: "2.0", id: msg.id, result: {
      content: [{ type: "text", text: result }]
    }});
  }
}

// Keep process alive (prevents premature exit)
setTimeout(() => {}, 86400000);
process.stderr.write("[my-server] ready\n");
```

## Crash Pattern (SDK-based servers)

```
Server started and connected successfully
Message from client: method="initialize" id=0
Server transport closed unexpectedly, this is likely due to the process exiting early
```

**Root cause:** `import { Server } from "@modelcontextprotocol/sdk/..."` fails because Claude's built-in Node.js doesn't have the SDK. Even when bundled, native addons may fail.

**Fix:** Replace SDK import with manual protocol (template above).

## Packaging

```
my-server/
├── server/
│   └── index.js        # Template above
├── package.json         # { "name": "...", "type": "module", "dependencies": {} }
├── manifest.json       # Standard MCPB manifest
└── icon.png            # 64x64 PNG
```

```bash
cd my-server && zip -r ~/Desktop/my-server.mcpb . -x ".DS_Store"
```

## Key Constraints

- Only `import` from Node.js built-ins: `child_process`, `fs`, `path`, `os`
- No `node_modules/` in `.mcpb` — Claude's Node.js can't resolve them
- Use `setTimeout(() => {}, 86400000)` to keep process alive
- All output to `process.stdout`; debug to `process.stderr`
