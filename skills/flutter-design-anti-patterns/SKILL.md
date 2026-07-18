---
name: flutter-design-anti-patterns
description: Flutter design quality rules — 31 anti-patterns across 14 categories. 3 core custom_lint rules (zero false positives) + AST-based detector for structural patterns. Born from Impeccable-inspired gap analysis + multi-model adversarial consultation (2026-07-11).
version: 2.0.0
category: flutter
triggers:
  - Before any Flutter PR merge
  - When UI/UX agent reviews a Flutter screen
  - When running design quality preflight checks
  - Constitutional Court design scan cron job
---

# Flutter Design Anti-Patterns — Deterministic Detection Rules

> **Inspired by:** Impeccable's 46 deterministic detector rules for web (HTML/CSS/DOM)
> **Our equivalent:** `custom_lint` plugin (3 core rules) + golden image tests (visual layer)
> **Principle:** Catch design defects BEFORE they reach the user. No LLM required for detection.
> **Source:** CarSah lessons, Hermex Android, Material Design 3, Flutter a11y best practices

---

## ═══ Multi-Model Consultation (2026-07-11) ═══

This skill was reviewed by 2 adversarial AI models in a 5-phase protocol. Key findings:

| Finding | Action Taken |
|---------|-------------|
| Regex v1 detector: 98% false positive rate (AP-020 = 927/945). "Noise generator with JSON output." | Marked as SPIKE. Superseded by `custom_lint`. |
| Impeccable inspects RENDERED DOM, not source code. We copied form, missed substance. | Added golden image test reference. |
| Missing categories: Images & Assets, Forms & Input, Keyboard & IME, Animation & Motion. | Added v2.0.0. |
| 31 patterns — ~7 solid, ~15 debatable, ~9 wrong/unimplementable. | Marked with `[CONSULTATION FLAG]`. |
| Core insight: "Stop trying to detect bad design. Make good design the only possible output." | Added Layer 1: Design Token Gate. |

**Verdict:** DEFER full 31-pattern detector. BUILD 3 core `custom_lint` rules + golden tests instead.

---

## ═══ Priority System ═══

### 🥇 Layer 1 — DESIGN TOKEN GATE (build now, zero false positives)
3 rules that **prevent** bad design, not just detect it:
1. **No raw `Color(0x...)`** outside theme definition files → ERROR
2. **No `EdgeInsets.only(left:/right:)`** → force `EdgeInsetsDirectional` → ERROR
3. **No raw `fontSize: N`** → force `Theme.of(context).textTheme` → WARNING

**Plugin:** `lint_plugin/` — `custom_lint` package. Add to `analysis_options.yaml`:
```yaml
analyzer:
  plugins:
    - flutter_design_lint
```

### 🥈 Layer 2 — VISUAL REGRESSION (build next)
Golden image tests + Stitch MCP reference comparison.

### 🥉 Layer 3 — PROCESS GATE (organizational)
DESIGN.md as pre-code gate. Every screen requires design spec before coding.

---

## ═══ Category 1: Color & Theme ═══

### AP-001 — Hardcoded Color (P0 🔴)
**What:** `Color(0xFF...)` used directly instead of `Theme.of(context).colorScheme.*`
**Why:** Bypasses dark mode, theming, brand consistency.
**Detection:** ✅ custom_lint AST rule (lint_plugin/rules/hardcoded_color.dart)
**Fix:**
```dart
// ❌ BROKEN
Container(color: Color(0xFF001F5E))
// ✅ CORRECT
Container(color: Theme.of(context).colorScheme.primary)
```

### AP-002 — Missing Dark Mode Variant (P1 🟡)
**What:** Widget defines color without checking `Theme.of(context).brightness`
**Why:** Screen unreadable in dark mode.
**Detection:** ⚠️ Runtime only — static analysis cannot resolve `Theme.of(context)` at compile time. [CONSULTATION FLAG: requires widget test]
**Fix:** Check `Brightness.dark` and provide alternate colors.

