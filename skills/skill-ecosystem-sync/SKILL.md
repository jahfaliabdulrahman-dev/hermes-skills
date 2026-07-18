---
name: skill-ecosystem-sync
description: Complete skill ecosystem update workflow — update all skills across 4 registries (npx/skills.sh, GitHub published, ClawHub/Hermes hub, profile swarm), audit modified bundled skills, install missing skills from external repos, and sync to all 10 Flutter swarm profiles. This is the ONE skill to load before any "update skills" task. Captured from the 2026-07-18 marathon session.
version: 1.0.0
author: Sulaiman
tags: [skills, update, devops, npx, clawhub, hermes, profiles, sync, maintenance]
---

# Skill Ecosystem Sync

Complete systematic workflow for updating ALL skills across the ecosystem. This covers 4 registries and 11 profiles. Load this skill whenever the user asks to update, check, or sync skills.

## Trigger

- "update skills" / "check for updates" / "sync skills"
- "publish skills" / "anything new in skills store"
- After any skill modification — this is the canonical sync procedure

---

## Phase 1: Update Published Repo Skills

Our skills live at `jahfaliabdulrahman-dev/hermes-skills` on GitHub.

```bash
# 1. Pull latest from the local repo clone
cd /tmp/hermes-skills && git pull

# 2. Sync ALL 10 published skills from repo → local store
for skill in flutter-android-build-system flutter-design-anti-patterns \
  flutter-isar-clean-arch-setup flutter-lessons-patterns flutter-patterns \
  flutter-soul-stewardship github-project-audit repo-front-door \
  specification-writing supabase-fullstack; do
  rsync -a --delete /tmp/hermes-skills/skills/$skill/ ~/.hermes/skills/$skill/
done
```

**PITFALL:** Some skills are in subdirectories (`flutter/`, `android/`, `devops/`, `research/`, `software-development/`). The rsync may place them at a different path than expected. Always verify:

```bash
for skill in ...; do
  find ~/.hermes/skills -maxdepth 3 -type d -name "$skill" | head -1
done
```

---

## Phase 2: Update npx/skills.sh External Skills

Skills installed from external repos via `npx skills`:

```bash
# 2a. Update all globally installed npx skills
npx skills update -g -y

# 2b. Check for NEW skills from known repos
# flutter/skills (was 10, now 22 — gained 12 Dart skills)
npx skills add flutter/skills -l 2>&1 | grep -E '^\│\s+[a-z]' | sed 's/│//g' | awk '{print $1}' | sort

# coreyhaines31/marketingskills (was 37, now 48 — gained 11)
npx skills add coreyhaines31/marketingskills -l 2>&1 | grep -E '^\│\s+[a-z]' | sed 's/│//g' | awk '{print $1}' | sort

# 2c. Install missing skills
npx skills add flutter/skills -g -y --skill '*'        # all 22
npx skills add coreyhaines31/marketingskills -g -y --skill '*'  # all 48
```

**Sources to check:**
| Source | Command | Purpose |
|--------|---------|---------|
| `flutter/skills` | `npx skills add flutter/skills -l` | Dart + Flutter official skills |
| `coreyhaines31/marketingskills` | `npx skills add coreyhaines31/marketingskills -l` | Marketing skills |
| `vercel-labs/agent-skills` | Already have find-skills | CLI skills |
| `upstash/context7` | Already have find-docs | Documentation |

---

## Phase 3: ClawHub / Hermes Hub Skills

Skills managed by `hermes skills` (separate from npx):

```bash
# 3a. Check for ClawHub updates
hermes skills check

# 3b. Apply available updates
hermes skills update

# 3c. Check user-modified bundled skills (9 total)
hermes skills list-modified
```

**Key: user-modified bundled skills.** These 9 skills have local customizations:
- `design-md`, `dogfood`, `google-workspace`, `hermes-agent`, `obsidian`
- `powerpoint`, `requesting-code-review`, `systematic-debugging`, `test-driven-development`

When `hermes skills check` finds an update, it preserves our modifications. BUT we must audit quality — ensure our changes are improvements, not regressions.

### Audit workflow for each modified skill:

```bash
hermes skills diff <name>

# Analyze:
# - Are deletions removing useful content? (google-workspace: YES - bad)
# - Are additions genuinely improving? (requesting-code-review: YES - good)
# - Is stock version superior? → reset to stock
# - Are our changes better? → keep

# If stock is better:
echo "y" | hermes skills reset <name> --restore
```

