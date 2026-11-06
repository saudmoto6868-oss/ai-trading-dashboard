"""Watch items (day_plan.watch): context setups (price action, Elliott ...) on 1H / 15m / 5m that agree with the 1D + 4H bias; never a trade; Telegram text + dedupe. Synthetic."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd
from modules import day_plan as D
import modules.scorer as SC

df = pd.DataFrame({"time": pd.date_range("2026-11-06", periods=80, freq="1h"), "open": 100.0, "high": 101.0, "low": 99.0, "close": 100.5, "volume": 1.0})
def sig(key, fam, d):
    return {"key": key, "family": fam, "name": f"{key} setup", "direction": d, "icon": "x", "prices": {}}
def vw(d):
    return {"tf": "x", "dir": d, "stars": 3, "signals": [], "price": 100.0, "atr": 1.0, "supports": [], "resistances": [], "time": pd.Timestamp("2026-11-06")}

orig_tv, orig_cd = D.tf_view, SC.cached_detect
try:
    D.tf_view = lambda d_, tf: vw("bullish") if tf in ("1d", "4h") else None
    SC.cached_detect = lambda d_: ([sig("pa_engulf", "PA", "bullish"), sig("pa_pin", "PA", "bearish"), sig("ob", "Unicorn", "bullish")], [])
    frames = {"1d": df, "4h": df, "1h": df, "15m": df, "5m": None}
    w = D.watch("HL:xyz:GOLD", frames, clock=D.session_clock("2026-11-06T08:00:00Z"))
    assert [x["tf"] for x in w] == ["1h", "15m"] and all(x["direction"] == "bullish" and x["names"] == ["pa_engulf setup"] and x["schools"] == ["Price action"] for x in w), w   # only PA / Elliott, only WITH the bias
    # no bias (1D and 4H disagree) -> nothing
    D.tf_view = lambda d_, tf: vw("bullish" if tf == "1d" else "bearish")
    assert D.watch("X", frames) == []
    D.tf_view = lambda d_, tf: vw("bullish") if tf in ("1d", "4h") else None
    items = D.scan_watch(["HL:xyz:GOLD", "BTC-USDT"], lambda s_, t_: df)
    assert len(items) == 6, len(items)   # 2 symbols x 3 trigger timeframes
finally:
    D.tf_view, SC.cached_detect = orig_tv, orig_cd
txt = D.format_watch(w, ar=True)
assert "للمراقبة" in txt and "HL:xyz:GOLD" in txt and "n<30" in txt and len(txt) < 3900
assert "Nothing" in D.format_watch([], ar=False)
sent, box = {}, []
n, _ = D.dispatch(w, sent, lambda t: box.append(t) or None, top_n=2, now=1000.0, fmt=lambda it: D.format_watch(it))
n2, _ = D.dispatch(w, sent, lambda t: box.append(t) or None, top_n=2, now=1500.0, fmt=lambda it: D.format_watch(it))
assert n == 2 and n2 == 0 and all("<b>" in b for b in box)
print("ok day watch")
