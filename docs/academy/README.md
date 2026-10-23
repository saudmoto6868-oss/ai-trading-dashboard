# أكاديمية 6868 X — مساران (مكتمل الفروع الأساسية)

| المسار | المجلد | الجمهور |
|--------|--------|--------|
| **AI / برمجة** | [`ai/`](ai/) | كود، Lab، موديلات، رادار |
| **عرض بصري** | [`visual/`](visual/) | واجهة الأكاديمية، شرح، mermaid |

**مرجع التنفيذ = `ai/` دائماً.**

## فهرس المدارس

| id | المدرسة | AI | Visual | دور النظام |
|----|---------|-----|--------|------------|
| levels | مستويات / PA | [01-levels.json.md](ai/01-levels.json.md) | [01-levels.md](visual/01-levels.md) | primary |
| trend | اتجاه / Turtle | [02-trend.json.md](ai/02-trend.json.md) | [02-trend.md](visual/02-trend.md) | primary |
| sessions | سيولة / جلسات | [03-sessions.json.md](ai/03-sessions.json.md) | [03-sessions.md](visual/03-sessions.md) | timing |
| smc | SMC / ICT | [04-smc.json.md](ai/04-smc.json.md) | [04-smc.md](visual/04-smc.md) | context |
| elliott | إليوت | [05-elliott.json.md](ai/05-elliott.json.md) | [05-elliott.md](visual/05-elliott.md) | context |
| gann | جان | [06-gann.json.md](ai/06-gann.json.md) | [06-gann.md](visual/06-gann.md) | context |
| harmonic | توافقي | [07-harmonic.json.md](ai/07-harmonic.json.md) | [07-harmonic.md](visual/07-harmonic.md) | context |
| orderflow | تدفق أوامر | [08-orderflow.json.md](ai/08-orderflow.json.md) | [08-orderflow.md](visual/08-orderflow.md) | execution_gate |
| meanrev | عودة للمتوسط | [09-meanrev.json.md](ai/09-meanrev.json.md) | [09-meanrev.md](visual/09-meanrev.md) | separate_system |

## ملفات مشتركة

- [`ai/SCHEMA.md`](ai/SCHEMA.md) — شكل YAML للسيتبات
- [`visual/STYLE_GUIDE.md`](visual/STYLE_GUIDE.md) — ألوان وتأثيرات العرض

## حالة

- [x] كل المدارس التسع على المسارين
- [ ] تبويب Streamlit يقرأ `visual/`
- [ ] parsers تقرأ `ai/` للـ Lab
