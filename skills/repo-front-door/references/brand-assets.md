# Brand Assets

Read this when producing an avatar, a social preview card, or any image
containing non-Latin text.

## Contents

- [Which asset do they actually mean?](#which-asset-do-they-actually-mean)
- [The avatar](#the-avatar)
- [The social preview card](#the-social-preview-card)
- [Complex scripts and RTL](#complex-scripts-and-rtl)
- [What you cannot automate](#what-you-cannot-automate)

## Which asset do they actually mean?

"The repo logo" is ambiguous and the two options behave very differently. Ask,
or infer from what they're doing:

| | Account avatar | Social preview |
|---|---|---|
| Where it shows | Beside the repo name, and on the profile | When the link is shared (WhatsApp, Slack, X) |
| Scope | **Every repo on the account**, plus the profile | That one repo only |
| Size | Square, 500px+ | 1280×640 |
| Set via | `github.com/settings/profile` | Repo Settings → General → Social preview |

If someone is handing a **link** to judges or investors, the social preview is
usually what they actually want — it's the thing that renders in the chat where
they paste it.

Flag the avatar's scope before they upload: it changes *every* repo on that
account and their profile page. People routinely don't realise this. On a
dedicated dev account that's usually fine; on a personal account it may not be.

## The avatar

Use `scripts/make_avatar.py` (path relative to the skill directory — expand it):

```bash
python3 <skill-dir>/scripts/make_avatar.py logo.jpeg -o avatar.png --preview
```

It crops to the mark's measured pixel bounds, pads, resizes, and — the part that
matters — counts how many mark pixels fall outside the inscribed circle. Platforms
mask avatars to circles; a mark that fits the square can still lose its corners.
If it reports clipping, raise `--padding`.

Verify the negative case once so you know the check is real: `--padding 0.0` on a
tall mark should report clipping and exit non-zero.

**Know what the check does and doesn't cover.** It proves nothing gets *sliced*.
It cannot tell you the result is *legible*. Those come apart in one specific way,
and it's the most common one:

- Most brand packs ship a **wide lockup** (symbol + wordmark). Squaring it around
  the long axis yields a thin strip floating in padding — nothing clips, the check
  passes, and the avatar is unreadable at its real display size of ~40px.
- The script warns when the mark exceeds ~2:1 and tells you to re-run with
  `--bbox X0,Y0,X1,Y1` around just the symbol. Take the warning seriously; a
  passing exit code is not the same as a usable avatar.
- **Always look at `--preview`.** It renders the actual circular crop. The
  numbers can't tell you it's ugly.

**The flags you'll actually reach for:**

| Flag | When |
|---|---|
| `--bg "#001F5E"` | The mark is light. On the default white it passes every geometric check and is invisible — the script warns, but pick a contrasting background up front. |
| `--bbox X0,Y0,X1,Y1` | Source is a lockup; crop to the symbol. |
| `--full-bleed` | The artwork already fills the frame (an app-icon tile, no surrounding background). Corner clipping is then expected — the platform's mask is part of the design — so it reports rather than fails. |
| `--tolerance N` | Detection went wrong. Raise it for noisy/JPEG sources, lower it for a low-contrast mark. This is the escape hatch when the "covers N% of the frame" guard fires. |
| `--preview` | Always. |

Design notes:
- At display size an avatar is ~40px. The symbol alone reads; a wordmark won't.
- Prefer a real transparent PNG export over `--bg transparent` on a JPEG. The
  script keys out the background by colour distance and warns when it does, but
  JPEG compression fringes the edges — it's a fallback, not a substitute.
- The mark is found by sampling the corners for the background and keeping what
  differs, so polarity doesn't matter and there's no invert flag to get wrong.
  It fails loudly (rather than silently measuring the background) when the
  detected "mark" covers most of the frame.

## The social preview card

Compose in HTML/CSS, render with headless Chrome (expand the skill path — it
won't resolve from the user's repo):

```bash
python3 <skill-dir>/scripts/render_card.py card.html -o card.png --ignore-bottom 10
```

Start from `assets/social-card-template.html`.

Requirements:
- **1280×640** exactly.
- **Under 1 MB** (GitHub rejects larger). A typical card lands ~300 KB.
- **~40pt safe zone** (≈53px at 1280 wide) — GitHub's upload dialog states this
  outright. Platforms crop cards; anything meaningful inside that margin can
  vanish. `render_card.py` measures the real margins and fails if content
  intrudes — *except* in any band you `--ignore`, which it stops checking and
  says so. Don't hide something you care about in an ignored band.

Two things that will bite you:

**Full-bleed elements.** A deliberate edge-to-edge accent bar is fine — but the
line where it meets the background is itself a strong edge spanning the whole
width, and the safe-zone check will read it as content touching the edge. Pass
`--ignore-bottom <height + 2>` to exclude the element *and* its boundary line.

**The white edge strip.** If only `body` carries the background, a sub-pixel gap
at the viewport edge exposes the default white canvas as a visible strip. Put the
background on `html, body` together.

Verify by *looking at it*, not just by the numbers passing. The first version of
one card had a faint watermark that measured fine but rendered as an ugly bright
rectangle, because the source image had a white background rather than
transparency. Numbers can't catch that; eyes can.

## Complex scripts and RTL

**Pillow cannot shape complex scripts** — Arabic, Persian, Urdu, Hindi, Thai —
unless built with `raqm`. Without it, letters render in isolated forms and in the
wrong direction: recognisably broken to any native reader, and embarrassing on
something shown to judges. Check before trusting it:

```python
from PIL import features
print(features.check('raqm'))    # False → do not draw non-Latin text with PIL
```

When it's `False`, a browser is the right tool: it shapes text correctly, handles
`dir="rtl"`, and gives you real CSS. That's why `render_card.py` drives Chrome
instead of drawing with Pillow.

If you must use Pillow, `arabic-reshaper` + `python-bidi` pre-shape the string —
but don't install packages on someone's machine unasked when a browser they
already have does it properly.

Other notes:
- Bundle the brand font by absolute `file://` path in `@font-face` so the render
  is reproducible and never silently falls back to a system face.
- `white-space: nowrap` on tagline lines stops reflow from pushing text into the
  crop zone at render size.
- **shields.io badges do render non-Latin text.** URL-encode it, then confirm the
  returned SVG contains the right glyphs rather than assuming:
  ```bash
  curl -s "https://img.shields.io/badge/<encoded>-2E7D32?style=for-the-badge" \
    | grep -o "<text[^>]*>[^<]*</text>"
  ```

## What you cannot automate

**GitHub has no API for uploading an account avatar or a repo social preview.**
Both are web-UI only. `PATCH /user` doesn't accept an avatar; there's no social
preview endpoint.

Don't imply you attempted it and hit an error, and don't quietly skip it. State
the limitation, then do everything around it so the human's part is one drag:

1. Generate the file at the exact right size and verify it.
2. Commit it into the repo (e.g. `assets/branding/`) so it's version-controlled
   and easy to find in Finder/Explorer.
3. Give the precise click path and the absolute file path.

- Avatar → `https://github.com/settings/profile` → click the avatar →
  *Upload a photo…*
- Social preview → repo **Settings** → **General** → **Social preview** →
  *Edit* → *Upload an image…*

## Never publish screenshots from a live session

A device mid-demo is logged into a real account. Screenshots will show the
owner's name, email, and — for a finance app — their actual balances and
transactions. That data ends up in a public README forever.

If visuals are needed: capture from a clean guest state, or skip them. For a
chat/conversational product a short **sample conversation** in markdown conveys
the product better than a screenshot anyway, and leaks nothing.
