# TIA Risk Engine v1 — implementation boundary

## Delivered
- Explicit, versioned `RiskPolicy`; there is no implicit 0.25% or 0.5% default.
- Instrument contract for tick/quantity increments, point value, multiplier, quote-to-account conversion, round-trip fee and funding reserve.
- Validated open positions with side-aware stop geometry.
- Stop-risk reservation for every open position.
- Mark-to-market unrealized P&L combined with realized P&L, paid fees and funding when calculating daily net drawdown.
- Per-trade, daily-loss, stop-count, aggregate portfolio open-risk, optional asset-class concentration, duplicate-symbol/side and reward:risk checks.
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


## Portfolio concentration extension
RiskPolicy may optionally define `max_asset_class_open_risk_pct`. When supplied, the engine sums reserved stop risk for existing positions in the proposed trade's asset class and adds proposed risk before checking the class cap. The class cap cannot exceed the total portfolio open-risk cap. Leaving it unset means no class-specific cap is asserted; it does not imply unlimited account leverage or margin safety.


## Existing AI Trading Dashboard feed bridge
- `modules/tia_market_evidence.py` catalogs and reuses the providers already present in this repository. It calls the existing `modules.spot_flow.fetch` adapter rather than creating a duplicate market-data client.
- **OKX public REST:** candles, recent trades, order-book snapshots, taker-volume history, perpetual open interest, funding and long/short account ratio. This is single-venue market evidence; it is not the user's OKX account.
- **Hyperliquid public info API:** xyz perpetual market list/prices/candles, order-book and trade context, funding and open interest where available. Metals and other TradFi symbols are perpetual/oracle-linked instruments, not the underlying cash-market feed; coverage is thinner than OKX.
- **Deribit public API:** BTC/ETH option book summaries and DVOL history. Useful for options regime/context, not user account state.
- **Cboe delayed quotes:** US equity/index option chains through the existing adapter; approximately 15-minute delay and endpoint/reuse limitations remain.
- **News:** Finnhub when a key is configured, with existing Alpha Vantage/RSS fallback paths. A headline is a catalyst candidate, not proof of impact.
- **Workspace evidence:** existing chart candles, Footprint/order-flow confluence, levels, journal and news context remain the source of those in-app observations. Journal records are not broker-confirmed fills.

### Evidence semantics
The bridge preserves each feed's `ok/why` state and does not turn a failed feed into zero. It records local collection time separately from provider event time. Since the existing order-flow adapter does not normalize provider event timestamps across all subfeeds, the snapshot is explicitly labeled `UNVERIFIED_PROVIDER_TIMESTAMP`; it must not pass a strict live freshness gate until source timestamps are exposed and validated.

### Account data still unavailable
The current public market adapters cannot prove account balance, equity, used/free margin, pending orders, broker-confirmed fills, commissions or funding debits/credits for the user's account. `account_data_capabilities()` exposes these as `UNAVAILABLE_NO_AUTHENTICATED_BROKER_ACCOUNT_ADAPTER`. No market price, funding rate, OI, journal row or public order-book snapshot may be substituted for those account facts.


## Market risk context from existing dashboard feeds
- `modules/tia_market_risk_context.py` turns the existing OKX/Hyperliquid `spot_flow.fetch` result into a typed, descriptive risk context. It does not open a second network client or duplicate provider logic.
- It reports directional evidence separately from execution/crowding flags: tape aggressor share, taker-volume slope and displayed-book imbalance contribute only to a consensus label (buy pressure, sell pressure, mixed, or insufficient).
- Review flags include displayed-book imbalance, configurable thin-book threshold (disabled unless explicitly set), positive-funding crowding, long-account crowding, OI context, unavailable order flow and unverified provider timestamps.
- Thresholds are configurable review heuristics, not validated predictive limits and not owner-approved policy. They do not alter risk budget, quantity, leverage, stops or order permission.
- Missing feeds remain unavailable; they are not treated as zero or as neutral evidence. Local collection time is not misrepresented as provider event time.
- The existing `volume_profile` / VP calculation is explicitly described as a volume-profile approximation, not exchange-level bid/ask footprint delta.
- Public order-book snapshots are venue-specific and cancellable; they do not establish global liquidity or historical depth.


## Instrument-spec evidence gate (reviewed against the current Dashboard repository)

The current repository contains symbol/watchlist and chart-provider mappings, not a verified broker contract-specification registry:
- `config.py` labels `US100`/`US500` as broker-dependent CFD names and the starter stock list as placeholders. TradingView mappings are chart symbols, not broker contract specifications.
- OKX public market adapters provide venue-specific crypto market data; they do not establish the user's broker lot size, account currency, fees or execution contract.
- Hyperliquid xyz exposes oracle-linked perpetual instruments for metals/TradFi symbols; these are not the underlying cash contract and do not establish an MT5 CFD specification.
- Deribit options and Cboe delayed option chains are not linear spot/CFD sizing specifications. Options require a separate premium/Greeks/multiplier/assignment model.
- The current public market adapters do not provide authenticated account equity, margin, fills, broker fees or financing.

Accordingly, no universal XAUUSD, FX, index-CFD, stock-CFD, futures, inverse/quanto crypto or options multiplier is inferred from the watchlist or chart symbol. A caller may use `size_trade` only after supplying an instrument specification verified against the actual execution venue/account, including quote currency, tick size, quantity step, point value, contract multiplier and applicable round-trip cost reserve. Until then the instrument is unsupported for automated sizing and must fail closed at the integration boundary.

### FX conversion consistency limitation
`size_trade` uses a timestamped `ConversionQuote` for the sizing calculation. `Position` currently stores `account_ccy_per_quote_ccy` inside `InstrumentSpec` for mark-to-market P&L and stop-risk projection. The caller must ensure this stored conversion is the same validated conversion used for the position snapshot and refresh it with a fresh quote as required. The normalized position contract does not yet carry its own FX quote timestamp/provenance; this is a production gate, not an assumed live conversion.

### Policy provenance note
The legacy `config.py` and `modules/desk_risk.py` currently state a 0.5% per-trade default and describe a 2026-11-09 owner decision, while earlier meeting notes recorded 0.25%. The isolated TIA engine deliberately has no default and requires an explicit versioned policy. The existence of the legacy 0.5% constant is not, by itself, permission to silently select it for TIA or to migrate the live Desk path.
