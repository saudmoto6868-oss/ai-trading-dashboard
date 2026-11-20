# Open items from the owner's requests (2026-11-20)

Branch: claude/trade-classification-scalp-swing-o4s4vh (= main at e824098b). Owner: "do everything left, arrange it with the new situation".

## Done and checked (on main)
- Top bar 9 -> 7; V7 and 2.6 Lab moved into the Lab hub (owner: leave them where they are).
- Spot desk widget in the Workspace: ideas, 4-horizon brain, setups with t / n, markets, log; class filter; brain line on top. Reads docs/spot/snapshot.json (daily, live on main 2026-11-20: 8 markets, 126 setups). Browser-tested on the real file.
- Trade Classes card: Spot brain line (display only; the verdict and the JS/Python parity are unchanged).
- Spot ideas workflow: ran OK on 2026-11-15 and the daily run committed the snapshot on 2026-11-20.

## Not verified
- Telegram delivery of the Spot / Trade Classes messages: the workflow steps succeeded, but the message text was not read (no log access from here).
- Trade Classes on live prices: mock-tested only; no forward trades yet (n < 30 = not evidence).

## Needs an owner decision (not started)
1. "Options" in the Spot universe: there is no options class today. Which options? (Options chain on US stocks via Cboe, or options on the crypto / metals already in Spot?)
2. Visual upgrade: which screen first (Workspace widgets, Spot desk page, or both), and which style reference (the owner's pictures are still waiting, item 26).
3. Unified "why" card: proposed shared shape for every school and desk = verdict, grade, FOR list, AGAINST list, stop, target, evidence (n, t). Confirm before I change the Trade Classes card and the Spot ideas.
4. A+ setups review (docs/research/A_PLUS_SETUPS.md): owner has not reviewed it yet.
5. Backtest of the A+ setups on real candles: needs a GitHub Actions run (sandbox cannot reach the price sites). Costs nothing money-wise, but it is a new workflow; approve to build it.
6. Telegram secrets SPOT_GH_* for the Spot online-ledger alerts: owner action.

## Order once decisions are in
1. Unified why card (item 3) across Trade Classes and Spot ideas.
2. A+ backtest workflow (item 5), results to docs/research/.
3. Visual upgrade (item 2) on the chosen screen.
4. Options class (item 1) only if the owner confirms the source.
