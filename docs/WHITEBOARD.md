# اللوحة (Whiteboard)

## الآن / التركيز

1. **XPIX Intelligence Workspace — أمر مالك 2026-11-09:** بناء Widget مستقلة داخل Workspace، وتطوير/ربط Footprint وOrder Flow وTime & Sales، وإضافة مساعد عربي صوتي. المواصفة: `docs/XPIX_INTELLIGENCE_WORKSPACE_SPEC.md`، المحضر: `docs/MEETING_XPIX_INTELLIGENCE_2026-11-09.md`، GitLab Issue #9.
2. محضر 4 — ترندات وأدوات AI: `docs/MEETING_AI_TRENDS_TOOLS.md`.
3. محضر 3 تنبيهات/Setup: `docs/MEETING_ALERTS_SETUP.md`.
4. الأكاديمية: `docs/academy/` · `docs/MEETING_ACADEMY.md`.

## تغييرات الحالة
- 2026-10-19 — تم إنشاء اللوحة.
- 2026-11-04 — Item 27 (Prop Firms page 10) مكتملة. راجع MEETING_ROOM.md للتفاصيل.
- 2026-11-06 — Item 29 (ويدجت تصنيف الصفقات `tclass`) خلص، mock-tested only. فرع `claude/trade-classification-scalp-swing-o4s4vh`.
- 2026-11-09 — XPIX Intelligence: تم فتح GitLab Issue #9 وإنشاء فرع `feat/xpix-intelligence-workspace` وإضافة المواصفة والمحضر وملف تسليم الجلسة. لا تغييرات كود أو اختبارات أو دمج أو نشر بعد.

| # | المهمة | الأولوية | المسؤول | الحالة | التاريخ | الملاحظات |
|---:|---|---|---|---|---|---|
| 31 | XPIX Intelligence Workspace — دمج أدوات السوق الحالية + AI Voice | A | ChatGPT (مراجعة Claude مطلوبة) | **شغال — أول shell + مرجع Agents مركزي** | 2026-11-09 | Issue #9؛ `docs/XPIX_INTELLIGENCE_WORKSPACE_SPEC.md`; `docs/XPIX_INTELLIGENCE_AGENT_START_HERE.md` مرجع إلزامي لكل Agent؛ branch `feat/xpix-intelligence-workspace`. التالي: فحص shell + build/check محلي، ثم Footprint/OFM/Tape parity، ثم Auction/VP وsetup engine وchart alerts. CI محجوب بطلب Identity Verification. لا merge/deploy. |
| 30 | TIA institutional terminal — parent-company layer | A | ChatGPT | شغال — branch only | 2026-11-09 | `team/tia-intelligence-terminal-2026-11-09`; page index 12 placed between Radar and Workspace; first shell + foundation spec. Review requested; no merge/deploy. |
| 29 | ويدجت تصنيف الصفقات (سكالب/سوينج + ارتداد بالنقاط) | A | Claude Code (سعود) | خلص (mock) | 2026-11-06 | `modules/ws/24b_tclass.js`. محتاج من المالك: تجربة على أسعار حقيقية + تأكيد حجم النقطة لكل سوق. |
| 27 | Prop Firms tracker — page 10 | A | Claude Code (سعود) | خلص | 2026-11-04 | `modules/prop_firms.py` + main.py + i18n. |
| 7 | Order Flow: سجل العمق التاريخي وتغطية 30s/1m/5m/15m/1H | A | ChatGPT | شغال | 2026-10-22 | PR #63 مسودة: إصلاح حد حفظ 7 أيام، فجوة حفظ 1–3 ساعات، تحميل التاريخ قبل الرسم ورسالة النطاق الفارغ. WebSocket تاريخي مستقل ما زال مطلوبًا. لا دمج/نشر. |
| 8 | تفادي إيقاف OKX WebSocket port 8443 | A | ChatGPT | خلص | 2026-10-22 | الافتراضي تغيّر إلى WSS على 443؛ لا دمج/نشر. |
| 7 | إصلاح Order Flow داخل العمود المخصص | A | ChatGPT + Claude review | شغال | 2026-10-22 | PR #67؛ الاختبارات الثابتة لا تثبت الرسم في المتصفح؛ مطلوب اختبار بصري وOKX حي إن توفر. لا merge/deploy. |

