# Answering a verdict on your own plan

Trigger: the peer returns FAIL / REQUEST_CHANGES on a **plan or design** (the review lands *before* the
code exists), and the founder's standing rule is that a peer verdict is never adopted on its authority:
«لا نسلم به إلا بالدليل والحجة والإثبات». The verdict is measured, exactly like the artifact would be.

## The response cycle

1. **Read the primary source, not the relayed summary.** The verdict's authoritative text is its committed
   letter — on the peer's branch (`git show <peer-branch>:<path>`), not the chat paste. A summary drops the
   enumerated list (which checks lack poisons, the exact remedy letters, the named open items) that your
   reply must answer one by one. Check the branch also exists locally before quoting it.
   **And enumerate EVERY delivery, not only the newest.** A peer that reviews a series writes one letter per
   round into its own mailbox directory (`handoff/<peer>/`), so "read them all" is literal: list the directory
   newest-first (`ls -lt handoff/<peer>/ | head`) and read each letter, because an EARLIER verdict can carry a
   numbered requirement list (`## المطلوب`) that the newest one does not re-raise — closing only the latest
   leaves that list open while the loop looks finished, and the peer re-finds it a round later. Keep the claim
   table per REQUIREMENT, not per verdict: one row per numbered item across all letters, each naming the commit
   that closed it, so a gap is visible before the peer finds it.
2. **Carry the peer's letter in YOUR delivery.** `git rebase <peer-branch>` puts the peer's commit under
   yours, so the mailbox gets their bytes and there is no second-hand copy; then verify:
   `git show <peer-sha>:<path> | shasum` == `git show HEAD:<path> | shasum`. A verdict that lives only in the
   peer's worktree is one `git worktree remove` from loss.
3. **Build a claim table: claim | the command YOU run | your real output | verdict.** Every row carries a
   command; agreement is a measurement, never an impression. Re-measure the peer's *own* figures too — a
   peer's arithmetic error is a finding of the same rank as yours.
4. **Find the artifact's own witness and let IT adjudicate.** Where the peer's reading and yours disagree,
   the deciding evidence is usually inside the artifact, not in either party's re-derivation (worked case: a
   range's opening balance — the peer's pre-movement value vs the post-movement one — settled by the printed
   cumulative footer delta: it matched one boundary exactly and contradicted the other by exactly the one
   A dispute resolved by re-deriving harder stays unresolved; a dispute resolved by the paper ends.
      **Tag that witness by WHERE IT LIVES:** a printed total inside the artifact is an INTERNAL witness — a
      transform applied document-wide scales it along with the values, so it stops adjudicating, and the exit
      condition for that class stays an artifact from outside the document. Calling an internal witness
      "quasi-external" breaches the tag ladder itself; when a peer catches that in its own letter it has
      protected the open item from being closed by a wrong remedy.
   paper ends.
5. **Run the peer's own proposed poisons.** If the poison they offer for a claimed hole passes, the hole is
   unproven — say so with the output. Their miss costs one line and removes a false constraint from your plan.
6. **Say which of their claims fell, with numbers.** A verdict that is 90% right is still 10% wrong, and the
   wrong 10% hardens into a rule if nobody measures it.
7. **Withdraw your own numbers that do not reproduce.** A figure whose generating command you can no longer
   re-derive — or whose DEFINITION (boundary, which rows are summed) was never stated — fails the evidence
   rule as surely as a hand-written one. Retract it in the same letter, hand authority to the tool that must
   emit it, and recompute every dependent number (the withdrawn count was load-bearing for a pack's size and
   composition: three published figures died with it).
8. **Close with «what I did NOT prove» and the condition that retires each item.** An open item with no
   expiry reads as permanent rigour and returns unchanged in every round.

## The measurement shapes that make a plan die (check these in your OWN plan first)

- **A number needs its DEFINITION, not only its command.** State the boundary/semantics beside the figure
  (which row is the opening; what the sum includes). Computed-but-undefined is not reproducible, and a peer
  will demonstrate it by shifting the boundary one row.
- **A closure/identity equation closes under any CONSISTENT omission.** Drop the boundary row and take the
  balance *after* it, and `opening + credits − debits = closing` still lands on 0.00 — a real movement then
  sits outside the ledger while the gate stays green. Pair every identity gate with (a) a mechanical boundary
  definition, (b) a counter of the items in the range, (c) a printed/external witness. Poison: shift the
  boundary by one row → the identity still closes, the counter and the witness must fail.
