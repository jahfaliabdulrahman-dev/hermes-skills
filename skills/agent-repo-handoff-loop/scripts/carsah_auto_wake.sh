#!/bin/bash
# CarSah AUTO-WAKE — the deterministic coordinator (replaces the LLM coordinator).
# Sees the marker mismatch and sends the direct wake command — exactly what the
# coordinator does manually, but as code: no LLM, no monitor, no suppression.
# no_agent cron: non-empty stdout is delivered; empty stdout = silent.
#
# RACE SAFETY (2026-08-10): shares carsah_loop.lock with the auto-rotate cron —
# whichever fires first holds the lock; the other defers to its next tick.
# PLUS: if the rotation conditions already hold (bloated session + clean tree),
# this script DEFERS entirely — the rotation will wake a fresh session which
# processes any pending review itself (its directive carries the guard).
#
# SESSION must be updated here whenever the implementer session rotates.

SESSION=<your-implementer-session-id>
REPO=/path/to/the/shared/repo
MARKER="$HOME/.hermes/state/carsah_last_seen_claude"
DIRECTIVE="$HOME/.hermes/scripts/carsah_wake_directive.txt"
LOG="$HOME/.hermes/state/carsah_wakes.log"
LOCK="$HOME/.hermes/state/carsah_loop.lock"
THRESHOLD=900

cd "$REPO" || exit 0

# Mutual exclusion with the auto-rotate cron.
[ -f "$LOCK" ] && exit 0
touch "$LOCK"; trap 'rm -f "$LOCK"' EXIT

git fetch -q origin main 2>/dev/null

LATEST=$(git log -1 --format=%H origin/main -- handoff/claude/ handoff/STATE.md)
[ -z "$LATEST" ] && exit 0
[ "$LATEST" = "$(cat "$MARKER" 2>/dev/null)" ] && exit 0   # nothing new / already processed

# Single-waker: if the implementer is already running, do nothing.
pgrep -f "hermes chat --resume $SESSION" >/dev/null && exit 0

# ROTATION PRIORITY: a bloated session at a clean boundary is the rotate cron's
# job — defer the wake; the fresh session will handle any pending review.
COUNT=$(sqlite3 "$HOME/.hermes/state.db" "SELECT count(*) FROM messages WHERE session_id='$SESSION' AND active=1" 2>/dev/null || echo 0)
if [ "${COUNT:-0}" -gt "$THRESHOLD" ] && [ -z "$(git status --porcelain | grep -v '.hermes/desktop-attachments')" ]; then
  exit 0   # rotation owns this tick
fi

# STALL: a new review exists and the implementer is idle → WAKE DIRECTLY.
git pull --rebase origin main >/dev/null 2>&1
hermes chat --resume "$SESSION" --reasoning max -q "$(cat "$DIRECTIVE")" -Q --max-turns 500 \
  >/dev/null 2>&1 &
echo "$(date +%H:%M:%S) WOKE $SESSION for $(echo $LATEST | cut -c1-10)" >> "$LOG"

# Deliver a short info line to the founder (English only).
echo "Auto-woke implementer for review $(echo $LATEST | cut -c1-10) — processing."
