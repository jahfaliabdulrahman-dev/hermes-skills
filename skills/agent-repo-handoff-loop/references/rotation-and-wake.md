# Rotation, wake machinery and coordinator plumbing

Split out of SKILL.md (2026-09-19) because the file crossed the skill size limit. Everything
here is the OPERATIONAL layer: how a long-lived implementer session is rotated, how it is woken,
how a stalled loop is diagnosed, and where the coordinator is deliberately NOT an LLM.

## Context relief: rotating a bloated implementer session


A resumed session's context grows every cycle (observed on CarSah: 280K → 388K
input tokens per call) and quality drifts with it (recurring evidence-hygiene
defects, verdict inflation). Rotate to a fresh session when: per-call input
tokens keep climbing, OR the process is alive but the log is silent for a long
stretch (possible hang), OR the same finding class recurs across reviews, OR —
the CORRUPTED variant (hit 2026-08-08, 8h silent deadlock) — the process is NOT
alive and every resume dies instantly with ZERO API calls after a "session
scope close failed" relay error: the coordinator fires but no implementer ever
appears. The corruption signal is a fixed last-activity timestamp in
`grep "<SESSION_ID>" agent.log` with no new `turn_context` since, while the
coordinator's own output files stay `no_change`.
Rotation recipe:

0. **Rotate PROACTIVELY, not only on failure (hard lesson, hit twice 2026-08-08/09):** a resumed implementer session that grows past ~700-900 messages and survives many wake cycles is corruption-prone — the relay "session scope close failed" recurred at 818 and 1172 messages, each time killing the loop until a manual diagnosis. Do NOT wait for the corruption signal. At the END of a delivery, if the session's message count is approaching ~800, retire it on the next wake: create the fresh session, re-point the coordinator, and let the new session continue from the (pushed) tree. The cost of one proactive rotation is far below the cost of a silent deadlock. **The threshold is MESSAGES (the measured proxy — corruptions seen at 818 and 1172), not tokens:** messages = the transcript's structural size (cheap: `SELECT count(*) FROM messages WHERE session_id=?`), per-call input tokens (`in=N` in agent.log) = context COST. Rotate when messages cross ~700-900 **or** when compression stops and `in=` keeps climbing — whichever comes first.

1. Confirm the old session's work is PUSHED and the tree is clean
   (`git status --porcelain` empty) — never rotate mid-edit.
2. Write a committed handoff brief (`handoff/implementer-brief.md`): approved /
   submitted steps, next step, protocol pointers, hard rules, the hardened
   submit checklist, first-wake instructions. The brief IS the new session's
   whole context — make it self-contained.