### AP-003 — Low Contrast Text (P0 🔴)
**What:** Text color too close to background — fails WCAG AA.
**Detection:** ⚠️ Runtime only — contrast depends on rendered pixels. [CONSULTATION FLAG: requires screenshot analysis or golden test]
**Fix:** Compute contrast ratio; ensure ≥4.5:1 for body text.

### AP-004 — Pure Black/White in Theme (P2 🟢)
**What:** `Colors.black` or `Color(0xFFFFFFFF)` used as surface.
**Why:** Always tint toward brand hue.
**Detection:** Regex (detect.dart.py) with theme-file exclusion.
**Fix:** Use `colorScheme.surface` / `colorScheme.background`.

---

## ═══ Category 2: Typography ═══

### AP-005 — Missing Text Overflow Handling (P0 🔴)
**What:** `Text()` without `overflow` or `maxLines` inside constrained parent.
**Detection:** ✅ custom_lint AST rule (structural check).
**Fix:** Add `maxLines: N, overflow: TextOverflow.ellipsis`.

### AP-006 — Flat Type Hierarchy (P1 🟡)
**What:** All text sizes within 2-4px of each other.
**Detection:** ⚠️ Advisory only — "subjective spacing" per consultation. [CONSULTATION FLAG: not deterministically detectable — requires visual assessment]
**Fix:** Use ≥1.25 ratio between hierarchy levels.

### AP-007 — Missing Text Scaling (P1 🟡)
**What:** Font sizes hardcoded without `MediaQuery.textScaler`.
**Detection:** Regex-based, incomplete. Use in conjunction with Layer 1 fontSize rule.
**Fix:** Material 3 text theme auto-scales — use it.

---

## ═══ Category 3: Layout & Spacing ═══

### AP-008 — Container Nesting Depth > 3 (P0 🔴)
**What:** `Container → Container → Container → Container` chain.
**Detection:** ✅ custom_lint AST rule (walk widget tree, count depth).
**Fix:** Merge Container properties into one.

### AP-009 — Fixed Dimensions Instead of Flexible (P0 🔴)
**What:** `SizedBox(width: 300)` without `LayoutBuilder`.
**Detection:** ⚠️ Regex-based — flags values ≥100px only. [CONSULTATION FLAG: arbitrary threshold — 120px flagged, 99px ignored. Use AST for context-aware check.]
**Fix:** Use `LayoutBuilder` or `MediaQuery`.

### AP-010 — Unbounded Height in ScrollView (P0 🔴)
**What:** `Expanded` inside `Column` inside `SingleChildScrollView`.
**Detection:** ✅ custom_lint AST rule (structural check).
**Fix:** Use `ListView` directly or `IntrinsicHeight`.

### AP-011 — Monotonous Spacing (P2 🟢)
**What:** Same `EdgeInsets.all(16)` everywhere.
**Detection:** ❌ SUBJECTIVE — removed from deterministic rules. [CONSULTATION FLAG: "CANNOT deterministically detect. One designer's consistent spacing system is another's monotonous."]
**Fix:** Vary spacing for rhythm — but only if visually warranted.

### AP-012 — Missing SafeArea (P0 🔴)
**What:** Root widget not wrapped in `SafeArea`.
**Detection:** ✅ custom_lint AST rule (check Scaffold ancestor chain).
**Fix:** Wrap in `SafeArea`.

---

## ═══ Category 4: States — Empty, Error, Loading ═══

### AP-013 — Missing Empty State (P1 🟡)
### AP-014 — Missing Error State (P0 🔴)
### AP-015 — Missing Loading State (P1 🟡)
### AP-016 — Button Without Loading State (P1 🟡)

**Detection:** ⚠️ AST-based structural check possible (check `AsyncValue.when` completeness, `onPressed: isLoading ? null : ...`). [CONSULTATION FLAG: requires deep AST analysis — v3 deliverable]

