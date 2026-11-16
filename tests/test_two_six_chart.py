"""2.6 chart setups (modules/two_six_chart.py) on hand-made candles; mock data only.
Run: python3 tests/test_two_six_chart.py"""
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules import two_six_chart as tc  # noqa: E402

F = (100, 101, 99, 100)
# H 110 @3, L 90 @7 (down leg 20), H 110.03 @11 -> equal highs; sweep @15; rally to 120 @17, then drop to 80 @20.
rows = [F] * 3 + [(100, 110, 99, 100)] + [F] * 3 + [(100, 101, 90, 100)] + [F] * 3 + [(100, 110.03, 99, 100)]
rows += [F] * 3 + [(100, 111, 99, 100), F, (100, 120, 99, 100), F, F, (100, 101, 80, 100)] + [F] * 60
df = pd.DataFrame(rows, columns=["open", "high", "low", "close"])
df.insert(0, "time", pd.date_range("2026-01-01", periods=len(df), freq="15min", tz="UTC"))
bars = tc.bars_from_df(df)

h2 = [p for p in tc.setups(bars, use_h1=False) if p["kind"] == "H2"]
assert len(h2) == 1, h2
p = h2[0]
u = 20 / 2.6
assert p["side"] == "SELL" and p["known"] == 15 and abs(p["entry"] - (110.03 + u)) < 1e-9, p
assert abs(p["stop"] - (110.03 + 2 * u)) < 1e-9 and p["tp1"] == 110.03 and abs(p["tp2"] - (110.03 - u)) < 1e-9, p
# filled @17 (high 120 >= entry 117.72, < stop 125.41); next bar low 99 <= TP2 102.34 -> TP2 at 18.
assert p["fill"] == 17 and p["status"] == "TP2" and p["exit"] == 18, p

# stop wins when one candle touches stop and target (worst case)
b2 = list(bars)
b2[18] = tc.es.Bar("18", 100, 130, 80, 100)
q = [s for s in tc.setups(b2, use_h1=False) if s["kind"] == "H2"][0]
assert q["status"] == "stopped" and q["exit"] == 18, q

h1 = [s for s in tc.setups(bars, use_h2=False)]
assert h1 and all(s["kind"] == "H1" for s in h1)
for s in h1:   # every plan: TP1 = 1R, TP2 = 2R
    r = abs(s["entry"] - s["stop"]) if s["fill"] is None else None
    if r:
        assert abs(abs(s["tp2"] - s["tp1"]) - r) < 1e-9, s

html = tc.chart_html(df, tc.setups(bars))
assert "createChart" in html and "addCandlestickSeries" in html and html.count("</script>") == 2
# regression: a same-kind extreme replaces the leg, never stacks a second leg from the same start
F = (100, 101, 99, 100)
rows = [F] * 3 + [(100, 110, 99, 100)] + [F] * 3 + [(100, 101, 90, 100)] + [F] * 3 \
    + [(100, 108, 99, 100)] + [F] * 3 + [(100, 112, 99, 100)] + [F] * 3 + [(100, 101, 80, 100)] + [F] * 10
zb = [tc.es.Bar(str(i), *r) for i, r in enumerate(rows)]
zl = tc.real_legs(zb, tc.es.confirmed_pivots(zb, 3, 3), 3.0)
starts = [a.idx for a, _ in zl]
assert len(starts) == len(set(starts)), [(a.idx, b.idx) for a, b in zl]
assert [(a.price, b.price) for a, b in zl] == [(110, 90), (90, 112), (112, 80)], zl

print("ok two_six_chart")
