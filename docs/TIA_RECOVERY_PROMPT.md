# New-chat recovery prompt — AI Trading Dashboard / TIA

You are continuing the existing `6868-group/ai-trading-dashboard` project (project ID `88622818`). Do not restart the project or ask the owner to repeat decisions already recorded.

## First recovery steps
1. Read `docs/AI_TRADING_DASHBOARD_CONVERSATION_ARCHIVE.md`.
2. Check the live GitLab state: current `main` SHA, open MRs, branch heads, pipelines and actual jobs. Do not trust stale status text without rechecking.
3. Read `docs/TIA_IMAGE_RESEARCH_INDEX.md` and `data/tia_image_research_index.json` for the 30 reference-image inventory.
4. Keep the work split into small isolated MRs created from current `main`.

## Current work boundaries
- Documentation/archive/recovery/image index is one independent increment.
- Shared knowledge routing is a separate increment containing only:
  - `modules/tia_knowledge_router.py`
  - `data/tia_platform_knowledge_registry.json`
  - `tests/test_tia_knowledge_router.py`
- Guidance presentation adapter and `modules/tia_page.py` integration are last. Before implementation, read the current `main` version of `modules/tia_page.py` and preserve:
  - market/symbol/Run Director toolbar controls inside the workspace;
  - URL parameters `tia_mkt`, `tia_sym`, `tia_run`;
  - Director report below the workspace.
  Add the read-only guidance panel after the Director report. Do not modify `modules/tia_workspace.py`.
- !46 does not need a merge from `main`. !47 is not to be integrated by this agent; the owner will resolve its conflicts in GitLab UI.
- Do not copy or overwrite files modified by other contributors. Do not force-push or rebase. Do not merge or deploy without owner approval.
- No automated trading or order execution.

## Shared knowledge router contract
The public API is:
- `load_registry()`
- `resolve_guidance(page, feature, task=None, available_data=None)`
- `list_routes()`

The router is read-only decision support. Missing data must produce explicit gates; never fabricate Footprint, DOM, Flow, Volume Profile, options or live values. Keep Spot separate from derivatives and keep venue-specific books separate. Unknown routes fail closed. Gann, Elliott, SMC/ICT and Harmonic remain hypotheses/context until independently validated.

## TIA reference image guidance
The 30 images are in the user's Library at `/TIA Image Research/Originals/TIA-Reference-01.jpg` … `TIA-Reference-30.jpg`. Binary images are not committed to the repository; the index is:
- `docs/TIA_IMAGE_RESEARCH_INDEX.md`
- `data/tia_image_research_index.json`

Treat #06 as the clearest footprint/order-flow visual reference; #03–05 as profile/auction context; #30 and #23–29 as radial/Gann/cycle research, not automatically a radial dashboard component. No dedicated heatmap dashboard reference has been confirmed from the numbered set; do not label one as such without inspecting the image. These are concept/research references, not a complete TIA dashboard design specification.

## CI and evidence
A pipeline is real only when GitLab returns a pipeline ID and its jobs are inspected. A zero-job pipeline, blocked pipeline creation, or request alone is not a test pass. Report compile/tests/smoke checks only when they actually ran, with exact job evidence. Preserve failed and inconclusive outcomes.

## Operating procedure
Work directly when safe. Use new branches from current `main` for each independent increment, use Commit API file actions for new files only, open small Draft MRs, and record their exact paths, SHAs, pipeline IDs, jobs and remaining blockers. Never claim Claude, Grok, Antigravity, Gemini or another agent received/finished work without verifiable evidence.
