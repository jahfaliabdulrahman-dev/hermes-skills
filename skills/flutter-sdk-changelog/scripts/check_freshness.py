#!/usr/bin/env python3
"""Freshness gate for flutter-sdk-changelog — fails when the Flutter world moved ahead of this skill.

Root cause it defends against: a "bridge the AI cutoff" skill can itself go stale, and CI that validates
STRUCTURE (frontmatter, link targets, prose style) never notices, because a wrong version number is
perfectly well-formed markdown. This gate validates FACTS instead.

Checks
  1. The stable release the matrix was generated against is still the live stable release.
  2. The newest Flutter minor in the matrix is not older than the live stable minor.
  3. Every `Dart feature -> Flutter floor` row in SKILL.md matches the generated matrix.
  4. Every row of the hand-curated "highest-impact deprecations" table in SKILL.md matches the
     generated deprecation reference (symbol -> first stable release).

Exit 0 = fresh. Exit 1 = drift or internal inconsistency.
Output is deterministic (no timestamps), so it can be used as a cron change-detector too.

Usage:
  python3 scripts/check_freshness.py            # checks the skill this script lives in
  python3 scripts/check_freshness.py --skill DIR
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

RELEASES_URL = "https://storage.googleapis.com/flutter_infra_release/releases/releases_macos.json"
DEFAULT_SKILL = Path(__file__).resolve().parent.parent


def minor(v: str) -> tuple[int, int]:
    m = re.match(r"^(\d+)\.(\d+)", v)
    return (int(m.group(1)), int(m.group(2))) if m else (0, 0)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill", default=str(DEFAULT_SKILL), help="skill directory to validate")
    args = ap.parse_args()
    skill = Path(args.skill).expanduser().resolve()

    problems: list[str] = []
    notes: list[str] = []

    skill_md_p = skill / "SKILL.md"
    matrix_p = skill / "references" / "flutter-to-dart-version-matrix.md"
    deprec_p = skill / "references" / "widget-deprecations-and-replacements.md"
    texts = {}
    for p in (skill_md_p, matrix_p, deprec_p):
        if p.is_file():
            texts[p] = p.read_text()
        else:
            problems.append(f"MISSING: {p}")
            texts[p] = ""
    skill_md, matrix, deprec = texts[skill_md_p], texts[matrix_p], texts[deprec_p]

    # ---------------------------------------------------------------- live release index
    live_version = None
    fl_minors: dict[tuple[int, int], tuple[str, str, str]] = {}
    try:
        rel = json.loads(urllib.request.urlopen(RELEASES_URL, timeout=60).read())
        by_hash = {r["hash"]: r for r in rel["releases"]}
        live_version = by_hash[rel["current_release"]["stable"]]["version"]
        for r in rel["releases"]:
            if r["channel"] != "stable":
                continue
            mm = re.match(r"^(\d+)\.(\d+)\.", r["version"])
            if not mm:
                continue
            key = (int(mm.group(1)), int(mm.group(2)))
            date = r["release_date"][:10]
            dm = re.match(r"^[\d.]+", r.get("dart_sdk_version") or "")
            if key not in fl_minors or date < fl_minors[key][1]:
                fl_minors[key] = (r["version"], date, dm.group(0) if dm else "")
    except (urllib.error.URLError, ValueError, KeyError, TimeoutError) as e:
        problems.append(f"NETWORK: could not read the Flutter release index ({e})")

    # ---------------------------------------------------------------- 1 & 2
    if live_version and matrix:
        m = re.search(r"Flutter `([\d.]+)` \(20\d\d-\d\d-\d\d\), bundling Dart `([\d.]+)`", matrix)
        if not m:
            problems.append("matrix: generated-header line not found")
        elif m.group(1) != live_version:
            problems.append(
                f"FLUTTER DRIFT: matrix generated against {m.group(1)}, live stable is {live_version}"
                " -> run scripts/build_flutter_sdk_changelog.py --fetch")
        else:
            notes.append(f"matrix generated against live stable {live_version}")

        rows = [tuple(int(x) for x in r) for r in re.findall(r"^\| \*\*(\d+)\.(\d+)\*\* \|", matrix, re.M)]
        if not rows:
            problems.append("matrix: no version rows parsed")
        else:
            newest_row, live_minor = max(rows), minor(live_version)
            if newest_row < live_minor:
                problems.append(
                    f"FLUTTER MINOR MISSING: matrix stops at {newest_row[0]}.{newest_row[1]}, live stable minor "
                    f"is {live_minor[0]}.{live_minor[1]}")
            else:
                notes.append(f"matrix covers {len(rows)} stable minors, up to {newest_row[0]}.{newest_row[1]}")

    # ---------------------------------------------------------------- 3: Dart feature -> Flutter floor
    if skill_md and fl_minors:
        dart2floor: dict[tuple[int, int], tuple[int, int]] = {}
        for k, (_ver, _date, dart) in fl_minors.items():
            if dart:
                dm = minor(dart)
                if dm not in dart2floor or k < dart2floor[dm]:
                    dart2floor[dm] = k
        checked = 0
        for claimed_dart, claimed_fl in re.findall(r"\| `\^(\d+\.\d+)\.0` \| `(\d+\.\d+)\.0` \|", skill_md):
            want = dart2floor.get(minor(claimed_dart))
            checked += 1
            if not want:
                problems.append(f"FLOOR ROW: Dart {claimed_dart} is not bundled by any stable Flutter release")
            elif f"{want[0]}.{want[1]}" != claimed_fl:
                problems.append(
                    f"FLOOR ROW WRONG: Dart ^{claimed_dart}.0 claims Flutter {claimed_fl}.0, real floor is "
                    f"{want[0]}.{want[1]}.0")
        notes.append(f"cross-checked {checked} Dart-floor rows against the release index")

    # ---------------------------------------------------------------- 4: impact table vs generated data
    if skill_md and deprec:
        bucket = None
        sym2b: dict[str, set[str]] = {}
        for line in deprec.splitlines():
            bm = re.match(r"^## First stable release: Flutter (\d+\.\d+)", line)
            if bm:
                bucket = bm.group(1)
                continue
            sm = re.match(r"^\|\s*`(\w+)`\s*\|", line)
            if sm and bucket:
                sym2b.setdefault(sm.group(1), set()).add(bucket)

        table = skill_md.split("Highest-impact deprecations")[-1].split("### Removed, not deprecated")[0]
        checked = 0
        for left, _mid, claimed in re.findall(r"^\|(.+?)\|(.+?)\|\s*(\d+\.\d+)\s*\|$", table, re.M):
            if "dart:ui" in left or "engine" in left:
                continue  # engine-side APIs are verified from docs.flutter.dev/release/breaking-changes
            syms = [s.split(".")[-1] for s in re.findall(r"`([A-Za-z_][\w.]*)`", left)]
            known = [s for s in syms if s in sym2b]
            if not known:
                continue  # rows about removed (not deprecated) APIs are verified from docs, not this tree
            checked += 1
            if not any(claimed in sym2b[s] for s in known):
                problems.append(
                    f"TABLE ROW WRONG: {'/'.join(known)} claims first stable {claimed}, generated data says "
                    f"{sorted(set().union(*(sym2b[s] for s in known)))}")
        notes.append(f"cross-checked {checked} highest-impact rows against the generated deprecations")

    # ---------------------------------------------------------------- report
    print("FLUTTER SDK CHANGELOG — FRESHNESS GATE")
    print(f"skill         : {skill.name}")
    print(f"flutter stable: {live_version or 'unknown'}")
    for n in notes:
        print(f"  ok   - {n}")
    if problems:
        print(f"\nDRIFT DETECTED ({len(problems)}):")
        for p in problems:
            print(f"  FAIL - {p}")
        print("\nFix: python3 scripts/build_flutter_sdk_changelog.py --fetch, then update the freshness "
              "contract block and the highest-impact table in SKILL.md.")
        return 1
    print("\nALL FRESH")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
