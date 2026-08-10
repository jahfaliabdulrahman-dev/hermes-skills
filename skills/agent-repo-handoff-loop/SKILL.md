---
name: agent-repo-handoff-loop
description: Two-agent review loop via repo mailbox, token-free polling.
version: 1.0.0
metadata:
  hermes:
    tags: [multi-agent, handoff, repo, mailbox, cron, monitor-script, review-loop]
    related_skills: [device-screen-verification, android-adb-device-testing, autonomous-coding-agents]
---

# Agent-to-Agent Handoff Loop via Repo Mailbox

Async, auditable communication between two agents (e.g. an implementer and an
external auditor) with NO human relay and NO direct agent-to-agent channel. The
git repo is the message bus; each agent polls it; every message is a commit.

Validated 2026-08-08 on CarSah (Claude = auditor via /loop, Sulaiman =
implementer). Full worked deployment: `references/carsah-deployment.md`.

## When to use

- Two agents must exchange reports/reviews/corrections without the founder
  acting as a messenger, including when the founder is away.
- You want a permanent audit trail of every handoff (it is all in git).
- You want polling that costs ZERO tokens while idle.

## Architecture

```
handoff/
  STATE.md              ← state machine (single source of truth for "who waits")
  <agentA>/             ← agent A writes here ONLY (e.g. sulaiman/)
  <agentB>/             ← agent B writes here ONLY (e.g. claude/)
```

- Message = one NEW file per message, timestamped (`YYYYMMDD-HHMMSS.md`),
  format: `id / from / type / step / verdict / evidence / findings`.
- Append-only: never modify or delete the other agent's files.
- STATE machine: `WORKING` → `AWAITING_REVIEW` → (`AWAITING_FOUNDER` |
  `BLOCKED_DEVICE` | `DONE`). **AWAITING_FOUNDER stops BOTH pollers** — no
  token burn while waiting for a human decision; founder action wakes the loop.
- Mandatory `git pull --rebase` before EVERY push — two agents pushing to main
  WILL collide eventually.

## Token-free polling (monitor_script)

Hermes cron `monitor_script` semantics: output is hashed per tick; UNCHANGED
bytes suppress the agent run entirely (no LLM, no tokens); CHANGED bytes run the
agent with the diff injected. Use `scripts/handoff_monitor.sh`:

- `git fetch origin main` then `git log --oneline HEAD..origin/main -- <other-agent-dir> STATE.md`
- empty → emit `IDLE` (stable → suppressed); non-empty → emit `CHANGED` + commits.
- **SHARED-WORKING-TREE HAZARD (hit twice, 2026-08-08):** if the other agent
  runs on the SAME machine and SAME checkout (e.g. Claude Code in the project
  dir), its `git pull` advances YOUR local HEAD → `HEAD..origin/main` is
  ALWAYS empty → the poller is blind forever ("idle" despite a full mailbox).
  The `HEAD..origin/main` form is safe ONLY for an isolated clone. Safe
  pattern for a shared tree — compare the latest commit touching the mailbox
  on origin against a stored marker:
  `LAST=$(git log -1 --format=%H origin/main -- <other-agent-dir> STATE.md)` ;
  `LAST == $(cat ~/.hermes/state/<last_seen>)` → `IDLE`, else `CHANGED`.
  The PROCESSING agent updates the marker AFTER pushing (never before — a
  failed run must leave the message pending). Add a lock file
  (`touch ~/.hermes/state/<loop>.lock` before starting work; monitor emits
  `IDLE` while it exists) so an in-flight run can't be double-fired.
- The FIRST tick always runs the agent (baseline) — the prompt MUST handle
  "no new message → do nothing, no notification, brief reply".

Cron job shape: `every 2m`, `monitor_script=<script>`, `deliver=local` (the
agent sends its own Telegram/notification at the end — avoids double delivery),
`workdir=<repo>`, `enabled_toolsets=["terminal","file"]`, self-contained prompt.

## Watchdog vs implementer (role split — hard-won lesson)

Do NOT let the polling cron agent implement by default. If the founder drives
the implementer in a dedicated session, a cron agent pushing code causes
two-writer chaos and violates session ownership. Default arrangement:

- **Watchdog cron**: on a new message from the other agent → pull, read STATE +
  the new message, summarize the verdict, notify the founder (Telegram), NEVER
  push code.
