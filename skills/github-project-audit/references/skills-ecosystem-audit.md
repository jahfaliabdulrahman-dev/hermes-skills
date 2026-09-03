# Skills.sh Ecosystem Audit

How to verify whether a skill on skills.sh is real, functional, and worth installing/recommending. Developed during the OfficeCLI + find-skills/find-docs audit (2026-07-18).

## Methodology

### 1. Sitemap Cross-Reference
```bash
curl -s 'https://www.skills.sh/sitemap-skills-1.xml' | grep -i '<skill-name>'
curl -s 'https://www.skills.sh/sitemap-skills-2.xml' | grep -i '<skill-name>'
```
**Pitfall:** skills.sh short URLs like `/s/<name>` return HTTP 200 for non-existent skills (Next.js shell). Sitemap is definitive.

### 2. GitHub Source Verification
- Verify repo: `https://api.github.com/repos/{owner}/{repo}`
- Check skills dir: `https://api.github.com/repos/{owner}/{repo}/contents/skills`
- Verify SKILL.md: raw.githubusercontent.com

### 3. Quality Signals
| Signal | Green Flag | Red Flag |
|--------|-----------|----------|
| Installs | 1,000+ | < 100 |
| Source | vercel-labs, anthropics, microsoft | Unknown author |
| SKILL.md | Complete YAML + procedural | Stub/empty |
| References | scripts/, references/ present | Bare SKILL.md only |
| Updates | Active in 30 days | Dead 6+ months |

### 4. Confounding Variable Trap (SELF-AUDIT) 🔥

**The #1 failure when auditing your OWN skills before publishing:** attributing success to the wrong variable.

**Real example (2026-07-18):** A governance skill claimed constitutional scaffolding improved EPIC completion. Facts:
- Zero profiles ever loaded the skill
- Zero cron jobs ran (Constitutional Court = placeholder)
- Simultaneous change: SOUL files rewritten from 2-3 lines → 150-581 lines

The governance constitution was a **spectator**, not a participant. SOUL quality was the real driver.

**Prevention:**
1. Did the thing we CLAIM fixed it actually get USED?
2. Did it run BEFORE the improvement?
3. Are there simultaneous changes that BETTER explain the outcome?
4. Is there a simpler explanation? (Occam's Razor)

**When found:** Remove from publication. Rename/restructure. Document honestly. Never ship unproven claims.

### 5. Merge Strategy
When an official skill complements yours:
1. Download official SKILL.md
2. Structure: `# Part 1: Official` / `# Part 2: Extended`
3. Preserve ALL official content
4. Name distinctly: `supabase-fullstack` not `supabase`

### 6. Pre-Publication Quality Gate
1. Has it been USED? — zero usage = theory, not a tool
2. Are referenced files real?
3. Is claimed variable REALLY the cause? (see §4)
4. Does it reference real projects? (LL-NNN/DEC-NNN traceable)

### Real Examples (2026-07-18)
| Skill | Sitemap? | Verdict |
|-------|----------|---------|
| vercel-labs/find-skills | ✅ | Real, installed |
| upstash/context7/find-docs | ✅ | Real, installed |
| /s/find-document | ❌ | Dead alias |
| swarm-governance | ❌ | REMOVED pre-pub (0 uses) |
