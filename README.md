# Hermes Skills — Production-Grade Agent Skills for Flutter, DevOps & AI Governance

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills.sh-10%20skills-6366f1)](https://skills.sh)

**A curated collection of battle-tested agent skills forged in production Flutter projects (CarSah, Hermex Android, Azdal) and multi-agent swarm governance research.**

These aren't tutorials. They're operational knowledge extracted from real projects — every pattern, pitfall, and protocol earned through production debugging, academic rigor, and 59+ documented lessons learned.

---

## Skills

### Flutter & Mobile

| Skill | Description | Size |
|-------|-------------|------|
| [`flutter-android-build-system`](skills/flutter-android-build-system/SKILL.md) | Complete Android build system knowledge — Gradle KTS, AGP 8.8+, namespace/packaging rules, R8/minify, hermex_android crash root-cause patterns (LL-024, LL-025) | 20 KB |
| [`flutter-design-anti-patterns`](skills/flutter-design-anti-patterns/SKILL.md) | 31 design anti-patterns detected at build-time via custom_lint rules — from Hero tag collisions to InputMethodManager ANR triggers | 17 KB |
| [`flutter-isar-clean-arch-setup`](skills/flutter-isar-clean-arch-setup/SKILL.md) | Production Flutter + Isar + Riverpod Clean Architecture from zero — models, repositories, providers, silent migrations, bilingual dynamic collections | 22 KB |
| [`flutter-lessons-patterns`](skills/flutter-lessons-patterns/SKILL.md) | Cross-project Flutter patterns from CarSah + Hermex Android + Azdal — 48 documented patterns (up from 45), now including Azdal Stage-4 cross-project lessons (LL-009/010/011) | 120 KB |
| [`flutter-patterns`](skills/flutter-patterns/SKILL.md) | Class-level Flutter patterns — ANR debugging (Signal 3/SIGQUIT), dialog transient file lifecycle, Flutter text field clipping, widget wrapping anti-patterns | 22 KB |

### Repository & DevOps

| Skill | Description | Size |
|-------|-------------|------|
| [`repo-front-door`](skills/repo-front-door/SKILL.md) | Polish any GitHub repo for outsiders — green CI, automated build artifacts, README structure with download-first layout, brand assets (avatar, social card with RTL support) | 9 KB |
| [`supabase-fullstack`](skills/supabase-fullstack/SKILL.md) | Complete Supabase workflow — frontend (supabase-js, SSR, auth/sessions), backend (Python, CLI, PostgreSQL), and DevOps (migrations, RLS, MCP). Merged from official @supabase/skills + production patterns from Azdal/Hermex | 12 KB |

### AI Governance & Swarm Intelligence

| Skill | Description | Size |
|-------|-------------|------|
| [`swarm-governance`](skills/swarm-governance/SKILL.md) | Flutter swarm governance constitution — 8-article constitutional framework with Constitutional Court (§VI), Governance Council (§V), EPIC completion gates (§19), and zero-trust enforcement protocol | 23 KB |
| [`scsi-self-correcting-swarm`](skills/scsi-self-correcting-swarm/SKILL.md) | Self-Correcting Swarm Intelligence architecture for Hermes Agent multi-agent systems — autonomous error detection, correction loops, and systemic self-healing | 8 KB |

### Research & Auditing

| Skill | Description | Size |
|-------|-------------|------|
| [`github-project-audit`](skills/github-project-audit/SKILL.md) | 10-layer deep evaluation of GitHub repositories — from API-verified stats (stars, bus factor, commit velocity) to ML model weight verification (safetensors inspection, parameter count, distribution sanity) and marketing funnel detection | 11 KB |

---

## Install

### Install all skills at once

```bash
npx skills add jahfaliabdulrahman-dev/hermes-skills
```

### Install individual skills

```bash
npx skills add jahfaliabdulrahman-dev/hermes-skills@repo-front-door
npx skills add jahfaliabdulrahman-dev/hermes-skills@flutter-isar-clean-arch-setup
npx skills add jahfaliabdulrahman-dev/hermes-skills@flutter-android-build-system
npx skills add jahfaliabdulrahman-dev/hermes-skills@flutter-design-anti-patterns
npx skills add jahfaliabdulrahman-dev/hermes-skills@flutter-lessons-patterns
npx skills add jahfaliabdulrahman-dev/hermes-skills@flutter-patterns
npx skills add jahfaliabdulrahman-dev/hermes-skills@swarm-governance
npx skills add jahfaliabdulrahman-dev/hermes-skills@scsi-self-correcting-swarm
npx skills add jahfaliabdulrahman-dev/hermes-skills@github-project-audit
npx skills add jahfaliabdulrahman-dev/hermes-skills@supabase-integration
```

---

## Why These Skills Exist

Every skill in this repository was born from a production failure that became a permanent lesson:

- **GL-016 (Identity Conflation):** An AI agent's confession was stored as a human statement because memory had no role-based segregation. → `scsi-self-correcting-swarm` now enforces Role-Based Memory tables (human/agent/system).
- **LL-024 (ClassNotFoundException):** `namespace` in `build.gradle.kts` didn't match `MainActivity.kt` package. → `flutter-android-build-system` now gates every build with 5 preflight checks.
- **LL-025 (Instant Crash):** `isMinifyEnabled=true` + Isar → R8 stripped adapters. → Same skill now auto-detects `isar:` in pubspec and blocks the misconfiguration.
- **Governance Deadlock (EPIC-001):** Lead Architect abandoned after 27 minutes because text-only SOUL.md provided no enforcement. → `swarm-governance` now enforces 6 constitutional gates before any EPIC closure.

**We don't ship "best practices." We ship scar tissue.**

---

## For Skill Authors

Each skill follows the [skills.sh](https://skills.sh) format:

```
skills/<name>/
├── SKILL.md          # YAML frontmatter + procedural knowledge
├── references/       # Deep-dive technical references
├── scripts/          # Automation scripts
└── assets/           # Templates, images, configuration
```

To contribute a skill to this collection:

1. Fork this repo
2. Create your skill directory under `skills/`
3. Write `SKILL.md` with proper YAML frontmatter (`name`, `description`, `version`)
4. Include references and scripts as needed
5. Submit a PR

---

## License

Apache 2.0 — see [LICENSE](LICENSE).

These skills are open-source and free to use, modify, and distribute. Attribution appreciated.

---

## Author

**Eng. Abdulrahman Jahfali** — 17 years in energy sector operations, AI/Flutter architect, swarm governance researcher.

- GitHub: [@jahfaliabdulrahman-dev](https://github.com/jahfaliabdulrahman-dev)
- Projects: CarSah, Hermex Android, Azdal, RQS V3.1, Kronos

---

<p align="center">
  <sub>Built with battle scars. Governed by constitution. Verified on device.</sub>
</p>
