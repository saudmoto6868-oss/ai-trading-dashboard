# مقارنتنا بأفضل المنصات + خطة الباك تيست المستمر (2026-11-20)

**الحالة:** بحث ويب + قراءة مستندات المشروع. مفيش كود اتغير. أسعار المنصات من صفحات متضاربة (إلا اللي معلّم رسمي)، وكل نسب النجاح عندهم تسويق غير متحقق. ما لقيتش تدقيق مستقل لأي منصة.

## 1. الاسمين (اتحددوا 2026-11-20)
- **"فلكس تشارت" = Flux Charts:** ناشر مؤشرات على TradingView: مؤشرات مجانية ومدفوعة، screeners، وbacktesters مدمجة في الـoverlays (SFX، supply/demand، price action، ICT Turtle Soup، Silver Bullet). Pro حوالي $59.99 شهريًا حسب موقع تجميع (مش متأكد من موقعهم). **ما لقيتش دليل على AI عندهم.** ([TradingView](https://il.tradingview.com/script/GjcM6I3h-Flux-Charts-SFX-Automation)، [PropFirmMatch](https://propfirmmatch.com/trading-tools/flux-charts))
- **"بيج بالوجا" = BigBeluga:** مؤلف مؤشرات على TradingView متخصص في السيولة والـSMC: FVG Order Blocks، Volume-Weighted OB، SMC toolkit (breakers، extreme highs/lows، EQH/EQL، liquidity wicks)، Liquidity Zones، **Liquidity Thermal Map**، Dynamic Liquidity Depth، High Volume Points. الأوصاف من كلام المؤلف، ومش متراجعة على الكود. ([SMC](https://tradingview.com/script/WTNPnxsp-BigBeluga-Smart-Money-Concepts)، [FVG OB](https://www.tradingview.com/script/xy4EFLtD-FVG-Order-Blocks-BigBeluga))

## 2. أفضل 10 (ترتيبي، مش ترتيب رسمي)

| # | المنصة | الأقوى فيها | الباك تيست | الـAI | الضعف المعروف |
|---|---|---|---|---|---|
| 1 | TradingView | مكتبة مؤشرات ضخمة + مجتمع | Strategy Tester + Deep Backtesting + replay (حسب الباقة) | غير مبحوث | repainting موثّق عندهم "مش bug" (pivots, `request.security`, `calc_on_every_tick`)؛ مفيش walk-forward لقيته |
| 2 | LuxAlgo | الأقرب فكريًا لنا: إشارات + AI + باك تيست | "Strategy Screener" (كان AI Backtesting Assistant): تشغيل مجدول (اثنين/أربع/جمعة 23:30 UTC)، فريمات 5m/15m/1h، **بيتقفل 2026-11-14 حسب الصفحة الرسمية** | بحث استراتيجيات بلغة طبيعية | مفيش walk-forward/OOS موثّق؛ الصفحة نفسها بتقول ممكن أخطاء؛ ادعاء non-repaint من مواقع مراجعة بس |
| 3 | TrendSpider | اكتشاف trendlines وFibs وأنماط تلقائي | عمق الباك تيست بيتحدد بالباقة (2h/5m/1m) | Sidekick (رسائل شهرية مجانية + إضافات مدفوعة) | تقييمات affiliate بس |
| 4 | Trade Ideas | سكانرز لحظية | OddsMaker (Premium) | Holly: إشارات بدخول/وقف/هدف | "60%+" تسويق غير متحقق |
| 5 | Tickeron | روبوتات AI وأنماط | نتايج "backtest" سنوية 20–70% حسب مواقع (مش live) | Y | شكاوى Trustpilot: إشارات مش مرتبطة بالنتيجة (حكايات، مش تدقيق) |
| 6 | Bookmap | مرجع depth heatmap / order flow | - | - | رسوم داتا السوق منفصلة |
| 7 | ATAS / Quantower / Sierra Chart | footprint وvolume profile وDOM وreplay | Quantower: backtest مدمج؛ ATAS: Market Replay | ? | منحنى تعلم صعب؛ أسعار متضاربة |
| 8 | Optuma | أدوات Gann وElliott الجدية (Gann Fan وBox وDynamic Square of 9 كإضافة مدفوعة) | قوي حسب مراجعين | ? | تقييم المراجعين منهجيته مش واضحة؛ السعر مش متأكد |
| 9 | Trading Central | تعرّف أنماط آلي مدمج في الوسطاء، فيه Elliott | ? | pattern recognition | بيتوزع عبر وسطاء |
| 10 | ChartPrime | مؤشرات TradingView مدفوعة | عبر TradingView | - | مفيش ادعاء رسمي non-repaint |

Finviz Elite وStockCharts أقل أهمية (باك تيست أساسي).

**المصادر (ثانوية، تحقق من الصفحات الرسمية قبل أي اقتباس سعر):** [TradingView pricing](https://www.tradingview.com/pricing/)، [TradingView: repainting](https://tradingview.com/pine-script-docs/concepts/repainting)، [LuxAlgo docs: AI Backtesting](https://docs.luxalgo.com/docs/ai-backtesting/introduction)، [LuxAlgo pricing](https://www.luxalgo.com/pricing.md)، [TrendSpider pricing](https://trendspider.com/pricing/)، [Trade Ideas pricing](https://www.trade-ideas.com/pricing/)، [Bookmap pricing](https://bookmap.com/pricing/)، [Optuma Gann tools](https://www.optuma.com/kb/optuma/gann-and-astro/gann-tools)، [Trading Central](https://www.tradingcentral.com/technical-insight)، [StockCharts pricing](https://stockcharts.com/pricing).

## 3. إحنا فين (من الكود والمستندات، مش من تجربة جديدة)

| البُعد | عندنا (دليله) | الفجوة مقابل السوق / المدارس |
|---|---|---|
| معلومات / أكاديمي | `docs/academy*` (9 مدارس) لكن Elliott وGann وHarmonic أربع سطور لكل واحد | ناقص تفصيل: [`SCHOOLS_GAP_ELLIOTT_GANN_HARMONIC_2026-11-20.md`](SCHOOLS_GAP_ELLIOTT_GANN_HARMONIC_2026-11-20.md) |
| مؤشرات | Workspace (شارت، DOM، order flow، Setup Card)، `signals.py` detectors، Elliott/Harmonic/Gann محدودة | Elliott: 12 فجوة؛ Harmonic: 5 من ~15 نمط؛ Gann: grid وlab فقط |
| أداء / باك تيست | `strategy_lab.py` walk-forward أسبوعي، t مقابل random، IS/OOS، net بعد 0.10R، `lab_holdout.py`، `PREREG_*` | **مفيش منافس لقيته بيعرض t-stat ولا OOS جنب IS.** ده أقوى فرق عندنا لو اتحافظ عليه |
| باك تيست مستمر | cron أسبوعي (الأحد 03:17 UTC) + spot الاثنين، والباقي يدوي (`backtest-real.yml`) | مفيش تشغيل يومي ولا "آخر تشغيل + ثغرات" ظاهر في الواجهة ولا تنبيه drift |
| تفكير / عقل عام | `brain_cron.py` كل 30 دقيقة (تنبيهات + Top 7 + مراجعة يومية بالمدرسة + أوزان تجريبية 0.7–1.3 على نقاط Top 7) | بيقترح بس، مش بيعدّل شيء. مفيش سيناريوهات Elliott/Gann/Harmonic جديدة |
| أجنت / AI | Mr X صوتي (Gemini Live)، Guide، `claude.yml` و`gemini-review.yml` و`school-review.yml` | مفيش أجنت متابعة لحظية ولا "المقفّل" (متقترح في غرفة الاجتماعات) |
| anti-repaint | **ما اتفحصش في الجلسة دي.** `signal_log.py` موجود | لازم فحص: هل الإشارة بتتجمّد وقت الظهور؟ (المنافسين مش بيضمنوه) |

## 4. الباك تيست المستمر: خيار مقترح (مش مبني)

الهدف: نبقى أصدق من السوق، مش أكتر ادعاءً. اللي عندنا الأساس، واللي ناقص التوقيت والعرض.

1. **توقيت:** تشغيل يومي خفيف على آخر N شمعة (rolling) + الأسبوعي الكامل زي ما هو. السبب: LuxAlgo بتشغّل 3 مرات في الأسبوع بدون OOS، فاليومي مع OOS نفسه ميزة.
2. **تجميد الإشارة وقت الظهور (anti-repaint):** كل إشارة تتسجل عند إغلاق الشمعة بوقتها ومفاتيحها وخطتها، وبعد كده تتحكم النتيجة فقط. مفيش إعادة حساب بأثر رجعي. (`signal_log.py` و`brain.py` عندهم الأساس؛ لازم نتأكد إنه مطابق.)
3. **تسجيل مسبق:** أي مفتاح جديد (نمط Elliott/Gann/Harmonic) يتسجل في `PREREG_*` قبل أول تشغيل، بفرضية وn هدف (≥100 لكل اسم نمط، ≥30 لكل split) وتكلفة.
4. **عرض في الواجهة:** لكل setup: n، avgR، t، IS مقابل OOS، net بعد التكلفة، "آخر تشغيل" و"الثغرات" (فريمات/رموز ما اتشغلتش)، وعلامة صريحة "مش دليل" تحت n=30.
5. **مراقب drift:** لو OOS avgR بقى أسوأ من IS بفرق ثابت لكذا تشغيل، تنبيه (مش تعديل تلقائي).
6. **ربط بـ"المقفّل":** تقرير أسبوعي بيقول إيه اتقفل وإيه فاضل، وإيه اتحسّن أو اتدهور، وإيه ممكن يتشال/يتخفف.
7. **حدود:** التكلفة (GitHub Actions)، وتحديد الرموز والفريمات (الأسبوعي كله ممكن يكون ثقيل يوميًا). ده قرار للمالك قبل أي workflow جديد.

**ممنوع:** تعديل أوزان أو عتبات الـscanner تلقائيًا، وأي live trading، ودمج في `main` من غير موافقة.

## 5. قرارات محتاجة المالك
1. اسم/لينك FlexCharts وBigPaloga.
2. نبني الباك تيست اليومي ولا نكتفي بالأسبوعي + عرض أحسن؟
3. أنماط Elliott/Gann/Harmonic الجديدة: Context بس، ولا مفاتيح lab بـ n ≥ 100؟
4. صور Elliott وGann وHarmonic (ما لقيتهاش) ومحادثة Signals.
