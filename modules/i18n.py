"""Item 21: Arabic for the Streamlit side of the dashboard (the Workspace already has its own en / ar texts).
L("English text") returns the Arabic version when the header language switch (session key "ws_lang") is "ar", otherwise the
English text unchanged. A missing entry simply stays English - never a blank. Trading terms traders use as-is in Arabic
(RSI, EMA, VWAP, SMC, ICT, Put/Call, Sharpe ...) stay in Latin letters."""
from __future__ import annotations

AR = {
    "Price": "السعر", "Change %": "التغير %", "20-bar %": "تغير 20 شمعة %", "Volume ×avg": "الفوليوم ×المتوسط", "Signals": "الإشارات", "Which": "أنهي إشارات",
    "Chart grid": "الشارتات",
    # Radar strip (design board 'Radar', 2026-10-22)
    "Market state (daily)": "حالة السوق (اليومي)", "Share of the Radar symbols above / below their daily EMA 20 and 50": "نسبة رموز الرادار فوق / تحت EMA 20 و50 على اليومي",
    "trend up": "ترند صاعد", "trend down": "ترند هابط", "range / mixed": "رينج / مختلط", "Strong news within 1 h": "خبر قوي خلال ساعة",
    "yes": "نعم", "no": "لا", "High-impact events from the economic calendar in the next hour; the Playbook says no entry +-1 h around them":
        "أحداث عالية التأثير من التقويم الاقتصادي في الساعة الجاية؛ الـ Playbook بيقول مفيش دخول ±1 ساعة حواليها",
    "Data age": "حداثة الداتا", "conditions": "شروط", "Detector evidence": "دليل الكاشف",
    # Radar views: Performance / Signal list / Correlation (2026-10-22)
    "Performance": "الأداء", "Signal list": "قائمة الإشارات", "Correlation": "الارتباط", "No candles yet.": "لسه مفيش شموع.",
    "Sort by": "رتّب حسب", "Symbols": "الرموز", "Up": "صاعد", "Down": "هابط", "Median": "الوسيط", "Volatility 24 h %": "التذبذب 24 ساعة %",
    "Change % by period (heat map)": "التغير % حسب المدة (خريطة حرارية)",
    "1h candles from the same source as the charts. Educational, not investment advice.": "شموع 1H من نفس مصدر الشارتات. تعليمي، مش توصية استثمارية.",
    "Need at least two symbols with candles.": "محتاج رمزين على الأقل فيهم شموع.",
    "Move together (corr >= 0.8): treat as one position": "بيتحركوا مع بعض (ارتباط ≥ 0.8): اعتبرهم صفقة واحدة",
    "Lowest correlation (diversify / hedge)": "أقل ارتباط (تنويع / تحوّط)",
    "Pearson correlation of 1h returns, last 260 candles. Correlation changes over time; it is not a forecast.":
        "ارتباط بيرسون لعوائد 1H، آخر 260 شمعة. الارتباط بيتغير مع الوقت، ومش توقع.",
    "Strategy": "استراتيجية", "Pattern": "نمط", "No signals on this timeframe right now.": "مفيش إشارات على الفريم ده دلوقتي.",
    "Signals live": "إشارات شغالة", "Symbols scanned": "رموز اتفحصت", "With positive lab net R": "صافي المعمل موجب",
    "Signal": "الإشارة", "Kind": "النوع", "Count": "العدد", "Lab net R": "صافي R في المعمل", "Lab n": "n في المعمل",
    "Lab net R = the weekly lab's average R after 0.1R costs for that detector on the nearest lab timeframe. A signal is a suggestion, not evidence, until it passes the gate.":
        "صافي R في المعمل = متوسط R الأسبوعي بعد تكلفة 0.1R للكاشف ده على أقرب فريم في المعمل. الإشارة اقتراح، مش دليل، لحد ما تعدّي البوابة.",
    # Radar trade card (task 17, 2026-10-22)
    "Trade card: no clear direction on this timeframe": "كارت الصفقة: مفيش اتجاه واضح على الفريم ده", "Buy": "شراء", "Sell": "بيع",
    "entry": "دخول", "stop": "وقف", "targets": "أهداف", "Against the side filter": "عكس فلتر الاتجاه المختار",
    "Suggestion from the rules, not an order; size by your risk per trade.": "اقتراح من القواعد، مش أمر؛ الحجم حسب مخاطرتك في الصفقة.",
    "signals": "إشارات", "hover the chart for the explanation": "قف بالماوس على الشارت للشرح",
    # Info strip (item 44) + Technical Office: Scanner control / Detector analysis (2026-10-22)
    "Info strip": "شريط المعلومات", "The thin line under the header: educational note, data sources, last lab run": "السطر الرفيع تحت الهيدر: ملاحظة تعليمي، ومصادر الداتا، وآخر تشغيل للمعمل",
    "Educational, not investment advice": "تعليمي، مش توصية استثمارية", "No automatic orders": "مفيش تنفيذ أوامر تلقائي",
    "Detector analysis": "تحليل الكاشف", "Preset by trading style": "إعداد جاهز حسب نوع التداول", "Manual": "يدوي", "Day": "داي تريد",
    "no lab row": "مش في المعمل", "What the lab says about these detectors on this timeframe": "المعمل بيقول إيه عن الكواشف دي على الفريم ده",
    "Lab timeframe": "فريم المعمل", "Negative after costs on the lab's numbers:": "سالب بعد التكلفة حسب أرقام المعمل:",
    "Apply to the Radar": "طبّق على الرادار", "Saved for this session. Open the Radar page to see it.": "اتحفظ للجلسة دي. افتح صفحة الرادار تشوفه.",
    "Radar now": "الرادار دلوقتي", "charts": "شارت", "All timeframes": "كل الفريمات", "Best timeframe": "أحسن فريم",
    "best timeframe minus random entries": "أحسن فريم ناقص الدخول العشوائي", "n >= 300 and avg R <= -0.06": "n ≥ 300 ومتوسط R ≤ ‎-0.06",
    "n under 100 on the best timeframe": "n أقل من 100 على أحسن فريم", "needs t > 3 and both halves positive": "محتاج t > 3 والنصين موجبين",
    "Trading styles": "أنواع التداول", "from the timeframes it was tested on": "من الفريمات اللي اتختبر عليها",
    "All numbers from the weekly lab file; net = avg R - 0.1R. Educational, not investment advice.": "كل الأرقام من ملف المعمل الأسبوعي؛ الصافي = متوسط R − 0.1R. تعليمي، مش توصية استثمارية.",
    # Technical Office: Strategy map (2026-10-22)
    "Strategy map": "خريطة الاستراتيجيات", "Clusters: what repeats what": "العناقيد: مين بيكرر مين", "Cluster": "العنقود", "Measures": "بيقيس",
    "Members": "الأعضاء", "Strongest member (lab, n >= 100)": "أقوى عضو (المعمل، n ≥ 100)", "Redundancy rule": "قاعدة التكرار",
    "Detectors that fire together (lab)": "كواشف بتظهر مع بعض (المعمل)", "Bars together": "شموع مشتركة", "Same direction": "نفس الاتجاه",
    "High same-direction share + many shared bars = the pair adds little to each other. About 50% = the pair is noise together.":
        "نسبة اتفاق عالية + شموع مشتركة كتير = الاتنين مش بيضيفوا لبعض. حوالي 50% = مع بعض ضوضاء.",
    "Does stacking more families help? (lab)": "هل زيادة عدد المدارس المتفقة بتفيد؟ (المعمل)", "Agreeing families": "مدارس متفقة",
    "Rows without opposing signals. More agreeing families gave no clear improvement (4+ was the worst row), and every row with n >= 100 is below zero after costs.":
        "الصفوف من غير إشارات معاكسة. زيادة المدارس المتفقة ماحسّنتش النتيجة بوضوح (4+ كانت أسوأ صف)، وكل صف n ≥ 100 تحت الصفر بعد التكلفة.",
    "Strategies as parts by role": "الاستراتيجيات كأجزاء حسب الوظيفة", "Strategy": "الاستراتيجية", "Role": "الوظيفة", "Part": "الجزء",
    "What it does here": "بيعمل إيه هنا", "Lab (best timeframe)": "المعمل (أحسن فريم)", "Try it on real candles": "جرّبها على شموع حقيقية",
    "Exploratory run: every variant you try counts as another trial. A real verdict needs a frozen out-of-sample window recorded in the meeting room before the run. Exit here = the engine's standard ATR stop and 1.5R target.":
        "تجربة استكشافية: كل نسخة بتجربها بتتحسب محاولة. الحكم الحقيقي محتاج نافذة out-of-sample مثبتة ومسجلة في المحضر قبل التشغيل. الخروج هنا = وقف ATR وهدف 1.5R بتوع المحرك.",
    "below the cost": "تحت التكلفة", "families": "مدارس",
    "IV rank (1 year)": "IV rank (سنة)", "min": "أقل", "max": "أعلى", "percentile": "المئين", "DVOL history not available": "تاريخ DVOL مش متاح",
    "The lab gives a t-stat to": "المعمل بيدّي t لـ", "detector rows (and": "صف كاشف (و", "chain rows): a row without t cannot pass the gate": "صف سلسلة): الصف من غير t ما يقدرش يعدّي البوابة",
    "Rows with a t-stat": "صفوف فيها t", "detector x timeframe; the gate needs t > 3": "كاشف × فريم؛ البوابة محتاجة t > 3",
    "Holdout tests run": "اختبارات مجمدة اتشغلت", "frozen holdouts on older candles": "اختبارات مجمدة على شموع أقدم",
    "Frozen holdout on older candles (1d)": "اختبار مجمّد على شموع أقدم (يومي)", "Holdout": "الاختبار المجمّد", "symbols": "رموز", "signals": "إشارة", "gross": "إجمالي",
    "Random entries": "دخول عشوائي", "gross avg R of random direction on the same bars": "متوسط R الإجمالي لاتجاه عشوائي على نفس الشموع", "vs random; the bar is 3": "مقابل العشوائي؛ الحد 3",
    "Halves": "النصين", "net, first / second half": "الصافي، النصف الأول / التاني", "rule frozen before the run": "القاعدة اتجمدت قبل التشغيل",
    "The agent needs a ChatGPT key (OPENAI_API_KEY) or the free Gemini key (GEMINI_API_KEY) in Streamlit secrets. Until then, build the rules by hand in Technical Office > Backtest.":
        "الوكيل محتاج مفتاح ChatGPT (OPENAI_API_KEY) أو مفتاح Gemini المجاني (GEMINI_API_KEY) في Secrets بتاعة Streamlit. لحد وقتها ابني القواعد بإيدك في المكتب الفني ← الباك تيست.",
    "Answered by": "الإجابة من",
    "Gaps: where the dashboard is thin": "الفجوات: فين اللوحة ضعيفة", "Gap": "الفجوة",
    "Taxonomy from practitioner and academic sources (labelled per strategy); numbers from data/strategy_lab.json. Educational, not investment advice.":
        "التصنيف من مصادر متداولين وأكاديمية (مكتوب مستوى الدليل لكل استراتيجية)؛ الأرقام من data/strategy_lab.json. تعليمي، مش توصية استثمارية.",
    # Options desk (2026-10-22)
    "Options desk": "مكتب الأوبشنز", "No option data.": "مفيش بيانات أوبشنز.", "Spot (index)": "السعر (المؤشر)", "Open interest": "المراكز المفتوحة (OI)",
    "Put / call (open interest)": "Put / Call (بالـ OI)", "all expiries": "كل الاستحقاقات", "Volume (24 h)": "الحجم (24 ساعة)", "Nearest expiry": "أقرب استحقاق",
    "days": "يوم", "ATM IV, nearest": "IV عند السعر، الأقرب", "annualised": "سنوي", "Days": "الأيام", "Max pain": "Max pain",
    "Skew ±10% (put IV - call IV)": "السكيو ±10% (IV البوت − IV الكول)", "Biggest strikes": "أكبر الـ strikes", "IV term structure": "هيكل الـ IV حسب المدة",
    "Strike": "الـ Strike", "Gold line = spot, purple dotted = max pain for this expiry.": "الخط الذهبي = السعر، البنفسجي المنقط = max pain للاستحقاق ده.",
    "The open interest and volume do not say if a trade opened or closed a position, or whether it was a hedge or a bet; put/call and walls are context. IV rank uses Deribit's DVOL daily history. Free Deribit data, about 2 minutes old. Educational, not investment advice.":
        "الـ OI والحجم مابيقولوش الصفقة فتحت ولا قفلت مركز، ولا كانت هيدج ولا رهان؛ فالـ put/call والـ walls سياق بس. الـ IV rank من تاريخ DVOL اليومي بتاع Deribit. بيانات Deribit مجانية، متأخرة حوالي دقيقتين. تعليمي، مش توصية استثمارية.",
    # Flow manual (2026-10-22)
    "Flow manual": "مانيوال الأوردر فلو", "Tools we have and their limits": "الأدوات اللي عندنا وحدودها", "Tool": "الأداة", "Shows": "بتبين", "Where": "فين", "Data": "الداتا", "Limits": "الحدود",
    "Methods: how to read, how to use, where it breaks": "الطرق: إزاي تقرأ، إزاي تستخدم، بتفشل فين", "Daily routine": "الروتين اليومي", "Step": "الخطوة", "What to do": "تعمل إيه",
    "Forward test: how a flow signal earns trust": "الاختبار الأمامي: إزاي الإشارة تكسب ثقة", "What is still missing": "اللي لسه ناقص",
    "Research sources are named per method (OPENED = read in full, otherwise a search snippet or background knowledge). Educational, not investment advice.":
        "مصادر البحث مكتوبة لكل طريقة (OPENED = اتقرأت كاملة، غير كده مقتطف بحث أو معرفة عامة). تعليمي، مش توصية استثمارية.",
    # Flow lab (2026-10-22)
    "Flow lab": "معمل الأوردر فلو", "Flow log (.jsonl)": "سجل الأوردر فلو (.jsonl)", "Cost per trade (bps)": "تكلفة الصفقة (نقطة أساس)",
    "Taker fee both ways + half spread + slippage; a planning number. 10 bps = 0.10%": "رسوم تيكر للدخول والخروج + نص السبريد + الانزلاق؛ رقم تخطيط. 10 نقط = 0.10%",
    "Collect now (seconds)": "اجمع دلوقتي (ثواني)", "Collect BTC / ETH / SOL now": "اجمع BTC / ETH / SOL دلوقتي", "Collecting from OKX ...": "بيجمع من OKX ...",
    "rows added": "صف اتضاف", "No log yet. Collect from the button above, or run: python modules/flow_log.py collect BTC-USDT,ETH-USDT,SOL-USDT 3600 2":
        "لسه مفيش سجل. اجمع من الزرار فوق، أو شغّل: python modules/flow_log.py collect BTC-USDT,ETH-USDT,SOL-USDT 3600 2",
    "Log": "السجل", "Rows": "الصفوف", "Hours covered": "الساعات المغطاة", "a few hours is a pipeline test, not evidence": "كام ساعة = اختبار للمسار، مش دليل",
    "Rules x horizons tried": "قواعد × آفاق اتجربت", "every variant counts as a trial; t > 3 is the bar": "كل نسخة بتتحسب محاولة؛ والحد t > 3",
    "Passed the gate": "عدّت البوابة", "n >= 100, t > 3, both halves positive, after cost": "n ≥ 100، t > 3، والنصين موجبين، بعد التكلفة",
    "Not enough rows for any horizon yet.": "الصفوف لسه مش كفاية لأي أفق.", "Rule": "القاعدة", "Horizon (s)": "الأفق (ث)", "gross bps": "الإجمالي bps", "net bps": "الصافي bps",
    "random-sign control": "ضابط العلامة العشوائية", "first half": "النصف الأول", "second half": "النصف التاني",
    "Rules are frozen in modules/flow_log.py (RULES): imb = book imbalance, ofi = top-of-book order-flow imbalance, cvd = taker buy minus sell. Poll cadence limits what is seen. Educational, not investment advice.":
        "القواعد مجمدة في modules/flow_log.py (RULES): imb = توازن الدفتر، ofi = عدم توازن تدفق الأوامر عند أفضل سعر، cvd = شراء المبادر ناقص البيع. فترة التسجيل بتحدد اللي بنشوفه. تعليمي، مش توصية استثمارية.",
    # Stats page (2026-10-22)
    "Lab evidence": "أدلة المعمل", "My journal": "سجل صفقاتي", "No lab file yet (data/strategy_lab.json).": "لسه مفيش ملف معمل (data/strategy_lab.json).",
    "weekly": "أسبوعي", "All detectors, avg R": "كل الكواشف، متوسط R",
    "Strongest detector x timeframe (n >= 100), by net avg R": "أقوى كاشف × فريم (n ≥ 100)، مرتبة بصافي متوسط R",
    "Detector": "الكاشف", "School": "المدرسة", "passed": "عدّى", "no t yet": "مفيش t لسه",
    "vs random = avg R minus the random-entry baseline on the same bars. 'no t yet' = the lab has not measured the t-stat for this row, so it cannot pass the gate.":
        "مقابل العشوائي = متوسط R ناقص متوسط الدخول العشوائي على نفس الشموع. «مفيش t لسه» = المعمل ماقاسش قيمة t للصف ده، فمينفعش يعدّي البوابة.",
    "Journal in R": "السجل بوحدة R", "closed": "مقفولة", "Profit factor": "معامل الربح", "gains / losses": "المكاسب ÷ الخسائر",
    "from the equity peak": "من أعلى قمة للرصيد", "evidence needs t > 3 and n >= 100": "الدليل محتاج t > 3 و n ≥ 100",
    "your avg R minus the lab's": "متوسطك ناقص متوسط المعمل", "Total": "الإجمالي",
    "Fewer than 30 trades: the live vs backtest comparison is noise for now.": "أقل من 30 صفقة: المقارنة مع الباك تيست لسه ضوضاء.",
    "Levels / breakouts": "المستويات / الاختراقات", "Momentum / divergence": "الزخم / الدايفرجنس", "Fibonacci": "فيبوناتشي", "Liquidity": "السيولة",
    "Trend (hedge fund)": "الترند (صناديق التحوط)", "Time (sessions)": "الوقت (الجلسات)", "Elliott wave": "موجات إليوت", "SMC / ICT": "SMC / ICT",
    "Trend (MA)": "الترند (المتوسطات)", "Intermarket (SMT)": "بين الأسواق (SMT)",
    # work board areas, workflow names, lab caption (2026-10-22)
    "Order flow": "الأوردر فلو", "Radar": "الرادار", "Technical Office": "المكتب الفني", "Workspace": "الـ Workspace", "Strategies": "الاستراتيجيات",
    "Playbook": "الـ Playbook", "Stats": "الإحصائيات", "AI": "الذكاء الاصطناعي", "Alerts": "التنبيهات", "Research": "البحث", "Operations": "التشغيل",
    "Security": "الأمان", "Data": "الداتا", "Priority": "الأولوية",
    "Activity summary": "ملخص النشاط", "Real-candle backtests (manual)": "باك تيست على شموع حقيقية (يدوي)", "Claude Code": "Claude Code",
    "Gemini review": "مراجعة Gemini", "Grok digest": "ملخص Grok", "Anthropic key check": "فحص مفتاح Anthropic", "Provider check": "فحص المزودين",
    "School review": "مراجعة المدارس", "Strategy lab": "معمل الاستراتيجيات", "Telegram alerts": "تنبيهات تليجرام",
    "Real OKX / Hyperliquid candles, run weekly by GitHub Actions, every result against a random-direction baseline. Evidence bar: n >= 100 and t > 3. Under 30 trades = not evidence. Judge by the net avg R column (0.1R costs per trade taken off); avg R alone has no costs.":
        "شموع حقيقية من OKX و Hyperliquid، بتشتغل كل أسبوع على GitHub Actions، وكل نتيجة مقارنة باتجاه عشوائي. شرط الدليل: n ≥ 100 و t > 3. أقل من 30 صفقة = مش دليل. احكم بعمود صافي R (بعد خصم 0.1R تكلفة لكل صفقة)؛ متوسط R لوحده من غير تكلفة.",
    # Playbook / Alerts / AI pages (2026-10-22)
    "By trading style": "حسب نوع التداول", "Schools": "المدارس", "Rules & timing": "القواعد والتوقيت", "Full document": "الوثيقة كاملة",
    "Setup": "الإعداد", "Entry": "الدخول", "net": "صافي", "Holding time": "مدة الصفقة", "Principles": "المبادئ", "Goal": "الهدف", "no lab data": "مفيش داتا lab",
    "minutes, closed in the same session": "دقايق، بيتقفل في نفس الجلسة", "hours, closed before the day ends": "ساعات، بيتقفل قبل آخر اليوم",
    "days to weeks": "أيام لأسابيع", "weeks to months": "أسابيع لشهور",
    "paused until evidence": "موقوف لحد الدليل", "candidate for testing": "مرشح للاختبار", "first backtest": "أول باك تيست", "needs more symbols": "محتاج رموز أكتر",
    "session liquidity (Judas, sweep, CRT on the 1H / 4H candle), only inside the kill zones, stop behind the sweep, target >= 2R because of costs":
        "سيولة الجلسة (Judas، Sweep، CRT على شمعة 1H / 4H)، في الـ Kill Zones بس، الوقف ورا الـ sweep، الهدف ≥ 2R عشان التكلفة",
    "session AMD, CISD after a sweep, RSI divergence for timing, no entry +-1 h around a strong news event":
        "AMD الجلسة، CISD بعد sweep، دايفرجنس RSI للتوقيت، مفيش دخول ±1 ساعة حوالين خبر قوي",
    "daily levels and liquidity lines, break of a daily level, MACD divergence on the daily, stop 1.5 ATR, size by volatility":
        "مستويات اليومي وخطوط السيولة، اختراق مستوى يومي، دايفرجنس MACD على اليومي، وقف 1.5 ATR، الحجم بالتقلب",
    "time-series momentum (the strongest published evidence), wide stop, small size by volatility, spread over markets":
        "ترند الزمن (أقوى دليل منشور)، وقف واسع، حجم صغير بالتقلب، تنويع على الأسواق",
    "100 forward trades on 5m inside the kill zones with net >= +0.05R before any scalp alert": "100 صفقة forward على 5m في الـ Kill Zones بصافي ≥ +0.05R قبل أي تنبيه سكالب",
    "grade A+++ (5 context layers) passes t > 3 with both halves positive after costs within 4 weeks": "درجة A+++ (5 طبقات سياق) تعدّي t > 3 والنصين موجبين بعد التكلفة خلال 4 أسابيع",
    "liqline 1d (the only daily detector with n >= 100) gets the first frozen out-of-sample backtest; verdict within a week": "liqline 1d (الكاشف اليومي الوحيد بـ n ≥ 100) ياخد أول باك تيست بنافذة مثبتة؛ الحكم خلال أسبوع",
    "add symbols until n >= 100 and compare with the random baseline before any verdict": "نزود الرموز لحد n ≥ 100 ونقارن بالعشوائي قبل أي حكم",
    "Timeframes step by about 4-6x (trend from the higher one, setup from the middle, entry from the lower). Numbers: weekly lab, net = avg R - 0.1R costs. Educational, not investment advice.":
        "الفريمات بنسبة 4–6 مرات (الاتجاه من الأكبر، الإعداد من النص، الدخول من الأصغر). الأرقام من الـ lab الأسبوعي، والصافي = متوسط R − 0.1R. تعليمي، مش توصية.",
    "Rules every strategy must pass": "القواعد اللي لازم أي استراتيجية تعدّيها", "both halves positive": "النصين موجبين",
    "Timing from the lab (UTC session and weekday, every detector pooled)": "التوقيت من الـ lab (الجلسة بتوقيت UTC واليوم، كل الكواشف مع بعض)",
    "Sources": "المصادر", "Radar alerts (task 17)": "تنبيهات الرادار (بند 17)", "Telegram workflow": "workflow تليجرام", "Dashboard banners": "تنبيهات الداشبورد",
    "on": "شغال", "off": "مقفول", "1m alerts": "تنبيهات 1m", "Alert sources": "مصادر التنبيهات", "Scanner alerts (Workspace)": "تنبيهات السكانر (الـ Workspace)",
    "strong setups ranked by evidence score": "الإعدادات القوية مرتبة بدرجة الدليل", "on: banners + sound": "شغال: تنبيه + صوت",
    "Telegram (sidebar)": "تليجرام (الشريط الجانبي)", "top alerts while the dashboard is open": "أقوى التنبيهات والداشبورد مفتوح",
    "needs TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID": "محتاج TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID", "Telegram (GitHub Actions)": "تليجرام (GitHub Actions)",
    "runs without the dashboard open": "بيشتغل والداشبورد مقفول", "every 30 min": "كل 30 دقيقة", "missing": "مش موجود",
    "switched off: -147R of -150R in the journal": "اتقفلت: −147R من −150R في الـ journal", "Radar confirmed setups": "إعدادات الرادار المؤكدة",
    "every chosen condition holds, with entry / stop": "كل الشروط متحققة، بالدخول والوقف", "Order-flow sync alerts": "تنبيهات تزامن الأوردر فلو",
    "book + tape agree with the setup": "الدفتر والشريط متفقين مع الإعداد", "waiting for the order-flow sync fix": "مستني إصلاح التزامن",
    "News alarm": "إنذار الأخبار", "strong news event: blinking light, short Arabic summary, source": "خبر قوي: لمبة وامضة، ملخص عربي، المصدر",
    "chat item 24.1, open": "بند الشات 24.1، مفتوح", "Paper-trading bot": "بوت تداول ورقي", "follows only rules that passed the lab, own track record": "بيتبع القواعد اللي عدّت الـ lab بس، وله سجله",
    "planned, never real orders": "مخطط، ومفيش أوامر حقيقية أبداً",
    "Telegram alerts go out two ways: from the sidebar while the dashboard is open, and from the GitHub Actions workflow every 30 minutes without it.":
        "تنبيهات تليجرام بتطلع بطريقتين: من الشريط الجانبي والداشبورد مفتوح، ومن workflow على GitHub Actions كل 30 دقيقة من غيره.",
    "Setting": "الإعداد", "Where": "المكان", "Bot token and chat id": "توكن البوت والـ chat id", "Schedule": "الجدول",
    "Timeframes / top / minimum quality": "الفريمات / العدد / أقل جودة", "Already-sent memory": "ذاكرة اللي اتبعت", "no repeats": "مفيش تكرار",
    "Use the sidebar > Telegram alerts > Send test message to check the link. The keys never go into the code or the chat.": "استخدم الشريط الجانبي ← تنبيهات تليجرام ← رسالة تجربة. المفاتيح مابتتكتبش في الكود ولا الشات.",
    "Field": "الحقل", "Source": "المصدر", "Symbol, timeframe, strategy": "الرمز، الفريم، الاستراتيجية", "Entry / stop / target": "الدخول / الوقف / الهدف",
    "existing scanner rules": "قواعد السكانر الموجودة", "Evidence": "الدليل", "Invalidation": "الإبطال", "stop level": "مستوى الوقف", "confirmed only": "المؤكد بس",
    "Educational, not investment advice. No automatic orders.": "تعليمي، مش توصية استثمارية. مفيش أوامر تلقائية.",
    "Mr X": "Mr X", "Backtest agent": "وكيل الباك تيست", "Agent desk": "مكتب الوكلاء", "Needs": "المطلوب", "owner decision": "قرار المالك",
    "A model key (OpenAI or the free Gemini key)": "مفتاح موديل (OpenAI أو Gemini المجاني)",
    "A GitHub token limited to this repository (write the meeting room, open an @claude request)": "توكن GitHub محدود على الريبو ده (يكتب في المحضر ويفتح طلب @claude)",
    "A daily spending cap": "سقف صرف يومي",
    "Until these are set, write tasks in the meeting room; the site manager distributes them.": "لحد ما دول يتظبطوا، اكتب المهام في المحضر، ومدير الموقع يوزعها.",
    # Radar screener + backtest agent (2026-10-22)
    "Screener": "السكرينر", "Trend": "الاتجاه", "up": "صاعد", "down": "هابط", "mixed": "مختلط", "Volume ≥ × average": "الفوليوم ≥ × المتوسط",
    "Signals ≥": "الإشارات ≥", "Trend up": "اتجاه صاعد", "Trend down": "اتجاه هابط", "Oversold (RSI ≤ 30)": "تشبع بيع (RSI ≤ 30)",
    "Overbought (RSI ≥ 70)": "تشبع شراء (RSI ≥ 70)", "Top movers over 20 bars": "الأكثر حركة على آخر 20 شمعة",
    "Educational, not investment advice. Same candles as the Charts tab; no automatic orders.": "تعليمي، مش توصية. نفس شموع تبويب الشارتات؛ مفيش أوامر تلقائية.",
    "Explain your idea to the backtest agent": "اشرح فكرتك لوكيل الباك تيست", "Or build the rules by hand": "أو ابني القواعد بإيدك",
    "The agent needs a free Gemini key (GEMINI_API_KEY in Streamlit secrets). Until then, build the rules by hand in Technical Office > Backtest.":
        "الوكيل محتاج مفتاح Gemini مجاني (GEMINI_API_KEY في Streamlit secrets). لحد ما يتحط، ابني القواعد بإيدك في المكتب الفني ← الباك تيست.",
    "Your idea": "فكرتك", "e.g. buy when RSI 14 is under 30 and the close is above the 200 EMA, on the daily chart": "مثال: اشتري لما RSI 14 يبقى تحت 30 والإغلاق فوق EMA 200، على اليومي",
    "Ask the agent": "اسأل الوكيل", "New conversation": "محادثة جديدة", "The agent asks": "الوكيل بيسأل",
    "Assumptions / not testable here": "افتراضات / حاجات ماتتختبرش هنا", "Test the agent's rules": "اختبر قواعد الوكيل",
    "avg R by timeframe (dashed = 0.1R cost)": "متوسط R حسب الفريم (المتقطع = تكلفة 0.1R)", "avg R by school (dashed = 0.1R cost)": "متوسط R حسب المدرسة (المتقطع = تكلفة 0.1R)",
    "loaded (the dashboard fetch is capped; long histories run in GitHub Actions)": "اتحملت (الداشبورد بيجيب عدد محدود؛ التاريخ الطويل على GitHub Actions)",
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
