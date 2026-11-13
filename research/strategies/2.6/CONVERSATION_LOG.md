# 2.6 — Conversation and decision record

Workstream: **2.6**  
Date opened in repository: 2026-11-13  
Repository: 6868-group/ai-trading-dashboard  
Branch: research/strategy-2-6-2026-11-13  
Merge request: https://gitlab.com/6868-group/ai-trading-dashboard/-/merge_requests/70

## Owner requests captured from this conversation

1. "عاوز مراجعة للحساب والفيديوهات الاستراتيجيات والافكار وطرق الدخول وابحث عن كل ذالك في الانترنت والافكار المشابهه والمدارس"
2. "افتح الفيديوهات وتفرج عليها. مش هبعتلك تسجيل ... أنت اعمل كده"
3. "خلص كل التساؤلات، وراجع و ابحث و خلص كل الفيديوهات. خليك في أساس الموضوع، و وفر ما تحرقش وترجع تراجع كل المحادثات من أول و تاني. خليك موفر كده"
4. "تمام كمل الاختبارات وشوف دقتها وحاول توسع الاختبار وتخلي الدقة أفضل وخلي يعني يكمل البحث بعد كده. واديني كل الداتا دي ابعتها لكلود على المسار منفصل على الميتينج روم بحيث إن هو يقدر يوصلها وأسميها الاستراتيجية 2.6. يعني حط المحادثة دي كلها بكل تفاصيلها، بكل لينكاتها هناك. وسميها زي ما قلتلك. وكمل شغلك بقى، الخطوات العملية الصحيحة التالية وكل ما يلزم"

## Research conclusions recorded
- 2.6 retracement distance corresponds to 1/2.6 = 38.4615% of the measured leg.
- 2.618 and 1/0.382 are close comparators, not identical to 2.6.
- 13/5 equals 2.6; 89/34 is approximately 2.618. This is numerical context, not proof of origin.
- Two separate hypotheses remain: (A) retracement entry inside a completed impulse; (B) range/2.6 projection from a liquidity reference. Do not pool them.
- Two Reels have prior analysis notes: DfopgmVi8Wu and DewFqk8inTf. Other Reel notes are classified in README as examples, promotions, or non-rule content.
- Rewatching all Reels was not completed in this pass: Instagram presented a login wall, and vidIQ analysis credits were insufficient (tool-reported renewal date 2026-12-13).
- Existing CFX tests use GC=F gold futures, not spot XAUUSD, and do not test 2.6. Their figures must not be attributed to this strategy.
- No XAUUSD historical backtest, accuracy, win-rate, expectancy, or profitability result is claimed.

## Work delivered to the branch
- research/strategies/2.6/README.md
- research/strategies/2.6/event_study.py
- research/strategies/2.6/CLAUDE_HANDOFF.md
- tests/test_two_six_event_study.py
- docs/MEETING_ROOM.md entry

## Test and CI record
- Local core checks: 3/3 passed (ratio arithmetic and causal pivot confirmation).
- GitLab MR pipelines failed before runner startup with ci_quota_exceeded. This is not a failed assertion.
- Repository unit tests and historical XAUUSD event study have not run.
- No live signal, XPIX/CFX integration, merge, or deployment was performed.

## Current blockers / next actions
1. Get historical broker XAUUSD M1/M5 OHLC with broker, timezone, date range, spread and commission metadata.
2. Resolve the creator's exact anchor, wick/body convention, entry, SL, TP, invalidation and timeframe from the original Reels.
3. Have Claude review the causal event-study implementation and improve de-clustering, costs, bootstrap, walk-forward and untouched holdout.
4. Run the two hypotheses independently, then compare 2.6 with 2.618, 1/0.382, nearby ratios and matched random controls.
5. Keep the research separate and do not claim an edge until the project gate is met (at least 100 trades and net t-stat above 3 after costs).
