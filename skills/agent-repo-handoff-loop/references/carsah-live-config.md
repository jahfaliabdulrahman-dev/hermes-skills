# CarSah Live Loop Configuration — the working system (as of 2026-08-11)

This is the CURRENT, verified configuration of the CarSah closed loop. The founder
explicitly protects it: **do not create new cron jobs, do not modify these four, do
not "improve" the loop.** The loop works; every "improvement" attempt so far cost
a day.

## The loop (one sentence)

The implementer executes and pushes → Claude (the auditor) polls, reviews, writes
its verdict and pushes → the auto-wake cron wakes the implementer for the next step
→ repeat. Founder role: zero (except AWAITING_FOUNDER decisions).

## The four cron jobs (Hermes) — DO NOT TOUCH

| Job | Schedule | Role |
|-----|----------|------|
| `carsah-auto-wake` | every 5m | Deterministic coordinator — sees a new `handoff/claude/` letter → wakes the implementer session (direct launch with the directive) |
| `carsah-auto-rotate` | every 30m | Retires a bloated implementer session (>900 msgs) at a clean delivery boundary; updates SESSION in ALL THREE scripts (self-update fix 2026-08-11) |
| `carsah-stuck-watchdog` | every 5m | Silent alarm — reports STUCK only when a review is unprocessed AND no implementer is running |
| `pen.dev wave2 generation` | daily 22:00 | Unrelated (design generation) — do not confuse with the loop |

All three loop crons are `no_agent` scripts under `~/.hermes/scripts/`. The lock
file `~/.hermes/state/carsah_loop.lock` prevents double work (shared with the
auditor side). The intentional-stop marker `~/.hermes/state/carsah_implementer_stopped`
stops ALL waking/rotation when the founder stops the implementer on purpose.

## Claude (auditor) — runs its OWN schedule, no Hermes cron

Claude Code runs in the project checkout with the `/loop 3m` directive below pasted
into an interactive session. Claude polls by itself; Hermes needs NO cron for the
auditor side.

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
Watch ONLY handoff/sulaiman/ (not STATE.md) — Claude's own STATE updates
would otherwise self-trigger its next poll.
```

Saved copy: `~/.hermes/scripts/carsah_auditor_directive.txt`.

## Markers (the shared-tree safety)

| Marker | Owner | Meaning |
|--------|-------|---------|
| `~/.hermes/state/carsah_last_seen_claude` | implementer side | latest commit touching `handoff/claude/` + STATE.md that was processed |
| `~/.carsah_last_seen_sulaiman` | Claude side | latest commit touching `handoff/sulaiman/` that was reviewed |
| `~/.hermes/state/carsah_loop.lock` | both | loop run in flight — suppress |
| `~/.hermes/state/carsah_implementer_stopped` | founder | intentional stop — suppress ALL waking/rotation |

## Proven failure modes (do NOT "fix")

1. **Shared checkout blindness:** Claude runs in the SAME checkout; its `git pull`
   advances local HEAD → `git log HEAD..origin/main -- handoff/sulaiman/` is ALWAYS
   empty. Marker-based compare against origin/main is mandatory.
2. **Watch ONLY `handoff/sulaiman/` on the auditor side** — watching STATE.md
   self-triggers (Claude updates STATE itself).
3. **Marker AFTER push, never before** — a failed run must leave the message pending.
4. **Orphan sessions (2026-08-11):** `auto-rotate` previously rotated from a stale
   SESSION forever because it updated only auto-wake + live, not itself — and it did
   not know about intentional stop. Both fixed: self-update + stop-marker + pgrep
   matches ANY implementer session, not one specific id.
5. **A wrong directive is worse than no directive:** a rule written as doctrine
   propagates perfectly (STOP-28: 44 sites in 13 files copied "pump inside runAsync"
   faithfully). The repo is the ONLY shared language; the auditor cannot see Hermes
   skills — anything it must verify must exist IN THE REPO.

## Cadence & budget

- Auditor poll: every 3m (idle = one line, near-zero cost).
- Implementer wake: 5m cron + direct launch (the path that never failed).
- Rotation: 30m check, only at a clean delivery boundary (>900 msgs).
- Founder notifications: Telegram `telegram:Abdulrahman Jahfali` — English only.

## Contact points (if something looks wrong)

- Check `~/.hermes/state/carsah_wakes.log` — every wake/rotation is logged.
- Check `pgrep -f "hermes chat --resume"` — exactly ONE implementer session must run.
- Check `pgrep -f carsah_live.sh` — the watcher terminal must be alive.
- Do NOT create new crons for the loop. If the loop stalls, the stuck-watchdog
  reports it; the fix is a direct launch, not a new job.
