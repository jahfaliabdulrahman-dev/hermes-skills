# Reviewing a peer agent's proposal dossier (roadmaps, plans, DDL, decisions)

The loop's peer also produces PROPOSAL documents — build change-lists, roadmaps to a future model,
framework decisions. Answering those is a different job from reviewing a diff: the artifact is a set of
CLAIMS, and the value added is separating what the peer measured from what it merely reasoned. Order
matters — the disagreement only lands if the measurements are settled first.

## 1. Verify the measured claims FIRST, and say which came out true

- Run the peer's own command for every code claim it makes, and report the results before any objection.
  A peer that wrote «measured, not remembered» earns that sentence back — and saying so explicitly is what
  makes the later disagreement credible instead of defensive.
- Then attack the INFERENCE, not the measurement. A dossier can be exact on every number and still wrong in
  what it concludes from them. Say it in that shape: «your measurements are true; this conclusion does not
  follow, for this reason». Do not soften the measurement audit to buy room for the objection.

## 2. Check each count against the line the TOOL prints, not the number beside it

- The recurring error is a count copied from a neighbouring column: «5,791 movements» slides into
  «5,791 dated rows» while the gate prints `5789/5789`. Quote the gate line, and name WHY the two differ
  (here: two anchor rows carry no date) — the corrected sentence should make the number say what it measures.
- Same class: a peer quoting the number of TESTS where the claim is about CASES.

## 3. Before attacking a round number, derive it

- A threshold like «≥ 15,000 samples» usually looks arbitrary and is often derivable from the peer's own
  artifact (measured witness-proven rows per layout × the layouts its own gate names). Deriving it converts
  a suspected decoration into a defensible gate; deriving it and finding nothing is what LICENSES the
  objection. Do this first — defending a peer's number with a measurement outweighs one more criticism, and
  it is also how you find that your own first read of it was cynicism.

## 4. Audit the DDL for silent-failure classes, never for style

- **An external-content FTS table with no sync triggers**: the index stops tracking writes, every later
  query answers from a stale set, and nothing errors. Ship the `AFTER INSERT/DELETE/UPDATE` triggers plus
  one `rebuild` after migration.
- **A tokenizer that does not normalise the language at hand**: Arabic letter variants (hamza forms,
  ta-marbuta, ya, tatweel) stay distinct, so search silently misses matches — and any comparison of that
  retrieval against another method then measures the tokenizer, not the method. Normalise before comparing.
- **A «text for exactness» rule the query layer can defeat**: money stored as TEXT, then aggregated with
  `SUM` → implicit cast → floats, which is the very thing the rule exists to prevent. State the prohibition
  and its companion rule (aggregate in the application with `Decimal`) in the same breath.
- Also worth encoding as a constraint rather than a check: «every row declares its proof source» belongs in
  the schema (`CHECK (proof_source = 'paper' OR proven_amount IS NOT NULL)`), so it cannot be lost when the
  gate is refactored.

## 5. Find the load-bearing premise and ask for its SOURCE

- A dossier usually rests on one external fact («the program requires framework X», «the client already
  runs Y»). It is not yours to assume and not yours to dismiss: name it as the premise, say that everything
  else follows from it, and ask for the source in writing. When the source arrives, record it in the state
  file with the decision — a decision recorded without its source is re-litigated by the next session.
- Related: a peer asking a question it cannot verify itself is showing judgement, not evasion. Answer it
  rather than treating the open question as a gap.

## 6. Check the plan against the environment it will actually run on

- A plan that assumes «one GPU card» on a machine with no card, a service the project does not run, or a
  dependency the venv lacks, invalidates its own schedule silently. Measure the environment (hardware,
  installed deps, quota) and re-rank the peer's candidates to the measured machine — the usual fix is to
  promote its small option from «alternative worth testing» to first candidate, and to make the expensive
  option a declared budget line before the phase, not after it.

## 7. Close with what you did NOT verify

- An explicit list — untested APIs, the peer's numbers with no command of yours behind them, comparisons that
  were argued from a document rather than run — keeps the review from reading as authority it has not earned,
  and it sets the next round: the first item on that list is the next experiment.

## Copy-forward discipline for the peer's letters

- Land the peer's letters into the repo mailbox **byte-for-byte** and verify with a hash per file. The sent
  letter is the record; your corrections live in YOUR letter, never inside their body.
- When the peer cannot push (its own session may refuse «out-of-place publication» to a public repo), pushing
  its branch or copying its letters forward is YOUR job: an untracked letter in a peer's worktree is one
  `git worktree remove` from loss, and the peer stopping instead of circumventing the refusal is correct
  behaviour to be recorded, not a failure to be fixed.

## 8. What the round OWES once an item is conceded

A concession is not a paragraph in the reply. Each accepted item converts into one of two artifacts, in the
same round as the acknowledgement:

- **A concession about your own MEASUREMENT ships as the probe that closes it.** If the peer shows that your
  headline claimed more than your evidence supports (a file's internal consistency presented as proof of its
  origin), the deliverable is the measurement you were missing plus the disclosure surface it feeds — the
  flags now read with a second tool, the «what this artifact cannot witness» block now printed on every run.
  The letter then reports the mechanism, not remorse.
- **A concession about a BEHAVIOUR becomes a number in a contract file, with a test that fails when it is
  absent.** «Make the cap an explicit limit instead of a default buried in code» is only satisfied when the
  value lives in the config/profile the project treats as the contract, the measured default it replaces is
  recorded beside it (so the difference is legible), and a test asserts the key exists and is positive.
  A knob that exists only in a letter drifts back into code on the next refactor.
- **Then re-check the peer's own demand for over-reach before adopting it wholesale.** Half of an objection can
  be exact while its remedy is not: adopt the part that is measurable, and say which part you narrowed and
  why — the peer's next letter will test the boundary you left.
- **Re-read the peer's ORIGINAL letters from disk before answering a version of them pasted into chat.** A
  paste is a rendering; the committed file is the record, and the sections a paste drops are usually the ones
  naming what the peer could not verify.
