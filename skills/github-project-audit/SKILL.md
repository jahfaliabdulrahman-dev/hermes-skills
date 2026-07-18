---
name: github-project-audit
description: Deep evaluation of a GitHub repository — structure, security, licensing, maintenance signals, and hype-vs-substance analysis.
category: research
---

# GitHub Project Audit

Use when the user asks to evaluate, review, or analyze a GitHub repository in depth.

## Methodology

Conduct a multi-layered investigation in parallel where possible:

### Layer 1 — Verified Stats (GitHub API)
```python
# Use execute_code to fetch and parse repo metadata
from hermes_tools import web_extract
result = web_extract(["https://api.github.com/repos/OWNER/REPO"])
```
Report: Stars, Forks, Language, Description, Default branch, Created, Pushed, Size, Open issues, License.

### Layer 2 — Contributors & Bus Factor
Fetch contributors via web_extract on `https://api.github.com/repos/OWNER/REPO/contributors?per_page=10`. Report top contributors, concentration risk, and bus factor.

### Layer 3 — Commit Activity & Velocity
Fetch commits via web_extract on `https://api.github.com/repos/OWNER/REPO/commits?per_page=15`. Check: Is it still active? How many commits/day? Single maintainer or team?

### Layer 4 — Documentation Analysis
Read these files if they exist:
- `README.md` — what they claim to be
- `LICENSE` — verify actual license file (not just Cargo.toml/package.json metadata)
- `SECURITY.md` — responsible disclosure process
- `ROADMAP.md` — future direction
- `CONTRIBUTING.md` — community governance

**Critical:** Compare declared license in config files vs actual LICENSE file. GitHub API returns `license: null` when no LICENSE file exists even if package metadata claims MIT/Apache.

### Layer 5 — Source Code Security Audit

#### 5a. Cross-Language Red Flag Patterns (check all repos)
Use GitHub code search via web_search or web_extract to scan for dangerous patterns:
- **Shell execution:** `exec.Command`, `Runtime.exec`, `subprocess`, `child_process`, `Process()`, `NSTask`
- **Network calls:** `http.Get`, `http.Post`, `URLSession`, `fetch`, `axios`, `net.Dial`
- **Obfuscation:** `base64`, `eval`, `exec`, `atob`, dynamic code generation

#### 5b. Dependency Audit
- **Go:** Review `go.mod` — look for unknown modules, excessive deps, or suspicious packages
- **Swift:** Review `Package.swift` dependencies — verify all git URLs are legitimate repos
- **Node:** Check `package.json` + `package-lock.json` for supply chain risks
- **Python:** Check `requirements.txt`/`pyproject.toml` for pinned versions and known vulns

#### 5c. Data Flow Analysis
Trace where data goes:
- **Inbound:** What permissions/API keys does the tool require?
- **Storage:** Where does it persist data? (local DB, files, cloud?)
- **Outbound:** What servers does it contact? Are they user-initiated or background?
- **Exfiltration risk:** Does any code send user data to unexpected endpoints?

#### 5d. Language-Specific Checks
- **Rust:** `unsafe_code` policy in Cargo.toml, TLS choice (rustls vs openssl), input sanitization in exec/shell paths
- **Go:** `exec.Command` usage, HTTP server exposure, CGO usage (`go-sqlite3` = native code)
- **Python:** dependency pinning, sandboxing, subprocess usage
- **Node:** eval usage, dependency audit, env variable handling
- **Swift:** `Process()` (NSTask) shell execution, `URLSession` network calls, keychain access, Accessibility API usage

### Layer 6 — Issues & PRs Reality Check
Fetch issues via web_extract on `https://api.github.com/repos/OWNER/REPO/issues?state=open&per_page=50`. Compare "open issues" count from repo metadata vs actual issues returned. Issues-disabled repos still show a count that includes PRs.

### Layer 7 — Releases & Maturity
Fetch releases via web_extract on `https://api.github.com/repos/OWNER/REPO/releases`. No releases = proof-of-concept, not production-ready.

### Layer 8 — ML/AI Model Legitimacy Verification
When the repo claims to release an ML model (especially foundation models, fine-tuned LLMs, or financial/timeseries models), verify the weights are REAL — not just config dummies or LFS pointer stubs.

#### 8a. Hugging Face Model Audit
- Hit `https://huggingface.co/api/models/ORG/MODEL` — check: `siblings` list, `downloads`, `likes`
- Models with zero downloads + zero likes + recent creation = red flag
- **Critical pitfall:** Hugging Face API returns `size: 0` for all LFS-tracked files (like `model.safetensors`). This is normal — LFS pointers are tiny text files pointing to the real binary. Do NOT flag "0 byte model" as a red flag — download the actual file to verify.
- Download the safetensors file via `https://huggingface.co/ORG/MODEL/resolve/main/model.safetensors` and check actual byte size with `wc -c`

#### 8b. Parameter Count Verification
For safetensors models, read the raw header WITHOUT torch dependency (see `references/safetensors-inspection.md`):
```bash
curl -sL "https://huggingface.co/ORG/MODEL/resolve/main/model.safetensors" -o /tmp/model.safetensors
python3 references/safetensors-inspection.md  # or inline the script
```
- Expected: `total_params ≈ claimed_params` (±1% tolerance for embedding/bias mismatches)
- For fp32 models: `file_size_bytes ≈ claimed_params × 4` (e.g., 24.7M params ≈ 94-99 MB)
- For fp16 models: `file_size_bytes ≈ claimed_params × 2`

