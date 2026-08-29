#!/usr/bin/env python3
"""Verify Spec Pack Compliance — checks a project's app-spec/ against the
25-file, 6-stage structure with gate readiness.

Usage:
    python3 verify_spec_pack.py /path/to/project

Exit code 0 = compliant, 1 = gaps found. CI-usable.
Built 2026-08-03 as part of Spec Pack Premium. Validated: correctly flagged
Azdal's legacy 22-slot structure as non-compliant with the 25-file system.
"""
import os
import sys

REQUIRED = {
    "00_project_stages.md": ("🗺️", "Stage 1", None),
    "01_product_discovery.md": ("1 🟢", "Stage 1", None),
    "02_project_context.md": ("1 🟢", "Stage 1", None),
    "03_project_overrides.md": ("1 🟢", "Stage 1", None),
    "04_monetization_entitlements.md": ("2 🟡", "Stage 2", None),
    "05_financial_model.md": ("2 🟡", "Stage 2", None),
    "06_assumptions_risks.md": ("2 🟡", "Stage 2", None),
    "07_user_flows_navigation.md": ("3 🟠", "Stage 3", ["```mermaid"]),
    "08_design_prototype.md": ("3 🟠", "Stage 3", ["## §"]),
    "09_prd.md": ("4 🔵", "Stage 4", ["```gherkin", "Given", "When", "Then"]),
    "10_data_model_erd.md": ("4 🔵", "Stage 4", None),
    "11_api_contract.md": ("4 🔵", "Stage 4", None),
    "12_flutter_architecture.md": ("4 🔵", "Stage 4", ["Hook System", "Screen State", "Error Handler", "Logger"]),
    "13_security_privacy.md": ("4 🔵", "Stage 4", None),
    "14_testing_acceptance.md": ("4 🔵", "Stage 4", None),
    "15_devops_release.md": ("4 🔵", "Stage 4", None),
    "16_ai_agent_contract.md": ("4 🔵", "Stage 4", ["Debt", "policy"]),
    "17_data_architecture_acid.md": ("4 🔵", "Stage 4", None),
    "18_implementation_backlog.md": ("4 🔵", "Stage 4", ["Dependency", "sequence"]),
    "19_decision_log.md": ("5 🟣", "Stage 5", None),
    "20_lessons_learned.md": ("5 🟣", "Stage 5", None),
    "21_zero_trust_red_team.md": ("5 🟣", "Stage 5", None),
    "22_admin_panel.md": ("6 ⚫", "Stage 6", None),
    "23_support_operations.md": ("6 ⚫", "Stage 6", None),
    "24_active_capabilities.md": ("6 ⚫", "Stage 6", None),
    "25_agent_operating_playbook.md": ("6 ⚫", "Stage 6", ["Route A", "Route B"]),
}

STAGE_FILES = {
    "1": ["01", "02", "03"],
    "2": ["04", "05", "06"],
    "3": ["07", "08"],
    "3.5": ["16", "18"],  # content lives inside these
    "4": ["09", "10", "11", "12", "13", "14", "15", "16", "17", "18"],
    "5": ["19", "20", "21"],
    "6": ["22", "23", "24", "25"],
}


def check_header(path: str) -> list:
    """Verify the mandatory header template."""
    problems = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            head = f.read(1500)
    except Exception:
        return ["unreadable"]
    if "Document ID:" not in head:
        problems.append("missing Document ID")
    if "Version:" not in head:
        problems.append("missing Version")
    if "Status:" not in head:
        problems.append("missing Status")
    if "Stage:" not in head:
        problems.append("missing Stage")
    if "Owner:" not in head:
        problems.append("missing Owner")
    if "Last Updated:" not in head:
        problems.append("missing Last Updated")
    if "Cross-Reference:" not in head:
        problems.append("missing Cross-Reference")
    if "[00_project_stages.md](00_project_stages.md)" not in head:
        problems.append("missing 00 cross-reference")
    return problems


def check_content(path: str, markers: list) -> list:
    problems = []
    if not markers:
        return problems
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return ["unreadable"]
    for m in markers:
        if m not in content:
            problems.append(f"missing content marker: {m}")
    return problems


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 verify_spec_pack.py /path/to/project")
        sys.exit(1)

    project = sys.argv[1]
    app_spec = os.path.join(project, "app-spec")
    if not os.path.isdir(app_spec):
        print(f"❌ No app-spec/ directory at {app_spec}")
        sys.exit(1)

    print(f"🔍 Verifying Spec Pack: {app_spec}\n")
    errors = 0
    warnings = 0

    for filename, (emoji, stage, markers) in REQUIRED.items():
        path = os.path.join(app_spec, filename)
        if not os.path.exists(path):
            print(f"  ❌ {filename} — MISSING ({stage})")
            errors += 1
            continue
        size = os.path.getsize(path)
        if size < 200:
            print(f"  ⚠️  {filename} — exists but tiny ({size} B); likely empty placeholder")
            warnings += 1
            continue
        header_issues = check_header(path)
        content_issues = check_content(path, markers) if markers else []
        all_issues = header_issues + content_issues
        if all_issues:
            print(f"  ⚠️  {filename} — {'; '.join(all_issues)}")
            warnings += 1
        else:
            print(f"  ✅ {filename}")

    print("\n" + "=" * 50)
    print(f"Files: {sum(1 for f in REQUIRED if os.path.exists(os.path.join(app_spec, f)))}/{len(REQUIRED)}")
    print(f"Errors: {errors}  Warnings: {warnings}")

    # Gate readiness summary
    print("\n🏁 Gate Readiness:")
    for stage, files in STAGE_FILES.items():
        present = sum(1 for f in files if any(x.startswith(f) for x in REQUIRED if os.path.exists(os.path.join(app_spec, x))))
        status = "✅" if present == len(files) else "❌"
        print(f"  {status} Stage {stage}: {present}/{len(files)} files")

    if errors:
        print("\n❌ NOT COMPLIANT — missing required files")
        sys.exit(1)
    if warnings:
        print("\n⚠️  COMPLIANT with warnings — review flagged files")
        sys.exit(0)
    print("\n✅ FULLY COMPLIANT")
    sys.exit(0)


if __name__ == "__main__":
    main()
