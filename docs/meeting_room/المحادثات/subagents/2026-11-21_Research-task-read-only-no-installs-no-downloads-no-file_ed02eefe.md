# Research task, read-only (no installs, no downloads, no file

- المصدر: `subagents`
- معرف الجلسة: `ed02eefe-8921-4ae5-8979-c856ae49faeb`
- البداية: 2026-11-21T07:56:41.389Z — النهاية: 2026-11-21T08:00:57.717Z
- الرسائل: مستخدم 38 · مساعد 36 · أدوات 36
- تنظيف الخصوصية: أرقام التليفون وال api_id والـ hash والمفاتيح والإيميلات اتشالت بـ regex، وده مش مضمون ١٠٠٪.

## ملخص تلقائي (مش تلخيص AI)
- مبني على أول طلب وآخر رد وقايمة طلبات المستخدم. راجع المحادثة الكاملة للتفاصيل.
- **أول طلب:** Research task, read-only (no installs, no downloads, no file writes). Verify facts as of today (2026-11-21) from official sources. Never guess: mark "unverified" when you cannot confirm.

Context: XXX, a one-person defensive security hub for macOS, wants a threat radar, AI-security references, and maybe a multi-provider storage view later.

A) Threat feeds — for each: official URL of the machine-readable feed/API, format, needs a key?, rate limits, license/terms, update frequency: CISA KEV JSON,
- **طلبات المستخدم (أول 15):**
  1. Research task, read-only (no installs, no downloads, no file writes). Verify facts as of today (2026-11-21) from official sources. Never guess: mark "
  2. <system-reminder>
Your final report is delivered through SubagentHandback: when your work is complete, call SubagentHandback({message: <your full repo
- **آخر رد للمساعد:** —

---

## المحادثة الكاملة

### user · 2026-11-21T07:56:41.389Z

Research task, read-only (no installs, no downloads, no file writes). Verify facts as of today (2026-11-21) from official sources. Never guess: mark "unverified" when you cannot confirm.

Context: XXX, a one-person defensive security hub for macOS, wants a threat radar, AI-security references, and maybe a multi-provider storage view later.

A) Threat feeds — for each: official URL of the machine-readable feed/API, format, needs a key?, rate limits, license/terms, update frequency: CISA KEV JSON, NVD CVE API 2.0, FIRST EPSS API, CVE.org/CVE Program (cvelistV5), OSV.dev API, GitHub Advisory Database (API/repo), MITRE ATT&CK (STIX via attack-stix-data; latest version number), MITRE ATLAS (latest data release), Apple security releases page/feed, abuse.ch (MalwareBazaar/URLhaus/ThreatFox: do they now require an Auth-Key?), CERT-EG / Saudi NCA CERT feeds if any.
B) Standards — confirm exact current versions: NIST CSF 2.0, CIS Controls (8.1?), NIST SP 800-61 Rev 3, NIST IR 8374 Rev 1, OWASP ASVS (5.0.0?), OWASP Top 10 for LLM Applications (latest year), OWASP Agentic AI / Agentic Security Initiative top 10 (exists? name/version), NIST AI RMF 1.0 + Generative AI Profile (AI 600-1).
C) Claude Code / AI security "skills": Trail of Bits security skills for Claude Code (repo URL, license, what's inside), any official Cloudflare "security audit" skill (does it exist? exact repo), well-known "cybersecurity skills" collections for Claude Code (repo, stars, last commit). For each: owner, license, last commit, do install scripts run code, risk notes.
D) Free cloud storage — current free quota and whether there is a public API, for: Google Drive, MEGA, OneDrive, Dropbox, Box, Proton Drive, pCloud, Koofr, Filen, kDrive (Infomaniak), Icedrive, TeraBox, iCloud Drive. Note inactivity/deletion policies if stated.

Return 4 compact tables (A–D) in English, with source URLs. No prose beyond one line of caveats per table.

### user · 2026-11-21T07:56:42.078Z

<system-reminder>
Your final report is delivered through SubagentHandback: when your work is complete, call SubagentHandback({message: <your full report>}). The call ends your run, so make it your last step. Only a SubagentHandback call reaches your caller as your result; plain text you write at the end is not delivered. Do not also send the report with SendMessage: your caller would get it twice.
</system-reminder>

### assistant · 2026-11-21T07:56:45.724Z

**أداة:** `ToolSearch`

```json
{
 "query": "select:WebSearch,WebFetch",
 "max_results": 2
}
```

### user · 2026-11-21T07:56:46.032Z

**نتيجة أداة:**
```

```

### assistant · 2026-11-21T07:56:48.790Z

**أداة:** `WebFetch`

```json
{
 "url": "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
 "prompt": "Feed URLs (JSON/CSV), update frequency, terms/license, any API key requirement."
}
```

### assistant · 2026-11-21T07:56:49.568Z

**أداة:** `WebFetch`

```json
{
 "url": "https://nvd.nist.gov/developers/start-here",
 "prompt": "API 2.0 endpoint, API key requirement, rate limits with and without key, recommended polling, terms of use/license."
}
```

### assistant · 2026-11-21T07:56:50.128Z

**أداة:** `WebFetch`

```json
{
 "url": "https://www.first.org/epss/api",
 "prompt": "API endpoint, key needed, rate limits, bulk CSV download URL, update frequency, license/usage terms."
}
```

### assistant · 2026-11-21T07:56:50.770Z

**أداة:** `WebFetch`

```json
{
 "url": "https://google.github.io/osv.dev/api/",
 "prompt": "API endpoints, key needed, rate limits, bulk data (GCS all.zip) location, license, update frequency."
}
```

### assistant · 2026-11-21T07:56:51.555Z

**أداة:** `WebFetch`

```json
{
 "url": "https://github.com/CVEProject/cvelistV5",
 "prompt": "Update frequency (deltas), license/terms of use, repo structure, CVE record format version, latest release/delta info."
}
```

### assistant · 2026-11-21T07:56:52.269Z

**أداة:** `WebFetch`

```json
{
 "url": "https://github.com/mitre-attack/attack-stix-data",
 "prompt": "Latest ATT&CK version number, STIX version, file paths for enterprise-attack json, license, update cadence."
}
```

### assistant · 2026-11-21T07:56:52.901Z

**أداة:** `WebFetch`

```json
{
 "url": "https://github.com/mitre-atlas/atlas-data",
 "prompt": "Latest ATLAS data release version/date, file formats (ATLAS.yaml, STIX), license."
}
```

### assistant · 2026-11-21T07:56:53.390Z

**أداة:** `WebFetch`

```json
{
 "url": "https://support.apple.com/en-us/100100",
 "prompt": "Is this the Apple security releases page; is there an RSS/feed link; latest entries listed."
}
```

### user · 2026-11-21T07:56:59.648Z

**نتيجة أداة:**
```
The server returned HTTP 404 Not Found.

The response body was not retrieved. If this URL requires authentication, use an authenticated tool (e.g. `gh` for GitHub, or an MCP-provided fetch tool) instead of WebFetch.
```

### user · 2026-11-21T07:56:59.908Z

**نتيجة أداة:**
```
The web page content you provided only includes the title "NVD - Home" and a list of topics: API 2.0 endpoint, API key requirement, rate limits with and without a key, recommended polling, and terms of use/license. It doesn't contain the details for any of them, so I can't report the endpoint URL, whether a key is required, the rate limits, the polling recommendations, or the license terms.

If you paste the full text of the page, I can summarize those sections.
```

### user · 2026-11-21T07:57:00.959Z

**نتيجة أداة:**
```
**Endpoints** (per the API overview):
- `POST /v1/query`: query vulnerabilities by project and commit hash or version
- `POST /v1/querybatch`: batched vulnerability queries
- `GET /v1/vulns/{id}`: returns a vulnerability by OSV ID
- `GET /v1experimental/importfindings`: experimental
- `POST /v1experimental/determineversion`: experimental
- `POST /v1experimental/ubuntu/binary-to-source`: experimental

**Rate limits:** "Currently there are no limits on the API." Response size is capped at 32MiB over HTTP/1.1, with no limit over HTTP/2.

**API key:** Not mentioned.

**Bulk data (GCS all.zip location):** Not mentioned. The page links to a "Data sources" section, but its content isn't included here.

**License:** Not mentioned.

**Update frequency:** Not mentioned.
```

### user · 2026-11-21T07:57:01.018Z

**نتيجة أداة:**
```
**Yes**, this is Apple's security releases page. The title and heading read "Apple security releases - Apple Support," and the page lists software updates with their CVE details.

**RSS/feed:** The page content shows no RSS or feed link.

**Latest entries** (as shown on the page, dated up to November 18, 2026):

- **HomeView Software Version 27.2.1** (18 Nov 2026): no published CVE entries
- **tvOS 27.2.1** (13 Nov 2026): Apple TV 4K 2nd generation and later
- **HomeView Software Version 27.2** (12 Nov 2026): Apple HomeView
- **iOS 27.2.1 and iPadOS 27.2.1** (09 Nov 2026)
- **iOS 26.7.3 and iPadOS 26.7.3** (09 Nov 2026)
- **macOS Golden Gate 27.2.1, macOS Tahoe 26.7.3, and macOS Sequoia 15.8.3** (09 Nov 2026)
- **watchOS 27.2.1, watchOS 26.6.1, and visionOS 27.2.1** (09 Nov 2026)

The page's layout makes the entry order a little unclear, so the dates are the most reliable guide.
```

### user · 2026-11-21T07:57:02.482Z