---

## ═══ Category 5: Accessibility (a11y) ═══

### AP-017 — Missing Semantics Widget (P1 🟡)
**Detection:** ✅ custom_lint AST rule.
**Fix:** Add `semanticLabel` or `Semantics` widget.

### AP-018 — Touch Target < 48px (P1 🟡)
**Detection:** ⚠️ Runtime — rendered size depends on parent constraints. [CONSULTATION FLAG: static analysis can approximate but not be definitive]
**Fix:** Minimum 48×48dp for interactive elements.

### AP-019 — Image Without Semantic Label (P1 🟡)
**Detection:** ✅ custom_lint AST rule.
**Fix:** Add `semanticLabel` parameter.

---

## ═══ Category 6: i18n / RTL ═══

### AP-020 — Hardcoded User-Facing String (P0 🔴)
**What:** English/Arabic text literal inside widget code.
**Detection:** ⚠️ Regex: 98% false positive rate. [CONSULTATION FLAG: Dart strings fundamentally ambiguous without AST. v1 regex is broken for this rule. Use AST-based analysis in v3.]
**Fix:** `AppLocalizations.of(context)!.key`.

### AP-021 — Missing RTL Directionality (P0 🔴)
**What:** `EdgeInsets.only(left: 16)`, `Alignment.centerLeft`.
**Detection:** ✅ custom_lint AST rule (lint_plugin/rules/ltr_edge_insets.dart).
**Fix:** Use `EdgeInsetsDirectional.only(start:)`.

### AP-022 — Missing TextDirection on Directional Widgets (P0 🔴)
**Detection:** ✅ custom_lint AST rule.

---

## ═══ Category 7: Components ═══

### AP-023 — ListTile Without contentPadding (P1 🟡)
### AP-024 — TextField Without Input Decoration (P1 🟡)
### AP-025 — ElevatedButton Without Minimum Size (P1 🟡) [CONSULTATION FLAG: should be P1 not P2 — WCAG 2.5.5 violation]

**Detection:** ✅ custom_lint AST rules for all three.

---

## ═══ Category 8: Performance ═══

### AP-026 — Unnecessary Rebuilds — No const Constructor (P1 🟡)
**Detection:** ⚠️ AST-based — but regex can't reliably detect. [CONSULTATION FLAG: listed but not regex-detectable. custom_lint can implement.]

### AP-027 — ListView.builder Without itemExtent (P1 🟡)
**Detection:** ❌ DANGEROUS ADVICE. [CONSULTATION FLAG: "For variable-height items, setting itemExtent breaks layout. The detector has no way to know item height. False positives on every variable-height ListView."]

---

## ═══ Category 9: Navigation & Structure ═══

### AP-028 — ScaffoldMessenger Before MaterialApp (P0 🔴)
### AP-029 — Missing PopScope for Unsaved Data (P1 🟡)

**Detection:** ✅ custom_lint AST rules.

---

## ═══ Category 10: General Anti-Patterns ═══

### AP-030 — AbsorbPointer as Layout Fix (P0 🔴)
**Detection:** Regex — flags ALL usage including legitimate ones (disabling forms during loading). [CONSULTATION FLAG: "Legitimate uses exist. The message 'likely hiding layout bug' is condescending and often flat wrong."]

### AP-031 — Hero Tag Collision (P0 🔴)
**Detection:** ✅ custom_lint AST rule (scan all Hero tags in route file).

---

## ═══ Category 11: Images & Assets (NEW — v2.0.0) ═══

### AP-032 — Network Image Without Error Builder (P1 🟡)
**What:** `Image.network(url)` without `errorBuilder`.
**Why:** Blank space when image fails to load.
**Fix:**
```dart
Image.network(url,
  errorBuilder: (ctx, err, stack) => Icon(Icons.broken_image),
)
```

