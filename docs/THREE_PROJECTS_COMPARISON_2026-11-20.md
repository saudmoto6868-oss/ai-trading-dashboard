# مقارنة المشاريع التلاتة: مكتب التداول (ai-desk) × AI Trading Dashboard × 6868 Capital Desk (2026-11-20)

**الحالة:** جرد ومقارنة. مفيش كود اتغير في أي مشروع. ai-desk اتقرا من نسخة محلية مؤقتة (`ai-desk2`، HEAD `bee8f2d`، 0.8.12). Capital Desk اتقرا **من الواجهة المنشورة بس** (الكود مش على الجهاز)، snapshot بتاريخ 18 نوفمبر 18:01 بتوقيت القاهرة. الأرقام اللي جاية من Capital Desk بتاعة المشروع ده على داتته، ومش متحقق منها عندنا.

| المشروع | المكان | النوع |
|---|---|---|
| **مكتب التداول = ai-desk** | GitLab `6868-group/ai-desk`، `ai-desk.onrender.com` | FastAPI + "trading floor" فيه 10 أجنتس LLM وgate |
| **AI Trading Dashboard (6868 X)** | الريبو ده (GitHub `saudmoto6868-oss/ai-trading-dashboard` + GitLab `6868-group/ai-trading-dashboard`) | Streamlit + Workspace JS |
| **6868 Capital Desk** | `capital-desk-dashboard.onrender.com` (مصدر الكود مش متاح محليًا) | داشبورد بحثي: Data Flow، معمل 52 detector، استراتيجيات، Small Caps |

## 1. 6868 Capital Desk (من الواجهة)

**تاباته:** Overview، Asset Brief، Data Flow، 52 Detectors، Strategies، Small Caps.

**اللي فيه ومش عندنا في الداشبورد:**
| الميزة | التفاصيل كما ظاهرة في الواجهة |
|---|---|
| **مسار داتا مؤسسي** | Ingest ← Validate (pandera schemas: 167,608 صف اتفحص، 0 صف سيئ) ← Store (DuckDB + Parquet، 20 series، 5.8 MB) ← Experiment (MLflow، run واحد) ← Decide |
| **حَكَم إحصائي أشد من بتاعنا** | DSR (Deflated Sharpe)، PBO/CSCV، Hansen SPA/StepM/MCS، BHY p-value، t > 3 **بعد تكاليف حقيقية** (fees، spread، slippage، funding بالـbps لكل detector) |
| **نتيجة المعمل** | **0 من 52 detector عدّى** بعد التكاليف؛ Hansen SPA p = 0.807؛ 39 detector اتختبر بـn ≥ 30. أمثلة من الجدول: Elliott wave 3 (n=1168، t net -15.64، gross -0.06R ← net -0.60R)، Elliott wave 5 (n=207، -0.13 ← -0.53R)، ICT 2022 (n=794، 0.07 ← -0.36R)، OTE Fibonacci (n=931، 0.01 ← -0.51R). التكلفة حوالين 16–22 bps لكل صفقة |
| **Asset Brief بسيناريوهين** | لكل أصل: اتجاه Weekly/Daily/4H/1H بـEMA 20/50/200، regime + ADX، ATR، RSI، حجم نسبي، مدى الجلسات (آسيا/لندن/نيويورك)، فجوات supply/demand مفتوحة، عناوين أخبار، و**Scenario A (ارتداد) وScenario B (رفض)** بدخول ووقف و3 أهداف — مكتوب عليها "مش إشارة". **ده بالظبط طبقة السيناريو اللي ناقصة في الداشبورد** |
| **استراتيجيات كمية (Phase 2 preview)** | Momentum TSMOM (12 شهر، vol target 10%)، Carry (spot طويل / HL perp قصير لما funding موجب)، Liquidity Gate (خليج + مصر)، Memecoin Safety Gate. مكتوب إن ولا واحدة عدّت DSR/PBO/SPA، والـCarry متفائل (من غير basis وborrow) |
| **Small Caps بفلتر أمان** | الخليج ومصر وmemecoins: traded value ≥ $1M/يوم، half-spread ≤ 1% (Corwin-Schultz)، ≤ 5% أيام من غير حجم، safety score (Amihud + spread + vol). 42 مؤهل من 58 |
| **خريطة حرارة وتدفق عالمي** | تغيّر يومي + regime لكل سوق (مأخوذ من regime classifier بتاع الداشبورد)، وترتيب الجلسات آسيا ← الخليج/مصر ← أوروبا ← أمريكا |
| **ترتيب momentum عبر الأصول** | 12-1 return / vol، فوق SMA200 (مأخوذ من `momentum.py` بتاع الداشبورد)؛ مكتوب "ترتيب مش توقع، مش مختبر" |
| **مصادر إضافية** | Binance، DexScreener، RugCheck، GoPlus (أمان العملات) |

