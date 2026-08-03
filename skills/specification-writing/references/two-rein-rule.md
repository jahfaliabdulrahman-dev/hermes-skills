# The Two-Rein Rule — Derivation & Source Material

> Reference file for specification-writing skill v3.4.0
> Created: 2026-07-30
> Sources: Anthropic YC Session (Boris Cherny), Token Economics Analysis, Founder Discussion

## Anthropic YC Insights (Boris Cherny on Claude Code)

1. **80% Prompt Reduction:** Anthropic removed 80% of Claude Code's internal prompts on Opus 5 release. Advanced models need less scaffolding.

2. **Verification over Prompt Engineering:** The key skill is now building automated verification (test suites, linters, UI diff tools), not crafting better prompts.

3. **Bun Case Study:** 500K lines Zig→Rust, 11 days, 64 parallel agents. Enabled by deterministic test suite as referee.

4. **Automated Maintenance:** 20-30 daily cron agents clean dead code, enforce consistency, expand tests.

### Caveats
- Context compounding: open loops → exponential token burn
- Requires deterministic tests: fails without them
- Human steering still needed: 3 critical bugs caught pre-merge in Bun rewrite

## Token Economics

| Approach | Cost | Time |
|----------|------|------|
| Traditional Outsourcing | $3K-$8K | 1-3 months |
| AI-Assisted ($100/mo) | ~$100 | 80% faster |

**Principles:** Max 3 retries, context isolation between modules, model cascading.

## Founder's Synthesis (2026-07-30)

Two extremes are both wrong when applied uniformly. The Governance Gradient is optimal:

| Stage | Error Cost | Safe to Delegate? |
|-------|:----------:|:-----------------:|
| 1-2 (Idea/Feasibility) | Strategic | ❌ |
| 3 (Design) | Hours | ✅ AI leads |
| 4 (Data/Security) | Weeks | ❌ |
| 5 (Iteration) | Days | ❌ |
| 6 (Production) | Business | ❌ |

**Model Cascading:** Loose rein → frontier models. Tight rein → mid-tier. Mechanical → lightweight.
