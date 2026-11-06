# بحث استراتيجيات — 2026-11-06 (أمر المالك: VWAP، المتوسطات، فكرة ناسداك، افتتاح الجلسات)

القاعدة: اللي لقيناه **أفكار للتجربة، مش أدلة**. أي نتيجة من بلوج / ريديت / سكريبت TradingView من غير out-of-sample وتكلفة = مش دليل.

| الفكرة | اللي لقيناه | قوة الدليل | اتعمل إيه |
|---|---|---|---|
| VWAP mean reversion (±2σ، رجوع للـVWAP) | شروحات + سكريبتات TradingView؛ أرقام عينات (PF 1.78، win ~59%) من مصدر بيبيع أدوات؛ بيفشل في الترند القوي (اقتراح فلتر ADX < 25) | ضعيف | مدرسة **VWAP** في Trade Classes (±2σ → هدف الـVWAP، ورجوع للـVWAP في الترند). حالة السوق chop / ترند بتتحسب في «ليه ماادخلش» |
| فكرة المالك: ناسداك شراء بس لما السعر تحت الـVWAP بـ25+ نقطة | مفيش اختبار مستقل لنفس القاعدة؛ بوست ريديت عن mean reversion شراء بس على ES/NQ (Sharpe ~3.6، والكومنتات بتشكك: tick data، walk-forward، survivorship) | مش متجرب | **★ استراتيجياتي**: «Nasdaq VWAP stretch (long only)» جاهزة ومفعلة: `close < vwap − 25 pts` على XYZ100/NQ، ستوب 1 ATR. السجل الفعلي في الجورنال |
| Opening Range Breakout (5m / 15m) على NQ/ES | 5m كانت حلوة 5 شهور ووحشة على 7 سنين؛ ~900 صفقة 15m على MNQ 2019-2026 (من غير أرقام كاملة)؛ ES وNQ مختلفين | ضعيف / متضارب | موجود أصلًا كإشارة «نطاق الافتتاح» في السكانر (بيدخل Trade Classes من مدرسة السكانر) |
| تقاطع EMA 9/21، 50/200 | ورقة arXiv (2602.10785): الأداء بيتغير جدًا مع نوافذ walk-forward؛ Golden Cross على الأسهم ~6.9% سنويًا أقل من buy & hold؛ مفيش اختبار out-of-sample محترم على كريبتو intraday بعد الرسوم | ضعيف | مدرسة **المتوسطات**: 9/21 مع فلتر EMA200، و50/200 |
| مستويات الجلسة (افتتاح اليوم / الأسبوع، أعلى وأقل اليوم اللي فات) | سكريبتات TradingView (Intraday Playbook Key Levels، Multi-VWAP) بترسم المستويات؛ مفيش نتايج | مفيش أرقام | مدرسة **مستويات الجلسة**: ارتداد عند PDH / PDL / افتتاح اليوم / الأسبوع، وكسر PDH / PDL. + سطر «الجلسة الجاية» والمرشحين قبلها |

## المصادر
- VWAP: https://pineify.app/free-tools/vwap-strategy-tradingview · https://therighttrader.com/learn/trading-strategies/vwap-mean-reversion · https://www.tradingview.com/script/kP7HmAzw-NQ-Phantom-Scalper-Pro
- ريديت (مرآة): https://reddit.sentinel-team.org/posts/1sm6y5g/snapshots/2026-04-17T18%3A50%3A14.038042Z
- ORB: https://ninjatrader-strategy-site.pages.dev/blog/opening-range-breakout-nq-futures · https://backtestsnotsignals.substack.com/p/opening-range-breakout-real-edge · https://red.ks32.dev/r/Daytrading/comments/1jraug5/15minute_opening_range_breakouts
- المتوسطات: https://arxiv.org/pdf/2602.10785v1 · https://quantifiedstrategies.substack.com/p/9-ema-trading-strategy-does-it-work
- مستويات: https://in.tradingview.com/script/0YTBYxSf-Intraday-Playbook-Key-Levels · https://www.tradingview.com/script/UkP9lPzF-Multi-Custom-VWAP/

## إزاي المحرك «بيتعلم» دلوقتي (من غير تكلفة)
1. كل صفقة «ادخل» بتدخل الجورنال بتاج المدرسة (`TC <school>`)، والجورنال بيتابعها لحد الهدف / الستوب.
2. بعد 10 صفقات مقفولة للمدرسة: كسبانة = نقطة زيادة في «ليه أدخل»، خسرانة = 1.5 في «ليه ماادخلش». أقل من 30 = مش دليل.
3. ترتيب المدارس من الجورنال ظاهر في الويدجت (📚).

## البحث اليومي (اقتراح، محتاج موافقة المالك لأنه بيكلف)
- workflow يومي على GitHub Actions: يقرا 3-5 مصادر عامة (RSS / صفحات)، يلخص بـ Gemini (أرخص موديل، حد يومي)، ويكتب ملف `docs/research/daily/<date>.md` بأفكار جديدة + القاعدة المقترحة بصيغة «استراتيجياتي».
- الأفكار ماتتفعلش لوحدها: المالك يضيفها من ★ استراتيجياتي، أو تتجرب في الـlab الأول (n ≥ 100، t > 3، النصين موجب، بعد التكلفة).
- ماتشغلش قبل موافقة المالك (قاعدة الـworkflows).
