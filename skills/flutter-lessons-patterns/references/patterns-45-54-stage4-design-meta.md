# Patterns 45-54 — Flutter Cross-Project Lessons

> Extracted from flutter-lessons-patterns SKILL.md (v2.24) — split for size. Read the index in SKILL.md for the classification map.

## Pattern 45 — Bundled-Task Pattern for Shared-File Conflicts (LL-051)
**Level:** 📏 RULE · SHOULD — File-affinity analysis — helper script exists but decision stays with planner


**Source:** hermex_android (2026-07-16) — RC6 Coordination

**Rule:** During EPIC decomposition, run a file-affinity analysis: for each target file, count how many planned tasks would modify it. Files with ≥3 modifying tasks should either: (a) be bundled into a single assignee task, or (b) have tasks sequenced (not parallel) with explicit merge checkpoints.

```bash
# File-affinity analysis (run during EPIC decomposition):
# For each file in the planned changeset, count task assignments:
for file in $(git diff --name-only main...HEAD); do
  count=$(grep -l "$file" <task-specs> | wc -l)
  if [ $count -ge 3 ]; then
    echo "⚠️  $file — $count tasks → BUNDLE or SEQUENCE"
  fi
done
```

**Why:** `chat_provider.dart` was the nexus for 5+ RC6 defects (error handling, profile switching, model selection, message rendering, stream handling). Multiple specialist agents working on parallel tasks all modified the same file, creating a merge-conflict storm. Bundling all `chat_provider.dart`-touching work into a single Phase 2 task with a single assignee eliminated the conflicts. Parallel task decomposition had assumed file-level isolation that didn't hold.

**Prevention:** Add file-affinity analysis to the Lead Architect's EPIC decomposition checklist. When a file has ≥3 modifying tasks, prefer bundling over sequencing — merge conflicts are harder to resolve than a single large PR.

---

<details>
<summary>📋 Full Original: LL-051</summary>

**LL-051: Bundled-Task Pattern for Shared-File Conflicts (chat_provider.dart nexus)
- **Date:** 2026-07-16
- **Stage:** RC6 Coordination
- **Files Affected:** lib/features/chat/providers/chat_provider.dart
- **Lesson:** chat_provider.dart was the nexus for 5+ RC6 defects. Multiple parallel tasks all modified the same file creating a merge-conflict storm. Bundling into a single task eliminated conflicts.
- **Root Cause:** Parallel task decomposition assumed file-level isolation. No "shared file conflict" detection in Kanban pipeline.
- **Prevention Rule:** During EPIC decomposition, run file-affinity analysis. Files with ≥3 modifying tasks should be bundled or sequenced.
- **Linked Decision ID:** N/A (process pattern)

</details>

---

- **Last Updated:** 2026-07-18 — v2.15.0 — New Patterns 46–48 (cross-project Stage 4): Never-Say-No-Data (cold-start UX), Live-Device Verification Supremacy (tests pass ≠ works), Regex-Gate Fallback + Disabled-Button Colors (LL-010, LL-011). Patterns count: 48.

---

## Pattern 46 — Never Say "No Data": Cold Start Intelligence (LL-009)
**Level:** 📏 RULE · SHOULD — Cold-start UX — design decision


**Source:** Azdal (2026-05-16) → `~/Projects/Azdal/app-spec/00_lessons_learned.md`

**Rule:** Apps that say "add more transactions to see insights" lose users. The first experience MUST deliver value using whatever context is available — income brackets, general estimates, confidence levels. Give value first, then ask minimal questions (3 max).

```dart
// ❌ BROKEN — user sees "no data" on first open
if (transactions.isEmpty) {
  return Text("Add transactions to see your financial health");
}

// ✅ CORRECT — use estimates with confidence levels
final estimate = IncomeBracketEstimate.forRegion('SA');
return FinancialHealthCard(
  score: estimate.medianScore,
  confidence: ConfidenceLevel.low, // honest about uncertainty
  prompt: "Connect your bank for a personalized score →",
);
```

**Why:** Onboarding delivers insight before asking for input. 77% of finance app users quit in 3 days due to empty-state friction. Every additional tap required before the user sees value reduces retention.

---

<details>
<summary>📋 Full Original: LL-009</summary>

