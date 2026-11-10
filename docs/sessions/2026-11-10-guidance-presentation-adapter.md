# Session increment — reusable guidance presentation adapter — 2026-11-10

## Implemented
- Added `modules/tia_guidance_panel.py`, a TIA-owned, presentation-neutral adapter around the canonical read-only router.
- The adapter returns a stable view model: status, route, purpose, selected schools, reasoning, missing capabilities, required outputs, next actions, related routes, safety rules and provenance.
- Unknown routes fail closed to a safe unmapped view. Missing capabilities remain visible and explicitly limit specialist checks.
- Added focused tests for Gann reasoning/provenance, missing classified-trade gates and unknown-feature behavior.
- Added the adapter and its tests to the TIA CI compile/test commands.

## Boundaries
- No Streamlit/page owner files changed; no live data calls, scanners, signals, orders or account actions.
- This creates a reusable presentation contract; it does not mean any page has been wired to render it.
- Tests have been added but not executed because the current GitLab pipelines fail before creating jobs (zero jobs observed).

## Next
- Owner-reviewed page integration, starting with a single surface and its actual control inventory.
- Restore CI job creation, then run all targeted tests.
