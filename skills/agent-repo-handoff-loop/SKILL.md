---
name: agent-repo-handoff-loop
description: Two-agent review loop via repo mailbox, token-free polling.
version: 1.0.0
metadata:
  hermes:
    tags: [multi-agent, handoff, repo, mailbox, cron, monitor-script, review-loop]
    related_skills: [device-screen-verification, android-adb-device-testing, autonomous-coding-agents]
---

# Agent-to-Agent Handoff Loop via Repo Mailbox

Async, auditable communication between two agents (e.g. an implementer and an
external auditor) with NO human relay and NO direct agent-to-agent channel. The
git repo is the message bus; each agent polls it; every message is a commit.

Validated 2026-08-08 on CarSah (Claude = auditor via /loop, Sulaiman =
implementer). Full worked deployment: `references/carsah-deployment.md`.

**Commissioned one-shot audits** (whole-system, at a gate) are a different contract from this
per-delivery loop: one lens per directive and session (engineering vs strategy), the mandate is a
repo document + a one-line kickoff, every embedded number is a labeled snapshot to re-measure, and
the report must carry stop criteria and a self counter-test. Skeletons + the trap list:
`references/external-audit-directives.md`.

## When to use

- Two agents must exchange reports/reviews/corrections without the founder
  acting as a messenger, including when the founder is away.
- **Founder-relayed variant (the loop has no pollers armed).** When the peer runs in a separate app with no
  access to the repo, the founder pastes each verdict in and each letter out. Then every round must END with a
  paste-ready relay block — the peer's read command (`git fetch origin && git show origin/main:<letter path>`)
  plus one paragraph on what it should answer — and the letter must be SELF-SUFFICIENT, because the peer reads
  the letter, not your session. Do not hunt for a monitor script or cron that was never armed in this shape of
  the loop; the founder is the transport, and the push is still the record.
  **But the peer may ALSO be committing its verdicts into the mailbox itself — check before trusting the paste.**
  On every founder message: `git fetch origin`, then `git ls-tree -r --name-only origin/main -- handoff/<peer>`
  and `git log --oneline -3 origin/main`. A peer that has its own shell writes each verdicts as a file in
  `handoff/<peer>/` and merges them; the founder's paste is then a convenience copy — and a long verdict pasted
  into a chat can arrive as a TRUNCATED diff (`… omitted N diff lines`) whose tail holds the actual
  requirements. Read the committed file whole from `origin/main`; the paste is a pointer, never the source.
  Corollary: when the mailbox is ahead of what you were given, answer the NEWEST verdict and re-read the older
  ones in full before declaring any requirement closed — a round whose first verdict listed six requirements
  and whose last listed three is not closed by satisfying three.
- You want a permanent audit trail of every handoff (it is all in git).
- You want polling that costs ZERO tokens while idle.

## Lessons from a full audit cycle

Worktree hygiene, fix-authorship, guard-vs-evidence, and hash rewrites each cost a
round: `references/worktree-evidence-lessons.md`.

**Answering the peer's PROPOSAL dossiers** (build change-lists, roadmaps, schema DDL, framework decisions)
is a different job from reviewing a diff: verify their measured claims first and SAY which came out true,
check each count against the line the tool prints rather than the number beside it, derive a round number
before attacking it, find the load-bearing external premise and ask for its source in writing, and audit any
DDL for silent-failure classes. Method + the closing «what I did NOT verify» list:
`references/reviewing-peer-proposals.md`.

