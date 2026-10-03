# Two-Layer Empty-Selection Guard — worked detail (DEC-069, CARRY-106, 2026-08-14)

Session-specific implementation record behind the operational rules in SKILL.md
("A founder walk is a first-class test"). Captured here so a future round can
reproduce the exact shape without re-deriving it.

## The founder-found defects (both "fatal", both invisible to 437 tests)

1. **Fresh add:** a service record could be saved with ZERO performed services
   selected. `_selectedTaskIds` empty → `performed` = empty list → `onSave`
   called with no validation. The Save button's disable condition covered
   `odometer == null || cost == null` but NEVER the task selection.
2. **Edit:** unchecking every service then saving was accepted — same hole in
   the edit path.

Why 437 tests + mutation suites + auditor reviews missed it: no gate ever asked
the founder's question — "can this form be saved in a state the domain
forbids?" The founder walking the app IS the test that finds it.

## The two-layer fix (exact shape)

**UI layer (both screens — add + edit):** the disable condition joins the
empty selection:

```dart
final canSave = _selectedTaskIds.isNotEmpty &&
    _parsedOdometer != null &&
    _parsedCost != null;
```

plus an l10n hint («اختر خدمة واحدة على الأقل» / "select at least one")
rendered under the list when the selection is empty.

**Business layer (defense in depth — the UI can be bypassed by a direct call):**

- `AddServiceRecordUseCase` rejects an EMPTY list → `ValidationFailure` with
  code `VALIDATION_EMPTY_TASKS`.
- `EditServiceRecordUseCase` rejects a NON-null empty list (`[]` = "remove
  them all" — forbidden) but ACCEPTS `null` (= "keep the existing links").
  The null-vs-empty distinction is the subtle half; collapsing them either
  blocks legitimate "don't touch" edits or re-opens the hole.

**Acceptance (mutation-proven):** disable the business check → the guard test
goes red; restore → green. A guard that cannot be turned red by a planted
violation is not a guard.

## CARRY-106 — coverage transfer when a rule change invalidates a test

The old F-01 test asserted «editing to REMOVE the last task deletes the link
and reverts the anchor (lastDoneKm null, notStarted)». DEC-069 forbade the
empty result, so that assertion could not survive — the rewrite to «empty list
is rejected» was CORRECT. But nothing replaced the original guarantee, and a
planted mutation (drop the removed tasks from `recalcById`) stayed GREEN —
the guard was silently gone.

The replacement test: a record with TWO tasks (oil + brakes) → delete ONE
(legal under DEC-069) → the removed task reverts to its anchor
(45,000 · 52,500 · upToDate) while the kept task holds (50,000 · 80,000), and
links verified on both sides.

**Rule:** rewriting a test whose assertion a rule change made impossible must
re-express the OLD guarantee against the NEW law — never just delete it.

## Verification evidence (what the delivery must show)

1. Device walk: fresh-add attempt with nothing selected → hint visible + Save
   `enabled=false` + a forced bypass does nothing. Same on the edit path.
2. Use-case direct call with empty list → named ValidationFailure.
3. Mutation: re-enable/accept-empty → guard test red → restored → green.
4. Local suite green + CI green with the workflow name + every step RAN.
