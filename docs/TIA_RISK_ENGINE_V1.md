# TIA Risk Engine v1 — implementation boundary

## Delivered
- Explicit, versioned `RiskPolicy`; there is no implicit 0.25% or 0.5% default.
- Instrument contract for tick/quantity increments, point value, multiplier, quote-to-account conversion, round-trip fee and funding reserve.
- Validated open positions with side-aware stop geometry.
- Stop-risk reservation for every open position.
- Mark-to-market unrealized P&L combined with realized P&L, paid fees and funding when calculating daily net drawdown.
- Per-trade, daily-loss, stop-count, aggregate-open-risk, duplicate-symbol/side and reward:risk checks.
- Fail-closed finite-number and identity validation.
- No order placement, broker writes, or automatic risk-profile selection.

## Critical integration gates (not yet production enforcement)
1. **Risk amount integrity:** caller-supplied `proposed_risk` is not yet derived from order quantity, entry, stop, instrument specification and execution-cost model. The caller must not be trusted until that binding is implemented.
2. **Freshness and provenance:** the caller must validate mark timestamps, provider identity, account currency and FX conversion age before constructing a snapshot.
3. **Persistence/session:** this module is stateless. Durable daily state, timezone-aware session rollover, event IDs/idempotency and concurrent updates require a separate transactional store.
4. **Portfolio policy:** current v1 enforces a total open-risk cap and same-symbol hedge rule. Per-asset-class, correlation, leverage, margin and concentration limits are not implemented.
5. **Operational validation:** unit tests are added but have not been executed in this connector workflow. No broker, live feed, Streamlit or full-suite validation has been performed.

## Policy decision
The older Order Flow implementation embeds 0.5%, while meeting notes also mention 0.25%. This branch deliberately requires an explicit `policy_id` and `version`; it does not settle that conflict. The example values in tests are fixtures only, not an owner-approved production policy.

## Integration plan
Keep this contract isolated until the owner approves the policy and the missing gates above are implemented and tested. Do not merge this branch into `main` as a claim of live enforcement.