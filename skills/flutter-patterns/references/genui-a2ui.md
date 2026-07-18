# Flutter GenUI & A2UI — Dynamic UI for AI Agents

> **Corrected:** 2026-05-16 — Previously assessed as "near impossible (9/10)."
> Actual difficulty: **5/10** with official Google tooling.

---

## Overview

Google released **A2UI (Agent-to-UI)** protocol in December 2025 and a companion
**Flutter GenUI SDK** (beta). These enable AI agents to describe UIs via
declarative JSON, which Flutter renders from a pre-built widget catalog.
This is NOT runtime code execution — it's JSON-driven widget composition,
making it app-store-safe.

---

## Key Facts

| Fact | Detail |
|------|--------|
| Protocol | A2UI — Agent-to-UI, open standard |
| Flutter package | `genui_a2ui` on pub.dev |
| Mechanism | Agent sends JSON UI schema → Flutter renders from widget catalog |
| Code execution | NONE — declarative only, safe for App Store / Play Store |
| Release date | December 2025 (Google Developers Blog) |

---

## Architecture

```
AI Agent → JSON UI Schema → genui_a2ui → Flutter Widget Catalog → Rendered UI
                                                                    ↓
                                                              User Interaction
                                                                    ↓
                                                              AI Agent (next turn)
```

The agent describes WHAT to show, not HOW to render it. The widget catalog
provides pre-built components (cards, charts, forms, buttons). The agent
composes them via JSON.

---

## Widget Catalog (Example Components)

```json
{
  "type": "bar_chart",
  "title": "Monthly Spending",
  "data": [...]
}
```

Common widget types for fintech/finance UIs:
- `summary_card` — key metric display
- `bar_chart`, `pie_chart`, `line_chart` — data visualization
- `action_buttons` — quick-reply buttons
- `quick_input_form` — minimal data capture

---

## Why This Matters for Baseera

The hybrid architecture (LLM for understanding, SQL/Python for math, GenUI for display)
is now **fully supported by official Flutter tooling**. This means:

1. The agent can dynamically compose financial dashboards based on user questions
2. No hardcoded report screens — UI adapts to the conversation
3. App-store compliant (no `eval()`, no code generation)
4. RTL/Arabic support via Flutter's built-in `Directionality`

---

## Sources

- Google Developers Blog: "Introducing A2UI" (Dec 15, 2025)
- [a2ui.org](https://a2ui.org/) — protocol specification
- [docs.flutter.dev/ai/genui](https://docs.flutter.dev/ai/genui) — Flutter GenUI SDK docs
- [pub.dev/packages/genui_a2ui](https://pub.dev/packages/genui_a2ui) — Dart package

---

## Pitfalls

- **NOT runtime code execution** — agent sends JSON, not Dart/JS. Gemini's claim
  that "the agent writes Flutter code" is misleading.
- **Widget catalog must be pre-defined** — the agent can only compose from
  widgets you've built. It cannot invent new widget types.
- **Beta status** — GenUI SDK is beta. Test thoroughly before production use.
- **Interaction round-trips** — each user action goes: tap → agent → new JSON.
  Latency must be managed (Gemini Flash for simple responses, Pro for complex).
