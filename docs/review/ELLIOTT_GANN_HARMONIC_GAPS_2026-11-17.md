# مراجعة فجوات: إليوت، جان، هارمونيك (2026-11-17)

الغرض: قايمة واضحة بالحاجات الناقصة، وإيه اللي اتعمل، وإيه اللي محتاج قرار من المالك. مفيش إشارات جديدة ولا تشغيل lab في المراجعة دي.

## 1. إليوت

| الموضوع | الحالة في الكود | ملاحظة |
|---|---|---|
| دافعة 1-5 (القواعد الثلاث) | موجود (`ewCount` في JS، `signals.elliott_bull`، `spot_ind.elliott`) | ثلاث تنفيذات بقواعد مختلفة شوية؛ لسه ماتوحدتش |
| A-B-C بسيط | موجود | zigzag بس في الشارت |
| Zigzag / Regular / Expanded / Running flat | **متنفذ** (`elliott_shapes.abc_shape`، JS port) | الحدود قراءتنا للكتب، تحتاج مراجعة المالك |
| Ending diagonal | **متنفذ** (`impulse_shape`) | الـ leading diagonal مش ممكن يتفرق عن الـ ending من 5 pivots لوحدهم؛ يحتاج سياق (موجتين قبله) |
| Triangles (contracting / expanding) | **متنفذ بطول الأرجل فقط** | ناقص خطوط الترند اللي بتقفل المثلث |
| W-X-Y (double zigzag / double three / combo) | **متنفذ** (`wxy_shape`) | ناقص triple (X-Y-X-Z) |
| Alternation (wave 2 sharp مقابل wave 4 sideways) | **مفقود** | قاعدة من بوستر R15 وR21؛ قابلة للقياس بعمق التراجع |
| تسميات فرعية (i-v جوه الموجة) | مفقود | تحتاج تقسيم أعلى degree |
| Degrees (Minor / Intermediate) | مفقود | تحتاج تعريف مستوى الـ zigzag لكل degree؛ الـ lab عنده 3 مستويات swing بس |
| منطقة Fibonacci للدافعة الأحدث (0.5 إلى 0.854) | مفقود | دراسة LuxAlgo في `docs/ELLIOTT_HARMONIC.md`؛ مش متنفذة |
| نتايج الـ lab (2026-11-15) | ew_r3_d2: avg +0.14R، صافي +0.04R، random +0.077R؛ مفيش YES | مش دليل، والـ lab محتاج إذن |

## 2. جان

| الموضوع | الحالة في الكود | ملاحظة |
|---|---|---|
| زوايا 1x1 و1x2 و2x1 على الشارت | **موجود** (`paintGann` في JS، `gannFitFor`) | الكود الحالي فيه fit وsquare of 9 وastro |
| Square of 9 | موجود (`spot_ind.sq9`، و`paintGann`) | |
| `gann_geom.py` (Python، وحدة ثابتة) | متنفذ كـ helper | **مش** مربوط بالشارت؛ الشارت بيستخدم منطقه الخاص |
| Offset angles (45/60/75/90 من محور) | مفقود | تعريف "المحور" و"الإزاحة" لسه مش واضح في الصور |
| Square of 12 / 144 | مفقود عن قصد | جدول أرقام من غير قاعدة قابلة للقياس |
| دوائر وزوايا حول pivot | مفقود | نفس المشكلة |

**تصحيح:** PR #245 كانت بتقول إن جان مش مرسوم على الشارت. ده غلط؛ جان موجود على الشارت فعلاً. الـ `gann_geom.py` helper بس.

## 3. هارمونيك

| الموضوع | الحالة في الكود | ملاحظة |
|---|---|---|
| Gartley / Bat / Butterfly / Crab / Cypher | موجود (`modules/harmonic.py`، JS mirror، `paintHarm`) | |
| النسب | مطابقة للكتب، ما عدا Cypher C | الكود 1.13–1.414؛ المصادر بتقول 1.272–1.414 (بحث LuxAlgo وغيره، مش كتب Carney الأصلية) |
| Spot desk | **متنفذ** (`spot_ind.reads["harmonic"]`، كارت في `spot_dash`) | |
| Decision desk | مفقود | `decision_desk` بيعرض lab evidence بس؛ مفيش دليل lab للأنماط دي |
| تقييم كل نمط باسمه في الـ lab | مفقود | محتاج n ≥ 100 لكل نمط؛ يحتاج إذن للتشغيل |
| Alternate / Deep Crab / Shark / Three Drives | مفقود | قابلة للتعريف بنسب؛ تحتاج قرار المالك |

## 4. اللي اتعمل في الجولة دي
- ما اتعملش تغيير في الكود. دي مراجعة فقط.
- الاختبارات الحالية لإليوت وجان والـ spot كلها OK (من الجولة اللي فاتت).

## 5. قرارات محتاجة المالك
1. Cypher C: 1.13 ولا 1.272؟ (التغيير بيغيّر نتايج الـ lab.)
2. هل نضيف Alternation وtriple W-X-Y للشارت؟
3. هل نشغّل الـ lab على الأشكال الجديدة (بتكلف)؟
4. Offset angles: تبعت لي تعريف "المحور" و"الإزاحة" من الصورة R01، أو نسيبها.
5. الـ decision desk: نعرض الأشكال بـ "لا يوجد دليل" لحد ما الـ lab يتشغل؟

## 6. مصادر
- LuxAlgo، Cypher pattern: https://www.luxalgo.com/library/concept/cypher/
- LuxAlgo، Harmonic & Fib ratio set: https://www.luxalgo.com/library/concept/harmonic-and-fib-ratio-set.md
- مصادر تعليمية متنوعة (TradingView وBabyPips وغيرها) بتتفق على النسب الأساسية، لكنها مش كتب أصلية؛ مش متحققة من كتاب Carney نفسه.