#### 8c. Weight Distribution Sanity Check
Trained weights should show:
- Mean near 0 (not 0.5, not 1.0 — those suggest random init or bugs)
- Std dev in 0.02-0.30 range (not 0.001 — dead weights; not 50+ — exploding)
- No tensors that are all-zeros or all-identical
- No extreme outliers (>50σ from mean)
- The output head/projection layers often have wider spread than internal layers — this is normal for trained models

Red flags for fake/dummy weights:
- All weights exactly 0 or exactly 1 — not trained
- Perfect uniform distribution — random init, not trained
- File is only config JSON with no actual tensor data (1-2 KB total)

#### 8d. Academic Paper Verification
For repos claiming a paper:
- Search arXiv: `https://arxiv.org/abs/XXXX.XXXXX` — does paper exist?
- Verify venue claims via DBLP: `https://dblp.org/search/publ/api?q=TITLE`
- Check Semantic Scholar: `https://api.semanticscholar.org/graph/v1/paper/ArXiv:XXXX.XXXXX?fields=citationCount,publicationVenue`
- Verify authors are real researchers (Google Scholar profiles, university affiliations)
- Cross-reference: does the GitHub author name match the paper's first author?

#### 8e. Training Code Reality Check
- Is there actual training/pre-training code, or only inference wrappers?
- Many academic repos release weights + inference but keep training pipeline closed — note this honestly
- Complete absence of any training code while claiming "open-source model" = partial openness

## Output Format

Structure the report as:
1. **Verified Stats** — what the numbers actually say
2. **Architecture & Structure** — code organization, tech stack
3. **Protocol/Design** — how it works internally
4. **Issues Analysis** — what kind of problems exist
5. **Security Assessment** — positives and concerns (red/yellow/green flags)
6. **License & Open Source** — is it legally usable?
7. **Maintenance Outlook** — will it be updated?
8. **Hype vs Substance** — honest verdict
9. **Risk Summary Table** — tool × risk level × key concern matrix

### Layer 9 — Business Model & Marketing Funnel Detection

When the repo is an "awesome list" or curated collection, trace the money:

- Check FUNDING.yml — does the repo accept sponsorships?
- Scan README for product banners (LaunchKit, SaaS, paid services)
- Map the org ecosystem — do they own multiple "awesome-*" repos funneling to a paid product?
- Watch for "Request private X" CTAs — paid service disguised as community feature
- Read CONTRIBUTING.md — does it actually accept external PRs, or are contributions blocked?
- AI-speak detection — files with "theatre-like darkness", "radical subtraction", "chiaroscuro" are AI-generated, not hand-curated
- Preview gap — do claimed files (preview.html) actually exist in the repo, or only on the monetized website?
- Auth routes on companion site — sign-in flows indicate a SaaS product behind the curtain

Flag pattern: "awesome list → product funnel" is a legitimate growth strategy but label it as marketing, not community altruism.

### Layer 10 — Comparison Audit

When the user asks "compare against what we have," benchmark the third-party repo against the user's equivalent toolkit:

1. Identify the user's equivalent capability (Stitch MCP, internal pipeline, etc.)
2. Load the relevant skill for the user's tool to get current capabilities
3. Build a comparison table: Nature, Creator, Output, Customization, Integration, Ownership, Business Model, Pricing, Risks
4. Render a verdict: complementary (use both), substitutive (pick one), or inferior (skip)?

**⚠️ PITFALL — Category Error in Comparison.** The most common failure: comparing form without understanding substance. Impeccable inspects rendered DOM (visual output); building a regex source-code scanner and calling it "the Flutter equivalent" is a category error. When the third-party tool operates at a different abstraction layer than your equivalent, state that honestly. Don't force-fit the comparison.

**⚠️ PITFALL — Adversarial validation before building.** After a comparison audit concludes with a "gap," the natural reflex is to build the equivalent immediately. Run a Light 2-Round adversarial consultation (see `multi-model-consultation` skill) before building. The consultation will catch whether you're building the right tool or just copying the form. Battle-tested: Flutter Design Anti-Patterns audit (2026-07-11) — consultation redirected from 31 regex patterns to 3 custom_lint rules.

Table template and real example in `references/comparison-audit-template.md`.

## Pitfalls
- High star count ≠ quality (viral drops can hit 100K+ stars in days)
- "Source-available" ≠ "open source" (no license = all rights reserved)
- Disabled issues = controlled narrative, not community-driven
- 2-3 contributors = bus factor of 1, high abandonment risk
- Compare age (days since creation) to stars for hype ratio
- GitHub API rate limits (60/hr unauthenticated) — fall back to web_search when hit
- Hardcoded API keys in source may be public demo keys — not always a real secret
- Third-party protocol libraries may violate platform ToS even if code is clean
- **"Is it real?" is the most common deep-dive intent** — prioritize Layers 1 (stats), 3 (commits), 6 (issues), and 8 (model verification). Skip security-heavy Layer 5 unless the repo is a dev tool the user might install.
- **Hugging Face API returns 0-byte sizes for LFS files** — this is normal. Download to verify real size.
- When API tools are unavailable, use terminal with curl, saving to temp files before processing
- **AI skills repos: see `references/ai-skills-ecosystem-audit.md`** — Claude/Cursor/Codex marketplace repos are predominantly markdown, not software. File-type composition is the #1 signal.
- **Single-dominant-contributor (>70% commits) = solo project** regardless of listed contributor count. Check distribution, not headline numbers.
