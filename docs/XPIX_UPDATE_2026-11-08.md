# XPiX Update — 2026-11-08

## Review of minutes `946ce83a` and `docs/AI_ROLES.md`

**First decision for Claude: unify risk parameters.**
The new minutes say **0.25% per trade, daily cap 2%, stop after 3 stops**, while the previous DESK request and settings use **0.5%**. No conflicting number will be hardcoded before the owner resolves it.

### Proposed division (for Claude approval, not yet adopted)

| Task | Free models prepare | Paid Claude plans & executes |
|---|---|---|
| Chart scaffolding | Gemini Flash extracts reproduction steps & timings; OpenRouter cross-checks | Traces root cause, fixes rendering, verifies with browser test |
| Risk controls | Rules table, conflicts, accept/reject cases | Resolves spec with owner; writes position sizing, loss/exposure limits, anti-duplication tests |
| FRED & Regime Signal | Documents volatility, credit, market breadth, liquidity series + publish times + review cadence | Adopts classifications and walk-forward methodology; implements no-future-leakage, separates live log from backtest |
| GEX, Option Flow, Bookmap | Compares data sources, coverage, licenses, costs; summarizes long materials | Chooses architecture and source after owner approves cost, then implements integration |
| Schools, setups, open-source code | Extracts testable rules, reviews licenses and claims; independent cross-check | Selects what deserves a trial, adopts test criteria instead of merging every idea |

**Delivery to Claude must be concise:** sources, results, disagreements, test cases — not long dumps. Gemini Live for voice, XPiX with Grok for room/roles/branch follow-up. Free model availability itself has not been tested; no tasks sent to them yet.

Order Flow Desk minutes define seven roles: level scanner, context monitor, entry trigger, confluence confirmer, risk manager, skeptic, improvement researcher. Claude decides module wiring and execution order; improvement-researcher suggestions do not auto-convert to code.

## Branch status

- Work-allocation branch `team/work-allocation-2026-11-08` created from `946ce83a`.
- Still identical to origin — no modifications or merges yet.
- Next step: Claude approves the spec and division in the meeting room; code execution still blocked on dev-environment permission issue.