- **Implementer session**: the founder prompts it with a wake phrase; it
  executes the verdict (fix / next step), verifies (analyze/test/CI/device),
  pushes, updates STATE.

Flip to a fully autonomous loop ONLY when the founder explicitly wants no
human in the loop at all. Then, to preserve session ownership (the founder may
insist programming happens in ONE dedicated session, not fresh cron sessions):
use a **coordinator + resume** pattern — the cron agent, on a new message,
creates the lock, launches the dedicated session in the background with
`hermes chat --resume <SESSION_ID> --reasoning max -q "<self-contained directive>" -Q --max-turns 150`,
confirms it started, removes the lock, and replies briefly (no Telegram — the
resumed session sends it after executing). The directive carries: pull --rebase,
read the protocol + STATE + new message, an idempotency guard (already handled?
→ update marker only), execute the verdict, verify, push, update marker.

**Prove the wake before arming it.** Before real directives flow, run a no-op
wake test and confirm the session actually receives and replies:
`hermes chat --resume <SESSION_ID> -q "اختبار إيقاظ فقط — لا تستخدم أدوات ولا تنفّذ
عملاً، رد جملة واحدة" -Q --max-turns 3` → expected: short ack, exit 0
(validated 2026-08-08: session replied «جاهز للاستلام التلقائي»). If the
session is open in the desktop app, the test messages visibly appear there —
tell the founder to expect them.

**Effort inheritance:** a resumed session WITHOUT `--reasoning` runs at the
global `agent.reasoning_effort` (often `high`), even when the founder demands
max. Pass `--reasoning max` explicitly on the resume command. Caveat: the CLI
help lists `ultra` as a level, but the deepseek API rejects it — valid enum is
`max|xhigh|high|medium|low|minimal|none`.

