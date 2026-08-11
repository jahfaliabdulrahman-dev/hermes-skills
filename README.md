# Hermes Skills — Production-Grade Agent Skills for Flutter, DevOps & AI Governance

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills.sh-11%20skills-6366f1)](https://skills.sh)
[![Sponsor](https://img.shields.io/badge/sponsor-GitHub%20Sponsors-ea4aaa.svg)](https://github.com/sponsors/jahfaliabdulrahman-dev)

**A curated collection of battle-tested agent skills forged in production Flutter projects (CarSah, Hermex Android, Azdal). Every pattern, pitfall, and protocol earned through real debugging sessions — 48 documented patterns and counting.**

---

## Skills

### 🧭 Foundation — Start Here

| Skill | Description | Size |
|-------|-------------|------|
| [`specification-writing`](skills/specification-writing/SKILL.md) | The AI-Agent App Build Specification Pack framework — 22-slot structure (27+ files) governing every project from product discovery to financial models and personal build plans. Enforces the NO PROCEDURAL REDUCTION rule. This is the blueprint every project starts from | 10 KB |
| [`flutter-soul-stewardship`](skills/flutter-soul-stewardship/SKILL.md) | Exact procedure for writing and maintaining SOUL.md agent identity files — the REAL driver of multi-agent swarm performance. Deterministic, cross-profile, machine-verifiable | 4 KB |

### Flutter & Mobile

| Skill | Description | Size |
|-------|-------------|------|
| [`flutter-android-build-system`](skills/flutter-android-build-system/SKILL.md) | Complete Android build system knowledge — Gradle KTS, AGP 8.8+, namespace/packaging rules, R8/minify, hermex_android crash root-cause patterns (LL-024, LL-025) | 20 KB |
| [`flutter-design-anti-patterns`](skills/flutter-design-anti-patterns/SKILL.md) | 31 design anti-patterns detected at build-time via custom_lint rules — from Hero tag collisions to InputMethodManager ANR triggers | 17 KB |
| [`flutter-isar-clean-arch-setup`](skills/flutter-isar-clean-arch-setup/SKILL.md) | Production Flutter + Isar + Riverpod Clean Architecture from zero — models, repositories, providers, silent migrations, bilingual dynamic collections | 22 KB |
| [`flutter-isar-testing`](skills/flutter-isar-testing/SKILL.md) | In-memory Isar testing setup (real Isar DB under `flutter test`) — `libisar.dylib` symlink, `openTestIsar()`, and the **STOP-28 corrected rule: `runAsync` wraps the WAITING only, never `pump`/`tap`** (the ambiguous wording that hung Linux CI for 10 min and spread to 13 files). ⚠️ **SELF-BUILT skill** — no official flutter.dev/isar.dev equivalent exists; review before trusting | 7 KB |
| [`flutter-lessons-patterns`](skills/flutter-lessons-patterns/SKILL.md) | Cross-project Flutter patterns from CarSah + Hermex Android + Azdal — 48 documented patterns (up from 45), now including Azdal Stage-4 cross-project lessons (LL-009/010/011) | 120 KB |
| [`flutter-patterns`](skills/flutter-patterns/SKILL.md) | Class-level Flutter patterns — ANR debugging (Signal 3/SIGQUIT), dialog transient file lifecycle, Flutter text field clipping, widget wrapping anti-patterns | 22 KB |

### Repository & DevOps

| Skill | Description | Size |
|-------|-------------|------|
| [`repo-front-door`](skills/repo-front-door/SKILL.md) | Polish any GitHub repo for outsiders — green CI, automated build artifacts, README structure with download-first layout, brand assets (avatar, social card with RTL support) | 9 KB |
| [`skill-ecosystem-sync`](skills/skill-ecosystem-sync/SKILL.md) | Complete skill ecosystem update workflow — update all skills across 4 registries (npx/skills.sh, GitHub, ClawHub, profile swarm). 5-phase systematic procedure. The meta-skill that keeps all other skills current | 6 KB |
| [`supabase-fullstack`](skills/supabase-fullstack/SKILL.md) | Complete Supabase workflow — frontend (supabase-js, SSR, auth/sessions), backend (Python, CLI, PostgreSQL), and DevOps (migrations, RLS, MCP). Merged from official @supabase/skills + production patterns from Azdal/Hermex | 12 KB |

### Research & Auditing

| Skill | Description | Size |
|-------|-------------|------|
| [`github-project-audit`](skills/github-project-audit/SKILL.md) | 10-layer deep evaluation of GitHub repositories — from API-verified stats (stars, bus factor, commit velocity) to ML model weight verification (safetensors inspection, parameter count, distribution sanity) and marketing funnel detection | 11 KB |

---

## 💎 Premium — Spec Pack Generator ($19)

The skills above are **free and open-source** (Apache 2.0) — that's the framework.

**Premium** is the automation that builds and verifies the entire Spec Pack for you:

| Feature | Free (GitHub) | Premium ($19) |
|---------|:-------------:|:--------------:|
| `specification-writing` SKILL.md framework | ✅ | ✅ |
| `generate_spec_pack.py` — creates all 27+ files | ❌ | ✅ |
| `verify_spec_pack.py` — exit-code compliance gate | ❌ | ✅ |
| Templates + landing README | ❌ | ✅ |
| Priority updates & support | ❌ | ✅ |

**Buy once, use forever.** Instant digital delivery — no subscription, no account required.

- 🔗 **Purchase:** [spec-pack-premium on Lemon Squeezy](https://jahfali-skills.lemonsqueezy.com)
- 🛒 **Also listed:** [MCP Market](https://mcpmarket.com)

---

## Install

### Install all skills at once

```bash
npx skills add jahfaliabdulrahman-dev/hermes-skills
```

### Install individual skills

```bash
npx skills add jahfaliabdulrahman-dev/hermes-skills --skill specification-writing
npx skills add jahfaliabdulrahman-dev/hermes-skills --skill flutter-soul-stewardship
npx skills add jahfaliabdulrahman-dev/hermes-skills --skill flutter-isar-clean-arch-setup
npx skills add jahfaliabdulrahman-dev/hermes-skills --skill flutter-android-build-system
npx skills add jahfaliabdulrahman-dev/hermes-skills --skill flutter-design-anti-patterns
npx skills add jahfaliabdulrahman-dev/hermes-skills --skill flutter-lessons-patterns
npx skills add jahfaliabdulrahman-dev/hermes-skills --skill flutter-patterns
npx skills add jahfaliabdulrahman-dev/hermes-skills --skill repo-front-door
npx skills add jahfaliabdulrahman-dev/hermes-skills --skill supabase-fullstack
npx skills add jahfaliabdulrahman-dev/hermes-skills --skill github-project-audit
npx skills add jahfaliabdulrahman-dev/hermes-skills --skill skill-ecosystem-sync
```

---

## Why These Skills Exist

Every skill in this repository was born from a production failure that became a permanent lesson:

- **LL-010 (Live-Device Verification):** 5 critical bugs found on real device AFTER `flutter analyze` clean + 34/34 tests passing + 2 AI auditors signing APPROVE. → `flutter-lessons-patterns` now enforces live-device verification as the final gate before any DONE declaration.
- **LL-024 (ClassNotFoundException):** `namespace` in `build.gradle.kts` didn't match `MainActivity.kt` package. → `flutter-android-build-system` now gates every build with 5 preflight checks.
- **LL-011 (Disabled Button Colors):** Material silently substitutes its default palette when `onPressed: null` — custom colors lost without error. → Same skill now enforces explicit `disabledBackgroundColor`/`disabledForegroundColor`.
- **SOUL Quality Conundrum:** EPIC-001 failed in 27 minutes because 2-3 line SOUL.md files gave agents no identity. After rewriting SOULs to 150-581 lines, EPIC-002 succeeded. → `flutter-soul-stewardship` is the real governance — not constitutional courts, but strong agent identity.

**We don't ship "best practices." We ship scar tissue.**

---

## Support

These skills are free and open-source (Apache 2.0). If they save you hours of debugging, consider supporting the work:

- 💖 [GitHub Sponsors](https://github.com/sponsors/jahfaliabdulrahman-dev) — recurring support
- ☕ Buy Me a Coffee — coming soon

Every contribution funds more battle-tested patterns, device verification, and new skills.

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