**نتيجة أداة:**
```
- **Latest ATT&CK version number:** The page doesn't state it. The only version mentioned is v9.0, given as an example.
- **STIX version:** STIX 2.1. The page says the data is in "STIX 2.1 JSON collections."
- **Enterprise ATT&CK JSON file paths:** `enterprise-attack/enterprise-attack.json` is the most recent release, without a version marking. Versioned releases sit in the same folder, such as `enterprise-attack/enterprise-attack-9.0.json`.
- **License:** The repository includes a LICENSE.txt file, but the page doesn't show its terms. The page says "Copyright 2020-2025 The MITRE Corporation. Approved for public release." It also links to the ATT&CK Terms of Use.
- **Update cadence:** The page doesn't specify one. It mentions a CHANGELOG.md and 106 commits, but no release schedule.
```

### user · 2026-11-21T07:57:02.509Z

**نتيجة أداة:**
```
**Update frequency:** The repository is updated "about every 7 minutes" using the official CVE Services API. Baseline zip files are issued daily at midnight UTC, and hourly delta zips are also provided. Deltas contain only changes since the baseline.

**License/terms of use:** The page does not name a specific open-source license. It says you may search, download, and use the content "per the CVE Program Terms of Use," which is linked from the page. The repository also doesn't accept pull requests, and it asks users to report issues through the Issue Tracker or the CVE Request Web Forms.

**Repo structure:**
- Top-level folders: `.github/workflows` and `cves`
- Top-level files: `.gitattributes`, `.gitignore`, and `README.md`
- Each CVE Record can contain a CNA container, a CVE Program Container (added after 7/31/2024 when the Program adds enrichment), and optional ADP containers, such as the CISA-ADP container.

**CVE Record format version:** The page notes a 2025-10-29 update to CVE Record Format version 5.2.0, which adds Package URL (PURL) support. A 2024 note says records may be formatted as 5.0 or 5.1, indicated by the "dataversion" field, and that the REST services moved to schema 5.1.1 in December 2024.

**Latest release/delta info:** The page does not list a specific latest release or delta. It describes the naming conventions for releases, such as `2024-04-04_all_CVEs_at_midnight.zip` for baselines and `2024-04-04_delta_CVEs_at_0100Z.zip` for deltas. The most recent note says a Date Normalization process runs from 2/16/26 to 2/28/26, during which `deltaLog.json` keeps only 15 days of history instead of the usual 30.
```

### user · 2026-11-21T07:57:02.858Z

**نتيجة أداة:**
```
**Latest release:** The page doesn't state a release date. The most recent content version it names is **2026.05** (`collection.version`), which appears in the examples. Format version is **6.1.0**. `dist/ATLAS-latest.yaml` always points to the latest content in the latest format, and `dist/manifest.yaml` maps each release to its format-version and file path.

**File formats:**
- **YAML:** The authoritative source. `dist/ATLAS-latest.yaml`, `dist/v6/ATLAS-{version}.yaml` (v6 history), and `dist/legacy/ATLAS-{version}.yaml` (original formats). `dist/ATLAS.yaml` is deprecated.
- **STIX 2.1:** Attack Flow bundles per case study, and ATLAS STIX JSON (optionally with ATT&CK Enterprise).
- **Excel (.xlsx):** Workbooks including `atlas-entities.xlsx` and case-study sheets.
- **ATT&CK Navigator layers:** Layer format 4.5, for the custom `atlas-atlas` domain.

**License:** The page links to a LICENSE file but doesn't summarize its terms. It only states: "©2021-2026 The MITRE Corporation. ALL RIGHTS RESERVED. Approved for Public Release; Distribution Unlimited." Check the LICENSE file for the terms that apply.
```

### user · 2026-11-21T07:57:03.973Z

**نتيجة أداة:**
```
**Feed URLs** (relative to https://www.cisa.gov):
- **CSV:** /sites/default/files/csv/known_exploited_vulnerabilities.csv
- **JSON:** /sites/default/files/feeds/known_exploited_vulnerabilities.json
- **JSON Schema:** /sites/default/files/feeds/known_exploited_vulnerabilities_schema.json (noted as updated 09-02-2026)
- **License:** /sites/default/files/licenses/kev/license.txt

**Update frequency:** The page doesn't state a schedule. Entries dated as recently as 2026-11-20 suggest the catalog is updated regularly. For notifications, the page offers a GovDelivery email subscription (topic USDHSCISA_136).

**Terms/license:** The page links to the license file, but its text isn't in the content provided, so I can't summarize the terms. Review the license file directly.

**API key:** The page doesn't mention any API key or authentication requirement for the feeds.
```

### assistant · 2026-11-21T07:57:08.212Z

**أداة:** `Bash`

```json
{
 "command": "cd /tmp; for r in mitre-attack/attack-stix-data mitre-atlas/atlas-data CVEProject/cvelistV5 trailofbits/skills github/advisory-database cloudflare/skills; do echo \"== $r\"; gh api repos/$r --jq '[.full_name,.license.spdx_id,.stargazers_count,.pushed_at,.archived]|@tsv' 2>&1 | head -3; done; echo; gh api repos/mitre-attack/attack-stix-data/releases/latest --jq '.tag_name+\" \"+.published_at' 2>&1; gh api repos/mitre-attack/attack-stix-data/contents/enterprise-attack --jq '.[].name' 2>&1 | sort -V | tail -4; gh api repos/mitre-atlas/atlas-data/releases/latest --jq '.tag_name+\" \"+.published_at' 2>&1; gh api repos/mitre-atlas/atlas-data/contents/dist --jq '.[].name' 2>&1 | head -20",
 "description": "Query GitHub repo metadata read-only"
}
```

### assistant · 2026-11-21T07:57:08.930Z

**أداة:** `WebFetch`

```json
{
 "url": "https://nvd.nist.gov/developers/vulnerabilities",
 "prompt": "Endpoint URL, API key, rate limits (requests per rolling 30 s) with/without key."
}
```

### assistant · 2026-11-21T07:57:09.628Z

**أداة:** `WebFetch`

```json
{
 "url": "https://www.first.org/epss/data_stats",
 "prompt": "How to download EPSS data, API endpoint api.first.org/data/v1/epss, update cadence, usage terms."
}
```

### assistant · 2026-11-21T07:57:10.374Z

**أداة:** `WebFetch`

```json
{
 "url": "https://abuse.ch/blog/community-first/",
 "prompt": "Does abuse.ch require Auth-Key for MalwareBazaar, URLhaus, ThreatFox APIs; since when; how to get key; license."
}
```

### user · 2026-11-21T07:57:21.741Z

**نتيجة أداة:**
```
== mitre-attack/attack-stix-data
mitre-attack/attack-stix-data	NOASSERTION	726	2026-11-05T16:45:25Z	false
== mitre-atlas/atlas-data
mitre-atlas/atlas-data	NOASSERTION	208	2026-10-28T22:54:41Z	false
== CVEProject/cvelistV5
CVEProject/cvelistV5		3301	2026-11-21T07:49:46Z	false
== trailofbits/skills
trailofbits/skills	CC-BY-SA-4.0	8321	2026-11-21T07:06:22Z	false
== github/advisory-database
github/advisory-database	CC-BY-4.0	2564	2026-11-21T06:36:47Z	false
== cloudflare/skills
cloudflare/skills	Apache-2.0	3418	2026-11-17T15:55:50Z	false

v20.1 2026-11-05T16:35:43Z
enterprise-attack-19.1.json
enterprise-attack-19.2.json
enterprise-attack-20.0.json
enterprise-attack-20.1.json
v2026.10 2026-10-28T22:55:06Z
ATLAS-latest.yaml
ATLAS.yaml
legacy
manifest.yaml
schemas
v6
```

### user · 2026-11-21T07:57:22.794Z

**نتيجة أداة:**
```
The server returned HTTP 404 Not Found.

The response body was not retrieved. If this URL requires authentication, use an authenticated tool (e.g. `gh` for GitHub, or an MCP-provided fetch tool) instead of WebFetch.
```

### user · 2026-11-21T07:57:24.457Z

**نتيجة أداة:**
```
The web page content you provided contains only the title "NVD - Home." It doesn't include an endpoint URL, API key information, or rate limits with or without a key, so I can't answer from it.

If you share the full page or the relevant API documentation, I can summarize those details.
```

### user · 2026-11-21T07:57:29.567Z

**نتيجة أداة:**
```
**Yes, for API access.** The post says that, beyond uploading contributions, users "should now authenticate to download API-related data - this is applicable to all users, across all platforms." It doesn't name ThreatFox, MalwareBazaar, or URLhaus individually.

**Timeline (post dated 18 November 2024):**
- **Now:** API-related data downloads require authentication. Unauthenticated users face API query rate limits and lose access to new data and functionality.
- **February 2025:** Authentication is required to use hunting functionality on MalwareBazaar and YARAify.
- **June 30, 2025:** Authentication becomes mandatory.

**How to get an Auth-Key:**
1. Sign up at https://auth.abuse.ch/ using an X, LinkedIn, Google, or GitHub account.
2. Connect at least one additional authentication provider.
3. Click "Save profile," then create an Auth-Key in the "Optional" section.
4. Send the key in an Auth-Key HTTP header with your API requests.

If you already have a profile, you only need steps 3 and 4.

**License:** The post doesn't state a license for the data or APIs. It only links to Terms and Conditions, Terms of Use, and a Privacy Policy, which aren't included here, so check those documents for usage terms.
```

### assistant · 2026-11-21T07:57:34.998Z

**أداة:** `Bash`

