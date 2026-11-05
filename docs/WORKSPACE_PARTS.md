# تقسيم `workspace_app.html` (2026-11-05)

الملف الأصلي (~980 KB، 6717 سطر) اتقسم لـ18 جزء في `modules/ws/` (بالترتيب الأبجدي لاسم الملف):

| الجزء | المحتوى |
|---|---|
| `00_head` / `01_style` / `02_body` / `03_script_boot` | رأس الصفحة، الـCSS، الـbody، سكربت الإعدادات |
| `10_feeds_charts_math` | Finnhub، Hyperliquid، فريمات OKX، الهارمونيك، الزجزاج، Volume profile، أوضاع الشارت |
| `11_i18n_helpers_themes` | الترجمة، الأدوات المساعدة، الثيمات |
| `12_news_filters_context` | الأخبار، فلاتر السكانر، خطة الصفقة، الميني شارت، Ctx، Alerts |
| `13_okx_levels_regime_footprint` | نداءات OKX المشتركة، Gann، SR، Regime، FPS، CandleCache |
| `14_journal_chain` | الجورنال و`Chain` |
| `15_ws_hub_indicators` | WebSocket، Hub، الأيقونات، الصوت، مؤشرات (ADX/CCI/SAR/دايفرجنس) |
| `20_chart_canvas` | شارت الكانفس |
| `21_drawing_tools` | أدوات الرسم |
| `22_ofmap` | **Order Flow Map** (`OFM`, نوع بانل `ofm`): هيت ماب للدفتر الواسع (الوقت × السعر) + خط السعر + فقاعات الصفقات + أعمدة الدفتر الحالي. بتقرا من `Hub` نفس الدفتر والصفقات (من غير طلبات زيادة) |
| `22_panels` | الـWs والـpanels كلها |
| `23_orderflow` | تجميع الأسعار، FLOWREAD، ZoneLog |
| `24_flow_confluence_misc` | Flow confluence وما بعده لحد الـGuide |
| `25_guide` | الشخصية الإرشادية، GVoice، GLive |
| `26_snap` | اللقطة والتسجيل |
| `27_xcmd` | `window.XCMD`: طبقة أوامر آمنة للسائقين الخارجيين (بوت XPiX عبر Playwright): state/setSymbol/setTf/toggle/draw/clearDrawings/addPanel/closePanel/shot. قراءة + رسم فقط، مفيش أوامر صفقات |
| `99_tail` | إغلاق السكربت والصفحة |

## القاعدة
- **الأجزاء هي المصدر.** `modules/workspace_app.html` ملف *مولَّد* (متخزّن في git عشان الاختبارات والـworkflows و`workspace.py` تفضل شغالة).
- بعد أي تعديل في جزء: `python3 scripts/build_workspace.py`، وارفع الاتنين.
- `tests/test_workspace_parts_sync.py` (و`python3 scripts/build_workspace.py --check`) بيفشل لو الملف المولَّد مش مطابق للأجزاء، يعني تعديل مباشر على `workspace_app.html` هيتكشف.
- القطع نصّي عند حدود الأقسام: الدمج بيطلع الملف الأصلي **حرفيًا** (اتأكدت بـ`cmp`). مفيش منطق اتنقل أو اتغيّر.

## لو عندك فرع قديم عدّل `workspace_app.html` مباشرة
هيتعارض. الحل: طبّق نفس التعديل على الجزء المقابل (دوّر على النص بـ`grep -n` في `modules/ws/`)، وبعدين شغّل السكربت. ما تحلّش الconflict في `workspace_app.html` نفسه، لأنه هيتولّد من جديد.