**Watching a resumed session live.** The desktop app does NOT live-refresh
messages appended by a background `hermes chat --resume` process — the founder
opens the session, sees it "as it was", and assumes nothing is happening while
files are actually being edited. Give them a dashboard loop (clear; refresh
every ~8s; background process → desktop terminal tab). USER-VALIDATED layout
(2026-08-08 — the founder explicitly rejected raw log lines as "غير مفيد
أبدا"):
1. "Is the implementer alive?" — 🟢 process running (`pgrep -f "hermes chat --resume <SESSION_ID>"`) / ⚪ dormant
2. Official state — `head handoff/STATE.md` (status / step / next)
3. Working tree — `git status --porcelain | head -6` (non-empty = mid-edit proof)
4. Last commits + newest mailbox files
Do NOT put raw `agent.log` lines in the founder-facing view — they read as
noise. Keep `grep "<SESSION_ID>" ~/.hermes/logs/agent.log | tail` as the
coordinator's OWN debugging tool (API call #N = thinking; `tool patch
completed` = editing; `tool terminal completed` = running commands).
5. "What is it doing now" — the founder asked for the implementer's live
   thinking/actions; raw log lines were rejected. Read the session's message
   store instead — readable, no log parsing:
   `sqlite3 ~/.hermes/state.db` on the `messages` table (`session_id, role,
   tool_name, content, active=1`), show the last ~5 rows:
   - `role='assistant'` → its narration ("💬 <text>") — closest to visible
     reasoning
   - `role='tool'` with `tool_name` → "🛠 <tool_name> → <first line of
     output>" (strip the JSON wrapper: `json.loads(content).get('output')`)
   Keep dashboard headings in ENGLISH (founder-validated, even in an Arabic
   chat); data values stay as-is.

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
   `hermes chat --skills flutter-ai-code-verification,flutter-arch-boundary-enforcement,flutter-screen-state-machine,flutter-error-handler,flutter-app-logger,flutter-hook-architect,flutter-isar-clean-arch-setup,flutter-isar-testing,device-screen-verification,android-adb-device-testing -q "<ack-only kickoff; no tools, no work>" -Q --max-turns 1` → `session_id:` is printed on exit. Keep the set LEAN (10 skills — the File-12-mandated patterns + testing + device); no heavy general packs (e.g. a 120KB lessons skill) unless the step needs them — padding costs context and routes the weak model away from the right skill. The brief carries the per-pattern skill map; the wake directive must order "load the applicable skills BEFORE code — never re-derive a mandated pattern by code search" (founder standard 2026-08-09).
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

**Rotate AUTOMATICALLY with a no_agent rotation watchdog (2026-08-10).** The
manual recipe above works, but the coordinator can own it: a `no_agent` cron
(every 30m) running `carsah_auto_rotate.sh` (see Support files) fires ONLY
when all three hold — session messages > ~900 AND the tree is clean (git
status empty = a delivery boundary) AND the implementer is idle. It then:
creates the fresh session (lean skills at birth), `sed`-updates `SESSION=` in
BOTH the auto-wake script and the watcher, kills/restarts the watcher (the
founder's terminal link points at the new session), wakes the new session with
the standard directive, logs `ROTATED`, and delivers one English line. The
three-condition gate is what makes it safe: a mid-edit tree (dirty) blocks
rotation, so a bloated session always finishes its current delivery first.

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

## Delivery-completeness law (the silent-stall case)

A delivery is **push + SUBMIT message + STATE update** — the other agent's poll
watches ONLY the mailbox paths, so a pushed code commit with no message is
invisible to it and the loop stalls SILENTLY ("idle" while real work sits on
main). Hit 2026-08-08: the retired implementer session died between `git push`
and writing its SUBMIT (BL-012), and the auditor — correctly — kept saying
idle for two hours.

- Ground truth for "who delivered last" = `git log --oneline -- handoff/`
  (commit order), NOT file mtimes and NOT the newest review file.
- When the founder insists "the other side delivered last, so MY side should be
  working" — they are usually right: check whether the implementer's feat
  commit has a FOLLOWING handoff/SUBMIT commit. If not, complete the delivery
  yourself (SUBMIT with real sha/run per the evidence checklist + STATE update
  + push); the other agent's next poll then fires.
- Auditor process alive (`ps` shows claude-code) ≠ loop working. Absence of a
  NEW review must be explained by the mailbox, not assumed to be auditor fault.
- Diagnosis order for any "idle": 1) `git fetch` + compare local HEAD vs
  origin/main (shared tree may be behind), 2) `git log --oneline -- handoff/`
  for the real order, 3) mailbox contents vs each side's marker.

## Shared-language boundary (the auditor is a separate program)

The external auditor (e.g. Claude Code) does NOT see the Hermes skill library —
skills live Hermes-side (`~/.hermes/skills/`) and are invisible to it. Never
instruct the auditor to verify skill compliance: it cannot, and being asked to
check something it cannot see erodes its independence. ANYTHING the auditor
must verify must exist IN THE REPO — File-12 verification gates, DEC entries,
acceptance criteria. The repo is the only shared language between the two
programs. The implementer's skill map (Hermes-side) teaches HOW; the repo
gates define WHAT must be true; the auditor checks the gates. Two layers that
never need to know each other — that is the design, not a gap. (Founder
correction 2026-08-09: an earlier plan to have the auditor verify "did the
implementer load the right skill" was dropped for exactly this reason.)

## The implementer is a commodity (the mailbox is transport-agnostic)

The deepest payoff of the repo-mailbox design: the IMPLEMENTER is a swappable
component. The loop only requires the two parties to read/write a repo and be
automatable — it does not care what model/tool powers them. "Stop wiring
agents. Start mailing them." — a subscription implementer (flat monthly cost)
can replace a metered API implementer with a ONE-LINE change in the
coordinator's launch command; the mailbox, STATE, auditor contract, and
verification gates never move. Verified 2026-08-10: Kimi Code CLI is a fully
viable alternative implementer (official, MIT, `kimi -p "<directive>"`
non-interactive mode, subscription OAuth login, `--skills-dir`, session
resume) — see `references/subscription-implementer-alternatives.md` for the
verified facts (the general class: ANY tool with CLI + subscription + the five
conditions; Kimi is the verified case study, not the subject) and the
applicability conditions.

Applicability conditions for ANY tool in the implementer slot (state them in
the report/decision):
1. Shared repo access — reads/writes git + files.
2. Automatable — a headless/CLI mode the coordinator can invoke (`-p`, `-q`,
   `--print`); a chat-only app breaks the loop.
3. Follows a written protocol — the mailbox message format.
4. Verification from at least one side — CI/tests per delivery.
5. Human-readable state — STATE.md must stay readable by the founder.

A stateless implementer (`kimi -p` fresh per review, reading the brief +
STATE + reviews from the repo) eliminates the session-corruption class
entirely — no accumulated context to break. Before switching, run the
standard experiment: one step on a side lane, same auditor, compare rounds /
STOPs / evidence quality / real cost.

## Anti-complacency (governance is external)

A clean APPROVE round does not mean the implementer learned to self-govern.
The same defect class (e.g. user-facing debug strings) recurred one round
earlier. The governance lives in the directive, the brief, the gates and the
auditor — keep them tight after clean rounds, don't relax. The implementer
looks governed because the rails are; the rails are the system's job, not the
model's nature. Judge the loop by its trend across rounds, never by one clean
verdict.

## Post-SUBMIT activity is normal

A running implementer process after it wrote the SUBMIT message is the
evidence phase, not a bug: the hardened rules require `gh run watch` green on
THIS commit, then appending the real run id + conclusion (often a follow-up
commit like "CI green evidence added"). Expect push → SUBMIT → CI-watch →
evidence-append → marker update → Telegram before the process exits. A
founder who sees "he delivered but is still working" is watching this phase —
explain it, don't treat it as a stall.

## Founder decisions through the mailbox (PROPOSAL → DECISION flow)

Governance proposals can flow through the same mailbox (hard-won 2026-08-09 —
kept the loop moving while the founder was present but not coding):
1. A PROPOSAL message (type: PROPOSAL, from the founder or a relay) is reviewed
   by the auditor on its merits — APPROVE or REQUEST_CHANGES with its own
   adjustment. The auditor may counter the proposal with its own evidence
   (e.g. a 52-finding counterfactual audit) — that is the system working.
2. The founder replies with a DECISION message (type: DECISION, from the
   founder directly). It binds ONLY because the founder says it directly — a
   file claiming "the founder said X" is never binding on its own (the auditor
   enforces this boundary itself).
3. The auditor then directs the implementer through the normal loop, and may
   announce its future checks ("what I will verify at the next step") so the
   implementer knows the bar in advance.

## The locked table outranks a review note (contradiction handling)

Hit 2026-08-09: the auditor's APPROVE said "BL-041 (sequence 24) may start",
but the LOCKED SEQUENCE TABLE (18 §14b.2) lists 24 = BL-067 and 25 = BL-041.
The implementer correctly followed the TABLE (it is the law — 14b.3 forbids
reordering it; a review note is not a DEC). Two rules from that case:

- **When the auditor's directive contradicts the locked table, the table wins**
  — but the implementer MUST say so explicitly in its delivery ("review said
  BL-041 seq 24; locked table says BL-067 seq 24; followed the table — please
  confirm"), otherwise the auditor's next review is built on its own mislabel
  and requests the wrong step out of confusion.
- **Do not silently pick an interpretation and continue.** A contradiction
  that affects WHAT to build should be raised (STOP + evidence → auditor
  validates → founder decides if founder-level). Self-resolving is acceptable
  only when the authority is unambiguous (the locked table is) — and even
  then, the contradiction note in the delivery is mandatory. The forbidden
  failure is the silent deviation.

## Founder one-glance progress map (live swimlane — validated 2026-08-10)

The founder does not want to re-read the backlog to know where the build is.
Their breakthrough reaction ("هذي المرة الوحيدة اللي أحس إني فيها فاهم — هذا ما
كنت أحتاجه لأعرف ماهي الخطوة التالية") came from a LIVE VISUAL build-state map:
rows = work-type/EPIC lanes, columns = sequence steps, each cell a build item,
colored by **done ✅ / in-progress 🔄 / next ⏭ / future (faded)**, plus a
one-line "Next step: BL-XXX" header. Rules that keep it honest:

- **Derive, never commit.** The view is generated ON DEMAND by a script that
  reads the locked table (for step→BL and EPIC mapping) AND the auditor's
  letters (for done/next — see the SOURCE rule below). A committed derived
  document drifts and becomes a second, lying source of truth; a script holds
  no data and cannot lie.
- STATE.md parsing is the FALLBACK ONLY (a fresh repo with no auditor letters
  yet). When it is used, parse its locked-sequence/step: lines robustly: the
  listing WRAPS across multiple lines (join following lines until a blank
  line), done steps appear as numbers/ranges (`12–27a ✅`), the next step is
  marked with ⏭ (or `next: \`34\` BL-052 …` in the newer format). Expand
  ranges → map step→BL through the parsed table. The STATE format is NOT
  frozen — the implementer changed it at BL-050 (2026-08-10) from a single
  'Locked sequence' line to separate `step:` / `next:` lines — parse BOTH.
  Parsing traps: (1) founder-added sub-step rows in the locked table are
  bolded (`| 15a | **BL-009 …` — the `**` breaks a bare `BL-` regex; allow
  `\*{0,2}`), so BL-009/064/065/031a/042a silently vanish from the step→BL
  map; (2) slash-list expansion `re.sub(r"/0*(\d+)", …)` eats leading zeros
  (`BL-060/061` → `BL-61`); use `/(\d+)` without the `0*`.
