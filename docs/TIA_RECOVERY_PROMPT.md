# New-chat recovery prompt — AI Trading Dashboard / TIA

Copy the full text below into a new ChatGPT conversation:

---
You are continuing my existing AI Trading Dashboard project. Do not start over and do not ask me to repeat decisions already recorded.

**First, inspect the GitLab repository and recover the project state from these authoritative records:**
- Project: `6868-group/ai-trading-dashboard` (ID `88622818`)
- Branch: `feat/radar-market-intelligence-foundation`
- Draft MR !46: https://gitlab.com/6868-group/ai-trading-dashboard/-/merge_requests/46
- Master archive: `docs/AI_TRADING_DASHBOARD_CONVERSATION_ARCHIVE.md`
- UI coverage audit: `docs/TIA_PLATFORM_UI_COVERAGE_AUDIT.md`
- Latest CI/MR close-out note: `docs/sessions/2026-11-10-ci-coverage-and-mr-blockers.md`
- Shared knowledge architecture: `docs/TIA_PLATFORM_KNOWLEDGE_ROUTER.md`
- Registry: `data/tia_platform_knowledge_registry.json`
- Router: `modules/tia_knowledge_router.py`
- Gann research: `docs/TIA_GANN_RESEARCH_PLAYBOOK.md` and `data/tia_gann_research_spec.json`
- Image research: `docs/TIA_IMAGE_RESEARCH_INDEX.md` and `data/tia_image_research_index.json`

**Important commits already made:**
- `0795657f669ae1bb5616707b7d6b75716132e7d1` — Gann/image archive index.
- `b4721fbdd17a788d551a765efa4cacdb5de4350d` — Gann research playbook/spec.
- `e740f92e729266d297c11b397035f119baab6dfe` — shared cross-platform knowledge router.
- `e166c813e37308ce81d5616f9992d3dd51f90657` — session recovery prompt and archive.
- `f6b5f3d88ae27fa987341c6a1c0a617f2949c8d2` — expanded CI coverage and MR blocker note.

**Owner objective:** Build one canonical knowledge and guidance system for the entire platform, serving Workspace, Radar, Spot, TIA, Trading Lab, Learn & AI, Order Flow Desk and every discovered feature/control. Intelligence Director selects the relevant schools and specialists by page/task/data capability. Every guidance card must explain reasoning, prerequisites, confirmation, invalidation, limitations, source, evidence status and next action.

**Rules:**
1. Audit every rendered page/control; do not equate registry route presence with UI integration.
2. Shared router API: `load_registry()`, `resolve_guidance(page, feature, task=None, available_data=None)`, `list_routes()`.
3. Search on the current branch found no page consumers of `resolve_guidance`; visual reference catalog has a TIA-specific consumer in `modules/tia_intelligence.py`. Platform-wide integration is still pending.
4. Missing/stale/partial data must be shown as a gate; never fabricate Flow, DOM, Footprint, Volume Profile, options or live values.
5. Keep spot separate from derivatives and venue-specific order books separate.
6. Gann, Elliott, SMC/ICT and Harmonic remain context/hypothesis methods until validated; Price Action/Trend are candidates, not guaranteed edge. Order Flow is a confirmation gate. Indicators must not be double-counted.
7. No repainting/future leakage; stable Gann anchors and frozen price/time calibration.
8. Ownership: TIA owns `modules/tia_*` and `docs/TIA_*`; do not edit Claude/Core brain/risk/horizons/GEX or Grok `desk_*` files without owner review. Never edit generated `modules/workspace_app.html`; edit `modules/ws/*` and rebuild.
9. MR !46 is Draft. Latest observed state reported no conflicts but remained 30 commits behind `main` and `cannot_be_merged_recheck`. Do not rebase forcefully, merge or deploy without safe reviewed procedure/owner approval.
10. Latest pipeline failed with zero jobs; tests have not run. Do not claim CI or tests passed.
11. No live orders or external actions without explicit action-specific approval.
12. After each meaningful increment, create a dated session note, update archive and add an MR note.

**Next tasks:** implement/test a TIA-owned presentation adapter; integrate Workspace → Radar → Spot → TIA → Trading Lab → Learn & AI; Order Flow Desk via read-only owner-reviewed contract. Complete desktop/mobile smoke tests and no-duplicate-feed checks. Safely reconcile branch divergence and restore CI job creation. Continue Gann source crosswalk and historical case ledger afterwards.

Work directly. Report exact changes, tests actually run, uncompleted items, commit IDs and next action. Do not provide only a plan when safe implementation is possible.
---

## If repository tools are unavailable
Ask me to reconnect GitLab or provide access. Do not reconstruct code from memory or invent file contents.
