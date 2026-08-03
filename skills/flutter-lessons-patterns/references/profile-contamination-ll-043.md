# LL-043: Cross-Project Profile Memory Contamination

> Added: 2026-07-20. Source: Azdal Phase 0 Foundation EPIC. 8/10 profiles contaminated.
> Severity: CRITICAL — silently corrupts all downstream routing.

## The Problem

Flutter swarm profiles are **cross-project** — the same profile serves CarSah, Azdal, Hermex, and future projects. When project-specific paths (e.g., `Azdal: /Users/.../Azdal`) are stored in profile MEMORY.md, the profile is poisoned.

### Incident chain

1. Lead Architect MEMORY.md had `Azdal: ~/Azdal/` (stale path — didn't exist)
2. EPIC delegated without explicit `# TARGET PROJECT:`
3. Lead Architect tried stale path → failed → fell back to Hermex Android
4. Searched Hermex for Azdal components → found nothing → flagged "cross-project contamination"
5. The contamination was the profile's own memory, not the EPIC

## The Fix

**Delete, don't correct.** Never update a stale path. DELETE the entire entry. Add guard:
```
⚠️ NO PROJECT PATHS — Cross-project profile. Project context from EPIC body, never from profile memory.
```

**Source of truth:** `# TARGET PROJECT: /absolute/path` in EPIC body. MCP bridge enforces this — `lead_delegate` requires `project_path`, refuses if path doesn't exist on disk.

## Prevention

```bash
# Audit all profiles for contamination
grep -rn "Projects/\|/Azdal\|/CarSah\|/hermex" ~/.hermes/profiles/flutter-*/memories/MEMORY.md
```
