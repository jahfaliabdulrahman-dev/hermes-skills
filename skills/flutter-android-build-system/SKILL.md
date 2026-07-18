---
name: flutter-android-build-system
description: Complete Flutter Android build system knowledge — Gradle configuration, namespace, applicationId, AGP versions, ProGuard/R8, Isar compatibility, signing, CI/CD. Merged from developer.android.com/build + isar.dev + docs.flutter.dev/deployment/android. MoA-audited 2026-07-06.
sources:
  - https://developer.android.com/build (Official AGP docs — namespace, build types, ProGuard)
  - https://isar.dev (Isar ProGuard keep rules)
  - https://docs.flutter.dev/deployment/android (Flutter deployment)
  - NOT: github.com/android/skills (MoA audit — covers app code, not build config)
---

# Flutter Android Build System — Authoritative Reference

## When to Load
- ANY Flutter project creating/editing `android/app/build.gradle.kts`
- ANY release/deployment task
- ANY CI/CD pipeline setup
- When `flutter build apk` fails with native errors

---

## 1. Namespace vs ApplicationId — The #1 Crash Source

### From developer.android.com (Official AGP Docs)
```kotlin
android {
    namespace = "com.example.app"  // R class, BuildConfig, manifest .ClassName resolution
    defaultConfig {
        applicationId = "com.example.app"  // Unique ID on device + Play Store
    }
}
```

**CRITICAL RULE:** `namespace` MUST equal the Kotlin package of `MainActivity.kt`.

```
AndroidManifest:  android:name=".MainActivity"
         ↓ resolved relative to namespace
Android looks for: {namespace}.MainActivity
         ↓
If namespace ≠ Kotlin package → ClassNotFoundException → CRASH BEFORE SPLASH
```

### Verification (MANDATORY before every build)
```bash
NS=$(grep -oP 'namespace\s*=\s*"\K[^"]+' android/app/build.gradle.kts)
PKG=$(grep -oP '^package\s+\K\S+' android/app/src/main/kotlin/**/MainActivity.kt)
[ "$NS" = "$PKG" ] || { echo "BLOCKED: namespace ≠ package"; exit 1; }
```

---

## 2. ProGuard / R8 — The Isar Incompatibility

### From developer.android.com
```kotlin
buildTypes {
    release {
        isMinifyEnabled = true   // Enables R8 code shrinking
        isShrinkResources = true // Shrinks resources
        proguardFiles(
            getDefaultProguardFile("proguard-android-optimize.txt"),
            "proguard-rules.pro"
        )
    }
}
```

### ⚠️ Isar + isMinifyEnabled = CRASH
R8 strips classes NOT directly referenced in Java/Kotlin. Isar adapter classes (CachedSessionAdapter, etc.) are loaded REFLECTIVELY by native code → stripped → `IsarError` → crash.

**Rule:** If `isar:` in `pubspec.yaml`, `isMinifyEnabled` MUST be `false` OR add explicit `-keep` rules.

### Isar ProGuard Keep Rules (from isar.dev)
```proguard
# Isar native bindings — DO NOT REMOVE
-keep class io.isar.** { *; }
-keepclassmembers class * {
    @io.isar.annotations.** <fields>;
}

# Isar generated adapters — loaded reflectively
-keep class * extends io.isar.IsarCollectionSchema { *; }

# If using isar_flutter_libs
-keep class com.example.isar_flutter_libs.** { *; }
-dontwarn com.example.isar_flutter_libs.**
```

### Full ProGuard Rules for Flutter + Isar
```proguard
# ─── Flutter Engine ───
-keep class io.flutter.app.** { *; }
-keep class io.flutter.plugin.** { *; }
-keep class io.flutter.embedding.** { *; }
-keep class io.flutter.** { *; }

# ─── Isar ───
-keep class io.isar.** { *; }
-keepclassmembers class * {
    @io.isar.annotations.** <fields>;
}
-keep class * extends io.isar.IsarCollectionSchema { *; }

# ─── Dio / OkHttp ───
-keep class okhttp3.** { *; }
-dontwarn okhttp3.**
-dontwarn okio.**

# ─── App Code ───
-keep class com.jahfali.hermex_android.** { *; }
-keepattributes Signature
-keepattributes *Annotation*

# ─── Secure Storage ───
-keep class com.it_nomads.fluttersecurestorage.** { *; }
```