```json
{
 "command": "cd /tmp; curl -sL -m 20 https://nvd.nist.gov/developers/start-here | sed 's/<[^>]*>/ /g' | tr -s ' \\n' | grep -iE \"rate|30 second|api key|50 requests|5 requests|six seconds|6 seconds\" | head -15; echo ===EPSS; curl -sL -m 20 \"https://api.first.org/data/v1/epss?cve=CVE-2024-3400\" | head -c 400; echo; curl -sI -m 20 https://epss.empiricalsecurity.com/epss_scores-current.csv.gz | head -5; echo ===CISA; curl -sI -m 20 https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json | head -3; echo ===OSV; curl -sI -m 20 https://osv-vulnerabilities.storage.googleapis.com/all.zip | head -3; echo ==GHSA; gh api repos/github/advisory-database/commits?per_page=1 --jq '.[0].commit.committer.date'; echo ==TOB; gh api repos/trailofbits/skills/contents --jq '.[].name' | tr '\\n' ' '; gh api repos/trailofbits/skills/contents/plugins --jq '.[].name' | tr '\\n' ' '",
 "description": "Probe feed endpoints and ToB repo layout"
}
```

### assistant · 2026-11-21T07:57:37.049Z

**أداة:** `Bash`

```json
{
 "command": "cd /tmp; gh api repos/cloudflare/skills/contents --jq '.[].name' | tr '\\n' ' '; echo; gh api repos/cloudflare/skills/contents/skills --jq '.[].name' 2>&1| tr '\\n' ' '; echo; gh api \"search/repositories?q=cybersecurity+skills+claude+code&sort=stars&per_page=8\" --jq '.items[]|[.full_name,.stargazers_count,.license.spdx_id,.pushed_at,.description]|@tsv'; echo; gh api \"search/repositories?q=security+skills+claude+in:name,description+topic:claude-skills&sort=stars&per_page=6\" --jq '.items[]|[.full_name,.stargazers_count,.license.spdx_id,.pushed_at]|@tsv'; echo; gh api \"search/repositories?q=Anthropic-Cybersecurity-Skills&per_page=3\" --jq '.items[]|[.full_name,.stargazers_count,.license.spdx_id,.pushed_at]|@tsv'",
 "description": "Inspect Cloudflare skills and search security skills repos"
}
```

### user · 2026-11-21T07:57:38.081Z

**نتيجة أداة:**
```
Exit code 1
(eval):1: ==EPSS not found
```

### user · 2026-11-21T07:57:43.794Z

<details><summary>نتيجة أداة (3646 حرف)</summary>

```
.agents .antigravity-plugin .claude-plugin .codex-plugin .cursor-plugin .github .gitignore .mcp.json CODEOWNERS CONTRIBUTING.md LICENSE README.md icon.png logo.svg mcp.json mcp_config.json plugin.json rules skills 
agents-sdk basin cf-cli cloudflare-app-bootstrap cloudflare-email-service cloudflare-one-migrations cloudflare-one cloudflare durable-objects frameworks-on-cloudflare gateway-workers k2 nextjs-on-cloudflare sandbox-migrate-to-next sandbox-next sandbox-stable turnstile-spin web-perf workers-best-practices workers-development workers-profiling wrangler 
mukul975/Anthropic-Cybersecurity-Skills	36478	Apache-2.0	2026-08-31T04:32:44Z	817 structured cybersecurity skills for AI agents · Mapped to 6 frameworks: MITRE ATT&CK, NIST CSF 2.0, MITRE ATLAS, D3FEND, NIST AI RMF & MITRE F3 (Fight Fraud) · agentskills.io standard · Works with Claude Code, GitHub Copilot, Codex CLI, Cursor, Gemini CLI & 20+ platforms · 29 security domains · Apache 2.0
samugit83/redamon	3459	MIT	2026-11-19T19:03:15Z	Open-source, self-hosted AI penetration testing framework: maps your attack surface into a graph, autonomously exploits it from a Kali sandbox with human approval gates, and opens PRs that fix what it finds. MCP both ways: plug in any MCP server as a tool, or drive RedAmon from Claude Code or your own agent.
Masriyan/Claude-Code-CyberSecurity-Skill	591	NOASSERTION	2026-10-20T02:54:51Z	22 production-quality Claude Code Skills for cybersecurity professionals , covering offensive security, defensive operations, reverse engineering, threat hunting, threat intelligence, purple team / adversary emulation, CSOC automation, AI/LLM security, mobile, OT/ICS, GRC, software supply chain security, and more. 
briiirussell/cybersecurity-skills	526	MIT	2026-11-19T01:15:41Z	Cybersecurity skills for AI coding agents (Claude Code, Cursor, Codex)
x-glacier/kali-pentest	190	Apache-2.0	2026-06-25T08:40:35Z	Kali Linux penetration testing skill for AI agents (Claude Code, OpenClaw, Hermes Agent). 200+ CLI tools, 15 scenario playbooks. Autonomously plans attack paths, selects tools, and integrates results across phases to adapt the penetration strategy — with human approval gates for high-risk actions.
mukul975/Threatswarm	100	MIT	2026-04-29T15:49:33Z	27 scope-enforced AI agents that run the full pentest kill-chain (recon → exploit → post-ex → DFIR → report) as a one-command Claude Code plugin. Backed by 754 MITRE-mapped skills.
26zl/cybersec-toolkit	100	MIT	2026-11-19T22:46:55Z	One command installs 670+ security tools on Debian/Ubuntu/Kali, Fedora, Arch, openSUSE and Termux. Its authorization-gated MCP server runs them in a disposable Kata Containers VM sandbox for Claude Code, Codex, Gemini CLI, OpenCode and other MCP clients. 872 agent skills for CTF, pentesting, bug bounty, DFIR and red/blue teams.
kaivyy/perseus	71	MIT	2026-10-31T12:03:31Z	AI-powered security assessment SKILLS for your codebase. Multi-language (JS, Go, Python, Rust, Java, PHP, Ruby, C#). Works with Claude Code, Codex, OpenCode, etc.

SnailSploit/Claude-Red	11326	MIT	2026-11-17T14:13:12Z
zhuyansen/awesome-claude-video-skills	2456	NOASSERTION	2026-11-20T16:37:28Z
dagoSte/squadra	984	MIT	2026-11-19T20:04:52Z
Masriyan/Claude-Code-CyberSecurity-Skill	591	NOASSERTION	2026-10-20T02:54:51Z
aiskillstore/marketplace	489		2026-11-20T16:43:17Z
agamm/claude-code-owasp	457	MIT	2026-11-03T19:29:21Z

mukul975/Anthropic-Cybersecurity-Skills	36478	Apache-2.0	2026-08-31T04:32:44Z
costrict-plugins-repo/mukul975-anthropic-cybersecurity-skills-cybersecurity-skills	77	Apache-2.0	2026-09-01T01:21:41Z
mukul975/BHUSA-Anthropic-CyberSecurity-Skills	10		2026-08-23T14:15:13Z
```

</details>

### assistant · 2026-11-21T07:57:48.839Z

**أداة:** `Bash`

```json
{
 "command": "cd /tmp; curl -sL -m 20 https://nvd.nist.gov/developers/start-here | sed 's/<[^>]*>/ /g' | tr -s ' \\n' | grep -iE \"30 second|50 requests|5 requests|six seconds|6 seconds\" | head -6\necho \"--EPSS\"; curl -sL -m 20 \"https://api.first.org/data/v1/epss?cve=CVE-2024-3400\" | head -c 300; echo; curl -sI -m 20 https://epss.empiricalsecurity.com/epss_scores-current.csv.gz | head -3\necho \"--CISA\"; curl -sI -m 20 https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json | head -3\necho \"--OSV\"; curl -sI -m 20 https://osv-vulnerabilities.storage.googleapis.com/all.zip | head -3\necho \"--GHSA\"; gh api \"repos/github/advisory-database/commits?per_page=1\" --jq '.[0].commit.committer.date'\necho \"--TOB\"; gh api repos/trailofbits/skills/contents --jq '.[].name' | tr '\\n' ' '; echo; gh api repos/trailofbits/skills/contents/plugins --jq '.[].name' | tr '\\n' ' '\necho; echo \"--TOB install scripts\"; gh api \"search/code?q=repo:trailofbits/skills+filename:install\" --jq '.items[].path' 2>&1 | head",
 "description": "Probe feed endpoints and ToB layout"
}
```

### assistant · 2026-11-21T07:57:50.329Z

**أداة:** `Bash`

```json
{
 "command": "cd /tmp; gh api \"search/repositories?q=cloudflare+security+audit+skill&per_page=6\" --jq '.items[]|[.full_name,.stargazers_count,.pushed_at]|@tsv'; echo; gh api repos/mukul975/Anthropic-Cybersecurity-Skills/contents --jq '.[].name' | tr '\\n' ' '; echo; gh api repos/Masriyan/Claude-Code-CyberSecurity-Skill/contents --jq '.[].name' | tr '\\n' ' '; echo; gh api repos/mukul975/Anthropic-Cybersecurity-Skills/commits?per_page=1 --jq '.[0].commit.committer.date'",
 "description": "Search Cloudflare audit skill and inspect collections"
}
```

### user · 2026-11-21T07:57:58.513Z

