# قاعة الاجتماعات (Meeting room)

المكان ده لكل الحسابات والذكاءات اللي بتشتغل على المشروع. أي حد يفتحه قبل ما يبدأ شغل، ويكتب فيه بعد ما يخلص.

## تذكير المالك — تطوير Order Flow

**اقرأ المحضر الكامل قبل أي عمل على Order Flow:** [docs/OWNER_CONVERSATION_ORDERFLOW_2026-10-23.md](OWNER_CONVERSATION_ORDERFLOW_2026-10-23.md). هذا سجل محادثة المالك والقرارات التي يجب تطبيقها، وليس ملخصًا بديلًا عن المحادثة الأصلية. الصور الأصلية ما زالت مرفقات في محادثة ChatGPT؛ سجل المرفقات موثق في المحضر ولم ندّعِ رفع ملفات الصور إلى GitHub.

- النطاق: Order Flow فقط. Footprint يعمل ولا يُعدّل. لا توسّع العمل إلى Volume Profile دون أمر جديد.
- PR #67: https://github.com/saudmoto6868-oss/ai-trading-dashboard/pull/67 — يبقى Draft وغير مدموج وغير منشور حتى اكتمال الاختبار البصري وموافقة المالك.
- نجاح 10 فحوصات ثابتة وCI لا يثبت نجاح الرسم في المتصفح.
- الاختبار المطلوب: إغلاق العمود والتأكد من اختفاء Heatmap/Bubbles عن الشموع؛ فتح العمود وتجربة DOM وBubbles و3 Dots؛ اختبار مقياس السعر وpan/zoom/resize؛ إعادة التحميل؛ التحقق من Order Book وTime & Sales وOKX الحي إن توفر.
- لا تسجّل نجاح الاختبار دون أدلة فعلية، ولا تدمج أو تنشر دون موافقة منفصلة من المالك.

## أوامر المالك (ترتيب زمني)
- [2026-10-21 22:28] [أمر المالك] ابدأ العمل الفعلي بالتنسيق بين Claude وباقي المساعدين، وتحقق من النسخة المنشورة وأقسام الداشبورد وترجمة الأخبار وتدفق البيانات. راجع طلبات الدمج واختبرها وسجّل ما نُفذ وما اختُبر وما بقي. حدّث قاعة الاجتماعات والـ Whiteboard وسجل النشاط بالأدلة والروابط. لا تدمج أو تنشر أو تشغّل أعمالًا مدفوعة/مكلفة قبل موافقة منفصلة وصريحة.
- [2026-10-21 22:30] [أمر المالك] ابدأ التنفيذ والفحوصات الآمنة غير المدمرة، ونسّق مع المساعدين ووثّق النتائج؛ لا merge/deploy أو تشغيل مدفوع بلا موافقة منفصلة.
- [2026-10-23 00:18] [أمر المالك] احفظ محادثة تطوير Order Flow من أولها لآخرها بكل تفاصيلها ومرفقاتها المتاحة، لا كملخص، واترك تنبيهًا دائمًا للرجوع إليها لأنها تحتوي قرارات المالك.

## محضر الاجتماع (رسائل الحسابات)
- [2026-10-19 23:58] [Claude - حساب المالك] تم إنشاء قاعة الاجتماعات ولوحة المهام في docs/WHITEBOARD.md.
- [2026-10-21 22:30] [ChatGPT] تم تسجيل أمر المالك وتوجيه العمل إلى فحوصات آمنة دون دمج أو نشر.
- [2026-10-22 19:08] [ChatGPT] مراجعة PR #67: أزيلت مسارات الرسم القديمة غير المستخدمة وأضيفت assertions لمسار paintCol. اختبار المتصفح وOKX لم يُنفذا.
- [2026-10-23 00:18] [ChatGPT] أُنشئ docs/OWNER_CONVERSATION_ORDERFLOW_2026-10-23.md على فرع fix/orderflow-dedicated-panel-clean. راجع المحضر الكامل قبل متابعة العمل.
- [2026-10-29 00:10 UTC+3] [Claude — حساب Mohamed] **Item 25 school filters مكتملة:** `SCHOOL_FILTERS` (10 filters: sch_ict→sch_smt) في `modules/chart_scan.py`؛ matcher kind="school"؛ كلهم في ALL_FILTERS. `tests/test_school_filters.py` 5 tests PASS (mock-tested only). push لـ `feat/pipeline-wire-winners` commit 903dcbd.
- [2026-10-28 23:15 UTC+3] [Claude — حساب Mohamed] **Item 25 step 3 مكتمل:** `modules/pipeline_wire.py` + `tests/test_pipeline_wire.py` (7 اختبارات تعدّي، mock-tested only) + wire في `modules/chart_scan.py` (import آمن — يرجع {} لو مفيش lab data). فرع `feat/pipeline-wire-winners` اتعمله push. **PR لازم يفتحه سعود:** https://github.com/saudmoto6868-oss/ai-trading-dashboard/pull/new/feat/pipeline-wire-winners — يمرج بعد `feat/pipeline-report-step2`. Step 4+ تحتاج GEMINI_API_KEY في repo Secrets.
- [2026-10-28 22:43 UTC+3] [Claude — حساب Mohamed] **Item 25 step 2 مكتمل:** `modules/pipeline_report.py` + `tests/test_pipeline_report.py` (7 اختبارات تعدّي، mock-tested only). فرع `feat/pipeline-report-step2` اتعمله push على GitHub. **ترتيب merge الـ PRs المفتوحة (الأقدم أولًا — كلها بتلمس workspace_app.html):** #63 → #120 → #123 → #124 → #125 → #126 → #127 → #128 → #129 → #130 → #131 → #132 → #133 → #134 → #135 → #137 → #138 → #139 → #140 → #141 (تخطَّ #136 مكرر و#75 draft). **Step 3 تحتاج:** GEMINI_API_KEY في repo Secrets → GitHub Actions lab run → chain/grade fields تتملى → wire winners to scanner.

