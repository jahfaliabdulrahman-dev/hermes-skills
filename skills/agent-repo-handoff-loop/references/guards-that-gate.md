# Guards that gate a PUSH (not a tree) — lessons with their measurements

Applies when a repository must stop a *commit/push* from publishing something, and when a
guard already exists but nobody can show it has ever blocked anything.

## 1. A guard that is always red is not enforcement — it is an invitation to `--no-verify`

Measured on a real repo: the guard matched a shape ("an amount-looking token") that appears in
**legitimate test fixtures**, so every push after it landed was red. The pushes went through
anyway — which is why a real secret reached public `main` twice. The fix is not "more rules":
it is a **ratchet** — a *published* baseline with a per-file COUNT (no values, no fingerprints,
no digests: a fingerprint of an enumerable domain is not a mask) that

- **passes** the declared debt (so the honest path is green and `--no-verify` stops being rational), and
- **fails** the moment one occurrence is added.

Prove both directions on the SAME mechanism, and quote both outputs:
`PASS — the pushed range adds no occurrence` and
`BLOCK — occurrences rose: tests/test_chain.py 9 → 10`.

Corollary: the debt number must be **re-measured**, never inherited. Fixing the matcher changed
the count 39 → 42, and rewriting one file removed an occurrence → 41. An inherited number is a
claim about a check that no longer exists.

## 2. "What a push newly publishes" = what the DESTINATION lacks — not `rev-list <local>`, and not all remotes

For a new branch (remote sha all zeros) `git rev-list <local>` returns the WHOLE history. Measured:
**1407 commits** instead of 3. Consequences, in order of nastiness:

1. the guard scans history that is **already public**, so declared debt in old commits becomes a
   **permanent hard block** — the always-red trap, reintroduced from another door;
2. cost is linear in the wrong thing (all history × all blobs).

Use `rev-list <remote>..<local>` when the destination's sha for the ref is known; for the zeros case
subtract **the destination's own refs** — not `--not --remotes`. Two measured reasons:

- **`--not --remotes` subtracts every remote**, so a commit a backup (second) remote already knows reads
  as "published": the range comes out empty and the push to the real destination — which does publish it
  — passes green. Same bytes: red with one remote, green once a second one is added.
- The destination is named on the command line: git hands the pre-push hook the destination as `$1`.
  Pass it through (`--pre-push --remote "$1"`) and scope the subtraction to that remote only.

**Never write the subtraction as a ref glob.** `git rev-list <sha> --not refs/remotes/R/*` does NOT
expand the pattern as a ref — git reads the unmatched argument as a **pathspec**, exits 0 and prints
NOTHING. That silent empty output is the worst possible answer for this guard: it reads as "nothing to
publish". Enumerate instead: `git for-each-ref --format=%(objectname) refs/remotes/R/` and pass those
shas to `--not`. And when the destination's refs cannot be read at all that is *not* «empty» — fail
closed with the fetch-then-retry instruction, because an unknown destination is exactly the case where a
subtraction assumption turns into a published secret.

Check whether git-wrapped guards in your repo, and the pre-push hook's own two guards, agree — two
guards that compute "the pushed set" differently will disagree in public.

### Emptiness is three states, not two

Any guard whose honest result can be empty must separate them, or one of them becomes a hole:

| State | Signal | Answer |
| :--- | :--- | :--- |
| Legitimately nothing to do — no refs to update, a branch deletion, a tip the destination already has | the input parsed and every range resolved | **pass, with a declaration** of what was therefore not checked |
| Could not read it — malformed/truncated input, a range that failed to resolve, unknown destination refs | the input did not parse, or a range did not resolve | **fail closed** |
| Empty measured against a set WIDER than the destination | the subtraction set carries refs this push does not target | **not a measurement** — fix the set, do not pass |

Three rules keep a relaxation honest:

- **A change that turns a block into a pass must arrive with a test that attacks the shape it newly
  admits.** The branch-deletion case proves the pass is safe; only the wider-subtraction case proves it is
  not too wide. Write it so it fails against the pre-fix code — and, when you can, so it fails against
  your own first attempt at the fix: a test that cannot tell two implementations apart is decoration.
- **Delete any assertion that cannot fail** instead of leaving it beside the new one. An assertion
  accepting `rc in (0, 1, 2)`, or either of two contradictory messages, documents nothing while
  inflating apparent coverage — in a guard's own test file that is a defect, not a nit.
