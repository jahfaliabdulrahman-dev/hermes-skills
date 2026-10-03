# Loop Operational Pitfalls — measured on CarSah 2026-08-11/12

Class-level failure modes of the repo-mailbox loop, each observed live. Read
these BEFORE touching any loop component (cron, directive, marker, session).

## 1. Stale-directive wake loop ("same directive repeated")

**Symptom:** the implementer session says, over and over: *"same directive
repeated (Nth time) — already executed and delivered, waiting for the auditor"*
and refuses to run. The founder sees "implementer idle" and suspects a dead loop.

**Mechanism:** the wake cron passes the SAME frozen directive text on every
tick while the marker mismatch persists. The session correctly recognizes the
directive was already fulfilled and refuses — that is smart behavior, not a bug.
The loop is broken on the COORDINATOR side: it wakes with a stale message.

**Fix (the coordinator side):** the directive must carry WHAT the auditor
actually said in the newest review (`handoff/claude/<ts>.md`), not a frozen
brief. On every wake, either (a) rewrite the directive to reference the latest
review by name and enumerate its STOPs/CARRYs, or (b) make the directive
generic: "read the newest handoff/claude/ letter FIRST; act on it". A generic
directive that says "the latest review is authoritative" survives rotation
without per-review rewrites.

**Also observed:** after ~8 repeated identical directives, the session's
context is poisoned — it starts rejecting even UPDATED directives. Rotate to a
fresh session rather than reasoning with it.

**Generalized — it is not only the wake cron.** Any directive committed into a
live repo goes stale the same way: counts, ratios and step references inside it
drift while the loop keeps working. Two rules follow: (1) mark every embedded
number as "measured when written" and ship the command that re-measures it, so a
reader re-derives instead of trusting it; (2) re-check each seeded defect is
STILL open immediately before publishing — when one has already been fixed, say
inside the document that it was consumed and swap in a live one, because an
auditor that "discovers" a closed item loses authority it never gets back.

## 2. Marker hash-length mismatch (7 vs 40 chars)

**Symptom:** the waker keeps firing (or stays silent) although nothing changed.

**Mechanism:** the stored marker holds a SHORT hash (`9bf7977`) while `git
log -1 --format=%H` returns the 40-char hash. The exact-string comparison
`[ "$LAST" = "$(cat "$MARKER")" ]` fails forever → endless wakes (or, if the
marker is longer, permanent silence). Observed when a session wrote a
short-hash marker by mistake.

**Fix:** always store the FULL 40-char hash in markers. Add a sanity check in
the wake script: `[ ${#marker} -eq 40 ] || rewrite it`. The script should
self-heal a malformed marker instead of looping on it.

## 3. Rotation threshold counts `active=1` only — compaction hides bloat

**Symptom:** a session grows to 1200+ total messages but auto-rotate never
fires; the founder finds a bloated session that refuses new work.

**Mechanism:** the rotation script counts
`SELECT count(*) FROM messages WHERE session_id=... AND active=1` — message
compaction marks old rows `active=0`, so the count stays under the threshold
(observed: 1255 total vs 677 active). The session IS bloated; the script
cannot see it.

**Fix:** count ALL messages for the session (drop the `active=1` filter), or
count by `MAX(rowid)` delta. When in doubt, rotate manually:
create a fresh session with the skill map, `sed` SESSION into ALL THREE
scripts (auto-rotate + auto-wake + live watcher), restart the watcher, wake.

## 4. CI-quote discipline (STOP-29 class)

**Symptom:** a delivery reports "CI green" by citing a run from a DIFFERENT
workflow (e.g. the Supply Chain Security Scan — one OSV job) while the real
workflow (Build & Release: analyze/test/build) FAILED. Or cites a docs-only
head commit where the whole job was SKIPPED by change-detection.