**LL-009: Never Say "No Data"**
- **Date:** 2026-05-16
- **Stage:** Triple-agent brainstorming
- **Lesson:** Apps that say "add more transactions to see insights" lose users. The first experience must deliver value.
- **Impact:** Designed Cold Start Intelligence: use income brackets, general estimates, confidence levels. Give value first, then ask minimal questions (3 max).
- **Rule:** Onboarding delivers insight before asking for input.
- **Source:** Azdal `01_prd.md`

</details>

---

## Pattern 47 — Live-Device Verification Supremacy (LL-010)
**Level:** 📏 RULE · SHOULD — Live-device supremacy — requires physical device, can't automate (founder standard)


**Source:** Azdal (2026-07-14) → `~/Projects/Azdal/app-spec/00_lessons_learned.md`

**Rule:** "Tests pass" and "agent/auditor approved it" are necessary but NEVER sufficient. Before accepting any "done" report, reproduce the flow on a real device and query the live database directly — do NOT trust the app's own "success" message.

```bash
# ✅ Verification pipeline for any database-write feature:
# 1. Reproduce the exact user flow on a real device
# 2. Query the live database independently (do NOT trust app's success message)
# 3. Confirm: row exists + right values + right timestamp
PGPASSWORD='<pwd>' psql "postgresql://postgres:***@db.<ref>.supabase.co:5432/postgres" \
  -c "SELECT * FROM purchases WHERE user_id = '<uuid>' ORDER BY created_at DESC LIMIT 5;"
```

