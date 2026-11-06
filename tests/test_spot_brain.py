"""Spot brain: order-flow parsers (T&S, taker CVD, book, footprint profile), COT parse + reading, the four horizons, the holdings
guard (exit below invalidation), Arabic text, the mosaic screen. No network. Plain script: python3 tests/test_spot_brain.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
import pandas as pd

from modules import spot_brain, spot_brain_view, spot_core as C, spot_flow as F, spot_inst as I

# T&S: 3 buys of 10 and 1 sell of 5 at 100
tp = F.parse_trades([{"px": "100", "sz": "10", "side": "buy", "ts": 3}, {"px": "100", "sz": "5", "side": "sell", "ts": 4},
                     {"px": "100", "sz": "10", "side": "buy", "ts": 1}, {"px": "100", "sz": "10", "side": "buy", "ts": 2}])
assert tp["ok"] and abs(tp["buy_share"] - 3000 / 3500) < 1e-9 and tp["cvd"] == [1000, 2000, 3000, 2500]
assert not F.parse_trades([])["ok"]
tk = F.parse_taker([[3, 10, 30], [1, 20, 10], [2, 10, 10]])   # [ts, sell, buy], newest first
assert tk["delta"] == [-10, 0, 20] and tk["cvd"] == [-10, -10, 10] and tk["slope"] > 0
bk = F.parse_book([[99.9, 10], [99.5, 10], [90, 1000]], [[100.1, 5], [100.5, 5]])
assert bk["ok"] and bk["imbalance"] > 0 and bk["wall_bid"] == 90 and abs(bk["mid"] - 100) < 1e-9
df = pd.DataFrame({"high": [101, 102, 103] * 5, "low": [99, 100, 101] * 5, "volume": [1, 5, 1] * 5})
vp = F.volume_profile(df, bins=20)
assert vp["ok"] and 100 <= vp["poc"] <= 102 and vp["val"] < vp["poc"] < vp["vah"]
rd = F.reading({"tape": tp, "taker": tk, "book": bk, "deriv": {"ok": True, "funding": 0.05, "ls_ratio": 2.5, "oi_chg_7d": 5}, "premium": {"ok": True, "premium_pct": 0.1}, "vp": vp})
assert rd["vote"] == 1 and any("زحمة" in x for x in rd["lines"]) and any("كوين بيس" in x for x in rd["lines"]) and any("POC" in x for x in rd["lines"])

# COT: commercials at the top of their 3-year range, speculators at the bottom
rows = [{"report_date_as_yyyy_mm_dd": str(pd.Timestamp("2023-01-03") + pd.Timedelta(weeks=k)), "comm_positions_long_all": 100000 + k * 300,
         "comm_positions_short_all": 200000, "noncomm_positions_long_all": 250000 - k * 200, "noncomm_positions_short_all": 60000, "open_interest_all": 5e5}
        for k in range(156)][::-1]
ct = I.parse(rows)
assert ct["ok"] and ct["comm_idx"] == 100 and ct["spec_idx"] == 0 and ct["date"].startswith("2025")
ir = I.reading(ct)
assert ir["vote"] == 1 and "الفلوس الذكية" in " ".join(ir["lines"])
assert not I.parse(rows[:5])["ok"] and I.reading({"ok": False, "why": "x"})["vote"] == 0
assert set(I.CODES) >= {"GOLD", "SILVER", "COPPER", "OIL", "EURUSD"} and I.CODES["GOLD"] == "088691"

# brain on synthetic gold (all frames from one daily series)
rng = np.random.default_rng(21)
n = 2600
c = 1900 * np.exp(np.cumsum(rng.normal(0.0005, 0.013, n)))
o = np.r_[c[0], c[:-1]]
day = pd.DataFrame({"time": pd.date_range("2018-01-01", periods=n, freq="D"), "open": o, "high": np.maximum(o, c) * 1.006, "low": np.minimum(o, c) * 0.994,
                    "close": c, "volume": 1.0})
agg = {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}


def get(sym, tf, limit=300):
    d = day.set_index("time")
    if tf == "1mo":
        return d.resample("MS").agg(agg).dropna().reset_index()
    if tf == "1w":
        return d.resample("W").agg(agg).dropna().reset_index().tail(limit).reset_index(drop=True)
    return day.tail(limit).reset_index(drop=True)


px = float(day.close.iloc[-1])
hold = C.positions([C.new_tx(side="buy", asset="GOLD", qty=2, unit="oz", price=px * 1.05, currency="USD", fx=48)], {"GOLD": px}, 50)
flow = {"tape": tp, "taker": tk, "book": bk, "deriv": {"ok": True, "funding": 0.001, "oi_chg_7d": 1.0, "ls_ratio": 1.2}, "premium": {"ok": False}, "vp": vp}
br = spot_brain.run("GOLD", "metals", "الدهب", get, hold, [{"title": "Missile strike escalates conflict"}], flow, ct)
assert set(br["horizons"]) == {"day", "week", "month", "year"}
for h in br["horizons"].values():
    assert -100 <= h["score"] <= 100 and h["verdict_ar"] in {x[2] for x in spot_brain.VERDICT} and h["reasons"]
assert br["guard"] and br["guard"][0]["action"] in ("hold", "reduce", "protect", "exit") and br["head"]
assert spot_brain.verdict(50)[0] == "buy" and spot_brain.verdict(-50)[0] == "sell" and spot_brain.verdict(0)[0] == "wait"
# guard: weekly close under the plan invalidation -> exit
b2 = dict(br["bundle"])
b2["plan"] = {**(b2.get("plan") or {}), "invalidation": px * 2}
g = spot_brain.think(b2, flow, ct, None, [], hold)["guard"][0]
assert g["action"] == "exit" and "الإلغاء" in g["why"]
txt = spot_brain.text_ar(br)
assert "الدهب" in txt and "اللي معاك" in txt and "مفيش أي أمر بيتنفذ" in txt
h = spot_brain_view.render(br, [{"name": "الدهب", "price": px, "wk": 1.0, "score": 20}])
assert "العقل المدبر" in h and h.count("<svg") >= 8 and "COT" in h and "الفوت برينت" in h and 'dir="rtl"' in h
print("test_spot_brain OK")
