"""Robustness tab reads the REAL lab rows: cell verdicts (n < 30 = not evidence, edge needs t above max(3, Bonferroni) + net > 0 in both halves),
net = avgR - 0.10R, 'survives trend' rule, and no invented numbers when the lab file is empty.
Run: PYTHONPATH=. python tests/test_quant_robustness.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.quant_robustness import COST_R, build_matrix, cell  # noqa: E402


def row(key, side, n, avg, t=1.0, is_avg=None, oos_avg=None, school="S", tf="all"):
    return {"key": key, "school": school, "tf": tf, "side": side, "n": n, "win": 50.0, "avgR": avg, "t": t,
            "is_n": n // 2, "is_avgR": avg if is_avg is None else is_avg, "oos_n": n - n // 2, "oos_avgR": avg if oos_avg is None else oos_avg}


assert cell(None)["verdict"] == "none"
assert cell(row("a", "trend-with", 29, 0.9, t=9))["verdict"] == "not_evidence"
c = cell(row("a", "trend-with", 200, 0.3, t=3.5))
assert c["verdict"] == "edge" and abs(c["net"] - (0.3 - COST_R)) < 1e-9, c
assert cell(row("a", "trend-with", 200, 0.3, t=2.0))["verdict"] == "positive"                 # t too small
assert cell(row("a", "trend-with", 200, 0.3, t=5, oos_avg=0.05))["verdict"] == "positive"     # OOS negative after costs
assert cell(row("a", "trend-with", 200, 0.08, t=5))["verdict"] == "negative"                  # gross + but net -

rows = [row("good", "all", 600, 0.3), row("good", "trend-with", 300, 0.3), row("good", "trend-against", 300, 0.25), row("good", "ses-London 07-12", 10, 1.0),
        row("bad", "all", 600, 0.3), row("bad", "trend-with", 300, 0.5), row("bad", "trend-against", 300, -0.2),
        row("one", "all", 90, 0.4), row("one", "trend-with", 90, 0.4),
        row("*ALL*", "trend-with", 999, 0.5), row("x", "trend-with", 99, 0.5, tf="1h"), row("v", "rr1.5", 99, 0.5, school="exit")]
m = build_matrix(rows)
assert [e["key"] for e in m] == ["good", "one", "bad"], [e["key"] for e in m]
g, o, b = m
assert g["survives_trend"] and g["tested"] == 2 and g["passed"] == 2 and g["cells"]["ses-London 07-12"]["verdict"] == "not_evidence"
assert not b["survives_trend"] and b["passed"] == 1
assert not o["survives_trend"]                      # only one trend context with evidence -> not "survives"
assert g["trials"] == 5 and g["t_bar"] == 3.0                      # few looks: the lab's own t > 3
assert build_matrix([]) == []
many = [row(f"k{i}", "trend-with", 100, 0.3, t=3.5) for i in range(300)]          # 300 looks: Bonferroni bar > 3.5, so no star
mm = build_matrix(many)
assert mm[0]["trials"] == 300 and mm[0]["t_bar"] > 3.5 and not any(c["verdict"] == "edge" for e in mm for c in e["cells"].values()), mm[0]["t_bar"]
assert cell(row("a", "trend-with", 200, 0.3, t=3.5), t_bar=3.9)["verdict"] == "positive"
print("ok quant_robustness")
