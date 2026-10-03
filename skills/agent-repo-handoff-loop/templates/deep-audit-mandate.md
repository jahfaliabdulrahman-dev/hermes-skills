# تكليف الفحص الشامل (Deep Audit) — <PROJECT> · المدقّق الخارجي: <AUDITOR>

> Copy-and-adapt skeleton. The rules behind each section (why it exists, what
> failure it prevents) live in `agent-repo-handoff-loop` SKILL.md under
> «Two directives, never one» — read that first.
>
> **Language:** write the mandate in the owner's language (Arabic by default),
> keeping commands, paths, identifiers and code in English. The auditor reads
> the repo file; the owner reads the summary.
>
> **Usage note to keep at the top of the file:** this is NOT the per-delivery
> loop directive (that one is `docs/<auditor>-directive.md`) — the loop judges
> one submission, this mandate judges the system. Paste line:
> `Read docs/<auditor>-deep-audit-directive.md and execute it literally — full audit, no code.`

---

## 0) Ordered read list (do not judge a file you have not opened)

1. Framework: <README> · <PLAN> · <contract/protocol> · <STATE>
2. Contracts & operations: <operations doc> · <checklist> · <suspects/gap log> · <resume doc>
3. Methodology: <what-if guide + last workshop, if the project keeps one>
4. Context + open items: <onboarding doc> · <the newest handoff message listing what the owner wants attacked>
5. Code: <modules> · <entry point / UI> · <tools> · <tests> · <CI + hooks>

## 1) What the project is — and why it exists

- What it does, for whom, on what input.
- **The central claim** — the one assertion the whole system exists to uphold.
  Name it as the thing the auditor is expected to attack.
- The core mechanism(s) that make the claim hold, and the independent referee
  that catches the failure mode the core mechanism CANNOT see.
- The end goal: what "finished" means, and what is explicitly out of scope.

## 2) How it evolved (honest, no marketing)

| Phase | What happened | Lesson extracted |
|---|---|---|

One row per phase, lesson per row — this is what stops the auditor proposing an
already-rejected approach.

## 3) Stack and architecture

| Layer | Tech | File | Hostile note aimed at the auditor |
|---|---|---|---|

Every row carries a pointed question or a known weakness — a descriptive table
produces a descriptive audit.

## 4) Measured baseline — CLAIMS, and the auditor's job is to falsify them

> Standing law: no number in this mandate is sacred. Every number is a claim.

| Claim | Where its evidence lives | How to falsify it |
|---|---|---|

**Seeds — 2 contradictions you verified yourself** (a doc figure that
disagrees with the run report; a documented count lagging the measured one):
1. <seed 1: both sides quoted + the command you ran>
2. <seed 2>
Then the mandatory task: sweep every number in every public doc against its
measured source.

## 5) Hard rules

1. **Privacy** — the report is a public surface: no real data, account numbers,
   names, absolute home paths, real-file names or screenshots in anything that
   gets committed. Local evidence dirs are READ-ONLY, never copied, never
   committed. Repo guard runs green before any push.
2. **Scope** — the repo is everything the auditor sees; no external skill
   library, nothing outside the project directory.
3. **No code** — proposals arrive as description + pseudo-code / unapplied
   diff. Only an explicit owner instruction crosses that line, and then the
   message must say so.
4. **Cost** — local checks are free, use them hard; paid calls only when a
   finding depends on it, with the reason and the price stated in the report.
5. **Known evidence trap** — <the field missing from the cache / the helper
   that returns zeros / whatever would manufacture a false finding>.
6. **Evidence discipline** — every finding carries the command that produced
   it; anything unchecked is written as «not verified» plus how to check it.
7. **Adversarial to ideas, not to people** — the system is the defendant.

## 6) Audit axes — each with pre-written hostile questions

For each axis: read the code → read the existing evidence → answer the
questions → record the result.

- **M1 Validity / core math** — can a "clean" verdict be produced on shifted
  data? do the safety states get treated as OK anywhere downstream? exact
  arithmetic or floats?
- **M2 Data provenance** — is every displayed value traceable to a reader or a
  derivation, or are there silent defaults rendered as data?
- **M3 Privacy / leak** — attack the guard itself: what does it not scan (text
  inside binaries, commit messages, history, escaped or non-Latin digits,
  service identifiers in the allowlist)? is the public fixture genuinely
  synthetic? what does the allowlist's growth pattern tell you?
- **M4 Resilience** — provider outage paths, retry/budget barriers, lock races
  (stale lock after a crash, two checkouts), atomicity of each per-item write.
- **M5 Answers / retrieval** — can an answer cite evidence it does not have, or
  show the wrong rows? where is the model allowed to compute? does the refusal
  set cover confident out-of-scope questions?
- **M6 Security / supply chain** — unpinned dependency ranges (unreproducible
  builds), keys in logs/exceptions, model download path, CI token permissions.
- **M7 Operations / continuity** — does the alarm actually reach a human? read
  the resume doc as a newcomer and TRY TO FAIL at resuming. what is lost if the
  local evidence directory disappears?
- **M8 Claim honesty** — every public doc number vs its source (mandatory),
  scope language for a provisional release, first-30-seconds impression of the
  repo for a stranger.
- **M9 Performance / cost / scale** — the measured per-unit cost and time,
  ranked options to reduce them without losing accuracy, parallelism limits,
  what breaks first on the second file / the second bank, retention policy.

## 7) Deliverables — one report, four parts

A. **Executive summary, ~20 lines, written first** (the owner reads this and
   decides).
B. **Weakness register** — one table:

| # | Weakness | Axis | Evidence (file:line + command + output) | Impact on which decision/value | Priority | Fix | Alternative A / B (trade-off) | Cost |
|---|---|---|---|---|---|---|---|---|

Priority: STOP (touches a real value) / P1 / P2 / P3. No item without
reproducible evidence; no item without concrete impact — the smallest impact is
dropped, not downgraded.

C. **Architecture alternatives** — ≥2 per major component with explicit
   trade-offs and a NAMED recommendation + why the other was rejected; plus the
   cheapest change that fixes 80% of the pain per component.
D. **What-if / premortem report** — by protocol (`what-if-analysis`), beginning
   with a verdict on the previous workshop's items (closed in substance /
   closed formally / open), then a fresh premortem, focused what-ifs on the
   current critical assumptions, the guide-word sweep, the positive face, and
   the ranked output table with indicator + owner per row.

## 8) What I do NOT want

<the anti-patterns list from the SKILL — a verdict without its command, generic
praise, doc restatement, uncosted rewrites, priority inflation, "not found =
not existing", ranking by wording.>

## 9) Delivery path

- Long form: `handoff/<auditor>/audit/<YYYYMMDD>-deep-audit.md` (+ per-section
  files if it grows; one index file).
- One mailbox message in `handoff/<auditor>/` with the standard header, pointing
  at the report and listing only the top 5 items.
- Do not touch the other side's mailbox files, the loop marker, or STATE's
  status/step fields (a notes line is enough — this is an audit, not a delivery
  review).
- `git pull --rebase` before push; the repo guard must be green.
- **Session budget:** if the axes do not all fit, deliver what is done plus an
  explicit list of what was NOT audited and why. A declared partial report
  beats an invented complete one.

## 10) Owner decisions

Anything needing an owner ruling goes into an «awaiting owner» list — no
execution on it.
