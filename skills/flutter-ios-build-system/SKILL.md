---
name: flutter-ios-build-system
version: 1.0.0
category: flutter
description: Complete Flutter iOS build system knowledge — Xcode, signing, TestFlight, App Store Connect. Built from the OFFICIAL flutter.dev deployment guide (docs.flutter.dev/deployment/ios, updated 2026-07-31) + verified live pitfalls from CarSah's first iOS build (2026-08-13).
triggers:
  - "build ios"
  - "testflight"
  - "xcode"
  - "ipa"
  - "app store connect"
---

# Flutter iOS Build System

> **Provenance: OFFICIAL SOURCE.** Every step below is transcribed from the
> official Flutter guide — `https://docs.flutter.dev/deployment/ios` (Flutter
> 3.44.7, page updated 2026-07-31) — plus verified pitfalls from CarSah's
> first-ever iOS build (2026-08-13, BL-100). Where a step comes from live
> experience and not the official guide, it is marked **[LIVE]**.

## 0. Prerequisites (hard requirements — check BEFORE anything)

| Requirement | Check command | Why |
|---|---|---|
| macOS device | `uname` — must be Darwin | Xcode only runs on macOS |
| Xcode installed | `xcodebuild -version` | Required to build/release |
| **iOS platform SDK installed** | `xcodebuild -showsdks \| grep -i iphoneos` | **[LIVE] CarSah's first pitfall: the simulator build failed with "missing iOS 26.5 platform" — the iOS SDK was NOT installed in Xcode. Fix: Xcode → Settings → Components → install the iOS platform (or `xcodebuild -downloadPlatform iOS`).** Without it, NO iOS build (device or simulator) can even be attempted. |
| CocoaPods | `pod --version` | iOS plugin dependencies |
| Apple Developer Program | `https://developer.apple.com/programs/` | Required to publish (99$/yr) |
| App Store Connect app record | Browser — appstoreconnect.apple.com | Register bundle ID + app record |

## 1. Register the app (one-time, founder-gated)

1. **Register a Bundle ID** — developer.apple.com → App IDs → + → Explicit App ID → ID like `com.carsah.carsah` → register.
2. **Create the app record** — App Store Connect → Apps → + → New App → check **iOS only** (Flutter has NO tvOS support — leave tvOS unchecked) → Create → App Information → select the Bundle ID.

## 2. Review Xcode project settings

```bash
open ios/Runner.xcworkspace
```
Verify in the Runner target:
- **General → Identity:** `Display Name` (user-visible) + `Bundle Identifier` (the registered App ID).
- **Signing & Capabilities:** `Automatically manage signing` = true (default; sufficient for most apps) + **Team** = your Apple Developer team.
- **Build Settings → Deployment:** `iOS Deployment Target` — Flutter supports iOS 13+; raise it only if plugins need newer APIs.

## 3. App icon & launch image

- Replace placeholder icons in `Assets.xcassets` (Runner folder) with the real app icons (HIG guidelines — light/dark/tinted variants).
- Verify: `flutter run` for icon; **hot RESTART (not hot reload)** for the launch image.

## 4. Version numbers

- `pubspec.yaml`: `version: 1.0.0+1` — build-name = `CFBundleShortVersionString`, build-number = `CFBundleVersion`.
- Override per build: `flutter build ipa --build-name X --build-number Y`.
- **Each TestFlight/App Store upload requires a UNIQUE build number.**

## 5. Build the archive + IPA

```bash
flutter build ipa
```
- Produces: `.xcarchive` in `build/ios/archive/` + `.ipa` in `build/ios/ipa/`.
- Consider `--obfuscate --split-debug-info` for release.
- Non-App-Store distribution: `--export-method ad-hoc | development | enterprise`.

## 6. Upload to App Store Connect (3 ways)

```bash
# 1. Command line (altool):
xcrun altool --upload-app --type ios -f build/ios/ipa/*.ipa --apiKey YOUR_KEY --apiIssuer YOUR_ISSUER
# 2. Transporter macOS app — drag-drop the .ipa
# 3. Xcode — open the .xcarchive → Validate App → address issues → Distribute App
```

## 7. TestFlight release

1. App Store Connect → app → **TestFlight tab** → Internal Testing → select build → Save.
2. Add internal testers' emails (Users and Roles page).
- External testing requires beta review; internal testers get builds instantly (up to 100 members).

## 8. App Store submission

1. Pricing and Availability → complete.
2. Status sidebar → **1.0 Prepare for Submission** → complete required fields.
3. **Submit for Review** → Apple reviews → release per Version Release settings.

## 9. CI/CD iOS (from the official CD guide)

- **Xcode Cloud post-clone script** (official pattern):
  ```bash
  set -e
  cd $CI_PRIMARY_REPOSITORY_PATH
  git clone https://github.com/flutter/flutter.git --depth 1 -b stable $HOME/flutter
  export PATH="$PATH:$HOME/flutter/bin"
  flutter precache --ios
  flutter pub get
  HOMEBREW_NO_AUTO_UPDATE=1 brew install cocoapods
  cd ios && pod install
  ```
- **fastlane** (official): project must build via `flutter build ipa`; fastlane match for certs; `app-store-connect publish` for upload; **`keychain use-login`** to avoid auth issues.

## Pitfalls — verified live (CarSah BL-100, 2026-08-13)

1. **[LIVE] Missing iOS platform SDK** — `flutter build ios` / simulator run fails with "missing iOS 26.5 platform" when Xcode's iOS SDK isn't installed. Verify FIRST with `xcodebuild -showsdks`. Fix: Xcode → Settings → Components → Install iOS platform.
2. **[LIVE] `pod install` side effects dirty the tree** — running pod install / first iOS build modifies `ios/Runner.xcodeproj/project.pbxproj` and adds `ios/Pods/` + `Podfile.lock`. Decide whether they are committed (they should be — podfile.lock + pbxproj are source) and check `git status` before assuming the tree is clean.
3. **Signing identity change = uninstall + data wipe on Android** (DEC-066) — the iOS equivalent: changing team/certificate can orphan provisioning; always keep the same signing identity across updates.
4. **tvOS checkbox must stay unchecked** — Flutter does not support tvOS; checking it creates an invalid app record.

## Verification checklist (before claiming "iOS build works")

- [ ] `xcodebuild -version` + `xcodebuild -showsdks | grep iphoneos` — SDK present
- [ ] `pod --version` — CocoaPods installed
- [ ] `flutter build ios --debug` (or simulator run) — compiles without the platform error
- [ ] `flutter build ipa` — produces .xcarchive + .ipa
- [ ] Bundle ID matches the App Store Connect record
- [ ] Build number unique per upload
