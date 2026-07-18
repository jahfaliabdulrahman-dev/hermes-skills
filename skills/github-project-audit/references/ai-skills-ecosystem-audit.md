# AI Agent Skills Ecosystem Audit — Extension to Layer 11

Added 2026-07-17 from live audit of 9 repos in the Claude Skills marketplace ecosystem.

## Core Insight

Repos in the Claude/AI agent skills ecosystem follow a different rulebook than traditional software. They are predominantly **markdown instruction files** (SKILL.md), not executable code. Stars are inflated by marketplace promotion. The key differentiator is **file-type composition.**

## The #1 Signal: Markdown-to-Code Ratio

When auditing an AI skills repo, count the file types before anything else:

```
Markdown files (>90% of total) + Zero executable code = Prompt/skill collection, NOT software
Markdown files + Actual code (Python/JS/TS/Rust/Go/Dart) = Legitimate tool with agent instructions
```

### Real examples from the 2026-07-17 audit:

| Repo | Stars | Markdown | Code Files | Verdict |
|------|-------|----------|------------|---------|
| `Leonxlnx/taste-skill` | 64K | 29 | **0** | Pure prompt — "gives AI good taste" is just design instructions |
| `obra/superpowers` | 256K | 82 | 47 (shell+JS) | Methodology with test infrastructure — legitimate but thin |
| `coreyhaines31/marketingskills` | 40K | 297 | 65 | Comprehensive prompt collection for 45 marketing domains |
| `upstash/context7` | 59K | Some | Heavy TS | Actual SaaS product — not a "skill" at all |
| `thedotmack/claude-mem` | 88K | Docs | JS package | Legitimate tool (npm package), but 95% single-contributor |

## Dominant-Contributor Analysis

The headline "100 contributors" is misleading. Check the distribution:

| Repo | Top Contributor | Their % | Real Team Size |
|------|----------------|---------|----------------|
| `thedotmack/claude-mem` | thedotmack | **95%** (1860/1960) | 1 |
| `obra/superpowers` | obra | **75%** (475/636) | 1 + minor contributors |
| `Leonxlnx/taste-skill` | Leonxlnx | **98%** (130/133) | 1 |
| `coreyhaines31/marketingskills` | coreyhaines31 | ~85% | 1 + minor |

**Rule:** >70% from one person = solo project, regardless of listed count.

## Claude Marketplace Ecosystem Red Flags

1. Repo exists solely as a Claude Code / Cursor / Codex plugin — no standalone runnable binary
2. Description format: "gives your AI [capability]" — this is a prompt, not a product
3. Multiple repos in one influencer thread pointing to same `anthropics/skills` base
4. "Not prompts. Not wrappers. A real operating stack." when the repo is just SKILL.md files
5. **Litmus test:** Delete the parent platform (Claude Code). Does this repo do anything? No → it's content, not infrastructure.

## Efficient Batch Audit Pattern

For auditing 3+ repos:

1. **GitHub API first** — fetch metadata for all repos in one loop (stars, language, dates, size)
2. **Contributor distribution** — fetch top 10 per repo, compute concentration
3. **Git tree** — fetch recursive tree, count markdown vs code files
4. **Sparse clone** only repos that pass initial filters:

```bash
git clone --depth 1 --filter=blob:none --sparse URL
cd REPO
git sparse-checkout set SKILL.md README.md skills/
```

5. **Read key files** with read_file, compare claims vs reality

## Comparison-to-Our-Projects Template

When asked "how does this compare to what we have?":

1. Identify our equivalent capability (not necessarily same form factor)
2. Count our comparable assets (skills, files, lines of research)
3. Build table: Nature, Technical Depth, Team, CI/CD, Governance, Research
4. **Avoid the category error:** don't compare markdown prompts to our governance architecture — state the abstraction level difference honestly
