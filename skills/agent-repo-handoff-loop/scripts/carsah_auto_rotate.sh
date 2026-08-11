#!/bin/bash
# CarSah AUTO-ROTATE — retires a bloated implementer session at a clean delivery boundary.
# Conditions (ALL must hold): session messages > THRESHOLD AND tree clean AND implementer idle.
# On rotation: create a fresh session (lean skills) -> update SESSION in ALL THREE scripts
# (auto-rotate + auto-wake + watcher) -> restart the watcher (the new terminal link) -> wake
# the new session with the standard directive -> log + inform the founder (English).
# no_agent cron: non-empty stdout is delivered; empty stdout = silent.
#
# INTENTIONAL-STOP GUARD (2026-08-11): if the founder stopped the implementer on purpose,
# the file ~/.hermes/state/carsah_implementer_stopped exists and BOTH loop scripts exit
# silently. The founder creates it when stopping, removes it when resuming. Without this,
# a deliberately-idle session looks "idle" to the rotate cron, which then spawns a new
# session — the orphan-session bug (08:12 + 10:12 on 2026-08-11: two sessions spawned
# while the implementer was stopped, one hit max-turns mid-fix).

SESSION=<your-implementer-session-id>
REPO=/path/to/the/shared/repo
DIRECTIVE="$HOME/.hermes/scripts/carsah_wake_directive.txt"
LOG="$HOME/.hermes/state/carsah_wakes.log"
THRESHOLD=900
LOCK="$HOME/.hermes/state/carsah_loop.lock"
STOP_MARKER="$HOME/.hermes/state/carsah_implementer_stopped"
SKILLS="flutter-ai-code-verification,flutter-arch-boundary-enforcement,flutter-screen-state-machine,flutter-error-handler,flutter-app-logger,flutter-hook-architect,flutter-isar-clean-arch-setup,flutter-isar-testing,device-screen-verification,android-adb-device-testing"

cd "$REPO" || exit 0

# INTENTIONAL-STOP: founder stopped the implementer — never rotate.
[ -f "$STOP_MARKER" ] && exit 0

# Mutual exclusion with the auto-wake cron — whoever holds the lock acts first.
[ -f "$LOCK" ] && exit 0
touch "$LOCK"; trap 'rm -f "$LOCK"' EXIT

# 1) session size
COUNT=$(sqlite3 "$HOME/.hermes/state.db" "SELECT count(*) FROM messages WHERE session_id='$SESSION' AND active=1" 2>/dev/null || echo 0)
[ "${COUNT:-0}" -gt "$THRESHOLD" ] || exit 0

# 2) clean tree = delivery boundary (ignore the founder's desktop-attachments untracked dir)
DIRTY=$(git status --porcelain | grep -v ".hermes/desktop-attachments" | wc -l | tr -d ' ')
[ "$DIRTY" = "0" ] || exit 0

# 3) implementer idle — ANY implementer session running, not just $SESSION
pgrep -f "hermes chat --resume" >/dev/null && exit 0

# ROTATE — create the fresh session (lean skills at birth)
NEWID=$(hermes chat --skills "$SKILLS" -q "You are the new CarSah implementer session (creation ack only). Do NOT execute anything — no tools, no git, no files. Confirm receipt in one sentence." -Q --max-turns 1 2>&1 | grep -oE "session_id: [0-9a-z_]+" | awk '{print $2}')
[ -z "$NEWID" ] && { echo "ROTATION FAILED — no new session id (provider down?). Direct-launch needed."; exit 0; }

# point ALL THREE scripts at the new session (self-update fixes the
# rotate-from-stale-session bug: it previously rotated from the OLD session
# forever because it only updated auto_wake + live)
sed -i '' "s/^SESSION=$SESSION$/SESSION=$NEWID/" "$HOME/.hermes/scripts/carsah_auto_rotate.sh"
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
