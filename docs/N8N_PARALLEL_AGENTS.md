# n8n + 7 parallel agents (research / preparation only - nothing built or run)

Status: proposal. The owner's n8n is installed but we do not know where it runs (cloud / self-hosted / which server). Step 0 is to find out.

## Pattern (conductor + 7 workers)
- **Conductor** = main Claude (decides the split, reviews every result, merges, commits).
- **n8n** = the dispatcher: one *Orchestrator* workflow (Webhook or manual trigger) fans out to 7 *Worker* sub-workflows (Execute Workflow node), each worker = AI Agent node (or HTTP call to the Claude API) with one task brief, then a merge step returns the 7 results to the conductor.
- Known caveat (n8n community threads): Execute Workflow nodes can run sequentially inside one execution; true parallelism usually needs (a) the "Wait for sub-workflow completion" option OFF + a webhook callback / wait-for-all loop, or (b) n8n **queue mode** with several workers. Treat "truly parallel" as unverified until tested on his instance.

## How to connect to the project
1. n8n -> GitHub node (or HTTP) with a **fine-grained token limited to this repo**; each worker works on its own branch `agent/<n>-<item>`, opens a PR; only the conductor merges to `main`.
2. Worker brief = one row of `PROJECT_STATUS.md` + `AGENTS.md` house rules (tests, honest-limits, no secrets).
3. Keys live in n8n Credentials, never in the repo or in chat.

## Splitting the remaining items (independent files -> few merge conflicts)
| Agent | Items | Main files |
|---|---|---|
| A1 | 13 Limit Tracking <-> order-book feed | workspace_app.html (Limit panel) |
| A2 | 14 ADX / CCI / SAR (+ the 2 open questions) | signals.py / workspace indicators |
| A3 | 15 SMA 10/40, Donchian 55, cross-sector momentum | strategies + tests |
| A4 | 20 Finviz-style pattern browser | new widget |
| A5 | 21 Arabic translation | arabic.py, T() dicts |
| A6 | 9 leftovers (preset modes, overlay redesign) | workspace_app.html (theme/chart) |
| A7 | Reviewer/tester: runs all tests, checks honest-limits, updates PROJECT_STATUS.md | tests/, docs |
Blocked / not for agents: 1 (needs OKX access), 4, 16 (keys), 18, 19 (credentials), 22 (design decision first).
Conflict risk: A1, A5, A6 all touch `workspace_app.html` (one big file) -> serialize those three or have them work on separate sections and rebase.

## First technical step
Ask the owner (or inspect): is n8n Cloud or self-hosted, version, and is **queue mode** on? Then build ONE worker end-to-end (A2 is the safest) before fanning out to seven.

## Cost / safety
7 parallel agents = 7x token use; set a per-run cap. Do not give workers push rights to `main`.
