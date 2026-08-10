#!/bin/bash
# CarSah AUTO-ROTATE — retires a bloated implementer session at a clean delivery boundary.
# Conditions (ALL must hold): session messages > THRESHOLD AND tree clean AND implementer idle.
# On rotation: create a fresh session (lean skills) -> update SESSION in BOTH scripts
# (auto-wake + watcher) -> restart the watcher (the new terminal link) -> wake the new
# session with the standard directive -> log + inform the founder (English).
# no_agent cron: non-empty stdout is delivered; empty stdout = silent.

SESSION=<your-implementer-session-id>
REPO=/path/to/the/shared/repo
DIRECTIVE="$HOME/.hermes/scripts/carsah_wake_directive.txt"
LOG="$HOME/.hermes/state/carsah_wakes.log"
THRESHOLD=900
LOCK="$HOME/.hermes/state/carsah_loop.lock"
SKILLS="flutter-ai-code-verification,flutter-arch-boundary-enforcement,flutter-screen-state-machine,flutter-error-handler,flutter-app-logger,flutter-hook-architect,flutter-isar-clean-arch-setup,flutter-isar-testing,device-screen-verification,android-adb-device-testing"

cd "$REPO" || exit 0

# Mutual exclusion with the auto-wake cron — whoever holds the lock acts first.
[ -f "$LOCK" ] && exit 0
touch "$LOCK"; trap 'rm -f "$LOCK"' EXIT

# 1) session size
COUNT=$(sqlite3 "$HOME/.hermes/state.db" "SELECT count(*) FROM messages WHERE session_id='$SESSION' AND active=1" 2>/dev/null || echo 0)
[ "${COUNT:-0}" -gt "$THRESHOLD" ] || exit 0

# 2) clean tree = delivery boundary (ignore the founder's desktop-attachments untracked dir)
DIRTY=$(git status --porcelain | grep -v ".hermes/desktop-attachments" | wc -l | tr -d ' ')
[ "$DIRTY" = "0" ] || exit 0

# 3) implementer idle
pgrep -f "hermes chat --resume $SESSION" >/dev/null && exit 0

# ROTATE — create the fresh session (lean skills at birth)
NEWID=$(hermes chat --skills "$SKILLS" -q "You are the new CarSah implementer session (creation ack only). Do NOT execute anything — no tools, no git, no files. Confirm receipt in one sentence." -Q --max-turns 1 2>&1 | grep -oE "session_id: [0-9a-z_]+" | awk '{print $2}')
[ -z "$NEWID" ] && { echo "ROTATION FAILED — no new session id (provider down?). Direct-launch needed."; exit 0; }

# point BOTH scripts at the new session
sed -i '' "s/^SESSION=$SESSION$/SESSION=$NEWID/" "$HOME/.hermes/scripts/carsah_auto_wake.sh"
sed -i '' "s/^SESSION=$SESSION$/SESSION=$NEWID/" "$HOME/.hermes/scripts/carsah_live.sh"

# restart the watcher (the new terminal link)
pkill -f carsah_live.sh 2>/dev/null
nohup bash "$HOME/.hermes/scripts/carsah_live.sh" >/dev/null 2>&1 &

# wake the new session with the standard directive
git pull --rebase origin main >/dev/null 2>&1
hermes chat --resume "$NEWID" --reasoning max -q "$(cat "$DIRECTIVE")" -Q --max-turns 500 >/dev/null 2>&1 &

echo "$(date +%H:%M:%S) ROTATED $SESSION -> $NEWID (msgs=$COUNT)" >> "$LOG"
echo "Rotated implementer session to $NEWID (old had $COUNT msgs) — new watcher linked."
