# Learning + AI Enhancement — Existing Platform Direction

Date: 2026-11-17
Owner direction: extend the existing learning and AI experience; do not create a new Academy, duplicate learning platform, or parallel curriculum.

## Owner decision

The owner explicitly clarified:
- Do not create a new Academy.
- The project already has Learning and AI; develop those existing surfaces.
- Reuse and improve the old lessons, schools, references, diagrams, learning path and research material.
- Add assistant-authored lessons where they genuinely add value, inside the existing learning structure.
- Improve the overall presentation and learning experience as appropriate, while preserving the existing project architecture and owner rules.

This direction supersedes the proposed standalone Workspace Academy widget port as a delivery objective. The branch `feat/workspace-academy-widget-port` was created before this clarification and must not be used to create a parallel Academy surface. Its changes remain unmerged and should be treated as superseded/abandoned unless a small part is later proven necessary for the existing Academy.

## Existing surfaces to preserve and evolve

1. **Academy page (PAGE 7)** — `render_academy_page()` in `main.py`, backed by `modules/academy.py`.
   - Existing views: Path, Schools, References, Lab tools.
   - Existing Arabic/English overlays and evidence/verdict labels remain canonical.
2. **AI page (PAGE 5)** — `modules/ai_page.py` + `modules/guide_ai.py`.
   - Mr X chart-aware assistant, shared provider/cache/cost controls, Backtest agent and Agent desk.
3. **Learn & AI hub (PAGE 15)** — retain its existing hub/navigation relationship; improve cross-links rather than create another learning destination.
4. **Trade Intelligence Center (PAGE 17)** — `modules/intelligence_center_ui.py` and Academy Core; shared knowledge, research and Meeting Room remain connected, not a duplicate course system.
5. **Existing Workspace guide** — keep its current role; do not add a second full Academy inside Workspace.

## Verified existing learning assets on current main

- `data/academy.json`: 4 reviewed-structure lesson records (statuses/verdicts retained).
- `data/academy_path.json`: 17 ordered learning-path lessons across 5 levels.
- `data/academy_deep.json`: 9 detailed school curricula.
- `data/academy_refs.json`: 7 preliminary sources and 18 claims.
- English mirrors exist for the lesson set, learning path, deep school curricula and references.
- `docs/academy/` and `docs/academy_en/`: visual, AI and curriculum files.
- `modules/academy_art.py`: existing educational diagrams.
- `modules/academy.py`: canonical loaders, language overlays, schools, path, references and deep lesson helpers.
- `modules/academy_intelligence.py`: shared evidence/knowledge store and review events.
- `modules/ai_page.py` + `modules/guide_ai.py`: existing AI experience.

These are the material to build on; do not duplicate their content into a new database, page, or curriculum.

## Enhancement plan

### A. Unify navigation and learning journey
- Keep the existing Academy, AI and Learn & AI entry points.
- Add contextual links between lessons, relevant school, project tool/widget, AI explanation and Lab evidence.
- Make the learner's next step obvious without adding a competing top-level destination.
- Preserve current navigation indices and page ownership; additive changes only.

### B. Improve lesson presentation
- Use a consistent lesson layout: learning objective, concept, visual/diagram, rules, bullish and bearish examples, execution checklist, common failure modes, evidence grade, source references, quiz/checkpoint and related project tools.
- Reuse existing SVG diagrams and current lesson content.
- Improve search/filter and progress/navigation only where existing state and persistence can support it reliably.
- Keep Arabic original text and English overlays aligned by stable lesson IDs.

### C. Add assistant-authored lessons into the existing system
- Add only non-duplicate lessons that close a real gap in the current 17-lesson path or nine-school curriculum.
- Each addition must include stable ID, source/provenance, learning objective, practical example, caveats, references, and a quiz/checkpoint where appropriate.
- Assistant-authored material starts as `draft` / `hypothesis` or equivalent unverified state; never silently mark it owner-approved, corroborated or empirically validated.
- Add the English overlay for each new Arabic lesson (same stable ID).
- Academy review status and Lab empirical evidence remain separate. Only Lab can establish empirical validation.

### D. Make AI a learning companion, not a competing academy
- AI can explain the selected lesson, translate it into a project-tool walkthrough, quiz the learner, compare competing interpretations, and identify missing evidence.
- Use existing provider selection, cache, quotas and token-budget policy; do not add a second model client or bypass cost caps.
- Feed the AI only concise lesson metadata and bounded chart summaries; never send raw candle history or secrets.
- AI-generated claims must link back to lesson/source records and clearly distinguish fact, interpretation, hypothesis and measured result.

### E. Connect to research and validation
- Link lessons to PAGE 17 shared knowledge records and relevant Lab outputs without copying the canonical evidence into multiple stores.
- Keep the TIA platform knowledge router as read-only guidance; Academy remains the lesson/course source, Academy Core owns durable knowledge records/review events, and Lab remains empirical validation authority.
- Keep LIVE / SNAPSHOT / MOCK ONLY / UNVERIFIED provenance labels visible wherever relevant.

## Non-negotiable boundaries

- No new Academy, parallel course database, duplicate lesson catalog or second AI assistant.
- Do not replace existing lessons; extend them by stable IDs and additive fields/files.
- Do not rewrite Arabic originals while adding English mirrors.
- Do not promote assistant-created content to owner-approved or empirically validated.
- No changes to PAGE 12 or specialist engines outside the approved scope.
- No merge to main or production deployment without owner approval.
- Workspace generated HTML must be rebuilt from `modules/ws/*` only if source parts are changed.
- GitLab CI is currently blocked by `ci_quota_exceeded`; report this honestly and do not claim tests passed without execution.

