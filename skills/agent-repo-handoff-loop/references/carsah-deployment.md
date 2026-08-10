# CarSah deployment — worked example (2026-08-08, FINAL architecture)

Concrete deployment of the repo-mailbox loop. Repo: jahfaliabdulrahman-dev/carsah.

## Committed artifacts (in the repo)

- `docs/handoff-protocol.md` — the protocol contract (message format, state
  machine, cadence, hard rules).
- `docs/claude-auditor-contract.md` — the auditor's standing role contract
  (Claude = external auditor: verify with evidence, red-team vs spec files,
  classify findings 16 §6a STOP/CARRY/ACCEPT, verdicts APPROVE /
  APPROVE_WITH_NOTES / REQUEST_CHANGES; never implement, never reorder the
  locked sequence). Must include a **"Where to find the changes"** section:
  BL-prefixed commits on main (`git log --oneline -10`, `git diff HEAD~3..HEAD`),
  CI via `gh run list`/`gh run view`, acceptance notes (14 §14.2) in commit
  bodies, screenshots delivered via Telegram/local — NOT committed; a missing
  or vague acceptance note is itself a finding.
- `handoff/STATE.md` + `handoff/sulaiman/` + `handoff/claude/` — mailboxes.

## Coordinator cron (Sulaiman side — final role)

