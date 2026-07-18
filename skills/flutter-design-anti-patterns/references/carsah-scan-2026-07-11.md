# CarSah Design Scan Results — 2026-07-11

First run of `detect.dart.py` on CarSah (92 `.dart` files, excluding `test/` and `generated/`).

## Summary

| Severity | Count |
|----------|-------|
| P0 | 933 (927 from AP-020 noise, ~6 actionable) |
| P1 | 2 |
| P2 | 10 |
| **Total** | 945 |

## Real (Actionable) Findings

### AP-001 — Hardcoded Color (5 findings)

| File | Line | Value |
|------|------|-------|
| `lib/features/dashboard/presentation/screens/dashboard_screen.dart` | 242 | `Color(0xFFF5F7FA)` |
| `lib/shared/widgets/selection_card.dart` | 34 | `Color(0xFFF5F5F5)` |
| `lib/shared/widgets/selection_card.dart` | 40 | `Color(0xFFE0E0E0)` |
| `lib/shared/widgets/selection_card.dart` | 43 | `Color(0xFFE8E8E8)` |
| `lib/shared/widgets/setup_step_scaffold.dart` | 95 | `Color(0xFFE0E0E0)` |

**Fix:** Replace with `Theme.of(context).colorScheme.surface` or equivalent theme token.

### AP-009 — Fixed Dimensions (1 finding)

| File | Line | Value |
|------|------|-------|
| `lib/features/records/presentation/dialogs/edit_record_dialog.dart` | 563 | `SizedBox(width: 120)` |

**Note:** Spacing-only `SizedBox(height: 8/16/32)` values excluded by regex filter (≤99px).

### AP-007 — Missing Text Scaling (2 findings)

Two `fontSize` declarations without nearby `textScaler` references.

### AP-004 — Pure Black/White (10 findings, P2)

All in `lib/app_theme.dart` — the theme definition file. These are legitimate theme definitions but flagged for awareness.

## Known Noise (AP-020 — Hardcoded Strings)

927 findings, majority are:
- Route path strings (`'detail/:id'`, `'edit/:id'`)
- Debug/Provider registration strings
- Short labels in navigation definitions
- Comments and docstrings

**Root cause:** Regex-based detection cannot distinguish user-facing strings from code infrastructure strings. v2 requires AST-based analysis.

## Detector Limitations (v1.0)

1. **AP-020 noise**: Regex is too broad for hardcoded string detection. Needs Dart AST parser.
2. **AP-003 not implemented**: Contrast computation requires CSS-style color parsing — not yet implemented.
3. **AST rules (AP-005, AP-006, AP-008, AP-010–AP-019, AP-022–AP-029, AP-031)**: All require `analyzer` package or `dart analyze` plugin. Marked as "v2 — AST-based" in skill.
4. **AP-026 (const constructor)**: Cannot be reliably detected with regex alone.
5. **File exclusions**: Only `test/` and `generated/` paths excluded. `app_theme.dart` manually excluded for AP-001.

## Next Steps for v2

1. Integrate `package:analyzer` for Dart AST parsing
2. Implement contrast ratio computation for AP-003
3. Add `.impeccable_ignore` style inline ignore comments
4. Build Flutter `flutter analyze` plugin wrapper for IDE integration