## Acceptance criteria

1. The current Academy page remains the single canonical learning destination.
2. All existing four lesson records, 17 path lessons, nine schools, seven references and 18 claims remain available after changes.
3. Arabic/English content remains paired by stable IDs.
4. New assistant-authored lessons are clearly labelled draft/unverified with provenance.
5. AI uses the existing provider/cost/cache path and can reference the selected lesson.
6. The learner can move from lesson → relevant tool → AI explanation → Lab evidence without duplicated content.
7. Existing Academy, AI, Learn & AI and PAGE 17 navigation continues to work.
8. Focused tests cover loaders, language overlays, evidence-state handling, lesson links and navigation.
9. Changes are delivered in an MR for review; no automatic merge.

## Current baseline

- Main SHA: `da6ad692c011e12354a958063fed487aff095c27` (rechecked 2026-11-17).
- Working branch: `feat/learning-ai-enhancement`, created from that SHA.
- CI quota issue remains unresolved; test execution must be reported separately from source review.


## Implemented first slice — MR !81

- MR: https://gitlab.com/6868-group/ai-trading-dashboard/-/merge_requests/81
- Branch: `feat/learning-ai-enhancement`
- Added optional selection of one existing Academy Path lesson in Mr X (AI PAGE 5).
- Mr X receives bounded lesson context only: ID/title/school/evidence grade, short concept, evidence note, up to three steps and up to three references.
- Chart context remains the existing compact computed summary; raw candles are not passed to the model.
- Reuses the existing provider, caps and cache; cache key now includes a fingerprint of the selected lesson context.
- Application language is passed from the current i18n setting.
- Added `tests/test_ai_page_academy_context.py` for canonical path loading and bounded/evidence-aware context.
- No new Academy page, lesson catalog, provider or database was created.

### Pipeline result

MR pipeline `3078847264` was created and immediately failed before runner startup. Jobs `streamlit_iframe_migration`, `risk_policy_tests`, `v7_structure_parity` and `mr_tests` all report `ci_quota_exceeded`; all have null `started_at`. No test command ran and no passing test is claimed.


## Cross-conversation research synthesis — applied to the existing Academy

The recovered XPiX decisions reinforce that the Academy must teach the shared decision process rather than present a collection of disconnected indicator schools.

### Unified decision sequence
1. Market regime (trend / range / transition).
2. Higher-timeframe directional bias.
3. Market structure and invalidation.
4. Location (level / zone / liquidity context).
5. Entry trigger (confirmed on closed bars; no future leakage).
6. Order-flow confirmation at the prepared location.
7. Session context and risk gate.

SMC / ICT, Gann, Elliott, Harmonic, VWAP, sessions and other schools remain contextual lenses. They do not independently authorize a trade or override the decision sequence. The order-flow layer is an execution confirmation gate, not a standalone strategy.

### Related project work to reuse, not duplicate
- XPIX SHIX / M7: treat its planned modules as a source of tool mappings and validation requirements; do not claim the port is complete until its own branch and tests establish that.
- Lab 2.6: reuse the existing research and test artifacts; do not create a second Lab or infer validated status from strategy notes.
- RSI Heatmap: treat regime / momentum / timeframe confluence as a discovery and context surface, not an entry signal or proof of edge.
- Risk policy from prior project decisions: teach the risk gate as mandatory; the exact numeric limits must be read from the canonical risk configuration before being displayed as live policy.
- Anti-repaint, closed-bar confirmation, no future leakage, signal deduplication, data-quality checks, out-of-sample / walk-forward and cost-aware measurement are explicit quality topics across the learning path.

### Implemented UI slice
- PAGE 7 Path now contains a collapsed “Unified trade-decision sequence” explainer above the existing course.
- It reuses the current Academy surface and language function; no new page, school, lesson database, provider, or AI client was added.
- The explainer explicitly says contextual schools do not override risk controls or Lab evidence.
- This is an instructional integration only; it does not alter scanner logic, signal generation, execution, risk settings, or PAGE 12.


### Canonical implementation detail
- The seven-step sequence is now exposed by `modules.academy.decision_sequence()` with stable IDs and Arabic/English labels.
- PAGE 7 renders that canonical helper rather than maintaining a second copy of the wording in `main.py`.
- Added `tests/test_academy_decision_sequence.py` to cover stable order/IDs and English overlay selection.
- This keeps the decision model reusable by future Academy / Mr X integration without duplicating definitions.

### Matimatiki 2.6 — reused existing research, not promoted to a lesson
- Added the existing Matimatiki 2.6 workstream to Academy References in Arabic and English using stable source ID `matimatiki-26` and claim ID `m26-01`.
- Preserved its unverified status and linked the existing session report, isolated research README and 2026-11-15 backtest report.
- The reference explicitly separates the 14-candle and time-cycle material, records the 34-trade positive exploratory variant and the distinct negative Hyperliquid indicator-plan test, and warns that their rules/data differ.
- No duplicate 2.6 Lab, approved lesson, strategy engine, or live trading logic was created.
- The Academy references loader overlays the English source/claim text by stable ID; Arabic originals remain intact.
