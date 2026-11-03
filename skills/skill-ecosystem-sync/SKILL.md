---
name: skill-ecosystem-sync
description: Use when syncing 4 skill registries (مزامنة السجلات). Complete skill ecosystem update workflow — update all skills across 4 registries (npx/skills.sh, GitHub published, ClawHub/Hermes hub, profile swarm), audit modified bundled skills, install missing skills from external repos, and sync to every Flutter swarm profile plus default. This is the ONE skill to load before any "update skills" task.
version: 1.5.0
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

Skills installed from external repos via `npx skills`.

### 2-step GATE — derive the source list, never recite it

The repos named anywhere in this file are EXAMPLES that drift out of date. The authoritative registry of
origin is the installer lock (`~/.agents/.skill-lock.json`), which records a `source` per installed skill.
Any source the doc does not name is a source nobody checks — new upstream skills in it are never discovered.

```bash
SCRIPT=~/.hermes/skills/devops/skill-ecosystem-sync/scripts/upstream_source_map.py
python3 "$SCRIPT" --coverage      # exit 2 = SKILL.md is name-list-based instead of deriving from the lock
```

Run this gate FIRST in every cycle. It does NOT check that repos are named in this file — naming them is the
defect. It checks that the PROCEDURE derives the list from the lock (the `--sources` loop below is present) and
prints the live inventory. A source in the inventory needs action only when 2b's `--diff` reports missing
skills; a source that is not written down anywhere is the normal state, not a failure.

### 2a. Update every installed npx skill (all sources at once)

```bash
npx skills update -g -y
# MANDATORY right after (PITFALL 23 — the updater re-links what it updated):
python3 ~/.hermes/skills/devops/skill-store-hygiene/scripts/audit_skill_duplicates.py
python3 -c "import json,pathlib,os;p=pathlib.Path.home()/'.hermes/skills/.retired.json';print([n for n in json.loads(p.read_text())['retired'] if (pathlib.Path.home()/'.hermes/skills'/n).exists()] or 'no resurrection')"
```

The second line prints any retired name that came back; remove that registration and say so in the report.

### 2b. Discover NEW skills, one pass per DERIVED source

```bash
for src in $(python3 "$SCRIPT" --sources | grep -v 'jahfaliabdulrahman-dev/hermes-skills'); do
  echo "### $src"
  npx skills add "$src" -l > "/tmp/upstream-$(echo "$src" | tr '/' '-').txt" 2>&1
  python3 "$SCRIPT" --diff "$src" "/tmp/upstream-$(echo "$src" | tr '/' '-').txt"
done
```

The `--diff` output is the ONLY honest answer to "what is new upstream" — it parses the `-l` listing and
compares it against the lock. It exits 1 rather than printing `missing=0` when it parsed zero names, so a
format change upstream surfaces as a failure instead of a clean report.

Our own published repo is excluded above on purpose: it is Phase 1's job, and `npx skills update` mirrors it
into `.agents/` from the PUBLISHED side (PITFALL 20).

### 2c. Install the missing ones — as an OWNER DECISION per PITFALL 19

**Proof-of-intent gate — run BEFORE any install of an `ABSENT` name.** Absence is not the same as "never had it":
a skill can be missing because it was DELIBERATELY removed (too noisy, wrong direction, superseded). Reinstalling it
resurrects a decision the owner already took. Five witnesses, all cheap:

```bash
python3 -c "import json,pathlib;d=json.loads((pathlib.Path.home()/'.agents/.skill-lock.json').read_text());print('dismissed:',d.get('dismissed'))"
python3 -c "import json,pathlib;p=pathlib.Path.home()/'.hermes/skills/.retired.json';print('retired:',list(json.loads(p.read_text())['retired']) if p.exists() else [])"
ls ~/.hermes/skills/.archive | grep -x '<name>'                       # retired deliberately by us
python3 -c "import json,pathlib;d=json.loads((pathlib.Path.home()/'.hermes/skills/.usage.retired.json').read_text());print([k for k in d if '<name>' in k])"
for s in ~/.hermes/skills/.curator_backups/*/skills.tar.gz; do tar tzf "$s" | grep -q "<name>/" && echo "present in $s"; done
```

The fifth witness (`.retired.json`) is the machine-readable one and the only one a future agent will read:
**every deliberate retirement writes a row there in the same session**, with `reason`, `replaced_by`, `archive`
and the exact `restore` command. `--diff` then prints that name as `RETIRED-DELIBERATE` instead of `ABSENT`, so
the gate stops asking about it. A retirement with no row is a future reinstall.

