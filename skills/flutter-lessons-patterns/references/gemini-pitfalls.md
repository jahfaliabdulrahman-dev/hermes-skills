# Gemini API Pitfalls — Azdal (2026-07-12)

> **Source:** Live device testing of Azdal Flutter app.
> **Context:** `google_generative_ai` package, `GeminiService` class.
> **Status:** Both pitfalls confirmed via logcat traces from real Android device.

---

## Pitfall 1 — Never Pin Dated Model Aliases

**Symptom:** Every OCR call fails in ~1.4s with:
```
OCR Gemini FAILED — "This model models/gemini-2.5-flash is no longer
available to new users."
```
Too fast to be real analysis — the API rejects the model name before processing.

**Root cause:** `_visionModel = 'gemini-2.5-flash'` — a dated alias that Google deprecated.

**Fix:** Use `gemini-flash-latest` — the auto-resolving alias that always points to the newest available Flash model. Gemini Flash is natively multimodal — no separate vision model needed.

**Rule:** Never use dated model name aliases (`gemini-2.5-flash`, `gemini-1.5-pro`, `gemini-2.0-flash`). Always use `-latest` variants:
- `gemini-flash-latest` — for text + vision (multimodal)
- `gemini-pro-latest` — for heavy reasoning

**Detection:** If `_modelName` or `_chatModel` or `_visionModel` contains a version number (2.5, 1.5, 2.0), flag it before commit.

**Same bug class as:** Stage 1 fix where `_chatModel` was pinned to `gemini-2.5-flash` instead of `gemini-flash-latest`. This is the OCR-specific repeat of the same mistake.

---

## Pitfall 2 — System Prompt Must Match Widget Computation

**Symptom:** `compound_split_card` shows "الإجمالي: 0 ريال" — total is always 0.

**Root cause — two layers:**

1. **Gemini correctly follows its own instruction:** The system prompt says `لا تحسب أبداً — الحسابات على Supabase` (never calculate — calculations on Supabase). Gemini correctly does NOT compute the total, so `widget.json['total']` is absent → defaults to 0.

2. **Widget reads static json once:** Even if Gemini DID send a total, `final total = (widget.json['total'] as num?)?.toInt() ?? 0` is read once at build time. The `+/-` adjuster buttons (`_adjust()`) mutate `_splits` but never update `total` — so it goes stale instantly.

**Fix — two layers:**

1. **Widget computes total locally:**
```dart
final total = _splits.fold<int>(
  0,
  (sum, s) => sum + ((s['amount'] as num?)?.toInt() ?? 0),
);
```
Recalculated on every build — correct on first render AND stays correct as the user adjusts.

2. **Prompt updated:**
```
لا ترسل حقل total مع compound_split_card — التطبيق يحسب الإجمالي تلقائياً من splits.
```

**Architectural principle (DEC-003):** LLM understands and routes — but NEVER calculates. Any derived numeric value visible to the user MUST be computed by Dart/SQL code, never from LLM output. The system prompt correctly refuses to calculate; the widget must not trust it to do so.

**Detection pattern (same class as Pattern 33):** Any widget that reads `widget.json['someNumber']` and displays it to the user. Trace: is this value computed locally from mutable state, or is it read once from static JSON? If the latter, it will be wrong on first render when Gemini omits it AND wrong after user interaction.

---

## Pitfall 3 — Never Let LLM Emit Actionable UI Directly

**Symptom:** User taps "✅ صحيح" to confirm a transaction → gets error "تعذر حفظ المعاملة — التصنيف غير متوفر". Confirmed via device logcat: sent "spent 22 riyal gas", got correct classification and confirm buttons, confirm failed.

**Root cause:** Two independent code paths produce identical-looking confirm UI:

1. **Path 1 (broken):** System prompt tells Gemini to emit `action_buttons` JSON → `_sendMessage` shows it directly → `_tryAutoClassify` never called → `_storedClassifications` never populated → confirm handler finds no stored classification → shows error.

2. **Path 2 (working):** Gemini returns plain text (no widget) → `_sendMessage` calls `_tryAutoClassify` → classification stored in `_storedClassifications` → Dart code constructs `action_buttons` from verified data → confirm works.

