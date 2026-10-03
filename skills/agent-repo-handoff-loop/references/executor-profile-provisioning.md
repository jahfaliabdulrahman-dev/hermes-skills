# Executor Profile Provisioning (CarSah → flutter-coding-bot, 2026-08-22)

Verified recipe for standing up a dedicated executor profile in Hermes that
carries a project's lessons into every future session. Executed for
`flutter-coding-bot` (replaces the per-project swarm profiles; the founder's
vision: one bot that grows smarter over time).

## Why this exists

The mailbox design made the IMPLEMENTER a commodity (swappable in one line).
Profiles extend this: the executor gets its own identity file (SOUL.md), its
own model lane, and its own memory — so lessons learned in one project are
BORN into the next session, no manual injection.

## Steps (exact)

### 1. Create with clone

```bash
hermes profile create flutter-coding-bot --clone-from default
```

- Clones config.yaml, skills/, memories/, sessions/ layout.
- ⚠️ The clone's skills are a SNAPSHOT. It may be missing skills edited after
  the profile list was last synced, or carry stale versions. See step 2.

### 2. Overwrite the must-be-current skills from the source of truth

```bash
rm -rf ~/.hermes/profiles/<name>/skills/flutter-lessons-patterns
cp -R ~/.agents/skills/flutter-lessons-patterns ~/.hermes/profiles/<name>/skills/
# repeat for any skill edited recently; then VERIFY:
grep -E "^version" ~/.hermes/profiles/<name>/skills/flutter-lessons-patterns/SKILL.md
```

- The default profile often reads skills from `~/.agents/skills/` (symlink
  confusion verified 2026-08-13: sessions searched `~/.hermes/skills/...`
  and wandered into `~/.hermes/lsp/node_modules`). If a skill's canonical
  source is `~/.agents/skills/`, that is what you copy.

### 3. Set the model lane in the profile's own config.yaml

```yaml
model:
  default: stealth/ox-alpha
  provider: nous
  reasoning_effort: max
```

- Per-session `-m`/`--provider` on every launch is fragile (one invocation
  point drifts). The profile default is the stable place; loop scripts still
  pass `-m` explicitly, but a manual launch without flags now gets the right
  model too.

### 4. Probe the model BEFORE arming anything

```bash
hermes chat --profile <name> -m stealth/ox-alpha --provider nous --reasoning max \
  -q "Reply with exactly: OK-OX" -Q --max-turns 1   # expect OK-OX
```

- A model listed in a provider catalog can STILL 404 on call (gated until
  activated — `deepseek-v4-pro-0813` was listed by Nous's catalog and
  returned HTTP 404). The probe is the only proof.
- **Live roster is the truth** (`curl <base>/v1/models` with the key):
  `stealth/ox-alpha` exists there but not in the stale local cache.

### 5. Write the profile's SOUL.md

Structure: mission one-liner → non-negotiables section (THE project's
hard-won rules, verbatim from frontmatter-level discipline) → operating
style → the skill list it must load before code. For CarSah-derived
non-negotiables, list: guard must be broken by the thing it guards (never a
copy); every delivery letter is an all-attempts ledger; SDK-not-memory;
named deviations (no silent divergence); pumpAndSettle banned / runAsync
wraps waiting only; register updated in the SAME commit.

### 6. Write the profile's MEMORY.md (cross_profile=true from default)

```bash
# through the memory/write file tool with cross_profile=true, e.g.
write_file path=~/.hermes/profiles/<name>/memories/MEMORY.md cross_profile=true
```

- Soft guard blocks default-profile writes to another profile's memory; the
  user's directive to build the bot IS the authorization.
- Profile MEMORY should carry project facts (repo paths, device ids,
  signing rule, standing DECs), not the default profile's generic notes.

### 7. Flip ALL loop scripts in ONE change

```bash
sed -i '' 's|hermes chat --resume "$SESSION" -m <old> --provider <p> --reasoning max|hermes chat --profile <name> --resume "$SESSION" -m <new> --provider <np> --reasoning max|' \
  ~/.hermes/scripts/carsah_auto_wake.sh
# same for carsah_auto_rotate.sh create + resume lines; then:
sed -i '' "s|^SESSION=<old>$|SESSION=<newid>|" wake rotate live
```

- Partial flips left the loop silently on the dead provider (2026-08-14) and
  left one script pointing at a retired session (2026-08-11). All three
  scripts + session id + profile + model change together in ONE edit.

### 8. Monitoring and DB location

- `~/.hermes/state.db` = DEFAULT profile's session store.
- A profile session's messages live in `~/.hermes/profiles/<name>/state.db`
  (`SELECT role, content FROM messages WHERE session_id=...`). Querying the
  wrong DB shows an empty/old transcript and looks like a dead agent.
- Runtime pointer convention: `/tmp/carsah_newid.txt` per profile.

## Resume latency (normal, not a hang)

A large session (2k+ messages — the CarSah implementer reached 500+ turns /
2.5k messages) takes ~1.5–2 min after `hermes chat --resume` before the
injected directive appears as the newest `role='user'` row in the session DB.
Liveness check = process alive AND wait; do NOT kill it as "stuck" inside
that window, do NOT re-issue the directive (duplicate user messages poison
the context). After ~2 min, check the newest user row; if absent, then
diagnose.

## Checklist

- [ ] Profile created (`hermes profile list` shows it)
- [ ] Must-be-current skills overwritten + version verified
- [ ] Model lane set in the profile config.yaml
- [ ] Probe returned OK
- [ ] SOUL.md written (non-negotiables + skill list)
- [ ] MEMORY.md written (project facts; cross_profile)
- [ ] All three loop scripts flipped in one change (`grep flutter-coding-bot` > 0)
- [ ] Per-profile state.db path known for monitoring
