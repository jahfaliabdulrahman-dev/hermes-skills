# Play Store Submission Checklist

From hermex_android `playstore/listing.md` — session 2026-07-16.

## Pre-Submission

- [ ] Google Play Developer account created ($25 one-time fee)
- [ ] App signed with release keystore (back up the keystore + passwords!)
- [ ] `versionCode` incremented (≥ previous submission + 1)
- [ ] `versionName` matches semantic version in CHANGELOG

## Build

```bash
# macOS with Arabic locale (MANDATORY env vars for AAB):
rm -rf build android/.gradle android/app/build
LC_ALL=C JAVA_TOOL_OPTIONS="-Duser.language=en -Duser.country=US" \
  flutter build appbundle --release
# Output: build/app/outputs/bundle/release/app-release.aab
```

## Upload to Play Console

1. Go to play.google.com/console
2. Create app → App name, default language, free/paid
3. Upload AAB in "Production" track
4. Fill store listing

## Store Listing Fields

| Field | Notes |
|-------|-------|
| App name | 30 chars max |
| Short description | 80 chars max |
| Full description | 4000 chars max, supports basic HTML |
| App icon | 512×512 PNG, ≤1MB |
| Feature graphic | 1024×500 PNG or JPEG |
| Screenshots | Min 2 phone screenshots (16:9 or 9:16), PNG/JPEG |
| Category | Tools (primary), Productivity (secondary) |
| Privacy policy URL | Must be valid HTTPS URL |
| Website | Optional |
| Email | Required for support contact |

## Privacy Policy

Host via GitHub Pages:
1. Create `docs/privacy.html` in repo
2. Settings → Pages → Source: main branch, `/docs` folder
3. URL: `https://<user>.github.io/<repo>/privacy.html`

Template includes: no data collection statement, local storage only, contact info.

## Content Rating

Complete the questionnaire in Play Console. Expected: **Everyone** (no objectionable content in Hermex).

## Data Safety

- **No data collected** (all data stays on user's server)
- **No data shared** with third parties
- **Encryption in transit:** Yes (HTTPS to user's server)
- **Data deletion:** User clears app storage in Android Settings

## Post-Submission

- First review typically takes 2-7 days
- Subsequent updates: 1-3 days
- Major policy changes may trigger re-review

## Common Rejections

| Issue | Fix |
|-------|-----|
| "Not enough information about app functionality" | Add more detail to description + screenshots |
| "Privacy policy missing or insufficient" | Ensure URL is HTTPS and clearly states data handling |
| "App icon doesn't meet guidelines" | Use 512×512 PNG with transparent background |
| "Target API level too low" | Bump `targetSdk` in build.gradle.kts |
| "Permission not declared" | Add to AndroidManifest.xml with justification |
