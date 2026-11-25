# V7 development (تاب V7) - نقطة البداية للشغل من أي مكان

**المهمة:** تطوير تاب **V7** في لوحة XPiX / 6868 X: شارت حي واحد (OKX للكريبتو، Hyperliquid xyz للذهب/الفضة/الأسهم/الفوركس) بكل أدوات CFX/SMC/ICT كخانات إظهار/إخفاء، عقل مفكر بالقواعد (عربي/إنجليزي)، ومرشحات صفقات بحثية مرسومة. **بحث فقط: مفيش توصية ولا أوامر ولا ادعاء ميزة.**

- الفرع: `v7-development` (الوثائق دي). الكود نفسه على `main` (آخر commit V7: `a876955`).
- المستودع: `saudmoto6868-oss/ai-trading-dashboard` (GitHub، المصدر الأساسي دلوقتي). مرآة GitLab: `6868-group/ai-trading-dashboard` (project 88622818). الموقع: https://board-1-ij40.onrender.com
- التاب: PAGE 18 في `main.py`، على الشريط العلوي جنب TIA (قرار المالك 21 نوفمبر). الدخول: `modules/v7_page.py` (`render()`).
- المالك: سعود، مصري، عاوز ردود قصيرة وصريحة ومش بيحب الكلام من غير تسليم. اقرأ `CLAUDE.md` (قواعد التوكنز والصدق) قبل أي حاجة.

## الملفات في المجلد ده
| ملف | فيه إيه |
|---|---|
| `STATUS.md` | اللي اتعمل / الناقص / مقابل طلبات المالك وبنود الـ 52 |
| `TIMELINE.md` | تسلسل الأحداث والقرارات 9-25 نوفمبر + الـ MRs والـ commits |
| `ARCHITECTURE.md` | خريطة الملفات، تدفق الداتا، أوامر التست، فخاخ تقنية |
| `PLAN_NEXT.md` | الدفعة 2 والدفعة 3 بالتفصيل: إزاي ننفّذ كل بند وإيه معيار القبول |
| `LESSONS_AND_RULES.md` | قواعد المالك + أخطاء اتعملت (متكررش) + قواعد الصدق |
| `OWNER_MESSAGES.md` | رسائل المالك حرفيًا (المسجّل) + تلخيص الأقدم |
| `NEXT_SESSION_PROMPT.md` | برومبت جاهز تلصقه في جلسة جديدة |
| `images/` | الصور اللي قدرت أسترجعها (صورة واحدة بس، شوف `images/README.md`) |
| `tools/v7_mock_smoke.js` | اختبار المتصفح بداتا وهمية (Playwright) |

## تشغيل سريع (أي جهاز)
```bash
git clone https://github.com/saudmoto6868-oss/ai-trading-dashboard && cd ai-trading-dashboard
git checkout main && git pull
pip install numpy tzdata streamlit==1.66.0        # + node >= 18 for the parity tests
for t in tests/test_v7_*.py tests/test_cfx_rr_policy.py; do PYTHONPATH=. python3 $t || echo FAIL $t; done
```
اقرأ `ARCHITECTURE.md` ثم `PLAN_NEXT.md` وابدأ من الدفعة 2.
