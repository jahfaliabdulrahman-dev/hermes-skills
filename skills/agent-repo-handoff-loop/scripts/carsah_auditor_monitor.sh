#!/bin/bash
# Auditor-side handoff monitor — deterministic wake for the EXTERNAL auditor
# (e.g. Claude Code). Mirrors the implementer-side handoff_monitor.sh but
# watches the IMPLEMENTER's mailbox (handoff/sulaiman/) and is meant to feed a
# Hermes cron whose agent then invokes the auditor headless.
#
# Deployed 2026-08-11 (CarSah): founder noticed the auditor scheduler was
# deleted while the implementer delivered into a dead mailbox — the loop was
# half-alive. This monitor + a cron (every 3m, monitor_script=this,
# enabled_toolsets=[terminal], workdir=<repo>) + `claude -p "$(cat <directive>)"`
# restores the full loop with ZERO tokens while idle.
#
# PROVEN FAILURE MODES (do not "fix"):
# - The auditor runs in the SAME shared checkout; its `git pull` advances
#   local HEAD -> `git log HEAD..origin/main -- <dir>` is ALWAYS empty.
#   MUST use the marker form (latest commit touching the mailbox on origin vs
#   a stored marker).
# - Watch ONLY the implementer mailbox (handoff/sulaiman/) — never STATE.md:
#   the auditor's own STATE updates would self-trigger its next poll.
# - The lock file is shared with the implementer side: if a loop run is in
#   flight, do nothing (no double work).

REPO="/path/to/the/shared/repo"        # <-- edit
MAILBOX="handoff/sulaiman"             # the IMPLEMENTER's mailbox
MARKER="$HOME/.<name>_last_seen_sulaiman"  # <-- edit (auditor-side marker)

cd "$REPO" || { echo "PATH_ERROR"; exit 1; }
[ -f "$HOME/.hermes/state/<loop>.lock" ] && { echo "IDLE (lock)"; exit 0; }

git fetch origin main 2>&1 | head -5
LAST=$(git log -1 --format=%H origin/main -- "$MAILBOX")
[ -z "$LAST" ] && { echo "IDLE (no mailbox history)"; exit 0; }
[ "$LAST" = "$(cat "$MARKER" 2>/dev/null)" ] && { echo "idle"; exit 0; }

echo "CHANGED $LAST — new implementer delivery to review."