3. Create the fresh session and capture its id — **pass the lean skill set at
   birth** so the implementer's skill index is populated from turn one:
   `hermes chat --skills flutter-ai-code-verification,flutter-arch-boundary-enforcement,flutter-screen-state-machine,flutter-error-handler,flutter-app-logger,flutter-hook-architect,flutter-isar-clean-arch-setup,flutter-isar-testing,device-screen-verification,android-adb-device-testing,flutter-lessons-patterns -q "<ack-only kickoff; no tools, no work>" -Q --max-turns 1` → `session_id:` is printed on exit.
   **The implementer model is `-m deepseek/deepseek-v4-pro --provider deepseek --reasoning max` (founder choice — the stronger Pro lane, not flash).** ⚠️ **PROVIDER SWITCHED 2026-08-14: from `nous` to `deepseek` (platform.deepseek.com) after the Nous credits ran out mid-session (HTTP 404 "requires available credits").** The switch must be applied in ALL THREE script invocation points — `carsah_auto_wake.sh` resume, `carsah_auto_rotate.sh` create, `carsah_auto_rotate.sh` resume — not just the manual launch; missing one leaves the loop silently on the dead provider. Probe the model before relaunching (`-q "Reply with exactly: OK" -Q --max-turns 1` → expect `OK`), because a model listed in a provider's catalog can still 404 on call (new models gated until activated — `deepseek-v4-pro-0813` was listed by Nous but returned HTTP 404). A dirty tree from FOUNDER manual edits (e.g. `ios/pbxproj` signing tweaks) blocks `git pull --rebase` — wrap the pull in `git stash push -- <paths>` → pull → `stash pop`, never discard or commit the founder's edits.
   **⚠️ CORRECTION 2026-08-13 — flutter-lessons-patterns IS mandatory at birth,
   and the older "keep the set LEAN; no heavy general packs (e.g. a 120KB
   lessons skill)" advice was WRONG and costly.** The project-lessons skill was
   missing from the birth set for 40+ build steps; the implementer never read
   Pattern 28 (reproduce the failing platform first) or the STOP-28 lessons,
   and repeated the same CI-hang mistake 5 times (~2h runner time) before the
   founder caught that the lessons skill was simply not loaded. A 120KB lessons
   skill is CHEAPER than one repeated 25-minute CI round. Audit the birth set
   periodically (every few rotations): a new lesson written anywhere must reach
   the implementer — skills are delivered at SESSION CREATION, never to a live
   session; a mid-build correction only reaches the next rotated session.
   **Also give the exact skill PATH when the session must read a skill file
   directly** — the session once wandered into `~/.hermes/lsp/node_modules`
   searching for a skill whose directory it could not find (`~/.agents/skills/...`
   vs `~/.hermes/skills/...` symlink confusion). The directive should name the
   absolute path (e.g. `~/.agents/skills/flutter-lessons-patterns/SKILL.md`)
   so the session reads it instead of searching the filesystem.
   **Also keep GENERAL skills free of raw project names (2026-08-13).** A
   general lessons skill (flutter-lessons-patterns) carried 31 raw references
   to project names (HermexApp, Azdal, CarSah) inside pattern BODIES — a fresh
   session reading it concluded it was a project-specific skill and went
   searching project directories instead of using it. The `**Source:**` line
   may cite origins; the pattern body, examples and titles must be generic
   (TheApp(), "one project's Stage 5", no project names in headers). A general
   skill that looks project-specific defeats its own loading.
   The brief carries the per-pattern skill map; the wake directive must order "load the applicable skills BEFORE code — never re-derive a mandated pattern by code search" (founder standard 2026-08-09).
4. Point the coordinator/resume target at the NEW session id; re-arm the cron.
   **Verify the cron came back ENABLED** — `cronjob action=update` returned the
   job as `enabled: false, state: paused` on 2026-08-09 (paused_at = the update
   moment) and the loop would have died silently; `cronjob action=resume` fixed
   it. Always check the update response's `enabled` field and resume if paused.
5. Update the live watcher script's SESSION var AND kill old watcher processes
   (stale watchers from earlier rotations keep the OLD session id in memory and
   then display the OPPOSITE of reality — "⚪ idle — waiting for wake" while the
   implementer is actively working, because their `pgrep -f "<old SESSION>"`
   never matches the new session). `process(action=kill)` every old
   `carsah_live.sh` process; restart one fresh watcher.
6. Retire the old session: `kill -9 <pid>` only after step 1 — SIGTERM alone
   may not take on a hung process.

**⚠️ AUTO-ROTATE IS FOUNDER-PAUSED (2026-08-13) — rotation is MANUAL-ONLY now.** The founder paused the auto-rotate cron by hand: «Auto rotate وقفته انا لأنه ان عمل مشكلة فيعملها كارثة» — after the orphan-session incidents (2026-08-11) and the poisoned-session/parallel-wake mess (2026-08-12), the founder decided the automatic rotation machinery costs more in incident risk than it saves. The coordinator must NOT re-arm or re-create the auto-rotate cron unless the founder explicitly asks. Rotation happens manually: coordinator creates the fresh session, syncs SESSION= in all THREE scripts, kills/restarts the watcher. The rotation recipe below still applies — but the trigger is a human decision, not a cron.

