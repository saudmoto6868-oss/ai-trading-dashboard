# Claude branch review — 2026-11-09

Rule (owner, 2026-11-08): every agent works on its own branch; nothing goes to `main` without Claude's approval.
Read-only review of what is open on GitLab today. "Not merged" below is a decision, not a missing step.

| Branch / MR | What it is | Verdict |
|---|---|---|
| `fix/manual-price-scale-lock` (!2, ChatGPT) | removed one line in the GENERATED `workspace_app.html` only | **Close.** Superseded by !6 (merged, owner-tested). A direct edit of the generated file is overwritten by the next build and fails `test_workspace_parts_sync`. MR closed; the branch itself must be deleted from the GitLab UI (no delete tool here). |
| `feat/tia-evidence-contracts-and-room-assets` (!4, draft) | evidence contract + FRED / CMC adapters, TIA page | **Keep draft.** Tests not run by the author. Before merge: run `tests/test_tia_*.py`; check that `tia_integrations` uses the new keyless `fred_regime` CSV or `fred_feed` (key) consistently. |
| `feat/tia-institutional-operating-model` (!5, draft) | operating model docs + label fixes in `tia_page.py` | **OK to merge after !4 / !7 are settled** (all three edit `modules/tia_page.py`: merge one, rebase the others). Docs only otherwise. |
| `feat/tia-native-knowledge-and-meeting-services` (!7, draft) | SQLite knowledge registry + meeting journal | **Keep draft.** Tests added but not run; Streamlit Cloud wipes local SQLite on restart, so this is not durable storage. |
| `audit/order-flow-risk-gex-review-2026-11-09` (!8, draft) | audit of my risk / GEX branch | **Useful; merge as a doc.** Risk is now resolved by the later owner policy: 0.25% base / 0.50% only for validated A+ with >=30 closed OOS trades; the GEX multiplier is a parameter (Deribit 1, US 100). Still open and true: open-position risk is not counted, daily state lives in the browser journal, GEX dealer sign is an assumption. |
| `feat/xpix-shix-m7-port-audit` (!10, draft) | audit + port plan for the M7 Pine indicator | **Merge as docs** when the owner wants; no code. |
| `feat/tia-risk-engine-contract-v1` (!13, draft) | larger risk engine (open risk, ledger, sizing) | **Retarget to `main`** (its target branch `claude/order-flow-desk-tab-2026-11-09` was merged and deleted); it now shows conflicts. The 0.25 vs 0.5 question is superseded by the later owner policy: 0.25% base / 0.50% only for validated A+ with >=30 closed OOS trades. Later it can replace `DeskRules` behind the same check() interface. Tests not run by the author. |
| `feat/academy-intelligence-core` | Academy knowledge work | **Do not merge yet.** Reported to contain `modules/.workspace_app_build.tmp` (build leftover, must be removed) and a page-index 12 clash with the TIA page (see !5's audit). |
| `team/tia-intelligence-terminal-2026-11-09` | TIA meeting-room archive view | Older than the merged TIA page (`09f6e43d`): check whether anything is not in `main` before deleting. |
| `team/work-allocation-2026-11-08`, `work-division` | Grok / XPiX planning docs | Approved in `docs/CLAUDE_REVIEW_2026-11-09.md`; can be deleted after the owner reads them. |
| `feat/brain-v2`, `claude/agent-result-2026-11-09`, `claude/gitlab-ci-2026-11-09` | already merged | Can be deleted. |

Not checked: none of the other agents' tests were run here (the cloud session has no checkout of the repo); the verdicts
above are from the merge requests' own descriptions and file lists.
