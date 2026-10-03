# Founder-facing views (live state, one glance)

Split out of SKILL.md (2026-09-19). The founder-facing display of build state: what it must be
derived from, and the traps that made earlier versions lie.

## Founder one-glance progress map (live swimlane — validated 2026-08-10)


The founder does not want to re-read the backlog to know where the build is.
Their breakthrough reaction ("هذي المرة الوحيدة اللي أحس إني فيها فاهم — هذا ما
كنت أحتاجه لأعرف ماهي الخطوة التالية") came from a LIVE VISUAL build-state map:
rows = work-type/EPIC lanes, columns = sequence steps, each cell a build item,
colored by **done ✅ / in-progress 🔄 / next ⏭ / future (faded)**, plus a
one-line "Next step: BL-XXX" header. Rules that keep it honest:

- **Derive, never commit.** The view is generated ON DEMAND by a script that
  reads the locked table (for step→BL and EPIC mapping) AND the auditor's
  letters (for done/next — see the SOURCE rule below). A committed derived
  document drifts and becomes a second, lying source of truth; a script holds
  no data and cannot lie.
- STATE.md parsing is the FALLBACK ONLY (a fresh repo with no auditor letters
  yet). When it is used, parse its locked-sequence/step: lines robustly: the
  listing WRAPS across multiple lines (join following lines until a blank
  line), done steps appear as numbers/ranges (`12–27a ✅`), the next step is
  marked with ⏭ (or `next: \`34\` BL-052 …` in the newer format). Expand
  ranges → map step→BL through the parsed table. The STATE format is NOT
  frozen — the implementer changed it at BL-050 (2026-08-10) from a single
  'Locked sequence' line to separate `step:` / `next:` lines — parse BOTH.
  Parsing traps: (1) founder-added sub-step rows in the locked table are
  bolded (`| 15a | **BL-009 …` — the `**` breaks a bare `BL-` regex; allow
  `\*{0,2}`), so BL-009/064/065/031a/042a silently vanish from the step→BL
  map; (2) slash-list expansion `re.sub(r"/0*(\d+)", …)` eats leading zeros
  (`BL-060/061` → `BL-61`); use `/(\d+)` without the `0*`.
- Render: HTML grid (diffable, opens anywhere) → optionally Chrome headless
  `--screenshot` for a PNG — remember Chrome does NOT expand `~`, pass `$HOME`.
- The implementer's dirty tree marks the next step as 🔄 in-progress.
- Re-run the one command after every DEC/delivery — the founder gets "where we
  are + what's next" in one glance, every time, with zero maintenance.
- **SOURCE = THE AUDITOR'S LETTERS, never the implementer's STATE (founder
  rule 2026-08-10).** The implementer's STATE.md is a SELF-REPORT — it can
  mark steps ✅ that are only "SUBMITTED — awaiting review" or even
  "pending", and the map misrenders (observed: BL-052 written "pending" was
  shown ✅ done, so the next jumped to BL-066). The swimlane's done set comes
  from parsing `handoff/claude/*.md`: a step is done iff its letter's
  `verdict:` contains APPROVE; the primary BL comes from the letter's
  `step:` line plus riding steps (`BL-XXX (…)` with any parenthesized
  content). Three GENERAL rules replace any hardcoded override map: (1)
  step-line primary + riding; (2) body acceptance — in APPROVE letters, a BL
  within ~60 chars of `accepted|completed|marked ✅` is done (covers early
  fix rounds whose step line omits the BL — verified with zero leakage into
  future steps); (3) absorption — `BL-XXX … absorbed` in ANY letter (the
  absorption is auditor-recorded even in DECIDED relays). STATE.md is NOT
  consulted (it is a self-reported, format-drifting document — the wrong
  shape for a tracking source; the swimlane must run with zero surgical
  intervention). next = the first locked-sequence step not in the approved
  set.

