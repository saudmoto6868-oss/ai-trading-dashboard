


## 2026-11-17 — Render staging preparation (ChatGPT)
- Created branch `deploy/render-xpix-staging` from current `main` at `da6ad692c011e12354a958063fed487aff095c27`.
- Added a Render Blueprint for a **Free staging-only** Streamlit service; manual deploy only, health check `/_stcore/health`. No production deployment or main-branch change.
- Added `docs/RENDER_DEPLOYMENT.md` documenting startup, optional secrets, Spot GitHub persistence, Academy SQLite ephemeral limitation, MT5 Linux limitation, and go-live checks.
- The staging service is not yet created in Render. Render account connection is still required. Do not enter paid compute or database plans without owner approval.
- No market feed was contacted from this change; no tests or live browser checks have run yet.
