---
name: scsi-self-correcting-swarm
description: Self-Correcting Swarm Intelligence architecture for Hermex Android. 5-layer pipeline that proactively discovers bugs, automatically classifies them, and self-updates prevention gates. Replaces reactive spoon-feeding of lessons learned.
---

# SCSI: Self-Correcting Swarm Intelligence

## What Is SCSI?

A 5-layer pipeline that replaces the reactive "human finds bug → Sulaiman documents → manual gate" cycle with automated self-correction. Designed for the 9-profile Flutter swarm (now 10 with flutter-curiosity-hunter).

## Architecture

```
L1: Curiosity Engine → L2: Red Team Audit → L3: RCA Pipeline → L4: Gate Factory → L5: Intelligence Accumulator
                                                                                              ↓
                                                                                    (feeds back to L1)
```

## Layer 1: Curiosity Engine (IMPLEMENTED)

**Profile:** `flutter-curiosity-hunter` (Sayyad)
**Script:** `scripts/scsi-hunt.py`
**Database:** `~/.hermes/bug-corpus/patterns.db`

Patterns are backfilled from LL-001 through LL-029. The hunter scans code against known anti-patterns on every build. CRITICAL matches block the build.

## Layer 2-5 (IMPLEMENTED 2026-07-06)

| Layer | Script | Status |
|-------|--------|--------|
| L1 | `scripts/scsi-hunt.py` | ✅ Pattern scanner with pattern DB |
| L2 | `scripts/scsi-redteam.py` | ✅ 9 attack vectors: AV-001 through AV-010 |
| L3 | `scripts/scsi-engine.py` | ✅ Auto-classify into 7 bug classes |
| L4 | `scripts/scsi-engine.py` | ✅ Auto-generate gates + update pattern DB |
| L5 | `scripts/scsi-engine.py` | ✅ File risk scoring + anomaly detection |

See `SCSI-self-correcting-swarm-intelligence.md` (931 lines) for full architecture spec.

## CI Integration (Complete)

```yaml
- name: Preflight (5 gates)
  run: bash scripts/android-preflight.sh
- name: SCSI L1 — Hunt
  run: python3 scripts/scsi-hunt.py --quick
- name: SCSI L2 — Red Team Audit
  run: python3 scripts/scsi-redteam.py --attack ALL || true
- name: SCSI L3-L5 — RCA + Gate Factory + Intelligence
  run: python3 scripts/scsi-engine.py --auto-fix || true
- flutter analyze → flutter test → flutter build apk
```

**CI Optimization:** `paths-ignore` on `app-spec/**`, `**.md`, `skills/**`, `docs/**` — skips APK rebuild on docs-only pushes.

## Bug Taxonomy (7 categories, 33+ patterns)

| Category | Examples |
|----------|----------|
| ANDROID_BUILD | namespace mismatch, ProGuard/Isar, cleartext HTTP |
| DART_RIVERPOD | state.copyWith before _buildHistory |
| UI_INTERACTION | dead buttons (null onPressed/onTap), bottom bar layout stacking |
| API_DATA | Flexible API response extraction (getDynamic) |
| NETWORK | macOS firewall Python binary |
| SECURITY | network_security_config |
| PROCESS | project setup |

**Latest additions (2026-07-09):** LL-031 (getDynamic for cron list), LL-032 (dead UI button detection), LL-033 (bottom bar layout — single Row eliminates overlap).

## Proven Success: C-2 Discovery (2026-07-09)

During the UI Polish phase, the Guardian found a bug that NO ONE reported:
- **C-2:** Error dismiss button on chat_screen.dart:237 had an EMPTY `GestureDetector.onTap` callback. User couldn't dismiss error banners.
- The Lead Architect folded the fix into TSK-ATTACH immediately.
- Fix: `onTap` wired to `ChatNotifier.clearError()` — one line.
- This validates SCSI: the system found a production bug before the user did.

## Key Files

- `scripts/scsi-hunt.py` — pattern scanner
- `scripts/android-preflight.sh` — 5 build gates
- `app-spec/00_lessons_learned.md` — LL catalog
- `~/.hermes/bug-corpus/patterns.db` — SQLite pattern database

