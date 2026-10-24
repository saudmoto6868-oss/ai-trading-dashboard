# SMC / ICT — عرض بصري كامل

> AI: [`../ai/04-smc.json.md`](../ai/04-smc.json.md) · أدلة: [`../BACKTEST_EVIDENCE.md`](../BACKTEST_EVIDENCE.md)

![دور](https://img.shields.io/badge/الدور-Context-94a3b8) ![تحذير](https://img.shields.io/badge/مش_Primary_افتراضي-f97316)

---

## السلسلة التي نعلّمها (لا نضمن الربح)

```mermaid
flowchart TB
  L["سيولة Equal H/L أو قمة جلسة"] --> S["كنس"]
  S --> B["BOS / إزاحة"]
  B --> Z["FVG أو OB"]
  Z --> R["رفض سعري"]
  style L fill:#f97316,color:#000
  style Z fill:#a855f7,color:#fff
  style R fill:#22c55e,color:#000
```

## Premium / Discount

```text
قمة النطاق ──── Premium (تفضيل بيع)
        EQ ──── الوسط
قاع النطاق ──── Discount (تفضيل شراء)
```

## بطاقات

| اسم | Long | Short |
|-----|------|-------|
| Sweep + FVG | كنس تحت + رجوع لفجوة صاعدة | كنس فوق + فجوة هابطة |
| Sweep + OB | طلب بعد إزاحة | عرض بعد إزاحة |
| OTE | ارتداد 62–79% بعد BOS صاعد | مرآة |

### صندوق صدق

الاختبارات الميكانيكية العامة غالباً **edge صغير** بعد التكاليف — ليست السردية على يوتيوب. في المشروع: Context حتى يثبت **R5**.

## في المشروع

يحتاج تعريفات كود ثابتة قبل Lab · لا ترفع Grade من SMC وحده.
