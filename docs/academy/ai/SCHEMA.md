# Academy AI Schema — مرجع البرمجة

كل مدرسة في `ai/` تلتزم بهذا الشكل حتى تقدر الموديلات والكود تقرأها بدون غموض.

## كائن المدرسة (School)

```yaml
id: string              # elliott | gann | harmonic | levels | ...
name_ar: string
name_en: string
role_in_system: primary | context | timing | execution_gate | separate_system
lab_status: unproven | candidate | primary_candidate | disabled_default
branches: [Branch]
setups: [Setup]
```

## Branch (فرع / درس)

```yaml
id: string
title: string
rules_hard: [string]      # لا تُكسر
rules_soft: [string]      # إرشادات
confirmations: [string]
invalidation: [string]
```

## Setup (سيتب قابل للتنفيذ)

```yaml
id: string
direction: long | short
name: string
context: string
entry_conditions: [string]   # كلها AND ما لم يُذكر OR
entry_trigger: string
stop_rule: string
targets: [string]
confirmations: [string]
invalidation_price_rule: string
example:
  symbol_notes: string
  points: { key: number }    # أسعار توضيحية
  narrative: string
risk_notes: string
detector_hint: string | null  # اسم محتمل في المشروع
```

## ألوان منطقية (للكود وليس للزينة)

| حالة | كود |
|------|-----|
| long_bias | +1 |
| short_bias | -1 |
| neutral | 0 |
| invalid | null |

## مبادئ تنفيذ

1. لا تدخل من `visual/` — اقرأ `ai/` فقط.
2. الأمثلة الرقمية للتوضيح والاختبار الوحيدي، ليست بيانات سوق.
3. `role_in_system: context` لا يرفع Grade وحده.