---

## 3. AGP Version Compatibility

| AGP | Key Change | Impact on Flutter |
|-----|-----------|-------------------|
| 8.8+ | `package` attribute in AndroidManifest.xml rejected | Breaks `isar_flutter_libs` (carries `package="..."`) |
| 8.11.1 | Default on `ubuntu-latest` CI runner | CI builds stricter than local |
| 9.0 | New DSL, Java 11 default | Plugin compatibility needed |
| **4.2** (Isar 3.1.0 compileSdk) | Resources reference attributes (`lStar`) introduced API 29+ | `AAPT: error: resource android:attr/lStar not found` — Isar 3.1.0 binary incompatible with AGP 8.8+ |

### Fix: isar_flutter_libs + AGP 8.8+

The `gradle.projectsEvaluated` hook below fixes the manifest `package` attribute rejection. **It does NOT fix the `lStar` resource incompatibility** — that requires either an AGP 8+ compatible Isar fork or deferring Isar entirely.
```kotlin
// android/build.gradle.kts (root)
gradle.projectsEvaluated {
    subprojects {
        if (name == "isar_flutter_libs") {
            // Disable verifyReleaseResources
            tasks.matching { it.name.contains("verifyReleaseResources") }.configureEach {
                enabled = false
            }
            // Strip package attribute from AndroidManifest
            tasks.matching { it.name.startsWith("process") && it.name.contains("Manifest") }.configureEach {
                doFirst {
                    val mf = file("${project.projectDir}/src/main/AndroidManifest.xml")
                    if (mf.exists() && mf.readText().contains("package=")) {
                        mf.writeText(mf.readText().replace(Regex("""package="[^"]*"\s*"""), ""))
                    }
                }
            }
        }
    }
}
```

---

## 4. Standard build.gradle.kts Template

```kotlin
// android/app/build.gradle.kts
plugins {
    id("com.android.application")
    id("kotlin-android")
    id("dev.flutter.flutter-gradle-plugin")
}

android {
    namespace = "com.jahfali.hermex_android"  // ← MUST match MainActivity.kt package!
    compileSdk = flutter.compileSdkVersion
    ndkVersion = flutter.ndkVersion

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = JavaVersion.VERSION_17.toString()
    }

    defaultConfig {
        applicationId = "com.jahfali.hermex_android"
        minSdk = 26
        targetSdk = 34
        versionCode = flutter.versionCode
        versionName = flutter.versionName
    }

    buildTypes {
        debug {
            isDebuggable = true
            applicationIdSuffix = ".debug"
        }
        release {
            isDebuggable = false
            isMinifyEnabled = false  // OFF if Isar in pubspec.yaml
            isShrinkResources = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            signingConfig = signingConfigs.getByName("debug")
        }
    }
}

flutter {
    source = "../.."
}
```

---

## 5. Network Security Config — LL-027 CRITICAL

### The Rule

For apps connecting to local Hermes servers via HTTP:

```xml
<!-- android/app/src/main/res/xml/network_security_config.xml -->
<network-security-config>
    <!-- Permit cleartext for local servers — Dart validates RFC 1918 only -->
    <base-config cleartextTrafficPermitted="true">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>
</network-security-config>
```

**Why:** Android's `<domain>` element does NOT support CIDR notation. If you whitelist specific IPs (192.168.1.1, 192.168.0.1), any other private IP (192.168.8.80, 10.0.0.50) is silently blocked. The connection times out with zero network activity reaching the server.

**LL-027:** 2+ hours lost debugging macOS firewall, port binding, gateway restarts — the actual bug was `cleartextTrafficPermitted="false"` in base-config blocking 192.168.8.80.

```yaml
name: Build APK
on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Android Preflight Check
        run: bash scripts/android-preflight.sh
      
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.41.6'
          channel: 'stable'
          cache: true
      
      - run: flutter pub get
      - run: flutter analyze
      - run: flutter test
      - run: flutter build apk --release
      
      - name: Publish to Releases
        uses: softprops/action-gh-release@v2
        with:
          tag_name: latest
          name: "Latest APK Build"
          files: build/app/outputs/flutter-apk/app-release.apk
          make_latest: true
```

---

## 6. Common Failures — Quick Reference

