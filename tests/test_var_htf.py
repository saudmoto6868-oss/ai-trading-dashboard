"""Lab rows *VARHTF*: exit variant x tf x trend side (htf side finding, docs/PREREG_2026-11-01.md). Synthetic, no network."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from collections import defaultdict
from modules import strategy_lab as sl

vht = defaultdict(list)
for i in range(40):
    vht[("rr1.5", "1h", "with")].append(1.5 if i % 3 == 0 else -1.0)     # avg -0.167
    vht[("rr1.5", "1h", "against")].append(1.5 if i % 2 == 0 else -1.0)  # avg +0.25
    vht[("rr1.5", "1h", "flat")].append(1.0)                             # flat side is skipped
vht[("rr2.0", "1h", "with")] = [2.0, -1.0] * 5                           # n 10 < MIN_N: skipped
rows = sl.var_htf_rows(vht)
assert {r["side"] for r in rows} == {"rr1.5 trend-with", "rr1.5 trend-against"}, rows
w = next(r for r in rows if r["side"].endswith("with")); a = next(r for r in rows if r["side"].endswith("against"))
assert w["key"] == "*VARHTF*" and w["school"] == "exit" and w["tf"] == "1h" and w["n"] == 40
assert w["avgR"] < 0 < a["avgR"] and abs(w["net"] - (w["avgR"] - sl.COST_R)) < 1e-3 and a["t"] > 0
# report renders the paired table; the old *VAR* table is unchanged
md = sl.report(rows, [], {}, {"built": 0, "symbols": [], "tfs": [], "series": []})
assert "Exit variant x timeframe x trend" in md and "| 1h | rr1.5 | 40 |" in md, md[-600:]
print("ok test_var_htf")
