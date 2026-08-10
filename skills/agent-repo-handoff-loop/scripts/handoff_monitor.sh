#!/bin/bash
# Hash-suppressed handoff poller for Hermes cron monitor_script.
# Emits STABLE "IDLE" when nothing new (agent run suppressed, ZERO tokens).
# Emits "CHANGED" + commits when the other agent's mailbox moved (agent runs).
#
# Deploy: copy to ~/.hermes/scripts/, edit REPO_PATH + MAILBOX_PATHS, then:
#   cronjob action=create ... monitor_script=<name>.sh schedule="every 2m"
REPO_PATH="/path/to/the/shared/repo"
# Paths that, when they change remotely, should wake the agent:
MAILBOX_PATHS="handoff/claude/ handoff/STATE.md"

cd "$REPO_PATH" || { echo "IDLE"; exit 0; }
git fetch -q origin main 2>/dev/null
NEW=$(git log --oneline HEAD..origin/main -- $MAILBOX_PATHS 2>/dev/null | head -20)
if [ -z "$NEW" ]; then
  echo "IDLE"
else
  echo "CHANGED"
  echo "$NEW"
fi