---

## Phase 4: Profile Swarm Sync

After updating default profile, sync ALL 10 Flutter swarm profiles:

```bash
KEY_SKILLS="flutter-android-build-system flutter-design-anti-patterns \
  flutter-isar-clean-arch-setup flutter-lessons-patterns flutter-patterns \
  flutter-soul-stewardship github-project-audit repo-front-door \
  specification-writing supabase-fullstack find-docs find-skills officecli"

for profile_dir in ~/.hermes/profiles/flutter-*/; do
  for skill in $KEY_SKILLS; do
    src="$HOME/.hermes/skills/$skill"
    target="$profile_dir/skills/$skill"
    if [ -d "$src" ] && [ ! -L "$target" ] && [ ! -d "$target" ]; then
      ln -s "$src" "$target"
    fi
  done
done
```

**Also sync any NEW skills installed from external repos** to all profiles (same pattern).

### Verification:

```bash
# Verify key skills present
for profile_dir in ~/.hermes/profiles/flutter-*/; do
  profile=$(basename "$profile_dir")
  missing=""
  for skill in $KEY_SKILLS; do
    [ ! -L "$profile_dir/skills/$skill" ] && [ ! -d "$profile_dir/skills/$skill" ] && missing="$missing $skill"
  done
  [ -z "$missing" ] && echo "✅ $profile" || echo "❌ $profile MISSING:$missing"
done
```

---

## Phase 5: Publishing

### To skills.sh (via npx)

The repo is auto-discovered when public and properly formatted:
- `skills/` directory with `SKILL.md` files
- `clawhub-skills` or `agent-skills` GitHub topics

Verify: `npx skills add jahfaliabdulrahman-dev/hermes-skills -l` should show all 10 skills.

### To ClawHub

**CLI publishing is NOT yet supported.** All skills must be submitted manually:

🔗 https://clawhub.ai/submit

Before submitting, run security scan:
```bash
hermes skills publish <path> --to clawhub
```

7/10 skills pass with SAFE verdict. 3/10 get CAUTION:
- `flutter-android-build-system` (5 findings) — likely shell scripts flagged
- `repo-front-door` (5 findings) — likely Python scripts flagged
- `flutter-patterns` (1 finding) — minor

---

## Summary: Total Skills Ecosystem

| Registry | Count | Update Command |
|----------|-------|---------------|
| Our published (GitHub) | 10 | `git pull && rsync` |
| npx external (agents/) | ~50 | `npx skills update -g -y` |
| ClawHub/Hermes hub | ~8 | `hermes skills check && hermes skills update` |
| Hermes built-in/bundled | ~40 | `hermes update` |
| Total default profile | ~89 | — |
| Each swarm profile | ~89 | symlinked from default |

---

## Pitfalls

- **PITFALL 1: npx vs hermes skills are separate.** `npx skills update` updates skills.sh-installed skills. `hermes skills check` updates ClawHub/bundled skills. Run BOTH.
- **PITFALL 2: flutter/skills grew from 10 to 22.** Always check `-l` (list) flag before assuming count.
- **PITFALL 3: google-workspace modifications were BAD.** Our edits removed API scopes, command examples, and safety rules. The stock is superior. Don't blindly keep all modifications.
- **PITFALL 4: Path inconsistency.** Skills may be at `~/.hermes/skills/<name>/` OR `~/.hermes/skills/<category>/<name>/`. Always `find` before publishing.
- **PITFALL 5: PromptScript never supports global installs.** Ignore those errors — they're expected.
- **PITFALL 6: specification-writing said 18 files but projects use 22+.** Updated to v2.0 (27+ files across 22 slots). Ensure this stays current as projects evolve.

---

## Session Reference

This skill was created from the 2026-07-18 marathon session where we:
1. Published 10 skills to skills.sh
2. Updated specification-writing from 18 → 22 slots
3. Installed 12 Dart skills from flutter/skills
4. Installed 11 marketing skills from coreyhaines31
5. Fixed google-workspace regression (restored stock)
6. Audited all 8 user-modified bundled skills
7. Synced skills to all 10 swarm profiles + default
8. Attempted ClawHub publishing (CLI not supported)
