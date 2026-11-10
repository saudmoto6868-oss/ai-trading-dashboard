# Session note — Claude, 2026-11-09 (Order Flow Desk day, GitLab)

**Asked (owner):** status on GitLab; fix the chart Manual/Auto problem (ChatGPT's fix did not hold); do everything that is
missing in order; adjust the look to the owner's picture; risk 0.5 % ("خليها نص"); delete ChatGPT's branch.

**Decided:** risk 0.5 % per trade (owner, directly); every change on its own branch, merged after a check; GEX and the FRED regime
are context, never entry signals; n < 30 = not evidence.

**Done (merged):** chart fully manual scale + no Manual/Auto button / Auto-Center (owner tested: works); time-axis dates;
Order Flow Desk widget; desk_risk + GEX + Options-desk GEX panel; FRED macro regime tab; order-flow setups backtest engine +
runner; Order Flow Map back in the widget menu; Gold Noir theme; brain plans show position size; branch review;
PROJECT_STATUS conflict markers removed. ChatGPT's MR !2 closed.

**NOT tested:** anything on live data (sandbox has no market access); the full app was not run here (no checkout) — UI pieces
were smoke-tested on stub pages / a stubbed Streamlit; the 5-setup backtest has NO results yet.

**Open / blocked:** GitLab identity verification (all CI fails without it) -> then run `of_setups_bt` on real trades;
delete branch `fix/manual-price-scale-lock` (UI only); risk policy was resolved by a later owner instruction (see correction below); draft MRs of other agents wait for their authors.


## Owner correction — 2026-11-09 (later than the original session decision)
The earlier flat 0.5% note above is superseded. The current policy is 0.25% base risk; 0.50% only automatically for grade exactly A+ with literal boolean validation_passed=true and integer validation_n >=30 closed out-of-sample trades for the same setup/rule version. Missing or malformed evidence stays at 0.25%. No manual selector. Daily cap 2%, lock after 3 stops, minimum R:R 1:2. See `modules/risk_policy.py` and MR !47.
