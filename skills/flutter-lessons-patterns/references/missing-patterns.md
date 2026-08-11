# Missing Flutter/Dart Patterns — Gap Analysis

> **Date:** 2026-07-12
> **Source:** Triple MoA Audit of `SKILL.md` v2.1.0
> **Status:** Identified, not yet implemented

These 9 patterns are missing from the canonical lessons learned file. They represent classes of bugs, performance issues, and architectural gaps commonly found in production Flutter codebases. Each should be promoted to a full pattern when a real-world CarSah or Hermex incident triggers it.

---

## M1 — Controller Disposal

**Rule:** `TextEditingController`, `AnimationController`, `FocusNode`, `ScrollController`, `PageController`, and any `Listenable` created in a `StatefulWidget` MUST be disposed in `dispose()`.

**Why:** Controllers hold native resources and listener lists. Not disposing them causes memory leaks that are silent and cumulative — the app appears fine during development but degrades over long sessions.

```dart
// ❌ BROKEN — memory leak
class _FormState extends State<FormWidget> {
  final _controller = TextEditingController();
  // never disposed
}

// ✅ CORRECT
class _FormState extends State<FormWidget> {
  late final _controller = TextEditingController();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
}
```

**Related lint:** `use_late_for_private_fields_and_variables` for `late final` pattern.

---

## M2 — Const Constructors for Rebuild Optimization

**Rule:** Widget constructors should be `const` wherever possible. Use `const` at the call site too.

**Why:** Flutter compares widget instances with `==`. If a widget is `const`, two instances with the same parameters are identical — Flutter skips the rebuild entirely. This is the cheapest performance optimization available.

```dart
// ❌ Avoids const
SizedBox(width: 16)

// ✅ Uses const (no rebuild)
const SizedBox(width: 16)
```

**Check:** `flutter analyze` with `prefer_const_constructors` lint rule catches most violations.

---

## M3 — Build Method Purity

**Rule:** NEVER perform side effects in `build()`. No API calls, no navigation, no state mutation, no `setState`. The `build()` method is called frequently and must be pure.

**Why:** Flutter calls `build()` any time the framework decides to — during layout, on theme changes, on orientation changes, on keyboard appearance. A side effect in `build()` will trigger on every one of these events, causing infinite loops or spammed API calls.

```dart
// ❌ BROKEN — triggers API call on every rebuild
@override
Widget build(BuildContext context) {
  ref.read(userProvider.notifier).fetchUser(); // INFINITE LOOP
  return Text('Hello');
}

// ✅ CORRECT — use initState or a Riverpod provider's build()
@override
void initState() {
  super.initState();
  WidgetsBinding.instance.addPostFrameCallback((_) {
    ref.read(userProvider.notifier).fetchUser();
  });
}
```

---

## M4 — Keys in Widget Trees

**Rule:** Use `ValueKey` when reordering/mutating lists of stateful widgets. Use `GlobalKey` sparingly for imperative access to widget state.

**Why:** Without keys, Flutter matches widgets by type and position. When a list reorders, State gets attached to the wrong widget (e.g., a checkbox's checked state jumps to a different row). Keys preserve identity across reorders.

```dart
// ❌ BROKEN — state will mis-match after reorder
ListView(
  children: items.map((item) => CheckboxTile(item)).toList(),
)

// ✅ CORRECT
ListView(
  children: items.map((item) => CheckboxTile(
    key: ValueKey(item.id),  // preserves state across reorder
    item: item,
  )).toList(),
)
```

---

## M5 — Error Boundaries / Crash Reporting

**Rule:** Every Flutter app MUST set `FlutterError.onError` and `PlatformDispatcher.instance.onError` to catch and report uncaught errors. Never let exceptions kill the app silently from the user's perspective.

**Why:** Without error boundaries, an uncaught exception in a frame callback paints a gray screen or kills the app entirely. The user sees a crash with zero diagnostic information. Error boundaries + a crash reporter (Sentry, Firebase Crashlytics) give you stack traces.

```dart
void main() {
  FlutterError.onError = (details) {
    FlutterError.presentError(details);
    // Send to crash reporter
  };
  PlatformDispatcher.instance.onError = (error, stack) {
    // Send to crash reporter
    return true; // true = handled
  };
  runApp(const MyApp());
}
```

---

## M6 — FutureProvider/StreamProvider vs Raw Widgets

**Rule:** Use `FutureProvider` / `StreamProvider` (Riverpod) instead of raw `FutureBuilder` / `StreamBuilder` in widget trees. Riverpod providers handle loading/error/data states automatically and can be tested independently.

**Why:** `FutureBuilder` and `StreamBuilder` re-execute on every rebuild unless carefully managed. Riverpod providers cache the result, deduplicate requests, and survive rebuilds. They also make error handling uniform.

```dart
// ❌ Re-executes on every build
FutureBuilder<User>(future: api.fetchUser(), ...)

// ✅ Cached, testable, survives rebuilds
final userProvider = FutureProvider<User>((ref) => api.fetchUser());
// In widget: ref.watch(userProvider).when(loading: ..., error: ..., data: ...)
```

---

## M7 — Isolate/Compute for Heavy Work

**Rule:** Offload CPU-intensive work (JSON parsing of large payloads, image processing, encryption, compression) to background isolates using `compute()` or `Isolate.run()`.

**Why:** Dart is single-threaded. Heavy synchronous work blocks the UI thread, causing visible frame drops (jank). The 16ms frame budget for 60fps is unforgiving.

```dart
// ❌ Blocks UI thread
final result = jsonDecode(largeJsonString);

// ✅ Runs on background isolate
final result = await compute(jsonDecode, largeJsonString);
```

---

## M8 — Golden Image Tests

**Rule:** For any custom widget whose visual appearance matters, add a golden image test. Run golden tests on CI against a known-good baseline.

**Why:** Unit tests verify logic; golden tests verify pixels. A typo in a `Text` widget, a missing `Padding`, or a broken `Theme` override will pass unit tests but change the rendered output. Golden tests catch these.

```dart
testWidgets('LoginButton matches golden', (tester) async {
  await tester.pumpWidget(const MaterialApp(home: LoginButton()));
  await expectLater(find.byType(LoginButton), matchesGoldenFile('login_button.png'));
});
```

**Pitfall:** Golden files are platform-specific (font rendering differs between macOS/Linux/Windows). Generate baselines on the same OS as CI.

---

## M9 — Adaptive Widgets for Platform-Appropriate UX

**Rule:** Use `Switch.adaptive()`, `CircularProgressIndicator.adaptive()`, `AlertDialog.adaptive()`, etc. on cross-platform apps. Don't show Material switches on iOS or Cupertino switches on Android.

**Why:** iOS users expect iOS controls. Android users expect Material controls. Mixing them signals "unpolished port" and reduces trust.

```dart
// ❌ Forces Material style on iOS
Switch(value: isOn, onChanged: ...)

// ✅ Platform-appropriate
Switch.adaptive(value: isOn, onChanged: ...)
```
