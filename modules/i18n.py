"""Item 21: Arabic for the Streamlit side of the dashboard (the Workspace already has its own en / ar texts).
L("English text") returns the Arabic version when the header language switch (session key "ws_lang") is "ar", otherwise the
English text unchanged. A missing entry simply stays English - never a blank. Trading terms traders use as-is in Arabic
(RSI, EMA, VWAP, SMC, ICT, Put/Call, Sharpe ...) stay in Latin letters."""
from __future__ import annotations

AR = {
    # Technical Office v2 tabs / control room / work board / backtest / operations, Radar tab bar (2026-10-22)
    "Control room": "غرفة التحكم", "Work board": "لوحة المهام", "Backtest": "الباك تيست", "Operations": "التشغيل", "Lab results": "نتايج الـ lab",
    "Charts": "الشارتات", "Heat map": "الخريطة الحرارية", "live": "مباشر", "down": "واقف", "key set": "المفتاح موجود", "no key": "مفيش مفتاح",
    "Telegram": "تليجرام", "Blocked tasks": "مهام واقفة", "Nothing has passed the evidence gate yet": "لسه مفيش حاجة عدّت بوابة الدليل",
    "info": "معلومة", "degraded": "متدهور", "blocked": "واقف", "every signal is a suggestion, not evidence": "كل إشارة اقتراح، مش دليل",
    "Hyperliquid is not answering": "Hyperliquid مش بيرد", "gold / oil / index charts stop updating": "شارتات الذهب والنفط والمؤشرات هتقف",
    "Evidence gate": "بوابة الدليل", "n >= 100 · t > 3 · net > 0 · both halves positive, after 0.1R": "n ≥ 100 · t > 3 · صافي موجب · النصين موجبين، بعد 0.1R",
    "groups passed": "مجموعات عدّت", "Alerts": "التنبيهات", "Indicators": "المؤشرات", "symbols": "رمز", "planning estimate": "تقدير للتخطيط",
    "Tasks in review": "مهام في المراجعة", "waiting for Gemini / owner": "مستنية Gemini / المالك", "Open tasks": "مهام مفتوحة", "work board": "لوحة المهام",
    "Live vs backtest": "الحي مقابل الباك تيست", "after 30-50 live trades": "بعد 30–50 صفقة حية", "Max drawdown": "أقصى تراجع", "from the backtest engine": "من محرك الباك تيست",
    "System map": "خريطة المنظومة", "From data to decision to evidence; every node shows its state": "من الداتا للقرار للدليل، وكل عقدة بحالتها",
    "crypto · candles, book, trades": "كريبتو · شموع، دفتر، صفقات", "gold · oil · indices · FX": "ذهب · نفط · مؤشرات · فوركس", "macro data": "اقتصاد كلي",
    "News & calendar": "الأخبار والتقويم", "Grok watch every 6 h": "Grok كل 6 ساعات", "Detectors": "الكواشف", "OFF": "مقفولة",
    "Scanner & Radar": "السكانر والرادار", "confirmed first, then candidates": "المؤكد الأول، بعدين المرشح", "Order flow": "الأوردر فلو",
    "footprint · book · tape": "فوتبرنت · دفتر · شريط", "rules + engine, verdict on out-of-sample": "قواعد + محرك، الحكم على out-of-sample",
    "Strategy import": "استيراد استراتيجية", "text / video link -> rules": "نص / رابط فيديو ← قواعد", "Alerts · Telegram": "التنبيهات · تليجرام",
    "confirmed only, never orders": "المؤكد بس، مش أوامر", "Journal": "الـ Journal", "in the browser · CSV export": "في المتصفح · تصدير CSV",
    "Model inventory": "سجل النماذج", "gate verdict per strategy": "حكم البوابة لكل استراتيجية", "Tools": "الأدوات",
    "strategy + symbol + timeframe, verdict on out-of-sample": "استراتيجية + رمز + فريم، الحكم على out-of-sample", "tab: Backtest": "تبويب: الباك تيست",
    "Strategy builder": "بناء الاستراتيجية", "indicator + condition + value, AND / OR, JSON": "مؤشر + شرط + قيمة، AND / OR، JSON",
    "text or link -> rules + assumptions": "نص أو رابط ← قواعد + افتراضات", "waiting: ChatGPT template": "مستني قالب ChatGPT",
    "Scanner control": "التحكم في السكانر", "filters, timeframe, confirmed / candidate": "فلاتر، فريم، مؤكد / مرشح", "Radar page": "صفحة الرادار",
    "Trade card": "كارت الصفقة", "entry, stop, target and the detector's evidence": "دخول، وقف، هدف، ودليل الكاشف", "task 17, after the ranking": "بند 17، بعد الترتيب",
    "alerts for confirmed setups only": "تنبيهات للمؤكد بس", "workflow every 30 min": "workflow كل 30 دقيقة", "Recording": "التسجيل",
    "snapshot / record the chart and the workspace": "لقطة / تسجيل للشارت والمساحة", "Workspace toolbar": "شريط أدوات الـ Workspace",
    "KPIs": "المؤشرات الرئيسية", "net R, profit factor, drawdown, t": "صافي R، Profit factor، تراجع، t", "Stats page": "صفحة Stats",
    "Area": "القسم", "All": "الكل", "WBS": "WBS", "Task": "المهمة", "Owner": "المسؤول", "Status": "الحالة", "Gate": "البوابة", "Next step": "الخطوة الجاية",
    "Work board updated": "لوحة المهام اتحدثت", "every change is also written in the meeting room": "كل تغيير بيتكتب كمان في المحضر",
    "done": "خلص", "running": "شغال", "decided": "اتقرر", "ready": "جاهز", "review": "مراجعة", "in progress": "جاري", "open": "مفتوح", "waiting": "مستني", "parked": "مؤجل",
    "Rules are kept for this session only (owner decision 2026-10-22). Small runs here; big runs go to GitHub Actions with the owner's approval. No orders, ever.":
        "القواعد بتتحفظ في الجلسة بس (قرار المالك 2026-10-22). التشغيل الصغير هنا، والكبير على GitHub Actions بموافقة المالك. مفيش أوامر أبداً.",
    "Symbol": "الرمز", "Logic": "المنطق", "Name": "الاسم", "Rules": "عدد القواعد", "Indicator": "المؤشر", "Period": "الفترة", "Condition": "الشرط",
    "Compare with": "قارن بـ", "number": "رقم", "Value": "القيمة", "Save rule": "احفظ القاعدة", "Saved for this session": "اتحفظت للجلسة دي",
    "Run backtest": "شغّل الباك تيست", "Saved this session": "المحفوظ في الجلسة", "Out-of-sample trades": "صفقات out-of-sample", "Win rate": "نسبة الفوز",
    "Verdict": "الحكم", "In-sample (info)": "In-sample (معلومة)", "Split frozen before any trade": "التقسيم اتثبت قبل أي صفقة", "candles": "شمعة",
    "not evidence": "مش دليل", "passes gate": "عدّى البوابة", "not yet": "لسه",
    "Workflow": "الـ Workflow", "File": "الملف", "Schedule (UTC cron)": "الجدول (UTC cron)", "Manual run": "تشغيل يدوي", "Repo writes": "بيكتب في الريبو",
    "writes to the repo": "بيكتب في الريبو",
    "Protecting main is on hold until the workflows that push to main open a pull request instead (owner rule: protect only if nothing breaks).":
        "حماية main متأجلة لحد ما الـ workflows اللي بتدفع على main تفتح PR بدل كده (قاعدة المالك: نحمي بس لو مفيش حاجة هتبوظ).",
    # Technical Office control room (2026-10-22)
    "Passed the evidence gate": "عدّى بوابة الدليل", "Detectors in the lab": "كواشف في الـ lab", "OFF (no longer decide a trade)": "مقفولة (ماتقررش صفقة)",
    "Best net avg R (n >= 100)": "أفضل صافي R (n ≥ 100)", "Cost per trade": "تكلفة الصفقة", "Last lab run": "آخر تشغيل lab",
    "n >= 100, t > 3, net > 0 and both halves positive after 0.1R costs": "n ≥ 100، t > 3، صافي موجب، والنصين موجبين بعد تكلفة 0.1R",
    "Scalp": "سكالب", "Day trade": "داي تريد", "Swing": "سوينج", "Position": "بوزيشن", "Style": "النوع", "Lab timeframes": "فريمات الـ lab",
    "Strongest detector (n >= 100)": "أقوى كاشف (n ≥ 100)", "net avg R": "صافي R", "vs random": "مقابل العشوائي",
    "The Playbook summary is older than the last lab run": "ملخص الـ Playbook أقدم من آخر تشغيل lab",
    "Nothing has passed the evidence gate yet: every signal is a suggestion, not evidence.": "لسه مفيش حاجة عدّت بوابة الدليل: كل إشارة اقتراح، مش دليل.",
    "Educational, not investment advice. Source: data/strategy_lab.json (weekly lab).": "تعليمي، مش توصية استثمارية. المصدر: data/strategy_lab.json (الـ lab الأسبوعي).",
    # Radar KPI strip (2026-10-22)
    "Matched": "مطابق", "Confirmed": "مؤكد", "Candidates": "مرشح", "Conditions chosen": "الشروط المختارة",
    "Every chosen condition holds on this chart": "كل الشروط المختارة متحققة على الشارت ده", "Some chosen conditions hold": "بعض الشروط المختارة متحققة",
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
    "Filters": "الفلاتر", "Hide filters": "إخفاء الفلاتر", "Timeframe": "الفريم", "Charts": "عدد الشارتات", "Side": "الاتجاه", "Match": "المطابقة", "Cross window": "نافذة التقاطع",
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
    "Lab": "المعمل", "Technical Office": "المكتب الفني", "Radar": "الرادار", "Playbook": "الدليل", "Stats": "الأداء", "AI": "الذكي", "Alerts": "التنبيهات", "Scanner": "السكانر", "Workspace": "الوورك سبيس"
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


# KPI strip (Stats page, modules/kpi.py)
AR.update({
    "Evidence": "الدليل", "passes gate": "عدّى البوابة", "not yet": "لسه مش دليل", "not evidence": "مش دليل",
    "needs": "محتاج", "avg R in both halves": "متوسط R في النصين", "Trades": "الصفقات", "Win rate": "نسبة النجاح",
    "Expectancy (R)": "متوسط الربح بالـ R", "Max drawdown (R)": "أقصى تراجع (R)", "After costs (R)": "بعد التكاليف (R)",
    "By symbol": "حسب العملة", "By strategy": "حسب الاستراتيجية",
    "Costs = {c} R per trade (planning estimate, not measured). Grey = under {n} trades, not evidence.": "التكاليف = {c} R للصفقة (تقدير تخطيط، مش متقاس). الرمادي = أقل من {n} صفقة، مش دليل.",
})
# Market map (Radar page, modules/market_map.py)
AR.update({
    "Market map": "خريطة السوق", "markets": "الأسواق", "up": "صاعد", "down": "هابط", "median change": "متوسط التغير",
    "Market map: Hyperliquid did not answer": "خريطة السوق: Hyperliquid ما ردش",
    "Market map: no markets with a reference price right now.": "خريطة السوق: مفيش أسواق بسعر مرجعي دلوقتي.",
    "Tile colour = change vs the previous day; tile size = 24h volume (no market cap is available for these markets). Breadth and strength describe the move, they do not predict it.":
        "لون المربع = التغير عن اليوم اللي فات؛ حجم المربع = حجم 24 ساعة (مفيش قيمة سوقية متاحة للأسواق دي). الاتساع والقوة بيوصفوا الحركة، ومابيتنبؤوش بيها.",
    "Class": "الفئة", "Markets": "الأسواق", "Avg change %": "متوسط التغير %", "Share up": "نسبة الصاعد",
})


def L(text: str) -> str:
    """Arabic when the language switch says 'ar', otherwise the English text unchanged."""
    return AR.get(text, text) if lang() == "ar" else text


RTL_CSS = """<style>
.block-container [data-testid="stMarkdownContainer"], .block-container [data-testid="stCaptionContainer"], .block-container [data-testid="stWidgetLabel"],
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"], section[data-testid="stSidebar"] [data-testid="stWidgetLabel"],
[data-testid="stExpander"] summary, [data-testid="stAlert"] { direction: rtl; text-align: right; }
.stTabs [data-baseweb="tab-list"] { direction: rtl; }
</style>"""
