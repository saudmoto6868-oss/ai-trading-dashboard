# Spot page: one-screen key view (2026-11-27)

## Goal (owner)
The key Spot view fits one screen width with **no vertical scroll**. Compact grid of cards, tabs for secondary detail,
collapsed sections. Target screen: **1440 x 900**. Screenshots at deviceScaleFactor 2 for the owner.

## What was there
- The Spot brain tab embedded one fixed-height HTML mosaic (`spot_brain_view.render`) at **1400 px** with scrolling:
  about 12 tiles, two columns, and a long bottom row. At 900 px tall it needs several screens.
- Other tabs were already secondary (ideas, crypto, metals, ledger, alerts, news, storage, analyzer).

## What changed
1. **New key view** `spot_brain_view.render_key()`: a fixed CSS grid, `100vh`, `overflow:hidden`.
   - Top strip: market, price, weekly change, decision (verdict + label).
   - Four horizon cards (day / week / month / year): verdict, score bar, entry / stop / target / R, two reasons.
   - Weekly chart with the plan levels (spans two columns).
   - Flow and COT tiles (funding, OI 7d, long/short, COT commercials).
   - Holdings guard (up to 3 lines), setups (up to 4, spans two), news (2), best entry (buy ladder + invalidation).
   - Footer: rules, not an order and not a promise of profit.
2. **Brain tab**: a radio switch. Default = **Key view** (620 px component, no scrolling). **Full detail** = the old mosaic (1400 px, scrolling), so nothing is lost.
   The thinking log stays in the collapsed expander under the view.
3. Only the selected view renders (Streamlit radio, not tabs), so the other one costs no time.

## How it was checked (and what was NOT)
- `tests/test_spot_key_view.py` (structure, no "None" / "undefined", disclaimer present) reuses the synthetic brain fixture of `tests/test_spot_brain.py`.
- **Playwright, Chromium, synthetic data** (`/opt/pw-browsers/chromium`): at **1440 x 900** and **1440 x 620**
  - no page scroll (document height = viewport height), no horizontal overflow,
  - no clipped card (every card's content fits its box).
  The 620 px case matches the height left for the component under a 900 px screen. The screenshot was reviewed once; then a clipped target value was fixed by letting that line wrap, and the layout was re-measured (not re-viewed).
- **Streamlit AppTest** (requirements installed, network patched to fail): the Spot page renders with 0 exceptions and the View radio is present.
- **NOT measured:** the real Streamlit chrome (top bar, page title, the metals toggle and the tab bar above the component).
  The 620 px budget assumes about 280 px of chrome. Check with the real app on a 1440 x 900 screen and adjust `height=` in `_tab_brain` if needed.
- **NOT tested:** real data. The fixture is synthetic, so line lengths and counts from live feeds may differ. Ellipsis keeps every line in its box, but check the cards with live data.

## Known issues / next steps
- `st.components.v1.html` shows a deprecation warning in Streamlit 1.66 ("will be removed after 2026-06-01"). Migrating to `st.iframe` is a separate task: it changes how the view is embedded in every spot tab.
- The metals/ledger toggle and tab bar take vertical space above the brain view. Moving the toggle into the ledger tab would give the key view more room.
- Checklist and sizing from `modules/spot_checklist.py` are not on the page yet (see `docs/SPOT_PLAN.md`, section 5).
