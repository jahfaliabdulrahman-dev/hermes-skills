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

### Lens 11 — Schema Migration Tests ⚠️ (HIGH-VALUE — often missing)
```bash
find test -iname "*migrat*"
grep -rn "Isar.open" lib/ --include="*.dart"
```
**Pass:** migration test exists AND Isar.open uses versioned schemas.
**Fail (zero migration tests):** schema WILL change (fields added, types changed) — a live-user DB upgrade without a migration test = silent data loss. This is the most expensive class of missing gate.

### Lens 12 — UseCase Enforcement (clean architecture)
```bash
echo "screens using ref.watch directly: $(grep -rln "ref.watch" lib/features/*/presentation/ | wc -l)"
echo "screens using UseCase:            $(grep -rln "UseCase\|usecase" lib/features/*/presentation/ | wc -l)"
```
**Interpretation:** if screens consume providers directly far more than UseCases, business logic lives in widgets → changing logic touches many screens (same pattern as missing component layer in Pattern 49, but for governance).

### Lens 13 — Domain-Layer Test Isolation
```bash
echo "total test files: $(find test -name '*.dart' | wc -l)"
find test -name "*.dart" | grep -iE "repositor|usecase|domain|service" | head -15
```
**Interpretation:** business logic (transactions, calculations, validations) must be unit-tested in isolation, not only through widget tests. UI tests passing with broken logic = false confidence.

### Lens 14 — Secure-Storage Decision (documented, not assumed)
```bash
grep -rn "secure_storage\|flutter_secure\|encrypt" pubspec.yaml lib/ 2>/dev/null
```
**Interpretation:** for local-first apps, "no secure storage" may be correct (DEC-001) — but it must be a DOCUMENTED decision, not an accident. If any token/credential enters the app later, a gate must exist to route it to secure storage.

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
