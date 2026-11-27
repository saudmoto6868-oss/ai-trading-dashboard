# Spot desk refactor plan (draft, not started)

Status: PLAN ONLY. No code changed for this. Waiting for the owner's OK in chat.
Branch: `claude/multi-asset-bot-plan-q8fhg8` (PR #297 is a draft: do not mark ready, do not merge). No GitLab push.

## Why
- `spot_brain.run()` calls news, flow, COT, ideas, and setups on every call, even when the brain or the page does not need them.
- `spot_learn.report_ar` is dead in production: only its test uses it. The learning job builds its own report (`spot_learn_job.report_text`).
- Owner direction (relayed 2026-11-27): only the brain decides; every other piece is a tool that runs on demand with a TTL cache; visuals re-render from brain output only; any timeframe can be chosen.

## Steps (each one: small change, tests run, commit, push)
1. **Remove dead code.** Delete `spot_learn.report_ar` and its two asserts in `tests/test_spot_learn.py`; keep `report_text` as the only report. No behaviour change in production.
2. **Lazy tools.** Split `spot_brain.run()` so each input is a tool with its own module and TTL cache: news (`spot_news`), flow (`spot_flow`), COT (`spot_inst`), ideas (`spot_ideas`), setups (`spot_setups`). The brain asks for a tool only when a selected horizon needs it. Unused tools are never imported.
3. **Timeframe skills.** A table of skills, each with a timeframe pair, its own entry/stop/target rules, and its own horizon key:
   - scalp 15m–1H · day 4H–1D · swing 1D–1W · monthly 1W–1M · yearly.
   The brain returns a verdict only for the skills the owner picks. The page shows only the picked horizons.
4. **Visuals from brain output only.** `render_key` / `render` take the brain result and nothing else; they never fetch. Refresh is a button that re-runs the brain.
5. **One-screen check.** Re-run the Playwright check (1440×900 and 1440×620, no scroll, no clipped card) after step 3, because the horizon count changes.
6. **Tests after each step:** `tests/test_spot_*.py` plus `tests/test_spot_key_view.py` and the Playwright check. Mark anything not run on live data as not tested.

## What this does NOT change
- No automatic weight changes (owner rule). The learning loop stays as it is.
- No live orders. Spot stays read-only and suggestion-only.
- Data sources unchanged (OKX / Yahoo / Hyperliquid / CFTC / news feeds).

## Decisions for the owner
1. OK to start steps 1–6 in this order?
2. Timeframe pairs above: keep as written, or change any?
3. Which horizons show by default on the key view (scalp, day, swing, monthly, yearly)?
