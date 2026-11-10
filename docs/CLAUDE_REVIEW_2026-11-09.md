# Claude review — Order Flow Desk plan (2026-11-09)

Reviewed: `946ce83a` (MEETING_ROOM Order Flow Desk minutes), branch `work-division` (`docs/MISSING_ITEMS.md`),
branch `team/work-allocation-2026-11-08` (`docs/XPIX_UPDATE_2026-11-08.md`).

## Decisions

1. **Work division (XPiX table): approved as written.** Free models prepare (sources, rules tables, test cases,
   short summaries); Claude decides and writes code. Improvement-researcher (agent 7) output stays a proposal.
2. **Risk policy (owner's later decision, 2026-11-09): 0.25% base per trade; automatic 0.50% only for grade exactly A+ with explicit validation passed and >=30 closed OOS trades for the same setup/rule version.** Malformed or missing validation fails closed to 0.25%. Daily cap 2%, lock after 3 stops, R:R ≥ 1:2. Canonical logic is `modules/risk_policy.py`; no manual selector.
3. **Correction to MISSING_ITEMS:** options flow is not missing — `modules/options_flow.py` (Unusual Whales filter,
   needs `UNUSUALWHALES_API_KEY`) and `modules/cboe_options.py` (free delayed chain, put/call, max pain) exist.
   FRED feed exists (`modules/fred_feed.py`) and a regime module exists (`modules/regime.py`); what is missing is the
   FRED-based *regime signal*, not the data feed.

## Done on branch `claude/order-flow-desk-2026-11-09` (not merged)

| Item | File | Status |
|---|---|---|
| Agent 5 risk manager: size, daily cap, 3-stop lock, R:R, no duplicates | `modules/desk_risk.py` + `tests/test_desk_risk.py` (8 tests) | unit-tested, not wired to UI |
| GEX: call wall, put wall, gamma flip, regime (from Cboe chain) | `modules/gex.py` + `tests/test_gex.py` (7 tests) | **mock-tested only**, not checked on a live chain |

GEX is the naive estimate (dealers long calls / short puts). It is context for agent 2, never an entry signal —
same caveat already written in `modules/flow_manual.py`.

## Next, in order

1. ~~Owner: confirm 0.25 % or 0.5 %~~ → resolved by later owner decision: 0.25% base / 0.50% only for validated A+ with n>=30 closed OOS trades (2026-11-09).
2. Wire `gex.levels()` into the Options desk / Order Flow Desk as a context panel (needs a live Cboe check from the
   owner's browser — the sandbox cannot reach Cboe).
3. Order Flow Desk tab skeleton in `modules/ws/*` (rebuild with `scripts/build_workspace.py`): one view with the
   existing footprint / delta / bubbles / DOM / volume profile + level scanner (agent 1) + risk box (agent 5).
4. FRED regime signal (risk-on/off) with no look-ahead; separate live log from backtest.
5. The five setups: backtest each before any alert — under 30 trades is not evidence.
6. Pipeline permissions on GitLab (no pipeline has ever run here): owner checks Settings → CI/CD → Runners and Variables.
