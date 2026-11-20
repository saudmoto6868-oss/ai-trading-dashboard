# TIA Risk Shadow Comparison — 2026-11-09

## Purpose
`modules/tia_risk_shadow.py` runs the existing `modules.desk_risk.DeskDay` rules and the new TIA `assess_new_trade` contract side by side for the same proposed trade. It is a diagnostic adapter only.

## Inputs must be explicit
- Legacy `DeskRules`, starting equity, realized P&L, stop count and open keys.
- TIA versioned `RiskPolicy` and a validated `RiskSnapshot`.
- Legacy caller-supplied risk amount and TIA proposed risk are passed separately. They are not assumed equal or equivalent.
- Proposed trade fields and asset class.

## Differences surfaced
- Allow/block disagreement.
- Per-trade, daily-loss, stop-count and reward:risk policy differences.
- Different realized-P&L inputs.
- TIA open-position unrealized P&L, fees or funding not represented in legacy daily state.
- TIA open-position stop-risk and symbol/hedging guards.
- Different legacy caller risk amount versus TIA proposed risk.

## Critical limitation
This is not yet a full migration adapter. Legacy `DeskDay` only sees realized P&L, a caller-supplied risk amount and a set of (symbol, side) keys. TIA uses a portfolio snapshot, open stop-risk reservation and mark-to-market P&L. The two results are intentionally not treated as directly interchangeable.

## Safety boundary
- No Streamlit UI wiring or decision-path replacement.
- No order placement or broker writes.
- No default risk profile is selected.
- Keep the MR Draft until policy ownership, intended target branch, and actual test execution are resolved.
- Run shadow comparisons over historical/replayed trade cases and inspect every disagreement before any cutover.
