---
name: flutter-isar-testing
category: software-development
description: In-memory Isar testing setup for Flutter — unit tests with real Isar DB on macOS
metadata:
  provenance: SELF-BUILT (CarSah + prior maintenance-app experience, 2026-08-09) — NOT from official flutter.dev/isar.dev sources. Subject to the same review standards as external skills (LL-053).
triggers:
  - "test isar"
  - "isar unit test"
  - "in-memory isar"
  - "flutter test isar"
  - "isar headless"
  - "libisar.dylib"
  - "isar test helper"
---

# Flutter Isar Testing — In-Memory Setup

## Problem
`flutter test` runs headless and can't find `libisar.dylib` on macOS. `Isar.open()` requires a real directory path (not null). Widget tests with the app's root widget crash (SIGTERM) because the app initializes Isar + all providers.

## Solution: 3-Part Setup

### 1. Symlink `libisar.dylib` to project root

Isar looks for the native library in the project root. `isar_flutter_libs` has it but `flutter test` doesn't link it automatically.

```bash
ln -sf "$HOME/.pub-cache/hosted/pub.dev/isar_flutter_libs-*/macos/libisar.dylib" \
  "$PWD/libisar.dylib"
```

### 2. Test helper — `openTestIsar()`

Create `test/helpers/test_helpers.dart`:

```dart
import 'dart:io';
import 'package:isar/isar.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Import ALL schemas + the isarProvider
import 'package:my_app/data/models/vehicle.dart';
import 'package:my_app/data/models/maintenance_record.dart';
import 'package:my_app/data/models/service_task.dart';
import 'package:my_app/data/models/part_price.dart';
import 'package:my_app/data/models/invoice_image.dart';
import 'package:my_app/data/datasources/local/isar_provider.dart';

Future<Isar> openTestIsar() async {
  final name = 'test_${DateTime.now().microsecondsSinceEpoch}';
  final dir = await Directory.systemTemp.createTemp('isar_test_');

  return Isar.open(
    [VehicleSchema, MaintenanceRecordSchema, ServiceTaskSchema,
     PartPriceSchema, InvoiceImageSchema],
    directory: dir.path,  // REQUIRED — Isar 3.1.0+1 doesn't accept null
    name: name,
  );
}

Future<List<Override>> createTestOverrides() async {
  final isar = await openTestIsar();
  return [isarProvider.overrideWithValue(isar)];
}
```

### 3. Test pattern

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:isar/isar.dart';
import 'helpers/test_helpers.dart';

void main() {
  late Isar isar;

  setUp(() async {
    isar = await openTestIsar();
  });

  tearDown(() async {
    await isar.close(deleteFromDisk: true);
  });

  group('My Test', () {
    test('CRUD works', () async {
      final vehicle = createTestVehicle(name: 'Test Car');
      await isar.writeTxn(() async {
        await isar.vehicles.put(vehicle);
      });

      final stored = await isar.vehicles.get(vehicle.id);
      expect(stored!.name, equals('Test Car'));
    });
  });
}
```

## Pitfalls & Fixes

### `isActiveEqualTo` not available for non-indexed bool
Isar only generates query methods for `@Index()` fields. For non-indexed booleans:
```dart
// ❌ Fails
final active = await isar.vehicles.where().isActiveEqualTo(true).findAll();

// ✅ Works
final all = await isar.vehicles.where().findAll();
final active = all.where((v) => v.isActive).toList();
```

### `SettingsNotifier` can't be used directly
`Notifier` requires a Riverpod container to build. Don't instantiate it directly:
```dart
// ❌ Fails — LateInitializationError
final notifier = SettingsNotifier();
notifier.build();
notifier.toggleLocale();

// ✅ Test SettingsState directly
const state = SettingsState(locale: AppLocale.en);
expect(state.t('app_title'), equals('My App'));
```

### Cost predictor outlier test needs enough normal data
With too few data points, the std dev is inflated and outliers aren't filtered:
```dart
// ❌ 4 normal + 1 outlier — std dev too high, outlier not filtered
final records = [100, 105, 110, 1000]; // mean=328, std=377, z(1000)=1.78 < 2.0

// ✅ 10 normal + 1 outlier — std dev stable, outlier filtered
final records = [100, 102, 104, 106, 108, 100, 102, 104, 106, 108, 10000];
```

### Don't double-close Isar
If `tearDown` calls `isar.close()`, don't close manually in the test:
```dart
// ❌ IsarError: instance already closed
test('test', () async {
  // ... test ...
  await isar.close(deleteFromDisk: false); // conflicts with tearDown
});

// ✅ Let tearDown handle cleanup
test('test', () async {
  // ... test ... (no manual close)
});
```

### Widget tests with the app's root widget crash in headless runner
The app's root widget `initState()` calls `initIsarDatabase()` which needs real native libs.
Options:
1. **Use `createTestOverrides()` + `ProviderScope`** to inject test Isar
2. **Move heavy widget tests to `integration_test/`** for device-based execution

### Widget tests hang: `pumpAndSettle timed out` with Isar under FakeAsync

`pumpAndSettle` waits until no frames are scheduled, but an infinite spinner (loading state) or real async Isar work never settles under the widget test's FakeAsync clock → the test times out.

- If the widget shows an infinite loading spinner by design, never `pumpAndSettle` while it is visible — use `await tester.pump(const Duration(...))` with explicit steps.
- Isar is REAL async; its futures do not resolve as the fake clock advances. For widgets that touch Isar: override the repository/use-case (inject fakes/Riverpod overrides) OR test with real-async patterns.
- **⚠️ STOP-28 correction (2026-08-11, LL-053):** the previous wording "test with real-async patterns (`tester.runAsync`) plus `pump()` with fixed durations" was AMBIGUOUS and was read as "call pump inside runAsync" — that nesting hung Linux CI for 10 minutes (fake-clock primitives inside real-clock runAsync starve waiting for a frame the real clock never schedules). It propagated to 13 files (44 sites). **The correct rule: `runAsync` wraps the WAITING only — NEVER `pumpWidget`/`pump`/`tap` inside it.** The safe shape is `settleReal` from `test/helpers/pump.dart` (runAsync wraps only the waiting, never a pump), and `test/structure/test_harness_policy_test.dart` fails on any NEW nesting. When a test passes locally but hangs CI on Linux — suspect this pattern first, not the scheduler.
- Diagnose before patching: probe whether the async layer resolves under FakeAsync at all (a quick `tester.runAsync` experiment) — throwing a different pump strategy blindly just moves the timeout.

## Integration Tests (Device-Based)

For tests that need real Isar + full app lifecycle:

```
integration_test/
  driver.dart
  tc01_test.dart
  app_full_flow_test.dart
```

```dart
import 'package:integration_test/integration_test.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  // ... tests run on device with real Isar
}
```

Run: `flutter test integration_test/` (requires connected device)

## Project File Structure
```
project/
  libisar.dylib              ← symlink to isar_flutter_libs
  test/
    helpers/
      test_helpers.dart      ← openTestIsar() + factory helpers
    TC001_test.dart          ← pure logic (no app root widget)
    TC002_test.dart          ← Isar CRUD
    ...
  integration_test/
    driver.dart              ← integration test driver
    app_full_flow_test.dart  ← full app on device
```
