# Read-only audit. Project: /Users/M7/XXX (Python stdlib servi

- المصدر: `subagents`
- معرف الجلسة: `ed02eefe-8921-4ae5-8979-c856ae49faeb`
- البداية: 2026-11-21T16:13:18.784Z — النهاية: 2026-11-21T16:16:55.542Z
- الرسائل: مستخدم 11 · مساعد 9 · أدوات 9
- تنظيف الخصوصية: أرقام التليفون وال api_id والـ hash والمفاتيح والإيميلات اتشالت بـ regex، وده مش مضمون ١٠٠٪.

## ملخص تلقائي (مش تلخيص AI)
- مبني على أول طلب وآخر رد وقايمة طلبات المستخدم. راجع المحادثة الكاملة للتفاصيل.
- **أول طلب:** Read-only audit. Project: /Users/M7/XXX (Python stdlib service in src/xxx/*.py, web UI in src/xxx/web/*.js + index.html, tests in tests/, CI in .github/workflows and .gitlab-ci.yml). The catalog docs/research/MASTER_CATALOG.md is stale: many rows marked NOT BUILT / PARTIAL were built since.

For each of these catalog row numbers: 2, 4, 6, 7, 15, 19, 23, 26, 27, 29, 41, 42, 45, 47, 55, 58, 60, 63, 68, 69, 76, 77, 87, 100, 101, 102, 103, 107, 118, 119, 132, 136, 141 — read the row's requirement, t
- **طلبات المستخدم (أول 15):**
  1. Read-only audit. Project: /Users/M7/XXX (Python stdlib service in src/xxx/*.py, web UI in src/xxx/web/*.js + index.html, tests in tests/, CI in .githu
  2. <system-reminder>
Your final report is delivered through SubagentHandback: when your work is complete, call SubagentHandback({message: <your full repo
- **آخر رد للمساعد:** —

---

## المحادثة الكاملة

### user · 2026-11-21T16:13:18.784Z

Read-only audit. Project: /Users/M7/XXX (Python stdlib service in src/xxx/*.py, web UI in src/xxx/web/*.js + index.html, tests in tests/, CI in .github/workflows and .gitlab-ci.yml). The catalog docs/research/MASTER_CATALOG.md is stale: many rows marked NOT BUILT / PARTIAL were built since.

For each of these catalog row numbers: 2, 4, 6, 7, 15, 19, 23, 26, 27, 29, 41, 42, 45, 47, 55, 58, 60, 63, 68, 69, 76, 77, 87, 100, 101, 102, 103, 107, 118, 119, 132, 136, 141 — read the row's requirement, then grep/read the code to decide the TRUE current status: BUILT / PARTIAL / NOT BUILT. Evidence = file + function name (e.g. `vulnintel.py apple_check`). Check src/xxx/autopilot.py (it has tiers with dns, ransomware, sensors checks), agents.py, care.py, guard.py, report.py, breach.py, repoguard.py, vulnintel.py, hardening.py, tools.py, rescue.py, sensors.py, accounts.py, historyscan.py, malware.py.

For PARTIAL / NOT BUILT rows, say in one line what exactly is missing and whether it is buildable with Python stdlib + tools already on the Mac (gh CLI signed in, rclone, ClamAV, system tools) without admin rights and without paid accounts.

Return a compact table: row | true status | evidence | missing part (if any) | buildable (yes/no + why). Max ~40 lines. Do not edit any file.

### user · 2026-11-21T16:13:21.044Z

<system-reminder>
Your final report is delivered through SubagentHandback: when your work is complete, call SubagentHandback({message: <your full report>}). The call ends your run, so make it your last step. Only a SubagentHandback call reaches your caller as your result; plain text you write at the end is not delivered. Do not also send the report with SendMessage: your caller would get it twice.
</system-reminder>

### assistant · 2026-11-21T16:13:25.325Z

**أداة:** `Bash`

```json
{
 "command": "cd /Users/M7/XXX && ls src/xxx | head -80; grep -nE '^\\|\\s*(2|4|6|7|15|19|23|26|27|29|41|42|45|47|55|58|60|63|68|69|76|77|87|100|101|102|103|107|118|119|132|136|141)\\s*\\|' docs/research/MASTER_CATALOG.md"
}
```

### user · 2026-11-21T16:13:30.709Z

<details><summary>نتيجة أداة (6581 حرف)</summary>

```
__init__.py
__main__.py
__pycache__
accounts.py
agents.py
alerts.py
assistant.py
autopilot.py
breach.py
briefing.py
browsers.py
care.py
cli.py
data
drivefile.py
driveindex.py
driveops.py
eventlog.py
guard.py
hardening.py
historyscan.py
location.py
malware.py
net.py
netscan.py
phish.py
projects.py
radar.py
repoguard.py
report.py
rescue.py
secrets_scan.py
sensors.py
storage.py
tools.py
updater.py
vulnintel.py
watch.py
web
webshield.py
whatif.py
24:| 2 | Real signature coverage: ClamAV DB + custom YARA rules. تغطية تواقيع حقيقية | A1§5, R3.1 | PARTIAL ClamAV 1.5.5 in `~/.xxx/clamav`; no YARA | yes (YARA wheel U) | P2 |
26:| 4 | Process monitor, suspicious process, stop own process only. مراقبة العمليات | R3.1 | PARTIAL `tools.py` (list, stop_process) | yes (osquery pilot) | P2 |
28:| 6 | Continuous background monitoring. مراقبة مستمرة | C, R3.1 | PARTIAL `watch.py` LaunchAgent every 15 min, opt-in | yes | P2 (tune) |
29:| 7 | Ransomware / mass-encryption detection. كشف الفدية | R3.1 | PARTIAL decoy files only (`watch.py`) | partly (rate of file changes via FSEvents; no kernel hooks) | P2 |
37:| 15 | Disk health and volume verify. صحة القرص | C | PARTIAL `tools.system` SMART line, `verify_disk` | yes | P2 |
45:| 19 | DNS and outbound-domain monitoring. مراقبة DNS | R3.2 | NOT BUILT | partly (per-app via LuLu; no packet capture without tap) | P2 |
49:| 23 | Per-app outbound firewall prompts. جدار ناري للاتصالات الصادرة | R3.2 | NOT BUILT | yes (LuLu) | P2 |
56:| 26 | Protect email, GitHub, GitLab accounts. حماية الحسابات | C, R3.3 | PARTIAL `repoguard.py` GitHub repos only | partly (read-only via official APIs) | P2 |
57:| 27 | MFA/passkey status reminder per account. تذكير MFA | R3.3, A1§6 | NOT BUILT | partly (checklist; providers hide 2FA state from others) | P2 |
59:| 29 | Leaked-credential / breach monitoring. تسريب بيانات | R3.3, C | NOT BUILT | partly: Pwned Passwords range API free, no key (V 200); breach list free (V 200); per-email lookup needs paid key (V 401) | P2 |
79:| 41 | GitHub posture: public/private, branch protection; plus collaborators, deploy keys, Actions permissions, secret-scanning alerts. حالة المستودعات | R3.4, A1§7 | PARTIAL `repoguard.py` (visibility, main protection) | yes (`gh`, read-only) | P2 |
80:| 42 | GitLab posture. حالة جيت لاب | C, A1§7 | NOT BUILT (labelled "not checked") | yes (`glab` or token, read-only) | P2 |
83:| 45 | CI/CD review: Actions permissions, unpinned actions. فحص CI | R3.4 | NOT BUILT | yes (read workflow YAML, local) | P2 |
85:| 47 | Detect code copy / exfiltration; decoys. كشف نسخ الكود | R13, C | PARTIAL decoy files | partly (cannot stop screenshots, R13 says so) | P2 |
97:| 55 | Backup status and tested restore, 3-2-1. نسخ احتياطي واختبار الاستعادة | R3.7, R10, A1§22 | NOT BUILT | yes (`tmutil`; Restic pilot) | P1 |
104:| 58 | EPSS exploit probability per CVE. احتمال الاستغلال | A1§8 | NOT BUILT | yes (api.first.org, TR) | P1 |
106:| 60 | Apple security releases vs installed macOS. تحديثات أبل | R4 | NOT BUILT | partly (HTML page parse only, TR) | P2 |
109:| 63 | Source registry, dedupe, severity + confidence, track to closure. سجل مصادر وحالة | R4, A1§8 | NOT BUILT | yes | P2 |
114:| 68 | Version-aware KEV match (Info.plist `CFBundleShortVersionString`). مطابقة بالإصدار | RM next | NOT BUILT | yes | P1 |
115:| 69 | Proactive alert to projects (ARABCO, AI Trading Dashboard, Technical Office) when their dependency has a CVE. تنبيه المشاريع | R9, A1§13, C | PARTIAL `projects.py` scans listed repos | yes (add repos to `~/.xxx/projects.json`) | P2 |
130:| 76 | Scan CLAUDE.md, skills, `.mcp.json` for injected instructions and new MCP servers. فحص ملفات الوكلاء | R7, R14 | NOT BUILT | yes (local grep rules) | P2 |
131:| 77 | Vet every skill/MCP/plugin before install, owner yes. فحص المهارات قبل التثبيت | R14, A1§17 | PARTIAL manual rule + TR table | yes | P2 |
145:| 87 | Voice in and out, Arabic. صوت عربي | C | PARTIAL `app.js` SpeechRecognition + speechSynthesis; spoken replies untested | yes (WKWebView support U) | P2 test |
166:| 100 | Disk space, health, performance; warn at 20% free. صحة وأداء الجهاز | R11, C 05:56 | PARTIAL `tools.system`; hook `disk-check.sh` | yes | P1 (card) |
167:| 101 | Cleanup: temp files, unneeded apps (list, owner deletes). تنظيف | R11, C | NOT BUILT | yes (list sizes; delete behind two clicks) | P2 |
168:| 102 | Check and install updates. تحديثات | R11 | PARTIAL `hardening.py` (`softwareupdate --list`) | yes (install by owner click) | P2 |
169:| 103 | Repair/refresh/maintenance tools. صيانة وإصلاح | C 16:07 | PARTIAL `tools.verify_disk` | yes | P2 |
177:| 107 | Storage discovery, read-only: `diskutil list/info`, `system_profiler`. اكتشاف الأقراص | A3§2A, C | PARTIAL `tools.system` | yes | P2 |
196:| 118 | Evidence/incident report file (events, hashes, times, chain hash). ملف البلاغ | C 12:02, 12:05 | NOT BUILT | yes | P2 |
197:| 119 | Read-only IP info: RDAP/whois owner and abuse contact. معلومات الـIP | C 12:02 | NOT BUILT | yes (RDAP is public JSON, U for rate limits) | P2 |
218:| 132 | Tools over display: see devices, Wi-Fi, in/out traffic, control. أدوات أكثر من العرض | C 15:29 | PARTIAL tabs network, connections, startup | yes | P2 |
222:| 136 | Each tab simple, explain and recommend. شرح وتوصيات | C 15:29 | PARTIAL | yes | P2 |
231:| 141 | Tests run and pass (27 on 3.9 and 3.11); CI on push. اختبارات و CI | RM | PARTIAL tests built; `.github/` absent | yes | P2 |
391:| 2 | EPSS column on KEV items | 58 | api.first.org | Mocked reply adds a score to a CVE row; offline shows "not checked", never 0. |
393:| 4 | Gitleaks pilot for repo history (optional, shown only if installed; install after owner yes) | 38, 30 | Gitleaks 8.30.1 | Temp repo with a dummy key in an old commit is reported with commit id; the full secret is not in the output or log; not installed shows "not installed". |
395:| 6 | GitHub guard extension: collaborators, deploy keys, Actions permissions, secret-scanning/Dependabot alert counts (read-only) | 41, 45, 26 | `gh` | Fixture JSON shows each flag; 403 shows "not verified (plan limit)"; no `gh` write call in the code (grep test). |
396:| 7 | GitLab guard (read-only), then mirror SHA check against GitHub | 42, 50 | `glab` or API token (owner login) | Fixture project JSON gives visibility and protected-branch flags; differing fixture SHAs show "mirror out of sync". |
404:| 15 | GitHub Actions: run unittest on Python 3.9 and 3.11 on every push (no `.github/` yet) | 141 | GitHub Actions | A push shows two green jobs; a deliberately failing test turns it red. |
```

</details>

### assistant · 2026-11-21T16:13:36.040Z

**أداة:** `Bash`

```json
{
 "command": "cd /Users/M7/XXX && ls .github/workflows .gitlab-ci.yml tests 2>&1 | head -50; wc -l src/xxx/*.py | tail -50; grep -nE '^def |^class ' src/xxx/{autopilot,agents,care,guard,report,breach,repoguard,vulnintel,hardening,tools,rescue,sensors,accounts,historyscan,malware,watch,projects,netscan,net,secrets_scan,eventlog}.py | cut -c1-110"
}
```

### user · 2026-11-21T16:13:41.624Z

<details><summary>نتيجة أداة (12941 حرف)</summary>

```
.gitlab-ci.yml

.github/workflows:
tests.yml

tests:
test_phish.py
test_storage_tools.py
test_v3.py
test_xxx.py
       2 src/xxx/__init__.py
       3 src/xxx/__main__.py
     264 src/xxx/accounts.py
      43 src/xxx/agents.py
      66 src/xxx/alerts.py
     269 src/xxx/assistant.py
     329 src/xxx/autopilot.py
      55 src/xxx/breach.py
     217 src/xxx/briefing.py
      92 src/xxx/browsers.py
     129 src/xxx/care.py
      88 src/xxx/cli.py
     128 src/xxx/drivefile.py
      84 src/xxx/driveindex.py
     129 src/xxx/driveops.py
      77 src/xxx/eventlog.py
     106 src/xxx/guard.py
      97 src/xxx/hardening.py
      77 src/xxx/historyscan.py
      44 src/xxx/location.py
     264 src/xxx/malware.py
      38 src/xxx/net.py
     111 src/xxx/netscan.py
      65 src/xxx/phish.py
     102 src/xxx/projects.py
     437 src/xxx/radar.py
     132 src/xxx/repoguard.py
      80 src/xxx/report.py
      34 src/xxx/rescue.py
     125 src/xxx/secrets_scan.py
      37 src/xxx/sensors.py
     205 src/xxx/storage.py
     232 src/xxx/tools.py
     120 src/xxx/updater.py
      85 src/xxx/vulnintel.py
     197 src/xxx/watch.py
      68 src/xxx/webshield.py
      47 src/xxx/whatif.py
    4678 total
src/xxx/agents.py:29:def overview(days: int = 7) -> dict:
src/xxx/breach.py:18:def _emails_path():
src/xxx/breach.py:22:def emails() -> list[str]:
src/xxx/breach.py:29:def set_emails(body: dict) -> tuple[int, str]:
src/xxx/breach.py:38:def check(opener=None) -> dict:
src/xxx/care.py:24:def _run(args: list[str], timeout: int = 30) -> str:
src/xxx/care.py:32:def parse_backup(latest: str, destinations: str) -> dict:
src/xxx/care.py:43:def backup_status() -> dict:
src/xxx/care.py:47:def pwned_count(password: str, fetcher=fetch) -> int:
src/xxx/care.py:59:def check_password(body: dict) -> tuple[int, dict]:
src/xxx/care.py:69:def ai_files(home: Path | None = None) -> list[Path]:
src/xxx/care.py:83:def mcp_servers(text: str) -> list[str]:
src/xxx/care.py:95:def scan_ai(home: Path | None = None) -> dict:
src/xxx/care.py:112:def disks() -> dict:
src/xxx/care.py:120:def biggest(folder: str | None = None, limit: int = 15) -> list[dict]:
src/xxx/repoguard.py:17:def gh_path() -> str:
src/xxx/repoguard.py:25:def github_name(repo: Path) -> str:
src/xxx/repoguard.py:35:def _gh(path: str) -> tuple[int, dict]:
src/xxx/repoguard.py:54:def parse_repo(status: int, body: dict) -> dict:
src/xxx/repoguard.py:60:def parse_protection(status: int) -> str:
src/xxx/repoguard.py:69:def github_repos() -> list[str]:
src/xxx/repoguard.py:85:def gitlab_repos() -> list[str]:
src/xxx/repoguard.py:98:def gitlab_visibility(path: str) -> str:
src/xxx/repoguard.py:109:def check() -> list[dict]:
src/xxx/repoguard.py:119:def _github_row(name: str) -> dict:
src/xxx/guard.py:17:def _run(args: list[str], timeout: int = 30) -> str:
src/xxx/guard.py:24:def recently_changed(seconds: int = 60) -> list[str]:
src/xxx/guard.py:34:def ransomware_signals(changed: list[str]) -> list[dict]:
src/xxx/guard.py:45:def parse_dns(text: str) -> list[str]:
src/xxx/guard.py:49:def dns_servers() -> list[str]:
src/xxx/guard.py:53:def odd_processes(ps_text: str) -> list[dict]:
src/xxx/guard.py:64:def process_signals() -> list[dict]:
src/xxx/guard.py:71:def unpinned_actions(text: str) -> list[str]:
src/xxx/guard.py:76:def workflows_report(repos: list[Path]) -> list[dict]:
src/xxx/guard.py:85:def _spots() -> dict:
src/xxx/guard.py:91:def cleanup() -> list[dict]:
src/xxx/guard.py:101:def reveal(body: dict) -> tuple[int, str]:
src/xxx/vulnintel.py:17:def parse_epss(raw: bytes) -> dict:
src/xxx/vulnintel.py:28:def epss(cves: list[str], fetcher=fetch) -> dict:
src/xxx/vulnintel.py:40:def app_versions() -> dict:
src/xxx/vulnintel.py:55:def parse_apple(page: str) -> list[dict]:
src/xxx/vulnintel.py:64:def _ver(text: str) -> tuple:
src/xxx/vulnintel.py:68:def macos_status(installed: str, rows: list[dict]) -> dict:
src/xxx/vulnintel.py:81:def apple_check(installed: str, fetcher=fetch) -> dict:
src/xxx/hardening.py:28:def _run(args: list[str], timeout: int = 20) -> str:
src/xxx/hardening.py:36:def parse(outputs: dict, listening_ports: set[str]) -> list[dict]:
src/xxx/hardening.py:63:def score(checks: list[dict]) -> int:
src/xxx/hardening.py:70:def status() -> dict:
src/xxx/hardening.py:86:def pending_updates() -> list[str]:
src/xxx/hardening.py:92:def open_setting(key) -> tuple[int, str]:
src/xxx/autopilot.py:26:def home() -> Path:
src/xxx/autopilot.py:30:def _load(name: str, default):
src/xxx/autopilot.py:37:def _save(name: str, value):
src/xxx/autopilot.py:45:def enabled() -> bool:
src/xxx/autopilot.py:49:def set_enabled(on) -> tuple[int, str]:
src/xxx/autopilot.py:59:def feed(limit: int = 60) -> list[dict]:
src/xxx/autopilot.py:67:def _feed_add(row: dict):
src/xxx/autopilot.py:72:def in_safe_dir(path: str) -> bool:
src/xxx/autopilot.py:77:def decide(signal: dict, auto_ok: bool) -> str:
src/xxx/autopilot.py:96:def tick(now: float, checks: dict, actions: dict) -> str:
src/xxx/autopilot.py:160:def _new_files_check():
src/xxx/autopilot.py:188:def _changes_check():
src/xxx/autopilot.py:197:def _decoy_check():
src/xxx/autopilot.py:202:def _settings_check():
src/xxx/autopilot.py:208:def _ransom_check():
src/xxx/autopilot.py:213:def _dns_check():
src/xxx/autopilot.py:224:def _process_check():
src/xxx/autopilot.py:229:def _sensor_check():
src/xxx/autopilot.py:238:def _breach_check():
src/xxx/autopilot.py:245:def _update_check():
src/xxx/autopilot.py:251:def _disk_check():
src/xxx/autopilot.py:257:def _apple_check():
src/xxx/autopilot.py:263:def _backup_check():
src/xxx/autopilot.py:269:def _quarantine(sig):
src/xxx/autopilot.py:278:def _decoy_action(sig):
src/xxx/autopilot.py:284:def _notify(text: str):
src/xxx/autopilot.py:299:def run_once() -> str:
src/xxx/autopilot.py:303:def undo(item_id) -> tuple[int, str]:
src/xxx/autopilot.py:319:def start(every: int = 60):
src/xxx/rescue.py:10:def _plist(args: list[str]) -> dict:
src/xxx/rescue.py:18:def describe(info: dict) -> dict:
src/xxx/rescue.py:26:def disks() -> list[dict]:
src/xxx/tools.py:23:def _run(command: list[str], timeout: int = 10) -> subprocess.CompletedProcess | None:
src/xxx/tools.py:30:def _out(command: list[str]) -> str:
src/xxx/tools.py:35:def parse_arp(text: str, gateway: str = "") -> list[dict]:
src/xxx/tools.py:46:def network() -> dict:
src/xxx/tools.py:62:def parse_lsof(text: str) -> dict:
src/xxx/tools.py:84:def connections() -> dict:
src/xxx/tools.py:89:def parse_ps(text: str, limit: int = 15) -> list[dict]:
src/xxx/tools.py:103:def inventory() -> list[str]:
src/xxx/tools.py:121:def system() -> dict:
src/xxx/tools.py:142:def verify_disk() -> tuple[int, str]:
src/xxx/tools.py:161:def stop_process(pid) -> tuple[int, str]:
src/xxx/tools.py:181:def signer(path: str) -> str:
src/xxx/tools.py:196:def _signer(path: str) -> str:
src/xxx/tools.py:208:def startup_items() -> list[dict]:
src/xxx/report.py:18:def public_ips(active: list[dict]) -> list[str]:
src/xxx/report.py:31:def parse_rdap(data: dict) -> dict:
src/xxx/report.py:45:def owner_of(ip: str) -> dict:
src/xxx/report.py:52:def build(events: list[dict], active: list[dict], lookup=owner_of, days: int = 7) -> str:
src/xxx/report.py:71:def write(_body=None) -> tuple[int, dict]:
src/xxx/historyscan.py:22:def gitleaks_path() -> str:
src/xxx/historyscan.py:27:def install(_body=None, fetcher=lambda url: fetch(url, limit=100_000_000, timeout=12
src/xxx/historyscan.py:52:def parse(report: list) -> list[dict]:
src/xxx/historyscan.py:57:def scan_all(_body=None) -> tuple[int, dict]:
src/xxx/sensors.py:14:def parse(log_text: str) -> dict:
src/xxx/sensors.py:31:def status(seconds: int = 90) -> dict:
src/xxx/accounts.py:49:def keychain_has(service: str) -> bool:
src/xxx/accounts.py:58:def keychain_secret(service: str) -> str:
src/xxx/accounts.py:66:def _ticks_path() -> Path:
src/xxx/accounts.py:70:def _gh_ok() -> bool:
src/xxx/accounts.py:79:def status() -> list[dict]:
src/xxx/accounts.py:108:def _service(sid):
src/xxx/accounts.py:112:def _terminal(command: str):
src/xxx/accounts.py:117:def connect(body: dict) -> tuple[int, str]:
src/xxx/accounts.py:177:def disconnect(body: dict) -> tuple[int, str]:
src/xxx/accounts.py:192:def open_page(body: dict) -> tuple[int, dict]:
src/xxx/accounts.py:205:def _free_name(exe: str, sid: str) -> str:
src/xxx/accounts.py:218:def _no_open_dir() -> Path:
src/xxx/accounts.py:228:def has_token(exe: str, name: str) -> bool:
src/xxx/accounts.py:240:def auth_url_from(proc, wait: float = 25.0) -> str:
src/xxx/accounts.py:254:def tick(body: dict) -> tuple[int, str]:
src/xxx/malware.py:29:def home() -> Path:
src/xxx/malware.py:33:def load_signatures() -> set[str]:
src/xxx/malware.py:41:def clamscan() -> str:
src/xxx/malware.py:50:def clam_home() -> Path:
src/xxx/malware.py:55:def update_clam_db(max_age: int = 86400) -> bool:
src/xxx/malware.py:73:def engine() -> dict:
src/xxx/malware.py:79:def sha256(path: Path) -> str:
src/xxx/malware.py:87:def check_file(path: Path, signatures: set[str]) -> Finding | None:
src/xxx/malware.py:102:def fingerprint(path: Path) -> str:
src/xxx/malware.py:111:def check_app(path: Path) -> Finding | None:
src/xxx/malware.py:123:def parse_clamscan(output: str) -> list[Finding]:
src/xxx/malware.py:128:def scan(root: Path, on_finding=None, on_progress=None) -> tuple[list[Finding], dict]:
src/xxx/malware.py:178:def scan_and_log(root: Path, on_finding=None, on_progress=None) -> tuple[list[Finding],
src/xxx/malware.py:197:def _index_path() -> Path:
src/xxx/malware.py:201:def list_quarantine() -> list[dict]:
src/xxx/malware.py:208:def _save(index: list[dict]):
src/xxx/malware.py:215:def quarantine(raw_path) -> tuple[int, str]:
src/xxx/malware.py:248:def restore(item_id) -> tuple[int, str]:
src/xxx/watch.py:22:def _home() -> Path:
src/xxx/watch.py:26:def _save_json(path: Path, value):
src/xxx/watch.py:33:def _load_json(path: Path, default):
src/xxx/watch.py:40:def parse_devices(data: dict) -> tuple[list[str], list[str]]:
src/xxx/watch.py:59:def devices() -> tuple[list[str], list[str]]:
src/xxx/watch.py:68:def snapshot() -> dict:
src/xxx/watch.py:78:def diff(old: dict, new: dict) -> list[tuple[str, str]]:
src/xxx/watch.py:86:def check_changes() -> list[tuple[str, str]]:
src/xxx/watch.py:99:def _sha(path: Path) -> str:
src/xxx/watch.py:103:def _in_git_repo(folder: Path) -> bool:
src/xxx/watch.py:107:def plant(raw_folder) -> tuple[int, str]:
src/xxx/watch.py:126:def check_canaries() -> list[dict]:
src/xxx/watch.py:142:def canaries() -> list[dict]:
src/xxx/watch.py:147:def plist_text(python: str, src: str) -> bytes:
src/xxx/watch.py:160:def _plist_path() -> Path:
src/xxx/watch.py:164:def agent_status() -> dict:
src/xxx/watch.py:168:def set_agent(on) -> tuple[int, str]:
src/xxx/watch.py:186:def notify(lines: list[str]):
src/xxx/watch.py:193:def run_once() -> list[str]:
src/xxx/projects.py:18:def repos() -> list[Path]:
src/xxx/projects.py:28:def parse_requirements(text: str) -> tuple[list[dict], list[str]]:
src/xxx/projects.py:43:def parse_package_lock(text: str) -> list[dict]:
src/xxx/projects.py:55:def manifests(repo: Path) -> dict:
src/xxx/projects.py:70:def match_osv(packages: list[dict], reply: dict) -> list[dict]:
src/xxx/projects.py:80:def osv_query(packages: list[dict]) -> list[dict]:
src/xxx/projects.py:89:def scan_repos(query=osv_query) -> list[dict]:
src/xxx/eventlog.py:19:def default_path() -> Path:
src/xxx/eventlog.py:23:def _digest(prev: str, body: dict) -> str:
src/xxx/eventlog.py:28:def read(path: Path) -> list[dict]:
src/xxx/eventlog.py:35:def _last_hash(path: Path) -> str:
src/xxx/eventlog.py:45:def append(kind: str, status: str, detail: str, source: str = "", path: Path | None = N
src/xxx/eventlog.py:67:def verify(path: Path | None = None) -> int | None:
src/xxx/net.py:12:def _ssl_context() -> ssl.SSLContext:
src/xxx/net.py:21:def fetch(url: str, limit: int = MAX_FEED_BYTES, timeout: int = 10) -> bytes:
src/xxx/net.py:30:def post_json(url: str, payload: dict, timeout: int = 30) -> dict:
src/xxx/secrets_scan.py:37:class Finding:
src/xxx/secrets_scan.py:45:def redact(secret: str, confidence: str) -> str:
src/xxx/secrets_scan.py:51:def scan_text(text: str, path: str) -> list[Finding]:
src/xxx/secrets_scan.py:68:def _scan_file(path: Path, stats: dict) -> list[Finding]:
src/xxx/secrets_scan.py:86:def scan_path(root: str | os.PathLike, on_finding=None, on_progress=None) -> tuple[
src/xxx/secrets_scan.py:105:def scan_and_log(root: Path, on_finding=None, on_progress=None) -> tuple[list[Find
src/xxx/secrets_scan.py:121:def _walk(root: Path):
src/xxx/netscan.py:22:def lan_targets(local_ip: str) -> list[str]:
src/xxx/netscan.py:34:def _ping(ip: str) -> bool:
src/xxx/netscan.py:41:def _open(ip: str, port: int) -> bool:
src/xxx/netscan.py:47:def private_mac(mac: str) -> bool:
src/xxx/netscan.py:55:def kind(open_ports: list[int]) -> str:
src/xxx/netscan.py:70:def upnp_on(gateway: str, timeout: float = 2.0) -> bool:
src/xxx/netscan.py:87:def scan() -> dict:
```

</details>

### assistant · 2026-11-21T16:13:44.954Z

**أداة:** `Bash`

```json
{
 "command": "cd /Users/M7/XXX/src/xxx && sed -n 150,300p autopilot.py; cat guard.py agents.py care.py | cut -c1-160"
}
```

### assistant · 2026-11-21T16:13:45.269Z

**أداة:** `Bash`

```json
{
 "command": "cd /Users/M7/XXX/src/xxx && cat repoguard.py vulnintel.py report.py sensors.py | cut -c1-170"
}
```

### user · 2026-11-21T16:13:52.854Z

<details><summary>نتيجة أداة (19489 حرف)</summary>

```
                continue
            state["last_notify"] = now
            state["notified_today"] += 1
            actions["notify"](text)
        state["seen"] = {k: v for k, v in seen.items() if now - v < DEDUPE * 7}
        _save("autopilot_state.json", state)
        return f"{len(signals)} signals, {acted} actions"


# ---------- real checks and actions (the tests pass fakes instead) ----------
def _new_files_check():
    from . import malware
    state = _load("autopilot_state.json", {})
    since = state.get("files_since", time.time() - 3600)
    files = [p for d in SAFE_DIRS for p in (Path.home() / d).glob("*") if p.is_file() and p.stat().st_mtime > since
             and p.suffix.lower() in RISKY]
    state["files_since"] = time.time()
    _save("autopilot_state.json", state)
    found = []
    for path in files[:200]:
        hit = malware.check_file(path, malware.load_signatures())
        if hit:
            found.append((path, hit.rule, hit.confidence))
    if files and malware.clamscan():
        listing = home() / "autopilot_files.txt"
        listing.write_text("\n".join(str(p) for p in files[:200]))
        out = subprocess.run(["nice", "-n", "15", malware.clamscan(), f"--database={malware.clam_home() / 'db'}", "--infected", "--no-summary",
                              f"--file-list={listing}"], capture_output=True, text=True, timeout=900).stdout
        found += [(Path(f.path), f.rule, f.confidence) for f in malware.parse_clamscan(out)]
    signals = []
    for path, rule, confidence in found:
        status = "FOUND" if confidence == "high" else "GUESS"
        mark = malware.fingerprint(path) if path.exists() else "unreadable"
        eventlog.append("malware", status, f"{rule} ({confidence}) autopilot | id {mark}", str(path))
        signals.append({"kind": "malware", "status": status, "subject": str(path), "why": rule, "fingerprint": mark})
    return signals


def _changes_check():
    from . import watch
    out = []
    for kind, item in watch.check_changes():
        k = "usb_keyboard" if kind == "usb" and "keyboard" in item.lower() else kind
        out.append({"kind": k, "status": "GUESS", "subject": item, "why": kind})
    return out


def _decoy_check():
    from . import watch
    return [{"kind": "decoy", "status": "FOUND", "subject": a["path"], "why": a["state"]} for a in watch.check_canaries()]


def _settings_check():
    from . import hardening
    weak = [c for c in hardening.status()["checks"] if c["state"] == "weak" and c["id"] in ("firewall", "filevault", "gatekeeper")]
    return [{"kind": "setting", "status": "GUESS", "subject": c["id"], "why": c["detail"]} for c in weak]


def _ransom_check():
    from . import guard
    return guard.ransomware_signals(guard.recently_changed(60))


def _dns_check():
    from . import guard
    state = _load("autopilot_state.json", {})
    now, before = guard.dns_servers(), state.get("dns")
    state["dns"] = now
    _save("autopilot_state.json", state)
    if before is not None and now and set(now) != set(before):
        return [{"kind": "dns", "status": "GUESS", "subject": ", ".join(now), "why": f"was {', '.join(before)}"}]
    return []


def _process_check():
    from . import guard
    return guard.process_signals()


def _sensor_check():
    from . import sensors
    st = sensors.status(70)
    if not st["active"]:
        return []
    who = ", ".join(st["apps"]) or "app unknown"
    return [{"kind": "sensor", "status": "GUESS", "subject": f"{'/'.join(st['sensors']) or 'camera/mic'}: {who}", "why": "macOS indicator on"}]


def _breach_check():
    from . import breach
    out = breach.check()
    return [{"kind": "breach", "status": "FOUND", "subject": r["email"], "why": ", ".join(r["breaches"][:5])}
            for r in out["results"] if r["breaches"]]


def _update_check():
    from . import updater
    st = updater.status()
    return [{"kind": "update", "status": "GUESS", "subject": st["latest"], "why": f"running {st['running']}"}] if st["available"] else []


def _disk_check():
    from . import care
    d = care.disks()
    return [{"kind": "disk", "status": "FOUND", "subject": f"{d['free_pct']}% free", "why": "under 20%"}] if d["free_pct"] < 20 else []


def _apple_check():
    from . import hardening, vulnintel
    a = vulnintel.apple_check(hardening._run(["sw_vers", "-productVersion"]))
    return [{"kind": "macos_update", "status": "GUESS", "subject": a["latest"], "why": f"this Mac {a['installed']}"}] if a["state"] == "update" else []


def _backup_check():
    from . import care
    b = care.backup_status()
    return [] if b["state"] == "ok" else [{"kind": "backup", "status": "GUESS", "subject": b["state"], "why": "time machine"}]


def _quarantine(sig):
    from . import malware
    code, message = malware.quarantine(sig["subject"])
    if code != 200:
        return f"not moved: {message}", ""
    item = next((i for i in reversed(malware.list_quarantine()) if i["original"] == sig["subject"]), {})
    return "moved to quarantine", item.get("id", "")


def _decoy_action(sig):
    from . import report
    code, result = report.write()
    return ("incident report written" if code == 200 else "report failed"), ""


def _notify(text: str):
    from . import alerts, watch
    watch.notify([text])
    alerts.send(text)  # phone (Telegram / Discord) when the owner connected one


# Every minute only cheap checks; anything that runs codesign, system_profiler or ClamAV waits 15 minutes.
CHECKS = {"minute": {"decoys": _decoy_check, "ransomware": _ransom_check, "dns": _dns_check, "sensors": _sensor_check,
                     "new_files": _new_files_check},  # cheap when nothing new arrived: only risky new files are scanned
          "quarter": {"changes": _changes_check, "settings": _settings_check, "processes": _process_check},
          "hour": {"backup": _backup_check, "disk": _disk_check},
          "day": {"apple": _apple_check, "breach": _breach_check, "update": _update_check}}
ACTIONS = {"malware": _quarantine, "decoy": _decoy_action, "ransomware": _decoy_action, "notify": _notify}


def run_once() -> str:
    return tick(time.time(), CHECKS, ACTIONS)
"""More guards for the autopilot: mass file changes (ransomware), DNS servers changing, programs
running from temporary or download folders, unpinned GitHub Actions, and a cleanup list.
All read-only; the autopilot decides what to do with the signals."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

RANSOM_EXT = re.compile(r"\.(locked|encrypted|crypt|crypted|enc|cry|lock|ransom|wncry|pay)$", re.I)
RANSOM_NOTE = re.compile(r"(how|help)[_ -]?(to)?[_ -]?(decrypt|restore|recover)|readme.*(decrypt|ransom)|_readme_?\.txt$", re.I)
WATCHED = ("Documents", "Desktop", "Downloads", "Pictures")
MASS_CHANGES = 300  # files changed in one minute that look like a mass rewrite
ODD_PLACES = re.compile(r"^(/private)?/tmp/|^/private/var/folders/[^/]+/[^/]+/T/(?!AppTranslocation)|/Downloads/")


def _run(args: list[str], timeout: int = 30) -> str:
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=timeout).stdout
    except (OSError, subprocess.TimeoutExpired):
        return ""


def recently_changed(seconds: int = 60) -> list[str]:
    """Files whose content changed in the last N seconds in the owner's main folders (Spotlight index)."""
    found = []
    for folder in WATCHED:
        path = Path.home() / folder
        if path.is_dir():
            found += _run(["mdfind", "-onlyin", str(path), f"kMDItemFSContentChangeDate >= $time.now(-{seconds})"]).splitlines()
    return found


def ransomware_signals(changed: list[str]) -> list[dict]:
    names = [Path(p).name for p in changed]
    odd = [n for n in names if RANSOM_EXT.search(n) or RANSOM_NOTE.search(n)]
    if odd:
        return [{"kind": "ransomware", "status": "FOUND", "subject": ", ".join(odd[:5]), "why": f"{len(odd)} files look encrypted or like a ransom note"}]
    if len(changed) >= MASS_CHANGES:
        return [{"kind": "ransomware", "status": "GUESS", "subject": f"{len(changed)} files in 1 minute",
                 "why": "mass change: a sync, backup or unzip can do this too"}]
    return []


def parse_dns(text: str) -> list[str]:
    return sorted({m for m in re.findall(r"nameserver\[\d+\]\s*:\s*(\S+)", text)})


def dns_servers() -> list[str]:
    return parse_dns(_run(["scutil", "--dns"]))


def odd_processes(ps_text: str) -> list[dict]:
    """Programs running from /tmp, a temp folder or Downloads: malware often starts there."""
    out = []
    for line in ps_text.splitlines():
        parts = line.strip().split(None, 1)
        if len(parts) == 2 and parts[0].isdigit() and ODD_PLACES.search(parts[1]):
            out.append({"kind": "process", "status": "GUESS", "subject": parts[1][:200], "why": f"pid {parts[0]} runs from a temporary or download folder",
                        "pid": int(parts[0])})
    return out


def process_signals() -> list[dict]:
    return odd_processes(_run(["ps", "-axo", "pid=,comm="]))


UNPINNED = re.compile(r"^\s*-?\s*uses:\s*['\"]?([\w.-]+/[\w./-]+)@([\w.-]+)['\"]?\s*(?:#.*)?$", re.M)


def unpinned_actions(text: str) -> list[str]:
    """GitHub Actions used by tag/branch instead of a full commit SHA (a changed tag can run new code)."""
    return [f"{name}@{ref}" for name, ref in UNPINNED.findall(text) if not re.fullmatch(r"[0-9a-f]{40}", ref)]


def workflows_report(repos: list[Path]) -> list[dict]:
    rows = []
    for repo in repos:
        files = list((repo / ".github" / "workflows").glob("*.y*ml"))
        bad = sorted({a for f in files for a in unpinned_actions(f.read_text(errors="replace"))})
        rows.append({"repo": repo.name, "workflows": len(files), "unpinned": bad})
    return rows


def _spots() -> dict:
    home = Path.home()
    return {"caches": home / "Library" / "Caches", "logs": home / "Library" / "Logs", "trash": home / ".Trash",
            "xcode": home / "Library" / "Developer" / "Xcode" / "DerivedData", "downloads": home / "Downloads"}


def cleanup() -> list[dict]:
    """Places that usually hold space you can free, with sizes. Nothing is deleted here."""
    rows = []
    for key, path in _spots().items():
        if path.exists():
            size = _run(["du", "-sk", str(path)], timeout=120).split("\t")[0]
            rows.append({"key": key, "path": str(path), "bytes": int(size) * 1024 if size.isdigit() else 0})
    return rows


def reveal(body: dict) -> tuple[int, str]:
    path = _spots().get(body.get("key")) if isinstance(body, dict) else None
    if not path or not path.exists():
        return 400, "bad request"
    subprocess.run(["open", str(path)], capture_output=True, timeout=30)  # Finder: the owner deletes himself
    return 200, "opened"
"""Agent Control Center: the seven specialist agents from the owner's design, each backed by the
modules that really do its job today, and the Master Orchestrator (the autopilot) that runs them.
Numbers come from the event log and the autopilot feed; nothing is invented."""
from __future__ import annotations

import time

from . import autopilot, eventlog

# id -> (kinds of events/feed rows that belong to it, the modules that do its work)
AGENTS = {
    "sentinel": ({"malware", "quarantine", "process", "sensor", "ransomware", "usb_keyboard", "usb"},
                 ["malware.py (ClamAV)", "autopilot: new files, processes, camera/mic", "guard.py: ransomware"]),
    "guardian": ({"devices", "ports", "bluetooth", "network", "dns", "watch"},
                 ["netscan.py", "watch.py: devices, ports, USB, Bluetooth", "guard.py: DNS"]),
    "threat_hunter": ({"whatif", "deps", "macos_update"},
                      ["CISA KEV + EPSS", "OSV.dev", "Apple releases", "briefing.py: What-If 7x7"]),
    "red_blue": ({"setting", "backup", "disk", "error"},
                 ["hardening.py: macOS checks", "care.py: backup, passwords", "defensive checks only, no attacks"]),
    "cloud_defender": ({"storage", "tools", "secret"},
                       ["repoguard.py: GitHub/GitLab", "historyscan.py: Gitleaks", "storage.py: rclone", "accounts.py"]),
    "forensics": ({"report", "canary", "decoy"},
                  ["report.py: incident file + RDAP", "rescue.py: disks", "eventlog.py: hash-chained log"]),
    "architect": ({"autopilot", "scan"},
                  ["care.py: AI-agent config check", "guard.py: Actions pinning", "projects.py"]),
}


def overview(days: int = 7) -> dict:
    since = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(time.time() - days * 86400))
    events = [dict(e, status="GUESS") if e.get("status") == "FOUND" and "(low)" in e.get("detail", "") else e
              for e in eventlog.read(eventlog.default_path()) if e.get("ts", "") >= since]  # old logs stored guesses as FOUND
    feed = [r for r in autopilot.feed(500) if r.get("ts", "") >= since[:19]]
    rows = []
    for agent, (kinds, modules) in AGENTS.items():
        mine = [e for e in events if e.get("kind") in kinds] + [r for r in feed if r.get("kind") in kinds]
        rows.append({"id": agent, "modules": modules,
                     "found": sum(1 for x in mine if x.get("status") == "FOUND"),
                     "guess": sum(1 for x in mine if x.get("status") == "GUESS"),
                     "actions": sum(1 for x in feed if x.get("kind") in kinds and x.get("did")),
                     "last": max((x.get("ts", "") for x in mine), default="")})
    return {"orchestrator": {"enabled": autopilot.enabled(), "actions_today": autopilot._load("autopilot_state.json", {}).get("auto_today", 0)},
            "agents": rows}
"""Care tools: backup status, password leak check, AI-agent config check, disks and space.
All read-only. Deleting or erasing anything is never done here."""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path

from .net import fetch

PWNED_RANGE = "https://api.pwnedpasswords.com/range/{}"
# Phrases that try to take over an AI agent when it reads a file (prompt injection).
INJECTION = re.compile(r"ignore (all |any )?(previous|prior|above) instructions|disregard (the )?(system|previous) (prompt|instructions)|"
                       r"new instructions:|send (the |your )?(api[_ ]?key|token|password)s? to\b|"
                       r"curl [^\n|]*\|\s*(ba)?sh|base64 -d[^\n]*\|\s*(ba)?sh", re.I)
# Lines that only describe or warn about injection (security docs) are not attacks.
DESCRIBES = re.compile(r"may contain|e\.g\.|example|such as|like [`\"']|never|not instructions|treat .* as data|detect|flag", re.I)


def _run(args: list[str], timeout: int = 30) -> str:
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return (result.stdout + result.stderr).strip()


def parse_backup(latest: str, destinations: str) -> dict:
    if "No destinations configured" in destinations:
        return {"state": "none", "age_days": None, "destination": ""}
    match = re.search(r"(\d{4}-\d{2}-\d{2})-(\d{6})", latest)
    name = re.search(r"Name\s*:\s*(.+)", destinations)
    if not match:
        return {"state": "unknown", "age_days": None, "destination": name[1].strip() if name else ""}
    age = (time.time() - time.mktime(time.strptime(match[1], "%Y-%m-%d"))) / 86400
    return {"state": "ok" if age <= 7 else "old", "age_days": round(age, 1), "destination": name[1].strip() if name else ""}


def backup_status() -> dict:
    return parse_backup(_run(["tmutil", "latestbackup"]), _run(["tmutil", "destinationinfo"]))


def pwned_count(password: str, fetcher=fetch) -> int:
    """How many times this password appears in known leaks. Only the first 5 characters of its
    SHA-1 hash leave the Mac (k-anonymity); the password itself is never sent or stored."""
    digest = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    body = fetcher(PWNED_RANGE.format(digest[:5])).decode("utf-8", "replace")
    for line in body.splitlines():
        suffix, _, count = line.strip().partition(":")
        if suffix == digest[5:]:
            return int(count or 0)
    return 0


def check_password(body: dict) -> tuple[int, dict]:
    password = [REDACTED]"password") if isinstance(body, dict) else None
    if not isinstance(password, str) or not password or len(password) > 256:
        return 400, {"message": "bad request"}
    try:
        return 200, {"message": "ok", "count": pwned_count(password)}
    except (OSError, ValueError):
        return 502, {"message": "source unavailable"}


def ai_files(home: Path | None = None) -> list[Path]:
    """Files that tell AI agents what to do: CLAUDE.md / AGENTS.md, skills, MCP server lists."""
    home = home or Path.home()
    found = [home / ".mcp.json", home / ".claude.json", home / ".claude" / "CLAUDE.md", home / "CLAUDE.md"]
    for root in (home / ".claude" / "skills", home / ".claude" / "agents", home / ".claude" / "commands"):
        if root.is_dir():
            found += [p for p in root.rglob("*") if p.suffix in (".md", ".json", ".sh", ".py") and p.is_file()][:2000]
    for docs in (home / "Documents",):
        if docs.is_dir():
            for project in docs.iterdir():
                found += [project / n for n in ("CLAUDE.md", "AGENTS.md", ".mcp.json")]
    return [p for p in found if p.is_file()]


def mcp_servers(text: str) -> list[str]:
    try:
        data = json.loads(text)
    except ValueError:
        return []
    servers = set((data.get("mcpServers") or {}).keys())
    for project in (data.get("projects") or {}).values():
        if isinstance(project, dict):
            servers |= set((project.get("mcpServers") or {}).keys())
    return sorted(servers)


def scan_ai(home: Path | None = None) -> dict:
    """Injection-like lines in agent instruction files, and every MCP server agents are told to load."""
    hits, servers = [], set()
    files = ai_files(home)
    for path in files:
        try:
            text = path.read_text(errors="replace")[:2_000_000]
        except OSError:
            continue
        if path.suffix == ".json":
            servers |= set(mcp_servers(text))
        for number, line in enumerate(text.splitlines(), 1):
            if INJECTION.search(line) and not DESCRIBES.search(line):
                hits.append({"file": str(path), "line": number, "text": line.strip()[:160]})
    return {"files": len(files), "hits": hits[:200], "mcp_servers": sorted(servers)}


def disks() -> dict:
    """Disks and free space; identify only (nothing is mounted, erased or repaired)."""
    stat = os.statvfs(str(Path.home()))
    total, free = stat.f_blocks * stat.f_frsize, stat.f_bavail * stat.f_frsize
    return {"free": free, "total": total, "free_pct": round(100 * free / total) if total else 0,
            "list": _run(["diskutil", "list"])[:6000]}


def biggest(folder: str | None = None, limit: int = 15) -> list[dict]:
    """Largest folders one level under a folder (sizes only)."""
    root = Path(folder or Path.home()).expanduser()
    out = _run(["du", "-sk", *[str(p) for p in root.iterdir() if not p.is_symlink()]], timeout=180) if root.is_dir() else ""
    rows = []
    for line in out.splitlines():
        size, _, path = line.partition("\t")
        if size.isdigit():
            rows.append({"path": path, "bytes": int(size) * 1024})
    return sorted(rows, key=[REDACTED] r: -r["bytes"])[:limit]
```

</details>

### user · 2026-11-21T16:13:53.399Z

<details><summary>نتيجة أداة (15217 حرف)</summary>

```
"""Repo guard: read-only checks of the owner's GitHub repos (public or private, main protected).
Uses the gh program the owner is already signed in to; never writes, never reads the token."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

from .projects import repos

REMOTE = re.compile(r"github\.com[:/]([^/]+)/([^/.\s]+?)(?:\.git)?$")


def gh_path() -> str:
    # Apps opened from Finder get a short PATH, so the usual install folders are checked too.
    for candidate in (shutil.which("gh"), str(Path.home() / ".local/bin/gh"), "/opt/homebrew/bin/gh", "/usr/local/bin/gh"):
        if candidate and os.access(candidate, os.X_OK):
            return candidate
    return ""


def github_name(repo: Path) -> str:
    try:
        url = subprocess.run(["git", "-C", str(repo), "remote", "get-url", "origin"],
                             capture_output=True, text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""
    match = REMOTE.search(url)
    return f"{match[1]}/{match[2]}" if match else ""


def _gh(path: str) -> tuple[int, dict]:
    """GET one GitHub API path. Returns (HTTP status, JSON body)."""
    gh = gh_path()
    if not gh:
        return 0, {}
    try:
        result = subprocess.run([gh, "api", "-i", "--method", "GET", path], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return 0, {}
    parts = re.split(r"\r?\n\r?\n", result.stdout, maxsplit=1)
    head, body = parts[0], parts[1] if len(parts) > 1 else ""
    status = re.match(r"HTTP/\S+ (\d+)", head)
    try:
        payload = json.loads(body) if body.strip() else {}
    except ValueError:
        payload = {}
    return (int(status[1]) if status else 0), payload


def parse_repo(status: int, body: dict) -> dict:
    if status != 200 or not isinstance(body.get("private"), bool):
        return {"visibility": "not verified", "branch": ""}
    return {"visibility": "private" if body.get("private") else "public", "branch": body.get("default_branch", "main")}


def parse_protection(status: int) -> str:
    return {200: "protected", 404: "not protected", 403: "not verified (plan limit)"}.get(status, "not verified")


GITHUB_OWNERS = ["saudmoto6868-oss"]  # the owner's second GitHub account (public repos only without its sign-in)
GITLAB_EXTRA = ["6868-group/ls3d-4f810cd5"]
LOCAL_ROOTS = [Path.home() / "Documents", Path.home()]


def github_repos() -> list[str]:
    """Every GitHub repo the signed-in gh account can see, plus the public ones of the other account."""
    names = []
    status, body = _gh("user/repos?per_page=100&affiliation=owner,collaborator,organization_member")
    if status == 200 and isinstance(body, list):
        names += [r["full_name"] for r in body if isinstance(r, dict) and r.get("full_name")]
    for owner in GITHUB_OWNERS:
        status, body = _gh(f"users/{owner}/repos?per_page=100")
        if status == 200 and isinstance(body, list):
            names += [r["full_name"] for r in body if isinstance(r, dict) and r.get("full_name")]
    return sorted(set(names), key=[REDACTED]


GITLAB_REMOTE = re.compile(r"gitlab\.com[:/]([^\s]+?)(?:\.git)?$")


def gitlab_repos() -> list[str]:
    """GitLab mirrors found in the git remotes of the owner's folders on this Mac."""
    found = set(GITLAB_EXTRA)
    for root in LOCAL_ROOTS:
        for folder in [p for p in root.iterdir() if (p / ".git").is_dir()] if root.is_dir() else []:
            try:
                out = subprocess.run(["git", "-C", str(folder), "remote", "-v"], capture_output=True, text=True, timeout=10).stdout
            except (OSError, subprocess.TimeoutExpired):
                continue
            found |= {m[1] for m in map(GITLAB_REMOTE.search, out.split()) if m}
    return sorted(found, key=[REDACTED]


def gitlab_visibility(path: str) -> str:
    """Without a sign-in, GitLab answers 200 only for public projects."""
    from urllib.parse import quote
    from .net import fetch
    try:
        fetch(f"https://gitlab.com/api/v4/projects/{quote(path, safe='')}")
        return "public"
    except OSError as error:
        return "private" if getattr(error, "code", None) == 404 else "not verified"


def check() -> list[dict]:
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(8) as pool:  # each repo needs ~6 GitHub calls; run repos side by side
        rows = list(pool.map(_github_row, github_repos()))
    for path in gitlab_repos():
        rows.append({"host": "GitLab", "repo": path, "visibility": gitlab_visibility(path), "protection": "not checked (needs GitLab sign-in)",
                     "alerts": "not checked"})
    return rows


def _github_row(name: str) -> dict:
    info = parse_repo(*_gh(f"repos/{name}"))
    row = {"host": "GitHub", "repo": name, "visibility": info["visibility"], "protection": "not verified", "alerts": "not verified"}
    if info["branch"]:
        row["protection"] = parse_protection(_gh(f"repos/{name}/branches/{info['branch']}/protection")[0])
        alerts = _gh(f"repos/{name}/vulnerability-alerts")[0]
        row["alerts"] = {204: "on", 404: "off"}.get(alerts, "not verified")
        keys_status, keys = _gh(f"repos/{name}/keys")
        row["deploy_keys"] = len(keys) if keys_status == 200 and isinstance(keys, list) else "not verified"
        collab_status, collab = _gh(f"repos/{name}/collaborators?per_page=100")
        row["collaborators"] = len(collab) if collab_status == 200 and isinstance(collab, list) else "not verified"
        perm_status, perm = _gh(f"repos/{name}/actions/permissions/workflow")
        row["workflow_token"] = perm.get("default_workflow_permissions", "not verified") if perm_status == 200 and isinstance(perm, dict) else "not verified"
    return row
"""Sharper vulnerability info: exploit probability (FIRST EPSS), installed app versions next to
"may affect you" matches, and Apple's own security releases versus this Mac's macOS version."""
from __future__ import annotations

import html
import json
import plistlib
import re
from pathlib import Path

from .net import fetch

EPSS_URL = "https://api.first.org/data/v1/epss?cve={}"
APPLE_URL = "https://support.apple.com/en-us/100100"


def parse_epss(raw: bytes) -> dict:
    data = json.loads(raw)
    out = {}
    for row in data.get("data") or []:
        try:
            out[row["cve"]] = {"epss": round(float(row["epss"]), 4), "percentile": round(float(row["percentile"]), 4)}
        except (KeyError, ValueError, TypeError):
            continue
    return out


def epss(cves: list[str], fetcher=fetch) -> dict:
    """Probability (0-1) that each CVE is exploited in the next 30 days. Missing = not checked."""
    scores = {}
    ids = [c for c in dict.fromkeys(cves) if re.fullmatch(r"CVE-\d{4}-\d{4,7}", c)]
    for start in range(0, len(ids), 100):
        try:
            scores.update(parse_epss(fetcher(EPSS_URL.format(",".join(ids[start:start + 100])))))
        except (OSError, ValueError):
            break
    return scores


def app_versions() -> dict:
    """Installed app name -> (version, last-modified time). Used to say "probably updated after the alert"."""
    found = {}
    for folder in (Path("/Applications"), Path.home() / "Applications"):
        for app in folder.glob("*.app") if folder.is_dir() else []:
            try:
                with open(app / "Contents" / "Info.plist", "rb") as f:
                    info = plistlib.load(f)
                name = str(info.get("CFBundleName") or app.stem)
                found[name] = (str(info.get("CFBundleShortVersionString", "")), app.stat().st_mtime)
            except (OSError, ValueError, plistlib.InvalidFileException):
                continue
    return found


def parse_apple(page: str) -> list[dict]:
    rows = []
    for row in re.findall(r"<tr>(.*?)</tr>", page, re.S):
        cells = [html.unescape(re.sub(r"<[^>]+>", "", c)).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
        if len(cells) >= 3:
            rows.append({"name": cells[0][:120], "for": cells[1][:120], "date": cells[2][:20]})
    return rows


def _ver(text: str) -> tuple:
    return tuple(int(x) for x in re.findall(r"\d+", text)[:3])


def macos_status(installed: str, rows: list[dict]) -> dict:
    """Newest macOS security release in the same major line as this Mac, and whether it is newer."""
    major = _ver(installed)[:1]
    same = [r for r in rows if r["name"].startswith("macOS") and _ver(re.sub(r"^macOS\D*", "", r["name"]))[:1] == major]
    newest = max(same, key=[REDACTED] r: _ver(re.sub(r"^macOS\D*", "", r["name"])), default=None)
    if not newest:
        return {"state": "not checked", "installed": installed, "latest": ""}
    latest = re.sub(r"^macOS\D*", "", newest["name"]).split("This update")[0].strip()
    newer = _ver(latest) > _ver(installed)
    return {"state": "update" if newer else "current", "installed": installed, "latest": newest["name"].split("This update")[0].strip(),
            "date": newest["date"]}


def apple_check(installed: str, fetcher=fetch) -> dict:
    try:
        return macos_status(installed, parse_apple(fetcher(APPLE_URL).decode("utf-8", "replace")))
    except (OSError, ValueError):
        return {"state": "not checked", "installed": installed, "latest": ""}
"""Incident report: one plain-text file the owner can give to the police, his provider or a network's
abuse desk. It holds what XXX saw (findings, watch alerts), the log's chain code so tampering shows,
and for each outside address this Mac talks to: who owns that network and its abuse contact (RDAP).
XXX never contacts anyone itself; the owner decides where the file goes."""
from __future__ import annotations

import ipaddress
import json
import time
from pathlib import Path

from . import eventlog, tools
from .net import fetch

RDAP = "https://rdap.org/ip/{}"


def public_ips(active: list[dict]) -> list[str]:
    found = []
    for conn in active:
        host = str(conn.get("remote", "")).rsplit(":", 1)[0].strip("[]")
        try:
            ip = ipaddress.ip_address(host)
        except ValueError:
            continue
        if ip.is_global and str(ip) not in found:
            found.append(str(ip))
    return found


def parse_rdap(data: dict) -> dict:
    """Network name, country and the abuse e-mail from an RDAP answer."""
    abuse = ""
    for entity in data.get("entities") or []:
        roles = entity.get("roles") or []
        stack = [entity, *(entity.get("entities") or [])]
        for item in stack:
            for field in (item.get("vcardArray") or [None, []])[1]:
                if field and field[0] == "email" and ("abuse" in roles or "abuse" in (item.get("roles") or [])):
                    abuse = abuse or str(field[3])
    return {"network": str(data.get("name", ""))[:80], "country": str(data.get("country", ""))[:8],
            "range": f"{data.get('startAddress', '')} - {data.get('endAddress', '')}", "abuse": abuse[:120]}


def owner_of(ip: str) -> dict:
    try:
        return parse_rdap(json.loads(fetch(RDAP.format(ip))))
    except (OSError, ValueError):
        return {"network": "not checked", "country": "", "range": "", "abuse": ""}


def build(events: list[dict], active: list[dict], lookup=owner_of, days: int = 7) -> str:
    since = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - days * 86400))
    recent = [e for e in events if e.get("ts", "") >= since and (e.get("status") in ("FOUND", "GUESS", "BLOCKED")
                                                               or e.get("kind") in ("watch", "canary"))]
    lines = ["XXX incident report", f"Created: {time.strftime('%Y-%m-%d %H:%M:%S %Z')}",
             f"Log chain code (last record): {events[-1]['hash'][:12] if events else '-'}  |  records: {len(events)}",
             f"Log intact: {eventlog.verify() is None}", "",
             f"What XXX saw in the last {days} days ({len(recent)} items):"]
    lines += [f"  {e['ts']}  {e['kind']:<10} {e['status']:<7} {e['detail'][:140]}  {e.get('source', '')[:120]}" for e in recent[-300:]]
    ips = public_ips(active)[:20]
    lines += ["", f"Outside addresses this Mac is talking to now ({len(ips)}): owner and abuse contact (RDAP)"]
    for ip in ips:
        info = lookup(ip)
        lines.append(f"  {ip:<40} {info['network']:<30} {info['country']:<4} abuse: {info['abuse'] or '-'}")
    lines += ["", "Notes:", "- An IP address shows a network, not a person. Only the provider (with a police request) can say who used it.",
              "- Keep this file and the ~/.xxx folder unchanged; the chain code above lets anyone check the log was not edited."]
    return "\n".join(lines) + "\n"


def write(_body=None) -> tuple[int, dict]:
    text = build(eventlog.read(eventlog.default_path()), tools.connections()["active"])
    folder = Path.home() / "Desktop"
    target = folder / f"XXX-report-{time.strftime('%Y%m%d-%H%M%S')}.txt"
    try:
        target.write_text(text)
    except OSError:
        return 403, {"message": "not permitted"}
    eventlog.append("report", "INFO", "incident report written", str(target))
    return 200, {"message": "report written", "path": str(target)}
"""Camera / microphone in use: read the same record macOS uses for the green/orange dot next to the
clock (ControlCenter sensor-indicator log; no admin rights needed). It can name the app when macOS
logs it; otherwise XXX says "in use, app unknown" instead of guessing. Apple may change this record."""
from __future__ import annotations

import re
import subprocess

PREDICATE = 'subsystem == "com.apple.controlcenter" AND (category == "sensor-indicators" OR category == "video-effects")'
ACTIVE = re.compile(r"(?:Sorted active attributions from SystemStatus update|activeCameraAttributions):\s*\[(.*?)\]\)?\s*$")
BUNDLE = re.compile(r"\b(?:[a-z0-9-]+\.){2,}[A-Za-z0-9.-]+\b")


def parse(log_text: str) -> dict:
    """The newest indicator lines win: empty brackets mean nothing is using camera or mic now."""
    latest = None
    for line in log_text.splitlines():
        match = ACTIVE.search(line.strip())
        if match:
            latest = (line, match[1].strip())
    if not latest or not latest[1]:
        return {"active": False, "apps": [], "sensors": []}
    inside = latest[1]
    sensors = [s for s in ("camera", "microphone") if s in inside.lower() or (s == "microphone" and "mic" in inside.lower())]
    if "activeCameraAttributions" in latest[0] and "camera" not in sensors:
        sensors.append("camera")
    apps = sorted({b for b in BUNDLE.findall(inside) if not b.startswith("com.apple.controlcenter")})
    return {"active": True, "apps": apps, "sensors": sensors, "raw": inside[:200]}


def status(seconds: int = 90) -> dict:
    try:
        out = subprocess.run(["/usr/bin/log", "show", "--last", f"{seconds}s", "--style", "compact", "--info", "--predicate", PREDICATE],
                             capture_output=True, text=True, timeout=40).stdout
    except (OSError, subprocess.TimeoutExpired):
        return {"active": False, "apps": [], "sensors": [], "error": "not checked"}
    return parse(out)
```

</details>

### assistant · 2026-11-21T16:13:56.332Z

**أداة:** `Bash`

```json
{
 "command": "cd /Users/M7/XXX/src/xxx && cat breach.py projects.py hardening.py | cut -c1-170; sed -n 100,232p tools.py | cut -c1-150; cat rescue.py; grep -nE 'kev|KEV|registry|dedupe|closure|severity|confidence|epss|app_versions|CFBundle|apple|version' radar.py briefing.py whatif.py | cut -c1-170 | head -60"
}
```

### user · 2026-11-21T16:14:02.983Z

<details><summary>نتيجة أداة (22387 حرف)</summary>

```
"""Email leak monitoring (optional): with the owner's own Have I Been Pwned API key in the Keychain
(xxx-hibp_key, a paid HIBP subscription), XXX checks his e-mail addresses once a day. Without a key,
the free manual check on the official site (Accounts tab) is the way."""
from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request

from . import eventlog
from .accounts import keychain_secret
from .net import _ssl_context

API = "https://haveibeenpwned.com/api/v3/breachedaccount/{}?truncateResponse=true"


def _emails_path():
    return eventlog.default_path().parent / "emails.json"


def emails() -> list[str]:
    try:
        return [e for e in json.loads(_emails_path().read_text()) if isinstance(e, str)]
    except (OSError, ValueError):
        return []


def set_emails(body: dict) -> tuple[int, str]:
    raw = body.get("emails") if isinstance(body, dict) else None
    if not isinstance(raw, str):
        return 400, "bad request"
    found = sorted({e.strip().lower() for e in re.split(r"[\s,;]+", raw) if re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-z]{2,}", e.strip(), re.I)})[:10]
    _emails_path().write_text(json.dumps(found))
    return 200, "saved"


def check(opener=None) -> dict:
    key = [REDACTED]"hibp_key")
    if not key:
        [REDACTED] {"ready": False, "emails": emails(), "results": []}
    results = []
    for email in emails():
        request = urllib.request.Request(API.format(urllib.parse.quote(email)), headers={"hibp-api-key": key, "user-agent": "xxx-security-hub"})
        try:
            with (opener or urllib.request.urlopen)(request, timeout=20, context=_ssl_context()) as response:
                names = [b.get("Name", "") for b in json.loads(response.read())]
        except urllib.error.HTTPError as error:
            names = [] if error.code == 404 else None
        except (OSError, ValueError):
            names = None
        results.append({"email": email, "breaches": names})
        if names:
            eventlog.append("breach", "FOUND", f"{email} appears in {len(names)} known leaks: {', '.join(names[:5])}", "haveibeenpwned")
    return {"ready": True, "emails": emails(), "results": results}
"""My projects radar: known vulnerabilities in the packages the owner's own repos depend on.
Only package name, version and ecosystem leave the Mac (to the free OSV.dev database)."""
from __future__ import annotations

import json
import re
from pathlib import Path

from . import eventlog
from .net import post_json

OSV_BATCH = "https://api.osv.dev/v1/querybatch"
DEFAULT_REPOS = ["/Users/M7/XXX", "~/Documents/ai-trading-dashboard", "~/Documents/evx", "~/Documents/social-analyzer"]
PINNED = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)(?:\[[^\]]*\])?\s*==\s*([^\s;#,]+)")
NAME = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)")


def repos() -> list[Path]:
    """The folders to check: ~/.xxx/projects.json (a JSON list of paths) or the owner's known repos."""
    try:
        listed = json.loads((eventlog.default_path().parent / "projects.json").read_text())
    except (OSError, ValueError):
        listed = DEFAULT_REPOS
    paths = [Path(p).expanduser() for p in listed if isinstance(p, str)]
    return [p for p in paths if p.is_dir()]


def parse_requirements(text: str) -> tuple[list[dict], list[str]]:
    """Pinned packages (name==version) and the names that have no exact version."""
    pinned, loose = [], []
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or line.startswith(("-", "git+", "http")):
            continue
        match = PINNED.match(line)
        if match:
            pinned.append({"name": match[1], "version": match[2], "ecosystem": "PyPI"})
        elif NAME.match(line):
            loose.append(NAME.match(line)[1])
    return pinned, loose


def parse_package_lock(text: str) -> list[dict]:
    data = json.loads(text)
    found = {}
    for key, info in (data.get("packages") or {}).items():
        if key.startswith("node_modules/") and isinstance(info, dict) and info.get("version"):
            found[(key.rsplit("node_modules/", 1)[1], info["version"])] = True
    for name, info in (data.get("dependencies") or {}).items():  # lockfile v1
        if isinstance(info, dict) and info.get("version"):
            found[(name, info["version"])] = True
    return [{"name": n, "version": v, "ecosystem": "npm"} for n, v in sorted(found)]


def manifests(repo: Path) -> dict:
    """Packages from the repo's top-level requirements*.txt and package-lock.json."""
    pinned, loose, files = [], [], []
    for path in sorted(repo.glob("requirements*.txt")):
        p, l = parse_requirements(path.read_text(errors="replace"))
        pinned += p; loose += l; files.append(path.name)
    lock = repo / "package-lock.json"
    if lock.is_file():
        try:
            pinned += parse_package_lock(lock.read_text(errors="replace")); files.append(lock.name)
        except ValueError:
            files.append(lock.name + " (unreadable)")
    return {"files": files, "packages": pinned, "loose": sorted(set(loose))}


def match_osv(packages: list[dict], reply: dict) -> list[dict]:
    """Pair each package with the vulnerability IDs OSV returned for it (same order as the query)."""
    hits = []
    for package, result in zip(packages, reply.get("results", [])):
        ids = [v["id"] for v in (result or {}).get("vulns", []) if "id" in v]
        if ids:
            hits.append({**package, "ids": ids})
    return hits


def osv_query(packages: list[dict]) -> list[dict]:
    hits = []
    for start in range(0, len(packages), 500):
        chunk = packages[start:start + 500]
        queries = [{"package": {"name": p["name"], "ecosystem": p["ecosystem"]}, "version": p["version"]} for p in chunk]
        hits += match_osv(chunk, post_json(OSV_BATCH, {"queries": queries}))
    return hits


def scan_repos(query=osv_query) -> list[dict]:
    report = []
    for repo in repos():
        found = manifests(repo)
        row = {"repo": repo.name, "path": str(repo), "files": found["files"], "packages": len(found["packages"]),
               "loose": found["loose"], "vulns": [], "error": ""}
        try:
            row["vulns"] = query(found["packages"]) if found["packages"] else []
        except (OSError, ValueError) as error:
            row["error"] = type(error).__name__
        for hit in row["vulns"]:
            eventlog.append("deps", "FOUND", f"{hit['name']} {hit['version']}: {', '.join(hit['ids'][:3])}", repo.name)
        report.append(row)
    return report
"""Security Center: the Mac's real protection settings, read with macOS's own tools (no admin
needed), a score, and for each weak setting the exact System Settings page that fixes it.
XXX never changes these settings itself: macOS requires the owner's own click and password."""
from __future__ import annotations

import re
import subprocess

from . import tools

FIREWALL = "/usr/libexec/ApplicationFirewall/socketfilterfw"
# Only these pages can be opened (no free-form URLs from the page).
SETTINGS = {
    "firewall": "x-apple.systempreferences:com.apple.preference.security?Firewall",
    "filevault": "x-apple.systempreferences:com.apple.preference.security?FileVault",
    "gatekeeper": "x-apple.systempreferences:com.apple.preference.security?General",
    "updates": "x-apple.systempreferences:com.apple.preferences.softwareupdate",
    "lock": "x-apple.systempreferences:com.apple.Lock-Screen-Settings.extension",
    "sharing": "x-apple.systempreferences:com.apple.preferences.sharing",
    "wifi": "x-apple.systempreferences:com.apple.wifi-settings-extension",
    "location": "x-apple.systempreferences:com.apple.preference.security?Privacy_LocationServices",
    "timemachine": "x-apple.systempreferences:com.apple.Time-Machine-Settings.extension",
}
# Port a sharing service listens on -> check id.
SHARING_PORTS = {"22": "remote_login", "5900": "screen_sharing", "445": "file_sharing", "7000": "airplay", "3283": "remote_management"}


def _run(args: list[str], timeout: int = 20) -> str:
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return (result.stdout + result.stderr).strip()


def parse(outputs: dict, listening_ports: set[str]) -> list[dict]:
    """Turn raw command output into checks: id, state (ok / weak / unknown), detail, fix page."""
    def check(cid, ok, detail, fix, weight):
        return {"id": cid, "state": "unknown" if ok is None else "ok" if ok else "weak", "detail": detail[:160],
                "fix": fix, "weight": weight}

    o = outputs
    lock = re.search(r"screenLock delay is (\w+)(?: seconds)?", o.get("lock", ""))
    delay = None if not lock else 0 if lock[1] == "immediate" else int(lock[1]) if lock[1].isdigit() else None
    wifi = re.search(r"Current Network Information:.*?Security: ([^\n]+)", o.get("wifi", ""), re.S)
    wifi_sec = wifi[1].strip() if wifi else ""
    checks = [
        check("firewall", None if not o.get("firewall") else "enabled" in o["firewall"], o.get("firewall", ""), "firewall", 15),
        check("stealth", None if not o.get("stealth") else "on" in o["stealth"].split("mode is")[-1], o.get("stealth", ""), "firewall", 5),
        check("filevault", None if not o.get("filevault") else "On" in o["filevault"], o.get("filevault", ""), "filevault", 20),
        check("gatekeeper", None if not o.get("gatekeeper") else "enabled" in o["gatekeeper"], o.get("gatekeeper", ""), "gatekeeper", 15),
        check("sip", None if not o.get("sip") else "enabled" in o["sip"], o.get("sip", ""), "", 15),
        check("auto_update", None if not o.get("updates") else "turned on" in o["updates"], o.get("updates", ""), "updates", 10),
        check("screen_lock", None if delay is None else delay <= 300, f"{delay} s" if delay is not None else "", "lock", 5),
        check("wifi", None if not wifi_sec else not re.search(r"None|WEP|Open", wifi_sec, re.I), wifi_sec, "wifi", 10),
    ]
    for port, cid in SHARING_PORTS.items():
        on = port in listening_ports
        checks.append(check(cid, not on, "on" if on else "off", "sharing", 5 if cid != "remote_login" else 10))
    return checks


def score(checks: list[dict]) -> int:
    """0-100 over the checks we could read. Unknown ones do not count either way."""
    known = [c for c in checks if c["state"] != "unknown"]
    total = sum(c["weight"] for c in known)
    return round(100 * sum(c["weight"] for c in known if c["state"] == "ok") / total) if total else 0


def status() -> dict:
    outputs = {
        "firewall": _run([FIREWALL, "--getglobalstate"]),
        "stealth": _run([FIREWALL, "--getstealthmode"]),
        "filevault": _run(["fdesetup", "status"]),
        "gatekeeper": _run(["spctl", "--status"]),
        "sip": _run(["csrutil", "status"]),
        "updates": _run(["softwareupdate", "--schedule"]),
        "lock": _run(["sysadminctl", "-screenLock", "status"]),
        "wifi": _run(["system_profiler", "SPAirPortDataType"], timeout=30),
    }
    ports = {c["port"] for c in tools.connections()["listening"] if c.get("exposed")}
    checks = parse(outputs, ports)
    return {"score": score(checks), "checks": checks, "macos": _run(["sw_vers", "-productVersion"])}


def pending_updates() -> list[str]:
    """Software updates macOS says are waiting (slow: asks Apple's server)."""
    text = _run(["softwareupdate", "--list"], timeout=120)
    return [m.strip() for m in re.findall(r"\* Label: (.+)", text)]


def open_setting(key) -> tuple[int, str]:
    url = SETTINGS.get(key) if isinstance(key, str) else None
    if not url:
        return 400, "bad request"
    _run(["open", url])
    return 200, "opened"
    return rows[:limit]


def inventory() -> list[str]:
    """Names of the apps installed on this Mac plus "macOS", for matching threat lists to it."""
    names = {"macOS"}
    for folder in (Path("/Applications"), Path.home() / "Applications", Path("/System/Applications")):
        try:
            apps = list(folder.glob("*.app"))
        except OSError:
            continue
        for app in apps:
            try:
                with open(app / "Contents" / "Info.plist", "rb") as f:
                    info = plistlib.load(f)
                names.add(str(info.get("CFBundleName") or app.stem))
            except (OSError, ValueError, plistlib.InvalidFileException):
                names.add(app.stem)
    return sorted(names)


def system() -> dict:
    """Load, memory, disk and the programs using the most CPU right now."""
    total = int(_out(["sysctl", "-n", "hw.memsize"]).strip() or 0)
    vm = _out(["vm_stat"])
    page = int((re.search(r"page size of (\d+) bytes", vm) or [0, "4096"])[1])
    reclaimable = sum(int(n) for n in re.findall(r"Pages (?:free|inactive|speculative):\s+(\d+)", vm))
    disk = shutil.disk_usage(Path.home())
    smart = re.search(r"SMART Status:\s+(.+)", _out(["diskutil", "info", "/"]))
    return {
        "user": getpass.getuser(),
        "cpus": os.cpu_count(),
        "load": round(os.getloadavg()[0], 2),
        "memory": {"total": total, "available": reclaimable * page},
        "disk": {"total": disk.total, "free": disk.free, "smart": smart[1].strip() if smart else ""},
        "processes": parse_ps(_out(["ps", "-axo", "pid,user,pcpu,pmem,rss,comm", "-r"])),
    }


_disk_lock = threading.Lock()


def verify_disk() -> tuple[int, str]:
    """Ask macOS to check the startup volume's structure. Read-only: it reports, it does not repair."""
    if not _disk_lock.acquire(blocking=False):
        return 409, "disk check already running"

    def work():
        try:
            result = _run(["diskutil", "verifyVolume", "/"], timeout=900)
            lines = [line.strip() for line in (result.stdout + result.stderr).splitlines() if line.strip()] if result else []
            healthy = bool(result) and result.returncode == 0
            eventlog.append("disk", "INFO" if healthy else "TODO", (lines[-1] if lines else "disk check did not run")[:200], "/")
        finally:
            _disk_lock.release()

    eventlog.append("disk", "INFO", "disk check started", "/")
    threading.Thread(target=work, daemon=True).start()
    return 202, "disk check started"


def stop_process(pid) -> tuple[int, str]:
    current = connections()
    known = {p["pid"]: p["command"] for p in system()["processes"]}
    known.update({c["pid"]: c["command"] for c in current["listening"] + current["active"]})
    # Only a program shown in the connections or top-programs list can be stopped: never an arbitrary pid.
    if not isinstance(pid, int) or isinstance(pid, bool) or pid <= 1 or pid not in known:  # pid 1 is the system itself
        return 400, "unknown process"
    if pid in (os.getpid(), os.getppid()):
        return 400, "cannot stop XXX itself"
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError:
        return 403, "not permitted"
    eventlog.append("process", "BLOCKED", f"stopped {known[pid]} (pid {pid})")
    return 200, "stopped"


_SIGNER_CACHE: dict = {}


def signer(path: str) -> str:
    """Who signed a program: 'apple', a developer name, 'adhoc', or 'unsigned'.
    Cached by file change time: codesign is slow and the answer only changes when the file does."""
    try:
        stamp = Path(path).stat().st_mtime_ns
    except OSError:
        stamp = None
    if stamp is not None and _SIGNER_CACHE.get(path, (None,))[0] == stamp:
        return _SIGNER_CACHE[path][1]
    who = _signer(path)
    if stamp is not None:
        _SIGNER_CACHE[path] = (stamp, who)
    return who


def _signer(path: str) -> str:
    verify = _run(["codesign", "--verify", path])
    if not verify or verify.returncode != 0:
        return "unsigned"
    details = _run(["codesign", "-dv", "--verbose=2", path])
    text = details.stderr if details else ""
    authority = re.search(r"Authority=(.+)", text)
    if not authority:
        return "adhoc"
    return "apple" if authority[1] in ("Software Signing", "Apple Mac OS Application Signing") else authority[1]


def startup_items() -> list[dict]:
    """Programs set to start by themselves. Malware uses these folders to survive a restart."""
    items = []
    for folder in STARTUP_DIRS:
        for plist in sorted(Path(folder).expanduser().glob("*.plist")):
            try:
                with open(plist, "rb") as f:
                    data = plistlib.load(f)
            except Exception:
                items.append({"label": plist.stem, "program": "", "plist": str(plist), "signer": "unreadable", "flag": True})
                continue
            arguments = [str(a) for a in data.get("ProgramArguments") or []]
            program = str(data.get("Program") or (arguments or [""])[0])
            if Path(program).name in INTERPRETERS and len(arguments) > 1:
                # The interpreter is Apple's; what matters is the script it is told to run.
                program, who = " ".join(arguments[:4]), "runs a script"
            elif not program.startswith("/"):
                who = "relative path"
            elif not Path(program).exists():
                who = "missing"
            else:
                who = signer(program)
            items.append({"label": str(data.get("Label", plist.stem)), "program": program, "plist": str(plist),
                          "signer": who, "flag": who in ("unsigned", "adhoc", "missing", "unreadable")})
    return items
"""Data rescue, step 1 only: identify every disk and its health without touching it (read-only
diskutil). Recovery itself (imaging, TestDisk/PhotoRec) is guided, never automatic: writing to a
failing disk can destroy what is left."""
from __future__ import annotations

import plistlib
import subprocess


def _plist(args: list[str]) -> dict:
    try:
        out = subprocess.run(args, capture_output=True, timeout=30).stdout
        return plistlib.loads(out) if out else {}
    except (OSError, subprocess.TimeoutExpired, plistlib.InvalidFileException, ValueError):
        return {}


def describe(info: dict) -> dict:
    return {"id": info.get("DeviceIdentifier", ""), "name": str(info.get("MediaName", ""))[:80],
            "size": int(info.get("TotalSize") or info.get("Size") or 0), "internal": bool(info.get("Internal")),
            "removable": bool(info.get("Removable") or info.get("RemovableMedia")), "ssd": bool(info.get("SolidState")),
            "bus": str(info.get("BusProtocol", "")), "smart": str(info.get("SMARTStatus", "Not Supported")),
            "virtual": str(info.get("VirtualOrPhysical", "")) == "Virtual"}


def disks() -> list[dict]:
    listing = _plist(["diskutil", "list", "-plist", "physical"])
    rows = []
    for whole in listing.get("WholeDisks", []):
        info = describe(_plist(["diskutil", "info", "-plist", whole]))
        if info["id"]:
            info["state"] = "ok" if info["smart"] == "Verified" else "failing" if info["smart"] == "Failing" else "unknown"
            rows.append(info)
    return rows
whatif.py:11:    ("exploited_app", "kev_matches", 1),
whatif.py:22:def facts(state: dict, connections: dict, startup: list, kev: list, projects: list, repos: list,
whatif.py:32:        "kev_matches": sum(1 for k in kev if k.get("affects_you")),
briefing.py:3:briefing: when, situation (3), right move (3), confidence. Advice only: nothing here can act.
briefing.py:27:Schema: {"situation":[3 strings], "right_move":[3 strings], "confidence":"low|medium|high",
briefing.py:59:    for k in ctx.get("kev", []):
briefing.py:61:            found.append({"kind": "kev", "id": k["id"], "score": 90 if k.get("ransomware") else 80,
briefing.py:66:                          "title": f"{row['repo']}: {hit['name']} {hit['version']}", "detail": " ".join(hit["ids"][:5])})
briefing.py:83:    "kev_matches": "exploited-vulnerability (KEV) entries from the last year whose product name matches an installed app: {v}",
briefing.py:94:    if sig["kind"] == "kev":
briefing.py:95:        lines.append("an installed app name matches this vulnerability's product (name only, version not checked)")
briefing.py:99:        lines.append(f"the owner's repo pins this package version: {_clean(sig['title'], 120)}")
briefing.py:127:    confidence = obj.get("confidence") if obj.get("confidence") in ("low", "medium", "high") else "low"
briefing.py:129:            "confidence": confidence if used else "low", "evidence_used": used,
briefing.py:171:STATIC_CARD = {"kev": "exploited_app", "deps": "vuln_package", "canary": "decoy_touched", "news": "exploited_app"}
radar.py:20:KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
radar.py:58:    """True when the product name of a KEV entry appears in an installed app name.
radar.py:59:    shortcut: name match only, no version ranges; a hint to check, not a verdict."""
radar.py:66:def parse_kev(raw: bytes, limit: int = 15, apps: list[str] | None = None, since: str | None = None) -> list[dict]:
radar.py:166:        # Logs written before GUESS existed stored low-confidence guesses as FOUND.
radar.py:188:def _kev_enriched() -> list[dict]:
radar.py:189:    """KEV list + exploit probability (EPSS) + the installed app's version and whether it changed after the alert."""
radar.py:190:    items = parse_kev(fetch(KEV_URL), apps=tools.inventory())
radar.py:191:    scores = vulnintel.epss([i["id"] for i in items])
radar.py:192:    versions = vulnintel.app_versions()
radar.py:197:            app = next((n for n in versions if product and (product in _plain(n) or _plain(n) in product)), "")
radar.py:199:                version, mtime = versions[app]
radar.py:201:                item.update(app=app, app_version=version, app_updated=updated, updated_after=updated > item["date"])
radar.py:231:    return whatif.facts(state(), tools.connections(), _data("startup"), _data("kev"), _data("projects"),
radar.py:237:    for key, route in (("kev", "/api/kev"), ("news", "/api/news"), ("projects", "/api/projects")):
radar.py:239:    return {"events": eventlog.read(eventlog.default_path())[-500:], "kev": _data("kev"), "news": _data("news"),
radar.py:271:    "/api/kev": lambda: cached("kev", _kev_enriched),
radar.py:272:    "/api/apple": lambda: cached("apple", lambda: vulnintel.apple_check(hardening._run(["sw_vers", "-productVersion"])), ttl=21600),
```

</details>

### assistant · 2026-11-21T16:14:07.269Z

**أداة:** `Bash`

```json
{
 "command": "cd /Users/M7/XXX && sed -n 40,80p src/xxx/radar.py | cut -c1-170; sed -n 186,215p src/xxx/radar.py|cut -c1-170; grep -nE 'SpeechRecognition|speechSynthesis|ar-SA|lang' src/xxx/web/*.js | head; cat .github/workflows/tests.yml .gitlab-ci.yml; grep -c 'def test' tests/*.py; grep -n 'route\\|\"/api/' src/xxx/radar.py | grep -iE 'gl|firewall|cleanup|report|mfa|accounts|backup|process|injection|ai' | cut -c1-150; grep -rniE 'mfa|2fa|passkey|two.factor' src/xxx/*.py src/xxx/web/*.js | cut -c1-140 | head; grep -rniE 'lulu|glab|yara|osquery|restic|rclone' src/xxx/*.py | cut -c1-120 | head -20"
}
```

### user · 2026-11-21T16:14:12.138Z

<details><summary>نتيجة أداة (8542 حرف)</summary>

```
    "/app7.js": ("app7.js", "text/javascript; charset=utf-8"),
    "/app8.js": ("app8.js", "text/javascript; charset=utf-8"),
    "/app9.js": ("app9.js", "text/javascript; charset=utf-8"),
    "/i18n.js": ("i18n.js", "text/javascript; charset=utf-8"),
    "/i18n_en.js": ("i18n_en.js", "text/javascript; charset=utf-8"),
}
_cache: dict = {}
_scan_lock = threading.Lock()


GENERIC_PRODUCTS = {"multipleproducts", "multiple", "products", "unknown"}


def _plain(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def affects(entry: dict, apps: list[str]) -> bool:
    """True when the product name of a KEV entry appears in an installed app name.
    shortcut: name match only, no version ranges; a hint to check, not a verdict."""
    product = _plain(entry.get("product", ""))
    if len(product) < 4 or product in GENERIC_PRODUCTS:
        return False
    return any(product in _plain(app) or _plain(app) == product for app in apps)


def parse_kev(raw: bytes, limit: int = 15, apps: list[str] | None = None, since: str | None = None) -> list[dict]:
    entries = json.loads(raw)["vulnerabilities"]
    entries.sort(key=[REDACTED] v: v.get("dateAdded", ""), reverse=True)
    apps = apps or []
    # Everything that matches this Mac first (from the whole list), then the newest general ones.
    # Old entries are most likely patched already; only the last year counts as "may affect you".
    since = since if since is not None else time.strftime("%Y-%m-%d", time.gmtime(time.time() - 365 * 86400))
    mine = [v for v in entries if v.get("dateAdded", "") >= since and affects(v, apps)][:30]
    rest = [v for v in entries[:limit] if v not in mine]
    return [{
        "id": v.get("cveID", ""),
        "title": f"{v.get('vendorProject', '')} {v.get('product', '')}".strip(),
        "date": v.get("dateAdded", ""),
        "action": v.get("requiredAction", ""),
        "ransomware": v.get("knownRansomwareCampaignUse") == "Known",


def _kev_enriched() -> list[dict]:
    """KEV list + exploit probability (EPSS) + the installed app's version and whether it changed after the alert."""
    items = parse_kev(fetch(KEV_URL), apps=tools.inventory())
    scores = vulnintel.epss([i["id"] for i in items])
    versions = vulnintel.app_versions()
    for item in items:
        item.update(scores.get(item["id"], {}))
        if item["affects_you"]:
            product = _plain(item["title"].split(" ", 1)[-1])
            app = next((n for n in versions if product and (product in _plain(n) or _plain(n) in product)), "")
            if app:
                version, mtime = versions[app]
                updated = time.strftime("%Y-%m-%d", time.localtime(mtime))
                item.update(app=app, app_version=version, app_updated=updated, updated_after=updated > item["date"])
    return items


def _clear_storage():
    for key in ("storage", "accounts", "drive"):
        _cache.pop(key, None)


accounts.ON_CONNECTED = _clear_storage


def _data_or_empty(key: str):
    return (_cache.get(key) or {}).get("value") or {"items": {"devices": []}, "error": None, "fetched": None}

src/xxx/web/app5.js:44:  if (!changed("accounts", [list, lang])) return;
src/xxx/web/app5.js:59:  if (c && changed("cleanup", [c, lang])) show("cleanup", table(["h_folder", "h_size", "h_action"], c.map(r => {
src/xxx/web/app5.js:63:  if (Array.isArray(w) && changed("workflows", [w, lang])) show("workflows", table(["h_repo", "h_wf", "h_unpinned"], w.map(r => [
src/xxx/web/app5.js:68:  if (!Array.isArray(d) || !changed("rescue", [d, lang])) return;
src/xxx/web/app5.js:76:  if (!s || !changed("sensors", [s, lang])) return;
src/xxx/web/app5.js:83:  if (!a || !changed("agents", [a, lang])) return;
src/xxx/web/app5.js:97:  if (!s || !changed("shield", [s, lang])) return;
src/xxx/web/app5.js:105:  if (!b || !changed("breach", [b, lang])) return;
src/xxx/web/app5.js:114:  if (!u || !changed("update", [u, lang])) return;
src/xxx/web/app5.js:129:  if (!b || !changed("browsers", [b, lang])) return;
name: tests
on: [push, pull_request]
permissions:
  contents: read
jobs:
  test:
    runs-on: macos-latest
    strategy:
      matrix:
        python: ["3.9", "3.11"]
    steps:
      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262  # v4
      - uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065  # v5
        with:
          python-version: ${{ matrix.python }}
      - run: python -m unittest discover -s tests
tests:
  image: python:3.11
  script:
    - python -m unittest discover -s tests
  allow_failure: true  # several checks need macOS tools; the GitHub macOS job is the main gate
tests/test_phish.py:6
tests/test_storage_tools.py:4
tests/test_xxx.py:27
tests/test_v3.py:49
290:    "/api/security": lambda: cached("security", lambda: {**hardening.status(), "backup": care.backup_status()}, ttl=120),
293:    "/api/aiscan": lambda: cached("aiscan", care.scan_ai, ttl=600),
297:    "/api/storage": lambda: cached("storage", storage.accounts, ttl=300),
301:    "/api/accounts": lambda: swr("accounts", accounts.status, ttl=60),
302:    "/api/cleanup": lambda: cached("cleanup", guard.cleanup, ttl=600),
303:    "/api/workflows": lambda: guard.workflows_report(projects.repos()),
309:    "/api/sync-pairs": syncpairs.pairs,
317:    "/api/stop": lambda body: tools.stop_process(body.get("pid")),
326:    "/api/sync-pairs": syncpairs.change,
329:    "/api/report": report.write,
338:    "/api/connect": lambda body: (_clear_storage(), accounts.connect(body))[1],
339:    "/api/disconnect": lambda body: accounts.disconnect(body),
340:    "/api/account-page": accounts.open_page,
341:    "/api/account-tick": accounts.tick,
350:    "/api/shield": lambda body: (_cache.pop("shield", None), webshield.toggle(body))[1],
351:    "/api/emails": lambda body: (_cache.pop("breach", None), breach.set_emails(body))[1],
src/xxx/accounts.py:6:  security page (2FA, login activity) and keeps the owner's checklist ticks.
src/xxx/accounts.py:46:CHECK_ITEMS = ["2fa", "recovery", "sessions", "apps"]
src/xxx/web/app5.js:32:    ["2fa", "recovery", "sessions", "apps"].forEach(item => {
src/xxx/web/i18n_en.js:82:    "wi_account_takeover_p": "Passkeys or MFA • A safe recovery email • A different password per account",
src/xxx/web/i18n_en.js:283:    "chk_2fa": "Two-step verification on",
src/xxx/web/i18n.js:84:    "wi_account_takeover_p": "مفاتيح مرور (passkeys) أو MFA • إيميل استرجاع سليم • ك
src/xxx/web/i18n.js:285:    "chk_2fa": "التحقق بخطوتين شغال",
src/xxx/agents.py:21:                       ["repoguard.py: GitHub/GitLab", "historyscan.py: Gitleaks", "storage.py: rcl
src/xxx/accounts.py:2:- Storage (rclone): one click opens the provider's consent page in the browser; rclone keeps the t
src/xxx/accounts.py:19:# id, name, group, how to connect, official sign-in page, official security page, rclone backend
src/xxx/accounts.py:21:    ("gdrive", "Google Drive", "storage", "rclone", "https://drive.google.com", "https://myaccoun
src/xxx/accounts.py:22:    ("onedrive", "OneDrive", "storage", "rclone", "https://onedrive.live.com", "https://account.m
src/xxx/accounts.py:23:    ("dropbox", "Dropbox", "storage", "rclone", "https://www.dropbox.com/login", "https://www.dro
src/xxx/accounts.py:24:    ("box", "Box", "storage", "rclone", "https://account.box.com/login", "https://app.box.com/acc
src/xxx/accounts.py:25:    ("pcloud", "pCloud", "storage", "rclone", "https://my.pcloud.com", "https://my.pcloud.com/#pa
src/xxx/accounts.py:26:    ("mega", "MEGA", "storage", "rclone-wizard", "https://mega.nz/login", "https://mega.nz/fm/acc
src/xxx/accounts.py:27:    ("koofr", "Koofr", "storage", "rclone-wizard", "https://app.koofr.net", "https://app.koofr.ne
src/xxx/accounts.py:28:    ("proton", "Proton Drive", "storage", "rclone-wizard", "https://drive.proton.me", "https://ac
src/xxx/accounts.py:81:    if storage.rclone_path():
src/xxx/accounts.py:82:        code, out = storage._rclone("listremotes", "--long")
src/xxx/accounts.py:85:            if name.strip() and has_token(storage.rclone_path(), name.strip()):
src/xxx/accounts.py:93:        if how.startswith("rclone"):
src/xxx/accounts.py:104:                     "connected": connected, "detail": detail, "ticks": ticks.get(sid, {}), "rcl
src/xxx/accounts.py:122:    if how.startswith("rclone"):
src/xxx/accounts.py:123:        exe = storage.rclone_path()
src/xxx/accounts.py:125:            storage.install()  # first connect installs rclone (official, checksum-verified)
src/xxx/accounts.py:126:            exe = storage.rclone_path()
```

</details>

### assistant · 2026-11-21T16:14:24.714Z

**أداة:** `Bash`

```json
{
 "command": "cd /Users/M7/XXX && grep -n 'Speech\\|speak\\|recogn' src/xxx/web/*.js | cut -c1-150 | head; grep -rn 'secret-scanning\\|secret_scanning\\|code-scanning\\|protected\\b' src/xxx/repoguard.py | head -3; grep -n 'scan_repos\\|projects\\.' src/xxx/autopilot.py src/xxx/watch.py | head; grep -rn 'rdap\\|owner_of' src/xxx/radar.py src/xxx/web/*.js | head -3; grep -rn 'state.*closed\\|resolved\\|dismiss\\|ack' src/xxx/eventlog.py src/xxx/radar.py | head -5; ls src/xxx/web; which glab gh rclone clamscan lulu 2>&1 | head; grep -n 'explain\\|_p\"\\|tip' src/xxx/web/i18n_en.js | wc -l; git log --oneline | head -3; python3 -m unittest discover -s tests 2>&1 | tail -3"
}
```

### user · 2026-11-21T16:15:38.223Z

<details><summary>نتيجة أداة (2530 حرف)</summary>

```
src/xxx/web/app.js:9:let busy = false, speakOn = false;
src/xxx/web/app.js:209:  $("speak").textContent = t(speakOn ? "speak_on" : "speak_off");
src/xxx/web/app.js:210:  $("speak").className = speakOn ? "active" : "";
src/xxx/web/app.js:211:  // Speech recognition exists in browsers but not inside the app window; there the dictation key does the job.
src/xxx/web/app.js:212:  $("mic").hidden = !(window.SpeechRecognition || window.webkitSpeechRecognition || nativeVoice());
src/xxx/web/app.js:218:function speak(text) {
src/xxx/web/app.js:221:  const utterance = new SpeechSynthesisUtterance(text);
src/xxx/web/app.js:223:  speechSynthesis.speak(utterance);
src/xxx/web/app.js:242:  if (reply && speakOn) speak(reply);
src/xxx/web/app.js:245:// In the app the Mac's own speech recognition does the listening; in a browser, the browser's.
src/xxx/repoguard.py:1:"""Repo guard: read-only checks of the owner's GitHub repos (public or private, main protected).
src/xxx/repoguard.py:61:    return {200: "protected", 404: "not protected", 403: "not verified (plan limit)"}.get(status, "not verified")
src/xxx/radar.py:23:    "The Hacker News": "https://feeds.feedburner.com/TheHackersNews",
src/xxx/radar.py:113:    """Answer at once with the last copy (even if old) and refresh it in the background."""
src/xxx/radar.py:244:    """Start one background scan. Findings reach the page through the event log."""
src/xxx/radar.py:284:    # Package lists go to osv.dev; GitHub checks use the owner's gh sign-in, read-only.
src/xxx/radar.py:290:    "/api/security": lambda: cached("security", lambda: {**hardening.status(), "backup": care.backup_status()}, ttl=120),
app.css
app.js
app2.js
app3.js
app4.js
app5.js
app6.js
app7.js
app8.js
app9.js
i18n.js
i18n_en.js
index.html
glab not found
/Users/M7/.local/bin/gh
rclone not found
clamscan not found
lulu not found
      13
0e3311d 1.5.0: phishing check for links/messages, router UPnP/Telnet/HTTP check, lock mark on encrypted files
dcf6c5f 1.4.0: share links with expiry, encrypted vault, placement rules by file type
dcba688 1.3.0 (in-app update): drag & drop upload (streamed, progress), deep drive index (stats by type per account, largest files, duplicates across accounts with delete), best place to store, update status every minute + check now
A leaked key stays leaked after you delete the line: rotate it at the provider.
log intact: /var/folders/17/rlyzwhrj4tdg8clx0k0m8bgh0000gp/T/tmpoqr2lflk/home/events.jsonl
0 found in 1 files; not scanned: 0 large, 0 binary, 0 unreadable
```

</details>

### assistant · 2026-11-21T16:15:40.700Z

**أداة:** `Bash`

```json
{
 "command": "cd /Users/M7/XXX && python3 -m unittest discover -s tests 2>&1 | grep -E '^Ran|^OK|FAILED'; grep -n 'speak_on\\|nativeVoice' src/xxx/web/app.js | head -4; grep -n 'sed\\|\"/api/ip\\|whois' src/xxx/radar.py | head -3"
}
```

### user · 2026-11-21T16:16:31.710Z

**نتيجة أداة:**
```
Ran 87 tests in 44.962s
OK
209:  $("speak").textContent = t(speakOn ? "speak_on" : "speak_off");
212:  $("mic").hidden = !(window.SpeechRecognition || window.webkitSpeechRecognition || nativeVoice());
246:const nativeVoice = () => window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.voice;
254:  if (nativeVoice()) {
279:    # Checking each program's signature is slow, so the list is reused for a few minutes.
```

### assistant · 2026-11-21T16:16:53.678Z

**أداة:** `SubagentHandback`

```json
{
 "message": "Audit of /Users/M7/XXX. Nothing was edited. `python3 -m unittest discover -s tests` ran 87 tests and all passed. `glab`, `rclone`, `clamscan` and `lulu` are not on PATH in my shell. `gh` is at ~/.local/bin/gh. ClamAV is in ~/.xxx/clamav per the catalog, and I did not check for it. Roughly: 18 rows BUILT, 14 PARTIAL, 1 NOT BUILT.\n\nrow | status | evidence | missing | buildable\n2 | BUILT | vulnintel.py epss/parse_epss; radar.py _kev_enriched merges the score | none | yes, done\n4 | BUILT | guard.py odd_processes/process_signals; autopilot _process_check; tools.py parse_ps, stop_process (own pids only), signer | osquery not needed | yes, done\n6 | BUILT | autopilot.py start/tick (minute, quarter, hour and day tiers); watch.py set_agent LaunchAgent | none | yes, done\n7 | BUILT | guard.py ransomware_signals (RANSOM_EXT, RANSOM_NOTE, 300 files/min); autopilot _ransom_check; decoys in watch.py | no kernel-level hook | yes (mdfind, no admin)\n15 | BUILT | tools.py system (SMART), verify_disk; rescue.py disks | none | yes, done\n19 | PARTIAL | guard.py dns_servers/parse_dns; autopilot _dns_check flags a changed resolver | no outbound-domain log. report.py only does RDAP on live IPs | partly: per-domain needs packet capture or a DNS proxy. Reverse-DNS of lsof peers is doable\n23 | NOT BUILT | no grep hit for lulu or firewall prompts. hardening.py only reads the macOS firewall state | per-app outbound prompts | no: needs a network extension (LuLu, admin). Could only list apps with live connections via tools.connections\n26 | PARTIAL | repoguard.py (GitHub and GitLab visibility); accounts.py status | no email protection. GitLab limited to public/private | partly: email has no read API. GitHub is done\n27 | PARTIAL | accounts.py CHECK_ITEMS has \"2fa\" tick; app5.js checklist | manual ticks only, no reminder or passkey status | yes: periodic reminder from the tick timestamps. Real 2FA state is not readable from outside\n29 | PARTIAL | breach.py check needs the owner's paid HIBP key; care.py pwned_count (free range API, k-anonymity) | free per-email lookup does not exist | no for email without the paid key. Password check is already done\n41 | PARTIAL | repoguard.py _github_row: visibility, branch protection, Dependabot alerts, deploy_keys, collaborators, workflow_token | secret-scanning alerts count | yes: gh api repos/X/secret-scanning/alerts, read-only (403 means \"not verified\")\n42 | PARTIAL | repoguard.py gitlab_repos/gitlab_visibility (unauthenticated GET). Protection column says \"not checked (needs GitLab sign-in)\" | protected branches, mirror SHA check | partly: needs a GitLab token or glab login. glab is not installed. Public projects only otherwise\n45 | BUILT | guard.py unpinned_actions/workflows_report; /api/workflows; repoguard.py workflow_token | workflow-level `permissions:` key not checked in YAML | yes, small add\n47 | PARTIAL | watch.py plant/check_canaries (decoys); autopilot _decoy_check | cannot detect actual copying, which the catalog admits | no beyond decoys\n55 | PARTIAL | care.py parse_backup/backup_status (tmutil); autopilot _backup_check | no tested restore, no 3-2-1 view | partly: can mount and checksum a sample from the TM snapshot. 3-2-1 could join the rclone/storage.py state\n58 | BUILT | see row 2 | none | yes, done\n60 | BUILT | vulnintel.py parse_apple/macos_status/apple_check; autopilot _apple_check; /api/apple | HTML-scrape fragility only | yes, done\n63 | PARTIAL | eventlog.py hash-chained log with status. Radar feeds (radar.py) | no dedupe by CVE, no severity+confidence record, no open/closed tracking | yes, a JSON state file\n68 | PARTIAL | radar.py affects() is name-only (its comment says so); _kev_enriched adds app_version and updated_after; vulnintel.py app_versions reads CFBundleShortVersionString | KEV does not carry fixed-version ranges, so the version is shown but not compared | partly: CISA data has no ranges. Needs NVD or OSV CPE data (free, no key but slow)\n69 | PARTIAL | projects.py scan_repos (OSV), default repos include ai-trading-dashboard; briefing.py; whatif.py | scan_repos is not in any autopilot tier, so no push alert | yes: add a \"day\" check to autopilot.CHECKS\n76 | BUILT | care.py scan_ai/INJECTION/mcp_servers; /api/aiscan; autopilot \"architect\" agent | no diff against a saved MCP baseline, so \"new server\" alerts are missing | yes, small add\n77 | PARTIAL | only care.py scan_ai on existing files | no pre-install vetting of a skill or MCP before install | yes: reuse INJECTION on a folder the owner points at\n87 | PARTIAL | app.js speak() with SpeechSynthesisUtterance, SpeechRecognition, nativeVoice() WKWebView bridge | Arabic locale/voice (ar-SA) not confirmed. I did not grep the lang value or test spoken replies | yes: stdlib + the OS voices, test only\n100 | BUILT | care.py disks (free_pct); tools.py system; autopilot _disk_check flags under 20% | none | yes, done\n101 | BUILT | guard.py cleanup/reveal (Finder opens, owner deletes); care.py biggest | \"unneeded apps\" list not found | yes: apps by last-used (mdls kMDItemLastUsedDate)\n102 | BUILT | hardening.py pending_updates; updater.py; autopilot _update_check/_apple_check; open_setting(\"updates\") | install is by the owner's click in System Settings (by design) | yes\n103 | PARTIAL | tools.py verify_disk (read-only) | no repair, cache refresh or maintenance actions | partly: user-level cache clears and Spotlight reindex need no admin. First Aid repair needs admin or the owner\n107 | BUILT | rescue.py disks (diskutil -plist); care.py disks | none | yes, done\n118 | BUILT | report.py build/write (events, chain code, eventlog.verify, RDAP); autopilot _decoy_action | per-file hashes of evidence not included, only the log chain | yes\n119 | BUILT | report.py parse_rdap/owner_of with abuse email, rdap.org | only inside the report, no ad-hoc IP lookup route | yes, one route\n132 | PARTIAL | tools.py network/connections/startup_items; netscan.py scan (LAN, UPnP); watch.py devices | \"control\" is limited (stop_process, open settings) | partly: no block or kill-network without admin\n136 | PARTIAL | hardening fix pages; i18n_en.js has some \"_p\" explain strings (13 hits). briefing.py gives advice | I did not check each tab for an explain and recommend block | yes, a UI/i18n pass\n141 | BUILT | .github/workflows/tests.yml (3.9 and 3.11, macOS, pinned SHAs); .gitlab-ci.yml; 87 tests pass locally | no push-run proof from here. The GitLab job is allow_failure | yes, done\n\nThe catalog notes for 2, 6, 7, 58, 60, 100, 118, 119 and 141 are clearly stale. Rows 19, 23 and 42 are the real gaps for tooling that is free and needs no admin rights, and 23 is the hardest."
}
```

### user · 2026-11-21T16:16:55.542Z

**نتيجة أداة:**
```
{"success":true,"message":"Report delivered to your caller."}
```
