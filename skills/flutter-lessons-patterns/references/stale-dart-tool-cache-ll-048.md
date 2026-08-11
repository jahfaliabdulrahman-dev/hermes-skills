# LL-048: Stale .dart_tool Cache — Full Reproduction Recipe

**Date:** 2026-07-21
**Project:** CarSah
**Session context:** Guardian hunt re-scan EPIC — 3 BLOCKER findings

## Reproduction

### Initial state
- CarSah project at `cf3759e` (committed) with large pending uncommitted diff (~39 modified, ~30 untracked files)
- Pending diff includes: `splash_screen.dart` migrated from `StatelessWidget` to `ConsumerStatefulWidget`, `app_router.dart` restructured from single-screen to shell with 3 branches + modal routes
- `edit_record_dialog.dart` uses `CarSahLocalization.of(context)` throughout

### Observed symptom
```
lib/app/splash_screen.dart:69:22: Error: The getter 'l10n' isn't defined for the type '_SplashScreenState'.
lib/app/splash_screen.dart:70:22: Error: The getter 'l10n' isn't defined for the type '_SplashScreenState'.
lib/app/splash_screen.dart:73:19: Error: The getter 'l10n' isn't defined for the type '_SplashScreenState'.
lib/features/history/presentation/edit_record_dialog.dart:533:34: Error: The getter 'l10n' isn't defined for the type '_EditRecordDialogState'.
```

### Source verification (on disk)
- `splash_screen.dart:58`: `final l10n = CarSahLocalization.of(context);` — PRESENT in build method
- `splash_screen.dart:71`: `Text(l10n.t('splash_title'), ...)` — uses l10n correctly
- Lines 69-70 in the file: `size: 72, color: theme.colorScheme.primary),` and `const SizedBox(height: 16),` — neither uses `l10n`
- `edit_record_dialog.dart:238`: `final l10n = CarSahLocalization.of(context);` — PRESENT
- `edit_record_dialog.dart:533`: `CarSahLocalization.of(context).t(...)` — uses proper accessor

**Key diagnostic:** Error line numbers DO NOT correspond to `l10n` usage in the actual files on disk. The errors reference old line numbers from a prior file state (before the pending diff was applied).

### Resolution
```bash
flutter clean   # deletes .dart_tool/, build/, ephemeral/
flutter pub get # regenerates package_config.json
flutter test    # 387/387 passed — 0 errors
```

### Root cause mechanism
1. `.dart_tool/` cached kernel files from a build where `splash_screen.dart` was a `StatelessWidget` (no `l10n` variable)
2. Pending diff rewrites the file as `ConsumerStatefulWidget` with `l10n` in build method
3. On `flutter test`, Dart compiler reads stale kernel cache, resolves symbols against old version
4. Old version has `_SplashScreenState` (now defined in pending diff) but at different line numbers — cache mismatch produces phantom errors
5. `flutter clean` wipes cache, forces full recompilation from source on disk → all errors vanish

## Hunting implications

When a Guardian/Hunt scan reports test failures:
1. **Verify source matches error line numbers** — if errors reference lines that don't contain the alleged symbol, suspect stale cache
2. **Run `flutter clean && flutter pub get && flutter test`** before escalating any test failure as a BLOCKER
3. **Stale cache can cause false-positive blockers** — the original HUNT_REPORT_20260721.md attributed test failures to Isar schema mismatch + missing isarDatabaseProvider overrides, but the actual cause was stale compilation artifacts

## Prevention checklist

Before running any Guardian hunt or full test suite on a project with pending diffs:
- [ ] `flutter clean`
- [ ] `flutter pub get`
- [ ] Verify `flutter analyze` is clean
- [ ] `flutter test`
- [ ] If any error line numbers don't match source → repeat clean cycle