**Answering a VERDICT on your own plan** (the peer returned FAIL / REQUEST_CHANGES before a line was built) is
its own cycle, and the founder's rule binds it: «لا نسلم به إلا بالدليل والحجة والإثبات» — a peer verdict is
MEASURED, never adopted on authority. Read the committed letter rather than a relayed summary; rebase your
branch onto the peer's commit so your delivery carries their bytes (verify by shasum); then answer
claim-by-claim with one command per claim, expecting to refute some of them (run the peer's own proposed
poison — one that passes disproves the claimed hole) and to withdraw YOUR OWN figures that do not reproduce,
in the same letter, along with every number that depended on them. Where the peer's reading of your evidence
disagrees with yours, look for the artifact's own printed witness and let IT adjudicate: a dispute settled by
re-deriving harder stays open, a dispute settled by the artifact ends. Method + the measurement shapes that
sink a plan (population-blind gates that measure a filter instead of the artefact, boundary-blind identity gates, one-directional metrics, self-selecting packs, aggregate counts with no member list, small-n):
`references/answering-a-verdict.md`. A PASS **that carries one condition** is its own cycle: re-measure the
condition's threshold against the FULL frozen input before promising it, question the condition's premise
before conforming to it, re-run every gate the relaxation touches, and declare the fallback numerically in the
same letter — a rule silent about its own failure mode gets decided under build pressure, by whoever is holding
the build. And a blocking item that turns out to be RIGHT is answered by confirming it on independent layers
(the two source artifacts' hashes · their period spans · their CONTENT intersection on the natural key), then
lifting the block, re-measuring in numbers what the remedy cost, and re-aiming the poison — negative control
included, so the shape the old gate falsely blocked is now a regression test.

## The owner's acceptance contract for a round (binds every delivery)

When the owner states the terms for accepting work, they are acceptance conditions, not advice — a round that
misses one is returned without a technical review. The standing set, in the owner's own emphasis:

1. **ONE artifact per round.** Results live in a single file — not a letter here, a state file there, and a
   third body in the PR. `STATE.md` keeps a status pointer (status/step/next), the PR body points at the
   file, and the file carries the evidence. Splitting the record is itself a finding.
2. **Test before delivering.** No result is delivered that was not executed; every number carries the command
   that produced it, and the command is printed beside the number.
3. **Be skeptical of your own results.** Attack your own artefact before the peer does, and announce what
   FAILED as loudly as what worked — a defect your own control caught, a regression you introduced, a framing
   you must withdraw. A report of wins only is unauditable.
4. **QA per STEP, and a guard is only proven by its fall.** Not a claim that the gate exists: the reviewer's
   test of a new guard is "re-inject its defect and show me the guard falls". Make that durable (a script that
   injects each defect, requires that guard's tests to fail, restores the bytes, compares a hash) rather than
   performing it once by hand; guards never re-injected stay `unknown`, never `safe`.
5. **Measure the side effects.** What the step touched without intending to: suite count and its delta,
   published documents carrying numbers, sealed artefacts (count and hash), identity fields, cost. State them
   per round — never assume safety.
6. **A brief or a roadmap you hand over is a STATUS DOCUMENT — every line is a claim.** Each item carries its
   gate in its own words plus its status, and each status says whether it was MEASURED now (with the command)
   or CITED from a letter; a status written from memory is a false claim with a deadline. Measure "not started"
   too (a negative claim needs the grep that returns empty). Keep in-flight work in its own section with an
   owner per line, exclusions in another so settled decisions are not re-litigated. Skeleton + the
   fresh-session-brief pattern: `references/fresh-session-brief.md`.

## Loop non-negotiables

Each of these cost a review cycle, and each is a shape the loop will meet again.

- **A history rewrite invalidates every hash your peer recorded.** Scrubbing a value out of history changes
  every commit after it, so the peer's reports cite commits that no longer resolve and its branch falls
  behind by every rewritten commit. Re-anchor the loop on **content**: say in the handoff AND in `STATE.md`
  that the old hashes are dead, pin the next review to the new head, and point the peer at
  `git diff --name-only` instead of a SHA. A peer reviewing from a stale branch is reviewing a different repo.
- **Every submission carries its full header, even a one-line change.** A state-file edit pushed without
  `id/from/to/type/step/commit/evidence/next` forces the peer to rebuild the file list itself — and it will
  say so, which is a wasted cycle spent on bookkeeping instead of the work.
- **Editing a sectioned state file: anchor on the header PLUS the line under it, never the bare header.**
  A patch that matches `## <section>` alone inserts ABOVE that section, so the new entry lands outside it and a
  duplicate header appears further down (hit twice in one loop); the file then carries a log section twice and
  the next reader answers from the wrong block. Match `<header>\n<first existing line>` (or the section's
  previous newest entry) to insert at the TOP of the section, and verify structure mechanically after every
  structural edit (`grep -c '^## <section>'` must be 1). One writer per state file per round, with a
  `<writer> · <time>` line, and the previous holder's block kept under a `(سابقًا)`-style marker rather than
  edited away.
- **The author of a fix may never be its judge.** If the peer crosses into writing code (authorized, and it
  must declare that in both the message and `STATE.md`), the implementer reviews it as a first-class
  submission: reproduce each claim with its own commands, answer the specific attack points the peer names,
  and issue PASS / REQUEST_CHANGES in the mailbox. Roles flip, the audit trail does not.
- **Refuse a destructive request with a replacement command, not a verdict.** A peer asking for
  `git restore --staged --worktree <file>` merely to *read* it gets the read-only form instead
  (`git fetch origin` then `git show origin/main:<path>`) — reading needs no write, and a restore over a stale
  remote-tracking ref silently revives an old value while a staged restore destroys un-committed work with no
  reflog. Hand back the exact command to run, plus the reason in one line.
- **Keep the peer isolated.** The auditor works in its own worktree; when one is recycled or deleted, its
  session silently lands in the implementer's checkout. Re-create a fresh worktree before the next review
  round rather than letting the reviewer edit the deliverable's working tree.
  **And a fresh worktree does not carry GITIGNORED data** — the peer's suite then SKIPS every guard whose input
  is the real local corpus (the very cases that certify the deliverable) and reports itself complete. Put the
  repo's data-link command in the peer's brief (`tools/link_local_data.sh <worktree>`, expected `0 skipped`),
  and read the class in `references/worktree-evidence-lessons.md` (environment-scoped coverage).
- **Anchor the delivery's sha to the MERGED history, never to your branch.** A `--rebase` (or squash)
  merge recreates the commits, so a `commit:` field written before the merge resolves only in the author's
  own clone (measured 2026-09-19: the branch sha `bfda506` became `184f0be` on main and the letter's anchor
  became unresolvable for anyone else). Read the sha AFTER the merge, and if the merge already happened,
  state the mapping in the same letter — otherwise the peer's first cycle is spent reporting a broken hash.
- **Measure a claim with the command that READS the thing the claim is about.** Two shapes cost a round
  each, one on each side of the same loop: `git log -S "<sha>" -- <path>` counts the string **per FILE**, so
  it names the commit that added the sha in a header while the cited LINE still held the old one (read the
  line: `git show <commit>:<path> | sed -n Np`, or `git log -L N,N:<path>`); and a judgement about a REMOTE
  branch made from a local ref (`git fetch --all` without `--prune`) reports a deleted branch as alive (ask
  the remote: `git ls-remote --heads origin`). A rebuttal built on the wrong command is a NEW false claim:
  when challenging a peer's record note, use the same class of command — and expect its timestamps back.
  **Third scope: the POPULATION, when membership is decided by a label your own code emits.** A date check
  filtered with `startswith("<movement label>")` reported `5789/5789` over a file holding 5791 dates; the two
  excluded rows were the anchors — exactly the rows five rounds had been spent on — so any future anchor losing
  its date would have passed green. Widening the check to the whole population is the fix, and each newly
  included row needs its own poison. Whenever a gate prints `N/N`, ask what it filtered OUT to get there.
- **A peer's archive-backed claim can be stale in EITHER direction — verify before adopting it, and correct
  your own error as loudly as theirs.** In one round each side was wrong once: a peer reported a branch as
  alive that was pruned (its own fetch lacked `--prune`), and the implementer attributed to the peer a stale
  read of a state file that was in fact correct. Both errors are record errors, neither moved a figure, and
  both belong in the next letter by name — a loop whose history is negotiable is worth nothing.

## Architecture

```
handoff/
  STATE.md              ← state machine (single source of truth for "who waits")
  <agentA>/             ← agent A writes here ONLY (e.g. sulaiman/)
  <agentB>/             ← agent B writes here ONLY (e.g. claude/)
```

- Message = one NEW file per message, timestamped (`YYYYMMDD-HHMMSS.md`),
  format: `id / from / type / step / verdict / evidence / findings`.
- Append-only: never modify or delete the other agent's files.
- **Your OWN sent letters are append-only too — correct by DECLARATION, not by rewriting.** A letter that is
  already in the history is the record: leave its body, and add a dated note in its correction block that
  names what is void and points at the live value; anything still live (STATE, a doc, a count in the
  contract) is fixed in place. Rewriting a sent body converts the audit trail into a document that can be
  improved after the fact — the one property a review loop cannot afford. The sharper form, from the peer
  that enforced it: *what was sent keeps its text; the dated declaration names what is void and points at
  the live value; what is still live is corrected where it lives.* **Read the composed file back (or `git diff`
  it) before committing it: a long drafted letter can carry a stray fragment from the drafting surface, and
  because a sent letter is never rewritten, a nonsensical line in it is permanent.**
- **An edit tool reports SUCCESS while changing NOTHING — verify the VALUE landed, not that the call
  returned.** A pattern replace that does not match its target (a different diacritic form, an extra word)
  exits clean, so the file keeps the old number; the local suite can still pass while the gate that compares
  the document against its DERIVED snapshot fails in CI. A measured number normally lives in two artifacts
  (the prose and the snapshot generated from the run), and one gate traverses both, so: edit the number where
  it lives, regenerate the snapshot, and **run that gate before pushing** (`pytest <the guarding test>.py`),
  then read the value back from the file. Applies equally to a claim written before its implementation.
- STATE machine: `WORKING` → `AWAITING_REVIEW` → (`AWAITING_FOUNDER` |
  `BLOCKED_DEVICE` | `DONE`). **AWAITING_FOUNDER stops BOTH pollers** — no
  token burn while waiting for a human decision; founder action wakes the loop.
- Mandatory `git pull --rebase` before EVERY push — two agents pushing to main
  WILL collide eventually.

**A recorded `commit:` anchor rots the moment history is rewritten.** The message format
mandates a sha, and any value-removal scrub (`git filter-repo` for a leaked account number,
secret, or path) rewrites EVERY commit — so earlier messages' `commit:` fields, and every
review that anchored to them, stop resolving (`git log <old-sha>..HEAD` → `fatal: ambiguous
argument: unknown revision`). A peer auditor then spends its first cycle reporting a broken
hash as a finding, and a reviewer that cannot resolve the anchor either approves blind or
stops the loop. Rules: anchor a review to the CURRENT HEAD (read after `pull --rebase`) and
judge CONTENT (`git diff --name-only <base>..HEAD`, the file list), never an old sha; when a
rewrite lands, write the stale-hash warning into `handoff/STATE.md` in the same delivery so
both sides read it before reviewing; and state the diff BASE explicitly, since a rewritten
ancestor changes what "since the last delivery" means. Note also that after such a rewrite
the only surviving copy of the old-shape reports is whatever the peer still holds locally —
see the worktree rule below.

**A peer's artifacts living in a git worktree are one deletion from loss.** An external agent
(driving a CLI that isolates itself in a `.claude/worktrees/<repo>-<task>-<hash>/` checkout)
writes its verdicts INTO that worktree, on its own branch, while the mailbox in `main` still
holds only a `.gitkeep`. Those files look safe — the directory mirrors the whole project — and
they are one `git worktree remove` from gone, taking the only record of the review with them.
Rules: after receiving a peer's verdict (any channel), COPY it into the repo mailbox path
(`handoff/<peer>/`) and commit it, so the audit trail lives where the loop reads; before
committing, run the repo's own guard over it — a peer's report may quote the very value the
review is about; and when the worktree is no longer needed, remove it with
`git worktree remove` + `git worktree prune`, never `rm -rf` (a bare delete leaves a stale
registration under `.git/worktrees` that reads as a broken repo). A worktree's subfolders
mirror the project because it IS the same repository checked out at a second path sharing one
`.git` — expect a second on-disk copy of anything that was local (ignored caches, real data)
at creation time, and treat that as an exposure question, not just disk usage.

**The PUSH is the record; the chat is not.** Letters, verdicts and `STATE.md` become durable only when they
reach the remote — conversation transcripts stay in each agent's own session store, outside the repo, and no
push preserves them. So when the founder asks whether the relay or the push is worth it, answer with the
mechanism: a verdict sitting on a peer's local branch is one `git worktree remove` from loss, and the cheapest
fix is to base YOUR branch on the peer's commit and push that — your delivery then carries their bytes into
`main` for free. Mechanics for a protected `main` (required status check): branch off the peer's commit →
`git push -u origin <branch>` → `gh pr create --base main --head <branch>` → `gh pr checks <n> --watch
--interval 10` → `gh pr merge <n> --rebase` (rebase keeps every commit and its authorship, so the peer's commit
lands under its own name) → `git fetch && git switch main && git merge --ff-only origin/main`. Then READ BACK
from `origin/main` (`git show origin/main:<path> | shasum` against the source commit) before telling anyone it
is safely stored. Two traps: pass the PR body with `--body-file <path>` (a heredoc inside `$( )` breaks the
shell as soon as the body holds backticks or apostrophes), and never trust the merge output as proof the files
arrived. **Third trap — the base must be CURRENT: a letter branch cut from an older base is refused at merge
time (`mergeStateStatus: BLOCKED`, with "add `--admin`" as the only hint), so your letter looks delivered while
the PEER's commit stays out of `main` — the half that goes missing silently. Rebase onto the live base and
re-push before merging: `git rebase origin/main` → `git push --force-with-lease` → `gh pr checks <n> --watch
--interval 10` (a freshly pushed head reports `BLOCKED` until the required check runs) → `gh pr merge <n>
--rebase`; then verify BOTH files byte-identical from `origin/main` — `git show origin/main:<peer letter> |
shasum` against the peer's own commit, and the same for yours.** **Verify the base BEFORE pushing, not at merge
  time:** a local `main` never set to track its upstream makes `git pull --ff-only` exit 0 while changing NOTHING,
  so a branch cut from it silently carries other commits' diffs into the PR (measured: a one-file document PR
  whose range listed four files). But first confirm the range is exactly what you meant to publish —
  `git fetch origin && git diff --name-only origin/main..HEAD` — and when it is not, `git rebase origin/main`,
  re-run the local gates on the new base, then push. A session that finds a dozen local-only branches holding the peer's past verdicts should say so and
offer to push the peer's refs too — the peer's own branches are not yours to move without a word.

**A peer asking to DESTROY state in order to READ it — answer with the read-only form.** In a shared
repo a peer (either side) will request a mutating git command whose stated purpose is inspection, e.g.
`git restore --source=origin/main --staged --worktree <file>` "to see the current version". Approving it
discards BOTH the working-tree and the index copy, and an uncommitted file has no reflog — anything
pending in that path is unrecoverable, including the peer's own accidental edits (in one loop the
outstanding edit was a leftover from a history rewrite that would have re-introduced the scrubbed
value). Rules for the approver:

