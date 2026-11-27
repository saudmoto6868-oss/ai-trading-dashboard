# تسليم جلسة المراجعة → فرع الصيانة ورفع الكفاءة (2026-11-25)

> **لأي أجينت أو حساب جديد:** الملف ده + `docs/MAINTENANCE_EFFICIENCY_PLAN.md` كفاية تبدأ بيهم. **ماتعيدش فحص** اللي مكتوب هنا إنه خلص؛ كله مدموج في `main` ومقاس.
> كاتب الملف: Claude (جلسة المراجعة، فرع `ccr-5f2f29af-anpyee`). الفترة: 2026-11-20 → 11-25.
> أمر المالك: "ارفع كل التفاصيل والخطة، قارن بخطة فرع الصيانة، حط الناقص، وتوصيات لأي أجينت يخش."

---

## 0. ابدأ من هنا (توفير توكنز — 5 دقايق بدل ساعة)
1. اقرا: `CLAUDE.md` → `docs/MAINTENANCE_EFFICIENCY_PLAN.md` (§1 القواعد، §8 المهام) → الملف ده (§3 الناقص، §5 التوصيات). **مش** كل `PROJECT_STATUS.md` ولا كل `docs/MEETING_ROOM.md`: اقرا آخر قسم "صيانة ورفع الكفاءة" بس.
2. اختار مهمة "مفتوح" من §8 في الخطة أو من §3 هنا، واكتب اسمك في سجل الشغل (`docs/MEETING_ROOM.md` → "صيانة ورفع الكفاءة" → "سجل الشغل") **قبل** ما تبدأ.
3. الأوامر الجاهزة:
   ```bash
   pip install -r requirements.txt                       # streamlit 1.66.0 مثبّت بالإصدار
   for t in tests/test_*.py; do PYTHONPATH=. python3 $t; done   # PYTHONPATH=. لازم (39 اختبار من غيره بيفشل)
   ls tests/test_*.py | xargs -P6 -I{} sh -c 'PYTHONPATH=. timeout 500 python3 {} >/dev/null 2>&1 || echo "FAIL {}"'   # نفس الكلام بالتوازي
   ruff check --select F401,F841,F601,F811,F821 --exclude research,modules/xpix_barcode_gen.py .   # بقايا الكود
   python3 scripts/build_workspace.py                     # بعد أي تعديل في modules/ws/*
   ```
4. **الحالة المعروفة للاختبارات (2026-11-25):** كلها بتعدي ما عدا `tests/test_bot_spot.py` = محتاج Playwright **بايثون** (مش متسطب في الساندبوكس؛ Playwright بتاع Node متسطب وشغال). ده مش بج.
5. **الساندبوكس:** مابيوصلش لمواقع الأسعار (OKX / Hyperliquid / Yahoo). اختبر بـmocks واكتب "mock-tested only". GitHub API شغال من خلال أدوات MCP.

---

