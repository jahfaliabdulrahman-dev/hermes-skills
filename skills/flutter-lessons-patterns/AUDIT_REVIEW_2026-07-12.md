# Flutter Cross-Project Patterns — Triple MoA Audit Review

> **Date:** 2026-07-12
> **Auditor:** Triple-Chinese MoA — Destroyer, System Critic, Lead Architect
> **File Reviewed:** `SKILL.md` v2.0.0 — 1051 lines, 28 patterns
> **Verdict:** **25/28 patterns correct, 1 WRONG, 1 NEEDS CORRECTION, 1 DUPLICATE**
> **Overall Correctness Score: 89.3% (25/28)**

---

## ═══ EXECUTIVE SUMMARY ═══

This file is **substantially correct** and represents real battle-tested lessons from CarSah and Hermex_Android. However, it has **one critical error** (Pattern 21 — Riverpod 3.0 API change), **one code error** (Pattern 14 — bash syntax), and **systematic documentation issues** (source attribution mismatches across 9 patterns). Additionally, **one pattern is a duplicate** (Pattern 28 = Pattern 13).

**MUST FIX before this becomes the single source of truth:**
1. ✋ **Pattern 21: AutoDisposeNotifier REMOVED in Riverpod 3.0** — WRONG, will not compile
2. ✋ **Pattern 14: Unclosed grep quote** — broken bash command
3. 🔧 **Pattern 28: Duplicate of Pattern 13** — merge or delete
4. 🔧 **Patterns 1-8, 12: Embedded lessons don't match displayed rules** — documentation integrity

---

## ═══ PATTERN-BY-PATTERN VERDICT TABLE ═══

| # | Pattern Name | Verdict | Issue |
|---|-------------|---------|-------|
| 1 | Provider Invalidation Rule | ✅ CORRECT | Embedded LL-003 doesn't match rule |
| 2 | Device Verification Gate | ✅ CORRECT | Embedded LL-002 doesn't match rule; process not code |
| 3 | Zero Hardcoded Strings | ✅ CORRECT | Embedded lessons don't match rule |
| 4 | Save-Gating Validators | ✅ CORRECT | Embedded LL-005, LL-017 don't match rule |
| 5 | Tests in Same PR | ✅ CORRECT | Embedded LL-007 doesn't match rule |
| 6 | Spec Sync Gate | ✅ CORRECT | Embedded LL-008 doesn't match rule |
| 7 | Design Before Implementation | ✅ CORRECT | Embedded LL-019 doesn't match; LL-016 does |
| 8 | 1-Day BL Maximum | ✅ CORRECT | Embedded LL-020 doesn't match rule |
| 9 | Android Namespace = MainActivity | ✅ CORRECT | — |
| 10 | Isar + ProGuard = Crash | ✅ CORRECT | Heavy-handed fix; ProGuard keep rules better |
| 11 | Official Android Sources | ✅ CORRECT | Process rule, not code pattern |
| 12 | Design Quality Anti-Patterns | ✅ CORRECT | Embedded LL-027 doesn't match rule |
| 13 | State Mutation Order | ✅ CORRECT | — |
| 14 | Silent API Key Redaction | 🔧 NEEDS CORRECTION | **Unclosed grep quote** |
| 15 | Fake Connection State | ✅ CORRECT | — |
| 16 | API Query Parameters | ✅ CORRECT | — |
| 17 | Verify On Disk | ✅ CORRECT | Meta-pattern, not code |
| 18 | ProviderScope in Tests | ✅ CORRECT | — |
| 19 | Empty Catch Forbidden | ✅ CORRECT | — |
| 20 | GoRouter Static Before Param | ✅ CORRECT | Confirmed against GoRouter docs |
| 21 | Notifier vs AutoDisposeNotifier | ❌ WRONG | **AutoDisposeNotifier REMOVED in Riverpod 3.0** |
| 22 | Repository Null-Safety | ✅ CORRECT | — |
| 23 | isBusy Guard | ✅ CORRECT | — |
| 24 | Router Wiring Gate | ✅ CORRECT | — |
| 25 | Provider Invalidation Layer | ✅ CORRECT | — |
| 26 | SSE Custom Parser | ✅ CORRECT | Add `dart:io` web-platform note |
| 27 | Branch Hygiene | ✅ CORRECT | Git pattern, not Flutter code |
| 28 | SSE Duplicate Prevention | ⚠️ DUPLICATE | Same as Pattern 13 |

