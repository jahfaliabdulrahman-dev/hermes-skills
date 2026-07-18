#!/usr/bin/env python3
"""Render an HTML card to an exact-size PNG with headless Chrome, and measure
whether its content survives platform cropping.

Why a browser instead of an image library: Pillow cannot shape complex scripts
(Arabic, Persian, Urdu, Hindi, Thai) unless built with `raqm` — letters come
out disconnected and in the wrong direction. A browser shapes text correctly,
handles RTL, and gives you real CSS. For a card that carries a brand's name in
its own script, that difference is the whole job.

Social platforms crop preview cards, so anything meaningful should sit ~40pt
(≈53px at 1280 wide) from every edge. This measures the actual content bounds
via edge detection — which works over gradients, unlike a flat colour test —
and reports the true margins.

CONTRACT — what this tool does and does not promise:
  Checks (mechanical): exact dimensions, under 1 MB, the file is FRESH (a failed
  render can't leave last run's image behind to "pass"), and luminance-contrasting
  content clears the safe zone. These are things eyes are bad at — you cannot
  eyeball 49px vs 53px, and the crop it guards against hasn't happened yet.
  Will NOT check: whether the card looks good, or content that contrasts only in
  hue (the margin scan is luminance-based). Open the PNG and look — this reports
  geometry, not taste.

Usage:
    python3 render_card.py card.html -o card.png
    python3 render_card.py card.html -o card.png --width 1280 --height 640
    python3 render_card.py card.html -o card.png --ignore-bottom 10

Requires: Pillow, and Google Chrome installed.
"""

import argparse
import os
import subprocess
import sys

try:
    from PIL import Image, ImageChops, ImageFilter
except ImportError:
    sys.exit("Pillow is required:  pip install Pillow")

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome", "chromium", "chromium-browser",
]


def find_chrome(explicit=None):
    if explicit:
        from shutil import which
        resolved = explicit if os.path.isfile(explicit) else which(explicit)
        if not resolved:
            sys.exit(f"--chrome {explicit!r} is not an executable that exists.")
        return resolved
    for c in CHROME_CANDIDATES:
        if os.path.isfile(c):
            return c
        from shutil import which
        if which(c):
            return which(c)
    sys.exit("Chrome/Chromium not found — pass --chrome /path/to/chrome")