## 1. اللي خلص (مدموج في `main`) — ماتعيدوش
| # | الإجراء | الريبو / PR / SHA الدمج | الاختبار اللي بيحميه |
|---|---|---|---|
| R1 | **بج:** Prop Firms — حساب باقيله 0 يوم (مستحق النهارده) كان بيختفي من "تنتهي قريبًا ≤7ي" وبيترتب آخر واحد (`_days_left(a) or 999`). الإصلاح `_days_left_sort` | dashboard #264 / `dff12a4` | `tests/test_prop_firms_days_left.py` (بيفشل من غير الإصلاح) |
| R2 | آخر 2 `components.v1.html` → `st.iframe`: مسجّل الشاشة (`modules/screen_recorder.py`, **height 1** لأن 0 مابيرسمش iframe خالص) + بيانات Prop Firms | #264 | `tests/test_streamlit_iframe_migration.py` بقى يمسك الصيغ المستعارة (`from streamlit.components.v1 import html`، `_comp.html(`)؛ اتجرّب في Chromium حقيقي: المسجّل اتحقن في الصفحة، 0 أخطاء |
| R3 | 59 `use_container_width=True` → `width="stretch"`؛ 3 widgets في Prop Firms من غير label → labels مخفية | #264 | 0 تحذيرات deprecation في المكتب الفني (AppTest) |
| R4 | 73 import مش مستخدم، متغيرات ميتة، f-strings من غير placeholders، 36 مفتاح مكرر في `i18n.AR` (القاموس **نفسه بالظبط** قبل وبعد — اتقارن برمجيًا) | #264 | ruff نضيف وقتها. **اتحفظ:** re-export في `modules/hub_regime.py` (`adx` وغيره، الاختبارات بتستخدمه) بـ`noqa` |
| R5 | صفحة **معاينة 22** (Lab hub > Preview): كل اللي مبني ومش ظاهر في مكان واحد، للقراءة بس | #264 | `tests/test_unwired_preview_app.py` (9 أقسام × عربي/إنجليزي، وبيفشل لو الصفحة اتشالت من الـhub) |
| R6 | **بج:** تنبيهات تيليجرام — `n<30` خام جوه رسايل `parse_mode=HTML` (`day_plan.format_setup`, `format_watch`, `brain.review_text`) → تيليجرام بيرفض الرسالة كلها (HTTP 400 "Unsupported start tag 30"). بقى `n&lt;30` + `telegram_alerts.send` بيعيد الإرسال كنص عادي لو اترفض | #277 / `a7e2f30` | فحص "HTML صالح لتيليجرام" في `test_setup_alerts` / `test_day_watch` / `test_brain` + `tests/test_telegram_plain_fallback.py` |
| R7 | **M3** اختبار ميزانية الحجم: `workspace_app.html` ≤ 1,350,000 (كان 1,290,470)، كل جزء في `modules/ws` ≤ 310,000 | #278 / `a58ae29` | `tests/test_workspace_size_budget.py` (بيفشل لو زاد 70 KB — اتجرّب) |
| R8 | market-radar-bot: الحالة (`seen/state/journal.json`) على فرع **`bot-state`** بدل commit على `main` كل نص ساعة؛ دمج آمن لو تشغيلتين اتسابقوا | bot #1 / `32b0fbe` | اتأكد على GitHub: تحديثات على `bot-state`، 0 commits على `main`؛ 1163 خبر قديم اتنقلوا كلهم |
| R9 | market-radar-bot: كرون الـCloudflare Worker (كل 5 د) يشغّل workflow الرادار عند :15/:45 بـ`GH_DISPATCH_TOKEN` | bot #2 / `5c1407c` | `worker/test_worker.mjs` (mock). **مش شغال لحد ما المالك يعمل deploy** |
| R10 | xpix: الـCI مايفشلش في كل push لحد ما `services/market-engine` يترفع | xpix #15 / `ec81929` | CI أخضر |
| R11 | أمر الاختبارات في `CLAUDE.md` / `PROJECT_STATUS.md` بقى بـ`PYTHONPATH=.` | #264 | — |

**قرارات اتاخدت (عشان ماتتناقشش تاني):**
- البج اللي بيظهر من `ruff` بعد دمج `main` (imports مش مستخدمة) = بقايا من شغل تاني، مش بج؛ اتشال في #264 (آخر دفعة: `look` في `render_chart_scanner` كان بقايا ميزة "فريم لكل شارت" اللي اتشالت).
- B023 (closure جوه loop) في ruff كلها false positives: الدالة بتتنادى في نفس اللفة.
- PLE2502 (حروف اتجاه في `arabic.py` / `flow_manual.py`) مقصودة للعربي.

---

