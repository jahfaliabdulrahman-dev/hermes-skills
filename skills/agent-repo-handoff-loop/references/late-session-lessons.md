# Late-session lessons (CarSah 2026-08-08, afternoon rounds)

## Single wake owner — the double-wake incident

If the OTHER agent also holds the resume mechanism (Claude Code can run
`hermes chat --resume` too, and the protocol may grant it the wake), ONE
message can wake the implementer TWICE — auditor direct wake + coordinator
wake — producing two parallel implementer sessions and duplicate SUBMITs for
the same commit (observed: messages 123016 + 123024; the implementer noticed
and documented the duplication itself; same sha, CI green, no corruption but
audit-trail noise).

Rule: exactly ONE wake path per loop. If the other agent insists on waking
directly, the coordinator must check for an already-running implementer at
LAUNCH time (lock file consulted by the launcher, not only by the monitor)
and skip its own wake.

### The escalation: noise → corruption → 8h silent deadlock (same day)

The 123016/123024 duplicate looked harmless ("no corruption but audit-trail
noise") — it was not. ~1h later the SAME session corrupted: 13:21:55 logged
`Hermes Relay session ... closed with errors: session scope close failed`.
From that moment every `hermes chat --resume <same-id>` died INSTANTLY with
ZERO API calls (no `turn_context`, no commits). The coordinator fired once
(13:37), its launch "succeeded" from its own view (process existed briefly
then vanished), and the monitor's hash suppression then silenced every later
tick → ~8 HOURS of deadlock: no commit, no message, no Telegram. The founder
returned at night asking "ليش سليمان وقف؟".

Corrupted-session diagnosis (the "why did the implementer stop" checklist):
1. `ps aux | grep "hermes chat --resume"` → no process.
2. `grep "<SESSION_ID>" ~/.hermes/logs/agent.log | tail` → last real activity
   (API call / turn_context) HOURS ago; nothing since.
3. Coordinator output files → all `no_change (agent run suppressed)` — the
   change was seen but the launch died, and suppression hides it.
4. `git log --oneline -- handoff/` → no new implementer commit since the last
   approval; Claude's review IS waiting (the work was authorized the whole time).

Fix (do not retry the same id): create a fresh session
(`hermes chat -q "<ack-only>" -Q --max-turns 1` → capture printed id),
re-point the coordinator's resume target, update the live-watcher `SESSION=`
line, launch directly. Record the single-waker rule + retirement procedure in
`docs/handoff-protocol.md` so the next reader doesn't rediscover it.

## Full AWAITING_FOUNDER cycle (validated)

The auditor escalates a spec contradiction (CarSah: DEC-004 vs 17 §3.1 —
nested writeTxn ownership) → the founder decides, and the decision lands as a
DEC-amendment commit (option B: exactly one transaction owner per operation)
→ the auditor records "founder gate closed — both pollers resume" and the
implementer continues per the amended decision, citing it in the fix.

The escalation is a designed checkpoint, NOT a stall: its exit is the decision
commit itself, and the review that follows cites it. When the founder asks
"did Sulaiman push?" after such a round, the answer's ground truth is
`git log --oneline -- handoff/` (commit order), not the newest review file.

## Related governance pattern: founder-requested recording

When the founder asks to "record it, but make it tight" (محكم), record the
item as a numbered-rules DEC (e.g. DEC-055 — dependency refresh is post-MVP,
gated, never mid-sequence) + a dated observation under the owning backlog
step (e.g. BL-003). Rules style: timing, scope, major-version gate (new DEC
before the bump), rollback path, same-commit rule, loop gates apply.
