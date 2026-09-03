---
name: skill-ecosystem-sync
description: Complete skill ecosystem update workflow — update all skills across 4 registries (npx/skills.sh, GitHub published, ClawHub/Hermes hub, profile swarm), audit modified bundled skills, install missing skills from external repos, and sync to every Flutter swarm profile plus default. This is the ONE skill to load before any "update skills" task.
version: 1.2.2
author: Sulaiman
tags: [skills, update, devops, npx, clawhub, hermes, profiles, sync, maintenance]
---

# Skill Ecosystem Sync

Complete systematic workflow for updating ALL skills across the ecosystem. This covers 4 registries and the full profile swarm. Counts in this skill are deliberately illustrative, never authoritative — always derive them live (`npx skills add <repo> -l`, `find ~/.hermes/skills -name SKILL.md | wc -l`) because published and installed counts drift. Load this skill whenever the user asks to update, check, or sync skills.

## Trigger

- "update skills" / "check for updates" / "sync skills"
- "publish skills" / "anything new in skills store"
- After any skill modification — this is the canonical sync procedure

---

## Phase 1: Bidirectional Sync — Our Published Skills

Our skills live at `jahfaliabdulrahman-dev/hermes-skills` on GitHub.

### Pre-step: ensure repo clone exists

`/tmp/` is cleared on reboot — the clone may be gone. If missing, clone fresh:

```bash
[ -d /tmp/hermes-skills ] || git clone https://github.com/jahfaliabdulrahman-dev/hermes-skills.git /tmp/hermes-skills
```

### Pull: GitHub → Local (download any remote changes)

```bash
cd /tmp/hermes-skills && git pull
```

### CRITICAL — Direction Check BEFORE local → repo rsync

The sync is NOT always local → repo. A local skill can regress (digest rewrite, restored old backup) below the repo's canonical version. **Before rsyncing, compare versions both ways:**

```bash
for skill in <published list>; do
  repo_ver=$(git -C /tmp/hermes-skills show HEAD:skills/$skill/SKILL.md 2>/dev/null | grep -m1 '^version' | awk '{print $2}')
  local_ver=$(find ~/.hermes/skills -maxdepth 3 -type d -name "$skill" -exec grep -m1 '^version' {}/SKILL.md \; 2>/dev/null | awk '{print $2}')
  echo "$skill: repo=$repo_ver local=$local_ver"
done
```

If `repo > local` (version higher, or repo has newer LL/pattern entries), **restore repo → local** instead:
`rsync -a /tmp/hermes-skills/skills/$skill/ ~/.hermes/skills/<category>/$skill/` — do NOT push the regression.

**Known failure mode (case study in [references/2026-08-08-sync-direction-regression.md](references/2026-08-08-sync-direction-regression.md)):** a local skill copy was once a digest while the repo held the canonical version with more accumulated patterns — a blind local→repo push would have deleted public content. Rule: if the repo version is higher or richer, restore repo → local; never push the regression. When versions tie, compare content (line counts, reference files) before choosing direction.

### Pre-push personal-path scan (SECURITY GATE)

Local edits often reintroduce hardcoded personal paths into public files. Before committing, scan:

```bash
grep -rn "/Users/<system-username>\|<your-home>" /tmp/hermes-skills/skills/ | grep -v "\.git"
```

Any hit = revert that file to HEAD (`git checkout -- <file>`) AND restore the generalized placeholder into the LOCAL copy too — otherwise the next sync re-dirties it. The recurring pattern: a personal absolute home path (`/Users/<name>/...`) or a concrete project path (`~/Projects/<concrete-project>/`) silently replaces the generalized placeholder (`<profile-home>`, `~/Projects/<project>/`) — the full case study with per-file detail is in [references/2026-08-08-sync-direction-regression.md](references/2026-08-08-sync-direction-regression.md).

### Generalization gate (authoring hygiene)

Before any sync that touches locally-authored skills, run:

```bash
python3 ~/.hermes/scripts/scan_case_hardening.py
```

Exit 1 = a local skill carries case-specific content (session dates, frozen
counts, personal paths, project bindings) in its MAIN SKILL.md. Migrate the
instance to an invariant (or move the case into `references/`) using the
procedure in the `skill-authoring-generalization` skill — never sync a skill
that fails this gate, or the contamination ships publicly.

### Push: Local → GitHub (upload our improvements)

**CRITICAL — If any locally-authored skills were modified locally, the repo must reflect it. Derive the set live: `ls ~/.hermes/skills/*/*/SKILL.md` cross-checked against the published-repo listing — never trust a memorized count.