| Symptom | Cause | Fix |
|---------|-------|-----|
| App crashes before splash | `namespace` ≠ `MainActivity` package | Match them — run preflight check |
| App crashes on first DB call | `isMinifyEnabled = true` + Isar | Set to false or add keep rules |
| `package` attribute error in CI | AGP 8.8+ rejects isar_flutter_libs manifest | Add gradle.projectsEvaluated hook |
| `flutter pub get` fails in CI | Flutter version mismatch | Match CI flutter-version to local |
| 403 on release publish | Missing `contents: write` | Add permissions block |
| `ClassNotFoundException` | See row 1 — namespace mismatch | Preflight Gate 1 |
| Phone times out connecting to server | Android blocks cleartext HTTP to private IP (LL-027) | Set base-config cleartext=true + usesCleartextTraffic |
| curl localhost:8642 works but phone can't connect | macOS firewall blocks Python binary (LL-028) | Add Python to firewall: `sudo socketfilterfw --add` |
| Static method fix in Dart doesn't take effect after hot reload | Hot reload doesn't propagate static method changes across compilation units (LL-030) | `flutter clean && flutter run` — full rebuild required; never trust `r`/`R` for static method edits |
| Tailscale/CGNAT IPs (100.64.x.x) rejected as "not local" | `isLocalNetwork()` only checks RFC 1918, not 100.64.0.0/10 | Add `_isTailscaleOrCGNAT()` checking second octet 64-127 — see `references/is-local-network-validation.md` |
| `AAPT: error: resource android:attr/lStar not found` (release only) | Isar 3.1.0 targets AGP 4.2; `lStar` resource attribute unresolved under AGP 8.8+ | Isar 3.1.0 fundamentally incompatible with AGP 8.8+. Defer Isar — do NOT patch pub-cache. See `flutter-isar-clean-arch-setup` §16d |
| All HTTP calls fail: `Failed host lookup (OS Error: No address associated with hostname, errno = 7)` | Missing `<uses-permission android:name="android.permission.INTERNET"/>` in AndroidManifest.xml | Add INTERNET permission. Flutter's debug manifest auto-adds it, but the release manifest does NOT on all platforms. Some OEM ROMs (Tecno HiOS, Transsion) enforce normal permissions strictly — without explicit INTERNET, DNS resolution is blocked for that app system-wide. Build succeeds, app launches, every network call fails instantly with errno 7. |
| `flutter build appbundle` fails: "Invalid dex file indices, expecting classes٢.dex but found classes2.dex" | **Arabic-Indic numerals (٠-٩) in D8/R8 dex filenames** — Java/JVM on macOS with `ar_SA` locale formats number strings using Eastern Arabic digits, but AGP's bundletool expects ASCII (0-9) | See §12 AAB Build + Arabic Locale Fix — requires Gradle cache purge + `LC_ALL=C` + `JAVA_TOOL_OPTIONS` env vars. **APK builds work fine** — this only affects AAB (App Bundle). |

---

## 7. macOS Firewall — LL-028 CRITICAL

### The Problem

macOS Application Firewall (`socketfilterfw`) blocks incoming connections to Python binaries it doesn't recognize. Hermes uses Python from uv's cache path which is NOT in the default firewall allow list.

### Symptoms
- `curl localhost:8642` → 200 ✓
- Phone/external → 192.168.x.x:8642 → timeout ✗  
- `lsof -i :8642` shows `*:8642` (correctly bound)
- But external connections silently dropped at OS level

### Fix
```bash
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add \
  ~/.local/share/uv/python/cpython-3.11*-macos-aarch64-none/bin/python3.11
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp \
  ~/.local/share/uv/python/cpython-3.11*-macos-aarch64-none/bin/python3.11
```
Or GUI: System Settings → Network → Firewall → Options → + → add Python binary.

### Prevention
After any `hermes update` or Python upgrade, verify the new binary is allowed. The path changes with each Python patch version.

---

## 8. Bash Portability — set -e + Arithmetic (CI)

### Pitfall
```bash
set -euo pipefail
PASS=0
((PASS++))  # GNU bash: 0++ = 0 (false) → exit 1 → set -e kills script
```
GNU bash (Ubuntu CI) and macOS bash handle arithmetic exit codes differently.

### Fix
```bash
_inc() { eval "$1=\$((\${$1} + 1))"; }
_inc PASS  # Always returns exit 0
```
Never use `((VAR++))` with `set -e` in portable scripts.

## 9. Dart/Riverpod State Mutation — LL-029

