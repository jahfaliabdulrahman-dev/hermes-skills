# Flutter to Dart SDK Version Matrix (generated, not hand-typed)

**Generated:** 2026-08-29 from `releases_macos.json` (Google's official release index).
**Current stable at generation time:** Flutter `3.47.2` (2026-08-27), bundling Dart `3.13.2`.

Every row below is the **first release of that minor line**. Regenerate with
`python3 scripts/build_flutter_sdk_changelog.py --fetch` — never edit version numbers by hand.

| Flutter minor | First release | Date | Bundled Dart SDK |
| :--- | :--- | :--- | :--- |
| **3.47** | `3.47.0` | 2026-08-12 | `3.13.0` |
| **3.44** | `3.44.0` | 2026-05-18 | `3.12.0` |
| **3.41** | `3.41.0` | 2026-02-11 | `3.11.0` |
| **3.38** | `3.38.0` | 2025-11-12 | `3.10.0` |
| **3.35** | `3.35.1` | 2025-08-14 | `3.9.0` |
| **3.32** | `3.32.0` | 2025-05-20 | `3.8.0` |
| **3.29** | `3.29.0` | 2025-02-12 | `3.7.0` |
| **3.27** | `3.27.0` | 2024-12-11 | `3.6.0` |
| **3.24** | `3.24.0` | 2024-08-06 | `3.5.0` |
| **3.22** | `3.22.0` | 2024-05-13 | `3.4.0` |
| **3.19** | `3.19.0` | 2024-02-15 | `3.3.0` |
| **3.16** | `3.16.0` | 2023-11-15 | `3.2.0` |
| **3.13** | `3.13.0` | 2023-08-16 | `3.1.0` |
| **3.10** | `3.10.0` | 2023-05-10 | `3.0.0` |
| **3.7** | `3.7.0` | 2023-01-24 | `2.19.0` |
| **3.3** | `3.3.0` | 2022-08-30 | `2.18.0` |
| **3.0** | `3.0.0` | 2022-05-11 | `2.17.0` |
| **2.10** | `2.10.0` | 2022-02-03 | `2.16.0` |
| **2.8** | `2.8.0` | 2021-12-09 | `2.15.0` |
| **2.5** | `2.5.0` | 2021-09-08 | `2.14.0` |
| **2.2** | `2.2.0` | 2021-05-18 | `2.13.0` |
| **2.0** | `2.0.0` | 2021-03-03 | `2.12.0` |
| **1.22** | `1.22.0` | 2020-10-01 | `2.10.0` |
| **1.20** | `1.20.0` | 2020-08-05 | `2.9.0` |
| **1.17** | `1.17.0` | 2020-05-06 | `not published` |

---

## Reading this matrix

1. **A Dart language feature needs both bounds.** `sdk: ^3.10.0` (dot shorthands) implies Flutter `>=3.38.0`;
   `sdk: ^3.13.0` (primary constructors) implies Flutter `>=3.47.0`. Look the Dart column up here before
   writing `environment:` in `pubspec.yaml`.
2. **Detect the project's version** with `flutter --version`, `.fvmrc`, `.fvm/fvm_config.json`, or `.puro.json`.
3. Releases older than the oldest row above are not in Google's machine-readable index; treat any older
   number as unverified and check `https://docs.flutter.dev/install/archive` manually.