### AP-033 — Thumbnail Without cacheWidth/cacheHeight (P1 🟡)
**What:** Large image displayed in small area without cache dimensions.
**Why:** Wastes memory decoding full resolution for thumbnail.
**Fix:** Add `cacheWidth: 200, cacheHeight: 200`.

### AP-034 — Missing gaplessPlayback (P2 🟢)
**What:** `FadeInImage` or `Image.network` without `gaplessPlayback: true` when replacing image.
**Why:** Flash of blank between image transitions.

---

## ═══ Category 12: Forms & Input (NEW — v2.0.0) ═══

### AP-035 — Keyboard Type Mismatch (P1 🟡)
**What:** `TextInputType.text` for email field, `TextInputType.number` for phone.
**Why:** Wrong keyboard frustrates users.
**Detection:** ✅ Heuristic AST check: field name contains "email" → should use `TextInputType.emailAddress`.

### AP-036 — Autocorrect on Name Field (P1 🟡)
**What:** `autocorrect: true` (default) on name fields.
**Why:** Autocorrect mangles names.
**Fix:** `autocorrect: false, enableSuggestions: false` on name fields.

### AP-037 — Password Field Without Toggle (P1 🟡)
**What:** `obscureText: true` without visibility toggle icon.
**Why:** User can't verify what they typed.
**Fix:** Add `suffixIcon` with visibility toggle.

---

## ═══ Category 13: Keyboard & IME (NEW — v2.0.0) ═══

### AP-038 — Missing resizeToAvoidBottomInset (P1 🟡)
**What:** `Scaffold` without `resizeToAvoidBottomInset: false` when needed (e.g., background image).
**Why:** Keyboard pushes content in undesirable ways.
**Detection:** ✅ AST check.

### AP-039 — Focus Node Not Disposed (P1 🟡)
**What:** `FocusNode()` created in `build()` without `dispose()`.
**Why:** Memory leak — focus nodes accumulate.
**Fix:** Use `initState` + `dispose` for FocusNode lifecycle.

---

## ═══ Category 14: Animation & Motion (NEW — v2.0.0) ═══

### AP-040 — Missing AnimatedContainer (P2 🟢)
**What:** `setState` wrapping Container property changes instead of `AnimatedContainer`.
**Why:** Janky transitions. Flutter has built-in implicit animations.
**Fix:** Replace `Container` + `setState` with `AnimatedContainer`.

### AP-041 — No Reduced Motion Handling (P1 🟡)
**What:** Animations without `MediaQuery.of(context).disableAnimations` check.
**Why:** Violates accessibility preferences.
**Fix:** Check `disableAnimations` and fall back to instant transition.

---

## ═══ Detection Engine Summary ═══

| Layer | Tool | Rules | False Positives | Status |
|-------|------|-------|----------------|--------|
| **v1 Spike** | Python regex | 7 | ~98% | ⚠️ SPIKE only — do not deploy |
| **v2 Production** | `custom_lint` plugin | 3 core + structural | ~0% | 🟢 Build now |
| **v3 Visual** | Golden image tests | TBD | N/A (visual) | 🟡 Build next |
| **Reference** | SKILL.md registry | 31 documented | N/A (documentation) | 🟢 Done |

### SPIKE Detector (v1)
`scripts/detect.dart.py` — Python regex scanner. Proved the concept. **NOT for production.** Superseded by `custom_lint`.

### Custom Lint Plugin (v2)
`lint_plugin/` — Dart `custom_lint` package. Add to any Flutter project:
```yaml
# analysis_options.yaml
analyzer:
  plugins:
    - flutter_design_lint
```
Then `flutter analyze` runs all rules automatically — IDE integration, CI-ready, zero false positives.

---

## ═══ Integration with Swarm ═══