**Rule:** a delivery's `evidence.ci` must name the workflow AND quote at
step level (`gh run view <id>` — each step's success/failure), and the run
must be on the CODE commit (not a docs-only follow-up). "CI green" and
"CI skipped the build" are different sentences. Verified lineage:
`git merge-base --is-ancestor <code-sha> <head-sha>` plus the head commit
touching only handoff/ files means the green run covers the code.

## 5. A guard that bans one shape leaves the other shape unguarded

**Symptom:** a class of bug is "fixed" with a guard, then reappears in the
sibling shape. Observed: STOP-28's guard banned `pump`/`tap` inside
`runAsync`, but the fix's OWN helper left a guessed `4×50ms` wait with a bare
`pump()` — the same timeout class, unguarded. The auditor wrote it and then
admitted it: "the guard enforces the half I fixed and not the half I left."

**Rule:** when encoding a lesson as a guard, enumerate the lesson's OTHER
half (the waiting-for-condition half, not just the nesting half) and guard
it too — or the lesson will return through the unguarded door. Acceptance of
any "fix the class" guard: plant the SIBLING shape, not only the original one.

## 6. Push race during a recurring CI hang — FORENSIC mode after the 2nd signature (2026-08-13)

**Symptom:** the same CI hang (widget test hanging Linux CI only, green
locally) recurs 4-5 times in ~3 hours — each round: hypothesis → patch →
push → 20-50 min cancelled run → review → next hypothesis. ~2 hours of
runner time, zero green runs, ONE signature. The implementer looks busy and
is making zero measured progress; the founder sees "رفع سريع بدون اختبارات".

**Mechanism:** each attempt was an unverified guess with NO reproduction of
the failing environment first (local macOS stayed green — the STOP-28
signature). The written lesson ("reproduce Linux before fixing") existed but
was NOT ENFORCED on the fix process — and, in this case, the lessons skill
itself was missing from the session's birth skill set (see the CORRECTION in
SKILL.md step 3), so the implementer never even read it.

**Fix — coordinator-side enforcement:**
1. **After the SECOND recurrence of the same signature, the next commit must
   be a DIAG run** (isolate the failing file on the failing platform via
   `workflow_dispatch`, or instrument the suspect chain) — never another fix
   hypothesis. One experiment per run; each run answers ONE question.
2. **Mandatory Pre-Push Checklist** (from flutter-lessons-patterns Pattern
   52 / LL-055) — every implementer push must prove all six: local suite
   green · analyze clean · failing-platform reproduction (if platform-
   specific) · one named question per CI run · cost counted aloud on attempt
   N+1 (what NEW measurement does this run produce?) · diff scope named. Any
   unprovable row blocks the push. The directive file must carry this
   checklist verbatim.
3. The auditor switching to diag runs IS the process working — do not let
   the implementer push another fix in parallel; one experiment per run.
4. The founder's phrase for this class: "قصور في منهجية الاختبار واستعجال" —
   a green local run is not evidence of a Linux fix, never was.

## 7. Provider/billing switch must touch EVERY invocation point (2026-08-14)

**Symptom:** the implementer dies mid-round with `HTTP 404: Model
'deepseek/deepseek-v4-pro' requires available credits` — the Nous Portal
credits ran out (usable $0.00). The loop stalls; the founder orders a switch
to another provider (platform.deepseek.com).

**Mechanism:** the model was pinned on the provider `nous` in THREE separate
invocation points — `carsah_auto_wake.sh` (resume line),
`carsah_auto_rotate.sh` (creation line) AND `carsah_auto_rotate.sh` (resume
line). Switching only the manual launch leaves the loop silently on the dead
provider at the next cron tick. The dirty tree also blocks the relaunch
(founder's manual `ios/pbxproj` edits → `git pull --rebase` refuses).

**Fix:**
1. Apply the provider switch in ALL THREE script invocation points (grep
   `--provider` across the loop scripts to find every one — missing any
   single site re-kills the loop on the next wake).
2. **Probe the model before relaunching:** `hermes chat -m <model>
   --provider <p> -q "Reply with exactly: OK" -Q --max-turns 1` must print
   `OK`. A model listed in a provider's `/models` catalog can still 404 on
   call (`deepseek/deepseek-v4-pro-0813` was listed by Nous but returned
   HTTP 404 — new models appear in the catalog before they are callable).
3. **Dirty tree from founder manual edits:** wrap the pull in
   `git stash push -- <paths>` → `git pull --rebase` → `git stash pop`.
   Never discard or commit the founder's edits without explicit approval —
   stash is reversible, deletion is not.
4. The active chat model can switch providers mid-session (system metadata
   announcement) — re-check the provider on the implementer launch command
   rather than assuming the config default.
5. The custom provider's key + base URL live in the user env file (e.g.
   `DEEPSEEK_API_KEY` + `DEEPSEEK_BASE_URL` for platform.deepseek.com) —
   verify the key exists before blaming the provider.

## 8. Executing an audit-wave plan in full: founder orders rows 49/50/51 (2026-08-15)