**المهم:** Capital Desk بيستخدم **نفس أسماء الـdetectors بتاعتنا** (pa_star، kzs، abc، wavec، ew3، ew5، m2022، ote، cisd، ...) وبيقيسهم بحكم أشد. يعني عنده دليل على مكتشفاتنا إحنا مش بنعرضه. والنتيجة (كل حاجة بتخسر بعد التكلفة) متسقة مع اللي لقيناه في 2.6.

## 2. مكتب التداول (ai-desk) مقابل الداشبورد (مقارنة كود، `ai-desk2` HEAD `bee8f2d`)

| المجال | ai-desk | الداشبورد | الفجوة |
|---|---|---|---|
| الأسواق | 36 رمز ثابت (`desk/config.py:96-135`): 11 FX، ذهب، فضة، بترول، 4 مؤشرات (SPX/NDX/DJI/RUT)، 6 كريبتو، 5 أسهم شرق أوسط (COMI، ETEL، أرامكو، الراجحي، إعمار)، 7 أسهم أمريكية؛ تحجيم بالجنيه والريال والدرهم (`risk.py:123-133`) | 11 فئة بتتكتشف لحظيًا من OKX + Hyperliquid + Yahoo (`asset_classes.py`)، memecoins، أوبشن؛ EGX وتداول 12 رمز لكل واحد بس متعلّمين `NO_FEED` | الداشبورد ناقصه: إعمار، DJI/RUT، وأسهم الشرق الأوسط في السكان والتحجيم. المكتب ناقصه: memecoins، أوبشن، كريبتو واسع، DAX/FTSE/N225 |
| المصادر | Binance، Yahoo، Kraken FX، FRED، Hyperliquid، DXY محسوب بمعادلة ICE، CFTC، أسعار فائدة OECD، ForexFactory، 4 RSS، wire inspector (`data/sources.py`، `server.py:326`) | OKX، Hyperliquid، Yahoo، Finnhub، Binance، MT5، TwelveData، FRED، CFTC، Cboe، DexScreener، CMC، Grok | الداشبورد ناقصه: Kraken FX احتياطي، فائدة OECD، DXY محسوب، wire inspector |
| المدارس | framework: topdown، fib/OTE، SMC، EMA/VWAP، SMT، scenarios؛ Wyckoff، order flow + **spoofing**، COT index، **seasonality**، **KairosBias** مركّب، **قوة العملات 28 زوج**، **فروق الفائدة**، fed path | ~30 detector + PA، ~50 مفتاح lab: Elliott، Harmonic، Gann، جلسات/killzones، Turtle/Donchian، divergence، breaker، CRT | الداشبورد ناقصه: seasonality، فروق الفائدة، قوة العملات، bias مركّب، spoofing. المكتب ناقصه: Elliott، Harmonic، Gann، جلسات، Turtle، divergence، breaker، CRT، PA |
| الأجنتس | **13 agent** (`agents/team.py:25-58`): رئيس + 8 متخصصين (Wyckoff، ICT، COT، OrderFlow، Sentiment، Macro، Seasonality، News) + Risk + Bull + Bear + Auditor + Reviewer؛ **Auditor بيرفض أي رقم مش موجود في نتيجة أداة**؛ gate بالكود؛ سلسلة providers (Groq ← Gemini ← OpenRouter ← DeepSeek) بـRPM | Mr X/Guide (Gemini، صوت Gemini Live)، `strategy_agent.py` (كلام ← قواعد)، bots مراجعة | الداشبورد ناقصه: floor نقاش متعدد الأجنتس، Auditor للأرقام، سلسلة providers. المكتب ناقصه: صوت، strategy agent |
| مسار الفكرة | 5 مراحل (`orchestrator.py:89-249`): سياق، تأكيد، توقيت، **skeptic بأسباب شك مسمّاة**، gate ← READY/PENDING/WATCH + **"ليه مفيش صفقة"**؛ سكان كل 15 دقيقة | scanner ← scorer ← خطة 3 books ← quality score بالـlab ← Telegram؛ **تجميد الإشارة وقت التنبيه** (`signal_log.py:49`) | كل واحد ناقصه اللي عند التاني |
| الجورنال | SQLite؛ تقييم كل ساعة؛ **مدير 5 دقايق** (BE بعد T1، trail 1.5 ATR، خروج T2)؛ درس LLM لكل صفقة؛ اقتراح أوزان عند ≥30 (مش بيتطبق لوحده) | JSON + localStorage + `.signal_log.jsonl` + brain؛ postmortem؛ Monte Carlo؛ طبقات Chain | — |
| المخاطرة | 0.5%/1%؛ حد يومي = نص حد الشركة؛ trailing max loss؛ **consistency cap**؛ discipline lock؛ 3 حسابات prop بمستويات | 0.25% (0.5% بس لـA+ متحقق بـn≥30 OOS)؛ 2% يومي؛ 3 stops = قفل اليوم؛ RR ≥ 2 | **متعارض** (قسم 4) |
| الباك تيست | قواعد يومية من غير تكاليف ومن غير OOS (`platform.py:290-338`)؛ بحث TSMOM/carry/COT مقابل buy-and-hold بتكاليف 1–2bp | walk-forward، t مقابل random، IS/OOS، 0.10R، تسجيل مسبق، holdout، cron أسبوعي | المكتب ناقصه المعمل كله. الداشبورد ناقصه: مقارنة buy-and-hold، TSMOM/carry/COT، replay لحسابات prop |
| التنبيهات | **مفيش** | Telegram بـquality score وdedupe، brain كل 30 دقيقة، spot، ساعة الأحداث، أخبار | المكتب ناقصه كله |
| الواجهة | 8 مجموعات/14 view: Floor، Narrative، Routine، Wire، … | 19 صفحة: Academy، Spot، Options، Research Hub، Prop… | — |

