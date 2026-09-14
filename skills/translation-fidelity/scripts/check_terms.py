#!/usr/bin/env python3
"""Term-base gate for Arabic outputs (translation-fidelity skill).

Usage:  python3 check_terms.py <file-or-dir> [...]
Scans *.md/*.html/*.txt for forbidden renderings (avoid lists) from
assets/term-base.json. Exit 1 on any hit; exit 0 when clean.
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent.parent
BASE = HERE / "assets" / "term-base.json"


def load_rules():
    data = json.loads(BASE.read_text(encoding="utf-8"))
    rules = []
    for e in data["entries"]:
        for a in e.get("avoid", []):
            rules.append((a, e["term"], e["ar"], e.get("note", "")))
    return rules


def files_of(target: str):
    p = pathlib.Path(target)
    if p.is_dir():
        out = []
        for ext in ("*.md", "*.html", "*.txt"):
            out += sorted(p.rglob(ext))
        return out
    return [p]


def scan(target: str, rules):
    hits = 0
    for f in files_of(target):
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            for avoid, term, ar, note in rules:
                if avoid and avoid in line:
                    hits += 1
                    extra = f" — {note}" if note else ""
                    print(f"HIT  {f}:{i}\n     «{avoid}» → المعتمد «{ar}» (لـ {term}){extra}")
    return hits


def main():
    args = [a for a in sys.argv[1:] if a != "--quiet"]
    if not args:
        print(__doc__)
        sys.exit(2)
    rules = load_rules()
    total = sum(scan(t, rules) for t in args)
    verdict = "PASS ✓" if total == 0 else f"FAIL — {total} إصابة"
    print(f"\n{verdict}")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