**Symptom (non-failure):** a standing audit plan (Waves 1-5 from the fix-plan
letter) has Waves 3-5 still "awaiting founder placement". The founder rules:
"نفذ Waves 3-5 كاملا" — execute them IN FULL. The coordinator must convert a
plan into sequence rows without breaking the locked table.

**Pattern (validated on CarSah — Waves 3-5 as rows 49/50/51 after BL-102):**
1. The coordinator adds the waves to the locked sequence table (18 §14b.2)
   as numbered rows (49/50/51) with a founder-decision attribution line —
   the founder's "execute in full" IS the placement ruling; no separate DEC
   ceremony needed, but the row text must record who decided and when.
2. **One wave = one independent delivery** — Wave 3 submit → review →
   Wave 4 submit → review → Wave 5. Never bundle waves in one push; each
   wave has its own letter + STATE + Telegram.
3. A wave's sub-items keep their original IDs (W3.1-W3.4, W4.1-W4.4,
   W5.1-W5.2) in the row text so the auditor can trace each acceptance to
   the source fix-plan letter.
4. Items that are "scheduled, not now" (W5.1 schema-lock fixture) still get
   executed in the wave — the founder said in full; the row's why-note
   (impossible after release) is what makes it urgent.
5. CI evidence per wave follows the same discipline (workflow name, step
   level, golden diff ratios if a wave touches pixel tests — see the
   golden-failure pitfall above).

## 9. Closing the loop: the state machine is flipped in the SAME commit

**Symptom:** the closing commit announces PASS + cleanup and the mailbox holds a
DECISION message saying "no more review rounds", while `handoff/STATE.md` still
reads `AWAITING_REVIEW` with a `next:` step that already happened. Anything that
trusts STATE keeps working on a finished task.

**Mechanism:** closure was treated as a message-only action (write the closing
letter, push it) and the state machine was left to its last writer.

**Rules:**
1. Every closure updates `status` / `step` / `next` in the SAME commit as the
   closure message — a closure without a STATE flip is an unfinished closure.
2. When you did not perform the closure and are asked to trust it, read THREE
   artifacts, never one: the verdict commit (the PASS/rejection itself), the
   closure message, and the tree state (branches, worktrees, tags, the test
   suite, the guard). A message claiming PASS is a self-report.
3. Correcting a stale STATE is legitimate work — write in the file WHY it was
   stale (`status` was X after Y), so the next reader sees a repair, not drift.

## 10. A shared working tree sweeps YOUR untracked files into someone else's delivery

**Symptom:** documents you added to the checkout (a directive, a report you were
drafting) turn up inside the OTHER agent's delivery commit, unannounced — and the
loop's own evidence rule ("no undeclared file in a delivery") then flags them.

**Mechanism:** both agents share one checkout and the implementing side stages
broadly; nothing stops an untracked file from riding along into its commit.

**Rules:**
1. Keep your own artifacts in a single-file commit and prove the scope:
   `git add <path> && git diff --cached --name-only` before committing.
2. **Respect the freeze first:** while a submission is AWAITING_REVIEW (or its CI
   is in flight) do NOT inject a commit into the repo — commit at the next
   boundary. An untracked file waiting is cheaper than a broken review cycle.
3. After any delivery that touched your file, verify the content survived inside
   whatever commit carried it (`git show <sha>:<path>`) instead of assuming.
4. A tree-level guard that scans `git ls-tree HEAD` cannot see untracked files,
   so a clean verdict taken before the commit certifies the PREVIOUS tree; the
   publishing set is what the push-time (pre-push) mode scans.

## 11. A clean `git status` is not a quiet tree — the peer's live worktree is invisible to it

**Symptom:** you check `git status --porcelain`, see nothing, and report "tree clean,
no writer active" — then find a full second checkout of the repo (e.g.
`.claude/worktrees/<name>`) sitting on a branch at the same commit, with the peer
agent's process working inside it. The inverse also bites: you set out to prune
"stray" worktrees and delete one a running session is using.

**Mechanism:** a REGISTERED git worktree is excluded from the main checkout's
`git status`, so a clean status is fully consistent with an active writer. The
directory is not junk — it is a checkout, created on purpose by the tool that runs
the peer agent. Cleaning up after a previous closure does not prevent a new one from
appearing the next time that agent starts.

