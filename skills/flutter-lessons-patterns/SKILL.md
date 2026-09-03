---
name: flutter-lessons-patterns
description: Cross-project Flutter patterns distilled from CarSah + Hermex_Android + Azdal — 54 programming patterns, each classified GATE/RULE/JUDGMENT + RFC 2119 negation (MUST/SHOULD/MAY), plus missing-gate detection lenses. Single source of truth for all Flutter/Dart/Android coding lessons. Load before every implementation task. Full bodies live in references/ (split 2026-08-22 for size).
version: 2.25.1
triggers:
  - Starting any Flutter implementation task
  - Creating a new BL (backlog item) or Kanban card
  - Reviewing code before merge
  - User mentions "lessons learned" or "patterns"
  - User asks "what went wrong last time"
  - Prompt engineering or LLM integration architecture decisions
  - History leak / cross-message contamination debugging in chat pipelines
  - Adding or modifying widget action payload forwarding
  - Interactive widget lifecycle (answered-once, form disable after submit)
  - Arabic-indic numeral normalization in form parsing
  - Duplicate bubble text from addBotMessage + widget question field
references:
  - Patterns 1-18 (core Flutter + Android + mobile) → references/patterns-01-18-core-android-mobile.md
  - Patterns 19-30 (extended mobile + meta) → references/patterns-19-30-extended-meta.md
  - Patterns 31-44 (multi-agent + widgets + RC6 era) → references/patterns-31-44-agents-widgets-rc6.md
  - Patterns 45-54 (Stage 4 + design + meta lessons) → references/patterns-45-54-stage4-design-meta.md
related_skills:
  - flutter-design-anti-patterns
  - flutter-android-build-system
  - android-preflight-verification
  - flutter-isar-clean-arch-setup
---

# Flutter Cross-Project Patterns — Unified Programming Lessons

> **Sources:** CarSah (LL-001–LL-020) + Hermex_Android (LL-001–LL-042) + Azdal
> **Patterns: 54** — full bodies are in the four reference files below (split 2026-08-22 because SKILL.md exceeded 100K and patches were being rejected).
> **Purpose:** SINGLE source of truth for ALL Flutter/Dart/Android programming lessons. Load before every implementation task. Governance/process lessons belong in `agent-repo-handoff-loop` (referenced from there) — this skill is code-level.

## Enforcement levels (adopted 2026-08-11 — founder decision)

Every pattern is classified by two exclusion filters then a weighted score:
1. **🚪 GATE** — machine-enforced: a lint/test/script fails the build if violated. Universal truth + costly to retrofit.
2. **📏 RULE** — documented convention enforced by review. Universal truth but not machine-detectable.
3. **🧭 JUDGMENT** — project decision: the skill gives criteria, the answer depends on project context.

**Negation axis (RFC 2119 mapping):** 🚪 MUST / MUST NOT · 📏 SHOULD / SHOULD NOT · 🧭 MAY.

## How to read this skill (IMPORTANT — this file is now an index)

1. **Read the pattern you need** from the reference file that carries it (map below).
2. **Always cite patterns by number** in reviews, letters, and code comments (Pattern 52, etc.) — the shared vocabulary.
3. **New patterns (55+) must be added directly to the appropriate references/ file** as `## Pattern N — ...` blocks — NEVER appended to SKILL.md (it will overflow again).
4. When the referenced file grows past ~50K, split again — one file per era, same convention.

## Pattern Index (54 patterns)

