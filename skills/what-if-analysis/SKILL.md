---
name: what-if-analysis
description: "Use when planning/gating — «ماذا لو» What-If anticipation."
version: 1.0.0
author: Sulaiman
tags: [planning, risk, premortem, what-if, hazop, anticipation, governance, methodology]
---

# What-If Analysis — anticipatory skepticism as a working protocol

Turn «ماذا لو» / "what if" from a talent into a **protocol**: assume the
failure (or event) HAS ALREADY HAPPENED, explain how it happened via backward
chains, extract early-warning indicators, assign owners. 75+ years of
independent practice across 8 fields (HAZOP 1963 · FMEA 1949 · Shell scenario
planning · CIA tradecraft · PreMortem · chaos engineering · counterfactual
psychology · Popper), distilled into ONE session protocol.

Use it when planning a project, committing to a big decision, closing a stage
gate, or when the user asks about «ماذا لو» / pre-mortem / anticipatory thinking.
The full Arabic methodology guide (8 schools, timeline, sources, templates,
anti-patterns) ships at **`references/what-if-guide.ar.md`** — read it when
teaching or when the user asks for the deep study version.

## Core mechanics — why it works

1. **Past tense beats future tense.** "The project already failed — why?"
   (prospective hindsight) raises correct reason-identification by ~30%
   (Mitchell/Russo/Pennington 1989; Klein HBR 2007 — the PreMortem).
2. **Ask how, not whether.** "How could it happen?" (CIA 2009) suspends the
   probability debate and moves straight to preparation.
3. **No indicator → anxiety; no owner → a promise.** A scenario with no
   early-warning signal or owner does not enter the output table.

## When to use (triggers)

- Before starting an EPIC / major commitment / Stage 0 → **full 60-min session**
- At every stage gate → **15-min quick pass** on the NEW critical assumptions
- Weekly during execution → indicator review, 15 min
- After any real incident → Qass Al-Haq (root cause) THEN "what if it recurs?"
- After unexpected big success → "what if it doubles — what breaks?" (SWIFT
  covers POSITIVE outcomes; the protocol is not only fear-mongering)

## The 60-minute session protocol

| Minutes | Step | Detail |
|---------|------|--------|
| 0–5 | Fix the scope | What system/decision? Write it — don't discuss from memory |
| 5–15 | PreMortem | "It failed disastrously in 3 months — write the reasons" (individual write 5m → share 5m) |
| 15–35 | Focused What-If | On 3–5 CRITICAL assumptions only: "assume it fell — how?" (backward chain) |
| 35–50 | Guide-word sweep | Over 5–8 main nodes × the relevant words (not all 7 per node) |
| 50–60 | Rank & output | Sort by (likelihood × impact) top-10; each item gets indicator + response + owner |

## Guide words — the 7 (from HAZOP, adapted universal)

| Word | Meaning | Software example | Ops/finance example |
|------|---------|------------------|---------------------|
| لا (No) | nothing happens | service silent | supply stops |
| أكثر (More) | quantity up | larger load | over-pressure |
| أقل (Less) | quantity down | missing columns | under-pressure |
| جزء من (Part of) | only half | half-page read | half shipment |
| بالإضافة إلى (As well as) | unexpected extra | new column appears | contaminant |
| عكس (Reverse) | inverted | pages reversed / sign flipped | reverse flow |
| غير ذلك (Other than) | entirely different | different bank/format | different material |

## Output table (copy-ready)

| # | What-if…? | Word | Impact | Likelihood | Early-warning indicator | Response | Owner |
|---|-----------|------|--------|-----------|-------------------------|----------|-------|

Impact/likelihood: low / medium / high. No fake numbers — relative ranking.

## Session rules (5)

1. Defer filtering — generate freely first, critique later.
2. No personal defense — challenge the plan, not the planner.
3. **Indicator or nothing** — a scenario with no early-warning signal = anxiety.
4. **Owner per item** — no owner = floating promise.
5. **Cadence review** — a session without follow-up is theater (10–15 min weekly).

## Anti-patterns

- «ماذا لو» without indicators → chronic anxiety consuming the team
- Opening every possibility without ranking → decision paralysis (top items act; the rest watch)
- Forgetting the positive face (what if it succeeds beyond plans?)
- Mixing anticipatory sessions with retrospective RCA — different meetings
- Skepticism aimed at people instead of ideas
- Over-documenting — one table per session is enough

## Integration with existing protocols

- **Red Team Attack** = adversarial EXECUTION of this method; **Qass Al-Haq**
  = its retrospective mirror; What-If = the ANTICIPATION layer before both.
- Drops into stage gates (3.5/4) and pairs with `specification-writing` /
  `architecture-critique`; every EPIC gets a PreMortem before kickoff.

## Solo mode (30 min)

1. Before any new commitment: "if this fails within 3 months — first 3 reasons?"
2. Before any technical decision: "if the main assumption falls — how do I detect it early?"
3. Weekly: "which indicator moved since last session?"
4. On big success: "if this doubles — what breaks?"

## Sources (compact)

Klein, *Performing a Project Premortem* (HBR 2007) · Mitchell/Russo/Pennington
1989 · CIA *Tradecraft Primer* (2009) · OSHA PSM accepted PHA methods (What-If,
HAZOP, FMEA, FTA) · HAZOP/IEC 61882 · SWIFT/ASEMS · Army *Red Team Handbook* ·
FMEA/MIL-P-1629 · principlesofchaos.org · Roese counterfactual theory · Popper
falsifiability. Full citations in the Arabic guide.