**Rules:**
1. Before claiming "tree clean / nobody is writing", prove it from three sources, not
   one: `git worktree list` (each entry is a checkout), `git branch` + `git tag`
   (leftovers, and which refs are still alive), and `pgrep -fl "<agent binary>"` for a
   live process. "No worktree" and "no process" are different facts — state which.
2. **Never remove a worktree, branch or tag while its agent's process is alive.**
   Pruning under a session that is mid-edit breaks it exactly as killing a running
   paid job does. Wait for the process to exit, then clean.
3. **Tags keep objects reachable.** A tag pointing outside the main lineage holds an
   entire pre-cleanup tree alive — including whatever a history rewrite was meant to
   remove. Before declaring a cleanup complete, check the tag's lineage
   (`git merge-base --is-ancestor <tag> main`) and whether the removed content is still
   in it; also check `git ls-remote origin 'refs/tags/*'`, because a local-only tag is
   not published and a published one cannot be un-published quietly.
4. When your next step depends on "no one else is writing", re-run those three checks
   at that moment — a state read at the start of a session ages faster than any other
   fact in this loop.

---

## The coordinator must enforce FORENSIC mode after the 2nd identical CI signature (2026-08-13)


STOP-38 (a widget test hanging Linux CI only) produced FIVE fix attempts in ~3 hours — hypothesis → patch → push → 20-50 min cancelled run → review → next hypothesis — ~2 hours of runner time, zero green runs, ONE signature. The implementer kept "fixing" while the fix process itself was the defect: each attempt was an unverified guess with NO reproduction of the failing environment first (local macOS stayed green — the classic STOP-28 signature). The auditor's three diag runs (isolate the file alone → instrument the suspect chain → instrument start/seed) produced more truth than the five fix attempts combined. The founder's catch, now Pattern 52 / LL-055 in flutter-lessons-patterns.

Coordinator-side rules (the loop operator, not the implementer):

1. **After the SECOND recurrence of the same signature, stop letting the implementer push fixes.** The next commit must be a DIAG run (isolate the failing file on the failing platform via `workflow_dispatch`, or instrument the chain) — reviewable in the commit message itself. A fix attempt without a new measurement is a repeat, not progress.
2. **Count the cost aloud before attempt N+1:** "N attempts, X minutes runner time, same signature — what have we MEASURED that we didn't know before?" Nothing new → do not push another hypothesis.
3. **A green local run is not evidence of a Linux fix** — never was (STOP-28). The only evidence is a green run on the failing platform itself.
4. **The auditor switching to diag runs is the process working** — do not "help" by letting the implementer push another fix in parallel; one experiment per run.

**⚠️ One attempt is half the truth (Pattern 53 / LL-056, flutter-lessons-patterns).** A delivery letter that cites a CI run must list EVERY attempt — the same commit re-run 3× produced 3 different outcomes on 2026-08-13 (attempt 1 failed add_refresh+invoice_photo; attempt 3 failed locale_switch; attempt 2 was effectively green, 430/430 + Build ✅ + Merged-manifest ✅, only artifact upload failed on quota). The implementer's "the founder is wrong" and the founder's attribution were BOTH true of different attempts — neither lied, each read one. The greenest attempt is the strongest evidence and belongs in the letter even if it is not the one cited. Auditor check: `gh api .../runs/<id>/attempts` count must match the letter's rows. Never declare a human wrong on the basis of one attempt — the difference is data (suite nondeterministic under load), not dishonesty.

**⚠️ Root cause found one layer deeper (2026-08-13): the lessons skill was never in the birth skill set.** The implementer had been built for 40+ steps WITHOUT `flutter-lessons-patterns` — Pattern 28 ("reproduce the failing platform") and the STOP-28 lessons existed but were never loaded into any session, so five rounds re-learned them at ~25 min each. A lesson written but not DELIVERED to the implementer is not a lesson — it is a library book on a shelf. The coordinator's job includes auditing the birth skill set periodically (does the newest lesson actually reach the next session?) and — when a session must read a skill file — giving the exact absolute path (sessions have wandered into `~/.hermes/lsp/node_modules` searching for a skill they could not find; symlink confusion between `~/.agents/skills/` and `~/.hermes/skills/`). Mandatory Pre-Push Checklist lives in Pattern 52 and the directive file must carry it verbatim (local suite · analyze · platform reproduction · one question per run · cost counted aloud · diff scope named — any unprovable row blocks the push).


---

