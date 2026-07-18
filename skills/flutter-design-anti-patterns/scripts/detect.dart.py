#!/usr/bin/env python3
"""
⚠️ SPIKE — Proof-of-concept only. NOT FOR PRODUCTION USE.
Built 2026-07-11 to validate the concept of deterministic Flutter design detection.
Superseded by the custom_lint plugin (see lint_plugin/).

Multi-model consultation verdict (2026-07-11):
  - Score: 2/10 — 98% false positive rate (AP-020 = 927/945 findings)
  - "This is not a detector. It's a noise generator with a JSON output."
  - "You built evidence that you need a different approach."

Kept as a reference artifact only. Do NOT integrate into pre-commit hooks or CI.

Usage (for historical reference only):
  python3 detect.dart.py lib/ --json
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

# ── Anti-Pattern Registry ──────────────────────────────────────────────
# NOTE: Only 7 of 31 patterns are regex-detectable. See SKILL.md for full registry.
# The custom_lint plugin (lint_plugin/) implements the 3 core rules properly via AST.

RULES = [
    # ═══ Color & Theme ═══
    (
        "AP-001",
        "color",
        "P0",
        "Hardcoded Color",
        re.compile(r"Color\(\s*0x[0-9A-Fa-f]{8}\s*\)"),
        "Hardcoded Color — use Theme.of(context).colorScheme instead",
    ),
    (
        "AP-004",
        "color",
        "P2",
        "Pure Black/White in Theme",
        re.compile(
            r"Colors\.(black|white)(?!\d)|Color\(\s*0x(F{6}|000000)(F{2})?\s*\)"
        ),
        "Pure black/white — use colorScheme.surface or tint toward brand hue",
    ),
    # ═══ Typography ═══
    (
        "AP-007",
        "typography",
        "P1",
        "Missing Text Scaling",
        re.compile(r"fontSize\s*:\s*\d+\.?\d*"),
        "FontSize without textScaler — may not respect accessibility scaling",
    ),
    # ═══ Layout ═══
    (
        "AP-009",
        "layout",
        "P0",
        "Fixed Dimensions",
        re.compile(
            r"(SizedBox|Container)\s*\(\s*(width|height)\s*:\s*(?![1-9]?[0-9]\b)[0-9]+\b"
        ),
        "Fixed dimensions — use LayoutBuilder or MediaQuery for responsiveness",
    ),
    (
        "AP-030",
        "layout",
        "P0",
        "AbsorbPointer Usage",
        re.compile(r"AbsorbPointer\s*\("),
        "AbsorbPointer — likely hiding layout bug. Fix widget hierarchy instead.",
    ),
    # ═══ i18n / RTL ═══
    (
        "AP-020",
        "i18n",
        "P0",
        "Hardcoded User String",
        re.compile(r"'[A-Za-z\u0600-\u06FF]{3,}[^']*'"),
        "Hardcoded string — use AppLocalizations.of(context)!.key instead",
    ),
    (
        "AP-021",
        "i18n",
        "P0",
        "LTR-Only EdgeInsets",
        re.compile(
            r"EdgeInsets\.only\s*\(\s*left\s*:|EdgeInsets\.only\s*\(\s*right\s*:|Alignment\.(centerLeft|topLeft|bottomLeft)"
        ),
        "LTR-only EdgeInsets/Alignment — use EdgeInsetsDirectional.only(start:) for RTL support",
    ),
]

# Patterns to EXCLUDE from AP-020 (hardcoded string) — things that look like strings but aren't UI copy
# NOTE: This is a losing battle. 98% false positive rate proves regex can't solve this.
AP020_EXCLUDE = re.compile(
    r"'.*\.(dart|json|png|jpg|svg|ttf|otf|g)\w*'|"  # file paths
    r"'[A-Za-z_]+\.[A-Za-z_]+'|"  # property access
    r"'[a-z]+:[a-z]+'|"  # route names
    r"'[a-z_]+'|"  # single-word identifiers
    r"'.*Provider.*'|'.*override.*'|'.*isar.*'|"  # code comments / debug strings
    r"'[A-Z][a-z]+ [A-Z]'|"  # short labels like 'Add Vehicle'
    r"'[A-Z][a-z]+'"  # single capitalized word
)

# Files EXCLUDED from AP-001 (hardcoded color) — theme definition files
AP001_EXCLUDE_FILES = re.compile(
    r"(app_theme|theme|colors|color_scheme|design_tokens)\.dart$",
    re.IGNORECASE,
)


def find_dart_files(target: str) -> list[Path]:
    path = Path(target)
    if path.is_file():
        return [path] if path.suffix == ".dart" else []
    dart_files = []
    for f in path.rglob("*.dart"):
        if "test" in f.parts or "generated" in f.parts or ".g.dart" in f.name:
            continue
        dart_files.append(f)
    return sorted(dart_files)


def scan_file(filepath: Path, severity_filter: str | None) -> list[dict]:
    findings = []
    try:
        content = filepath.read_text(encoding="utf-8")
        lines = content.split("\n")
    except Exception:
        return []

    for rule_id, category, severity, name, pattern, message in RULES:
        if severity_filter and severity != severity_filter:
            continue

        # Skip AP-001 on theme definition files (colors belong there)
        if rule_id == "AP-001" and AP001_EXCLUDE_FILES.search(str(filepath)):
            continue

        for match in pattern.finditer(content):
            matched_text = match.group(0)

            # AP-020 exclusion filter
            if rule_id == "AP-020" and AP020_EXCLUDE.match(matched_text):
                continue

            line_num = content[: match.start()].count("\n") + 1
            col = match.start() - (content[: match.start()].rfind("\n") + 1) + 1
            snippet = (
                lines[line_num - 1].strip()[:120] if line_num <= len(lines) else ""
            )

            findings.append(
                {
                    "id": rule_id,
                    "category": category,
                    "severity": severity,
                    "name": name,
                    "file": str(filepath),
                    "line": line_num,
                    "column": col,
                    "message": message,
                    "matched": matched_text[:80],
                    "snippet": snippet,
                }
            )

    return findings


def main():
    parser = argparse.ArgumentParser(
        description="⚠️ SPIKE — Flutter Design Detector v1 (proof-of-concept, not production)"
    )
    parser.add_argument("target", help="File or directory to scan")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    parser.add_argument(
        "--severity", choices=["P0", "P1", "P2"], help="Filter by severity level"
    )
    parser.add_argument(
        "--quiet", action="store_true", help="Suppress output, exit code only"
    )
    args = parser.parse_args()

    target = Path(args.target)
    if not target.exists():
        print(f"Error: '{args.target}' not found", file=sys.stderr)
        sys.exit(2)

    dart_files = find_dart_files(args.target)
    if not dart_files:
        if args.json:
            print(
                json.dumps(
                    {
                        "findings": [],
                        "summary": {"P0": 0, "P1": 0, "P2": 0, "total": 0},
                    }
                )
            )
        sys.exit(0)

    all_findings = []
    for f in dart_files:
        all_findings.extend(scan_file(f, args.severity))

    summary = defaultdict(int)
    for finding in all_findings:
        summary[finding["severity"]] += 1
    summary["total"] = len(all_findings)

    if args.json:
        output = {
            "findings": all_findings,
            "summary": {
                "P0": summary.get("P0", 0),
                "P1": summary.get("P1", 0),
                "P2": summary.get("P2", 0),
                "total": summary["total"],
            },
            "files_scanned": len(dart_files),
            "_warning": "SPIKE — 98% false positive rate. Use custom_lint plugin instead.",
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    elif not args.quiet:
        for f in all_findings:
            sev_color = {"P0": "🔴", "P1": "🟡", "P2": "🟢"}.get(f["severity"], "⚪")
            print(
                f"{sev_color} {f['severity']} {f['id']} {f['file']}:{f['line']}:{f['column']}"
            )
            print(f"   {f['message']}")
            print(f"   → {f['matched']}")
            print()

        print(
            f"─── {summary['total']} findings ({summary.get('P0',0)} P0, {summary.get('P1',0)} P1, {summary.get('P2',0)} P2) in {len(dart_files)} files"
        )
        print("⚠️  WARNING: ~98% false positive rate. Use custom_lint plugin for production.")

    sys.exit(1 if all_findings else 0)


if __name__ == "__main__":
    main()