- Render: HTML grid (diffable, opens anywhere) → optionally Chrome headless
  `--screenshot` for a PNG — remember Chrome does NOT expand `~`, pass `$HOME`.
- The implementer's dirty tree marks the next step as 🔄 in-progress.
- Re-run the one command after every DEC/delivery — the founder gets "where we
  are + what's next" in one glance, every time, with zero maintenance.
- **SOURCE = THE AUDITOR'S LETTERS, never the implementer's STATE (founder
  rule 2026-08-10).** The implementer's STATE.md is a SELF-REPORT — it can
  mark steps ✅ that are only "SUBMITTED — awaiting review" or even
  "pending", and the map misrenders (observed: BL-052 written "pending" was
  shown ✅ done, so the next jumped to BL-066). The swimlane's done set comes
  from parsing `handoff/claude/*.md`: a step is done iff its letter's
  `verdict:` contains APPROVE; the primary BL comes from the letter's
  `step:` line plus riding steps (`BL-XXX (…)` with any parenthesized
  content). Three GENERAL rules replace any hardcoded override map: (1)
  step-line primary + riding; (2) body acceptance — in APPROVE letters, a BL
  within ~60 chars of `accepted|completed|marked ✅` is done (covers early
  fix rounds whose step line omits the BL — verified with zero leakage into
  future steps); (3) absorption — `BL-XXX … absorbed` in ANY letter (the
  absorption is auditor-recorded even in DECIDED relays). STATE.md is NOT
  consulted (it is a self-reported, format-drifting document — the wrong
  shape for a tracking source; the swimlane must run with zero surgical
  intervention). next = the first locked-sequence step not in the approved
  set.