When building chat/message history in Riverpod providers:

```dart
// ❌ WRONG: history snapshot taken AFTER mutation → duplicate messages
state = state.copyWith(messages: [...state.messages, userMessage]);
final history = _buildHistory();  // contains the just-added userMessage!

// ✅ RIGHT: snapshot BEFORE mutation
final history = _buildHistory();  // only previous messages
state = state.copyWith(messages: [...state.messages, userMessage]);
```

**This causes:** Two consecutive `role: user` messages in API requests → Hermes API rejects (strict alternation enforcement).

**Prevention:** Unit test verifying exactly one `role: user` per send. PR checklist: "Does state.copyWith() precede a history snapshot?"

---

## 7. Preflight Verification (run before every build)

```bash
#!/bin/bash
# scripts/android-preflight.sh
# MoA-audited: LL-024, LL-025 enforcement

set -e
echo "=== Android Preflight Verification ==="

# Gate 1: namespace == MainActivity.kt package
NS=$(grep -oP 'namespace\s*=\s*"\K[^"]+' android/app/build.gradle.kts 2>/dev/null || echo "")
PKG=$(find android/app/src/main/kotlin -name "*.kt" -exec grep -oP '^package\s+\K\S+' {} \; 2>/dev/null || echo "")
if [ -z "$NS" ] || [ -z "$PKG" ]; then
    echo "❌ GATE 1 FAILED: Cannot extract namespace or package"
    exit 1
fi
if [ "$NS" != "$PKG" ]; then
    echo "❌ GATE 1 FAILED: namespace='$NS' ≠ package='$PKG'"
    echo "   Fix: Make namespace in build.gradle.kts match MainActivity.kt package."
    exit 1
fi
echo "✅ Gate 1: namespace == package ($NS)"

# Gate 2: Isar + isMinifyEnabled
if grep -q 'isar:' pubspec.yaml 2>/dev/null; then
    if grep -q 'isMinifyEnabled\s*=\s*true' android/app/build.gradle.kts 2>/dev/null; then
        echo "❌ GATE 2 FAILED: Isar detected + isMinifyEnabled=true"
        echo "   Fix: Set isMinifyEnabled=false or add -keep rules from isar.dev."
        exit 1
    fi
    echo "✅ Gate 2: Isar + ProGuard compatible (isMinifyEnabled=false)"
fi

# Gate 3: applicationId consistency
APP_ID=$(grep -oP 'applicationId\s*=\s*"\K[^"]+' android/app/build.gradle.kts 2>/dev/null || echo "")
if [ -n "$APP_ID" ] && [ "$APP_ID" != "$NS" ]; then
    echo "⚠️  Gate 3 WARNING: applicationId='$APP_ID' ≠ namespace='$NS'"
    echo "   Valid but unusual. Verify intent."
else
    echo "✅ Gate 3: applicationId consistent"
fi

# Gate 4: AGP + isar_flutter_libs compat
if grep -q 'isar_flutter_libs' pubspec.yaml 2>/dev/null; then
    if ! grep -q 'gradle.projectsEvaluated' android/build.gradle.kts 2>/dev/null; then
        echo "❌ GATE 4 FAILED: isar_flutter_libs detected but no AGP 8.8+ compat hook"
        echo "   Fix: Add gradle.projectsEvaluated block from flutter-android-build-system §3."
        exit 1
    fi
    echo "✅ Gate 4: isar_flutter_libs AGP compat hook present"
fi

echo ""
echo "=== ALL GATES PASSED — Safe to build ==="
```

---

## Sources (MoA-Verified)
- https://developer.android.com/build/gradle-build-overview
- https://isar.dev (ProGuard keep rules for Isar)
- https://docs.flutter.dev/deployment/android
- https://developer.android.com/build/releases/past-releases (AGP release notes)

## 10. Dart-Side HTTP Validation — isLocalNetwork() Pattern (LL-030)

### The Pattern

For apps connecting to servers with user-provided URLs, enforce HTTP-only-on-local-network at the Dart level (complementing `network_security_config.xml`):

