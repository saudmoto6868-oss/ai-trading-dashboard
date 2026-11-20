# TIA — Unified Market Risk Context

## Purpose
The options context and the existing order-flow context are composed as separate evidence components. The composer does not sum unlike measurements, invent a confidence percentage, or allow options positioning to manufacture directional confirmation.

## Existing sources reused
- Crypto options: Deribit's public BTC/ETH option-book summaries and DVOL history through `modules.options_desk`.
- US listed options: Cboe delayed quote chain through `modules.cboe_options`.
- US options gamma context: existing `modules.gex` estimator.

## Interpretation constraints
- Deribit underlying price is the nearest-expiry forward/underlying proxy, not an independently verified spot index.
- Put/call ratios, open interest, volume, max pain and strike walls do not disclose opening/closing intent, dealer inventory, or hedge direction.
- Cboe delayed data is approximately 15 minutes delayed and its public endpoint is undocumented/unofficial.
- Existing GEX assumes calls positive and puts negative; public chain data cannot verify dealer positioning. The estimator uses a multiplier of 100.
- Order-flow context is venue-specific; displayed book depth can be cancelled. Local collection time does not establish provider-event freshness.
- Missing values remain missing. No source is treated as zero when unavailable.

## Safety boundary
The unified object preserves the raw flow and options components. It has no composite score and no execution authority. It does not change position size, leverage, stops, risk limits, or order permissions. Any future predictive use requires separate methodology, provenance, out-of-sample validation, and owner approval.
