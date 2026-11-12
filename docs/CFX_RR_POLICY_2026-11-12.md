# CFX Reward/Risk Policy Alignment — 2026-11-12

Status: proposed in MR !64; not merged.

The owner-approved unified policy recorded in `PROJECT_STATUS.md` on 2026-11-09 requires minimum R:R >= 1:2. The CFX research pipeline still had `RR1_MIN = 1.5`; this branch raises it to `2.0` in both `research/cfx/cfx_pipeline.py` and `research/cfx/cfx_lib.py`.

The target filter now rejects 1.5R and accepts 2R or higher. The old CFX backtest figures (n=83, 37.35%, +0.238R) were generated under the 1.5R gate; they are now explicitly labeled historical and must not be represented as results for the 2.0R filter. A new backtest at 2.0R remains required. `tests/test_cfx_rr_policy.py` exercises the actual `apply_rr_gate` function using a stub for the research-only oscillator dependency and verifies the library constant matches.

Validation:
- Required `cfx_rr_policy` job passed on pipeline 529 for the code change.
- Pipeline 531 reruns the same hard gate after documentation updates.

Scope note: the CFX research pipeline calculates entry/stop/target R multiples; it does not implement portfolio position sizing. This change does not claim to wire A+/30-trade risk percentage sizing into CFX and does not add order execution.