**نتيجة أداة:**
```
--EPSS
{"status":"OK","status-code":200,"version":"1.0","access":"public","total":1,"offset":0,"limit":100,"data":[{"cve":"CVE-2024-3400","epss":"0.999990000","percentile":"1.000000000","date":"2026-11-20"}]}

HTTP/2 302 
server: CloudFront
date: Sat, 21 Nov 2026 07:57:53 GMT
--CISA
HTTP/2 200 
content-type: application/json
x-content-type-options: nosniff
--OSV
HTTP/2 200 
content-type: application/zip
x-guploader-uploadid: AFy3sg1XzYn57bMhYJHMt9OdhyassJlRk3rGA1jptHwQt9mkCA6R050dcOendPI87NMU5JyG
--GHSA
2026-11-21T06:36:44Z
--TOB
.claude-plugin .github .gitignore .pre-commit-config.yaml AGENTS.md CLAUDE.md CODEOWNERS LICENSE Makefile README.md plugins ruff.toml 
agentic-actions-auditor audit-context-building building-secure-contracts burpsuite-project-parser c-review chrome-mcp-troubleshooting code-improver constant-time-analysis culture-index cvss-scoring devcontainer-setup differential-review dimensional-analysis dwarf-expert entry-point-analyzer firebase-apk-scanner fp-check gh-cli git-cleanup github-triage goal-prompt insecure-defaults let-fate-decide modern-cpp modern-python mutation-testing open-sourcing patching-bugs post-patch-validation property-based-testing regression-hunt review-walkthrough rust-review second-opinion semgrep-rule-creator semgrep-rule-variant-creator sharp-edges spec-to-code-compliance static-analysis supply-chain-risk-auditor testing-handbook-skills trailmark variant-analysis vulnerability-triage-brocards writing-lean-proofs yara-authoring zeroize-audit 
--TOB install scripts
plugins/code-improver/evals/reviewer-unavailable/graders/says-install-plugin-dev.md
plugins/devcontainer-setup/skills/devcontainer-setup/resources/install.sh
plugins/devcontainer-setup/skills/devcontainer-setup/resources/post_install.py
```

### user · 2026-11-21T07:58:01.767Z

**نتيجة أداة:**
```
Exit code 1
nightmaregaming6969-art/cloudflare-security-audit-skill	3	2026-09-17T12:54:59Z
preventor-sec/security-audit-skill	2	2026-10-22T13:45:06Z
47thtechcorner/RayCodes_security-audit-skill	2	2026-09-22T20:01:36Z
jnMetaCode/security-audit-skill-zh	2	2026-10-05T13:03:22Z
kilofafeure/cloudflare-security-audit-skill-	1	2026-11-15T06:52:58Z
iamrudhresh/cloudflare-security-audit-skill	0	2026-11-05T08:27:49Z

.claude-plugin .github .gitignore AGENTS.md ATTACK_COVERAGE.md CITATION.cff CODE_OF_CONDUCT.md CONTRIBUTING.md LICENSE README.fr.md README.md SCOPE.md SECURITY.md SUPPORT.md assets docs index.json mappings skills tools 
.claude-plugin .github .gitignore CHANGELOG.md CLAUDE.md CODE_OF_CONDUCT.md CONTRIBUTING.md INSTALL.md LICENSE Makefile NOTICE README.md SECURITY.md USAGE.md assets cyberskill docs pyproject.toml requirements-dev.txt schemas skills tests tools 
(eval):1: no matches found: repos/mukul975/Anthropic-Cybersecurity-Skills/commits?per_page=1
```

### assistant · 2026-11-21T07:58:06.477Z

**أداة:** `Bash`

```json
{
 "command": "cd /tmp; for u in https://nvd.nist.gov/developers/start-here https://nvd.nist.gov/general/news; do curl -sL -m 20 $u | sed 's/<[^>]*>/ /g' | tr -s ' \\n' | grep -iE \"rolling|requests|rate\" | head -4; done\ngh api \"repos/mukul975/Anthropic-Cybersecurity-Skills/commits?per_page=1\" --jq '.[0].commit.committer.date'\ngh api repos/mukul975/Anthropic-Cybersecurity-Skills/contents/tools --jq '.[].name' | tr '\\n' ' '\ngh api repos/trailofbits/skills/contents/LICENSE --jq .name; gh api repos/cloudflare/skills --jq .owner.login",
 "description": "NVD rate limit text; skills commit dates"
}
```

### assistant · 2026-11-21T07:58:07.068Z

**أداة:** `WebSearch`

```json
{
 "query": "NVD API rate limit 50 requests rolling 30 second window with API key public rate limit 5 requests",
 "mode": "standard"
}
```

### assistant · 2026-11-21T07:58:07.637Z

**أداة:** `WebSearch`

```json
{
 "query": "OWASP Top 10 for LLM Applications 2026 OWASP Top 10 for Agentic Applications 2026 release",
 "mode": "standard"
}
```

### assistant · 2026-11-21T07:58:08.127Z

**أداة:** `WebSearch`

```json
{
 "query": "OWASP ASVS 5.0.0 released latest version",
 "mode": "standard"
}
```

### assistant · 2026-11-21T07:58:08.636Z

**أداة:** `WebSearch`

```json
{
 "query": "CIS Controls latest version v8.1 v9 2026 release",
 "mode": "standard"
}
```

### assistant · 2026-11-21T07:58:09.086Z

**أداة:** `WebSearch`

```json
{
 "query": "NIST SP 800-61 Rev 3 final; NIST IR 8374 Rev 1 ransomware profile status",
 "mode": "standard"
}
```

### user · 2026-11-21T07:58:14.657Z

**نتيجة أداة:**
```
2026-08-31T04:32:42Z
README.md agentskills-skill.schema.json collision-allowlist.json detect-collisions.py generate-index.py lint-baseline.json lint-descriptions.py skill_frontmatter.py update-contributors.py validate-agentskills.py validate-skill.py LICENSE
cloudflare
```

### user · 2026-11-21T07:58:18.355Z

<details><summary>نتيجة أداة (2585 حرف)</summary>

```
Web search results for query: "OWASP ASVS 5.0.0 released latest version"

Links: [{"title":"github.com","url":"https://github.com/OWASP/ASVS"},{"title":"OWASP Application Security Verification Standard (ASVS)","url":"https://owasp.org/ASVS/"},{"title":"raw.githubusercontent.com","url":"https://raw.githubusercontent.com/OWASP/ASVS/master/README.md"},{"title":"OWASP Application Security Verification Standard (ASVS)","url":"https://www.owasp.org/index.php/ASVS_V1_Architecture"},{"title":"OWASP Application Security Verification Standard (ASVS)","url":"https://www.owasp.org/index.php/ASVS_V2_Authentication"},{"title":"OWASP Application Security Verification Standard (ASVS)","url":"https://www.owasp.org/index.php/ASVS"},{"title":"OWASP Application Security Verification Standard (ASVS)","url":"https://owasp.org/projects/asvs?tab=supporters"},{"title":"OWASP Application Security Verification Standard (ASVS)","url":"https://owasp.org/projects/asvs?tab=asvs-users"},{"title":"OWASP Application Security Verification Standard (ASVS)","url":"https://owasp.org/www-project-ASVS/"},{"title":"OWASP Application Security Verification Standard (ASVS)","url":"https://www.owasp.org/index.php/OWASP_Application_Security_Verification_Standard"},{"title":"OWASP Application Security Verification Standard (ASVS)","url":"https://owasp.org/projects/asvs"},{"title":"OWASP Application Security Verification Standard (ASVS)","url":"https://owasp.org/www-project-application-security-verification-standard/"},{"title":"owasp release version 5 0 of the application security verification standard asvs","url":"https://assuranceinaction.intertek.com/post/102kghm/owasp-release-version-5-0-of-the-application-security-verification-standard-asvs"},{"title":"ASVS 5.0 Update","url":"https://groups.google.com/a/owasp.org/g/leaders/c/Cj4Y6W1aZHg"}]

The latest stable release is ASVS 5.0.0, dated May 2025. OWASP's timeline lists 30 May 2025 as the date ASVS 5.0.0 was released live at Global AppSec EU Barcelona 2025. The project's GitHub README describes 5.0.0 as the latest stable version, and the OWASP project page shows it as the latest version, labeled "Bleeding Edge."

The next planned release is a patch, not a new major version. The next release target will be a patch release, version 5.0.1. The master branch on GitHub is a different matter: it will always be the "bleeding edge version" which might have in-progress changes or other edits open. For stable references, use the v5.0.0 tag.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### user · 2026-11-21T07:58:18.699Z

<details><summary>نتيجة أداة (3589 حرف)</summary>

```
Web search results for query: "CIS Controls latest version v8.1 v9 2026 release"

Links: [{"title":"The Ongoing Evolution of the CIS Critical Security Controls","url":"https://www.cisecurity.org/insights/blog/ongoing-evolution-cis-critical-security-controls"},{"title":"The ongoing evolution of the CIS Critical Security Controls","url":"https://www.helpnetsecurity.com/?p=320246"},{"title":"The ongoing evolution of the CIS Critical Security Controls","url":"https://www.helpnetsecurity.com/2025/01/09/cis-security-controls-v8-1/"},{"title":"Center for Internet Security (CIS) Releases CIS Controls v8.1 with New Governance Recommendations","url":"https://www.cisecurity.org/about-us/media/press-release/center-for-internet-security-releases-cis-controls-v8-1-with-new-governance-recommendations"},{"title":"Center for Internet Security (CIS) Releases CIS Critical Security Controls v8 to Reflect Evolving Technology, Threats","url":"https://www.cisecurity.org/press-release/center-for-internet-security-cis-releases-cis-controls-v8-to-reflect-evolving-technology-threats/"},{"title":"Center for Internet Security (CIS) Releases CIS Critical Security Controls v8 to Reflect Evolving Technology, Threats","url":"https://www.cisecurity.org/about-us/media/press-release/center-for-internet-security-cis-releases-cis-controls-v8-to-reflect-evolving-technology-threats"},{"title":"The 18 CIS Critical Security Controls","url":"https://cisecurity.org/controls/cis-controls-list/"},{"title":"Group Purchasing","url":"https://www.sans.org/critical-security-controls/"},{"title":"Group Purchasing","url":"https://www.sans.org/critical-controls"},{"title":"18 is the new 20 cis controls v8 is here","url":"https://www.cisecurity.org/blog/18-is-the-new-20-cis-controls-v8-is-here/"},{"title":"CIS Critical Security Controls Version 8.1","url":"https://www.cisecurity.org/controls/v8-1"},{"title":"CIS Benchmarks November 2026 Update","url":"https://www.cisecurity.org/insights/blog/cis-benchmarks-november-2026-update"},{"title":"tackling new cis controls","url":"https://www.tripwire.com/state-of-security/tackling-new-cis-controls"},{"title":"CIS Critical Security Controls v8.1","url":"https://www.cisecurity.org/insights/white-papers/cis-critical-security-controls-v8-1"},{"title":"Arctic Wolf Blog Post","url":"https://arcticwolf.com/?p=49848"},{"title":"Episode 91: What You Need to Know about CIS Controls v8.1","url":"https://www.cisecurity.org/insights/podcast/episode-91-what-you-need-to-know-about-cis-controls-v81"}]

