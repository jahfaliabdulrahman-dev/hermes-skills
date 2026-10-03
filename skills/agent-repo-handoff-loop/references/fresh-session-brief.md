# Handing state forward: the fresh-session brief, and the roadmap half

When a long loop has burned its context, when the founder wants to work in a clean window, or when a
multi-week effort needs a checklist a reader outside the loop can follow, the artifact is the same class:
**a document in the repo that carries state, gates and next steps**, so the next session starts from the repo
and not from a chat log.

## The move: put the brief IN the repo, hand over ONE line

A 150-line prompt pasted into chat cannot be reviewed, cannot be corrected when a figure moves, and is gone
the moment the session scrolls. Commit the brief as a repo file and give the founder a single paste-ready line:

```
read handoff/PROMPT-<effort>.md and execute it from the top
```

The brief is then versioned, diffable by the peer auditor, and re-readable after any context loss. Publish it
through the normal path (branch → PR → green check → merge) and read the merge sha from `origin/main`
afterwards; verify the PR range is exactly the one file you meant to publish.

## Skeleton — every section earns its place

1. **Where to start** — the files to read FIRST, in order, each with one clause on why (state file, acceptance
   contract, protocol that lists the gates, risk register, the plan, the newest letters). Name which skills to
   load. The new session knows NOTHING; it learns the project from the repo, so a brief without this section
   produces a session that invents its own context.
2. **The measured state** — the numbers as of writing, each with its source; where the inputs live; the
   invariants that must not move; and an explicit "do not re-measure what was just measured" (or the first hour
   is spent rebuilding the baseline instead of advancing it).
3. **The constitution** — the rules that each cost a review round, imperative, one line of mechanism each. This
   is the highest-value section: it is the only place a new session can learn in one page what the previous one
   learned in twenty cycles.
4. **The gates as COMMANDS** — the exact invocations with expected outputs, including environment fixes (the
   data-link script, the expected skip count). A gate the reader cannot run is not a gate. Mark any gate that
   costs money with its price.
5. **The items** — one per workstream: goal · exactly what to do · **its acceptance evidence** (what must be true
   when it is done). No item without a gate.
6. **Operating obligations** — one step per round, state file updated in the same commit as the close, the
   peer's letters copied into the mailbox, owner decisions recorded verbatim (with the date they were decided).
7. **Exclusions** — settled decisions that must not be re-opened. An exclusion written down is cheaper than the
   argument it prevents, and it stops a fresh session from "improving" a deliberate choice.
8. **The first steps** — literally the first actions, ending with "produce a short plan for item X and wait for
   approval before writing code" when the founder wants to learn rather than only receive.
9. **What this document does NOT prove** — estimates flagged as estimates, claims cited from letters rather than
   measured today, premises owned by somebody else (a committee, a provider, a spec).

## The roadmap half: same discipline, several tracks

A roadmap is a brief with statuses attached. Rules that make it usable instead of decorative:

- **One track per audience, clearly separated**, each with **its own definition of done**. A single blended list
  hides the fact that the tracks finish differently — and one may finish while the other is still unproven.
- **Every line is a claim.** Mark done / partial / not started, and beside each mark say whether that status was
  MEASURED now (with the command) or CITED from a letter. Never infer a status from the fact that no letter
  mentioned it.
- **Measure the negative too.** "Not started" is a claim: grep for the symbol, module, or import the item would
  introduce (`grep -rln <symbol> src tools` → empty is evidence; "I did not see it" is not).
- **Bind every item to its gate in the item's own words** («the rendered file equals the current file row by row
  — one difference = stop»). Where the closing condition is a DECISION rather than a measurement, say so and
  name the owner; never present a decision as pending work.
- **Keep in-flight work OUT of the tracks** — its own section, one owner per line, with its measured state. The
  plan and the hour's work are different objects; mixing them makes both unreadable.
- **Never copy a guarded value to make a document look complete**: name the invariant and state that its value is
  read by command from its source. Run the repo's guards over the new document before committing it.
- **Close with what the document does not prove** — estimates as estimates, external premises as unowned, and
  any status list scoped to what was actually found in the state file and letters.