---

## ═══ CRITICAL FIXES ═══

### ❌ FIX 1 — Pattern 21: AutoDisposeNotifier removed in Riverpod 3.0 (WRONG)

**Severity:** 🔴 CRITICAL — Code will not compile in Riverpod 3.x

**Problem:** Riverpod 3.0 (released 2025) **removed** `AutoDisposeNotifier`, `AutoDisposeFamilyNotifier`, `AutoDisposeRef`, and `FamilyNotifier`. They are unified into the single `Notifier` class. Auto-dispose behavior is now controlled by the provider declaration, not the notifier class.

**Old (Riverpod 2.x — WRONG for 2026):**
```dart
// ❌ WILL NOT COMPILE in Riverpod 3.x
class TaskListNotifier extends Notifier<TaskListState> { ... }

// ❌ WILL NOT COMPILE in Riverpod 3.x
class SearchQueryNotifier extends AutoDisposeNotifier<String> { ... }
```

**New (Riverpod 3.x — CORRECT for 2026):**
```dart
// ✅ Server data — survives tab switches
// Always extend Notifier. Auto-dispose is on the PROVIDER, not the class.
class TaskListNotifier extends Notifier<TaskListState> {
  @override
  TaskListState build() => TaskListState.initial();
  // ... methods
}

final taskListProvider = NotifierProvider<TaskListNotifier, TaskListState>(
  TaskListNotifier.new,
);

// ✅ Transient UI state — auto-disposed when widget leaves tree
class SearchQueryNotifier extends Notifier<String> {
  @override
  String build() => '';
  // ... methods
}

final searchQueryProvider = NotifierProvider.autoDispose<SearchQueryNotifier, String>(
  SearchQueryNotifier.new,
);
```

**The distinction still exists — it's just on the provider, not the class:**
- `NotifierProvider<X, S>(X.new)` — keeps state alive (server data)
- `NotifierProvider.autoDispose<X, S>(X.new)` — discards when no listeners (transient UI)

**Rule text should be updated to:**
> Use `NotifierProvider.autoDispose<>()` for transient UI state (form data, search queries). Use plain `NotifierProvider<>()` for data fetched from the server. ALL notifiers extend `Notifier` — the auto-dispose decision is on the provider declaration, not the class hierarchy.

**Also affects Pattern 25:** References "parent providers" which is an older terminology. In Riverpod 3.0, providers use `ref.watch()` in `build()` to express dependencies. Clarify that a notifier should never invalidate providers it depends on via `ref.watch()`.

---

### 🔧 FIX 2 — Pattern 14: Unclosed grep quote (NEEDS CORRECTION)

**Severity:** 🟡 MEDIUM — Bash command won't run

**Old (broken):**
```bash
grep -rn "apiKey: *** lib/ || true
grep -rn 'api_key: \*\*\*' lib/ || true
```

**New (corrected):**
```bash
grep -rn "apiKey: \*\*\*" lib/ || true
grep -rn 'api_key: \*\*\*' lib/ || true
```

---

### ⚠️ FIX 3 — Pattern 28: Duplicate of Pattern 13 (DUPLICATE)

**Problem:** Pattern 28 ("SSE Duplicate Message Prevention") and Pattern 13 ("State Mutation Order: Snapshot BEFORE Mutating") both reference LL-029 and teach **the exact same pattern**: take a snapshot before mutating state. Pattern 28 adds an SSE-specific wrapper but the underlying rule is identical.

**Recommendation:** DELETE Pattern 28. Merge the SSE-specific context (the 4-step sequence) into Pattern 13 as an extended example, or keep Pattern 13 as the canonical pattern and remove the duplicate.

---

## ═══ SYSTEMATIC DOCUMENTATION ISSUES ═══

### Source Attribution Mismatches (9 patterns affected)

The file embeds "Full Original" lessons under each pattern that often describe a DIFFERENT lesson than the displayed rule. This means someone expanding the `<details>` section to learn more would get confused. This is a documentation integrity issue that undermines trust.

