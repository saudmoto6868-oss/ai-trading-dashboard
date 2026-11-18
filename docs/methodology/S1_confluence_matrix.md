# مصفوفة التلاقي للمؤشرات والإشارات (سكالب وصفقات سريعة): 18 نوفمبر 2026

> XPiX Signals (Grok). المصادر: `modules/ws/*.js` (Workspace)، و `modules/signals.py` و `sig_filters.py` و `elliott_lab.py` و `harmonic.py` و `gann_lab.py` و `of_setups_bt.py` و `v7_live_smc.js` و `rsi_setups.py` و `strategy_rules.py` (main)، ومهارات `ai-desk`. الأرقام من باك تست S1 (18 نوفمبر، `docs/backtests/S1_2026-11-18/`) ومن `STRATEGY_LAB.md` (13 نوفمبر، net بعد 0.1R). مفيش حاجة معتمدة (n≥100 و t>3).
> المفتاح: **م** = مانع (veto)، **ت** = تأكيد، **ز** = زناد دخول، **هـ** = هدف/مستوى، **ل** = لايف بس (مش مختبر).

| # | المؤشر / الإشارة | بيقيس إيه | الدور في السكالب | مشابه / مكرر لـ | يأكده | يناقضه | الدليل | ترتيب السكالب |
|---|---|---|---|---|---|---|---|---|
| 1 | اتجاه الساعة EMA20/50 (`TCE.bias`، structure.md) | الترند | **م** (ضد الاتجاه ممنوع) | MA ribbon، Donchian، ADX | MSB/BOS، PSAR 15m | زونات السكالب العكسية | gross t=3.05 مع الاتجاه، net −0.157R ضده (t −8.2) | 1 |
| 2 | Kill Zones (`kz`، الجلسات) | التوقيت والسيولة | **م** (برة KZ وآسيا ممنوع) | ORB، sess_amd، Judas | KZS، السحب | — | gross t=3.17 جوه KZ؛ آسيا 5m −0.18R (t −4.8) | 2 |
| 3 | فلتر الامتداد (>2–2.5 ATR-1h عن EMA20؛ skeptic.md) | المطاردة | **م** | RSI متشبع، BB برة | — | breakout | المطاردة −0.20R (t −2.5)؛ درس EURUSD و Gold | 3 |
| 4 | التكلفة/الوقف (سبريد ÷ المخاطرة) | الجدوى | **م** (>0.08R) | — | — | 1m على المعادن/الفوركس | تكلفة 1m: Silver 0.34R، EURUSD 0.36R | 4 |
| 5 | سحب سيولة + رفض (`sweep_rej`، TCE.rejection) | فخ السيولة | **ز** | sweep، liqline، lvl_sweep، KZS | KZ، bias، PDH/PDL، امتصاص (ل) | BOS في نفس الاتجاه | 5m bias+kz: n=112، +0.074R (gross +0.205) | 5 |
| 6 | Kill Zone Sniper (`kzs`) | سحب قوي بجسم وحجم | **ز** (أقوى نسخة من 5) | 5 | الحجم 1.5x، bias | — | n=14، +0.34R: قليل جداً | 6 |
| 7 | PDH/PDL، قمة/قاع الساعة، Equal H/L (`lv`، `ll`، liquidity_ohl) | مستويات السيولة | **هـ** + مكان الزناد | level، ohl_open | السحب، VP | — | `lvl_sweep` لوحده سلبي (−0.17R)؛ ينفع كهدف مش كدخول | 7 |
| 8 | VWAP ±σ (`vwap`) | القيمة العادلة اليومية | **ت** (شراء تحت VWAP / بيع فوقه) + هدف | POC | السحب في الخصم | الترند القوي (ADX>30) | `vwap2` kz: +0.007R؛ lab vwap −0.097R | 8 |
| 9 | Volume Profile POC/VAH/VAL (`vp`) | مناطق الحجم | **هـ** والوقف ورا POC | VWAP | Gann، EMA20 | — | درس BNB (الوقف تحت POC اتضرب) | 9 |
| 10 | PSAR (`psar`، حزمة MT5) | اتجاه قصير | **ت** (1m للدخول، 15m للفلتر) | MA ribbon، Fractals | bias | زونات عكسية | `psar_trend` kz +0.024R؛ درس ETH/BTC (دخول استمراري) | 10 |
| 11 | Scalp Zones Stoch(5,9,3)+RSI14 (`zn`) | تشبع قصير | **ت** في اتجاه الساعة بس | BSO، RSI(2)، RSI+MA 92/8 | bias، VWAP | الترند القوي | bias+kz −0.013R؛ درس Gold (SELL 15:55) | 11 |
| 12 | MSB: OB + Breaker (`msb`، sig_filters strict_smc) | تغيير الهيكل | **هـ**/منطقة | ob، breaker، unicorn، m2022 | الحجم (ob_volume)، FVG | ضد bias | lab: msb_ob −0.061، breaker −0.055، ob −0.085 | 12 |
| 13 | FVG / iFVG (`v7_live_smc`) | فجوة عدم توازن | **هـ**/منطقة دخول limit | OB، unicorn | OTE | — | lab: fvg −0.042 (n=3161) | 13 |
| 14 | OTE 0.62–0.79 (`ote`، fibonacci.md) | عمق الارتداد | منطقة limit | fib | FVG، OB | ADX>30 (ارتداد ضحل) | lab: ote −0.025 (n=785) | 14 |
| 15 | Gann (زوايا، مربع 9، دورات، `gann_lab`) | مستويات سعر/زمن | **هـ** (جني ربح، وقف) | Fib extensions | VP، VWAP | — | OOS 15m +0.126R مقابل عشوائي (t 1.49)؛ درس Copper/Silver | 15 |
| 16 | Harmonic (`harm`، harmonic.py) | PRZ انعكاس | **م** للأهداف (ما تحطش T3 جوه PRZ) | Elliott نهاية 5 | Gann | ترند قوي | درس Silver (PRZ 44.79–45.35) | 16 |
| 17 | Elliott (`ew`، elliott_lab R1–R3، WXY في الأكاديمية) | عدّ الموجات | **م** (ما تبيعش بعد موجة 5 دافعة كاملة) | Harmonic | Wyckoff | — | lab: ew_r3_d2 +0.041R (n=148)؛ التصحيحات المركبة مش detector | 17 |
| 18 | Wyckoff (`wyckoff_phases`) | مرحلة السوق | فلتر اتجاه يومي | bias | Elliott | — | lab: wyck +0.17R (n=177) ← أفضل مدرسة سوينج، مش سكالب | 18 |
| 19 | Divergence RSI/MACD (`div`) | تباطؤ | **م** للدخول المعاكس | rsi_div | Harmonic | الترند | lab: rsi_div −0.092؛ درس Gold (دايفرجنس صاعد = ما تبيعش) | 19 |
| 20 | SMT (`smt`) | اختلاف أسواق مترابطة | **ت** للسحب | — | السحب | — | مش مختبر في S1 | 20 |
| 21 | Delta / CVD / Footprint (`delta`، `fp`، `bvd`) | العدوانية | **ت** (ل) | — | الامتصاص | — | `of_setups_bt.py`: لسه مفيش نتائج | ل |
| 22 | الامتصاص (absorption) | حجم كبير بدون حركة | **ت** (ل) عند الوقف | DOM | السحب | — | نفس 21 | ل |
| 23 | Time & Sales / DOM / Liquidations (`sync`، `dom`، `liqm`) | الشريط والدفتر | **ت** (ل)؛ ما ندخلش من الدفتر لوحده | — | 21 | Spoofing | `dom_reject` مش قابل للاختبار | ل |
| 24 | ADX/DMI، CCI، MACD، BB، Donchian | ترند/زخم | ADX>30 = **م** للدخول عند نص المنطقة | 1 | 1 | 11 | درس Copper (ADX15 41.7) | — |

**ثلاثيات التلاقي المقترحة للسكالب:** (1) سحب PDH/PDL أو قمة/قاع 20 شمعة + إغلاق رفض 5m + مع اتجاه الساعة جوه KZ؛ (2) + السحب في خصم/علاوة VWAP؛ (3) + هدف T2 قبل Gann/POC/PRZ.
**المكررات:** sweep ≈ liqline ≈ lvl_sweep ≈ KZS (نختار KZS/sweep_rej)؛ OB ≈ breaker ≈ unicorn ≈ MSB (نختار MSB strict)؛ Stoch/RSI2/BSO/RSI-MA (نختار `zn`)؛ PSAR ≈ ribbon ≈ fractals (نختار PSAR).