Path 1 was the DEFAULT — the system prompt actively pushed Gemini toward it. This isn't an edge case — it's the path the prompt was designed for.

**Fix:** Remove ALL actionable UI instructions from the system prompt. The app constructs UI from data it can verify — the LLM only describes data in plain text.

```diff
-عند تصنيف معاملة، أرسل رداً يحتوي على JSON widget بالصيغة التالية:
-```json
-{
-  "widget": "action_buttons",
-  ...
-}
-```
+عبر عن التصنيف بنص عادي فقط — لا ترسل أزرار (action_buttons).
+التطبيق هو المسؤول عن بناء أزرار التأكيد والتعديل بنفسه.
```

**Architectural principle:** DEC-003 says "LLM understands and routes — but NEVER calculates." This extends the same principle to UI: "LLM describes — app constructs actionable UI." The LLM should never be the source of JSON that triggers user actions (confirm, save, delete, approve) because the app needs to store and verify the underlying data BEFORE showing actionable UI.

**Compound split audit:** `compound_split_card` was checked for the same bug class. Not affected — its splits travel through action callbacks, not stored state.

**Detection:** grep system prompts for `"widget": "action_buttons"` and `"widget": "quick_input_form"` — any instruction that tells the LLM to emit JSON that triggers a user action is a candidate for this bug class.

**Related:** flutter-lessons-patterns Pattern 37 (same bug, code-path perspective), Pattern 33 (Stored First Decision — the storage pattern that Path 1 bypassed).

---

## Pitfall 4 — Prompt Scope: Block Specific Widget Types, Not All Structured Output

**Symptom:** After fixing Pitfall 3 (removing `action_buttons` from system prompt), the confirmation buttons disappeared entirely. User sent "صرفت ٥٦ ريال بنزين" → Gemini responded with plain text → `_tryAutoClassify` returned null → no confirm buttons ever appeared.

**Root cause:** The initial Pitfall 3 fix was too aggressive. The system prompt said:
```
عبر عن التصنيف بنص عادي فقط — لا ترسل أزرار (action_buttons).
```
The phrase "عبر عن التصنيف بنص عادي فقط" (express the classification in plain text only) blocked ALL structured/JSON output — including the classification call's response. Since `_tryAutoClassify` also uses `sendMessage` (which injects the system prompt), its call was also suppressed from returning structured classification data.

**The two affected calls:**
1. **Main chat call** (intended fix target): should NOT emit `action_buttons` JSON ✅
2. **Classification call** (`_tryAutoClassify`): SHOULD return structured classification data ❌ blocked

Both calls share `_systemPrompt` via `sendMessage`. The fix that blocked one call also blocked the other.

**Fix:** Narrow the exclusion to the specific widget type, not all JSON:
```diff
-عبر عن التصنيف بنص عادي فقط — لا ترسل أزرار (action_buttons).
-التطبيق هو المسؤول عن بناء أزرار التأكيد والتعديل بنفسه.
+لا ترسل أبداً زر التأكيد (action_buttons widget JSON).
+التطبيق هو المسؤول عن بناء أزرار ✅ صحيح / 🔄 تعديل بنفسه.
```

**And update the classification prompt** to explicitly request JSON:
```diff
-صنف المعاملة التالية واستخرج:
-- amount (رقم)
-- category (فئة)
-...
+أجب بصيغة JSON فقط، بدون أي نص آخر:
+{"amount": الرقم, "category": "الفئة", "tone": "green أو gray أو red"}
```

**Detection checklist for any system prompt modification:**
- [ ] Does this prompt code block a SPECIFIC widget type, or ALL structured output?
- [ ] Are there OTHER callers of `sendMessage` that also receive this system prompt?
- [ ] If a second caller needs structured output, does the exclusion block it?
- [ ] Can the classification call use a different method without the system prompt?

**Related:** Pattern 37 in flutter-lessons-patterns (code-path perspective), `references/arabic-numerals.md` (Arabic-Indic conversion added in the same fix).
