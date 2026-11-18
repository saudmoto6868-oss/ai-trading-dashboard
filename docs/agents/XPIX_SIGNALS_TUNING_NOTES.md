# ملاحظات ضبط الإعدادات: XPiX Signals (Grok)، 18 نوفمبر 2026

> ملاحظات بس، **ما اتعدلش أي كود**. المنصتين: `ai-trading-dashboard` (Workspace / signals / alerts / cards) و `ai-desk` (مدارس المكتب). كل سطر: الإعداد المقترح ← ليه ← يأكده/يناقضه ← الدرس.
> الدروس: [L](https://gitlab.com/6868-group/ai-trading-dashboard/-/blob/review/top7-postmortem-2026-11-18/docs/reviews/2026-11-18_top7_lessons_ar.md) (ETH، Copper، BNB، EURUSD، BTC، Gold، Silver). الأدلة: [S1](../methodology/S1_scalp_draft.md)، [المصفوفة](../methodology/S1_confluence_matrix.md). كله تجريبي لحد ما يعدّي n≥100 و t>3.

## A) Workspace (`modules/ws`)
| الخيار | الملاحظة |
|---|---|
| `ma` EMA20/50 1h | خليه **مانع** افتراضي للإشارات والكروت (ضده = لا). يأكده MSB/PSAR 15m، يناقضه zn العكسي. [L: EURUSD/Gold] |
| `kz` Kill Zones | ظلّل آسيا كـ"لا سكالب" (5m −0.18R)؛ إشارات KZS/sweep جوه London/NY AM بس. [S1 §3] |
| `kzs` KZ Sniper | سيب جسم 0.9 ATR وحجم 1.5x؛ ضيف شرط bias الساعة وفلتر الامتداد. يأكده sweep_rej. [L: Silver 15:00] |
| `zn` Scalp Zones (5,9,3 + RSI14) | اعرض الإشارة في اتجاه الساعة بس؛ العكسي "تحذير" مش دخول. يناقضه ADX>30. [L: Gold 15:55] |
| `psar` / `mt5` (ribbon+SAR+fractals) | PSAR 15m = فلتر "إلغاء قبل التفعيل" لو قلب ضدنا؛ PSAR 1m = تأكيد الزناد. [L: ETH/BTC] |
| `msb` OB + BB | فعّل `SIGF_STRICT_SMC=1` و `ob_volume` على الكريبتو؛ OB كهدف/منطقة limit مش زناد (lab ob −0.085R). |
| `ote` | ما تحطش الدخول عند 0.62 لو ADX15>30؛ استخدم حافة المنطقة أو قلب PSAR. يأكده FVG. [L: Copper] |
| `vwap` | ضيف ±2σ وعلّم خصم/علاوة؛ بيع تحت VWAP في ترند هابط مطاردة إلا بعد سحب. [L: EURUSD] |
| `vp` POC/VAH/VAL | الوقف **ورا** POC + 0.1 ATR، مش قدامه. يأكده Gann/EMA20. [L: BNB] |
| `gann` | استخدم مستويات 1H/4H **كأهداف وجني ربح** (OOS 15m t 1.49)؛ مش زناد. [L: Copper/Silver] |
| `astro` | سيبه مقفول للسكالب (lab: القمر مفيهوش ميزة). |
| `harm` Harmonic | لو T2/T3 جوه PRZ → اقفل قبله؛ PRZ = مانع لأهداف الاستمرار. يناقضه ترند ADX قوي. [L: Silver] |
| `ew` Elliott | علّم "موجة 5 كاملة" كمانع لدخول نفس الاتجاه؛ WXY/التصحيحات المركبة لسه مش detector، تحتاج اختبار. [L: EURUSD] |
| `div` RSI/MACD/Vol | دايفرجنس ضد الصفقة قبل التفعيل = إلغاء الأمر المعلّق. [L: Gold] |
| `lv` / `ll` / `llt` مستويات وسيولة | PDH/PDL و EQH/EQL كأهداف T1/T2؛ `lvl_sweep` لوحده سلبي (−0.17R). [L: BTC/ETH] |
| `smt` | استخدمه تأكيد للسحب (Gold مقابل Silver، NDX مقابل SPX)؛ مش مختبر. |
| `delta` `fp` `bvd` `dcol` `ofg` `read` `sync` `dom` `liqm` | تأكيد لايف بس، مكتوب على الكارت "لايف/مش مختبر"؛ ما ندخلش من الدفتر لوحده (ai-desk orderflow). |
| `bso` / `r2` / `rm` / `cci` / `macd` | مكررين مع `zn`؛ اختار واحد للسكالب (`zn`). MACD موجب مع بيع = تحذير. [L: EURUSD] |
| `adx` | ADX15>30: الدخول عند حافة المنطقة/قلب PSAR مش نصها. [L: Copper] |
| `don` / `s26` / `sbox` | `sbox` (المربع) افتراضي في كروت السكالب؛ s26 و Donchian سوينج مش سكالب. |
| بريسيتات `smc` `kzs` `flow` `mt5` | بريسيت سكالب مقترح: ma+kz+vwap+kzs+zn+psar+lv (اللي بيستخدمه `scalp_now.py`). |

## B) الإشارات والتنبيهات والكروت (`modules`)
| الخيار | الملاحظة |
|---|---|
| `signals.py` detect_all | ضيف بوابة امتداد >2.5 ATR-1h و bias قبل أي تنبيه (المطاردة −0.20R، ضد الاتجاه −0.16R). |
| `sig_filters.py` | خلي strict_smc/ob_volume/bo_volume شغالين افتراضياً على الكريبتو؛ ممنوع على الفوركس (مفيش حجم حقيقي). |
| `alerts.py` / `telegram_alerts.py` / `spot_alerts_cron.py` | ما تبعتش تنبيه سكالب برة KZ أو لو التكلفة >0.08R؛ اكتب "تجريبي" لحد n≥100 و t>3. |
| `24b_tclass.js` / `tclass.py` كروت الصفقة | ضيف للكارت: نص عند 1R + تعادل، وقف زمني، ومانع الامتداد. [L: Silver، القواعد] |
| `pointSize` | الأهداف بالنقط واقعية في BTC بس؛ باقي الأدوات بالـR. [S1 §1] |
| `rsi_setups.py` / `rsi_confluence.py` | "خارج من التشبع" في اتجاه الساعة بس = تأكيد؛ ضدها = وصف مش دخول. |
| `level_sweeps.py` / `liquidity_ohl.py` | اربطها بإغلاق رفض 5m (`sweep_rej`)، مش لمس المستوى. |
| `elliott_lab.py` / `harmonic.py` / `gann_lab.py` | استخدمهم موانع/أهداف في الكروت؛ ew_r3_d2 (+0.041R net) يستاهل اختبار مع bias. |
| `wyckoff_phases.py` | فلتر يومي للسوينج (+0.17R net، n=177)، مش للسكالب. |
| `of_setups_bt.py` | شغّل الباك تست على aggTrades كريبتو (absorption، cvd_div) عشان يبقى فلتر مختبر. |
| `day_plan.py` / `daily_top.py` | أضف مستويات `prep_day.py` (PDH/PDL، POC، Gann9، FVG/OB 1h). |
| `desk_risk.py` / `risk_engine.py` | سقف مجموعة الارتباط 2R وحد يومي −2R؛ أمس الـ7 كانوا نفس الفكرة (شورت دولار/مخاطرة). [L: الكل] |

## C) ai-desk (`desk/tools`، `desk/agent/skills`)
| المدرسة / الأداة | الملاحظة |
|---|---|
| structure.md | "ممتد >2 ATR عن EMA20 استنى" = أقوى مانع أمس؛ خليه hard في المشكّك. [L: EURUSD/Gold] |
| skeptic.md | بيع في خصم + دايفرجنس = hard veto مش soft. [L: Gold] |
| ict.md / smc_tool | السحب + الإغلاق لازم يكونوا جوه KZ؛ OB/FVG أهداف ومناطق، مش زناد لوحدهم. |
| fibonacci.md / fib_tool | OTE ممنوع كدخول في ترند ADX>30. [L: Copper] |
| topdown_tool | PDH/PDL ومنتصف أمس = أهداف السكالب. |
| wyckoff_tool | فلتر يومي (Spring/UT)؛ أمس الكل SOW. |
| candles.md | Pin/Engulfing **مقفولة** عند مستوى = زناد S1. |
| orderflow.md / test_spoof | تأكيد لايف؛ "مفيش شريط مجاني للفوركس والذهب: قول كده" يتكتب على الكارت. |
| risk.md | 0.5% للصفقة، جزئي عند أول سيولة ثم تعادل، ارتباط >0.8 = صفقة واحدة. [L: الكل] |
| **مصدر البيانات** | أدوات المكتب بتسحب من yfinance: نستخدم القواعد بس على بيانات الداشبورد. |
