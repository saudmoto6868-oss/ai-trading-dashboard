"""Setup alerts (day_plan.setup_alerts / format_setup): a detector key that fired gets its own plan and an expected move in points; too-small moves are dropped; with / against the 1D+4H bias is shown."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from modules import day_plan as D
import modules.scorer as SC

df = pd.DataFrame({"time": pd.date_range("2026-11-06", periods=80, freq="1h"), "open": 100.0, "high": 101.0, "low": 99.0, "close": 100.5, "volume": 1.0})
def sig(key, fam, d, **p):
    return {"key": key, "family": fam, "name": f"{key} {d}", "direction": d, "icon": "x", "prices": p}
def vw(d, price=4100.0):
    return {"tf": "x", "dir": d, "stars": 3, "signals": [], "price": price, "atr": 6.0, "supports": [4080.0, 4060.0], "resistances": [4130.0, 4160.0, 4200.0], "time": pd.Timestamp("2026-11-06")}

o_tv, o_cd = D.tf_view, SC.cached_detect
try:
    D.tf_view = lambda d_, tf: vw("bullish" if tf in ("1d", "4h") else "neutral")
    SC.cached_detect = lambda d_: ([sig("cisd", "Liquidity", "bullish", lvl=4075.0, sl=4070.0, st=4160.0), sig("ew3", "Elliott", "bearish"), sig("ob", "Unicorn", "bullish")], [])
    frames = {tf: df for tf in D.CHAIN}
    a = D.setup_alerts("HL:xyz:GOLD", frames, clock=D.session_clock("2026-11-06T08:00:00Z"), min_points=100)
    keys = {(x["key"], x["direction"], x["tf"]) for x in a}
    assert ("cisd", "bullish", "1h") in keys and ("ew3", "bearish", "1h") in keys and ("ob", "bullish", "1h") not in keys, keys      # 'ob' is not an alert key; each key once per timeframe
    c = next(x for x in a if x["key"] == "cisd" and x["tf"] == "1h")
    assert c["with_bias"] is True and next(x for x in a if x["key"] == "ew3")["with_bias"] is False
    assert c["entry"] > c["stop"] and c["tps"][0] > c["entry"] and c["move_points"] >= 100 and c["risk_points"] > 0
    assert D.setup_alerts("HL:xyz:GOLD", frames, min_points=10**7) == []                       # a move that cannot reach the threshold is dropped
    t = D.format_setup(c, ar=True)
    assert "CISD" in t and "مع اتجاه" in t and "نقطة" in t and len(t) < 3900
    assert "against" in D.format_setup(next(x for x in a if x["key"] == "ew3"), ar=False)
    res = D.scan_setups(["HL:xyz:GOLD"], lambda s_, t_: df)
    assert res and res[0]["with_bias"] is True                                                    # with-bias alerts first
finally:
    D.tf_view, SC.cached_detect = o_tv, o_cd
print("ok setup alerts:", len(a))
