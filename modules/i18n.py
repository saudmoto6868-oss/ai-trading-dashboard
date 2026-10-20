"""Item 21: Arabic for the Streamlit side of the dashboard (the Workspace already has its own en / ar texts).
L("English text") returns the Arabic version when the header language switch (session key "ws_lang") is "ar", otherwise the
English text unchanged. A missing entry simply stays English - never a blank. Trading terms traders use as-is in Arabic
(RSI, EMA, VWAP, SMC, ICT, Put/Call, Sharpe ...) stay in Latin letters."""
from __future__ import annotations

AR = {
    # tabs
    "🧩 Workspace": "🧩 مساحة العمل", "📊 Chart Scanner": "📊 سكانر الشارت", "🪙 Crypto": "🪙 كريبتو", "💱 Forex": "💱 فوركس",
    "🥇 Metals": "🥇 معادن", "📈 Stocks": "📈 أسهم", "🐸 Meme Coins": "🐸 عملات الميم", "📈 Performance": "📈 الأداء",
    # sidebar
    "Settings": "الإعدادات", "Auto-refresh (live data)": "تحديث تلقائي (بيانات لحظية)", "Refresh every (seconds)": "التحديث كل (ثانية)",
    "Play sound on NEW strong signals": "صوت مع كل إشارة قوية جديدة", "Order Book / Time & Sales": "دفتر الأوامر / الصفقات اللحظية",
    "Smart trade = size >= N x median print": "صفقة ذكية = الحجم >= N × متوسط الصفقة",
    "Prints this many times larger than the median trade in the window are flagged SMART; 2.5x that is WHALE.":
        "الصفقات الأكبر من متوسط الصفقة بالعدد ده تتعلّم SMART، و2.5 ضعف كده تبقى WHALE (حوت).",
    "Big limit order = N x median level": "أمر ليمت كبير = N × متوسط المستوى",
    "Used by the DOM highlight and by Limit Tracking.": "بيستخدمه تمييز الـ DOM ومتابعة الأوامر الكبيرة.",
    "DOM / Time&Sales refresh (seconds)": "تحديث الـ DOM والصفقات (ثانية)",
    "How often the two order-flow panels update by themselves (flashes appear on each update).": "كل قد إيه اللوحتين بيتحدثوا لوحدهم (الوميض بيظهر مع كل تحديث).",
    "Absorption = level volume >= N x median level": "امتصاص = حجم المستوى >= N × متوسط المستوى",
    "Heavy volume trading at one price while the price barely moves.": "حجم تداول كبير عند سعر واحد والسعر تقريباً مش بيتحرك.",
    "Telegram alerts (optional)": "تنبيهات تليجرام (اختياري)", "Send the best alerts to Telegram": "ابعت أحسن التنبيهات على تليجرام",
    "Only the top-ranked alerts (evidence score, not a proven win rate). Needs TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in Secrets.":
        "أعلى التنبيهات ترتيباً بس (درجة أدلة، مش نسبة نجاح مثبتة). محتاج TELEGRAM_BOT_TOKEN و TELEGRAM_CHAT_ID في الـ Secrets.",
    "Max alerts per scan": "أقصى عدد تنبيهات في كل مسح", "Minimum quality (0-100)": "أقل جودة (0-100)", "Send test message": "ابعت رسالة تجربة",
    "Sent.": "اتبعتت.",
    "Quality = strategy families agreeing + daily bias / premium-discount / killzone + reward:risk. It ranks the evidence; it does not predict success.":
        "الجودة = عدد عائلات الاستراتيجيات المتفقة + اتجاه اليوم / بريميوم-ديسكاونت / الكيل زون + العائد:المخاطرة. دي بترتب الأدلة، مش بتتوقع النجاح.",
    "Chart / Layout": "الشارت / الشكل", "Workspace height (px)": "ارتفاع مساحة العمل (بكسل)", "Page background": "خلفية الصفحة",
    "Accent colour (tabs, highlights)": "لون التمييز (التابات والعلامات)",
    "Per-widget colours: use the two colour dots in each Workspace widget's title bar.": "ألوان كل widget: استخدم النقطتين الملونين في شريط عنوانه.",
    "streamlit-autorefresh is not installed - add it to requirements.txt.": "streamlit-autorefresh مش متسطّب - ضيفه في requirements.txt.",
    # header
    "Asset class": "فئة السوق", "Asset class: drives the Chart Scanner, Ready trades and the Workspace watchlist together.":
        "فئة السوق: بتتحكم في سكانر الشارت والصفقات الجاهزة وقائمة المتابعة مع بعض.",
    "Market": "نوع السوق", "Spot / Perpetual swap / dated Futures (OKX).": "سبوت / عقود دائمة / عقود آجلة بتاريخ (OKX).", "Language": "اللغة",
    "Macro watchlist": "مؤشرات الاقتصاد الكلي", "US economy (FRED)": "الاقتصاد الأمريكي (FRED)",
    "Monthly/daily official data, not live prices. Needs FRED_API_KEY in Secrets.": "بيانات رسمية شهرية / يومية، مش أسعار لحظية. محتاج FRED_API_KEY في الـ Secrets.",
    "Crypto": "كريبتو", "Forex": "فوركس", "Metals": "معادن", "Oil & Gas": "بترول وغاز", "Indices": "مؤشرات", "Stocks": "أسهم", "Bonds": "سندات",
    "Options": "أوبشنز", "Meme coins": "عملات الميم", "Egypt (EGX)": "مصر (EGX)", "Saudi (Tadawul)": "السعودية (تداول)",
    "Spot": "سبوت", "Perp (swap)": "عقود دائمة (swap)", "Futures": "عقود آجلة",
    # scanner / tabs
    "Trade type": "نوع الصفقة", "No symbols match the current filter.": "مفيش رموز مطابقة للفلتر الحالي.",
    "Filters": "الفلاتر", "Timeframe": "الفريم", "Charts": "عدد الشارتات", "Side": "الاتجاه", "Match": "المطابقة", "Cross window": "نافذة التقاطع",
    "Trend stack": "ترتيب الترند", "Price vs EMA": "السعر مقابل EMA", "EMA vs EMA": "EMA مقابل EMA", "Pair": "الزوج", "Patterns": "الأنماط",
    "Strategies / signals (Elliott, SMC, ICT, Harmonic, VWAP ...)": "الاستراتيجيات / الإشارات (إليوت، SMC، ICT، هارمونيك، VWAP ...)",
    "Both": "الاتنين", "Buy only": "شراء بس", "Sell only": "بيع بس", "All selected": "كل المختار", "Any selected": "أي واحد من المختار",
    "above": "فوق", "below": "تحت", "crossed above": "قطع لفوق", "crossed below": "قطع لتحت",
    "Bullish (px>9>20>50)": "صاعد (السعر>9>20>50)", "Bearish (px<9<20<50)": "هابط (السعر<9<20<50)", "Above all EMAs": "فوق كل المتوسطات", "Below all EMAs": "تحت كل المتوسطات",
    "No symbols match the selected conditions right now.": "مفيش رموز مطابقة للشروط دي دلوقتي.",
    "Plain-language Arabic analysis of this setup (same as the Crypto tab)": "تحليل مبسط بالعربي للسيت اب ده (زي تاب الكريبتو)",
    "Scanner": "السكانر", "Scan timeframe": "فريم المسح", "Symbol": "الرمز", "Top chart": "الشارت اللي فوق", "Bottom chart": "الشارت اللي تحت",
    "Watchlist": "قائمة المتابعة", "Chart symbol": "رمز الشارت",
    "★ glowing = big resting order (blinks white when trades hit it). Level flash = just traded. Blue outline = size grew.":
        "★ منوّر = أمر كبير مستني (بيومض أبيض لما الصفقات تضربه). وميض المستوى = لسه متداول. إطار أزرق = الحجم زاد.",
    "**Time & Sales** &middot; Smart / Whale / Absorb": "**الصفقات اللحظية** &middot; ذكية / حوت / امتصاص",
    "**Limit Tracking** &middot; big limit orders placed / pulled / filled": "**متابعة الأوامر الكبيرة** &middot; اتحطت / اتشالت / اتنفذت",
    "Snapshot based (compares each refresh), so quick spoof-and-cancel inside one refresh is not seen. PULLED = vanished without trading.":
        "مبني على لقطات (بيقارن كل تحديث)، فالأوامر الوهمية اللي بتتحط وتتشال بسرعة جوه تحديث واحد مش بتبان. PULLED = اختفى من غير تنفيذ.",
    "Drag a title bar to move, drag the corner to resize, - minimise, square = maximise (double-click title too). Widgets with the same # in the title bar share one symbol. Layout is remembered in your browser. Data comes straight from OKX in your browser, no refresh needed.":
        "اسحب شريط العنوان عشان تحرّك، واسحب الركن عشان تكبّر، - تصغير، المربع = تكبير (أو دبل كليك على العنوان). الـ widgets اللي ليها نفس الرقم # بتشارك نفس الرمز. الترتيب بيتحفظ في المتصفح. البيانات بتيجي مباشرة من OKX ومن غير ريفرش.",
    # stocks tab
    "Cross-sector momentum (hedge-fund relative-strength ranking)": "الزخم بين القطاعات (ترتيب القوة النسبية لصناديق التحوط)", "Universe": "المجموعة",
    "US sectors (SPDR ETFs)": "قطاعات أمريكا (SPDR ETFs)", "Crypto majors": "العملات الكبيرة",
    "Ranking by the 12-1 month return divided by volatility (the latest month is skipped). LONG candidate = top third with a positive 12-1 return and price above SMA 200; AVOID = bottom third, negative and below SMA 200. Crypto trades 7 days a week, so its '12 months' are 252 daily bars (~8 calendar months). A ranking, not a forecast - not backtested in this project.":
        "الترتيب بعائد 12 شهر من غير آخر شهر مقسوم على التذبذب. مرشح شراء = التلت الأعلى بعائد موجب وفوق متوسط 200؛ ابعد = التلت الأسفل بعائد سالب وتحت متوسط 200. الكريبتو بيتداول 7 أيام، فالـ 12 شهر عنده = 252 شمعة يومي (حوالي 8 شهور). ترتيب مش توقع - متجربش في باك تست.",
    "US options chain (Cboe, ~15 min delayed)": "سلسلة الأوبشنز الأمريكية (Cboe، متأخرة حوالي 15 دقيقة)", "Underlying (stock / ETF / index)": "الأصل (سهم / ETF / مؤشر)",
    "Expiry": "تاريخ الانتهاء", "Underlying": "الأصل", "Put/Call volume": "Put/Call (الحجم)", "Put/Call open interest": "Put/Call (العقود المفتوحة)",
    "Max pain (this expiry)": "Max pain (للتاريخ ده)",
    "Source: Cboe's public delayed-quotes JSON (free, no key, ~15 min delayed, unofficial - it can change without notice). Indices: SPX, NDX, RUT, VIX. Max pain and put/call ratios describe positioning; they are not a forecast. Crypto options (BTC / ETH) stay live in the Workspace watchlist (OKX, category Options).":
        "المصدر: بيانات Cboe العامة المتأخرة (ببلاش، من غير مفتاح، متأخرة حوالي 15 دقيقة، مش رسمية وممكن تتغير). المؤشرات: SPX وNDX وRUT وVIX. Max pain ونسب Put/Call بتوصف المراكز، مش توقع. أوبشنز الكريبتو (BTC / ETH) لحظية في قائمة المتابعة (OKX، فئة Options).",
    "News sentiment + movers (Alpha Vantage)": "مزاج الأخبار + الأكثر حركة (Alpha Vantage)", "Tickers (optional, e.g. AAPL,NVDA)": "الرموز (اختياري، مثلاً AAPL,NVDA)",
    "Options flow (Unusual Whales) - ask-side, OTM, single-leg, premium >= $45k, vol > OI": "تدفق الأوبشنز (Unusual Whales) - جهة الطلب، OTM، رجل واحدة، بريميوم >= 45 ألف $، الحجم > العقود المفتوحة",
    "Refresh flow": "حدّث التدفق",
    # meme / performance
    "Meme coin / whale tracking (DEXScreener)": "متابعة عملات الميم والحيتان (DEXScreener)", "Search token (name or contract address)": "ابحث عن توكن (اسم أو عنوان العقد)",
    "No pairs found, or DEXScreener rate limit hit — try again shortly.": "مفيش أزواج، أو DEXScreener وقف الطلبات مؤقتاً — جرّب كمان شوية.",
    "Enter a token name or contract address above to search live DEXScreener pairs.": "اكتب اسم توكن أو عنوان عقد فوق عشان تدوّر في أزواج DEXScreener اللحظية.",
    "Performance report (QuantStats)": "تقرير الأداء (QuantStats)", "Risk per trade (% of account)": "المخاطرة في الصفقة (% من الحساب)",
    "Need at least 5 closed trades for meaningful statistics.": "محتاج 5 صفقات مقفولة على الأقل عشان الإحصائيات يبقى ليها معنى.",
    "Total return": "إجمالي العائد", "Trades": "الصفقات", "Max drawdown": "أقصى تراجع", "Win rate": "نسبة النجاح", "Stats source": "مصدر الإحصائيات",
    "QuantStats is not installed here, so only the built-in statistics are shown.": "QuantStats مش متسطّب هنا، فبيظهر الإحصائيات الأساسية بس.",
    "Upload the Workspace journal CSV": "ارفع ملف الجورنال CSV من مساحة العمل",
    "Trade type filter": "فلتر نوع الصفقة", "User name": "اسم المستخدم", "Password": "كلمة السر", "Log in": "دخول",
    "Wrong user name or password.": "اسم المستخدم أو كلمة السر غلط.", "Too many wrong tries - wait": "محاولات غلط كتير - استنى", "**Scanner**": "**السكانر**", "**Watchlist**": "**قائمة المتابعة**", "(change them in the top row)": "(غيّرهم من الصف اللي فوق)",
    "live OKX perpetual instruments (no MetaTrader needed). News and the economic calendar are in the header and the Workspace.":
        "عقود OKX الدائمة اللحظية (من غير MetaTrader). الأخبار والأجندة الاقتصادية في الهيدر وفي مساحة العمل.",
    "Journal CSV (columns: time, r)": "ملف الجورنال CSV (الأعمدة: time, r)",
    "The Workspace journal lives in your browser, so export it first: Journal widget > CSV button. Upload that file here. Returns = R x the % of the account you risk per trade. Evidence from the dashboard's own signals only - not a proven edge.":
        "الجورنال متخزن في المتصفح، فصدّره الأول: widget الجورنال > زرار CSV. وارفع الملف هنا. العائد = R × نسبة الحساب اللي بتخاطر بيها في الصفقة. دي أدلة من إشارات الداشبورد بس - مش ميزة مثبتة.",
    "Mr X - AI analyst": "مستر X - المحلل الذكي", "Symbol": "الرمز", "Timeframe": "الفريم", "New chat": "محادثة جديدة",
    "Ask Mr X about this chart, a setup, risk...": "اسأل مستر X عن الشارت ده، أو صفقة، أو المخاطرة...",
    "Answers are education, not financial advice. Mr X only sees a short summary of the chart (price, trend, RSI, ATR, range).": "الإجابات تعليمية مش نصيحة مالية. مستر X بيشوف ملخص قصير للشارت بس (السعر، الاتجاه، RSI، ATR، المدى).",
    "Mr X is thinking...": "مستر X بيفكر...", "Today's question limit is reached.": "خلصت أسئلة النهارده.", "No AI key in Secrets.": "مفيش مفتاح ذكاء في Secrets.",
    "Mr X could not answer": "مستر X معرفش يرد",
    "Add GEMINI_API_KEY (free) or ANTHROPIC_API_KEY in Streamlit Secrets to talk to Mr X.": "حط GEMINI_API_KEY (مجاني) أو ANTHROPIC_API_KEY في Secrets عشان تكلم مستر X.",
    "Material": "الخامة", "Auto (from the theme)": "تلقائي (من الثيم)", "None": "بدون", "Brushed steel": "ستيل مصقول", "Paper": "ورق", "Wood": "خشب", "Fabric": "قماش", "Glass": "زجاج", "Carbon fibre": "كاربون",
    "Theme": "الثيم", "Language": "اللغة", "Coming": "قريباً", "Classic": "كلاسيك",
    "Slots 3-7: send a picture and the theme gets built.": "الخانات من ٣ لـ ٧: ابعت صورة والثيم يتعمل.",
    "Theme and language (Alt+T / Alt+L)": "الثيم واللغة (Alt+T / Alt+L)",
    "Lab": "المعمل", "Playbook": "الدليل", "Stats": "الأداء", "AI": "الذكي", "Alerts": "التنبيهات", "Scanner": "السكانر", "Workspace": "الوورك سبيس"
}


# Languages offered in the top bar. To add one: put its code here and give L() its table (like the Arabic one above);
# until it has a table it is listed as "soon" and cannot be picked.
LANGS = {"en": ("English", "EN", True), "ar": ("العربية", "ع", True), "fr": ("Français", "FR", False), "es": ("Español", "ES", False),
         "tr": ("Türkçe", "TR", False), "ru": ("Русский", "RU", False), "zh": ("中文", "中", False)}


def lang() -> str:
    try:
        import streamlit as st
        return st.session_state.get("ws_lang", "en")
    except Exception:
        return "en"


def L(text: str) -> str:
    """Arabic when the language switch says 'ar', otherwise the English text unchanged."""
    return AR.get(text, text) if lang() == "ar" else text


RTL_CSS = """<style>
.block-container [data-testid="stMarkdownContainer"], .block-container [data-testid="stCaptionContainer"], .block-container [data-testid="stWidgetLabel"],
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"], section[data-testid="stSidebar"] [data-testid="stWidgetLabel"],
[data-testid="stExpander"] summary, [data-testid="stAlert"] { direction: rtl; text-align: right; }
.stTabs [data-baseweb="tab-list"] { direction: rtl; }
</style>"""
