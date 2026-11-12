# Open-source tools from Grok's list — what is worth trying (Claude, 2026-11-09)

Rule from the minutes: community code is a starting point to TEST, never a source of decisions. Nothing below is installed or
merged. Licences come from web listings (not the LICENSE file itself) unless marked otherwise: re-check before copying any code.

| Tool | What it is | Licence (as listed) | What we already have | Verdict |
|---|---|---|---|---|
| Freqtrade | full crypto bot: backtesting, hyperopt, FreqAI, Telegram | GPL-3.0 | our own backtests (`strategy_lab`, `of_setups_bt`), Telegram bot | **Do not merge code.** GPL-3.0 would pull the dashboard under GPL if we ever distribute it. Useful only as an outside cross-check: run one of our rules in Freqtrade and compare trades. Optional, low priority. |
| vectorbt (open-source) | fast vectorised backtests / parameter sweeps | Apache 2.0 + Commons Clause (no selling software whose value is vectorbt) | slow per-bar loops in the lab | **Worth a trial in the lab only** (research dependency, not in the app): parameter-robustness sweeps for the strategy lab and the 5 order-flow setups. vectorbt PRO is a separate paid, non-commercial licence: no. The "VectorBT MCP server" is a third-party wrapper: not reviewed. |
| smartmoneyconcepts (joshyattridge) | Python SMC indicators: FVG, order blocks, BOS / CHoCH, liquidity | not confirmed in this search | our own SMC / ICT detectors (`signals.py`, Workspace) | **Use as a parity check, not a replacement:** a test that runs both on the same candles and lists where they disagree (finds bugs in ours). Confirm the licence first. |
| daily_stock_analysis (ZhuLinsen) | LLM stock analysis for A/H/US markets + scheduled push | MIT | Spot brain / ideas desk, Telegram digests | **Ideas only** (report layout, push channels). Its market focus (China A/H shares) and LLM verdicts do not fit our evidence rules. |
| smc-icm-trading (GdotAiM), pyvsmc, ClawStreet | SMC workspace / numpy-polars SMC library / OpenClaw trading skill | not verified | — | **Not reviewed:** no confirmed source or licence found yet. Skip until someone links the repo and its LICENSE. |

Suggested next step (if the owner wants one): the smartmoneyconcepts parity test, because it can catch errors in detectors the
scanner already uses. The vectorbt trial waits for real data (GitLab CI needs identity verification first).

Sources (web listings, 2026-11-09): pypi.org/project/smartmoneyconcepts, github.com/joshyattridge, awesome.ecosyste.ms (freqtrade),
sourceforge.net/projects/freqtrade.mirror, vectorbt.dev/terms, vectorbt.pro/terms/software-license, ossinsight.io (daily_stock_analysis).
