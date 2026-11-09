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

## Follow-up slice: quantity sizing and daily ledger
- `modules/tia_risk_ledger.py` adds quantity sizing derived from equity, explicit risk %, entry/stop, tick size, quantity step, point value, multiplier, fee/funding reserve and a timestamped FX conversion quote.
- Sizing rounds quantity down and rejects stale/future FX timestamps, currency mismatches, off-tick prices and quantities below minimum increment.
- `RiskLedger` adds file-backed SQLite sessions keyed by account + IANA timezone + local session date, immutable event rows, payload hashes, duplicate-event idempotency and conflicting-replay rejection.
- Session identity locks start equity and policy version for that local trading day. Session rollover is based on the configured timezone (including timezone database DST rules).

### Remaining persistence and sizing limits
- SQLite is appropriate only as a local/single-host interim ledger on a reliable local filesystem. It is not a distributed lock or multi-host production database. Use a transactional server database for horizontally scaled deployments.
- The event journal now has a deterministic replay projection for position open/mark/close, realized P&L, fees, funding and explicitly classified stops. It validates reconstructed positions against instrument specs. Recovery/reconciliation against broker statements and a durable projection cache are still required before live enforcement.
- The sizing function returns an auditable proposed quantity but has not yet been wired into Order Flow Desk's UI/decision path. Existing callers must not continue supplying arbitrary risk amounts as if verified.
- Broker-specific contract semantics (inverse contracts, quanto, options Greeks, FX pip value, CFD lot conventions, exchange fee tiers, maker/taker and funding schedules) need provider/instrument adapters and verified specs. The generic linear point-value model must not be applied to them without an adapter.
- No automatic stop movement, partial fill, slippage or gap-through-stop simulation is included.


## Event replay contract
The ledger accepts only the documented projection event types: `position_open`, `position_mark`, and `position_close`. Close events must carry an explicit boolean `stopped`; negative realized P&L alone does not increment the stop counter. Replay rejects duplicate active position IDs, marks/closes of unknown positions, malformed instrument specs, and unsupported event types. This projection is a deterministic rebuild from the append-only journal, not broker reconciliation.


## Broker position reconciliation boundary
- `modules/tia_risk_reconciliation.py` defines a normalized, read-only broker snapshot contract. It compares account identity, position IDs, symbols, side, quantity and entry against the event-ledger projection.
- A snapshot is accepted only when the source/account are present, its timestamp is timezone-aware and within the configured age, and the provider explicitly marks the snapshot complete.
- Ledger-only positions, broker-only positions, changed position attributes, stale/incomplete snapshots and account mismatches all fail closed. No reconciliation function writes to a broker or alters the ledger.
- Provider adapters are still required to map broker-specific position IDs, netting/hedging models, partial fills and contract quantities into this normalized contract. A broker that cannot provide stable position IDs needs a documented deterministic identity adapter and ambiguity handling.
- This compares positions, not balances, cash, margin, orders, executions, accrued commissions or financing statements. Those are separate reconciliation domains and remain mandatory before production risk enforcement.
