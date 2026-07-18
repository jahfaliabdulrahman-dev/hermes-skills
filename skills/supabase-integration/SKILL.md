---
name: "supabase-integration"
description: "Complete Supabase workflow — Python client, CLI, PostgreSQL, Flutter integration, schema deployment, and credential management. Use when connecting to Supabase, deploying schemas, or troubleshooting Supabase connectivity."
---

# Supabase Integration

Complete Supabase workflow — Python client, CLI, PostgreSQL, Flutter integration, and project setup. Covers connection, schema deployment, auth, and troubleshooting.

## Triggers

- "supabase" — any mention
- "connect to database" in context of Supabase
- "setup backend" for Flutter projects
- Deploying SQL schemas
- Supabase CLI operations
- "change region" / "migrate region" for Supabase projects
- "setup supabase" / "configure supabase"
- "enable anonymous" / "anonymous sign-in" / "anon sign"
- "enable auth provider" / "enable MFA" / "auth settings"

## Quick Reference: Current Projects

| Project | Supabase Status | Ref | Region |
|---------|----------------|-----|--------|
| Azdal | Schema ready (`INIT-03_supabase_schema.md`) | `kqhyjngtquutzdvjfbnf` | Central EU (Frankfurt) 🇩🇪 |

Credentials stored in project `.env` files — NEVER hardcode in code or chats.

## Support Files

- `references/venv-python-path.md` — Exact Python venv paths to avoid version mismatch errors
- `references/region-migration.md` — How to migrate a Supabase project to a different region
- `templates/supabase.env` — Standard `.env` template for Flutter + Supabase projects

---

## Connection Methods (3 tiers)

### Tier 1: supabase-py (Python — fastest for agent use)

```python
from supabase import create_client

url = "https://<project-ref>.supabase.co"
key = "<anon-key>"
client = create_client(url, key)

# Verify connection with a table query
result = client.table("your_table").select("*").limit(1).execute()
```

**Install**: Use the Hermes venv Python explicitly (see `references/venv-python-path.md` for exact commands). Always prefer the venv python over system python to avoid version mismatch errors.

### Tier 2: Supabase CLI (npx — migrations, local dev, edge functions)

```bash
npx supabase --version  # verify installed
npx supabase login       # INTERACTIVE — needs browser/TTY
npx supabase init        # creates supabase/ directory
npx supabase link --project-ref <ref>
npx supabase db push     # push local migrations to remote
```

### Tier 3: Direct PostgreSQL (psql — raw SQL access)

```bash
PGPASSWORD='<password>' psql "postgresql://postgres:<password>@db.<ref>.supabase.co:5432/postgres"
```

---

## Auth Configuration via CLI (`config push`)

Auth settings (anonymous sign-ins, provider toggles, MFA, email/SMS config) can be changed **without the Dashboard** by editing `supabase/config.toml` and pushing it to the remote project.

### Workflow

```bash
# 1. Edit the auth section in config.toml
#    Key settings: enable_anonymous_sign_ins, enable_signup, [auth.external.*]

# 2. Push to remote (requires prior `supabase link` or --project-ref)
npx supabase config push --project-ref <ref>
```

The command shows a diff of all changes across API/DB/Auth/Storage and **prompts for confirmation** before applying Auth changes. Pipe `echo "Y"` for automated runs:

```bash
echo "Y" | npx supabase config push --project-ref <ref>
```

### Verifying Auth changes took effect

Query the GoTrue settings endpoint with the anon key:

```bash
curl -s "https://<ref>.supabase.co/auth/v1/settings" \
  -H "apikey: <anon-key>" \
  -H "Authorization: Bearer <anon-key>" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print('anonymous_users:', d['external']['anonymous_users'])"
```

### When to use `config push` vs Dashboard

| Task | Method |
|------|--------|
| Enable anonymous sign-ins | `config push` ✅ |
| Toggle email confirmations | `config push` ✅ |
| Add OAuth provider (Google, Apple, etc.) | Dashboard (secrets required) |
| Change JWT expiry | `config push` ✅ |
| Configure MFA | `config push` ✅ |