- **A malformed input line is not an empty input.** A non-empty stream that yields no readable entry is
  state two (fail closed): parse the input shape strictly (the exact field count you expect) and count
  the lines you could not read.

## 3. The hook is the only honest test of the hook

Two defects survived unit tests and died on the first real `git push`:

- reading pushed blobs with a text-mode subprocess (`text=True`) — an undecodable blob raises
  `UnicodeDecodeError` mid-scan. A blob that is not valid text is skipped **deliberately**, and
  that skip is a declared rule, not an accident;
- reading `stdin` MORE THAN ONCE: the pre-push protocol delivers the refs on stdin, and the first
  child that reads it consumes them. `REFS=$(cat)` once, then feed every guard from the variable.

So: run the hook **by hand** first (`printf '<local ref> <local sha> <remote ref> <remote sha>\n'
| .githooks/pre-push`) for both the existing-branch and new-branch shapes, then push for real
without `--no-verify` and quote the hook's own line from the successful push.

## 4. Resolve the evidence directory by its EVIDENCE, not by its directory

A guard that needs a local manifest/key/secret must find it from anywhere (`--git-common-dir` in a
linked worktree, a subdirectory, another checkout of the same clone). Test for the **file**, not
for the parent directory: a linked worktree carried `data/sample/` (a tracked fixture) so the
`data/` check resolved to the wrong root and the guard fell closed on a legitimate push.

And keep fail-closed honest: no evidence ⇒ non-zero exit, with a single explicit flag that
*declares* the absence on surfaces where the evidence legitimately does not exist (CI), and prints
what it therefore did NOT check. A green CI badge must never be quotable as "the amounts are clean"
when the manifest was never there.

## 5. A temporary harness built from `HEAD` measures what was committed

The injection harness (poison a value, require the guard to fall) created its scratch worktree from
`HEAD` — so it exercised the *committed* guard and reported "all poisons survived" while the fix
sat uncommitted in the working tree. Copy the working tree (`tools/`, `src/`) over the scratch
checkout, and say so in the harness. This mistake repeats across projects; it is the same class as
"a guard's worktree measured the wrong revision".

## 6. Guard the guard: audit each guard by making it fall

Add the new guard to the repo's guard-audit (inject a defect in its code, require its tests to
fail, verify the file hash is restored). A guard that is not in that list is declared open, not
assumed working. Cheap strong injection for a matcher-shaped guard: make the predicate return
`False` — the scan finds nothing, and a strict `xfail` declared-debt test flips to XPASS ⇒ failure.

## 7. Report discipline when answering a hostile review

- Every claim gets the command and its output; never "verified" as an adjective.
- A claim in your own previous letter that turns out false is **corrected in place with a dated
declaration** — the sent text stays, and the new block names what is void. Do not silently edit history.
- List separately: (a) claims of the reviewer that FELL (with the measurement), (b) your own numbers
  that MOVED, (c) what you did NOT prove. The reviewer's wrong sub-claims must be answered with a
  measurement, not with agreement.
- Anchor the delivery to the **merged** sha (a squash/rebase merge rotates the branch sha); state the
  branch shas as history.
- Read CI from the **log**, not the badge: quote the step line that shows the guard actually ran and
  what it printed about what it could not check.

## 8. When the repo gates your own REPORT with a script, its shape is a contract

A report gate (`scripts/check_*.py` run over the delivery document) parses **line by line** and refuses
the delivery on shape, not on substance: a well-argued report can be rejected three times in a row for
format alone. Learn the parser's expectations before writing the prose:

- **Fixed section names, in the language the parser expects, verbatim.** A report whose *content* is in
the working language but whose *headings* are the parser's English names passes; translating the headings
fails the required-section check. Keep content and headings in their separate languages.
- **The verdict section must contain one of the accepted tokens literally** — a verdict written as prose
  ("the blocking items are closed") is not a verdict to a parser.
- **One finding = ONE line**: severity label + `file:line` citation + evidence tag, all on the same line.
  Continuation lines that carry a tag are parsed as separate findings with no severity; a finding line
  whose citation the parser cannot recognize is rejected as uncited. Prose around a finding is safe —
  wrapping the finding itself is not.
- **Run the gate's `--self-test` once** before trusting a green run over your own report: a gate never
  seen to fail is `unknown`, not `safe`.
- Write the skeleton first and fill it second; after any structural edit, run the gate on the exact file
  you are about to quote, and expect a second iteration.
