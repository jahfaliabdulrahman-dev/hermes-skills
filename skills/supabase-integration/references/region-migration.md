# Supabase Region Migration Guide

## Why
Supabase regions CANNOT be changed on an existing project. If you created a project in the wrong region (e.g., Sydney for a Saudi-based user), you must create a new project and transfer everything.

## When to migrate
- Latency is noticeably high (>200ms from your location)
- Project was created in wrong region accidentally
- Moving from a distant region (Oceania, US West) to a closer one (Frankfurt for ME)

## Step-by-step: Fresh migration (no data)

This was validated on 2026-07-12 when migrating Azdal from Sydney → Frankfurt.

### 1. Check current projects
```bash
npx supabase projects list
```
Note the org-id and old project ref.

### 2. Create new project in target region
```bash
npx supabase projects create "<name>" \
  --org-id <org-id> \
  --db-password '<password>' \
  --region eu-central-1 \
  --size nano
```

### 3. Get new project credentials
```bash
npx supabase projects api-keys --project-ref <new-ref> --output json
```
Extract:
- `type: "publishable"` → `SUPABASE_ANON_KEY`
- URL: `https://<new-ref>.supabase.co`
- DB: `postgresql://postgres:<password>@db.<new-ref>.supabase.co:5432/postgres`

### 4. Update .env
Replace old project ref with new one in all variables.

### 5. Re-link CLI
```bash
cd <project-dir>
npx supabase link --project-ref <new-ref>
```

### 6. Delete old project
```bash
# NOTE: ref is positional, NOT --project-ref flag
npx supabase projects delete <old-ref> --yes
```

### 7. Verify
```bash
# Python
python3 -c "
from supabase import create_client
c = create_client('https://<new-ref>.supabase.co', '<anon-key>')
print('✅ Connected to', c.supabase_url)
"

# CLI
npx supabase projects list
```

## If project has data
1. Dump schema: Use Supabase Dashboard SQL Editor → export
2. Dump data: Use `npx supabase db dump` or Dashboard export
3. Create new project (steps 1-3 above)
4. Restore schema first, then data
5. Verify row counts match
6. Delete old project (step 6)