- **A one-directional metric false-passes.** An abstention-only score is 100% for a system that refuses
  everything; an intersection-ratio citation metric is unchanged by a fabricated citation (the poison does
  not bite in the direction that matters). Publish both directions — precision beside coverage, correct
  abstentions beside false abstentions — and print each rate's DENOMINATOR next to the rate.
- **A gate must measure the ARTEFACT, not a filter inside it.** A number computed over a subset describes the
  subset: an intersection gate keyed on the selected ranges (150 items) while the artefact was the whole pack
  (200 = frozen set + ranges) declared 100 items where the truth was 133 — a third of the cost invisible, and
  the item was the one the owner was about to be asked to approve. Its own poison sat INSIDE the filter and
  bit hard, which is the lesson: a poison that lives inside the population proves the gate bites, never that
  its population is complete. Rules: the population is the whole artefact and it is PRINTED beside the number
  (`|200| = frozen 50 + ranges 150`, never a bare 150); the volume gate and the intersection gate work on the
  same population; and every gate needs a POPULATION CONTROL beside its poison — an item that belongs to the
  population but sits outside the old filter (a captured item drawn from the frozen set) which the old code
  could not see. **The diagnostic that exposes the class before a peer does: a cost figure that moves with a
  knob that should not affect it.** This price swung 86 → 123 as the filter's composition changed while the
  real figure stayed ~32.6%, because the pack is a fixed size and what moves between its parts stays inside
  it — a figure that tracks the knob is a figure about the knob.
- **A cost is stated in TWO columns whenever the decision spends data.** A cash figure alone reads as "free":
  `$0 in cash (re-derived from the run cache) · −1,253 of 3,841 training rows = 32.6%, leaving 283 pages`.
  One column is half a disclosure, and the missing half is the one the decision actually spends.
- **A pack whose membership comes from the evaluated system's own outputs selects itself.** As the system
  improves, the hard cases leave the set: the score rises without improvement on a fixed set. Freeze the
  membership LIST at build time, verify against the list's hash, never re-run the classifier inside the
  verifier, and publish classification drift as a separate report *about the system*.
