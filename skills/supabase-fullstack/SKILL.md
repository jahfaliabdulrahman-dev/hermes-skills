---
name: supabase-fullstack
description: "Complete Supabase workflow — frontend (supabase-js, SSR, Next.js, React, auth/sessions), backend (Python, CLI, PostgreSQL, RLS), and DevOps (migrations, edge functions, MCP). Merged from official @supabase/skills (frontend) + hermes-skills supabase-integration (backend). Use for any Supabase task regardless of stack."
version: "1.0.0"
author: "Supabase (frontend) + Hermes Skills (backend) — merged & extended"
---

# Supabase Fullstack

Complete Supabase knowledge covering frontend, backend, CLI operations, and security. Merged from the official Supabase agent skill (frontend focus) and production backend patterns from Azdal, CarSah, and Hermex Android.

## When to Use

ANY task involving Supabase — Database, Auth, Edge Functions, Realtime, Storage, Vectors, Cron, Queues, client libraries (supabase-js, @supabase/ssr, supabase-py), Flutter integration, CLI operations, MCP server, schema changes, migrations, RLS, security audits.

---

# Part 1: Frontend (Official Supabase)

## Core Principles

**1. Supabase changes frequently — verify against changelog before implementing.**
Fetch `https://supabase.com/changelog.md`, scan for `breaking-change` tags, follow linked pages. Then look up the relevant topic using MCP `search_docs` or append `.md` to any docs URL.

**2. Verify your work.** After any fix, run a test query. A fix without verification is incomplete.

**3. Recover from errors, don't loop.** If an approach fails after 2-3 attempts, stop and reconsider. Try a different method, check documentation, inspect errors, review logs.

