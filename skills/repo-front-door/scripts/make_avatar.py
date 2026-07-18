#!/usr/bin/env python3
"""Crop a logo into a square avatar and render a circular-crop preview to look at.

Most brand packs ship a wide logo on a flat background. Avatars are square and
platforms (GitHub, Slack, X) mask them to a circle — so a naive resize squashes
the mark or lets the platform slice its edges.

How it finds the mark: the background is whatever colour the corners are (true of
essentially every logo export), and the mark is everything that differs from it.
That's polarity-agnostic — dark-on-white, white-on-navy, anything-on-anything —
and it compares all three channels, so a colour that only matches in brightness
isn't lost.

CONTRACT — what this tool does and does not promise:
  Checks (mechanical, better done by code than eyes):
    · output is a square PNG at the requested size, written from the region you
      specified
    · the detected mark isn't obviously wrong (near-empty, or the whole frame)
    · --bbox actually fits inside the source
  Will NOT check — because the operator can see, and code guessing at vision is
  where this script used to grow bugs without end:
    · whether the mark clips the circle
    · whether it's visible against the background
    · whether it looks good
  All three of those are answered by opening the preview it always writes. Do
  that. A passing exit code means "file written", nothing more.

Usage:
    python3 make_avatar.py LOGO.png -o avatar.png
    python3 make_avatar.py LOGO.jpeg -o avatar.png --bg "#001F5E"
    python3 make_avatar.py LOGO.png -o avatar.png --bg transparent
    python3 make_avatar.py LOCKUP.png -o avatar.png --bbox 432,99,824,581
    python3 make_avatar.py APP-ICON.png -o avatar.png --full-bleed

Requires: Pillow
"""

import argparse
import sys

try:
    from PIL import Image, ImageChops, ImageDraw
except ImportError:
    sys.exit("Pillow is required:  pip install Pillow")

MARK_CUTOFF = 8        # alpha/mask value above which a pixel counts as mark
LOCKUP_ASPECT = 2.0    # longer:shorter than this and it isn't just a symbol


def parse_color(value):
    """Accept '#RRGGBB', 'R,G,B', or 'transparent'."""
    if value.lower() in ("transparent", "none"):
        return None
    if value.startswith("#"):
        v = value.lstrip("#")
        if len(v) != 6:
            raise ValueError(f"expected #RRGGBB, got {value!r}")
        return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))
    parts = value.split(",")
    if len(parts) != 3:
        raise ValueError(f"expected R,G,B or #RRGGBB, got {value!r}")
    return tuple(int(p) for p in parts)


