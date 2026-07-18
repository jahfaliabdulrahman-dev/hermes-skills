---
name: repo-front-door
"description": "Polish repo for outsiders: green CI, download, README, brand."
version: 0.1.0
author: Hermes
platforms: [macos, linux]
metadata:
  hermes:
    tags: [Repo, CI, Release, README, Brand, SocialCard, Avatar]
---

# Repo Front Door

Turn a code repository into a credible front door for outsiders who will judge
the project by its link — hackathon judges, investors, stakeholders, testers.
Covers: making CI genuinely green, automating a downloadable build artifact on a
rolling release, restructuring the README so the download or demo is the hero,
and producing brand assets (square avatar, 1280×640 social preview card,
including non-Latin/RTL text).

Use this skill whenever someone outside the team will evaluate the project from
its repo URL. The pieces travel together: a red ✗ reads as "the app is broken"
to a non-technical evaluator no matter how well the app actually runs.

## When to Use

- "Make the repo look professional"
- "CI is red" or "fix CI"
- "Add a download/release" or "the APK is stale"
- "Update the README" or "README buries the download"
- "Create a logo/avatar/social card for the repo"
- "Getting ready for a demo/hackathon/judge review"
- Any one of the above — they travel together; do all relevant steps

## Prerequisites

- `gh` CLI authenticated (`gh auth status`)
- `flutter` (if Flutter project), or equivalent build tool
- Python 3 with `Pillow` (`pip install Pillow`)
- Google Chrome or Chromium (for social card rendering)
- Repo cloned locally with push access

## How to Run

Work through the six steps in order. Each step's verification protects the next.
Script paths are relative to this skill's directory — expand them with
`python3 ~/.hermes/skills/repo-front-door/scripts/…`.

## Quick Reference

| Step | What | Key Command |
|------|------|-------------|
| 1 | Audit from outside | `gh run list --limit 15`, `gh release view --json ...` |
| 2 | Green CI | Pin toolchain versions, `--no-fatal-infos`, verify exit code |
| 3 | Download artifact | CI workflow → rolling `latest` release, permanent URL |
| 4 | README restructure | Download-first, `<details>` blocks, verify with `gh api /markdown` |
| 5 | Brand assets | `scripts/make_avatar.py`, `scripts/render_card.py` |
| 6 | Flag what's manual | GitHub has no API for avatar/social-preview upload |

Permanent download URL (never changes):
`https://github.com/OWNER/REPO/releases/latest/download/<asset-name>`

## Procedure

### 1. Look at the repo as an outsider first

Before touching anything, gather what a stranger sees:

```bash
gh run list --limit 15
gh release view --json tagName,publishedAt,assets
gh repo view --json owner,description,homepageUrl
```

Read the README top-to-bottom as if you'd never seen the project. Where is the
download? How many scrolls?

Report what you find plainly, including how long a problem has existed.

### 2. Make CI green — and make green mean something

**Trap 1 — toolchain version drift.** CI pinned to an older SDK produces errors
that exist only in CI:

```bash
flutter --version                        # local
grep -rn "version" .github/workflows/   # CI
```

Pin CI to the version actually used to build. A CI testing a different toolchain
than you ship is testing fiction.

**Trap 2 — linters exit non-zero on advisory findings.** `flutter analyze` exits
1 on info-level hints. Verify with:

```bash
flutter analyze --no-fatal-infos; echo "exit: $?"
```

Make advisory findings non-blocking, but **fix real warnings** rather than
muting them.

Add the test suite to CI so green means "compiles + analyzes clean + tests pass":

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
          flutter-version: '3.44.6'
          channel: 'stable'
      - run: flutter pub get
      - run: flutter analyze --no-fatal-infos
      - run: flutter test
```

Keep the workflow file path stable — renaming `lint.yml` → `ci.yml` orphans the
old entry in the Actions tab.

If CI genuinely can't go green in time, add an honest one-line note to the
README: "CI currently fails on X; the app builds and runs, see below."

### 3. Guarantee a working download

Automate the build so the artifact can never drift from the code. See
`references/ci-and-releases.md` for the complete workflow.

**The permanent URL:**
```
https://github.com/OWNER/REPO/releases/latest/download/<asset-name>
```

**The tag gotcha:** `gh release upload latest <file> --clobber` swaps the asset
but does NOT move the git tag. Fix: `git tag -f latest "$GITHUB_SHA" && git push
-f origin latest` as part of the build.

First run needs the release created: `gh release create latest --title "Latest
build" --notes "Automatically built." || true`

