# Directives for a One-Shot External Audit (the directive is a repo document)

Use when the owner asks for an independent review of the WHOLE system rather than of a single
delivery: a forensic/engineering audit of code and data, or a strategy audit of the idea, the
market and the economics. Both travel through the same mailbox as the review loop, but they
are a different contract and a different session.

## Why the directive lives in the repo

The external agent (Claude Code, Codex, any CLI) **cannot see the Hermes skill library or
anything outside the checkout**. The repo is the only shared language. So the mandate is a file
the agent reads on its own (`docs/<agent>-<lens>-directive.md`) delivered with a one-line
kickoff, never a wall of text pasted into a chat the next agent cannot re-read.

- Anything the auditor must verify has to exist in the repo (files, gates, acceptance
  criteria). Never instruct it to check a skill, a convention, or a memory that lives
  Hermes-side — it cannot, and asking it to check something invisible erodes its edge.
- Write an owner-facing preamble at the top: what this directive is for, when to run it, and
  what it is NOT (the per-delivery review). Future sessions and the owner read that first.

## One lens per directive (the mistake that costs the most)

Engineering/forensic (does the system do what it claims?) and strategy/judgement (is it worth
building, for whom, at what price, what would make a rational owner stop?) are **separate
directives and separate sessions**. Merged into one, the engineering register dominates, the
business verdict arrives last and thin, and the auditor has spent its context on code. Run
engineering first if both are needed — the strategy pass then re-ranks the engineering findings
from the business side and is expected to disagree with their order.

## Section skeleton that worked (engineering lens)

1. Identity and role + the rule that the auditor does not write code.
2. Ordered read list (docs first, then code) — "no verdict on a file you did not open".
3. What the project is, why it exists, how it evolved, the stack, the end goal — so the auditor
   can name the central claim it is attacking.
4. The measured baseline presented as **claims to falsify**, each with where its evidence lives
   and how to disprove it.
5. Governing rules: privacy of the auditor's own report, repo-only scope, no code, cost gate.
6. Attack axes with ready-made hostile questions: correctness and reproducibility · provenance ·
   privacy and leakage · resilience · output honesty · security and supply chain · operations
   and continuity · claim honesty · cost and scale.
7. Required deliverables (below).
8. A what-if section running the full anticipatory protocol.
9. What NOT to produce: verdicts without a reproduced command · praise · re-narrating the
   documentation · rewrite-it-all advice with no cost attached.
10. Delivery path, evidence rules, and the owner-decisions list.
11. Cost/effort budget, plus permission to deliver a partial report that names what it did not
    examine (a declared gap beats a guessed completion).

## Section skeleton that worked (strategy / market lens)

- Separate three questions and forbid merging them: is the technique sound · is the product
  wanted · can it be defended. "Technique excellent, nobody needs it" must surface in exactly
  those words.
- State the project's hard constraints as the **measuring stick for every alternative**, not as
  background: degraded scans, non-latin digits, table layouts with no fixed schema, high-stakes
  outputs, mandatory transparency, data residency, one-person operation.
- Force a scored table over whole architecture families (purpose-built local reader · generic
  cloud reader · strict hybrid with an independent referee · a big vendor's prebuilt service ·
  avoid the hard input entirely · human-in-the-loop · service-before-software), judged on
  accuracy · provability · cost per unit · sustainability · compliance · effort, with a
  recommendation AND why each loser loses. Relative grades only — no invented percentages.
- Ask the question that can hurt: is the difficulty real, or manufactured by the choice of
  input? Then require what value remains once the input is clean.
- Market rules to state in the directive: every figure carries a link and a date · fact,
  estimate and opinion labelled · no invented market size ("no source found" is the answer) ·
  absent network access must be declared, never guessed around.
- Demand the economics of the alternative the buyer already has (the human hours it costs),
  not only a competitor's per-unit price.
- Require falsifiable assumptions each with its **cheapest experiment**, kill criteria written
  before the emotional moment, a self counter-test (strongest argument against its own verdict
  plus the single observation that would flip it), and an explicit statement of its own limits.
- Language rule: plain language for the non-specialist, each technical term glossed once in
  parentheses, and no table without a sentence saying what it means.

## Required deliverables (both lenses)

| Deliverable | Shape |
|---|---|
| Executive card | ~20 lines, written **first** and revised at the end; the owner reads only this |
| Register | Table: finding · evidence (file:line + command + output) · impact · priority · fix · alternatives with trade-offs · cost |
| Alternatives | Per component, ≥ 2, with a recommendation and an explicit "why not" for the others |
| Assumptions | What must be true · cheapest test · cost · what happens if it falls |
| Stop criteria | What evidence should make the owner abandon the route — written in advance |
| Self counter-test | Strongest argument against its own verdict + the flip condition |
| Limits | What it did not verify, and how someone else could |
| Owner decisions | Listed separately; never executed by the auditor |

## Verification battery for the returned report

1. Read it against the commit it claims to have judged (`git log -1 --format=%H` at that
   moment). An unpinned verdict on a moving tree is unactionable.
2. Reproduce the load-bearing claims only (usually 3–5), cheapest-first, then sample the rest.
   A report is never accepted or rejected as a block.
3. Go to PRIMARY sources for outside-world claims: the vendor's own capability page, the
   regulator's own text. The peer's summary is a claim, not a citation.
4. Recompute any arithmetic that carries a conclusion (a margin, a total, a ratio) — ratios with
   the wrong denominator are the recurring defect.
5. Grade each claim three ways: confirmed · confirmed and stronger than stated · confirmed but
   conditional (the condition is what makes it actionable). Publish the grade table and say
   where you disagree with the ranking instead of rubber-stamping it.

## Cost discipline

A well-scoped audit costs $0: re-derivation from artifacts already on disk plus free local
gates. State in the directive that any paid call requires its reason and price in the report,
and that re-measuring what already exists beats re-running it.

## After the audit lands: turn its conditions into repo containers

A strategy audit usually ends with conditions ("N conversations", "measure X", "stop if Y").
Conditions left in prose evaporate; each one needs a container created while the audit is fresh:

- **A conversation log** with one row per conversation (date · role — never the name · how you
  reached them · the exact questions · the number THEY said · the outcome), a **verdict counter**
  whose deciding row is money paid before delivery, and the **stop criteria copied into the same
  file**. The criteria must exist on paper before the emotional moment, not after it.
- **A plain-language one-pager for the prospective buyer**: what it is · who it is for and who it
  is NOT · exactly what the deliverable contains · the measured numbers with their source · and a
  **"what I do NOT promise"** section. Stated limits are the credibility asset here, not a
  weakness to hide — the buyer's first question is about the failure mode.
- **A dated correction instead of a rewrite** when an older document turns out to state something
  false (a comfortable privacy claim, a stale capability line). Keep the original sentence, put the
  dated correction under it, and say why: a session record that is silently edited stops being a
  record. Correct the live checklists outright — only the historical file is preserved.
- **Privacy rule for the containers themselves** — they get published. Codes instead of names, no
  employers, no contact details, no quoted real documents, no real account or serial numbers. The
  file that proves the market is also the easiest one to leak through.
- **The strategy verdict is ranked, not additive.** Expect it to re-rank the engineering register
  from the business side (deprioritise hardening for a product with zero users; lift a regulatory
  blocker above every code finding). When the two lists disagree, the business ranking decides what
  gets built next — state that rule instead of averaging the lists.
