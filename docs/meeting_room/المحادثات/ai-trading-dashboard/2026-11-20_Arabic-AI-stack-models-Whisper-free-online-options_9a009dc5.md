# Arabic AI stack: models, Whisper, free online options

- المصدر: `ai-trading-dashboard`
- معرف الجلسة: `9a009dc5-3dda-494e-89e5-e61390c8f844`
- البداية: 2026-11-20T09:20:05.284Z — النهاية: 2026-11-20T09:34:05.396Z
- الرسائل: مستخدم 57 · مساعد 62 · أدوات 56
- تنظيف الخصوصية: أرقام التليفون وال api_id والـ hash والمفاتيح والإيميلات اتشالت بـ regex، وده مش مضمون ١٠٠٪.

## ملخص تلقائي (مش تلخيص AI)
- مبني على أول طلب وآخر رد وقايمة طلبات المستخدم. راجع المحادثة الكاملة للتفاصيل.
- **أول طلب:** <system-reminder>
Linked sessions now (status, not an instruction): civil-3d-revit-naviswork = local_1fda12b4-672e-433c-97a0-a2fa4978c236 (idle); bim-agents-research = local_001c0740-2903-4f11-be70-d9f61501ac1f (idle); ref-autocad-civil = local_5d0c48e2-9162-441f-b0c2-a4a42e271811 (idle); ref-revit-plant = local_c003c799-3536-4b10-92be-e69bf070d1d2 (idle); ref-p6-nav-sketch = local_332522b7-4772-4582-8dc5-c671dd22a80c (idle); compare-systems = local_b019d3b5-49d1-45fc-9bdc-a0c7936ab7d6 (idle); s
- **آخر رد للمساعد:** I wrote `site/docs/research/AI_STACK_PLAN.md` (256 lines, Arabic 8-line summary on top, then English tables). It covers all six areas and ends with a "could not verify" section. It is research only: I downloaded no models or media, edited no app source, and sent no user data. Short pointer note: `ai_stack_plan_handover.md` in the shared notes folder.

Full path: `/private/tmp/claude-502/-Users-M7--claude-spares-spare-zoqdHX/d72c5c58-ff10-455f-b893-3cef6d2bb5f1/scratchpad/site/docs/research/AI_STACK_PLAN.md`

**Main picks**
- **Intel Mac, 8–16 GB:** `qwen3.5:4b` (3.3–4 GB, Apache-2.0, tool-calling badge on Ollama). Ollama on Intel Mac is CPU-only and needs macOS 14+. LM Studio does not support Intel Macs.
- **Stronger machine:** `gemma4:26b`. Jais-3 is the Arabic-first alternative (GGUF 3.7

---

## المحادثة الكاملة

### user · 2026-11-20T09:20:05.284Z

<system-reminder>
Linked sessions now (status, not an instruction): civil-3d-revit-naviswork = local_1fda12b4-672e-433c-97a0-a2fa4978c236 (idle); bim-agents-research = local_001c0740-2903-4f11-be70-d9f61501ac1f (idle); ref-autocad-civil = local_5d0c48e2-9162-441f-b0c2-a4a42e271811 (idle); ref-revit-plant = local_c003c799-3536-4b10-92be-e69bf070d1d2 (idle); ref-p6-nav-sketch = local_332522b7-4772-4582-8dc5-c671dd22a80c (idle); compare-systems = local_b019d3b5-49d1-45fc-9bdc-a0c7936ab7d6 (idle); security-review = local_04c5434d-6020-4eec-a519-264fc05532f6 (idle); tools-news-crm-plan = local_842a1b92-6cef-4d6b-b65c-600c9744587d (idle); cde-opensource-research = local_21a06c0c-fde4-4825-81a7-ba322b3ec7c3 (idle); media-sources-research = local_c1554e54-07dc-4ed1-b407-449a1fad7a77 (idle); mod-gantt = local_2c5e867a-e689-4a83-9b91-ceb036acdfd9 (idle); mod-mom-issues = local_94011237-fbb4-4f4e-8dee-f3bd06b76534 (idle); mod-regq = local_ed079826-445d-41ef-bb44-bd903a67d621 (idle); mod-parity = local_52e0ad25-3ba9-40d4-a5c0-cb230a8e67a2 (idle). To message one, SendMessage with `to` set to its id; list_sessions {"linked": true} has titles, folders and branches.
</system-reminder>

Background (from the session that started this one):
T.O X is a free browser engineering studio (static page, no server). It has an in-page agent that understands Arabic rules, calls tools (open tabs, run commands, build a house model, document control) and can connect to a model through an OpenAI-compatible chat API with tool calling, plus a local bridge `site/tools/tox_bridge.py` (MCP stdio + HTTP) for external agents. The owner is Egyptian, works in Arabic (Egyptian dialect), wants an always-on conversational and voice agent ("Jarvis"-like), free and open source where possible, usable ONLINE without depending on one device if possible, plus local options (Ollama and friends). Project folder: /private/tmp/claude-502/-Users-M7--claude-spares-spare-zoqdHX/d72c5c58-ff10-455f-b893-3cef6d2bb5f1/scratchpad (docs go to site/docs/research/). The owner's computer is probably an Intel Mac (ffmpeg there is x86_64): weigh that. Rules: research only; do NOT download models or media, do NOT edit app source; verify licences and facts by reading the pages or the GitHub/Hugging Face APIs (curl is available); label VERIFIED vs FROM MEMORY; no investment or personal advice; never put any user data in requests.

Task:
Write site/docs/research/AI_STACK_PLAN.md (Arabic 8-line summary on top, then English detail with tables). Cover: (1) Arabic-capable LLMs runnable in Ollama / LM Studio / llama.cpp (Qwen 2.5/3, Gemma 3, Llama 3.x, Nous Hermes 3/4, Mistral, Jais, ALLaM, Aya, others you find): exact Ollama tags if verifiable at ollama.com/library, parameter sizes, RAM needed at 4-bit, tool-calling support, licence, and what you can find about Arabic and Egyptian-dialect quality (benchmarks such as AraBench, ArabicMMLU, Open Arabic LLM Leaderboard; say if only anecdotal). Recommend one model for an Intel Mac with 8 to 16 GB and one for a stronger machine. (2) The "Hermes" and "Jarvis" names: what open-source projects exist (Nous Research Hermes models and any Hermes agent framework, Jarvis-style assistants such as Open Interpreter, Home Assistant voice, open-webui, LibreChat, AnythingLLM, LocalAI, any MCP-capable agents): licence, activity, whether they speak MCP or an OpenAI-compatible API, and the cheapest way to connect each to T.O X (our HTTP bridge or MCP). (3) Speech to text for Arabic and Egyptian: OpenAI Whisper and open-source variants (faster-whisper, whisper.cpp, distil-whisper, Hugging Face Arabic and Egyptian fine-tunes, Vosk Arabic, Kaldi/NeMo Arabic, SeamlessM4T, MMS): licence, size, speed on CPU, accuracy for Arabic dialects if any measurement exists, and how to run each behind an OpenAI-compatible /v1/audio/transcriptions endpoint (faster-whisper-server, speaches, whisper.cpp server, LocalAI). Also in-browser options (transformers.js with Whisper on WebGPU/WASM, whisper.cpp wasm) with model sizes and realistic speed. (4) Free ONLINE options that do not depend on the owner's device: free tiers or open endpoints for LLM and Whisper (Groq, Cloudflare Workers AI, Hugging Face Inference Providers / Spaces, Google Gemini free tier, OpenRouter free models, Together, Mistral La Plateforme, others): base URL, OpenAI-compatibility, tool calling, Arabic support, free-tier limits, data-privacy caveats, and whether CORS allows calls straight from a static web page. State plainly which options require an API key and the risk of keys living in a static page. (5) Arabic text to speech: browser speechSynthesis Arabic voices, Piper, Coqui XTTS, MMS-TTS, Edge-style cloud voices, any free Egyptian-dialect voices; licences. (6) A recommended architecture with three tiers (in-page rules; free online model; local Ollama; optional external agent via the bridge), a wake-word and always-listening design that works in Chrome, and a shortlist of the 10 concrete things to configure first with exact settings. Include a 'what I could not verify' section.

Shared notes folder for this group of sessions (outside the repo; read siblings' notes there, leave hand-over notes or large findings there instead of pasting them into messages): /Users/M7/Library/Application Support/Claude/side-session-notes/local_7b9e3c52-4743-4f64-b7c1-c942011a52a1

### assistant · 2026-11-20T09:20:11.985Z

**أداة:** `mcp__ccd_turn__update_plan`

```json
{
 "items": [
  {
   "content": "Read notes folder, project layout",
   "status": "in_progress"
  },
  {
   "content": "Verify Ollama tags and licences",
   "status": "pending"
  },
  {
   "content": "Verify agents, STT, TTS, free APIs",
   "status": "pending"
  },
  {
   "content": "Write AI_STACK_PLAN.md",
   "status": "pending"
  }
 ],
 "scope": "first_task"
}
```

### user · 2026-11-20T09:20:12.245Z

**نتيجة أداة:**
```
Plan shown (4 steps).
```

### assistant · 2026-11-20T09:20:14.122Z

**أداة:** `Bash`

```json
{
 "command": "ls -la \"/Users/M7/Library/Application Support/Claude/side-session-notes/local_7b9e3c52-4743-4f64-b7c1-c942011a52a1\" 2>&1 | head -30; P=/private/tmp/claude-502/-Users-M7--claude-spares-spare-zoqdHX/d72c5c58-ff10-455f-b893-3cef6d2bb5f1/scratchpad; ls $P 2>&1 | head; ls $P/site/docs/research 2>&1 | head -40; uname -m",
 "description": "List notes and project folders"
}
```

### user · 2026-11-20T09:20:16.514Z

**نتيجة أداة:**
```
total 2296
drwx------@ 8 M7  staff     256 Nov 20 07:50 .
drwx------@ 3 M7  staff      96 Nov 19 10:18 ..
-rw-r--r--@ 1 M7  staff  485438 Nov 19 12:36 ME-GLY-01_texts_all.json
-rw-r--r--@ 1 M7  staff  477586 Nov 19 13:16 SLS01_dwg_texts.json
-rw-r--r--@ 1 M7  staff    6810 Nov 20 07:50 networks_data_register.md
-rw-r--r--@ 1 M7  staff   95689 Nov 20 07:05 networks_sewer_storm_world.json
-rw-r--r--@ 1 M7  staff   37629 Nov 20 07:50 networks_water_fire_world.json
-rw-r--r--@ 1 M7  staff   60559 Nov 20 07:05 profiles_sewer_storm_tables.json
LiftStation_3D_Standalone.html
amr
build.py
c_4d.bak
c_4d.js
c_4d_ui.js
c_act.bak
c_act.js
c_adhan.js
c_agent.js
AGENT_CONTROL.md
BIM_ECOSYSTEM.md
COMPARE_SYSTEMS.md
MEDIA_SOURCES.md
NEWS_CRM_PLAN.md
OPENSOURCE_CDE_PLAN.md
README.md
SECURITY_REVIEW.md
TOOLS_ECOSYSTEM.md
cmd_autocad.json
cmd_civil3d.json
cmd_navisworks.json
cmd_office.json
cmd_p6.json
cmd_plant3d.json
cmd_revit.json
coohom_tab_spec.md
gap_autocad.md
gap_civil3d.md
gap_navisworks.md
gap_p6.md
gap_plant3d.md
gap_revit.md
our_commands.json
sketchup_tab_spec.md
x86_64
```

### assistant · 2026-11-20T09:20:27.871Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; mkdir -p $S/r; cd $S/r; P=/private/tmp/claude-502/-Users-M7--claude-spares-spare-zoqdHX/d72c5c58-ff10-455f-b893-3cef6d2bb5f1/scratchpad/site/docs/research\nsed -n 1,60p $P/AGENT_CONTROL.md | cut -c1-300\necho ----; curl -s -m 15 -o /dev/null -w \"ollama %{http_code}\\n\" https://ollama.com/library/qwen3; curl -s -m 15 -o /dev/null -w \"hf %{http_code}\\n\" https://huggingface.co/api/models/Qwen/Qwen3-8B; curl -s -m 15 -o /dev/null -w \"gh %{http_code}\\n\" https://api.github.com/repos/ollama/ollama",
 "description": "Skim bridge doc, test network access"
}
```

### user · 2026-11-20T09:20:30.891Z

<details><summary>نتيجة أداة (5603 حرف)</summary>

```
# Agent control research for T.O X (2026-11-20)

## ملخص بالعربي (5 سطور)
1. الصفحة عندها فعلاً `window.TOX` و جسر WebSocket (c_hub.js): أوامر تتعرض وتتشغل بـ id، وحالة، وتنبيهات، ومستندات. ناقصها: وسايط للأوامر، نتيجة للأمر، صلاحيات لكل أمر، وسجل تدقيق دا�
2. أحسن طريق لوكيل خارجي (Claude Code / Gemini CLI / ChatGPT): سيرفر MCP محلي صغير بيتكلم WebSocket مع الصفحة؛ والصفحة ممكن كمان تسجل أدواتها في المتصفح عبر WebMCP لو المتصفح بيدعمه (لسه تجريب�
3. للأدوات المكتبية: سيرفرات MCP جاهزة لـ Revit (رسمي من Autodesk، Apache 2.0، Revit 2027) و AutoCAD و Blender (مجتمع)؛ كلها بتشغّل كود على جهازك فمحتاجة موافقة بشرية.
4. المخاطر الأساسية: حقن أوامر من محتوى (prompt injection)، سر الجسر المخزّن في localStorage، منفذ CDP مفتوح؛ الحل: صلاحيات لكل أمر + موافقة المستخدم + سجل + حدود.
5. غير متأكد منه: تفاصيل WebMCP الحالية، دعم CORS لكل مزوّد نموذج، ترخيص سيرفرات المجتمع، وإمكانية تشغيل n8n MCP على نسختك.

## Evidence labels
- **VERIFIED** = seen in a search result text from the cited URL on 2026-11-20 (excerpt, not always the whole page).
- **READ** = read directly in the T.O X source (read-only, `c_hub.js`).
- **MEMORY** = my own knowledge, no URL read.
- No vendor code or artwork copied.

---

## 1. What T.O X already has (READ: `scratchpad/c_hub.js`, 6986 bytes)

- `window.TOX` = frozen object, `version:'1'`, methods from `TOXAPI`:
  - `commands()` -> list of `{id,en,ar,help}` from `XC` (every command with a title)
  - `run(id)` -> runs `XC[id].run()`, returns `true` or throws `unknown command`. **No arguments, no result data.**
  - `state()` -> project name, current tab, tab types, history position, docs count, summary
  - `pulse()` -> alert items `{severity,text}`
  - `docs()`, `addDoc(o)` (fields truncated: subject 200, body 8000), `setStatus(ref,st)` (validates ref and status), `search(q)`, `summary()`
- WebSocket bridge (`hubConnect`, `hubHandle`): off by default; JSON `{id, token, method, params}` -> `{id, result|error}`; requires shared secret of 8+ chars; warns with confirm() if the URL is not loopback (`127.0.0.1`, `localhost`, `[::1]`); keeps last 60 log lines in memory; panel `p_hub` under 
- The Agent panel (`p_agent`) already calls model APIs from the page (per the hub text: Claude, Gemini, OpenRouter, Mistral, OpenAI-compatible local servers). Keys stay in the browser.
- The hub text mentions `docs/AGENT_BRIDGE.md`. I did not check that it exists.

Gaps against what the owner wants (agents that control tools, ask questions, show indicators, open/close tabs):
1. `run(id)` cannot pass arguments (no "draw wall from A to B", no "open tab X").
2. No structured result or error codes; no way to read back the effect of a command.
3. No per-command permission class: an agent that can `run` can run anything in `XC`, including destructive commands.
4. No human-approval prompt for risky commands.
5. Audit log is 60 lines in memory only.
6. Secret stored in plain `localStorage` (`xto-hub`): readable by any script in the same origin and by browser extensions.
7. No "ask the user" channel and no "indicator" API for agents.
8. The WebSocket token is sent in each message (fine on loopback, bad on a remote `ws://`; use `wss://` only).
9. `hubHandle` has no rate limit and no origin/session binding.

---

## 2. Options compared

### 2.1 MCP (Model Context Protocol)
- Spec: servers expose tools; HTTP transports can use OAuth 2.1 (server = resource server; PKCE required for clients in the 2025-03-26 revision; tokens never in URL; 401 / 403 semantics). Authorization is optional; STDIO servers should take credentials from the environment instead. VERIFIED: https:/
- **Browser MCP**: an MCP server that controls a browser (see 2.4).
- **Filesystem MCP**: reads/writes local files. Risk: exposes the disk; restrict to one project folder (MEMORY).
- **Custom MCP server for T.O X**: a small local process (Node or Python) that (a) speaks MCP over STDIO to Claude Code/Desktop, Gemini CLI, etc., and (b) holds a loopback WebSocket the page connects to (the existing hub). Each MCP tool maps 1:1 to a TOX method. This reuses `c_hub.js` unchanged on t
- Needs from the user: Node/Python on the machine, one config line in the agent client, a shared secret. No cloud key for the bridge itself.
- Risks: tool-result text from documents/web is untrusted data and can carry prompt injection; a local MCP server runs with your user rights (MEMORY, general MCP practice).

### 2.2 Function calling (no MCP)
- Every major API (Claude, OpenAI, Gemini, Grok, OpenAI-compatible local servers like Ollama/LM Studio) accepts a list of tool definitions with JSON-schema parameters and returns a tool call that your code executes. Behaviour and schema dialect differ slightly per vendor (MEMORY: I did not read each
- Fit for T.O X: the in-page Agent panel can run the loop itself: send tools list, get a tool call, execute via `TOX`, send the result. No bridge needed, the page talks straight to the model API.
- Browser-direct calls: Anthropic requires the opt-in header `anthropic-dangerous-direct-browser-access: true`; the key is visible to anyone with dev tools, so this is only for bring-your-own-key use (VERIFIED: https://simonwillison.net/2024/Aug/23/anthropic-dangerous-direct-browser-access). Other p
- User provides: their own API key (stored in browser only, per owner rule), or a local model URL.
- Risks: key theft by XSS or extensions; cost runaway (set max steps and max tokens); same prompt injection risk.

### 2.3 WebSocket bridge to the page (already built)
----
ollama 200
hf 200
gh 200
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### assistant · 2026-11-20T09:20:37.761Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\nmkdir -p ol; \nfor m in qwen2.5 qwen3 qwen3-vl gemma3 gemma3n llama3.1 llama3.2 llama3.3 hermes3 nous-hermes2 mistral mistral-nemo mistral-small aya aya-expanse command-r7b-arabic command-r7b phi4 gpt-oss deepseek-r1 granite3.3 smollm2 qwen2.5-coder jais allam; do\n (curl -s -m 25 https://ollama.com/library/$m -o ol/$m.html -w \"$m %{http_code}\\n\") & done; wait\ncurl -s -m 25 \"https://ollama.com/search?q=arabic\" -o ol/search_arabic.html; curl -s -m 25 \"https://ollama.com/search?q=hermes\" -o ol/search_hermes.html; curl -s -m 25 \"https://ollama.com/search?q=qwen\" -o ol/search_qwen.html;curl -s -m 25 \"https://ollama.com/search?q=gemma\" -o ol/search_gemma.html\ncat > $S/strip.py <<'EOF'\nimport re,sys,html\nt=open(sys.argv[1],errors='ignore').read()\nt=re.sub(r'<(script|style)[^>]*>.*?</\\1>','',t,flags=re.S)\nt=re.sub(r'<[^>]+>','\\n',t)\nt=html.unescape(t)\nlines=[l.strip() for l in t.split('\\n') if l.strip()]\nprint('\\n'.join(lines))\nEOF\nfor f in search_arabic search_hermes; do echo \"== $f\"; python3 -I $S/strip.py ol/$f.html | head -60; done",
 "description": "Fetch Ollama library pages and searches"
}
```

### user · 2026-11-20T09:20:43.647Z

**نتيجة أداة:**
```
allam 404
jais 404
nous-hermes2 200
aya-expanse 200
qwen3 200
mistral-nemo 200
aya 200
mistral 200
granite3.3 200
qwen3-vl 200
hermes3 200
llama3.1 200
qwen2.5 200
phi4 200
gpt-oss 200
command-r7b-arabic 200
mistral-small 200
llama3.3 200
llama3.2 200
command-r7b 200
gemma3n 200
gemma3 200
deepseek-r1 200
smollm2 200
qwen2.5-coder 200
== search_arabic
arabic · Ollama
GitHub
187.7K
Download
Models
Docs
Pricing
Sign in
Download
Models
Docs
Pricing
Sign in
i.value).length + (size.value ? 1 : 0) || '';
"
>
Models
Popular
Newest
Name
Price
Context
Popular
Popular
Newest
Name
Price
Context
Filters
Where
Any
Local
Cloud
Capabilities
Tools
Thinking
Vision
Embedding
Decision
Download size
Any size
Up to 8 GB
Up to 16 GB
Up to 32 GB
Up to 64 GB
Over 64 GB
Show 20+ models
arabic · Ollama
Search for models on Ollama.
command-r7b-arabic
1y
tools
A new state-of-the-art version of the lightweight Command R7B model that excels in advanced Arabic language capabilities for enterprises in the Middle East and Northern Africa.
219.3K
5 tags
7b
deepseek-coder-v2
2y
An open-source Mixture-of-Experts code language model that achieves performance comparable to GPT4-Turbo in code-specific tasks.
3.4M
== search_hermes
hermes · Ollama
GitHub
187.7K
Download
Models
Docs
Pricing
Sign in
Download
Models
Docs
Pricing
Sign in
i.value).length + (size.value ? 1 : 0) || '';
"
>
Models
Popular
Newest
Name
Price
Context
Popular
Popular
Newest
Name
Price
Context
Filters
Where
Any
Local
Cloud
Capabilities
Tools
Thinking
Vision
Embedding
Decision
Download size
Any size
Up to 8 GB
Up to 16 GB
Up to 32 GB
Up to 64 GB
Over 64 GB
Show 20+ models
hermes · Ollama
Search for models on Ollama.
hermes3
1y
tools
Hermes 3 is the latest version of the flagship Hermes series of LLMs by Nous Research
1.8M
65 tags
3b
8b
70b
405b
openhermes
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

### assistant · 2026-11-20T09:20:48.498Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\npython3 -I $S/strip.py ol/search_hermes.html | sed -n 60,110p | tr '\\n' '|' ; echo\nfor m in qwen3 qwen2.5 gemma3 gemma3n llama3.1 llama3.2 hermes3 mistral mistral-nemo aya-expanse aya command-r7b-arabic phi4 gpt-oss; do echo \"=== $m\"; python3 -I $S/strip.py ol/$m.html | grep -nE \"^[a-z0-9.\\-]+:[a-z0-9.\\-]+$\" | head -0; python3 -I $S/strip.py ol/$m.html | awk 'BEGIN{p=0} /Models|Readme/{p=1} p' | grep -E \"^[0-9.]+(GB|MB)$|^[a-z0-9.\\-]+:[a-z0-9._\\-]+$|[0-9]+K$|^(Text|Image)$|tools|License|Apache|Community|Gemma|Qwen|Meta|CC-BY\" | head -40 | tr '\\n' '|'; echo; done 2>&1 | cut -c1-900",
 "description": "Parse Ollama tags sizes per model"
}
```

### user · 2026-11-20T09:20:53.824Z

<details><summary>نتيجة أداة (8413 حرف)</summary>

```
openhermes|2y|OpenHermes 2.5 is a 7B model fine-tuned by Teknium on Mistral with fully open datasets.|2M|35 tags|nous-hermes2|2y|The powerful family of models by Nous Research that excels at scientific discussion and coding tasks.|1.1M|33 tags|10.7b|34b|nous-hermes|3y|General use models based on Llama and Llama 2 from Nous Research.|1.3M|63 tags|7b|13b|nous-hermes2-mixtral|1y|The Nous Hermes 2 model from Nous Research, now trained over Mixtral.|620.7K|18 tags|8x7b|edtorre/qwen3.5-hermes|4mo|vision|tools|thinking|A compact, agent-tuned Qwen 3.5 model built for local agent harnesses like Hermes Agent. Based on `qwen3.5:latest` with Q4_K_M quantization for a lightweight 6.6 GB footprint, while|retaining strong tool-calling, vision, and thinking capabilities.|4,435|edtorre/hermes-qwen3.5-9b-abliterated|1mo|vision|1,375|ericli1018/Hermes3.6-35B-A3B-Uncensored-Genesis-V7|3mo|vision|Ollama repack of Qwen3.6-35B-A3B Genesis Hermes V7 with APEX/APEX-Compact, Vision, and 224K context for coding agents.|1,666|3 tags|edtorre/gemma4|4mo|vision|tools|thinking|Gemma 4 12B agent-tuned for Hermes Agent and other local agent harnesses. One built for 20GB GPUs the other for 8GB GPUs.|1,529|2 tags|
=== qwen3
head: illegal line count -- 0
Qwen3 is the latest generation of large language models in Qwen series, offering a comprehensive suite of dense and mixture-of-experts (MoE) models.|Qwen3 is the latest generation of large language models in Qwen series, offering a comprehensive suite of dense and mixture-of-experts (MoE) models.|tools|qwen3:latest|qwen3:latest|5.2GB|40K|Text|qwen3:0.6b|qwen3:0.6b|523MB|40K|Text|qwen3:1.7b|qwen3:1.7b|1.4GB|40K|Text|qwen3:4b|qwen3:4b|2.5GB|256K|Text|qwen3:8b|qwen3:8b|5.2GB|40K|Text|qwen3:14b|qwen3:14b|9.3GB|40K|Text|qwen3:30b|qwen3:30b|19GB|256K|Text|qwen3:32b|qwen3:32b|
=== qwen2.5
head: illegal line count -- 0
Qwen2.5 models are pretrained on Alibaba's latest large-scale dataset, encompassing up to 18 trillion tokens. The model supports up to 128K tokens and has multilingual support.|Qwen2.5 models are pretrained on Alibaba's latest large-scale dataset, encompassing up to 18 trillion tokens. The model supports up to 128K tokens and has multilingual support.|tools|qwen2.5:latest|qwen2.5:latest|4.7GB|32K|Text|qwen2.5:0.5b|qwen2.5:0.5b|398MB|32K|Text|qwen2.5:1.5b|qwen2.5:1.5b|986MB|32K|Text|qwen2.5:3b|qwen2.5:3b|1.9GB|32K|Text|qwen2.5:7b|qwen2.5:7b|4.7GB|32K|Text|qwen2.5:14b|qwen2.5:14b|9.0GB|32K|Text|qwen2.5:32b|qwen2.5:32b|20GB|32K|Text|qwen2.5:72b|qwen2.5:72b|
=== gemma3
head: illegal line count -- 0
gemma3:latest|gemma3:latest|3.4GB|128K|gemma3:270m|gemma3:270m|292MB|32K|Text|gemma3:1b|gemma3:1b|806MB|32K|Text|gemma3:4b|gemma3:4b|3.4GB|128K|gemma3:12b|gemma3:12b|8.2GB|128K|gemma3:27b|gemma3:27b|17GB|128K|Gemma is a lightweight, family of models from Google built on Gemini technology. The Gemma 3 models are multimodal—processing text and images—and feature a 128K context window with support for over 140 languages. Available in 270M, 1B, 4B, 12B, and 27B parameter sizes, they excel in tasks like question answering, summarization, and reasoning, while their compact design allows deployment on resource-limited devices.|Text|The quantization aware trained Gemma 3 models preserves similar quality as half precision models (BF16) while maintaining a lower memory footprint (3x less compared to non-quantized models).|Gemma 3 270M|Gemma 3 270m instruction tuned|Gemma 3 PT 1B|Gemma 3 PT 4B|
=== gemma3n
head: illegal line count -- 0
Gemma 3n models are designed for efficient execution on everyday devices such as laptops, tablets or phones.|Gemma 3n models are designed for efficient execution on everyday devices such as laptops, tablets or phones.|gemma3n:latest|gemma3n:latest|9.8GB|32K|gemma3n:e2b|gemma3n:e2b|7.8GB|32K|gemma3n:e4b|gemma3n:e4b|9.8GB|32K|Gemma 3n models are designed for efficient execution on everyday devices such as laptops, tablets or phones. These models were trained with data in over 140 spoken languages.|Gemma 3n models use selective parameter activation technology to reduce resource requirements. This technique allows the models to operate at an effective size of 2B and 4B parameters, which is lower than the total number of parameters they contain.|to previous Gemma models. All testing was conducted without safety filters to|violations, and showed significant improvements over previous Gemma mod
=== llama3.1
head: illegal line count -- 0
Llama 3.1 is a new state-of-the-art model from Meta available in 8B, 70B and 405B parameter sizes.|Llama 3.1 is a new state-of-the-art model from Meta available in 8B, 70B and 405B parameter sizes.|tools|llama3.1:latest|llama3.1:latest|4.9GB|128K|Text|llama3.1:8b|llama3.1:8b|4.9GB|128K|Text|llama3.1:70b|llama3.1:70b|43GB|128K|Text|llama3.1:405b|llama3.1:405b|243GB|128K|Text|Meta Llama 3.1|The upgraded versions of the 8B and 70B models are multilingual and have a significantly longer context length of 128K, state-of-the-art tool use, and overall stronger reasoning capabilities. This enables Meta’s latest models to support advanced use cases, such as long-form text summarization, multilingual conversational agents, and coding assistants.|Meta also has made changes to their license, allowing developers to use the outputs from Llama models, including the 405B model, to improve other models
=== llama3.2
head: illegal line count -- 0
Meta's Llama 3.2 goes small with 1B and 3B models.|Meta's Llama 3.2 goes small with 1B and 3B models.|tools|llama3.2:latest|llama3.2:latest|2.0GB|128K|Text|llama3.2:1b|llama3.2:1b|1.3GB|128K|Text|llama3.2:3b|llama3.2:3b|2.0GB|128K|Text|The Meta Llama 3.2 collection of multilingual large language models (LLMs) is a collection of pretrained and instruction-tuned generative models in 1B and 3B sizes (text in/text out). The Llama 3.2 instruction-tuned text only models are optimized for multilingual dialogue use cases, including agentic retrieval and summarization tasks. They outperform many of the available open source and closed chat models on common industry benchmarks.|The 3B model outperforms the Gemma 2 2.6B and Phi 3.5-mini models on tasks such as:|The Meta Llama 3.2 collection of multilingual large language models (LLMs) is a collection of pretrained and instruction-tuned generative m
=== hermes3
head: illegal line count -- 0
tools|hermes3:latest|hermes3:latest|4.7GB|128K|Text|hermes3:3b|hermes3:3b|2.0GB|128K|Text|hermes3:8b|hermes3:8b|4.7GB|128K|Text|hermes3:70b|hermes3:70b|40GB|128K|Text|hermes3:405b|hermes3:405b|229GB|128K|Text|
=== mistral
head: illegal line count -- 0
tools|mistral:latest|mistral:latest|4.4GB|32K|Text|mistral:7b|mistral:7b|4.4GB|32K|Text|Mistral is a 7B parameter model, distributed with the Apache license. It is available in both instruct (instruction following) and text completion.|Mistral is a 7B parameter model, distributed with the Apache license. It is available in both instruct (instruction following) and text completion.|
=== mistral-nemo
head: illegal line count -- 0
tools|mistral-nemo:latest|mistral-nemo:latest|7.1GB|1000K|Text|mistral-nemo:12b|mistral-nemo:12b|7.1GB|1000K|Text|
=== aya-expanse
head: illegal line count -- 0
tools|aya-expanse:latest|aya-expanse:latest|5.1GB|8K|Text|aya-expanse:8b|aya-expanse:8b|5.1GB|8K|Text|aya-expanse:32b|aya-expanse:32b|20GB|8K|Text|Released under CC-BY-NC license with additional usage policies|- Released under CC-BY-NC license with additional usage policies|
=== aya
head: illegal line count -- 0
aya:latest|aya:latest|4.8GB|8K|Text|aya:8b|aya:8b|4.8GB|8K|Text|aya:35b|aya:35b|20GB|8K|Text|
=== command-r7b-arabic
head: illegal line count -- 0
219.3K|tools|command-r7b-arabic:latest|command-r7b-arabic:latest|5.1GB|16K|Text|command-r7b-arabic:7b|command-r7b-arabic:7b|5.1GB|16K|Text|
=== phi4
head: illegal line count -- 0
phi4:latest|phi4:latest|9.1GB|16K|Text|phi4:14b|phi4:14b|9.1GB|16K|Text|
=== gpt-oss
head: illegal line count -- 0
tools|gpt-oss:latest|gpt-oss:latest|14GB|128K|Text|gpt-oss:20b|gpt-oss:20b|14GB|128K|Text|gpt-oss:120b|gpt-oss:120b|65GB|128K|Text|gpt-oss:20b-cloud|gpt-oss:20b-cloud|128K|Text|gpt-oss:120b-cloud|gpt-oss:120b-cloud|128K|Text|Permissive Apache 2.0 license:|- **Permissive Apache 2.0 license:** Build freely without copyleft restrictions or patent risk—ideal for experimentation, customization, and commercial deployment.|
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### assistant · 2026-11-20T09:20:59.918Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\nfor m in qwen3.5 qwen3.6 gemma4 llama4 ministral-3 mistral-small3.2 qwen3-next glm-4.7-flash lfm2 granite4 olmo3 nemotron-3-nano; do (curl -s -m 25 https://ollama.com/library/$m -o ol/$m.html -w \"$m %{http_code}\\n\") & done; wait\ncurl -s -m 25 \"https://ollama.com/library?sort=newest\" -o ol/newest.html\npython3 -I $S/strip.py ol/newest.html | awk 'NR>40' | head -150 | tr '\\n' '|' | cut -c1-3500; echo\nfor m in qwen3.5 qwen3.6 gemma4 ministral-3 mistral-small3.2 granite4 llama4; do echo \"=== $m\"; python3 -I $S/strip.py ol/$m.html | grep -E \"^[0-9.]+(GB|MB)$|^[a-z0-9.\\-]+:[a-z0-9._\\-]+$|^[0-9]+K$|^tools$|^vision$|^thinking$|Apache|License|licen\" | head -32 | tr '\\n' '|' | cut -c1-900; echo; done",
 "description": "Check newest Ollama models"
}
```

### user · 2026-11-20T09:21:05.217Z

<details><summary>نتيجة أداة (5871 حرف)</summary>

```
olmo3 404
llama4 200
lfm2 200
granite4 200
nemotron-3-nano 200
glm-4.7-flash 200
gemma4 200
ministral-3 200
qwen3.6 200
mistral-small3.2 200
qwen3.5 200
qwen3-next 200
autotrust-jev|AutoTrust’s decision models return choices, yes/no probabilities, and ratings for the questions you supply|vision|decision|9b|35b|62.4K|Pulls|11|Tags|Updated|2 weeks ago|kimi-k3.1-pro|Kimi K3.1 Pro is an open-weight, natively multimodal agentic model and our most capable 3T-class model to date, with a 1M-token context window and major gains in coding, 3D creation, financial research, and factual accuracy.|vision|tools|thinking|cloud|25.5K|Pulls|1|Tag|Updated|2 weeks ago|pplx-decider-flash|pplx-decider-flash is a 4B decision model from Perplexity, built on Qwen3.5-4B|vision|decision|4b|49.6K|Pulls|5|Tags|Updated|2 weeks ago|mimo-v2.6|MiMo-V2.6-Distill-Qwen-9B is Xiaomi MiMo’s 9B model for code and agent workflows|vision|tools|thinking|9b|128.6K|Pulls|8|Tags|Updated|2 weeks ago|lfm3|LFM3-1.7B is a tri-hybrid model for local agents and specialized applications.|tools|thinking|1.7b|107.4K|Pulls|9|Tags|Updated|3 weeks ago|lfm3-audio|LFM3-Audio-2B is a compact, fully featured audio model.|vision|tools|audio|2b|53.2K|Pulls|8|Tags|Updated|3 weeks ago|lfm3-omni|a single end-to-end model that understands text, images, video and audio, and answers in text and speech|vision|tools|audio|2b|78.9K|Pulls|8|Tags|Updated|3 weeks ago|lfm3-vl|LFM3-VL-2B is a vision-language model for on-device visual understanding.|vision|tools|thinking|2b|61.9K|Pulls|9|Tags|Updated|3 weeks ago|d3|Turn text, structured data, and images into scored choices, yes/no answers, and ratings.|vision|decision|2b|4b|9b|27b|115.1K|Pulls|16|Tags|Updated|3 weeks ago|phonon|Phonon is Gradium’s text-to-speech family. It turns written text into spoken audio as it generates, making it useful for reading assistant replies, narrating passages, and adding a voice to local apps.|161.4K|Pulls|14|Tags|Updated|3 weeks ago|minimax-m3.1-flash|As a next-generation Flash model, M3.1 Flash delivers a generational leap in agentic tasks, coding, Computer Use and cybersecurity, while making online inference nearly three times faster and reducing usage costs by 70%.|vision|tools|thinking|cloud|55.7K|Pulls|1|Tag|Updated|1 month ago|flint|Flint is a 39.8 billion-parameter mixture-of-experts model from Recursive, built for coding agents.|tools|thinking|40b|108.9K|Pulls|7|Tags|Updated|4 weeks ago|d1-omni|d1-omni is a multimodal 600M decision model from Liquid AI|vision|decision|audio|600m|2b|70.4K|Pulls|8|Tags|
=== qwen3.5
vision|tools|thinking|qwen3.5:latest|qwen3.5:latest|256K|qwen3.5:0.8b|qwen3.5:0.8b|256K|qwen3.5:2b|qwen3.5:2b|256K|qwen3.5:4b|qwen3.5:4b|256K|qwen3.5:9b|qwen3.5:9b|256K|qwen3.5:27b|qwen3.5:27b|256K|qwen3.5:35b|qwen3.5:35b|22GB|256K|qwen3.5:122b|qwen3.5:122b|81GB|256K|qwen3.5:0.8b-mlx|qwen3.5:0.8b-mlx|1.2GB|
=== qwen3.6
vision|tools|thinking|qwen3.6:latest|qwen3.6:latest|23GB|256K|qwen3.6:27b|qwen3.6:27b|256K|qwen3.6:35b|qwen3.6:35b|23GB|256K|qwen3.6:27b-mlx|qwen3.6:27b-mlx|19GB|256K|qwen3.6:35b-mlx|qwen3.6:35b-mlx|23GB|256K|
=== gemma4
vision|tools|thinking|gemma4:latest|gemma4:latest|128K|gemma4:e2b|gemma4:e2b|128K|gemma4:e4b|gemma4:e4b|128K|gemma4:12b|gemma4:12b|256K|gemma4:26b|gemma4:26b|256K|gemma4:31b|gemma4:31b|256K|gemma4:e2b-mlx|gemma4:e2b-mlx|7.5GB|128K|gemma4:e4b-mlx|gemma4:e4b-mlx|9.5GB|128K|gemma4:12b-mlx|gemma4:12b-mlx|7.7GB|
=== ministral-3
vision|tools|ministral-3:latest|ministral-3:latest|6.0GB|256K|ministral-3:3b|ministral-3:3b|3.0GB|256K|ministral-3:8b|ministral-3:8b|6.0GB|256K|ministral-3:14b|ministral-3:14b|9.1GB|256K|Apache 2.0 License: Open-source license allowing usage and modification for both commercial and non-commercial purposes.|* Apache 2.0 License: Open-source license allowing usage and modification for both commercial and non-commercial purposes.|
=== mistral-small3.2
vision|tools|mistral-small3.2:latest|mistral-small3.2:latest|15GB|128K|mistral-small3.2:24b|mistral-small3.2:24b|15GB|128K|
=== granite4
tools|granite4:latest|granite4:latest|2.1GB|128K|granite4:350m|granite4:350m|708MB|32K|granite4:1b|granite4:1b|3.3GB|128K|granite4:3b|granite4:3b|2.1GB|128K|are finetuned from their base models using a combination of open source instruction datasets with permissive license and internally collected synthetic datasets. They feature improved instruction following (IF) and tool-calling capabilities, making them more effective in enterprise applications.|License:|Apache 2.0|**Granite 4.0 models** are finetuned from their base models using a combination of open source instruction datasets with permissive license and internally collected synthetic datasets. They feature improved instruction following (IF) and tool-calling capabilities, making them more effective in enterprise applications.|- License: [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0)|
=== llama4
vision|tools|llama4:latest|llama4:latest|67GB|llama4:16x17b|llama4:16x17b|67GB|llama4:128x17b|llama4:128x17b|245GB|Llama 4 is intended for commercial and research use in multiple languages. Instruction tuned models are intended for assistant-like chat and visual reasoning tasks, whereas pretrained models can be adapted for natural language generation. For vision, Llama 4 models are also optimized for visual recognition, image reasoning, captioning, and answering general questions about an image. The Llama 4 model collection also supports the ability to leverage the outputs of its models to improve other models including synthetic data generation and distillation. The Llama 4 Community License allows for these use cases.|: Use in any manner that violates applicable laws or regulations (including trade compliance laws). Use in any other way that is prohibited by the Acceptable Use Policy a
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### assistant · 2026-11-20T09:21:07.628Z

