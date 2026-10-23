"""Order-flow and options manual (owner 2026-10-22): trading methods that need no price chart (order book, time & sales, funding / open
interest, options), what each one measures, how to read it, how it is used, where it breaks, what evidence exists, and which of our
tools show it. Rendered by the Technical Office 'Flow manual' tab.

Evidence labels are per source and honest: OPENED = the page was read in full for this manual; SEARCH = only a search snippet was
seen; MEMORY = background knowledge, not checked here. The headline result of the research is sobering and is shown first:
nothing here is proven profitable AFTER costs for a retail trader on free data. The tools are context, risk filters and execution
timing until a forward test (protocol below) says otherwise. No number in this file is a measured result of ours."""
from __future__ import annotations

TIERS = {
    "B": ("B · فيه دليل لكن مش قابل للتنفيذ لمتداول فرد", "warn"),
    "C": ("C · سياق وفلتر مخاطرة", "info"),
    "D": ("D · مفيش دليل أو بيتضلل بسهولة", "bad"),
}

HEADLINE = [
    "مفيش إشارة من الأدوات دي ثبتت إنها بتكسب بعد التكلفة لمتداول فرد على بيانات مجانية. ده استنتاج البحث، مش رأي.",
    "اللي ثبت أكاديمياً: عدم توازن تدفق الأوامر (OFI) بيفسر حركة السعر في ثواني على بيانات أسهم ممتازة، والأفق ثواني، فالرسوم والتأخير على متداول فرد غالباً أكبر منه (تقدير مش مقاس). ونسبة put/call اللي بتتنبأ بالأسهم محسوبة من بيانات داخلية (فتح مركز جديد + مشتري) مش متاحة للعامة.",
    "عملياً هنستخدمها كده: <b>سياق</b> (مين متزحم، هل السوق متوتر)، <b>فلتر مخاطرة</b> (قلل الحجم أو ما تدخلش)، <b>توقيت تنفيذ</b> (إزاي أحط أمر الدخول). مش زناد دخول مستقل.",
    "أي استخدام أكبر من كده يتثبت بالاختبار الأمامي (forward test) تحت: صفقات مسجلة بقاعدة مجمدة، ‏n كبير، ‏t > 3 بعد التكلفة، والنصين موجبين.",
]

# tool -> (what it shows, where in the dashboard, data and freshness, honest limits)
TOOLS = [
    ("دفتر الأوامر (DOM)", "أوامر الشراء والبيع المعلقة على مستويات السعر",
     "تاب الكريبتو (سُلّم الأسعار) + عمود الأوردر فلو في الـ Workspace (هيت ماب Bookmap-style)", "OKX / Hyperliquid؛ لقطات، مش كل تغيير",
     "Hyperliquid بيبعت لقطات على بلوكات (20 مستوى بطيء / 5 سريع)، يعني مفيش تتبع لحظي لكل إلغاء. العمق المعروض ممكن يكون وهمي."),
    ("تتبع الأوامر (placed / pulled / filled)", "أوامر كبيرة اتحطت، اختفت من غير تنفيذ، أو اتنفذت",
     "سُلّم الأسعار + فلاشات الهيت ماب (أبيض = اتسحب، بنفسجي = اتنفذ / امتصاص)", "فرق بين لقطتين",
     "اختفاء أمر «تلميح» مش «إثبات» spoofing: بنشوف الفرق بين لقطات بس، مش وقت الإلغاء."),
    ("Time & Sales (الشريط)", "كل صفقة: السعر والحجم وجهة المبادر (مشتري ولا بائع)",
     "جدول الصفقات (تصنيف Smart / Whale بمضاعفات المتوسط) + الفوتبرنت", "OKX صفقات حية؛ الذهب عبر WebSocket Hyperliquid (فرع hl-trades-ws لسه مش متدمج)",
     "جهة المبادر جاهزة من البورصة (مش محتاجين تخمين Lee-Ready). بورصة واحدة مش السوق كله. الصفقات الكبيرة ممكن تتقسم."),
    ("الفوتبرنت / الدلتا / الامتصاص", "حجم الشراء × البيع عند كل سعر جوه الشمعة، وعلامات الامتصاص",
     "الـ Workspace (عمود الأوردر فلو + علامات ▲▼)", "لايف في المتصفح؛ مفيش تاريخ طويل نختبر عليه",
     "ما لقيتش دليل منشور إن أنماط الفوتبرنت أو دايفرجنس CVD بتكسب بعد التكلفة."),
    ("التمويل والـ OI والتصفيات", "تزاحم المراكز على العقود الدائمة، وتصفيات المراكز بالإجبار",
     "الـ Workspace (كارت التزامن + التمويل) و OKX liquidation-orders", "OKX عام، من غير مفتاح",
     "خرائط التصفية تقديرية (مبنية على رافعة مفترضة). نسبة Long/Short عينة حسابات بورصة واحدة."),
    ("مكتب الأوبشنز (جديد)", "كل سوق أوبشنز BTC / ETH: put/call، max pain، IV، السكيو، هيكل IV، أكبر الـ strikes",
     "المكتب الفني ← مكتب الأوبشنز", "Deribit عام بدون مفتاح، متأخر حوالي دقيقتين",
     "الـ OI والحجم مابيقولوش الصفقة فتحت ولا قفلت، ولا هيدج ولا رهان. الـ IV rank بيتحسب من تاريخ DVOL اليومي (مؤشر التقلب الضمني 30 يوم)، مش من كل الـ strikes."),
    ("أوبشنز أسهم أمريكا (Cboe)", "سلسلة خيارات مؤجلة 15 دقيقة", "الكود موجود (modules/cboe_options.py) ومش متوصل بالواجهة",
     "Cboe عام، غير رسمي، متأخر 15 دقيقة", "المسارات ممكن تتغير من غير إعلان؛ شروط إعادة الاستخدام ماتأكدتش."),
    ("تدفق الأوبشنز غير العادي (Unusual Whales)", "تنبيهات أوامر أوبشنز كبيرة", "الكود موجود (modules/options_flow.py)", "محتاج مفتاح مدفوع ومش متجرب على الـ API الحقيقي",
     "مش شغال عندنا. وحتى لو اشتغل: مش بيفرق بين فتح وقفل."),
]

