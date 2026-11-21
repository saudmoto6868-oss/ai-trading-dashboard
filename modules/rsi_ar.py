"""Arabic labels for the RSI board. Data stays English; the page translates with these maps."""

SCHOOL = {"Structure": "الهيكل SMC", "Liquidity": "السيولة", "Imbalance": "الفجوات FVG",
          "Elliott": "إليوت", "Fib/Harmonic": "فيبو وهارمونيك", "Trend": "الترند", "Momentum": "الزخم",
          "Price action": "البرايس أكشن", "Order flow": "الأوردر فلو"}

VERDICT = {"Long setup": "صفقة شراء", "Short setup": "صفقة بيع", "Bullish build-up": "بداية صعود",
           "Preparing to drop": "بتجهز تنزل", "Leaning up": "ميلان للصعود", "Leaning down": "ميلان للنزول",
           "Topping: overbought, sellers building": "قمة: تشبع شرائي والبيعيين بيزيدوا",
           "Basing: oversold, buyers building": "قاع: تشبع بيعي والشيريين بيزيدوا",
           "Coiling: squeeze, wait for break": "ضغط: استنى الكسر", "No edge": "مفيش ميزة"}

PHASE = {"rev_down": "خارج من التشبع الشرائي", "rev_up": "خارج من التشبع البيعي",
         "ext_up": "تشبع شرائي وبيطلع", "ext_dn": "تشبع بيعي وبينزل",
         "stall_ob": "تشبع شرائي وبيتوقف", "stall_os": "تشبع بيعي وبيتوقف",
         "mom_up": "زخم صاعد (كسر 60)", "mom_dn": "زخم هابط (كسر 40)",
         "squeeze": "استعداد: ضغط", "drift": "حركة عادية"}

TAG = {"Urgent": "عاجل", "Fresh": "جديدة", "MTF aligned": "الفريمات متفقة", "Pullback": "تصحيح",
       "Reversal": "انعكاس", "Momentum": "زخم", "Squeeze": "ضغط", "Divergence": "دايفرجنس",
       "Fast move": "حركة سريعة", "Volume spike": "فوليوم عالي"}

BAND = {"Overbought": "تشبع شرائي", "Strong": "قوي", "Neutral": "محايد", "Weak": "ضعيف", "Oversold": "تشبع بيعي"}

REGIME = {"Trend": "ترند", "Chop": "تذبذب", "Hi-Vol": "تقلب عالي", "Crash": "هبوط حاد", "Squeeze": "ضغط",
          "Thin": "سيولة خفيفة", "Mixed": "مختلط", "—": "—"}
