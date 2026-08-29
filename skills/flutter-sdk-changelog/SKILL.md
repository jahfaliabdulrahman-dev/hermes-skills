---
name: flutter-sdk-changelog
description: >-
  Use when you need a Flutter version fact: which Dart SDK ships with a Flutter release, what the correct
  `environment:` bounds are for a language feature, what replaced a deprecated widget or property, what changed
  between two Flutter versions, or how to step a legacy Flutter app up to current stable. Every version number
  here is generated from Google's official release index and the flutter/flutter stable source tree, never from
  model memory.
sources:
  - https://storage.googleapis.com/flutter_infra_release/releases/releases_macos.json (Google's official release index — every version/date/Dart mapping)
  - https://github.com/flutter/flutter (stable branch, read with `git grep` over live @Deprecated annotations)
  - flutter/flutter docs/contributing/Tree-hygiene.md (the beta-marker → first-stable derivation rule)
  - https://docs.flutter.dev/release/breaking-changes/wide-gamut-framework (Color.withOpacity phase 1 = 3.27)
  - Audited then rejected as a source - https://github.com/RandalSchwartz/dart-sdk-skills (MIT) — see Provenance
---

# Flutter SDK Version, Deprecation & Migration Reference

> **Freshness contract — read first.**
> Generated **2026-08-29**. Stable at generation time: **Flutter `3.47.2`** (2026-08-27) bundling **Dart `3.13.2`**.
> Regenerate with `python3 scripts/build_flutter_sdk_changelog.py --fetch` (~4s; resolves the SDK from
> `$FLUTTER_ROOT` or `which flutter`, no hard-coded paths).
> Drift is detected by `python3 scripts/check_freshness.py` — exit 1 means the published stable moved
> ahead of these files. **If the gate fails, regenerate before answering any version question.**

## Rule 0 — never state a Flutter version from memory

Flutter ships a new stable minor roughly every 3 months, so any version fact held in model weights is stale by
construction. This skill exists because that staleness silently breaks `pubspec.yaml` bounds and CI.

1. Version/Dart mapping → read [`references/flutter-to-dart-version-matrix.md`](references/flutter-to-dart-version-matrix.md) (generated).
2. Deprecated symbol → read [`references/widget-deprecations-and-replacements.md`](references/widget-deprecations-and-replacements.md) (generated, 217 members, Flutter 3.13 → 3.44).
3. If the answer is not in either file, verify live before answering:
   ```bash
   curl -s https://storage.googleapis.com/flutter_infra_release/releases/releases_macos.json | python3 -c "import json,sys; d=json.load(sys.stdin); h=d['current_release']['stable']; r=[x for x in d['releases'] if x['hash']==h][0]; print(r['version'], r['release_date'][:10], r['dart_sdk_version'])"
   flutter --version              # what THIS machine has
   ```

---

## 🎯 Highest-impact deprecations (verified against the 3.47 stable tree)

These are the ones that actually hit an app being upgraded. Full list in the generated reference.