```bash
cd /tmp/hermes-skills

# 1. Sync all published skills FROM local → repo.
# The published set is DERIVED from the repo itself (the repo listing is the source of truth —
# it has grown repeatedly and any hardcoded list goes stale within one cycle, PITFALL 11):
for skill in $(git -C /tmp/hermes-skills ls-tree --name-only HEAD:skills/); do
  
  # Find actual path (skills may be in subdirectories)
  src=$(find -L ~/.hermes/skills -maxdepth 4 -type d -name "$skill" -exec test -f {}/SKILL.md \; -print | head -1)  # -L: follow symlinks (PITFALL 8)
  if [ -n "$src" ] && [ -f "$src/SKILL.md" ]; then
    rsync -a "$src/" /tmp/hermes-skills/skills/$skill/
  fi
done

# 2. Check if any changes exist
git status

# 3. If changes → commit + push
if ! git diff --quiet || ! git diff --cached --quiet; then
  git add -A
  git commit -m "🔄 Sync: local improvements to published skills"
  git push
fi
```

**PITFALL:** This is BIDIRECTIONAL. Always pull FIRST to avoid conflicts. Then push our improvements.

### Verify

```bash
cd /tmp/hermes-skills && git log --oneline -3
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

**Key: user-modified bundled skills.** The skills below carry local customizations (derive the current set live — the list drifts as new bundled skills get customized):
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

See `references/2026-07-18-skill-audit-findings.md` for the full 8-skill audit results and the google-workspace regression analysis.

---

## Phase 4: Profile Swarm Sync

After updating default profile, sync ALL Flutter swarm profiles (derive the live list: `ls ~/.hermes/profiles/ | grep -v default`):

```bash
KEY_SKILLS="flutter-android-build-system flutter-design-anti-patterns \
  flutter-isar-clean-arch-setup flutter-lessons-patterns flutter-patterns \
  flutter-soul-stewardship github-project-audit repo-front-door \
  specification-writing supabase-fullstack skill-ecosystem-sync \
  find-docs find-skills officecli"

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

Verify: `npx skills add jahfaliabdulrahman-dev/hermes-skills -l` and confirm the listed count matches the local published set derived above (the count drifts — PITFALL 11).

### To ClawHub

**CLI publishing is NOT yet supported.** All skills must be submitted manually:

🔗 https://clawhub.ai/submit

Before submitting, run security scan:
```bash
hermes skills publish <path> --to clawhub
```

Most skills pass with SAFE verdict; a minority get CAUTION (historically for shell/Python scripts and long code blocks). Historically flagged:
- `flutter-android-build-system` (5 findings) — likely shell scripts flagged
- `repo-front-door` (5 findings) — likely Python scripts flagged
- `flutter-patterns` (1 finding) — minor

---

## Summary: Total Skills Ecosystem

| Registry | Count | Update Command |
|----------|-------|---------------|
| Our published (GitHub) | 11 | `git pull && rsync` (bidirectional) |
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
- **PITFALL 7: Cross-project lesson fragmentation.** LL-009/010/011 were discovered in Azdal's `app-spec/00_lessons_learned.md` but never promoted to the central `flutter-lessons-patterns` skill — Claude was saving lessons to project-internal files instead of the cross-project repository. During every sync cycle, check ALL active project `app-spec/00_lessons_learned.md` files (Azdal, Hermex, CarSah) for orphaned LL/DEC entries not yet in the central skill.
- **PITFALL 8: `find -type d` misses symlinked skills.** `flutter-design-anti-patterns` and `supabase-fullstack` live as symlinks → `~/.agents/skills/<name>`. Use `find -L` or `ls -la ~/.hermes/skills/` to spot them; rsync from the symlink TARGET.
- **PITFALL 9: `hermes skills check` reports stale `update_available`.** After `hermes skills update <name>` the flag can persist even when content is current. Verify against the official source: `curl -sL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/optional-skills/<path>/SKILL.md | diff - <local>` (path from `hermes skills inspect <name>` or the index cache). Zero diff = flag is stale, ignore.
- **PITFALL 10: nested skills block the hub updater.** `adversarial-ux-test` sits under `dogfood/` which is BOTH a skill dir (has SKILL.md) and a category — the installer refuses ("Refusing to install into 'dogfood'"). Apply the update manually: fetch SKILL.md from the raw GitHub path above and `cp` it over the local file. Verify with diff.
- **PITFALL 11: published count drifts.** The repo's skill count has grown repeatedly (e.g. when `swarm-executive-controller` joined it became stale within one cycle). Re-run `npx skills add jahfaliabdulrahman-dev/hermes-skills -l` to list; never trust a memorized count.
- **PITFALL 12: marketing repo count drifts.** The external marketing repo's count has repeatedly grown while local installs lagged behind (several skills were once discovered missing locally only during a sync). Install any that `comm -23` reports missing; some local dirs are RENAMED (ab-testing→ab-test-setup, cro→form-cro/page-cro/popup-cro, launch→launch-strategy...) — compare by frontmatter `name:` field, not directory name.

---

## Session Reference

The founding session record — the full marathon log (publication, audits, installs, the google-workspace stock-restore decision, and the v1.1.0 bidirectional-sync addition) — lives in [references/2026-07-18-skill-audit-findings.md](references/2026-07-18-skill-audit-findings.md). Case history belongs there, not here; keep this file general.
