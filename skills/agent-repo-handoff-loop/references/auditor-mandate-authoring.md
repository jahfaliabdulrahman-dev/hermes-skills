# Authoring third-party auditor mandates

A mandate is the DOCUMENT you hand an outside agent (a different program, with no
access to your skills or memory) so it can judge your work. The repo is the only
shared language: anything the auditor must verify has to exist in the repo — and the
mandate itself is a repo artifact, which makes it a public surface too.

## The three shapes (do not merge them into one prompt)

| Shape | Who the auditor is in it | What it judges | When it runs | Its output |
|---|---|---|---|---|
| **Per-delivery review** | an independent reviewer | one submission: its claims vs reproduced evidence | every delivery, on a loop | verdict (approve / request-changes / stop) + numbered findings |
| **Deep technical audit** | a hostile engineer | the SYSTEM: correctness, provenance, resilience, guards, ops | at a big gate (before publishing, before generalizing) | weakness register + architectural alternatives + what-if |
| **Strategy / market review** | a CEO + investor + engineer | the IDEA: purpose, roadmap, viability, market, moat | before a strategic decision (publish, price, scale) | verdict card + alternatives scorecard + market evidence + kill criteria |

Merging shapes produces a mandate that judges nothing well: a delivery reviewer
cannot see the system, a system auditor does not know the market, and both drown if
asked to do everything in one session. One shape per session, one paste per shape.

## Anatomy of a deep/strategy mandate

Each section exists for a named failure. Ship all of them.

