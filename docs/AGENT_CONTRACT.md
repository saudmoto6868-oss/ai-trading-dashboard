# Shared agent contract (proposal, 2026-11-09)

Status: PROPOSAL on branch `claude/agent-contract-2026-11-09`. Docs only. Not merged. Review in the meeting room, then the owner.
Owner order (2026-11-09): the three work streams stay SEPARATE in code. They may read each other's ideas, borrow tools, ask each other questions and cooperate, but only through the contract below, never by editing each other's files.

## 1. Three streams, three code areas
| Stream | Who | Code area (only they edit it) | Output |
|---|---|---|---|
| Order Flow Desk | Grok + its free-model agents | `modules/desk_*`, `docs/proposals/grok/` | proposals, rule tables, test cases |
| TIA terminal | ChatGPT | `modules/tia_*`, `docs/TIA_*` | UI shell, brand, geometry views |
| Core / money logic | Claude | `modules/day_plan.py`, `horizons.py`, `brain*.py`, `desk_risk.py`, `gex.py`, `risk_engine.py` | scanner, plans, risk, grading |
Nobody edits `modules/workspace_app.html` directly (generated from `modules/ws/*` by `scripts/build_workspace.py`). Every stream works on its own branch.

## 2. The one shared thing: the agent result
Every agent (Grok's 7 desk agents, TIA's 7 functions, Claude's brain jobs) returns the same JSON object:
```
{
  "agent": "level_scanner",            // stable id, see mapping in section 3
  "stream": "grok|tia|claude",
  "symbol": "HL:xyz:GOLD",
  "verdict": "bullish|bearish|neutral|skip|info",
  "evidence": [{"what": "...", "value": 0, "unit": "pts"}],
  "source": "OKX|Hyperliquid|Cboe|FRED|RSS|lab|manual",
  "ts": "2026-11-09T05:00:00Z",
  "coverage": "which bars / how many / what window",
  "quality": "live|delayed|mock|estimate|missing",
  "n": 0,                                // sample size behind a statistic; n < 30 = NOT EVIDENCE
  "note": "one sentence"
}
```
Rules (from TIA's data-integrity rule + the repo rules): never label mock or estimate as live; no probabilities, only counts of agreeing evidence; no orders; secrets never in the object.

## 3. Role mapping (same job, two names)
| Grok desk agent | TIA function | Existing code in `main` |
|---|---|---|
| 1 level scanner | 4 Order Flow & Liquidity (+3 Technical for levels) | `modules/level_sweeps.py` (prior day / week / month, Asian range) |
| 2 context monitor | 2 Market Intelligence | `news_watch.py`, `event_clock.py`, `regime.py`, `cboe_options.py`, `fred_feed.py` |
| 3 entry trigger | 3 Technical Intelligence | `signals.py`, `pa_patterns.py`, `day_plan.setup_alerts` |
| 4 confluence confirmer | 4 Order Flow & Liquidity | `scorer.py`, `daily_top.py`, `horizons.py` grades |
| 5 risk manager | 6 Quant Validation & Risk | `desk_risk.py` (branch `claude/order-flow-desk-2026-11-09`) |
| 6 skeptic | 7 Trade Review & Decision | `brain.review_text`, `brain.stats` |
| 7 improvement researcher | 5 Strategy & Innovation Lab | `strategy_lab.py` (lab), proposals only |
| (none) | 1 Intelligence Director | `brain_cron.py` is the only orchestrator today |

## 4. How the streams use each other without merging
- Read: any stream may read another's output files / contract objects and docs.
- Borrow: a tool is borrowed by importing a PUBLIC function from `modules/` of another stream (read-only use) and noting it in the meeting room; if the owner stream changes the signature it says so there.
- Ask: questions go in `docs/MEETING_ROOM.md` (single room; TIA's archive `docs/TIA_MEETING_ROOM.md` stays as the identity/asset archive and links back).
- Cooperate: proposals from free models go to `docs/proposals/<stream>/<date>-<topic>.md` (sources, rule table, test cases). Nothing in `proposals/` becomes code without a Claude review and an owner order.

## 5. Gate before anything reaches `main`
1. Own branch, unit tests pass, `tests/test_workspace_parts_sync.py` if the workspace changed.
2. Say what was NOT tested; mock-tested stays labelled mock-tested.
3. Statistics: n >= 30 or it is written as NOT EVIDENCE; a rule goes live only after the lab gate in `docs/PIPELINE.md`.
4. Claude review note in the meeting room, then the owner's explicit "merge N".
5. **Session note (owner rule, 2026-11-09):** every contributor (Grok, ChatGPT / TIA, each Claude session) keeps a note of THEIR conversation and what happened in it, in `docs/sessions/<who>-<date>-<topic>.md` (or inside their own tab / work item for TIA). A short factual log is enough: what the owner asked, what was decided, what was done, what was NOT tested, what is open. No secrets, tokens or personal data in the note. A merge request that has no session note for its work gets one requested at review; it does not block a fix that the owner asked to merge right away.

### Standing merge rule (owner, 2026-11-09)
The reviewer merges finished (non-draft) merge requests from the owner's sessions without waiting for a separate command, after a quick check of: secrets, conflicts, `workspace_app.html` generated from `modules/ws/*`, the evidence rule (n < 30 = not evidence), and the agreed risk numbers. Draft merge requests are not merged until their author marks them ready.

## 6. Owner decisions (2026-11-09) and what is still open
- DECIDED by the owner: the three streams stay separate in code; they may read, borrow, ask and cooperate through this contract. The contract is approved to go to the meeting room.
- Risk per trade — **superseded by the later owner decision recorded 2026-11-09**: base is **0.25%** of equity. Automatic **0.50%** is permitted only for grade exactly A+, `validation_passed` as the literal boolean `true`, and `validation_n` as an integer >= 30 closed out-of-sample trades for the same setup/rule version. No manual selector. Any missing, mock/delayed, malformed, or insufficient validation metadata falls back to 0.25%. Daily max loss 2%, lock after 3 stops, minimum R:R 1:2. Canonical implementation: `modules/risk_policy.py`; browser logic mirrors it.
- MR #3 (TIA shell) review by Claude, read-only: the page code is static (no market data, strings are constants, `unsafe_allow_html` only for fixed HTML) and import-guarded by try/except. ONE behaviour change to decide: `_PAGE_ORDER = [1, 12, 0, 11, ...]` puts Radar FIRST and the Workspace third, while main has the Workspace first; it also breaks the rule "Spot right after Radar" (Spot is now fourth). Suggested order: `[0, 1, 12, 11, 2, 7, 3, 4, 8, 9, 10, 5, 6]` (Workspace, Radar, TIA, Spot) unless the owner wants Radar first. The `_PAGES` comment is stale. No browser / mobile test yet.
- Do the two meeting rooms stay (TIA = identity archive, MEETING_ROOM = decisions)? Proposed: yes, with links.
- GitLab CI: no pipeline has run yet. Needs a runner and variables (owner: Settings > CI/CD) and a `.gitlab-ci.yml` for the Telegram jobs.

## 7. Known problems found while reading the branches
- `feat/academy-intelligence-core` commits a temporary build file `modules/.workspace_app_build.tmp` (5111 lines). Do not merge that file.
- The TIA shell has no browser or mobile test yet.
- GEX is a naive dealer-sign estimate on a delayed Cboe chain, mock-tested only.


## Owner-approved unified risk policy — 2026-11-09
- One deterministic policy for every engine; no user-selectable risk percentage.
- Base risk is 0.25% of equity per trade.
- Automatic step-up to 0.50% only when setup grade is exactly A+, validation explicitly passed, and at least 30 closed out-of-sample trades exist for that setup/rule version.
- Missing validation metadata, mock/delayed evidence, fewer than 30 trades, or any grade below A+ always means 0.25%.
- Daily maximum loss remains 2%; stop after 3 stops; minimum R:R remains 1:2.
- The policy does not authorize automatic order placement. Python engines use modules/risk_policy.py; browser Order Flow Desk mirrors the same fail-closed rule.