| Pattern | Claimed Source | Embedded Lesson | What It Should Be |
|---------|---------------|-----------------|-------------------|
| 1 — Invalidation | LL-003 | Notifier vs AutoDisposeNotifier | A generic invalidation lesson or LL-007 |
| 2 — Device Verification | LL-002 | SSE Streaming | A device testing lesson |
| 3 — Zero Hardcoded Strings | LL-001 | Server Connection naming | An i18n/app-localizations lesson |
| 4 — Save-Gating Validators | LL-005 | GoRouter route ordering | A form validation lesson |
| 5 — Tests in Same PR | LL-007 | Provider Invalidation (widget layer) | A testing discipline lesson |
| 6 — Spec Sync Gate | LL-008 | Optimistic UI for skills toggle | A spec sync process lesson |
| 7 — Design First | LL-019 | Empty Catch Blocks | A design-before-code lesson |
| 8 — 1-Day BL Max | LL-020 | Stale Router wiring | A BL sizing lesson |
| 12 — Design Anti-Patterns | LL-027 | Cleartext HTTP blocked | A design quality lesson |

**Root cause:** The embedded `<details>` blocks were likely auto-generated from a lessons-learned file and attached to patterns by LL-001 through LL-042 numbering, but the pattern rules were written independently. The mapping is incorrect.

**Remediation (choose one):**
- **Option A:** Remove all embedded lessons. Keep only the pattern rule text + code. The embedded lessons create conflicts and bloat — the file is 1051 lines for 28 patterns, ~65% of which is duplicate/irrelevant embedded content.
- **Option B:** Correctly re-map each embedded lesson to match its pattern rule. This is labor-intensive and the embedded lessons are already available under their correct patterns (Patterns 13-28).

**Recommendation: Option A.** The embedded lessons are already correctly placed under Patterns 13-28 where they match. Patterns 1-8 should just have the rule text and code. This would cut the file by ~40% and eliminate confusion.

---

## ═══ ADDITIONAL OBSERVATIONS ═══

### 1. Pattern 10 — Isar + ProGuard: Heavy-Handed Fix

The pattern says `isMinifyEnabled = false` — this disables ALL ProGuard/R8 optimizations, not just Isar-related stripping. The professional approach is to add **ProGuard keep rules** for Isar-generated classes while keeping minification on:

```kotlin
# proguard-rules.pro
-keep class com.example.isar.** { *; }
-keep class io.isar.** { *; }
-keep class * extends io.isar.IsarObject { *; }
-dontwarn io.isar.**
```

The current approach is safe and works, but the skill should document both options: the sledgehammer (`isMinifyEnabled = false`) and the scalpel (keep rules).

### 2. Pattern 26 — SSE Parser: `dart:io HttpClient` Not Cross-Platform

`dart:io HttpClient` does **not work on Flutter Web**. If any future project targets web, this pattern will break. Add a note:

> ⚠️ `dart:io` is NOT available on Flutter Web. For web-compatible SSE, use `package:web_socket_channel` with a polyfill or `dart:html EventSource`. The `dio` package with `ResponseType.stream` is another cross-platform option.

### 3. Pattern 23 — isBusy: Theoretical Race Condition

The pattern `if (state.isBusy) return; state = state.copyWith(isBusy: true);` has a theoretical TOCTOU race. In practice, Riverpod serializes notifier method calls per instance, so this is safe. But a comment noting the single-threaded guarantee would be helpful for readers unfamiliar with Riverpod's execution model.

### 4. Pattern 2 — `flutter analyze` ≠ `dart analyze`

The YAML example says `flutter analyze: pass` which is correct for Flutter projects. However, for packages that don't depend on Flutter, use `dart analyze`. Minor point, but the skill should note the distinction.

---

## ═══ MISSING PATTERNS ═══

These are patterns that exist in production Flutter codebases and should be included:

| # | Missing Pattern | Why It Matters |
|---|----------------|----------------|
| M1 | **Controller disposal** — `TextEditingController`, `AnimationController`, `FocusNode`, `ScrollController` MUST be disposed in `dispose()` | Memory leaks are silent and cumulative |
| M2 | **Const constructors** — Widgets should use `const` constructors where possible for rebuild optimization | Performance — prevents unnecessary widget rebuilds |
| M3 | **Build method purity** — No side effects (API calls, navigation, state mutation) in `build()` | Flutter calls `build()` frequently; side effects cause infinite loops |
| M4 | **Keys in widget trees** — When to use `ValueKey`, `GlobalKey`, `ObjectKey` | Incorrect keys cause state loss in list reordering |
| M5 | **Error boundaries** — `FlutterError.onError` and `PlatformDispatcher.instance.onError` for crash reporting | Uncaught errors kill the app silently |
| M6 | **FutureProvider/StreamProvider** — When to use each vs raw `FutureBuilder`/`StreamBuilder` | Riverpod providers handle loading/error/data states better |
| M7 | **Isolate/Compute for heavy work** — Offloading JSON parsing, image processing, encryption to background isolates | UI thread blocking causes jank |
| M8 | **Golden image tests** — Visual regression testing for UI components | Catches visual regressions that unit tests miss |
| M9 | **Adaptive widgets** — `Switch.adaptive()`, `CircularProgressIndicator.adaptive()` for platform-native feel | Professional Android + iOS apps need platform-appropriate widgets |

