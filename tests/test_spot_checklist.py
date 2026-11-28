"""Spot checklist + sizing (modules/spot_checklist.py). Synthetic plan dicts, no network. Plain script."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules import spot_checklist as K

ROWS_OK = [{"tf": t, "available": True} for t in ("1d", "1w", "1mo")]


def plan(**kw):
    p = {"price": 99.0, "action": "accumulate", "buys": [100.0, 95.0, 90.0], "sells": [120.0, 140.0], "invalidation": 85.0,
         "rows": ROWS_OK, "score": 50}
    p.update(kw)
    return p


def main():
    ok = 0
    # Sizing: equity 10k, avg 100, invalidation 90 -> stop 10%, 1% risk = $100 -> position $1000 (under the 25% cap).
    s = K.size_plan(10000, 100.0, 90.0)
    assert s["ok"] and abs(s["total_usd"] - 1000) < 1e-6 and abs(s["risk_usd"] - 100) < 1e-6, s
    ok += 1
    # Tight stop (1%) would ask for $10k: capped at 25% of equity = $2500, and the risk is then below 1%.
    s = K.size_plan(10000, 100.0, 99.0)
    assert s["ok"] and abs(s["total_usd"] - 2500) < 1e-6 and "الحد الأقصى" in s["why"], s
    assert s["risk_usd"] < 100, s
    ok += 1
    # Stop wider than 20% is refused, not sized.
    s = K.size_plan(10000, 100.0, 70.0)
    assert not s["ok"] and s["total_usd"] == 0, s
    ok += 1
    # Invalidation above the entry or missing values: refused.
    assert not K.size_plan(10000, 100.0, 105.0)["ok"]
    assert not K.size_plan(0, 100.0, 90.0)["ok"]
    ok += 1

    # Good plan with equity and budget: every check passes (the verdict still says it is not a promise).
    c = K.checklist(plan(), equity=10000, budget=1000)
    ids = {i["id"]: i["ok"] for i in c["items"]}
    assert ids["data"] and ids["levels"] and ids["invalidation"] and ids["chase"] and ids["rr"] and ids["size"] and ids["budget"] and ids["plan_side"], c
    assert c["failed"] == 0 and c["unknown"] == 0, c
    assert "ضمان" in c["verdict"]
    ok += 1

    # Price chased far above the first buy level: 'chase' fails -> verdict says no entry.
    c = K.checklist(plan(price=110.0), equity=10000, budget=1000)
    assert {i["id"]: i["ok"] for i in c["items"]}["chase"] is False and c["verdict"] == "ممنوع الدخول", c
    ok += 1

    # Plan says wait: 'plan_side' fails.
    c = K.checklist(plan(action="wait"), equity=10000)
    assert {i["id"]: i["ok"] for i in c["items"]}["plan_side"] is False and c["failed"] >= 1
    ok += 1

    # No equity given: sizing and budget are UNKNOWN, never a silent pass.
    c = K.checklist(plan())
    ids = {i["id"]: i["ok"] for i in c["items"]}
    assert ids["size"] is None and "budget" not in ids and c["unknown"] >= 1, c
    ok += 1

    # Budget above the allowed size fails.
    c = K.checklist(plan(), equity=10000, budget=5000)
    assert {i["id"]: i["ok"] for i in c["items"]}["budget"] is False
    ok += 1

    # Missing a timeframe: data check fails.
    c = K.checklist(plan(rows=ROWS_OK[:2]))
    assert {i["id"]: i["ok"] for i in c["items"]}["data"] is False
    ok += 1

    # Take-profit: two targets -> 1/3, 1/3, rest trails. One target -> 1/3 then the rest.
    tp = K.take_profit_plan(9.0, [140.0, 120.0])
    assert [round(x["units"], 6) for x in tp] == [3.0, 3.0, 3.0] and tp[0]["target"] == 120.0 and tp[-1]["target"] is None, tp
    tp = K.take_profit_plan(9.0, [120.0])
    assert [round(x["units"], 6) for x in tp] == [3.0, 6.0], tp
    assert K.take_profit_plan(9.0, []) == []
    ok += 1
    print(f"test_spot_checklist: {ok} groups passed")


if __name__ == "__main__":
    main()
