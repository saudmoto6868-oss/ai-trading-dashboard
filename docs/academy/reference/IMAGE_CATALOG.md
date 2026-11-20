# كتالوج الصور المرجعية (أكاديمية)

الغرض: مرجع واحد لكل صورة يبعتها المالك: إيه اللي فيها، أي مدرسة، وإيه حالتها عندنا. الصور مش إشارات ولا أدلة ربح.
**قاعدة:** أي فكرة مالهاش تعريف قابل للقياس تتسجل هنا كـ "مرجع فقط" ومتدخلش الشارت.

## حالات الاستخدام
- **مُنفّذ جزئيًا**: موجود في الكود بس بشكل ناقص.
- **مفقود**: مش موجود في الكود.
- **قابل للاختبار**: له قواعد واضحة، يتقاس في الـ lab بالشروط (n ≥ 100، t > 3، النصفين موجبين، بعد التكلفة).
- **مرجع فقط**: لا تعريف قابل للقياس (أرقام/أسطورة/رموز). ممنوع يبقى إشارة.

## الجدول

| ID | الملف | المحتوى | المدرسة | حالتنا عندها | الخطوة الجاية |
|---|---|---|---|---|---|
| R01 | `R01-offset-angle-corrections.jpg` | زوايا Offset (45°، 60°، 75°، 90°) من محور هبوط سابق على شارت | Gann | مفقود (مش متحقق منه في الكود) | تعريف قابل للقياس للزوايا، ثم lab |
| R02 | `R02-harmonic-overtones-music-ratios.jpg` | overtones ونسب موسيقية (9:8، 81:64، 256:243) | مرجع فقط | مرجع فقط | لا شيء |
| R03 | `R03-gann-angler-square-of-twelve.jpg` | جدول Square of Twelve (Gann Angler) | Gann | مفقود | نفس R01: تعريف ثم lab |
| R04 | `R04-flower-of-life-1-432.jpg` | Flower of Life و"1/432" | مرجع فقط | مرجع فقط | لا شيء |
| R05 | `R05-tesla-369-solfeggio-wheel.jpg` | عجلة 3-6-9 وترددات Solfeggio | مرجع فقط | مرجع فقط | لا شيء |
| R06 | `R06-harmonic-xabcd-ratios.jpg` | XABCD بنسب 0.618 / 0.786 / 1.27 | Harmonic | مُنفّذ جزئيًا: `modules/harmonic.py` فيه Gartley / Bat / Butterfly / Crab / Cypher، وlab key `harmonic` | قياس كل نمط باسمه في الـ lab (n ≥ 100 لكل نمط) |
| R07 | `R07-titius-bode-horizons.jpg` | Titius-Bode وأفق الكواكب | مرجع فقط | مرجع فقط | لا شيء |
| R08 | `R08-fib-fan-arc-on-price.jpg` | مروحة وقوس Fibonacci على سعر | Fibonacci / Gann | مُنفّذ جزئيًا (Fib targets في Spot، والـ fan في Workspace) | القوس غير موجود؛ قابل للقياس لو له تعريف |
| R09 | `R09-compounding-elliott-and-cheat-sheet.jpg` | Elliott مركب + cheat sheet (قواعد، Fib expansions/retracements) | Elliott | مُنفّذ جزئيًا (1-5 وA-B-C بس) | الـ expansions والـ retracements: قياس بتعريف واضح |
| R10 | `R10-solfeggio-369-digit-sum.jpg` | جمع الأرقام 3-6-9 على ترددات Solfeggio | مرجع فقط | مرجع فقط | لا شيء |
| R11 | `R11-elliott-fib-targets-ext-1-3-5.jpg` | أهداف Elliott: امتداد 1 و3 و5 + ABC / WXY | Elliott | مُنفّذ جزئيًا (أهداف 1.618 فقط) | تسمية WXY مفقودة |
| R12 | `R12-digit-wheel-1-9.jpg` | عجلة الأرقام 1-9 | مرجع فقط | مرجع فقط | لا شيء |
| R13 | `R13-hui-monthly-triangles-wedge.jpg` | HUI شهري: triangles، rectangle، falling wedge | تحليل فني عام | خارج Elliott؛ pattern detection (غير مفحوص هنا) | نتحقق من `pa_patterns` قبل أي قرار |
| R14 | `R14-digital-root-table.jpg` | جدول الجذر الرقمي 1-72 | مرجع فقط | مرجع فقط | لا شيء |
| R15 | `R15-elliott-rules-alternation-corrective-set.jpg` | القواعد الثلاث، Alternation، impulse، Zigzag، Flat، Double/Triple zigzag، Double/Triple 3، Contracting/Expanding triangle، Leading/Ending diagonal | Elliott | مفقود (غير الدافعة 1-5 وA-B-C) | **المرجع الرئيسي للتصحيحات المركبة** |
| R16 | `R16-elliott-impulse-abc-fib-ratios.jpg` | دافعة 1-5 + ABC بنسب 0.618 / 1.618 / 0.382 / 0.236 | Elliott | مُنفّذ جزئيًا | تعريف المسافات والقيود كاملة |
| R17 | `R17-soybeans-1949-planet-lines.jpg` | Soybeans 1949 مع خطوط كواكب (Mars / Jupiter) | Astro / Gann | مرجع فقط | لا شيء |
| R18 | `R18-gc-square-of-144.jpg` | /GC مع Square of 144 وخطوط Gann | Gann | مفقود | نفس R01 |
| R19 | `R19-gann-circle-45-on-price.jpg` | دائرة Gann وخطوط 45° على سعر | Gann | مفقود | نفس R01 |
| R20 | `R20-fib-fan-from-A-to-C.jpg` | مروحة Fibonacci من A نحو B وC (0.382 إلى 3.618) | Fibonacci | مُنفّذ جزئيًا (Fib targets) | المدى الكامل 0.382–3.618 يحتاج تعريف |
| R21 | `R21-elliott-shapes-poster.jpg` | بوستر أشكال Elliott: Five wave، Symmetrical، Ending diagonal، Running/Expanded/Regular flat، Impulse، Ascending، Reverse symmetrical | Elliott | مفقود (الـ flat والـ triangle والـ diagonal) | تصنيف الأشكال كتسميات بس (من R15 وR21) |

## ملاحظات
- **Elliott (R09، R11، R15، R16، R21):** أهم مجموعة. الجدول بيكشف إن الكود بيغطي الدافعة و A-B-C البسيطة بس.
- **Gann (R01، R03، R08، R18، R19، R20):** مش موجود كاملًا. أي زاوية أو مربع لازم تتعرّف بأرقام قبل ما تتقاس.
- **أرقام/كواكب/ترددات (R02، R04، R05، R07، R10، R12، R14، R17):** مرجع للمذاكرة بس. مش هتدخل المؤشر.
- الصور نفسها بقت نسخ في `docs/academy/reference/images/` (21 ملف، ~1.5MB). المصدر الأصلي هو رفع المالك.
