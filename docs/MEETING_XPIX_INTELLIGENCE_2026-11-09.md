# محضر تطوير XPIX Intelligence — 2026-11-09

## [أمر المالك] نطاق التطوير
المالك طلب تطوير أدوات الـWorkspace الموجودة (Footprint وOrder Flow وTime & Sales وما يرتبط بها) وإنشاء Widget جديدة مستقلة تجمع الأدوات والمخرجات والمدخلات والمؤشرات، مع مساعد ذكي يشرح بالعربية ويقدم شرحًا صوتيًا عند ظهور فرصة أو تغير مهم في حالة الصفقة.

## الاسم المعتمد مبدئيًا
- اسم العرض: **XPIX Intelligence**
- اسم اللوحة الداخلي: `intel`
- الوصف: مركز تحليل وقرار متعدد الأسواق يجمع الأدوات الحالية، ويقدم Trade Plan مفسرًا ومساعدًا صوتيًا عربيًا.
- لا يُستبدل أي Panel حالي؛ تبقى الأدوات الأصلية قابلة للاستخدام منفردة.

## تدقيق المستودع بتاريخ 2026-11-09
- المشروع: `6868-group/ai-trading-dashboard`.
- الفرع الأساسي: `main`.
- فرع العمل: `feat/xpix-intelligence-workspace`.
- ملف Workspace المولد: `modules/workspace_app.html`.
- مصدره: `modules/ws/*`، ويجب تشغيل `python3 scripts/build_workspace.py` بعد أي تعديل على الأجزاء.
- الأجزاء ذات الصلة: `13_okx_levels_regime_footprint.js`, `22_ofmap.js`, `22_panels.js`, `23_orderflow.js`, `24_flow_confluence_misc.js`, `25_guide.js`.
- توجد بالفعل Footprint وOrder Flow Heatmap وDOM وTime & Sales/Tape وLimit Tracking وVolume Profile وFlow Confluence وSetup Card وSignals/Alerts وGuide.
- `modules/guide_ai.py` يدعم مسار نصي OpenAI عند تهيئته، كما يدعم Gemini؛ مسار الصوت الحي الحالي Gemini Live في `modules/guide_bridge/`. المطلوب دراسة إعادة استخدام Guide الحالي وتوسيع قدراته، لا إنشاء مساعد مكرر.
- يوجد بالفعل اختبار Order Flow بصري: عند إغلاق العمود يجب اختفاء Heatmap/Bubbles من فوق الشموع، مع اختبار DOM/Bubbles/3 dots ومقياس السعر وpan/zoom/resize/reload وبيانات Order Book وTime & Sales.
- سلوك Footprint الحالي خط أساس محمي؛ يجب تسجيل parity قبل تغيير الحساب أو العرض.

## مواصفات الWidget
التبويبات: Overview، Footprint Lab، Order Flow، Liquidity Map، Time & Sales، DOM Analytics، Auction & Volume، Options/GEX، Setups، Trade Plan، Risk & Execution، AI Voice.

المخرجات:
- سياق السوق والاتجاه والنظام الحالي.
- حالة البيانات ومصدرها وتوقيتها وجودتها.
- Setup status: WATCH / WAIT / READY / INVALID / NO TRADE.
- منطقة الدخول، شرط التفعيل، الإبطال، الستوب، الأهداف، حجم المركز والمخاطرة.
- الأدلة المؤيدة، التعارضات، أسباب رفض الصفقة.
- شرح عربي مصري نصي وصوتي، قابل للكتم والإيقاف والمقاطعة، مع منع التكرار عند كل Tick.

## الحوكمة
- تحليل ومساعدة وPaper-first فقط.
- لا ربط بحساب تداول أو محفظة أو مفاتيح وسيط، ولا إرسال أوامر تداول أو تنفيذ آلي.
- الحسابات السعرية والمخاطر وحالة الصفقة من محركات حتمية، والـLLM يشرح فقط.
- Verifier مستقل يمنع التوصية إذا البيانات قديمة أو بها فجوة تسلسل أو الرمز/السوق غير مطابق أو الحسابات ناقصة.
- لا ادعاء ربح أو احتمالية فوز دون اختبارات خارج العينة وبعد تكاليف التداول.
- لا شراء API ولا تشغيل Workflows مدفوعة ولا دمج أو نشر دون موافقة منفصلة.

## خطة التنفيذ
1. Audit للـPanels والـHub والـFeeds والـstate والـstorage والـGuide والاختبارات، مع تسجيل خط أساس.
2. بناء Shell للـWidget `intel` من أجزاء Workspace المصدرية.
3. ربط الأدوات الموجودة بمخرجات الـHub/Cache المشتركة دون polling مكرر.
4. بناء Decision Packet وVerifier حتمي.
5. توسيع Guide الحالي للشرح العربي والصوت، مع تقييم OpenAI voice كخيار دون كسر Gemini Live.
6. Replay / Backtest / Walk-forward / OOS مع Spread وFees وSlippage.
7. موصلات منفصلة حسب السوق والبورصة ومصدر البيانات.

## الحالة
- تم إنشاء فرع منفصل.
- تم إنشاء المواصفة في `docs/XPIX_INTELLIGENCE_WORKSPACE_SPEC.md`.
- تم فتح GitLab Issue #9.
- لم يتم تعديل كود Workspace حتى الآن.
- لم تُشغّل اختبارات أو Workflows.
- لا يوجد Merge أو Deploy.