---

## ═══ DUPLICATED EMBEDDED LESSONS ═══

The following original lessons appear in **multiple** patterns as embedded full-text duplicates. This inflates the file and creates maintenance burden — if the lesson is updated, both copies must be updated.

| Lesson ID | Appears In |
|-----------|-----------|
| LL-002 (SSE Streaming) | Pattern 2, Pattern 26 |
| LL-003 (Notifier/AutoDispose) | Pattern 1, Pattern 21 |
| LL-005 (GoRouter Ordering) | Pattern 4, Pattern 20 |
| LL-006 (Repository Null-Safety) | Pattern 3, Pattern 22 |
| LL-007 (Widget Layer Invalidation) | Pattern 5, Pattern 25 |
| LL-017 (Router Wiring Gap) | Pattern 4, Pattern 24 |
| LL-018 (ProviderScope Test) | Pattern 3, Pattern 18 |
| LL-019 (Empty Catch Blocks) | Pattern 7, Pattern 19 |
| LL-024 (Namespace Mismatch) | Pattern 9, Pattern 11 |
| LL-025 (Isar + ProGuard) | Pattern 10, Pattern 11 |
| LL-029 (State Mutation Order) | Pattern 13, Pattern 28 |

**Recommendation:** After fixing the attribution mismatches (Patterns 1-8, 12), each original lesson should appear in exactly ONE pattern. This is already true for Patterns 13-28 — the duplicates are in Patterns 1-8 and 11-12.

---

## ═══ RIVERPOD 3.0 COMPATIBILITY SUMMARY ═══

All Riverpod-related patterns were audited for Riverpod 3.0 compatibility:

| Pattern | Status | Notes |
|---------|--------|-------|
| 1 — Provider Invalidation | ✅ Compatible | `ref.invalidate()` unchanged in 3.0 |
| 18 — ProviderScope in Tests | ✅ Compatible | `ProviderScope` unchanged |
| 21 — Notifier vs AutoDisposeNotifier | ❌ BROKEN | `AutoDisposeNotifier` class removed |
| 22 — Repository Null-Safety | ✅ Compatible | Not Riverpod-specific |
| 23 — isBusy Guard | ✅ Compatible | Pattern still valid, TOCTOU note added |
| 25 — Widget Layer Invalidation | ✅ Compatible | Correct advice; clarify "parent provider" terminology |

---

## ═══ FINAL RECOMMENDATIONS ═══

### Must fix (before promotion to single source of truth):
1. **Pattern 21:** Rewrite for Riverpod 3.0 — remove `AutoDisposeNotifier`, use `NotifierProvider.autoDispose<>()`
2. **Pattern 14:** Fix unclosed grep quote
3. **Pattern 28:** Delete (duplicate of Pattern 13)

### Should fix (documentation integrity):
4. **Patterns 1-8, 12:** Fix embedded lesson mismatches (remove or re-map)
5. **All duplicated embedded lessons:** Keep one copy per lesson ID

### Consider adding:
6. **Pattern 10:** Add ProGuard keep rules as alternative to `isMinifyEnabled = false`
7. **Pattern 26:** Add `dart:io` web-platform compatibility note
8. **9 missing patterns** (M1-M9 above)

---

## ═══ PROCESS NOTE ═══

Several patterns (2, 5, 6, 8, 11, 17, 27) are **process/workflow rules**, not Flutter/Dart programming patterns. They are valuable but belong in a governance document (`00_governance_lessons.md`), not in a programming patterns skill. Consider splitting: keep patterns 1, 3, 4, 7, 9, 10, 13-16, 18-26, 28 as programming patterns, and move 2, 5, 6, 8, 11, 17, 27 to governance.

---

**Audit completed:** 2026-07-12
**Reviewer signature:** Triple-Chinese MoA — Destroyer ✅ | System Critic ✅ | Lead Architect ✅