The latest published version I found is **CIS Controls v8.1**, released in June 2024. I found no evidence of a released v9 as of November 2026.

- **v8.1 release:** CIS announced it on June 25, 2024 as an iterative update to CIS Controls v8 and minimizes disruption to Controls users. Its main additions were a "Governance" security function and alignment with NIST CSF 2.0 (the addition of the "Governance" security function).
- **Current status:** CIS's own v8.1 page still points to v8.1 as the download, and it lists v8.0 and v7.1 as older versions.
- **v9 status:** CIS says it is already working on ideas for Version 9 of the CIS Controls. A podcast episode also gave a sneak peek into the development of version 9.0. These are development signals, not a release.

The search results were mostly older articles and pages, so a v9 release announced after them would not show up here. Check cisecurity.org/controls for the current version before relying on this.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### user · 2026-11-21T07:58:19.541Z

<details><summary>نتيجة أداة (4270 حرف)</summary>

```
Web search results for query: "OWASP Top 10 for LLM Applications 2026 OWASP Top 10 for Agentic Applications 2026 release"

Links: [{"title":"🚀 Announcing the OWASP Top 10 (Risks and Mitigations) for Agentic AI Applications","url":"https://se.linkedin.com/in/khalid-c-553b5713"},{"title":"🚀 Announcing the OWASP Top 10 (Risks and Mitigations) for Agentic AI Applications","url":"https://ca.linkedin.com/in/ayhantek"},{"title":"OWASP Top 10 for Agentic Applications 2026 Is Here – Why It Matters and How to Prepare","url":"https://paloaltonetworks.com/blog/cloud-security/owasp-agentic-ai-security/"},{"title":"🚀 Announcing the OWASP Top 10 (Risks and Mitigations) for Agentic AI Applications","url":"https://mx.linkedin.com/in/sejowalker"},{"title":"🚀 Announcing the OWASP Top 10 (Risks and Mitigations) for Agentic AI Applications","url":"https://my.linkedin.com/in/rahul-lohar"},{"title":"OWASP Top 10 for Agentic Applications 2026 Is Here – Why It Matters and How to Prepare","url":"https://www.paloaltonetworks.com/blog/?p=349925"},{"title":"owasp top 10 for agentic application","url":"https://genai.owasp.org/resource/owasp-top-10-for-agentic-application"},{"title":"owasp top 10 for agentic applications","url":"https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications/"},{"title":"OWASP Top 10 for Agentic Applications – The Benchmark for Agentic Security in the Age of Autonomous AI","url":"https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/"},{"title":"owasp top 10 for agentic applications for 2026","url":"https://genai.owasp.org/resource/2025-12-09/owasp-top-10-for-agentic-applications-for-2026"},{"title":"OWASP Top 10 for Agentic Applications – The Benchmark for Agentic Security in the Age of Autonomous AI","url":"https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agent"},{"title":"owasp top 10 for agentic applications","url":"https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications/"},{"title":"OWASP Drops First AI Agent Risk List","url":"https://www.techrepublic.com/de/article/news-owasp-ai-agent-risk-list/"},{"title":"owasp genai security project unveils 2026 top 10 for llm applications new agent control standard and sponsors as community tops 30000 members","url":"https://genai.owasp.org/announcement/owasp-genai-security-project-unveils-2026-top-10-for-llm-applications-new-agent-control-standard-and-sponsors-as-community-tops-30000-members/"},{"title":"owasp genai security project unveils 2026 top 10 for llm applications new agent control standard and sponsors as community tops 30000 members","url":"https://genai.owasp.org/2026/09/01/owasp-genai-security-project-unveils-2026-top-10-for-llm-applications-new-agent-control-standard-and-sponsors-as-community-tops-30000-members/"},{"title":"OWASP Drops First AI Agent Risk List - TechRepublic","url":"https://www.techrepublic.com/article/news-owasp-ai-agent-risk-list/"}]

The OWASP Top 10 for Agentic Applications appears to have been released first, in December 2025, and the 2026 Top 10 for LLM Applications followed in 2026.

- **Agentic Top 10:** OWASP's GenAI Security Project published it on December 9, 2025, at the London Agentic Security Summit. Hundreds of experts contributed to it, and it is a globally peer-reviewed framework covering risks for autonomous AI systems. Palo Alto Networks dated its own coverage December 10, 2025.
- **LLM Top 10 2026:** The project's press release, dated in the URL as September 1, 2026, announced the 2026 Top 10 for LLM Applications alongside the Agent Control Standard. The new edition surpassed 10,000 downloads within its first 48 hours. The release also expands mappings to other leading frameworks, including NIST, MITRE ATLAS, CWE and the OWASP GenAI Security Project's Top 10 for Agentic Applications.

The sources are not fully consistent on dates. One press-release snippet is truncated at "2, 2026," so I have only the URL's September 1 date, and some OWASP page listings show unrelated later dates. Check the official pages at genai.owasp.org for exact release dates.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### user · 2026-11-21T07:58:20.183Z

<details><summary>نتيجة أداة (3689 حرف)</summary>

```
Web search results for query: "NVD API rate limit 50 requests rolling 30 second window with API key public rate limit 5 requests"

Links: [{"title":"U.S. flag   An official website of the United States government","url":"https://nvd.nist.gov/developers/start-here"},{"title":"U.S. flag   An official website of the United States government","url":"https://nvd.nist.gov/general/news/API-Key-Announcement"},{"title":"U.S. flag   An official website of the United States government","url":"https://nvd.nist.gov/General/News/changes-to-feeds-and-apis"},{"title":"Nist Rate Limits","url":"https://apis.io/rate-limits/nist/nist-rate-limits/"},{"title":"U.S. flag   An official website of the United States government","url":"https://nvd.nist.gov/general/news/changes-to-feeds-and-apis"},{"title":"U.S. flag   An official website of the United States government","url":"https://nvd.nist.gov/developers/api-key-requested"},{"title":"api workflows","url":"https://nvd.nist.gov/developers/api-workflows"},{"title":"DEV Community","url":"https://dev.to/ayinedjimi-consultants/how-to-scrape-and-parse-cve-data-from-nvd-api-v2-3p0p"},{"title":"diff mbox series","url":"https://patchwork.yoctoproject.org/comment/15662"},{"title":"github.com","url":"https://github.com/api-evangelist/nvd"},{"title":"diff mbox series","url":"https://patchwork.yoctoproject.org/project/oe-core/patch/[REDACTED_EMAIL]/"},{"title":"NVD API 2.0 Python API","url":"https://libraries.io/pypi/nvd-api"},{"title":"Huge News!Announcing our $40M Series B led by Abstract Ventures.Learn More","url":"https://socket.dev/pypi/package/nvd-api"},{"title":"Terms of Use","url":"https://open.windriver.com/info/uni-license-list/licenses/nist-nvd-api-tou.html"},{"title":"vulnerabilities 1","url":"https://nvd.nist.gov/developers/vulnerabilities-1"},{"title":"nvd cve api","url":"https://apis.io/apis/nvd/nvd-cve-api/"},{"title":"github.com","url":"https://github.com/nodejs/node/commit/373304b0c7"},{"title":"github.com%2Fkannkyo%2Fnvd api","url":"https://awesome.ecosyste.ms/projects/github.com%2Fkannkyo%2Fnvd-api"}]

The official NVD developer page confirms the numbers you mentioned. Anonymous callers are held to five requests in any rolling half-minute span, while a registered API key raises that ceiling to 50 in the same window The public rate limit (without an API key) is 5 requests in a rolling 30 second window; the rate limit with an API key is 50 requests in a rolling 30 second window.

NVD still advises pacing your requests even with a key. Its guidance is to pause for several seconds between calls so legitimate requests aren't refused it is still recommended that your application sleeps for several seconds between requests so that legitimate requests are not denied. The commonly cited practice is a six-second pause, which NVD recommends for users without a key It is also recommended that users "sleep" their scripts for six seconds between requests.

A few related points:
- Rate limits are counted per key, not per user. Rate limits may be reached by the total number of requests from all instances when the application queries the NVD API, even if multiple users access your application through different IP addresses.
- Keys are meant for one person or organization. Keys should not be used by, or shared with, individuals or organizations other than the original requestor.
- Third-party sources agree on the figures. The apis.io profile lists the anonymous limit at 5 per 30-second window and the keyed limit at 50, and a Yocto Project patch uses a 6-second delay without a key and 0.6 seconds with one.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### user · 2026-11-21T07:58:20.489Z

<details><summary>نتيجة أداة (2658 حرف)</summary>

