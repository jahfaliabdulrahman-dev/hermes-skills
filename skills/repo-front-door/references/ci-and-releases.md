# CI and Releases

Read this when fixing red CI or automating a downloadable build. Examples are
Flutter/Android because that's where these were learned, but the failure modes
are toolchain-agnostic — the same three traps show up in Node, Python, and Go.

## Contents

- [Why CI is red](#why-ci-is-red)
- [A CI workflow that means something](#a-ci-workflow-that-means-something)
- [Build and publish a downloadable artifact](#build-and-publish-a-downloadable-artifact)
- [The rolling-tag trap](#the-rolling-tag-trap)
- [Secrets](#secrets)
- [Verifying from outside](#verifying-from-outside)

## Why CI is red

Diagnose before changing anything. Pull the actual failing log rather than
guessing from the job name:

```bash
gh run list --limit 15
gh run view <run-id> --log > /tmp/ci.log
tail -40 /tmp/ci.log
```

Note how long it's been failing (`gh run list` shows dates). "Red since July 13"
tells you it's environmental drift, not the last commit.

### Trap 1 — toolchain version drift

CI pinned to an older SDK than the dev machine produces errors that exist only
in CI. Always compare the two:

```bash
flutter --version                        # local
grep -rn "flutter-version\|node-version\|python-version" .github/workflows/
```

Real case: `Color.withValues()` needs Flutter 3.27+; the dev ran 3.44.6 and CI
was pinned to 3.24 → 5 `undefined_method` errors, invisible locally, red CI for
three days.

Pin CI to the version you actually build with. A CI testing a different
toolchain than you ship is testing fiction — it will both miss real breakage and
invent fake breakage.

### Trap 2 — linters exit non-zero on advisory findings

`flutter analyze` exits 1 on *any* finding, including info-level style hints. So
after fixing every real error, CI stays red because of `prefer_const`
suggestions. The finding count won't tell you — check the exit code:

```bash
flutter analyze; echo "exit: $?"                    # 1, even with 0 errors
flutter analyze --no-fatal-infos; echo "exit: $?"   # 0
```

Make advisory findings non-blocking, but **fix real warnings rather than muting
them**. If you silence warnings too, green stops carrying information and the
next real bug ships quietly. The point isn't a green badge — it's a badge that
means something.

Equivalents: ESLint `--max-warnings=N`, `ruff check` severity config,
`golangci-lint` severity rules.

## A CI workflow that means something

Green should mean "compiles + analyzes clean + tests pass", not "lints ok".
Tests usually run without credentials — verify locally first.

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  analyze-and-test:
    name: Analyze & Test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.44.6'   # must match local — see Trap 1
          channel: 'stable'
      - run: flutter pub get
      - run: flutter analyze --no-fatal-infos
      - run: flutter test
```

Keep the file path stable when rewriting a workflow. GitHub keys workflows by
path, so renaming `lint.yml` → `ci.yml` orphans the old entry in the Actions tab
(it lingers with no new runs) and adds a second one. Updating the file's contents
and its internal `name:` updates the existing entry in place — a cleaner Actions
tab for whoever is looking at it, which is the whole point.

## Build and publish a downloadable artifact

Automating the build is what stops the download from drifting from the code.
Trigger on push to main so every merge refreshes it, plus manual dispatch.

```yaml
name: Build APK

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: write        # needed to push the tag and upload the asset

jobs:
  build:
    name: Build Release APK
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '17'

      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.44.6'
          channel: 'stable'

      - run: flutter pub get

      - name: Reconstruct .env from secrets
        run: |
          {
            echo "SUPABASE_URL=${{ secrets.SUPABASE_URL }}"
            echo "SUPABASE_ANON_KEY=${{ secrets.SUPABASE_ANON_KEY }}"
            echo "GEMINI_API_KEY=${{ secrets.GEMINI_API_KEY }}"
          } > .env

      - name: Build release APK
        run: flutter build apk --release --dart-define-from-file=.env

      - name: Point the "latest" tag at this commit
        run: |
          git tag -f latest "$GITHUB_SHA"
          git push -f origin latest

      - name: Publish to the "latest" release
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          gh release upload latest \
            build/app/outputs/flutter-apk/app-release.apk \
            --clobber
```

Before assuming a release build needs signing setup, check — many projects sign
release with the debug key, which produces a perfectly installable sideload APK
and needs no keystore secrets:

```bash
grep -n "signingConfig" android/app/build.gradle.kts
```

**The rolling release has to exist before anything can upload to it.**
`gh release upload latest …` fails on a repo that has never had one, so the first
run needs it created once — by hand, or defensively in the workflow:

```bash
gh release create latest --title "Latest build" --notes "Automatically built." \
  || true    # already exists — fine
```

### The permanent download URL

GitHub always serves the newest release's asset here:

```
https://github.com/OWNER/REPO/releases/latest/download/<asset-name>
```

Put that in the README. It never needs updating — no versioned links, no
maintenance, no stale-link risk when someone shares it months later.

## The rolling-tag trap

**`gh release upload latest <file> --clobber` swaps the asset but does not move
the git tag.** The release keeps advertising whatever commit the tag was first
cut from. You end up with a current artifact on a page claiming a commit from
days ago — and a reviewer who notices loses trust in everything else on the page.

The fix is the tag step in the workflow above. To verify tag and HEAD agree:

```bash
gh api repos/OWNER/REPO/git/refs/tags/latest --jq '.object.sha'
git rev-parse HEAD
```

To repair an already-stale tag by hand:

```bash
git fetch origin --tags
git tag -f latest <correct-sha>
git push origin latest --force
```

Moving a tag doesn't detach or delete its release — the release follows the tag
name, so the displayed commit updates. Tag pushes won't retrigger these
workflows either (they trigger on branch pushes), so there's no loop.

## Secrets

Set them from the local env file rather than pasting values through a chat or
shell history:

```bash
grep '^SUPABASE_URL=' .env | cut -d= -f2- | gh secret set SUPABASE_URL
gh secret list
```

Tell the user which secrets you set and why. Be accurate about exposure rather
than alarming or hand-waving: if a key is already compiled into a public
artifact (a deliberate, documented trade-off in many client-side apps), then
putting it in Actions secrets is strictly *safer* than the status quo — secrets
never appear in logs. Say that plainly; don't smuggle it past them, and don't
inflate it either.

## Verifying from outside

Watch the run to completion instead of pushing and hoping:

```bash
gh run watch <run-id> --exit-status
```

Then confirm the artifact is genuinely reachable and is what it claims to be:

```bash
curl -sIL "https://github.com/OWNER/REPO/releases/latest/download/app-release.apk" \
  | grep -iE "^HTTP/2 200|content-type|content-length"
# want: 200, content-type: application/vnd.android.package-archive, sane length
```

A useful sanity check on your own verification: run it once against a
deliberately wrong URL (misspell the owner) and confirm it 404s. A check that
passes on nonsense isn't a check.

Finally, compare the asset's `updatedAt` against the run time to prove the file
came from CI rather than an old manual upload:

```bash
gh release view latest --json assets --jq '.assets[] | {name, size, updatedAt}'
```
