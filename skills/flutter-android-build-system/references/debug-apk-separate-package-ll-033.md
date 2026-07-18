# Debug APK Installs as Separate Package (LL-033)

## When This Bites
You build a debug APK (`flutter build apk --debug`), run `adb install -r`, get "Success", but the user opens the app and sees old code — no changes applied. You check `dumpsys package com.app | grep lastUpdateTime` and it shows an old timestamp.

## Root Cause
The project's `build.gradle.kts` has `applicationIdSuffix = ".debug"` in the debug build type. This means:

| Build type | Package name | Installs as |
|-----------|-------------|------------|
| Release | `com.jahfali.hermex_android` | Main app |
| Debug | `com.jahfali.hermex_android.debug` | **Separate app** |

`adb install -r` replaces the debug app, but the user's launcher icon opens the **release** app by default. They never see your changes.

## Detection
```bash
# List both packages
adb shell pm list packages | grep hermex
# Output: com.jahfali.hermex_android (release — user opens this)
#         com.jahfali.hermex_android.debug (debug — your build)

# Check debug package timestamp
adb shell dumpsys package com.jahfali.hermex_android.debug | grep lastUpdateTime
# Should show fresh timestamp — confirms install succeeded
```

## Fix Options

### Option A: Build release APK (preferred for device testing)
```bash
flutter build apk --release
adb install -r build/app/outputs/flutter-apk/app-release.apk
# Now verify the MAIN app timestamp:
adb shell dumpsys package com.jahfali.hermex_android | grep lastUpdateTime
```

### Option B: Tell user to open debug variant
Tell the user: "Your launcher now has TWO Hermex icons. The one with the debug ribbon/badge is the updated version." This is error-prone — most users won't switch.

### Option C: Remove the suffix temporarily
Comment out `applicationIdSuffix = ".debug"` in `build.gradle.kts`, rebuild debug. **Do NOT commit this change.**

## Hermex-Specific History
- 2026-07-16: Two consecutive "adb install success but app unchanged" incidents. First with release APK (router fix — installed correctly), second with debug APK (session title fix — installed as separate com.jahfali.hermex_android.debug). User opened the release app and reported "ما ثبت التطبيق."