```
Web search results for query: "NIST SP 800-61 Rev 3 final; NIST IR 8374 Rev 1 ransomware profile status"

Links: [{"title":"Official websites use .gov","url":"https://csrc.nist.gov/projects/ransomware"},{"title":"Official websites use .gov","url":"https://csrc.nist.gov/pubs/ir/8374/r1/final"},{"title":"Official websites use .gov","url":"https://csrc.nist.gov/publications/detail/nistir/8374/final"},{"title":"Official websites use .gov","url":"https://csrc.nist.gov/pubs/ir/8374/final"},{"title":"Official websites use .gov","url":"https://csrc.nist.gov/Projects/ransomware"},{"title":"nvlpubs.nist.gov","url":"https://nvlpubs.nist.gov/nistpubs/ir/2022/NIST.IR.8374.pdf"},{"title":"nvlpubs.nist.gov","url":"https://nvlpubs.nist.gov/nistpubs/ir/2026/NIST.IR.8374r1.pdf"},{"title":"www.nist.gov","url":"https://www.nist.gov/node/1696411"},{"title":"Date Published: February 2022","url":"https://csrc.nist.gov/Pubs/ir/8374/Final"},{"title":"Official websites use .gov","url":"https://csrc.nist.gov/Pubs/ir/8374/IPD"},{"title":"www.nist.gov","url":"https://www.nist.gov/node/1914406"},{"title":"nist ir 8374r1 ransomware risk management cybersecurity framework 20 community profile","url":"https://www.nist.gov/publications/nist-ir-8374r1-ransomware-risk-management-cybersecurity-framework-20-community-profile"},{"title":"Official websites use .gov","url":"https://csrc.nist.gov/News/2022/final-ransomware-risk-management-csf-profile"},{"title":"nvlpubs.nist.gov","url":"https://nvlpubs.nist.gov/nistpubs/ir/2025/NIST.IR.8374r1.ipd.pdf"},{"title":"Official websites use .gov","url":"https://csrc.nist.gov/news/2026/ransomware-risk-management-ir-8374r1"},{"title":"Official websites use .gov","url":"https://csrc.nist.gov/projects/ransomware-protection-and-response"}]

The search found clear results for the ransomware profile but nothing on SP 800-61 Rev. 3, so I can't confirm that one's status.

**NIST IR 8374 Rev. 1 (ransomware profile): final.** NIST's ransomware project page says the final version is out and titled it a Cybersecurity Framework profile. The NIST document's history lists a final Rev. 1 dated 06/11/26, and it supersedes the 2022 IR 8374. The revision was updated to align with the NIST CSF 2.0 after originally being built on CSF 1.1. Earlier, the Rev. 1 draft said it would replace the original NISTIR 8374 once finalized.

**NIST SP 800-61 Rev. 3: no results.** None of the results mentioned SP 800-61 at all, so I can't say whether it's final. You'd need to check the NIST CSRC publications page directly for its current status.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### assistant · 2026-11-21T07:58:24.706Z

**أداة:** `Bash`

```json
{
 "command": "cd /tmp; for u in https://csrc.nist.gov/pubs/sp/800/61/r3/final https://csrc.nist.gov/pubs/ai/600/1/final https://www.nist.gov/itl/ai-risk-management-framework https://csrc.nist.gov/pubs/cswp/29/final https://genai.owasp.org/llm-top-10/ https://support.apple.com/en-us/100100; do echo \"== $u\"; curl -sL -m 25 \"$u\" | sed 's/<script[^>]*>.*<\\/script>//g;s/<[^>]*>/ /g' | tr -s ' \\n' | grep -iE \"published|final|version|revision|status|2026|rss|feed|LLM[0-9]+\" | head -8 | cut -c1-220; done",
 "description": "Fetch standards pages for status"
}
```

### assistant · 2026-11-21T07:58:26.878Z

**أداة:** `Bash`

```json
{
 "command": "cd /tmp; curl -sI -m 20 https://developer.apple.com/news/releases/rss/releases.rss | head -3; curl -sL -m 20 https://cert.gov.eg | sed 's/<[^>]*>/ /g' | tr -s ' \\n' | grep -iE \"rss|feed|advisor\" | head -5; curl -sI -m 20 https://nca.gov.sa | head -2; curl -sL -m 20 https://cert.gov.sa | sed 's/<[^>]*>/ /g' | tr -s ' \\n' | grep -iE \"rss|feed\" | head; curl -sI -m 15 https://urlhaus-api.abuse.ch/v1/urls/recent/ | head -1; curl -s -m 15 -X POST https://mb-api.abuse.ch/api/v1/ -d \"query=get_recent&selector=time\" | head -c 200",
 "description": "Probe Apple RSS, CERT-EG, NCA, abuse.ch auth"
}
```

### user · 2026-11-21T07:58:33.855Z

<details><summary>نتيجة أداة (2653 حرف)</summary>

```
== https://csrc.nist.gov/pubs/sp/800/61/r3/final
 Final Pubs 
 Date Published: April 2025 
 04/03/25: SP 800-61 Rev. 3 (Final) 
 rss 
== https://csrc.nist.gov/pubs/ai/600/1/final
 Final Pubs 
 and all final NIST cybersecurity and privacy publications. 
 rss 