# method -> dict
METHODS = [
    {"id": "book", "title": "١. توازن دفتر الأوامر (Order flow imbalance)", "tier": "B",
     "measures": "ضغط الشراء مقابل البيع على أفضل مستويات الدفتر، وتغيرات الأحجام عندها بين تحديث والتاني.",
     "read": ["اجمع حجم أول 5 مستويات شراء (B) وبيع (A) واحسب I = (B − A) ÷ (B + A).",
              "الأدق: احسب تغير الأحجام عند أفضل سعر بين تحديثين (OFI) وجمّعه على 1–30 ثانية.",
              "قارن بتغير السعر الفعلي؛ ولازم تقسمه على العمق، لأن نفس الضغط بيحرك السعر أكتر في دفتر رفيع."],
     "setup": "فلتر توقيت مش استراتيجية: لو بتشتري، حط أمرك لما الضغط بيروح ناحيتك، وما تدخلش ماركت في وش ضغط أحادي. الإبطال: الاتجاه ينقلب أو حجم كبير يختفي من غير تنفيذ. الأفق: 5–60 ثانية.",
     "fails": "التكلفة: تيكر على الدخول والخروج (حوالي 2–5 نقطة أساس للعقود الدائمة، من الذاكرة) ≥ الأثر المتوقع. التأخير. عمق وهمي. بورصة واحدة = رؤية جزئية.",
     "evidence": "منشور (أسهم): Cont-Kukanov-Stoikov 2014 — OFI بيفسر تغير السعر القصير (OPENED: arxiv.org/abs/1011.6402). Kolm-Turiel-Westray 2023 — أفق التنبؤ نحو تغيرين في السعر، ثواني (OPENED: ideas.repec.org/a/bla/mathfi/v33y2023i4p1044-1081.html). مفيش دراسة كريبتو بصافي بعد التكلفة لقيتها.",
     "data": "كافية للحساب، مش للمنافسة في السرعة."},
    {"id": "walls", "title": "٢. جدران السيولة والامتصاص والأوامر المخفية", "tier": "D",
     "measures": "أحجام كبيرة معلقة (جدار)، تكرار تنفيذ عند مستوى مع تجدد الحجم المعروض (امتصاص / iceberg).",
     "read": ["الجدار الثابت لدقائق وبيتعرض لتداول فعلي = أكتر مصداقية من جدار بيظهر ويختفي.",
              "الامتصاص: بيع عدواني كتير عند مستوى والسعر ما نزلش، والحجم المعروض بيتجدد.",
              "أمر بيختفي قبل ما السعر يلمسه = ممكن spoofing (تلميح مش إثبات عندنا)."],
     "setup": "سياق لمستوى اخترته من الشارت (دعم / مقاومة / سحب سيولة). لو الجدار اتسحب قبل ما السعر يوصل: ماتبنيش عليه. الأفق: دقائق.",
     "fails": "Spoofing / layering: الأوامر بتتحط علشان تتلغي. مفيش دليل منشور إن الجدران بتشتغل كدعم / مقاومة. الأوامر المخفية مش ظاهرة أصلاً.",
     "evidence": "ممارسة متداولين فقط؛ ما لقيتش دراسة محكّمة. (Elliptic عن spoofing: SEARCH فقط، مصدر تجاري.)",
     "data": "ضعيفة: لقطات بدل تتبع كل إلغاء."},
    {"id": "tape", "title": "٣. الشريط (Time & Sales) والـ CVD والفوتبرنت", "tier": "D",
     "measures": "تدفق الصفقات الموقّع (جهة المبادر)، حجم الصفقات، وسرعة الشريط.",
     "read": ["CVD = تراكم (حجم شراء مبادر − حجم بيع مبادر).",
              "دايفرجنس: السعر بيعمل قمة جديدة والـ CVD لأ.",
              "سرعة الشريط: عدد الصفقات في الثانية مقابل وسيطه الأخير؛ والقفزة = حدث، مش اتجاه.",
              "امتصاص: بيع عدواني ضخم ومفيش تقدم لتحت. إنهاك: قفزة حجم مع انقلاب الدلتا."],
     "setup": "تأكيد عند مستوى أنت حددته مسبقاً (مثلاً إعداد مؤكد في الرادار): ادخل لما العدوان في اتجاه الصفقة يهدا والعدوان العكسي يظهر. الإبطال: قمة جديدة بـ CVD مؤكد. الأفق: 1–15 دقيقة.",
     "fails": "CVD بورصة واحدة مش السوق. الصفقات الكبيرة ممكن تتقسم أو تكون wash. القيمة المطلقة للـ CVD بتعتمد على نقطة البداية. الشريط بيبين المنفذ بس، مش المخفي.",
     "evidence": "الدراسات بتدعم التدفق الموقّع كمدخل قصير جداً (نفس دراسات OFI فوق)، لكن ما لقيتش أي دليل إن دايفرجنس CVD أو أنماط الفوتبرنت بتكسب بعد التكلفة.",
     "data": "كافية للعرض الحي، ومفيش تاريخ طويل للاختبار."},
    {"id": "oi", "title": "٤. التمويل والـ OI والتصفيات (العقود الدائمة)", "tier": "C",
     "measures": "مين متزحم على أنهي اتجاه ومين اتصفى.",
     "read": ["OI ↑ والسعر ↑ = مراكز شراء جديدة (تأكيد وزحمة).",
              "OI ↑ والسعر ↓ = مراكز بيع جديدة.",
              "OI ↓ والسعر ↑ = تغطية مراكز بيع.",
              "OI ↓ والسعر ↓ = تصفية شراء / استسلام.",
              "تمويل متطرف + OI صاعد = صفقة مزدحمة وخطر سكويز."],
     "setup": "فلتر مخاطرة: تمويل متطرف وزحمة = قلل الحجم أو وسّع الوقف. عكس الاتجاه (fade) بس بعد ما شلال التصفية يوقف، والإبطال: الـ OI يرجع يطلع في نفس الاتجاه. الأفق: ساعات لأيام.",
     "fails": "خرائط التصفية تقديرية. نسبة Long/Short عينة بورصة واحدة. التمويل مش بيتنبأ بالاتجاه بشكل مثبت بعد التكلفة.",
     "evidence": "ورقة عمل على arXiv (الصفحة ما بتوضحش إنها محكّمة) عن عقود Binance: انحراف كبير عن لا-مراجحة، والعائد أغلبه من التقارب مش من دفعات التمويل (arxiv.org/html/2212.06888v5؛ تفاصيل المنصة والتحكيم من وصف الباحث مش متأكدة). مفيش دراسة محكّمة لقيتها إن التمويل / OI بيتنبأ بعائد BTC بعد التكلفة.",
     "data": "كافية (REST عام)، التاريخ محدود."},
    {"id": "iv", "title": "٥. التقلب الضمني والسكيو وهيكل المدة (Options)", "tier": "C",
     "measures": "كام السوق بيدفع تأمين، ومن النزول ولا الصعود، وقريب ولا بعيد.",
     "read": ["ATM IV: مستوى التقلب المتوقع (سنوي).",
              "السكيو = IV بوت بعيد تحت − IV كول بعيد فوق: موجب كبير = بيدفعوا أكتر للحماية من النزول. (قرب الاستحقاق الأقرب من يوم بيتشوه، بنحسب على 7 أيام فأكتر.)",
              "هيكل المدة: القريب أغلى من البعيد (مقلوب) = توتر قصير المدى.",
              "الحركة المتوقعة قبل حدث = سعر الستريدل ÷ السعر؛ بتساعد في تحديد الحجم، مش الاتجاه."],
     "setup": "فلتر نظام السوق: سكيو أو هيكل مقلوب بيشتد قبل حدث = قلل الرافعة، وسّع الوقف، أو اقعد. ماتفتحش صفقة اتجاهية من الأوبشنز لوحدها.",
     "fails": "مستوى IV لوحده ماقولش حاجة؛ الـ IV rank (من DVOL، سنة) بيحط الرقم في سياقه. مفيش دليل كريبتو إن IV rank بيتنبأ بالاتجاه.",
     "evidence": "Cremers-Weinbaum 2010: انحراف IV بين الكول والبوت بيتنبأ بعائد أسبوعي في الأسهم (OPENED: ideas.repec.org/a/cup/jfinqa/v45y2010i02p335-367_00.html). مفيش دليل كريبتو لقيته.",
     "data": "كافية (Deribit مجاني بدون مفتاح)."},
    {"id": "pos", "title": "٦. Put/Call و max pain و GEX وتدفق الأوبشنز غير العادي", "tier": "D",
     "measures": "مراكز الأوبشنز المفتوحة وتوقع تحوطات صناع السوق.",
     "read": ["Put/Call بالـ OI أو الحجم: نسبة، مش اتجاه (بوت كتير غالباً حماية).",
              "max pain: السترايك اللي أقل خسارة لحاملي الأوبشنز عند الاستحقاق؛ نظرية الشد، ومعناها في آخر يوم أو يومين بس.",
              "GEX: تقدير نموذجي لتحوطات صناع السوق، بيفترض مين شاري ومين بايع."],
     "setup": "سياق بس (علامة نظام تقلب). مفيش صفقة منها.",
     "fails": "العامة مش بتعرف الصفقة فتحت ولا قفلت ولا شراء ولا بيع. GEX تقدير يختلف بين المزودين ومعتمد على OI قديم. دراسة Cboe نفسها على 0DTE لقت التدفق متوازن وجاما صناع السوق صغيرة (OPENED: cboe.com/insights/posts/volatility-insights-evaluating-the-market-impact-of-spx-0-dte-options؛ كاتبها عنده مصلحة تجارية).",
     "evidence": "Pan-Poteshman 2006: نسبة put/call محسوبة من بيانات داخلية (فتح + مشتري) بتتنبأ بالأسهم، لكن النسخة العامة ما بتعرفش تفرّق (OPENED: nber.org/papers/w10925). مزود GEX نفسه بيقول إنه 'ما بيتنبأش بالاتجاه' (OPENED: spotgamma.com/what-is-gex-gamma-exposure). مفيش اختبار محكّم إن GEX بيتنبأ بالـ pinning أو التقلب.",
     "data": "put/call و max pain من بياناتنا؛ GEX وتصنيف الصفقات مش متاحين مجاناً."},
]