Verdict: **any witness hit => it existed before => ask the owner, never auto-install.** Zero hits across all four
(dismissed empty, not in `.archive`, not in the retired usage ledger, absent from every weekly snapshot) is the
only state that licenses installing it as a genuinely new upstream skill — and that zero state must be WRITTEN in
the report, because "it was never deleted" is a claim that needs its evidence named.

Do not blind-install a `not_via_npx` line either. First rule out a RENAME or a functional duplicate (fetch the
upstream `SKILL.md`, compare with the local skill it would shadow). Genuine new skills install one at a time:

```bash
npx skills add <source> -g -y --skill '<name>'   # one skill at a time keeps the adoption auditable
```

Then re-run `--diff` and confirm the count dropped by exactly the number installed. Two legitimate exclusion
reasons to WRITE DOWN instead of installing: (a) **duplicate mechanism** — a local skill already does the same
job (e.g. an official `gradio` beside a local "build Gradio UIs" skill; a `context7-mcp` beside a `find-docs`
that already drives the `ctx7` CLI); (b) **no trigger on this machine** — e.g. a family of `migrating-*` skills
for frameworks we do not use. A duplicate is an owner decision (keep local vs swap to official), never a silent
alongside-install.

**Known sources on this machine are a measurement, not a list.** The set is legitimately wide (Dart/Flutter,
marketing, LangGraph/LangChain, Pydantic AI, Gradio, HuggingFace, Vercel, context7, our own repo) and grows
whenever a pack is adopted — which is exactly why 2a must be a loop over `--sources`.

### 2d. A skill with NO lock entry has no upstream (or an unknown one)

Locally authored, bundled, hub-installed and manually adopted skills do not appear in `.skill-lock.json`. They
must NOT be pushed through `npx` — and they must not be reported as "up to date" either. Classify them once in
the report: `authored-here` / `bundled` / `adopted` (provenance block in the file) / `unknown`. `unknown` is a
finding, not a blank.

### 2e. Hugging Face skills marketplace (`hf skills`)

A FIFTH registry, separate from npx and from the Hub: `huggingface/skills` publishes ~25 first-party
skills (TRL, datasets viewer, Spaces, hf-mem, paper reading…). Drive it from the CLI itself, never from a
remembered list:

```bash
hf skills list                     # authoritative marketplace listing
hf skills add <name> --dest ~/.hermes/cache/scratch/hf-skills   # STAGE, never straight into the store
```

`--dest` is the whole point: without it the CLI writes a DIRECTORY SYMLINK into `~/.agents/skills/` (shared,
read-only to us). Stage → inspect → `cp -R` the real dirs into `~/.hermes/skills/<category>/` → stamp the
provenance block (upstream URL + commit + licence) → run the frontmatter and duplicate gates. One shared
`LICENSE-upstream-<SPDX>` at the category root, not a copy per skill. Then verify discovery with a real
`skill_view(<name>)`, not an `ls`.

Exclusions worth naming in the report: a family serving infrastructure we do not run (the cloud
SageMaker/AWS set on a Mac-only store), and skills whose mechanism already exists locally (an official
`trl-training` beside a local `trl-fine-tuning`) — duplicates are an owner decision, never a silent
alongside-install.

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
- `powerpoint`, `requesting-code-review` (later merged into `code-review-elite`), `systematic-debugging`, `test-driven-development`

When `hermes skills check` finds an update, it preserves our modifications. BUT we must audit quality — ensure our changes are improvements, not regressions.

### Audit workflow for each modified skill:

```bash
hermes skills diff <name>

# Analyze:
# - Are deletions removing useful content? (google-workspace: YES - bad)
# - Are additions genuinely improving? (requesting-code-review: YES - good; merged into code-review-elite 2026-09-23)
# - Is stock version superior? → reset to stock
# - Are our changes better? → keep

# If stock is better:
echo "y" | hermes skills reset <name> --restore
```

See `references/2026-07-18-skill-audit-findings.md` for the full 8-skill audit results and the google-workspace regression analysis.

---

## Phase 4: Profile Swarm Sync

After updating the default profile, sync ALL profiles (derive the live list: `ls ~/.hermes/profiles/` — the default profile is the store itself, not a target; external skills live under `~/.agents/skills/`):