== https://www.nist.gov/itl/ai-risk-management-framework
(()=>{var e={8122(e,t,r){"use strict";r.d(t,{a:()=>i});var n=r(944);function i(e,t){try{if(!e||"object"!=typeof e)return(0,n.R)(3);if(!t||"object"!=typeof t)return(0,n.R)(4);const r=Object.create(Object.getPrototypeOf(t)
 On April 7, 2026, NIST released a concept note for an AI RMF Profile on Trustworthy AI in Critical Infrastructure . The profile will guide critical infrastructure operators towards specific risk management practices to 
 class="usa-button usa-button--outline webform-dialog webform-dialog-narrow nist-page-feedback__button"
 href="/webform/page_feedback?page=https://www.nist.gov/itl/ai-risk-management-framework&page_title=AI Risk Management Framework&source_entity_type=node&source_entity_id=1674601"
 data-dialog-options="{&quot;dialogClass&quot;:&quot;no-titlebar page-feedback&quot;}" rel="nofollow"
 RSS Feed 
 href="/webform/nist_gov_feedback?page=/itl/ai-risk-management-framework"
 title="Provide feedback" rel="nofollow" data-dialog-options="{&quot;dialogClass&quot;:&quot;no-titlebar page-feedback&quot;}">Feedback 
== https://csrc.nist.gov/pubs/cswp/29/final
 Final Pubs 
 and all final NIST cybersecurity and privacy publications. 
 rss 
== https://genai.owasp.org/llm-top-10/
				var mi_version = '11.3.0';
var ecs_ajax_params = {"ajaxurl":"https://genai.owasp.org/wp-admin/admin-ajax.php","posts":"{\"post_type\":\"llmrisk\",\"error\":\"\",\"m\":\"\",\"p\":0,\"post_parent\":\"\",\"subpost\":\"\",\"subpost_id\":\"\",\"attachm
class="hfeed site" id="page">
					 Join us in London, Black Hat Week on 12/9/2026 &#8211; Agentic AI Security Summit Europe 2026 				 
 LLM01:2025 Prompt Injection 
 LLM02:2025 Sensitive Information Disclosure 
 LLM03:2025 Supply Chain 
 LLM04:2025 Data and Model Poisoning 
== https://support.apple.com/en-us/100100
 showHelpFulfeedBack: true,
 hlsUrl: "/clientside/versioned/hls.1eb8e605.js"
 publish_date: "11182026",
 status: "unarchived",
 version: "121.0.0.0"
 appDataSchemaVersion: '2.0.0',
 The latest version of iOS and iPadOS is 27.2.1. Learn how to update the software on your iPhone or iPad . The latest version of macOS is 27.2.1. Learn how to&nbsp; update the software on your Mac &nbsp;and how to allow 
 Note that after a software update is installed for iOS, iPadOS, tvOS, watchOS, and visionOS, it cannot be downgraded to the previous version.
```

</details>

### user · 2026-11-21T07:58:58.472Z

**نتيجة أداة:**
```
HTTP/1.1 200 OK
Server: Apple
Date: Sat, 21 Nov 2026 07:58:00 GMT
HTTP/2 308 
date: Sat, 21 Nov 2026 07:58:37 GMT
HTTP/1.1 401 Unauthorized
{"error": "Unauthorized"}
```

### assistant · 2026-11-21T07:59:01.338Z

**أداة:** `WebFetch`

```json
{
 "url": "https://genai.owasp.org/2026/09/01/owasp-genai-security-project-unveils-2026-top-10-for-llm-applications-new-agent-control-standard-and-sponsors-as-community-tops-30000-members/",
 "prompt": "What exactly was released: name/version of LLM Top 10 2026, release date, and the Agent Control Standard. Quote nothing; summarize."
}
```

### assistant · 2026-11-21T07:59:02.475Z

**أداة:** `WebSearch`

```json
{
 "query": "free cloud storage 2026 Google Drive 15GB MEGA 20GB pCloud Koofr 10GB Filen 10GB kDrive 15GB Icedrive 10GB TeraBox 1TB Proton Drive 5GB Box 10GB Dropbox 2GB OneDrive 5GB",
 "mode": "extended"
}
```

### user · 2026-11-21T07:59:06.472Z

**نتيجة أداة:**
```
The OWASP GenAI Security Project released the **OWASP Top 10 for LLM Applications 2026**, the latest edition of its flagship guidance on the most critical security risks for applications built on large language models. The announcement is dated **September 2, 2026**, though the blog post is dated September 1, 2026.

The project also donated the **Agent Control Standard (ACS)**. It complements the project's existing work on agentic AI risks, controls, identity, governance, and testing by moving that guidance toward runtime enforcement.
```

### user · 2026-11-21T07:59:09.634Z

<details><summary>نتيجة أداة (3126 حرف)</summary>

```
Web search results for query: "free cloud storage 2026 Google Drive 15GB MEGA 20GB pCloud Koofr 10GB Filen 10GB kDrive 15GB Icedrive 10GB TeraBox 1TB Proton Drive 5GB Box 10GB Dropbox 2GB OneDrive 5GB"

Links: [{"title":"Best Free Cloud Storage in 2026: 6 Services Compared - TechRepublic","url":"https://www.techrepublic.com/article/news-best-free-cloud-storage-2026/"},{"title":"Best Free Cloud Storage in 2026: 8 Services Compared","url":"https://dupple.com/learn/best-free-cloud-storage"},{"title":"Best Free Cloud Storage in 2026: 10 Free Plans Compared","url":"https://techpresso.co/reviews/best-free-cloud-storage"},{"title":"Best Free Cloud Storage 2026: 9 Free Plans Compared","url":"https://www.mrplanb.com/storage/top-free-cloud-storage"},{"title":"Best Free Cloud Storage 2026: What You… - The Day Current","url":"https://thedaycurrent.com/guides/best-free-cloud-storage"},{"title":"Free Cloud Storage Plans in 2026: Get More for Free","url":"https://allcloudhub.com/free-cloud-storage-plans/"},{"title":"Top Cloud Storage Free Plans of 2026 (Ranked & Tested)","url":"https://ai-refresh.com/tech-help/cloud-storage-free-plans/"},{"title":"14 Best Free Cloud Storage Plans for 2026 (Up to 50 GB Free & Zero-Knowledge Encryption)","url":"https://startupcredits.org/blog/free-cloud-storage-services"},{"title":"Best Free Cloud Storage in 2026: Free Limits Compared","url":"https://techjournal.org/best-free-cloud-storage"}]

The search confirmed most of your list, but not kDrive or Filen, and Proton Drive's figure conflicts between sources.

- **MEGA (20 GB):** Several sources call it the most free space, and it includes end-to-end encryption on the free tier. MEGA wins on raw free space with 20GB versus pCloud's 10GB, and MEGA includes zero-knowledge encryption for free while pCloud charges extra for it. Its free tier has transfer limits, and an over-limit account locks after 30 days and its data is deleted 45 days later.
- **Google Drive (15 GB):** The space is shared with Gmail and Photos. One source notes some new accounts in select regions get 5 GB until a phone number is added.
- **pCloud (10 GB):** pCloud requires completing a short checklist (email verification, app install) to reach the full amount.
- **Koofr (10 GB), Icedrive (10 GB), Box (10 GB):** Koofr is listed as 10 GB free forever. Icedrive's free plan has no desktop sync or file versions. Box's free tier has a single file can't exceed 250 MB cap.
- **Proton Drive (5 GB, conflicting):** Most sources say 5 GB, but one comparison lists 2 GB, up to 5 GB, so check Proton's current page.
- **TeraBox (1 TB):** One source says its free tier comes with limits such as a 4 GB per-file upload cap, ads, and slower transfer speeds.
- **Dropbox (2 GB), OneDrive (5 GB):** Dropbox's free plan covers 2 GB on up to 3 devices. OneDrive's 5 GB suit[s] Windows and Apple users, and one source says it fills the moment Windows backup turns on.
- **kDrive (15 GB) and Filen (10 GB):** The results didn't cover either, so I couldn't verify them.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### assistant · 2026-11-21T07:59:12.515Z

**أداة:** `WebFetch`

```json
{
 "url": "https://kdrive.infomaniak.com/en",
 "prompt": "Free plan storage size, API availability, inactivity deletion policy."
}
```

### assistant · 2026-11-21T07:59:13.015Z

**أداة:** `WebFetch`

```json
{
 "url": "https://filen.io/pricing",
 "prompt": "Free plan storage size; is there a public API/SDK; inactivity policy."
}
```

### assistant · 2026-11-21T07:59:13.545Z

**أداة:** `WebFetch`

```json
{
 "url": "https://proton.me/drive/pricing",
 "prompt": "Free plan storage; public API?; inactivity deletion policy."
}
```

### assistant · 2026-11-21T07:59:14.015Z

**أداة:** `WebFetch`

```json
{
 "url": "https://www.pcloud.com/pricing.html",
 "prompt": "Free plan storage; inactivity deletion policy; API."
}
```

### assistant · 2026-11-21T07:59:14.465Z

**أداة:** `WebFetch`

```json
{
 "url": "https://mega.io/pricing",
 "prompt": "Free plan storage; transfer quota; inactivity deletion policy; public SDK/API."
}
```

### assistant · 2026-11-21T07:59:14.915Z

**أداة:** `WebFetch`

```json
{
 "url": "https://koofr.eu/pricing/",
 "prompt": "Free plan storage; API; inactivity policy."
}
```

### assistant · 2026-11-21T07:59:15.335Z

**أداة:** `WebFetch`

```json
{
 "url": "https://www.dropbox.com/basic",
 "prompt": "Free storage size; inactivity deletion policy."
}
```

### assistant · 2026-11-21T07:59:15.834Z

**أداة:** `WebFetch`

```json
{
 "url": "https://www.box.com/pricing/individual",
 "prompt": "Free plan storage and file size cap; inactivity policy."
}
```

### user · 2026-11-21T07:59:16.556Z

**نتيجة أداة:**
```
Claude Code is unable to fetch from mega.io
```

### user · 2026-11-21T07:59:19.085Z

**نتيجة أداة:**
```
**Free plan storage:** The Free plan includes 10 GB and is listed as "Free forever." It also includes one Koofr Vault Safe Box, 7 days of deleted file retention, and a 50 GB daily public transfer limit.

**API:** The page doesn't mention an API.

**Inactivity policy:** The page doesn't mention an inactivity policy.
```

### user · 2026-11-21T07:59:19.396Z

**نتيجة أداة:**
```
Dropbox Basic includes **2 GB of storage**. The page says, "Sign up for 2 GB of storage, and start accessing and sharing photos, documents, and other files from any device."

The page doesn't mention an inactivity deletion policy, so I can't say whether free accounts are deleted after a period of inactivity. Dropbox's Privacy & terms page or Help Center would likely cover that.
```

### user · 2026-11-21T07:59:20.308Z

**نتيجة أداة:**
```
The provided web page content is only the title "kDrive" and a logo. It doesn't mention the free plan's storage size, API availability, or inactivity deletion policy. To get these details, you'd need the full kDrive pricing, FAQ, or policy pages.
```

### user · 2026-11-21T07:59:20.877Z

**نتيجة أداة:**
```
pCloud is a cloud storage service for files, photos, and documents. It is Swiss-based and emphasizes privacy and encryption. You can choose to store your data in Europe or the USA. The site reports 24M+ users, 130+ countries, 99.98% uptime, and 989B+ files uploaded.

Key features include:
- **Access from anywhere** on laptops, phones, and tablets.
- **File sharing** with others.
- **Storage freedom**, which frees up device space while keeping your files available.
- **Auto-backup and sync**, so files update automatically.
- **Large file support**, with unlimited upload and download speed.

Plans include Individual, Family, and Business options. The free plan has storage, an inactivity deletion policy, and API access. No credit card is required to sign up. pCloud also offers pCloud Pass, pCloud Transfer, pCloud Save, and a developer API.
```

### user · 2026-11-21T07:59:21.638Z

**نتيجة أداة:**
```
- **Free plan storage:** The page doesn't state the size of a free plan. It lists only paid Pro plans, from Pro I (200 GiB) to Pro X (10 TiB), and a "Get started for free" button that links to registration.
- **Public API/SDK:** The page doesn't explicitly say whether a public API or SDK is available. The footer has a "Developers" link to docs.filen.io, which suggests developer documentation exists, but the page doesn't describe it.
- **Inactivity policy:** The FAQ asks "Does Filen delete data after a period of inactivity?" but the answer isn't included in the page content. The Terms of Service or Privacy Policy, linked in the footer, may address this, or you can contact Filen.
```

### user · 2026-11-21T07:59:22.144Z

**نتيجة أداة:**
```
**Free plan storage and file size limits:**

- **Individual (free):** 10 GB of storage and a 250 MB file upload limit. Each file keeps 1 version. Shared-link downloads are capped at 10 GB per user per month.
- **Free Developer:** 10 GB of storage and a 2 GB file upload limit, with 10K API calls and 1,000 Box AI units per month.

**Inactivity policy:** The page doesn't address one. For details, check the [Fair Use Policy](/legal/fairusepolicy) or Box's [help center](https://support.box.com/hc/en-us).
```

### user · 2026-11-21T08:00:26.723Z

**نتيجة أداة:**
```
ETIMEDOUT: connection timed out, read
```

### assistant · 2026-11-21T08:00:57.452Z

**أداة:** `SubagentHandback`

```json
{
 "message": "Research as of 2026-11-21. \"V\" = verified live this session (fetch, curl or gh API). \"U\" = unverified or taken from third-party sources.\n\n**A. Threat feeds**\n| Feed | Machine-readable URL | Format | Key? | Rate limit | License/terms | Update freq |\n|---|---|---|---|---|---|---|\n| CISA KEV | https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json (HTTP 200 V); also .../csv/known_exploited_vulnerabilities.csv; schema .../feeds/known_exploited_vulnerabilities_schema.json | JSON/CSV | No | none stated | license file at /sites/default/files/licenses/kev/license.txt (text not read: U) | not stated; entries dated 2026-11-20 seen |\n| NVD CVE API 2.0 | https://services.nvd.nist.gov/rest/json/cves/2.0 (endpoint from memory: U); docs https://nvd.nist.gov/developers/start-here | JSON | Optional, free key | 5 req / rolling 30 s without key, 50 with key; NVD advises a ~6 s sleep (per search snippet of the official page) | NVD API Terms of Use (not read: U) | continuous |\n| FIRST EPSS | https://api.first.org/data/v1/epss?cve=CVE-... (V, returned data dated 2026-11-20, \"access\":\"public\"); bulk https://epss.empiricalsecurity.com/epss_scores-current.csv.gz (302 redirect V) | JSON / CSV.gz | No | not stated (U) | FIRST terms page not read (U) | daily |\n| CVE Program cvelistV5 | https://github.com/CVEProject/cvelistV5 | CVE JSON 5.x (5.2.0 noted 2025-10-29) | No | normal GitHub limits | CVE Program Terms of Use; repo has no SPDX license | repo about every 7 min; daily midnight-UTC baseline zip; hourly delta zips |\n| OSV.dev | POST https://api.osv.dev/v1/query, /v1/querybatch, GET /v1/vulns/{id}; bulk https://osv-vulnerabilities.storage.googleapis.com/all.zip (HTTP 200 V) | JSON | No | \"no limits\" on API; 32 MiB response cap on HTTP/1.1 | per-source (U) | continuous |\n| GitHub Advisory DB | https://github.com/github/advisory-database (CC-BY-4.0 V); REST /advisories | OSV JSON | Repo: no. REST API: token optional (U) | GitHub API limits (U) | CC-BY-4.0 | last commit 2026-11-21 06:36Z (V) |\n| MITRE ATT&CK | https://github.com/mitre-attack/attack-stix-data, enterprise-attack/enterprise-attack.json | STIX 2.1 | No | n/a | MITRE ATT&CK Terms of Use, repo SPDX NOASSERTION | latest is **v20.1** (release 2026-11-05, files enterprise-attack-20.1.json) |\n| MITRE ATLAS | https://github.com/mitre-atlas/atlas-data, dist/ATLAS-latest.yaml | YAML (authoritative), STIX 2.1, xlsx | No | n/a | MITRE, repo SPDX NOASSERTION (terms U) | latest release tag **v2026.10** (2026-10-28) |\n| Apple security releases | https://support.apple.com/en-us/100100 | HTML only; no RSS link found on the page | No | n/a | Apple site terms | latest listed: macOS 27.2.1 / iOS 27.2.1 (2026-11-09), macOS 26.7.3, HomeView 27.2.1 (2026-11-18) |\n| abuse.ch (MalwareBazaar / URLhaus / ThreatFox) | mb-api.abuse.ch/api/v1/, urlhaus-api.abuse.ch/v1/, threatfox-api.abuse.ch | JSON/CSV | **Yes, Auth-Key** | unauthenticated is limited | see abuse.ch terms (U) | continuous |\n| CERT-EG / Saudi NCA | https://cert.gov.eg, https://nca.gov.sa | none found | n/a | n/a | n/a | n/a |\n\nCaveats for A:\n- abuse.ch: its 2024-11-18 post says authentication is mandatory from 2025-06-30, and an unauthenticated MalwareBazaar POST returned 401. Get a key at https://auth.abuse.ch/.\n- CERT-EG and NCA: no machine-readable feed found. nca.gov.sa returned a 308 redirect that I did not follow, so treat NCA as U.\n- The NVD rate-limit figures come from a search snippet of the official page, not a direct fetch.\n\n**B. Standards**\n| Standard | Current version | Status / date | Source |\n|---|---|---|---|\n| NIST CSF 2.0 | 2.0 (CSWP 29) | final, Feb 2024 (date from memory: U) | https://csrc.nist.gov/pubs/cswp/29/final |\n| CIS Controls | v8.1 | released 2024-06-25; no v9 found as of Nov 2026 | https://www.cisecurity.org/controls/v8-1 |\n| NIST SP 800-61 | Rev 3 | final, 2025-04-03 (V) | https://csrc.nist.gov/pubs/sp/800/61/r3/final |\n| NIST IR 8374 | Rev 1, \"Ransomware Risk Management: CSF 2.0 Community Profile\" | final, 2026-06-11 per search results; PDF at nvlpubs.nist.gov/nistpubs/ir/2026/NIST.IR.8374r1.pdf | https://csrc.nist.gov/pubs/ir/8374/r1/final |\n| OWASP ASVS | 5.0.0 | released 2025-05-30; next planned is 5.0.1 (patch) | https://github.com/OWASP/ASVS |\n| OWASP Top 10 for LLM Applications | **2026 edition** | announced 2026-09-01/02 | https://genai.owasp.org/2026/09/01/owasp-genai-security-project-unveils-2026-top-10-for-llm-applications-new-agent-control-standard-and-sponsors-as-community-tops-30000-members/ |\n| OWASP Top 10 for Agentic Applications | 2026 (\"ASI01..ASI10\" naming is from memory: U) | published 2025-12-09 | https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/ |\n| NIST AI RMF | 1.0 | no revision found; 2026-04-07 concept note for a Critical Infrastructure profile (V) | https://www.nist.gov/itl/ai-risk-management-framework |\n| NIST AI 600-1 (GenAI Profile) | final | July 2024 (date from memory: U); page exists on csrc | https://csrc.nist.gov/pubs/ai/600/1/final |\n\nCaveat for B: genai.owasp.org/llm-top-10/ still showed the LLM01:2025 list when I fetched it, so the 2026 edition's item list is not read. Confirm its exact title before citing.\n\n**C. Claude Code / AI security skills** (all repos checked via the GitHub API, V)\n| Repo | Owner | License | Stars | Last push | Contents | Risk notes |\n|---|---|---|---|---|---|---|\n| https://github.com/trailofbits/skills | Trail of Bits | CC-BY-SA-4.0 | 8,321 | 2026-11-21 | Plugin marketplace of ~45 plugins: static-analysis, semgrep-rule-creator, variant-analysis, differential-review, supply-chain-risk-auditor, insecure-defaults, sharp-edges, fp-check, yara-authoring, agentic-actions-auditor, cvss-scoring, c-review, rust-review, and others | Only install-time code found is devcontainer-setup's install.sh and post_install.py. Otherwise markdown prompts. Read before enabling. CC-BY-SA is share-alike if you copy content. |\n| https://github.com/cloudflare/skills | Cloudflare | Apache-2.0 | 3,418 | 2026-11-17 | skills/: workers-best-practices, wrangler, durable-objects, turnstile-spin, web-perf, cloudflare-one, and others. **No \"security audit\" skill.** Also ships .mcp.json | Official org. An MCP config means remote tool access, so review it. |\n| \"cloudflare-security-audit-skill\" clones (e.g. nightmaregaming6969-art/..., kilofafeure/..., iamrudhresh/...) | random users | n/a | 0-3 | Sep-Nov 2026 | n/a | **Not official.** Do not install. |\n| https://github.com/mukul975/Anthropic-Cybersecurity-Skills | mukul975 (individual, not Anthropic) | Apache-2.0 | 36,478 | 2026-08-31 | ~817 skills mapped to ATT&CK, NIST CSF, ATLAS, D3FEND; tools/ holds validators | Name implies Anthropic ownership; it is not. Offensive-heavy content. Scripts not audited (U). |\n| https://github.com/SnailSploit/Claude-Red | SnailSploit | MIT | 11,326 | 2026-11-17 | offensive-security skills (from search hit; contents not inspected: U) | Offensive content, not audited. |\n| https://github.com/Masriyan/Claude-Code-CyberSecurity-Skill | Masriyan | NOASSERTION | 591 | 2026-10-20 | 22 skills | No clear license. |\n| https://github.com/agamm/claude-code-owasp | agamm | MIT | 457 | 2026-11-03 | OWASP-focused skill | Small repo, not audited. |\n\nCaveat for C: I did not read install scripts in the third-party collections. Star counts are from the GitHub search API.\n\n**D. Free cloud storage** (official-page checks where noted; otherwise third-party blogs, U)\n| Service | Free quota | Public API? | Inactivity / deletion | Source |\n|---|---|---|---|---|\n| Google Drive | 15 GB, shared with Gmail and Photos (U; blogs) | Yes, Drive API v3 (U, from memory) | 2-year inactivity policy (U, from memory) | blogs listed in search |\n| MEGA | 20 GB (U); transfer quota applies | Yes, MEGA SDK and MEGAcmd (U) | over-limit accounts lock after 30 days and data is deleted 45 days later (U; third-party) | mega.io was blocked for fetch |\n| OneDrive | 5 GB (U) | Yes, Microsoft Graph (U) | not stated | U |\n| Dropbox | 2 GB (V) | Yes, Dropbox API (U) | not stated on page | https://www.dropbox.com/basic |\n| Box | 10 GB, 250 MB file cap (V); Free Developer plan: 10 GB, 2 GB file cap, 10K API calls/month (V) | Yes | not stated | https://www.box.com/pricing/individual |\n| Proton Drive | 5 GB per most blogs, one lists 2 GB: U | No public API (U) | U | pricing page timed out |\n| pCloud | 10 GB (U); page says the free plan has an inactivity deletion policy and API access (V); policy details not read | Yes | Yes, exists, specifics U | https://www.pcloud.com/pricing.html |\n| Koofr | 10 GB \"Free forever\" (V); 50 GB/day public transfer; 7-day deleted-file retention | Not on pricing page (U; a REST API exists per memory) | not mentioned | https://koofr.eu/pricing/ |\n| Filen | free size not on pricing page (10 GB per blogs: U) | Yes, SDK docs at docs.filen.io (link only) | FAQ question exists, answer not captured: U | https://filen.io/pricing |\n| kDrive (Infomaniak) | 15 GB per blogs: U (official page empty) | U | U | https://kdrive.infomaniak.com/en |\n| Icedrive | 10 GB, no desktop sync or versions (U; blog) | U | U | U |\n| TeraBox | 1 TB, 4 GB per-file cap, ads (U; blog) | U | U | U |\n| iCloud Drive | 5 GB (U) | No general public API (U) | U | U |\n\nCaveat for D: only Dropbox, Box, Koofr and the pCloud summary were verified from official pages. Everything else needs checking on the official site before you build on it."
}
```

### user · 2026-11-21T08:00:57.717Z

**نتيجة أداة:**
```
{"success":true,"message":"Report delivered to your caller."}
```