- **Once a set is frozen, its rule is a LIST, not a formula.** A modular reservation (`page % k`) cannot
  survive any contiguous selection, so the frozen list becomes the exclusion list for training/capture, and
  the capture tool must refuse to write a page the list owns (that refusal is the gate's poison).
  **And an exclusion claim is an INTERSECTION per document, recomputed from an append-only log that lives
  outside the tree** — the already-captured items were chosen under the OLD rule, and a manifest kept inside
  the tree dies with whatever it documents. Measure it before promising it: in a real round every page of the
  existing capture sat inside the first candidate selection, so a naive range would have absorbed 100% of it.
  Block those items from selection too, and keep `set ∩ captured = ∅` as a gate with its own poison (put a
  captured item into the set → the gate fails by name).
  **"Per document" is a requirement on the KEY, not a property that was measured.** A live version of this gate
  was keyed on the page number alone while the capture and the evaluated set came from two different documents;
  the peer's blocking item named it and was right. Verify the identity before believing the exclusion: hash both
  source files (`sha256(...)[:16]`) and the collision is visibly a coincidence of numbering, then confirm with
  the two documents' PERIOD spans (computed from their own rows — zero shared pages in the measured round) and
  with the CONTENT intersection on the natural key (date · amount · direction — 0 of 297 samples). Identity is
  the keying check; content is the only check that actually MEASURES contamination, because two documents with
  different hashes can cover the same period and the same rows and pass an identity check while contaminating
  anyway. When the counterpart list does not exist, the printed value is `unknown` — never `∅`.
- **Small-n honesty:** a 50-item set is ≈±8.3 points at 90% (it cannot separate 90 from 98); print
  fractions, not percentages, for classes under 10 items (one miss in a 4-item class is 25 points); report
  arms separately instead of weighting them (a weight puts a judgement inside a number that must stay
  mechanical).
- **A measurement helper must not share mutable state between the values it reports.** An accumulator that is
  appended and then cleared in the same expression yields the same empty object in every slot, so the reported
  lengths collapse to 0/1 instead of the true 2 — a wrong number in the safe-looking direction, produced by the
  instrument rather than by the data. Keep such helpers pure over independent values, and assert a NON-TRIVIAL
  case (a run of exactly two must read 2): a fixture where every run has length one passes under the defect,
  which is what let it survive an earlier round.
- **A count with no member list cannot enter a set operation — declare it count-only and BOUND the result.**
  A source report can carry a class as a bare number (`checked: 17`, `unchecked: 2`) with no membership
  anywhere, so any union or overlap computed over it is a guess. Print the sum AND the union, tag each class
  with the file and field it was read from, mark the list-less ones `aggregate-only`, and give the honest
  interval (`union between 8 and 27`) instead of the flattering single value; a plan's composition figure then
  fails to reproduce visibly rather than silently — real case: a claimed `22 structural of a 50-item set`
  whose sum matched (4+3+4+2+17 = 30) while only 8 items had lists, and whose reader half measured 68 items,
  not the claimed 30, which also proved the set was built by a DIFFERENT rule than the one being described
  (mechanical closure vs symptom flag) and that the set's size had been an input all along. Hand the number
  authority to the tool and correct the prose in the same letter; where the definition itself is contractual,
  declare it and leave the change to the committee rather than editing the contract alone.
- **Declare an impossibility STRUCTURALLY, never as a shortfall a bigger input could close.** "Short by 49
  items" invites "find a longer document"; the structural form ends the question — a periodic reservation of
  every k-th item can never place two reserved items adjacent, so a free run is bounded by k-1 neighbours
  times the released exceptions, i.e. a small constant, while a contiguous run of 50 demands more than any
  corpus of this construction can give. State the bound, and tighten it even when the conclusion does not
  change: a bound wrong in the safe direction (measured 2 reported as 1, while the structural ceiling is 3)
  reassures without warrant, and the next reader who measures it stops trusting the letter.

## Answering a PASS that carries a condition

A PASS *with one gate* is answered by measuring the gate's PREMISE before satisfying the gate: conforming to an
impossible rule is exactly the failure the gate existed to prevent.

- **Re-measure the condition's own threshold with the FULL frozen input.** Worked case: "three ranges free of
  the frozen set, each ≥50 items". With the full frozen set, free runs of that length number exactly one, and
  the best per segment were 39 · 54 · 29 — unsatisfiable as written. The peer had measured with a PARTIAL set
  and saw three, with no margin: a partial input makes a constraint look feasible. Never promise a threshold
  you have only tested against a partial corpus.
- **Then question the premise, not only the threshold.** The constraint existed to avoid double-counting items
  that are in the set twice — but the ranges are set members either way, so the blocked class inside a range
  costs nothing. Relaxing that premise turned one impossible threshold into several available ranges
  (163 + 241 + 50 + 110 = 564 items against 150 required).
- **Re-run every gate the relaxation touches, and let the artifact answer.** Ranges that contain the blocked
  class were re-measured for closure: identity plus BOTH printed deltas at 0.00, with the item counts beside
  them (732 · 1,682 · 1,400). A relaxation is admissible only with the gate re-measured — never with the
  argument that it "should" still hold.
- **Declare the fallback numerically in the same letter, before the gate can fire.** Satisfy "choose now
  rather than under build pressure" with three parts: the gate FAILS BY NAME and prints the measured numbers
  it saw; the first fallback (more, shorter ranges) and the last resort (a smaller, declared set) are written
  down; and the measurement shows the fallback is not needed today. A rule silent about its own failure mode
  is decided by whoever is under pressure when it fires.
- **A rule change invalidates prior claims about the old rule; recompute them per item.** Switching a
  selection rule means previously captured/trained items were picked under the old one, so "nothing in the set
  was trained on" is an intersection to compute, not a consequence to assert.
- **When your count and the peer's differ, hunt the DEFINITION before assuming an error.** 27 vs 25 resolved
  as: two of them sit adjacent to the single item that carried no classification, so one count includes them
  and the other does not — both correct under their definitions, and the difference is itself a boundary
  question. State the definition you counted under; do not "fix" a difference that is not one.
- **Record the peer's self-corrections as loudly as your own.** A peer that retracts its own framing — e.g.
  admitting a witness it called external actually lives inside the artifact — has just kept an open item from
  being closed by a wrong remedy; that item stays open with its real exit condition.

## When the condition's fix is a CODE change: close the hole without opening one

Satisfying a condition by editing the tool is where a fix becomes the next defect: the reviewer's next pass can
find that the guard you added lets the tool DEMOTE a proven value to `null` and exit 0 — a loss with a green run.
The root sits one layer below the obvious one, and a guard-only fix cannot hold without it.

- **A writer MERGES its declaration into the artifact; it never rebuilds the container.** Re-assigning the whole
  block (`report["provenance"] = {…}`) drops every field a previous run declared, and the erasure happens BEFORE
  any guard reads the state — the guard then sees an empty block and concludes it is free to write. Grep the
  assignment: a writer that constructs a fresh dict for a block it does not exclusively own is this defect.
- **A guard whose precondition is `None` BY DESIGN can never fire.** Requiring a field that is legitimately
  absent (the identity is unknown — the very reason the tool exists) is the same dead-check class as a matcher
  that exams zero rows; a branch gated on another field being non-empty joins the class. Judge a precondition by
  whether it is SATISFIABLE on the real artifact, not by whether it is present in the code.
- **Scope a skip-early guard to "nothing can be learned", not to "a value exists".** Skipping when the declared
  value is present *and* the source file is present means a CONFLICTING source never gets compared and passes
  undetected. Skip only where there is no source to verify against; where a source exists, verify it.
- **A proven value is never downgraded silently.** Upgrade unknown → value (allow it); downgrade value → unknown,
  replace value → *other* value, and accept an absent source only by STOPPING BY NAME with a non-zero exit and
  BOTH values printed (the established one and the newly derived one). A real replacement requires an explicit
  flag, and the honest neighbour of a missing source is a declared `unknown` — never an empty string, never `∅`.
  The loud no-op is the fix; a quiet success is the defect.
- **Test every STATE TRANSITION, not every state — the previous state is part of the input.** A case proving
  `empty → null` cannot see `filled → null`. One case per transition: empty→value, value→identical (no-op that
  declares itself), value→conflicting (stops by name), value→source-absent (keeps and says so). Re-run the
  reviewer's own command VERBATIM as the first case and report the before/after value pair — "the suite is green"
  and "the proven value survived" are different claims, and only the second one answers the finding.
- **A downstream consumer must fail on the degraded value, not absorb it.** Where the artifact's key can arrive as
  `null`, the build that reads it stops by name: passing `null` through as `unknown` recreates precisely the state
  the earlier gate was built to escape, which is why such a defect outranks an ordinary one when scoping the next
  step.

## When the peer's blocking item is RIGHT

Accepting a verdict is not echoing it: confirm it on independent layers, then strengthen the fix with the check
neither side ran, and re-measure what the remedy COSTS before signing it.

1. **Confirm the blocking claim on more than one layer before conforming to it.** The three cheap layers, in
   order: IDENTITY (hash both source artifacts — differing `sha256[:16]` makes the collision a coincidence of
   numbering), PERIOD (each document's own date span ⇒ zero shared pages in the measured round), CONTENT (count
   the intersection on the natural key — 0 of 297). Two layers already refute the contamination the gate claimed
   to block; the third is the one that measures it, and it is the one to keep as the standing check.
2. **Lift the block and state what it cost, in numbers.** A remedy that protects nothing is a real loss: name
   the items freed and the selection start that changes (page 1 instead of page 18), so the next reader sees a
   correction adopted rather than a concession — and say plainly that it overturns your own earlier figure (the
   number the block rested on becomes 0%), because a wrong constraint that reads as caution is still a wrong claim.
 **The cost of adopted work is reported in two columns (cash · data), with the share of the artefact it
 consumes and what remains after it.**
3. **Re-aim the poison at the shape the fix now admits — negative control first.** The case the OLD gate falsely
   blocked must now pass, and that case is the regression test for the defect the peer found; then add the case
   the new content check must catch (a counterpart row sharing the pack's date/amount/direction).
4. **A right verdict usually means the OUTER rule was mis-scoped, not just the code.** Rewrite the rule where it
   is written (the plan, the gate's own declaration) so the next implementation cannot re-derive the same
   mis-keying from a rule that never said which parts must match which.
5. **A forced consequence is not an independent witness — count your evidence honestly.** When one field sits
   INSIDE the composite key, disjointness on that field FORCES the result on the others: the honest description
   is "two independent witnesses + one necessary consequence", never three witnesses. Say it in the letter
   rather than banking the extra strength — a consequence dressed as an independent check is the same class of
   error as a fabricated figure, and it hides that the check has never actually bitten.
   **And measure the key's discriminating power before trusting it:** a single field matched ~68% of rows across
   two unrelated sources, so an amount-only key would have been 68% false alarms — that measurement, not taste,
   is what justifies the fuller tuple. And where a check's passing result is inherited from a gap in the input,
   it has not been tested at all — say so (see the `prepared` vs `tested` label in Measurement hygiene).
6. **Lifting a block lands on a BOUNDARY the rule never had.** Removing a blocked class returns the selection to
   item one — where a predecessor-anchored rule has no predecessor at all, so it either dies on the first case
   or shifts silently to item two. Enumerate the rule's own boundary cases (first item, empty input, last item)
   and branch each one explicitly: an anchor stated as the artifact's printed opening value with zero cumulative
   totals, and its own poison. State the poison's MAGNITUDE, not just its direction — "anchoring one item later
   shifts the deltas by exactly X and Y" catches the partial degradation a boolean "fails" hides — and the
   SIGN is information: a NEGATIVE shift says the wrong anchor CONSUMED an item that still sits inside the
   range, so the reading names the mechanism, not only the size. The poison should also trip SEVERAL gates with
   DIFFERENT values (defect case: identity 100.00 · debit delta −650.00 · credit delta −750.00); gates that all
   print the same number are one measurement echoed, and saying so is what turns "independent gates" from an
   assertion into a demonstration. State the poison's PRECONDITION too — the same mis-anchoring on a range that
   starts one item later closes at 0.00 and is CORRECT, so a poison without its precondition is a future false
   alarm (measured: range 2–171 anchored on frame 1 → identity 0.00, 1,630 items).

## Measurement hygiene while you do this

- **Probing unknown data: print KEYS and COUNTS, never raw value distributions.** One exploratory `print`
  of a full field dump can flood more context than the entire review costs — keep the probe bounded, then
  measure deliberately.
- **Rebuild every count from the artifact you delivered**, not from the design document: a census the plan
  promises and the tool cannot re-emit is not a number. **And take it from the COMMIT, not from the working
  tree:** `ls` / `ls -A` on a directory counts artifacts of the moment (a `__pycache__` appears after the first
  test run, `.DS_Store` comes and goes), so the same claim yields different numbers on the two sides of the loop
  and both parties look wrong — `git ls-tree -r <sha> -- <path> | wc -l` is a function of the commit, and that
  command is printed beside the figure. When a count differs, first ask whether the two commands are functions of
  the same thing before calling it a discrepancy: the stable convention is the one that cannot change under the
  other party's feet.
- **A state file records its WRITER and TIME.** A state file that changes mid-round with no writer recorded
  means two writers on one file — and whichever plan it now describes can be read downstream as approved.
- **When the peer's claim is about a function, run the function.** Cheapest falsification available: one
  call on the two strings they named, and the claim is either dead or confirmed before you spend a paragraph
  on it.
- **Count with a POSITIVE predicate.** A unit is what it HAS, never what it is NOT: "rows that carry an amount"
  excludes the carry-forward row; "rows whose status is not <X>" silently includes it. Real off-by-one: 1,642
  vs 1,641 on the same range, where the opening row rode along inside the negation. Name the predicate,
  re-count, then compare — and say whether the repair was a DEFINITION fix or a value change (a definition
  repair leaves every equation unchanged while moving the printed count).
- **Label each gate `prepared` or `tested`, and say which.** Prepared = built and never exercised on a case
  that could break it, including a result inherited from a gap in the input (disjoint periods, absent
  counterpart list). Writing the state beside the gate turns its first real test into an expected event rather
  than a silent assumption of strength.
- **A component the plan NAMES may not exist — enumerate the paths before promising its output.** A plan's own
  vocabulary reads as an inventory: a tool, flag, doc or test suite can be referenced across many rounds
  ("then `--build` emits the list") while never having been written, because the name came from the design and
  the design was never diffed against the tree. Cost of skipping the check: the round's promise describes
  running something that must first be written, and the peer scopes its next review at the wrong artifact.
  So before a letter promises an artifact, list the concrete paths it depends on (`tools/`, `docs/`, `tests/`
  contents, or a direct existence probe) and say for each whether it exists; when it does not, the step is
  **writing, not running**, and following an existing precedent in the same tree (an established tool's
  declaration/backfill pattern) is part of the answer.