Checking newer Ollama models (qwen3.5, gemma4) sizes, then HF licences and Arabic benchmarks.

### assistant · 2026-11-20T09:21:10.619Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\nfor m in qwen3.5 gemma4 qwen3.6; do echo \"== $m\"; python3 -I $S/strip.py ol/$m.html | grep -nE \"^(qwen|gemma)[0-9.]+:[a-z0-9._-]+$\" | head -0; python3 -I $S/strip.py ol/$m.html | sed -n 1,400p | grep -E -B0 -A4 \"^$m:(latest|0.8b|2b|4b|9b|27b|35b|e2b|e4b|12b|26b|31b)$\" | tr '\\n' '|' | cut -c1-1200; echo; done\necho; python3 -I $S/strip.py ol/qwen3.5.html | grep -iE \"arabic|languages|201|licen|apache\" | head -8 | cut -c1-300\npython3 -I $S/strip.py ol/gemma4.html | grep -iE \"arabic|languages|140|licen|apache|audio\" | head -8 | cut -c1-300",
 "description": "Get qwen3.5 gemma4 tag sizes and licences"
}
```

### assistant · 2026-11-20T09:21:15.367Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\nhf(){ curl -s -m 20 \"https://huggingface.co/api/models/$1\" | python3 -I -c \"\nimport sys,json\ntry:\n d=json.load(sys.stdin); c=d.get('cardData') or {}\n print('$1','| lic:',c.get('license'),c.get('license_name',''),'| dl:',d.get('downloads'),'| lastmod:',d.get('lastModified','')[:10],'| tags:',[t for t in d.get('tags',[]) if t.startswith('license') or t in('ar','arabic')][:3])\nexcept Exception as e: print('$1 ERR',e)\n\"; }\nfor m in Qwen/Qwen3-8B Qwen/Qwen2.5-7B-Instruct Qwen/Qwen3.5-9B google/gemma-3-12b-it NousResearch/Hermes-3-Llama-3.1-8B NousResearch/Hermes-4-14B NousResearch/Hermes-4-70B mistralai/Mistral-Nemo-Instruct-2407 inceptionai/jais-family-13b-chat inceptionai/jais-adapted-7b-chat inceptionai/jais-family-6p7b-chat humain-ai/ALLaM-7B-Instruct-preview CohereLabs/c4ai-command-r7b-arabic-02-2025 CohereLabs/aya-expanse-8b CohereLabs/aya-23-8B FreedomIntelligence/AceGPT-v2-8B-Chat meta-llama/Llama-3.1-8B-Instruct openai/gpt-oss-20b SILMA-AI/SILMA-9B-Instruct-v1.0 google/gemma-4-12b-it; do hf $m & done; wait",
 "description": "Query HF API for model licences"
}
```

### user · 2026-11-20T09:21:16.985Z

<details><summary>نتيجة أداة (2996 حرف)</summary>

```
== qwen3.5
head: illegal line count -- 0
qwen3.5:latest|6.6GB - 7.6GB · 256K context window · Text, Image · 1 month ago|qwen3.5:latest|6.6GB - 7.6GB|256K|Text, Image|qwen3.5:0.8b|1.2GB - 1.3GB · 256K context window · Text, Image · 1 month ago|qwen3.5:0.8b|1.2GB - 1.3GB|256K|Text, Image|qwen3.5:2b|2.7GB - 3.1GB · 256K context window · Text, Image · 1 month ago|qwen3.5:2b|2.7GB - 3.1GB|256K|Text, Image|qwen3.5:4b|3.3GB - 4.0GB · 256K context window · Text, Image · 1 month ago|qwen3.5:4b|3.3GB - 4.0GB|256K|Text, Image|qwen3.5:9b|latest|6.6GB - 7.6GB · 256K context window · Text, Image · 1 month ago|qwen3.5:9b|latest|6.6GB - 7.6GB|256K|Text, Image|qwen3.5:27b|17GB - 20GB · 256K context window · Text, Image · 1 month ago|qwen3.5:27b|17GB - 20GB|256K|Text, Image|qwen3.5:35b|22GB · 256K context window · Text, Image · 1 month ago|qwen3.5:35b|22GB|256K|Text, Image|qwen3.5:122b|
== gemma4
head: illegal line count -- 0
gemma4:latest|6.6GB - 9.5GB · 128K context window · Text, Image · 1 month ago|gemma4:latest|6.6GB - 9.5GB|128K|Text, Image|gemma4:e2b|4.6GB - 7.5GB · 128K context window · Text, Image · 1 month ago|gemma4:e2b|4.6GB - 7.5GB|128K|Text, Image|gemma4:e4b|latest|6.6GB - 9.5GB · 128K context window · Text, Image · 1 month ago|gemma4:e4b|latest|6.6GB - 9.5GB|128K|Text, Image|gemma4:12b|7.7GB - 8.0GB · 256K context window · Text, Image · 1 month ago|gemma4:12b|7.7GB - 8.0GB|256K|Text, Image|gemma4:26b|16GB - 19GB · 256K context window · Text, Image · 1 month ago|gemma4:26b|16GB - 19GB|256K|Text, Image|gemma4:31b|19GB - 20GB · 256K context window · Text, Image · 1 month ago|gemma4:31b|19GB - 20GB|256K|Text, Image|gemma4:e2b-mlx|
== qwen3.6
head: illegal line count -- 0
qwen3.6:latest|23GB · 256K context window · Text, Image · 3 weeks ago|qwen3.6:latest|23GB|256K|Text, Image|qwen3.6:27b|18GB - 19GB · 256K context window · Text, Image · 1 month ago|qwen3.6:27b|18GB - 19GB|256K|Text, Image|qwen3.6:35b|latest|23GB · 256K context window · Text, Image · 3 weeks ago|qwen3.6:35b|latest|23GB|256K|Text, Image|

: Expanded support to 201 languages and dialects, enabling inclusive, worldwide deployment with nuanced cultural and regional understanding.
* MMLU-ProX: we report the averaged accuracy on 29 languages.
* WMT24++: a harder subset of WMT24 after difficulty labeling and rebalancing; we report the averaged scores on 55 languages using XCOMET-XXL.
- **Global Linguistic Coverage**: Expanded support to 201 languages and dialects, enabling inclusive, worldwide deployment with nuanced cultural and regional understanding.
* MMLU-ProX: we report the averaged accuracy on 29 languages.<br>
* WMT24++: a harder subset of WMT24 after difficulty labeling and rebalancing; we report the averaged scores on 55 languages using XCOMET-XXL.<br>
audio
Audio
Text, Image, Audio
Text, Image, Audio
Audio Encoder Parameters
No Audio
For optimal performance with multimodal inputs, place image and/or audio content
140
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### user · 2026-11-20T09:21:18.312Z

<details><summary>نتيجة أداة (2142 حرف)</summary>

```
Qwen/Qwen2.5-7B-Instruct | lic: apache-2.0  | dl: 6391398 | lastmod: 2025-01-12 | tags: ['license:apache-2.0']
Qwen/Qwen3-8B | lic: apache-2.0  | dl: 6141295 | lastmod: 2025-07-26 | tags: ['license:apache-2.0']
google/gemma-3-12b-it | lic: gemma  | dl: 405701 | lastmod: 2025-03-21 | tags: ['license:gemma']
NousResearch/Hermes-3-Llama-3.1-8B | lic: llama3  | dl: 328613 | lastmod: 2024-09-08 | tags: ['license:llama3']
Qwen/Qwen3.5-9B | lic: apache-2.0  | dl: 6395460 | lastmod: 2026-03-02 | tags: ['license:apache-2.0']
NousResearch/Hermes-4-14B | lic: apache-2.0  | dl: 5467 | lastmod: 2026-01-09 | tags: ['license:apache-2.0']
CohereLabs/c4ai-command-r7b-arabic-02-2025 | lic: cc-by-nc-4.0  | dl: 1576 | lastmod: 2025-10-30 | tags: ['ar', 'license:cc-by-nc-4.0']
google/gemma-4-12b-it ERR Expecting value: line 1 column 1 (char 0)
mistralai/Mistral-Nemo-Instruct-2407 | lic: apache-2.0  | dl: 89767 | lastmod: 2025-07-28 | tags: ['license:apache-2.0']
FreedomIntelligence/AceGPT-v2-8B-Chat | lic: apache-2.0  | dl: 1475 | lastmod: 2024-11-14 | tags: ['ar', 'license:apache-2.0']
inceptionai/jais-family-6p7b-chat ERR Expecting value: line 1 column 1 (char 0)
inceptionai/jais-adapted-7b-chat ERR Expecting value: line 1 column 1 (char 0)
inceptionai/jais-family-13b-chat ERR Expecting value: line 1 column 1 (char 0)
CohereLabs/aya-23-8B | lic: cc-by-nc-4.0  | dl: 4705 | lastmod: 2025-09-11 | tags: ['ar', 'license:cc-by-nc-4.0']
CohereLabs/aya-expanse-8b | lic: cc-by-nc-4.0  | dl: 26719 | lastmod: 2026-01-09 | tags: ['ar', 'license:cc-by-nc-4.0']
meta-llama/Llama-3.1-8B-Instruct | lic: llama3.1  | dl: 4097176 | lastmod: 2024-09-25 | tags: ['license:llama3.1']
openai/gpt-oss-20b | lic: apache-2.0  | dl: 5560822 | lastmod: 2025-08-26 | tags: ['license:apache-2.0']
NousResearch/Hermes-4-70B | lic: llama3  | dl: 4155 | lastmod: 2025-09-02 | tags: ['license:llama3']
SILMA-AI/SILMA-9B-Instruct-v1.0 ERR Expecting value: line 1 column 1 (char 0)
humain-ai/ALLaM-7B-Instruct-preview | lic: apache-2.0  | dl: 9684 | lastmod: 2025-07-14 | tags: ['ar', 'license:apache-2.0']
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### assistant · 2026-11-20T09:21:24.562Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\nq(){ curl -s -m 20 \"https://huggingface.co/api/models?search=$1&limit=${2:-8}&sort=downloads&direction=-1\" | python3 -I -c \"\nimport sys,json\nfor d in json.load(sys.stdin): print(d['id'],'| dl',d.get('downloads'),'|',[t for t in d.get('tags',[]) if t.startswith('license:')])\"; }\necho \"--jais\"; q jais 8; echo \"--silma\"; q silma 5; echo \"--gemma-4\"; q gemma-4 8; echo \"--allam\"; q ALLaM 6; echo \"--egyptian llm\"; q egyptian 8; echo \"--arabic-gguf\";q arabic+gguf 6\necho \"--OALL\"; curl -s -m 20 -o /dev/null -w \"%{http_code}\\n\" https://huggingface.co/api/spaces/OALL/Open-Arabic-LLM-Leaderboard; curl -s -m 20 \"https://huggingface.co/api/spaces/OALL/Open-Arabic-LLM-Leaderboard\" | python3 -I -c \"import sys,json;d=json.load(sys.stdin);print(d.get('lastModified'),d.get('runtime',{}).get('stage'),d.get('likes'))\"",
 "description": "Search HF for Jais, Gemma4, OALL"
}
```

### assistant · 2026-11-20T09:21:25.070Z

**أداة:** `WebSearch`

```json
{
 "query": "Open Arabic LLM Leaderboard OALL v2 results Qwen Gemma ALLaM Jais Egyptian dialect benchmark",
 "mode": "standard"
}
```

### user · 2026-11-20T09:21:30.936Z

<details><summary>نتيجة أداة (2988 حرف)</summary>

```
--jais
mradermacher/Jais-3-32B-GGUF | dl 17717 | ['license:apache-2.0']
IFM/Jais-ASR | dl 11718 | ['license:apache-2.0']
optimum-intel-internal-testing/tiny-random-jais | dl 10318 | []
IFM/Jais-ASR-W4A16-AWQ | dl 8627 | ['license:apache-2.0']
IFM/Jais-3-32B-GGUF | dl 4174 | ['license:apache-2.0']
IFM/Jais-3-7B-GGUF | dl 3431 | ['license:apache-2.0']
inception42/Jais-2-8B-Chat | dl 3086 | ['license:apache-2.0']
IFM/Jais-ASR-GGUF | dl 2767 | ['license:apache-2.0']
--silma
silma-ai/SILMA-9B-Instruct-v1.0 | dl 2485 | ['license:gemma']
silma-ai/silma-embedding-matryoshka-v0.1 | dl 2182 | ['license:apache-2.0']
bartowski/SILMA-9B-Instruct-v1.0-GGUF | dl 1473 | ['license:gemma']
silma-ai/SILMA-Kashif-2B-Instruct-v1.0 | dl 1420 | ['license:gemma']
silma-ai/silma-tts | dl 1300 | ['license:apache-2.0']
--gemma-4
google/gemma-4-31B-it | dl 6148549 | ['license:apache-2.0']
google/gemma-4-26B-A4B-it | dl 4940525 | ['license:apache-2.0']
google/gemma-4-E4B-it | dl 4328955 | ['license:apache-2.0']
google/gemma-4-E2B-it | dl 2768990 | ['license:apache-2.0']
unsloth/gemma-4-12b-it-GGUF | dl 2569871 | ['license:apache-2.0']
unsloth/gemma-4-26B-A4B-it-GGUF | dl 2311900 | ['license:apache-2.0']
nvidia/Gemma-4-26B-A4B-NVFP4 | dl 1808180 | ['license:apache-2.0']
google/gemma-4-12B-it | dl 1585858 | ['license:apache-2.0']
--allam
humain-ai/ALLaM-7B-Instruct-preview | dl 9684 | ['license:apache-2.0']
bartowski/ALLaM-AI_ALLaM-7B-Instruct-preview-GGUF | dl 2741 | ['license:apache-2.0']
mradermacher/midad-allam-7b-i1-GGUF | dl 1223 | ['license:apache-2.0']
mastouri/ALLaM-7B-Arabic-SFT | dl 428 | ['license:apache-2.0']
mradermacher/ALLaM-7B-Toxic-Prompt-Detect-GGUF | dl 389 | []
mradermacher/ALLaM-7B-Arabic-SFT-GGUF | dl 306 | ['license:apache-2.0']
--egyptian llm
IbrahimAmin/egyptian-arabic-wav2vec2-xlsr-53 | dl 1283 | ['license:apache-2.0']
mradermacher/gemma-3-egyptian-4b-v1-GGUF | dl 865 | ['license:apache-2.0']
mohammedaly22/whisper-large-v3-turbo-egyptian-code-switching | dl 797 | ['license:mit']
mradermacher/gemma-3-12b-Egyptian-GGUF | dl 438 | []
MAdel121/whisper-small-egyptian-arabic | dl 381 | ['license:mit']
IbrahimAmin/code-switched-egyptian-arabic-whisper-small | dl 366 | ['license:apache-2.0']
mradermacher/Egyptian-Arabic-Translator-Llama-3-8B-GGUF | dl 339 | ['license:llama3']
NAMAA-Space/NAMAA-Egyptian-TTS | dl 303 | ['license:mit']
--arabic-gguf
handy-computer/cohere-transcribe-arabic-07-2026-gguf | dl 174728 | ['license:apache-2.0']
SalahALHaismawi/Nuqta-Arabic-OCR-4B-GGUF | dl 10322 | ['license:apache-2.0']
mradermacher/Gemma-4-26B-A4B-Arabic-It-i1-GGUF | dl 6432 | ['license:apache-2.0']
SalahALHaismawi/Nuqta-Arabic-OCR-0.8B-GGUF | dl 4099 | ['license:apache-2.0']
mradermacher/Gemma-4-E4B-Arabic-It-i1-GGUF | dl 3721 | ['license:apache-2.0']
yemeni-ai-lab/gemma-4-e2b-yemeni-arabic-assistant-GGUF | dl 2066 | ['license:cc-by-nc-sa-4.0']
--OALL
200
2025-10-09T10:34:33.000Z RUNNING 184
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### user · 2026-11-20T09:21:36.216Z

<details><summary>نتيجة أداة (2878 حرف)</summary>

```
Web search results for query: "Open Arabic LLM Leaderboard OALL v2 results Qwen Gemma ALLaM Jais Egyptian dialect benchmark"

Links: [{"title":"The Open Arabic LLM Leaderboard 2","url":"https://huggingface.co/blog/leaderboard-arabic-v2"},{"title":"Jais 2: A Family of Arabic-Centric Open Large Language Models","url":"https://arxiv.org/pdf/2608.13580"},{"title":"Open Arabic LLM Leaderboard","url":"https://huggingface.co/organizations/OALL/activity/all"},{"title":"Hugging Face","url":"https://huggingface.co/datasets/OALL/v2_results/tree/main/Qwen/Qwen2-7B-Instruct"},{"title":"ALLaM: Large Language Models for Arabic and English","url":"https://arxiv.org/pdf/2407.15390"},{"title":"CamelEval: Advancing Culturally Aligned Arabic Language Models and Benchmarks","url":"https://arxiv.org/pdf/2409.12623"},{"title":"HELM Arabic","url":"https://crfm.stanford.edu/2025/12/18/helm-arabic.html"},{"title":"Hugging Face","url":"https://huggingface.co/datasets/OALL/requests_v2/tree/main/Qwen"},{"title":"GemmAr: Enhancing LLMs Through Arabic Instruction-Tuning","url":"https://arxiv.org/pdf/2407.02147"},{"title":"BALSAM: A Platform for Benchmarking Arabic Large Language Models","url":"https://arxiv.org/pdf/2507.22603"}]

I ran one search. It did not turn up OALL v2 leaderboard scores for Qwen, Gemma, ALLaM, or Jais, and it found nothing on an Egyptian dialect benchmark specifically.

- **OALL v2 background:** Hugging Face's February 2025 announcement says the new version keeps Arabic tasks from Meta's Belebele (Arabic-MSA and Arabic-Dialects), which is the closest dialect coverage I found. It also says the first version had a large portion of datasets and tasks originated from non-Arabic-speaking contexts.
- **Qwen:** The OALL v2 results repository has per-model result files, including a Qwen2-7B-Instruct entry, but the search only returned the file listing, not the scores.
- **Gemma and ALLaM:** The Jais 2 paper includes a comparison table of open models up to 13B parameters with ALLaM-7B-Instruct-preview and several Gemma variants. The table's rows don't carry column headers in the snippet, so I can't tell which benchmark each number belongs to. The OALL organization page notes that ALLaM-7B-Instruct-preview was ranked on OALL/Open-Arabic-LLM-Leaderboard as well.
- **Jais:** The ALLaM paper's comparison table lists Jais and Jais-Chat variants, but it is not an OALL v2 result.
- **Caveat on the leaderboard:** A community post on the OALL page argues that likelihood-based leaderboards can be gamed through distillation, so scores from those leaderboards should be read with caution.

To get the actual OALL v2 numbers and any Egyptian-dialect breakdown, the next step is to open the leaderboard Space on Hugging Face or the v2_results dataset directly.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### assistant · 2026-11-20T09:21:42.049Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\ncurl -s -m 25 https://huggingface.co/inception42/Jais-2-8B-Chat -o jais2.html; python3 -I $S/strip.py jais2.html | grep -iE \"arabic|dialect|egypt|parameter|license|context|ollama|gguf|tool\" | head -30 | cut -c1-400\necho ======; curl -s -m 25 https://arxiv.org/abs/2608.13580 -o jais2abs.html; python3 -I $S/strip.py jais2abs.html | sed -n 1,40p | cut -c1-900",
 "description": "Read Jais 2 model card and abstract"
}
```

### assistant · 2026-11-20T09:21:44.894Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\ncurl -s -m 25 https://huggingface.co/blog/leaderboard-arabic-v2 -o oall2.html; python3 -I $S/strip.py oall2.html | grep -iE \"dialect|egypt|belebele|ArabicMMLU|AlGhafa|ALRAGE|MadinahQA|AraTrust|top|leader\" | head -25 | cut -c1-500\necho =====HELM; curl -s -m 25 https://crfm.stanford.edu/2025/12/18/helm-arabic.html -o helm.html; python3 -I $S/strip.py helm.html | grep -iE \"arabic|dialect|rank|best|gpt|gemini|qwen|jais|allam|llama|gemma\" | head -25 | cut -c1-500",
 "description": "Read OALL v2 blog and HELM Arabic"
}
```

### user · 2026-11-20T09:21:46.114Z

<details><summary>نتيجة أداة (2252 حرف)</summary>

```
Exit code 1
","chat_template":"{% set loop_messages = messages %}{% for message in loop_messages %}{% set content = '<|start_header_id|>' + message['role'] + '<|end_header_id|>' + message['content'] | trim + '<|eot_id|>' %}{% if loop.index0 == 0 %}{% set content = bos_token + content %}{% endif %}{{ content }}{% endfor %}{% if add_generation_prompt %}{{ '<|start_header_id|>ai<|end_header_id|>' }}{% endif %}",
Arabic
License:
Ollama
Jais-2: The Next Generation of Arabic Frontier LLMs
Jais-2: The Next Generation of Arabic Frontier LLMs
Jais-2-8B-Chat is a bilingual Arabic–English language model developed by MBZUAI, Inception, and Cerebras.
Jais-2-8B-Chat Model is trained from scratch on Arabic and English data and is powered by a custom Arabic-centric vocabulary, it efficiently captures Modern Standard Arabic, regional dialects, and mixed Arabic–English code-switching.
The model is openly available under a Apache 2.0 license and also deployed as a fast, production-ready chat experience running on Cerebras hardware.
: Arabic (MSA & dialects) and English
Parameters
Context Length
: Rotary Position Embeddings (RoPE), Squared-ReLU activation, custom μP parameterization, and 8:1 filter-to-hidden size ratio.
# Example Arabic prompt
# Example Arabic prompt
Arabic ability:
(English and Arabic) and
c4ai-command-r7b-arabic-02-2025
c4ai-command-r7b-arabic-02-2025
Jais-2-8B delivers competitive Arabic and English instruction-following performance across IFEval.
Jais-2-8B achieves the highest scores across nearly all AraGen metrics, outperforming Fanar-1-9B-Instruct and ALLaM-7B on Arabic generative tasks.
: Researchers focusing on Arabic NLP, multilingual modeling, or cultural alignment
: Companies targeting Arabic-speaking markets
: Integrating Arabic language capabilities into applications and workflows
Investigating Arabic linguistic or cultural patterns
Building chat assistants for Arabic-speaking audiences
Performing sentiment and market analysis in regional contexts
Summarizing or processing bilingual Arabic–English documents
Creating culturally resonant Arabic marketing and entertainment content for regional audiences
Applications requiring strong performance outside Arabic or English languages
(eval):3: ===== not found
```

</details>

### user · 2026-11-20T09:21:47.836Z

<details><summary>نتيجة أداة (5045 حرف)</summary>

```
Exit code 1
The Open Arabic LLM Leaderboard 2
The Open Arabic LLM Leaderboard 2
Current status of Arabic LLMs leaderboards
Impact of the previous leaderboard
Why do we need a new leaderboard?
Current status of Arabic LLMs leaderboards
The growing availability of LLMs supporting Arabic, both as monolingual and multilingual models, prompted the community to create dedicated Arabic language leaderboards. Previously, Arabic-focused leaderboards were typically confined to narrow benchmarks introduced by specific authors, often as demos for their work. In these cases, the authors would set up leaderboards to demonstrate how models performed on a particular task or dataset. Alternatively, other leaderboards required users to run eva
: Many community members lack access to the substantial computational resources needed to evaluate all available open-source models in order to establish which model would be best for their downstream project or application, being forced to rely only on the results shared by model makers in their documentation, which many times does not allow for a direct comparison. This high cost in both time and compute power can become a major barrier to participation in further developing Arabic LLMs, makin
: Because some platforms required users to evaluate their models independently and then simply submit a file of scores, there was no robust mechanism to ensure those results were accurate or even produced through a genuine evaluation. This lack of centralized verification could potentially undermine the credibility and fairness of the leaderboard.
Open Arabic LLM Leaderboard - OALL
AraGen Leaderboard
, the first generative tasks leaderboard for Arabic, introducing the 3C3H evaluation metric, which uses dynamic evaluation cycles with private test, and provides a native-Arabic and culturally-aware generative tasks dataset, AraGen Bench, to assess LLMs across four main tasks.
Arabic leaderboard
as part of their multilingual leaderboards. The benchmark empowering this leaderboard remains always private like all the other languages within their family of leaderboards, and relies on human-preference evaluation, using a dataset of 1,000 Arabic prompts designed to enhance chatbot interaction capabilities across complex and culturally nuanced conversations.
Impact of the previous leaderboard
In less than 7 months after its launch, the first version of the Open Arabic LLM Leaderboard quickly became a vital platform for the Arabic AI community, attracting over 46,000 visitors and more than 2,000 visits in the past month (January 2025). The HuggingFace space received over 100 likes and 8 citations on Google Scholar. The community submitted more than 700 models, ranging from 1B to over 70B parameters. The submitted models originate from more than 180 unique organizations making it one o
As depicted in Figure 1, among the ~700 models submitted to the initial version of the leaderboard, the majority are chat and finetuned models, comprising over 70%, whereas pretrained models constitute only 11%. In terms of model size, more than 50% of the models are smaller than 7B parameters.
Compared to leaderboards for other languages and as shown in Figure 2, the Open Arabic LLM leaderboard stands out as one of the most active, following closely behind the
leaderboards, all within less than a year of its launch. Considering that Arabic is one of the most spoken languages globally, yet has relatively limited content available on the internet, these figures carry even greater significance compared to other languages.
Figure 2: Number of evaluated models versus uptime in months for different MCQ leaderboards hosted on huggingface.
Why do we need a new leaderboard?
Recent discussions within the community, including critiques of the Open Arabic LLM Leaderboard (OALL) and similar initiatives,
[2]. Many researchers, developers, and language enthusiasts have emphasized the need for more direct evaluations of Arabic-specific tasks, increased transparency in how benchmarks are created, and the inclusion of more diverse datasets that reflect the breadth of Arabic dialects, domains, and real-world applications. These insights have played a central role in shaping the updated leaderboard.
The Arabic language presents unique challenges and characteristics that require specialized evaluation beyond what general NLP tasks can capture. These include intricate grammar, rich and complex morphology, the diversity of spoken dialects, and culturally nuanced safety-related considerations. A leaderboard that addresses these factors can provide a clearer picture of how well models perform in real-world Arabic language contexts.
Additionally, some benchmarks from the first version of OALL became less effective over time as models achieved near-perfect scores, limiting their ability to differentiate incremental improvements. In response, the new leaderboard replaces these saturated benchmarks, introducing a more relevant and up-to-date suite of evaluation tasks.
(eval):3: ====HELM not found
```

</details>

### assistant · 2026-11-20T09:21:54.019Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\ncurl -s -m 25 https://crfm.stanford.edu/2025/12/18/helm-arabic.html -o helm.html; python3 -I $S/strip.py helm.html | sed -n 1,60p | cut -c1-600\necho \"-----JAIS2 api\"; curl -s -m 20 \"https://huggingface.co/api/models?search=jais-2&limit=12\" | python3 -I -c \"\nimport sys,json\nfor d in json.load(sys.stdin): print(d['id'],d.get('downloads'),[t for t in d.get('tags',[]) if t.startswith('license:')])\"\ncurl -s -m 20 https://huggingface.co/api/models/inception42/Jais-2-8B-Chat | python3 -I -c \"\nimport sys,json;d=json.load(sys.stdin);print(d.get('safetensors',{}).get('total'),d.get('lastModified'),d.get('createdAt'))\"",
 "description": "Read HELM Arabic and Jais-2 variants"
}
```

### assistant · 2026-11-20T09:21:54.492Z

**أداة:** `WebSearch`

```json
{
 "query": "Egyptian Arabic dialect LLM evaluation benchmark Qwen Gemma Llama 2026 dialect performance gap MSA",
 "mode": "standard"
}
```

### user · 2026-11-20T09:21:57.256Z

<details><summary>نتيجة أداة (3247 حرف)</summary>

```
Stanford CRFM
People
Report
Research
HELM
Levanter
FMTI
Openness
Ecosystem Graphs
Policy
Blog
HELM Arabic
Authors:
Yifan Mai and
Rida Taleb and
Ahmed Elhagry
As part of our efforts to better understand the multilingual capabilities of large language models (LLMs), we present
HELM Arabic
, a leaderboard for transparent and reproducible evaluation of LLMs on Arabic language benchmarks. This leaderboard was produced in collaboration with
Arabic.AI
.
Benchmark
HELM Arabic builds on a collection of established Arabic-language evaluation tasks that are widely used in the research community
1
. It includes the following seven benchmarks:
AlGhafa
2
— an Arabic language multiple choice evaluation benchmark derived from publicly available NLP datasets
ArabicMMLU
3
— a native Arabic language question answering benchmark using questions sourced from school exams across diverse educational levels in different countries spanning North Africa, the Levant, and the Gulf regions
Arabic EXAMS
4
— the Arabic language subset of the EXAMS multilingual question answering benchmark, which consists of high school exam questions across various school subjects
MadinahQA
3
— a question answering benchmark published by MBZUAI that tests knowledge of Arabic language and grammar
AraTrust
5
— an Arab-region-specific safety evaluation dataset consisting of human-written questions including direct attacks, indirect attacks, and harmless requests with sensitive words
ALRAGE
1
— an Arabic language passage-based open-ended model-graded question answering benchmark that reflects retrieval-augmented generation use cases
ArbMMLU-HT
6
— a translation of MMLU to Arabic by human translators published by MBZUAI
We made the following decisions in our evaluation methodology:
We used Arabic letters for the options in the multiple choice question answering prompt template, which better reflects LLM usage within the Arabic language context.
We used zero-shot prompting to make the tasks more challenging; all evaluated models were instruction-tuned and did not need few-shot prompting.
We limited the evaluation to 1000 randomly sampled instances from each subset to reduce imbalances in the number of instances across subsets.
We disabled thinking on models with an optional thinking mode, and excluded models that had a mandatory thinking mode that could not be disabled.
Models
We evaluated a several leading models on the leaderboard. These models can be grouped into three main groups:
Closed-weights multilingual models —
Arabic.AI LLM-X
,
Arabic.AI LLM-S
,
Command A
,
-----JAIS2 api
jais001/distilgpt2-finetuned-wiki 0 []
jais001/distilgpt2-finetuned-wikitext2 0 []
hussain2030/jais13bchat2 15 ['license:apache-2.0']
JaiSurya/PPO-LunarLander-v2 4 []
danfeg/jais-13b-chat_finetuned_2481 9 []
FatimaZahra25/jais-13b-chat-4bits 8 []
jaishaktawat/Llama-2-7b-chat-finetune 6 []
inception42/jais-family-2p7b-chat 155 ['license:apache-2.0']
inception42/jais-family-2p7b 260 ['license:apache-2.0']
abdo-Mansour/jais-family-2p7b-chat-GPTQ-4 0 []
abdo-Mansour/jais-family-2p7b-chat-HQQ-4 0 []
abdo-Mansour/jais-family-2p7b-chat-BnB-8 11 []
8090401280 2026-08-18T09:59:48.000Z 2025-12-09T09:19:57.000Z
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### user · 2026-11-20T09:22:02.704Z

<details><summary>نتيجة أداة (3147 حرف)</summary>

```
Web search results for query: "Egyptian Arabic dialect LLM evaluation benchmark Qwen Gemma Llama 2026 dialect performance gap MSA"

Links: [{"title":"DialectalArabicMMLU: Benchmarking Dialectal Capabilities","url":"https://arxiv.org/html/2510.27543v1"},{"title":"2026.abjadnlp 1.41","url":"https://aclanthology.org/2026.abjadnlp-1.41.pdf"},{"title":"arxiv.org","url":"https://arxiv.org/pdf/2409.11404v2"},{"title":"arxiv.org","url":"https://arxiv.org/pdf/2409.11404v3"},{"title":"AraDiCE: Benchmarks for Dialectal and Cultural Capabilities in LLMs","url":"https://arxiv.org/html/2409.11404v3"},{"title":"AraDiCE: Benchmarks for Dialectal and Cultural Capabilities in LLMs","url":"https://arxiv.org/html/2409.11404v1"},{"title":"arxiv.org","url":"https://arxiv.org/pdf/2412.04193v2"},{"title":"Fanar: An Arabic-Centric Multimodal Generative AI Platform","url":"https://arxiv.org/pdf/2501.13944"},{"title":"2026.vardial 1.1","url":"https://aclanthology.org/2026.vardial-1.1.pdf"},{"title":"DialectalArabicMMLU: Benchmarking Dialectal Capabilities in Arabic and Multilingual Language Models","url":"https://preview.aclanthology.org/ingest-lrec/2026.lrec-main.251/"}]

The search turned up several relevant benchmarks, but none that test Qwen or Gemma on Egyptian Arabic specifically, so I can't confirm a current Egyptian-vs-MSA gap for those models.

- **DialectalArabicMMLU (2025/2026):** This benchmark covers Syrian, Egyptian, Emirati, Saudi, and Moroccan Arabic. Its authors report the first unified, human-curated resource for measuring dialectal understanding in Arabic, and their analysis finds substantial performance disparities across dialects. It was accepted at LREC 2026.
- **AraDiCE (2024):** This benchmark covers Levantine and Egyptian dialects. It found that they are better at encoding and understanding dialects than at generating or translating them. It also reported that multilingual LLMs, such as Llama3 and Mistral, show a substantial deficiency in adapting to Arabic dialects. Arabic-centric models did better, but their performance still lags compared to MSA or English.
- **AL-QASIDA (Egyptian and Moroccan generation):** This study reports that LLMs do not produce DA as well as they produce MSA. It also found that one author needed 14 turns of conversation before the LLM used the desired dialect.
- **3LM (2025):** This work offers 45K post-edited dialectal samples across Egyptian, Syrian, and Gulf varieties and a cultural benchmark.
- **Dialect translation (AbjadNLP 2026):** This study evaluates 16 LLMs on Arabic-English translation across 16 dialects, using BLEU, ChrF, COMET, and LLM-as-a-judge metrics.