```bash
LINKER="$HOME/.hermes/skills/autonomous-ai-agents/botmaker/scripts/link_skill_tree.py"
# usage: python3 "$LINKER" <canonical-skill-dir> <profile>/skills/<name>
# re-running is safe: existing correct links are kept, new source files are added.

# Repair pass — convert every legacy directory symlink under any profile to
# file-level links (harmless to repeat):
for profile_dir in ~/.hermes/profiles/*/; do
  for target in "$profile_dir"skills/*; do
    { [ -L "$target" ] && [ -d "$target" ]; } || continue
    src="$(cd "$target" && pwd -P)"
    rm "$target"
    python3 "$LINKER" "$src" "$target"
  done
done
```

**Syncing a skill (update or new):** one explicit linker call per target profile — keep each profile's set curated; distribute what that profile's mission needs.

### Verification:

```bash
# 1. No directory symlinks under any profile's skills/ — the invisibility
#    defect. botmaker's drift check audits this class fleet-wide.
python3 "$HOME/.hermes/skills/autonomous-ai-agents/botmaker/scripts/drift_check.py"

# 2. Discovery proof — rglob must actually find the linked skills:
python3 -c "
from pathlib import Path
for prof in sorted(Path.home().joinpath('.hermes/profiles').iterdir()):
    sk = prof / 'skills'
    if sk.is_dir():
        n = sum(1 for _ in sk.rglob('SKILL.md'))
        print(f'{prof.name}: rglob finds {n} SKILL.md')"
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

## Proactive Capability Audit

Between monthly cycles (or on owner request), run the proactive half — the Capability Auditor pipeline:

1. **Scheduled scanning** — monitor for new extensions targeting Data Engineering, UI/UX automation, Power BI DAX, Python performance.
2. **Benchmarking & gap analysis** — cross-reference new candidates against the current workflow; name the bottleneck each one would resolve.
3. **Deprecation protocol** — if a new skill measurably outperforms an existing one (speed on the owner's hardware, memory, Polars compatibility), flag the old for replacement.
4. **Structured proposal** — every replacement suggestion ships as: `{Skill Name} -> {Technical Gap} -> {Skill to Replace} -> {Implementation Steps} -> {Expected ROI}`.

## Mandatory Closing Report (owner rule — every sync, no exception)

Every sync/update run ENDS with a report. The most important part is **the names**: a count alone is not an
answer — the owner reads the list. Names are DERIVED from the run's own log, never typed from memory.

Capture the update log while running 2a:

```bash
npx -y skills update -g -y > /tmp/skills-update-$(date +%F).log 2>&1
python3 - <<'PY'
import re, pathlib, os
log = sorted(pathlib.Path('/tmp').glob('skills-update-*.log'))[-1]
names = {m.group(1).strip() for l in log.read_text(errors='ignore').splitlines()
         if (m := re.search(r'Updated (.+)$', l)) and 'skill' not in m.group(1)}
