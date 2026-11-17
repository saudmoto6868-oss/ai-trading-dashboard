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