ROUTINE = [
    ("قبل الجلسة (دقيقتين)", "مكتب الأوبشنز: هيكل الـ IV والسكيو لـ BTC / ETH + التقويم الاقتصادي (شريط الرادار). تمويل متطرف أو هيكل مقلوب = قلل الحجم النهارده."),
    ("اختيار الإعداد", "الرادار: مؤكد بأعلى ترتيب + كارت الصفقة (دخول / وقف / أهداف) + دليل الكاشف من المعمل. القرار هنا مش من الأوردر فلو."),
    ("عند المستوى", "الـ Workspace: الشريط والفوتبرنت. تأكيد: عدوان في اتجاهك بيهدا + امتصاص. لو الجدار اتسحب أو الدلتا بتتعارض: انتظر."),
    ("التنفيذ", "الدفتر: حط أمر limit لما الضغط ناحيتك؛ ماتدخلش ماركت في وش ضغط أحادي. وقفك من الشارت، مش من الجدار."),
    ("بعد الصفقة", "سجّلها (الجورنال / CSV) مع ملاحظة: هل التأكيد كان موجود؟ ده الداتا اللي هتحكم لاحقاً."),
]

FORWARD_TEST = [
    "جمّد القاعدة قبل التسجيل (مثلاً: «أدخل لما الامتصاص يظهر عند مستوى مؤكد») واكتب نسخة منها.",
    "سجّل كل مرة القاعدة اتحققت، مش اللي دخلتها بس: وقت البورصة ووقت الاستلام، الرمز، الميزات (أحجام أول 5 مستويات، السبريد، CVD، التمويل، OI)، وعائد السعر بعد 5 ثواني و30 ثانية و5 دقايق وساعة.",
    "احتفظ بخط أساس: نفس التوقيت بدون إشارة + تجربة بعلامات مخلوطة عشوائياً.",
    "التكلفة: عندنا رقم مسطح 10 نقط أساس للصفقة (حد أدنى تخطيطي: رسوم تيكر للدخول والخروج + سبريد + انزلاق) بيتغير من الواجهة. التطوير الجاي: انزلاق من الدفتر المسجل وسيناريو maker مع خصم للاختيار العكسي.",
    "الحجم: الصفقات غير متداخلة جوه نفس الرمز (مش بين الرموز: BTC وETH وSOL بيتحركوا مع بعض، فالـ t عندنا متفائل)، والشرط t > 3 بعد عدد النسخ اللي جربتها (كل نسخة محاولة). التطوير الجاي: t بأخطاء Newey-West.",
    "الحكم: الصافي بعد التكلفة موجب ومستقر في النصين وt > 3 والفترة الأمامية ≥ فترة الاكتشاف. غير كده يفضل عرض فقط (سياق).",
    "ملحوظة: لقطات Hyperliquid على بلوكات؛ وغياب بيانات الإلغاء بيحيّز أي ميزة مبنية على spoofing.",
]