| Deprecated | Replacement | First stable |
| :--- | :--- | :--- |
| `cacheExtent`, `cacheExtentStyle` (all scroll views, viewports, reorderable lists) | `scrollCacheExtent` | 3.44 |
| `ReorderableList.onReorder` | `onReorderItem` (it fixes the `newIndex` off-by-one for the removed item) | 3.44 |
| `SlideTransition` / `SizeTransition` `axisAlignment` | `alignment` (controls both axes) | 3.44 |
| `TextInput.setStyle` | `updateStyle` | 3.44 |
| `ImageFilter`-carrying `filter` on render objects | `filterConfig` | 3.41 |
| `CupertinoSheetRoute.builder` / `pageBuilder` | `scrollableBuilder` | 3.41 / 3.35 |
| `Expansible` `duration` / `curve` / `reverseCurve` | `animationStyle` | 3.41 |
| `Semantics.focusable`, `isFocusable` | `focused` (setting it implies focusable) | 3.38 |
| `findChildIndexCallback` (`ListView.separated`, slivers) | `findItemIndexCallback` (item indices, not child indices) | 3.38 |
| `SemanticsService.announce` | `sendAnnouncement` (multi-window safe) | 3.38 |
| `TickerMode.of` / `getNotifier` | `TickerMode.valuesOf` / `getValuesNotifier` | 3.38 |
| `Radio` / `RadioListTile` / `CupertinoRadio` `groupValue` + `onChanged` | wrap in a `RadioGroup` ancestor | 3.35 |
| `CupertinoDynamicColor` `value`/`red`/`green`/`blue`/`opacity`/`withOpacity` | component accessors `.r/.g/.b/.a`, `toARGB32()`, `withValues()` | 3.35 |
| `AppBarTheme.color` | `backgroundColor` | 3.35 |
| `DropdownButtonFormField.value` | `initialValue` | 3.35 |
| `Switch` / `SwitchListTile` `activeColor` | `activeThumbColor` (+ `activeTrackColor`) | 3.32 |
| `ExpansionTileController` | `ExpansibleController` | 3.32 |
| `Tooltip.height` / `TooltipThemeData.height` | `constraints` | 3.32 |
| `Color.withOpacity` (dart:ui, not the framework tree) | `Color.withValues(alpha: …)` — wide-gamut migration, avoids 8-bit precision loss | 3.27 |
| `MaterialState*` family | `WidgetState`, `WidgetStateProperty`, `WidgetStatesController` | 3.22 |
| `Form.onPopInvoked` | `onPopInvokedWithResult` | 3.24 |
| `WillPopScope` | `PopScope(canPop:, onPopInvokedWithResult:)` — required for Android predictive back | 3.13 |
| `textScaleFactor` (all widgets) | `textScaler` (nonlinear text scaling) | 3.13 |

### Removed, not deprecated — hard build breaks
`FlatButton` → `TextButton`; `RaisedButton` → `ElevatedButton`; `OutlineButton` → `OutlinedButton`;
`TextTheme.headline1…6` / `bodyText1/2` / `subtitle1/2` → `displayLarge…bodyLarge/titleMedium`;
`ThemeData.accentColor` → `ColorScheme.secondary`; `Scaffold.of(context).showSnackBar` →
`ScaffoldMessenger.of(context).showSnackBar`; `ThemeData.toggleableActiveColor` → per-widget
`WidgetStateProperty`. Verified absent from the 3.47 tree — these produce compile errors, not warnings.

---

## 🔗 Dart feature → required Flutter floor

A Dart language feature needs the Flutter release that bundles that Dart SDK. Derived from the generated matrix:

| Dart feature | `sdk:` lower bound | Implies Flutter `>=` |
| :--- | :--- | :--- |
| Primary constructors | `^3.13.0` | `3.47.0` |
| Private named parameters | `^3.12.0` | `3.44.0` |
| Dot shorthands (`.blue`, `crossAxisAlignment: .start`) | `^3.10.0` | `3.38.0` |
| Sound flow analysis | `^3.9.0` | `3.35.0` |
| Null-aware elements (`[?maybe]`) | `^3.8.0` | `3.32.0` |
| Wildcard variables `_` | `^3.7.0` | `3.29.0` |
| Digit separators | `^3.6.0` | `3.27.0` |

Pair this skill with `dart-sdk-changelog` for the Dart-side feature matrix.

---

## 🛠️ Runbooks

### 1. "What replaced X?" / analyzer reports a deprecation
1. Grep the generated reference: `grep -i "<symbol>" references/widget-deprecations-and-replacements.md`.
2. Try the automated migration first — Flutter policy requires a data-driven fix with every framework
   deprecation (`docs/contributing/Tree-hygiene.md`), so this usually does the whole job:
   ```bash
   dart fix --dry-run     # inspect
   dart fix --apply       # migrate
   ```