1. **Role** — name the judgment positions explicitly ("a third party who is at once a
   CEO who shipped products, an investor, and an engineer"), and forbid flattery in the
   first paragraph. Distance is the product; politeness destroys it.
2. **Mandatory reading, in order** — repo docs, then the protocol, then the code, then
   `git log`. Add "do not judge a file you have not opened".
3. **What the thing IS and WHY it exists** — including the central claim the auditor
   should attack. State the claim as a target, not a slogan.
4. **How it evolved** — a short stage table with the lesson per stage, so the auditor
   does not propose what was already tried and dropped.
5. **Tech and architecture** — a table where every row carries a "hostile note" pointing
   the auditor at that component's weak seam. A plain inventory gets skimmed.
6. **The measured baseline, labelled as CLAIMS** — plus the standing law: *every number
   here is a claim; your job is to find the number nothing supports*. This is the single
   most valuable instruction in the whole document.
7. **Hard rules** — privacy of the report itself, repo-is-all-you-see, no code unless
   commissioned, cost accounting, "a verdict without a command is not a verdict", and
   "write 'not verified' when you did not verify it".
8. **Scope as axes with ready attack questions** — 6-9 axes, each naming the components,
   the questions, and which evidence artifact to consult. Ready questions beat
   "find weaknesses".
9. **Deliverable shape** — a verdict card of <=20 lines FIRST (the owner reads only that
   on the first pass), then registers/tables, then the counter-test.
10. **The what-if report** — by protocol, not mood: assume the failure already happened,
    explain how, then require an early-warning indicator and an owner per item.
    *No indicator = anxiety; no owner = a floating promise.* An item with neither is
    deleted from the table, not softened.
11. **What I do NOT want** — the anti-patterns that make a report worthless: verdicts
    without commands, general praise, re-summarizing the docs, "rewrite it all" with no
    cost, inflating cosmetics to P1 or deflating a safety item to P3.
12. **Delivery + session budget** — where to write it (the auditor's own mailbox dir),
    the standard message header, the guard to run before pushing, and the closing rule:
    *an incomplete declared report beats a complete guessed one*.
13. **Start now** — no asking permission, no commenting on the instructions.

## Always-on rules, whatever the shape

- **The mandate is a public surface.** It gets committed to a repo others can read: no
  account numbers, names, absolute paths, document titles, or case details. The
  auditor's own report is the same surface — say so in the mandate and require the
  publish/leak guard before the report is pushed. Sensitive context stays in the owner's
  session, not in the artifact.
- **Numbers are snapshots, not facts.** Any figure baked into a directive (commit count,
  test count, ratio) is stale the moment the repo moves — and a live repo moves while you
  are still writing. Mark every number "measured when written" and ship the command that
  re-measures it (`git rev-list --count HEAD`, the test command, the report path).
- **Seeds are perishable.** A seeded defect ("README says X while the log says Y — start
  here") is what proves the auditor's method bites. Re-check it is STILL open immediately
  before publishing; when it has already been fixed, say inside the mandate that it was
  consumed and swap in a fresh one. An auditor that "discovers" a closed item loses
  authority it never gets back.
- **Point it at prior third-party output, and license contradiction.** When another
  auditor already produced a report, order the new one to read it, to say what it took
  from it, and explicitly authorize it to disagree — otherwise you pay twice for the
  same finding list.
- **Pin the moment** in a live repo: order the auditor to record the commit hash it
  judged (`git log -1 --format=%H`) and to say when it is judging a moving target.
- **Split the questions so a technical win cannot hide a business loss.** Ask separately:
  is it correct? is it wanted? is it defensible? One "what do you think" collapses three
  verdicts into one, and the strongest answer drowns the others.
- **Force a counter-test on the auditor's own verdict** — the strongest argument against
  itself, the one piece of evidence that would flip it, the cheapest experiment per
  critical assumption, and explicit **kill criteria** (what evidence would make stopping
  the rational call). Without this, a report is an opinion with tables.
- **Cost is part of the evidence.** Separate what is local and free (tests, guards,
  re-deriving from cached artifacts) from what is paid (live model calls, full runs):
  free evidence is to be used hard; paid evidence only to settle something that decides a
  finding, with the reason and the price stated in the report.
- **Market claims need sources or they are deleted.** Any figure with no link and date is
  removed, and (fact) / (estimate) / (my opinion) are never mixed. Forbid inventing a
  market size outright, and require the auditor to say "no network access" rather than
  dress a guess as research.
- **Prescribe language and shape.** The owner's language first, plain sentences, a
  foreign term once in parentheses at first use, and no table without a plain sentence
  under it saying what it means. Jargon density reads as hedging.

## Pre-flight checklist before pasting a mandate

- [ ] one shape only (review / audit / strategy), and it says what it is NOT
- [ ] mandatory reading list, with an order
- [ ] the central claim stated as a target
- [ ] every number marked as a snapshot with its measuring command
- [ ] each seeded defect re-verified as still open (or replaced)
- [ ] prior third-party output named, with permission to contradict it
- [ ] privacy rules: no identifiers in the mandate or the report; guard before push
- [ ] deliverable path + message header + verdict-card-first shape
- [ ] counter-test and kill criteria demanded explicitly
- [ ] session budget + "incomplete declared beats complete guessed"

---

## Two directives, never one: the per-delivery loop and the one-shot DEEP AUDIT


The mailbox needs TWO separate directive artifacts, and a healthy project has
both. Conflating them wastes the auditor: one either re-reviews a delivery
forever or audits a system when a step was asked for.

| Artifact | Fires | Judges | Output |
|---|---|---|---|
| loop directive (`docs/<auditor>-directive.md`) | every delivery, on the auditor's own `/loop` | ONE submission against the gates | APPROVE / REQUEST_CHANGES / STOP |
| deep-audit mandate (`docs/<auditor>-deep-audit-directive.md`) | once per big gate (public release, second file/bank, commercial offer) | the SYSTEM | weakness register + alternatives + what-if |

Cross-reference the two files in one line each, from inside the repo (the
auditor sees nothing else), and say explicitly which is which — an auditor
holding both will otherwise apply the wrong one.

### Shape of the deep-audit mandate (every part earns its place)

1. **Ordered read list first** — framework docs, contracts, methodology notes,
   the open-items message, then code. State the law: do not judge a file you
   have not opened.
2. **What the project is / why it exists / how it evolved / the stack / the end
   goal.** Write evolution as a table with one row per phase carrying the LESSON
   extracted — otherwise the auditor re-proposes what was already tried and
   rejected.
3. **The measured baseline as FALSIFIABLE CLAIMS**: a claim / where-its-evidence-
   lives / how-to-falsify table, plus the standing law «no number in this
   mandate is sacred — every number is a claim». Asserting the numbers as fact
   hands the auditor a script to parrot back.
4. **Seed the mandate with 2 contradictions YOU verified yourself** (a doc
   figure that disagrees with the run report, a documented count that lags the
   measured one). Two purposes: it proves the auditor's method actually bites,
   and the owner gets a checkerboard to validate the report against. Label them
   seeds, never the audit's findings — the point is the check, not the answer.
5. **Hard rules block** — scope (the repo is everything it can see), no
   implementation code, cost, privacy (below).
6. **N audit axes, each with pre-written hostile questions** (math/validity,
   provenance, PII, resilience, retrieval/answers, supply chain, continuity,
   claim honesty, cost/scale). The questions are what make an axis produce
   findings; «review the security» produces prose.
7. **Deliverable shape** — an executive summary of ~20 lines FIRST (the owner
   reads only that before deciding), then a weakness register table, then
   architecture alternatives with a named recommendation and a why-not per
   rejected option, then a per-component «cheapest change that fixes 80%».
8. **A what-if / premortem section that runs by protocol** (load
   `what-if-analysis`), including a verdict on the PREVIOUS workshop.
9. **An explicit anti-patterns list for auditors** (below).
10. **Delivery path + session budget** — a declared partial report beats an
    invented complete one.

### Anti-patterns list to embed in the mandate (auditors repeat these)

- A verdict without the command that produced it; a figure copied out of a doc
  as if verified.
- Generic praise («the code is well written») with no item, no evidence, no cost.
- Restating the docs — the value lives in the CONTRADICTION between doc, code
  and reality.
- A rewrite or technology swap proposed with no measured cost/effort/risk.
- Inflating a cosmetic note to P1, or demoting a safety item to P3.
- «If I did not find it, it does not exist» — unverified must be written as
  «not verified» PLUS how it could be verified.
- Ranking by severity of wording instead of (impact × likelihood).

### Auditing a PUBLIC repo: the report itself is a publication surface

- The mandate file gets committed, so it carries NO personal case specifics, no
  names, no real data — keep the sensitive context in the owner's session, not
  in the artifact the auditor reads from `origin/main`.
- Say it in the mandate: the auditor's REPORT is pushed too. Ban real rows,
  account numbers, absolute home paths and screenshots inside it, and require
  the repo's own publish guard as the pre-push gate.
- Real-corpus artifacts (caches, run reports) are usually gitignored, but the
  auditor runs in the SAME checkout and can read them. Authorize read-only
  access, forbid modification and commit — the raw evidence is what makes its
  findings checkable.
- Give the cheap path explicitly: audit the EXISTING evidence (cache + run
  reports + code) instead of re-running a paid pipeline; a paid call is allowed
  only when a finding depends on it, with the cost declared in the report.
- **Warn about the cache-versus-report mismatch before it manufactures a false
  finding.** A cached per-item record can lack a field the run report derives
  (cached rows missing a side/direction column make a totals helper return
  zeros) — every manual comparison built on the raw cache is then void. Name
  the trap and the safe path (re-derive through the same function the run
  used), or the auditor's first «finding» is its own artifact error.

### A gate the reviewer cannot re-derive is theatre — and human arbitration needs provenance

The deepest finding a deep audit can produce is not about the code: it is that one of your OWN
declared gates is unverifiable by the other agent. Real case: a headline verdict («621 pages
verified, 0 off») was a formal review gate, yet re-deriving it from the repo gave a DIFFERENT
number (615 verified / 6 off), because three values had been corrected by hand in a data file under
a field name that exists in no tracked line of code — the original wrong read was still sitting
next to it. The reviewer's only options were to approve a number it could not check (theatre) or to
refuse the delivery on structural grounds (the loop stops).

Rules:

- **A gate sentence must be reproducible by ONE command the reviewer can run**, from the pushed
  tree alone, with no local state and no Hermes-side file. When writing a protocol's gate list, run
  each command from a fresh clone before promising it.
- **Human arbitration is legitimate — invisible arbitration is not.** When the owner's eye is the
  authority (the machine's re-read was rejected but the printed value was readable), the corrected
  value must carry provenance: page · field · old · new · who · why · the visual evidence, with the
  ORIGINAL kept beside it. Then the headline number stays re-derivable and the gate keeps its meaning.
  The alternative — hand-editing the data — silently converts a verified claim into an assertion.
- **A reviewer that must choose between approving blind and stopping the loop is a design defect,
  not a reviewer problem.** Fix the gate, not the reviewer.
- **Verify the auditor's figures before acting on them, and say so when yours was the wrong one.**
  In one audit a figure was overstated ~10× while another was exactly right and the implementer's own
  count was wrong. Re-measure each claim; correct your own number in the next message.

### Validate the mandate with the repo's own guard before handing it over

Run the repository's guard engine over the mandate file itself (import the
module and call its text/path scanners, or dry-run the pre-push path) — do not
eyeball it. Two facts that bite:

- A new UNTRACKED file shows CLEAN under a `--tree` scan, because tree mode
  lists the committed tree (`git ls-tree -r HEAD`) and an untracked file is
  simply not in it. The pre-push hook scans the refs being pushed, so the file
  IS caught at push time. Read the guard's modes before trusting a clean run.
- When the guard flags a token that is legitimately present (the owner's own
  name inside a service identifier), REWORD the file — do not add an allowlist
  exception for a new document. The allowlist is the one place a real leak can
  hide behind a written reason; keep it from growing.

