# Tecno HiOS — INTERNET Permission Enforcement

> **Source:** Azdal (2026-07-12) — device testing on Tecno LJ7 (HiOS)
> **Bug:** App built and launched but ALL network calls (Gemini + Supabase) failed with DNS `errno = 7`
> **Root cause:** `AndroidManifest.xml` missing `<uses-permission android:name="android.permission.INTERNET"/>`

---

## Background

Android `INTERNET` is a **normal** permission (protection level: `normal`). Per Android documentation, normal permissions are granted automatically at install time on Android 6.0+ (API 23+). Most OEMs honor this. Transsion's HiOS (Tecno, Infinix, Itel) does NOT — it enforces all permissions strictly regardless of protection level.

## Reproduction

1. Any Flutter app without explicit `<uses-permission android:name="android.permission.INTERNET"/>` in `AndroidManifest.xml`
2. Built and installed on Tecno/Infinix/Itel device running HiOS
3. Any HTTP/HTTPS call fails with `SocketException: Failed host lookup` (`errno = 7`)
4. Wi-Fi and mobile data confirmed working (browser loads websites)
5. `adb logcat` shows identical `errno = 7` for ALL hostnames

## The fix

```xml
<!-- android/app/src/main/AndroidManifest.xml -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <!-- Required for network access on Transsion HiOS devices -->
    <uses-permission android:name="android.permission.INTERNET"/>
    <!-- ... -->
</manifest>
```

## How to detect without a Tecno device

Look for this pattern in logcat:
```
Failed host lookup: '<hostname1>' (OS Error: No address associated with hostname, errno = 7)
Failed host lookup: '<hostname2>' (OS Error: No address associated with hostname, errno = 7)
```

If TWO OR MORE unrelated hostnames fail with identical `errno = 7` in the same session → OS-level denial. Single-host DNS failure could be the host itself being down; multi-host is a permission issue.

## Prevention checklist

- [ ] `INTERNET` permission explicitly declared in main AndroidManifest.xml
- [ ] `ACCESS_NETWORK_STATE` declared for connectivity detection
- [ ] Manifest tested on at least one Transsion device (Tecno, Infinix, Itel)
- [ ] CI includes INTERNET permission presence check: `grep -q "android.permission.INTERNET" android/app/src/main/AndroidManifest.xml`

## Related lessons

- **Pattern 11:** Official Android Sources Mandatory (namespace, ProGuard, AGP — same class: Android OS details Flutter devs miss)
- **Pattern 9:** Android Namespace = MainActivity Package (another OS-level detail)
- **LL-024, LL-025:** hermex_android build failures — same class of Android-specific gaps
