# Claude (review + brain) session note, 2026-11-09

Who: the Claude session that reviews and builds the brain (Telegram alerts, Top 7, horizons, grading). Language with the owner: Egyptian Arabic, short.
This is a log of what happened, not evidence of anything. No secrets in it.

## What the owner asked, in order
1. Brain v2: news from outside the calendar, previous day / week / month and Asian-range sweeps, a scan of every holding horizon (scalp, day, swing, position) every 4 hours with A+ / A grades, and an experimental adaptive weight per school.
2. When the GitHub account got suspended: a free alternative host (GitLab), a full backup of the repo, getting the dashboard to run on the owner's Mac.
3. Read the meeting room and the work of Grok (Order Flow Desk, 7 agents, 5 setups) and ChatGPT (TIA terminal, 7 functions), compare them, keep them separate in code and let them cooperate.
4. Risk per trade: owner left it to Claude. Wyckoff phases, the Telegram pipeline on GitLab, merge of finished work.

## Decisions
- Brain v2 merged to `main` (MR !1, 2026-11-08).
- The three streams stay separate in code; they cooperate through `docs/AGENT_CONTRACT.md` and the shared result object `modules/agent_result.py`. Others drop `*.jsonl` files in `data/agent_results/`.
- Historical risk note: the owner initially said "خليها نص" (0.5%). This was superseded by the later owner decision on 2026-11-09: 0.25% base; automatic 0.50% only for grade exactly A+ with explicit validation passed and >=30 closed OOS trades for the same setup/rule version. No manual selector; malformed/missing validation stays at 0.25%. Daily cap 2%, lock after 3 stops, R:R >= 1:2. Canonical policy: modules/risk_policy.py; see MR !47.
- Standing merge rule and this session-note rule: see `docs/AGENT_CONTRACT.md` section 5.

## Done (merged on GitLab main)
!12 `.gitlab-ci.yml` (Telegram jobs, runs only from a schedule or the Run button), !16 agent contract, !17 Wyckoff phases A-E (context label, not in DETECTORS), !18 agent results in the daily brain review, !23 CI cache for `.brain_agents.jsonl`.

## NOT tested
- The GitLab pipeline has never run (no CI variables yet, no schedule). Free CI minutes are limited.
- Telegram delivery, real RSS feeds from the runner, the 1W candles on every data source, the horizons builder on real data, Wyckoff on real candles.
- The full test suite was interrupted by a worker restart; the relevant tests were run one by one and passed.

## Open
- Owner: add `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in GitLab CI/CD variables, then Run pipeline; create the pipeline schedule.
- TIA page order (Radar first vs Workspace first) and the Spot-after-Radar rule.
- Risk choice is resolved by the later owner instruction: 0.25% base / 0.50% only for explicitly validated A+ setups with >=30 closed OOS trades. Implementation and tests are in MR !47; pending review and execution of CI after GitLab identity verification.
- Every GitLab pipeline fails with "Identity verification is required in order to run CI jobs" (reported by the Order Flow Desk session): the owner must verify the account at gitlab.com/-/identity_verification before any CI job can run.
- Draft MRs (#4, #5, #7, #8, #10, #13) wait for their authors.
- Weekly lab result could not be read (GitHub Actions unreachable); the video school (Instagram / channel) is waiting for a rules table.
