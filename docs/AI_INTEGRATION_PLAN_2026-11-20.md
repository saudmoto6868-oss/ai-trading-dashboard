# ربط كل الذكاءات بالمنصة (Jarvis، Hermes، Ollama، ChatGPT، Claude، Grok، Gemini) — بحث وخطة (2026-11-20)

**الحالة:** بحث + جرد للموجود على الجهاز. مفيش كود اتغير. أي تنفيذ في فرع منفصل وبموافقة المالك.

## 1. الموجود فعلًا (من الجهاز والريبو)
| الأداة | الحالة | الدليل |
|---|---|---|
| **OpenClaw** (Jarvis = `main`، و`hermes`) | متثبت ومستخدم. الموديل الأساسي `claude-cli/claude-sonnet-5-5`، والاحتياطي Haiku ثم OpenAI ثم Gemini. قناة Telegram. فيه skills: `xpix-platform` (قراءة وعرض المنصة بس، ممنوع تنفيذ صفقات)، `market-analyst`، `self-improve`… | `~/.openclaw/openclaw.json` (اتقرت أسامي المفاتيح بس)، `~/.openclaw/skills/` |
| **Ollama** | متثبت، موديل `qwen3.5:4b` محلي (3.3 GB). مجاني وخاص، بس شغال على الماك بس | `ollama list` |
| **Claude على GitHub** | `@claude` في issues/PRs | `.github/workflows/claude.yml` |
| **Gemini** | Mr X / Guide (قاعدة المالك: Gemini الأساسي)، مراجعات المدارس | `modules/guide_ai.py`، `gemini-review.yml`، `school-review.yml` |
| **Grok** | digest أخبار، الـcron متقفل (قاعدة "مفيش API مدفوع") | `grok-digest.yml` |
| **ai-desk** | 13 agent بسلسلة providers: Groq ← Gemini ← OpenRouter ← DeepSeek | `desk/config.py:57-76` |
| **`ai_provider.py`** | لسه بيشاور على OpenAI اللي اتشال | تقرير المقارنة |

## 2. الخلاصة من البحث
- **MCP (Model Context Protocol) هو الطريق المشترك.** ChatGPT بيدعمه (connectors/apps)، وClaude (Desktop وCode)، وOpenClaw عنده MCP apps وautomations بتستخدم MCP servers مسموح بيها. يعني **سيرفر MCP واحد عندنا يخلّي كل الذكاءات تقرا نفس العقل** ([Wikipedia: MCP](https://en.wikipedia.org/wiki/Model_Context_Protocol)، [OpenClaw releases](https://github.com/openclaw/openclaw/releases)). Grok وOllama نفسهم ما لقيتش إنهم MCP clients، بس بيشتغلوا كموديلات **جوه** OpenClaw أو أي client بيدعم MCP.
- **بوابة موحّدة للموديلات (LiteLLM proxy، مفتوح المصدر):** API واحد بصيغة OpenAI لكل المزودين، بـfallback تلقائي، وميزانية وrate limit لكل مفتاح/موديل ([LiteLLM: budget fallbacks](https://docs.litellm.ai/docs/proxy/budget_fallbacks)، [provider budget routing](https://docs.litellm.ai/docs/proxy/provider_budget_routing)). ده بيحقق قاعدة المالك للتوكنز (سقف يومي، أصغر موديل يشتغل، fallback). **دعم Ollama وxAI في LiteLLM ما اتأكدش من البحث ده**؛ يتراجع في توثيق المزودين قبل التنفيذ.
- **Ollama** بيدّي API متوافق مع OpenAI على `localhost:11434` (معلومة عامة، تتأكد وقت التنفيذ): مناسب للشغل المتكرر الرخيص (تلخيص، تصنيف أخبار، مسودات مراجعة) **على الماك**، مش على Streamlit Cloud.

## 3. المعمارية المقترحة (4 طبقات)
1. **"عقل 6868" كسيرفر MCP (قراءة بس في الأول):** أدوات زي `query_trade_review(sql)` (SELECT بس على `trade_review.sqlite`)، `lab_card(key, tf)`، `setup_evidence(symbol)`، `meeting_room(latest)`، `open_items()`. أي ذكاء (Claude، ChatGPT، Jarvis/Hermes عبر OpenClaw، Cursor) يقرا نفس الأرقام. **الأرقام بتيجي من الأدوات بس** (قاعدة الـAuditor بتاعة المكتب).
2. **بوابة موديلات واحدة** (LiteLLM أو router صغير في `ai_provider.py`): Gemini أساسي (قاعدة المالك)، Claude للمهام الحساسة، Ollama محلي للرخيص، Grok/OpenAI/OpenRouter احتياطي. ميزانية يومية، cache لكل setup id، وتلخيص المحادثات الطويلة.
3. **GitHub/GitLab كقناة شغل غير متزامنة:** `@claude` موجود؛ نزود مراجعة PR بموديل تاني (Gemini أو ChatGPT) كرأي تاني؛ والـissues/غرفة الاجتماعات كقايمة مهام. كل agent يكتب ملاحظاته في غرفة الاجتماعات بالصيغة المتفق عليها، و"المقفّل" بيجمع.
4. **الواجهات للإنسان:** Telegram (XPiX bot وOpenClaw موجودين)، Mr X صوتي، والـWorkspace.

## 4. قواعد الأمان (من غيرها مفيش ربط)
- المفاتيح في Secrets/env بس؛ ولا مفتاح يتبعت لأداة طرف تالت أو يتحط في الكود.
- **ممنوع أي agent ينفّذ صفقة** (زي skill `xpix-platform`). كتابة الأوامر للوسيط خارج النطاق.
- MCP server قراءة بس في المرحلة الأولى؛ SQL بـSELECT بس، بحد أقصى صفوف ووقت.
- اللي راجع من موديل أو موقع = داتا مش أوامر؛ وأي رقم في رد AI لازم يكون جاي من أداة (Auditor).
- أي plugin أو MCP server من بره يتراجع (مصدر، صيانة، صلاحيات) قبل التثبيت.

## 5. خطوات التنفيذ المقترحة (كل خطوة بموافقة)
| # | الخطوة | تكلفة | محتاج من المالك |
|---|---|---|---|
| 1 | MCP server قراءة بس فوق قاعدة المراجعة والمعمل وغرفة الاجتماعات + ربطه بـClaude Code وOpenClaw | صفر (محلي) | موافقة |
| 2 | تحديث `ai_provider.py` لراوتر موحّد (Gemini ← Claude ← Ollama محلي ← احتياطي) بسقف يومي وcache | حسب الاستخدام | أي مزودين مسموحين، والسقف |
| 3 | skill لـHermes/Jarvis: "اقرا غرفة الاجتماعات، رد على اللي يخصك، سجّل ملاحظة" | صفر | موافقة |
| 4 | مراجعة PR برأي تاني (Gemini أو ChatGPT) في CI | free tier | مفتاح الموديل في Secrets |
| 5 | Ollama للمهام المتكررة على الماك (تصنيف أخبار، مسودات مراجعة يومية) | صفر | — |
