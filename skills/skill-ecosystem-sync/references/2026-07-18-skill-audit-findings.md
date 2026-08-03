# 2026-07-18: Skill Audit Session Findings

Complete audit of 8 user-modified bundled Hermes skills. Results and resolutions.

## google-workspace — CRITICAL (RESTORED TO STOCK)

This was the ONLY skill where our modifications were worse than the original.

### What we broke:

1. **API scopes downgraded**: `drive` → `drive.readonly`, `documents` → `documents.readonly`
   - Impact: Could no longer create/upload/delete Drive files or create/edit Docs
   - Root cause: Overzealous "least privilege" without understanding workflow needs

2. **Command examples deleted**: 16 useful reference commands removed
   - Drive: upload, download, get, create-folder, share, delete
   - Docs: create, append
   - Sheets: create
   - Impact: Agent had no reference for common operations

3. **Safety rules weakened**: Original rule covered "email + calendar + drive + docs + sheets"
   - Our version only mentioned "email + calendar events"
   - Impact: Could accidentally modify/delete Drive files without confirmation

4. **Header case fix was misguided**: We changed `_headers_dict` to remove `.lower()`
   - Stock uses case-insensitive lookup: `.lower()` on all header names
   - Our version was case-sensitive: would break if API returned different casing
   - Stock approach is MORE robust

### Resolution:
```bash
echo "y" | hermes skills reset google-workspace --restore
```

### Lesson:
Not all local modifications are improvements. When a skill has more deletions than additions (-558 vs +63), red-flag it immediately. The stock bundled skills are written by domain experts — audit thoroughly before keeping modifications.

---

## All 8 Modified Skills — Audit Summary

| Skill | +Added | -Deleted | Verdict | Action |
|-------|--------|----------|---------|--------|
| requesting-code-review | +40 | -1 | ✅ GOOD | Keep — added Parallel 3-Agent Simplify pattern |
| powerpoint | +37 | -5 | ✅ GOOD | Keep — added corporate template extraction + structural QA |
| test-driven-development | +39 | -23 | ✅ GOOD | Keep — added Tracer Bullets + anti-pattern warning |
| design-md | +141 | -14 | ✅ GOOD | Keep — enhanced description + pitfalls |
| obsidian | +95 | -33 | ✅ GOOD | Keep — simplified vault path handling |
| dogfood | +1 | 0 | ✅ GOOD | Keep — trivial change |
| hermes-agent | +363 | -529 | ✅ GOOD | Keep — added Hermes Workspace documentation |
| google-workspace | +63 | -558 | 🔴 BAD | **RESTORED TO STOCK** |

### Audit decision framework:

- **Deletions > Additions?** → RED FLAG. Check if useful content was removed.
- **API scopes changed?** → RED FLAG. Verify with user before changing permissions.
- **Safety rules weakened?** → AUTO-REJECT. Never reduce security.
- **Pure additions with no deletions?** → Likely good.
- **Additions with minor cleanup deletions?** → Usually fine.