## 2. المقارنة: خطة فرع الصيانة × شغل جلسة المراجعة
| موضوع | خطة الصيانة (`MAINTENANCE_EFFICIENCY_PLAN.md`) | جلسة المراجعة | النتيجة |
|---|---|---|---|
| الهدف | السرعة والتخفيف (المتصفح، الشارت، الخلفية، تقسيم `main.py`) | الصحة والتنضيف (بجات، كود ميت، APIs قديمة، تنبيهات) | **مكمّلين لبعض، مفيش تكرار** |
| المرحلة 5 (تنضيف) | "إزالة الكود اللي مابقاش حد بيستخدمه بقائمة يوافق عليها المالك" | التنضيف الآمن **خلص** (R3، R4)، و"القائمة" = صفحة المعاينة 22 (R5) | المرحلة 5 فاضلها قرار المالك على القائمة بس |
| M3 (1.6) | مفتوح | **خلص** (R7) | ✅ |
| الحجم | القلب ≤ 400 KB (مبدئي، §7 قرار 4) | حارس على 1.35 MB دلوقتي (R7) | لما المرحلة 2 تخلص: **وطّوا** الأرقام في `test_workspace_size_budget.py` للحجم الجديد |
| الخلفية / الجدولة | §10: Oracle VM + Cloudflare Workers "بدل جدول GitHub المتأخر" | **مقاس:** جدول GitHub "كل 30 د" بيشتغل فعليًا كل **4–10 ساعات** (Telegram alerts وMarket Radar، 11-23 → 11-25) + أول Worker cron اتكتب (R9) | بيأكد §10.2 بأرقام؛ R9 هو نموذج جاهز لبند 3 في §10.2 |
| snapshots في git branch | §10.2 بيقترح "git branch خاص (زي `bot-state`)" | الطريقة **اتنفذت واتجربت** في market-radar-bot (R8): تحميل من الفرع، دمج آمن، إعادة 3 مرات | انسخوا سكربت الحفظ من `market-radar-bot/.github/workflows/market-radar.yml` (خطوة "Save bot state") لـM8 |
| التنبيهات | مش مذكورة | **كانت بايظة:** 7 من 8 تشغيلات فاشلة (R6 + سر غلط، شوف §3 P0-1) | لازم تتصلح قبل §10.3 (الأتمتة) |
| شبكة الأمان للاختبارات | القاعدة 4: parity + AppTest | **مفيش CI بيشغّل الاختبارات كلها على أي PR** (3 workflows بس على PR، كل واحد اختبار واحد) | ناقص — §3 P1-1 |
| الـrepos التانية | الداشبورد بس | market-radar-bot + xpix اتراجعوا واتصلحوا (R8–R10) | ضيفوهم في نطاق الخطة لو هتنقلوا الخلفية لـOracle |
| ملكية الملفات | §8 جدول ملكية | — | **تعارض متكرر:** آخر `docs/MEETING_ROOM.md` وأول سجل `PROJECT_STATUS.md` (كل دمج بيتعارض) → قاعدة في §5 |
| الأرقام في §2 | `tests/` = 208 ملف | 208 ملف، كلهم بيعدّوا ما عدا `test_bot_spot` (بيئة) | متطابق |

**الخلاصة:** خطة الصيانة صح وترتيبها صح (قياس → متصفح → شارت خفيف → خلفية برا → تقسيم). اللي كان ناقص فيها: **شبكة أمان آلية** (CI) قبل ما أجينتس كتير يعدّلوا بالتوازي، **إصلاح التنبيهات** قبل الأتمتة، وإن **الجدولة المتأخرة مقاسة** ولها حل جاهز.

---

## 3. الناقص (backlog مرتب) — اختار من هنا أو من §8 في الخطة
### P0 — على المالك (مفيش كود يحلها)
| # | المطلوب | ليه |
|---|---|---|
| P0-1 | **`TELEGRAM_CHAT_ID` في secrets الداشبورد = رقم شات المالك** (نفس اللي في market-radar-bot) | كل إرسال من الداشبورد بيفشل 403 "the bot can't send messages to the bot" = السر الحالي رقم بوت. اللوج بقى يقولها صريح (R6) |
| P0-2 | market-radar-bot: secrets `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID` + `GH_DISPATCH_TOKEN` (fine-grained، الريبو ده، Actions: Read and write) → Actions → **Deploy XPiX chat room** | يفعّل R9 + الأخبار كل 5 د؛ الـworkflow عمره ما اتشغل. الخطوات في `SETUP_AR.md` خطوة 5 |
| P0-3 | قرار صفحة المعاينة 22: كل عنصر يفضل / يتعدل / يتمسح | المرحلة 5 مستنياه |
| P0-4 | حساب Oracle Cloud (§10.2 في الخطة) | M8 / M9 مستنيينه |
| P0-5 | القياس 0.1 على جهازه (Chrome Task Manager، 5 د) + ساعة الجهاز (Sync now) | M0 |

