# اللوحة (Whiteboard)

## الآن / التركيز

1. **محضر 4 — ترندات وأدوات AI:** `docs/MEETING_AI_TRENDS_TOOLS.md` (أمر مالك — ابدأوا الشغل)  
2. محضر 3 تنبيهات/Setup: `docs/MEETING_ALERTS_SETUP.md`  
3. أكاديمية: `docs/academy/` · `docs/MEETING_ACADEMY.md`

## تغييرات الحالة
- 2026-10-19 — تم إنشاء اللوحة.
- 2026-11-04 — Item 27 (Prop Firms page 10) مكتملة. راجع MEETING_ROOM.md للتفاصيل.
- 2026-11-06 — Item 28 (ويدجت تصنيف الصفقات `tclass`) خلص، mock-tested only. فرع `claude/trade-classification-scalp-swing-o4s4vh`.

| 28 | ويدجت تصنيف الصفقات (سكالب/سوينج + ارتداد بالنقاط) | A | Claude Code (سعود) | **خلص (mock)** | 2026-11-06 | `modules/ws/24b_tclass.js`. محتاج من المالك: تجربة على أسعار حقيقية + تأكيد حجم النقطة لكل سوق. |
| 27 | Prop Firms tracker — page 10 | A | Claude Code (سعود) | **خلص** | 2026-11-04 | `modules/prop_firms.py` + main.py + i18n. أمر للمالك: أضف تواريخ Ignite وPhoenix عبر Edit. |

| 7 | Order Flow: سجل العمق التاريخي وتغطية 30s/1m/5m/15m/1H | A | ChatGPT | شغال | 2026-10-22 | PR #63 مسودة: إصلاح حد حفظ 7 أيام، فجوة حفظ 1–3 ساعات، تحميل التاريخ قبل الرسم ورسالة النطاق الفارغ. اكتشاف: مصدر الدفتر الحالي REST polling 1.5s مع cache 10s؛ وضع WebSocket تاريخي مستقل ما زال مطلوبًا. لا دمج/نشر. |

| 8 | تفادي إيقاف OKX WebSocket port 8443 | A | ChatGPT | خلص | 2026-10-22 | الافتراضي تغيّر إلى WSS على 443؛ OKX أعلنت توقف 8443 في 2026-10-31. راجع أي CFG.wsBase مخصص قبل الإطلاق. ضمن PR #63، دون دمج/نشر. |
| 7 | إصلاح Order Flow داخل العمود المخصص | A | ChatGPT + Claude review | شغال | 2026-10-22 | PR #67؛ CI الأولي ناجح، أضيفت assertions لمسار paintCol بعد مراجعة Claude؛ متبقي CI بعد آخر commit واختبار متصفح/OKX. لا merge/deploy. |
## من محضر الترندات (مفتوح)

- [ ] M1 تعليقات الفريق  
- [ ] M2 اختيار فئة للتعمق  
- [ ] M3 جدول مقارنة أدوات  
- [ ] M4 قائمة رفض  
- [ ] M5 ربط لاحق بالمشروع فقط بأمر جديد
