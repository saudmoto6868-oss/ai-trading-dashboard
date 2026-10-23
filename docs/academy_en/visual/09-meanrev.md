# Mean Reversion — Full Visual Overview

> AI: [`../ai/09-meanrev.json.md`](../ai/09-meanrev.json.md)

![role](https://img.shields.io/badge/Role-Separate_system-a855f7)

---

## The key to understanding

```mermaid
flowchart LR
  ADXlow["Low ADX / range"] --> MR["The Mean Reversion book runs"]
  ADXhigh["High ADX / breakout"] --> TF["Switch MR off: leave the trend"]
  style MR fill:#a855f7,color:#fff
  style TF fill:#22c55e,color:#000
```

If you run MR during a strong thrust = you are buying a falling knife or selling a rocket.

```text
---- range top -- sell exhaustion
         middle / VWAP
---- range bottom -- buy exhaustion
```

## Cards

| | Long | Short |
|--|------|-------|
| Condition | Range + a low + oversold | Range + a high + overbought |
| Entry | A return inside the range | A return inside |
| Stop | Outside the edge | Outside the edge |
| Target | The middle, then the other edge | The middle |

## In the project

A system separate from the trend Grade · research **R3** then portfolio **R10**.
