# Order Flow Desk — Risk and GEX Audit

Date: 2026-11-09  
Scope: read-only review of `claude/order-flow-desk-2026-11-09` against `main`.  
Reviewed source: one branch commit, `modules/desk_risk.py`, `modules/gex.py`, `modules/cboe_options.py`, `modules/options_desk.py`, `modules/flow_manual.py`, and the branch's two new test scripts.  
This document is an audit record only. It does not modify or merge the Order Flow branch.

## Executive result

The branch adds useful isolated calculations and openly documents important data limitations. It is **not ready to be treated as a live risk gate or production GEX service**. The code is not wired to the UI, GEX has mock-only tests, Cboe's public delayed endpoint is unofficial, and the risk manager does not yet account for all portfolio/day-risk states.

No live Cboe request was made and no provider output was independently verified in this review.

## 1. Position sizing and daily risk manager

### Positive findings
- Pure functions with no network or Streamlit dependency.
- Position sizing rounds quantity down when a positive lot step is supplied.
- Reward:risk checks, duplicate-key checks, per-trade cap, daily realized-loss cap and stop-count lock are centralized in `DeskRules` / `DeskDay`.
- Eight focused test functions are supplied.
- No order-placement action is present.

### Blocking issues before any UI enforcement

1. **Daily loss excludes open/unrealized P&L.** `loss_pct` and `remaining_budget()` use realized P&L only. A position can be deeply underwater while the gate still reports remaining daily capacity. Add mark-to-market P&L, fees, funding and a documented equity baseline; define whether the cap is based on realized, unrealized, or total equity drawdown.
2. **Open risk is not reserved.** `open()` stores only a (symbol, side) key. It does not reserve risk amount or aggregate correlated/open exposure. Several individually allowed trades can exceed the daily loss budget when stops are hit together.
3. **Duplicate prevention is directional only.** The key allows a long and a short in the same symbol simultaneously. Define whether hedged positions are allowed and whether one symbol can have multiple strategy positions.
4. **Input validation is incomplete.** Validate finite numbers (reject NaN/inf), positive start equity, non-negative finite P&L, valid side, positive point value, and valid quantity step. Negative `qty_step` is currently silently treated as no rounding. `DeskDay(0)` can later divide by zero.
5. **Risk checks accept a caller-supplied risk amount.** The gate does not bind that number to the entry, stop, quantity, point value, contract multiplier, currency conversion, or fees. The sizing result and gate must share a typed instrument specification and recompute the worst-case risk.
6. **Stop/target direction is inferred from entry/stop only.** The API does not receive trade side. Validate side and require stop and target to be on the correct side for that direction; reject malformed geometry.
7. **Daily state has no persistence or session boundary.** In-memory `DeskDay` resets on process restart and has no timezone/session/day rollover or idempotent trade IDs. It cannot safely enforce a daily cap across app workers or sessions.
8. **Stop count semantics are ambiguous.** The default counts every negative-P&L trade as a stop. Partial exits, commissions, manual closes, breakeven, and non-stop exits need explicit classification.
9. **No portfolio or correlated risk aggregation.** There is no account/currency/asset-class exposure, simultaneous stop scenario, leverage, margin, broker-specific contract spec, or funded-account rule profile.
10. **Risk policy conflict remains unresolved.** The branch uses 0.25% per trade while historical settings reportedly use 0.5%. Do not hard-wire either as an approved owner policy until the source-of-truth decision is confirmed. The code should require a named, versioned profile rather than silently defaulting.

### Required tests
- NaN, infinity, zero/negative equity, invalid stop, invalid target, wrong-side target, invalid quantity step and point value.
- Open risk reservation, opposing-side positions, multiple instruments, correlated exposure and simultaneous stops.
- Floating loss plus fees/funding at and beyond daily cap.
- Restart persistence, duplicate trade-event replay, session rollover/timezone and concurrent callers.
- Contract multipliers, tick/lot sizes, currency conversion, futures/CFD/spot/crypto instrument specs.
- Explicit classification of stopped vs discretionary losing exits.

## 2. GEX model and Cboe source

### Positive findings
- The code labels the dealer-position sign as an assumption, not observed truth.
- GEX is explicitly context-only and not an entry signal.
- The Cboe adapter labels the endpoint unofficial and delayed; the branch does not claim a live verification.
- Tests cover synthetic walls, sign flips, IV percent normalization, expired contracts and feed gamma.

### Blocking issues

