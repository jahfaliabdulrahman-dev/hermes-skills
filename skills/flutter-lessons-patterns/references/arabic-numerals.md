# Arabic-Indic Numerals in Dart/Flutter — Regex + Conversion

> **Source:** Azdal (2026-07-12) — device testing with Arabic financial input
> **Bug:** `_tryAutoClassify` returned null for transactions typed with Arabic-Indic numerals (٠-٩)
> **Root cause:** Dart `RegExp(r'\d+')` may not match Arabic-Indic digits depending on platform/engine

---

## The Problem

Arabic speakers commonly switch between Western (0-9) and Arabic-Indic (٠-٩) numerals in the same message. Phone keyboards often default to Arabic-Indic when Arabic language is active.

```dart
// ❌ BROKEN — '\d' may not match Arabic-Indic ٠-٩
RegExp(r'\d+').hasMatch('صرفت ٥٦ ريال');  // → false on many platforms

// ✅ CORRECT — explicit character class
RegExp(r'[0-9٠-٩]').hasMatch('صرفت ٥٦ ريال');  // → true
```

## The Conversion Utility

```dart
/// Convert Arabic-Indic numerals (٠-٩) to Western (0-9).
static String arabicToWestern(String input) {
  const arabic = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩'];
  const western = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];
  var result = input;
  for (var i = 0; i < 10; i++) {
    result = result.replaceAll(arabic[i], western[i]);
  }
  return result;
}

// Usage:
final digits = '٥٦';
final western = arabicToWestern(digits);  // → '56'
final amount = int.tryParse(western);      // → 56
```

## Where This Matters

- **Transaction amount extraction** — users type "صرفت ٥٦ ريال"
- **OCR receipt totals** — Arabic receipts use Arabic-Indic numerals
- **Cold start income entry** — users may type Arabic-Indic in numeric fields
- **Any `int.parse()` or `double.parse()` call** — these only accept Western numerals

## Detection Checklist

- [ ] Any `RegExp(r'\d')` that parses user input → replace with `[0-9٠-٩]`
- [ ] Any `int.parse()` or `double.parse()` on user input → run through `arabicToWestern()` first
- [ ] OCR output parsing: does Gemini return Western or Arabic-Indic numerals?
- [ ] Keyboard type: are numeric TextFields forcing Western keyboard (`TextInputType.number`)?

## Platform Note

Dart's `\d` in `RegExp` depends on the engine:
- **ECMAScript mode (default):** `\d` = `[0-9]` only — does NOT match Arabic-Indic
- **Unicode mode (`unicode: true`):** `\d` = Unicode Nd category — includes Arabic-Indic

Do NOT rely on Unicode mode being available — always use explicit character class for cross-platform safety.

## Related

- `flutter-lessons-patterns` — Pattern 35 (Compute Derived Values Locally — same class: never trust implicit encoding)