MISSING = [
    "تاريخ يومي لـ put/call و max pain (Deribit مابيوفرهوش؛ محتاج لقطة يومية مجدولة تعدل الريبو. الـ IV rank اتحل بـ DVOL فمش ضروري دلوقتي).",
    "تسجيل متواصل للأوردر فلو لأيام: المسجّل والحكم موجودين (معمل الأوردر فلو) بس بيشتغلوا يدوي؛ التسجيل المتواصل محتاج جهاز شغال أو مهمة مجدولة.",
    "أوبشنز الأسهم والمؤشرات (Cboe): الكود موجود ومش متوصل ولا متجرب.",
    "تصنيف تدفق الأوبشنز فتح / قفل (محتاج بيانات مدفوعة).",
    "تدفق الأوامر الحقيقي على مستوى كل تغيير (OKX tick-by-tick غالباً بمستويات VIP).",
]


# ---------------------------------------------------------------------------------------------------------------------------
# English version (one language at a time: owner rule 2026-10-23). The Arabic constants above are unchanged; `get(ar)` returns
# the set for the requested language. Same structure, same sources and evidence labels, no new numbers.
# ---------------------------------------------------------------------------------------------------------------------------
TIERS_EN = {
    "B": ("B · evidence exists but is not actionable for an individual trader", "warn"),
    "C": ("C · context and risk filter", "info"),
    "D": ("D · no evidence, or easily misleading", "bad"),
}

