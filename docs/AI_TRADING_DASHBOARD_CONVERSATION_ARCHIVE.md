# AI Trading Dashboard — Conversation & Work Recovery Archive

**Purpose:** durable source of truth for project decisions and work across ChatGPT conversations. This archive is inside the repository so a lost, crashed or inaccessible chat does not erase the engineering context.

## Current project pointer
- Project: `6868-group/ai-trading-dashboard`
- Project ID: `88622818`
- Current working branch for this work: `feat/radar-market-intelligence-foundation`
- Draft MR !46: https://gitlab.com/6868-group/ai-trading-dashboard/-/merge_requests/46
- Status: knowledge registry/router committed; integrations into all page UIs remain pending; MR not merged; tests added but not run; CI not passed.

## Read these first when resuming
1. [New-chat recovery prompt](TIA_RECOVERY_PROMPT.md) — copy/paste instructions for a new conversation.
2. [Latest ChatGPT session record](sessions/chatgpt-2026-11-10-platform-knowledge-router.md) — exact request, decisions, commits, status and ordered next work.
3. [Shared platform knowledge router](TIA_PLATFORM_KNOWLEDGE_ROUTER.md) — architecture and integration contract.
4. [Gann research playbook](TIA_GANN_RESEARCH_PLAYBOOK.md) — Gann constraints, math, calibration and validation.
5. [Gann/image research index](TIA_IMAGE_RESEARCH_INDEX.md) — archived reference-image inventory and research priorities.
6. [TIA foundation](TIA_FOUNDATION.md) and [TIA agent persistence](TIA_AGENT_PERSISTENCE.md) — TIA architecture and persistence limitations.
7. [TIA meeting room](TIA_MEETING_ROOM.md) — identity, decisions and project references.
8. [Shared agent contract](AGENT_CONTRACT.md) — team ownership, handoffs and review gates.

## Verified work ledger
| Commit | Work | Status |
|---|---|---|
| `0795657f669ae1bb5616707b7d6b75716132e7d1` | Gann and geometry image archive index | committed on working branch |
| `b4721fbdd17a788d551a765efa4cacdb5de4350d` | Gann research playbook and JSON spec | committed on working branch |
| `e740f92e729266d297c11b397035f119baab6dfe` | Cross-platform knowledge registry/router, contract tests and docs | committed on working branch |

## Operating rule
Every substantial conversation/work increment must create a new dated note in `docs/sessions/`, then update this archive with a link and the new commit(s). Never overwrite older session records. Distinguish owner decisions, proposals, implemented code, tests actually run, tests not run, and open tasks. Never store passwords, API keys, tokens, private account details or other secrets in this archive.

## Current next action
Use the ordered tasks in [the latest session record](sessions/chatgpt-2026-11-10-platform-knowledge-router.md). Start by inspecting the actual current branch/MR and then perform the full UI option inventory. Do not assume that a registry route means a page is already integrated.