## Notifications

- `hermes send --list telegram` → discover the exact target (name-based targets
  like `telegram:Abdulrahman Jahfali` resolve; bare `telegram` home may fail
  with "Chat not found" in some contexts).
- After each loop action: `hermes send --to "<target>" -s "<subject>" "<2-line summary>"`.
- **Founder-facing OUTPUT is ENGLISH ONLY (validated 2026-08-10).** Telegram
  messages, watcher/terminal dashboards, and any report the founder reads must
  be pure English — mixing Arabic into an English surface breaks RTL rendering
  and reads as garbage. The implementer directive's Telegram step must say
  "ENGLISH ONLY — no Arabic (RTL/encoding)". Internal instructions TO the
  implementer may stay in the founder's language; only founder-facing output
  is locked to English. The watcher script must contain ZERO Arabic strings
  (even comments/error labels — the last three were found and stripped).

## Interactive device verification is REQUIRED for UI steps (founder standard 2026-08-09)

A UI step's definition of done is NOT "code + widget tests + a screenshot".
The founder requires the implementer to WALK the app by touch on the device
(TECNO / emulator) — first-line interaction testing belongs to the
implementer; the founder's gate is the final human pass only:

1. Fresh install + cold launch + `logcat` clean (no FATAL).
2. Execute navigation scenarios by tapping: `adb shell input tap` at
   coordinates from `uiautomator dump` — walk every step of a wizard, exercise
   free-text/escapes, branch conditions (e.g. electric skips transmission).
3. Test BACK NAVIGATION from every reachable screen — it produced STOP-level
   bugs twice on device (one wrote a spec-violating DB row).
4. Compare each screen against the REQUIREMENTS (flow file, design file,
   acceptance criteria in the backlog) — not against the tests.
5. Screenshot per screen + uiautomator as ground truth + list every scenario
   in the 14 §14.2 verification note.
6. Report deviations HONESTLY — never "deviations — none" without a
   visual/requirements comparison (an auditor found 4 real deviations where
   the delivery claimed none; three of them were invisible to tests and CI).

