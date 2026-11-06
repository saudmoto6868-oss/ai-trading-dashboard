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