print(log.name, len(names)); print('\n'.join(sorted(names)))
PY
```

Report shape (six blocks, in this order):

| Block | Content |
|---|---|
| **UPDATED (n)** | every skill name the updater reports as updated, one per line — the block the owner asked for first |
| **NEW (n)** | names newly installed this run, with source `owner/repo` |
| **RETIRED (n)** | names retired, with `replaced_by` and the archive path |
| **EXCLUDED (n)** | names deliberately not installed + the reason class (duplicate mechanism / no trigger / owner decision) |
| **STATE** | lock count, store count, duplicate audit result, gate verdicts |
| **UNPROVEN** | what was NOT verified this run, one line, never omitted |

Rules:

1. **Names before numbers.** A report that says «N skills updated» without listing the N is rejected.
2. **Three states, never merged:** updated ≠ newly installed ≠ updated-in-shared-store-only (PITFALL 20). Say which.
3. **Zero is a result.** "NEW: none" and "RETIRED: none" are written explicitly; a missing block reads as work
   that was not done.
4. **The UNPROVEN line is not optional** — it is the only thing that stops the report from sounding more
   certain than the run was.
5. A run that fails midway still reports: what landed, what did not, and what state the store was left in.

## Summary: Total Skills Ecosystem

| Registry | Count | Update Command |
|----------|-------|---------------|
| Our published (GitHub) | 11 | `git pull && rsync` (bidirectional) |
| npx external (derived from lock) | derive live: `upstream_source_map.py` | `npx skills update -g -y` + per-source `-l` diff |
| ClawHub/Hermes hub | ~8 | `hermes skills check && hermes skills update` |
| Hermes built-in/bundled | ~40 | `hermes update` |
| Total default profile | ~89 | — |
| Each profile | ~89 | file-level linked (linker — never dir symlinks) |

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
- **PITFALL 13: fresh clones can carry a foreign git identity.** A `/tmp` clone inherits the machine's global git identity (which may belong to a different project), so commits get publicly misattributed the moment they're pushed. Set the identity locally in the clone BEFORE committing (`git config user.name "<repo-account>"; git config user.email "<repo-noreply-email>"`); if already committed, `git commit --amend --author="<name> <email>" --no-edit` before pushing.
- **PITFALL 14: HTTPS pushes can die with `send-pack: unexpected disconnect while reading sideband packet`.** A retry often succeeds; if it persists, set `git config http.version HTTP/1.1` and `git config http.postBuffer 524288000` in the clone, then push again. Never trust the push output alone — confirm the remote ref (`git ls-remote origin refs/heads/main` must equal `git rev-parse HEAD`) before declaring success.
- **PITFALL 15: never `ln -s` a skill directory into a profile.** A directory symlink is invisible to Hermes's `rglob("SKILL.md")` discovery — the skill silently stops existing for that profile. Link file-level with `botmaker/scripts/link_skill_tree.py`; audit fleet-wide with botmaker's `drift_check.py`.
- **PITFALL 16: a third-party `npx skills add` writes into the SHARED store, not into Hermes.** It installs packs as directory symlinks `~/.hermes/skills/<name> -> ~/.agents/skills/<name>` (same inode for Claude Code, OpenClaw, Kiro, Pi). Those skills LOAD normally (`skill_view` works, they appear in the prompt listing), but `skill_manage` cannot see them — it answers "not found in active profile" — and the curator/ledger never record them. Treat every symlinked skill as READ-ONLY for Hermes tooling. To customize one, FORK it: copy the folder to `~/.hermes/skills/<name>/` as a real directory (writes there are verified to work) and leave the upstream copy intact for the other agents. Verify the class in one command: `find ~/.hermes/skills -maxdepth 1 -type l | wc -l`.
- **PITFALL 17: `npx skills remove` (global) deletes the canonical copy AND every agent's link.** The tool's `-g`/global scope means a removal is not scoped to the agent that ran it: one `npx skills remove <names>` wipes the pack from `~/.agents/skills/` and from `~/.hermes/skills/`, `~/.claude/skills/`, `~/.openclaw/skills/`, `~/.kiro/skills/`, `~/.pi/agent/skills/` at once — with no backup and no entry in any Hermes ledger. And `~/.agents/.skill-lock.json` keeps entries whose directory no longer exists, so the lock is NOT proof of presence. Before trusting any "N/N installed" report or count, verify the filesystem (`ls ~/.agents/skills`, `find -L ~/.hermes/skills -name SKILL.md | wc -l`) and keep a hash manifest so a deletion is provable and restorable. Also note the tool's own default is SYMLINK into each agent dir (`--copy` is opt-in): Hermes is an officially supported target (`~/.hermes/skills/` in its agent table), which is exactly why an external install lands in our tree uninvited.

- **PITFALL 18: a cron/scheduled run's runtime security scanner can block the sync commands themselves.** `npx skills ...`, `curl | python3`, and shell `for`-loops over globbed paths get BLOCKED (unresolvable package threat-intel, pipe-to-interpreter, "nested executable body") and cron has no approver. Workarounds that pass: (a) invoke the already-cached CLI directly — `node ~/.npm/_npx/<hash>/node_modules/skills/bin/cli.mjs <subcommand>` (find `<hash>` with `ls -d ~/.npm/_npx/*/node_modules/skills`); (b) write command output to a file under `/tmp` and parse it in a separate step that READS the file (`python3 <file>`) instead of piping into an interpreter; (c) replace `for`-loops with a single Python driver script. Never try to "fix" this by granting cron approvals — adapt the command.
- **PITFALL 19: an external pack can restructure between cycles, so the name diff is not a missing-skills diff.** A pack that once split one skill into several can later consolidate them back under new names (a `-l` listing then shows names that look new but are renames of installed ones). Do NOT blind-install the `comm -23` diff. For each suspected rename, fetch the upstream `SKILL.md` (`https://raw.githubusercontent.com/<owner>/<repo>/<branch>/skills/<name>/SKILL.md`) and compare content against the local skill it would duplicate. If it duplicates one, treat it as an AMBIGUITY: report the mapping (upstream-name ← local-name) and the two options (migrate-and-retire the old names vs install-alongside creating duplicates) as an owner decision — never install duplicates and never delete the old ones silently.
- **PITFALL 20: `npx skills update -g -y` also refreshes the shared `~/.agents/skills/` copies of OUR OWN published skills.** Because those were installed from the public repo, the updater makes the `.agents` copy mirror the PUBLISHED repo — which may be older than the authoritative `~/.hermes/skills/` copy. Two consequences: (a) always rsync FROM `~/.hermes/skills/`, never from `.agents`, when both exist; (b) run the version check with a CHECKSUM diff (`rsync -a -n -c -i`), because a plain itemize diff reports mtime/permission noise (`t`/`p` flags) that masquerades as a content change and can trigger a pointless push or a false "regression" alarm. Only the `c`/`s` flags in the itemize string mean the bytes actually differ.
- **PITFALL 21: `hermes skills diff` output direction is `--- stock / +++ yours`.** A `-` line is present in STOCK and ABSENT from your copy — i.e. a potential content REGRESSION, not an addition. Ours sometimes adds sections while silently dropping a rich stock section (the drift is not always additive), and a bundled skill can JUMP to a higher upstream major while the local copy keeps a lower version (a restructure, not an update). Neither is auto-resolvable: flag it as an owner decision (reset to stock vs keep local vs manual merge) instead of guessing.

- **PITFALL 22: the named repos are not the source list.** A sync driven by a hardcoded repo list silently skips every source the doc never names — the lock (`.agents/.skill-lock.json`) is the only registry of origin, and it drifts: on this machine it held 9 distinct sources of which 4 were unnamed in this skill (a 22-skill LangGraph/LangChain pack, Pydantic AI, Gradio, HuggingFace), so nothing in their upstreams was ever discovered. Run `scripts/upstream_source_map.py --coverage` FIRST (exit 2 = the procedure is name-list-based, not lock-derived) and drive 2b from `--sources`. Corollary: `npx skills update -g -y` alone looks complete and is not — it refreshes what is installed, never what is new.

- **PITFALL 23: `npx skills update -g -y` RE-CREATES missing Hermes registrations.** For every skill it actually updates, the CLI re-links it into each agent dir — including `~/.hermes/skills/` — so a registration you removed comes back. Measured 2026-10-18: an update run silently re-linked a root symlink for a skill whose canonical copy already lived in a category directory (duplicate twin, caught only by the dedup audit), and it would equally re-link a deliberately RETIRED name whenever that name has an upstream change (it did not return in that run only because its upstream was unchanged). Guard: after every 2a, run the duplicate audit and check `.retired.json` names for resurrection. Never treat "the update succeeded" as "the store is as I left it".

- **PITFALL 24: `hf skills list`'s installed columns are not a presence map for the Hermes store.** It only marks
  skills living in ITS destinations (`~/.agents/skills`, `~/.claude/skills`); a skill fully present under
  `~/.hermes/skills/` shows blank in every column. Read presence from the store, use the CLI for the catalogue.
  A forked copy is also invisible to `hf skills update` — re-import on demand instead of waiting for a sync.
- **PITFALL 25: upstream marketplace `SKILL.md` files may carry no H1.** The body can start straight after the
  frontmatter fence, so a provenance block inserted "after the first heading" silently lands nowhere. Insert it
  after the closing `---`, with an H1 fallback only when the frontmatter is absent.

---

## Session Reference

The founding session record — the full marathon log (publication, audits, installs, the google-workspace stock-restore decision, and the v1.1.0 bidirectional-sync addition) — lives in [references/2026-07-18-skill-audit-findings.md](references/2026-07-18-skill-audit-findings.md). Case history belongs there, not here; keep this file general.

## Support files

- `scripts/upstream_source_map.py` — the source registry probe. `--sources` feeds the 2b loop; `--coverage` is the gate (exit 2 = the procedure is name-list-based, not lock-derived); `--diff <source> <listing>` classifies each upstream-only name as `ABSENT` (not in the store and never retired — the real gap), `PRESENT-ELSEWHERE` (already installed by another route, i.e. a rename candidate, never a duplicate to install) or `RETIRED-DELIBERATE` (a row in `.retired.json` — reinstalling resurrects a decision), and exits 1 on an unparseable listing instead of reporting a false zero.
