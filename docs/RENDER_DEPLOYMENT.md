# XPiX — Render staging deployment

## Scope
This Blueprint creates a **staging-only** Streamlit web service. It does not deploy to production, change GitLab `main`, merge any MR, run a trading workflow, or configure broker access.

## Blueprint
- File: `render.yaml`
- Service: `xpix-ai-trading-dashboard-staging`
- Runtime: Python 3.11.11
- Build: `pip install -r requirements.txt`
- Start: `streamlit run main.py --server.address 0.0.0.0 --server.port $PORT --server.headless true`
- Health check: `/_stcore/health`
- Auto deploy: disabled; deploys are manually triggered after review.
- Plan: Free for a first staging smoke test only.

## Important persistence warning
Render Free web services have an ephemeral filesystem and can spin down/restart. The configured Academy SQLite path under `/tmp` is deliberately temporary for staging; do not store authoritative knowledge or user data there.

The Spot ledger uses the private GitHub store only when both `SPOT_GH_TOKEN` and `SPOT_GH_REPO` are configured. Without them, Spot falls back to local disk and data can be lost on a restart. Configure these only with a fine-grained token scoped to a dedicated **private** data repository; never put the token in Git.

The Academy module can use PostgreSQL via `DATABASE_URL`, but a production database has not been provisioned or migrated in this change. Do not treat the staging SQLite database as persistent. Before production, provision a paid persistent datastore or complete a tested PostgreSQL migration and backup/restore test. Free Render Postgres expires after 30 days and is not suitable as the production store.

## Optional environment secrets
Set only the providers the owner intends to use:
- `ANTHROPIC_API_KEY`, `GUIDE_PROVIDER=claude`, optional `GUIDE_MODEL`
- `GEMINI_API_KEY` (or `GOOGLE_API_KEY`), optional `GEMINI_MODEL`
- `FINNHUB_API_KEY`, `FINNHUB_WS_TOKEN` (browser-visible; separate from the server key)
- `FRED_API_KEY`, `CURRENTS_API_KEY`, `TWELVEDATA_API_KEY`, `ALPHAVANTAGE_API_KEY`
- Telegram: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` (leave disabled until explicitly configured)
- Spot persistence: `SPOT_GH_TOKEN`, `SPOT_GH_REPO`, optional `SPOT_GH_BRANCH`
- `APP_USERS` or `APP_PASSWORD` only when the owner is ready to turn on login. The repository explicitly says the auth gate is off until launch.

Never commit secret values. Never reuse broker credentials.

## Go-live checklist
1. Connect the GitLab repository to Render and select branch `deploy/render-xpix-staging`.
2. Review the Blueprint diff and confirm the free staging service.
3. Deploy manually; inspect build logs and `/_stcore/health`.
4. Verify app startup and each data source independently; record Live / Delayed / Fallback / Offline with timestamps.
5. Test Workspace, Radar, Spot, TIA, Trading Lab, Learn & AI and Order Flow Desk on desktop and mobile.
6. Verify Spot ledger persistence and Academy persistence/backup before any production use.
7. Upgrade compute/database only after the owner reviews the current Render price and approves the recurring cost.
8. Keep production deployment separate and require explicit owner approval.

## Current known constraints
- MT5 Python integration is Windows-only; it will not work on Render's Linux runtime. Use the existing supported public data providers instead.
- External market APIs may be blocked, rate-limited, delayed or require keys. A configured adapter is not proof of a live feed.
- The existing CI pipeline issue (failed pipeline with zero jobs on MR !46) is not fixed by this Blueprint. CI must be repaired and run before production.
