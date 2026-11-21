# Tabs, Spot integration and next steps (2026-11-15)

Owner asked: merge what is pending, cut the number of top tabs, fold tabs into options, review Spot for the Workspace and the other tools, and say what the visual / thinking layer needs next.

## 1. Done today
- **Merged** `claude/trade-classification-scalp-swing-o4s4vh` into `main` (merge commit `c085a92`). Main had moved (2.6 Strategy Intelligence, V7, Lab, token rules); conflicts were only `docs/ACTIVITY_LOG_AUTO.md` (deleted on main, now git-ignored) and the generated workspace page, rebuilt from the 22 parts.
- **Tests after the merge:** workspace parts sync, Trade Classes engine, JS/Python parity (300 judgements identical), cron dry run, daily research, browser mock (`tests/browser/tclass_mock.js`) all pass. Tests cover synthetic candles only.
- **Top bar 9 -> 7 items.** V7 and 2.6 Lab moved into the Lab hub as sub-tabs (`_HUBS[14]`). Top bar is now: Workspace, Radar, Spot, TIA, Trading, Lab, Learn & AI. Streamlit AppTest on pages Lab / V7 / 2.6 Lab: no exceptions (network blocked).
  - **Reversal note:** the owner had asked for V7 and 2.6 Lab as their own top tabs (2026-11-12 / 11-13). This change overrides that to meet the new "fewer tabs" request. One-line revert: move 18, 19 back into `_PAGE_ORDER` in `main.py`.
  - TIA stays a top tab (reviewer decision 2026-11-09).

## 2. Current tab map
| Top tab | Contents |
|---|---|
| Workspace | Widget dashboard (chart, Setup Card, Trade Classes, Signals, Alerts ...) |
| Radar | Chart scanner |
| Spot | Spot desk: ideas, brain, ledger, analyzer, setup library (own sub-tabs, owner decision 2026-11-09) |
| TIA | Institutional intelligence terminal (own page) |
| Trading | sub-tabs: Journal, Prop Firms, Options & macro, Alerts (+ others in `_HUBS[13]`) |
| Lab | sub-tabs: Technical Office, Research Hub, Playbook, V7, 2.6 Lab |
| Learn & AI | sub-tabs: Academy, AI, Trade Intelligence Center |

Hub rows are already one compact row of sub-tabs, so dropdowns are not needed there.

## 3. Spot: what is and is not in the Workspace
- Spot lives only in Streamlit page 11 (`modules/spot_page.py`, `spot_brain.py`, `spot_ideas.py`, `spot_setups.py`, `spot_ind.py`).
- Telegram has partial Spot: `/spot /inv /find /spotalerts /spotxl /ideas /outlook` (`spot_query.py`, `bot_router.py`). Telegram parts were not run live.
- **Not yet in the Workspace widgets or the Guide.** Candidate widgets: "Spot brain" (4 horizons + holdings guard), "Spot setups" (library + live setups), "Spot ideas" (daily desk). Each reads the same `data/spot` files and the same `spot_setups` evidence file, so no duplicate logic.
- Spot setup evidence (`data/spot_setup_evidence.json`) is weekly, with a luck guard t >= 3. Widgets must show the t and n next to each setup, never a bare plan.

## 4. Visual and "thinking" layer: honest status
- Trade Classes already shows, per idea: the schools, the case for and against, hard stops, a second look, and grades A+ / A / B / C.
- It is still **mock-tested only**: no live prices, no forward trades (n < 30 = not evidence).
- A full "thinking brain" covering every school, news, Spot and the journal in one engine is multi-session work. This doc is the plan, not the build.

## 5. Proposed order (owner to confirm)
1. Add Spot brain + Spot setups as Workspace widgets (read-only, reuse `data/spot`).
2. Add Spot to the Guide's context, so the Guide can answer about Spot setups with their t / n.
3. Unify the "why" card across Trade Classes, Spot and the Radar (same schema: for, against, stop, second look, grade, evidence n / t).
4. Visual upgrade: one marker and chart style shared across Workspace and Spot Analyzer.
5. Run the Telegram Spot jobs once on GitHub (owner presses Run) to see real output.

Not done today: items 1-5 above; live-data checks; any change to the Spot page itself.