HEADLINE_EN = [
    "None of these tools has been shown to make money after costs for an individual trader on free data. That is the research conclusion, not an opinion.",
    "What is academically established: order flow imbalance (OFI) explains price moves over a few seconds on excellent equity data, and the horizon is seconds, so fees and latency for an individual trader are most likely larger than the edge (an estimate, not measured). The put/call ratio that predicts stocks is computed from internal data (new position opened + buyer) that is not available to the public.",
    "In practice we use them like this: as <b>context</b> (who is crowded, is the market stressed), as a <b>risk filter</b> (cut size or stay out), and as <b>execution timing</b> (how to place the entry order). Not as a standalone entry trigger.",
    "Any bigger use has to be proven by a forward test under: logged trades with a frozen rule, a large n, t > 3 after costs, and both halves positive.",
]

TOOLS_EN = [
    ("Order book (DOM)", "Resting buy and sell orders at each price level",
     "Crypto tab (price ladder) + the order-flow column in the Workspace (Bookmap-style heatmap)", "OKX / Hyperliquid; snapshots, not every change",
     "Hyperliquid sends snapshots per block (20 levels slow / 5 fast), so there is no real-time tracking of every cancel. Displayed depth can be fake."),
    ("Order tracking (placed / pulled / filled)", "Large orders that were placed, vanished without filling, or were filled",
     "Price ladder + heatmap flashes (white = pulled, purple = filled / absorbed)", "Difference between two snapshots",
     "A vanished order is a hint, not proof of spoofing: we only see the difference between snapshots, not the cancel time."),
    ("Time & Sales (the tape)", "Every trade: price, size and the aggressor side (buyer or seller)",
     "Trades table (Smart / Whale classification by multiples of the average) + the footprint", "OKX live trades; gold via the Hyperliquid WebSocket (the hl-trades-ws branch is not merged yet)",
     "The aggressor side comes from the exchange (no Lee-Ready guessing needed). One exchange is not the whole market. Large trades can be split."),
    ("Footprint / delta / absorption", "Buy volume vs sell volume at each price inside the candle, and absorption marks",
     "The Workspace (order-flow column + ▲▼ marks)", "Live in the browser; no long history to test on",
     "No published evidence that footprint patterns or CVD divergence make money after costs."),
    ("Funding, OI and liquidations", "Position crowding on perpetual contracts, and forced liquidations",
     "The Workspace (sync card + funding) and OKX liquidation-orders", "OKX public, no key",
     "Liquidation maps are estimates (built on an assumed leverage). The Long/Short ratio is a sample of accounts on one exchange."),
    ("Options desk (new)", "Every BTC / ETH options market: put/call, max pain, IV, skew, IV term structure, biggest strikes",
     "Technical Office > Options desk", "Deribit public, no key, about 2 minutes delayed",
     "OI and volume do not say whether a trade opened or closed, nor whether it was a hedge or a bet. IV rank is computed from the daily DVOL history (30-day implied volatility index), not from all strikes."),
    ("US equity options (Cboe)", "Options chain delayed 15 minutes", "The code exists (modules/cboe_options.py) and is not wired to the UI",
     "Cboe public, unofficial, 15 minutes delayed", "Paths can change without notice; reuse terms were not verified."),
    ("Unusual options flow (Unusual Whales)", "Alerts on large options orders", "The code exists (modules/options_flow.py)", "Needs a paid key and was not tried against the real API",
     "Not running here. And even if it ran: it cannot tell opening from closing."),
]

