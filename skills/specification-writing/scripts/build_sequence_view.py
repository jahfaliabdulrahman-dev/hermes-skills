#!/usr/bin/env python3
"""build_sequence_view.py — GENERAL TEMPLATE (adapt paths, then run on demand).

Reads a Stage-3.5 backlog (locked build sequence table + work-type/EPIC sections)
and the loop's STATE file, and prints/generates two READ views of the SAME truth:

  1. Sequence view  — step | BL | EPIC | why  (the build story)
  2. Swimlane view  — which EPIC lands where (splits visible)
  3. --html FILE    — self-contained HTML swimlane with LIVE state:
                     ✓ done / 🔄 in-progress / ⏭ next / faded future,
                     plus a one-line "Next step: BL-XXX" header.

Why this shape (validated on CarSah, 2026-08-10 — the founder's breakthrough:
"this is what I needed to know what the next step is" — human-first, not
technical):
  * DERIVED, never committed — the script holds NO data; it reads the backlog +
    STATE at run time, so it cannot drift into a second, lying source of truth.
    Run it again after any DEC/delivery; the map updates itself.
  * The locked table stays the single source of truth; EPIC ids are frozen
    mid-build (they are audit-trail labels — reviews/DECs reference them).

Parsing assumptions (spec-pack convention) — tune the constants below:
  - Work-type sections:  "## 5. EPIC-01 — Project Foundation"
  - Items in a section:  "### BL-040 Add Service Record"
  - Locked table header: "### 14b.2 The Locked Build Sequence"
  - STATE file line:     "Locked sequence (18 §14b.2): 1–10 ✅ · ... ⏭ ..."
    (the listing WRAPS across lines — join until a blank line)

Usage:
    python3 build_sequence_view.py [backlog.md] [STATE.md]
    python3 build_sequence_view.py --html out.html
"""

import argparse
import re
import subprocess
from pathlib import Path

DEFAULT_BACKLOG = Path("app-spec/18_implementation_backlog.md")
DEFAULT_STATE = Path("handoff/STATE.md")
# Tune to the actual file: the locked-sequence section header and the STATE line prefix.
SEQUENCE_HEADER = "### 14b.2 The Locked Build Sequence"
STATE_PREFIX = "Locked sequence"
MAX_STEP = 45  # columns in the swimlane grid — set to the max step number


def _num(s: str) -> int:
    m = re.match(r"\d+", s or "")
    return int(m.group()) if m else 0


def parse_backlog(path: Path):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # 1) EPIC sections: "## N. EPIC-XX — name" headers give line ranges.
    epic_sections = []  # (start, end, epic_id, name)
    for i, ln in enumerate(lines):
        m = re.match(r"^##\s+\d+[a-z]?\.\s+(EPIC-\d+)\s*[—-]\s*(.+)$", ln)
        if m:
            epic_sections.append([i, None, m.group(1), m.group(2).strip()])
    for j in range(len(epic_sections) - 1):
        epic_sections[j][1] = epic_sections[j + 1][0]
    if epic_sections:
        epic_sections[-1][1] = len(lines)

    # 2) BL -> EPIC from the ### BL-XXX headings inside each EPIC section.
    bl_epic = {}
    for start, end, epic_id, _ in epic_sections:
        for ln in lines[start:end]:
            m = re.search(r"^###\s+(BL-\d+[a-z]?)", ln)
            if m:
                bl_epic[m.group(1)] = epic_id

    # 3) The locked sequence table: "| # | BL-XXX desc | why |"
    seq = []
    in_table = False
    for ln in lines:
        if SEQUENCE_HEADER in ln:
            in_table = True
            continue
        if in_table and (ln.startswith("| # |") or ln.startswith("|---")):
            continue
        if in_table and ln.startswith("|"):
            m = re.match(r"\|\s*(\d+[a-z]?)\s*\|\s*(BL-\d+[a-z]?)\s+([^|]*?)\s*\|\s*([^|]*?)\s*\|", ln)
            if m:
                seq.append({"step": m.group(1), "bl": m.group(2),
                            "desc": m.group(3).strip(), "why": m.group(4).strip()})
            continue
        if in_table and ln.startswith("**Not in this sequence"):
            break
    return bl_epic, epic_sections, seq