| Hook Point | Action |
|------------|--------|
| **IDE** | Red squiggles in VS Code/Android Studio (via `custom_lint` + `analysis_options.yaml`) |
| **Pre-commit** | `flutter analyze` automatically runs custom_lint rules — block on ERROR |
| **CI/CD** | Same `flutter analyze` in GitHub Actions — zero config |
| **Constitutional Court** | Weekly golden image diff against Stitch references |
| **UI/UX Agent** | Load this skill before every task |
| **PR Review** | Zero-Trust Auditor checks `flutter analyze` output |

---

---

## ═══ Category 15: State & Data Flow (NEW — v2.1.0) ═══

### AP-042 — Dual-Path UI: Same Surface, Different State (P0 🔴)

**What:** Two independent code paths produce identical-looking interactive UI (e.g., confirm buttons, compound split card), but only ONE path populates the state the confirm/edit handlers depend on. The user sees the same buttons regardless of which path fired, but one path silently breaks.

**Example — Transaction Confirm (Azdal, 2026-07-12):**
```dart
// Path 1: Gemini's main response emits action_buttons JSON directly
// → _storedClassifications NEVER populated → confirm always fails
if (response.widget != null) {
  chatNotifier.addBotMessage(text, widget: response.widget);
}
// Path 2: _tryAutoClassify builds action_buttons from Dart
// → _storedClassifications correctly populated → confirm works
else {
  _storedClassifications[id] = txResult;
  chatNotifier.addBotMessage(text, widget: action_buttons);
}
```

**Why this is catastrophic:** The user sees identical UI from both paths — there's no visual difference. Tapping confirm works on Path 2, silently fails on Path 1. The bug survives unit tests (both flows look correct in isolation), survives `flutter analyze`, and only surfaces on real device interaction.

**Detection:** Architecture-level — not detectable by static analysis. Requires code review checklist: "For each interactive widget type, trace ALL code paths that can produce it. Verify every path populates the state the widget's action handlers read."

**Fix pattern — Three options, in order of preference:**
1. **Collapse to one path** — remove the prompt/instruction that creates the second path. Only ONE code path ever produces this widget type.
2. **Gate the dangerous path** — if the prompt can't be removed, add a hard filter: `if (widgetType == 'action_buttons') { /* drop, fall through to safe path */ }`
3. **Populate state in ALL paths** — if both paths must remain, ensure every path populates the shared state before showing UI.

**Real battle history (Azdal):**
- `action_buttons`: 5 attempts to fix. Root cause: `_systemPrompt` explicitly instructed Gemini to emit action_buttons JSON. Fix: removed instruction, made `_tryAutoClassify` the sole path.
- `compound_split_card`: Same pattern. System prompt instructed emission. History contamination made it worse — Gemini merged prior transactions. Fix: removed instruction + dedicated `classifyTransaction()` with isolated prompt + filtered history.

**Prevention:** When writing system prompts for LLMs that emit widget JSON, explicitly forbid widgets whose confirm/edit lifecycle depends on app-side state. Better: never let LLM freeform output produce actionable UI — build all actionable UI from structured classification results.

---

## ═══ Source & Evolution ═══

- **v1.0.0** — Initial 31 patterns + regex detector (2026-07-11)
- **v2.0.0** — Multi-model consultation feedback integrated
- **v2.1.0** — AP-042: Dual-Path UI anti-pattern, Category 15 added (2026-07-13, from Azdal history-leak debugging session):
  - Added 4 missing categories (Images, Forms, Keyboard, Animation)
  - Marked 9 problematic rules with `[CONSULTATION FLAG]`
  - Documented 3 core custom_lint rules as Layer 1
  - Added golden image test reference (Layer 2)
  - SPIKE banner on v1 regex detector
  - AP-011 removed from deterministic rules (subjective)
  - AP-027 flagged as dangerous advice
  - AP-006, AP-018 flagged as runtime-only
- **v3.0.0 (planned)** — Full AST rules + golden test integration