## 3. مين ياخد إيه من مين
**الداشبورد ياخد من ai-desk (أهم 10):** Auditor الأرقام (`team.py:69-120`)؛ مرحلة skeptic بأسباب شك وREADY/PENDING/WATCH (`orchestrator.py:176-234`)؛ سطر "ليه مفيش صفقة" (`:257-262`)؛ مدير 5 دقايق للأفكار الأوتوماتيك (`manage.py:34-133`)؛ سلسلة providers بـRPM (`config.py:57-84`)؛ حسابات prop (trailing max loss، consistency cap، حد شخصي، توجيه بمستويات) (`risk.py:56-81,166`)؛ أدوات ماكرو (فروق فائدة، قوة 28 زوج، COT index، seasonality) (`macro.py:51-107`، `market.py:42-83`)؛ spoofing (`orderflow.py:65-141`)؛ بحث TSMOM/carry/COT مقابل buy-and-hold (`research.py`)؛ مصادر احتياطية (Kraken FX، ICE DXY، wire inspector).

**ai-desk ياخد من الداشبورد (أهم 10):** المعمل (walk-forward، t، IS/OOS، 0.10R)؛ التسجيل المسبق والـholdout؛ مخاطرة مربوطة بالتحقق (`risk_policy.py`)؛ Telegram بـquality score؛ تجميد الإشارة؛ Monte Carlo للجورنال؛ قفل اليوم بعد 3 stops؛ detectors الجلسات وCRT؛ أخبار بمستويات + FRED stress؛ قوايم EGX/تداول الأوسع وتغطية OKX. **ومهم: يملا `alerts`/`ready` بدل `[]` في `desk/pro.py:76-78`.**

