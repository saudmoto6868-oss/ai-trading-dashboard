# New-chat recovery prompt — AI Trading Dashboard / TIA

Copy the full text below into a new ChatGPT conversation:

---
You are continuing my existing AI Trading Dashboard project. Do not start over and do not ask me to repeat decisions already recorded.

**First, inspect the GitLab repository and recover the project state from these authoritative records:**
- Project: `6868-group/ai-trading-dashboard` (ID `88622818`)
- Branch: `feat/radar-market-intelligence-foundation`
- Draft MR !46: https://gitlab.com/6868-group/ai-trading-dashboard/-/merge_requests/46
- Session record: `docs/sessions/chatgpt-2026-11-10-platform-knowledge-router.md`
- Recovery prompt: `docs/TIA_RECOVERY_PROMPT.md`
- Master archive index: `docs/AI_TRADING_DASHBOARD_CONVERSATION_ARCHIVE.md`
- Shared knowledge architecture: `docs/TIA_PLATFORM_KNOWLEDGE_ROUTER.md`
- Registry: `data/tia_platform_knowledge_registry.json`
- Router: `modules/tia_knowledge_router.py`
- Gann research: `docs/TIA_GANN_RESEARCH_PLAYBOOK.md` and `data/tia_gann_research_spec.json`
- Image research: `docs/TIA_IMAGE_RESEARCH_INDEX.md` and `data/tia_image_research_index.json`

**Important commits already made:**
- `0795657f669ae1bb5616707b7d6b75716132e7d1` — Gann/image archive index.
- `b4721fbdd17a788d551a765efa4cacdb5de4350d` — Gann research playbook/spec.
- `e740f92e729266d297c11b397035f119baab6dfe` — shared cross-platform knowledge router.

**My requirement:** Build one canonical knowledge and guidance system for the entire platform, not just Gann or TIA. It must serve Workspace, Radar, Spot, TIA, Trading Lab, Learn & AI, Order Flow Desk, Footprint, patterns, indicators and every other discovered option. The Intelligence Director/mastermind should select the right schools and specialists for each page/task, explain how to think and analyze, specify data requirements, confirmation, invalidation, next actions and links to learning/lab evidence.

**Continue with these rules:**
1. Read the session record and current code before making changes.
2. Audit every page and every option/control; record coverage explicitly.
3. Use the shared read-only API `load_registry()`, `resolve_guidance(page, feature, task=None, available_data=None)`, `list_routes()`.
4. Extend the canonical registry instead of creating duplicate knowledge silos.
5. Missing/stale/partial data must be shown as a gate; never fabricate Flow, DOM, Footprint, Volume Profile, options or live values.
6. Keep spot separate from derivatives and keep venue-specific books separate.
7. Gann, Elliott, SMC/ICT and Harmonic remain context/hypothesis methods until validated; Price Action/Trend are candidates, not guaranteed edge. Order Flow is a confirmation gate. Indicators must not be double-counted.
8. No repainting, no future leakage, stable Gann anchors, frozen price/time calibration, and no chart scale distortion.
9. Preserve ownership boundaries: TIA owns `modules/tia_*` and `docs/TIA_*`; do not edit Claude/Core brain/risk/horizons/GEX files or Grok's `desk_*` files without their owner review. Never edit generated `modules/workspace_app.html` directly; edit `modules/ws/*` and rebuild.
10. Do not merge MR !46 or deploy without the required review/owner approval. Do not claim tests or CI passed unless actually executed.
11. No live orders or external actions without explicit action-specific approval.
12. After every meaningful work increment, save a dated session note in `docs/sessions/`, update the archive index and add an MR note.

**Next task, in order:** inspect current GitLab branch/MR and repository; run safe local targeted tests if possible; perform a complete live UI option inventory; map every option to knowledge routes and data gates; integrate the router page-by-page (Workspace → Radar → Spot → TIA → Trading Lab → Learn & AI; Order Flow Desk via read-only contract); add tests and desktop/mobile checks. Continue primary-source Gann research and the historical case ledger after that.

Work directly and report what was actually changed, what was not done, test status, commit IDs and the exact next action. Do not give me a plan only when a safe direct implementation step is available.
---

## If repository tools are unavailable
Ask me to reconnect GitLab or provide access to the project. Do not reconstruct the code from memory or invent file contents. Use the session record as the decision source and clearly mark anything you cannot verify.
