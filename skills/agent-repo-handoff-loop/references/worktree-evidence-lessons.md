# Loop lessons that cost a cycle each (measured on a real audit)

From a full implement→audit→fix→re-audit cycle (2026-09). Each item below is a
shape that produced a wasted round, a lost artifact, or a red push.

## 1. One worktree per round, created and removed by the same agent

- Create before the round (`git worktree add .claude/worktrees/review-N -b claude/review-N`),
  remove after it. Never reuse a recycled one: a session whose cwd is a recycled
  worktree silently loses its uncommitted files.
- Remove with `git worktree remove` then `git worktree prune` — **never `rm -rf`**,
  which leaves a stale registration in `.git/worktrees` that shows as a dead entry
  in every `git worktree list` afterwards.
- Before removing, run the pre-flight in the worktree(s):
  `git status --short` (must be empty) and `git log --oneline origin/main..HEAD`
  (count what is not yet upstream). Removing a worktree does NOT delete its branch,
  so an unpushed commit survives in the branch — but an uncommitted file does not.
- Watch for nested worktrees (`…/worktrees/A/.claude/worktrees/B`): remove the inner
  one first or git refuses the outer. Nested worktrees appear when a session inside a
  worktree creates another one.
- A recycled worktree can carry a leftover staged modification from an old state
  (e.g. a value that a history rewrite had removed). Inspect before trusting it.

## 2. Whoever writes a fix cannot judge it

If the auditor is explicitly authorised to implement a fix, the implementer must
review that fix before the loop closes, and the handoff must say so. An auditor who
ships code and then issues his own verdict is a judge of his own work — the exact
failure the loop exists to prevent. Expect a `REQUEST_CHANGES` whose author names
what he wants attacked; answer by *running* those attacks, not by reading the diff.

## 3. The repo's own guard may block the audit message

A publish guard that blocks long digit runs and hashes will block the evidence that
documents them (a full sha, a CI run id, a probe string). The rule is right; the
message is what must change:

- Describe the value and give a command that reproduces it
  (`python3 -c "print('1'*4+'2'*9)"`), instead of pasting it.
- Give the CI run as `gh run list --commit <sha>` rather than an 11-digit id.
- **Do not** widen the rule to fit your message, and do not add an allowlist entry
  without a written reason. Both weaken the thing being demonstrated.

**But tell that apart from a genuine FALSE POSITIVE — the RULE is still not what changes; the EXEMPTION is.**
The test is whether the blocked text could ever hold the real value. A rule that welds equal-width digit
groups (to catch `1234 5678 9012`) also welds a space-separated list of page numbers written in ordinary
prose — a real false positive — and the remedy is not to stop welding. **Discriminating by width and
separator was tried and reverted**: exempting 3-wide groups separated by spaces admits a fifteen- or
eighteen-digit account written the same way, silently, and no green run shows the loss. So:

- **A false positive on evidence gets a per-file exemption with a WRITTEN reason** (the repo's allowlist
  mechanism), never a tree-wide loosening. Where rewording is enough, reword: describe the value and give a
  command that reproduces it instead of pasting it.
- **Declare the price of the strictness.** The class the rule still blocks on purpose — a page-number list
  separated by spaces is blocked deliberately, because the rule cannot tell it from an account written the
  same way — belongs in the letter, or a deliberate cost reads as an oversight.
- **Any relaxation that does ship is documented where the code was**: the rollback and its reason live beside
  the rule, so it cannot be re-applied by accident in the next round.
- **The guard's own test file must itself pass the guard**: build forbidden strings at runtime (`"9" * 4`,
  `" ".join(_run(str(n), 3) for n in …)`) rather than as literals, or the honest fix is blocked by its own
  suite and the temptation is to relax the rule until the tests go green again.
- Expect this class exactly when the guard works on freshly generated evidence: digests, run ids, truncated
  hashes, and lists of page numbers all look like account numbers to a shape-only matcher.

## 6. An evidence file that carries the decision must have a WRITER

A verdict assembled by hand — numbers copied from two run files into a report — cannot be audited: a reviewer
finds a figure with no owner, and two files then disagree about the same quantity with nobody able to say
which is right. Rules for any file whose numbers justify a spend or a merge:

- **Reduce raw results to a verdict with a committed TOOL, not by hand.** Declare the criteria inside that
  tool (what counts as a win, the tie-breaks, which losses are kept), so the judgement is re-derivable, and
  test that two runs produce identical bytes. The tool, not the file, is the thing under review.