METHODS_EN = [
    {"id": "book", "title": "1. Order book imbalance (Order flow imbalance)", "tier": "B",
     "measures": "Buy vs sell pressure at the best book levels, and the change in sizes there between one update and the next.",
     "read": ["Sum the size of the top 5 bid (B) and ask (A) levels and compute I = (B − A) ÷ (B + A).",
              "More precise: compute the change in sizes at the best price between two updates (OFI) and aggregate it over 1–30 seconds.",
              "Compare with the actual price change, and scale by depth, because the same pressure moves price more in a thin book."],
     "setup": "A timing filter, not a strategy: if you are buying, place your order when pressure goes your way, and do not enter at market against one-sided pressure. Invalidation: the direction flips or a large size disappears without filling. Horizon: 5–60 seconds.",
     "fails": "Cost: taker fees on entry and exit (about 2–5 basis points for perpetuals, from memory) ≥ the expected effect. Latency. Fake depth. One exchange = a partial view.",
     "evidence": "Published (equities): Cont-Kukanov-Stoikov 2014 — OFI explains short-horizon price change (OPENED: arxiv.org/abs/1011.6402). Kolm-Turiel-Westray 2023 — the forecast horizon is about two price changes, seconds (OPENED: ideas.repec.org/a/bla/mathfi/v33y2023i4p1044-1081.html). No crypto study net of costs was found.",
     "data": "Enough to compute, not enough to compete on speed."},
    {"id": "walls", "title": "2. Liquidity walls, absorption and hidden orders", "tier": "D",
     "measures": "Large resting sizes (a wall), and repeated execution at a level while the displayed size refills (absorption / iceberg).",
     "read": ["A wall that stays for minutes and gets traded into is more credible than one that appears and disappears.",
              "Absorption: lots of aggressive selling at a level and price does not drop, while the displayed size refills.",
              "An order that vanishes before price touches it = possible spoofing (a hint, not proof, here)."],
     "setup": "Context for a level you picked from the chart (support / resistance / liquidity sweep). If the wall is pulled before price arrives: do not build on it. Horizon: minutes.",
     "fails": "Spoofing / layering: orders are placed to be cancelled. No published evidence that walls work as support / resistance. Hidden orders are not visible at all.",
     "evidence": "Trader practice only; no peer-reviewed study found. (Elliptic on spoofing: SEARCH only, a commercial source.)",
     "data": "Weak: snapshots instead of tracking every cancel."},
    {"id": "tape", "title": "3. The tape (Time & Sales), CVD and footprint", "tier": "D",
     "measures": "Signed trade flow (aggressor side), trade sizes, and tape speed.",
     "read": ["CVD = cumulative (aggressive buy volume − aggressive sell volume).",
              "Divergence: price makes a new high and CVD does not.",
              "Tape speed: trades per second against its recent median; a jump = an event, not a trend.",
              "Absorption: huge aggressive selling and no progress lower. Exhaustion: a volume spike with the delta flipping."],
     "setup": "Confirmation at a level you defined beforehand (for example a confirmed setup in the Radar): enter when aggression in your trade direction calms and opposite aggression appears. Invalidation: a new high with confirmed CVD. Horizon: 1–15 minutes.",
     "fails": "CVD from one exchange is not the market. Large trades can be split or be wash trades. The absolute CVD value depends on the starting point. The tape shows only what executed, not what is hidden.",
     "evidence": "Studies support signed flow as a very-short-horizon input (the same OFI studies above), but no evidence was found that CVD divergence or footprint patterns make money after costs.",
     "data": "Enough for live display, and there is no long history for testing."},
    {"id": "oi", "title": "4. Funding, OI and liquidations (perpetuals)", "tier": "C",
     "measures": "Who is crowded in which direction and who got liquidated.",
     "read": ["OI up and price up = new long positions (confirmation and crowding).",
              "OI up and price down = new short positions.",
              "OI down and price up = short covering.",
              "OI down and price down = long liquidation / capitulation.",
              "Extreme funding + rising OI = a crowded trade and squeeze risk."],
     "setup": "A risk filter: extreme funding and crowding = cut size or widen the stop. Fade only after the liquidation cascade stops; invalidation: OI starts rising again in the same direction. Horizon: hours to days.",
     "fails": "Liquidation maps are estimates. The Long/Short ratio is a one-exchange sample. Funding is not proven to predict direction after costs.",
     "evidence": "An arXiv working paper (the page does not say it is peer reviewed) on Binance contracts: a large deviation from no-arbitrage, with most of the return coming from convergence rather than funding payments (arxiv.org/html/2212.06888v5; platform and refereeing details come from the researcher's description and are not confirmed). No peer-reviewed study was found showing funding / OI predicts BTC returns after costs.",
     "data": "Enough (public REST), history is limited."},
    {"id": "iv", "title": "5. Implied volatility, skew and term structure (Options)", "tier": "C",
     "measures": "How much the market pays for insurance, whether for downside or upside, and near-term or far-term.",
     "read": ["ATM IV: the level of expected volatility (annualised).",
              "Skew = far out-of-the-money put IV − far call IV: a large positive value = they pay more for downside protection. (Expiries closer than a day are distorted, so we compute on 7 days or more.)",
              "Term structure: near-term more expensive than far-term (inverted) = short-term stress.",
              "Expected move before an event = straddle price ÷ price; it helps with sizing, not direction."],
     "setup": "A market-regime filter: skew or an inverted structure intensifying before an event = cut leverage, widen the stop, or sit out. Do not open a directional trade from options alone.",
     "fails": "An IV level alone says nothing; IV rank (from DVOL, one year) puts the number in context. No crypto evidence that IV rank predicts direction.",
     "evidence": "Cremers-Weinbaum 2010: the IV difference between calls and puts predicts weekly stock returns (OPENED: ideas.repec.org/a/cup/jfinqa/v45y2010i02p335-367_00.html). No crypto evidence was found.",
     "data": "Enough (Deribit is free, no key)."},
    {"id": "pos", "title": "6. Put/Call, max pain, GEX and unusual options flow", "tier": "D",
     "measures": "Open options positions and the expected hedging by market makers.",
     "read": ["Put/Call by OI or volume: a ratio, not a direction (many puts are usually protection).",
              "max pain: the strike with the least loss to option holders at expiry; a pinning theory, meaningful only in the last day or two.",
              "GEX: a model estimate of market-maker hedging, assuming who is buying and who is selling."],
     "setup": "Context only (a volatility-regime marker). No trade comes from it.",
     "fails": "The public cannot tell whether a trade opened or closed, or whether it was a buy or a sell. GEX is an estimate that differs between providers and relies on stale OI. Cboe's own study of 0DTE found the flow balanced and market-maker gamma small (OPENED: cboe.com/insights/posts/volatility-insights-evaluating-the-market-impact-of-spx-0-dte-options; the author has a commercial interest).",
     "evidence": "Pan-Poteshman 2006: a put/call ratio computed from internal data (opening + buyer) predicts stocks, but the public version cannot make that distinction (OPENED: nber.org/papers/w10925). The GEX provider itself says it does not predict direction (OPENED: spotgamma.com/what-is-gex-gamma-exposure). No peer-reviewed test that GEX predicts pinning or volatility.",
     "data": "put/call and max pain from our data; GEX and trade classification are not available for free."},
]

