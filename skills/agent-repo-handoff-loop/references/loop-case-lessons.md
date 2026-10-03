# Case lessons that produced durable rules

Split out of SKILL.md (2026-09-19). Each case below is a real incident; the RULE is the part to
carry forward, the narration is the evidence that the rule was earned.

## STOP-28: when the implementer keeps failing, the founder can assign the fix to the auditor (2026-08-11)


After five implementer attempts on one CI hang (BL-068/STOP-28 — a widget test that hung Linux CI for exactly 10 minutes), the founder assigned the fix to the AUDITOR (Claude) across the usual contract boundary. The auditor's commit said it plainly: "This crosses the auditor contract's 'do not write implementation code' boundary by explicit founder instruction; recorded rather than done quietly." The fix worked: the auditor removed Isar+runAsync from the test at the root, added a harness policy test that fails on any NEW nesting of the bad pattern, and **paid the debt file-by-file** (13 files → 8 → 0) with each file run and verified alone before moving on — a bulk sweep had dropped 6 tests, because "the waiting is not transferable: every screen waits for something different" (a filled field, a loading spinner vanishing, a delete button, a transient splash that any added delay corrupts). Then it wrote a full 9-section investigation (`docs/lessons/`) including its own three mistakes.

Lessons for the loop:
1. **The founder can temporarily reassign the implementer's STOP to the auditor** — but only by explicit founder instruction, and the commit must SAY the boundary was crossed on instruction (audit honesty beats quiet role-floating).
2. **Debt repayment is file-by-file, not a sweep** — the sweep that "should work" dropped 6 tests because the waiting condition differs per screen. Run each file alone after fixing it; the guard's allowlist only shrinks.
3. **The meta-failure: a wrong rule written as doctrine spreads perfectly.** The ambiguous skill wording ("runAsync plus pump()") was copied into 13 files (44 sites) and review approved it every time — review compares code against the rule, so a wrong rule is self-validating. **A scan catches what a review repeats** (it measures code, not belief). When a test passes on one machine and fails on another, stop fixing the symptom and find what DIFFERS between the machines (clock domain, speed, runner load) — five rounds were lost to not asking this.
4. **When the implementer is on hold, the AUDITOR can still legally own a fix** — the hold is on the implementer, not on the loop. The founder-side coordinator can wake the auditor path instead.


## Measuring suite nondeterminism: N consecutive reruns on ONE unchanged commit (AUDIT-01, 2026-08-14)


When the suite fails a DIFFERENT test each run (same commit, 4 attempts → failure sets `{add_refresh, invoice_photo}` · `{}` · `{locale_switch ×2}` · `{}`), the cause is suite nondeterminism under load — and the ONLY evidence that names it is a measurement, not an explanation. The AUDIT-01 recipe (validated on CarSah — 11 consecutive runs on the unchanged commit `77fc07d`, 11/11 green, closed the audit):

1. **Pin one commit and do NOT change it.** The measurement is about the suite, so the code must be frozen.
2. **`gh run rerun <run-id>` is the mechanism — NOT `workflow_dispatch`.** Verify the workflow's `on:` block first: `Build & Release` declares `push` only (no `workflow_dispatch`), so `workflow_dispatch` fails. A rerun needs no commit and no workflow change.
3. **Record the failure set EVERY run** — N runs, N rows in the delivery letter: what passed, what failed, what was infra-only (quota, upload). Consecutive green runs close the nondeterminism audit together with the flake question.
4. **Interpretation discipline:** «deterministic» means «no flake in N runs», not «the flake is impossible» — historically-flaky waits still in the tree stay a latent risk; say so in the letter.
5. **The measurement pays for itself immediately:** when a round DOES turn red during the measurement window, check whether the red is a real signal (e.g. a linter suggestion that broke the OTHER analyzer — Pattern 54) before calling it flake. Naming each red as either signal or noise is the whole point.


## A founder walk is a first-class test — walk the primary forms empty


Founder-urgent fix DEC-069 (2026-08-14): by USING the app, the founder found two "fatal" defects that 437 tests, mutation-suite discipline and auditor reviews had all missed — a service record could be saved with ZERO performed services selected (fresh add), and editing allowed unchecking every service then saving. The UI disabled Save for missing odometer/cost but never for an empty task selection; the use case's `required List<ServiceTask>` accepted an empty list. Operational rules for the loop:

1. **Any delivery touching a form with a mutable selection must include the empty-selection attempt in its device walk** — attempt to save with nothing selected; prove the primary action is disabled AND a direct use-case call is rejected (two-layer guard: UI disable + business-layer `ValidationFailure`, distinguishing `null`=keep from `[]`=reject in edit paths).
2. **When a rewrite makes an old test's assertion impossible, the coverage must be re-expressed** (CARRY-106): "editing to remove the last task reverts the anchor" became "empty list is rejected" — the rewrite was correct, but nothing replaced the original guarantee until the auditor's mutation proved the guard was gone. Rewriting a test without replacing its coverage is silently losing a guard.
3. **The auditor's mutation is the acceptance** — restore the deleted behavior check, expect the guard test to go red, restore, green. A guard that cannot be turned red by a planted violation is not a guard.


## CARRY HOLD — a review that defers to the founder is a STOP-light (2026-08-10)


When a review says a decision is deferred to the founder — "design gate stays
the founder's", "founder-owned", AWAITING_FOUNDER — the implementer must NOT
execute the related CARRY. Hold it: stay in AWAITING_FOUNDER and wait for the
founder's ruling, because the founder may REDEFINE the CARRY (observed
2026-08-10: the implementer executed CARRY-57 as "name the deviations with
owners" per the auditor's wording, then the founder's relay landed 6 minutes
later redefining it as "adopt the prototype (button, sub-line, form)" — a
wasted round, then a redo). Race shape: the founder's relay arrives AFTER the
implementer's submission because both travel through the mailbox. The
implementer cannot see the relay coming, but it CAN see the deferral signal in
the review — that signal is the instruction to hold. Add to the directive:
"if the review defers a decision to the founder, do NOT execute the related
CARRY — remain AWAITING_FOUNDER until the founder rules."

