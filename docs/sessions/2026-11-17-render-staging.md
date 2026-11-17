# XPiX Render staging preparation — 2026-11-17

## Goal
Prepare a safe, separate Render staging deployment from current GitLab main and record the latest Claude/Gemini updates relevant to the existing Guide AI integration.

## Branch
- deploy/render-xpix-staging
- Base SHA: da6ad692c011e12354a958063fed487aff095c27
- Latest commit at checkpoint: ec7db30f915c57d71e3fd753505d52c0b5e59bf5

## Changes
- Added render.yaml: free staging web service, manual deploy only, Streamlit health check.
- Added docs/RENDER_DEPLOYMENT.md: Render startup, optional environment secrets, persistence warnings, staging-to-production checklist.
- Added docs/AI_PROVIDER_UPDATE_2026-11-17.md: official Anthropic and Google update review plus integration recommendations.
- Updated PROJECT_STATUS.md with this checkpoint.

## Decisions
- Do not touch main or MR !46.
- Do not provision paid services or a production database without explicit cost approval.
- Free Render filesystem is ephemeral. Academy SQLite is temporary in staging. Spot requires its existing private GitHub store configuration for persistence. Production requires a tested persistent database/storage plan.
- MT5 Python bindings are Windows-only and will not run on Render's Linux runtime.
- Claude Fable 5.2 / Gemini API model choices are research candidates only; no model IDs or provider defaults changed.
- Render account/plugin connection is not yet confirmed; the Render service has not been created.

## Tests and evidence
- GitLab commits created; no local Python tests, YAML schema validation, browser test, Render build, or live market-data test was executed.
- Official sources reviewed and linked in docs/AI_PROVIDER_UPDATE_2026-11-17.md.

## Next
1. Connect Render integration/account.
2. Create the Blueprint staging service from this branch and inspect deploy logs.
3. Run app smoke tests and verify each feed with timestamps and source labels.
4. Test Spot and Academy persistence before production.
5. Repair CI and only then consider a production release.
