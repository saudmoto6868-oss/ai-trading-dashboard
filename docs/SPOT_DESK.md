# Spot desk (page 11, after the Radar)

Real spot trading records for crypto + metals, kept like an institution: every buy / sell with all its details, invoices
and receipts, online storage with full history, an automatic copy on the Mac, alerts, and a Telegram bot that answers
from the same data. Nothing in it places an order.

## Pieces
| File | Job |
|---|---|
| `modules/spot_core.py` | units / karats / EGP, the 30 standard fields (`FIELDS`), costs, ledger -> positions + P&L (metal move vs dollar move), ladder, alerts, Excel export / template / import with column matching, printable invoice |
| `modules/spot_data.py` | live prices: OKX spot, Hyperliquid metals, Yahoo futures history, USD/EGP |
| `modules/spot_plan.py` | long-only plan from the schools on 1D / 1W / 1M (+ yearly). **Not backtested: not evidence.** |
| `modules/spot_store.py` | storage: private GitHub repo when the keys exist, else the server disk |
| `modules/spot_page.py` | the page: Crypto, Metals, Ledger & invoices, Alerts, News & sources, Storage / Excel / fields |
| `modules/spot_query.py` | read-only answers for the Telegram bot |
| `modules/spot_alerts_cron.py` | alerts checked every 30 min on GitHub Actions (page open or not) |
| `tools/spot_backup/` | automatic copy on the Mac every 48 h |

## Records
- Standard fields: date, buy/sell, asset, item type (bar / coin / jewelry / scrap / crypto), net + gross weight, unit, purity,
  price, currency, USD/EGP rate at that time, workmanship per gram, fees, tax, other costs, invoice no., party + phone + tax id,
  channel (B2C / B2B / exchange), payment method, settlement date, status (settled / pending / cancelled), vault / wallet,
  serial no., hallmark, order id, tx hash, reference, notes, files (PDF / image / Excel).
- **My fields:** add any extra column (text / number / date / list) in the "Storage, Excel & fields" tab; it appears in the form,
  the table, Excel, the invoice and the bot. Removing a field hides it; saved values stay.
- Costs that change the P&L: fees + tax + other costs + workmanship per gram x weight. Cancelled records are not counted.

## Excel
- **Export everything:** Transactions (every field + my fields + totals) / Positions / Prices / Guide.
- **Blank form:** the same columns + one example row + a Guide sheet (what each column means, allowed values).
- **Import any sheet** (ours, a shop's, an exchange's): the page matches the columns (English / Arabic names), you fix the
  matching by hand, and you can **save the matching as a named form** for next time. Unmatched columns can be kept inside the record.

## Storage online (owner action)
1. On GitHub create a NEW **private** repository, empty, e.g. `xpix-spot-data`.
2. GitHub > Settings > Developer settings > Fine-grained tokens > Generate: Repository access = only `xpix-spot-data`,
   Permissions > Contents = **Read and write**. Nothing else.
3. Streamlit Cloud > the app > Settings > Secrets, add:
   ```
   SPOT_GH_TOKEN = "github_pat_..."
   SPOT_GH_REPO = "saudmoto6868-oss/xpix-spot-data"
   ```
4. Same two values in this repo's GitHub Actions secrets (for the 30-min alerts) and in `~/.xpix_spot_backup.env` on the Mac.
Every save becomes a commit in that repo = full history (who / when / what changed). If two devices save at the same time
the second one is refused with a message (no silent overwrite). If you already have records on the server disk: download the
ZIP backup BEFORE adding the keys, then restore it after.

## Automatic copy on the Mac
```
bash tools/spot_backup/install_mac.sh            # creates ~/.xpix_spot_backup.env (fill the 2 keys) + the hourly job
python3 tools/spot_backup/spot_backup.py --now   # first copy by hand
```
Every hour (and at login) it checks: if the last good copy is older than `SPOT_BACKUP_HOURS` (48; set 24 or 72 if you like)
it makes `~/XPiX-Spot-Backup/XPiX-Spot-<date>/` (ledger.json + all files + Excel), verifies it, and only then deletes the
older copy (`SPOT_BACKUP_KEEP=1`). Offline -> nothing is deleted. Log: `~/Library/Logs/xpix_spot_backup.log`.