```dart
static bool isLocalNetwork(String url) {
  final uri = Uri.tryParse(_normalizeUrl(url));
  if (uri == null) return false;
  final host = uri.host.toLowerCase();

  if (host == 'localhost' || host == '127.0.0.1') return true;
  if (host.startsWith('192.168.')) return true;
  if (host.startsWith('10.')) return true;
  if (host.startsWith('172.') && _isPrivate172(host)) return true;
  // Tailscale / CGNAT: 100.64.0.0/10
  if (host.startsWith('100.') && _secondOctetBetween(host, 64, 127)) return true;
  return false;
}
```

**Key ranges:**
- RFC 1918: 192.168.0.0/16, 10.0.0.0/8, 172.16.0.0/12
- Tailscale/CGNAT: 100.64.0.0/10 (second octet 64–127)

### Anti-Pitfall: Duplicated _validateUrl()

Do NOT duplicate the validation logic in both the UI form validator and the repository layer. One static `validateUrl()` method on the repository, called by both:

```dart
// ✅ Right: UI delegates to repository
String? _validateUrl(String? value) {
  return ServerRepository.validateUrl(value?.trim() ?? '');
}

// ❌ Wrong: copy-pasted validation logic in ConnectionScreen AND ServerRepository
```

Duplication caused a real bug where the repository's `isLocalNetwork()` was fixed but the UI validator appeared stale — actually a hot-reload build-cache issue (see §6 Quick Reference), but the structural duplication made debugging harder.

See `references/is-local-network-validation.md` for the full audit trace including all call sites and test cases.

## 11. Dart HttpClient + UTF-8 Encoding (SSE/REST)

### Pitfall: `request.write()` on Android with non-ASCII

`HttpClientRequest.write(String)` fails on some Android versions when the body contains non-ASCII characters (Arabic, CJK, emoji). Error: `Invalid argument (string): Contains invalid characters`.

**Fix — use bytes, not strings:**
```dart
// Fails on Android:
request.write(jsonEncode(body));

// Always works:
request.headers.set('Content-Type', 'application/json; charset=utf-8');
final bodyBytes = utf8.encode(jsonEncode(body));
request.contentLength = bodyBytes.length;
request.add(bodyBytes);
```
This applies to SSE streaming (`sse_client.dart`) and any REST client using `dart:io` HttpClient.

## 12. AAB Build + Play Store Submission (LL-034)

### The Arabic-Indic Numeral Problem

On macOS with Arabic locale (`ar_SA`), `flutter build appbundle --release` fails with:

```
FAILURE: Invalid dex file indices, expecting file 'classes٢.dex' but found 'classes2.dex'
```

**Root cause:** Java's `String.format("%d", ...)` and `Integer.toString()` respect the system locale. On `ar_SA`, numbers are formatted with Arabic-Indic digits (٠١٢٣٤٥٦٧٨٩). D8/R8 generates `.dex` files with these numerals, but AGP's bundletool expects ASCII digits (0-9).

The error direction (٢→2 vs 2→٢) depends on which build step cached which numeral style first. Both directions have been observed.

**Why APK works but AAB fails:** `flutter build apk` uses a different packaging pipeline (`apkbuilder`) that is locale-agnostic. Only `bundleRelease` → `bundletool` triggers the mismatch.

### Fix (Three Steps — ALL Required)

```bash
# 1. Purge stale Gradle cache with wrong-numeral dex files
rm -rf build android/.gradle android/app/build

# 2. Force C locale (ASCII) for shell, AND English locale for JVM
LC_ALL=C JAVA_TOOL_OPTIONS="-Duser.language=en -Duser.country=US" \
  flutter build appbundle --release

# 3. Verify
ls -lh build/app/outputs/bundle/release/app-release.aab
```

**On CI (Ubuntu):** Not affected — CI always runs with `LANG=C.UTF-8` or `en_US.UTF-8`. This is a macOS + Arabic-locale-specific issue.

### Version Code Management

Play Store requires monotonically increasing `versionCode`. Best practice: manage in one place:

```kotlin
// android/app/build.gradle.kts
defaultConfig {
    versionCode = flutter.versionCode   // reads from pubspec.yaml
    versionName = flutter.versionName
}
```

```yaml
# pubspec.yaml — single source of truth
version: 0.2.0+6   # +6 = versionCode
```

### Play Store Checklist

See `references/playstore-submission-checklist.md` for the full submission workflow including:
- Privacy policy hosting (GitHub Pages from `/docs`)
- AAB upload vs APK
- Store listing asset requirements (screenshots, feature graphic, icon)
- Content rating questionnaire
- Data safety section
- App signing key backup