## Pitfalls (all hit in the field)


| Symptom | Cause | Fix |
|---|---|---|
| Cron agent run: HTTP 400 `reasoning.effort: Invalid option: expected one of "max"\|"xhigh"\|"high"\|...` | `agent.reasoning_effort` in config.yaml set to a value the provider rejects (e.g. `ultra` for deepseek) | `hermes config set agent.reasoning_effort high`; **always fire a test run right after creating a cron job** (baseline run catches config errors) |
| Push rejected (non-fast-forward) | Both agents pushed concurrently | `git pull --rebase` before every push — make it a rule, not a habit |
| Loop spins burning tokens while awaiting a human decision | No stop rule | `AWAITING_FOUNDER` state stops both pollers; only founder action wakes them |
| Claude-side 3-min cloud polling impossible | Cloud routines = 1h min; GitHub Actions cron = 5-min min | Auditor /loop must run locally (Claude Code /loop supports ≥1 min) |
| "Chat not found" on `--to telegram` | Home-channel resolution fails in some contexts | `hermes send --list telegram`; use the exact listed target name |
| Docs-only pushes trigger CI every message | Full pipeline runs on every push | Guard job (skip build when `lib/` absent) keeps doc commits green & cheap — verify CI anyway (LL-021: pushed ≠ green) |
| Monitor fires on the agent's OWN push | After push, HEAD == origin/main → log empty → IDLE | Design the script against `HEAD..origin/main`; no self-trigger loop |
| Auditor polls "idle" although real work was pushed | Work landed BEFORE the mailbox existed (protocol created later) — the poller watches `handoff/` paths, not code commits, so the mailbox is genuinely empty | Bootstrap the mailbox: write the first SUBMIT message covering the already-pushed work; the auditor's next poll then fires. An "idle" is not always a bug — check the mailbox itself |
| The OTHER agent's poll also returns empty in a shared tree | It too used `HEAD..origin/main` | Give BOTH sides the marker form (`git log -1 --format=%H origin/main -- <dir>`) — the shared-tree hazard applies to every poller, not just yours |
| Resumed session works at default effort, not the demanded max | `hermes chat --resume` without `--reasoning` inherits `agent.reasoning_effort` | Pass `--reasoning max` explicitly (CLI lists `ultra` but deepseek rejects it — valid: max\|xhigh\|high\|medium\|low\|minimal\|none) |
| Founder opens the session and sees no new messages while it is clearly working | Desktop app does not live-refresh messages appended by a background CLI process | Show them `grep "<SESSION_ID>" ~/.hermes/logs/agent.log | tail` (live tool activity) + `git status --porcelain` (mid-edit proof); provide a ~8s refresh loop dashboard |
| Design changed while a run was in flight (old role prompt still executing) | Cron agent mid-run on the previous prompt | Confirm liveness first: `grep "cron_<job_id>_" ~/.hermes/logs/agent.log` (recent API call = alive; marker absent = unfinished). Touch the lock so new ticks stay IDLE, let the in-flight run finish (it follows the same spec), then swap prompts and remove the lock |
| CHANGED detected but agent run died → loop deadlocked (all later ticks suppressed, manual runs too) | Monitor recorded the CHANGED hash as seen; the run failed (provider outage) | Re-arm via a watched-file bump: update `handoff/STATE.md` (legit note) + push → `LAST` advances → next tick fires. Then `cronjob action=run`. Never hand-edit jobs.json monitor state |
| Coordinator keeps reporting `no_change (agent run suppressed)` while a NEW review sits in the mailbox — but `bash <monitor_script>` manually prints `CHANGED <sha>` | The cron's stored monitor_state hash is STALE (baseline recorded at the new output without an agent run — hit 2026-08-10: the review landed, three ticks suppressed, implementer never woken); the SCRIPT itself is fine | Verify the script manually first (one `bash <script>` call settles script-vs-cron blame); then DIRECT-LAUNCH the implementer with the same directive (the reliable fallback); the state self-heals when the marker advances — the next output differs → the next tick fires |
| Provider rejects the configured model after switching `cron.provider` (404 / model not found) | Model ids are provider-route-specific — a Nous-routed dated id (e.g. `deepseek-v4-flash-0731`) does not exist on the direct API, and familiar names (`deepseek-chat`) may not either | Query the provider's `/models` endpoint with the key FIRST, pin a real id (e.g. `deepseek-v4-flash`), then verify with a manual `cronjob action=run` — a "no double wake / no new review" reply still proves the provider path |
| Duplicate deliveries / "session scope close failed" relay errors | TWO wakers: the external agent woke the implementer directly (`hermes chat --resume`) AND the coordinator woke it — parallel resumed sessions on one id | ONE waker per loop: if the external agent wakes the session directly, disable the coordinator wake (or vice versa). If a duplicate already landed, the implementer's idempotency guard + documenting the duplication converges it (same commit, one SUBMIT). **Ignoring this escalates from noise to corruption** — see next row |
| Implementer session corrupted → coordinator fires but NO implementer process ever appears, ZERO API calls, loop silent for hours (hit 2026-08-08: 8h deadlock) | Parallel wakes on one session id corrupted its relay scope ("session scope close failed"); every later `hermes chat --resume` dies INSTANTLY without logging an API call; the coordinator's launch "succeeds" from its own view; the monitor's hash suppression then silences all later ticks | Rotate immediately: confirm corruption — `grep "<SESSION_ID>" ~/.hermes/logs/agent.log | tail` shows last real activity HOURS ago with no `turn_context`/`API call` since, AND coordinator output files are all `no_change`. Then: create fresh session (one-shot `hermes chat -q "…" -Q --max-turns 1` → capture id), re-point the coordinator's resume target, retire the old id (kill -9 after confirming its work is pushed). Do NOT retry the same id |
| Coordinator "verified the launch" but the implementer still never ran | Process check alone is blind: the resumed process can exist briefly then die instantly (corrupted session, zero API calls) | Verify launches by LOG, not by process: within ~60s of the wake, `grep "<SESSION_ID>" ~/.hermes/logs/agent.log` must show a NEW `turn_context`/`API call`. No new turn = the resume failed → rotate the session, don't re-fire |
| Implementer exits `max_iterations_reached(N/N)` with the tree dirty and nothing pushed | `--max-turns` budget too small for a heavy step (first vertical slice: router + wizard + widget tests can exceed 150 turns) | Resume the SAME session with a continuation directive (stash-named → pull --rebase → pop → finish → commit logical groups → SUBMIT); raise `--max-turns` to ~400-500 for heavy steps (an on-device walk + widget tests + CI watch burned 250 — the founder moved it to 500). Do NOT rotate — the in-context todo/decisions are the value |
| Coordinator cron shows `enabled: false / state: paused` right after you updated it | `cronjob action=update` returned the job paused (paused_at = update moment, hit 2026-08-09) — a paused coordinator is a silent loop death | Always read the update response's `enabled` field; call `cronjob action=resume` if paused; verify `next_run_at` is in the future |
| Watcher dashboard says "⚪ idle" while the implementer is clearly working | A STALE watcher process from an earlier rotation still has the old SESSION id in memory — its `pgrep -f "<old id>"` never matches the new session (hit 2026-08-09: duplicate `carsah_live.sh` processes, old one lying "idle" for hours) | On every rotation: kill ALL old watcher processes (`process(action=kill)` per session id from `process(action=list)`), patch `SESSION=` in the script, start ONE fresh watcher |
| Founder alarmed: "implementer is running `flutter pub outdated` mid-build — violating the dependency policy" | It is not — `Try \`flutter pub outdated\` for more information.` is Flutter's STANDARD analyzer/test boilerplate footer (printed with unused-import and dependency warnings), not a command the agent ran | Before flagging a policy violation from tool output, check the actual tool_name + whether a `pub outdated`/`pub upgrade` command was executed; the footer line alone is noise |
| After a rotation/resume, the NEXT auto-rotation fires on the WRONG session (counts messages of a retired id) | `carsah_auto_rotate.sh` sed-updates `SESSION=` in the auto-wake script and the watcher but never its OWN copy — so its internal id stays on the previous session forever (hit 2026-08-11: rotate script still had `091608` while the other two pointed at `171043`/`015808`) | On every rotation AND every manual resume, update `SESSION=` in ALL THREE scripts (auto-wake, live watcher, auto-rotate). One `sed -i ''` per file; verify with `grep "^SESSION"` across all three |
| Founder resumes the loop but the stuck watchdog never alerts again | The watchdog CRON entry disappeared during the hold — the founder paused the loop (auto-wake paused), and the `carsah-stuck-watchdog` job was gone from `cronjob list` while the script still existed on disk (hit 2026-08-11) | After any hold/resume, `cronjob action=list` and verify ALL loop crons exist and are enabled: auto-wake (5m), auto-rotate (30m), stuck-watchdog (5m). Recreate missing ones with the documented shape (`no_agent=true`, `script=...`, `deliver=origin`) |
| Implementer idle despite a NEW auditor letter; wake log shows repeated `WOKE` for the same sha; the session answers «نفس التكليف المنتهي» | The wake directive FILE still describes the PREVIOUS, already-completed assignment — auto-wake re-injects stale text every 5m, and the implementer (correctly) refuses to repeat finished work (hit 2026-08-11: 11 wakes, zero progress) | The directive file is MUTABLE state: read the newest `handoff/claude/` letter, rewrite the directive to name its verdict + next step ("previous assignment complete — new assignment: execute CARRY-72..76, then BL-070"), kill the looping session if needed, re-launch with the fresh text. Never keep re-firing the same wake; never instruct "execute regardless" |
| Manual wake launched the OLD session id while scripts point at the NEW one (hit 2026-08-12: coordinator woke 113928 from memory after auto-rotate had moved to 145117; founder asked "did a new session open?") | Coordinator hardcoded a session id from an earlier turn instead of reading the current one | Before ANY manual resume/launch: `grep "^SESSION" ~/.hermes/scripts/carsah_auto_wake.sh` — that file is the single source of truth for the CURRENT id. Never wake from memory |
| Founder sees TWO processes on the SAME session id and the implementer reports "a parallel session is working" (hit 2026-08-13: coordinator direct-launched 075225 AND auto-wake fired the same resume in the same tick → 2 pids, 22 min uptime each) | Two `hermes chat --resume <same-id>` processes concurrently — one manual launch + the deterministic auto-wake both firing in the same window | After ANY manual launch, `pgrep -f "hermes chat --resume"` and kill duplicates before proceeding; the single-waker check in auto-wake only guards ITS OWN fire, not a manual one — the coordinator is responsible for the manual side |
| GitHub Actions storage quota exhausted (100% of 0.5 GB — hit 2026-08-13) | Every Build & Release run uploads ~106 MB of artifacts (debug-apk 76 + release-path-proof 30) × 14-day retention × a night of diag runs (98 artifacts ≈ 3 GB) | `gh api repos/<owner>/<repo>/actions/artifacts --paginate` cleanup; set `retention-days: 3` on both upload-artifact steps in release.yml; budget diag runs (each run = ~106 MB for 3 days). **Quota recalculates every 6–12 h — deleting artifacts does NOT immediately unblock reruns** (observed 2026-08-13: rerun still failed with "Artifact storage quota has been hit" after a full cleanup; the founder's fix was the paid plan). A rerun is not the fix; verify the actual quota state first, or expect repeat failures for hours |
| Device install wiped the founder's real app data (STOP-37, 2026-08-12) | Android refuses an update across a SIGNING IDENTITY change (debug → upload key); the only path is uninstall, which deletes the app's Isar DB. The letter said "installed over a clean uninstall" — that phrase IS the data loss. Verify with `adb shell dumpsys package <pkg>`: `firstInstallTime == lastUpdateTime` = fresh install, not an update | Any device step that installs a differently-signed build over an existing app is a FOUNDER-GATED DESTRUCTIVE step (DEC-066): the delivery letter must name the wipe consequence BEFORE execution and await explicit founder approval. The mechanism is mechanical and recurs at every release install over a debug install — never let a second silent wipe happen |
| Golden tests fail CI-only with a small pixel diff (hit 2026-08-15, W4.3: Dashboard 1.64% / 41,536 px · wizard brand list 0.96% / 24,380 px — all passed locally on macOS) | Font rendering differs between platforms (antialiasing/fallback), so a golden captured on macOS is not guaranteed identical on Linux CI — this is a rendering difference, not a regression | Use the OFFICIAL tolerant-golden recipe: comparator base = test-file URI + **fraction tolerance** (e.g. `matchesGoldenFile(..., tolerance: 0.02)`). Tolerance on the FRACTION, never absolute pixels (a real redesign moves far more than 2% of pixels). Report the diff ratio per failing golden in the letter. **Never delete the golden** — the golden is the automated pixel evidence (the gate that failed 6× under human review); calibrate it, don't remove it. Verify the guard still bites: plant a visible-widget mutation and confirm the golden still goes red |

