#!/bin/bash
# Stuck watchdog — SILENT unless a review is unprocessed AND no implementer is running.
# For a no_agent cron: non-empty stdout is delivered verbatim; empty stdout = silent.
# The LLM coordinator's auto-wake proved unreliable (provider 502/503 + stale monitor
# suppression, 2026-08-10) — this watchdog is the independent alarm: it reports STUCK
# so the founder-side agent can direct-launch the implementer (the path that never failed).
#
# Edit these three for your loop:
REPO="/path/to/the/shared/repo"
MAILBOX_PATHS="handoff/claude/ handoff/STATE.md"   # the OTHER agent's mailbox + state
MARKER="$HOME/.hermes/state/carsah_last_seen_claude"

cd "$REPO" || exit 0
git fetch -q origin main 2>/dev/null
LAST=$(git log -1 --format=%H origin/main -- $MAILBOX_PATHS 2>/dev/null)
[ -z "$LAST" ] && exit 0
[ "$LAST" = "$(cat "$MARKER" 2>/dev/null)" ] && exit 0   # nothing new / already processed
# A new review is unprocessed — is ANY implementer session already on it?
# (session id rotates on rotation, so match broadly)
pgrep -f "hermes chat --resume" >/dev/null && exit 0
MSG=$(git log -1 --format="%h %s" origin/main -- $MAILBOX_PATHS)
echo "STUCK: unprocessed review ($MSG) — implementer idle. Direct-launch needed."