1. **Contract multiplier is globally fixed at 100.** This must be an instrument/contract specification, not a universal constant. Validate multiplier and deliverable for each underlying and option class before comparing dollar GEX.
2. **Dealer sign is a model assumption.** Calls-positive / puts-negative is not actual dealer inventory or positioning. Preserve this assumption in every UI/table/export and never label the resulting regime as observed dealer gamma.
3. **Feed gamma provenance is not checked.** The adapter accepts a `gamma` field without verifying units, timestamp, underlying spot, model, or whether it belongs to the same snapshot. If the feed gamma is stale or uses a different spot, walls can be misleading.
4. **Gamma flip uses a different gamma basis.** `by_strike()` can use feed gamma, but `gamma_flip()` always recomputes Black–Scholes gamma. The resulting walls/net GEX and flip may therefore not be internally comparable. Expose methodology and make the calculation basis explicit.
5. **Input validation is too permissive.** Reject invalid/non-positive spot and strikes, malformed expiry/type, negative or non-finite OI, invalid IV, invalid width/steps/max_days, and unknown option types. Current unknown types fall into the put sign via the startswith check.
6. **Zero/invalid IV handling can silently create zero gamma.** Distinguish missing IV, zero IV and rejected contracts; report coverage counts and dropped-row reasons rather than quietly treating them as no exposure.
7. **Expiry/time convention is date-only.** The model floors all same-day expiries to one day. That avoids a numerical blow-up but is not a defensible intraday 0DTE treatment. Use exact time-to-expiry with timezone and market close, with a tested near-expiry policy.
8. **Gamma flip is a coarse grid interpolation.** A finite grid may miss multiple roots or a narrow sign change. Validate width/steps, detect all sign changes, report no-root/ambiguous-root state, and expose resolution.
9. **No data-quality contract.** Results need source, fetched-at, delayed/as-of time, underlying spot and its timestamp, expiry coverage, OI timestamp, IV/gamma coverage, multiplier, model, and assumptions.
10. **Cboe endpoint is unofficial.** Community-derived field names and OCC parsing may break. HTTP 200 does not mean data is current or complete. Add schema/coverage checks and explicit stale/unavailable/partial status. Confirm reuse terms before production.
11. **Caching has no stale-state metadata.** A cached tuple has no returned age/status. Callers must not mistake a cached delayed response for live data.
12. **No live-chain test.** Synthetic unit tests do not validate endpoint schema, actual gamma units, spot alignment, expiry coverage, index symbols, or real-world numerical plausibility.

### Required tests
- Known option-chain fixtures with independently calculated gamma and contract multipliers.
- Missing/malformed/unknown option type, invalid strikes, invalid spot, NaN/inf/negative OI and IV.
- Feed gamma timestamp/spot mismatch and mixed feed/model gamma behavior.
- 0DTE with actual expiry time and timezone.
- Multiple/no gamma flips and grid-resolution sensitivity.
- Cboe schema drift, partial chains, stale cache, HTTP errors, rate limiting and underlying spot missing.
- Snapshot reproducibility: same input and methodology must produce same outputs.

## 3. Integration and order-flow architecture

- The reviewed branch adds `desk_risk.py` and `gex.py`, but its own review notes say neither is wired to the UI. This is appropriately cautious.
- Do not place GEX in the execution path. If later displayed, label it **modeled options context — delayed — assumption-based** and show source age and coverage.
- The current Cboe chain is US equity/index options only; it is not a proxy for BTC/ETH options. The existing Deribit options desk is a separate crypto options source and must retain its own provider, units, expiries and contracts.
- Do not infer global market depth from one exchange. OKX/Hyperliquid order books and trades are venue-specific observations.
- Do not reconstruct historical resting liquidity from OHLCV or trade candles. Historical depth requires a recorded depth feed with sequence continuity, reconnect/resync logic and gap markers.
- Keep executed trades, resting orders, estimated liquidity, liquidation estimates and options-derived positioning as distinct evidence types.
- Existing Radar, Workspace, Technical Office and Options Desk remain authoritative modules. Integrate by explicit contracts; do not duplicate their state or silently change existing behavior.

## 4. Owner policy and dependencies

- Risk per trade remains unresolved between 0.25% and 0.5% in the branch's own review notes. Until resolved, preserve it as a configurable, versioned policy requiring explicit selection; do not wire a default as an approved account rule.
- Cboe live access was not validated in this review. A user-side browser check may help validate reachability, but must not be described as a reproducible server-side integration test.
- The branch's note says GitLab CI has not run because runner/configuration is absent. No passing pipeline is claimed here.

## 5. Recommended order of work

1. Keep the current Order Flow branch isolated and unmerged.
2. Harden and test the risk calculation contract, including open and unrealized risk, before connecting it to any decision surface.
3. Keep GEX as an optional delayed context panel only after source, multiplier, gamma basis and data-quality checks are explicit.
4. Audit the actual OKX/Hyperliquid WebSocket ingestion and browser workspace independently: sequence numbers, reconnect/resync, timestamp age, gap detection, duplicate events and bounded history.
5. Add a separate historical-liquidity recorder only from real depth messages; no candle-derived substitute.
6. Add integration tests and a full UI regression pass before merging.
7. Preserve human approval for any trade decision; this module must not place live orders.

## Status

**Audit completed; no code from the Order Flow branch merged or modified.** This is a source-level review, not a live provider validation or full test run.
