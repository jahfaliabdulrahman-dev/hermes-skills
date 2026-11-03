#!/usr/bin/env python3
"""Upstream source map for the installed skill store.

WHY THIS EXISTS: the documented repos in SKILL.md are EXAMPLES, not the source
list. The only authoritative registry of origin is the installer lock file,
which records `source` per installed skill. Hardcoding the repo list silently
skips every skill whose upstream is not named in the doc -- new skills in those
repos are then never discovered.

Usage:
  python3 upstream_source_map.py                 # full map: source -> count -> names
  python3 upstream_source_map.py --sources       # unique sources only (feed a loop)
  python3 upstream_source_map.py --coverage      # gate: is the procedure source-derived?
  python3 upstream_source_map.py --diff pydantic/skills /tmp/pyd_listing.txt
                                                 # upstream names missing locally

Exit codes: 0 ok; 1 argument/lock/parse problem; 2 --coverage found a name-list-based procedure.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import sys

LOCK = pathlib.Path.home() / ".agents" / ".skill-lock.json"
SKILL_MD = pathlib.Path(__file__).resolve().parent.parent / "SKILL.md"

# `npx skills add <repo> -l` renders skills as:  <bar><4 spaces><name>
STORE = pathlib.Path.home() / ".hermes" / "skills"
RETIRED = STORE / ".retired.json"
NAME_RE = re.compile(r"^[\u2502|]\s{4}([a-z0-9][a-z0-9-]*)\s*$")
DECLARED_RE = re.compile(r"^name:\s*[\"']?([A-Za-z0-9._-]+)", re.M)


def retired_names(path: pathlib.Path = RETIRED) -> set:
    """Names deliberately retired by us -- reinstalling them resurrects a decision."""
    if not path.exists():
        return set()
    try:
        return set(json.loads(path.read_text()).get("retired", {}))
    except (json.JSONDecodeError, OSError):
        print(f"WARN: {path} unreadable -- treating as empty, verify by hand", file=sys.stderr)
        return set()


def store_names(root: pathlib.Path = STORE) -> set:
    """Every skill name the STORE already holds, whatever route installed it.

    The lock only knows what `npx` installed. A skill can also be present via the
    hub, a manual copy, a local authoring or a profile link -- and counting those
    as 'missing upstream' is a false alarm that would push duplicates in.
    """
    names = set()
    if not root.exists():
        return names
    for skill_md in root.rglob("SKILL.md"):
        if ".archive" in skill_md.parts:
            continue
        names.add(skill_md.parent.name)
        try:
            head = skill_md.read_text(errors="ignore")[:800]
        except OSError:
            continue
        if m := DECLARED_RE.search(head):
            names.add(m.group(1))
    return names


def load(lock: pathlib.Path = LOCK) -> dict:
    if not lock.exists():
        sys.exit(f"lock not found: {lock} (nothing installed through the shared store?)")
    data = json.loads(lock.read_text())
    skills = data.get("skills")
    if not isinstance(skills, dict):
        sys.exit(f"unexpected lock shape in {lock}: no 'skills' mapping")
    return skills


def by_source(skills: dict) -> dict:
    out = collections.defaultdict(list)
    for name, meta in skills.items():
        out[meta.get("source") or "<unknown>"].append(name)
    return {k: sorted(v) for k, v in out.items()}


def cmd_map(skills: dict) -> int:
    groups = by_source(skills)
    print(f"locked skills: {len(skills)} | distinct sources: {len(groups)}\n")
    for src in sorted(groups):
        print(f"## {src}  ({len(groups[src])})")
        print(", ".join(groups[src]))
        print()
    return 0


def cmd_sources(skills: dict) -> int:
    for src in sorted(by_source(skills)):
        print(src)
    return 0


def cmd_coverage(skills: dict) -> int:
    """Gate: is the PROCEDURE source-derived, or name-list-based?

    The invariant is NOT "every source is named in SKILL.md" -- naming them is the
    defect this gate exists to kill. It is: SKILL.md derives the list from the lock.
    """
    if not SKILL_MD.exists():
        sys.exit(f"SKILL.md not found at {SKILL_MD}")
    doc = SKILL_MD.read_text()
    markers = {
        "upstream_source_map.py": "upstream_source_map.py" in doc,
        "--sources": "--sources" in doc,
        "--diff": "--diff" in doc,
    }
    for marker, present in markers.items():
        print(f"{'OK  ' if present else 'GAP '} procedure marker: {marker}")
    groups = by_source(skills)
    print(f"\ninventory (derived, informational): {len(skills)} skills across {len(groups)} sources")
    for src in sorted(groups):
        print(f"  {len(groups[src]):3d}  {src}")
    missing = [m for m, present in markers.items() if not present]
    if missing:
        print(f"\nFAIL: SKILL.md is name-list-based (missing {', '.join(missing)}) "
              f"-> sources outside the list are never checked")
        return 2
    print("\nPASS: sources are derived from the lock, so a new source needs no doc edit")
    return 0


def cmd_diff(skills: dict, source: str, listing: pathlib.Path) -> int:
    if not listing.exists():
        sys.exit(f"listing not found: {listing} (save the `npx skills add <src> -l` output first)")
    upstream = [m.group(1) for m in map(NAME_RE.match, listing.read_text().splitlines()) if m]
    if not upstream:
        sys.exit("parsed 0 skill names -- the listing format changed; inspect the file before trusting a diff")
    local = set(by_source(skills).get(source, []))
    missing = sorted(set(upstream) - local)
    known = store_names()
    gone = retired_names()
    retired = [n for n in missing if n in gone]
    absent = [n for n in missing if n not in known and n not in gone]
    elsewhere = [n for n in missing if n in known and n not in gone]
    print(f"{source}: upstream={len(set(upstream))} via_lock={len(local)} "
          f"not_via_npx={len(missing)} [absent={len(absent)} "
          f"present_other_route={len(elsewhere)} retired={len(retired)}]")
    for n in absent:
        print(f"  ABSENT             {n}")
    for n in elsewhere:
        print(f"  PRESENT-ELSEWHERE  {n}")
    for n in retired:
        print(f"  RETIRED-DELIBERATE {n}  (see .retired.json -- do NOT reinstall)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Map installed skills to their upstream sources.")
    ap.add_argument("--lock", type=pathlib.Path, default=LOCK)
    ap.add_argument("--sources", action="store_true")
    ap.add_argument("--coverage", action="store_true")
    ap.add_argument("--diff", nargs=2, metavar=("SOURCE", "LISTING_FILE"))
    a = ap.parse_args()
    skills = load(a.lock)
    if a.diff:
        return cmd_diff(skills, a.diff[0], pathlib.Path(a.diff[1]))
    if a.coverage:
        return cmd_coverage(skills)
    if a.sources:
        return cmd_sources(skills)
    return cmd_map(skills)


if __name__ == "__main__":
    raise SystemExit(main())
