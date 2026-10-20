# Who does what (AI team) - 2026-10-19

Rule: free models do the volume; paid credit is spent only where a wrong answer costs real money.
Numbers from the lab decide trades. AI opinions are never evidence (n >= 100, t > 3, out-of-sample).

| role | provider | cost | why this one | tasks |
|---|---|---|---|---|
| Long-text research and reviews | Gemini (flash) | free tier, sometimes busy | good with long documents | school reviews, risk and scalp checklists (docs/reviews) |
| Second opinion on the same text | OpenRouter free models | free | a different model family checks the first | cross-check of every Gemini review |
| Code changes, bug fixes, workflows | Claude via `@claude` on GitHub | paid credit | strongest at editing this repo safely | only real tasks: a bug, a change to the scanner or the chart. No chat questions |
| Voice / Mr X in the app | Gemini Live | free tier | already built | live voice and typed answers |
| Decide what to trust | the lab (strategy-lab workflow) | free (GitHub) | measured, not opinion | every rule before it goes live |
| Not used now | OpenAI (credit spent / removed), DeepSeek (401), Mistral (not connected) | - | - | connect only when the key works and the task is worth it |

## Credit rules
- Before any `@claude` request: is it a change to code or a decision with money at stake? If not, do it in a free model.
- One `@claude` request per clear task (write the task fully in the first comment).
- Lab and review runs are manual (workflow_dispatch), so nothing spends in the background.
