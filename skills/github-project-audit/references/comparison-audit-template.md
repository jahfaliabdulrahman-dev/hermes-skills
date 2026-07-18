# Comparison Audit Template

Use when the user asks to benchmark a third-party repository/tool against their own equivalent toolkit.

## Table Structure

| Dimension | Third-Party | Our Toolkit |
|-----------|------------|-------------|
| **Nature** | Static/dynamic, content vs pipeline | What form does it take? |
| **Creator** | Company/individual behind it | Who built ours? |
| **Output** | What does it produce? | What does our equivalent produce? |
| **Customization** | Pre-made vs custom | Can we create from scratch? |
| **Integration** | Copy-paste vs API | How does it connect to our workflow? |
| **Ownership** | Third-party risk | First-party guarantee |
| **Business Model** | How do they make money? | Our cost structure |
| **Pricing** | Free, freemium, paid? | Our pricing |
| **Risks** | Bus factor, abandonment, pivot-to-paid | Our risks |

## Verdict Categories

- **Complementary** — use both, they solve different parts of the problem
- **Substitutive** — pick one, they solve the same problem
- **Inferior** — skip, ours does everything better

## Real Example (awesome-design-md vs Google Stitch)

| Dimension | awesome-design-md | Google Stitch |
|-----------|-------------------|---------------|
| Nature | Static markdown files | Live design-to-code pipeline |
| Creator | VoltAgent (startup, 1 developer) | Google |
| Output | DESIGN.md text files only | DESIGN.md + screenshots + HTML |
| Customization | Pick from 73 pre-made brands | Create custom design language |
| Integration | Copy-paste file into project | MCP API with tool calls |
| Ownership | Third-party, bus factor = 1 | First-party, Google-backed |
| Business Model | Marketing funnel → paid products | Google Cloud service |
| Pricing | Free (paid private requests) | Free (API key required) |
| Risks | Abandonment, pivot-to-paid | Google service deprecation |

**Verdict:** Complementary but asymmetric. Use awesome-design-md for design inspiration/reference. Use Stitch for actual production pipeline.
