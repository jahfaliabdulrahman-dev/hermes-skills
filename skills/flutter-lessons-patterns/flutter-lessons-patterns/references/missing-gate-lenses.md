# Missing-Gate Detection Lenses — Runnable Checklist Catalog

**Source:** CarSah (2026-08-11) — founder question "what code-design gate are we blind to?" → 14-lens audit found 4 real gaps in 3 minutes on a mature codebase.

**How to use:** run each lens before an EPIC close / release candidate. A lens is: trigger → exact command → interpretation. Any UNEXPECTED result is a candidate missing gate. Do not trust memory — run the commands.

**How lenses are born:** a gate is discovered (a) when a bug bites in another project, (b) when a thought-experiment ("what if we swap X?") reveals a structural assumption, or (c) when an external standard (OWASP, Google engineering practices, official docs) is imported. When ANY project discovers a gap, ADD it here (LL-045: lessons flow to the shared knowledge base).

---

## The 14-Lens Catalog

### Lens 1 — Layer Boundaries: feature → feature imports
```bash
grep -rn "import '..features" lib/ --include="*.dart" | grep -v "features/.*/features"
```
**Pass:** zero cross-feature imports (or documented shared-core only).
**Fail:** feature A reaching into feature B internals → architecture decay.

### Lens 2 — Logger Gate: raw debugPrint/print outside AppLogger
```bash
grep -rn "debugPrint\|print(" lib/ --include="*.dart" | grep -viE "logger|_log\.|AppLogger"
```
**Pass:** zero. **Fail:** raw prints carry no level/category/persistence (DEC-046 rationale).

### Lens 3 — Deprecated APIs (example: withOpacity → withValues in recent Flutter)
```bash
grep -rn "withOpacity" lib/ --include="*.dart"
```
**Pass:** zero. **Fail:** deprecation warnings accumulate; future Flutter upgrade breaks silently. *Note: this lens is version-specific — check current Flutter deprecations and update the pattern.*

### Lens 4 — Data-Layer Leakage: Isar/db direct in presentation layer
```bash
grep -rn "isar\." lib/features/*/presentation/ --include="*.dart"
```
**Pass:** zero (presentation talks to providers only). **Fail:** UI bypasses the data boundary.

### Lens 5 — Accessibility: IconButton tooltips
```bash
echo "total IconButtons: $(grep -rn "IconButton(" lib/ --include="*.dart" | wc -l)"
echo "with tooltip:      $(grep -rn "IconButton(" lib/ --include="*.dart" -A2 | grep -c "tooltip")"
```
**Pass:** counts equal (or documented exceptions). **Fail:** icon-only buttons without tooltips are inaccessible (screen readers, RTL).

### Lens 6 — Build-Performance: async work / FutureBuilder in build()
```bash
grep -rn "FutureBuilder\|async\b.*build\|_loadAsync" lib/features/*/presentation/*.dart --include="*.dart"
```
**Pass:** zero. **Fail:** work in build → jank, rebuild storms.

### Lens 7 — Async-Gap Safety: BuildContext across await
```bash
grep -rn "if (!context.mounted)" lib/ --include="*.dart" | wc -l
```
**Pass:** context.mounted guards exist wherever context is used after await (use_build_context_synchronously).
**Fail:** zero guards in a codebase with async UI actions → crash risk on unmounted widgets.

### Lens 8 — Dependency Weight
```bash
sed -n '/^dependencies:/,/^dev_dependencies:/p' pubspec.yaml
```
**Interpretation:** every dependency is a maintenance + APK-size + supply-chain surface. Heavy UI kits / platform-channel packages need a DEC (see Pattern 49 decision framework).

### Lens 9 — const Discipline (rebuild performance)
```bash
grep -rn "const " lib/features/<hot-screen-dir>/*.dart | wc -l
```
**Interpretation:** low const count in hot screens → avoidable rebuilds. (Heuristic; combine with performance profiling.)

### Lens 10 — Error Handling: try/catch coverage in presentation
```bash
grep -rn "catch" lib/features/*/presentation/*.dart --include="*.dart" | wc -l
```
**Interpretation:** async operations without catch → unhandled exceptions. Cross-check with async call sites.

### Lens 11 — Schema-Compat Fixture (Isar 3 has NO migration API — corrected 2026-08-11)
```bash
grep -rn "migrat" ~/.pub-cache/hosted/pub.dev/isar-3.1.0+1/lib/ | head -3   # expect ZERO
grep -n "static Future<Isar> open" ~/.pub-cache/hosted/pub.dev/isar-3.1.0+1/lib/src/isar.dart
```
**⚠️ CORRECTION (auditor-verified):** this lens was originally written as "migration test on versioned schemas" — **Isar 3 has no such mechanism**: `Isar.open` takes no `version` parameter and the package has zero `migrat*` symbols. A "migration harness" would be a documented myth. Auto schema evolution is safe for add/remove field but **silently loses data on type change/rename** — with no callback to notice.
**Pass:** a committed reference `.isar` fixture exists (captured at release schema-lock — impossible to reproduce "v1" after launch) AND a compat test opens it under the current schema.
**Fail:** no fixture — migration (to Drift or Isar itself) would start blind with no description of the schema the user's data was written with.
**Timing:** fixture capture is a **release-gate item at schema-lock**, not a pre-release task — after publishing, an original v1 can never be reproduced.