**Rotate AUTOMATICALLY with a no_agent rotation watchdog (2026-08-10) — NOW PAUSED per the founder ruling above.** The manual recipe above works, but the coordinator can own it: a `no_agent` cron (every 30m) running `carsah_auto_rotate.sh` (see Support files) fires ONLY when all three hold — session messages > ~900 AND the tree is clean (git
status empty = a delivery boundary) AND the implementer is idle. It then:
creates the fresh session (lean skills at birth), `sed`-updates `SESSION=` in
BOTH the auto-wake script and the watcher, kills/restarts the watcher (the
founder's terminal link points at the new session), wakes the new session with
the standard directive, logs `ROTATED`, and delivers one English line. The
three-condition gate is what makes it safe: a mid-edit tree (dirty) blocks
rotation, so a bloated session always finishes its current delivery first.

**⚠️ AUTO-ROTATE IGNORES AN INTENTIONAL HOLD — it treats idle as
ready-to-rotate (hit 2026-08-11, orphan sessions edited files mid-hold).**
When the founder pauses the loop ("never wake him", deliberate hold), pausing
ONLY the auto-wake cron is NOT enough: `carsah_auto_rotate.sh`'s third
condition is "implementer idle" (`pgrep "hermes chat --resume $SESSION"`
absent) — which is EXACTLY what an intentional hold looks like. The rotate
cron keeps firing every 30m, creating fresh sessions, and waking them with the
standard directive. Observed: founder paused auto-wake at 10:11; auto-rotate
(never paused) spawned sessions `20260811_081149_c56247` and
`20260811_101210_b2d9e2` at 08:12 and 10:12; one orphan (081149) ran the
implementer directive and EDITED `test/features/settings/settings_screen_test.dart`
(mid-hold!) before dying at max-turns — a change attributed to "the
implementer" that no authorized session made. **Rules:**
1. **Pause ALL THREE loop crons when holding — auto-wake AND auto-rotate AND
   stuck-watchdog.** A hold is a full-loop pause; any cron left running that
   can spawn or edit is a live unauthorized writer.
2. **Before blaming "the implementer" for a file change, verify the WRITER.**
   Check `stat -f "%Sm" <file>` (mtime), `sqlite3 ~/.hermes/state.db "SELECT
   id, datetime(created_at/1000,'unixepoch','localtime') FROM sessions ORDER
   BY created_at DESC LIMIT 5"` for new session ids, and
   `grep -E "ROTATED|WOKE" ~/.hermes/state/carsah_wakes.log` — a file edited
   while the founder believes the loop is stopped is an orphan-session edit,
   not implementer work. Revert or quarantine it before building on it.
3. The rotate script has a SECOND bug that makes the first worse: it
   `sed`-updates `SESSION=` in the auto-wake script and the watcher but NEVER
   its own copy (hit 2026-08-11: rotate script still had `091608` after
   rotating to `171043`, so it counted messages on the retired session
   `964 > 900` and rotated the SAME old session repeatedly, spawning a new
   orphan every 30m). On every rotation/resume, sync `SESSION=` in ALL THREE
   scripts (see the Manual resume section).
4. **MECHANICAL guard beats human discipline (deployed 2026-08-11): add an
   INTENTIONAL-STOP marker file** (`~/.hermes/state/carsah_implementer_stopped`)
   that BOTH loop scripts check FIRST and exit silently if present. The
   founder creates it when holding, removes it when resuming. Do not rely on
   "remember to pause all three crons" — the marker makes the hold
   self-enforcing even if a cron is left scheduled. Both scripts also check
   `pgrep -f "hermes chat --resume"` (ANY implementer session, not
   `$SESSION`) so a rotated session id can never fool the idle check. The
   scripts in `scripts/` carry both guards — copy them, don't re-derive.

Cadence matters too: if the loop is fast and the founder is not watching,
lengthen the poll interval (2m → 10m) so each wake is meaningful and the
mailbox has time to settle — cheaper and calmer, same correctness.


## Turn-budget exhaustion (`max_iterations_reached`) — continue, don't rotate


Distinct failure from corruption (hit 2026-08-08 on CarSah BL-020): the session
is FINE, but the `--max-turns N` budget on the resume command ran out mid-step.
Log shows `Turn ended: reason=max_iterations_reached(150/150)`. The tell: the
process is gone, the tree is DIRTY with real work (many files, e.g. 31:
router + feature screens + tests), and NO commit/SUBMIT was pushed. The
implementer often reports honestly ("غير جاهز للتسليم") before the turn ends.

Recovery — resume the SAME session (it holds the todo + sequencing decisions;
rotation would throw that away):

1. Do NOT rotate. The context is intact; the problem is only the budget.
2. Resume with a CONTINUATION directive (not the fresh-review wake): "واصل من
   حيث توقفت — نفدت ميزانية الدورات قبل إتمام التسليم، وعملك موجود في الشجرة.
   راجع todo الخاص بك …". Explicitly warn about uncommitted work.
3. The pull will fail on the dirty tree — tell it to `git stash push` (named,
   e.g. `BL009-BL020-wip`) → `git pull --rebase` → restore (`stash pop`).
   Never `pull --rebase` over uncommitted work blindly.
4. Ask for logical commit groups, declared (two consecutive steps may land in
   one delivery — name them: e.g. BL-009 then BL-020 — no smuggled files).
5. Raise `--max-turns` on the continuation — GENEROUS headroom, not a tight
   budget. A heavy UI step (first vertical slice + widget tests + an on-device
   walk + CI watch) exhausted 150 then 250 in successive attempts (2026-08-10
   BL-044); the founder's fix was 500, and the coordinator directive now
   launches at 500 by default. Use ~400-500 for steps that include interactive
   device verification — turns are cheap; a mid-step stall costs a wake cycle
   and a dirty-tree continuation.

Compression vs rotation: Hermes auto-compaction IS enabled by default
(config `compression: enabled, threshold 0.5, in_place`) yet a resumed
implementer session still grew 280K→388K input tokens per call — do NOT
assume compaction will rescue a long implementer session. For repo-as-truth
loops, rotation at phase boundaries is the design; compression stays as an
in-session safety net. And the corruption failure was NOT a size problem
(parallel wakes broke the relay scope) — compression cannot prevent it.


## Recovery: re-arming a deadlocked monitor


New failure class (2026-08-08): a tick detects `CHANGED` and starts its agent
run, but the run DIES (provider outage — e.g. 6× `InternalServerError` retries
over ~17 min). The monitor still records the CHANGED hash as "seen" → **every
later tick outputs identical bytes → suppressed forever** (scheduled ticks AND
manual `cronjob action=run`). Meanwhile the scheduler skips ticks while the
job is "already running" (a long API retry chain delays the next tick).

Recovery (deterministic, no marker surgery):
1. Confirm the dead run: `grep "cron_<job_id>_" ~/.hermes/logs/agent.log | tail`
   shows retries then silence; `last_status: error` in the job record.
2. Bump a WATCHED file — update `handoff/STATE.md` (legit state change, note
   the re-arm) and push. `LAST` advances → the monitor's next output differs
   from the recorded hash → the next tick fires the agent again.
3. `cronjob action=run` (manual) to fire immediately instead of waiting a full
   interval.
Do NOT hand-edit `jobs.json` monitor state, and do NOT delete the marker (the
implementer's idempotency guard would then stop it from working). The STATE
bump is the clean re-arm.

Provider-path fallback (2026-08-08): when the coordinator's agent runs keep
failing while the loop must continue (observed: the cron path on provider
`nous` hit repeated Cloudflare `HTTP 524` timeouts while the desktop chat ran
`deepseek` successfully), check `agent.log` for which provider each path
actually uses, then launch the implementer DIRECTLY — the exact coordinator
directive as `hermes chat --resume <SESSION_ID> --reasoning max -q "<directive>"`
in the background — same payload, working provider. The cycle continues while
the coordinator retries; when it recovers it must not double-wake (see the
single-wake-owner rule). Do NOT record "provider X is broken" — the outage is
transient; the durable pattern is "verify the live provider path and carry the
directive through it".

**Move the coordinator OFF a flaky provider (2026-08-09/10).** The coordinator
is a LIGHT task (fetch + marker compare + launch) — it does not need the
session's best model. `hermes config set cron.provider <p>` +
`hermes config set cron.model <m>` moves the cron path to a direct provider
(e.g. the direct DeepSeek API) while the implementer session stays on the
primary. BEFORE pinning a model NAME, verify the provider's actual roster by
calling its OpenAI-compatible `/models` endpoint with the API key (a plain
listing request — never guess the model id). Dated/route-qualified ids do NOT
transfer between providers: `deepseek-v4-flash-0731` is a Nous-routed id; the
direct API serves `deepseek-v4-flash` / `deepseek-v4-pro` (and there is no
`deepseek-chat` either — verify, don't assume). Config keys verified to exist
in the `cron:` section of config.yaml: `cron.provider` / `cron.model`.


## STUCK WATCHDOG — the independent alarm (auto-wake proved unreliable 2026-08-10)


One day produced every wake failure: provider 502/503, stale monitor-state
suppression (cron reported `no_change` while the script manually printed
`CHANGED <new-sha>`), and the implementer sitting idle with a pending review.
The LLM coordinator cannot be trusted to wake reliably. Two layers make the
loop self-alarming:

- **Direct launch is the reliable wake path.** `hermes chat --resume <session>
  -q "<full directive>" -Q --max-turns 250` from the founder-side session
  never failed; the coordinator failed on outages and staleness. When the
  founder reports an idle implementer with a pending review, direct-launch
  FIRST, diagnose the coordinator after.
- **Add a `no_agent` stuck watchdog** (the alarm that needs no LLM): a cron
  job with `no_agent=true`, `script=...`, `schedule=every 5m`,
  `deliver=origin`. The script is SILENT (empty stdout → no delivery) unless
  the latest commit touching the mailbox paths != the marker AND no
  `hermes chat --resume` process is running — then it prints
  `STUCK: unprocessed review (<sha> <subject>) — implementer idle.
  Direct-launch needed.` Non-empty stdout is delivered verbatim; the
  founder-side agent sees it and direct-launches. This is the alarm the
  coordinator cannot be trusted to be. Working script:
  `scripts/stuck_watchdog.sh` (parameterize REPO, MAILBOX_PATHS, MARKER;
  the implementer pgrep intentionally matches ANY `hermes chat --resume`
  because the session id rotates).
- The stale-monitor state self-heals at the next output change (after the
  implementer pushes again the output differs) — but don't wait for it.


## DETERMINISTIC COORDINATOR — replace the LLM coordinator entirely (final fix 2026-08-10)


Four consecutive stalls in one day (provider 502/503, stale monitor-state
suppression, the implementer ending its turn without updating the marker, the
LLM cron agent itself failing) proved the LLM coordinator cannot be trusted to
wake reliably — it is a LIGHT, deterministic job (fetch + marker compare +
launch) that an LLM only makes fragile. **Kill it. Make the coordinator a
`no_agent` cron running a script that does exactly what the founder-side agent
does manually: see the mismatch, send the direct command.** Zero LLM, zero
monitor hash, zero suppression:

- Script `carsah_auto_wake.sh` (see Support files — add it there):
  1. `git fetch -q origin main`
  2. `LATEST=$(git log -1 --format=%H origin/main -- <mailbox paths>)`; if
     `LATEST == $(cat $MARKER)` → exit silently (nothing new / processed).
  3. `pgrep -f "hermes chat --resume <SESSION>"` → exit silently
     (Single-waker: already working — and automatic RETRY next tick if a
     previous wake died, which is exactly the self-healing the LLM version
     lacked).
  4. `git pull --rebase origin main`, then launch in the background:
     `hermes chat --resume <SESSION> --reasoning max -q "$(cat <directive-file>)" -Q --max-turns 500 &`
  5. Append `WOKE <sha>` to a wake log + print one English line (delivered).
- The directive lives in a separate TEXT FILE (the same self-contained
  implementer directive: pull → read brief/STATE/review → load skills →
  idempotency guard → execute → hardened SUBMIT → English Telegram → update
  marker). The script only injects it — the implementer still updates the
  marker itself; if it ends before step 11, the next tick re-wakes and the
  implementer's own guard makes it idempotent (safe, automatic).
- Cron shape: `every 5m`, `no_agent=true`, `script=<auto_wake.sh>`,
  `deliver=origin` (the one-line WOKE info goes to the founder; silence when
  nothing). DELETE the LLM coordinator job and any redundant watchdog —
  one deterministic coordinator, no overlapping alarms. Update `SESSION=` in
  the script on every session rotation (one line — the same single point the
  coordinator used to have).
- This is the pattern's own principle applied to its plumbing: coordination is
  CODE, not conversation. The mailbox made the IMPLEMENTER a commodity; the
  auto-wake makes the COORDINATOR a commodity too.
- **RACE SAFETY between the wake and the rotate crons (2026-08-10).** Two
  no_agent coordinators (wake every 5m + rotate every 30m) can fire in the
  same window at a delivery boundary — the wake would start the OLD bloated
  session while the rotate creates the NEW one = parallel implementers =
  the corruption class. Two guards, both in the scripts: (1) a shared lock
  file (`carsah_loop.lock`) — whichever fires first holds it, the other
  defers to its next tick; (2) ROTATION PRIORITY — the wake script, before
  launching, re-checks the rotation conditions (messages > threshold AND
  tree clean) and DEFERS entirely: the rotate cron will wake a fresh session
  which processes any pending review itself (the standard directive carries
  the idempotency guard). Rotation wins at a boundary; wake wins mid-build.


## Auditor-side automation — the auditor runs its OWN schedule; NEVER create a Hermes cron for it (founder ruling 2026-08-11)


The implementer side has auto-wake + auto-rotate + watchdog, but the AUDITOR side is deliberately manual: Claude Code runs in the project checkout with the `/loop 3m` directive pasted into an interactive session — Claude polls by itself, Hermes needs NO cron for the auditor side. When the auditor's scheduler was deleted, the implementer delivered into a dead mailbox — **half-alive loop: implementer pushing, auditor never reading**. Symptom: `handoff/sulaiman/` advances while `handoff/claude/` never gains a new file and the implementer's wake never fires (its monitor watches the auditor mailbox).

**⚠️ FOUNDER RULING (2026-08-11, after the coordinator tried to "fix" this): DO NOT create a Hermes cron job for the auditor.** An attempted `carsah-auditor-loop` cron (every 3m + monitor_script + headless `claude -p`) was created and then DELETED on explicit founder instruction: "لا تلعب في cron job اللي عندنا لأنها مضبوطة خلاص — اللي أضفته امسحه وثبّت الحالية. أنا طلبت النص اللي أعطي تطبيق كلود علشان يعمل لنفسه جدوله". The four cron jobs are PROTECTED (auto-wake 5m + auto-rotate 30m + stuck-watchdog 5m + pen.dev daily — the last is unrelated to the loop). When asked for "the auditor's scheduler", the answer is the DIRECTIVE TEXT to paste into Claude Code, never new infrastructure. The rule: **a stalled auditor = re-paste the `/loop 3m` directive into Claude Code (or direct-launch it), not a new cron job.**

Correct restoration sequence when the auditor loop dies:

1. Confirm the auditor cron is NOT part of the loop's required set — the loop is THREE Hermes crons (auto-wake, auto-rotate, stuck-watchdog) plus the auditor's own interactive `/loop 3m`.
2. The directive file is the single artifact: `~/.hermes/scripts/carsah_auditor_directive.txt` (full text also in `references/carsah-live-config.md`). Give the founder the TEXT to paste into Claude Code — self-contained: fetch → marker check (`~/.carsah_last_seen_sulaiman`) → pull → read protocol+contract+STATE+newest message → review commits + CI → write verdict in handoff/claude/ → update STATE → push → update marker → gh run watch.
3. Watch ONLY `handoff/sulaiman/` (never STATE.md — the auditor's own STATE updates would self-trigger its next poll). Same shared-tree rule: marker form against origin/main, never `HEAD..origin/main`.
4. If headless invocation is ever needed for a one-off: `claude -p "$(cat ~/.hermes/scripts/carsah_auditor_directive.txt)" --max-turns 100` works (test with `claude -p "Reply with exactly: OK" --max-turns 1` first) — but that is a ONE-SHOT repair tool, NOT a cron pattern.
5. After a hold/resume, `cronjob action=list` and confirm the THREE loop crons exist and are enabled (a cron can vanish silently — the stuck watchdog did 2026-08-11).


## Manual wake: read SESSION= from the script, never from memory (2026-08-12)


After an automatic rotation, the coordinator manually woke the OLD session id (from memory) while the scripts pointed at the NEW one — the old session was bloated/poisoned, the new one held the real context, and the founder asked "did a new session open without me knowing?" Diagnosis of any wake: `grep "^SESSION" ~/.hermes/scripts/carsah_auto_wake.sh` is the single source of truth for the CURRENT session id. Never hardcode an id from an earlier turn; on manual resume/launch, read it from the script first.


## Manual resume after a founder hold (2026-08-11)


When the founder has explicitly paused the loop ("never wake him", hold on
implementer) and later lifts it ("resume the build"), the resume is a manual
rotation + re-arm — do NOT just unpause the wake cron and expect the old
session to continue (it is over the message threshold and was deliberately
stopped). Verified sequence (CarSah, founder lifted the hold at 01:58):

1. Read the LATEST auditor letter first (`ls -t handoff/claude/ | head -1`)
   — the resume directive is only correct if it names the real next step and
   any standing carries (the auditor's letter is the source, never STATE).
2. Clean the tree to a true delivery boundary: remove stray untracked junk
   (e.g. `rm -rf scripts/__pycache__/`) so the rotation-condition check
   (`git status --porcelain` empty) and the new session start clean.
3. Create the fresh session with the lean 10-skill set (see rotation recipe
   step 3) and capture `session_id` from the one-shot ack.
4. **Update SESSION= in ALL THREE scripts — auto-wake, live watcher, AND
   auto-rotate.** The rotate script's own `SESSION=` is the one everyone
   forgets: `carsah_auto_rotate.sh` sed-updates the OTHER two scripts when it
   fires but never ITSELF, so after any rotation it still points at the
   retired session id — the next auto-rotation would count messages on a
   dead session. On a manual resume, sync all three with one `sed -i ''`.
5. Restart the watcher (kill ALL old `carsah_live.sh` processes, start one
   fresh — stale watchers lie "idle" against the old id), then `git pull
   --rebase` and launch the wake: `hermes chat --resume <NEWID> --reasoning
   max -q "$(cat <directive-file>)" -Q --max-turns 500` in the background.
6. **Verify the full cron set came back — the stuck watchdog can vanish
   silently during a hold.** `cronjob action=list` showed the auto-wake job
   PAUSED (founder paused it to stop the loop) AND the `carsah-stuck-watchdog`
   job GONE entirely (script still on disk, cron entry missing). Resume
   auto-wake, recreate the watchdog with the same shape (`no_agent=true`,
   `script=carsah_stuck_watchdog.sh`, `every 5m`, `deliver=origin`).
7. Log the manual wake in the wakes log + one English line to the founder.

The founder's "resume" is a full system re-arm, not a single unpause.


## Wake directive staleness — the implementer refuses an outdated task (2026-08-11)


The deterministic auto-wake injects `$(cat <directive-file>)` on EVERY wake. If that
file still describes the PREVIOUS assignment (e.g. "fix STOP-28") after the review
it served has been resolved and a NEW review has landed, the implementer correctly
refuses to execute — observed: the session replied
«موقفي ثابت — نفس التكليف المنتهي، المرة الحادية عشرة والمائة. لا تنفيذ؛ أتحرك عند
حكم مدقق جديد أو توجيه محدّث فقط» while auto-wake logged `WOKE` eleven times for
the same already-reviewed delivery. The loop looks broken (implementer idle despite
a fresh auditor letter) but the machinery is fine — the MESSAGE it delivers is stale.

Rules:

1. **The directive's END-STATE is a STATIC, source-deriving template — not a per-review rewrite (founder ruling 2026-08-12: "مين المفترض انه يكتب الديركتيف؟").** The final form that ended the recurrence: the directive contains NO step numbers, NO carries, NO situation summary — it tells the session to READ the sources itself (`handoff/STATE.md` + newest `handoff/claude/` letter + the locked table 18 §14b.2) and execute whatever the verdict says, one step per delivery. Per-round hand-written directives were the ANTI-PATTERN: every embedded status went stale the moment the review landed, the implementer (correctly) refused the finished task, and the coordinator's "fix" (rewrite again) produced the poisoned-session loop. Once the static form is in place, the coordinator NEVER edits the directive for a new review — the session finds the new verdict in the mailbox on its own. Only structural changes (protocol, skill set, hard rules) justify an edit.
2. **Make the directive orient, don't embed.** A directive that instructs the session to READ the latest auditor letter first and act on IT (plus a short orientation) stays fresh forever — the letter is the source of truth. If you catch yourself about to write "the new assignment is CARRY-72..76, then BL-070" into the file, stop: that is the stale-rewrite pattern. The session can read those numbers from the mailbox.
3. **"The task is already done" is a DIRECTIVE-STALENESS signal, not implementer
   obstinacy.** If a resumed session refuses with "same finished task", do NOT keep
   re-firing the same wake (11 wasted fires observed) — read the newest auditor
   letter yourself, and if the directive is still in the stale per-review form,
   REPLACE it with the static source-deriving template (above), kill the stuck
   session if it is looping on refusal, and re-launch. If the directive is ALREADY
   static, the refusal means the session is poisoned (see next section) — rotate.
4. The implementer's refusal is CORRECT behavior (it refuses to repeat completed
   work) — the fix is on the coordinator side, never a directive that says "execute
   regardless".


## Poisoned session — after N refusals, ROTATE, do not re-wake (2026-08-12)


The stale-directive case has a WORSE stage. After a session has refused the same
wake ~8 times, its context is full of near-identical user prompts; when the
coordinator finally delivers a genuinely NEW directive (rewritten, naming the new
STOPs), the session may still dismiss it as "نفس التوجيه المكرر (الثامنة) — منفَّذ
ومُسلَّم" — it has learned a refusal pattern and no longer reads the content. Do
NOT keep re-firing the same session with the corrected text:

1. **A session that has refused N times is poisoned — create a fresh session**
   (same lean-skill birth + SESSION= sync in all THREE scripts + fresh watcher),
   and launch the new directive there. Fresh context reads the new text; the
   poisoned context pattern-matches "توجيه محدّث" → refuses.
2. **Check the TOTAL message count, not the active count, before blaming
   auto-rotate.** `carsah_auto_rotate.sh` counts `active=1` messages only;
   compaction marks old messages `active=0`, so a genuinely bloated session
   (1,255 total) showed 677 active and never crossed the 900 threshold — the
   automatic rotation NEVER fired, leaving the poisoned session in place.
   Diagnose with `SELECT count(*) FROM messages WHERE session_id=...` (total),
   and when total > ~900 but active < threshold, rotate MANUALLY. (Fix the
   script's count to total when you touch it.)
3. **Before declaring "the implementer isn't working", check what the newest
   auditor letter actually says** — the loop may be fine and the letter may be a
   REQUEST CHANGES the directive has not yet named. The implementer's "waiting for
   a new verdict" is correct when the verdict exists but was never passed to it.