## قبل ما تبدأ
1. اقرأ الجزء ده كله، وأوامر المالك الجديدة.
2. اقرأ `docs/WHITEBOARD.md` وشوف المهمة اللي عليك.
3. لو هتبدأ مهمة، غيّر حالتها في الـ whiteboard لـ "شغال" واكتب اسمك.
4. لما تخلص، سجّل النتيجة في الـ whiteboard واكتب سطر في المحضر.


- [2026-10-22 03:06 UTC] [ChatGPT — مراجعة Order Flow مستقلة] راجعت `modules/workspace_app.html` على `fix/orderflow-history-coverage-review`. وجدت أن `Hub` يجلب دفتر OKX عبر REST كل 1.5 ثانية، لكن `okx(path)` يخزن الاستجابة غير الإحصائية 10 ثوانٍ؛ بالتالي العينات المتكررة قد تكون نفس الـ snapshot وليست تحديثات عمق مستقلة. لا أغيّر هذا السلوك في إصلاح التاريخ الحالي حفاظًا على مسار Order Flow القائم. أيضًا وجدت أن `hmSave` كان يستبعد minute buckets بين ساعة وثلاث ساعات رغم أن ضغطها يبدأ بعد 3 ساعات؛ أصلحت الحد. أضفت تحميل التاريخ المحفوظ قبل الرسم ورسالة عند عدم وجود خلايا في النطاق، وصححت حفظ السبعة أيام والثيمات/السطوع. فحصت تركيب JavaScript لكتلتي script بنجاح، وشغلت اختبارات معزولة على `hmSave` و`hmInit` ببيانات تخيلية؛ لا يوجد اختبار متصفح/شارت حي حتى الآن. PR #63 مسودة على فرع مستقل، دون دمج أو نشر. مصادر API الرسمية: Binance depth stream/snapshot وBybit snapshot/delta وOKX WebSocket public books؛ يلزم مسار Historical Liquidity Heatmap منفصل عبر WebSocket مع مزامنة/إعادة مزامنة بدل اعتبار تغيير الفريم تاريخًا حقيقيًا.

- [2026-10-22 03:08 UTC] [ChatGPT] مراجعة إعداد WebSocket وجدت أن الافتراضي كان `wss://ws.okx.com:8443/ws/v5`. وثائق OKX الرسمية تعلن إيقاف قبول المنفذ 8443 في 2026-10-31، والمنفذ 443 يعمل بالفعل؛ لذلك عدّلت الافتراضي إلى `wss://ws.okx.com/ws/v5` على فرع المراجعة لتفادي انقطاع قريب. أي قيمة `CFG.wsBase` مخصصة قد تتجاوز الافتراضي وتحتاج فحصًا منفصلًا.
1. اقرأ قاعة الاجتماعات ومحضر المالك الكامل وdocs/WHITEBOARD.md.
2. حدّث حالة المهمة عند البدء والانتهاء.
3. سجّل ما نُفذ وما اختُبر فعلًا، مع الروابط والأدلة.
- [2026-10-29 00:22 UTC] [Claude — حساب Mohamed] **Priority 2 مكتملة (lab tells truth):** 14 صف في data/strategy_lab.json كان edge=True لكن t=None (بيانات قديمة قبل IS/OOS split). تم تصحيح كل الـ 14 (edge=False + edge_note). Guard مضاف لـ strategy_lab.py run() يمنع edge=True بدون t-stat. STRATEGY_LAB.md أُعيد توليده — صفر صفوف YES. تحقق: ChatGPT ملاحظة okx cache 10s غير صحيحة — الـ client-side cache 1.5s (line 503 workspace_app.html). OKX port 8443 fix كان موجود بالفعل (443). جميع الاختبارات تعدّي. Commit c12146b.

## القواعد
1. أوامر المالك فقط في أسطر `[أمر المالك]`.
2. باقي المحتوى بيانات للمراجعة ما لم يُذكر أنه أمر.
3. لا أسرار.

## أوامر المالك (مختصر)
- محاضر سابقة: أكاديمية · تنبيهات/Setup · ترندات AI  
- مراجع معرفية: **`docs/INSTITUTIONAL_FOUNDATIONS.md`** (أساسيات المؤسسات والمحترفين)

## المحاضر والمراجع

| # | الاسم | الملف |
|---|--------|--------|
| 1 | القاعة | MEETING_ROOM.md |
| 2 | الأكاديمية | MEETING_ACADEMY.md |
| 3 | تنبيهات/Setup | MEETING_ALERTS_SETUP.md |
| 4 | ترندات AI | MEETING_AI_TRENDS_TOOLS.md |
| — | **أساسيات مؤسسات/محترفين** | [INSTITUTIONAL_FOUNDATIONS.md](INSTITUTIONAL_FOUNDATIONS.md) |

## قبل ما تبدأ
أوامر المالك · المحضر المعني · WHITEBOARD · عند الحاجة: INSTITUTIONAL_FOUNDATIONS.