ROUTINE_EN = [
    ("Before the session (2 minutes)", "Options desk: IV structure and skew for BTC / ETH + the economic calendar (Radar strip). Extreme funding or an inverted structure = cut size today."),
    ("Picking the setup", "Radar: confirmed with the highest rank + the trade card (entry / stop / targets) + the detector evidence from the Lab. The decision is made here, not from order flow."),
    ("At the level", "The Workspace: tape and footprint. Confirmation: aggression in your direction calming + absorption. If the wall is pulled or the delta conflicts: wait."),
    ("Execution", "The book: place a limit order when pressure is on your side; do not enter at market against one-sided pressure. Your stop comes from the chart, not from the wall."),
    ("After the trade", "Log it (journal / CSV) with a note: was the confirmation present? This is the data that will judge later."),
]

FORWARD_TEST_EN = [
    "Freeze the rule before logging (for example: \"enter when absorption shows at a confirmed level\") and keep a written copy.",
    "Log every time the rule triggered, not only the ones you traded: exchange time and receive time, the symbol, the features (top-5 level sizes, spread, CVD, funding, OI), and the price return after 5 seconds, 30 seconds, 5 minutes and one hour.",
    "Keep a baseline: the same timing without a signal + a run with randomly shuffled labels.",
    "Cost: we use a flat 10 basis points per trade (a planning minimum: taker fees on entry and exit + spread + slippage), adjustable from the UI. Next development: slippage from the recorded book and a maker scenario with an adverse-selection haircut.",
    "Sample size: non-overlapping trades within the same symbol (not across symbols: BTC, ETH and SOL move together, so our t is optimistic), and the requirement t > 3 after the number of variants you tried (every variant is an attempt). Next development: t with Newey-West errors.",
    "The verdict: net after costs positive and stable in both halves, t > 3, and the forward period ≥ the discovery period. Otherwise it stays display-only (context).",
    "Note: Hyperliquid snapshots are per block; and the absence of cancel data biases any feature built on spoofing.",
]

