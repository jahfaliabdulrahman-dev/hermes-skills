# RLS Policy Verification

After deploying a Supabase schema, verify that Row-Level Security (RLS) is properly configured on all tables.

## Method 1: Direct PostgreSQL (psycopg2 — most reliable)

```python
import psycopg2

conn = psycopg2.connect(
    "postgresql://postgres:<password>@db.<ref>.supabase.co:5432/postgres"
)
cur = conn.cursor()

# Count RLS policies
cur.execute("""
    SELECT tablename, policyname, cmd
    FROM pg_policies
    WHERE schemaname = 'public'
    ORDER BY tablename, cmd, policyname;
""")

policies = cur.fetchall()
print(f"RLS Policies: {len(policies)}")

# Verify RLS is ON for each table
cur.execute("""
    SELECT tablename, rowsecurity
    FROM pg_tables
    WHERE schemaname = 'public'
    ORDER BY tablename;
""")

for tablename, rls in cur.fetchall():
    status = "ON" if rls else "OFF — FIX REQUIRED"
    print(f"  {tablename}: RLS={status}")

conn.close()
```

**Install psycopg2**: `pip install psycopg2-binary` (use hermes venv)

## Method 2: Supabase SQL Editor (no tooling needed)

1. Open: `https://app.supabase.com/project/<ref>/sql/new`
2. Run:
```sql
SELECT tablename, policyname, cmd
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, cmd, policyname;
```
3. Verify count matches expected (e.g., 14 for Azdal)

## Method 3: anon-key REST query (limited)

The anon key CANNOT query `pg_policies` directly (it's in `pg_catalog`, not exposed via PostgREST). It CAN query each table to verify access:

```python
from supabase import create_client

client = create_client(url, anon_key)
tables = ['transactions', 'commitments', 'goals', 'integrity_scores', 'purchase_decisions']

for table in tables:
    try:
        r = client.table(table).select('*', count='exact').limit(0).execute()
        print(f"  {table}: accessible, {r.count} rows")
    except Exception as e:
        print(f"  {table}: BLOCKED — {e}")
```

A 200 response from each table means RLS allows anon SELECT. A 403/401 means RLS is blocking. Both outcomes are useful — the point is to verify that RLS is *active and behaving as expected*.