**Why (from one project's Stage 4):** 5 critical bugs found AFTER `flutter analyze` clean, `flutter test` 34/34 passing, Zero-Trust Auditor APPROVE with 0 CRITICAL, and SCSI Guardian ALL CLEAR:
1. Purchase-confirmation insert against columns that don't exist on live table (100% failure rate)
2. Submit button never disabled (unlimited duplicate writes)
3. Success messages showing same sentence twice
4. Arabic-Indic numerals silently failing every form-field parse
5. A regression introduced BY the fix for #2 — key rename (`_form_kind` → `form_kind`) silently dropped

None were reachable by static analysis or unit tests. Every one found by: real device + direct database query.

---

<details>
<summary>📋 Full Original: LL-010</summary>

**LL-010: Passing Tests and Agent Self-Approval Are Not Verification**
- **Date:** 2026-07-14
- **Stage:** Stage 4 (BUY+INTG) live device testing
- **Lesson:** 5 critical bugs found on live device AFTER all gates passed. Unit tests re-derived target formulas as local constants instead of instantiating the actual service — they would pass unchanged against a broken implementation.
- **Rule:** Reproduce the flow live and check the live data source directly. Route B's own audit/guardian layer missed all 5 bugs.
- **Source:** Azdal `12_decision_log.md` DEC-036

</details>

---

## Pattern 48 — Regex Pre-Filter Gates + Disabled Button Colors (LL-011)
**Level:** 📏 RULE · SHOULD — Regex fallback + disabled colors — behavioral, review catches


**Source:** Azdal (2026-07-15) → `~/Projects/Azdal/app-spec/00_lessons_learned.md`

**Rule A — Regex pre-filter fallback:** Any local keyword/regex gate standing in front of an LLM classifier for a correctness-critical feature MUST have a fallback path. A miss degrades to confidently-wrong-and-silent, not "slower but correct."

```dart
// ❌ regex-only gate — miss = silently falls through to generic chat
if (_looksLikeBuyIntent(message)) {
  return await purchaseService.evaluate(message);
}
// Falls through — user gets generic coach reply, purchase is silently ignored

// ✅ regex gate with safety-net classifier fallback
if (_looksLikeBuyIntent(message)) {
  return await purchaseService.evaluate(message);
}
// Fallback: if message is substantial (>20 chars, contains Arabic), 
// call classifier anyway as safety net
if (message.length > 20 && containsArabic(message)) {
  final intent = await classifier.classify(message);
  if (intent == Intent.buy) {
    return await purchaseService.evaluate(message);
  }
}
```

**Rule B — Disabled button colors:** `ElevatedButton.styleFrom(backgroundColor:, foregroundColor:)` only styles the ENABLED state. Once `onPressed: null`, Material silently substitutes its default disabled palette. Always set `disabledBackgroundColor`/`disabledForegroundColor` explicitly.

```dart
// ❌ custom colors silently lost when button is disabled
ElevatedButton(
  style: ElevatedButton.styleFrom(
    backgroundColor: Color(0xFF001F5E),
    foregroundColor: Colors.white,
  ),
  onPressed: isAnswered ? null : () => submit(),  // ← colors LOST when null
  child: Text("Submit"),
)

// ✅ explicit disabled colors
ElevatedButton(
  style: ElevatedButton.styleFrom(
    backgroundColor: Color(0xFF001F5E),
    foregroundColor: Colors.white,
    disabledBackgroundColor: Color(0xFF001F5E).withOpacity(0.5),
    disabledForegroundColor: Colors.white70,
  ),
  onPressed: isAnswered ? null : () => submit(),
  child: Text("Submit"),
)
```

**Verification:** When debugging button colors, measure actual RGB pixel values from a live screenshot — opacity-wrapper fixes treat the wrong layer and look plausible without fixing anything.

---

<details>
<summary>📋 Full Original: LL-011</summary>

**LL-011: A Local Regex Gate May Decide Cost, Never Correctness — And a "Disabled" Style Isn't Automatically Your Style**
- **Date:** 2026-07-15
- **Stage:** Second live-device retest of Stage 4, escalated to Opus 4.8
- **Lesson:** Two traps: (1) Regex pre-filters required exact hamza spelling, dropping common dialect typing silently. (2) ElevatedButton colors silently lost when disabled — only pixel-sampling a live screenshot revealed the real mechanism.
- **Rule:** Regex gates need fallback paths. Disabled button styles must be explicit.
- **Source:** Azdal DEC-037, DEC-037-B

</details>

## Pattern 49 — Design System Architecture: Tokens Gate, Sub-Themes Rule, Components Judgment (LL-052)

**Source:** CarSah (2026-08-11) — founder/Claude design discussion → `fluttergems.dev` evaluation; verified against `lib/shared/design_system/app_theme.dart` + 28 consuming files.

**The lesson is THREE layers, not one.** "Theme swapping" means different costs depending on which layer you touch. Decide per layer, and give each a different enforcement level:

### Layer 1 — Design tokens (GATE: mandatory + contract test)

A single Dart file builds `ColorScheme`/`ThemeData` from an explicit value table (no `ColorScheme.fromSeed`), and ALL screens consume it via `Theme.of(context)` — never by direct import of the theme class, never by hardcoded `Color(0x...)` literals.

```dart
// ✅ tokens in ONE file, consumed via Theme.of(context) everywhere
final scheme = Theme.of(context).colorScheme;
// ❌ hardcoded color literals leak outside the token file:
static const _softAmber = Color(0xFFB08900);  // BAD — survives token swaps
```

- **Enforcement:** a contract test that (1) bans `ColorScheme.fromSeed` across `lib/`, (2) scans every `scheme.<role>` used in code and asserts it is explicitly defined (no Material fallback), (3) pins hex values and fonts literally. Retrofitting tokens costs little; the leak is what kills swaps — 3 hardcoded colors survived in a mature codebase.
- **Payoff:** swapping the palette package (`flex_color_scheme`, `dynamic_color`, …) = editing one file + updating the test; 28 consuming files adapt automatically.

### Layer 2 — ThemeData sub-themes (RULE: define before customizing)

`ThemeData` ships `cardTheme`, `appBarTheme`, `textButtonTheme`, `chipTheme`, … — define shape/elevation/typography THERE, once. Per-file repetition of the same `elevation: 0` + `RoundedRectangleBorder(...)` across 5+ files is the symptom this rule prevents: changing card corner radius app-wide then means touching 5 places instead of 1.

- **Rule:** any widget-style attribute repeated in 2+ files belongs in a sub-theme. This is cheap, always right, and independent of project size.

### Layer 3 — Component wrapper layer (JUDGMENT: project decision, NOT a gate)

`AppButton`/`AppCard` wrappers protect against full UI-kit swaps (`shadcn_ui`, `GetWidget`, …) — but retrofitting them means rewriting every screen, and mandating them in a small/short-lived project is over-engineering. Decide by project ambition: long-lived product → build the wrapper layer from day one; small/throwaway → skip, tokens + sub-themes are enough.

**Decision framework — adopting any external UI/theme package (write a DEC with these criteria):**
1. **RTL tested in practice** — Arabic-first projects: most fluttergems UI libs are built and tested LTR-only. This is the FIRST exclusion filter, before scores.
2. **No native code** — Dart-only packages have near-zero Android-policy risk; packages with platform channels add a maintenance surface.
3. **pub.dev floor** — score, last-update recency, open-issue count. fluttergems is a catalog, not a quality certificate.
4. **State-management compatibility** — UI kits that bundle their own controllers can collide with Riverpod/Bloc.

**Android policy reality check:** `compileSdk`/`minSdk`/`targetSdk` come from `flutter.compileSdkVersion` etc. — Google Play targetSdk mandates are solved by Flutter/AGP upgrades, NOT by theme-package upgrades. The real abandonment risk for a Dart package is being pinned to an old Flutter API — which is exactly what the Layer-1/3 separation contains (dead package = one-file swap, not a rewrite).

**Verification:** before any theme/UI-kit adoption, walk a real RTL screen on-device (Arabic text, right-aligned layout, back navigation) — never assume "it should work."

---

## Pattern 50 — Missing-Gate Detection: Run Lenses, Not Memory (LL-053)

**Source:** CarSah (2026-08-11) — founder question "what code-design gate are we blind to?" → 14-lens audit of a mature codebase found 4 real gaps in 3 minutes.

**Rule:** You cannot think your way to unknown unknowns. Missing design gates surface when you RUN a known checklist ("lens") against the code — each lens is accumulated experience from other projects, and any unexpected result is a candidate missing gate. Before every EPIC close / release candidate, run the lens catalog (`references/missing-gate-lenses.md`), not your memory.

```bash
# Before milestone close — run the catalog, don't recall it:
# Lens 11 (highest value — often missing):
find test -iname "*migrat*"          # 0 results = schema migration untested = silent data loss risk
# Lens 12 (governance leakage):
grep -rln "ref.watch" lib/features/*/presentation/ | wc -l   # direct provider use in screens
grep -rln "UseCase" lib/features/*/presentation/ | wc -l      # vs UseCase-mediated screens
```

**Why this is a meta-gate:** the audit found the codebase's KNOWN gates all passing (no debugPrint, no layer-boundary imports, no deprecated API) — yet 4 unknown gates were invisible to memory and surfaced instantly by running commands: **no Isar migration test · UseCase boundary not enforced (19 screens ref.watch vs 6 UseCase) · domain logic thinly unit-tested · no documented secure-storage decision.** Lenses convert "what could be wrong?" into "run this command, read this result."

**How lenses are born (the answer to "how do we find what we don't know"):**
1. **Harvest from other projects** — every project is a different failure lens (theme swap → Pattern 49; this audit → Pattern 50).
2. **Import external standards** — OWASP MASVS, Google engineering practices, official Flutter/Isar docs, published post-mortems.
3. **Capability Auditor** (SOUL.md) — continuously scan for new skills/extensions that could fill a gap.
4. **When any project discovers a gap, ADD it to the lens catalog** (LL-045: lessons flow to the shared knowledge base).

**Rule:** lenses live in the shared skill so EVERY project benefits. New lens discovered → add to `references/missing-gate-lenses.md` with trigger + exact command + interpretation.

---

## Pattern 51 — go_router Shells: relative child paths + measured-resolved-behaviour (LL-054)

**Source:** CarSah (2026-08-12) — BL-075 (the 3-tab navigation shell). Two lessons from one round.

**Level:** 🚪 GATE · MUST — both are machine-detectable; the second is exactly the "a gate measures the source, not the behaviour" shape.

**Rule A — Branch child paths MUST be RELATIVE.** go_router concatenates parent+child paths LITERALLY. An absolute child path (`'/history/detail/:id'`) nested under a `/history` branch resolves to `/history/history/detail/:id` → Page Not Found. Only a relative child (`'detail/:id'`) resolves to `/history/detail/:id`.

```dart
// ❌ BROKEN — resolves to /history/history/detail/:id
GoRoute(path: '/history', routes: [GoRoute(path: '/history/detail/:id', ...)])
// ✅ CORRECT
GoRoute(path: '/history', routes: [GoRoute(path: 'detail/:id', ...)])
```

**Rule B — Path collectors must measure RESOLVED full paths, never declared spellings.** Both TC-NAV-001 and the reachability gate stayed green while the route above was broken at resolution, because they collected `route.path` as declared. Walk the PARSED tree (`router.configuration.routes`) and join parent+child the way go_router does:

```dart
String full = route.path.startsWith('/') ? '$parent${route.path}' : '$parent/${route.path}';
```

The device walk found the Page Not Found that the suite could not see — Rule B converts that regression class into suite-red.

**Verification:** any shell/route-structure change gets a device tap through a NESTED route (e.g. list → detail) — the one shape regex/unit collectors measure least accurately. Also walk one tab switch in BOTH locales when the shell has a deliberate directional override (RTL order pinning: assert the bar's `Directionality` is LTR in the Arabic app — Home stays left).

---

## Pattern 52 — Repeated CI Failures Are a Forensic Investigation, Not a Push Race (LL-055)

**Source:** CarSah (2026-08-13) — STOP-38: a widget test (`rollback_flow_test`, TC-HIST-006) hung on Linux CI only. **Five fix attempts in ~3 hours, each ~25 min of runner time wasted, all cancelled — because each was a hypothesis → patch → push → wait, with NO reproduction of the failing environment first.** The lesson is the founder's catch, proven by the run log.

**Level:** 📏 RULE · SHOULD — process discipline, not machine-detectable.

**The failure pattern (what NOT to do):**
```
1. Hypothesis about the hang → patch → push → CI runs 20–50 min → cancelled → review
2. New hypothesis → patch → push → CI runs again → cancelled → review
3. ...five times. ~2 hours of runner time. Zero green runs. One signature.
```
Each attempt *felt* like progress; the run log shows five identical executions of the same unverified guess. Local macOS stayed green (430/430) — the classic STOP-28 signature (passes here, hangs on Linux) — and the written rule ("reproduce Linux before fixing") was ignored because it was not enforced on the fix process itself.

**The forensic method (what to do instead):**
1. **Isolate FIRST, hypothesize SECOND.** Run the failing file ALONE on the failing platform (CI `workflow_dispatch` on a branch, or a Linux container locally) before writing any fix. A 25-minute whole-suite run to discover nothing is 25 minutes wasted; a single-file run localises in minutes.
2. **Instrument, don't guess.** Add temporary prints/markers around the suspect chain (start/seed, the awaited call, teardown) — the run tells you WHERE it hangs; only then do you know WHAT to fix. The auditor's three diag runs (isolate 006 → instrument rescheduleNotifications → instrument 006 start/seed) produced more truth than the five fix attempts combined.
3. **One run per question.** Each CI run should answer exactly one question (does it hang without the suite? does it hang at seed? does it hang at teardown?). Mixing questions = unreadable runs.
4. **Count the cost aloud.** Before attempt N+1 of the same signature, state: "N attempts, X minutes of runner time, same signature — what have we MEASURED that we didn't know before?" If the answer is nothing new, the next attempt is not a fix, it's a repeat.
5. **A green local run is not evidence of a Linux fix** — it never was (STOP-28). The ONLY evidence is a green run on the failing platform itself.

**The meta-lesson (why this recurs):** a written rule ("reproduce the failing env first") exists in the lessons, but the fix process had no gate on it — so five rounds re-learned it at ~25 min each. **Process rules need the same enforcement as code rules:** when the same signature recurs twice, the process itself is the defect — switch to forensic mode (isolate + instrument) and do not push another hypothesis until a measurement exists.

**Verification:** when a CI hang recurs 2+ times with the same signature, the next commit MUST be a diag run (isolate/instrument), not a fix — reviewable in the commit message itself.

### Mandatory Pre-Push Checklist (every implementer, every push — no exceptions)

Before ANY push to the shared tree, the implementer must have run ALL of:

| # | Check | Command / proof |
|---|---|---|
| 1 | **Local full suite** | `flutter test --concurrency=1 --timeout 60s` — ALL pass locally |
| 2 | **Analyze clean** | `flutter analyze` — No issues found |
| 3 | **Failing-platform reproduction** | IF the row involves a platform-specific defect (Linux CI hang, iOS-only, OEM ROM): the failing file ALONE was run on that platform BEFORE the fix, and the fix is measured against that isolation result |
| 4 | **One question per run** | The CI run this push will answer is named in the commit message (e.g. "answers: does 006 hang alone?") |
| 5 | **Cost counted aloud** | If this is attempt N+1 of the same signature: the commit message states N attempts + what NEW measurement this run produces (or the push is a repeat, which is forbidden) |
| 6 | **Diff scope named** | `git diff --name-only` listed — no surprise files (e.g. unrelated Waves work) ride along |

If ANY row is not provable, the push is not allowed — fix the gap first. A push without rows 3–5 during a repeated-CI-failure is a **push race**, not a fix (LL-055).

---

## Pattern 53 — One Attempt Is Half the Truth: Open Every Attempt Before Claiming Attribution (LL-056)

**Source:** CarSah (2026-08-13) — STOP-38 closure round. The same commit (`1985b0a`) was re-run THREE times and produced THREE different outcomes: attempt 1 failed `add_refresh` + `invoice_photo`; attempt 3 failed `locale_switch`; attempt 2 was **effectively green (430/430, Build ✅, Merged-manifest ✅ — only the artifact upload failed on quota)**. The implementer's letter cited attempt 1 and declared the founder's attribution wrong; the founder's attribution matched attempt 3. **Neither was lying — each had read one attempt.** The strongest evidence in the whole round (the near-green attempt 2) was absent from the letter because nobody opened all three.

**Level:** 🚪 GATE · MUST — a delivery letter that cites CI evidence must list EVERY attempt.

**The rule:** When a delivery cites a CI run as evidence:
1. **Open every attempt** (`actions/runs/<id>/attempts/<n>/jobs`), not just the latest log — the run id alone hides which attempt an evidence block describes.
2. **List the outcome of each attempt** in the letter — N attempts, N rows: what passed, what failed, what was infra-only (quota, runner TLS, upload).
3. **Do not declare a human wrong on the basis of one attempt.** If your evidence and theirs differ, the difference is data (the suite is nondeterministic under load), not proof either of you lied.
4. **The greenest attempt is the strongest evidence** — a near-green run (all but infra upload) is closer to "the suite passes" than any red run is to "the suite fails". It belongs in the letter, not hidden because it was not the one you cited.
5. **N consecutive green runs close a nondeterminism STOP together with the flake question** — the failure sets from N runs are the data that names the cause, a measurement, not another hypothesis.

**Meta-lesson:** "the claim built on one attempt is half the truth no matter how honest" — and "the strongest evidence can be lost because nobody opened all the attempts". The CI evidence section of a delivery letter is a **complete ledger of attempts**, not a single cherry-picked citation.

**Verification:** any delivery letter citing a run that has >1 attempt must contain an attempts table. Auditor checks: `gh api .../runs/<id>/attempts` count matches the letter's rows.

---

## Pattern 54 — The Linter's Suggestion Is Not Always the Fix: Conflicting Analyzers (LL-057)

**Source:** CarSah (2026-08-14) — CARRY-106 round. CI rejected `tasks?[index]?.id` with `use_null_aware_elements` (the linter suggests `?task`). The implementer applied the linter's suggestion literally → CI red AGAIN. Root cause found by measurement, not guesswork: the project runs TWO analyzers in CI — a newer one (suggests `?task`) and an OLDER one pinned inside `isar_generator` (does not understand `?task` — rejects it). One fix satisfies both: the plain statement form. `build_runner` was added to the local verification loop so the conflict surfaces locally, not in CI.

**Level:** 📏 RULE · SHOULD — when a CI analyzer rejects your change and its suggestion causes ANOTHER rejection, suspect conflicting analyzers before trusting either.

**The rule:** When a lint rejection appears, do not assume the linter's suggested replacement is correct:
1. **Check for a second analyzer** — code-generation packages (isar_generator, build_runner plugins) pin their own analyzer versions, which can be older than the standalone `flutter analyze` one.
2. **If two analyzers disagree** — the suggested form may fail the other. Prefer the form that satisfies BOTH (usually the more explicit/statement form).
3. **Add codegen to the LOCAL verification loop** (`build_runner` before/with `flutter analyze`) so the conflict appears on the developer's machine, not as a CI round-trip.
4. This is a measurement discovery: the fix came from reading WHY the second rejection happened, not from blindly following either tool.

**Meta-lesson:** "the tool that flags the error is not the tool that defines the fix". A linter suggestion is a hypothesis, not an instruction — verify it against the FULL build pipeline.

**Verification:** any round where a lint fix causes a second CI rejection must record the conflicting-analyzer check (or state why it does not apply) in the delivery letter.

---

- **flutter-design-anti-patterns** — 31 Flutter design anti-patterns across 14 categories. Includes custom_lint plugin (3 core rules) and SPIKE regex detector. Load for any UI-related task. 🔗 `~/.hermes/skills/flutter/flutter-design-anti-patterns/`
- **flutter-input-hardening** — Centralized input sanitization and validation for Flutter
- **flutter-isar-clean-arch-setup** — Clean Architecture project structure with Isar + Riverpod