def render(chrome, html_path, out_path, width, height):
    url = "file://" + os.path.abspath(html_path)
    out_abs = os.path.abspath(out_path)

    # Delete any previous render BEFORE invoking Chrome. The workflow this
    # script exists for is iterative — render, tweak the CSS, render again to
    # the same path — so a stale file at the target is the normal state, not an
    # edge case. Without this, a Chrome failure leaves last run's image in
    # place and every check below happily "verifies" an image we never made.
    if os.path.exists(out_abs):
        os.unlink(out_abs)

    cmd = [
        chrome, "--headless", "--disable-gpu", "--hide-scrollbars",
        "--allow-file-access-from-files",
        f"--screenshot={out_abs}",
        f"--window-size={width},{height}",
        url,
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
    except OSError as e:
        sys.exit(f"Could not run {chrome!r}: {e}")
    if proc.returncode != 0:
        sys.exit(f"Chrome exited {proc.returncode} — nothing rendered.\n"
                 f"{proc.stderr[-800:]}")
    if not os.path.exists(out_abs):
        sys.exit(f"Chrome reported success but produced no file.\n{proc.stderr[-800:]}")


# FIND_EDGES has no neighbouring pixels to work with at the image perimeter,
# so it fabricates a bright frame there (measured: ~29-48, i.e. above the
# content threshold, while true background 2px inland reads 0-9). Without
# discarding that ring, every card looks like content touches all four edges.
FILTER_BORDER = 2


def content_margins(img, ignore_edges):
    """Locate real content via edge energy.

    Text and logos create strong local gradients; a smooth background gradient
    creates almost none (measured on a real card: gradient peaks at 15, text
    at 255). That makes this robust on dark, light, or gradient cards without
    needing to know the background colour.
    """
    W, H = img.size
    # Edge-detect per channel and keep the strongest, rather than greyscaling
    # first: a colour that differs in hue but matches in brightness (bright red
    # on mid-grey) collapses to a flat tone in greyscale and becomes invisible
    # to the check — while being perfectly legible in the actual card.
    channels = [c.filter(ImageFilter.FIND_EDGES) for c in img.convert("RGB").split()]
    combined = ImageChops.lighter(ImageChops.lighter(channels[0], channels[1]),
                                  channels[2])
    mask = combined.point(lambda p: 255 if p > 30 else 0)

    top_i, right_i, bottom_i, left_i = ignore_edges
    top_i = max(top_i, FILTER_BORDER)
    right_i = max(right_i, FILTER_BORDER)
    bottom_i = max(bottom_i, FILTER_BORDER)
    left_i = max(left_i, FILTER_BORDER)

    region = mask.crop((left_i, top_i, W - right_i, H - bottom_i))
    box = region.getbbox()
    if not box:
        return None
    x0, y0, x1, y1 = box
    x0 += left_i; x1 += left_i
    y0 += top_i;  y1 += top_i
    return {
        "bbox": (x0, y0, x1, y1),
        "left": x0, "right": W - x1,
        "top": y0, "bottom": H - y1,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=640)
    ap.add_argument("--safe-pt", type=float, default=40.0,
                    help="safe-zone in points (default 40). GitHub's own social-"
                         "preview upload dialog states: 'We recommend leaving a "
                         "40pt border around the important details of your social "
                         "card to make sure nothing gets cropped.' 40pt x 96/72 "
                         "= 53px at 1280 wide.")
    ap.add_argument("--chrome", help="explicit Chrome/Chromium path")
    ap.add_argument("--ignore-top", type=int, default=0)
    ap.add_argument("--ignore-right", type=int, default=0)
    ap.add_argument("--ignore-bottom", type=int, default=0,
                    help="px to ignore for a deliberate full-bleed element (e.g. an "
                         "accent bar). Give it the element's height PLUS ~2px: the "
                         "line where it meets the background is itself a strong edge "
                         "spanning the full width, and will otherwise read as content.")
    ap.add_argument("--ignore-left", type=int, default=0)
    args = ap.parse_args()

    chrome = find_chrome(args.chrome)
    render(chrome, args.html, args.output, args.width, args.height)

    img = Image.open(args.output).convert("RGB")
    if img.size != (args.width, args.height):
        print(f"\u26a0 rendered {img.size}, expected ({args.width}, {args.height})")

    # 40pt is defined against a 1280-wide card; scale if the card differs.
    safe_px = int(args.safe_pt * (args.width / 1280) * (4 / 3))

    m = content_margins(img, (args.ignore_top, args.ignore_right,
                              args.ignore_bottom, args.ignore_left))
    size_kb = os.path.getsize(args.output) / 1024

    print(f"written   : {args.output}  {img.size[0]}x{img.size[1]}  {size_kb:.0f} KB")

    oversize = size_kb > 1024
    if oversize:
        print("\u2717 over 1 MB — GitHub rejects social previews above that")

    if not m:
        print("no content detected — is the card blank?")
        return 1

    print(f"content   : {m['bbox']}")
    print(f"margins   : left {m['left']}px  right {m['right']}px  "
          f"top {m['top']}px  bottom {m['bottom']}px")
    print(f"safe zone : {safe_px}px ({args.safe_pt}pt)")

    # The invariant: ANY ignore band of N > 0 means the outer N px of that edge
    # were never examined, so "all content clears" is a claim this cannot make —
    # regardless of how N compares to the safe zone. (An earlier version only
    # warned when N >= safe_px, which merely moved the false pass to N = safe_px
    # - 1: text 16px from the edge still got a confident ✓ under N=52.)
    ignored = {"top": args.ignore_top, "right": args.ignore_right,
               "bottom": args.ignore_bottom, "left": args.ignore_left}
    unchecked = [k for k, v in ignored.items() if v > 0]
    for k in unchecked:
        covers = " — that spans the entire safe zone" if ignored[k] >= safe_px else ""
        print(f"\u26a0 {k:<6}  : outer {ignored[k]}px NOT examined (--ignore-{k}){covers}."
              f"\n           Anything you placed in that band is unverified.")

    tight = [k for k in ("left", "right", "top", "bottom") if m[k] < safe_px]
    if tight:
        print(f"\u2717 too close to the edge: {', '.join(tight)} — content may be cropped")
        return 1

    scope = ("all content" if not unchecked
             else f"content outside the ignored {'/'.join(unchecked)} band"
                  f"{'s' if len(unchecked) > 1 else ''}")
    print(f"{'\u2713' if not oversize else '~'} {scope} clears the safe zone")
    print("\u2192 open the PNG and look — this reports geometry, not whether it looks good.")
    return 1 if oversize else 0


if __name__ == "__main__":
    sys.exit(main())
