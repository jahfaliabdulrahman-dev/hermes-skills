#!/usr/bin/env python3
"""Build the flutter-sdk-changelog reference documents from AUTHORITATIVE sources only.

Sources (no hand-typed version numbers anywhere):
  1. https://storage.googleapis.com/flutter_infra_release/releases/releases_macos.json
     -> every stable Flutter release, its date and its bundled Dart SDK.
  2. the flutter/flutter git tree on the *stable* branch, fetched into the local Flutter SDK checkout
     -> every live @Deprecated annotation, verbatim.

Deprecation-version rule (from flutter/flutter docs/contributing/Tree-hygiene.md):
  the annotation records "the beta version at time of deprecation", so the first STABLE
  release that carries a deprecation is the next stable minor after that marker.

Usage:
  python3 scripts/build_flutter_sdk_changelog.py --fetch      # fetch stable, then regenerate
  python3 scripts/build_flutter_sdk_changelog.py              # regenerate from the last fetch
  python3 scripts/build_flutter_sdk_changelog.py --out DIR    # write elsewhere

Portability: the Flutter SDK checkout is resolved from $FLUTTER_ROOT, else from `which flutter`.
Output defaults to `<skill>/references/` relative to this script, so the skill works wherever it is
installed (Hermes, Claude, plain checkout) with no absolute paths.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from collections import defaultdict
from pathlib import Path

RELEASES_URL = "https://storage.googleapis.com/flutter_infra_release/releases/releases_macos.json"
MIN_MARKER = (3, 10)
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "references"


# ---------------------------------------------------------------- environment
def resolve_flutter_root(explicit: str | None) -> Path:
    """Locate a Flutter SDK *git checkout* (not a zip install) without hard-coding any path."""
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit).expanduser())
    if os.environ.get("FLUTTER_ROOT"):
        candidates.append(Path(os.environ["FLUTTER_ROOT"]).expanduser())
    which = shutil.which("flutter")
    if which:
        candidates.append(Path(os.path.realpath(which)).parent.parent)
    for c in candidates:
        if (c / "packages" / "flutter" / "lib").is_dir() and (c / ".git").exists():
            return c
    sys.exit(
        "FATAL: no Flutter SDK git checkout found.\n"
        "  Tried: --flutter-root, $FLUTTER_ROOT, `which flutter`.\n"
        "  This script reads @Deprecated annotations out of the SDK's own git tree, so the SDK must be a\n"
        "  git clone (the standard `git clone`/Homebrew/`fvm` installs are). Pass --flutter-root PATH."
    )


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True).stdout


def resolve_rev(root: Path, do_fetch: bool) -> str:
    """Return a rev that certainly points at current stable."""
    if do_fetch:
        r = subprocess.run(["git", "-C", str(root), "fetch", "--depth", "1", "origin", "stable"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"FATAL: git fetch failed in {root}:\n{r.stderr.strip()}")
        return "FETCH_HEAD"
    for rev in ("FETCH_HEAD", "origin/stable", "stable"):
        if subprocess.run(["git", "-C", str(root), "rev-parse", "--verify", "--quiet", rev],
                          capture_output=True).returncode == 0:
            return rev
    sys.exit(f"FATAL: no stable rev in {root}. Re-run with --fetch.")


# ---------------------------------------------------------------- release index
def load_releases() -> tuple[dict, dict[tuple[int, int], tuple[str, str, str]]]:
    raw = json.loads(urllib.request.urlopen(RELEASES_URL, timeout=60).read())
    by_hash = {r["hash"]: r for r in raw["releases"]}
    cur_stable = by_hash[raw["current_release"]["stable"]]
    minors: dict[tuple[int, int], tuple[str, str, str]] = {}
    for r in raw["releases"]:
        if r["channel"] != "stable":
            continue
        m = re.match(r"^(\d+)\.(\d+)\.", r["version"])
        if not m:
            continue
        key = (int(m.group(1)), int(m.group(2)))
        date = r["release_date"][:10]
        dm = re.match(r"^[\d.]+", r.get("dart_sdk_version") or "")
        dart = dm.group(0) if dm else "not published"
        if key not in minors or date < minors[key][1]:
            minors[key] = (r["version"], date, dart)
    return cur_stable, minors


# ---------------------------------------------------------------- deprecations
def declared_symbol(decl: str) -> str:
    """Extract the declared identifier from a Dart declaration line, ignoring default values."""
    cm = re.search(r"\b(?:class|typedef|enum|mixin|extension)\s+(\w+)", decl)
    if cm:
        return cm.group(1)
    tm = re.search(r"\b(?:this|super)\.(\w+)", decl)
    if tm:
        return tm.group(1)
    head = decl.split("=")[0].split("=>")[0]
    pm = re.search(r"(\w+)\s*\($", head.strip()) or re.search(r"(\w+)\s*\(", head)
    if pm:
        return pm.group(1)
    ids = re.findall(r"[A-Za-z_]\w*", head.rstrip(" ,;{"))
    return ids[-1] if ids else decl[:40]


def collect_deprecations(root: Path, rev: str, stable_minors: list[tuple[int, int]]):
    files = sorted(set(
        line.split(":", 1)[1]
        for line in git(root, "grep", "-l", "-i", "-E", "deprecated after v", rev, "--",
                        "packages/flutter/lib", "packages/flutter_test/lib").splitlines()
        if ":" in line
    ))
    if not files:
        sys.exit(f"FATAL: no deprecation-carrying files found at {rev}. Wrong rev or shallow tree?")
    print(f"framework files carrying deprecations: {len(files)}")

    ann = re.compile(r"@Deprecated\(\s*((?:'(?:[^'\\]|\\.)*'\s*)+),?\s*\)", re.S)
    vre = re.compile(r"deprecated after v(\d+)\.(\d+)", re.I)
    badstart = ("//", "@", "/*", "*")

    def first_stable(marker: tuple[int, int]):
        for k in stable_minors:
            if k > marker:
                return k
        return None

    # One archive extraction beats one `git show` per file. A fresh temp dir per run, so a stale
    # extraction can never silently shadow a new fetch.
    src = Path(tempfile.mkdtemp(prefix="fl_stable_src_"))
    try:
        subprocess.run(
            f'git -C "{root}" archive {rev} -- packages/flutter/lib packages/flutter_test/lib | tar -x -C "{src}"',
            shell=True, check=True)
        groups: dict[tuple[int, int] | None, dict] = defaultdict(dict)
        for f in files:
            p = src / f
            if not p.is_file():
                continue
            text = p.read_text(errors="ignore")
            short = (f.replace("packages/flutter/lib/src/", "")
                      .replace("packages/flutter_test/lib/src/", "flutter_test/"))
            for m in ann.finditer(text):
                msg = " ".join(re.findall(r"'((?:[^'\\]|\\.)*)'", m.group(1)))
                msg = re.sub(r"\s+", " ", msg).strip()
                vm = vre.search(msg)
                if not vm:
                    continue
                marker = (int(vm.group(1)), int(vm.group(2)))
                if marker < MIN_MARKER:
                    continue
                tail = text[m.end():m.end() + 400]
                decl = ""
                for line in tail.splitlines():
                    s = line.strip()
                    if not s or s.startswith(badstart):
                        continue
                    decl = s
                    break
                sym = declared_symbol(decl)
                advice = re.sub(r"\s*This (?:feature|API) was deprecated after v[\d.\-a-z]+\.?\s*$", "", msg).strip()
                groups[first_stable(marker)].setdefault((sym, short), {
                    "symbol": sym, "file": short, "advice": advice,
                    "marker": f"v{marker[0]}.{marker[1]}", "decl": decl[:90],
                })
        return groups
    finally:
        shutil.rmtree(src, ignore_errors=True)


# ---------------------------------------------------------------- writers
def write_matrix(out: Path, today: str, cur_stable: dict, minors: dict, stable_minors: list) -> None:
    cur_dart = re.match(r"^[\d.]+", cur_stable.get("dart_sdk_version", "?") or "?").group(0)
    lines = [
        "# Flutter to Dart SDK Version Matrix (generated, not hand-typed)",
        "",
        f"**Generated:** {today} from `releases_macos.json` (Google's official release index).",
        f"**Current stable at generation time:** Flutter `{cur_stable['version']}` "
        f"({cur_stable['release_date'][:10]}), bundling Dart `{cur_dart}`.",
        "",
        "Every row below is the **first release of that minor line**. Regenerate with",
        "`python3 scripts/build_flutter_sdk_changelog.py --fetch` — never edit version numbers by hand.",
        "",
        "| Flutter minor | First release | Date | Bundled Dart SDK |",
        "| :--- | :--- | :--- | :--- |",
    ]
    for k in reversed(stable_minors):
        ver, date, dart = minors[k]
        lines.append(f"| **{k[0]}.{k[1]}** | `{ver}` | {date} | `{dart}` |")
    lines += [
        "",
        "---",
        "",
        "## Reading this matrix",
        "",
        "1. **A Dart language feature needs both bounds.** `sdk: ^3.10.0` (dot shorthands) implies Flutter `>=3.38.0`;",
        "   `sdk: ^3.13.0` (primary constructors) implies Flutter `>=3.47.0`. Look the Dart column up here before",
        "   writing `environment:` in `pubspec.yaml`.",
        "2. **Detect the project's version** with `flutter --version`, `.fvmrc`, `.fvm/fvm_config.json`, or `.puro.json`.",
        "3. Releases older than the oldest row above are not in Google's machine-readable index; treat any older",
        "   number as unverified and check `https://docs.flutter.dev/install/archive` manually.",
    ]
    (out / "flutter-to-dart-version-matrix.md").write_text("\n".join(lines) + "\n")


def write_deprecations(out: Path, today: str, cur_stable: dict, short_rev: str, groups: dict) -> None:
    d = ["# Flutter Widget & API Deprecations (generated from the stable source tree)",
         "",
         f"**Generated:** {today} by `scripts/build_flutter_sdk_changelog.py` from the",
         "`flutter/flutter` **stable** branch (`git grep` over `@Deprecated` annotations at "
         f"`{short_rev}`, Flutter `{cur_stable['version']}`).",
         "",
         "**How the version column is derived:** `docs/contributing/Tree-hygiene.md` requires the annotation to record",
         "*the beta version current when the deprecation landed* (`This feature was deprecated after v<beta>`).",
         "The first **stable** release that carries it is therefore the next stable minor after that marker.",
         "Both numbers are given: `First stable` (derived) and `Source marker` (verbatim from the code).",
         "",
         "⚠️ Deprecated is not removed: Flutter currently does **not** remove deprecated APIs on a schedule",
         "(same doc). But several pre-3.10 APIs *were* removed in the past and no longer exist at all —",
         "see the removal list at the end.",
         ""]
    for fs in sorted([k for k in groups if k], reverse=True):
        recs = sorted(groups[fs].values(), key=lambda r: (r["file"], r["symbol"]))
        d.append(f"## First stable release: Flutter {fs[0]}.{fs[1]}  ({len(recs)} deprecated members)")
        d.append("")
        d.append("| Deprecated | Replacement / guidance | Source file | Marker |")
        d.append("| :--- | :--- | :--- | :--- |")
        for r in recs:
            adv = r["advice"].replace("|", "\\|")
            d.append(f"| `{r['symbol']}` | {adv} | `{r['file']}` | `{r['marker']}` |")
        d.append("")
    d += [
        "---",
        "",
        "## Removed, not deprecated — these no longer exist in the SDK",
        "",
        "Verified absent from the current stable tree (`git grep 'class FlatButton'` returns nothing).",
        "Code using them does not compile at all, so treat them as hard build breaks, not warnings:",
        "",
        "| Removed API | Modern equivalent |",
        "| :--- | :--- |",
        "| `FlatButton` | `TextButton` |",
        "| `RaisedButton` | `ElevatedButton` |",
        "| `OutlineButton` | `OutlinedButton` |",
        "| `TextTheme.headline1` … `headline6`, `bodyText1/2`, `subtitle1/2` | `displayLarge` … `bodyLarge`, `titleMedium` … |",
        "| `ThemeData.accentColor` | `ColorScheme.secondary` |",
        "| `Scaffold.of(context).showSnackBar(...)` | `ScaffoldMessenger.of(context).showSnackBar(...)` |",
        "| `ThemeData.toggleableActiveColor` | per-widget `WidgetStateProperty` colors |",
        "",
    ]
    (out / "widget-deprecations-and-replacements.md").write_text("\n".join(d) + "\n")


# ---------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fetch", action="store_true",
                    help="run `git fetch --depth 1 origin stable` in the SDK checkout first")
    ap.add_argument("--flutter-root", default=None, help="path to a Flutter SDK git checkout")
    ap.add_argument("--out", default=str(DEFAULT_OUT), help=f"output directory (default: {DEFAULT_OUT})")
    args = ap.parse_args()

    root = resolve_flutter_root(args.flutter_root)
    rev = resolve_rev(root, args.fetch)
    short_rev = git(root, "rev-parse", "--short", rev).strip()
    print(f"flutter sdk   : {root}")
    print(f"rev           : {rev} ({short_rev})")

    cur_stable, minors = load_releases()
    stable_minors = sorted(minors)
    print(f"stable minors found: {len(stable_minors)} (oldest {stable_minors[0]}, newest {stable_minors[-1]})")
    print(f"live stable   : {cur_stable['version']} ({cur_stable['release_date'][:10]})")

    groups = collect_deprecations(root, rev, stable_minors)

    out = Path(args.out).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    today = datetime.date.today().isoformat()
    write_matrix(out, today, cur_stable, minors, stable_minors)
    write_deprecations(out, today, cur_stable, short_rev, groups)

    total = sum(len(v) for k, v in groups.items() if k)
    print(f"wrote {out/'flutter-to-dart-version-matrix.md'} ({len(stable_minors)} minors)")
    print(f"wrote {out/'widget-deprecations-and-replacements.md'} ({total} deprecated members, "
          f"{len([k for k in groups if k])} release buckets)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