3. Only hand-edit what `dart fix` leaves behind, then `flutter analyze`.

### 2. Choosing `environment:` bounds for a package
1. Decide the newest Dart language feature the code actually uses (see `dart-sdk-changelog`).
2. Set `sdk: '^<that Dart minor>'`.
3. Add the matching `flutter:` floor from the matrix — never guess it:
   ```yaml
   environment:
     sdk: ^3.12.0
     flutter: ">=3.44.0"
   ```
4. Verify on the machine that will build: `flutter --version` and `dart analyze`.

### 3. "What's new in Flutter X.Y?"
1. Confirm X.Y is a real stable minor in the matrix (Flutter skips numbers: there is no stable 3.30, 3.33,
   3.36, 3.40, 3.43 — those are dev/beta cycles only).
2. State the bundled Dart SDK and release date from the matrix.
3. List the deprecations whose `First stable` equals X.Y from the generated reference.
4. For anything beyond that, read the official release notes rather than guessing:
   `https://docs.flutter.dev/release/release-notes`.

### 4. Rescuing a legacy Flutter app
1. Read the current bounds from `pubspec.yaml` and the matrix row for that Flutter minor.
2. Step in **stable minors**, never in one jump — build and run tests at each stop.
3. At each stop: `dart fix --apply`, then `flutter analyze`, then run the app.
4. Pre-3.0 (Dart < 2.12) apps must cross sound null safety first — that is a Dart-side migration; use
   `dart-sdk-changelog`'s legacy rescue guide before touching widgets.
5. Material 3 is the default theme since Flutter 3.16; if the app pins `useMaterial3: false`, treat the M3
   switch as its own change with visual review, not a side effect of the upgrade.

### 5. Refreshing this skill (do this, do not patch numbers by hand)
```bash
cd <this skill directory>
python3 scripts/build_flutter_sdk_changelog.py --fetch   # re-extracts the stable tree itself
python3 scripts/check_freshness.py                       # must print ALL FRESH, exit 0
```
The generator finds the Flutter SDK via `$FLUTTER_ROOT`, else `which flutter`, and needs it to be a git
checkout (standard `git clone`, Homebrew and `fvm` installs are). Pass `--flutter-root PATH` otherwise.
Then update the "Freshness contract" block and the highest-impact table if new buckets appeared — the
gate fails if that table disagrees with the generated data, so it cannot silently rot.

Automate it: run `scripts/check_freshness.py` on a schedule (cron / CI). It prints deterministic output
and exits non-zero only on real drift, so it is safe as a change-detector that wakes an agent up.

---

## 📌 Provenance and why this is not an upstream copy

Built after auditing [`RandalSchwartz/dart-sdk-skills`](https://github.com/RandalSchwartz/dart-sdk-skills)
(MIT) on 2026-08-29. Its Dart half was adopted (see `dart/dart-sdk-changelog`); its Flutter half was rejected
and rebuilt here because it carried three defects that this design structurally prevents:

| Upstream defect | Root cause | Fix applied here |
| :--- | :--- | :--- |
| Version matrix ended at "Flutter 3.27 / 3.29 — Late 2024 / 2025", missing 6 stable minors and ~18 months | hand-typed tables, and CI gates that only checked frontmatter, link targets and style ("e.g."/"i.e." bans) — never a version fact | matrices are **generated** from `releases_macos.json` + the stable git tree, and a cron freshness gate fails when the published stable moves ahead of the file |
| `Flutter 3.27 / 3.29 → Dart 3.7 / 3.8` (both off by one; truth is 3.6.0 and 3.7.0) | mapping written from memory | mapping read from the release index, per release |
| `Color.withOpacity` "deprecated in Flutter 3.22" | recalled, not checked; the wide-gamut phase 1 actually landed in stable **3.27.0** (docs.flutter.dev/release/breaking-changes/wide-gamut-framework) | deprecation versions derive from the `@Deprecated` marker in the source plus the documented beta→stable rule |
