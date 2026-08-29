#!/usr/bin/env python3
"""Tamper suite for this skill's freshness gate.

A gate that cannot fail is theatre. This suite copies the skill into a throwaway directory, breaks
exactly ONE fact per case, and asserts the gate exits 1 with the expected reason — plus a control case
proving an untouched copy still exits 0.

Usage (from anywhere):
    python3 scripts/test_gate_tamper.py            # tests the skill this script lives in
    python3 scripts/test_gate_tamper.py <skill-dir>

Case 5 exists because the gate originally MISSED it: an emptied deprecation reference made every
cross-check "unverifiable", so the gate reported ALL FRESH on a gutted skill. The fix was a structural
floor (minimum symbols/buckets/cross-checked rows). Keep that case — it is the regression test for the
one blind spot this gate is known to have had.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
GATE = "scripts/check_freshness.py"

CASES: list[tuple[str, str, callable, str]] = [
    ("stale stable version in the matrix header",
     "references/flutter-to-dart-version-matrix.md",
     lambda t: re.sub(r"Flutter `[\d.]+` \((20\d\d-\d\d-\d\d)\)", "Flutter `3.29.0` (2025-02-12)", t, count=1),
     "FLUTTER DRIFT"),
    ("newest minor row deleted from the matrix",
     "references/flutter-to-dart-version-matrix.md",
     lambda t: re.sub(r"^\| \*\*\d+\.\d+\*\* \|.*\n", "", t, count=1, flags=re.M),
     "FLUTTER MINOR MISSING"),
    ("wrong Dart-to-Flutter floor row in SKILL.md",
     "SKILL.md",
     lambda t: t.replace("| `^3.10.0` | `3.38.0` |", "| `^3.10.0` | `3.32.0` |", 1),
     "FLOOR ROW WRONG"),
    ("wrong first-stable in the highest-impact table",
     "SKILL.md",
     lambda t: re.sub(r"(`scrollCacheExtent` \| )3\.\d+( \|)", r"\g<1>3.29\g<2>", t, count=1),
     "TABLE ROW WRONG"),
    ("deprecation reference emptied",
     "references/widget-deprecations-and-replacements.md",
     lambda t: t.split("## First stable release")[0],
     "TOO THIN"),
]


def run(gate_path: Path) -> tuple[int, str]:
    r = subprocess.run([sys.executable, str(gate_path)], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def main() -> int:
    if not (SKILL / GATE).is_file():
        print(f"gate not found: {SKILL/GATE}")
        return 2
    work = Path(tempfile.mkdtemp(prefix="gate_tamper_"))
    failures = 0
    try:
        control = work / "control"
        shutil.copytree(SKILL, control)
        rc, _ = run(control / GATE)
        ok = rc == 0
        print(f"[control] untouched copy{'':>32} rc={rc} -> {'GREEN (correct)' if ok else 'FAILED WRONGLY'}")
        failures += (not ok)

        for i, (label, relpath, mutate, expect) in enumerate(CASES, 1):
            d = work / f"case{i}"
            shutil.copytree(SKILL, d)
            f = d / relpath
            before = f.read_text()
            after = mutate(before)
            if after == before:
                print(f"[case {i}] {label:<46} FIXTURE MISSING — anchor not found, case is a no-op")
                failures += 1
                continue
            f.write_text(after)
            rc, out = run(d / GATE)
            reason_ok = expect in out
            detected = rc == 1 and reason_ok
            verdict = "DETECTED" if detected else ("WRONG REASON" if rc == 1 else "MISSED")
            print(f"[case {i}] {label:<46} rc={rc} -> {verdict}")
            for line in out.splitlines():
                if line.strip().startswith("FAIL"):
                    print(f"          {line.strip()[:120]}")
            failures += (not detected)
    finally:
        shutil.rmtree(work, ignore_errors=True)

    total = len(CASES)
    print(f"\ntamper cases detected: {total - failures if failures <= total else 0}/{total}")
    if failures:
        print("SUITE FAILED — the gate cannot be trusted until every case exits 1 for the right reason.")
        return 1
    print("SUITE PASSED — the gate detects every seeded defect and stays green on a clean copy.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