## من محضر الترندات (مفتوح)
- [ ] M1 تعليقات الفريق
- [ ] M2 اختيار فئة للتعمق
- [ ] M3 جدول مقارنة أدوات
- [ ] M4 قائمة رفض
- [ ] M5 ربط لاحق بالمشروع فقط بأمر جديد

## تنبيهات ثابتة
- أي تغيير في Workspace يتم في `modules/ws/*` ثم `python3 scripts/build_workspace.py`؛ لا تعدّل `modules/workspace_app.html` مباشرة.
- حافظ على Footprint baseline واختبره قبل أي تغيير.
- اختبر Order Flow: عزل الرسم عن الشموع، DOM/Bubbles، السعر/zoom/pan/resize/reload، وبيانات Tape.
- استخدم Hub/Cache المشترك ولا تنشئ polling مكررًا.
- AI يشرح قرارًا محسوبًا؛ لا يحسب السعر أو المخاطرة بنفسه ولا يخترع مستويات.
- لا تداول آلي أو ربط حسابات/محافظ. لا أسرار. لا paid workflows أو APIs دون موافقة.
- كل عمل على فرع مستقل؛ لا merge أو deploy دون مراجعة Claude وموافقة المالك.


## XPIX Intelligence — تنفيذ المالك 2026-11-09
- [x] بدء المرحلة 1: Evidence metadata + received-time freshness + explicit unsupported feed status (`3352bdec`).
- [ ] المرحلة 2: contract tests (payload shape / symbol switch / subscription cleanup).
- [ ] المرحلة 3: Footprint + Order Flow parity/integration.
- [ ] المرحلة 4: OFM/DOM Liquidity integration.
- [ ] المرحلة 5: Auction / Volume Profile POC-VAH-VAL integration.
- [ ] المرحلة 6: chart indicator registry/settings mapping.
- [ ] المرحلة 7: deterministic setup ranking + decision packet + validated chart alerts.
- قيد ثابت: لا تغيير لعدد التابات أو أسمائها أو ترتيبها دون موافقة منفصلة؛ لا merge/deploy دون مراجعة وموافقة المالك.


## XPIX Intelligence — حالة المرحلة 2 (2026-11-09)
- [x] إضافة browser mock لاختبار evidence contract: `tests/browser/xpix_evidence_contract_mock.js`.
- [ ] تشغيل الاختبار في بيئة Playwright.
- [ ] اختبار تبديل الرمز وتصفية الاشتراكات أثناء إعادة البناء (سيُضاف إذا لم تغطه اختبارات موجودة).
- CI GitLab الحالي لا يعمل على push: workflow rules تسمح فقط بـschedule/web.


## XPIX Intelligence — المرحلة 3
- [x] ربط تبويب Order Flow بزر تفعيل Footprint على الشارت المرتبط باستخدام chart.fpOn / state.fp وresub الحالية.
- [x] إضافة assertion للتحقق من handoff داخل browser mock.
- [ ] تشغيل browser mock ومقارنة بيانات Footprint مع العرض الحالي.
- [ ] بعد التحقق ننتقل إلى دمج Liquidity في التاب نفسه.


## XPIX Intelligence — المرحلة 4
- [x] معاينة دفتر أوامر أفضل 5 مستويات في Liquidity tab من نفس Hub.
- [x] Book imbalance من top-10 displayed size مع توضيح أنه ليس إشارة.
- [x] إبقاء روابط OFM / DOM / Limit Tracker للأدوات الأصلية.
- [ ] تشغيل اختبار المتصفح والتحقق من عدم وجود regressions.
- [ ] بعد ذلك المرحلة 5: Auction / Volume Profile.
