# AI Trading Dashboard — Conversation & Work Recovery Archive

**Purpose:** durable source of truth for project decisions and work across ChatGPT conversations. This archive is inside the repository so a lost, crashed or inaccessible chat does not erase the engineering context.

## Current project pointer
- Project: `6868-group/ai-trading-dashboard`
- Project ID: `88622818`
- Current working branch for this work: `feat/radar-market-intelligence-foundation`
- Draft MR !46: https://gitlab.com/6868-group/ai-trading-dashboard/-/merge_requests/46
- Status: registry/router and TIA guidance adapter committed; platform UI coverage audit added; no page consumer of shared router found yet; MR remains Draft/unmerged and 30 commits behind main; latest pipeline failed with zero jobs; tests have not been executed.

## Read these first when resuming
1. [New-chat recovery prompt](TIA_RECOVERY_PROMPT.md) — copy/paste instructions for a new conversation.
2. [Latest guidance adapter increment](sessions/2026-11-10-guidance-presentation-adapter.md) — reusable TIA-owned view-model contract and tests (not yet executed).
3. [Latest platform UI coverage audit](TIA_PLATFORM_UI_COVERAGE_AUDIT.md) — route inventory, consumer search evidence, surface matrix and prioritized integration backlog.
4. [Latest CI/MR close-out note](sessions/2026-11-10-ci-coverage-and-mr-blockers.md) — verified blockers and CI coverage update.
5. [Latest ChatGPT session record](sessions/chatgpt-2026-11-10-platform-knowledge-router.md) — original request, decisions and implementation.
6. [Shared platform knowledge router](TIA_PLATFORM_KNOWLEDGE_ROUTER.md) — architecture and integration contract.
7. [Gann research playbook](TIA_GANN_RESEARCH_PLAYBOOK.md) — Gann constraints, math, calibration and validation.
8. [Gann/image research index](TIA_IMAGE_RESEARCH_INDEX.md) — archived reference-image inventory and research priorities.
9. [TIA foundation](TIA_FOUNDATION.md) and [TIA agent persistence](TIA_AGENT_PERSISTENCE.md) — TIA architecture and persistence limitations.
10. [TIA meeting room](TIA_MEETING_ROOM.md) — identity, decisions and project references.
11. [Shared agent contract](AGENT_CONTRACT.md) — team ownership, handoffs and review gates.

## Verified work ledger
| Commit | Work | Status |
|---|---|---|
| `0795657f669ae1bb5616707b7d6b75716132e7d1` | Gann and geometry image archive index | committed on working branch |
| `b4721fbdd17a788d551a765efa4cacdb5de4350d` | Gann research playbook and JSON spec | committed on working branch |
| `e740f92e729266d297c11b397035f119baab6dfe` | Cross-platform knowledge registry/router, contract tests and docs | committed on working branch |
| `e166c813e37308ce81d5616f9992d3dd51f90657` | Session recovery prompt and master archive | committed on working branch |
| `f6b5f3d88ae27fa987341c6a1c0a617f2949c8d2` | Expanded TIA CI coverage and documented MR blockers | committed on working branch |
| `bc996f65936c3db563d1e470f69ed63f7245f1a8` | Platform UI coverage audit and recovery-record refresh | committed on working branch |
| `007718114ebaf47315f5c47d09248b081ece40d3` | TIA guidance presentation adapter, tests and CI inclusion | committed on working branch |
| NEXT | Platform UI-to-knowledge coverage audit | added in the current increment |

## Operating rule
Every substantial conversation/work increment must create a new dated note in `docs/sessions/`, then update this archive with a link and the new commit(s). Never overwrite older session records. Distinguish owner decisions, proposals, implemented code, tests actually run, tests not run, and open tasks. Never store passwords, API keys, tokens, private account details or other secrets in this archive.

## Current next action
Follow the prioritized backlog in [the platform UI coverage audit](TIA_PLATFORM_UI_COVERAGE_AUDIT.md). Begin with a reusable TIA-owned presentation adapter and tests, then integrate page-by-page under the ownership rules. Resolve the 30-commit divergence safely and restore CI job creation before treating the MR as mergeable.