1. Return the read that needs no write: `git show origin/main:<path> | sed -n '<from>,<to>p'`. Same bytes,
   zero destruction — when a destructive command is proposed, first ask what the peer is trying to LEARN.
2. `git status --short <path>` before deciding anything: an informed approval needs the pending diff.
3. If a real sync is required, order it `git stash push -- <path>` → `restore` → `pop`; a blind restore is
   only safe when `status` proved the path is clean.
4. `git fetch origin` before reading ANY `origin/*` ref. A stale remote-tracking ref returns the OLD file,
   and the peer then reports a finding about a version that was replaced hours ago — the false finding
   costs more than the fetch.
5. Decide on the command's merits, not on the approval prompt's reason. A transient harness message
   ("classifier error — retrying often succeeds") says nothing about the command; a destructive command
   does not become safe because the block was noise, and a safe one does not become dangerous because a
   gate mis-fired.
6. The standing role rule makes this cheap to enforce: the reviewer does not modify the implementer's
   files. Reverting a file in the implementer's working copy IS a modification — reading is the only
   reason it is allowed, and reading never needs it.

## Token-free polling (monitor_script)

Hermes cron `monitor_script` semantics: output is hashed per tick; UNCHANGED
bytes suppress the agent run entirely (no LLM, no tokens); CHANGED bytes run the
agent with the diff injected. Use `scripts/handoff_monitor.sh`:

- `git fetch origin main` then `git log --oneline HEAD..origin/main -- <other-agent-dir> STATE.md`
- empty → emit `IDLE` (stable → suppressed); non-empty → emit `CHANGED` + commits.
- **SHARED-WORKING-TREE HAZARD (hit twice, 2026-08-08):** if the other agent
  runs on the SAME machine and SAME checkout (e.g. Claude Code in the project
  dir), its `git pull` advances YOUR local HEAD → `HEAD..origin/main` is
  ALWAYS empty → the poller is blind forever ("idle" despite a full mailbox).
  The `HEAD..origin/main` form is safe ONLY for an isolated clone. Safe
  pattern for a shared tree — compare the latest commit touching the mailbox
  on origin against a stored marker:
  `LAST=$(git log -1 --format=%H origin/main -- <other-agent-dir> STATE.md)` ;
  `LAST == $(cat ~/.hermes/state/<last_seen>)` → `IDLE`, else `CHANGED`.
  The PROCESSING agent updates the marker AFTER pushing (never before — a
  failed run must leave the message pending). Add a lock file
  (`touch ~/.hermes/state/<loop>.lock` before starting work; monitor emits
  `IDLE` while it exists) so an in-flight run can't be double-fired.