### تحديث 2026-11-27 (اقرا ده الأول)
- **M10 + M11 + M13 خلصوا** على إيد حساب تاني (`5b749edf`): `.github/workflows/tests.yml` بيشغّل كل الاختبارات (`scripts/run_tests.py`) + ruff على كل PR وعلى `main`، وكل الـactions بقت v6. آخر التشغيلات خضرا. الجدول تحت **تاريخي**؛ الحالة الحقيقية في §8 في الخطة.
- **M0، M4، M5، M6 خلصوا؛ M1 وM7 شغالين** (حساب تاني). **M8 / M9 / M12 مستنيين المالك.** يعني مفيش مهمة مفتوحة من غير صاحب دلوقتي.
- `tests/test_bot_spot.py` بيعدي لما Playwright بايثون يبقى متسطب (اتجرّب: `pip install playwright==1.63.0` بنفس نسخة متصفح الساندبوكس) — الـCI بيسطّبه.
- **تنبيهات الداشبورد** اتسجلت في محضر البوتات: `docs/MEETING_BOTS_JARVIS_HERMES.md` مشكلة 8.

### P1 — لأجينت (مهام جديدة، مش في §8، مفيش تصادم مع M0–M9)
| # | المهمة | الملفات (ملكية) | ليه / إزاي |
|---|---|---|---|
| **M10** | **CI للاختبارات كلها على كل PR** | `.github/workflows/tests.yml` (جديد) | أهم واحدة: أجينتس كتير بالتوازي من غير حارس = رجوع بجات. Python 3.12، `pip install -r requirements.txt`، الحلقة المتوازية من §0 بـ`PYTHONPATH=.`، `timeout`. `test_bot_spot` يا إما `pip install playwright && playwright install chromium` يا إما يتعلّم كـ"يحتاج متصفح" في سطر واحد واضح (**مش** يتشال). قيسوا الزمن الأول |
| **M11** | حارس بقايا الكود في نفس الـCI | `.github/workflows/tests.yml` | `ruff check --select F821,F811,F601` (أخطاء حقيقية بس) يفشل الـPR؛ `F401,F841` تحذير بس. **سبب:** بعد كل دمج من `main` كان بيرجع 1–3 imports ميتة |
| **M12** | بعد P0-2: الـWorker يشغّل `telegram-alerts.yml` بتاع الداشبورد في ميعاده كمان (نفس `kickRadar`) | `market-radar-bot/worker/worker.js` + توكن على ريبو الداشبورد | تنبيهات الداشبورد "كل 30 د" بتشتغل كل 4–10 س |
| **M13** | تحديث الـactions المثبتة على Node 20 | `.github/workflows/*.yml` | تحذير "Node.js 20 is deprecated … forced to run on Node.js 24" في كل تشغيل (checkout / setup-python / cache / upload-artifact). ملكية كل الـworkflows → واحد بس يعملها، بعد M10 |

### P2 — مفيدة بعدين
- `perf_baseline.py` (M0): ابدأوا من نمط AppTest في §4 (زمن كل صفحة أوفلاين) + نمط Chromium (زمن فتح حقيقي على `streamlit run` محلي بـmocks).
- `modules/rsi_heatmap.py` وغيره: `ruff F401` بيظهر تاني بعد دمج شغل جديد — M11 يحلها من جذرها.
- الموديولات المبنية ومش متوصّلة (`tia_*` السبعة، `zone_collector`، …): ماتلمسهاش لحد P0-3.

---