### PITFALL: `projects api-keys` truncates keys

The CLI deliberately masks full API key values in output (shows `eyJhbG...KOIA` or Unicode middle-dot padding). These **cannot be extracted** from the CLI — use the Dashboard or a stored `.env` file for full keys. For the Management API (PATCH `api.supabase.com`), you need a Personal Access Token from `https://supabase.com/dashboard/account/tokens`, not a project API key.

---

## Pitfalls & Fixes

### PITFALL 1: `supabase login` fails in non-TTY
```
Cannot use automatic login flow inside non-TTY environments.
```
**Fix A**: User runs `npx supabase login` in their own terminal → browser opens → auto-auth.
**Fix B**: Generate access token at [supabase.com/dashboard/account/tokens](https://supabase.com/dashboard/account/tokens), then:
```bash
npx supabase login --token <access-token>
# OR
export SUPABASE_ACCESS_TOKEN=<access-token>
```

### PITFALL 2: Python venv version mismatch
System Python 3.13 importing hermes venv's Python 3.11 pydantic → `ModuleNotFoundError: pydantic_core._pydantic_core`.
**Fix**: ALWAYS use the hermes venv Python explicitly. See `references/venv-python-path.md`. Do NOT use system `pip3` or `python3` for project tools — they may resolve against wrong venv packages.

### PITFALL 3: Anon key format variations
Supabase anon keys can be:
- `sb_publishable_...` (newer format)  
- `eyJ...` (JWT format)
Both work — don't flag format as error when verifying.

### PITFALL 4: First query fails with PGRST205
```
{"code": "PGRST205", "message": "Could not find the table 'public.X' in the schema cache"}
```
This is NORMAL on a fresh project — means auth succeeded but no tables exist yet. Connection is working. Proceed to deploy schema.

### PITFALL 5: `projects delete` rejects `--project-ref` flag
```
Unrecognized flag: --project-ref in command supabase projects delete
```
**Fix**: The ref is POSITIONAL, not a flag:
```bash
# WRONG
npx supabase projects delete --project-ref <ref>
# RIGHT
npx supabase projects delete <ref> --yes
```

### PITFALL 6: API keys are ALWAYS truncated — CLI security design

`npx supabase projects api-keys` shows truncated keys in ALL output formats — text AND JSON. The CLI deliberately masks full key values with `...` (e.g., `eyJhbG...KOIA`) and Unicode middle-dot padding (`········`). This is a security feature, not a display bug.

```bash
# ALL of these truncate — there is NO way to get full keys from the CLI:
npx supabase projects api-keys --project-ref <ref>              # truncated
npx supabase projects api-keys --project-ref <ref> --output json # ALSO truncated
npx supabase projects api-keys --project-ref <ref> --output json | python3 -c "import json,sys; [print(k['api_key']) for k in json.load(sys.stdin)]"  # STILL truncated — dots are literal chars
```

**Real fixes for getting full keys:**
1. **Dashboard** → Project Settings → API → copy full key
2. **`.env` file** (if already stored there)
3. **Management API** (requires Personal Access Token from `https://supabase.com/dashboard/account/tokens`, NOT a project API key)

**Why this matters:** You cannot programmatically enable auth providers or anonymous sign-ins via the GoTrue Admin API without the `service_role` key. But the CLI hides it. Use `supabase config push` instead (see "Auth Configuration via CLI" above) — it uses the CLI's internal auth token, not project API keys.

### PITFALL 7: Project name collision on creation
```
Project with name "X" already exists in your organization.
```
**Fix**: Use a slightly different name. The old project must be deleted first if you want to reuse the exact name.

### PITFALL 8: Hardcoded Supabase credentials in Flutter `main.dart`
Credentials written as string literals in code — inconsistent with env-based services like `gemini_service.dart`, and undoes the `.env` setup. Also makes region migration painful (code changes required).

**Anti-pattern** (what to catch and fix):
```dart
await Supabase.initialize(
  url: 'https://kqhyjngtquutzdvjfbnf.supabase.co',       // ❌ hardcoded
  publishableKey: 'eyJhbG...6Bik',                        // ❌ hardcoded
);
```

**Fix**: Use `Platform.environment` — matches `gemini_service.dart`'s pattern, zero additional deps:
```dart
import 'dart:io' show Platform;

await Supabase.initialize(
  url: Platform.environment['SUPABASE_URL'] ?? '',
  publishableKey: Platform.environment['SUPABASE_ANON_KEY'] ?? '',
);
```

**Why NOT flutter_dotenv**: The project already uses `Platform.environment` for `GEMINI_API_KEY`. Adding a second mechanism (`.env` file load at runtime) creates inconsistency. For tests/desktop: pass env vars via shell. For mobile: `--dart-define-from-file=.env` at build time.

### PITFALL 9: `.env.template` blocked by `.env.*` gitignore rule
Standard pattern `.env` + `.env.*` blocks ALL env variants. The negation `!.env.example` only allows ONE file. If the project also has `.env.template`, it stays blocked.

**Fix**: Add negation for each template variant:
```gitignore
.env
.env.*
!.env.example
!.env.template
```
**Verification**: `git status` should show `.env.example` and `.env.template` as trackable, but `.env` still ignored.

---

## .env Template

See `templates/supabase.env` for the standardized `.env` template. Variables: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `DATABASE_URL`, `GEMINI_API_KEY`.

**Always create THREE files:**
- `.env` — real credentials (gitignored — never committed)
- `.env.example` — same structure, placeholder values (`your-anon-key-here`, etc.) — safe to commit
- `.env.template` — same as `.env.example`, but with instructional header for new developers

**`.gitignore` MUST use negation rules** to allow template files while blocking `.env`:
```gitignore
.env
.env.*
!.env.example
!.env.template
```

Without the `!` negations, `.env.*` blocks ALL env variants including templates. Verify with `git status` after setup.

---

## Schema Deployment Workflow

1. Read the schema file (e.g., `app-spec/INIT-03_supabase_schema.md`)
2. Open Supabase SQL Editor: `https://app.supabase.com/project/<ref>/sql/new`
3. Paste and execute SQL blocks in order
4. Verify tables via `client.table("<name>").select("*").limit(1).execute()` for each
5. Verify RLS policies are enabled — use `psycopg2` to query `pg_policies` directly (see `references/rls-verification.md`)
6. Verify all tables have `rowsecurity = true` in `pg_tables`
7. Run `flutter analyze` to confirm no code regression after any credential refactoring

---

## Region Selection (Middle East / Saudi Arabia)

Supabase regions are set at project creation and CANNOT be changed later. To change region, you must create a new project and migrate.

### Best regions for Saudi Arabia (ordered by latency):

| Region Code | Location | Approx. Latency | Notes |
|-------------|----------|-----------------|-------|
| `eu-central-1` | Frankfurt 🇩🇪 | ~80ms | **Recommended** — best infrastructure for ME |
| `ap-south-1` | Mumbai 🇮🇳 | ~90ms | Geographically closer, less reliable infrastructure |
| `eu-west-1` | Ireland 🇮🇪 | ~120ms | Acceptable fallback |

### Creating a project in a specific region:

```bash
npx supabase projects create "<name>" \
  --org-id <org-id> \
  --db-password '<password>' \
  --region eu-central-1 \
  --size nano
```

Get your org-id from: `npx supabase projects list`

### Migrating to a new region (fresh project, no data):

1. Create new project in desired region
2. Get new credentials: `npx supabase projects api-keys --project-ref <new-ref> --output json`
3. Update `.env` with new URL and anon key
4. Re-link CLI: `npx supabase link --project-ref <new-ref>`
5. Delete old project: `npx supabase projects delete <old-ref> --yes` (positional, NOT `--project-ref`)
6. Verify connection to new project

---

## Verification Checklist

- [ ] `supabase-py` imports without error (use hermes venv python)
- [ ] `create_client(url, key)` succeeds
- [ ] At least one table query returns 200 (not PGRST205 or 404)
- [ ] `npx supabase --version` returns version
- [ ] `.env` file created with correct variables
- [ ] Schema deployed and verified
