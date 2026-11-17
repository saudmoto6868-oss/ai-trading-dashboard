# TIA Risk Integration Gap — 2026-11-09

## Repository evidence
The current risk-related Dashboard code includes:
- `modules/desk_risk.py`: legacy Order Flow Desk risk helper.
- `modules/risk_engine.py`: setup-aware scanner plan builder.
- `modules/tia_risk_engine.py`, `tia_risk_ledger.py`, `tia_risk_reconciliation.py`: new isolated TIA contract, ledger and read-only reconciliation.
- `modules/tia_market_evidence.py`, `tia_market_risk_context.py`, `tia_options_risk_context.py`, `tia_unified_market_risk.py`: market evidence and descriptive context.

## Critical legacy mismatch
The legacy `modules/desk_risk.py` hardcodes a default `DeskRules.risk_pct = 0.5`, `daily_max_loss_pct = 2.0`, `max_stops = 3`, and `min_rr = 2.0`. Its module doc attributes 0.5% to an owner decision on 2026-11-09, while TIA risk-engine policy records an unresolved 0.25% vs 0.5% conflict and requires callers to supply an explicit versioned policy.

The legacy helper also:
- checks daily loss from realized P&L only; it has no open-position unrealized P&L, fees or funding in the daily guard;
- keys open positions by (symbol, side), so opposite-side positions can coexist without an explicit hedging policy;
- accepts caller-supplied risk amount rather than deriving and reconciling it against instrument tick/point value, entry, stop and quantity;
- has no durable event ledger, idempotent event ingestion, broker reconciliation or account/session timezone model;
- defaults every losing closed trade to a stop unless the caller explicitly overrides `stopped`.

The new TIA engine must not silently replace this helper until the owner resolves the risk policy, the integration branch is available, and a migration plan is reviewed.

## Integration blocker
The MR target branch `claude/order-flow-desk-tab-2026-11-09` was not present when checked; GitLab branch lookup returned 404 and branch search did not find it. The source branch contains the legacy risk helper but not the requested target-branch integration context. No retargeting to `main` was performed.

## Required next steps
1. Owner confirms the governing risk policy version and percentages.
2. Restore or identify the intended Order Flow Desk target branch.
3. Define a compatibility adapter from the Desk UI to explicit TIA policy, instrument specs, account/session snapshot and ledger.
4. Run the full Python suite, AppTest, and browser/mobile checks in a real project environment.
5. Shadow-compare legacy and TIA decisions before any UI cutover; do not execute orders.