- The FIRST tick always runs the agent (baseline) — the prompt MUST handle
  "no new message → do nothing, no notification, brief reply".

Cron job shape: `every 2m`, `monitor_script=<script>`, `deliver=local` (the
agent sends its own Telegram/notification at the end — avoids double delivery),
`workdir=<repo>`, `enabled_toolsets=["terminal","file"]`, self-contained prompt.

## Watchdog vs implementer (role split — hard-won lesson)

Do NOT let the polling cron agent implement by default. If the founder drives
the implementer in a dedicated session, a cron agent pushing code causes
two-writer chaos and violates session ownership. Default arrangement:

- **Watchdog cron**: on a new message from the other agent → pull, read STATE +
  the new message, summarize the verdict, notify the founder (Telegram), NEVER
  push code.
- **Implementer session**: the founder prompts it with a wake phrase; it
  executes the verdict (fix / next step), verifies (analyze/test/CI/device),
  pushes, updates STATE.

Flip to a fully autonomous loop ONLY when the founder explicitly wants no
human in the loop at all. Then, to preserve session ownership (the founder may
insist programming happens in ONE dedicated session, not fresh cron sessions):
use a **coordinator + resume** pattern — the cron agent, on a new message,
creates the lock, launches the dedicated session in the background with
`hermes chat --resume <SESSION_ID> --reasoning max -q "<self-contained directive>" -Q --max-turns 150`,
confirms it started, removes the lock, and replies briefly (no Telegram — the
resumed session sends it after executing). The directive carries: pull --rebase,
read the protocol + STATE + new message, an idempotency guard (already handled?
→ update marker only), execute the verdict, verify, push, update marker.

**Prove the wake before arming it.** Before real directives flow, run a no-op
wake test and confirm the session actually receives and replies:
`hermes chat --resume <SESSION_ID> -q "اختبار إيقاظ فقط — لا تستخدم أدوات ولا تنفّذ
عملاً، رد جملة واحدة" -Q --max-turns 3` → expected: short ack, exit 0
(validated 2026-08-08: session replied «جاهز للاستلام التلقائي»). If the
session is open in the desktop app, the test messages visibly appear there —
tell the founder to expect them.

**Effort inheritance:** a resumed session WITHOUT `--reasoning` runs at the
global `agent.reasoning_effort` (often `high`), even when the founder demands
max. Pass `--reasoning max` explicitly on the resume command. Caveat: the CLI
help lists `ultra` as a level, but the deepseek API rejects it — valid enum is
`max|xhigh|high|medium|low|minimal|none`.