- Job `carsah-loop-coordinator` (renamed twice: poller → watchdog →
  coordinator, tracking the founder's decisions). Schedule `every 10m`
  (founder decision 2026-08-08 — was 2m), `monitor_script=carsah_handoff_monitor.sh`,
  `deliver=local`, `workdir=/Users/abdurrahmanjahfali/Projects/CarSah`,
  toolsets terminal+file.
- Role: on a new handoff/claude/ message → `git pull --rebase` → **skip if the
  implementer is already running** (`pgrep -f "hermes chat --resume <SESSION>"`
  — single-waker rule, hard-won 2026-08-09: parallel wakes corrupt the relay) →
  touch `~/.hermes/state/carsah_loop.lock` → launch the implementer session in
  the background:
  `hermes chat --resume 20260809_210102_1126c8 -q "<self-contained directive>" -Q --max-turns 250`
  → confirm it started → remove the lock → brief reply. NO Telegram from the
  coordinator — the resumed session sends it after executing.
- The directive (current): pull --rebase (stash-aware — the tree may hold the
  previous session's work) → read brief + protocol + STATE + newest review →
  **load the applicable skills from the brief's skill map BEFORE code (never
  re-derive a mandated pattern by code search)** → idempotency guard →
  execute verdict → verify (analyze/test/CI-watch/**interactive device walk —
  founder standard 2026-08-09**) → write handoff/sulaiman/ reply + STATE →
  push → `gh run watch` → informational Telegram → update marker.
- Monitor script: marker-based (origin/main latest commit touching
  handoff/claude/ + STATE.md vs `~/.hermes/state/carsah_last_seen_claude`),
  plus lock check → IDLE while the lock exists. Deadlock recovery: if a tick
  detects CHANGED but the agent run dies (provider outage), re-arm by bumping
  STATE.md (advances LAST → next tick fires) — never hand-edit the monitor
  state.

## Implementer session

- Current session `20260809_210102_1126c8` — the founder insists programming
  happens in a DEDICATED session (never in fresh cron sessions). Rotation
  history: `20260808_035645_d57403` → `20260808_112219_30b1bb` →
  `20260808_220333_60877a` → `20260809_103806_24dd79` (retired at 2183
  messages — the record) → `20260809_210102_1126c8` — retired on corruption
  (relay "session scope close failed" at high message counts, twice) and
  PROACTIVELY once the session approaches ~700-900 messages (rotation recipe,
  main SKILL.md). The 2026-08-09 evening rotation was the first to create the
  fresh session WITH the lean `--skills` set (rotation recipe step 3) — born
  with its skill index populated; the rotation also required killing a stale
  duplicate watcher that displayed "⚪ idle" against the retired id.
- **Wake test (proven 2026-08-08):** `hermes chat --resume <id> -q "اختبار
  إيقاظ فقط — لا تستخدم أدوات ولا تنفّذ عملاً، رد جملة واحدة" -Q --max-turns 3`
  → session replied «جاهز للاستلام التلقائي», exit 0. Always run this no-op
  test before arming real directives.
- **Create fresh sessions WITH the lean skill set** (see main SKILL.md rotation
  recipe — `--skills` with the 10 File-12/testing/device skills, no fluff).
- The directive: pull --rebase → read protocol + contract + STATE + newest
  message → idempotency guard (marker matches, or a reply to this review
  already exists → update marker only) → execute verdict → verify
  (analyze/test/CI-watch/device) → write handoff/sulaiman/ reply + STATE →
  push → `gh run watch` → informational Telegram → update marker.

## Auditor side (Claude) — /loop prompt, MARKER-BASED (corrected)

The FIRST version used `git log HEAD..origin/main -- handoff/sulaiman/` and
reported "idle" forever: Claude Code runs in the SAME shared checkout, its
`git pull` keeps local HEAD == origin/main, so HEAD-relative logs are always
empty. Corrected prompt:

```text
/loop 3m نفّذ بالترتيب (Bash حقيقي، لا تخمين):
REPO="/Users/abdurrahmanjahfali/Projects/CarSah"
0) اختبار ذاتي (أول مرة): ls "$REPO/handoff/sulaiman/" — إن فشل: قل PATH_ERROR وتوقف.
1) git -C "$REPO" fetch origin main 2>&1 | head -5        ← بدون -q (الأخطاء تظهر)
2) LAST=$(git -C "$REPO" log -1 --format=%H origin/main -- handoff/sulaiman/)
   MARKER="$HOME/.carsah_last_seen_sulaiman"
3) إن كان "$LAST" = "$(cat "$MARKER" 2>/dev/null)" → قل "idle" فقط وتوقف.
4) وإلا: pull --rebase → اقرأ protocol + contract + STATE + أحدث رسالة →
   راجع الالتزامات (git log/diff) → افحص CI (gh run list/view) →
   اكتب حكمك في handoff/claude/<ts>.md (id/from/type/step/verdict/evidence/
   findings، كل finding بصنف 16 §6a ومصدر) + حدّث STATE.md →
   push (pull --rebase أولًا) → echo "$LAST" > "$MARKER" (بعد الدفع فقط!) →
   gh run watch.
قواعد: لا تكتب كودًا؛ لا تغيّر التسلسل المقفَل؛ handoff/sulaiman/ قراءة فقط؛
AWAITING_FOUNDER عند حاجة قرار مالك.
```

Watch ONLY `handoff/sulaiman/` (not STATE.md) — Claude's own STATE updates
would otherwise self-trigger its next poll.

## Telegram target

`hermes send --list telegram` → `telegram:Abdulrahman Jahfali` (name-based
works; bare `--to telegram` failed with "Chat not found" in the desktop context).

## Config fix that was required

First cron baseline run failed: HTTP 400 `reasoning.effort: Invalid option:
expected one of "max"|"xhigh"|"high"|...` — config had
`agent.reasoning_effort: ultra` (invalid for deepseek). Fixed with
`hermes config set agent.reasoning_effort high`; next run `last_status: ok`.

## Evidence chain used by both agents

- Every step lands as a BL-prefixed commit; acceptance note (14 §14.2: build
  hash, device, scenarios, PASS/FAIL) in the commit body.
- Device verification: TECNO LJ7 or emulator `test_avd` (same adb pipeline);
  screenshots delivered via Telegram + /tmp, NOT committed.
- First real audit value (Claude REVIEW of BL-001/002): APK byte-identity
  reproduced two independent ways (pulled live install + clean rebuild), 12/12
  tests by name, adversarial flag probe planted+deleted, and a genuine STOP-1
  on the CI guard (tip-only check skips build for multi-commit pushes) — the
  external-audit loop caught what self-review missed.
