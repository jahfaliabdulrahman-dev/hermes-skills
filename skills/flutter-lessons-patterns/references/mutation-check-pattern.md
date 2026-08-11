# Mutation Check Pattern — Repeatable Test Perturbation Artifact

Trigger: Any task that claims "tests verify correctness." A mutation check proves tests actually catch bugs — not just that they pass against green code.

## The Script Template

Save as `tool/mutation_check.sh` in the project root. Customize the two perturbation blocks per suite.

```bash
#!/usr/bin/env bash
# Mutation Check — Repeatable per-suite perturbation artifact
# Run from project root: bash tool/mutation_check.sh
set -euo pipefail

EVIDENCE_DIR="test/fixtures/mutation_evidence"
mkdir -p "$EVIDENCE_DIR"

PASS=0; FAIL=0

run_suite() { flutter test "$1" 2>&1; }

# ═══ Suite 1: <name> ═══
SRC="lib/path/to/service.dart"
TEST="test/path/to/service_test.dart"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# GREEN baseline
run_suite "$TEST" | tail -5

# Perturb ONE line using Python (NOT sed — special chars break sed silently)
python3 -c "
with open('$SRC', 'r') as f:
    content = f.read()
old = '    <exact original line with indentation>'
new = '    <mutated line> // MUTATED'
if old not in content:
    print('ERROR: target line not found', file=sys.stderr)
    sys.exit(1)
content = content.replace(old, new)
with open('$SRC', 'w') as f:
    f.write(content)
"

# RED phase — MUST FAIL
RED_FILE="$EVIDENCE_DIR/<suite>_red_${TIMESTAMP}.txt"
set +e; run_suite "$TEST" > "$RED_FILE" 2>&1; RED_EXIT=$?; set -e
if [ $RED_EXIT -ne 0 ]; then
  echo "PASS: Suite went RED as expected (exit=$RED_EXIT)"
  ((PASS++))
else
  echo "FAIL: Suite did NOT go RED — mutation check broken!"
  ((FAIL++))
fi
tail -15 "$RED_FILE"

# Revert
git checkout -- "$SRC"

# GREEN phase — MUST PASS
GREEN_FILE="$EVIDENCE_DIR/<suite>_green_${TIMESTAMP}.txt"
set +e; run_suite "$TEST" > "$GREEN_FILE" 2>&1; GREEN_EXIT=$?; set -e
if [ $GREEN_EXIT -eq 0 ]; then
  echo "PASS: Suite GREEN after revert"
  ((PASS++))
else
  echo "FAIL: Suite did NOT recover after revert!"
  ((FAIL++))
fi

# ... repeat for each suite ...

# Final report
echo "PASS: $PASS / <total>"; echo "FAIL: $FAIL / <total>"
if [ $FAIL -eq 0 ]; then exit 0; else exit 1; fi
```

## Why Python, not sed

Dart code perturbation via `sed` fails silently because:
- Parentheses `(` `)` are literal in BRE but have meaning in ERE — sed behavior is context-dependent
- Slashes `/` in code paths like `totalCount / totalEver` require delimiter switching
- Multi-line patterns require hold-space tricks
- When sed fails to match, it exits 0 with no change — the mutation never applies and tests stay GREEN

Python `content.replace(old, new)` with exact string matching is unambiguous. The `if old not in content` guard catches mismatches.

## Integrity Check After Run

```bash
# lib/ must be net-unchanged
git diff --name-only lib/    # must return nothing
grep -c "MUTATED" lib/**/*.dart   # must return 0
```

## Example: DEC-048 Re-Introduction (Integrity Score)

Perturb the no_deletion_rate formula from the FIXED version:
```dart
noDeletionRate = (totalCount / totalEver * 100).clamp(0, 100);
```
Back to the BUGGY version:
```dart
noDeletionRate = ((totalCount - deletedCount) / totalCount * 100).clamp(0, 100);
// MUTATED: DEC-048 bug re-introduced
```

The surviving real test `heavy deletions — rate clamped to 0–100` asserts `no_deletion_rate: 23` for `totalCount: 3, deletedCount: 10`. The buggy formula gives `(3-10)/3*100 = -233 → clamped to 0`. Expected 23, got 0 — RED.

## Example: DTI Cap Weakening (Purchase Decision)

Perturb `if (dti > 0.33)` to `if (dti > 0.99)`. The test `DTI > 33% → hard no` uses `income: 5000, commitments: 2000 → DTI=0.4`. With the cap at 0.99, 0.4 passes — verdict becomes 'yes' instead of 'no'. RED.