## Adding a New Pattern

```sql
INSERT INTO patterns (ll_id, title, category, severity, root_cause, fix_summary, pattern_regex, file_glob, prevention_gate)
VALUES ('LL-030', 'Title', 'CATEGORY', 'CRITICAL', 'Root cause', 'Fix', 'regex', 'file.glob', 'gate');
```

## Pitfalls

- **Guardian stays RUNNING — never blocks itself between cycles.** Old protocol required `kanban_block()` at end of each cycle. NEW protocol: the guardian runs CONTINUOUSLY, pauses 60s between cycles, auto-re-scans. No blocking needed.

- **TRUTH CHECK is mandatory before any APPROVE.** `grep` the old pattern in the target file. If found → REJECT regardless of test results. Tests can pass while production code is unchanged.

- **SCSI cannot operate if swarm gateways are closed.** This was the root cause of the 5 blocked/pending tasks discovered 2026-07-06. SCSI reports "clean" because it scans code, not infrastructure. But if profile gateways are stopped, Kanban tasks pile up silently. Always run `hermes gateway status` alongside SCSI. A project is only truly complete when `hermes kanban list --status blocked` and `hermes kanban list --status todo` both return empty. The `flutter-curiosity-hunter` profile itself needs a running gateway to receive SCSI tasks via Kanban.

- **SCSI Hunt false positives from verification-gate patterns.** Patterns that use `prevention_gate` (commands) instead of `pattern_regex` (text matching) will not fire during SCSI scans. This is by design — they're meant to be run by preflight, not SCSI. Keep `pattern_regex` NULL for verification-gate patterns to avoid false matches.

## Self-Improvement Loop

1. Bug found (by user OR SCSI) → 2. Pattern added to DB → 3. Next hunt smarter → 4. Gates auto-evolve

## SCSI Guardian Protocol (Kanban Integration)

The `flutter-curiosity-hunter` (SCSI Layer 1-5) operates as a **per-board Kanban guardian** — spawned fresh for each Kanban board/epic, closed when the board is complete. NEVER create two guardians on the same project simultaneously. One board = one guardian.

### Guardian runs CONTINUOUSLY — never blocks itself

Between scan cycles the guardian pauses 60 seconds and auto-re-scans. It stays in RUNNING state for the entire board lifecycle. No kanban_block() between cycles. When all epic tasks complete, the Lead Architect closes the guardian.

### Governance Constitution Compliance

The Guardian operates under the Swarm Governance Constitution (`~/.hermes/swarm/constitution.yaml`):
- **Art. II §6:** Guardian ALL CLEAR is Gate 6 of EPIC completion — no EPIC closes without it
- **Art. IV:** CRITICAL findings trigger L2 escalation within 15 minutes if unacknowledged
- **Art. I:** Guardian has `escalate_critical_directly_to_human` — no Lead intermediary required
- **Art. VI:** Constitutional Court monitors Guardian heartbeat — if Guardian silent, Court escalates

### Gatekeeper Protocol — Auto-Complete

When a task is blocked with `review-required`, the guardian scans and:
- **APPROVE:** Auto-unblocks + auto-completes. Zero human intervention.
- **REJECT:** Comments with specific reason. Lead creates rework task.

### Detector Role — Findings Escalate to Lead

```
Hunter DETECTS → reports CRITICAL to Lead with (WHAT, WHERE, WHY)
    ↓
Lead + Experts CONVENE → Lead DECIDES → Lead DISPATCHES fix
    ↓
Fix merges → hunter auto-detects → re-scans → auto-approves
```

**CRITICAL RULE:** The hunter NEVER creates fix tasks. Detection only.

### TRUTH CHECK — Mandatory grep before APPROVE

Before approving any bug fix, grep the OLD pattern in the target file:
```bash
grep -n "old-pattern" lib/path/to/file.dart
```
If found → REJECT: task claim is FALSE. Production code unchanged.

### Guardian Task Template

Use the FULL template from `task-dispatch-template` (النموذج المعتمد):

```bash
hermes kanban create "🛡️ SCSI GUARDIAN: [Epic Name]" \
  --assignee flutter-curiosity-hunter \
  --goal --goal-max-turns 200
```
