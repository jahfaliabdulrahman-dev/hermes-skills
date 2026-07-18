# Competitive Benchmark — Reference Results
# Session: 2026-07-11
# Context: ArXiv paper "Machine-Enforceable AI Governance"

## Round 1: Standalone Bug Fixing (n=1 per model)

Same 4-bug suite (C-1 through C-5), fresh git worktree, 200 turns.

| Model | Generation | Bugs Fixed | Time | Files | Notes |
|-------|-----------|------------|------|-------|-------|
| GPT-4o | 2024 | 0/4 | 29s | 0 | Planning only, no file edits |
| Claude Sonnet 4 | 2024 | 0/4 | 3m 55s | 0 | Planning only, no file edits |
| GPT-4.1 | 2026 | 4/4 | 143s | 8 | 4 commits, all bugs verified |
| Gemini 2.5 Pro | 2025 | 4/4 | 206s | 11 | 4 commits, 259+ 80- |
| DeepSeek-v4-pro | 2026 | 4/4 | 313s | 8+ | 4 commits |
| Claude Opus 4 | 2026 | 4/4 | 312s | 10 | 4 commits, 266+ 30- |

## Round 2: Orchestration Benchmark (n=1 per model)

Each model acts as Lead Architect for 9-agent swarm WITHOUT constitution. Text-only SOUL governance.

| Model | Bugs Fixed | Time | Files | Key Behavior |
|-------|-----------|------|-------|-------------|
| MiniMax M3 | 4/4 | 10m 23s | 14 | Bundled TTF fonts + OFL; MoA deadlock→self-recover |
| Qwen 3.7 Plus | 4/4 | 11m 12s | 9 | 3 reports (REPORT, COMPLETE, RELEASE CHECKLIST) |
| GLM-5.2 | 4/4 | 19m 2s | 13 | SCSI scan (6 patterns, 0 findings); 4554+ insertions |
| Claude Sonnet 5 | 0/4 | 20m 30s | 0 | Workspace contamination→analysis paralysis→exit |

## Our System (Constitution)

| Metric | Value |
|--------|-------|
| Model | DeepSeek-v4-pro (Triple-Chinese MoA) |
| Governance | 8-article constitution, 6 gates, Constitutional Court |
| Bugs Fixed | 4/4 |
| Time | 3h 16m |
| Gates Met | 6/6 (all verified) |
| Regressions | 0 |
| Guardian | ALL CLEAR |
| Human Help | Secrets only |

## Key Findings

1. **Frontier convergence:** All 2025-2026 models hit 4/4 standalone.
2. **25% ungoverned failure:** 1 in 4 orchestrators fail without constitution.
3. **Governance = product:** 3h 16m = 5min bug-fix + 3h 11min governance work. Each gate maps to a documented failure mode (GL-001 through GL-013).
4. **Self-correction works:** Lead Architect detected Ruling #497 vs WONTFIX contradiction and self-corrected.