The likely cause of the gap is that post-training uses existing human-labeled data, which is typically MSA. The sources also note that models have the capability to understand and model DA, but that they default to MSA regardless.

For Qwen, Gemma, and Llama results on Egyptian specifically, I'd need a more targeted search. DialectalArabicMMLU is the most likely source for per-model Egyptian numbers.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### assistant · 2026-11-20T09:22:07.597Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\ncurl -s -m 30 https://arxiv.org/html/2510.27543v1 -o dmmlu.html; python3 -I $S/strip.py dmmlu.html | grep -iE \"egypt|qwen|gemma|llama|jais|allam|fanar|average|best\" | head -40 | cut -c1-420\necho ----HELMmodels; python3 -I $S/strip.py helm.html | sed -n 60,120p | cut -c1-500",
 "description": "Extract Egyptian numbers and HELM models"
}
```

### user · 2026-11-20T09:22:09.588Z

<details><summary>نتيجة أداة (6256 حرف)</summary>

```
extends the MMLU-Redux framework through manual translation and adaptation of 3K multiple-choice question–answer pairs into five major dialects (Syrian, Egyptian, Emirati, Saudi, and Moroccan), yielding a total of 15K QA pairs across 32 academic and professional domains (22K QA pairs when also including English and MSA). The benchmark enables systematic assessment of LLM reasoning and comprehension beyond MSA, supp
, a new benchmark specifically designed to evaluate the capabilities of LLMs across five major Arabic dialects: Syrian, Egyptian, Emirati, Saudi, and Moroccan. Building upon the English-based MMLU-Redux
focused on bridging Arabic, STEM, and code, introducing a set of rigorous benchmarks to evaluate Arabic-enabled LLMs on scientific reasoning and programming tasks. It extended prior efforts by targeting domains that require structured problem-solving, such as mathematics, physics, and computer science, where Arabic benchmarks have been notably lacking. These initiatives, together with Arabic-centric models such as Ja
, ALLaM
, and Fanar
offers the most comprehensive attempt so far at LLM evaluation for dialectal Arabic, contributing 45K post-edited dialectal samples across Egyptian, Syrian, and Gulf varieties of Arabic and introducing a fine-grained cultural question–answering component. While it marks a significant step toward dialectal evaluation by extending MMLU-style tasks to Arabic dialectal varieties, its dataset is largely derived from mac
expands benchmarking into a multimodal setting by evaluating image captioning and visual question–answering across Jordanian, Emirati, Egyptian, and Moroccan Arabic dialects. The evaluation results revealed that current Arabic vision–language models (VLMs) struggle with dialect-specific visual understanding: even GPT-4V
) multiple-choice question–answering (MCQA) pairs into five dialects representing the geographical spread of the Arab World: Egypt (
This evaluation step showed that only about 5% of the translations contained some inaccuracies. Almost all dialectical translations had average assessments between good (4) and very good (5) levels, except for the UAE dialect, which was only marginally below good (at 3.94).
shows some dataset statistics: number of dialects, domains, questions, translations, including both average and total counts.
further zooms into the average length of the questions and the answers across the investigated dialects/languages in our dataset: we can see that the lengths are similar across the Arabic varieties, with English being slightly longer.
Average question and choice length (characters and words) across the dialects.
We made sure we included Arabic-enabled large language models that were developed in the Arab region, e.g., ALLaM
, Fanar
, and Jais
, in addition to recent, multilingual models of comparable sizes such as Google’s Gemma-3
jais-13b-chat
gemma-3-12b-it
Fanar-1-9B-Instruct
ALLaM-AI
ALLaM-7B-Instruct
jais-6p7b-chat
gemma-3-4b-it
Qwen
Qwen3-4B-Instruct*
jais-2p7b-chat
The evaluated language models. (* Based on Qwen2 language support)
jais-13b-chat
gemma-3-12b-it
Fanar-1-9B-Instruct
ALLaM-7B-Instruct
jais-6p7b-chat
gemma-3-4b-it
Qwen3-4B-Instruct
jais-2p7b-chat
Average
setting. (Average of 5 runs for the 32 different topics. Random chance =
Egyptian dialect
All the tasks use a multiple-choice format to maintain strict methodological alignment with MMLU. The model inference is performed using the log-likelihood evaluation mode, where each answer option is appended to the input prompt and the log-likelihood of that option appearing after the given prompt is output by the model. The option with the highest log-likelihood is chosen as the model’s answer, and this predicti
setting for QA. For each model–dialect pair, we report the average accuracy over the 32 domains with the experiment repeated five times. Based on these results, we make a number of interesting observations:
----HELMmodels
,
Gemini 2.5
,
GPT-4.1
,
GPT-5.1
and
Mistral Large
model families
Open-weights multilingual models —
DeepSeek v3.1
,
Falcon3
,
Llama 3.3
,
Llama 4
,
Qwen2.5
, and
Qwen3
model families
Open-weights models that were trained or fine-tuned specifically for the Arabic language —
AceGPT-v2
,
ALLaM
,
JAIS
, and
SILMA
model families
Results
The
leaderboard results
show that LLMs have made significant progress in Arabic language understanding over the last few years.
Arabic.AI LLM-X achieved the highest mean score, as well as the highest scores for AlGhafa, EXAMS, MadinahQA, AraTrust, ALRAGE, and Translated MMLU
Qwen3 235B A22B Instruct 2507 FP8 was the best performing open-weights model, with a mean score of 0.786.
Open-weights multilingual models performed well relative to closed-weights multilingual models. Out of the top 10 models, 4 models were multilingual open-weights models: Qwen3 235B A22B Instruct 2507 FP8, Llama 4 Maverick (17Bx128E) Instruct FP8, Qwen3-Next 80B A3B Instruct, and DeepSeek v3.1.
Open-weights models that were trained or fine-tuned specifically for the Arabic language underperformed compared to the other two model groups. However, this may be explained by the age of these models; the most recent model family in this group, AceGPT-v2, was released in October 2024, more than a year ago.
As with all HELM leaderboards, this leaderboard provides full transparency into all LLM requests and responses, and the results are
reproducible
using the
HELM open source framework
. We hope that this leaderboard will be a valuable resource for the Arabic NLP community.
Errata (2026-06-03)
v1.0.0
of the leaderboard was affected by a bug that caused the context to be omitted when evaluating models on context-based question answering in ArabicMMLU and MadinahQA. For more information, refer to GitHub pull requests
#4218
and
#4127
. This bug has been corrected in
v2.0.0
of the leaderboard, which caused slight changes to some scores. The results in this post refer to the
v1.0.0
of the leaderboard.
References
El Filali, A., Manel, A., Hussain, T., Alzubaidi, A., Cojocaru, R., Hacid, H., & Fourrier, C. (2025, March 24). The open arabic llm leaderboard 2.
https://huggingface.co/blog/leaderboard-arabic-v2
↩
↩
2
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### assistant · 2026-11-20T09:22:14.329Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\npython3 -I - <<'EOF'\nimport re,html\nt=open('dmmlu.html',errors='ignore').read()\nfor i,tb in enumerate(re.findall(r'<table.*?</table>',t,flags=re.S)):\n    rows=[]\n    for tr in re.findall(r'<tr.*?</tr>',tb,flags=re.S):\n        cells=[re.sub(r'\\s+',' ',html.unescape(re.sub(r'<[^>]+>','',c))).strip() for c in re.findall(r'<t[hd].*?</t[hd]>',tr,flags=re.S)]\n        rows.append(cells)\n    txt=' '.join(' '.join(r) for r in rows)\n    if 'Egypt' in txt and 'Qwen3' in txt:\n        print('TABLE',i)\n        for r in rows[:14]: print(' | '.join(r)[:300])\nEOF",
 "description": "Parse DialectalArabicMMLU result tables"
}
```

### user · 2026-11-20T09:22:15.319Z

**نتيجة أداة:**
```
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

### assistant · 2026-11-20T09:22:18.417Z

Status: LLM section verified (Ollama tags, HF licences). Now batch-checking GitHub repos for agents, STT and TTS (licence, activity).

### assistant · 2026-11-20T09:22:22.467Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\ngh_(){ curl -s -m 20 \"https://api.github.com/repos/$1\" | python3 -I -c \"\nimport sys,json\nd=json.load(sys.stdin)\nif 'full_name' not in d: print('$1','ERR',d.get('message')); sys.exit()\nl=d.get('license') or {}\nprint(d['full_name'],'| lic:',l.get('spdx_id'),'| stars:',d['stargazers_count'],'| pushed:',d['pushed_at'][:10],'| archived:',d['archived'],'|',(d.get('description') or '')[:90])\"; }\nfor r in NousResearch/hermes-agent NousResearch/Hermes-Function-Calling OpenInterpreter/open-interpreter OpenInterpreter/01 home-assistant/core open-webui/open-webui danny-avila/LibreChat Mintplex-Labs/anything-llm mudler/LocalAI block/goose cline/cline continuedev/continue All-Hands-AI/OpenHands OpenHands/OpenHands langgenius/dify n8n-io/n8n ollama/ollama ggml-org/llama.cpp lmstudio-ai/lms sst/opencode openclaw/openclaw ; do gh_ $r & done; wait",
 "description": "Query GitHub repo metadata for agent projects"
}
```

### assistant · 2026-11-20T09:22:26.838Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\ngh_(){ curl -s -m 20 \"https://api.github.com/repos/$1\" | python3 -I -c \"\nimport sys,json\nd=json.load(sys.stdin)\nif 'full_name' not in d: print('$1','ERR',d.get('message')); sys.exit()\nl=d.get('license') or {}\nprint(d['full_name'],'| lic:',l.get('spdx_id'),'| stars:',d['stargazers_count'],'| pushed:',d['pushed_at'][:10],'| archived:',d['archived'],'|',(d.get('description') or '')[:80])\"; }\nfor r in openai/whisper SYSTRAN/faster-whisper speaches-ai/speaches fedirz/faster-whisper-server ggml-org/whisper.cpp huggingface/distil-whisper huggingface/transformers.js xenova/whisper-web alphacep/vosk-api alphacep/vosk-server k2-fsa/sherpa-onnx k2-fsa/sherpa-ncnn NVIDIA/NeMo facebookresearch/seamless_communication facebookresearch/fairseq rhasspy/piper OHF-Voice/piper1-gpl coqui-ai/TTS idiap/coqui-ai-TTS rhasspy/wyoming-piper OHF-Voice/wyoming-faster-whisper kokoro-onnx/kokoro-onnx hexgrad/kokoro mozilla/TTS m-bain/whisperX ; do gh_ $r & done; wait",
 "description": "Query GitHub metadata for STT and TTS projects"
}
```

### user · 2026-11-20T09:22:28.444Z

<details><summary>نتيجة أداة (2666 حرف)</summary>