## Telegram bot (read-only)
`scripts/xpix_bot.py` already routes these; any other bot can call `spot_query.handle(text)` -> (reply, files):
| Command | Answer |
|---|---|
| `/spot` | positions, average cost, open P&L in USD + EGP (metal vs dollar part), realized |
| `/inv <no. / shop / date / asset>` | matching invoices; one match -> its files + the printable invoice |
| `/find <text>` | any field, custom fields included |
| `/spotalerts` | active alerts and which are hit now |
| `/spotxl` | Excel of everything |
| free text | `spot_query.llm_context(question)` gives the bot's LLM only the matching rows (small, cheap) |
The bot needs `SPOT_GH_TOKEN` + `SPOT_GH_REPO` in its own environment (the Mac), next to `XPIX_BOT_TOKEN` / `XPIX_OWNER_CHAT_ID`.
It never writes the ledger (adding records from Telegram = later, only with the owner's OK).

## Telegram bot - platform control + spot (owner 2026-11-06)
Write normally in Arabic; `modules/bot_router.py` turns it into SAFE actions (view / screenshot / symbol / timeframe /
widget / indicator / analyzer / briefing / ledger). Nothing places an order. Unknown text -> Claude answers.
| You write | The bot does |
|---|---|
| ابعتلي صورة الدهب على الأسبوعي مع اليوت | Elliott on, gold, 1W, screenshot |
| افتح التايم اند سيلز للبيتكوين | opens Time & Sales, BTC, screenshot |
| افتح تتبع الأوامر وعمق السوق | Limit Tracking + DOM, screenshot |
| شوفلي SMT على الايث 4 ساعات / شيل الجان | indicator on / off + screenshot |
| الدهب هيطلع الأسبوع الجاي؟ | weekly briefing in Arabic + analyzer image |
| وريني المحلل للفضة | analyzer image |
| هات فاتورة INV-12 / مراكزي / اكسل | ledger answers + files |
Commands: `/help`, `/shot BTC 4H`, `/panel tape|dom|ofm|limits|liq|signals|posn`, `/ind ew|gann|smt|div|harm|kz|vp|rsi|macd on|off`,
`/spotchart GOLD`, `/outlook GOLD`, `/spot`, `/inv`, `/find`, `/spotalerts`, `/spotxl`.
**Weekly briefing on its own** (bot running on the Mac): every `XPIX_OUTLOOK_DAY` (0 Mon .. 6 Sun, default 6) at/after
`XPIX_OUTLOOK_HOUR` (default 20, Mac time) for `XPIX_OUTLOOK_SYMS` (default `GOLD,BTC`): this week's move in $/oz (or $ and %),
the typical weekly move (ATR 14 weekly), the side of the schools, where it may go next week (next target / support), ICT zone,
SMC demand zone, Elliott, Gann time window, SMT, the staged buys and the invalidation. Statistical range, not a promise.

## Backtest (runs on its own)
`.github/workflows/spot-backtest.yml` every Monday 03:17 UTC (+ "Run workflow" button): `scripts/spot_backtest.py` walks
crypto majors + gold / silver / copper / platinum week by week (1W + 1M score, no look-ahead), measures 4- and 12-week returns
by score bucket and sends a short Arabic result to Telegram (`TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID`). The Analyzer is an
optional tab (last one, loads only on request) until the result says the score helps.

## Setup library (owner 2026-11-06: "every setup of every school, keep reviewing")
`modules/spot_setups.py`: (1) every Radar detector + harmonic on 1M / 1W / 1D, bullish = buy, bearish = EXIT (spot never
shorts); (2) spot-only setups (CATALOG): Elliott wave 2 / wave 3 go / wave 4 / wave 5 done; hidden / triple / MACD-histogram /
MA-distance / OBV divergence, bearish divergence in the premium; Gann square of 9 + time window, 50 % of the range, 1x1 angle
(scale = half the average bar range, stated), 90 / 180 / 360-day anniversaries; golden / death cross, 200-week reclaim / loss,
52-week breakout, Bollinger squeeze; Mayer < 0.8 / > 2.4, under the 200-week; COT extremes; funding crowding, CVD absorption.
Weekly lab `scripts/spot_setups_lab.py` (in spot-backtest.yml, Mondays): each setup on 1W (8-week return) and 1D (10-day),
walk-forward on 18 markets vs the baseline, no overlap, Welch t; 'worked' needs n >= 30 AND t >= 3 (about 90 setups are tested
together, so t = 2 happens by luck). Results committed to `data/spot_setup_evidence.json`, shown next to every live setup,
in the library tab and used by the brain (setups the lab found worse are ignored). New ideas: school-review topic
`spot_setups`. Adding a setup = one CATALOG entry + one rule in `spot_only`; the next Monday measures it.

## Spot brain (first tab, owner 2026-11-06: "a mastermind for spot only")
`modules/spot_brain.py`: one market -> verdict on 4 horizons (day 1-3 d: 4H + order flow + news; week 1-4 w: 1D + 1W + recipes;
month 1-3 m: 1W + 1M + ICT zone + COT; year 6-12 m: 1M + 200-week avg / Mayer / drawdown + COT) -> buy / accumulate / wait /
reduce / sell-protect with entry, stop, target; plus a holdings guard for every ledger position (hold / reduce / protect / exit).
Order flow `spot_flow.py` (OKX: T&S 500 prints, 24 h taker CVD, book 400 levels, OI, funding, long/short, Coinbase premium,
7-day volume profile = footprint-lite; Hyperliquid for metals / oil). Institutions `spot_inst.py` (CFTC COT, legacy report,
3-year COT index of commercials and large speculators; codes checked with Equibles). Screen `spot_brain_view.py` = mosaic
in the reference-picture style. Bot `/brain GOLD` or «اعمل إيه في الدهب»; the daily Telegram job also sends GOLD + BTC brains.
Not backtested per horizon; CFTC / OKX rubik / Coinbase endpoints not reachable from the sandbox (parsers tested with sample JSON).

## Daily ideas desk (second tab, owner 2026-11-06)
`modules/spot_ideas.py` thinks about spot trades on 8 markets (gold, silver, copper, oil, EUR/USD, BTC, ETH, SOL) from the
1M / 1W / 1D / 4H readings + the Radar detectors + chart patterns + tagged news (`spot_news.py`, keyword rules EN / AR):
7 recipes - discount accumulation (SMC + ICT), 20 / 55-week breakout retest (classic / Turtle), bullish chart pattern,
Elliott ABC end + daily CHoCH, RSI divergence in the discount, Gann level + time window, avoid / take profit (premium).
An idea needs its first structural target >= 1.5 R. Each card: own chart, entry ladder, stop, targets, schools that agree,
base + alternative scenario, KPIs, news. The thinking log says what was checked and why an idea was rejected.
`modules/spot_board.py` draws it (reference picture style). Page: cached 6 h + Refresh + "Send to Telegram".
Daily Telegram: `.github/workflows/spot-ideas.yml` 04:41 UTC (picture + text); bot `/ideas` or «أفكار السبوت».
Not backtested; mock-tested only.

## Keys / secrets summary
| Name | Where | Why |
|---|---|---|
| `SPOT_GH_TOKEN`, `SPOT_GH_REPO` | Streamlit Secrets + GitHub Actions secrets + Mac (`~/.xpix_spot_backup.env`, bot env) | online storage |
| `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | Streamlit Secrets + GitHub Actions (already used) | alert messages |
| `XPIX_BOT_TOKEN`, `XPIX_OWNER_CHAT_ID` | Mac env (already used by the bot) | bot commands |

## Not done / honest
- Mock-tested only (sandbox cannot reach OKX / Yahoo / Hyperliquid / GitHub API); the GitHub store was tested against a fake API.
- The plan is not backtested; alerts fire at most every 30 min (GitHub schedule can be late).
- Instagram / TikTok reading is not built (needs a scraping service key + owner decision).