## 4. أنماط جاهزة (انسخ، ماتكتبش من الأول)
**AppTest لصفحة بعينها، الشبكة مقفولة** (الأساس لاختبارات الصفحات ولـM0):
```python
import os, sys, requests
ROOT = "<repo>"; sys.path.insert(0, ROOT); os.chdir(ROOT)
def _fail(*a, **k): raise requests.exceptions.ConnectionError("blocked")
requests.get = requests.post = _fail; requests.Session.request = _fail
from streamlit.testing.v1 import AppTest
at = AppTest.from_file(ROOT + "/main.py", default_timeout=300)
at.session_state["page"] = 2; at.session_state["to_tab"] = "Control room"; at.session_state["ws_lang"] = "ar"   # صفحة جوه hub: page=<hub>, hub_<hub>=<page>
at.run(); assert not at.exception and not at.error
```
- **فخ:** AppTest مايقدرش يضغط زرار بعد ما الصفحة اتعرضت بالعربي (الـradio بـ`format_func` عربي) → اضغط الزراير بالإنجليزي بس.
- **فخ:** لو صفحة مش موصّلة، AppTest بيرجع لصفحة تانية من غير خطأ → اختبر وجود عنوان الصفحة نفسه (زي `test_unwired_preview_app.py`).

**متصفح حقيقي** (Playwright بتاع Node متسطب؛ بايثون لأ):
```bash
streamlit run main.py --server.headless true --server.port 8598 &   # ثم:
NODE_PATH=$(npm root -g) node check.js   # chromium.launch() → page.goto('http://localhost:8598/?page=2') → pageerror + innerText
```
- `st.iframe(height=0)` **مابيرسمش** iframe؛ استخدم `height=1` جوه container مخفي. الـiframe بتاع `st.iframe` بيقدر يوصل `window.parent` (same-origin، اتجرّب).

**إثبات إن الاختبار بيمسك البج:** شغّله على الكود قبل الإصلاح (يفشل) وبعده (ينجح). مثال: `git stash` → شغّل → `git stash pop`. **ماتستخدمش `git checkout <file>` على ملف فيه تعديل مش متسجّل.**

---

## 5. توصيات لأي أجينت يخش
1. **اكتب اسمك على المهمة قبل ما تبدأ** (سجل الشغل). ملف واحد = صاحب واحد (§8 في الخطة).
2. **ماتعيدش اكتشاف الريبو.** الملف ده + الخطة + `CLAUDE.md` كفاية. استخدم `rg -n` و`sed -n` على مدى محدد؛ ماتطبعش ملفات كبيرة (`workspace_app.html` 1.3 MB بسطور طويلة).
3. **فرع لكل مهمة** `maint/<اسم>`، PR صغير، اختبار بيفشل قبل وبينجح بعد، قياس قبل/بعد لأي ادعاء سرعة.
4. **قبل الدمج:** `git fetch origin main && git merge origin/main` ثم الاختبارات كلها (الحلقة المتوازية). `main` بيتحرك بسرعة (PR #264 اتعارض 5 مرات في يومين) — اتوقع تعارض.
5. **منع التعارض في الملفات المشتركة:** في `PROJECT_STATUS.md` (السجل) وفي `docs/MEETING_ROOM.md`: ضيف سطرك **تحت أحدث 3 بنود**، مش أول سطر تحت العنوان ولا آخر سطر في الملف. السطر اللازق في العنوان بيتعارض في كل دمج.
6. **`ruff` بعد كل merge من `main`**: الـF401/F841 الجديدة غالبًا بقايا من شغل غيرك؛ اتأكد إنها مش re-export (دوّر على `alias.name` مش بس `from x import name`) قبل ما تشيلها.
7. **تيليجرام HTML:** أي `<` في النص لازم `&lt;` (و`&` → `&amp;`). استخدم `esc()` الموجودة.
8. **الأمانة:** "mock-tested only" لأي حاجة شبكة؛ "مش دليل" تحت n=30؛ ماتخترعش أسعار. اكتب "ماتجربش" (السيرفر المنشور، جهاز المالك، بيانات حية).
9. **الدمج في `main`:** بعد موافقة المالك (أو تفويض صريح منه)، مش من تعليق على GitHub.
10. **تقرير النهاية لكل مهمة:** الفرع، PR، SHA الدمج، قبل → بعد، الاختبارات اللي اتشغلت فعلًا، اللي ماتجربش — في سجل الشغل.