**Capital Desk ← الاتنين:** الحكم الإحصائي الأشد (DSR، PBO، SPA، BHY، تكاليف bps حقيقية)، Asset Brief بسيناريوهين، فلتر أمان small caps، مسار داتا (pandera + Parquet + MLflow). **والاتنين ← Capital Desk:** Workspace اللحظي، order flow، Elliott/Harmonic/Gann، Telegram brain.

## 4. تعارضات لازم المالك يحسمها
| القاعدة | ai-desk | الداشبورد |
|---|---|---|
| المخاطرة للصفقة | 0.5% (حد 1%) (`desk/risk.py:5,25`) | 0.25%، و0.5% لـA+ متحقق بس (`risk_policy.py:4-6`). وCFX جوه الداشبورد لسه 0.5 |
| الوقف اليومي | نص حد الشركة (2–2.5%) | 2% + 3 stops |
| حجب الأخبار | 12 ساعة قبل الخبر العالي (`config.py:205`) | ±1 ساعة / 30 دقيقة قبل و15 بعد (`event_clock.py:114`) — **ومتضارب جوه الداشبورد نفسه** |
| الأهداف | 2R و3R؛ أقل من 1R = veto | TP 1.5/2.5/3.5R؛ lab 1.5R؛ RR أدنى 2 — **متضارب جوه الداشبورد** |
| توافق الفريم الكبير | عدم التوافق = **veto** (`orchestrator.py:220`) | التداول مع ترند الفريم الكبير **أسوأ من العشوائي** (t -6.39، n=36,512، `docs/PIPELINE.md:68`) — **تعارض جوهري** |
| تجميع الأسباب | 3 أسباب من قسمين = ترقية؛ النجوم بتوجّه الحساب | تكديس الـdetectors ما بيحسّنش؛ النجوم كانت مقلوبة |
| معيار الدليل | n ≥ 30، Sharpe مقابل buy-and-hold | n ≥ 100، t > 3، OOS، بعد التكلفة؛ وCapital Desk أشد (DSR/PBO/SPA) |
| التكاليف | 1–2bp في البحث؛ صفر في باك تيست الـwatchlist | 0.10R ثابت؛ Capital Desk: 16–22 bps حقيقية |
| انتهاء الـpending | 24 ساعة | 48 شمعة |
| عند T1 | الوقف لـBE من غير تقليل | 50% خروج + BE عند +1R |
| الـLLM | Groq ثم Gemini | Gemini بس (قاعدة المالك)؛ Guide بيستخدم Claude لو فيه مفتاح؛ `ai_provider.py:14` لسه بيشاور على OpenAI اللي اتشال |
| أسماء الرموز | `BTCUSD`، `XAUUSD` | `BTC-USDT`، `HL:xyz:GOLD` |

متفقين على: trail 1.5 ATR، الوقف يتحسب الأول لو الشمعة لمست الاتنين، ونفس endpoint بتاع CFTC.

**ما اتفحصش:** باقي JS المكتب، thresholds في `tools/framework.py`، وكود Capital Desk نفسه. تخمينات: veto عدم التوافق في المكتب ممكن يكون في الـpipeline بس مش في الـfloor؛ رموز مصر والسعودية في الداشبورد ممكن تترسم من Yahoo رغم `NO_FEED`.