| # | Pattern | File |
|--|--|--|
| 1 | Provider Invalidation Rule (LL-003) | patterns-01-18-core-android-mobile |
| 2 | Device Verification Gate (LL-002 + LL-013) | patterns-01-18-core-android-mobile |
| 3 | Zero Hardcoded Strings (LL-001 + LL-006 + LL-018) | patterns-01-18-core-android-mobile |
| 4 | Save-Gating Validators (LL-005 + LL-017) | patterns-01-18-core-android-mobile |
| 5 | Tests in Same PR (LL-007) | patterns-01-18-core-android-mobile |
| 6 | Spec Sync Gate (LL-008) | patterns-01-18-core-android-mobile |
| 7 | Design Before Implementation (LL-016 + LL-019) | patterns-01-18-core-android-mobile |
| 8 | 1-Day BL Maximum (LL-020) | patterns-01-18-core-android-mobile |
| 9 | Android Namespace = MainActivity Package (LL-024) | patterns-01-18-core-android-mobile |
| 10 | Isar + ProGuard = Crash (LL-025) | patterns-01-18-core-android-mobile |
| 11 | Official Android Sources Mandatory (LL-026) | patterns-01-18-core-android-mobile |
| 12 | Design Quality Anti-Patterns (LL-027 — Cross-Reference) | patterns-01-18-core-android-mobile |
| 13 | State Mutation Order: Snapshot BEFORE Mutating (LL-029) | patterns-01-18-core-android-mobile |
| 14 | Silent API Key Redaction: `***` Literal (LL-022) | patterns-01-18-core-android-mobile |
| 15 | Fake Connection State: Never Set 'connected' Without Health Check (LL-023) | patterns-01-18-core-android-mobile |
| 16 | API Query Parameters: Always Pass `include_disabled=true` (LL-042) | patterns-01-18-core-android-mobile |
| 17 | Verify On Disk Before Claiming (Meta-Pattern — Sulaiman Session 2026-07-11) | patterns-01-18-core-android-mobile |
| 18 | ProviderScope in Widget Tests: Mirror main.dart Exactly (LL-018) | patterns-01-18-core-android-mobile |
| 19 | Empty Catch Blocks FORBIDDEN in Security Paths (LL-019) | patterns-19-30-extended-meta |
| 20 | GoRouter: Static Routes BEFORE Parameterized (LL-005) | patterns-19-30-extended-meta |
| 21 | Provider Hygiene: NotifierProvider vs NotifierProvider.autoDispose (LL-003) | patterns-19-30-extended-meta |
| 22 | Repository Null-Safety: Accept Nullable Dependencies (LL-006) | patterns-19-30-extended-meta |
| 23 | isBusy Guard: Provider-Level Atomicity (LL-004) | patterns-19-30-extended-meta |
| 24 | Router Wiring Gate: Feature NOT Done Until Wired (LL-017) | patterns-19-30-extended-meta |
| 25 | Provider Invalidation: Widget Layer, Not Provider Internals (LL-007) | patterns-19-30-extended-meta |
| 26 | SSE Parser: Custom Format Handling (LL-002 + HERMEX-007) | patterns-19-30-extended-meta |
| 27 | Branch Hygiene: Verify Baseline Before Starting Work (LL-033) | patterns-19-30-extended-meta |
| 28 | [DUPLICATE — See Pattern 13] SSE Duplicate Message Prevention: Snapshot BEFORE Streaming (LL-029 — Extended) | patterns-19-30-extended-meta |
| 29 | API Response Key Format: Use `data`, Not `messages` (LL-041) | patterns-19-30-extended-meta |
| 30 | Build Responsibility: Lead Architect Coordinates, DevOps Builds (LL-044) | patterns-19-30-extended-meta |
| 31 | Lessons Flow to Shared Knowledge Base (LL-045) | patterns-31-44-agents-widgets-rc6 |
| 32 | Impact Analysis Before Implementation (LL-046) | patterns-31-44-agents-widgets-rc6 |
| 33 | Stored First Decision: Never Re-Call Non-Deterministic APIs | patterns-31-44-agents-widgets-rc6 |
| 34 | Riverpod Reactive Service: Bridge Platform SDK Callbacks to StateNotifier | patterns-31-44-agents-widgets-rc6 |
| 35 | Compute Derived Values Locally: Never Trust LLM Math | patterns-31-44-agents-widgets-rc6 |
| 36 | Ephemeral Message Lifecycle: Track Id, Remove, Replace | patterns-31-44-agents-widgets-rc6 |
| 37 | LLM Must Not Emit Actionable UI: App Constructs UI From Verified Data | patterns-31-44-agents-widgets-rc6 |
| 38 | Android INTERNET Permission on Custom OEM ROMs | patterns-31-44-agents-widgets-rc6 |
| 39 | Widget "Answered Once": Buttons Disabled After First Action | patterns-31-44-agents-widgets-rc6 |
| 40 | Full-File Rewrite Callback Verification | patterns-31-44-agents-widgets-rc6 |
| 41 | Error-Handling Architecture: validateStatus + interceptor + sanitizeError (LL-047) | patterns-31-44-agents-widgets-rc6 |
| 42 | Certificate Pinning Uniform Wiring: Single ApiClient Provider (LL-048) | patterns-31-44-agents-widgets-rc6 |
| 43 | Reactive Profile Switching: Watch connectionProvider (LL-049) | patterns-31-44-agents-widgets-rc6 |
| 44 | Gate Rescan Integrity: Re-test SPECIFIC Rejected Findings (LL-050 / ADR-012) | patterns-31-44-agents-widgets-rc6 |
| 45 | Bundled-Task Pattern for Shared-File Conflicts (LL-051) | patterns-45-54-stage4-design-meta |
| 46 | Never Say "No Data": Cold Start Intelligence (LL-009) | patterns-45-54-stage4-design-meta |
| 47 | Live-Device Verification Supremacy (LL-010) | patterns-45-54-stage4-design-meta |
| 48 | Regex Pre-Filter Gates + Disabled Button Colors (LL-011) | patterns-45-54-stage4-design-meta |
| 49 | Design System Architecture: Tokens Gate, Sub-Themes Rule, Components Judgment (LL-052) | patterns-45-54-stage4-design-meta |
| 50 | Missing-Gate Detection: Run Lenses, Not Memory (LL-053) | patterns-45-54-stage4-design-meta |
| 51 | go_router Shells: relative child paths + measured-resolved-behaviour (LL-054) | patterns-45-54-stage4-design-meta |
| 52 | Repeated CI Failures Are a Forensic Investigation, Not a Push Race (LL-055) | patterns-45-54-stage4-design-meta |
| 53 | One Attempt Is Half the Truth: Open Every Attempt Before Claiming Attribution (LL-056) | patterns-45-54-stage4-design-meta |
| 54 | The Linter's Suggestion Is Not Always the Fix: Conflicting Analyzers (LL-057) | patterns-45-54-stage4-design-meta |
| 55 | Process & Governance Patterns: Phased QA, EPIC Gates, Evidence Discipline (multi-project post-mortems) | process-governance-patterns |

> **Note on numbering:** the reference files keep their original `## Pattern N` headings (the extraction was mechanical — content is identical to v2.24). The index above is for navigation; the **real mapping is Pattern N → reference file**, not the index row numbers.

---

*Skill divided 2026-08-22 (founder decision). Original v2.24 content preserved byte-for-byte inside the four reference files. Version 2.25 — index-only SKILL.md, full content in references/.*
