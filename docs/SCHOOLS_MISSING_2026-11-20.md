# المدارس والطرق اللي مش عندنا (بحث 2026-11-20)

**الحالة:** بحث ويب، أغلبه من ملخصات وabstracts. ما اتقراش ولا بحث كامل ولا كتاب أصلي. أي رقم يتأكد من المصدر الأولي قبل ما حد يبني عليه. مفيش كود اتغير.

**درجة الدليل:** A = أبحاث محكّمة ومتكررة · B = بحث أو كام بحث أو نتايج مختلطة · C = كلام ممارسين/بائعين بس · F = هامشي.
**الداتا:** OHLC · V = حجم · TICK = تيك/دفتر أوامر · OPT = أوبشن · FUND = بيانات شركات · EXT = داتا خارجية.

**خلفية لازم تتقرا مع الجدول:** مراجعة Park & Irwin لـ95 دراسة حديثة: 56 إيجابية، 20 سلبية، 19 مختلطة، مع تحذير من data snooping واختيار القواعد بعد النتيجة وتقدير تكاليف غلط ([S1](https://ideas.repec.org/a/bla/jecsur/v21y2007i4p786-826.html)). إعادة اختبار قواعد Brock-Lakonishok-LeBaron بعد تصحيح data snooping ما لقتش قاعدة بسيطة مربحة على DJIA وS&P ([S32](https://core.ac.uk/download/37964017.pdf)). وCapital Desk بتاعنا لقى 0 من 52 detector بيعدّي بعد التكاليف (`THREE_PROJECTS_COMPARISON_2026-11-20.md`).

| المدرسة | الفكرة | السيت أب كما بيتدرّس | داتا | دليل | صعوبة |
|---|---|---|---|---|---|
| Market Profile / TPO + Auction Market Theory | السوق مزاد؛ الوقت عند كل سعر = القيمة | Value area 70%، Initial balance = أول ساعة، الامتداد بره الـIB = مبادرة | OHLC داخل اليوم | C | متوسطة (الـvolume profile عندنا) |
| VSA (Tom Williams) | الجهد (حجم) مقابل النتيجة (مدى وإغلاق) | stopping volume، test bar، no-demand، upthrust؛ شورت بعد upthrust مؤكد، وقف فوق الشمعة | OHLC+V | C | قليلة-متوسطة (بيكمّل Wyckoff) |
| Dow Theory | الترند الأساسي يتأكد لما المؤشرين يتفقوا | شراء/بيع على التأكيد | OHLC لمؤشرين | **B** (توقعات Hamilton 1902–29 أدّت alpha) [S2](https://viking.som.yale.edu/the-dow-theory-william-peter-hamiltons-track-record-re-considered) | قليلة |
| Ichimoku (+ نظرية الزمن والموجات) | خطوط توازن وسحابة | فوق السحابة + تقاطع Tenkan/Kijun = شراء؛ وقف عند Kijun أو السحابة | OHLC | B-/مختلط: ربح على مؤشرات أسهم، لا على FX؛ إعادة اختبار فشلت ولقت look-ahead [S6](https://ideas.repec.org/a/wly/ijfiec/v26y2021i4p5321-5336.html) | قليلة (خطوط)، عالية (الزمن) |
| DeMark (TD Sequential/Combo/Lines) | عدّ الإنهاك | Setup 9 إغلاقات مقابل 4 قبلها؛ Countdown 13؛ TDST إبطال | OHLC | C (رسم TDST مختلف عليه) | قليلة-متوسطة |
| Murrey Math | المدى أتمان (من Gann) | العكس عند 8/8 و0/8؛ 4/8 أقوى | OHLC | C | قليلة |
| Andrews pitchfork / median line | السعر بيرجع للخط الأوسط | هدف = الخط الأوسط؛ قاعدة Hagopian | OHLC | C ("80%" غير متحقق) | متوسطة |
| Point & Figure | صناديق وانعكاسات من غير زمن | breakout فوق double top؛ count للأهداف | OHLC | B- (أبحاث قليلة جدًا) | قليلة-متوسطة |
| Renko / Kagi / Three Line Break | شارت بالحركة مش بالزمن | انعكاس الطوبة/الخط | OHLC | C | قليلة |
| Hurst cycles | دورات اسمية ونسب توافقية | عبور FLD = توقيت | OHLC | C | عالية |
| Bill Williams | Alligator وfractals وAO/AC | breakout fractal بعد Alligator + تأكيد AO | OHLC | C | قليلة |
| Elder (Triple Screen، Impulse) | المد في الفريم الكبير والموجة في الصغير | اتجاه MACD-hist أسبوعي، تصحيح oscillator يومي، دخول كسر قمة الشمعة | OHLC | C | قليلة |
| Darvas box | صناديق عند قمم جديدة | شراء كسر قمة الصندوق، وقف تحته | OHLC+V | ما اتحققش؛ القرب من قمة 52 أسبوع له دليل (George & Hwang) [S5](https://typeset.io/pdf/the-52-week-high-and-momentum-investing-4u9j16d52p.pdf) | قليلة |
| CANSLIM (O'Neil) | نمو أساسي + breakout من قاعدة | cup-with-handle، وقف 7–8% | OHLC+V+FUND | B- (شاشة AAII ورقية) | عالية |
| Weinstein stages | 4 مراحل حول متوسط 30 أسبوع | breakout المرحلة 2 بحجم (1.5x–3x، مفيش رقم ثابت) | OHLC+V أسبوعي | C | قليلة |
| Minervini (trend template، VCP) | فلتر المرحلة 2 + تصحيحات بتضيق | قالب 8 نقاط، breakout pivot، وقف 7–8% | OHLC+V | C | قليلة-متوسطة |
| Turtle / Donchian | breakout قناة | دخول 20/55 يوم، وقف 2N (ATR 20)، خروج 10/20 عكسي، إضافة كل ½N | OHLC | B (عائلة trend following) | قليلة |
| Larry Williams | volatility breakout، %R، Oops | buy stop عند الافتتاح + k × مدى أمس؛ Oops | OHLC | C | قليلة |
| Crabel (NR4/NR7، stretch) | الانكماش قبل التمدد | NR7 ثم ORB | OHLC | C (بيدي ضغط مش اتجاه) | قليلة |
| Raschke (Holy Grail، Turtle Soup، 80-20) | تصحيح في ترند قوي؛ كسر فاشل | Holy Grail: ADX>30 وطالع، رجوع لـEMA20؛ Turtle Soup: عكس قمة 20 يوم جديدة اتقفلت جوه | OHLC | C | قليلة |
| Al Brooks | قراءة شمعة بشمعة | H2/L2 دخول تاني | OHLC | C | متوسطة |
| Mark Fisher ACD | Opening range + مسافات A/C | A-up = OR high + A | OHLC داخل اليوم | C | قليلة-متوسطة |
| Pivot points (classic، Camarilla، Woodie، DeMark) | مستويات من H/L/C أمس | Camarilla: عكس عند H3/L3، breakout عند H4/L4 | OHLC | B- غير مباشر (Osler) [S13](https://www.newyorkfed.org/research/epr/00v06n2/0007osle.html) | قليلة |
| Anchored VWAP (Shannon) | متوسط التكلفة من حدث | ارتكاز عند gap أو swing؛ استرجاع/خسارة = تغيّر السيطرة | OHLC+V | C | قليلة |
| Kase | زخم ووقف معدّلين بالتقلب | DevStops، Peak Oscillator | OHLC | C (معادلات مغلقة) | قليلة-متوسطة |
| Breadth / Hindenburg | داخلية السوق | قمم وقيعان جديدة > 2.2–2.8% … | EXT | C | متوسطة |
| COT | ضغط التحوط وازدحام المضاربين | عكس التطرف | EXT (CFTC أسبوعي) | B مختلط [S11](https://ageconsearch.umn.edu/record/54547/files/JARE_Aug09__04R_pp276-296.pdf) | قليلة-متوسطة |
| **Seasonality** | تأثيرات التقويم | نفس الشهر من السنة، Halloween | OHLC تاريخ طويل | **A-/B** [S7](https://econpapers.repec.org/RePEc:eee:jfinec:v:87:y:2008:i:2:p:418-445) [S8](https://ideas.repec.org/a/aea/aecrev/v92y2002i5p1618-1635.html) | قليلة |
| Intermarket (Murphy) | دولار وسلع وسندات وأسهم مرتبطين | السندات تلف قبل الأسهم… | OHLC متعدد | C | قليلة-متوسطة |
| Options GEX | تحوط الديلرز بيكبّر أو يهدّي الحركة | gamma سالبة = زخم داخل اليوم | OPT | **B** (JFE 2021) [S12](https://pure.eur.nl/en/publications/hedging-demand-and-market-intraday-momentum/) | عالية |
| **Pairs / stat-arb** | ارتداد الفرق للمتوسط | فتح عند 2σ، قفل عند التقاطع | OHLC متعدد | **A-** لكن الميزة اضمحلت [S3](https://nber.org/papers/w7032) [S4](https://rpc.cfainstitute.org/research/financial-analysts-journal/2010/does-simple-pairs-trading-still-work) | متوسطة |
| **Quant factors (BAB، Quality)** | علاوات مقطعية | long low-beta / short high-beta | OHLC (BAB)، FUND | **A** [S9](https://papers.ssrn.com/abstract=2312432) | متوسطة-عالية |
| ML | متنبئات غير خطية | أشجار وشبكات عصبية | OHLC+V+FUND | **A** للأسهم الأمريكية المقطعية [S10](https://nber.org/papers/w25398)، مش لأصل واحد داخل اليوم | عالية |
| Financial astrology | توقيت قمري/كوكبي | عوائد أقل حوالين البدر | تقويم | **F** [S14](https://personal.lse.ac.uk/yuan/papers/lunar.pdf) | قليلة |

## أول 10 يتضافوا (بالأولوية: الدليل ثم الداتا اللي عندنا)
1. **Head & shoulders / triangles / flags بطريقة Lo-Mamaysky-Wang** (kernel smoothing): الطريقة الوحيدة لاكتشاف الأنماط ليها أصل في Journal of Finance [S40](https://www.nber.org/papers/w7613). OHLC. متوسطة.
2. **لوحة Seasonality** (نفس الشهر، Halloween، أول/آخر الشهر): أقوى دليل أكاديمي، OHLC، سهلة. كـContext مش إشارة.
3. **Pairs / z-score للفرق** (ذهب-فضة، BTC-ETH، مؤشرات): دليل A- بس الميزة قلّت.
4. **Donchian/Turtle بوقف ATR**: بيكمّل TSMOM في Capital Desk.
5. **القرب من قمة 52 أسبوع + ترتيب breakout بأسلوب Darvas.**
6. **Market Profile / TPO + Initial Balance** فوق الـvolume profile الموجود (Context).
7. **Anchored VWAP + Pivots (classic/Camarilla).**
8. **VSA bar classifier** (بيكمّل Wyckoff اللي مراحله A–E ناقصة).
9. **NR4/NR7 + Crabel stretch** كفلتر على الـORB: اختبار جاهز ORB مقابل ORB+NR7.
10. **Elder Impulse / Triple Screen أو تأكيد Dow** كبوابة فريمات، مربوطة بالـregime.

**يتأجل:** GEX (محتاج داتا أوبشن)، factors وCANSLIM (محتاجين fundamentals)، ML (تكلفة وoverfitting)، Hurst (صعب ودليل C)، astrology (يتشال أو يتعلّم هامشي).

## ما اتحققش / متضارب
- ما اتقراش خالص: قواعد Darvas، نظرية الزمن والموجات في Ichimoku، قواعد Raschke 80-20، معادلة DeMark pivot الكاملة، أدلة Fama-French value.
- قواعد متضاربة: رسم TDST، رقم حجم Weinstein، خروج Turtle System 1 (10 مقابل 15 شمعة)، معادلات Camarilla وWoodie.
- ادعاءات نسب نجاح غير متحققة: P&F 71–92%، pitchfork 80%، Hindenburg، AVWAP "100%"، Kase "مثبت إحصائيًا"، عوائد AAII CANSLIM.

**القاعدة:** أي مدرسة جديدة تدخل الـlab بفرضية مسجّلة قبل التشغيل، بتكاليف حقيقية، وبالحكم الأشد (DSR/PBO/SPA زي Capital Desk)، قبل ما تتحول لإشارة.
