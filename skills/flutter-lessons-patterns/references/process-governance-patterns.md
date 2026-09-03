# Process & Governance Patterns (from multi-project post-mortems)

Generalized from cross-project post-mortem analysis. These are orchestration
and QA-process patterns, not code patterns — they apply to any multi-agent
Flutter project and any EPIC-style workflow.

## 1. Phased QA Gate (anti: Big Bang Testing)

Never decompose a project as "all features → single QA phase at the end."
Defects found late cost exponentially more and cascade rework across
completed features.

**Rule:** Decompose QA into phases matching feature-delivery groups. Each
phase must pass its QA gate before the next phase begins implementation.
Sequence: F-001 build → QA ✅ → F-002+F-003 build → integration QA ✅ → … →
final integration QA → zero-trust audit → release.

## 2. Release Must Push (remote backup is a deliverable)

A release/devops task that builds and signs but never initializes git or
pushes leaves the project with zero remote backup.

**Rule:** Every RELEASE task must list as mandatory deliverables:
(1) `git init` if not a repo, (2) remote repo creation, (3) `git push`.
These belong in the task body, not the worker's discretion.

## 3. Orchestrators Verify, Never Implement

An orchestrator/lead profile executing code changes directly bypasses every
quality gate at once: no task, no spec consultation, no independent review,
no documentation, no decision log, no backup. Even correct code loses
traceability and institutional memory.

**Rule:** Code flows task → specialized worker → QA → audit → deploy. The
orchestrator coordinates, approves, and verifies — it does not write
application code, regardless of urgency.

## 4. EPIC Closure Gate: All Children Terminal

An EPIC/parent task marked done while child tasks still run misleads
downstream workers into starting on stale preconditions.

**Rule:** A parent task may not transition to done until every child task
reaches a terminal state (done/blocked/cancelled). Pre-completion gate:
query child states, block completion if any remain active.

## 5. EPIC Dependency Direction (anti: parents deadlock)

Setting child tasks' `parents: [EPIC_ID]` creates a circular wait: children
wait for the EPIC, the EPIC waits for children — the pipeline deadlocks.

**Rule:** Never parent sub-tasks to their own EPIC. EPIC cards are
decomposition markers, not dependencies. Children either have no parents or
depend on a sequential predecessor within the same EPIC.

## 6. Re-verify Counts at Session Start

A test count recorded in a task body drifts across environments (branches,
partial checkouts, cached builds). Reviewers chasing a stale number waste a
whole session.

**Rule:** Any task citing a count (tests, files, endpoints) must re-compute
it live at session start. Never inherit a count from a prior session.

## 7. Branch Hygiene: Verify Baseline Before Work

Orphaned WIP commits on shared branches (from rebases or abandoned saves)
contain analyzer errors that trigger false alarms.

**Rule:** Before starting on a shared branch, verify HEAD matches the
expected baseline (`git log --oneline -5`). If stale WIP exists: reset to
the last clean commit or cherry-pick completed fixes; document the baseline
in the task body.

## 8. A Token Is Not Done Until the Widget Tree Consumes It

Theme tokens (or any spec constants) defined in code + spec but never wired
into the widget tree are unreachable dead configuration marked "complete."

**Rule:** A definition is not done until end-to-end wiring is proven. Write
a test that toggles the behavior (e.g. `ThemeMode.light`) and asserts a
visible element actually changes. Wire-up is a separate acceptance criterion.

## 9. Release Gates Block Builds

A release published before its spec-sync/audit gates passed forces a
takedown and a regression release.

**Rule:** The release task must check gate status before running any build
command. RED gate = blocked build. Pre-build verification is a step in the
release workflow, not an afterthought.

## 10. Gate Tasks Require Evidence

Gate tasks (QA, verification, audit) ticked done without evidence are worse
than no gate — they manufacture false confidence.

**Rule:** Every gate task body carries a "Results / Evidence" field that
must hold verifiable output (log, diff, screenshot, health check) before the
task can complete. Empty evidence = cannot transition to done.

## 11. Build Boundary: Coordinators Don't Close Build Tasks

A coordinator closing BUILD tasks without a verifiable artifact (APK, IPA)
breaks the release pipeline's chain of accountability.

**Rule:** Build tasks are assigned exclusively to the build/release worker.
Coordinators may create and sequence them but may not close them without the
verifiable artifact and the build worker's approval.

## 12. Lessons Elevation Is an EPIC Exit Criterion

Lessons reach the shared knowledge base only when a dedicated documentation
task exists. Without that gate, even the meta-lesson about elevating lessons
gets lost.

**Rule:** Every EPIC ends with a documentation task listing the LL-IDs to
elevate. The EPIC is not closed until the steward completes the elevation.