- **Never truncate an evidence list.** A `list[:14]` in a report dropped seven witnesses, one of them serving
  the author's own conclusion — a truncated list reads as full coverage and silently narrows what anyone can
  check. Emit every entry and assert `len(list) == counter` in the suite.
- **A value that names its source must be read FROM that source.** A cell claiming a setting comes "per the
  contract" while the code never opens the contract is a fabrication with good intentions: open the source and
  refuse delivery on a mismatch, by name.
- **State the comparison's bias and the read that would remove it.** When both arms are scored against a
  reference one of them produced, say so in the artifact; a stranger arm reproducing the same figure is what
  retires the doubt, and a paid read is what closes the residual unknown.
- **Import a peer's letter byte-for-byte and prove it.** Copy the file, then hash source and destination and
  record both in a manifest — a paraphrase loses the peer's own numbers, and the loop's trail is only worth
  what its bytes are.

## 4. A history rewrite invalidates every hash in every message

After `git filter-repo` (purging a leak, for example) the shas quoted in already
written audit reports no longer resolve. Handoffs must then anchor on **content and
commands**, not hashes, and the state file should say so explicitly — otherwise the
next reviewer spends a cycle on `fatal: unknown revision`.

## 5. Why the loop is worth its overhead

Self-review structurally cannot see its own blind spots: test suites where every
case passes for the wrong reason (a marker matched inside an unrelated word), guards
blind to the idiom the guarded file itself uses, and claims that drifted from the
measured report. An auditor who *measures with commands* finds those in minutes; the
author who wrote them cannot, because the same assumption produced both.

## 7. Late-round lessons: the exemption hole, the self-comparison, the declared list

- **Your new tests will cover the safe direction and miss the hole the fix opened.** The reviewer's sentence to
  earn: *the tests cover the safe cases and not one attacks the hole the exemption creates.* Add the case that
  feeds the newly admitted input, and assert the pair — rule blocks the real value, exemption resolves for the
  documented one.
- **A self-comparison is a dead check.** `v["spend"] == round(v.get("a_spend", v["spend"]), 4)` reduces to
  `x == round(x, 4)` and can never fail; derive the expected number inside the test from the raw sources.
- **Count the declared file list against the diff.** In one round 13 paths changed and 6 were declared, and the
  omitted one was the security guard — the path that feels like "part of the fix" rather than an artifact. Paste
  `git diff --name-only`, count, then write the header.
- **An environment delta is a measurement to make, never to rationalise — and the coverage it hides is usually
  the part that matters.** One suite read all-green in the main tree and `3 skipped` in the peer's worktree;
  the MEASURED cause is that `git worktree` does not carry GITIGNORED data, so the cases fed by the real local
  corpus — the ones that certify the deliverable — skip silently out of the reviewer's run, which then reports
  itself complete. Four rules:
  - **A guard about "is our coverage environment-dependent?" is itself code in an environment.** It was skipped
    in exactly the tree it was written to diagnose. Grade it by building a real worktree from the CURRENT WORKING
    COPY (a worktree from `HEAD` grades the committed revision, not the change about to be committed), running the
    suite there, and asserting the SKIP LINES NAME what is missing — a bare `skip()` reads as a pass, so an
    undeclared skip and a green test are the same byte pattern to a reader.
  - **Resolve interpreter and shared-repo paths structurally, not relatively:** `sys.executable` over a
    repo-relative venv, `git rev-parse --git-common-dir` over `__file__`. A guard that can be absent because of
    where it was run stops being a guard.
  - **Ship the remedy as one command** (`tools/link_local_data.sh <worktree>`) and give that command to the peer
    in its brief; a fix the reviewer must re-derive is a fix the reviewer skips.
  - **Reconcile a red/green delta on a CLEAN CLONE of the current head**, where the honest report is
    `N passed · k skipped, each named · 0 failed`. A delta explained in prose is a claim; the same delta
    reproduced and then removed is a measurement.
- **Every hand-typed number in one round was wrong; every tool-derived one was right.** A stated test count, a
  coverage pair that did not add up, a "zero spend" that measured $0.1963 — when the artifact already prints a
  count, quote what it printed instead of re-typing it, and treat "my hand is the writer" as the defect, not the
  convenience.
