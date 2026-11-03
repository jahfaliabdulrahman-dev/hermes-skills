---
name: github-project-audit
version: 1.0.0
description: Use when auditing a GitHub repo (فحص مستودع، نجوم، رخصة). Deep evaluation of a GitHub repository — structure, security, licensing, maintenance signals, and hype-vs-substance analysis.
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

**Star history is NOT reliably available from the API.** `repos/O/R/stargazers` can 404 even with an
authenticated token, and the GraphQL `stargazers` connection can return `totalCount: 0` with empty
edges. Do not fight it and do not fall back to a third-party series — use dated **Wayback snapshots**
of the repo page and read the exact counter out of the archived HTML:
```bash
curl -s "https://web.archive.org/cdx/search/cdx?url=github.com/OWNER/REPO&output=json&filter=statuscode:200"
curl -s "https://web.archive.org/web/TS/https://github.com/OWNER/REPO" -o snap.html
grep -oE 'repo-stars-counter-star[^>]{0,160}' snap.html   # aria-label="N users starred", title="N,NNN"
```
**Also check the OLD repo name** — a renamed repo has snapshots under its previous slug (find it via
`git log --grep=renamed` or the `repository =` field history in Cargo.toml/package.json); those give the
true early baseline the current URL never had.

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

**Then census the pull requests — this is the absorption signal, and it is the half a star count hides.**
Merge commits are NOT the merge history: squash and rebase merges leave a plain commit message ending in
`(#N)`, so a repo can show 28 commits with only 8 `Merge pull request` messages and still have merged a
dozen PRs. Count from the issues endpoint, where every PR carries a `pull_request` object. The **search
API** is the cheap path and it keeps answering after the 60/hr core quota is spent:
```bash
curl -s "https://api.github.com/search/issues?q=repo:OWNER/REPO+is:pr+is:merged&per_page=100"   # total_count
curl -s "https://api.github.com/search/issues?q=repo:OWNER/REPO+is:pr+is:open&sort=created&order=asc&per_page=15"
```
Report four numbers: merged count, open count, the **date of the last merge**, and the **age of the oldest
open PR**. `open_issues_count` in the repo metadata is the SUM of issues and PRs (measured: 133 = 29
issues + 104 PRs) — decompose it before quoting either half.

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

### Layer 11 — Dev-Tool Claims Verification (Oracle Test)

When a dev tool claims accuracy ("retrieves any function", "detects dead code"), do not take README numbers at face value — and do not rely on the tool's own eval corpus alone. Run a mini-oracle on the user's OWN code before adoption:

1. Build ground truth cheaply with the language's own tooling: Python `ast` module (~20 lines), Dart `dart analyze` + a quick AST pass, TS `ts-morph`. A few hundred symbols is enough.
2. Run the tool on the same code; compute precision/recall/F1 (tp/fp/fn against your oracle).
3. Compare against the dumb baseline the tool claims to beat (usually grep). Graph-vs-grep is a fair headline — but check the comparison isn't rigged: exact-name matching vs substring search inflates precision trivially.
4. Judge the tool's own evals for honesty: do they publish oracles, baselines, and raw tp/fp/fn? (Battle-tested 2026-08-22: code-graph-rag publishes oracle evals — 0.91 F1 graph retrieval vs 0.38 grep — that transparency was the deciding trust signal.)
5. Adopt only if it beats grep/language tooling on YOUR code by a margin that matters for the workflow. Otherwise the verdict comes free from the oracle, no live install needed.

#### 11a. For a generator: open the OUTPUT, do not read the docs about it

When the claim is about what a tool produces ("native shapes, not images", "no rasterization",
"real charts"), the proof is inside the produced file. Produce one yourself and open it:

1. Run the tool on a **minimal input you wrote** — smallest thing the contract accepts, one page,
   three elements. A tool that needs a full design spec first will say so, by name; follow each refusal
   (they are the pipeline), and note how many gates it took to reach an artifact.
2. Parse the output **without their tools** (`zipfile` + `ElementTree` for OOXML; grep the XML): count the
   thing the claim is about against its opposite — `p:sp` native shapes vs `p:pic` rasterized images,
   `ppt/media/*` emptiness, `a:prstGeom` presets (`roundRect` from `rx`, `ellipse` from `circle`).
3. **Verify the units arithmetic by hand.** One EMU-per-pixel constant check (`132 px × 9525 = 1,257,300`)
   either matches the file or the "conversion" is a re-render. Geometry that matches exactly is much
   stronger evidence than a screenshot.
4. **Cross-check their own report against yours** — and check the report names the source it measured
   (a `source_fingerprint.digest` present in BOTH the quality report and the post-export report is what
   stops a stale gate from being passed off as a fresh one).

#### 11b. Running a third-party test suite: attribute every failure before reporting it

A red suite is a claim about *the suite* first. Measured (2026-10-10, 55 test files / ~700 tests):
`--maxfail` gives "39 failed, 676 passed, 1185 subtests passed" — and the failures split by cause:

- `ModuleNotFoundError: No module named 'docx'` in a test, while `requirements.txt` routes `.docx`
  through another library → **a real gap in their declared install contract** (attributable to them).
- `TypeError: cannot unpack non-iterable SimpleNamespace` raised inside `urllib3/connection.py` → the
  dependency set vs the local interpreter, **not their code**.
- `AssertionError: Lists differ: /private/var/... != /var/...` → macOS `/private` symlink resolution.
- nine failures sharing one message from their own test helper (an empty selection list) → **unresolved:
  say so, attribute nothing.**