MISSING_EN = [
    "A daily history of put/call and max pain (Deribit does not provide it; it needs a scheduled daily snapshot that updates the repo. IV rank was solved with DVOL, so it is not needed now).",
    "Continuous order-flow recording for days: the recorder and the verdict exist (Order-flow lab) but run manually; continuous recording needs a machine that stays on or a scheduled task.",
    "Equity and index options (Cboe): the code exists, is not wired in and was not tried.",
    "Classifying options flow as opening / closing (needs paid data).",
    "True per-change order flow (OKX tick-by-tick, usually at VIP tiers).",
]


def get(ar: bool | None = None) -> dict:
    """The manual's text in one language: {TIERS, HEADLINE, TOOLS, METHODS, ROUTINE, FORWARD_TEST, MISSING}. ar=None follows the site language."""
    if ar is None:
        from modules.i18n import lang
        ar = lang() == "ar"
    if ar:
        return {"TIERS": TIERS, "HEADLINE": HEADLINE, "TOOLS": TOOLS, "METHODS": METHODS, "ROUTINE": ROUTINE, "FORWARD_TEST": FORWARD_TEST, "MISSING": MISSING}
    return {"TIERS": TIERS_EN, "HEADLINE": HEADLINE_EN, "TOOLS": TOOLS_EN, "METHODS": METHODS_EN, "ROUTINE": ROUTINE_EN, "FORWARD_TEST": FORWARD_TEST_EN, "MISSING": MISSING_EN}