### Lens 12 — Screens Must Not Read Repositories Directly (corrected 2026-08-11)
```bash
# NOT the 19-vs-6 ref.watch ratio — that compares different populations
# (ref.watch is the idiomatic Riverpod read; UseCase count measures nothing).
# The real violation is screens bypassing the application layer entirely:
grep -rn "RepositoryProvider\|\.repository\b" lib/features/*/presentation/*.dart | grep -v "// \|app_providers"
```
**⚠️ CORRECTION (auditor-verified):** the original "19 ref.watch vs 6 UseCase" metric was **invalid** — `ref.watch` on feature providers (`activeVehicleProvider`, `maintenanceOutlookProvider`…) is exactly the correct Riverpod usage, and 9 of 10 features already have an `application/` layer. **The real, bounded, grep-able gate:** screens that read `repository`/`service` directly, bypassing the application layer. Known sites are finite (~8, e.g. edit_record_screen:142/313/314, record_detail_screen:435, add_service_record_screen:84, settings_screen:111, odometer_step_screen:129/135). One-line gate, countable, perfect for `test/structure/`.
**Interpretation:** a screen owning the wiring (use-case providers defined INSIDE a view file) is both an architectural violation AND the reason those use cases have zero test coverage (they are not in the provider tree the tests override) — one fix closes both.

### Lens 13 — Domain-Layer Test Isolation
```bash
echo "total test files: $(find test -name '*.dart' | wc -l)"
find test -name "*.dart" | grep -iE "repositor|usecase|domain|service" | head -15
```
**⚠️ CORRECTION (auditor-verified):** "55 files, thin coverage" was an impression, not a measurement. Count **by named use case**: `grep -rl "CreateVehicleUseCase" test/` etc. — two were at zero (`CreateVehicleUseCase`, `SetActiveVehicleUseCase`), five covered. **And name-counting can mislead both ways:** `CreateVehicleUseCase` had zero *class-name* references yet its behavior IS covered through `setup_wizard_test` walking the wizard — the precise gap is the class's own unexercised branches. Beware similarly-named pairs (`SwitchActiveVehicleUseCase` tested, `SetActiveVehicleUseCase` not — two classes, adjacent behavior).
**Interpretation:** business logic must be unit-tested in isolation; count named classes, then verify behavior coverage (a wizard walk may cover it).

### Lens 14 — Documented Security Rules Need a Gate, Not a Decision (corrected 2026-08-11)
```bash
grep -rn "Must not store" app-spec/13_security_privacy.md   # the decision EXISTS
grep -rn "secure_storage\|flutter_secure\|encrypt" pubspec.yaml lib/ 2>/dev/null
```
**⚠️ CORRECTION (auditor-verified):** the original claim "no documented decision" was **wrong** — `13 §5.1` explicitly forbids raw VIN/auth/payment tokens/API keys, and §14 names encryption a non-goal. **The real gap is narrower:** a documented rule with **no automated gate** — nothing fails the build if a token field appears. One-line grep gate (`Must not store` → enforcement test in `test/structure/`).
**Methodological lesson (this lens's own failure):** concluding "undecided" by grepping code without reading the spec that decides it — for a governance-heavy project this is a structural blind spot of the lens set.

---

## Audit Evidence (CarSah 2026-08-11 — what the lenses found)

| Lens | Result | Verdict |
|---|---|---|
| 1 Layer boundaries | zero cross-feature imports | ✅ gate holds |
| 2 Logger gate | zero raw prints | ✅ gate holds |
| 3 Deprecated API | zero withOpacity | ✅ gate holds |
| 4 Isar in presentation | zero | ✅ gate holds |
| 5 IconButton tooltips | 3 buttons / 2 tooltips | ⚠️ 1 missing |
| 6 async in build | zero | ✅ gate holds |
| 7 context.mounted | 5 guards | ✅ gate holds |
| 8 dependency weight | lean (7 deps, all justified) | ✅ |
| 9 const discipline | 54 in dashboard | ✅ healthy |
| 10 error handling | 12 catches in presentation | ⚠️ verify coverage |
| 11 **migration tests** | **0 migration tests; Isar.open at lib/data/local/isar_database.dart:30** | ❌ **MISSING GATE** |
| 12 **UseCase enforcement** | **19 screens ref.watch vs 6 UseCase** | ❌ **NOT ENFORCED** |
| 13 **domain test isolation** | **55 test files, only 5 in test/data, 1 use-case test** | ⚠️ **THIN** |
| 14 **secure-storage decision** | **no secure_storage, no documented decision** | ❌ **UNDOCUMENTED** |

**Bottom line:** 4 real gaps invisible to memory, found by running commands. This is the proof that lenses > recall.

---

## ⚠️ Post-Audit Correction — the lens set itself was audited (2026-08-11)

The external auditor re-produced every lens command on the live repo and found **3 of the 14 lenses were wrong** (Lens 11: migration API that doesn't exist; Lens 12: metric comparing different populations; Lens 14: concluded "undocumented" without reading the spec). **The corrected lenses above carry the corrections inline.**

**The meta-lesson — a wrong lens is worse than no lens:** a wrong lens produces a false result on every run, in every project, forever — costing time and credibility. Before trusting a lens result, verify the lens measures what it claims:
1. **Verify the API exists** before writing a lens around it (Lens 11: `Isar.open` has no version param).
2. **Verify the metric measures the claim** (Lens 12: ref.watch count vs business-logic-in-widgets are different populations).
3. **Read the spec before concluding "undocumented"** (Lens 14: the decision existed in 13 §5.1 — the gap was the missing gate, not the missing decision).
4. **A lens that produces a false positive poisons every downstream decision** — a scan catches what review repeats; a wrong scan repeats wrongness.
