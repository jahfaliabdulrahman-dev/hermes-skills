#!/bin/bash
# AUTO-WAKE — the deterministic coordinator for a repo-mailbox loop
# (replaces the fragile LLM coordinator: no LLM, no monitor, no suppression).
# Sees the marker mismatch and sends the direct wake command.
# no_agent cron: non-empty stdout is delivered; empty stdout = silent.
#
# GENERAL TEMPLATE — edit the five vars below for your loop:
#   SESSION      = the implementer's Hermes session id
#   REPO         = the shared repo checkout (both agents use the same tree)
#   MARKER       = a file holding the last-seen review commit (any path)
#   DIRECTIVE    = a text file with the self-contained implementer directive
#   MAILBOX_PATHS = git pathspec of the mailbox dirs + STATE file

SESSION=<your-implementer-session-id>
REPO=/path/to/the/shared/repo
MARKER="$HOME/.hermes/state/<loop>_last_seen"
DIRECTIVE="$HOME/.hermes/scripts/<loop>_wake_directive.txt"
MAILBOX_PATHS="handoff/<auditor>/ handoff/STATE.md"
LOG="$HOME/.hermes/state/<loop>_wakes.log"

cd "$REPO" || exit 0
git fetch -q origin main 2>/dev/null

LATEST=$(git log -1 --format=%H origin/main -- $MAILBOX_PATHS)
[ -z "$LATEST" ] && exit 0
[ "$LATEST" = "$(cat "$MARKER" 2>/dev/null)" ] && exit 0   # nothing new / already processed

# Single-waker: if the implementer is already running, do nothing.
pgrep -f "hermes chat --resume $SESSION" >/dev/null && exit 0

# STALL: a new review exists and the implementer is idle → WAKE DIRECTLY.
git pull --rebase origin main >/dev/null 2>&1
hermes chat --resume "$SESSION" --reasoning max -q "$(cat "$DIRECTIVE")" -Q --max-turns 500 \
  >/dev/null 2>&1 &
echo "$(date +%H:%M:%S) WOKE $SESSION for $(echo $LATEST | cut -c1-10)" >> "$LOG"

# Deliver a short info line to the founder (English only).
echo "Auto-woke implementer for review $(echo $LATEST | cut -c1-10) — processing."