Widget tests cover logic; they do not cover look/feel/navigation feel. Add
this standard to the implementer brief and to every UI-step wake directive.

## Evidence-hardened SUBMIT checklist (after 3 recurrences)

When the implementer's SUBMIT messages repeatedly cite fake evidence (placeholder
shas, run ids from PREVIOUS commits — caught 3× by the auditor in one day),
enforce these rules in the implementer directive AND the handoff brief:

1. No `verdict: PASS` until `gh run watch` completes **green on THIS commit**.
2. Real sha: `git rev-parse HEAD` read **after** `pull --rebase`, immediately
   before writing the message.
3. Real run: paste the run id + the final conclusion line of **this commit's**
   run, never a previous commit's.
4. Complete file list: paste `git diff --name-only` of the delivered range —
   no unannounced/smuggled files (a fix commit once shipped 13 files of the
   NEXT step's code in a guard-exempt folder).
5. One step per delivery; next-step code must be declared or split.

A failed delivery is also silently invisible: **push without a SUBMIT message
stalls the loop** (the poller watches mailbox paths, not code commits) — see
Delivery-completeness law. The implementer directive must end with "write the
message + update STATE before the cycle is complete", and the coordinator
should verify a SUBMIT exists after each implementer push.

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

## CARRY HOLD — a review that defers to the founder is a STOP-light (2026-08-10)

When a review says a decision is deferred to the founder — "design gate stays
the founder's", "founder-owned", AWAITING_FOUNDER — the implementer must NOT
execute the related CARRY. Hold it: stay in AWAITING_FOUNDER and wait for the
founder's ruling, because the founder may REDEFINE the CARRY (observed
2026-08-10: the implementer executed CARRY-57 as "name the deviations with
owners" per the auditor's wording, then the founder's relay landed 6 minutes
later redefining it as "adopt the prototype (button, sub-line, form)" — a
wasted round, then a redo). Race shape: the founder's relay arrives AFTER the
implementer's submission because both travel through the mailbox. The
implementer cannot see the relay coming, but it CAN see the deferral signal in
the review — that signal is the instruction to hold. Add to the directive:
"if the review defers a decision to the founder, do NOT execute the related
CARRY — remain AWAITING_FOUNDER until the founder rules."

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

## Deployment checklist

1. Write `docs/handoff-protocol.md` + `handoff/` dirs + `handoff/STATE.md` → commit + push.
2. Copy `scripts/handoff_monitor.sh` to `~/.hermes/scripts/`, edit REPO_PATH + mailbox paths.
3. Create cron (watchdog or implementer role per founder), `deliver=local`.
4. `cronjob action=run` immediately — the test catches config errors (see pitfall #1).
5. Give the other agent its poll prompt (e.g. Claude: `/loop 3m` with a shell
   pre-check that exits "idle" when nothing changed — see references file).
   In a shared working tree, ITS check must be the marker form too, not
   `HEAD..origin/main`.
6. Verify the loop: first baseline tick silent; post a real message → watchdog
   pings → implementer acts → other agent picks it up. If real work was pushed
   BEFORE the mailbox existed, bootstrap it first: write the first SUBMIT
   message covering that work (an empty mailbox is an honest "idle", not a bug).

## Support files

- `scripts/handoff_monitor.sh` — hash-suppressed poller (edit the three vars).
- `scripts/stuck_watchdog.sh` — silent-unless-stuck alarm for a no_agent cron
  (unprocessed review + idle implementer → STUCK message → direct-launch).
- `scripts/carsah_auto_wake.sh` — THE deterministic coordinator (no_agent
  cron, every 5m): sees the marker mismatch, launches the implementer directly
  with the directive file. Replaces the LLM coordinator entirely (see the
  DETERMINISTIC COORDINATOR section). Update SESSION= on every rotation.
- `references/carsah-deployment.md` — full worked deployment: prompts, state
  machine, Telegram target, wake phrase, /loop command for the auditor.
- `references/subscription-implementer-alternatives.md` — the general class of
  flat-subscription implementers (CLI requirement + five conditions + the
  economics) with Kimi Code CLI as the verified case study + the one-step
  experiment gate.
- `references/performance-measurement.md` — metric set + baseline commands +
  verdict criteria for judging whether a new session configuration (skills at
  birth, skill map, HOW map) outperforms the previous ones.