def read_state(path: Path, seq: list):
    """done BL ids + next BL, from the STATE file's locked-sequence line.
    Pitfall: the listing WRAPS across multiple lines — join until a blank line.
    Done steps appear as numbers/ranges ('12–27a ✅'); next step is marked ⏭."""
    done_steps, next_step = set(), None
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        text = ""
    m = re.search(re.escape(STATE_PREFIX) + r"[^\n]*:\s*(.+)", text)
    if not m:
        return set(), None
    lines = text.splitlines()
    idx = next((i for i, l in enumerate(lines) if STATE_PREFIX in l), -1)
    buf = [m.group(1).strip()]
    for l in lines[idx + 1:]:
        if not l.strip():
            break
        buf.append(l.strip())
    parts = " · ".join(buf).split("·")
    for i, seg in enumerate(parts):
        if "⏭" in seg:
            mm = re.search(r"(\d+[a-z]?)", seg)
            if mm:
                next_step = mm.group(1)
            parts = parts[:i]
            break
    for seg in parts:
        for a, b in re.findall(r"(\d+[a-z]?)\s*[–—-]\s*(\d+[a-z]?)", seg):
            for n in range(_num(a), _num(b) + 1):
                done_steps.add(str(n))
            if re.search(r"[a-z]$", b):
                done_steps.add(b)
        for n in re.findall(r"(?<!\d)(\d+[a-z]?)(?!\d)", seg):
            done_steps.add(n)
    step_to_bl = {s["step"]: s["bl"] for s in seq}
    done = {step_to_bl[s] for s in done_steps if s in step_to_bl}
    return done, (step_to_bl.get(next_step) if next_step else None)


def first_appearance(eid, epic_steps):
    steps = epic_steps.get(eid, [])
    return _num(steps[0]["step"]) if steps else 999


def seq_view(seq, bl_epic):
    out = ["# Build Sequence View (DERIVED)\n", "| # | Item | EPIC | Why here |", "|---|---|---|---|"]
    for s in seq:
        out.append(f"| {s['step']} | {s['bl']} {s['desc']} | {bl_epic.get(s['bl'], '?')} | {s['why'] or '—'} |")
    return "\n".join(out)


def swim_view(seq, epic_sections, bl_epic_map):
    epic_steps = {}
    for s in seq:
        epic_steps.setdefault(bl_epic_map.get(s["bl"], "?"), []).append(s)
    out = ["# Swimlane View (DERIVED)\n"]
    for _s, _e, eid, name in sorted(epic_sections, key=lambda e: first_appearance(e[2], epic_steps)):
        steps = epic_steps.get(eid, [])
        if not steps:
            continue
        nums = [str(_num(s["step"])) for s in steps]
        ranges, lo, hi = [], nums[0], nums[0]
        for n in nums[1:]:
            if int(n) == int(hi) + 1:
                hi = n
            else:
                ranges.append(f"{lo}" if lo == hi else f"{lo}-{hi}")
                lo = hi = n
        ranges.append(f"{lo}" if lo == hi else f"{lo}-{hi}")
        out.append(f"**{eid} — {name}**: steps {', '.join(ranges)} · {', '.join(s['bl'] for s in steps)}")
    return "\n".join(out)