```
n8n-io/n8n | lic: NOASSERTION | stars: 211484 | pushed: 2026-11-20 | archived: False | Fair-code workflow automation platform with native AI capabilities. Combine visual buildin
open-webui/open-webui | lic: NOASSERTION | stars: 159133 | pushed: 2026-11-20 | archived: False | User-friendly AI Interface (Supports Ollama, OpenAI API, ...)
home-assistant/core | lic: Apache-2.0 | stars: 92397 | pushed: 2026-11-20 | archived: False | :house_with_garden: Open source home automation that puts local control and privacy first.
openinterpreter/01 | lic: AGPL-3.0 | stars: 5165 | pushed: 2024-11-01 | archived: False | The #1 open-source voice interface for desktop, mobile, and ESP32 chips.
NousResearch/hermes-agent | lic: MIT | stars: 264852 | pushed: 2026-11-20 | archived: False | The agent that grows with you
NousResearch/Hermes-Function-Calling | lic: MIT | stars: 1504 | pushed: 2025-12-22 | archived: False | 
danny-avila/LibreChat ERR Moved Permanently
OpenInterpreter/open-interpreter ERR Moved Permanently
ggml-org/llama.cpp | lic: MIT | stars: 135804 | pushed: 2026-11-20 | archived: False | LLM inference in C/C++
block/goose ERR Moved Permanently
langgenius/dify | lic: NOASSERTION | stars: 161552 | pushed: 2026-11-20 | archived: False | Build Agentic workflows, RAG pipelines, with rich AI model and tool support on one collabo
Mintplex-Labs/anything-llm | lic: MIT | stars: 68457 | pushed: 2026-11-20 | archived: False | Stop renting your intelligence. Own it with AnythingLLM. Everything you need for a powerfu
mudler/LocalAI | lic: MIT | stars: 50462 | pushed: 2026-11-20 | archived: False | LocalAI is the open-source AI engine. Run any model - LLMs, vision, voice, image, video - 
cline/cline | lic: Apache-2.0 | stars: 71786 | pushed: 2026-11-19 | archived: False | Autonomous coding agent as an SDK, IDE extension, or CLI assistant.
continuedev/continue | lic: Apache-2.0 | stars: 36525 | pushed: 2026-11-20 | archived: False | open-source coding agent
All-Hands-AI/OpenHands ERR Moved Permanently
sst/opencode ERR Moved Permanently
openclaw/openclaw | lic: MIT | stars: 394867 | pushed: 2026-11-20 | archived: False | The AI that really does things. Any OS. Any Platform. The lobster way. 🦞 
OpenHands/OpenHands | lic: MIT | stars: 93885 | pushed: 2026-11-20 | archived: False | 🙌 OpenHands: AI-Driven Development
ollama/ollama | lic: MIT | stars: 187713 | pushed: 2026-11-19 | archived: False | Get up and running with Kimi, GLM, MiniMax, DeepSeek, gpt-oss, Qwen, Gemma and other model
lmstudio-ai/lms | lic: MIT | stars: 5443 | pushed: 2026-11-17 | archived: False | LM Studio CLI
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### user · 2026-11-20T09:22:30.344Z

<details><summary>نتيجة أداة (3476 حرف)</summary>

```
ggml-org/whisper.cpp | lic: MIT | stars: 55357 | pushed: 2026-11-20 | archived: False | Port of OpenAI's Whisper model in C/C++
rhasspy/wyoming-piper ERR Moved Permanently
facebookresearch/seamless_communication | lic: NOASSERTION | stars: 11909 | pushed: 2026-09-08 | archived: False | Foundational Models for State-of-the-Art Speech and Text Translation
coqui-ai/TTS | lic: MPL-2.0 | stars: 46258 | pushed: 2024-08-16 | archived: False | 🐸💬 - a deep learning toolkit for Text-to-Speech, battle-tested in research and p
fedirz/faster-whisper-server ERR Moved Permanently
SYSTRAN/faster-whisper | lic: MIT | stars: 26885 | pushed: 2026-11-12 | archived: False | Faster Whisper transcription with CTranslate2
openai/whisper | lic: MIT | stars: 113149 | pushed: 2026-08-31 | archived: False | Robust Speech Recognition via Large-Scale Weak Supervision
speaches-ai/speaches | lic: MIT | stars: 3774 | pushed: 2026-11-20 | archived: False | 
huggingface/distil-whisper | lic: MIT | stars: 4116 | pushed: 2025-01-08 | archived: False | Distilled variant of Whisper for speech recognition. 6x faster, 50% smaller, wit
OHF-Voice/wyoming-faster-whisper | lic: MIT | stars: 410 | pushed: 2026-11-19 | archived: False | Wyoming protocol server for faster whisper speech to text system
rhasspy/piper | lic: MIT | stars: 11337 | pushed: 2025-08-26 | archived: True | A fast, local neural text to speech system
alphacep/vosk-server | lic: Apache-2.0 | stars: 1263 | pushed: 2025-07-25 | archived: False | WebSocket, gRPC and WebRTC speech recognition server based on Vosk and Kaldi lib
NVIDIA/NeMo ERR Moved Permanently
k2-fsa/sherpa-ncnn | lic: Apache-2.0 | stars: 1801 | pushed: 2026-11-12 | archived: False | Real-time speech recognition and voice activity detection (VAD) using next-gen K
huggingface/transformers.js | lic: Apache-2.0 | stars: 16436 | pushed: 2026-11-18 | archived: False | State-of-the-art Machine Learning for the web. Run 🤗 Transformers directly in yo
kokoro-onnx/kokoro-onnx ERR Not Found
idiap/coqui-ai-TTS | lic: MPL-2.0 | stars: 2356 | pushed: 2026-11-16 | archived: False | 🐸💬 - a deep learning toolkit for Text-to-Speech, battle-tested in research and p
hexgrad/kokoro | lic: Apache-2.0 | stars: 10253 | pushed: 2025-08-06 | archived: False | https://hf.co/hexgrad/Kokoro-82M
m-bain/whisperX | lic: BSD-2-Clause | stars: 25513 | pushed: 2026-11-12 | archived: False | WhisperX:  Automatic Speech Recognition with Word-level Timestamps (& Diarizatio
xenova/whisper-web | lic: None | stars: 3344 | pushed: 2024-10-01 | archived: False | ML-powered speech recognition directly in your browser
facebookresearch/fairseq | lic: MIT | stars: 32204 | pushed: 2025-09-30 | archived: True | Facebook AI Research Sequence-to-Sequence Toolkit written in Python.
mozilla/TTS | lic: MPL-2.0 | stars: 10187 | pushed: 2023-11-09 | archived: False | :robot: :speech_balloon: Deep learning for Text to Speech  (Discussion forum: ht
k2-fsa/sherpa-onnx | lic: Apache-2.0 | stars: 16061 | pushed: 2026-11-20 | archived: False | Speech-to-text, text-to-speech, speaker diarization, speech enhancement, source 
alphacep/vosk-api | lic: Apache-2.0 | stars: 15274 | pushed: 2026-10-15 | archived: False | Offline speech recognition API for Android, iOS, Raspberry Pi and servers with P
OHF-Voice/piper1-gpl | lic: GPL-3.0 | stars: 6333 | pushed: 2026-11-19 | archived: False | Fast and local neural text-to-speech engine
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### assistant · 2026-11-20T09:22:37.186Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\ngh_(){ curl -sL -m 20 \"https://api.github.com/repos/$1\" | python3 -I -c \"\nimport sys,json\nd=json.load(sys.stdin)\nif 'full_name' not in d: print('$1','ERR',d.get('message')); sys.exit()\nl=d.get('license') or {}\nprint(d['full_name'],'| lic:',l.get('spdx_id'),'| stars:',d['stargazers_count'],'| pushed:',d['pushed_at'][:10],'| archived:',d['archived'],'|',(d.get('description') or '')[:80])\"; }\nfor r in danny-avila/LibreChat OpenInterpreter/open-interpreter block/goose sst/opencode NVIDIA/NeMo rhasspy/wyoming-piper fedirz/faster-whisper-server; do gh_ $r & done; wait\ncurl -sL -m 25 https://raw.githubusercontent.com/NousResearch/hermes-agent/main/README.md -o hermes_readme.md; wc -c hermes_readme.md; grep -inE \"mcp|openai|ollama|voice|speech|telegram|whisper|tts|license|install|curl|model|provider|openrouter|gateway|skill|memory\" hermes_readme.md | head -60 | cut -c1-260",
 "description": "Follow redirects, read Hermes agent README"
}
```

### user · 2026-11-20T09:22:39.331Z

<details><summary>نتيجة أداة (8485 حرف)</summary>

```
rhasspy/wyoming-piper ERR API rate limit exceeded for 196.136.31.109. (But here's the good news: Authenticated requests get a higher rate limit. Check out the documentation for more details.)
aaif-goose/goose | lic: Apache-2.0 | stars: 56809 | pushed: 2026-11-20 | archived: False | an open source, extensible AI agent that goes beyond code suggestions - install,
anomalyco/opencode | lic: MIT | stars: 228130 | pushed: 2026-11-20 | archived: False | The open source coding agent.
openinterpreter/openinterpreter | lic: Apache-2.0 | stars: 68920 | pushed: 2026-11-20 | archived: False | A coding agent for open models like Kimi K3.1 and GLM 5.3
LibreChat-AI/LibreChat | lic: MIT | stars: 47364 | pushed: 2026-11-20 | archived: False | Enhanced ChatGPT Clone: Features Agents, MCP, Skills, DeepSeek, Anthropic, AWS, 
speaches-ai/speaches | lic: MIT | stars: 3774 | pushed: 2026-11-20 | archived: False | 
NVIDIA-NeMo/Speech | lic: Apache-2.0 | stars: 18769 | pushed: 2026-11-20 | archived: False | A scalable generative AI framework built for researchers and developers working 
   17496 hermes_readme.md
12:  <a href="https://github.com/NousResearch/hermes-agent/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License: MIT"></a>
19:**The self-improving AI agent built by [Nous Research](https://nousresearch.com).** It's the only agent with a built-in learning loop — it creates skills from experience, improves them during use, nudges itself to persist knowledge, searches its own past 
21:Use any model you want — [Nous Portal](https://portal.nousresearch.com), OpenRouter, OpenAI, your own endpoint, and [many others](https://hermes-agent.nousresearch.com/docs/integrations/providers). Switch with `hermes model` — no code changes, no lock-i
25:<tr><td><b>Lives where you do</b></td><td>Telegram, Discord, Slack, WhatsApp, Signal, and CLI — all from a single gateway process. Voice memo transcription, cross-platform conversation continuity.</td></tr>
26:<tr><td><b>A closed learning loop</b></td><td>Agent-curated memory with periodic nudges. Autonomous skill creation after complex tasks. Skills self-improve during use. FTS5 session search with LLM summarization for cross-session recall. <a href="https://git
28:<tr><td><b>Delegates and parallelizes</b></td><td>Spawn isolated subagents for parallel workstreams. In Desktop, choose their provider, model, and limits under Settings → Model → Subagents, then Apply the complete route. Write Python scripts that call t
30:<tr><td><b>Research-ready</b></td><td>Batch trajectory generation, trajectory compression for training the next generation of tool-calling models.</td></tr>
35:## Quick Install
40:curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
45:> **Heads up:** Native Windows runs Hermes without WSL — CLI, gateway, TUI, and tools all work natively. If you'd rather use WSL2, the Linux/macOS one-liner above works there too. Found a bug? Please [file issues](https://github.com/NousResearch/hermes-ag
50:iex (irm https://hermes-agent.nousresearch.com/install.ps1)
53:The source installer delegates Python 3.14, Node.js, npm, pnpm, ripgrep, FFmpeg,
56:See [installation methods](https://hermes-agent.nousresearch.com/docs/getting-started/installation)
57:for the separate MSIX/App Installer package and its update ownership.
59:> **Android / Termux:** A signed APT repository is available for aarch64 devices, with a `stable` channel (tagged releases) and a prerelease `canary` channel. The package includes Python, Node.js, and the TUI. Use the [Termux guide](https://hermes-agent.nou
61:> **Windows:** Native Windows is fully supported — the PowerShell one-liner above installs everything. If you'd rather use WSL2, the Linux command works there too. Native Windows install lives under `%LOCALAPPDATA%\hermes`; WSL2 installs under `~/.hermes`
63:After installation:
74:If your antivirus (Bitdefender, Windows Defender, etc.) quarantines `uv.exe` from the Hermes `bin` folder (`%LOCALAPPDATA%\hermes\bin\uv.exe`), this is a **false positive**. The file is Astral's `uv` — the Rust Python package manager Hermes bundles to man
79:# Install GitHub CLI if needed
80:winget install --id GitHub.cli
111:hermes model        # Choose your LLM provider and model
115:hermes gateway      # Start the messaging gateway (Telegram, Discord, etc.)
127:Hermes works with whatever provider you want — that's not changing. But if you'd rather not collect five separate API keys for the model, web search, image generation, TTS, and a cloud browser, **[Nous Portal](https://portal.nousresearch.com)** covers al
129:- **300+ models** — pick any of them with `/model <name>`
130:- **Tool Gateway** — web search, image generation (FAL), text-to-speech (OpenAI), cloud browser (Browser Use), all routed through your sub. No extra accounts.
132:One command from a fresh install:
138:That logs you in via OAuth, sets Nous as your provider, and turns on the Tool Gateway. Check what's wired up any time with `hermes portal info`. Full details on the [Tool Gateway docs page](https://hermes-agent.nousresearch.com/docs/user-guide/features/too
140:You can still bring your own keys per-tool whenever you want — the gateway is per-backend, not all-or-nothing.
146:Hermes has two entry points: start the terminal UI with `hermes`, or run the gateway and talk to it from Telegram, Discord, Slack, WhatsApp, Signal, or Email. Once you're in a conversation, many slash commands are shared across both interfaces.
150:| Start chatting                 | `hermes`                                      | Run `hermes gateway setup` + `hermes gateway start`, then send the bot a message |
152:| Change model                   | `/model [provider:model]`                     | `/model [provider:model]`                                                        |
156:| Browse skills                  | `/skills` or `/<skill-name>`                  | `/<skill-name>`                                                                  |
160:For the full command lists, see the [CLI guide](https://hermes-agent.nousresearch.com/docs/user-guide/cli) and the [Messaging Gateway guide](https://hermes-agent.nousresearch.com/docs/user-guide/messaging).
170:| [Quickstart](https://hermes-agent.nousresearch.com/docs/getting-started/quickstart)                 | Install → setup → first conversation in 2 minutes          |
172:| [Configuration](https://hermes-agent.nousresearch.com/docs/user-guide/configuration)                | Config file, providers, models, all options                |
173:| [Messaging Gateway](https://hermes-agent.nousresearch.com/docs/user-guide/messaging)                | Telegram, Discord, Slack, WhatsApp, Signal, Home Assistant |
176:| [Skills System](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills)              | Procedural memory, Skills Hub, creating skills             |
177:| [Memory](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory)                     | Persistent memory, user profiles, best practices           |
178:| [MCP Integration](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp)               | Connect any MCP server for extended capabilities           |
190:If you're coming from OpenClaw, Claude Code, Codex CLI or Cursor, Hermes can import your settings, memories and skills (and, for OpenClaw, API keys when you ask for them).
192:**During setup:** `hermes setup` asks whether to import from another agent, pre-selects the ones it finds (`~/.openclaw`, `~/.claude`, `~/.codex`, `~/.cursor`), installs the official `agent-importers` plugin and runs the import with a preview first.
194:**Anytime after install:**
197:hermes plugins install agent-importers          # once per profile
207:- **Memories** — MEMORY.md and USER.md entries
208:- **Skills** — user-created skills → `~/.hermes/skills/openclaw-imports/`
211:- **API keys** — allowlisted secrets (Telegram, OpenRouter, OpenAI, Anthropic, ElevenLabs), only with `--migrate-secrets`
212:- **TTS assets** — workspace audio files
232:- 📚 [Skills Hub](https://agentskills.io)
234:- 🔌 [computer-use-linux](https://github.com/avifenesh/computer-use-linux) — Linux desktop-control MCP server for Hermes and other MCP hosts, with AT-SPI accessibility trees, Wayland/X11 input, screenshots, and compositor window targeting.
239:## License
241:MIT — see [LICENSE](LICENSE).
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### assistant · 2026-11-20T09:22:46.547Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\nfor u in docs/user-guide/features/mcp docs/integrations/providers docs/user-guide/features/api-server docs/user-guide/messaging; do f=hd_$(echo $u|tr '/' '_').html; curl -sL -m 25 https://hermes-agent.nousresearch.com/$u -o $f -w \"$u %{http_code} %{size_download}\\n\"; done\npython3 -I $S/strip.py hd_docs_user-guide_features_mcp.html | grep -inE \"stdio|http|sse|streamable|oauth|config.yaml|mcp_servers|url:|command:\" | head -14 | cut -c1-240\necho ---prov; python3 -I $S/strip.py hd_docs_integrations_providers.html | grep -inE \"ollama|lm studio|openai-compatible|custom endpoint|groq|gemini|openrouter|base_url|localhost\" | head -14 | cut -c1-240\necho ---api; python3 -I $S/strip.py hd_docs_user-guide_features_api-server.html | head -30 | cut -c1-240\ncurl -sL -m 25 \"https://hermes-agent.nousresearch.com/docs/sitemap.xml\" | grep -oE \"<loc>[^<]*(api|openai|voice|acp|server)[^<]*\" | head -15",
 "description": "Read Hermes Agent docs for MCP and API"
}
```

### user · 2026-11-20T09:22:50.529Z

<details><summary>نتيجة أداة (2670 حرف)</summary>

```
docs/user-guide/features/mcp 200 207421
docs/integrations/providers 200 345883
docs/user-guide/features/api-server 200 186373
docs/user-guide/messaging 200 198285
51:mcp_servers
53:config.yaml
64:Local stdio servers and remote HTTP MCP servers in the same config
72:~/.hermes/config.yaml
74:mcp_servers
118:For an OAuth entry the card shows the authorization link.
148:linear       enabled                Linear issue/project management (remote OAuth)
160:mcp_servers
173:OAuth
175:auth: oauth
178:OAuth
187:self-hosted instance over HTTP with browser OAuth. No local bridge or n8n
197:/mcp-server/http
203:Complete browser OAuth. If needed, run
---prov
39:This page covers setting up inference providers for Hermes Agent — from cloud APIs like OpenRouter and Anthropic, to self-hosted endpoints like Ollama and vLLM, to advanced routing and fallback configurations. You need at least one pro
58:OpenRouter
59:OPENROUTER_API_KEY
63:hermes auth add openrouter --type oauth
64:(browser login via OpenRouter's PKCE flow; stores a key in the credential pool)
168:model.base_url
323:Google / Gemini
326:GEMINI_API_KEY
330:gemini
344:OPENAI_BASE_URL
363:Ollama Cloud
365:→ "Ollama Cloud" (provider:
366:ollama-cloud
367:; cloud-hosted Ollama API)
---api
API Server | Hermes Agent
Skip to main content
Hermes Agent
Docs
Marketplace
Download
English
English
简体中文
Home
GitHub
Discord
Search
User Stories & Use Cases
Browse the Marketplace
Getting Started
Using Hermes
Features
Overview
Tool Gateway
Core
Automation
Media & Web
Management
Hermes Web Dashboard
Extending the Dashboard
API Server
Subscription Proxy
Skills
Messaging Platforms
<loc>https://hermes-agent.nousresearch.com/docs/developer-guide/acp-internals
<loc>https://hermes-agent.nousresearch.com/docs/developer-guide/observer-hooks
<loc>https://hermes-agent.nousresearch.com/docs/developer-guide/plugins/public-api
<loc>https://hermes-agent.nousresearch.com/docs/developer-guide/subagent-lifecycle-api
<loc>https://hermes-agent.nousresearch.com/docs/guides/use-voice-mode-with-hermes
<loc>https://hermes-agent.nousresearch.com/docs/user-guide/features/acp
<loc>https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server
<loc>https://hermes-agent.nousresearch.com/docs/user-guide/features/codex-app-server-runtime
<loc>https://hermes-agent.nousresearch.com/docs/user-guide/features/voice-mode
<loc>https://hermes-agent.nousresearch.com/docs/user-guide/skills/optional/gaming/gaming-minecraft-modpack-server
<loc>https://hermes-agent.nousresearch.com/docs/user-guide/skills/optional/web-development/web-development-har-derived-api-client
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### assistant · 2026-11-20T09:22:54.506Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\npython3 -I $S/strip.py hd_docs_user-guide_features_api-server.html | awk 'NR>60' | grep -vE \"^(English|Home|Docs)$\" | head -45 | cut -c1-300\necho ----voice; curl -sL -m 25 https://hermes-agent.nousresearch.com/docs/user-guide/features/voice-mode -o hd_voice.html; python3 -I $S/strip.py hd_voice.html | grep -inE \"whisper|stt|tts|edge|piper|arabic|language|local|groq|wake|browser|elevenlabs|openai\" | head -22 | cut -c1-260",
 "description": "Read Hermes API server and voice docs"
}
```

### user · 2026-11-20T09:22:56.299Z

<details><summary>نتيجة أداة (2212 حرف)</summary>

```
change-me-local-dev
# Optional: only if a browser must call Hermes directly
# API_SERVER_CORS_ORIGINS=http://localhost:3000
2. Start the gateway
​
hermes gateway
You'll see:
[API Server] API server listening on http://127.0.0.1:8642
3. Connect a frontend
​
Point any OpenAI-compatible client at
http://localhost:8642/v1
:
# Test with curl
curl
http://localhost:8642/v1/chat/completions
\
-H
"Authorization: Bearer change-me-local-dev"
\
-H
"Content-Type: application/json"
\
-d
'{"model": "hermes-agent", "messages": [{"role": "user", "content": "Hello!"}]}'
Or connect Open WebUI, LobeChat, or any other frontend — see the
Open WebUI integration guide
for step-by-step instructions.
Conversation and terminal-result semantics
​
API requests use the gateway's durable admission queue. Structured image content stays
structured through execution; it is not interpreted as a gateway slash command.
/v1/runs
and
/v1/responses
retain the conversation declared by
X-Hermes-Session-Key
. An explicit session or response chain takes precedence and
does not transfer its conversation identity to a different header.
A nonempty
/v1/runs
conversation_history
is authoritative, even with an explicit
session_id
. Otherwise session continuation loads history when the turn executes,
----voice
25:Wake Word
28:Browser
36:Voice & TTS
56:Wake Word
89:OpenAI TTS via the Tool Gateway — no separate OpenAI key needed. On a fresh install,
131:, and Faster-Whisper where supported
132:CLI audio and optional local STT
140:tts-premium
141:elevenlabs
142:ElevenLabs TTS provider
143:Local Faster-Whisper is excluded on native Windows ARM64 and Intel macOS.
144:Use a cloud or command-based STT provider on those targets.
147:the microphone/playback dependencies without local STT. The
150:not mean every voice or wake engine.
151:NeuTTS is a separate optional runtime and downloads models on first use.
169:# for NeuTTS
179:# for NeuTTS
194:Local NeuTTS provider
200:# Speech-to-Text — local provider needs NO key at all
201:# PM prepares local Faster-Whisper on supported targets; no STT API key is needed.
202:GROQ_API_KEY
205:# Groq Whisper — fast, free tier (cloud)
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### assistant · 2026-11-20T09:23:03.245Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\npython3 -I $S/strip.py hd_voice.html | sed -n 50,100p | cut -c1-260 | tr '\\n' ' ' | cut -c1-2500; echo\necho ---pypi; curl -s -m 20 https://pypi.org/pypi/ctranslate2/json | python3 -I -c \"\nimport sys,json\nd=json.load(sys.stdin);print(d['info']['version'])\nfs=[f['filename'] for f in d['urls']]\nprint([f for f in fs if 'macosx' in f])\"\ncurl -s -m 20 https://pypi.org/pypi/faster-whisper/json | python3 -I -c \"\nimport sys,json\nd=json.load(sys.stdin);print('faster-whisper',d['info']['version'],d['info']['license'] or d['info'].get('license_expression'))\"\ncurl -s -m 20 https://pypi.org/pypi/speaches/json | python3 -I -c \"\nimport sys,json\nd=json.load(sys.stdin);print('speaches',d['info']['version'],d['info'].get('requires_python'))\" ",
 "description": "Check Hermes wake word, PyPI ctranslate2 wheels"
}
```

### assistant · 2026-11-20T09:23:06.097Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\nq(){ curl -s -m 20 \"https://huggingface.co/api/models?search=$1&limit=${2:-8}&sort=downloads&direction=-1\" | python3 -I -c \"\nimport sys,json\nfor d in json.load(sys.stdin): print(d['id'],'| dl',d.get('downloads'),'|',[t.replace('license:','') for t in d.get('tags',[]) if t.startswith('license:')])\"; }\necho --egy-whisper; q whisper+egyptian 8; echo --arabic-whisper; q whisper+arabic 10; echo --mms; q mms-1b-all 3; echo --seamless; q seamless-m4t 5; echo --fastconformer; q arabic+fastconformer 5; echo --cohere-transcribe; q cohere-transcribe 6; echo --jais-asr; q Jais-ASR 3",
 "description": "Search HF for Arabic and Egyptian ASR models"
}
```

### user · 2026-11-20T09:23:09.055Z

<details><summary>نتيجة أداة (2501 حرف)</summary>

```
Exit code 1
Voice Mode Hermes Agent supports full voice interaction across CLI and messaging platforms. Talk to the agent using your microphone, hear spoken replies, and have live voice conversations in Discord voice channels. If you want a practical setup walkthrough with recommended configurations and real usage patterns, see Use Voice Mode with Hermes . For hands-free session start — saying "hey hermes" (or any phrase) to open a fresh voice session on the CLI, TUI, or desktop app — see Wake Word . Prerequisites ​ Before using voice features, make sure you have: Hermes Agent installed — via the install script (see Installation ) An LLM provider configured — run hermes model or set your preferred provider credentials in ~/.hermes/.env A working base setup — run hermes to verify the agent responds to text before enabling voice tip The ~/.hermes/ directory and default config.yaml are created automatically the first time you run hermes . You only need to create ~/.hermes/.env manually for API keys. Nous Portal covers both A paid Nous Portal subscription supplies the LLM (step 2) and OpenAI TTS via the Tool Gateway — no separate OpenAI key needed. On a fresh install, hermes setup --portal wires both up at once. Overview ​ Feature Platform Description Interactive Voice CLI Press Ctrl+B to record, agent auto-detects silence and responds Auto Voice Reply 
---pypi
4.9.0
['ctranslate2-4.9.0-cp310-cp310-macosx_11_0_arm64.whl', 'ctranslate2-4.9.0-cp310-cp310-macosx_11_0_x86_64.whl', 'ctranslate2-4.9.0-cp311-cp311-macosx_11_0_arm64.whl', 'ctranslate2-4.9.0-cp311-cp311-macosx_11_0_x86_64.whl', 'ctranslate2-4.9.0-cp312-cp312-macosx_11_0_arm64.whl', 'ctranslate2-4.9.0-cp312-cp312-macosx_11_0_x86_64.whl', 'ctranslate2-4.9.0-cp313-cp313-macosx_11_0_arm64.whl', 'ctranslate2-4.9.0-cp313-cp313-macosx_11_0_x86_64.whl', 'ctranslate2-4.9.0-cp314-cp314-macosx_11_0_arm64.whl', 'ctranslate2-4.9.0-cp314-cp314-macosx_11_0_x86_64.whl', 'ctranslate2-4.9.0-cp314-cp314t-macosx_11_0_arm64.whl', 'ctranslate2-4.9.0-cp314-cp314t-macosx_11_0_x86_64.whl', 'ctranslate2-4.9.0-cp315-cp315-macosx_11_0_arm64.whl', 'ctranslate2-4.9.0-cp315-cp315-macosx_11_0_x86_64.whl', 'ctranslate2-4.9.0-cp315-cp315t-macosx_11_0_arm64.whl', 'ctranslate2-4.9.0-cp315-cp315t-macosx_11_0_x86_64.whl', 'ctranslate2-4.9.0-cp39-cp39-macosx_11_0_arm64.whl', 'ctranslate2-4.9.0-cp39-cp39-macosx_11_0_x86_64.whl']
faster-whisper 1.2.1 MIT
Traceback (most recent call last):
  File "<string>", line 3, in <module>
KeyError: 'info'
```

</details>

### user · 2026-11-20T09:23:13.029Z

<details><summary>نتيجة أداة (2541 حرف)</summary>

```
--egy-whisper
mohammedaly22/whisper-large-v3-turbo-egyptian-code-switching | dl 797 | ['mit']
MAdel121/whisper-small-egyptian-arabic | dl 381 | ['mit']
IbrahimAmin/code-switched-egyptian-arabic-whisper-small | dl 366 | ['apache-2.0']
AbdelrahmanHassan/whisper-large-v3-egyptian-arabic | dl 208 | ['apache-2.0']
moeshawky/faster-whisper-small-egyptian-arabic | dl 143 | ['mit']
maryamas222/whisper-large-v3-egyptian-lora-v4 | dl 81 | ['apache-2.0']
RingoJet/whisper-small-egyptian-arabic-mgb3 | dl 75 | ['apache-2.0']
nabbra/whisper-medium-egyptian-arabic-ct2 | dl 51 | ['apache-2.0']
--arabic-whisper
oddadmix/whisper-large-v3-arabic-dialectal-v2 | dl 1516 | ['apache-2.0']
oddadmix/whisper-large-v3-turbo-arabic-dialectal-v2 | dl 1357 | ['apache-2.0']
oddadmix/whisper-large-v3-turbo-arabic-dialectal | dl 903 | ['apache-2.0']
MohamedRashad/Arabic-Whisper-CodeSwitching-Edition | dl 396 | ['gpl-3.0']
MAdel121/whisper-small-egyptian-arabic | dl 381 | ['mit']
IbrahimAmin/code-switched-egyptian-arabic-whisper-small | dl 366 | ['apache-2.0']
Omar10lfc/whisper-large-v3-turbo-arabic-ct2-int8 | dl 307 | ['apache-2.0']
Omar10lfc/whisper-small-arabic-ct2-int8 | dl 260 | ['apache-2.0']
Omar10lfc/whisper-large-v3-arabic-ct2-int8 | dl 239 | ['apache-2.0']
AbdelrahmanHassan/whisper-large-v3-egyptian-arabic | dl 208 | ['apache-2.0']
--mms
facebook/mms-1b-all | dl 234617 | ['cc-by-nc-4.0']
OpenVoiceOS/mms-1b-all-onnx | dl 112 | ['cc-by-nc-4.0']
Xenova/mms-1b-all | dl 92 | []
--seamless
facebook/seamless-m4t-v2-large | dl 332027 | ['cc-by-nc-4.0']
facebook/hf-seamless-m4t-medium | dl 7383 | ['cc-by-nc-4.0']
huggingface-mic/seamless-m4t-v2-large-mic | dl 2375 | []
facebook/hf-seamless-m4t-large | dl 699 | ['cc-by-nc-4.0']
nphearum/seamless-m4t-v2-large | dl 53 | ['cc-by-nc-4.0']
--fastconformer
abdullahtb/FastConformer-Arabic-SADA-Finetune-SAREI | dl 24 | ['apache-2.0']
--cohere-transcribe
handy-computer/cohere-transcribe-03-2026-gguf | dl 965694 | ['apache-2.0']
handy-computer/cohere-transcribe-arabic-07-2026-gguf | dl 174728 | ['apache-2.0']
CohereLabs/cohere-transcribe-arabic-07-2026 | dl 136694 | ['apache-2.0']
CohereLabs/cohere-transcribe-03-2026 | dl 88342 | ['apache-2.0']
cstr/cohere-transcribe-03-2026-GGUF | dl 7159 | ['apache-2.0']
BarathwajAnandan/cohere-transcribe-03-2026-CoreML-6bit | dl 6160 | ['gpl-3.0']
--jais-asr
IFM/Jais-ASR | dl 11718 | ['apache-2.0']
IFM/Jais-ASR-W4A16-AWQ | dl 8627 | ['apache-2.0']
IFM/Jais-ASR-GGUF | dl 2767 | ['apache-2.0']
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### assistant · 2026-11-20T09:23:19.635Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\ncard(){ curl -sL -m 25 \"https://huggingface.co/$1/raw/main/README.md\" -o card_$(echo $1|tr '/' '_').md; }\nfor m in CohereLabs/cohere-transcribe-arabic-07-2026 IFM/Jais-ASR oddadmix/whisper-large-v3-turbo-arabic-dialectal-v2 AbdelrahmanHassan/whisper-large-v3-egyptian-arabic mohammedaly22/whisper-large-v3-turbo-egyptian-code-switching MAdel121/whisper-small-egyptian-arabic nabbra/whisper-medium-egyptian-arabic-ct2; do card $m; done\nfor f in card_*.md; do echo \"=========== $f ($(wc -c <$f))\"; grep -iE \"wer|cer|egypt|dialect|parameter|size|arabic|params|license|latency|rtfx|real-time|languages|mgb|dataset\" $f | head -14 | cut -c1-260; done",
 "description": "Read ASR model cards for WER and sizes"
}
```

### user · 2026-11-20T09:23:23.829Z

<details><summary>نتيجة أداة (6101 حرف)</summary>

```
=========== card_AbdelrahmanHassan_whisper-large-v3-egyptian-arabic.md (    3558)
license: apache-2.0
- arabic
- egyptian-arabic
datasets:
- MightyStudent/Egyptian-ASR-MGB-3
- wer
- name: AbdelrahmanHassan/whisper-large-v3-egyptian-arabic
    dataset:
      name: Egyptian-ASR-MGB-3
      type: MightyStudent/Egyptian-ASR-MGB-3
    - type: wer
# Whisper Large V3 Fine-tuned for Egyptian Arabic
This model is a fine-tuned version of [openai/whisper-large-v3](https://huggingface.co/openai/whisper-large-v3) on the [Egyptian-ASR-MGB-3](https://huggingface.co/datasets/MightyStudent/Egyptian-ASR-MGB-3) dataset.
This model has been fine-tuned using LoRA (Low-Rank Adaptation) to improve automatic speech recognition performance on Egyptian Arabic dialect.
=========== card_CohereLabs_cohere-transcribe-arabic-07-2026.md (     151)
Access to model CohereLabs/cohere-transcribe-arabic-07-2026 is restricted. You must have access to it and be authenticated to access it. Please log in.
=========== card_IFM_Jais-ASR.md (   37725)
license: apache-2.0
- arabic
- arabic-dialects
Jais-ASR is IFM's state-of-the-art speech recognition model for Arabic as it is spoken: Modern Standard Arabic and dialects from 19 Arab countries, with natural code-switching into English, French, Spanish, and Italian. Based on Jais-3-4B, it adds optional dia
  <img src="assets/jais-asr-benchmarks.png" alt="Average word and character error rates on the Open Universal Arabic ASR Leaderboard. Jais-ASR has the lowest of both, 22.85% WER and 8.37% CER, ahead of Audar-ASR-V1-Turbo, Speechmatics Melia 1, ElevenLabs Scrib
- **Leading performance in Arabic ASR.** Jais-ASR has the lowest average error rates on the [Open Universal Arabic ASR Leaderboard](https://github.com/Natural-Language-Processing-Elm/open_universal_arabic_asr_leaderboard), 22.85% WER and 8.37% CER, ahead of ev
- **Built for Arabic as it is spoken in real life.** MSA and dialects across 19 countries, natural code-switching with English, French, Spanish, and Italian, and robust transcription in noisy, real-world recordings.
- **Accurate and faithful.** Optional diacritization, built-in language and dialect identification, and transcripts designed to avoid memorized boilerplate, repetition loops, and translating speech instead of transcribing it. When there is no speech, the model
The [Open Universal Arabic ASR Leaderboard](https://github.com/Natural-Language-Processing-Elm/open_universal_arabic_asr_leaderboard) covers six public test sets spanning read speech, broadcast media, and conversational dialects, in clean and noisy conditions.
<div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;margin:0 auto;padding:8px 0 16px;overflow-x:auto"><table style="display:table;width:100%;table-layout:fixed;border-collapse:collapse;font-size:12px;margin:0"><thead><tr><th s
<p style="font-size:1.25em;line-height:1.6">Error rates in %; lower is better. Average is the macro-average over the six test sets. Jais-ASR was measured with the leaderboard's evaluation script. Scores for the other open-weight models are taken from the leade
Jais-ASR brings Arabic speech transcription, code-switching, diacritization, and language identification into one model, with controls to tailor the output to your application.
- **Transcribe multilingual speech as spoken.** Enable `code_switch=True` to keep English, French, Spanish, or Italian spans in their original script alongside Arabic, useful for interviews and everyday conversations.
- **Add diacritics for clearer Arabic pronunciation.** Enable `diacritics=True` to add vowel marks to Arabic transcripts, making them easier to read and supporting language learning. Diacritics and code-switching can be enabled together.
=========== card_MAdel121_whisper-small-egyptian-arabic.md (    7779)
license: mit 
- arabic
- egyptian-arabic
datasets:
- MAdel121/arabic-egy-cleaned
- wer
- cer
- name: whisper-small-egyptian-arabic
    dataset:
      name: MAdel121/arabic-egy-cleaned (Test Split)
      type: MAdel121/arabic-egy-cleaned
      - type: wer
        name: Test WER
      - type: cer
=========== card_mohammedaly22_whisper-large-v3-turbo-egyptian-code-switching.md (    5234)
license: mit
datasets:
- MohamedRashad/arabic-english-code-switching
- wer
- arabic
- egyptian
- egyptian-arabic
# Whisper Large V3 Turbo — Egyptian Arabic Code-Switching
Fine-tuned [openai/whisper-large-v3-turbo](https://huggingface.co/openai/whisper-large-v3-turbo) for **Egyptian Arabic** with **Arabic↔English code-switching** support.
| **Base model** | `openai/whisper-large-v3-turbo` (809M params) |
| **Fine-tuned on** | [MohamedRashad/arabic-english-code-switching](https://huggingface.co/datasets/MohamedRashad/arabic-english-code-switching) |
| **Language** | Egyptian Arabic + English (code-switching) |
The base Whisper model transcribes everything in Arabic script, even English words. This fine-tuned version **outputs English words in English** when the speaker code-switches.
model_id = "mohammedaly22/whisper-large-v3-turbo-egyptian-code-switching"
=========== card_nabbra_whisper-medium-egyptian-arabic-ct2.md (     383)
license: apache-2.0
- nabbra/whisper-medium-egyptian-arabic
=========== card_oddadmix_whisper-large-v3-turbo-arabic-dialectal-v2.md (   11250)
license: apache-2.0
datasets:
- arabic
- dialectal-arabic
- wer
- cer
# whisper-large-v3-turbo-arabic-dialectal-v2
multi-dialect Arabic on the **dialect-balanced** dataset
[`oddadmix/lahgtna-v3-small`](https://huggingface.co/datasets/oddadmix/lahgtna-v3-small) (52k train / 2.6k test, **seed 42**,
> [`oddadmix/whisper-large-v3-turbo-arabic-dialectal`](https://huggingface.co/oddadmix/whisper-large-v3-turbo-arabic-dialectal).
## Results (balanced test split ~2,600 clips, `clean_text` WER/CER)
| | WER | CER |
## Per-dialect accuracy (v3 balanced test, `clean_text`)
WER / CER on each dialect's 200 held-out clips, easiest to hardest. Gulf/Levantine transcribe best; Maghrebi (Tunisian/Algerian/Moroccan) is hardest — consistent across every model.
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### assistant · 2026-11-20T09:23:26.869Z

Status: STT candidates found (Jais-ASR, Cohere Transcribe Arabic, Egyptian Whisper fine-tunes). Pulling their WER numbers next.

### assistant · 2026-11-20T09:23:31.255Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\npython3 -I - <<'EOF'\nimport re,html\nt=open('card_IFM_Jais-ASR.md',errors='ignore').read()\nfor tb in re.findall(r'<table.*?</table>',t,flags=re.S)[:1]:\n    for tr in re.findall(r'<tr.*?</tr>',tb,flags=re.S):\n        c=[re.sub(r'\\s+',' ',html.unescape(re.sub(r'<[^>]+>','',x))).strip() for x in re.findall(r'<t[hd].*?</t[hd]>',tr,flags=re.S)]\n        print(' | '.join(c)[:230])\nfor k in ['size','Parameters','parameters','4B','GB','RTF','speed','hardware','GGUF','llama.cpp','Ollama','vLLM']:\n    for m in re.finditer(k,t):\n        pass\nprint([l[:200] for l in t.split('\\n') if re.search(r'GGUF|llama\\.cpp|vLLM|VRAM|CPU|B parameters',l)][:8])\nEOF\necho ---ABD; sed -n 1,40p card_AbdelrahmanHassan_whisper-large-v3-egyptian-arabic.md | grep -iE \"value|wer|%\" | head; grep -iE \"wer|cer|loss\" card_MAdel121_whisper-small-egyptian-arabic.md | head -8 | cut -c1-200\necho ---dial; grep -A14 \"## Results\" card_oddadmix_whisper-large-v3-turbo-arabic-dialectal-v2.md | cut -c1-200; grep -iE \"egypt\" card_oddadmix_whisper-large-v3-turbo-arabic-dialectal-v2.md | head -4 | cut -c1-200",
 "description": "Extract ASR WER numbers from cards"
}
```

### assistant · 2026-11-20T09:23:33.485Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\ncurl -sL -m 25 https://raw.githubusercontent.com/Natural-Language-Processing-Elm/open_universal_arabic_asr_leaderboard/main/README.md -o oua.md; wc -c oua.md; grep -iE \"whisper|egypt|mgb|sada|common voice|fleurs|average|\\|\" oua.md | head -40 | cut -c1-260",
 "description": "Read Open Universal Arabic ASR leaderboard README"
}
```

### user · 2026-11-20T09:23:34.702Z

<details><summary>نتيجة أداة (3499 حرف)</summary>

```
 |  | Open-weight models | Closed models
 | Jais-ASR | Audar-ASR-V1-Turbo | cohere-transcribe-arabic-07-2026 | omniASR-LLM-7B | Qwen3-Omni-30B-A3B | Qwen3-ASR-1.7B | Voxtral-Small-24B | Melia 1Speechmatics | Scribe v2ElevenLabs
Word error rate (WER, %) ↓
AverageMacro-average, six test sets | 22.85 | 23.17 | 25.87 | 28.32 | 30.71 | 33.36 | 34.47 | 23.51 | 24.54
SADASaudi dialectal broadcast | 30.85 | 28.92 | 37.47 | 41.61 | 44.82 | 45.53 | 50.82 | 34.74 | 33.96
Common Voice 18MSA read speech | 8.56 | 8.09 | 5.82 | 8.75 | 11.46 | 16.90 | 15.25 | 5.19 | 8.71
MASC cleanMSA lectures, clean | 16.12 | 16.73 | 19.60 | 19.69 | 21.47 | 24.37 | 23.96 | 16.23 | 16.91
MASC noisyMSA lectures, noisy | 25.44 | 27.19 | 27.07 | 29.29 | 30.85 | 34.29 | 34.43 | 25.89 | 27.15
MGB-2MSA broadcast news | 9.59 | 11.08 | 15.54 | 14.13 | 13.09 | 16.57 | 16.03 | 12.61 | 10.30
Casablanca8 dialects, conversational | 46.56 | 47.02 | 49.71 | 56.46 | 62.55 | 64.47 | 66.30 | 46.41 | 50.20
Character error rate (CER, %) ↓
AverageMacro-average, six test sets | 8.37 | 9.23 | 11.80 | 12.52 | 13.67 | 12.33 | 15.29 | 10.62 | 9.96
SADASaudi dialectal broadcast | 14.33 | 13.40 | 23.53 | 24.95 | 26.11 | 19.90 | 28.85 | 21.21 | 16.48
Common Voice 18MSA read speech | 2.70 | 2.46 | 1.62 | 2.71 | 4.28 | 5.06 | 5.54 | 1.62 | 3.00
MASC cleanMSA lectures, clean | 3.76 | 5.32 | 6.45 | 5.76 | 5.59 | 5.72 | 7.06 | 5.11 | 4.97
MASC noisyMSA lectures, noisy | 7.51 | 9.78 | 10.13 | 10.66 | 11.28 | 10.84 | 12.22 | 9.47 | 9.36
MGB-2MSA broadcast news | 3.92 | 5.64 | 8.40 | 7.10 | 6.20 | 6.25 | 7.41 | 5.88 | 4.78
Casablanca8 dialects, conversational | 18.02 | 18.75 | 20.66 | 23.96 | 28.53 | 26.23 | 30.64 | 20.41 | 21.18
["Jais-ASR is IFM's state-of-the-art speech recognition model for Arabic as it is spoken: Modern Standard Arabic and dialects from 19 Arab countries, with natural code-switching into English, French, Sp", '- **Ready for production.** Run it with Transformers, or serve it with the included vLLM plugin behind an OpenAI-compatible `/v1/audio/transcriptions` endpoint. The bf16 weights are 11.4 GB.', '### Serving with vLLM', 'Jais-ASR ships with a vLLM plugin in [`vllm_plugin/`](https://huggingface.co/IFM/Jais-ASR/tree/main/vllm_plugin). Install it in its own environment, then start the server:']
---ABD
- wer
    - type: wer
      value: 0.4739  # Will be filled from your evaluation
- wer
- cer
      - type: wer
        name: Test WER
      - type: cer
        name: Test CER
*   Performance on noisy audio may vary, as only specific augmentations (DropChunk, DropFreq, DropBitResolution) were used during training.
| WER    | 22.69     |
---dial
## Results (balanced test split ~2,600 clips, `clean_text` WER/CER)

| | WER | CER |
|---|---|---|
| **This model (v2)** | **0.3324** | 0.125 |

## Per-dialect accuracy (v3 balanced test, `clean_text`)

WER / CER on each dialect's 200 held-out clips, easiest to hardest. Gulf/Levantine transcribe best; Maghrebi (Tunisian/Algerian/Moroccan) is hardest — consistent across every model.

| Dialect | WER | CER | n |
|---|---|---|---|
| Saudi/Gulf (`sa`) | 0.173 | 0.049 | 200 |
| Egyptian (`eg`) | 0.245 | 0.125 | 200 |
| Iraqi (`iq`) | 0.260 | 0.070 | 200 |
| Egyptian (`eg`) | 0.245 | 0.125 | 200 |
| Egyptian (`eg`) | <audio controls preload="none" src="https://huggingface.co/oddadmix/whisper-large-v3-turbo-arabic-dialectal-v2/resolve/main/samples/1.wav"></audio> | <span dir="rtl">لا، في ك
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### user · 2026-11-20T09:23:36.030Z

**نتيجة أداة:**
```
    4598 oua.md
| Test Set                                                                                        | Num Dialects   | Test (h)    |
|-------------------------------------------------------------------------------------------------|----------------|-------------|
| [SADA](https://www.kaggle.com/datasets/sdaiancai/sada2022)                                      | 10             | 10.7        |
| [Common Voice 18.0](https://commonvoice.mozilla.org/en/datasets)                                | 25             | 12.6        |
| [MASC (Clean-Test)](https://ieee-dataport.org/open-access/masc-massive-arabic-speech-corpus)    | 7              | 10.5        |
| [MASC (Noisy-Test)](https://ieee-dataport.org/open-access/masc-massive-arabic-speech-corpus)    | 8              | 8.9         |
| [MGB-2](http://www.mgb-challenge.org/MGB-2.html)                                                | Unspecified    | 9.6         |
| [Casablanca](https://huggingface.co/datasets/UBC-NLP/Casablanca)                                | 8              | 7.7         |
Please run the above evaluation for all the test sets under `datasets/`, calculate the average WER/CER, then launch an issue or PR letting us know about your model, training data, and its performance.
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

### assistant · 2026-11-20T09:23:44.497Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\ncurl -sL -m 25 https://raw.githubusercontent.com/speaches-ai/speaches/master/README.md -o speaches.md; curl -sL -m 25 https://raw.githubusercontent.com/ggml-org/whisper.cpp/master/examples/server/README.md -o wcpp_server.md; curl -sL -m 25 https://raw.githubusercontent.com/ggml-org/whisper.cpp/master/README.md -o wcpp.md\necho SPEACHES; wc -c speaches.md; grep -iE \"openai|transcriptions|speech|kokoro|piper|docker|realtime|cors|arabic|vad|CPU\" speaches.md | head -14 | cut -c1-240\necho WCPPSRV; wc -c wcpp_server.md; grep -iE \"v1/audio|openai|inference|cors|convert|port|--host|response_format\" wcpp_server.md | head -12 | cut -c1-240\necho WCPP; grep -iE \"wasm|webassembly|intel|x86|accelerate|metal|coreml|quantiz|mb|memory|ram\" wcpp.md | head -16 | cut -c1-200\ncurl -s -m 20 \"https://huggingface.co/api/models/handy-computer/cohere-transcribe-arabic-07-2026-gguf\" | python3 -I -c \"\nimport sys,json;d=json.load(sys.stdin);print([(s['rfilename']) for s in d.get('siblings',[])][:12], d.get('gguf',{}).get('total'))\"",
 "description": "Read speaches and whisper.cpp server docs"
}
```

### assistant · 2026-11-20T09:23:48.057Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\nhfsz(){ curl -s -m 20 \"https://huggingface.co/api/models/$1/tree/main?recursive=true\" | python3 -I -c \"\nimport sys,json\ntry:\n fs=json.load(sys.stdin); \n tot=sum(f.get('size',0) for f in fs if f['type']=='file' and f['path'].endswith(('.onnx','.bin','.safetensors')) )\n print('$1', [ (f['path'],round(f.get('size',0)/1e6)) for f in fs if f['type']=='file' and f['path'].endswith('.onnx')][:8])\nexcept Exception as e: print('$1','ERR')\"; }\nfor m in onnx-community/whisper-tiny onnx-community/whisper-base onnx-community/whisper-small onnx-community/whisper-large-v3-turbo; do hfsz $m & done; wait\ncurl -s -m 20 \"https://huggingface.co/api/models?search=whisper&author=onnx-community&limit=15&sort=downloads&direction=-1\" | python3 -I -c \"\nimport sys,json\nfor d in json.load(sys.stdin): print(d['id'],d.get('downloads'))\"",
 "description": "Check ONNX Whisper model sizes for browser"
}
```

### user · 2026-11-20T09:23:51.047Z

<details><summary>نتيجة أداة (3043 حرف)</summary>

```
SPEACHES
    2076 speaches.md
`speaches` is an OpenAI API-compatible server supporting streaming transcription, translation, and speech generation. Speach-to-Text is powered by [faster-whisper](https://github.com/SYSTRAN/faster-whisper) and for Text-to-Speech [piper](ht
- OpenAI API compatible. All tools and SDKs that work with OpenAI's API should work with `speaches`.
- Audio generation (chat completions endpoint) | [OpenAI Documentation](https://platform.openai.com/docs/guides/realtime)
  - Async speech to speech interactions with a model (audio in, audio out)
- Text-to-Speech via `kokoro`(Ranked #1 in the [TTS Arena](https://huggingface.co/spaces/Pendrokar/TTS-Spaces-Arena)) and `piper` models.
- GPU and CPU support.
- [Deployable via Docker Compose / Docker](https://speaches.ai/installation/)
- [Realtime API](https://speaches.ai/usage/realtime-api)
### Realtime API
### Speech Generation
WCPPSRV
    6398 wcpp_server.md
Simple http server. WAV Files are passed to the inference model via http requests.
  -oved D,   --ov-e-device DNAME [CPU    ] the OpenVINO device used for encode inference
  --host HOST,                   [127.0.0.1] Hostname/ip-adress for the server, or a unix socket path ending in .sock
  --port PORT,                   [8080   ] Port number for the server
  --inference-path PATH,         [/inference] Inference path for all requests
  --convert,                     [false  ] Convert audio to WAV, requires ffmpeg on the server
**/inference**
curl 127.0.0.1:8080/inference \
-F response_format="json"
You can benchmark the Whisper server using the provided bench.js script with [k6](https://k6.io/). This script sends concurrent multipart requests to the /inference endpoint and is fully configurable via environment variables.
  --env ENDPOINT=/inference \
  --env RESPONSE_FORMAT=json
WCPP
- Apple Silicon first-class citizen - optimized via ARM NEON, Accelerate framework, Metal and [Core ML](#core-ml-support)
- AVX intrinsics support for x86 architectures
- [Integer quantization support](#quantization)
- Zero memory allocations at runtime
- [x] Mac OS (Intel and Arm)
- [x] [WebAssembly](examples/whisper.wasm)
On Apple Silicon, the inference runs fully on the GPU via Metal:
## Memory usage
| tiny   | 75 MiB  | ~273 MB |
| base   | 142 MiB | ~388 MB |
| small  | 466 MiB | ~852 MB |
## Quantization
`whisper.cpp` supports integer quantization of the Whisper `ggml` models.
Quantized models require less memory and disk space and depending on the hardware can be processed more efficiently.
Here are the steps for creating and using a quantized model:
# quantize a model with Q5_0 method
['.gitattributes', 'LICENSE', 'NOTICE', 'README.md', 'cohere-transcribe-arabic-07-2026-BF16.gguf', 'cohere-transcribe-arabic-07-2026-F16.gguf', 'cohere-transcribe-arabic-07-2026-Q4_K_M.gguf', 'cohere-transcribe-arabic-07-2026-Q5_K_M.gguf', 'cohere-transcribe-arabic-07-2026-Q6_K.gguf', 'cohere-transcribe-arabic-07-2026-Q8_0.gguf'] 2049026832
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### user · 2026-11-20T09:23:52.650Z

<details><summary>نتيجة أداة (2154 حرف)</summary>

```
onnx-community/whisper-base [('onnx/decoder_model.onnx', 208), ('onnx/decoder_model_bnb4.onnx', 122), ('onnx/decoder_model_fp16.onnx', 104), ('onnx/decoder_model_int8.onnx', 53), ('onnx/decoder_model_merged.onnx', 209), ('onnx/decoder_model_merged_bnb4.onnx', 122), ('onnx/decoder_model_merged_fp16.onnx', 105), ('onnx/decoder_model_merged_int8.onnx', 54)]
onnx-community/whisper-large-v3-turbo [('onnx/decoder_model.onnx', 688), ('onnx/decoder_model_bnb4.onnx', 327), ('onnx/decoder_model_fp16.onnx', 344), ('onnx/decoder_model_int8.onnx', 440), ('onnx/decoder_model_merged.onnx', 688), ('onnx/decoder_model_merged_bnb4.onnx', 328), ('onnx/decoder_model_merged_fp16.onnx', 344), ('onnx/decoder_model_merged_int8.onnx', 440)]
onnx-community/whisper-tiny [('onnx/decoder_model.onnx', 118), ('onnx/decoder_model_bnb4.onnx', 86), ('onnx/decoder_model_fp16.onnx', 59), ('onnx/decoder_model_int8.onnx', 30), ('onnx/decoder_model_merged.onnx', 119), ('onnx/decoder_model_merged_bnb4.onnx', 86), ('onnx/decoder_model_merged_fp16.onnx', 60), ('onnx/decoder_model_merged_int8.onnx', 31)]
onnx-community/whisper-small [('onnx/decoder_model.onnx', 615), ('onnx/decoder_model_bnb4.onnx', 226), ('onnx/decoder_model_fp16.onnx', 308), ('onnx/decoder_model_int8.onnx', 156), ('onnx/decoder_model_merged.onnx', 615), ('onnx/decoder_model_merged_bnb4.onnx', 226), ('onnx/decoder_model_merged_fp16.onnx', 309), ('onnx/decoder_model_merged_int8.onnx', 157)]
onnx-community/whisper-base 259849
onnx-community/whisper-tiny.en 225127
onnx-community/whisper-small 173756
onnx-community/whisper-tiny 111965
onnx-community/whisper-base_timestamped 100835
onnx-community/whisper-base.en 91268
onnx-community/whisper-small_timestamped 55417
onnx-community/whisper-large-v3-turbo 53555
onnx-community/whisper-tiny_timestamped 38483
onnx-community/whisper-tiny.en_timestamped 28550
onnx-community/whisper-base.en_timestamped 24285
onnx-community/whisper-large-v3-turbo_timestamped 19100
onnx-community/whisper-small.en 9311
onnx-community/whisper-small.en_timestamped 4995
onnx-community/whisper-medium_timestamped 2338
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### assistant · 2026-11-20T09:24:03.284Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\npf(){ n=$1; u=$2; out=$(curl -s -m 20 -i -X OPTIONS -H \"Origin: https://example.github.io\" -H \"Access-Control-Request-Method: POST\" -H \"Access-Control-Request-Headers: authorization,content-type\" \"$u\" | tr -d '\\r' | grep -iE \"^HTTP/|^access-control-allow-(origin|headers|methods)\" | tr '\\n' ' '); echo \"$n | $u | $out\"; }\npf groq-chat https://api.groq.com/openai/v1/chat/completions &\npf groq-stt https://api.groq.com/openai/v1/audio/transcriptions &\npf openrouter https://openrouter.ai/api/v1/chat/completions &\npf gemini-openai https://generativelanguage.googleapis.com/v1beta/openai/chat/completions &\npf hf-router https://router.huggingface.co/v1/chat/completions &\npf mistral https://api.mistral.ai/v1/chat/completions &\npf mistral-stt https://api.mistral.ai/v1/audio/transcriptions &\npf together https://api.together.xyz/v1/chat/completions &\npf cerebras https://api.cerebras.ai/v1/chat/completions &\npf cloudflare-openai https://api.cloudflare.com/client/v4/accounts/x/ai/v1/chat/completions &\npf github-models https://models.github.ai/inference/chat/completions &\npf nvidia https://integrate.api.nvidia.com/v1/chat/completions &\npf sambanova https://api.sambanova.ai/v1/chat/completions &\npf cohere-compat https://api.cohere.ai/compatibility/v1/chat/completions &\npf openai https://api.openai.com/v1/chat/completions &\npf anthropic https://api.anthropic.com/v1/messages &\npf ollama-local-nonexistent http://127.0.0.1:11434/v1/chat/completions &\nwait",
 "description": "Test CORS preflight on free LLM API endpoints"
}
```

### user · 2026-11-20T09:24:07.840Z

<details><summary>نتيجة أداة (3937 حرف)</summary>

```
ollama-local-nonexistent | http://127.0.0.1:11434/v1/chat/completions | HTTP/1.1 403 Forbidden 
groq-chat | https://api.groq.com/openai/v1/chat/completions | HTTP/2 204  access-control-allow-headers: authorization,content-type access-control-allow-methods: GET,HEAD,PUT,PATCH,POST,DELETE access-control-allow-origin: * 
groq-stt | https://api.groq.com/openai/v1/audio/transcriptions | HTTP/2 204  access-control-allow-headers: authorization,content-type access-control-allow-methods: GET,HEAD,PUT,PATCH,POST,DELETE access-control-allow-origin: * 
openrouter | https://openrouter.ai/api/v1/chat/completions | HTTP/2 204  access-control-allow-origin: * access-control-allow-headers: Authorization,User-Agent,X-Api-Key,X-CSRF-Token,X-Requested-With,Accept,Accept-Version,Content-Length,Content-Encoding,Content-MD5,Content-Type,Date,X-Api-Version,HTTP-Referer,X-Windowai-Title,X-Openrouter-Title,X-Title,X-Openrouter-Categories,X-Openrouter-App-Visibility,X-Session-Id,X-Openrouter-Trace,X-Stainless-Lang,X-Stainless-Package-Version,X-Stainless-OS,X-Stainless-Arch,X-Stainless-Runtime,X-Stainless-Runtime-Version,X-Stainless-Retry-Count,X-Stainless-Timeout,X-Stainless-Helper-Method,Protection-Key,Idempotency-Key,Payment-Authorization,PAYMENT-SIGNATURE,traceparent,tracestate,b3 access-control-allow-methods: GET,OPTIONS,PATCH,DELETE,POST,PUT 
cloudflare-openai | https://api.cloudflare.com/client/v4/accounts/x/ai/v1/chat/completions | HTTP/2 405  
nvidia | https://integrate.api.nvidia.com/v1/chat/completions | HTTP/2 200  
hf-router | https://router.huggingface.co/v1/chat/completions | HTTP/2 200  access-control-allow-origin: * access-control-allow-headers: authorization,content-type 
gemini-openai | https://generativelanguage.googleapis.com/v1beta/openai/chat/completions | HTTP/2 200  access-control-allow-origin: https://example.github.io access-control-allow-methods: DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT access-control-allow-headers: authorization,content-type 
mistral-stt | https://api.mistral.ai/v1/audio/transcriptions | HTTP/2 200  access-control-allow-origin: * access-control-allow-headers: Authorization,Content-Type,User-Agent,Cache-Control,Keep-Alive,X-Mistral-User-Agent,X-External-Organization-Id,X-External-Workspace-Id access-control-allow-methods: GET,HEAD,PUT,PATCH,POST,OPTIONS,DELETE 
mistral | https://api.mistral.ai/v1/chat/completions | HTTP/2 200  access-control-allow-origin: * access-control-allow-headers: Authorization,Content-Type,User-Agent,Cache-Control,Keep-Alive,X-Mistral-User-Agent,X-External-Organization-Id,X-External-Workspace-Id access-control-allow-methods: GET,HEAD,PUT,PATCH,POST,OPTIONS,DELETE 
anthropic | https://api.anthropic.com/v1/messages | HTTP/2 400  access-control-allow-methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT access-control-allow-headers: authorization,content-type 
openai | https://api.openai.com/v1/chat/completions | HTTP/2 200  access-control-allow-origin: https://example.github.io access-control-allow-headers: authorization,content-type access-control-allow-methods: GET, OPTIONS, POST 
cerebras | https://api.cerebras.ai/v1/chat/completions | HTTP/2 200  access-control-allow-origin: * access-control-allow-methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT access-control-allow-headers: authorization,content-type 
github-models | https://models.github.ai/inference/chat/completions | HTTP/2 200  
together | https://api.together.xyz/v1/chat/completions | HTTP/2 200  access-control-allow-origin: * access-control-allow-headers: authorization,content-type access-control-allow-methods: POST,OPTIONS 
sambanova | https://api.sambanova.ai/v1/chat/completions | HTTP/2 200  
cohere-compat | https://api.cohere.ai/compatibility/v1/chat/completions | HTTP/2 200  access-control-allow-headers: Authorization, Content-Type access-control-allow-methods: POST access-control-allow-origin: *
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### assistant · 2026-11-20T09:24:20.015Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\nf(){ curl -sL -m 30 -A \"Mozilla/5.0\" \"$2\" -o pg_$1.html -w \"$1 %{http_code} %{size_download}\\n\"; }\nf groq_rl https://console.groq.com/docs/rate-limits & f groq_models https://console.groq.com/docs/models & f groq_stt https://console.groq.com/docs/speech-to-text & f cf_price https://developers.cloudflare.com/workers-ai/platform/pricing/ & f cf_compat https://developers.cloudflare.com/workers-ai/configuration/open-ai-compatibility/ & f or_limits https://openrouter.ai/docs/api-reference/limits & f gem_rl https://ai.google.dev/gemini-api/docs/rate-limits & f gem_price https://ai.google.dev/gemini-api/docs/pricing & f hf_price https://huggingface.co/docs/inference-providers/pricing & f mistral_tier https://docs.mistral.ai/deployment/laplateforme/tier & f cerebras_rl https://inference-docs.cerebras.ai/support/rate-limits & f ollama_faq https://raw.githubusercontent.com/ollama/ollama/main/docs/faq.mdx & wait\necho GROQ-RL; python3 -I $S/strip.py pg_groq_rl.html | grep -iE \"free|developer|whisper|RPM|RPD|TPM|ASH|audio\" | head -14 | cut -c1-240\necho GROQ-STT; python3 -I $S/strip.py pg_groq_stt.html | grep -iE \"whisper|arabic|\\\\$|price|25 ?MB|file size|translation|languages|turbo|v3\" | head -12 | cut -c1-240\necho CF; python3 -I $S/strip.py pg_cf_price.html | grep -iE \"free|10,000|neurons|daily|whisper|\\\\$0\" | head -10 | cut -c1-260\necho CFCOMPAT; python3 -I $S/strip.py pg_cf_compat.html | grep -iE \"v1|base|chat|completions|audio|transcri|embeddings\" | head -10 | cut -c1-240",
 "description": "Fetch free tier docs for Groq and Cloudflare"
}
```

### user · 2026-11-20T09:24:51.759Z

<details><summary>نتيجة أداة (2301 حرف)</summary>

```
cf_price 200 131083
cf_compat 200 120654
groq_models 200 374362
ollama_faq 200 18583
groq_rl 200 321036
groq_stt 200 397993
hf_price 200 136663
cerebras_rl 200 266781
or_limits 200 549787
gem_rl 200 47753
gem_price 200 156059
mistral_tier 000 0
GROQ-RL
Dashboard
Developer Resources
Developer Community
Developer Resources
Developer Community
RPM:
RPD:
TPM:
ASH:
Audio seconds per hour
Audio seconds per day
ITPM:
OTPM:
Let's say your RPM = 50 and your TPM = 200K. If you were to send 50 requests with only 100 tokens within a minute, you would reach your limit even though you did not send 200K tokens within those
GROQ-STT
enable near-instant transcriptions and translations. With Groq API, you can integrate high-quality audio
Translations
https://api.groq.com/openai/v1/audio/translations
whisper-large-v3-turbo
Whisper Large V3 Turbo
A fine-tuned version of a pruned Whisper Large V3 designed for fast, multilingual transcription tasks.
whisper-large-v3
Whisper Large V3
Provides state-of-the-art performance with high accuracy for multilingual transcription and translation tasks.
Which Whisper Model Should You Use?
whisper-large-v3
If your application requires multilingual support and you need the best price for performance, use
CF
What are Neurons?
Workers AI has updated pricing to be more granular, with per-model unit-based pricing presented, but still billing in neurons in the back end.
Free and Paid Workers plans
$0.011 per 1,000 Neurons
Our free allocation allows anyone to use a total of
10,000 Neurons per day at no charge
. To use more than 10,000 Neurons per day, you need to sign up for the
. On Workers Paid, you will be charged at $0.011 / 1,000 Neurons for any usage above the free allocation of 10,000 Neurons per day.
All limits reset daily at 00:00 UTC. If you exceed any one of the above limits, further operations will fail with an error.
Free
CFCOMPAT
Chat Completions and embeddings
through Chat Completions (
/v1/chat/completions
/v1/embeddings
/v1/responses
baseURL
Chat Completions and embeddings
Most Workers AI text generation models support the OpenAI Chat Completions API. Embedding models support the OpenAI Embeddings API.
by setting the Workers AI base URL, API token, and model name.
baseURL:
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### assistant · 2026-11-20T09:24:59.004Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\npython3 -I $S/strip.py pg_groq_rl.html | grep -n -iE -A9 \"^whisper-large-v3-turbo$\" | head -24 | tr '\\n' '|' | cut -c1-600; echo\npython3 -I $S/strip.py pg_groq_rl.html | grep -n -iE -B1 -A9 \"^(llama-3.3-70b-versatile|openai/gpt-oss-20b|qwen/qwen3-32b)$\" | head -40 | tr '\\n' '|' | cut -c1-900; echo\necho GROQMODELS; python3 -I $S/strip.py pg_groq_models.html | grep -E \"^[a-z0-9\\-]+/[a-z0-9.\\-]+$|^(llama|whisper|gpt|qwen|allam|playai)[a-z0-9.\\-]*$\" | sort -u | head -30 | tr '\\n' ' '; echo\necho GEMINI; python3 -I $S/strip.py pg_gem_price.html | grep -n -iE \"free of charge|^free tier|Free Tier|Input price|gemini-.*flash\" | head -14 | cut -c1-200\npython3 -I $S/strip.py pg_gem_rl.html | grep -iE \"free tier|project|RPD|per day|rate limits are|12 pm|pacific\" | head -8 | cut -c1-260\necho GEM-OPENAI; curl -sL -m 20 https://ai.google.dev/gemini-api/docs/openai -o pg_gem_openai.html; python3 -I $S/strip.py pg_gem_openai.html | grep -iE \"base_url|generativelanguage|audio|function call|tool\" | head -8 | cut -c1-200",
 "description": "Extract Groq and Gemini free limits"
}
```

### user · 2026-11-20T09:25:02.585Z

<details><summary>نتيجة أداة (2489 حرف)</summary>

```
272:whisper-large-v3-turbo|273-20|274-2K|275--|276--|277-7.2K|278-28.8K|279-Rate Limit Headers|280-In addition to viewing your limits on your account's|281-limits|
243--|244:openai/gpt-oss-20b|245-30|246-1K|247-8K|248-200K|249--|250--|251-openai/gpt-oss-safeguard-20b|252-3|253-1K|
GROQMODELS
canopylabs/orpheus-arabic-saudi canopylabs/orpheus-v1-english llama-3.1-8b-instant llama-3.3-70b-versatile meta-llama/llama-prompt-guard-2-22m meta-llama/llama-prompt-guard-2-86m meta-models/muse-spark-open minimaxai/minimax-m2.7 openai/gpt-oss-120b openai/gpt-oss-20b openai/gpt-oss-safeguard-20b qwen/qwen3.8-27b whisper-large-v3 whisper-large-v3-turbo 
GEMINI
7:Start building free of charge with generous limits, then scale up with prepaid
76:Gemini 4 Carbon is not available on the Free tier. Every token the model processes is counted and billed, including thinking tokens and internal tool system instructions and function declarations w
82:* Free Tier
85:* Input price
122:* Free Tier
125:* Input price
149:* Free Tier
152:* Input price
176:* Free Tier
179:* Input price
231:Gemini 4 Argon is not available on the Free tier. Every token the model processes is counted and billed, including thinking tokens and internal tool system instructions and function declarations w
237:* Free Tier
240:* Input price
277:* Free Tier
Rate limits are usually measured across three dimensions:
* Requests per day (**RPD**)
Rate limits are applied per project, not per API key. Requests per day (**RPD**)
quotas reset at midnight Pacific time.
conceptually similar to TPM. Other models might have a token per day limit
1,500 requests per day (RPD) per project on the Gemini Developer API (see
Rate limits are more restricted for experimental and preview models.
Rate limits are tied to the project's usage tier. As your API usage and spending
GEM-OPENAI
base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
baseURL: "https://generativelanguage.googleapis.com/v1beta/openai/"
curl "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions" \
* **`base_url="https://generativelanguage.googleapis.com/v1beta/openai/"`:** This
base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
baseURL: "https://generativelanguage.googleapis.com/v1beta/openai/"
curl "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions" \
base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### assistant · 2026-11-20T09:25:09.084Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\npython3 -I $S/strip.py pg_groq_rl.html | sed -n 195,300p | tr '\\n' '|' | cut -c1-1800; echo\npython3 -I $S/strip.py pg_groq_rl.html | grep -n -iE \"free plan|developer plan|Free$|on_demand|Developer$\" | head -8\necho ---GEM; python3 -I $S/strip.py pg_gem_price.html | sed -n 100,150p | tr '\\n' '|' | cut -c1-1800",
 "description": "Show Groq rate table rows and Gemini pricing"
}
```

### user · 2026-11-20T09:25:10.723Z

<details><summary>نتيجة أداة (3009 حرف)</summary>

```
to access higher limits,|Batch|and|Flex|processing, and more. Note that the limits shown below are the base limits for the Developer plan, and higher limits are available for select workloads and enterprise use cases.|Free Plan Limits|Developer Plan Limits|MODEL ID|RPM|RPD|TPM|TPD|ASH|ASD|canopylabs/orpheus-arabic-saudi|10|100|1.2K|3.6K|-|-|canopylabs/orpheus-v1-english|10|100|1.2K|3.6K|-|-|meta-llama/llama-prompt-guard-2-22m|30|14.4K|15K|500K|-|-|meta-llama/llama-prompt-guard-2-86m|30|14.4K|15K|500K|-|-|openai/gpt-oss-120b|30|1K|8K|200K|-|-|openai/gpt-oss-20b|30|1K|8K|200K|-|-|openai/gpt-oss-safeguard-20b|3|1K|2K|200K|-|-|qwen/qwen3.8-27b|30|1K|8K|200K|-|-|whisper-large-v3|20|2K|-|-|7.2K|28.8K|whisper-large-v3-turbo|20|2K|-|-|7.2K|28.8K|Rate Limit Headers|In addition to viewing your limits on your account's|limits|page, you can also view rate limit information such as remaining requests and tokens in HTTP response|headers as follows:|The following headers are set (values are illustrative):|Header|Value|Notes|retry-after|2|In seconds|x-ratelimit-limit-requests|14400|Always refers to Requests Per Day (RPD)|x-ratelimit-limit-tokens|18000|Always refers to Tokens Per Minute (TPM)|x-ratelimit-remaining-requests|14370|Always refers to Requests Per Day (RPD)|x-ratelimit-remaining-tokens|
194:Developer plan
199:processing, and more. Note that the limits shown below are the base limits for the Developer plan, and higher limits are available for select workloads and enterprise use cases.
200:Free Plan Limits
201:Developer Plan Limits
---GEM
---|* Grounding with Google Search{% sup %}*{% /sup %}|* Not available|* 5,000 free search requests per month (shared across all Gemini 3 and newer models),|then $14 per 1,000 requests (subject to a [daily cap](/docs/pricing#pricing-for-tools) of 1,500 requests per day).|---|* Grounding with Google Maps|* Not available|* 5,000 requests per month (free, shared across all Gemini 3 and newer models), then $14 / 1,000|search queries.|---|* Used to improve our products|* Not available|* [No](/docs/terms)|{% /table %}|{% sup %}*{% /sup %} A customer-submitted request to Gemini may result in one or|more queries to Google Search. You will be charged for each individual search|query performed.|{% /tab %}|{% tab title="Batch" %}|{% table %}|* Feature|* Free Tier|* Paid Tier, per 1M tokens in USD|---|* Input price|* Not available|* $1.00 through November 30, 2026.|$2.00 starting December 1, 2026.|---|* Output price (including thinking tokens)|* Not available|* $5.00 through November 30, 2026.|$10.00 starting December 1, 2026.|---|* Context caching price|* Not available|* $0.05 through November 30, 2026.|$0.10 starting December 1, 2026.|Implicit caching only (explicit caching is not supported).|---|* Used to improve our products|* Not available|* [No](/docs/terms)|{% /table %}|{% /tab %}|{% tab title="Flex" %}|{% table %}|* Feature|* Free Tier|* Paid Tier, per 1M tokens in USD|
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### assistant · 2026-11-20T09:25:15.669Z

Status: CORS tested on 17 endpoints, Groq/Gemini limits read. Now OpenRouter, Cloudflare, HF, Mistral limits and the TTS side.

### assistant · 2026-11-20T09:25:20.723Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\necho GEM-models-free; python3 -I $S/strip.py pg_gem_price.html | grep -iE \"^#+ |^Gemini [0-9]|gemini-[0-9a-z.\\-]+$\" | head -16 | cut -c1-120\npython3 -I $S/strip.py pg_gem_price.html | grep -n -B2 -A3 -iE \"^\\* Input price$\" | sed -n 1,16p | tr '\\n' '|' | cut -c1-700; echo\necho OR; python3 -I $S/strip.py pg_or_limits.html | grep -iE \":free|free model|20 requests|50 requests|1000 requests|\\\\$10|credits|per day\" | head -8 | cut -c1-300\necho HF; python3 -I $S/strip.py pg_hf_price.html | grep -iE \"free|\\\\$0\\.|monthly credits|PRO|credits|Team|Enterprise\" | head -10 | cut -c1-300\necho CFmodels; curl -sL -m 30 \"https://developers.cloudflare.com/workers-ai/models/\" -o pg_cf_models.html; python3 -I $S/strip.py pg_cf_models.html | grep -iE \"whisper|llama-3|qwen|gemma|gpt-oss|aya|melotts|deepgram|arabic|mistral|hermes\" | sort -u | head -24 | cut -c1-120\necho ollamaORIG; grep -inE \"OLLAMA_ORIGINS|403|cors|allow\" ollama_faq.html 2>/dev/null | head -0; grep -inE \"OLLAMA_ORIGINS\" ollama_faq.html | head -6 | cut -c1-240",
 "description": "Extract OpenRouter HF Cloudflare Gemini free facts"
}
```

### user · 2026-11-20T09:25:22.476Z

<details><summary>نتيجة أداة (5367 حرف)</summary>

```
GEM-models-free
> - Gemini Docs MCP server (consistent live info): https://gemini-api-docs-mcp.dev
# Gemini Developer API pricing
## Gemini 4 Carbon  {% id="gemini-4-carbon" %}
Gemini 4 Carbon is not available on the Free tier. Every token the model processes is counted and billed, including thin
## Gemini 4 Argon  {% id="gemini-4-argon" %}
Gemini 4 Argon is not available on the Free tier. Every token the model processes is counted and billed, including think
## Gemini 4 Neon  {% id="gemini-4-neon" %}
Gemini 4 Neon is not available on the Free tier. Every token the model processes is counted and billed, including thinki
## Gemini 4 Hydrogen  {% id="gemini-4-hydrogen" %}
## Gemini 3.8 Flash  {% id="gemini-3.8-flash" %}
## Gemini 3.6 Flash  {% id="gemini-3.6-flash" %}
## Gemini 3.5 Transcribe Live  {% id="gemini-3.5-transcribe-live" %}
## Gemini 3.5 Transcribe  {% id="gemini-3.5-transcribe" %}
## Gemini 3.5 Flash-Lite  {% id="gemini-3.5-flash-lite" %}
## Genie 4  {% id="genie-4" %}
## Gemini Omni 1.2 Flash  {% id="gemini-omni-1.2-flash" %}
83-* Paid Tier, per 1M tokens in USD|84----|85:* Input price|86-* Not available|87-* $2.00 through November 30, 2026.|88-$4.00 starting December 1, 2026.|--|123-* Paid Tier, per 1M tokens in USD|124----|125:* Input price|126-* Not available|127-* $1.00 through November 30, 2026.|128-$2.00 starting December 1, 2026.|--|150-* Paid Tier, per 1M tokens in USD|151----|
OR
How do I use the best free models in OpenRouter?
errors, including for free models. Adding credits to put your balance above zero allows you to use those models again.
The budget applies to prepaid accounts spending their own credits, and only to a subset of them: accounts whose balance is below a threshold, and, while the mechanism is being rolled out, newer accounts without an established spending history. A larger balance raises the budget up to the ceiling, an
: If you’re using a free model variant (with an ID ending in
Requests per day
count toward a daily limit for your account or organization. The limit is 10,000 requests per day by default, and it resets at 00:00 UTC.
, when you hit one of the platform limits above (free-model requests per minute or per day, key-management requests per day, per-IP burst limits, or DDoS protection).
{"docsConfig":{"theme":"mint","$schema":"https://mintlify.com/docs.json","name":"OpenRouter | Documentation","colors":{"primary":"#7624F4","light":"#7624F4","dark":"#C8FF00"},"logo":{"light":"https://mintcdn.com/openrouter-d02e98a0/ksNSeB_K7gD-BUDh/assets/logo-v2-light.svg?fit=max\u0026auto=format\u
HF
Enterprise
Team & Enterprise
Hugging Face PRO
Enterprise Support
Inference Providers
Inference Providers documentation
Inference Providers
Inference Providers
Inference Providers
Routing and Providers
CFmodels
Building upon Mistral Small 3 (2501), Mistral Small 3.1 (2503) adds state-of-the-art vision understanding and enhances l
DeepSeek-R1-Distill-Qwen-32B is a model distilled from DeepSeek-R1 based on Qwen2.5. It outperforms OpenAI-o1-mini acros
Deepgram
EmbeddingGemma 2 is an open multimodal embedding model built by Google DeepMind which maps text (incl. code), images, vi
EmbeddingGemma is a 300M parameter, state-of-the-art for its size, open embedding model from Google, built from Gemma 3 
Gemma 4 is Google's most intelligent family of open models, built from Gemini 3 research to maximize intelligence-per-pa
Llama Guard 3 is a Llama-3.1-8B pretrained model, fine-tuned for content safety classification. Similar to previous vers
MeloTTS is a high-quality multi-lingual text-to-speech library by MyShell.ai.
MistralAI
OpenAI’s open-weight models designed for powerful reasoning, agentic tasks, and versatile developer use cases – gpt-
OpenAI’s open-weight models designed for powerful reasoning, agentic tasks, and versatile developer use cases – gpt-
QwQ is the reasoning model of the Qwen series. Compared with conventional instruction-tuned models, QwQ, which is capabl
Qwen
Qwen 3.8 27B is a 27-billion-parameter instruction-tuned language model from Alibaba's Qwen family, designed for vision,
Qwen2.5-Coder is the latest series of Code-Specific Qwen large language models (formerly known as CodeQwen). As of now, 
Qwen3 is the latest generation of large language models in Qwen series, offering a comprehensive suite of dense and mixt
The Mistral-7B-Instruct-v0.2 Large Language Model (LLM) is an instruct fine-tuned version of the Mistral-7B-v0.2.
The Qwen3 Embedding model series is the latest proprietary model of the Qwen family, specifically designed for text embe
This is a Gemma-2B base model that Cloudflare dedicates for inference with LoRA adapters. Gemma is a family of lightweig
This is a Gemma-7B base model that Cloudflare dedicates for inference with LoRA adapters. Gemma is a family of lightweig
Transcribe audio using Deepgram’s speech-to-text model
Whisper is a general-purpose speech recognition model. It is trained on a large dataset of diverse audio and is also a m
Whisper is a pre-trained model for automatic speech recognition (ASR) and speech translation.
Whisper is a pre-trained model for automatic speech recognition (ASR) and speech translation. Trained on 680k hours of l
ollamaORIG
head: illegal line count -- 0
ugrep: warning: ollama_faq.html: No such file or directory
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### assistant · 2026-11-20T09:25:31.324Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\npython3 -I - <<'EOF'\nimport re\nt=open('pg_gem_price.html',errors='ignore').read()\nt=re.sub(r'<[^>]+>','\\n',t)\nsecs=re.split(r'\\n## ',t)\nfor s in secs:\n    name=s.split('\\n')[0][:40]\n    if re.match(r'(Gemini 3\\.8 Flash|Gemini 3\\.6 Flash|Gemini 3\\.5 Flash-Lite|Gemini 3\\.5 Transcribe)\\b',name):\n        m=re.search(r'Input price\\s*\\n\\*? ?\\s*\\n?(.{0,160})',s.replace('\\n\\n','\\n'))\n        i=s.find('Input price')\n        print(name,'=>',' '.join(s[i:i+260].split())[:230])\nEOF\necho ---OR; python3 -I $S/strip.py pg_or_limits.html | grep -inE \"free\" | head -14 | cut -c1-330\necho ---HF; python3 -I $S/strip.py pg_hf_price.html | sed -n 40,90p | tr '\\n' ' ' | cut -c1-1500; echo\ngrep -inE \"OLLAMA_ORIGINS\" pg_ollama_faq.html | head -4 | cut -c1-260\ncurl -sL -m 25 https://docs.mistral.ai/getting-started/models/ -o /dev/null -w \"mistral-docs %{http_code}\\n\"; curl -sL -m 25 \"https://help.mistral.ai/en/articles/455206-how-can-i-try-the-api-for-free-with-the-experiment-plan\" -o pg_mistral_free.html -w \"mistral-free %{http_code}\\n\"; python3 -I $S/strip.py pg_mistral_free.html | grep -iE \"free|experiment|rate|phone|data|train\" | head -8 | cut -c1-260",
 "description": "Extract Gemini free tier OpenRouter HF Mistral details"
}
```

### user · 2026-11-20T09:25:58.007Z

<details><summary>نتيجة أداة (3982 حرف)</summary>

```
Gemini 3.8 Flash  {% id=&quot;gemini-3.8 => Input price * Free of charge * $0.75 through December 31, 2026. $1.50 starting January 1, 2027. --- * Output price (including thinking tokens) * Free of charge * $3.75 through December 31, 2026. $7.50 starting January 1, 2027. ---
Gemini 3.6 Flash  {% id=&quot;gemini-3.6 => Input price * Free of charge * $0.75 through December 31, 2026. $1.50 starting January 1, 2027. --- * Output price (including thinking tokens) * Free of charge * $3.75 through December 31, 2026. $7.50 starting January 1, 2027. ---
Gemini 3.5 Transcribe Live  {% id=&quot; => Input price * Free of charge * $3.50 or $0.005/min{% sup %}*{% /sup %} (audio) --- * Output price (including thinking tokens) * Free of charge * $21.00 or $0.004/min{% sup %}*{% /sup %} (text) --- * Grounding with Google Search * 
Gemini 3.5 Transcribe  {% id=&quot;gemin => Input price * Free of charge * $2.00 or $0.003/min{% sup %}*{% /sup %} (audio) --- * Output price (including thinking tokens) * Free of charge * $12.00 or $0.002/min{% sup %}*{% /sup %} (text) --- * Grounding with Google Search * 
Gemini 3.5 Flash-Lite  {% id=&quot;gemin => Input price * Free of charge * $0.30 (text / image / video / audio) --- * Output price (including thinking tokens) * Free of charge * $2.50 --- * Context caching price * Not available * $0.03 $1.00 / 1,000,000 tokens per hour (sto
Gemini 3.8 Flash TTS  {% id=&quot;gemini => Input price * Free of charge * $0.50 (text) through December 31, 2026. $1.00 (text) starting January 1, 2027. --- * Output price * Free of charge * $9.00 (audio) through December 31, 2026. $18.00 (audio) starting January 1, 2027. 
Gemini 3.8 Flash-Lite TTS  {% id=&quot;g => Input price * Free of charge * $0.50 (text) through December 31, 2026. $1.00 (text) starting January 1, 2027. --- * Output price * Free of charge * $6.00 (audio) through December 31, 2026. $12.00 (audio) starting January 1, 2027. 
---OR
10:How do I use the best free models in OpenRouter?
136:How many requests you can make (free-model request caps, key-management caps, per-IP burst limits, and DDoS protection)
138:headers on free-model and key-management errors
378:is_free_tier: false,
384:free_model_daily_requests: {
549:is_free_tier
554:free_model_daily_requests
561:// Free-model requests recorded so far in the current UTC day
566:// Free-model requests allowed per UTC day (see the free usage limits below)
571:// Free-model requests left in the current UTC day
638:FreeModelDailyRequests
644:# Free-model requests recorded so far in the current UTC day
647:# Free-model requests allowed per UTC day (see the free usage limits below)
650:# Free-model requests left in the current UTC day
---HF
AWS Trainium & Inferentia Accelerate Bitsandbytes CLI Chat UI Dataset viewer Datasets Deploying on AWS Diffusers Google Cloud Google TPUs Gradio Hub Hub Python Library Huggingface.js Inference Endpoints (dedicated) Inference Providers Kernels LeRobot Leaderboards Lighteval Microsoft Azure OpenEnv Optimum PEFT Reachy Mini Safetensors Sentence Transformers TRL Tasks Text Embeddings Inference Tokenizers Trackio Transformers Transformers.js Xet smolagents timm Search documentation main EN Get Started Inference Providers Pricing and Billing Concepts Routing and Providers Hub Integration and Settings Security Capabilities Chat Completion Responses API (beta) 
226:Ollama allows cross-origin requests from `127.0.0.1` and `0.0.0.0` by default. Additional origins can be configured with `OLLAMA_ORIGINS`.
228:For browser extensions, you'll need to explicitly allow the extension's origin pattern. Set `OLLAMA_ORIGINS` to include `chrome-extension://*`, `moz-extension://*`, and `safari-web-extension://*` if you wish to allow all browser extensions access, or speci
232:OLLAMA_ORIGINS=chrome-extension://*,moz-extension://*,safari-web-extension://* ollama serve
mistral-docs 000
mistral-free 404
Data Processing Addendum
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### assistant · 2026-11-20T09:26:06.092Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\npython3 -I - <<'EOF'\nimport re\nt=open('pg_gem_price.html',errors='ignore').read()\ni=t.find('id=\"gemini-3.8-flash\"') if 'id=\"gemini-3.8-flash\"' in t else t.find('gemini-3.8-flash')\nseg=t[i:i+6000]\nj=seg.find('Used to improve our products')\nprint(' '.join(re.sub(r'<[^>]+>',' ',seg[j:j+300]).split()))\nEOF\npython3 -I $S/strip.py pg_or_limits.html | grep -inE \"per minute|20 |50 |1,?000 free|10 credits|purchased|at least\" | head -10 | cut -c1-340\necho ---HFcredits; python3 -I $S/strip.py pg_hf_price.html | grep -iE \"free users|\\\\$0|\\\\$2|\\\\$9|credit|monthly\" | head -8 | cut -c1-300\necho ---CFwhisper; python3 -I $S/strip.py pg_cf_models.html | grep -E \"^@cf/[a-z0-9/_.\\-]+\" | sort -u | grep -iE \"whisper|llama|qwen|gemma|gpt-oss|mistral|melotts|aura|nova\" | head -20\ncurl -sL -m 20 \"https://developers.cloudflare.com/workers-ai/models/whisper-large-v3-turbo/\" -o pg_cfw.html; python3 -I $S/strip.py pg_cfw.html | grep -iE \"arabic|neurons|per minute|input|\\\\$\" | head -6 | cut -c1-200",
 "description": "Gemini free data use, OpenRouter limits, CF models"
}
```

### assistant · 2026-11-20T09:26:10.927Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\ngh_(){ curl -sL -m 20 \"https://api.github.com/repos/$1\" | python3 -I -c \"\nimport sys,json\nd=json.load(sys.stdin)\nif 'full_name' not in d: print('$1','ERR',d.get('message')[:40]); sys.exit()\nl=d.get('license') or {}\nprint(d['full_name'],'| lic:',l.get('spdx_id'),'| stars:',d['stargazers_count'],'| pushed:',d['pushed_at'][:10],'| arch:',d['archived'],'|',(d.get('description') or '')[:70])\"; }\nfor r in ricky0123/vad Picovoice/porcupine dscripka/openWakeWord MycroftAI/mycroft-precise OHF-Voice/wyoming-openwakeword OHF-Voice/piper1-gpl rhasspy/piper-voices kyutai-labs/moshi microsoft/VibeVoice hexgrad/kokoro huggingface/transformers.js-examples jozefchutka/whisper-webgpu k2-fsa/sherpa-onnx openai/openai-agents-python livekit/agents pipecat-ai/pipecat; do gh_ $r & done; wait",
 "description": "Check wake-word VAD and voice repos metadata"
}
```

### user · 2026-11-20T09:26:12.375Z

**نتيجة أداة:**
```
Used to improve our products * [Yes](/docs/terms) * [No](/docs/terms) {% /table %} {% /tab %} {% tab title=&quot;Batch&quot; %} {% table %} * Feature * Free Tier * Paid Tier, per 1M tokens in USD --- * Input price * Not available * $0.375 through December 31, 2026.
1232:Credits purchased (all time)
1233:Requests per minute
1236:At least
1245:tier is selected by all-time credits purchased, independently of
1248:credits); an account that has purchased fewer credits than that reports
1271:: These endpoints also limit how many requests each client IP address can make per minute:
1324:, when you hit one of the platform limits above (free-model requests per minute or per day, key-management requests per day, per-IP burst limits, or DDoS protection).
1354:, purchase at least
1378:{"page":{"pagePath":"api_reference/limits","slug":"/api_reference/limits","pageMetadata":{"publish":true,"title":"Limits","description":"Credit Limits and Rate Limits","seoTitle":"API Credit \u0026 Rate Limits | Handle 402 and 429 Errors in OpenRouter","og:site_name":"OpenRouter Documentation","og:title":"API Credit \u0026 Rate Limit
---HFcredits
Included Monthly Credits
PRO users and Team or Enterprise organizations receive monthly credits to use with Inference Providers. Free users can use Inference Providers by purchasing credits, or by upgrading to
Monthly Credits
Free Users
Your monthly credits automatically apply when you route requests through Hugging Face. For Team or Enterprise organizations, credits are shared among all members.
can use the API beyond their included monthly credits (if any) by purchasing additional credits. This ensures uninterrupted access to models for production workloads.
Monthly
---CFwhisper
$0.000513 per audio minute
Input
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

### user · 2026-11-20T09:26:13.539Z

**نتيجة أداة:**
```
ricky0123/vad ERR API rate limit exceeded for 196.136.31.1
Picovoice/porcupine ERR API rate limit exceeded for 196.136.31.1
dscripka/openWakeWord ERR API rate limit exceeded for 196.136.31.1
MycroftAI/mycroft-precise ERR API rate limit exceeded for 196.136.31.1
OHF-Voice/wyoming-openwakeword ERR API rate limit exceeded for 196.136.31.1
pipecat-ai/pipecat ERR API rate limit exceeded for 196.136.31.1
k2-fsa/sherpa-onnx ERR API rate limit exceeded for 196.136.31.1
OHF-Voice/piper1-gpl ERR API rate limit exceeded for 196.136.31.1
livekit/agents ERR API rate limit exceeded for 196.136.31.1
openai/openai-agents-python ERR API rate limit exceeded for 196.136.31.1
microsoft/VibeVoice ERR API rate limit exceeded for 196.136.31.1
hexgrad/kokoro ERR API rate limit exceeded for 196.136.31.1
huggingface/transformers.js-examples ERR API rate limit exceeded for 196.136.31.1
jozefchutka/whisper-webgpu ERR API rate limit exceeded for 196.136.31.1
kyutai-labs/moshi ERR API rate limit exceeded for 196.136.31.1
rhasspy/piper-voices ERR API rate limit exceeded for 196.136.31.1
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

### assistant · 2026-11-20T09:26:19.202Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\npython3 -I $S/strip.py pg_or_limits.html | sed -n 1225,1262p | tr '\\n' '|' | cut -c1-900; echo\npython3 -I $S/strip.py pg_or_limits.html | grep -inE \"free-model|free model\" | sed -n 1,12p | cut -c1-300\npython3 -I $S/strip.py pg_hf_price.html | grep -n -A6 -E \"^Free Users$\" | head -12 | tr '\\n' '|'; echo\ngh auth status 2>&1 | head -3",
 "description": "Read OpenRouter free limits and HF credits"
}
```

### user · 2026-11-20T09:26:21.581Z

<details><summary>نتيجة أداة (2013 حرف)</summary>

```
to avoid hitting the cap partway through.|Rate limits|Rate limits govern how many requests you can make. There are a few rate limits that apply to certain types of requests, regardless of account status:|Free usage limits|: If you’re using a free model variant (with an ID ending in|:|), the following limits apply:|Credits purchased (all time)|Requests per minute|Requests per day|Less than|At least|The|free_model_daily_requests|field in the|GET /api/v1/key|response above reports the daily counter and ceiling that gate your free-model requests when these limits apply to your account. Accounts and endpoints exempt from free-model limits, and BYOK requests, are not gated by it, so|remaining|reflects the tier policy rather than an enforced ceiling for them. The per-minute limit is not reported there. The|limit|tier is selected by all-time credits purchased, independently of|is_free_tier|. T

10:How do I use the best free models in OpenRouter?
136:How many requests you can make (free-model request caps, key-management caps, per-IP burst limits, and DDoS protection)
138:headers on free-model and key-management errors
561:// Free-model requests recorded so far in the current UTC day
566:// Free-model requests allowed per UTC day (see the free usage limits below)
571:// Free-model requests left in the current UTC day
644:# Free-model requests recorded so far in the current UTC day
647:# Free-model requests allowed per UTC day (see the free usage limits below)
650:# Free-model requests left in the current UTC day
837:// Free-model requests recorded so far in the current UTC day
841:// Free-model requests allowed per UTC day (see the free usage limits below)
845:// Free-model requests left in the current UTC day
134:Free Users|135-None|136--|137-yes (credits purchase required)|138-PRO Users|139-$2.00|140-All Hugging Face compute services|
github.com
  ✓ Logged in to github.com account 686877M (keyring)
  - Active account: true
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### assistant · 2026-11-20T09:26:28.222Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\ng(){ gh api -X GET \"repos/$1\" --jq '\"\\(.full_name) | lic: \\(.license.spdx_id) | stars: \\(.stargazers_count) | pushed: \\(.pushed_at[0:10]) | arch: \\(.archived) | \\(.description[0:70])\"' 2>&1 | head -1; }\nfor r in ricky0123/vad Picovoice/porcupine dscripka/openWakeWord OHF-Voice/wyoming-openwakeword pipecat-ai/pipecat livekit/agents rhasspy/piper-voices kyutai-labs/moshi hexgrad/kokoro  OHF-Voice/piper1-gpl open-webui/open-webui n8n-io/n8n coqui-ai/TTS idiap/coqui-ai-TTS; do g $r & done; wait\necho ---licenses; gh api repos/open-webui/open-webui/license --jq '.license.name, (.content|@base64d|.[0:700])' 2>&1 | head -14",
 "description": "Query GitHub via gh for wake word and TTS repos"
}
```

### user · 2026-11-20T09:26:32.654Z

<details><summary>نتيجة أداة (2692 حرف)</summary>

```
ricky0123/vad | lic: NOASSERTION | stars: 2079 | pushed: 2026-09-12 | arch: false | Voice activity detector (VAD) for the browser with a simple API
{"message":"Not Found","documentation_url":"https://docs.github.com/rest/repos/repos#get-a-repository","status":"404"}gh: Not Found (HTTP 404)
{"message":"Not Found","documentation_url":"https://docs.github.com/rest/repos/repos#get-a-repository","status":"404"}gh: Not Found (HTTP 404)
pipecat-ai/pipecat | lic: BSD-2-Clause | stars: 17356 | pushed: 2026-11-20 | arch: false | Open Source framework for voice agents, multimodal apps, and realtime 
hexgrad/kokoro | lic: Apache-2.0 | stars: 10253 | pushed: 2025-08-06 | arch: false | https://hf.co/hexgrad/Kokoro-82M
dscripka/openWakeWord | lic: Apache-2.0 | stars: 2962 | pushed: 2025-12-30 | arch: false | An open-source audio wake word (or phrase) detection framework with a 
Picovoice/porcupine | lic: Apache-2.0 | stars: 5026 | pushed: 2026-11-12 | arch: false | On-device wake word detection powered by deep learning
open-webui/open-webui | lic: NOASSERTION | stars: 159133 | pushed: 2026-11-20 | arch: false | User-friendly AI Interface (Supports Ollama, OpenAI API, ...)
livekit/agents | lic: Apache-2.0 | stars: 15285 | pushed: 2026-11-20 | arch: false | A framework for building realtime voice AI agents 🤖🎙️📹 
OHF-Voice/piper1-gpl | lic: GPL-3.0 | stars: 6333 | pushed: 2026-11-19 | arch: false | Fast and local neural text-to-speech engine
kyutai-labs/moshi | lic: Apache-2.0 | stars: 11566 | pushed: 2026-09-09 | arch: false | Moshi is a speech-text foundation model and full-duplex spoken dialogu
n8n-io/n8n | lic: NOASSERTION | stars: 211485 | pushed: 2026-11-20 | arch: false | Fair-code workflow automation platform with native AI capabilities. Co
idiap/coqui-ai-TTS | lic: MPL-2.0 | stars: 2356 | pushed: 2026-11-16 | arch: false | 🐸💬 - a deep learning toolkit for Text-to-Speech, battle-tested in rese
coqui-ai/TTS | lic: MPL-2.0 | stars: 46258 | pushed: 2024-08-16 | arch: false | 🐸💬 - a deep learning toolkit for Text-to-Speech, battle-tested in rese
---licenses
Other
Open WebUI License

Copyright (c) 2023- Open WebUI Inc. [Created by Timothy Jaeryang Baek]
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### assistant · 2026-11-20T09:26:47.092Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\nq(){ curl -s -m 20 \"https://huggingface.co/api/models?search=$1&limit=${2:-6}&sort=downloads&direction=-1\" | python3 -I -c \"\nimport sys,json\nfor d in json.load(sys.stdin): print('  ',d['id'],'| dl',d.get('downloads'),'|',[t.replace('license:','') for t in d.get('tags',[]) if t.startswith('license:')])\"; }\necho tts-egyptian; q tts+egyptian 6; echo habibi; q habibi+tts 5; echo orpheus-arabic; q orpheus+arabic 5; echo chatterbox; q chatterbox+multilingual 4; echo mms-tts-ara; q mms-tts-ara 3; echo xtts; q xtts-v2 3; echo arabic-tts; q arabic+tts 10\necho piper-ar; curl -s -m 20 \"https://huggingface.co/api/models/rhasspy/piper-voices/tree/main/ar?recursive=true\" | python3 -I -c \"\nimport sys,json\nprint([f['path'] for f in json.load(sys.stdin) if f['path'].endswith('.onnx')])\"\necho kokoro; curl -sL -m 20 https://huggingface.co/hexgrad/Kokoro-82M/raw/main/README.md | grep -iE \"arabic|languages|lang_code|apache\" | head -6 | cut -c1-200",
 "description": "Search HF for Arabic TTS models and Piper voices"
}
```

### assistant · 2026-11-20T09:26:50.501Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\ncurl -sL -m 30 \"https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=tts\" -o pg_az_tts.html -w \"azure %{http_code} %{size_download}\\n\"; python3 -I $S/strip.py pg_az_tts.html | grep -iE \"ar-EG|ar-SA|ar-AE\" | head -8 | cut -c1-200\ncurl -sL -m 30 \"https://ai.google.dev/gemini-api/docs/speech-generation\" -o pg_gem_tts.html -w \"gemtts %{http_code}\\n\"; python3 -I $S/strip.py pg_gem_tts.html | grep -iE \"ar-EG|Arabic\" | head -4 | cut -c1-200\ncurl -sL -m 30 \"https://raw.githubusercontent.com/rany2/edge-tts/master/README.md\" -o edge.md -w \"edge-tts %{http_code}\\n\"; grep -iE \"license|unofficial|Microsoft Edge|online|api\" edge.md | head -6 | cut -c1-200\ngh api repos/rany2/edge-tts --jq '\"\\(.license.spdx_id) | \\(.stargazers_count) | \\(.pushed_at[0:10])\"'",
 "description": "Check Azure Arabic voices, Gemini TTS, edge-tts"
}
```

### user · 2026-11-20T09:26:54.119Z

<details><summary>نتيجة أداة (3117 حرف)</summary>

```
tts-egyptian
   NAMAA-Space/NAMAA-Egyptian-TTS | dl 303 | ['mit']
   MAdel121/f5-tts-egyptian-arabic | dl 36 | ['cc-by-nc-4.0']
   ehabnegm/masri-higgs-v3-egyptian-tts | dl 32 | ['other']
   ehabnegm/higgs-tts-3-4b-egyptian-v3 | dl 31 | []
   ehabnegm/higgs-tts-3-4b-egyptian-v3-serve | dl 15 | []
   Momenrezk11/NAMAA-Egyptian-TTS | dl 14 | ['mit']
habibi
   SWivid/Habibi-TTS | dl 44432 | ['cc-by-nc-sa-4.0']
   Jip7e/habibi-tts-doda-darija | dl 2948 | ['apache-2.0']
   mohamedalgmaal/Habibi-TTS | dl 37 | ['cc-by-nc-sa-4.0']
   niobures/Habibi-TTS | dl 3 | ['cc-by-nc-sa-4.0']
   bmz86/habibi-tts-endpoint | dl 0 | ['cc-by-nc-sa-4.0']
orpheus-arabic
   mradermacher/Vysakh-Orpheus-3B-Arabic-v1.1-GGUF | dl 63 | []
   Abdullah-Baqais/orpheus-arabic-tts-16bit | dl 26 | []
   TaffaByte/orpheus_arabic_finetune_16bit | dl 22 | ['apache-2.0']
chatterbox
   mlx-community/chatterbox-multilingual-v3 | dl 7153 | ['mit']
   BricksDisplay/Chatterbox-Multilingual-TTS-GGUF | dl 5776 | ['mit']
   onnx-community/chatterbox-multilingual-ONNX | dl 3578 | ['mit']
   aufklarer/Chatterbox-Multilingual-MLX-fp16 | dl 1340 | ['mit']
mms-tts-ara
   facebook/mms-tts-ara | dl 5050 | ['cc-by-nc-4.0']
   facebook/mms-tts-urd-script_arabic | dl 3260 | ['cc-by-nc-4.0']
   facebook/mms-tts-uig-script_arabic | dl 2549 | ['cc-by-nc-4.0']
xtts
   coqui/XTTS-v2 | dl 4979633 | ['other']
   onicubag/xTTSv2-GGUF | dl 172141 | ['mpl-2.0']
   tts-hub/XTTS-v2 | dl 51179 | ['other']
arabic-tts
   facebook/mms-tts-urd-script_arabic | dl 3260 | ['cc-by-nc-4.0']
   facebook/mms-tts-uig-script_arabic | dl 2549 | ['cc-by-nc-4.0']
   facebook/mms-tts-kmr-script_arabic | dl 2389 | ['cc-by-nc-4.0']
   IbrahimSalah/Arabic-TTS-Spark | dl 2035 | ['fair-noncommercial-research-license']
   mradermacher/saudi-arabic-tts-GGUF | dl 509 | ['mit']
   anwar-dev/Bayan-Arabic-TTS-v1.0 | dl 462 | ['other']
   ffuy87y/spark-tts-clartts-arabic-v1 | dl 292 | []
   ixxan/mms-tts-uig-script_arabic-UQSpeech | dl 287 | ['cc-by-nc-4.0']
   omarabdelrahim/spark-tts-clartts-arabic-v1 | dl 247 | []
   AhmedEladl/Magpie-TTS-Saudi-Arabic | dl 219 | ['cc-by-nc-4.0']
piper-ar
['ar/ar_JO/kareem/low/ar_JO-kareem-low.onnx', 'ar/ar_JO/kareem/medium/ar_JO-kareem-medium.onnx']
kokoro
license: apache-2.0
**Kokoro** is an open-weight TTS model with 82 million parameters. Despite its lightweight architecture, it delivers comparable quality to larger models while being significantly faster and more cost-
> This is an Apache-licensed model, and Kokoro has been deployed in numerous projects and commercial APIs. We welcome the deployment of the model in real use cases.
You can run this basic cell on [Google Colab](https://colab.research.google.com/). [Listen to samples](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/SAMPLES.md). For more languages and details, 
pipeline = KPipeline(lang_code='a')
[Kokoro](/kˈOkəɹO/) is an open-weight TTS model with 82 million parameters. Despite its lightweight architecture, it delivers comparable quality to larger models while being significantly faster an
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### user · 2026-11-20T09:26:58.596Z

**نتيجة أداة:**
```
azure 200 377486
ar-AE
ar-EG
ar-SA
ar-AE
ar-EG
ar-SA
ar-AE
ar-EG
gemtts 200
| Egyptian Arabic | ✔️ | ✔️ |
| Standard Arabic (Arab script) | ✔️ | ✔️ |
| Standard Arabic (Latn script) | ✔️ | ✔️ |
edge-tts 200
`edge-tts` is a Python module that allows you to use Microsoft Edge's online text-to-speech service from within your Python code or using the provided `edge-tts` or `edge-playback` command.
Support for custom SSML was removed because Microsoft prevents the use of any SSML that could not be generated by Microsoft Edge itself. This means that all the cases where custom SSML would be useful
NOASSERTION | 12588 | 2026-11-18
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

### assistant · 2026-11-20T09:27:15.572Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\nrd(){ curl -sL -m 25 \"https://raw.githubusercontent.com/$1\" -o rd_$2.md -w \"$2 %{http_code} %{size_download}\\n\"; }\nrd mudler/LocalAI/master/README.md localai & rd Mintplex-Labs/anything-llm/master/README.md anything & rd open-webui/open-webui/main/README.md owui & rd LibreChat-AI/LibreChat/main/README.md libre & rd openinterpreter/openinterpreter/main/README.md oi & rd ricky0123/vad/master/README.md vad & rd dscripka/openWakeWord/main/README.md oww & wait\nfor f in localai anything owui libre oi; do echo \"== $f\"; grep -iE \"mcp|openai.compatible|openai api|whisper|speech|voice|tts|stt|license\" rd_$f.md | head -7 | cut -c1-230; done\necho == oww; grep -iE \"jarvis|alexa|pre-trained|hey_|browser|javascript|onnx|tflite|license|cc by\" rd_oww.md | head -8 | cut -c1-230\necho == vad; grep -iE \"browser|onnx|silero|license|npm|webgpu|wasm\" rd_vad.md | head -5 | cut -c1-200\necho == ha; curl -sL -m 25 https://www.home-assistant.io/integrations/mcp_server/ -o pg_ha_mcp.html -w \"%{http_code}\\n\"; python3 -I $S/strip.py pg_ha_mcp.html | grep -iE \"model context|MCP server|Assist|stdio|SSE|streamable|http\" | head -5 | cut -c1-240\ncurl -sL -m 25 https://www.home-assistant.io/voice_control/ -o pg_ha_voice.html -w \"%{http_code}\\n\"; python3 -I $S/strip.py pg_ha_voice.html | grep -iE \"arabic|wake word|whisper|piper|wyoming|languages|openai|LLM|local\" | head -8 | cut -c1-240",
 "description": "Grep agent project READMEs for MCP and OpenAI API"
}
```

### user · 2026-11-20T09:27:16.827Z

<details><summary>نتيجة أداة (4210 حرف)</summary>

```
Exit code 1
localai 200 17808
oww 200 27414
owui 200 7247
anything 200 25769
oi 200 8364
vad 200 3123
libre 200 14939
== localai
<a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square" alt="MIT license"></a>
**LocalAI** runs open models for chat, images, speech and video on your own machines. The API speaks the OpenAI and Anthropic formats. Your team gets chats, files and documents on top, and the assistant can write and run code. It 
- **Chats, agents, Projects and a team**: chats and saved agents that use tools, [MCP](https://localai.io/docs/features/mcp/) servers, files, Knowledge collections and skills. [Projects](https://localai.io/docs/features/projects/)
- **Every kind of model, one API**: text, vision, speech to text, text to speech, images, video, music and sound, embeddings and reranking, in the OpenAI and Anthropic formats (with ElevenLabs-compatible text to speech and sound g
![LocalAI is a small core with an API, chats and agents, files, collections, team sharing, a model gallery and an MCP client and server for agent tools. Backends such as llama.cpp, vLLM, MLX and whisper.cpp plug in on one side, ad
| [Chats](https://localai.io/docs/features/chats/) | Conversations the server keeps, with saved agents that use tools, [MCP](https://localai.io/docs/features/mcp/), skills and files, triggers, and chat apps |
| [Text generation](https://localai.io/docs/models/capabilities/text/text-generation/) | `llama.cpp`, `transformers`, `vllm` ... [and more](https://localai.io/docs/models/compatibility-table/), with an [OpenAI-compatible tools API
== anything
  <a href="https://github.com/Mintplex-Labs/anything-llm/blob/master/LICENSE" target="_blank">
      <img src="https://img.shields.io/static/v1?label=license&message=MIT&color=white" alt="License">
- [MCP-compatibility](https://docs.anythingllm.com/mcp-compatibility/overview)
- Works with all popular [closed and open-source LLM providers](#supported-llms-embedder-models-speech-models-and-vector-databases).
### Supported LLMs, Embedder Models, Speech models, and Vector Databases
- Generic OpenAI-compatible embedding APIs
**TTS (text-to-speech) support:**
== owui
<p>Open WebUI is <a href="https://docs.openwebui.com/"><strong>a home for AI</strong></a>: an extensible, easy-to-use, self-hosted platform built to run entirely offline. Connect local models through Ollama or use OpenAI-compatibl
| `:slim`   | Lightweight image using external services for embeddings, document extraction, and voice |
| `-e OPENAI_API_KEY=[REDACTED]                  | Set your OpenAI API key                                                                  |
#### License
Includes code under the Open WebUI License, which requires preserving the Open WebUI branding, and prior contributions under their original licenses. See [LICENSE](./LICENSE) and [LICENSE_HISTORY](./LICENSE_HISTORY) for terms and 
== libre
- **Tools and prompts:** Use MCP Apps, deferred Tool Search, clearer approvals, and Langfuse prompts in the catalog and Agent instructions.
  - [Custom Endpoints](https://www.librechat.ai/docs/quick_start/custom_endpoints): Use any OpenAI-compatible API with LibreChat, no proxy required
    - Flexible & Extensible: Use MCP Servers, tools, file search, code execution, and more
    - [Agent Plugins](https://www.librechat.ai/docs/features/agent_plugins): Experimentally bundle deployment Skills and MCP servers into startup-loaded packages
    - [Model Context Protocol (MCP) Support](https://modelcontextprotocol.io/clients#librechat) for Tools
  - Text-to-image with [Stable Diffusion](https://www.librechat.ai/docs/features/image_gen#3--stable-diffusion-local), [Flux](https://www.librechat.ai/docs/features/image_gen#4--flux), or any [MCP server](https://www.librechat.ai/
- 🗣️ **Speech & Audio**:  
== oi
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/License-Apache--2.0-white?style=flat-square" /></a>
MCP, ACP, and the Codex exec protocol. Product-specific storage under
- Runs any selected OpenAI-compatible provider through Chat Completions with
- Supports `exec`, MCP, skills, hooks, permissions, and `AGENTS.md`.
## License
(eval):5: = not found
```

</details>

### assistant · 2026-11-20T09:27:24.929Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\necho \"[oww]\"; grep -iE \"jarvis|alexa|pre-trained|browser|javascript|onnx|license|cc by|hey\" rd_oww.md | head -8 | cut -c1-230\necho \"[vad]\"; grep -iE \"browser|onnx|silero|license|npm|webgpu|wasm\" rd_vad.md | head -4 | cut -c1-200\ncurl -sL -m 25 https://www.home-assistant.io/integrations/mcp_server/ -o pg_ha_mcp.html -w \"ha-mcp %{http_code}\\n\"; python3 -I $S/strip.py pg_ha_mcp.html | grep -iE \"model context|MCP server|stdio|SSE|streamable|http\" | head -5 | cut -c1-240\ncurl -sL -m 25 https://www.home-assistant.io/voice_control/ -o pg_ha_voice.html -w \"ha-voice %{http_code}\\n\"; python3 -I $S/strip.py pg_ha_voice.html | grep -iE \"arabic|wake word|whisper|piper|wyoming|languages|openai|LLM\" | head -8 | cut -c1-240\ncurl -sL -m 25 https://docs.openwebui.com/features/mcp -o pg_owui_mcp.html -w \"owui-mcp %{http_code}\\n\"; python3 -I $S/strip.py pg_owui_mcp.html | grep -iE \"streamable|mcpo|native|OpenAPI|MCP\" | head -6 | cut -c1-240\necho \"[mdn]\"; curl -sL -m 25 https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition -o pg_mdn_sr.html -w \"%{http_code}\\n\"; python3 -I $S/strip.py pg_mdn_sr.html | grep -iE \"server|processLocally|local|continuous|privacy|Chrome|installOnDevice|ar-\" | head -8 | cut -c1-240\ncurl -sL -m 25 https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis/getVoices -o pg_mdn_sv.html -w \"%{http_code}\\n\"; python3 -I $S/strip.py pg_mdn_sv.html | grep -iE \"voiceschanged|asynchron|empty|localService\" | head -4 | cut -c1-240",
 "description": "Check wake word, HA voice, Open WebUI MCP, MDN speech APIs"
}
```

### assistant · 2026-11-20T09:27:28.771Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\nq(){ curl -s -m 20 \"https://huggingface.co/api/models?author=$1&sort=lastModified&direction=-1&limit=${2:-10}\" | python3 -I -c \"\nimport sys,json\nfor d in json.load(sys.stdin): print('  ',d['id'],d.get('lastModified','')[:10],[t.replace('license:','') for t in d.get('tags',[]) if t.startswith('license:')])\"; }\necho nous; q NousResearch 12\ncurl -sL -m 20 https://huggingface.co/api/models/ResembleAI/chatterbox | python3 -I -c \"\nimport sys,json;d=json.load(sys.stdin);print('chatterbox',[t for t in d.get('tags',[]) if t.startswith('license')],d.get('lastModified','')[:10])\"\ncurl -sL -m 20 https://huggingface.co/ResembleAI/chatterbox/raw/main/README.md | grep -iE \"arabic|ar\\b|languages|23\" | head -4 | cut -c1-200\necho ALLaM-tags; curl -sL \"https://huggingface.co/api/models?author=humain-ai&limit=10&sort=lastModified&direction=-1\" | python3 -I -c \"\nimport sys,json\nfor d in json.load(sys.stdin): print('  ',d['id'],d.get('lastModified','')[:10],[t.replace('license:','') for t in d.get('tags',[]) if t.startswith('license:')])\"",
 "description": "List Nous Hermes models, Chatterbox languages, ALLaM"
}
```

### user · 2026-11-20T09:27:33.742Z

<details><summary>نتيجة أداة (3223 حرف)</summary>

```
[oww]
openWakeWord is an open-source wakeword library that can be used to create voice-enabled applications and interfaces. It includes pre-trained models for common words & phrases that work well in real-world environments.
You can try an online demo of the included pre-trained models via HuggingFace Spaces [right here](https://huggingface.co/spaces/davidscripka/openWakeWord)!
On Linux systems, both the [onnxruntime](https://pypi.org/project/onnxruntime/) package and [tflite-runtime](https://pypi.org/project/tflite-runtime/) packages will be installed as dependencies since both inference frameworks are 
For quick local testing, clone this repository and use the included [example script](examples/detect_from_microphone.py) to try streaming detection from a local microphone. You can individually download pre-trained models from cur
# One-time download of all pre-trained models (or only select models)
    wakeword_models=["path/to/model.tflite"],  # can also leave this argument empty to load all of the included pre-trained models
    wakeword_models = ["hey jarvis"],
4) Require **little to no manual data collection** to train new models. The included models (see the [Pre-trained Models](#pre-trained-models) section for more details) were all trained with *100% synthetic* speech generated from 
[vad]
[![npm vad-web](https://img.shields.io/npm/v/@ricky0123/vad-web?color=blue&label=%40ricky0123%2Fvad-web&style=flat-square)](https://www.npmjs.com/package/@ricky0123/vad-web)
[![npm vad-react](https://img.shields.io/npm/v/@ricky0123/vad-react?color=blue&label=%40ricky0123%2Fvad-react&style=flat-square)](https://www.npmjs.com/package/@ricky0123/vad-react)
This package aims to provide an accurate, user-friendly voice activity detector (VAD) that runs in the browser. By using this package, you can prompt the user for microphone permissions, start recordi
Under the hood, these packages run [Silero VAD](https://github.com/snakers4/silero-vad) [[1]](#1) using [ONNX Runtime Web](https://github.com/microsoft/onnxruntime/tree/main/js/web) / [ONNX Runtime No
ha-mcp 200
Model Context Protocol - Home Assistant
Model Context Protocol
Model Context Protocol
Third-party software that connects to Home Assistant through the Model Context Protocol integration.
Model Context Protocol
ha-voice 200
Supported languages and sentences
OpenAI
LLM integration
wake word
wake words
To further improve your setup, try building other voice assistant satellite devices that allow you to add Assist with wake words to all your rooms:
wake word detection on your Android phone
Supported languages and sentences
owui-mcp 404
[mdn]
200
Privacy
On some browsers, speech recognition uses a server-based recognition engine by default.
processLocally
SpeechRecognition.continuous
Controls whether continuous results are returned for each recognition, or only a single result. Defaults to single (
SpeechRecognition.processLocally
Specifies whether speech recognition must be performed locally on the user's device.
recognition.continuous = false;
200
speechSynthesis.onvoiceschanged !== undefined
speechSynthesis.onvoiceschanged = populateVoiceList;
voiceschanged
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### user · 2026-11-20T09:27:38.286Z

**نتيجة أداة:**
```
nous
   NousResearch/Arete-27B 2026-11-06 ['apache-2.0']
   NousResearch/moe-10b-a1b-8k-wsd-lr3e4-1t 2026-04-01 []
   NousResearch/Kimi-K2-Thinking-Alternate-Tokenizer 2026-02-10 []
   NousResearch/nomos-1 2026-01-10 ['apache-2.0']
   NousResearch/Hermes-4-14B 2026-01-09 ['apache-2.0']
   NousResearch/NousCoder-14B 2026-01-05 ['apache-2.0']
   NousResearch/Hermes-4.3-36B 2025-12-06 ['apache-2.0']
   NousResearch/Hermes-4.3-36B-GGUF 2025-12-03 ['apache-2.0']
   NousResearch/Hermes-4.3-36B-centralized 2025-12-03 []
   NousResearch/k2-merged-3.5T-fp8 2025-11-15 ['other']
   NousResearch/k2-merged-3.5T-bf16 2025-11-15 ['other']
   NousResearch/huskyholdem-batches 2025-09-24 []
chatterbox ['license:mit'] 2026-06-10
- ar
**Chatterbox Multilingual V3** is the latest general-purpose multilingual TTS model in the Chatterbox family. It keeps the same 0.5B model size while improving speaker similarity, reducing hallucinati
V3 is designed for broad language coverage like V2, but with stronger stability and more expressive generation. It is the recommended multilingual model for users who want one voice cloning model that
Alongside V3, we are releasing the **Single Language Pack**: dedicated finetunes for priority languages where tighter quality control, stronger language-specific behavior, and more specialized speech 
ALLaM-tags
   humain-ai/ALLaM-7B-Instruct-preview 2025-07-14 ['apache-2.0']
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

### assistant · 2026-11-20T09:27:49.072Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\ncurl -sL -m 20 https://raw.githubusercontent.com/ollama/ollama/main/docs/macos.mdx | grep -iE \"intel|apple silicon|macos [0-9]|requirement|metal\" | head -8 | cut -c1-250\necho \"[lmstudio]\"; curl -sL -m 25 https://lmstudio.ai/docs/app/system-requirements -o pg_lms.html -w \"%{http_code}\\n\"; python3 -I $S/strip.py pg_lms.html | grep -iE \"mac|intel|apple silicon|arm|x64|16GB|RAM\" | head -8 | cut -c1-240\necho \"[inception42]\"; curl -s \"https://huggingface.co/api/models?author=inception42&sort=lastModified&direction=-1&limit=12\" | python3 -I -c \"\nimport sys,json\nfor d in json.load(sys.stdin): print('  ',d['id'],d.get('lastModified','')[:10])\"\necho \"[IFM]\"; curl -s \"https://huggingface.co/api/models?author=IFM&sort=lastModified&direction=-1&limit=14\" | python3 -I -c \"\nimport sys,json\nfor d in json.load(sys.stdin): print('  ',d['id'],d.get('lastModified','')[:10])\"\necho \"[ollama jais?]\"; curl -s -m 20 \"https://ollama.com/search?q=jais\" | python3 -I $S/strip.py /dev/stdin | sed -n 30,50p | tr '\\n' '|' | cut -c1-500",
 "description": "Check Intel Mac support and Jais variants"
}
```

### user · 2026-11-20T09:27:59.179Z

**نتيجة أداة:**
```
## System Requirements
## Filesystem Requirements
[lmstudio]
200
Supported CPU, GPU types for LM Studio on Mac (M1/M2/M3/M4), Windows (x64/ARM), and Linux (x64/ARM64)
macOS
Chip: Apple Silicon (M1/M2/M3/M4).
macOS 14.0 or newer is required.
16GB+ RAM recommended.
You may still be able to use LM Studio on 8GB Macs, but stick to smaller models and modest context sizes.
Intel-based Macs are currently not supported. Chime in
LM Studio is supported on both x64 and ARM (Snapdragon X Elite) based systems.
[inception42]
   inception42/Jais-3-MoVA-36B-A4B 2026-11-12
   inception42/Jais-3-7B 2026-11-12
   inception42/Jais-3-7B-Uno 2026-11-12
   inception42/Jais-3-375B-A23B 2026-11-12
   inception42/Jais-3-32B 2026-11-12
   inception42/Jais-3-32B-Uno 2026-11-12
   inception42/Jais-3-3.7B 2026-11-12
   inception42/Jais-3-3.7B-Uno 2026-11-12
   inception42/Jais-3-0.9B 2026-11-12
   inception42/Jais-3-0.9B-Uno 2026-11-12
   inception42/Jais-2-70B-Chat 2026-08-18
   inception42/Jais-2-8B-Chat 2026-08-18
[IFM]
   IFM/latent-feedback-checkpoints 2026-11-13
   IFM/PAN2 2026-11-12
   IFM/Jais-3-MoVA-36B-A4B-MLX-bf16 2026-11-11
   IFM/Jais-3-MoVA-36B-A4B-MLX-8bit 2026-11-11
   IFM/Jais-3-MoVA-36B-A4B-MLX-4bit 2026-11-11
   IFM/Jais-3-7B-MLX-bf16 2026-11-11
   IFM/Jais-3-7B-MLX-8bit 2026-11-11
   IFM/Jais-3-7B-MLX-4bit 2026-11-11
   IFM/Jais-3-32B-MLX-bf16 2026-11-11
   IFM/Jais-3-32B-MLX-8bit 2026-11-11
   IFM/Jais-3-32B-MLX-4bit 2026-11-11
   IFM/Jais-3-3.7B-MLX-bf16 2026-11-11
   IFM/Jais-3-3.7B-MLX-8bit 2026-11-11
   IFM/Jais-3-3.7B-MLX-4bit 2026-11-11
[ollama jais?]
Where|Any|Local|Cloud|Capabilities|Tools|Thinking|Vision|Embedding|Decision|Download size|Any size|Up to 8 GB|Up to 16 GB|Up to 32 GB|Up to 64 GB|Over 64 GB|Show 20+ models|jais · Ollama|Search for models on Ollama.|jais/GLaDOS|
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

### assistant · 2026-11-20T09:28:07.191Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\ncurl -sL -m 25 https://huggingface.co/inception42/Jais-3-7B/raw/main/README.md -o jais3.md; wc -c jais3.md; grep -iE \"dialect|egypt|tool|context|license|parameters|benchmark|AraGen|Arabic|chat|instruct|base|gguf\" jais3.md | head -24 | cut -c1-300\necho \"[ollama intel]\"; gh api repos/ollama/ollama/releases --jq '.[0:25]|.[]|select(.body|test(\"Intel|x86_64|darwin\";\"i\"))|\"\\(.tag_name): \\(.body|split(\"\\n\")|map(select(test(\"Intel|x86\";\"i\")))|.[0:2]|join(\" / \"))\"' 2>&1 | head -6 | cut -c1-300\ncurl -sL -m 20 https://raw.githubusercontent.com/ollama/ollama/main/docs/macos.mdx | head -30 | cut -c1-200",
 "description": "Read Jais-3 card and Ollama Intel Mac notes"
}
```

### user · 2026-11-20T09:28:26.745Z

<details><summary>نتيجة أداة (3538 حرف)</summary>

```
   90550 jais3.md
license: apache-2.0
Jais-3-7B is the medium dense member of the Jais-3 family: a 7B-class decoder-only model with a 512K context window.
> - GGUF for llama.cpp and Ollama: [IFM/Jais-3-7B-GGUF](https://huggingface.co/IFM/Jais-3-7B-GGUF)
  <a href="https://huggingface.co/inception42/Jais-3-7B/resolve/main/assets/jais-3-7b-benchmarks.png" target="_blank">
    <img src="assets/jais-3-7b-benchmarks.png" alt="Jais-3-7B benchmark results" width="100%">
## Benchmark Results
<div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;margin:0 auto;padding:8px 0 16px;overflow-x:auto"><table style="display:table;width:100%;table-layout:fixed;border-collapse:collapse;font-size:12px;margin:0"><thead><tr><th style="width:23%;border-bottom:none"></th
> Starred (\*) benchmarks have been audited for sample quality. Items with ambiguous questions, invalid answer options, or indefensible gold labels were excluded, since they can penalize a correct answer or reward a lucky guess. Scores on these benchmarks are reported on the cleaned sets. The audit 
> Benchmarks marked with ^ will be released by IFM soon.
  --enable-auto-tool-choice \
  --tool-call-parser k2_horizon
  --tool-call-parser k2_horizon
> Recommended settings: `reasoning_effort="high"`, the sampling hyperparameters in the table below, and at least 32,768 output tokens.
> Reasoning depth is selected per request through `chat_template_kwargs`. Thinking is returned in `reasoning_content` and the answer in `content`.
| Parameter | Default | Thinking mode, English | Thinking mode, Arabic |
<div class="barA"><label for="a1">Reasoning Example</label><label for="a2">Tool Calling Example</label></div>
client = OpenAI(base_url="http://localhost:30000/v1", api_key="EMPTY")
response = client.chat.completions.create(
    extra_body={"top_k": 20, "chat_template_kwargs": {"reasoning_effort": "high"}},
client = OpenAI(base_url="http://localhost:30000/v1", api_key="EMPTY")
tools = [{
        "parameters": {
available_tools = {"get_current_time": get_current_time}
for _ in range(5):  # call the model, run any requested tools, repeat until it answers
[ollama intel]
v0.40.16: [Ripple Preview](https://ollama.com/library/ripple-preview) from Ricursive Intelligence is a 65B dense model built for agentic coding.
---
title: macOS
---

## System Requirements

* MacOS Sonoma (v14) or newer
* Apple M series (CPU and GPU support) or x86 (CPU only)


## Filesystem Requirements

The preferred method of installation is to mount the `ollama.dmg` and drag-and-drop the Ollama application to the system-wide `Applications` folder.  Upon startup, the Ollama app will verify the `olla

Once you've installed Ollama, you'll need additional space for storing the Large Language models, which can be tens to hundreds of GB in size.  If your home directory doesn't have enough space, you ca

### Changing Install Location

To install the Ollama application somewhere other than `Applications`, place the Ollama application in the desired location, and ensure the CLI `Ollama.app/Contents/Resources/ollama` or a sym-link to 


## Troubleshooting

Ollama on MacOS stores files in a few different locations.
- `~/.ollama` contains models and configuration
- `~/.ollama/logs` contains logs
    - *app.log* contains most recent logs from the GUI application
    - *server.log* contains the most recent server logs
- `<install location>/Ollama.app/Contents/Resources/ollama` the CLI binary
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### assistant · 2026-11-20T09:28:32.090Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\npython3 -I - <<'EOF'\nimport re,html\nt=open('jais3.md',errors='ignore').read()\ntbs=re.findall(r'<table.*?</table>',t,flags=re.S)\nprint(len(tbs))\nfor tb in tbs[:1]:\n    for tr in re.findall(r'<tr.*?</tr>',tb,flags=re.S):\n        c=[re.sub(r'\\s+',' ',html.unescape(re.sub(r'<[^>]+>','',x))).strip() for x in re.findall(r'<t[hd].*?</t[hd]>',tr,flags=re.S)]\n        if c: print(' | '.join(c)[:260])\nEOF\ngrep -inE \"egypt|dialect\" jais3.md | head -6 | cut -c1-260",
 "description": "Extract Jais-3-7B benchmark table"
}
```

### user · 2026-11-20T09:28:33.261Z

<details><summary>نتيجة أداة (4558 حرف)</summary>

```
1
 |  | Reference models
 | Jais-3-7B | Gemma-4-E4B-it | Gemma-4-12B-it | Qwen3.5-9B | Falcon-H1-7B-Instruct | Allam 7B | Fanar-1-9B-Instruct
# Params | 7B | 8B | 12B | 9B | 7B | 7B | 9B
# Activated/Effective params | 7B | 4B | 12B | 9B | 7B | 7B | 9B
Architecture | Dense | Dense | Dense | Dense | Dense | Dense | Dense
Open-ended Generation
AraGen
AraGen v3 (3C3H)09-2025 | 55.0 | 48.8 | 62.8 | 55.7 | 28.0 | 44.9 | 40.1
Correctness | 63.7 | 58.8 | 73.5 | 67.0 | 34.8 | 52.2 | 48.6
Completeness | 62.1 | 57.7 | 72.4 | 66.4 | 32.7 | 47.2 | 45.9
Conciseness | 20.6 | 10.7 | 18.4 | 13.9 | 10.6 | 30.8 | 17.7
Helpfulness | 58.8 | 51.2 | 66.7 | 57.9 | 26.1 | 43.4 | 40.2
Honesty | 62.0 | 56.7 | 72.4 | 62.8 | 29.9 | 47.0 | 41.9
Harmlessness | 62.9 | 57.7 | 73.2 | 66.4 | 33.6 | 48.9 | 46.2
Knowledge & Reasoning
General Knowledge & Comprehension
Arabic MMLU*Accuracy | 85.2 | 77.5 | 84.1 | 80.9 | 63.3 | 71.2 | 65.8
BelebeleAccuracy | 92.9 | 88.7 | 93.6 | 89.2 | 72.9 | 78.8 | 79.9
STEM & Math
AraSTEM*Accuracy | 92.6 | 89.7 | 93.7 | 93.4 | 76.6 | 79.0 | 73.0
Arabic GSM8K*Accuracy | 92.7 | 87.0 | 92.6 | 91.4 | 85.0 | 56.8 | 75.3
GATmath*Accuracy | 96.4 | 94.4 | 98.0 | 97.3 | 45.5 | 38.4 | 40.6
Professional Domains
MedAraBench*Accuracy | 78.3 | 68.4 | 81.0 | 80.8 | 48.0 | 49.1 | 50.7
Arabic Legal (HELM)*Accuracy | 65.9 | 63.1 | 67.4 | 64.3 | 57.9 | 61.2 | 61.8
Arabic Language & Culture
Islamic Knowledge & Arab Culture
IslamicQAAccuracy (mean of the 4 below) | 83.8 | 71.6 | 78.2 | 69.3 | 61.5 | 67.1 | 62.8
PaLM-X 2025-2*Accuracy | 91.2 | 82.9 | 89.6 | 84.5 | 74.3 | 85.9 | 80.3
QIAS-1*Accuracy | 88.5 | 62.5 | 74.5 | 61.1 | 44.0 | 31.2 | 36.3
QIAS-2*Accuracy | 80.7 | 69.5 | 81.3 | 72.3 | 65.8 | 72.9 | 64.9
IslamicEval2025-1B*Accuracy | 74.9 | 71.4 | 67.5 | 59.3 | 61.9 | 78.4 | 69.7
Arab CultureAccuracy (mean of the 3 below) | 83.8 | 78.5 | 84.2 | 77.3 | 65.5 | 76.1 | 71.1
ArabCulture*Accuracy | 84.9 | 81.6 | 87.0 | 80.4 | 72.4 | 77.7 | 77.3
AraDiCE-Culture*Accuracy | 81.0 | 76.0 | 81.6 | 74.9 | 59.2 | 79.3 | 67.0
Arabic Cuisine^Accuracy | 85.5 | 77.8 | 84.1 | 76.6 | 65.0 | 71.3 | 68.9
Dialects
Dialectal Arabic MMLU*Accuracy | 83.6 | 76.6 | 83.5 | 80.4 | 58.5 | 56.6 | 58.2
Dialect Identification (QADI)Accuracy | 69.0 | 59.8 | 62.1 | 35.7 | 38.1 | 42.8 | 46.2
Alyah*Accuracy | 80.7 | 77.2 | 82.5 | 68.3 | 65.7 | 77.5 | 69.6
Linguistics & Literature
Arabic MMLU with diacriticsAccuracy | 83.6 | 74.5 | 83.2 | 77.3 | 52.3 | 61.9 | 54.9
FannOrFlop-MCQAccuracy | 69.4 | 64.0 | 66.2 | 58.2 | 51.4 | 66.7 | 63.3
Arabic Linguistics^Accuracy (mean of the 2 below) | 93.2 | 84.1 | 93.0 | 81.5 | 47.5 | 67.5 | 57.6
DiacritizationAccuracy | 90.8 | 76.6 | 88.7 | 82.8 | 48.6 | 75.0 | 68.3
ParsingAccuracy | 95.5 | 91.6 | 97.4 | 80.2 | 46.4 | 59.9 | 46.9
Translation
FLORES200+LLM-as-a-judge | 90.6 | 84.0 | 89.5 | 74.3 | 59.8 | 74.5 | 68.4
Assistant Capabilities
Instruction Following
Arabic IFBench^Accuracy (prompt-level strict) | 91.6 | 42.6 | 75.3 | 58.3 | 26.2 | 18.9 | 25.8
Arabic IFEvalAccuracy | 80.2 | 72.3 | 78.7 | 73.8 | 62.4 | 48.0 | 44.6
Long Context
AA-LCR (Ar)Accuracy | 65.0 | - | 49.0 | 68.0 | 9.0 | - | -
Factuality & Hallucination
HalluScoreAccuracy | 55.1 | 38.2 | 55.4 | 48.8 | 14.7 | 34.8 | 42.4
SimpleQA Verified (Ar)Aggregate (2/3 F-score + 1/3 non-hallucination rate) | 25.7 | 24.4 | 9.4 | 8.5 | 3.8 | 4.2 | 6.1
F-score | 4.3 | 3.1 | 5.6 | 10.5 | 3.5 | 4.1 | 5.9
Non-hallucination rate | 68.3 | 67.0 | 17.1 | 4.4 | 4.5 | 4.5 | 6.6
Agentic
Terminal Bench 2.1Accuracy (Avg@3) | 46.4 | 1.9 | 27.3 | 29.2 | 0.0 | 0.0 | 0.0
GDPValAccuracy (@ 75% threshold) | 60.5 | 5.5 | 17.7 | 19.1 | 0.0 | 0.0 | 0.0
MCPMarkAccuracy (Pass@1) | 49.6 | 3.2 | 17.3 | 31.5 | 0.0 | 0.0 | 0.0
WildClawBench (English text-only subset)Mean Score@3 | 38.9 | 22.3 | 29.0 | 34.4 | 9.4 | 0.0 | 0.0
Apex-Agents (420 text-only subset, loop agent)Pass@1 (Accuracy) | 21.7 | 1.0 | 7.6 | 5.0 | 0.5 | 0.0 | 0.0
GAIA v2 lit (Ar)Accuracy (Pass@1) | 44.9 | 19.4 | 39.4 | 29.1 | 0.0 | 0.0 | 0.0
Arabic File ProcessingAccuracy (@ 75% threshold) | 45.5 | 0.0 | 0.9 | 0.5 | 0.0 | 0.0 | 0.0
SWE-Bench Verified (Offline)Accuracy (Pass@1) | 70.2 | 4.4 | 28.2 | 50.8 | 0.0 | 0.0 | 0.0
BrowseComp-PlusAccuracy | 67.7 | 21.2 | 21.9 | 49.5 | 0.4 | 0.1 | 0.4
38:<div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;margin:0 auto;padding:8px 0 16px;overflow-x:auto"><table style="display:table;width:100%;table-layout:fixed;border-collapse:collapse;font-size:12px;margin:0"><thead><tr><t
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### assistant · 2026-11-20T09:28:46.080Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\nfor m in Jais-3-7B-GGUF Jais-3-3.7B-GGUF Jais-3-32B-GGUF; do curl -s -m 20 \"https://huggingface.co/api/models/IFM/$m/tree/main\" | python3 -I -c \"\nimport sys,json\ntry:\n fs=json.load(sys.stdin); print('$m',[(f['path'],round(f.get('size',0)/1e9,2)) for f in fs if f['path'].endswith('.gguf') and ('Q4' in f['path'] or 'Q5_K_M' in f['path'] or 'Q8' in f['path'])])\nexcept Exception as e: print('$m ERR')\"; done\ncurl -sL -m 25 https://huggingface.co/inception42/Jais-3-32B/raw/main/README.md -o jais3_32.md\npython3 -I - <<'EOF'\nimport re,html\nt=open('jais3_32.md',errors='ignore').read()\ntb=re.findall(r'<table.*?</table>',t,flags=re.S)\nfor tr in re.findall(r'<tr.*?</tr>',tb[0],flags=re.S):\n    c=[re.sub(r'\\s+',' ',html.unescape(re.sub(r'<[^>]+>','',x))).strip() for x in re.findall(r'<t[hd].*?</t[hd]>',tr,flags=re.S)]\n    s=' | '.join(c)\n    if re.search(r'Reference|Jais-3-32B|# Params|AraGen v3|Arabic MMLU\\*|Dialectal Arabic MMLU|Arabic IFEval|MCPMark|Alyah|FLORES',s): print(s[:260])\nEOF\necho; curl -s -m 20 https://huggingface.co/api/models/NousResearch/Hermes-4.3-36B-GGUF/tree/main | python3 -I -c \"\nimport sys,json\nprint([(f['path'],round(f.get('size',0)/1e9,1)) for f in json.load(sys.stdin) if 'Q4_K_M' in f['path']])\"",
 "description": "Check Jais-3 GGUF sizes and 32B benchmarks"
}
```

### user · 2026-11-20T09:28:48.825Z

**نتيجة أداة:**
```
Jais-3-7B-GGUF [('Jais-3-7B-Q4_K_M.gguf', 5.59), ('Jais-3-7B-Q5_K_M.gguf', 6.47), ('Jais-3-7B-Q8_0.gguf', 9.57)]
Jais-3-3.7B-GGUF [('Jais-3-3.7B-Q4_K_M.gguf', 3.16), ('Jais-3-3.7B-Q5_K_M.gguf', 3.64), ('Jais-3-3.7B-Q8_0.gguf', 5.39)]
Jais-3-32B-GGUF [('Jais-3-32B-Q4_K_M.gguf', 21.08), ('Jais-3-32B-Q5_K_M.gguf', 24.7), ('Jais-3-32B-Q8_0.gguf', 36.97)]
 |  | Reference models
 | Jais-3-32B | Falcon-H1-34B-Instruct | Gemma-4-31B-it | Muse-Glimmer-30B | Qwen3.8-27B | Fanar-2-27B
# Params | 32B | 34B | 31B | 30B | 27B | 27B
AraGen v3 (3C3H)09-2025 | 71.0 | 45.0 | 73.4 | 75.6 | 66.7 | 55.9
Arabic MMLU*Accuracy | 88.6 | 73.7 | 89.5 | 87.0 | 85.8 | 66.3
Dialectal Arabic MMLU*Accuracy | 88.5 | 71.5 | 89.4 | 87.0 | 87.0 | 28.2
Alyah*Accuracy | 83.0 | 71.8 | 88.4 | 80.3 | 77.7 | 36.3
FLORES200+LLM-as-a-judge | 91.5 | 70.6 | 92.8 | 84.8 | 81.8 | 71.2
Arabic IFEvalAccuracy | 80.0 | 66.8 | 78.7 | 79.5 | 77.0 | 49.8
MCPMarkAccuracy (Pass@1) | 66.1 | 0.8 | 48.8 | 44.9 | 49.6 | 12.1

[('hermes-4_3_36b-Q4_K_M.gguf', 21.8)]
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

### assistant · 2026-11-20T09:28:58.701Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\ncurl -s -m 30 https://openrouter.ai/api/v1/models -o or_models.json -w \"or-models %{http_code} %{size_download}\\n\"\npython3 -I - <<'EOF'\nimport json\nd=json.load(open('or_models.json'))['data']\nfr=[m for m in d if m['id'].endswith(':free')]\nprint('total',len(d),'free',len(fr))\nfor m in fr[:60]:\n    sp=m.get('supported_parameters',[])\n    print(m['id'],'| ctx',m.get('context_length'),'| tools' if 'tools' in sp else '| -')\nEOF\necho \"[gem fc]\"; python3 -I $S/strip.py pg_gem_openai.html | grep -iE \"function|tool|audio|transcri|embedding\" | head -5 | cut -c1-160\ncurl -sL -m 25 -A \"Mozilla/5.0\" https://console.groq.com/docs/tool-use -o pg_groq_tool.html -w \"groq-tool %{http_code}\\n\"; python3 -I $S/strip.py pg_groq_tool.html | grep -iE \"tool use|parallel|supported|gpt-oss|llama\" | head -4 | cut -c1-200\ncurl -sL -m 25 -A \"Mozilla/5.0\" https://docs.mistral.ai/getting-started/models/models_overview/ -o /dev/null -w \"mistral %{http_code}\\n\"; curl -sL -m 25 \"https://mistral.ai/pricing\" -o pg_mistral_price.html -w \"mistral-price %{http_code}\\n\"; python3 -I $S/strip.py pg_mistral_price.html | grep -iE \"experiment|free|data|training|api\" | head -6 | cut -c1-200",
 "description": "List OpenRouter free models, check tool-use docs"
}
```

### user · 2026-11-20T09:29:27.821Z

**نتيجة أداة:**
```
or-models 200 926144
total 477 free 12
inclusionai/ling-3.2-flash:free | ctx 1048576 | tools
baidu/ernie-5.5-flash-preview:free | ctx 1024000 | tools
liquid/lfm-3-1.7b:free | ctx 262144 | tools
particle-ai/particle-1:free | ctx 1048576 | tools
recursive/flint-v1.0:free | ctx 262144 | tools
nvidia/nemotron-3.5-super-vl:free | ctx 1000000 | tools
dots-studio/dots-3-note-preview:free | ctx 512000 | tools
nvidia/nemotron-3.5-lightning:free | ctx 1000000 | tools
nvidia/nemotron-3-ultra-550b-a55b:free | ctx 1000000 | tools
nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free | ctx 256000 | tools
google/gemma-4-26b-a4b-it:free | ctx 262144 | tools
google/gemma-4-31b-it:free | ctx 262144 | tools
[gem fc]
functionality, so they can't be used at the same time.
async function main() {
## Function calling  {% id="function-calling" %}
Function calling makes it easier for you to get structured data outputs from
generative models and is [supported in the Gemini API](/docs/function-calling).
groq-tool 200
Tool Use Overview - GroqDocs
Tool Use
Tool Use
Tool Use
mistral 000
mistral-price 200
Free
Start Free
$25.5 /mo in API credits.
$15 /mo in API credits.
Data export.
Free
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

### assistant · 2026-11-20T09:29:50.418Z

**أداة:** `Bash`

```json
{
 "command": "S=/private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/9a009dc5-3dda-494e-89e5-e61390c8f844/scratchpad; cd $S/r\nfor m in whisper-tiny whisper-base whisper-small whisper-large-v3-turbo; do curl -s -m 20 \"https://huggingface.co/api/models/onnx-community/$m/tree/main/onnx?recursive=true\" | python3 -I -c \"\nimport sys,json\nfs={f['path'].split('/')[-1]:round(f.get('size',0)/1e6) for f in json.load(sys.stdin)}\nprint('$m','enc_int8',fs.get('encoder_model_int8.onnx'),'enc_q4',fs.get('encoder_model_q4.onnx'),'enc_fp16',fs.get('encoder_model_fp16.onnx'),'dec_merged_int8',fs.get('decoder_model_merged_int8.onnx'),'dec_merged_q4',fs.get('decoder_model_merged_q4.onnx'))\"; done",
 "description": "Get ONNX Whisper encoder sizes"
}
```

### user · 2026-11-20T09:29:53.190Z

**نتيجة أداة:**
```
whisper-tiny enc_int8 10 enc_q4 9 enc_fp16 17 dec_merged_int8 31 dec_merged_q4 87
whisper-base enc_int8 23 enc_q4 19 enc_fp16 41 dec_merged_int8 54 dec_merged_q4 124
whisper-small enc_int8 92 enc_q4 66 enc_fp16 177 dec_merged_int8 157 dec_merged_q4 233
whisper-large-v3-turbo enc_int8 645 enc_q4 425 enc_fp16 1274 dec_merged_int8 440 dec_merged_q4 334
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

### assistant · 2026-11-20T09:30:28.028Z

**أداة:** `Bash`

```json
{
 "command": "cd /tmp 2>/dev/null; for m in Qwen/Qwen3.5-4B Qwen/Qwen3.5-27B inception42/Jais-3-3.7B inception42/Jais-3-32B google/gemma-4-26B-A4B-it; do curl -s -m 20 \"https://huggingface.co/api/models/$m\" | python3 -I -c \"\nimport sys,json\nd=json.load(sys.stdin);print('$m',[t.replace('license:','') for t in d.get('tags',[]) if t.startswith('license:')],d.get('safetensors',{}).get('total'),d.get('lastModified','')[:10])\"; done",
 "description": "Verify licences of recommended models"
}
```

### user · 2026-11-20T09:30:31.521Z

**نتيجة أداة:**
```
Qwen/Qwen3.5-4B ['apache-2.0'] 4659865088 2026-03-02
Qwen/Qwen3.5-27B ['apache-2.0'] 27781427952 2026-11-20
inception42/Jais-3-3.7B ['apache-2.0'] 5058255360 2026-11-12
inception42/Jais-3-32B ['apache-2.0'] 34779304960 2026-11-12
google/gemma-4-26B-A4B-it ['apache-2.0'] 25805936206 2026-07-20
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

### assistant · 2026-11-20T09:30:53.997Z

**أداة:** `Bash`

```json
{
 "command": "P=/private/tmp/claude-502/-Users-M7--claude-spares-spare-zoqdHX/d72c5c58-ff10-455f-b893-3cef6d2bb5f1/scratchpad; ls $P/site/tools/ 2>&1 | head; grep -nE \"argparse|add_argument|--mcp|--http|--port|usage|Access-Control|CORS|def do_(GET|POST|OPTIONS)|/tools|/call|/mcp|bearer|token|127.0.0.1|8765|ws\" $P/site/tools/tox_bridge.py | head -40 | cut -c1-200; wc -l $P/site/tools/tox_bridge.py",
 "description": "Read bridge usage and endpoints (read-only)"
}
```

### user · 2026-11-20T09:30:54.878Z

**نتيجة أداة:**
```
build_standalone.py
tox_bridge.py
8:       python3 tools/tox_bridge.py --http-only
9:       curl -H "x-tox-token: TOKEN" -d '{"tool":"say","args":{"text":"ابني فيلا 12 في 10 دورين 5 غرف"}}' http://127.0.0.1:8766/call
12:is exposed to the network. Listens on 127.0.0.1 only. A random token is printed on start (or set TOX_TOKEN);
20:TOKEN = [REDACTED]"TOX_TOKEN") or secrets.token_urlsafe(12)
30:    ("list_documents", "Document register rows (ref, type, subject, status, due).", {}),
67:        return {"error": "timeout: is the T.O X page open and connected? (Bridge pane, token above)"}
83:        self.send_header("Access-Control-Allow-Origin", "*")
84:        self.send_header("Access-Control-Allow-Headers", "content-type,x-tox-token")
85:        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
93:        t = self.headers.get("x-tox-token") or (q.get("t") or [""])[0]
96:    def do_OPTIONS(self):
99:    def do_GET(self):
104:            return self._send(401, {"error": "bad token"})
113:    def do_POST(self):
115:            return self._send(401, {"error": "bad token"})
137:        if p == "/call":
145:    srv = ThreadingHTTPServer(("127.0.0.1", PORT), H)
147:    sys.stderr.write("T.O X bridge on http://127.0.0.1:%d  token: %s\n" % (PORT, TOKEN))
180:        elif meth == "tools/call":
198:    if "--http-only" in sys.argv:
     202 /private/tmp/claude-502/-Users-M7--claude-spares-spare-zoqdHX/d72c5c58-ff10-455f-b893-3cef6d2bb5f1/scratchpad/site/tools/tox_bridge.py
```

### assistant · 2026-11-20T09:30:57.740Z

Writing the document now.

### assistant · 2026-11-20T09:33:09.496Z

**أداة:** `Write`

```json
{
 "file_path": "/private/tmp/claude-502/-Users-M7--claude-spares-spare-zoqdHX/d72c5c58-ff10-455f-b893-3cef6d2bb5f1/scratchpad/site/docs/research/AI_STACK_PLAN.md",
 "content": "# AI stack plan for T.O X: Arabic LLM, \"Jarvis\" agent, speech in/out (2026-11-20)\n\n## ملخص بالعربي (8 سطور)\n1. أحسن موديل محلي لجهاز Intel Mac فيه 8–16 جيجا: `qwen3.5:4b` (حوالي 3.3–4 جيجا، بيدعم الأدوات، رخصة Apache). لو الجهاز 16 جيجا جرّب كمان `Jais-3-7B` (GGUF من IFM، 5.6 جيجا، أقوى في العربي حسب أرقام الشركة نفسها) بس دعمه للأدوات في Ollama مش متأكد منه. للجهاز القوي: `gemma4:26b` أو `Jais-3-32B`.\n2. الجهاز الـ Intel بيشغّل Ollama على المعالج بس (CPU only، ومطلوب macOS 14+)، و LM Studio مش بيدعم Intel Mac خالص. يعني المتوقع بطيء (كام توكن في الثانية)، فخلّي قواعد الصفحة (Tier 0) تعمل أغلب الشغل والموديل للأسئلة الحرة بس.\n3. \"Hermes\" هو موديلات Nous Research (Hermes 3/4) **وكمان** وكيل جاهز اسمه Hermes Agent (رخصة MIT، بيتكلم MCP، وعنده سيرفر OpenAI-compatible على 127.0.0.1:8642، وبيشتغل من تليجرام). أرخص ربط بـ T.O X: نضيف `tox_bridge.py` كسيرفر MCP في ملف إعداداته.\n3. (تابع) \"Jarvis\": مفيش مشروع واحد بالاسم؛ البدائل المفتوحة: Open Interpreter (Apache، وكيل برمجة)، Home Assistant Assist (Apache، صوت + Wake word)، Open WebUI / LibreChat / AnythingLLM / LocalAI (واجهات وسيرفرات، أغلبها MIT وبتدعم MCP). Open WebUI رخصتها مخصصة (لازم تحافظ على الاسم والشعار).\n4. الصوت→نص: Whisper (MIT) هو الأساس. أحسن نتيجة عربي مقاسة وجدتها: Jais-ASR (Apache، حجم 11.4 جيجا bf16، مش للـ CPU الضعيف)؛ للجهاز الضعيف: whisper.cpp بموديل small (حوالي 850 ميجا رام). فيه ضبط دقيق للمصري على Hugging Face (MIT/Apache) بس أرقامه بيقيسها أصحابه بس. حتى أحسن موديل بيعمل ~47% WER على لهجات محادثة (Casablanca)، يعني اللهجة لسه صعبة.\n5. أونلاين مجاني من غير جهازك: Groq (Whisper turbo + LLM)، Gemini (فيه Transcribe و TTS مجاني ويدعم المصري)، OpenRouter (12 موديل مجاني منهم Gemma 4)، Cloudflare Workers AI (10,000 neuron/يوم). اختبرت CORS بنفسي: Groq / OpenRouter / Gemini / Mistral / Together / Cerebras / HF بيسمحوا بالنداء من صفحة static؛ Cloudflare REST و GitHub Models و NVIDIA و SambaNova لأ (محتاجين وسيط).\n6. كل الخدمات دي محتاجة API key، والمفتاح اللي في صفحة static ظاهر لأي حد يفتح DevTools. الحل: مفتاح مخصص منفصل لكل مزوّد + حدود استهلاك، أو وسيط Cloudflare Worker بيخبّي المفتاح. الخطة المجانية في Gemini بتستخدم بياناتك لتحسين منتجاتهم (مكتوب في صفحة الأسعار) — متبعتش بيانات مشروع حساسة.\n7. TTS عربي: أسهل حاجة `speechSynthesis` في المتصفح (الأصوات بتختلف حسب النظام)، وأحسن صوت مصري مجاني لقيته: Gemini TTS (يدعم Egyptian Arabic)، و Azure/Edge (ar-EG-Salma/Shakir، سحابي)، ومحلياً Piper عنده صوت أردني بس (kareem). XTTS و MMS و Habibi-TTS رخصتها non-commercial.\n8. المعمارية: Tier 0 قواعد الصفحة، Tier 1 موديل أونلاين مجاني، Tier 2 Ollama محلي، Tier 3 وكيل خارجي عبر الجسر. الـ wake word في Chrome: Web Speech API (`ar-EG`، continuous) + زر Push-to-talk دايماً؛ ومفيش \"always-on\" حقيقي لو التاب اتقفل. القسم 6 فيه أول 10 إعدادات بالقيم. وفي آخر الملف \"اللي ماقدرتش أتأكد منه\".\n\n---\n\n## 0. Method and labels\n- **VERIFIED** = read on 2026-11-20 from the cited page or API (Ollama library pages, Hugging Face API/model cards, GitHub API/README, vendor docs, PyPI JSON) or measured by me (CORS preflights).\n- **VENDOR** = number published by the model's own authors; not independently reproduced.\n- **MEMORY** = my own knowledge, not read today. Treat as a lead.\n- I downloaded no model or media. I sent no user data in any request. CORS tests were `OPTIONS` preflights with a fake origin and no key.\n- Machine assumption: owner's computer is probably an **Intel Mac** (my shell here reports `x86_64`). The macOS version is unknown; Ollama needs macOS 14+ (VERIFIED, docs/macos.mdx).\n- The model landscape moved a lot in 2025-2026 (Qwen3.5/3.6, Gemma 4, Jais 2/3, Hermes 4.x). Several names below postdate older write-ups; everything was re-read today.\n\n---\n\n## 1. Arabic-capable LLMs\n\n### 1.1 Hardware reality check (VERIFIED)\n- Ollama on Mac: \"Apple M series (CPU and GPU support) or x86 (CPU only)\", macOS Sonoma 14+.\n- LM Studio on Mac: Apple Silicon only, macOS 14+. \"Intel-based Macs are currently not supported.\" So **LM Studio is out** for an Intel Mac.\n- llama.cpp supports Intel Macs (CPU, Accelerate/AVX; MEMORY for exact speed).\n- Rule of thumb (MEMORY): RAM needed at 4-bit = Ollama download size + 1 to 2 GB for a 4-8K context; more for long context. CPU-only 7-9B at Q4 on an older Intel laptop: roughly 2-5 tokens/s (estimate, measure with `ollama run <tag> --verbose`).\n- Qwen3.5/Gemma 4 are \"thinking\" models by default: for voice, switch thinking off or the first word arrives late (MEMORY: Ollama API field `\"think\": false`).\n\n### 1.2 Model table (sizes = Ollama download at default quant, VERIFIED; \"tools\" = Ollama capability badge)\n| Model | Exact Ollama tag(s) | Size on disk (~RAM at 4-bit) | Tools | Licence | Arabic evidence |\n|---|---|---|---|---|---|\n| **Qwen3.5** | `qwen3.5:4b` 3.3-4.0 GB, `:9b` 6.6-7.6 GB, `:27b` 17-20 GB, `:35b` 22 GB, `:2b` 2.7-3.1 GB, `:0.8b` | 4b: ~5-6 GB; 9b: ~9-10 GB | yes (+vision, thinking) | Apache-2.0 (HF: 4B, 9B, 27B) | Ollama page: \"201 languages and dialects\" (VENDOR). 9B in IFM table: ArabicMMLU 80.9, Dialectal MMLU 80.4, Arabic IFEval 73.8, FLORES 74.3, MCPMark 31.5 (VENDOR, section 1.3) |\n| Qwen3 | `qwen3:4b` 2.5 GB, `:8b` 5.2 GB, `:14b` 9.3 GB, `:30b` 19 GB | 8b: ~7 GB | yes | Apache-2.0 (8B) | no Arabic number found |\n| Qwen2.5 | `qwen2.5:7b` 4.7 GB, `:14b` 9.0 GB, `:32b` 20 GB | 7b: ~6 GB | yes | Apache-2.0 (7B) | HELM Arabic (Dec 2025) lists the Qwen2.5/Qwen3 families as strong open multilingual models; best open model there: Qwen3 235B, mean 0.786 (v1.0.0) |\n| Qwen3.6 | `qwen3.6:27b` 18-19 GB, `:35b`/latest 23 GB | needs 24-32 GB | yes | not read | no Arabic number found |\n| **Gemma 4** | `gemma4:e2b` 4.6-7.5, `:e4b` 6.6-9.5, `:12b` 7.7-8.0, `:26b` 16-19, `:31b` 19-20 GB | e4b ~8-10 GB | yes (+vision, thinking; E2B/E4B take audio input) | Apache-2.0 (HF 12B/26B-A4B/31B) | IFM table: 12B ArabicMMLU 84.1, Dialectal MMLU 83.5, AraGen 62.8; 31B: 89.5 / 89.4 / 73.4 (VENDOR) |\n| Gemma 3 | `gemma3:4b` 3.4 GB, `:12b` 8.2 GB, `:27b` 17 GB | 12b ~10 GB | **no tools badge** | \"gemma\" custom terms | \"140+ languages\" (Ollama page). SILMA-9B is a Gemma-2 fine-tune (gemma licence) |\n| Llama 3.1/3.2/3.3 | `llama3.1:8b` 4.9 GB, `llama3.2:3b` 2.0 GB, `llama3.3` (70B) | 8b ~7 GB | yes | Llama community licence | AraDiCE: multilingual Llama/Mistral \"show substantial deficiency\" on dialects (search snippet, arXiv 2409.11404). Arabic is not in Llama 3.1's official language list (MEMORY) |\n| **Hermes 3** (Nous) | `hermes3:3b` 2.0 GB, `:8b` 4.7 GB, `:70b` 40 GB | 8b ~6.5 GB | yes (tuned for it) | llama3 licence (HF) | Llama-3.1 base, so Arabic is only so-so (MEMORY). No number found |\n| **Hermes 4 / 4.3** (Nous) | not in official Ollama library (community repacks only, e.g. `edtorre/qwen3.5-hermes`). HF GGUF: `NousResearch/Hermes-4.3-36B-GGUF` Q4_K_M 21.8 GB | 36B: ~26 GB | yes (agent-tuned, MEMORY) | Apache-2.0 (4-14B, 4.3-36B); Hermes-4-70B = llama3 | no Arabic number found |\n| Mistral 7B / Nemo 12B / Ministral 3 | `mistral:7b` 4.4 GB, `mistral-nemo:12b` 7.1 GB, `ministral-3:3b/8b/14b` 3.0/6.0/9.1 GB | nemo ~9 GB | yes | Apache-2.0 | Mistral 7B weak in Arabic (MEMORY); Nemo lists Arabic among its languages (MEMORY) |\n| Aya Expanse | `aya-expanse:8b` 5.1 GB, `:32b` 20 GB (8K ctx) | 8b ~7 GB | yes | **CC-BY-NC** (non-commercial) | Arabic is one of 23 languages (MEMORY) |\n| Command R7B Arabic | `command-r7b-arabic:7b` 5.1 GB (16K ctx) | ~7 GB | yes | **CC-BY-NC-4.0** (HF) | made for Arabic (Ollama page: \"excels in advanced Arabic\"); HELM did not include it |\n| **Jais 3** (MBZUAI/IFM, released 2026-11-12) | **not in Ollama library** (`/library/jais` = 404). GGUF: `IFM/Jais-3-3.7B-GGUF` Q4_K_M 3.16 GB, `IFM/Jais-3-7B-GGUF` Q4_K_M 5.59 GB, `IFM/Jais-3-32B-GGUF` Q4_K_M 21.08 GB. Run: `ollama run hf.co/IFM/Jais-3-7B-GGUF:Q4_K_M` (MEMORY that Ollama accepts `hf.co/` GGUF; the model card says \"GGUF for llama.cpp and Ollama\") | 3.7b ~5 GB; 7b ~8 GB; 32b ~25 GB | card shows tool calling via vLLM/SGLang parser `k2_horizon`; **not verified in Ollama/llama.cpp** | Apache-2.0 (3.7B, 7B, 32B cards) | best Arabic numbers in section 1.3 (VENDOR). Only 8 days old: no third-party review yet |\n| Jais 2 | `inception42/Jais-2-8B-Chat` (8.09 B params), `Jais-2-70B-Chat` | 8b: ~10 GB (no GGUF checked) | not stated | Apache-2.0 | card: \"highest scores across nearly all AraGen metrics\" vs Fanar-1-9B and ALLaM-7B (VENDOR); superseded by Jais 3 |\n| ALLaM 7B (HUMAIN) | HF `humain-ai/ALLaM-7B-Instruct-preview` (+ bartowski GGUF); no Ollama tag (`/library/allam` = 404) | ~6 GB | not stated | Apache-2.0 | July 2025 preview; Jais-3 table: ArabicMMLU 71.2, IFEval 48.0, MCPMark 0 (VENDOR) |\n| AceGPT-v2 / SILMA 9B | HF `FreedomIntelligence/AceGPT-v2-8B-Chat` (Apache-2.0), `silma-ai/SILMA-9B-Instruct-v1.0` (gemma licence) | 6-8 GB | no | see left | HELM Arabic: Arabic-specific older models (AceGPT-v2 Oct 2024) \"underperformed\" general multilingual ones |\n| gpt-oss | `gpt-oss:20b` 14 GB | ~16 GB | yes | Apache-2.0 | no Arabic number found; too big for 8-16 GB CPU |\n| Community Egyptian tunes | e.g. `mradermacher/gemma-3-egyptian-4b-v1-GGUF` (Apache-2.0) | ~4 GB | no | varies | 865 downloads; unvetted. Only worth an A/B test |\n\n### 1.3 What is known about Arabic and Egyptian quality\n**Benchmarks that exist (VERIFIED existence):**\n- Open Arabic LLM Leaderboard v2 (HF/TII, blog 2025-02): ArabicMMLU, AlGhafa, MadinahQA, AraTrust, ALRAGE, Belebele (MSA + dialects). Space still running (last modified 2025-10-09). It is log-likelihood multiple choice; a community post warns it can be gamed by distillation.\n- HELM Arabic (Stanford + Arabic.AI, 2025-12-18): 7 benchmarks. Best open model: Qwen3 235B A22B (mean 0.786). Older Arabic-specific models trailed.\n- AraGen (generative, 3C3H metric), DialectalArabicMMLU (Syrian, **Egyptian**, Emirati, Saudi, Moroccan; LREC 2026), AraDiCE (Levantine + **Egyptian**), 3LM (Egyptian/Syrian/Gulf), AL-QASIDA (Egyptian + Moroccan generation).\n- Findings in the abstracts I read: models **understand** dialect better than they **generate** it; they default to MSA; Arabic-centric models do better but still lag MSA/English. For AL-QASIDA one author needed 14 chat turns before the LLM kept the requested dialect (search snippet).\n- **I could not extract per-model Egyptian-only scores** (tables did not parse). So there is **no verified Egyptian-dialect number for Qwen, Gemma or Jais** in this document.\n\n**Only comparison I could read in full (VENDOR, from the Jais-3 model cards; authors chose the rivals and prompts):**\n| 7-9B class | Jais-3-7B | Qwen3.5-9B | Gemma-4-12B | Gemma-4-E4B | ALLaM-7B | Fanar-1-9B |\n|---|---|---|---|---|---|---|\n| ArabicMMLU | 85.2 | 80.9 | 84.1 | 77.5 | 71.2 | 65.8 |\n| Dialectal Arabic MMLU | 83.6 | 80.4 | 83.5 | 76.6 | 56.6 | 58.2 |\n| Dialect ID (QADI) | 69.0 | 35.7 | 62.1 | 59.8 | 42.8 | 46.2 |\n| AraGen v3 | 55.0 | 55.7 | 62.8 | 48.8 | 44.9 | 40.1 |\n| Arabic IFEval | 80.2 | 73.8 | 78.7 | 72.3 | 48.0 | 44.6 |\n| FLORES200+ (translation, judge) | 90.6 | 74.3 | 89.5 | 84.0 | 74.5 | 68.4 |\n| MCPMark (tool use) | 49.6 | 31.5 | 17.3 | 3.2 | 0 | 0 |\n\n| ~30B class | Jais-3-32B | Gemma-4-31B | Qwen3.8-27B | Fanar-2-27B |\n|---|---|---|---|---|\n| ArabicMMLU | 88.6 | 89.5 | 85.8 | 66.3 |\n| Dialectal Arabic MMLU | 88.5 | 89.4 | 87.0 | 28.2 |\n| AraGen v3 | 71.0 | 73.4 | 66.7 | 55.9 |\n| Arabic IFEval | 80.0 | 78.7 | 77.0 | 49.8 |\n| MCPMark | 66.1 | 48.8 | 49.6 | 12.1 |\n\nReading: Jais-3 and Gemma 4 are close at 12B/31B; Jais-3 leads at 7B on multiple choice and instruction following; Gemma-4-12B leads on open generation (AraGen). These are multiple-choice *understanding* tests, not Egyptian *conversation*. Treat as \"likely good\", then run your own 20-sentence Egyptian test (section 6, item 10).\n\n### 1.4 Recommendation\n- **Intel Mac, 8-16 GB, one model: `qwen3.5:4b`** (3.3-4.0 GB, Apache-2.0, tool calling badge, thinking switchable). Reason: only candidate that is small enough for 8 GB CPU-only, has verified tool calling in Ollama, and has an Arabic-family number (the 9B sibling) in the same table as the Arabic specialists. At 16 GB step up to `qwen3.5:9b`.\n  - **A/B candidate, not yet recommended:** `hf.co/IFM/Jais-3-3.7B-GGUF:Q4_K_M` (3.16 GB) or Jais-3-7B (5.59 GB). Arabic should be better; tool calling and the chat template in Ollama are unverified. Try it for free-text answers only; keep Qwen for tool calls.\n- **Stronger machine (Apple Silicon 32 GB+ or a GPU): `gemma4:26b`** (16-19 GB MoE with ~4B active per HF name `26B-A4B`, Apache-2.0, tools badge): fast and, for the 31B sibling, top of the table. Arabic-first alternative: Jais-3-32B Q4_K_M (21 GB), best tool-use score (MCPMark 66.1, VENDOR) but tooling in Ollama unverified.\n- Hermes models are worth using for **agent/JSON discipline**, not for Arabic.\n\n---\n\n## 2. \"Hermes\" and \"Jarvis\": open-source projects (GitHub API, VERIFIED 2026-11-20)\n\nNote: GitHub star counts below are what the API returned; two (Hermes Agent, OpenClaw) are extremely high, so treat popularity as a signal, not as proof of quality.\n\n| Project | Licence | Last push | Speaks | Cheapest way to connect to T.O X |\n|---|---|---|---|---|\n| **Hermes models** (Nous Research) | per model (above) | HF 2025-2026 | weights only | use as the local model in Ollama/llama.cpp (GGUF) |\n| **Hermes Agent** `NousResearch/hermes-agent` | MIT | 2026-11-20 | **MCP client** (stdio + remote HTTP, OAuth, `mcp_servers:` in `~/.hermes/config.yaml`); **OpenAI-compatible server** on `127.0.0.1:8642/v1` (`API_SERVER_KEY`, optional `API_SERVER_CORS_ORIGINS`); gateway to Telegram/Discord/Slack/WhatsApp/Signal/email; voice mode with wake word (\"hey hermes\"); skills + memory | **MCP:** add `tox_bridge.py` (stdio, default mode) under `mcp_servers:`; the page must be open and connected to the bridge. **API:** point the T.O X Agent panel at `http://127.0.0.1:8642/v1`. **Caveat:** its docs say local Faster-Whisper is excluded on Intel macOS; use cloud or command-based STT. Its installer pulls Python 3.14, Node, ffmpeg |\n| **Open Interpreter** `openinterpreter/openinterpreter` | Apache-2.0 (was AGPL earlier; the old `01` voice project is AGPL and last pushed 2024-11-01: dead) | 2026-11-20 | now \"a coding agent for open models\"; MCP, ACP, hooks, permissions, any OpenAI-compatible provider | MCP stdio entry for `tox_bridge.py`. Code-execution agent: keep permissions strict |\n| **Home Assistant** (Assist) | Apache-2.0 | 2026-11-20 | voice pipeline (wake word, STT, TTS via Wyoming), OpenAI/LLM conversation agents, **MCP integration** (client side, documented) | Only if the owner already runs HA. Otherwise skip |\n| **Open WebUI** | custom \"Open WebUI License\" (BSD-style **plus a branding-preservation clause**; GitHub shows NOASSERTION) | 2026-11-20 | Ollama + any OpenAI-compatible API; built to run offline; voice via external services | Add the bridge as an OpenAPI/MCP tool server (MEMORY; I could not open its MCP doc page, 404). Check the licence before any commercial use |\n| **LibreChat** `LibreChat-AI/LibreChat` | MIT | 2026-11-20 | custom OpenAI-compatible endpoints, **MCP servers**, agents, speech | MCP stdio/HTTP entry in its config |\n| **AnythingLLM** | MIT | 2026-11-20 | many providers, **MCP-compatibility**, built-in STT/TTS options | MCP server entry in its agent config; desktop app, easy on a Mac |\n| **LocalAI** | MIT | 2026-11-20 | **one server for chat, STT, TTS**, in OpenAI and Anthropic formats; **MCP client and server**; backends llama.cpp, vLLM, MLX, whisper.cpp | Best \"single local endpoint\" candidate: `/v1/chat/completions` + `/v1/audio/transcriptions` + `/v1/audio/speech`. Runs in Docker (CPU on Intel Mac; RAM overhead) |\n| **Goose** `aaif-goose/goose` | Apache-2.0 | 2026-11-20 | MCP-native extensible agent | MCP entry for the bridge |\n| **OpenClaw** | MIT | 2026-11-20 | personal assistant over messaging, \"any OS\" (README not read) | not evaluated |\n| **n8n** | fair-code (Sustainable Use; **not OSI open source**) | 2026-11-20 | workflows; MCP server/client nodes (MEMORY) | optional glue only |\n| Voice frameworks: **pipecat** (BSD-2), **LiveKit Agents** (Apache-2.0), **Moshi** (Apache-2.0, English speech-text model) | | | | overkill for a static page |\n\nThe bridge facts (READ in `site/tools/tox_bridge.py`): default mode = MCP over stdio; `--http-only` = HTTP on `127.0.0.1:8766` with `POST /call {\"tool\",\"args\"}` and header `x-tox-token`; CORS is `*` but the token is required. So any agent that can run a process (MCP) or send one HTTP POST can drive the page. No change needed for the options above.\n\n---\n\n## 3. Speech to text (Arabic, Egyptian)\n\n### 3.1 Models\n| Model | Licence | Size / runtime | Evidence |\n|---|---|---|---|\n| **OpenAI Whisper** (tiny 39M ... large-v3 1.55B, turbo 809M; sizes MEMORY except turbo, HF card) | MIT (GitHub) | whisper.cpp RAM (VERIFIED README): tiny ~273 MB, base ~388 MB, small ~852 MB (disk 75/142/466 MiB). Larger: MEMORY | No Arabic-dialect WER for base Whisper verified today. |\n| **faster-whisper** (CTranslate2) | MIT | PyPI `ctranslate2` 4.9.0 has **macOS x86_64 wheels** (VERIFIED), so it installs on Intel Macs even though Hermes Agent excludes it | speed: MEMORY, ~2-4x faster than openai-whisper on CPU |\n| **whisper.cpp** | MIT | runs on Intel Mac (README: \"Mac OS (Intel and Arm)\", AVX, Accelerate, quantisation, WebAssembly) | best fit for an Intel CPU |\n| distil-whisper | MIT | English-only distillation (MEMORY) | not useful for Arabic |\n| **Egyptian Whisper fine-tunes (HF)** | MIT / Apache-2.0 | `MAdel121/whisper-small-egyptian-arabic` (MIT, card shows test WER 22.69 on its own split), `AbdelrahmanHassan/whisper-large-v3-egyptian-arabic` (Apache, LoRA on MGB-3; card WER field 0.4739 with a template comment, so unreliable), `mohammedaly22/whisper-large-v3-turbo-egyptian-code-switching` (MIT, 809M, keeps English words in Latin), `moeshawky/faster-whisper-small-egyptian-arabic` (MIT, CT2), `nabbra/whisper-medium-egyptian-arabic-ct2` | all self-reported, tiny download counts (hundreds). Must be tested on your own audio |\n| **oddadmix dialectal Whisper** `whisper-large-v3-turbo-arabic-dialectal-v2` | Apache-2.0 | 809M | card: overall WER 0.3324 on its balanced 2.6k-clip test; **Egyptian subset WER 0.245 / CER 0.125 on 200 clips** (Saudi/Gulf 0.173; Maghrebi hardest). Self-reported |\n| **Jais-ASR** (IFM) | Apache-2.0 | 11.4 GB bf16; community GGUF and W4A16 exist; vLLM plugin with OpenAI `/v1/audio/transcriptions` | **Open Universal Arabic ASR Leaderboard (VENDOR, card table):** avg WER 22.85 / CER 8.37 over six sets: SADA 30.85, Common Voice MSA 8.56, MASC clean 16.12, MASC noisy 25.44, MGB-2 9.59, **Casablanca (8 dialects, conversational) 46.56** |\n| **Cohere Transcribe Arabic 07-2026** | Apache-2.0 (HF tag) | ~2.05 B params; official repo is gated; community GGUF `handy-computer/...-gguf` (Q4_K_M/Q8_0); runtime for those GGUFs unverified | same leaderboard: avg WER 25.87 (Common Voice 5.82 is the best of all columns) |\n| Vosk Arabic / Kaldi | Apache-2.0 (vosk-api, vosk-server) | small offline models, WebSocket server | no Arabic WER read; accuracy is generally below Whisper (MEMORY) |\n| NeMo (NVIDIA-NeMo/Speech) | Apache-2.0 | FastConformer; one Arabic SADA fine-tune on HF with 24 downloads | no usable number |\n| SeamlessM4T v2 / MMS-1B-all | **CC-BY-NC-4.0** | 1-2B | non-commercial; heavy |\n\nTake-aways: (1) even the best leaderboard model gets **~47% WER on conversational multi-dialect speech**; Egyptian-only fine-tune cards show 22-25% on their own data, which is not comparable. (2) For short **commands** (\"افتح تاب الدوكيومنت\") errors matter less because the rule layer can fuzzy-match; for dictation it matters. (3) Domain words (طلمبات، مانهول، منسوب) need an initial prompt/biasing (MEMORY: Whisper `initial_prompt`, `--prompt` in whisper.cpp).\n\n### 3.2 Serve behind an OpenAI-compatible `/v1/audio/transcriptions`\n| Server | How | Notes |\n|---|---|---|\n| **speaches** (`speaches-ai/speaches`, MIT, ex faster-whisper-server) | Docker or `uv`; OpenAI API compatible STT (faster-whisper), TTS (Kokoro, Piper), Realtime API | VERIFIED README. Intel Mac: Docker Desktop CPU path; model download on first call |\n| **whisper.cpp server** (MIT) | `whisper-server -m ggml-small.bin --host 127.0.0.1 --port 8081 --convert -l ar` ; flag `--inference-path` exists (VERIFIED README), so `--inference-path /v1/audio/transcriptions` should make OpenAI SDKs work (**untested**; default path is `/inference`, field `file`, `response_format=json`) | `--convert` needs ffmpeg (you have x86_64 ffmpeg). CORS headers: not checked, so test or put a proxy in front |\n| **LocalAI** (MIT) | STT/TTS/chat in one OpenAI-style server | heaviest, most complete |\n| Jais-ASR | vLLM plugin gives the endpoint (README) | needs a GPU-class machine |\n\n### 3.3 In the browser (transformers.js, Apache-2.0, pushed 2026-11-18)\nModels `onnx-community/whisper-{tiny,base,small,large-v3-turbo}` (ONNX files, sizes VERIFIED from HF API; totals = encoder + merged decoder):\n| Model | int8 download | q4 download | Realistic use |\n|---|---|---|---|\n| tiny | ~41 MB (10+31) | ~96 MB | wake-phrase check only; Arabic accuracy poor (MEMORY) |\n| base | ~77 MB (23+54) | ~143 MB | short commands, MEMORY: poor on dialect |\n| small | ~249 MB (92+157) | ~299 MB | usable for commands; on WASM CPU likely slower than real time on an Intel laptop (MEMORY, measure) |\n| large-v3-turbo | ~1085 MB (645+440) | ~759 MB (425+334) | needs WebGPU; Intel iGPU speed unknown |\n- WebGPU in Chrome on macOS: shipped (MEMORY); Intel iGPU performance is the unknown. Fall back to WASM (single/multi-thread needs cross-origin isolation headers for threads: MEMORY).\n- whisper.cpp also builds to WASM (`examples/whisper.wasm`, in README list). Same size/speed trade-off.\n- Cache the model in the browser (Cache API) so the first-time download happens once.\n- Verdict: in-browser Whisper = offline fallback for **short commands** (base/small). For real dictation use a server (local or Groq).\n\n---\n\n## 4. Free ONLINE options (not tied to the owner's device)\n\n**CORS column = my own `OPTIONS` preflight from a fake `https://example.github.io` origin, 2026-11-20 (VERIFIED, no key sent).** \"Direct\" means a static page can call it with `fetch`. Gemini and OpenAI echo the allowed origin (so the real page origin works).\n\n| Provider | Base URL (OpenAI-compatible) | Direct from static page? | Tools | Free-tier limits (VERIFIED unless noted) | Arabic | Privacy |\n|---|---|---|---|---|---|---|\n| **Groq** | `https://api.groq.com/openai/v1` (`/chat/completions`, `/audio/transcriptions`) | **Yes** (204, ACAO `*`) incl. STT endpoint | yes (Tool Use docs exist) | Free-plan tab: `openai/gpt-oss-20b` / `-120b` / `qwen/qwen3.8-27b`: 30 RPM, 1K RPD, 8K TPM, 200K TPD. `whisper-large-v3(-turbo)`: 20 RPM, 2K RPD, 7.2K audio-s/hour, 28.8K audio-s/day. `canopylabs/orpheus-arabic-saudi` (TTS): 10 RPM, 100 RPD, 3.6K TPD. (Rate table has a Developer-plan tab too; I read the table under the Free tab) | Whisper `language=ar`; LLM Arabic quality unmeasured | US cloud; retention policy not read |\n| **Google Gemini API** | `https://generativelanguage.googleapis.com/v1beta/openai/` | **Yes** (echoes origin) | yes (function calling documented) | Free tier exists for Gemini 3.8 / 3.6 Flash, 3.5 Flash-Lite, **3.5 Transcribe**, **3.8 Flash TTS**; \"not available\" on Gemini 4 models. Quotas per project, reset midnight Pacific; exact RPD not read | strong Arabic; TTS table lists **Egyptian Arabic** | **Free tier: \"Used to improve our products: Yes\"** (pricing table); paid: No |\n| **OpenRouter** | `https://openrouter.ai/api/v1` | **Yes** (ACAO `*`) | per model | 12 `:free` models today incl. `google/gemma-4-26b-a4b-it:free`, `google/gemma-4-31b-it:free` (both with tools, 262K ctx), several Nemotron. Free limits tier by credits bought; **exact numbers not extracted**, MEMORY: 20 RPM, 50/day below $10 purchased, 1000/day above (verify) | Gemma 4 = decent | free providers may log prompts (MEMORY) |\n| **Hugging Face Inference Providers** | `https://router.huggingface.co/v1` | **Yes** | per model | **Free users: no monthly credits; must purchase credits** (VERIFIED); PRO gets $2.00/month | per model | per provider |\n| **Mistral La Plateforme** | `https://api.mistral.ai/v1` (also `/audio/transcriptions`) | **Yes** | yes | free \"Experiment\" tier existence MEMORY (docs pages I tried returned 404/timeout; pricing page shows a Free plan with \"Start Free\") | Mistral Arabic: moderate (MEMORY) | free tier may train on data (MEMORY) |\n| **Together** | `https://api.together.xyz/v1` | **Yes** | yes | no free tier verified (MEMORY: trial credit only) | per model | |\n| **Cerebras** | `https://api.cerebras.ai/v1` | **Yes** | yes | rate-limit page fetched, numbers not extracted | per model | |\n| **Cloudflare Workers AI** | `https://api.cloudflare.com/client/v4/accounts/<id>/ai/v1` (chat, embeddings, responses only) | **No** (OPTIONS = 405). Needs a Worker proxy | yes (model-dependent) | **10,000 Neurons/day free**, then $0.011 per 1,000 Neurons; resets 00:00 UTC. Models include Gemma 4, Qwen 3.8 27B, gpt-oss, Whisper (e.g. large-v3-turbo about $0.0005 per audio minute) and MeloTTS | Whisper ok; MeloTTS Arabic not confirmed | |\n| GitHub Models, NVIDIA NIM (`integrate.api.nvidia.com`), SambaNova | | **No CORS headers** (preflight 200 without ACAO) | | not read | | proxy needed |\n| Anthropic / OpenAI | | OpenAI echoes origin; Anthropic needs its opt-in browser header | | paid only | | not free |\n\n**API keys, plainly:** every row above needs an API key (create an account first). None works key-less. A key typed into a static page is **readable by anyone who opens DevTools, by browser extensions, and by any script on the same origin**; if the page is public, never ship a key inside the file.\nOptions, cheapest first:\n1. **Bring-your-own-key**: owner pastes a *dedicated* free-tier key at runtime; store in `sessionStorage` (cleared on tab close) rather than `localStorage`; one key per provider; set the provider's spend/usage limits; rotate if exposed. (Same weakness already noted for the bridge secret in AGENT_CONTROL.md.)\n2. **Tiny proxy (Cloudflare Worker / any serverless)** holding the key as a secret, locked to the page's `Origin`, with a per-IP rate limit and a model allow-list. The key never reaches the browser. Cost: free tier (Worker free quota, MEMORY ~100K requests/day).\n3. Local model (no key at all) for private data.\n**Privacy:** do not send project drawings, client names or numbers to free tiers that train on data (Gemini free = yes, VERIFIED). Keep a \"private mode\" that forces Tier 0/2 only.\n\n---\n\n## 5. Arabic text to speech\n| Option | Egyptian? | Licence | Notes |\n|---|---|---|---|\n| **Browser `speechSynthesis`** | depends on OS/browser voices | n/a | Zero setup. Voices list loads asynchronously (`voiceschanged`, MDN). Filter `v.lang.startsWith('ar')`; try `ar-EG`, fall back to `ar-SA`. macOS ships Arabic voices (MEMORY: Maged `ar-SA`; Egyptian voice not guaranteed). Edge exposes Azure \"Online (Natural)\" voices incl. `ar-EG` (MEMORY). Quality varies; **test on the owner's machine** |\n| **Gemini TTS** (3.8 Flash TTS, Flash-Lite TTS) | **Yes**, \"Egyptian Arabic\" in supported languages table (VERIFIED) | cloud | **Free of charge on the free tier** (pricing table), CORS yes; free tier data is used to improve products |\n| **Azure Neural / Edge voices** `ar-EG-SalmaNeural`, `ar-EG-ShakirNeural` | **Yes** (`ar-EG` listed in Azure language-support page, VERIFIED; voice names MEMORY) | cloud, paid | `edge-tts` (Python, 12.6K stars, licence NOASSERTION/LGPL?, not read) calls Edge's online service **unofficially**; Microsoft removed custom SSML; ToS risk, may break. Not for a product |\n| **Piper** | Jordanian only: `ar_JO-kareem-low/medium` (VERIFIED, HF `rhasspy/piper-voices/ar`) | original `rhasspy/piper` MIT but **archived** 2025-08-26; active fork `OHF-Voice/piper1-gpl` is **GPL-3.0**; voice licences vary (check each) | CPU, fast, offline; runs behind speaches. No Egyptian voice |\n| **Kokoro-82M** | no Arabic (card lists other languages) | Apache-2.0 | fast but skip for Arabic |\n| **Coqui XTTS-v2** | Arabic supported (MEMORY), voice cloning | HF licence tag \"other\" (CPML, non-commercial, MEMORY); Coqui the company is gone (main repo last push 2024-08, fork `idiap/coqui-ai-TTS` MPL-2.0 for code) | heavy on CPU |\n| **MMS-TTS** `facebook/mms-tts-ara` | MSA-like | **CC-BY-NC-4.0** | small VITS, robotic |\n| **Habibi-TTS** `SWivid/Habibi-TTS` | multi-dialect Arabic (MEMORY: includes Egyptian) | **CC-BY-NC-SA-4.0** | non-commercial; F5-based, GPU wanted |\n| **Egyptian community TTS** `NAMAA-Space/NAMAA-Egyptian-TTS` (MIT), `MAdel121/f5-tts-egyptian-arabic` (CC-BY-NC), `ehabnegm/masri-higgs-v3-egyptian-tts` | **Egyptian**, hundreds of downloads | MIT / NC / other | promising, unvetted; model sizes and CPU speed not checked |\n| **Chatterbox Multilingual V3** (Resemble AI) | has `ar` in its language list (VERIFIED), dialect unknown | MIT | 0.5B; ONNX and GGUF ports exist; slow on Intel CPU (MEMORY) |\n| Groq `orpheus-arabic-saudi` | Saudi, not Egyptian | per Groq terms | free: 100 requests/day only |\n\nBest free Egyptian-sounding voice today = **Gemini TTS** (online). Best offline = whichever OS voice sounds acceptable; Piper `kareem` as a Levantine fallback.\n\n---\n\n## 6. Recommended architecture\n\n### 6.1 Three tiers plus an optional external agent\n```\nMic -> [wake/VAD] -> STT -> text\n                           |\n Tier 0  in-page rules (Arabic intents, tools: open tab, build house, docs)  --handled--> speak/act\n                           | not understood\n Tier 1  free online model  (Groq / Gemini / OpenRouter)   [needs key, not private]\n                           | offline / private / quota hit\n Tier 2  local Ollama       (qwen3.5:4b, OpenAI-compatible, tools)\n                           | long autonomous tasks\n Tier 3  external agent via bridge (Hermes Agent / Goose / Claude Code, MCP or HTTP POST /call)\ntext -> TTS (Gemini TTS | speechSynthesis | Piper)\n```\nRules: Tier 0 first (instant, free, offline, safe). Route to Tier 1 only for non-sensitive text; Tier 2 for private text or when offline; tool results from documents are **untrusted data** (prompt injection). Tool allow-list, confirm destructive commands, max 4 tool steps, max 400 output tokens, timeout 20 s.\n\n### 6.2 Wake word and always-listening in Chrome (what works)\n- **Truth first:** a browser tab can only listen **while it is open, the mic permission is granted, and the OS is awake**. Chrome throttles background tabs; closing the tab ends everything. For a real always-on assistant you need a small local daemon, not a web page.\n- **Design A (recommended, zero install):** Web Speech API `SpeechRecognition` with `lang='ar-EG'`, `continuous=true`, `interimResults=true`, auto-restart in `onend` (backoff 300 ms). Match wake phrases fuzzily (\"جارفس\"، \"جارفيس\"، \"يا جارفس\") on interim results. Caveats from MDN: recognition is **server-based by default on some browsers** (audio goes to the vendor), `processLocally` exists but is not universally available. Whether Chrome accepts `ar-EG` and keeps listening for hours: MEMORY, test it.\n- **Design B (private, more work):** `@ricky0123/vad-web` (Silero VAD, ONNX Runtime Web, runs locally, MIT per package; GitHub shows NOASSERTION) detects speech start/end; send each segment to STT (Tier: browser whisper-base / local whisper.cpp / Groq) and check the transcript for the wake word. Costly if STT is cloud (quota: Groq 2K requests/day), so gate by VAD and by segment length (< 3 s).\n- **Design C (daemon, truly always-on):** `openWakeWord` (Apache-2.0, Python/ONNX, has a pre-trained **\"hey jarvis\"** model, last push 2025-12-30) or Picovoice Porcupine (Apache-2.0 SDK, needs an AccessKey, MEMORY) running locally, then post text to the bridge `POST /call`. Intel Mac: onnxruntime works (MEMORY).\n- Always provide **push-to-talk** (Space or a button) and a visible mic indicator. Stop recognition while TTS speaks (`speechSynthesis.speaking`) to avoid hearing itself. Request `navigator.wakeLock` (screen) only if the owner wants the tab to stay awake (MEMORY).\n- Mixed content: an `https://` page calling `http://127.0.0.1:11434` is treated as a trustworthy origin by Chrome, but Chrome has been adding a \"local network access\" permission prompt (MEMORY, 2025-2026): expect a prompt.\n\n### 6.3 Ten things to configure first (exact settings)\n1. **Let the page call Ollama.** My preflight to `127.0.0.1:11434` answered **403** for a foreign origin, matching Ollama's origin check; docs: allowed by default only for `127.0.0.1`/`0.0.0.0`, others via `OLLAMA_ORIGINS` (VERIFIED, faq.mdx). On macOS: `launchctl setenv OLLAMA_ORIGINS \"https://YOUR-PAGE-ORIGIN,http://localhost:*\"` then quit and reopen the Ollama app. Test: `curl -i -X OPTIONS -H \"Origin: https://YOUR-PAGE-ORIGIN\" -H \"Access-Control-Request-Method: POST\" http://127.0.0.1:11434/v1/chat/completions` should return 2xx.\n2. **Pull the model:** `ollama pull qwen3.5:4b` (3.3-4.0 GB). Agent panel: base URL `http://127.0.0.1:11434/v1`, model `qwen3.5:4b`, key `ollama` (dummy), temperature 0.3, max_tokens 400, tools on, max 4 tool steps. Turn thinking off for voice (Ollama request field `\"think\": false`, MEMORY).\n3. **System prompt in Egyptian Arabic with 3-5 few-shot examples** (\"رد بالمصري، جملة قصيرة، من غير تشكيل\"), because models drift to MSA (AraDiCE/AL-QASIDA). Keep replies under ~25 words for TTS.\n4. **Tier 1 online:** Groq base `https://api.groq.com/openai/v1`, model `openai/gpt-oss-20b` (30 RPM, 1K RPD, 200K TPD) for tools; or Gemini base `https://generativelanguage.googleapis.com/v1beta/openai/`, model `gemini-3.8-flash` (free). Third choice OpenRouter `google/gemma-4-26b-a4b-it:free`. One throwaway key per provider, stored in `sessionStorage`; client-side limiter: 20 calls/min, 200/day.\n5. **Cloud STT:** `POST https://api.groq.com/openai/v1/audio/transcriptions`, multipart: `model=whisper-large-v3-turbo`, `language=ar`, `response_format=json`, `temperature=0`, `file=<MediaRecorder audio/webm;codecs=opus>` (webm accepted: MEMORY). Cap at 20 RPM / 7,200 audio-s per hour; record 8 s max per command.\n6. **Local STT (private/offline):** build whisper.cpp, then `whisper-server -m models/ggml-small.bin --host 127.0.0.1 --port 8081 --convert -l ar --inference-path /v1/audio/transcriptions` and check CORS headers with the same `OPTIONS` test (if absent, add a tiny proxy). Expected RAM ~850 MB (VERIFIED README). Add `--prompt \"هندسة مدنية، منسوب، مانهول، طلمبة، شبكة صرف\"` to bias vocabulary (flag name MEMORY).\n7. **Egyptian STT A/B:** record 20 of your own commands; compare plain `small` vs `MAdel121/whisper-small-egyptian-arabic` (MIT, convert with whisper.cpp's HF-to-ggml script, MEMORY) vs Groq turbo. Keep the winner by word error on *your* sentences. Do not trust model-card WERs.\n8. **TTS:** default `speechSynthesis`: `speechSynthesis.getVoices()` after `voiceschanged`, pick first voice with `lang==='ar-EG'`, else `ar-SA`; rate 1.0, pitch 1.0; cancel on new user speech. Upgrade path: Gemini TTS model `gemini-3.8-flash-tts` (free tier, Egyptian Arabic listed) for natural voice when online.\n9. **Wake word:** Design A above (`ar-EG`, continuous, restart on `onend`) plus a push-to-talk key as the always-available fallback; echo guard while speaking.\n10. **Connect the external agent and the safety gate:** run `python3 site/tools/tox_bridge.py` (MCP stdio) and add it as an MCP server in Hermes Agent / Goose / Open Interpreter; or `--http-only` and `curl -H \"x-tox-token: [REDACTED]" -d '{\"tool\":\"say\",\"args\":{\"text\":\"...\"}}' http://127.0.0.1:8766/call`. Set `TOX_TOKEN` yourself (not the printed random one if you script it). Hermes API server (optional): `API_SERVER_KEY=[REDACTED], `API_SERVER_CORS_ORIGINS=<page origin>`, then `hermes gateway`, base URL `http://127.0.0.1:8642/v1`. Require human confirmation for delete/overwrite commands; log every tool call.\n\n---\n\n## 7. What I could not verify\n- **Egyptian-dialect quality of any LLM:** no per-model Egyptian number extracted (DialectalArabicMMLU tables did not parse). All comparisons in 1.3 are vendor-published, multiple-choice, and from the Jais-3 cards.\n- Jais-3: released 2026-11-12; no independent review; **tool calling in Ollama/llama.cpp, chat template, and whether Ollama's `hf.co/` pull works for these GGUFs not tested**. 3.7B/32B licence read from tags/cards only for the headline models.\n- Tokens/second on your Intel Mac for every model: not measured (no model was downloaded). RAM figures = download size + rule of thumb.\n- Groq free-plan numbers: I read the table under the \"Free Plan Limits\" tab, but the page text also says limits shown are \"the base limits for the Developer plan\"; confirm in your Groq console. Gemini free RPD per model not read. OpenRouter exact free RPM/RPD not extracted. Cerebras limits not extracted. Mistral and Together free-tier terms not read (docs 404).\n- Provider data-retention/training policies (Groq, OpenRouter free providers, Mistral, Together, Cloudflare): not read. Only Gemini's free-tier \"used to improve products\" was verified.\n- CORS beyond preflight: I did not make real authenticated calls, so streaming, audio upload size limits and error-path CORS headers are untested. whisper.cpp server and speaches CORS behaviour not tested.\n- Whether `--inference-path /v1/audio/transcriptions` makes whisper.cpp fully OpenAI-compatible (field names, response shape): untested.\n- Web Speech API: `ar-EG` support, continuous-listening duration and server-vs-local processing in current Chrome: not tested. Chrome local-network-access prompt: from memory.\n- Browser Whisper speed on Intel/WebGPU: unmeasured. Whisper base-model Arabic WER: not found.\n- Jais-ASR, Cohere Transcribe Arabic: numbers are the vendors' own (Jais-ASR measured with the leaderboard script by its authors). Cohere GGUF runtime unknown; official Cohere repo is gated.\n- Egyptian TTS community models (NAMAA, f5, Higgs): not listened to, size/speed unchecked. Edge/Azure voice names `ar-EG-Salma/Shakir`: `ar-EG` verified, names from memory. `edge-tts` licence not read.\n- OpenClaw, Goose internals, Open WebUI MCP support, n8n MCP: only repo metadata/READMEs; not evaluated in depth. GitHub star counts for Hermes Agent and OpenClaw are unusually high; I did not audit them.\n- Hermes 4 base models, Llama 3.1 official language list, Mistral Nemo language list, Aya's 23 languages, Whisper parameter sizes except where noted: MEMORY.\n- Nothing here is investment, legal or personal advice. Licences summarised from tags and READMEs, not legal review: check each before shipping.\n"
}
```

### user · 2026-11-20T09:33:10.006Z

**نتيجة أداة:**
```
File created successfully at: /private/tmp/claude-502/-Users-M7--claude-spares-spare-zoqdHX/d72c5c58-ff10-455f-b893-3cef6d2bb5f1/scratchpad/site/docs/research/AI_STACK_PLAN.md (file state is current in your context — no need to Read it back)
```

### assistant · 2026-11-20T09:33:36.821Z

**أداة:** `Edit`

```json
{
 "replace_all": false,
 "file_path": "/private/tmp/claude-502/-Users-M7--claude-spares-spare-zoqdHX/d72c5c58-ff10-455f-b893-3cef6d2bb5f1/scratchpad/site/docs/research/AI_STACK_PLAN.md",
 "old_string": "3. \"Hermes\" هو موديلات Nous Research (Hermes 3/4) **وكمان** وكيل جاهز اسمه Hermes Agent (رخصة MIT، بيتكلم MCP، وعنده سيرفر OpenAI-compatible على 127.0.0.1:8642، وبيشتغل من تليجرام). أرخص ربط بـ T.O X: نضيف `tox_bridge.py` كسيرفر MCP في ملف إعداداته.\n3. (تابع) \"Jarvis\": مفيش مشروع واحد بالاسم؛ البدائل المفتوحة: Open Interpreter (Apache، وكيل برمجة)، Home Assistant Assist (Apache، صوت + Wake word)، Open WebUI / LibreChat / AnythingLLM / LocalAI (واجهات وسيرفرات، أغلبها MIT وبتدعم MCP). Open WebUI رخصتها مخصصة (لازم تحافظ على الاسم والشعار).\n4. الصوت→نص: Whisper (MIT) هو الأساس. أحسن نتيجة عربي مقاسة وجدتها: Jais-ASR (Apache، حجم 11.4 جيجا bf16، مش للـ CPU الضعيف)؛ للجهاز الضعيف: whisper.cpp بموديل small (حوالي 850 ميجا رام). فيه ضبط دقيق للمصري على Hugging Face (MIT/Apache) بس أرقامه بيقيسها أصحابه بس. حتى أحسن موديل بيعمل ~47% WER على لهجات محادثة (Casablanca)، يعني اللهجة لسه صعبة.\n5. أونلاين مجاني من غير جهازك: Groq (Whisper turbo + LLM)، Gemini (فيه Transcribe و TTS مجاني ويدعم المصري)، OpenRouter (12 موديل مجاني منهم Gemma 4)، Cloudflare Workers AI (10,000 neuron/يوم). اختبرت CORS بنفسي: Groq / OpenRouter / Gemini / Mistral / Together / Cerebras / HF بيسمحوا بالنداء من صفحة static؛ Cloudflare REST و GitHub Models و NVIDIA و SambaNova لأ (محتاجين وسيط).\n6. كل الخدمات دي محتاجة API key، والمفتاح اللي في صفحة static ظاهر لأي حد يفتح DevTools. الحل: مفتاح مخصص منفصل لكل مزوّد + حدود استهلاك، أو وسيط Cloudflare Worker بيخبّي المفتاح. الخطة المجانية في Gemini بتستخدم بياناتك لتحسين منتجاتهم (مكتوب في صفحة الأسعار) — متبعتش بيانات مشروع حساسة.\n7. TTS عربي: أسهل حاجة `speechSynthesis` في المتصفح (الأصوات بتختلف حسب النظام)، وأحسن صوت مصري مجاني لقيته: Gemini TTS (يدعم Egyptian Arabic)، و Azure/Edge (ar-EG-Salma/Shakir، سحابي)، ومحلياً Piper عنده صوت أردني بس (kareem). XTTS و MMS و Habibi-TTS رخصتها non-commercial.\n8. المعمارية: Tier 0 قواعد الصفحة، Tier 1 موديل أونلاين مجاني، Tier 2 Ollama محلي، Tier 3 وكيل خارجي عبر الجسر. الـ wake word في Chrome: Web Speech API (`ar-EG`، continuous) + زر Push-to-talk دايماً؛ ومفيش \"always-on\" حقيقي لو التاب اتقفل. القسم 6 فيه أول 10 إعدادات بالقيم. وفي آخر الملف \"اللي ماقدرتش أتأكد منه\".",
 "new_string": "3. \"Hermes\" = موديلات Nous Research **وكمان** وكيل جاهز اسمه Hermes Agent (MIT، بيتكلم MCP، وعنده سيرفر OpenAI-compatible على 127.0.0.1:8642، وبيشتغل من تليجرام): أرخص ربط إننا نضيف `tox_bridge.py` كسيرفر MCP في إعداداته. \"Jarvis\" مفيش مشروع واحد بالاسم؛ البدائل: Open Interpreter (Apache)، Home Assistant Assist (Apache)، LibreChat / AnythingLLM / LocalAI (MIT + MCP)، و Open WebUI (رخصة مخصصة بشرط الحفاظ على الاسم).\n4. الصوت→نص: Whisper (MIT) هو الأساس؛ للجهاز الضعيف whisper.cpp بموديل small (حوالي 850 ميجا رام). فيه ضبط دقيق للمصري على Hugging Face بس أرقامه بيقيسها أصحابه، وحتى أحسن موديل (Jais-ASR) بيعمل ~47% خطأ كلمات على لهجات المحادثة. اللهجة لسه صعبة، فجرّب على صوتك أنت.\n5. أونلاين مجاني: Groq (Whisper turbo + LLM)، Gemini (Transcribe و TTS مجاني ويدعم المصري)، OpenRouter (12 موديل مجاني منهم Gemma 4)، Cloudflare (10,000 neuron/يوم). اختبرت CORS بنفسي: Groq / OpenRouter / Gemini / Mistral / Together / Cerebras / HF بيسمحوا بالنداء من صفحة static؛ Cloudflare و GitHub Models و NVIDIA و SambaNova لأ. **كلهم محتاجين API key**، والمفتاح في صفحة static ظاهر لأي حد يفتح DevTools: استخدم مفتاح مخصص بحدود، أو وسيط Worker. خطة Gemini المجانية بتستخدم بياناتك لتحسين منتجاتهم.\n6. TTS عربي: `speechSynthesis` في المتصفح أسهل حاجة (الأصوات حسب النظام). أحسن صوت مصري مجاني لقيته Gemini TTS (سحابي)، و Azure ar-EG (سحابي، مدفوع). Piper المحلي عنده صوت أردني بس. XTTS و MMS و Habibi-TTS رخصتها non-commercial.\n7. المعمارية: Tier 0 قواعد الصفحة، Tier 1 موديل أونلاين مجاني، Tier 2 Ollama محلي، Tier 3 وكيل خارجي عبر الجسر. الـ wake word في Chrome: Web Speech API (`ar-EG`، continuous) + زر Push-to-talk دايماً؛ مفيش \"always-on\" حقيقي لو التاب اتقفل. القسم 6.3 فيه أول 10 إعدادات بالقيم.\n8. لقيت إن ناس كتير بتقيس العربي بأسئلة اختيار من متعدد، ومفيش رقم مؤكد للمصري لأي موديل لغوي. كل أرقام Jais-3 من الشركة نفسها، وأنا ما حمّلتش أي موديل ولا قست سرعة على جهازك. القسم 7 فيه كل اللي ماقدرتش أتأكد منه."
}
```

### assistant · 2026-11-20T09:33:38.925Z

**أداة:** `Edit`

```json
{
 "replace_all": false,
 "file_path": "/private/tmp/claude-502/-Users-M7--claude-spares-spare-zoqdHX/d72c5c58-ff10-455f-b893-3cef6d2bb5f1/scratchpad/site/docs/research/AI_STACK_PLAN.md",
 "old_string": "Upgrade path: Gemini TTS model `gemini-3.8-flash-tts` (free tier, Egyptian Arabic listed) for natural voice when online.",
 "new_string": "Upgrade path: Gemini \"3.8 Flash TTS\" (free tier, Egyptian Arabic listed; I read the model's pricing heading, not its exact API id, so look it up in the Gemini models list) for a natural voice when online."
}
```

### user · 2026-11-20T09:33:39.617Z

**نتيجة أداة:**
```
The file /private/tmp/claude-502/-Users-M7--claude-spares-spare-zoqdHX/d72c5c58-ff10-455f-b893-3cef6d2bb5f1/scratchpad/site/docs/research/AI_STACK_PLAN.md has been updated successfully. (file state is current in your context — no need to Read it back)
```

### user · 2026-11-20T09:33:40.215Z

**نتيجة أداة:**
```
The file /private/tmp/claude-502/-Users-M7--claude-spares-spare-zoqdHX/d72c5c58-ff10-455f-b893-3cef6d2bb5f1/scratchpad/site/docs/research/AI_STACK_PLAN.md has been updated successfully. (file state is current in your context — no need to Read it back)
```

### assistant · 2026-11-20T09:33:46.985Z

**أداة:** `Bash`

```json
{
 "command": "P=/private/tmp/claude-502/-Users-M7--claude-spares-spare-zoqdHX/d72c5c58-ff10-455f-b893-3cef6d2bb5f1/scratchpad/site/docs/research/AI_STACK_PLAN.md; wc -l -c $P; N=\"/Users/M7/Library/Application Support/Claude/side-session-notes/local_7b9e3c52-4743-4f64-b7c1-c942011a52a1/ai_stack_plan_handover.md\"\ncat > \"$N\" <<EOF\n# AI_STACK_PLAN hand-over (2026-11-20)\nDoc: $P\nPicks: Intel Mac 8-16GB = qwen3.5:4b (Ollama CPU-only, macOS 14+, LM Studio unsupported). Strong machine = gemma4:26b. A/B: Jais-3 GGUF (released 2026-11-12, tool calling in Ollama unverified).\nHermes Agent (MIT) = MCP client + OpenAI API on 127.0.0.1:8642; connect via tox_bridge.py stdio.\nCORS preflight tested: direct OK = Groq, OpenRouter, Gemini, Mistral, Together, Cerebras, HF router. No CORS = Cloudflare REST, GitHub Models, NVIDIA, SambaNova.\nLocal port 11434 returned 403 to foreign origin: set OLLAMA_ORIGINS.\nNo verified Egyptian-only LLM score found. See section 7 of the doc.\nEOF\nls -la \"$N\"",
 "description": "Check doc size, write hand-over note"
}
```

### user · 2026-11-20T09:33:48.498Z

**نتيجة أداة:**
```
     256   39713 /private/tmp/claude-502/-Users-M7--claude-spares-spare-zoqdHX/d72c5c58-ff10-455f-b893-3cef6d2bb5f1/scratchpad/site/docs/research/AI_STACK_PLAN.md
-rw-r--r--@ 1 M7  staff  781 Nov 20 11:33 /Users/M7/Library/Application Support/Claude/side-session-notes/local_7b9e3c52-4743-4f64-b7c1-c942011a52a1/ai_stack_plan_handover.md
```

### assistant · 2026-11-20T09:33:57.022Z

**أداة:** `mcp__ccd_turn__wrap_up`

```json
{
 "recap": "Wrote AI_STACK_PLAN.md (256 lines, Arabic 8-line summary plus English tables) covering all six areas and a \"could not verify\" section. Research only: nothing downloaded, no app source touched, no user data sent. Nothing run on the Intel Mac itself, so speeds are unmeasured."
}
```

### user · 2026-11-20T09:33:57.370Z

**نتيجة أداة:**
```
Nothing is pending, so the app draws no box; the recap is the session's status. Your closing message is your answer to the user: write it now, as the last thing you say this turn.
```

### assistant · 2026-11-20T09:34:05.396Z

I wrote `site/docs/research/AI_STACK_PLAN.md` (256 lines, Arabic 8-line summary on top, then English tables). It covers all six areas and ends with a "could not verify" section. It is research only: I downloaded no models or media, edited no app source, and sent no user data. Short pointer note: `ai_stack_plan_handover.md` in the shared notes folder.

Full path: `/private/tmp/claude-502/-Users-M7--claude-spares-spare-zoqdHX/d72c5c58-ff10-455f-b893-3cef6d2bb5f1/scratchpad/site/docs/research/AI_STACK_PLAN.md`

**Main picks**
- **Intel Mac, 8–16 GB:** `qwen3.5:4b` (3.3–4 GB, Apache-2.0, tool-calling badge on Ollama). Ollama on Intel Mac is CPU-only and needs macOS 14+. LM Studio does not support Intel Macs.
- **Stronger machine:** `gemma4:26b`. Jais-3 is the Arabic-first alternative (GGUF 3.7B, 7B and 32B; released 2026-11-12, so there are no outside reviews yet).
- **Hermes:** the models, and also a separate agent, Hermes Agent (MIT). It speaks MCP and exposes an OpenAI-compatible server on `127.0.0.1:8642`. The cheapest link to T.O X is adding `tox_bridge.py` as an MCP server in its config.
- **Free online:**
  - I tested CORS directly: Groq, OpenRouter, Gemini, Mistral, Together, Cerebras and the Hugging Face router allow calls from a static page. Cloudflare REST, GitHub Models, NVIDIA and SambaNova do not.
  - All of them need an API key, and a key in a static page is visible in DevTools.
  - Gemini's free tier uses your data to improve their products.
- **Ollama on this machine:** a call to `127.0.0.1:11434` with a foreign origin returned 403. Setting `OLLAMA_ORIGINS` fixes it (item 1 in the config list).

**What I could not verify** (full list in section 7 of the doc)
- I found no verified Egyptian-dialect score for any LLM. The Arabic comparison tables come from the Jais-3 model cards, so the authors chose the rivals and prompts.
- Tokens per second on an Intel Mac, Web Speech `ar-EG` behaviour, and tool calling for Jais-3 in Ollama are all untested.
- Some free-tier numbers (OpenRouter, Cerebras, Mistral, Together) and the privacy policies of most providers were not extracted.

Skipped as out of scope: running any model, and a deeper look at OpenClaw and n8n.