**4. Exposing tables to the Data API:** Newly created tables may not be auto-exposed via the Data (REST) API depending on [Data API settings](https://supabase.com/dashboard/project/<ref>/integrations/data_api/settings). `anon` and `authenticated` roles may need explicit `GRANT` access. This is separate from RLS.

**5. RLS on every table in exposed schemas** (includes `public` by default). After enabling RLS, create policies matching the actual access model — don't default every table to the same `auth.uid()` pattern.

## Security Checklist

### Auth & Session Security
- **Never use `user_metadata` in JWT authorization.** `raw_user_meta_data` is user-editable. Store authorization data in `raw_app_meta_data` / `app_metadata`.
- **Deleting a user does not invalidate existing tokens.** Sign out/revoke sessions first. Validate `session_id` against `auth.sessions` for strict guarantees.
- **JWT claims are not always fresh** — tokens must be refreshed to pick up new `app_metadata`.

### API Key & Client Exposure
- **Never expose `service_role` key in public clients.** Use publishable keys for frontend. `NEXT_PUBLIC_` env vars are sent to browser.

### RLS, Views & Privileged Code
- **Views bypass RLS by default.** Postgres 15+: `CREATE VIEW ... WITH (security_invoker = true)`. Older: revoke access from `anon`/`authenticated` or put in unexposed schema.
- **UPDATE requires SELECT policy.** Without SELECT, updates silently return 0 rows.
- **`auth.role()` is deprecated** — use `TO authenticated` or `TO anon` instead. `auth.role() = 'authenticated'` breaks silently with anonymous sign-ins.
- **`TO authenticated` alone is BOLA/IDOR.** Always combine with ownership predicate:
  ```sql
  CREATE POLICY "example" ON table_name FOR SELECT
  TO authenticated
  USING ( (SELECT auth.uid()) = user_id );
  ```
- **UPDATE needs both USING and WITH CHECK.** Without `WITH CHECK`, users can reassign `user_id`:
  ```sql
  CREATE POLICY "example" ON table_name FOR UPDATE
  TO authenticated
  USING ( (SELECT auth.uid()) = user_id )
  WITH CHECK ( (SELECT auth.uid()) = user_id );
  ```
- **`SECURITY DEFINER` functions bypass RLS.** Never add `SECURITY DEFINER` to resolve a permission error. Prefer `SECURITY INVOKER`.
- **`SECURITY DEFINER` in `public` is callable by all roles.** Postgres grants `EXECUTE` to `PUBLIC` by default. Keep in non-exposed schema, include `auth.uid()` check, run `supabase db advisors`.

### Storage Access Control
- **Storage upsert requires INSERT + SELECT + UPDATE.** Granting only INSERT silently fails on replacement.

### Dependency Security
- **Always pin versions and commit lockfiles** for supabase-js, @supabase/ssr, supabase-py, etc.

For full security guide: `https://supabase.com/docs/guides/security/product-security.md`

## Supabase CLI

```bash
supabase --help                    # All top-level commands
supabase <group> --help            # Subcommands
supabase <group> <command> --help  # Flags for specific command
```

**Known gotchas:**
- `supabase db query` requires CLI v2.79.0+
- `supabase db advisors` requires CLI v2.81.3+
- For imperative migrations: `supabase migration new <name>` first — never invent filenames
- For declarative schemas: edit `supabase/schemas/`, then generate migration

## Supabase MCP Server

Setup: https://supabase.com/docs/guides/getting-started/mcp

**Troubleshooting:**
1. `curl -so /dev/null -w "%{http_code}" https://mcp.supabase.com/mcp` — 401 = server up
2. Check `.mcp.json` has correct server URL
3. Authenticate via OAuth 2.1 flow

## Schema Changes Workflow

### Declarative (when `supabase/schemas/` exists)
Edit schema files → generate migration → review. See [Declarative schemas guide](https://supabase.com/docs/guides/local-development/declarative-database-schemas).

### Imperative (no declarative schemas)
Use `execute_sql` (MCP) or `supabase db query` (CLI) to iterate. Do NOT use `apply_migration` for iteration — it writes migration history on every call.

**When ready to commit:**
1. Run `supabase db advisors` → fix issues
2. Review Security Checklist
3. `supabase db pull <name> --local --yes`
4. Verify: `supabase migration list --local`

---

# Part 2: Backend & DevOps (Hermes Skills)

## Connection Methods (3 tiers)

### Tier 1: supabase-py (Python — fastest for agent use)

```python
from supabase import create_client

url = "https://<project-ref>.supabase.co"
key = "<anon-key>"
client = create_client(url, key)

# Verify connection
result = client.table("your_table").select("*").limit(1).execute()
```

**Install**: Use the project venv Python explicitly. Do NOT use system `pip3`/`python3`.

### Tier 2: Supabase CLI (npx — migrations, local dev, edge functions)

```bash
npx supabase --version
npx supabase login       # INTERACTIVE — needs browser/TTY
npx supabase init
npx supabase link --project-ref <ref>
npx supabase db push
```

### Tier 3: Direct PostgreSQL (psql — raw SQL access)

```bash
PGPASSWORD='<password>' psql "postgresql://postgres:***@db.<ref>.supabase.co:5432/postgres"
```

## Auth Configuration via `config push`

Edit `supabase/config.toml` → push without Dashboard:

```bash
npx supabase config push --project-ref <ref>
# For automated runs:
echo "Y" | npx supabase config push --project-ref <ref>
```

**Verification:**
```bash
curl -s "https://<ref>.supabase.co/auth/v1/settings" \
  -H "apikey: <anon-key>" \
  -H "Authorization: Bearer <anon-key>" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print('anonymous_users:', d['external']['anonymous_users'])"
```

| Task | Method |
|------|--------|
| Enable anonymous sign-ins | `config push` ✅ |
| Toggle email confirmations | `config push` ✅ |
| Add OAuth provider (Google, Apple) | Dashboard (secrets required) |
| Change JWT expiry | `config push` ✅ |
| Configure MFA | `config push` ✅ |

## Flutter Integration

### PITFALL: Hardcoded Supabase credentials in `main.dart`

**Anti-pattern:**
```dart
await Supabase.initialize(
  url: 'https://kqhyjngtquutzdvjfbnf.supabase.co',    // ❌ hardcoded
  publishableKey: 'eyJhbG...6Bik',                     // ❌ hardcoded
);
```

**Fix — use `Platform.environment`:**
```dart
import 'dart:io' show Platform;

await Supabase.initialize(
  url: Platform.environment['SUPABASE_URL'] ?? '',
  publishableKey: Platform.environment['SUPABASE_ANON_KEY'] ?? '',
);
```

For mobile: `--dart-define-from-file=.env` at build time.

### .env Template

Always create THREE files:
- `.env` — real credentials (gitignored)
- `.env.example` — placeholder values, safe to commit
- `.env.template` — instructional header for new developers

**`.gitignore` MUST use negation:**
```gitignore
.env
.env.*
!.env.example
!.env.template
```

Without `!` negations, `.env.*` blocks ALL env variants including templates.

## Schema Deployment Workflow

1. Read schema file (e.g., `app-spec/INIT-03_supabase_schema.md`)
2. Open SQL Editor: `https://app.supabase.com/project/<ref>/sql/new`
3. Execute SQL blocks in order
4. Verify each table: `client.table("<name>").select("*").limit(1).execute()`
5. Verify RLS — query `pg_policies` directly
6. Verify all tables have `rowsecurity = true` in `pg_tables`
7. Run `flutter analyze` after any credential refactoring

## Region Selection (Middle East / Saudi Arabia)

| Region | Location | Latency | Notes |
|--------|----------|---------|-------|
| `eu-central-1` | Frankfurt 🇩🇪 | ~80ms | **Recommended** for ME |
| `ap-south-1` | Mumbai 🇮🇳 | ~90ms | Closer, less reliable |
| `eu-west-1` | Ireland 🇮🇪 | ~120ms | Acceptable fallback |

```bash
npx supabase projects create "<name>" \
  --org-id <org-id> \
  --db-password '<password>' \
  --region eu-central-1 \
  --size nano
```

Region CANNOT be changed later — to migrate, create new project and transfer.

---

# Part 3: Production Pitfalls (ALL)

### PITFALL 1: `supabase login` fails in non-TTY
```
Cannot use automatic login flow inside non-TTY environments.
```
**Fix A**: User runs `npx supabase login` in their terminal.
**Fix B**: Generate access token at [supabase.com/dashboard/account/tokens](https://supabase.com/dashboard/account/tokens) → `npx supabase login --token <token>` or `export SUPABASE_ACCESS_TOKEN=<token>`.

### PITFALL 2: Python venv version mismatch
System Python 3.13 importing hermes venv's Python 3.11 pydantic → `ModuleNotFoundError`.
**Fix**: ALWAYS use the project venv Python explicitly.

### PITFALL 3: First query fails with PGRST205
NORMAL on fresh project — auth succeeded but no tables exist. Connection is working.

### PITFALL 4: `projects delete` rejects `--project-ref` flag
**Fix**: The ref is POSITIONAL: `npx supabase projects delete <ref> --yes` — NOT `--project-ref <ref>`.

### PITFALL 5: API keys ALWAYS truncated in CLI
`supabase projects api-keys` truncates in ALL formats (text AND JSON). Use Dashboard or `.env` for full keys.

### PITFALL 6: Project name collision
Use a slightly different name. Old project must be deleted first to reuse exact name.

### PITFALL 7: `.env.template` blocked by `.env.*` gitignore
Add negation: `!.env.template`.

### PITFALL 8: Tests + Agent Approval ≠ Verification (LL-010)
From Azdal Stage 4: 5 critical bugs found on live device AFTER 34/34 tests passing + Zero-Trust Auditor APPROVE + SCSI Guardian ALL CLEAR. Always verify on real device with direct database queries.

### PITFALL 9: Regex Pre-Filter Gates (LL-011)
Local RegExp gates before LLM classifiers are fine for cost optimization — but MUST have a fallback path. A miss degrades to confidently-wrong-and-silent, not "slower but correct."

### PITFALL 10: Disabled Button Colors (LL-011)
`ElevatedButton.styleFrom(backgroundColor:, foregroundColor:)` only styles the ENABLED state. Once `onPressed: null`, Material silently substitutes its default disabled palette. Always set `disabledBackgroundColor`/`disabledForegroundColor` explicitly.

---

## Verification Checklist

- [ ] supabase-py imports without error (use project venv python)
- [ ] `create_client(url, key)` succeeds
- [ ] At least one table query returns 200
- [ ] `npx supabase --version` returns version
- [ ] `.env` file created, `.env.example` + `.env.template` committed
- [ ] Schema deployed and verified via direct DB query
- [ ] RLS policies verified via `pg_policies`
- [ ] All tables have `rowsecurity = true`
- [ ] No hardcoded credentials in source code
- [ ] Security Checklist reviewed for auth/storage/views changes
- [ ] **Live device verification** — tests passing ≠ it works (LL-010)