Recipe: `--continue-on-collection-errors` (one module calling `sys.exit(1)` at import aborts the whole
collection), `--tb=line` then `sort | uniq -c` to group failures by *message* rather than reading them one
by one, and `python -c "import …"` to prove a missing module is absent from the declared requirements.
Report the split, never the headline count — and never the exit code read through a pipe (`cmd | tail`
returns *tail's* status; on macOS `timeout` does not exist either, so a "successful" install step may never
have run).

## Pitfalls
- **`closed` is not `merged` — and a PR's own description is not the maintainer's claim.** An external PR can be closed unmerged while its body reads as a completed fix (measured: a closed PR asserted a `SECURITY.md` was added; the file had never existed in the entire history — verify with `git log --all -- '*SECURITY*'`, not `ls`). Check `merged_at`, not `state`.
- **Large external PRs split on request can still rot.** When a maintainer says "split this into N PRs", re-check EACH child's merge state weeks later: 1-of-10 merged is a real finding about external-contribution absorption, invisible if you only read the original thread.
- **README badge alt-text is a claim, and it may drop a qualifier.** A badge whose alt says "#1 Repository of the Day" can be wired to a language-filtered endpoint whose own `aria-label` reads "number 1 **Rust** repository of the day", while the all-languages best rank is #8. Fetch the badge SVG and read its `aria-label`; compare against the public ranking page.
- **Verify signed/notarized claims on the ARTIFACT, not the docs.** Download the release binary: `codesign -dvvv`, `spctl -a -t open -vv`, `xcrun stapler validate`, and compare the tarball `sha256` with the checksum hard-coded in the installer. Docs go stale in both directions (a README claimed "not yet signed" for a binary that was signed). For a macOS `.app`/`.dmg`, follow `references/macos-app-artifact-verification.md`.
- **"No network / no telemetry" is proved by LINKAGE and ENTITLEMENTS, not by grep on symbol names.** `otool -L` (only `/System/Library` and `/usr/lib` entries ⇒ no third-party SDK can call out) + the entitlement dump (an empty one means *no declared capability*, NOT sandboxed — say which you observed) + the URL strings inside the binary. `nm -u` is supporting only: `_CGSMainConnectionID` is CoreGraphics' window-server connection and matches a naive `connection|socket` grep in every AppKit app. When the claim is about the product rather than the binary, check the vendor's own site too — the app not connecting says nothing about the page.
- **A published size figure is usually stale by one release.** Measure the binary, the bundle (sum of file sizes) and the archive before disagreeing with it, then read the breakdown for the cause — a single `.icns` at 1.06 MB was 35% of a 3.03 MB bundle, an icon heavier than 1,900 lines of code.
- **An outbound URL is not telemetry, and it is not nothing.** A URL handed to `NSWorkspace.open` is disclosure by the browser, not an app connection — but read its query string: `?update=<version>&lang=<lang>` behind a "Check for Updates…" menu item tells the site the user's version and language, on one click, by choice. Name it at that exact size.
- **"Privacy-respecting" telemetry: read the payload struct, not the README list.** A doc enumerating exclusions (no code, no prompts, no paths) can still omit that user-entered FREE TEXT from an onboarding form is uploaded. Grep the event-construction functions for real field names; and check whether consent is opt-in or opt-out.
- **A tempting coincidence is not a finding.** A dated third-party thread matching your repo's spike magnitude AND timing may reference an entirely different project — read the source links before naming it.
- **Skills.sh ecosystem:** See `references/skills-ecosystem-audit.md` for the full methodology on auditing skills published on skills.sh. Key trap: short URLs like `/s/<name>` can return HTTP 200 for non-existent skills because Next.js renders a shell page. Always cross-reference the sitemap and verify GitHub source.
- **A claim about a METHOD must be read from its committed OUTPUT, not its prose — and a "missing enforcement" claim must enumerate the whole surface.** Two measured failures in one audit (2026-10-06): (1) `grep -rn 'frozen' src/` returned nothing, so the rule was reported as "policy, not gate" — but the rule lived in the agent-facing skill layer, and its **commit history** showed it had been refined across **nine adversarial review rounds** with a mechanical discriminator ("would this have failed on the parent too? no ⇒ it is a result"). The verdict flipped. (2) The single most informative artifact in the repo — an exported run's `evidence/run-manifest.json` (command + device + status + sha256 per file + explicit list of what was NOT bundled) and its `reports/*.md` research output — was never read before grading the methodology, yet it was the only real evidence of the method producing something. **Surface to enumerate: code + agent-facing docs/skills + the history of those docs.** **Separate three claims before calling a rule a strength:** is it *earned* (traced to a review/incident)? is it *constrained* (a mechanical criterion)? is it *enforced* (a gate that blocks)? One does not imply another.
- **High star count ≠ quality** (viral drops can hit 100K+ stars in days)
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
- **Confounding variable trap (self-auditing):** When auditing your OWN skills/repos before publishing, the #1 failure is attributing success to the wrong variable. Example: a governance skill claimed constitutional scaffolding improved EPIC completion — but zero profiles ever loaded it, zero cron jobs ran, and SOUL rewrites (2→581 lines) happened simultaneously. Always verify: did the thing we CLAIM fixed it actually get USED? Timeline match? Simultaneous changes that better explain the outcome?
- **Skills ecosystem repos are predominantly markdown:** Claude/Cursor/Codex marketplace repos can have 9,500+ entries that are just SKILL.md files. File-type composition is the #1 signal. Check for actual code, scripts, and references — not just markdown wrappers. Skills.sh short URLs like `/s/<name>` can return HTTP 200 for non-existent skills (Next.js renders a shell page) — always cross-reference sitemaps.
