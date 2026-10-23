# خريطة المؤشرات ↔ الأكاديمية ↔ المشروع

هذا الملف **مرجع تقني** للفريق: كل مدرسة تشير لأي طبقة/كاشف/مؤشر محتمل في 6868 X.

> الأسماء أدناه منطقية/من الوثائق السابقة؛ عند التعارض مع الكود الحي، الكود هو الحقيقة — حدّث هذا الملف.

## طبقات الرادار (Decision Chain)

| طبقة | مدارس تغذّيها | مخرجات متوقعة |
|------|----------------|----------------|
| Regime | trend, meanrev gate | trend / range / unknown |
| HTF | trend, levels structure | bias +1/0/-1 |
| Location | levels, smc premium-discount | discount / premium / EQ |
| Trigger | levels, trend breakout, sessions sweep, harmonic D | setup id |
| OF gate | orderflow | pass / fail / n/a |
| Timing | sessions | in_kz / out |
| Plan | الكل بعد المرور | stop, targets, R |

## ربط المدارس بالمؤشرات والأدوات

| مدرسة | مؤشرات / أدوات شارت | موديول/كاشف محتمل | ملاحظات |
|--------|---------------------|-------------------|--------|
| levels | Pivots, zones, ATR stops | level, ohl_break | Primary مرشح |
| trend | Donchian 20/55, SMA 10/40, ATR | turtle55, sma1040 | يومي |
| sessions | Session high/low, PDH/PDL | liqline, session tags | Timing |
| smc | FVG boxes, OB zones, EQ | (يحتاج تعريف كود) | Context |
| elliott | ZigZag, Fib, OTE | elliott helpers | Context + invalidation |
| gann | Fan, Sq9 levels | Se7s-style / AUTO | Context؛ حساس للمقياس |
| harmonic | XABCD, PRZ | harmonic_* per pattern | ε نسب |
| orderflow | T&S, Delta, Gauge, Limit Track, DOM | absorption, dom_panel | Gate فقط |
| meanrev | RSI, BB, ADX gate, VWAP | (منفصل) | لا تدمج مع trend Grade |

## مؤشرات مساعدة مشتركة (تأكيد لا مدرسة)

| مؤشر | استخدام أكاديمي |
|------|------------------|
| ATR | وقف، وحدات ترند، فلتر ضجيج |
| ADX | بوابة range vs trend لـ meanrev |
| VWAP | هدف MR / مرجع جلسات |
| Volume / delta | تأكيد عند المستوى |
| EMA/SMA | انحياز سريع؛ لا يغني عن structure |

## سياسة المرجع

1. أي مؤشر جديد في الواجهة يُوثَّق هنا + سطر في المدرسة المعنية تحت `ai/`.  
2. لا يُرفع مؤشر لـ primary إلا بعد مسار Lab في DEVELOPMENT_NOTES (R*).  
3. العرض البصري يشرح؛ هذا الملف يربط التنفيذ.
