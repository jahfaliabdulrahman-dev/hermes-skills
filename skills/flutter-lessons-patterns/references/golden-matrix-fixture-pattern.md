# Golden Matrix Fixture Pattern — Honest Router Assertion

Trigger: A spec matrix (e.g., `app-spec/*_golden_intent_matrix.md`) needs to be converted into a testable JSONL fixture with a deterministic harness.

## The Core Principle

A spec matrix's `expected_gate` column often conflates the regex-gate decision (what `IntentRouter.classify()` returns) with the downstream safety-net/LLM path. The JSONL fixture's `expected_gate` MUST equal the actual router output — not the aspirational full-pipeline result. A matrix that asserts aspirational behavior instead of actual output is itself a fake test.

## Reconciliation Protocol

1. Run `IntentRouter.classify()` independently against every row's message
2. Where spec's expected_gate ≠ actual classify output, reconcile to the ACTUAL value
3. Annotate each reconciled row with a `RECONCILED` note documenting WHY
4. Keep `expected_intent` as the aspirational target for future diff (e.g., Phase 0.5 tool-calling router)
5. NEVER silently rewrite expected_gate to make green — the reconciliation must be product-visible

## JSONL Fixture Schema

One JSON object per line, git-tracked at `test/fixtures/golden_intent_matrix.jsonl`:

```json
{"id":"GM-001","message":"عندي قسط تمارا ٢٠٠ ريال","expected_intent":"setup_commitment","expected_gate":"setup_commitment","requires_llm_classify":true,"ground_truth":null,"notes":"Commitment keyword + BNPL provider + amount"}
```

Required fields: id, message, expected_intent, expected_gate, requires_llm_classify, ground_truth, notes.

- `expected_gate`: one of setup_commitment | buy_intent | integrity_query | budget_query | general_chat — MUST match `IntentRouter.classify()` output
- `expected_intent`: 10-value enum (setup_commitment, setup_goal, evaluate_purchase, buy_query, view_integrity, view_budget, log_expense, log_compound_expense, clarify, general_chat) — aspirational for Phase 0.5
- `ground_truth`: nullable literal JSON (never LLM-derived per DEC-024). For figure-bearing rows: `{"item":"جوال","amount":3000}` or `{"items":[{"item":"جوال","amount":2000},{"item":"دراجة","amount":800}]}`
- `notes`: reconciliation annotations, keyword context, DEC references

## Harness Template

Save as `test/golden_intent_matrix_test.dart`:

```dart
import 'dart:convert';
import 'dart:io';
import 'package:flutter_test/flutter_test.dart';
import 'package:myapp/features/chat/routing/intent_router.dart';

const _gateMap = <String, GateDecision>{
  'setup_commitment': GateDecision.setupCommitment,
  'buy_intent': GateDecision.buyIntent,
  'integrity_query': GateDecision.integrityQuery,
  'budget_query': GateDecision.budgetQuery,
  'general_chat': GateDecision.generalChat,
};

const _validIntents = {
  'setup_commitment', 'setup_goal', 'evaluate_purchase', 'buy_query',
  'view_integrity', 'view_budget', 'log_expense', 'log_compound_expense',
  'clarify', 'general_chat',
};

List<Map<String, dynamic>> _loadFixture() {
  final file = File('test/fixtures/golden_intent_matrix.jsonl');
  if (!file.existsSync()) {
    throw StateError('Fixture not found at ${file.path}. Run from project root.');
  }
  return file.readAsLinesSync()
    .where((l) => l.trim().isNotEmpty)
    .map((l) => jsonDecode(l) as Map<String, dynamic>)
    .toList();
}

void main() {
  late List<Map<String, dynamic>> rows;
  setUpAll(() { rows = _loadFixture(); });

  test('fixture has exactly N rows', () {
    expect(rows.length, 32); // adjust per matrix
  });

  test('all expected_intent values present with >=2 rows each', () {
    final counts = <String, int>{};
    for (final r in rows) { counts[r['expected_intent']] = (counts[r['expected_intent']] ?? 0) + 1; }
    for (final intent in _validIntents) {
      expect(counts[intent] ?? 0, greaterThanOrEqualTo(2));
    }
  });

  test('every row has IntentRouter.classify == expected_gate', () {
    for (final r in rows) {
      final actual = IntentRouter.classify(r['message'] as String);
      final expected = _gateMap[r['expected_gate']]!;
      expect(actual, expected, reason: '${r['id']}: "${r['message']}"');
    }
  });

  test('reconciled rows carry RECONCILED notes', () {
    for (final r in rows) {
      if ((r['notes'] as String).contains('RECONCILED')) {
        expect(IntentRouter.classify(r['message'] as String), GateDecision.generalChat,
          reason: '${r['id']}: reconciled row must return generalChat');
      }
    }
  });

  test('ground_truth stores amounts as int literals (DEC-024)', () {
    for (final r in rows) {
      final gt = r['ground_truth'];
      if (gt != null && gt['amount'] != null) {
        expect(gt['amount'], isA<int>(), reason: '${r['id']}: amount must be int literal, not double');
      }
    }
  });
}
```

## File-Path Resolution

The harness loads the JSONL from a package-relative path (`test/fixtures/...`), not an absolute path. This works under `flutter test` from the project root AND in CI because Flutter sets the working directory to the project root.

## Scope Guard

The harness asserts ONLY the regex-gate output (`IntentRouter.classify`). It does NOT assert the full expected_intent path — that requires FakeGeminiService + chat_screen wiring and is deferred to a later phase (e.g., Phase 0.5 tool-calling router). The harness is deterministic, network-free, and provably green with zero pinned LLM responses.
