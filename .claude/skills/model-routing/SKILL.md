---
name: model-routing
description: Select an appropriately capable model for each task without sacrificing correctness or safety.
---

# Model routing

Choose by task risk and acceptance criteria, not by habit.

- Low risk and easy to verify: use a fast/low-cost model for bounded extraction, formatting, or routine summaries.
- Normal engineering: use a capable coding model for implementation, tests, and routine debugging.
- High impact: use the strongest available reasoning model for architecture, security, financial/risk logic, ambiguous bugs, and independent final review.

Escalate when the current model cannot meet the acceptance criteria. Do not force a cheap model on a difficult task. Use currently available model identifiers; do not hard-code assumed future model names.

A model switch does not change the required tests or review standard.