Verify tag and HEAD agree:
```bash
gh api repos/OWNER/REPO/git/refs/tags/latest --jq '.object.sha'
git rev-parse HEAD
```

### 4. Make the README download-first

Structure: **logo → name → one-line pitch → big download button → everything
else.** The download should be visible without scrolling.

- A shields.io badge wrapped in `<a>` reads as a real button.
- Add a plain text link beside the badge as fallback.
- Push deep docs into `<details>` blocks.
- For chat/conversational products, a sample conversation conveys the idea better
  than screenshots — and leaks nothing.

**Never publish screenshots from a real logged-in session.**

Avoid spaces in asset filenames. Verify the render before pushing:
```bash
gh api --method POST /markdown -f mode=gfm -f text="$(cat README.md)" > /tmp/r.html
```

### 5. Brand assets

Two different things, often confused:

| Asset | Scope | Size |
|--------|-------|------|
| **Account avatar** | Every repo + profile | Square, 500px+ |
| **Social preview** | One repo | 1280×640 |

**Avatar:** Use `scripts/make_avatar.py`. Derives crop from pixels, pads, and
verifies nothing clips under the circular crop platforms apply.

**Social card:** Compose in `assets/social-card-template.html`, render with
`scripts/render_card.py`. Why a browser? Pillow cannot shape complex scripts
(Arabic, Persian, Urdu, Hindi, Thai) unless built with `raqm`. Check:
```bash
python3 -c "from PIL import features; print(features.check('raqm'))"
```

Keep all meaningful content ~40pt (≈53px at 1280 wide) away from edges.
`render_card.py` measures real margins and fails when content intrudes.

### 6. What you cannot automate

**GitHub has no API for uploading an account avatar or a repo social preview.**
Do the part you can: produce a verified file, commit it to the repo, and give
the exact click path:

- Avatar → `https://github.com/settings/profile` → click avatar → *Upload a photo…*
- Social preview → repo **Settings** → **General** → **Social preview** → *Edit* → *Upload an image…*

Flag the scope surprise: the avatar changes **every** repo on that account.

## Verification

Every claim is checkable from outside:

```bash
# Download actually serves the artifact
curl -sIL "https://github.com/OWNER/REPO/releases/latest/download/<asset>" \
  | grep -iE "^HTTP/2 200|content-type|content-length"

# Logo actually resolves from the README's path
curl -s -o /dev/null -w "%{http_code}\n" \
  "https://raw.githubusercontent.com/OWNER/REPO/main/<path>"

# CI actually passes now
gh run watch <run-id> --exit-status
```

Watch a build through to completion rather than pushing and assuming.

## Pitfalls

- **Tag drift:** `gh release upload latest --clobber` updates the asset but not
  the tag. Always move the tag in the build workflow.
- **Workflow rename:** Renaming a workflow file orphans the old entry in the
  Actions tab. Edit the file in place instead.
- **Pillow + non-Latin text:** Pillow renders Arabic/Persian/etc. disconnected
  and backward without `raqm`. Use a browser for text rendering.
- **Avatar scope:** Changing the account avatar changes it for every repo and the
  profile page — alert the user before they upload.
- **Screenshots from live session:** A real device mid-demo exposes the owner's
  name, email, and data. Use guest state or skip screenshots.
- **Spaces in asset filenames:** `logo.jpeg` forces `%20` in references. Use
  hyphenated names.

## Reference files

- `references/ci-and-releases.md` — complete CI + build-and-publish workflows, secrets, tag mechanics
- `references/brand-assets.md` — avatar and social card specs, complex-script rendering, safe zones

## Scripts

- `scripts/make_avatar.py` — logo → square avatar, with circular-crop preview
- `scripts/render_card.py` — HTML → exact-size PNG via headless Chrome, with safe-zone measurement
- `assets/social-card-template.html` — starting point for a social card (RTL-ready)