def mark_mask(img, tolerance, full_bleed=False):
    """Binary mask (255 = mark) of where the artwork is.

    Real alpha wins when present. Otherwise the four corners give the background
    colour and every pixel differing from it by more than `tolerance` on any
    channel is mark. Comparing against the sampled background (not a fixed
    brightness) is what makes this polarity-agnostic — an earlier version keyed
    on "darker than X" and silently treated the background as the artwork on
    white-on-navy logos.
    """
    if img.mode in ("RGBA", "LA"):
        alpha = img.getchannel("A")
        if alpha.getextrema()[0] < 255:          # genuine transparency present
            return alpha.point(lambda p: 255 if p > MARK_CUTOFF else 0)

    if full_bleed:                               # the whole frame IS the artwork
        return Image.new("L", img.size, 255)

    rgb = img.convert("RGB")
    w, h = rgb.size
    px = rgb.load()
    corners = [px[0, 0], px[w - 1, 0], px[0, h - 1], px[w - 1, h - 1]]
    bg = tuple(sorted(c[i] for c in corners)[1] for i in range(3))

    diff = ImageChops.difference(rgb, Image.new("RGB", rgb.size, bg))
    r, g, b = diff.split()
    per_pixel_max = ImageChops.lighter(ImageChops.lighter(r, g), b)
    return per_pixel_max.point(lambda p: 255 if p > tolerance else 0)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--size", type=int, default=512,
                    help="output edge in px (default 512; platforms want >=500)")
    ap.add_argument("--padding", type=float, default=None,
                    help="padding as a fraction of the mark's long side (default "
                         "0.16, or 0 with --full-bleed). If the preview shows the "
                         "mark touching the circle, raise it.")
    ap.add_argument("--bg", default="#FFFFFF",
                    help="'#RRGGBB', 'R,G,B', or 'transparent' (default #FFFFFF). "
                         "If the preview shows a blank circle, the mark matches "
                         "the background — pick a contrasting colour.")
    ap.add_argument("--tolerance", type=int, default=32,
                    help="how far a pixel must differ from the corner-sampled "
                         "background to count as mark (default 32). Raise for "
                         "noisy/JPEG sources, lower for a low-contrast mark.")
    ap.add_argument("--full-bleed", action="store_true",
                    help="the artwork already fills the frame (an app-icon tile) "
                         "— skip background detection, use the whole image")
    ap.add_argument("--bbox",
                    help="crop to X0,Y0,X1,Y1 in source pixels — use this to pick "
                         "the symbol out of a symbol+wordmark lockup")
    args = ap.parse_args()

    if args.size < 1:
        sys.exit("--size must be positive")
    if args.size < 500:
        print(f"note   : --size {args.size} is below the 500px platforms expect; "
              f"it will look soft.")
    padding = args.padding if args.padding is not None else (
        0.0 if args.full_bleed else 0.16)
    if padding < 0:
        sys.exit("--padding cannot be negative")
    try:
        bg = parse_color(args.bg)
    except ValueError as e:
        sys.exit(f"--bg: {e}")

    src = Image.open(args.source)
    src = src.convert("RGBA" if src.mode in ("RGBA", "LA", "P") else "RGB")
    W, H = src.size

    src_mask = mark_mask(src, args.tolerance, args.full_bleed)
    source_has_alpha = src.mode == "RGBA" and src.getchannel("A").getextrema()[0] < 255

    # These guards catch "detection went wrong", not "the design is bad". --bbox
    # and --full-bleed are the operator telling us where the artwork is, so the
    # auto-detection guard has no standing to overrule them.
    if not args.bbox and not args.full_bleed and not source_has_alpha:
        coverage = src_mask.histogram()[255] / (W * H)
        if coverage > 0.80:
            sys.exit(
                f"The detected mark covers {coverage:.0%} of the frame. Either the "
                f"artwork fills it (pass --full-bleed for an app-icon tile), or "
                f"--tolerance (now {args.tolerance}) is too low for a noisy source.")
        if coverage < 0.005:
            sys.exit(
                f"Almost no mark detected ({coverage:.2%}). The image may be blank, "
                f"or --tolerance (now {args.tolerance}) is too high for a "
                f"low-contrast mark.")

    if args.bbox:
        try:
            box = tuple(int(v.strip()) for v in args.bbox.split(","))
        except ValueError:
            sys.exit("--bbox needs four integers: X0,Y0,X1,Y1")
        if len(box) != 4:
            sys.exit("--bbox needs exactly X0,Y0,X1,Y1")
        x0, y0, x1, y1 = box
        # PIL pads an out-of-range crop with black, which composites in as opaque
        # artwork — refuse instead of silently corrupting the result.
        if not (0 <= x0 < x1 <= W and 0 <= y0 < y1 <= H):
            sys.exit(f"--bbox {x0},{y0},{x1},{y1} doesn't fit inside the {W}x{H} "
                     f"source (need 0 <= x0 < x1 <= {W}, 0 <= y0 < y1 <= {H}).")
    else:
        box = src_mask.getbbox()
        if not box:
            sys.exit("No mark found — try lowering --tolerance.")

    mark = src.crop(box)
    cropped_mask = src_mask.crop(box)
    mw, mh = mark.size

    side = int(max(mw, mh) * (1 + padding * 2)) or 1
    offset = ((side - mw) // 2, (side - mh) // 2)

    canvas = Image.new("RGBA", (side, side),
                       (0, 0, 0, 0) if bg is None else bg + (255,))
    # Paste through the mark mask when the source has no real alpha but we need
    # transparency, or its background lands as opaque pixels.
    paste_mask = mark if source_has_alpha else (cropped_mask if bg is None else None)
    canvas.paste(mark, offset, paste_mask)

    out = canvas.resize((args.size, args.size), Image.LANCZOS)
    if bg is not None:
        out = out.convert("RGB")
    out.save(args.output)

    # Always render the circular preview. This — an image the operator looks at —
    # is the real check for clipping and visibility, which is why the script no
    # longer tries to compute either.
    prev_path = args.output.rsplit(".", 1)[0] + "-circle.png"
    S = args.size
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, S, S), fill=255)
    rgba = out if out.mode == "RGBA" else out.convert("RGBA")
    inner = Image.new("RGB", (S, S), (255, 255, 255))
    inner.paste(rgba, (0, 0), rgba.getchannel("A"))   # transparent → white, not black
    prev = Image.new("RGB", (S, S), (235, 237, 240))
    prev.paste(inner, (0, 0), mask)
    prev.save(prev_path)

    aspect = max(mw, mh) / max(min(mw, mh), 1)

    print(f"source : {W}x{H}"
          f"{'  (has alpha)' if source_has_alpha else ''}"
          f"{'  [--full-bleed]' if args.full_bleed else ''}")
    print(f"mark   : {box}  ({mw}x{mh}){'  [--bbox]' if args.bbox else ''}")
    print(f"written: {args.output}  ({S}x{S})")
    if bg is None and not source_has_alpha:
        print("note   : no source alpha — background keyed out by colour distance; "
              "JPEG edges will fringe. Prefer a real transparent PNG.")
    if aspect > LOCKUP_ASPECT and not args.bbox and not args.full_bleed:
        print(f"\u26a0 warn : mark is {aspect:.1f}:1 — that's a lockup or strip, not a "
              f"symbol. Squaring it")
        print(f"         is unreadable at ~40px. Re-run with --bbox around just "
              f"the symbol.")
    print(f"\n\u2192 LOOK AT {prev_path} — it shows the actual circular crop.")
    print("  Mark touching the circle? raise --padding. Blank circle? the --bg "
          "matches the mark.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
