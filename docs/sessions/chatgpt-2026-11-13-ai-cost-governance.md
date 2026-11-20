# Session note — AI cost governance pilot

Date: 2026-11-13
Branch: `feature/ai-cost-governance`
Base commit: `1500a7a2ab386555e3b41a22f73455ba50c89269`

## Owner request
Create a separate branch and implement shared rules, Skills, and a safe cost-governance approach that reduces unnecessary usage without harming project quality.

## Audit findings
- `.claude/settings.json` already has a `PostToolUse` hook invoking `scripts/activity_hook.py`.
- `scripts/activity_hook.py` appends tool name, bounded target, and success/failure to `docs/ACTIVITY_LOG_AUTO.md`; it intentionally does not record file contents and does not measure provider token usage or billing cost.
- `CLAUDE.md`, `AGENTS.md`, and `docs/AGENT_PROMPT.md` already contain overlapping context-efficiency, branch, testing, and safety instructions.
- `docs/AI_ROLES.md` contains an older provider/model cost allocation; it should be reconciled separately rather than silently overwritten.
- `docs/AGENT_CONTRACT.md` is explicitly marked as a proposal on another branch; it defines agent ownership and output contracts but does not implement task budgets or usage measurement.
- `.claude/` currently contains only `settings.json`; no repository-local Skills were found in that directory.

## Changes in this pilot
- Added `docs/AI_COST_POLICY.md`.
- Added four on-demand Skills: cost-aware planning, context hygiene, model routing, and quality preservation.
- Did not modify existing settings, hooks, activity logs, project code, CI, or third-party plugin configuration.

## Verification
- GitLab branch and source files were inspected through repository APIs.
- No local runtime was available through this GitLab operation; Skills were not executed and no test suite was run.
- No usage/cost baseline was collected.
- No third-party plugin was installed or authorized.

## Next steps
1. Review and reconcile the older model/provider allocation in `docs/AI_ROLES.md`.
2. Design a read-only usage report from actual available Claude Code usage records; distinguish provider-reported usage from estimates.
3. Add tests for any future logger/guard before wiring it into `.claude/settings.json`.
4. Compare a representative task against a baseline for both usage and quality.
5. Keep this branch Draft until owner review; no merge or deployment.