def swim_html(seq, epic_sections, bl_epic_map, done=None, in_progress=False):
    done = done or set()
    epic_steps = {}
    for s in seq:
        epic_steps.setdefault(bl_epic_map.get(s["bl"], "?"), []).append(s)
    next_bl = next((s["bl"] for s in seq if s["bl"] not in done), None)
    palette = ["#2563eb", "#7c3aed", "#0d9488", "#ea580c", "#dc2626",
               "#16a34a", "#ca8a04", "#db2777", "#4f46e5", "#0891b2", "#65a30d"]
    order = sorted(epic_sections, key=lambda e: first_appearance(e[2], epic_steps))
    color = {e[2]: palette[i % len(palette)] for i, e in enumerate(order)}
    rows = []
    for _s, _e, eid, name in order:
        steps = epic_steps.get(eid, [])
        if not steps:
            continue
        cells = []
        for n in range(1, MAX_STEP + 1):
            hit = [s for s in steps if _num(s["step"]) == n]
            if not hit:
                cells.append('<td style="border:1px solid #f0f0f0;background:#fafafa;"></td>')
                continue
            bl, c = hit[0]["bl"], color[eid]
            if bl == next_bl and in_progress:
                style = "background:#f59e0b;color:#fff;text-align:center;font-size:11px;border:2px solid #b45309;border-radius:8px;padding:4px 2px;"
                label = f"🔄 {bl}"
            elif bl == next_bl:
                style = f"background:#fff;color:#111;text-align:center;font-size:11px;border:3px solid {c};border-radius:8px;padding:3px 2px;font-weight:700;"
                label = f"⏭ {bl}"
            elif bl in done:
                style = f"background:{c};color:#fff;text-align:center;font-size:10px;border:1px solid #fff;border-radius:6px;padding:4px 2px;"
                label = f"✓ {bl}"
            else:
                style = f"background:{c}33;color:{c};text-align:center;font-size:10px;border:1px solid {c}44;border-radius:6px;padding:4px 2px;"
                label = bl
            cells.append(f'<td style="{style}">{label}</td>')
        rows.append(
            f'<tr><td style="font-weight:600;padding:6px 10px;white-space:nowrap;border-right:3px solid {color[eid]};">{eid}<br>'
            f'<span style="font-weight:400;color:#666;font-size:10px;">{name}</span></td>' + "".join(cells) + "</tr>")
    headers = "".join(f"<th>{n}</th>" for n in range(1, MAX_STEP + 1))
    status = (f"<p style='color:#111827;font-weight:600;font-size:15px;'>Next step: "
              f"<span style='color:#b45309;'>{next_bl or '—'}</span>"
              f"{' — in progress now 🔄' if in_progress else ' — ready to start ⏭'}</p>")
    return f"""<!DOCTYPE html>
<html dir="ltr"><head><meta charset="utf-8"><title>Build swimlane</title></head>
<body style="font-family:-apple-system,'Segoe UI',Tahoma,sans-serif;background:#f6f7fb;margin:24px;">
<h2 style="color:#111827;">Build Swimlane <span style="font-weight:400;color:#6b7280;font-size:14px;">(DERIVED — generated on demand, never committed)</span></h2>
{status}
<table style="border-collapse:separate;border-spacing:2px;width:100%;">
<thead><tr><th style="text-align:left;min-width:170px;">EPIC</th>{headers}</tr></thead>
<tbody>{''.join(rows)}</tbody></table>
<p style="color:#6b7280;font-size:12px;">✓ done · 🔄 in progress · ⏭ next · faded = future. Splits are deliberate: dependencies, not categories, order the build.</p>
</body></html>"""


def tree_dirty(repo_root: Path) -> bool:
    r = subprocess.run(["git", "status", "--porcelain", "--", "lib/", "test/"],
                       capture_output=True, text=True, cwd=str(repo_root))
    return bool(r.stdout.strip())


def main():
    ap = argparse.ArgumentParser(description="Derived sequence/swimlane views from the locked backlog")
    ap.add_argument("backlog", nargs="?", default=str(DEFAULT_BACKLOG))
    ap.add_argument("state", nargs="?", default=str(DEFAULT_STATE))
    ap.add_argument("--html", metavar="FILE", help="write the live HTML swimlane to FILE")
    args = ap.parse_args()

    backlog = Path(args.backlog)
    state = Path(args.state)
    bl_epic, epic_sections, seq = parse_backlog(backlog)

    if args.html:
        done, next_bl = read_state(state, seq)
        dirty = tree_dirty(backlog.resolve().parent.parent)
        Path(args.html).write_text(
            swim_html(seq, epic_sections, bl_epic, done=done, in_progress=dirty and next_bl is not None),
            encoding="utf-8")
        print(f"wrote {args.html} — done={len(done)}, next={next_bl}, tree_dirty={dirty}")
        return
    print(seq_view(seq, bl_epic))
    print()
    print(swim_view(seq, epic_sections, bl_epic))


if __name__ == "__main__":
    main()