**Watching a resumed session live.** The desktop app does NOT live-refresh
messages appended by a background `hermes chat --resume` process — the founder
opens the session, sees it "as it was", and assumes nothing is happening while
files are actually being edited. Give them a dashboard loop (clear; refresh
every ~8s; background process → desktop terminal tab). USER-VALIDATED layout
(2026-08-08 — the founder explicitly rejected raw log lines as "غير مفيد
أبدا"):
1. "Is the implementer alive?" — 🟢 process running (`pgrep -f "hermes chat --resume <SESSION_ID>"`) / ⚪ dormant
2. Official state — `head handoff/STATE.md` (status / step / next)
3. Working tree — `git status --porcelain | head -6` (non-empty = mid-edit proof)
4. Last commits + newest mailbox files
Do NOT put raw `agent.log` lines in the founder-facing view — they read as
noise. Keep `grep "<SESSION_ID>" ~/.hermes/logs/agent.log | tail` as the
coordinator's OWN debugging tool (API call #N = thinking; `tool patch
completed` = editing; `tool terminal completed` = running commands).
5. "What is it doing now" — the founder asked for the implementer's live
   thinking/actions; raw log lines were rejected. Read the session's message
   store instead — readable, no log parsing:
   `sqlite3 ~/.hermes/state.db` on the `messages` table (`session_id, role,
   tool_name, content, active=1`), show the last ~5 rows:
   - `role='assistant'` → its narration ("💬 <text>") — closest to visible
     reasoning
   - `role='tool'` with `tool_name` → "🛠 <tool_name> → <first line of
     output>" (strip the JSON wrapper: `json.loads(content).get('output')`)
   Keep dashboard headings in ENGLISH (founder-validated, even in an Arabic
   chat); data values stay as-is.

## Delivery-completeness law (the silent-stall case)

A delivery is **push + SUBMIT message + STATE update** — the other agent's poll
watches ONLY the mailbox paths, so a pushed code commit with no message is
invisible to it and the loop stalls SILENTLY ("idle" while real work sits on
main). Hit 2026-08-08: the retired implementer session died between `git push`
and writing its SUBMIT (BL-012), and the auditor — correctly — kept saying
idle for two hours.

- Ground truth for "who delivered last" = `git log --oneline -- handoff/`
  (commit order), NOT file mtimes and NOT the newest review file.
- When the founder insists "the other side delivered last, so MY side should be
  working" — they are usually right: check whether the implementer's feat
  commit has a FOLLOWING handoff/SUBMIT commit. If not, complete the delivery
  yourself (SUBMIT with real sha/run per the evidence checklist + STATE update
  + push); the other agent's next poll then fires.
- Auditor process alive (`ps` shows claude-code) ≠ loop working. Absence of a
  NEW review must be explained by the mailbox, not assumed to be auditor fault.
- Diagnosis order for any "idle": 1) `git fetch` + compare local HEAD vs
  origin/main (shared tree may be behind), 2) `git log --oneline -- handoff/`
  for the real order, 3) mailbox contents vs each side's marker.

## Shared-language boundary (the auditor is a separate program)

The external auditor (e.g. Claude Code) does NOT see the Hermes skill library —
skills live Hermes-side (`~/.hermes/skills/`) and are invisible to it. Never
instruct the auditor to verify skill compliance: it cannot, and being asked to
check something it cannot see erodes its independence. ANYTHING the auditor
must verify must exist IN THE REPO — File-12 verification gates, DEC entries,
acceptance criteria. The repo is the only shared language between the two
programs. The implementer's skill map (Hermes-side) teaches HOW; the repo
gates define WHAT must be true; the auditor checks the gates. Two layers that
never need to know each other — that is the design, not a gap. (Founder
correction 2026-08-09: an earlier plan to have the auditor verify "did the
implementer load the right skill" was dropped for exactly this reason.)

## The implementer is a commodity (the mailbox is transport-agnostic)

The deepest payoff of the repo-mailbox design: the IMPLEMENTER is a swappable
component. The loop only requires the two parties to read/write a repo and be
automatable — it does not care what model/tool powers them. "Stop wiring
agents. Start mailing them." — a subscription implementer (flat monthly cost)
can replace a metered API implementer with a ONE-LINE change in the
coordinator's launch command; the mailbox, STATE, auditor contract, and
verification gates never move. Verified 2026-08-10: Kimi Code CLI is a fully
viable alternative implementer (official, MIT, `kimi -p "<directive>"`
non-interactive mode, subscription OAuth login, `--skills-dir`, session
resume) — see `references/subscription-implementer-alternatives.md` for the
verified facts (the general class: ANY tool with CLI + subscription + the five
conditions; Kimi is the verified case study, not the subject) and the
applicability conditions.

Applicability conditions for ANY tool in the implementer slot (state them in
the report/decision):
1. Shared repo access — reads/writes git + files.
2. Automatable — a headless/CLI mode the coordinator can invoke (`-p`, `-q`,
   `--print`); a chat-only app breaks the loop.
3. Follows a written protocol — the mailbox message format.
4. Verification from at least one side — CI/tests per delivery.
5. Human-readable state — STATE.md must stay readable by the founder.

A stateless implementer (`kimi -p` fresh per review, reading the brief +
STATE + reviews from the repo) eliminates the session-corruption class
entirely — no accumulated context to break. Before switching, run the
standard experiment: one step on a side lane, same auditor, compare rounds /
STOPs / evidence quality / real cost.

## Anti-complacency (governance is external)

A clean APPROVE round does not mean the implementer learned to self-govern.
The same defect class (e.g. user-facing debug strings) recurred one round
earlier. The governance lives in the directive, the brief, the gates and the
auditor — keep them tight after clean rounds, don't relax. The implementer
looks governed because the rails are; the rails are the system's job, not the
model's nature. Judge the loop by its trend across rounds, never by one clean
verdict.

## Post-SUBMIT activity is normal

A running implementer process after it wrote the SUBMIT message is the
evidence phase, not a bug: the hardened rules require `gh run watch` green on
THIS commit, then appending the real run id + conclusion (often a follow-up
commit like "CI green evidence added"). Expect push → SUBMIT → CI-watch →
evidence-append → marker update → Telegram before the process exits. A
founder who sees "he delivered but is still working" is watching this phase —
explain it, don't treat it as a stall.

**Founder preference (2026-08-13): a submitted delivery is a FREEZE.** While
a submission is in AWAITING_REVIEW — or its CI run is still in flight — the
implementer must NOT add speculative work (extra drains, tweaks, extra
instrumentation, "improvements" layered on the fix). The founder's words:
«لا يتفلسف حتى التسليم يكتمل» — stop philosophizing until the delivery
completes. One delivery at a time; a fix for a NEW finding waits for the
review that names it. This is distinct from the evidence phase above
(run-watch + evidence-append ARE part of the delivery and must finish).

## Founder decisions through the mailbox (PROPOSAL → DECISION flow)

Governance proposals can flow through the same mailbox (hard-won 2026-08-09 —
kept the loop moving while the founder was present but not coding):
1. A PROPOSAL message (type: PROPOSAL, from the founder or a relay) is reviewed
   by the auditor on its merits — APPROVE or REQUEST_CHANGES with its own
   adjustment. The auditor may counter the proposal with its own evidence
   (e.g. a 52-finding counterfactual audit) — that is the system working.
2. The founder replies with a DECISION message (type: DECISION, from the
   founder directly). It binds ONLY because the founder says it directly — a
   file claiming "the founder said X" is never binding on its own (the auditor
   enforces this boundary itself).
3. The auditor then directs the implementer through the normal loop, and may
   announce its future checks ("what I will verify at the next step") so the
   implementer knows the bar in advance.

### Every gate check needs a poison that names it — or nobody knows it is alive

A gate's checks look identical dead and alive in a green run, and two classes of dead check exist:
death by WRONG KEY (the filter matches nothing, so it exams zero rows) and death by DISABLED
CONDITION (`or not required` short-circuits it). Declaring the examined count catches the first
class only; the second says the count, prints the shortfall, and exits zero. So:

- **One poison per check, and assert the FAILING CHECK'S NAME** — not merely a failure. A single
  poisoned cell can trip four checks at once, and a dead check then hides under its neighbour's body.
- **A poison that damages the artifact AFTER it is built never exercises the BUILDER.** Post-build poisons
  mutate a finished artifact, so the code that CONSTRUCTS it is never run on damaged input — which is
  exactly where the crashes live (a sort key mixing text and numbers, a role read from the wrong source, a
  gap the builder must refuse). Keep a second family that corrupts the INPUT first — delete a row to open a
  gap, make one amount locally doubtful, flip a declared role — then RUN the build, and assert both the
  builder's own verdict and the gate's named check. The tell that the family is missing: the builder passes
  every case because no case ever fed it a damaged input, and one real input then kills the export.
- **Make coverage self-enforcing:** a test that fails when a check exists with no poison case. The
  verdict and the evidence for it get added in the same change, or the suite blocks.
- **The poison must attack the hole YOUR change opened, not the neighbours.** When a fix adds an exemption,
  softens a matcher, or introduces a bypass, a suite that proves only that the exemption works certifies the
  wrong thing: it says nothing about what the exemption now lets through. The required case feeds the newly
  admitted shape and asserts the PAIR — the rule still blocks the real value AND the exemption resolves for
  the one documented case. Real shape: three new tests, all testing the safe direction, none attacking the
  hole the fix created.
- **Never widen a shared rule to admit one document — exempt that document, in writing, and declare the price.**
  A matcher loosened tree-wide for a single file also admits every real value of the same shape, and the loss is
  silent (measured: skipping three-digit groups separated by spaces lets a fifteen- or eighteen-digit account
  written that way pass). The per-file exemption carrying a written reason is the mechanism for this; where the
  rule stays deliberately strict, name the price in the letter, because undeclared strictness reads as an
  oversight.
- **A NEW document is a fresh chance to re-publish a guarded value — cite it by SOURCE, never by copy.** Status
  reports, roadmaps and briefs quote numbers, and quoting is precisely what the guard exists to stop (measured: a
  newly written roadmap was blocked with `2 occurrences` because the two totals and the closing balance were
  copied into the prose). Three wrong fixes in order of temptation: allowlist the file (exempts a whole document
  whose content changes next week); paraphrase the value to slip the pattern (the leak is still in the tree); drop
  the claim (the document loses its point). Correct fix: make the document POINT — «the four invariants must not
  move; their values are read by command from their source, not written in prose» — and name the guard that
  enforces it. Run the repo's guards over every new prose artifact BEFORE committing it, and again after any rebase.
- **A check that compares a value to itself can never fail.** An assertion whose expected side is read back from
  the object under test — or falls back to the observed value when the key is missing (`v["spend"] ==
  round(v.get("a_spend", v["spend"]), 4)`) — is dead on arrival and passes in every run. Derive the expected
  number independently inside the test from the raw sources, then compare. This is the third dead-check class,
  beside death by WRONG KEY and death by DISABLED CONDITION. **The same death arrives one level down through a
  truthiness fallback:** `Decimal("0.00") or Decimal("-1")` evaluates to `-1`, so a legitimate ZERO turns into a
  violation (measured in four call sites in one pass) — write `x if x is not None else y`, never `x or y`, for any
  value a zero can carry.
- **A green run can also mean a proven value was silently REMOVED — the fourth class, death by SILENT DEMOTION.**
  When a tool (re)writes a declaration into an artifact, two questions decide whether its green run means anything:
  does it MERGE into the existing block or REBUILD it (a rebuild erases prior declarations before any guard reads
  them), and does any guard require a field that is `None` by design (then that guard can never fire). Rules that
  close the class: unknown → value may upgrade; value → unknown, value → a different value, or an absent source must
  STOP BY NAME with a non-zero exit and both values printed; a skip-early guard is scoped to "nothing can be
  learned", not to "a value exists"; and the suite needs one case per STATE TRANSITION, because `empty → null`
  cannot see `filled → null`. Detail: `references/answering-a-verdict.md` (When the condition's fix is a CODE change).
- **A LIVE gate can still be WRONG: it fires on a key collision between two different entities.** A check that
  matches an item in the evaluated set against a counterpart list by NUMBER alone (page, line, index) blocks the
  item whenever the two lists come from different documents — real case: eleven evaluated pages blocked because
  an unrelated 16-page capture used the same page numbers, pushing a range's start from page 1 to page 18 for
  zero protection. So every poison set needs a **NEGATIVE CONTROL — a case that must NOT trip the gate** (a
  counterpart item carrying another document's identity goes in, the gate stays green), and the intersection
  itself is keyed on an identity DERIVED from the source (`sha256(file)[:16]`), never on a number the two
  artifacts happen to share. Identity is the KEY; it is not the MEASUREMENT — see the same rule in
  `references/answering-a-verdict.md`.
- **Never let an empty result stand where the evidence is MISSING — print `unknown`/`مجهول`.** `set ∩ captured
  = ∅` asserts cleanliness; if the counterpart list does not exist (lost, never built, or scoped to another
  document), the honest output is `unknown`, and the gate's exit condition is PRODUCING that list (a $0
  re-capture from the run cache), not printing a green empty set. An empty result and an unmeasured one look
  identical in a report and mean opposite things.
- **Run the gate IN-PROCESS in the poison suite, not as a subprocess.** Dozens of poison cases cost under a
  second if the test imports the gate module, sets its `sys.argv`, captures stdout, and reads the module's
  failure list directly — clear that module-level list before every run, and assert on the FAILING CHECK'S
  NAME from the list rather than scraping the printed text. A subprocess per poison is what pushes such a
  suite out of CI.
- **A measurement performed by a DELEGATED independent verifier counts only when its command AND its exit
  status come back with it.** A seat/peer child returns a confident report whether or not its measuring step
  actually ran, so a blocker citing no command is **unmeasured** — steer the child and re-ask rather than
  believing it or discarding it. Brief every such child the same way: the artifact pinned as a command
  (`git diff <fixed-point>...HEAD`) to be read from the repo rather than from your description, read-only
  (no writes, no `git checkout`, no sub-agents), the code marked as DATA rather than instructions, and one
  closed verdict vocabulary. Then **re-verify every blocking claim yourself**: several independent seats
  landing on one root cause is a confirmed defect class, not three opinions — and a fix that relaxes a
  check needs a test that fails against the pre-fix code, or it certifies nothing.
- **A check whose condition can be satisfied elsewhere in the artifact is dead weight.** Real case:
  «the summary declares the gap ledger» passed because two totals rows said «(after gap entries)», so
  the dedicated row could be deleted and the check still went green. Require the DECLARATION ROW
  (label + value), not a string that appears somewhere in the sheet.
- **A name assembled from data needs a guard against its own placeholder.** An emitted check name built
  from a data field degrades to a placeholder when that field is absent (`قيد ص?`, `None`, `{}`), and no
  poison sees it — a poison matches the emitted name by PREFIX, and `قيد ص?` still matches `قيد ص`. Two
  rules: fail the gate on any emitted name carrying an unresolved placeholder, and when the preferred
  source is missing, name by ORDINAL (`gap entry #1`) rather than printing an empty slot. Cover the
  fallback with a case that BLANKS the field the name prefers — filling that source field is part of the
  fix, not just correcting the lookup key.
- **A declaration the artifact makes about ITSELF is checked against its SOURCE — and when that source lives
  outside the artifact, the poison must mutate the SOURCE.** The shape of a real `REQUEST_CHANGES`: two checks
  read the delivered workbook's own summary rows («reader identity: X» · «N items unstamped»), so a fabricated
  identity and a counter claiming zero both passed on a corpus the run cache showed as 629 unstamped items read
  by two reader identities — `grep -c "<the declared field>" <gate>.py` returned **0**, i.e. the gate never read
  the cache and could only compare the document to itself. The fix is three checks (declared identity equals the
  cache's · declared count equals the measured count · the corpus carries ONE identity), and the third cannot be
  poisoned in the workbook at all: declare a second poison class over the RUN DIRECTORY and widen the coverage
  rule to both classes, or the coverage guard turns red on the new check and the temptation is to exempt it.
- **Answer a peer's hole-proof with the same poisons twice, on the REAL artifact.** Run its cases BEFORE the fix
  — they must PASS, because that failure to bite IS the hole, and demonstrating it on the live deliverable settles
  whether the peer is right; then re-run the identical cases AFTER it, where they must fail BY NAME while the
  honest artifact still passes. Quote both runs in the letter (input, expected, observed, exit code): compliance
  dressed as agreement is what a reviewer cannot distinguish from a fix.
- **One producer, several artifact variants: the PROSE is part of the artifact, and each variant needs its own
  fixture.** Adding a second layout by declaring its role in a contract (no code change per layout) is the right
  shape — and it is exactly when the document starts lying: the second workbook carried sixteen «not proven»
  entries for items the period summary witnesses, a per-item verdict reading «no printed totals» in a design that
  prints none by construction, and a limits sheet copied verbatim from the first layout (images and paper in a path
  that has neither). Every number was right. So: derive each fixed sentence from the role the contract declares,
  keep the required statements as a contract field the gate reads (one per variant) instead of strings hard-coded
  in the gate, give **each variant its own fixture and its own poison**, and read the BUILT artifact sheet by sheet
  before writing the letter — a template read cannot show the row that survived the copy, and one sheet then holds
  the same label twice with contradictory content. A poison that survives is a claim about the poison first:
  widening it until the required CONTENT is actually gone (empty the sheet, not one cell) is what separates «the
  check is dead» from «my poison was weak».
- **Run the poisons in CI, and state the boundary.** The private corpus cannot enter CI, so the
  poisons ride a synthetic fixture whose arithmetic is locked inside the fixture itself; the delivered
  real artifact keeps whatever external injections exist. Name-level coverage complete +
  shape-level coverage partial is an honest, checkable claim — say it in those words.
- **A light CI job is a dependency probe for free.** Adding the injection suite to CI immediately
  exposed that importing the package pulled a PDF parser (an eager `__init__`): make the public names
  import lazily (PEP 562), and check the probe that gates "is the full stack installed?" — it silently
  flipped to True and activated a dormant local-only check in CI.

## The locked table outranks a review note (contradiction handling)

Hit 2026-08-09: the auditor's APPROVE said "BL-041 (sequence 24) may start",
but the LOCKED SEQUENCE TABLE (18 §14b.2) lists 24 = BL-067 and 25 = BL-041.
The implementer correctly followed the TABLE (it is the law — 14b.3 forbids
reordering it; a review note is not a DEC). Two rules from that case:

- **When the auditor's directive contradicts the locked table, the table wins**
  — but the implementer MUST say so explicitly in its delivery ("review said
  BL-041 seq 24; locked table says BL-067 seq 24; followed the table — please
  confirm"), otherwise the auditor's next review is built on its own mislabel
  and requests the wrong step out of confusion.
- **Do not silently pick an interpretation and continue.** A contradiction
  that affects WHAT to build should be raised (STOP + evidence → auditor
  validates → founder decides if founder-level). Self-resolving is acceptable
  only when the authority is unambiguous (the locked table is) — and even
  then, the contradiction note in the delivery is mandatory. The forbidden
  failure is the silent deviation.

## Notifications

- `hermes send --list telegram` → discover the exact target (name-based targets
  like `telegram:Abdulrahman Jahfali` resolve; bare `telegram` home may fail
  with "Chat not found" in some contexts).
- After each loop action: `hermes send --to "<target>" -s "<subject>" "<2-line summary>"`.
- **Founder-facing OUTPUT is ENGLISH ONLY (validated 2026-08-10).** Telegram
  messages, watcher/terminal dashboards, and any report the founder reads must
  be pure English — mixing Arabic into an English surface breaks RTL rendering
  and reads as garbage. The implementer directive's Telegram step must say
  "ENGLISH ONLY — no Arabic (RTL/encoding)". Internal instructions TO the
  implementer may stay in the founder's language; only founder-facing output
  is locked to English. The watcher script must contain ZERO Arabic strings
  (even comments/error labels — the last three were found and stripped).

## Interactive device verification is REQUIRED for UI steps (founder standard 2026-08-09)

A UI step's definition of done is NOT "code + widget tests + a screenshot".
The founder requires the implementer to WALK the app by touch on the device
(TECNO / emulator) — first-line interaction testing belongs to the
implementer; the founder's gate is the final human pass only:

1. Fresh install + cold launch + `logcat` clean (no FATAL).
2. Execute navigation scenarios by tapping: `adb shell input tap` at
   coordinates from `uiautomator dump` — walk every step of a wizard, exercise
   free-text/escapes, branch conditions (e.g. electric skips transmission).
3. Test BACK NAVIGATION from every reachable screen — it produced STOP-level
   bugs twice on device (one wrote a spec-violating DB row).
4. Compare each screen against the REQUIREMENTS (flow file, design file,
   acceptance criteria in the backlog) — not against the tests.
5. Screenshot per screen + uiautomator as ground truth + list every scenario
   in the 14 §14.2 verification note.
6. Report deviations HONESTLY — never "deviations — none" without a
   visual/requirements comparison (an auditor found 4 real deviations where
   the delivery claimed none; three of them were invisible to tests and CI).

Widget tests cover logic; they do not cover look/feel/navigation feel. Add
this standard to the implementer brief and to every UI-step wake directive.

## Evidence-hardened SUBMIT checklist (after 3 recurrences)

When the implementer's SUBMIT messages repeatedly cite fake evidence (placeholder
shas, run ids from PREVIOUS commits — caught 3× by the auditor in one day),
enforce these rules in the implementer directive AND the handoff brief:

1. No `verdict: PASS` until `gh run watch` completes **green on THIS commit**.
2. Real sha: `git rev-parse HEAD` read **after** `pull --rebase`, immediately
   before writing the message.
3. Real run: paste the run id + the final conclusion line of **this commit's**
   run, never a previous commit's.
4. Complete file list: paste `git diff --name-only` of the delivered range —
   no unannounced/smuggled files (a fix commit once shipped 13 files of the
   NEXT step's code in a guard-exempt folder). **Count it against the header:** the declared list needs one
   entry per changed path, and the path most often omitted is the one you think of as "part of the fix"
   rather than as an artifact — measured: 13 changed, 6 declared, and the missing one was the security guard
   itself. Hiding a change to a gate or a guard is the worst case of that class, so re-read the diff against
   the header immediately before committing, not while drafting.
5. One step per delivery; next-step code must be declared or split.
6. **Re-run every claim on the DELIVERED artifact before writing the letter.** A claim can precede its
   implementation: one letter asserted a naming fix whose new fallback still read a column name that does
   not exist, so the claim was false while every gate stayed green — and the fixture's own poison could not
   see it because poisons match by prefix. Two habits close it: run the exact command behind each sentence
   on the BUILT artifact (not on the code you just wrote), and count the thing your claim names — the
   number of poison CASES and the number of TESTS in a file are different numbers (`len(POISONS)` vs a
   pytest summary), and quoting the wrong one is a false claim a reader can check in one command.
7. **Every line of the letter's «not proven» field names what RETIRES it.** An open item with no expiry — the
   measurement, the artifact, or the input only the founder can supply — reads as permanent rigour and comes back
   unchanged in every round; write the closing condition beside the item, and delete the item the moment it closes
   (a claim that outlives its fix is the same defect as a fabricated one, one round later).

A failed delivery is also silently invisible: **push without a SUBMIT message
stalls the loop** (the poller watches mailbox paths, not code commits) — see
Delivery-completeness law. The implementer directive must end with "write the
message + update STATE before the cycle is complete", and the coordinator
should verify a SUBMIT exists after each implementer push.

## Green ≠ ran: cite the WORKFLOW that runs the suite (2026-08-12)

A delivery cited run `31557832912` as "CI green" — that run is the **Supply Chain
Security Scan** workflow (one OSV job). The workflow that runs
Analyze/Gate/Test/Build/Merged-manifest-audit is **Build & Release**, and on the
same commit it FAILED (Test hung 10 min; the audit step after it was skipped).
Three green-looking facts (Supply Chain success · a docs-only head commit whose
whole build job was SKIPPED by change-detection · the delivery's own claim) —
none of which is "the suite passed". Rules:

1. **Read CI, don't quote it:** `gh run list --workflow "Build & Release"` for the
   run on the CODE commit; quote the step-level result (`Merged-manifest audit:
   success`) from THAT workflow. A run id without its workflow name is
   meaningless.
2. **"CI green" and "CI skipped the build" are different sentences** — docs-only
   commits legitimately skip the build; citing them as green is a false claim.
3. The auditor treats a green quote from the wrong workflow as a STOP-level
   finding (`STOP-29`), and the lesson generalizes: any evidence claim must name
   its exact source (workflow, run, commit), or it is not evidence.

## Deployment checklist

1. Write `docs/handoff-protocol.md` + `handoff/` dirs + `handoff/STATE.md` → commit + push.
   The protocol must ENUMERATE the verification gates as commands with success
   criteria and name the authoritative artifact for each (test suite · end-to-end
   gate on a locked sample · leak/secret scanner · baseline corpus numbers). The
   auditor cannot see Hermes skills or local notes — gates it cannot run are gates
   it cannot check, and "verify the delivery" without commands degrades into
   reviewing prose. Mark any gate that costs money (a live end-to-end call) with
   its price, so the auditor knows when to run it and states that in its verdict.
   **Commit the auditor's own directive INTO the repo** (`docs/<auditor>-directive.md`)
   and hand the owner that text to paste: a versioned directive is reviewable,
   survives session loss, and both sides read the same bytes. It is a public
   artifact — no absolute home paths in it, or a repo leak-scan blocks the push.
2. Copy `scripts/handoff_monitor.sh` to `~/.hermes/scripts/`, edit REPO_PATH + mailbox paths.
3. Create cron (watchdog or implementer role per founder), `deliver=local`.
4. `cronjob action=run` immediately — the test catches config errors (see pitfall #1).
5. Give the other agent its poll prompt (e.g. Claude: `/loop 3m` with a shell
   pre-check that exits "idle" when nothing changed — see references file).
   In a shared working tree, ITS check must be the marker form too, not
   `HEAD..origin/main`.
6. Prove BOTH directions before handing the loop over. (a) The auditor's first
   tick: run its own comparison by hand — `LAST=$(git log -1 --format=%H origin/main -- <other-agent-dir>)`
   against the marker file; `LAST != marker` means the first review WILL fire,
   `LAST == marker` means it would idle forever (usually no bootstrap message, or
   a marker pre-set wrongly). (b) Real work pushed BEFORE the mailbox existed
   must be bootstrapped: the first SUBMIT message covers that work (an empty
   mailbox is an honest "idle", not a bug). Then the normal cycle: watchdog pings
   → implementer acts → other agent picks it up.

## Support files

**Split note (2026-09-19):** the file crossed the 100k skill limit and became unpatchable; the operational
sections moved out whole into `references/` — `rotation-and-wake.md` (rotation, wakes, crons, stalled-loop
diagnosis), `founder-views.md` (the founder-facing live state view), `loop-case-lessons.md` (STOP-28, suite
nondeterminism, founder walk, CARRY HOLD), and the pitfalls/FORENSIC-mode and mandate-authoring sections
were appended to `loop-operational-pitfalls.md` and `auditor-mandate-authoring.md`. Keep SKILL.md lean: new
depth goes to a reference named by topic, not into this file.
**How to split again — the cap will be hit again, and the failure mode is worse than bloat: once a SKILL.md
crosses the limit it becomes UNWRITABLE, so the skill stops accepting the very lesson that prompted the split.**
Move WHOLE sections, never fragments (a section cut mid-argument leaves two half-rules that contradict each
other when read alone); name each reference by TOPIC, never by incident or date, and group sections that share
a topic into one file; keep one line per reference in the Support-files list (a reference nothing links to is
invisible); run a zero-loss proof before declaring it done — every moved section's heading AND a distinctive
sentence from its body exist in the new layout, and no heading now appears twice, since a duplicated section
header makes the next reader answer from the wrong block; then prove the file is writable again by writing the
lesson that was waiting. A body that keeps growing is itself the signal: the next lesson belongs in an existing
reference, not here "for now".

- `scripts/handoff_monitor.sh` — hash-suppressed poller (edit the three vars).
- `scripts/stuck_watchdog.sh` — silent-unless-stuck alarm for a no_agent cron
  (unprocessed review + idle implementer → STUCK message → direct-launch).
- `scripts/carsah_auto_wake.sh` — THE deterministic coordinator (no_agent
  cron, every 5m): sees the marker mismatch, launches the implementer directly
  with the directive file. Replaces the LLM coordinator entirely (see the
  DETERMINISTIC COORDINATOR section). Update SESSION= on every rotation.
- `references/carsah-deployment.md` — full worked deployment: prompts, state
  machine, Telegram target, wake phrase, /loop command for the auditor.
- `references/carsah-live-config.md` — **the CURRENT, verified live configuration
  (2026-08-11): the four protected cron jobs, the auditor's /loop 3m directive
  (full text), the four markers, proven failure modes, and the rule: do not create
  new crons for the loop.** Read this before touching anything in the loop.
- `references/loop-operational-pitfalls.md` — the loop's measured failure modes
  in one place: stale-directive wake loop, marker 7-vs-40-char hash mismatch
  (endless wakes or permanent silence), rotation counting `active=1` only
  (compaction hides bloat — count TOTAL messages), CI-quote discipline (name the
  workflow, quote step level, never a docs-only commit), the guard-one-shape-
  leaves-the-other-half lesson (STOP-28's own fix carried a guessed 4×50ms wait —
  the auditor admitted "the guard enforces the half I fixed and not the half I
  left"; plant the SIBLING shape, not only the original), the provider/billing
  switch that must touch EVERY invocation point, cross-platform golden-test
  failures (tolerant-golden recipe — fraction tolerance, never delete the
  golden), and the execute-audit-waves-in-full pattern (one wave = one delivery).
- `references/fresh-session-brief.md` — handing state to a FRESH session (or a reader outside the loop): commit
  the brief in the repo and paste one line; the section skeleton, the constitution section, and the same
  discipline applied to a multi-track roadmap with gate-bound, measured statuses.
- `references/reviewing-peer-proposals.md` — judging the peer's PROPOSAL dossier (roadmaps, framework
  decisions, schema DDL): measure-first verification, count-vs-gate-line, deriving a round number, DDL
  silent-failure classes (unsynced FTS, non-normalising tokenizer, TEXT money + SUM), the load-bearing
  premise and its source, environment checks, and the unverified-list close.
- `references/subscription-implementer-alternatives.md` — the general class of
  flat-subscription implementers (CLI requirement + five conditions + the
  economics) with Kimi Code CLI as the verified case study + the one-step
  experiment gate.
- `references/performance-measurement.md` — metric set + baseline commands +
  verdict criteria for judging whether a new session configuration (skills at
  birth, skill map, HOW map) outperforms the previous ones.
- `references/guards-that-gate.md` — when a repo must stop a PUSH from publishing something and
  nobody can show the guard ever blocked anything: the ratchet (published per-file counts, passes
  declared debt / fails an increase), "what a push newly publishes = what the DESTINATION lacks"
  (a wider subtraction set is a hole; the `--not <glob>` pathspec trap; the three states of an empty
  result — nothing to do · could not read it · empty-against-a-wider-set), fail-closed with a declaring
  flag, hook defects that only a real push finds (stdin read once, undecodable blobs), the report
  discipline when a hostile review lands, and the line-by-line contract of a script that gates your
  own report.
- `references/empty-selection-guard-de069.md` — worked detail of the
  two-layer empty-selection guard (UI disable + use-case `ValidationFailure`,
  `null`=keep vs `[]`=reject) and the CARRY-106 coverage-transfer rule —
  exact code shape + mutation acceptance, from the 2026-08-14 founder-urgent
  fix.
- `templates/deep-audit-mandate.md` — copy-and-adapt skeleton for the one-shot
  DEEP AUDIT directive (section order + placeholders + the owner-facing usage
  note). Pair it with the mandate rules in this SKILL's «Two directives»
  section, which carry the why behind each part.

## Moved out of this file (read on demand)

The operational depth lives in `references/` — SKILL.md keeps the rules that must be in context on every
wake, and points at the rest. Nothing was deleted in this split (2026-09-19), it was relocated:

| Topic | File |
|---|---|
| Rotating a bloated session, wake machinery, crons, stalled-loop diagnosis, single-waker rules | `references/rotation-and-wake.md` |
| The pitfalls table (every one hit in the field) + coordinator FORENSIC mode | `references/loop-operational-pitfalls.md` |
| Authoring the auditor's mandate (loop directive vs one-shot deep audit, anti-patterns) | `references/auditor-mandate-authoring.md` |
| The founder-facing live state view and its traps | `references/founder-views.md` |
| Case lessons (STOP-28, suite nondeterminism, founder walk, CARRY HOLD) | `references/loop-case-lessons.md` |
