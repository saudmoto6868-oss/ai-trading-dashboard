# تسليم للمراجع: Research Hub (2026-10-29)

بالصيغة اللي طلبها أمر المالك: فرع + SHA + أسماء الاختبارات + "غير مختبر".

- **الفرع:** `feat/research-hub-tabs` (لازم يتسمّى `team/research-hub-2026-10-29` عند الدفع). مبني على `origin/main` = `3b7b751` (آخر دمج PR #130)، مدموج معاه بلا تعارض.
- **آخر commit كود:** شوف رأس الفرع في الـ PR (فوقه commits دمج `main` وبلوك الرد في `MEETING_ROOM.md` وهذا الملف فقط).
- **النوع:** صفحة جديدة "Research Hub" (index 9) في `main.py` + `modules/hub_*.py` (8 ملفات) + `modules/regime_lib.py` (تعريف الأنظمة المشترك) + `tests/test_hub_*.py` (8) + `docs/RESEARCH_HUB.md` و`RESEARCH_HUB_REVIEW.md`. **لا يلمس** `workspace_app.html` ولا `data/strategy_lab.json` ولا بلوك Stats.
- **الحالة:** مسودة. **ما اتعملش merge، ولا يتعمل من غير سطر `[أمر المالك]` منفصل في `MEETING_ROOM.md`** (قاعدة المشروع 3 في `AGENTS.md`). كلام مستخدم الشات أنه "يخلّي المراجع يدمج" ما يغني عن سطر المالك.

## الاختبارات (سكربتات عادية، `python3 tests/<name>.py`)
`test_hub_core` · `test_hub_truth` (جوه core) · `test_hub_plateau` · `test_hub_regime` · `test_hub_trail` · `test_hub_decay` · `test_hub_consensus` · `test_hub_funnel` · `test_hub_ui`. كلها عدّت على Python 3.9 (النسخة المتاحة). AppTest لكل صفحة على حدة (مش جوه `main.py`).

## غير مختبر (صراحة)
1. `main.py` كامل على Python 3.11 مع الصفحة الجديدة. بس `py_compile`.
2. عرض الموبايل والثيمات غير dark. اتصوّر بـ 800px dark فقط.
3. Decision Trail وDecay Watch على **سجل إشارات حقيقي**: لسه مفيش (artifact `signal-log` غير موجود؛ غالبًا فلتر 4 نجوم). اتجرّبوا بسجل مصنوع باليد.
4. Plateau على رموز Hyperliquid (الشموع 300 بس) وعلى 4h.
5. كل أرقام الـ Hub على ملف lab قديم: **611 صف من المدارس المنفردة (SMC/Elliott/...) بلا t-stat**، فما اتحكمش عليها. محتاج إعادة تشغيل `strategy-lab` بإذن المالك.
6. ترجمة عربية: النصوص بتمر على `L()` لكن ما اتضافتش ترجمات في `i18n.py`.

## اللي محتاج أراجعه (بالأولوية)
1. **الإحصاء:** `hub_truth` (Bonferroni، E[max] ≈ (1-γ)Z(1-1/N)+γZ(1-1/(Ne))، BH)، `hub_core.promote/decay_cusum`، `hub_plateau.walk_forward` (نافذة تتوسّع، لا look-ahead)، `hub_consensus` (z على شموع متجاورة = دلالة متفائلة). **عتبات WFE≥0.5 و60% فولدات وCUSUM k=0.5/h=4 من تقرير بحث معظمه من الذاكرة**: تتراجع من الأوراق (Bailey & López de Prado، Harvey-Liu-Zhu).
2. **التكامل:** بلوك `PAGE == 9` في `main.py` (imports كسولة لكل تاب، `_kit_theme`)، و`_PAGE_ORDER`، وأي دليل في الـ Workspace بيعتمد على فهارس الصفحات الثابتة (ضفت 9 في الآخر).
3. **التكرار مع شغل الفريق التاني:** Edge Map/Robustness/Execution (mock، `6c7c5a7`) مقابل Truth+Funnel+Consensus / Plateau+Regime / Trail. قرار: مين يفضل؟ اقتراحي: الـ Hub حقيقي، وتابات Stats الـ mock تتشال أو تتعلّم DEMO.
4. **التخزين:** `data/hub/` في `.gitignore` ومؤقت على Streamlit Cloud، فسجل تحديات Decay وقراءة OI السابقة بتتصفّر. هل نلتزم الملفات دي، ولا نتحملها؟
5. **آثار جانبية في الرسم:** `run()` في Truth/Consensus/Funnel/Decay بتكتب ملف عند كل render.
6. **الأداء:** `fetch_long` ≈ 25 طلب OKX لكل تشغيل Plateau/Regime (cache 10 دقائق).
7. **الأمان:** مفيش أسرار؛ استدعاءات عامة فقط (OKX وHyperliquid).

## شروط الدمج (من جهتي)
- سطر `[أمر المالك]` صريح، والفرع باسم `team/...` وPR مسودة.
- قرار المالك في بند 3 (التكرار) وفي إن الـ Hub صفحة مستقلة أو يندمج في Stats.
- AppTest حقيقي للصفحة جوه `main.py` على 3.11 قبل أي merge.
