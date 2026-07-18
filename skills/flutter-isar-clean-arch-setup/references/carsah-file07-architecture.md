# CarSah File 07 Architecture — BL-001 Implementation

> Reference for the CarSah MVP Flutter project structure.
> Source: `app-spec/07_flutter_architecture.md` v3.0.0
> Implemented: 2026-06-10 (commit c0b1134)

## Architecture Decision

**Clean Architecture + Feature-first Modules + Riverpod + Isar**

```
Presentation → Application → Domain ← Data
```

- Presentation depends on Application
- Application depends on Domain
- Data implements Domain repository contracts
- Data must NOT leak Isar objects into UI

## Technology Stack

| Component | Choice |
|-----------|--------|
| Framework | Flutter (Android + iOS) |
| State | Riverpod (no code-gen in MVP) |
| DB | Isar Local NoSQL v3.1+ |
| Routing | go_router ^14.8.1 |
| UI | Material Design 3, Elegant Theme, Light only |
| Localization | AR-first, EN toggle (intl ^0.19.0) |
| Files | path_provider ^2.1.5 |

## Explicitly NOT in MVP

- No backend / Firebase / Supabase / REST / GraphQL
- No auth / payment / push notification SDKs
- No QR / VIN / license scan packages
- No analytics / crash reporting

## Feature Flags (all false in MVP)

enableAuth, enableBackend, enableCloudSync, enablePayments, enableQrSync,
enableVinScan, enableLicenseScan, enablePrecisionPlan, enablePrecisionTheme,
enablePushNotifications

## Directory Layout (37 dirs, 36 .dart files)

```
lib/
├── app/                      5 files
│   ├── carsah_app.dart       MaterialApp.router, ConsumerWidget, AR locale
│   ├── app_bootstrap.dart    isarReadyProvider FutureProvider
│   ├── app_router.dart       19 GoRoute definitions (all placeholder screens)
│   ├── app_theme.dart        ElegantTheme: #7C5CFC purple + #14B8A6 teal
│   └── app_locale.dart       t() helper stub
├── core/                     6 subdirs
│   ├── errors/failure.dart   sealed AppFailure → 5 subtypes
│   ├── result/result.dart    sealed Result<T> → Success | Failure
│   ├── localization/         AR/EN translation maps (BL-007)
│   ├── validation/           Field validators
│   ├── constants/            App constants
│   └── widgets/              Shared widgets
├── domain/                   4 subdirs
│   ├── entities/entities.dart          7 entities: Vehicle, OdometerReading,
│   │                                    ServiceTask, ServiceRecord, KnownCostItem,
│   │                                    FluidDetail, AuditAnswer
│   ├── enums/enums.dart                8 enums: PlanLevel, TaskStatus, EnergyType,
│   │                                    TransmissionType, SourceLabel, AuditSeverity,
│   │                                    TirePosition, FluidType (20 values)
│   ├── value_objects/value_objects.dart  Odometer(km), Cost(sar), SourceLabel
│   └── repositories/repository_contracts.dart  9 abstract interfaces
├── data/                     4 subdirs
│   ├── local/isar_database.dart        CarSahDatabase singleton stub
│   ├── local/isar_collections/         @collection models (BL-010)
│   ├── local/mappers/                  Isar ↔ domain (BL-010)
│   └── repositories/                   Implementations (BL-010)
├── features/                 6 modules × 2 subdirs each
│   ├── vehicle_setup/        CreateVehicleUseCase, GenerateTasksUseCase
│   ├── dashboard/            GetDashboardStateUseCase (Virgin/Zen/Active)
│   ├── history/              Add/Edit/SoftDelete/GetHistory use cases
│   ├── mechanic_card/        GetMechanicCardSnapshotUseCase (local only)
│   ├── audit/                AddAuditAnswerUseCase, GetAuditQuestionsUseCase
│   └── settings/             ChangeLocaleUseCase, GetVehicleListUseCase
├── shared/                   4 subdirs
│   ├── design_system/        Elegant Theme tokens + semantic colors
│   ├── source_labels/        AR/EN display: Smart Standard / Custom (INV-008)
│   ├── smart_standard_plan/  19 conservative intervals + 19 task codes
│   └── terminology/          Saudi workshop terms
└── main.dart                 ProviderScope → CarSahApp
```

## Elegant Theme Colors

| Token | Hex | Usage |
|-------|-----|-------|
| Primary | #7C5CFC | Buttons, selected nav, focus borders |
| Secondary | #14B8A6 | Accents |
| Smart Standard Amber | #FFA726 | Plan indicators (NOT red) |
| Zen Green | #4CAF50 | Success state indicator |
| Pending Odometer | #78909C | Neutral, calm, non-warning |
| Accent Border | #7C5CFC | History card borders |

## 9 Repository Contracts (domain/repositories/)

1. VehicleRepository — create, update, softDelete, getById, getActive, getNonDeleted, countNonDeleted
2. OdometerRepository — addReading, getLatest, getHistory
3. ServiceTaskRepository — generateSmartStandard, getByVehicle, getByTaskCode, recalculate, updateStatus
4. ServiceRecordRepository — add, update, softDelete, getByVehicle, getById, getLatestForTask
5. CostItemRepository — addBatch, updateBatch, getByRecord, sumByRecord
6. FluidDetailRepository — addBatch, updateBatch, getByRecord, getLatestByType, getMostUsed
7. AuditRepository — addAnswer, getByTaskCode, getByVehicle
8. AppSettingsRepository — setActiveVehicle, getActiveVehicleId, getLocale, setLocale

## Smart Standard Plan Intervals

| Task | Interval (km) |
|------|---------------|
| Engine oil + filter | 7,500 |
| Air/Cabin filter | 15,000 |
| Wiper blades | 15,000 |
| Brake fluid | 30,000 |
| Brake pads | 30,000 |
| Battery check | 30,000 |
| Fuel filter | 45,000 |
| Coolant | 60,000 |
| Spark plugs | 60,000 |
| ATF (automatic) | 80,000 |
| ATF (manual) / Serpentine / Differential / Transfer case / Brake rotors / AC | 60,000 |
| Timing belt | 100,000 |
| Tire rotation | 10,000 |

## Error Handling

- `sealed class AppFailure` — 5 subtypes: ValidationFailure, PersistenceFailure, NotFoundFailure, BusinessRuleFailure, VehicleLimitFailure
- `sealed class Result<T>` — Success<T>(data) | Failure<T>(error)
- No raw exceptions shown to user
- Double-tap Save protection: disable button + idempotency guard

## Commit Reference

- Repo: `github.com/jahfaliabdulrahman-dev/carsah`
- Commit: `c0b1134` — "BL-001: Flutter MVP project structure per File 07 architecture"
- 42 files changed, +1,137 / -141 lines
- `flutter analyze`: 0 errors, 0 warnings
