# AI Trading Dashboard — Conversation & Work Recovery Archive

**Purpose:** durable repository record of project decisions, implementation boundaries, and recovery instructions.

## Current source of truth
- Project: `6868-group/ai-trading-dashboard` (ID `88622818`)
- Current base used for the isolated documentation increment: `main` at `4ba86a1da43d848ebb06df8db66e2d1f5a2a796c`.
- Documentation increment: `docs/tia-recovery-image-index-2026-11-10` (Draft MR will target `main`).
- Image index in repository: [docs/TIA_IMAGE_RESEARCH_INDEX.md](TIA_IMAGE_RESEARCH_INDEX.md)
- Machine-readable image index: [data/tia_image_research_index.json](../data/tia_image_research_index.json)
- New-chat recovery instructions: [docs/TIA_RECOVERY_PROMPT.md](TIA_RECOVERY_PROMPT.md)

## Work split and ownership
1. This increment contains documentation/archive/recovery/image-index material only.
2. The independent knowledge-router increment is tracked on a separate branch and MR: router module, registry JSON, and focused tests only.
3. The TIA guidance presentation adapter and `modules/tia_page.py` integration are intentionally deferred to the final increment. Before touching the page, inspect current `main` and preserve its workspace toolbar, `tia_mkt`/`tia_sym`/`tia_run` URL handling, and Director report placement below the workspace.
4. No merge of `main` into !46 is required or authorized by this work. The owner will resolve !47 from GitLab UI.
5. Do not rebase, force-push, edit files owned by another contributor, or deploy. No live orders or automated execution.

## Reference archive
The 30 numbered reference images are retained in the user's Library under `/TIA Image Research/Originals/`, named `TIA-Reference-01.jpg` through `TIA-Reference-30.jpg`. The JPEG binaries are not copied into this repository; the repository stores their index and research metadata only.

The index distinguishes:
- Order-flow / footprint and auction/profile material from true dashboard UI design.
- Gann wheels and radial geometry from a radial dashboard widget.
- Concept references from validated trading rules.

No image-derived concept authorizes order placement. OHLCV does not reconstruct true volume-at-price or classified footprint prints.

## Recovery procedure
1. Read this archive and `docs/TIA_RECOVERY_PROMPT.md`.
2. Check the current `main` SHA and open MRs before continuing; do not assume this archive's commit state is still current.
3. Review each isolated MR and its actual pipeline/jobs. A pipeline request or zero-job pipeline is not a passing test.
4. Keep documentation, shared knowledge routing, and guidance UI integration as separate review units.
5. Preserve owner decisions and report exact changed paths, SHAs, pipeline IDs/statuses, and anything not tested.

## Evidence discipline
Record separately: source material, extracted descriptions, implemented code, tests actually run, tests not run, and unresolved assumptions. Never invent image mappings, live data, agent completion, or test results. Never store credentials, API keys, tokens, or private account details here.
