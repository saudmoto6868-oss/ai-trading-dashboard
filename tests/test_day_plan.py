"""Day plan (modules/day_plan.py): confluence logic, modes, filters, sessions, exits (partial + trailing vs fixed), Telegram text. Synthetic, no network."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from modules import day_plan as D


def view(tf, d, stars=3, price=4100.0, atr=6.0, keys=("ote",), fam="Fib", sup=(4080.0, 4060.0), res=(4130.0, 4160.0, 4200.0)):
    sig = [{"key": k, "family": fam, "name": f"{k} signal", "direction": d, "icon": "x", "prices": {}} for k in keys]
    return {"tf": tf, "dir": d, "stars": stars, "signals": sig if d != "neutral" else [], "price": price, "atr": atr, "supports": list(sup), "resistances": list(res), "time": pd.Timestamp("2026-11-06 09:00")}

def run(views, **kw):
    orig = D.tf_view
    D.tf_view = lambda df, tf: views.get(tf)
    try:
        frames = {tf: object() for tf in D.CHAIN}
        return D.build("HL:xyz:GOLD", frames, clock=D.session_clock("2026-11-06T12:00:00Z"), **kw)
    finally:
        D.tf_view = orig

B, S, N = "bullish", "bearish", "neutral"
agree = {"1d": view("1d", B), "4h": view("4h", B), "1h": view("1h", B), "15m": view("15m", B), "5m": view("5m", N)}
# 1) confluence mode: bias bullish (1D + 4H), triggers 1H and 15m agree -> two plans, best confluence first
plans = run(agree, mode="conf")
assert [p["tf"] for p in plans] in (["1h", "15m"], ["15m", "1h"]) and all(p["direction"] == B and p["confluence"]["n"] == 4 and p["confluence"]["bias_strength"] == 2 for p in plans), plans
p = plans[0]
assert p["entry"] > p["stop"] and p["tps"][0] > p["entry"] and p["rr1"] >= 1 and p["risk_points"] > 0 and p["move_points"] > 0 and p["exit"]["style"] == "partial+trail", p
# gold: 1 point = 0.1 -> points are 10x the dollars
assert p["point"] == 0.1 and abs(p["move_points"] - round(abs(p["tps"][-1] - p["entry"]) / 0.1)) <= 1

# 2) higher timeframes in conflict, or only one trigger agrees without enough chain -> nothing in confluence mode
assert run({**agree, "1d": view("1d", S)}, mode="conf") == []
assert run({"1d": view("1d", N), "4h": view("4h", N), "1h": view("1h", B), "15m": view("15m", B), "5m": view("5m", B)}, mode="conf") == []
# 3) scalp: one chosen timeframe, higher timeframe may be undecided but may not argue; fixed exits
sc = run({**agree, "1d": view("1d", N), "4h": view("4h", N), "5m": view("5m", B)}, mode="scalp", trigger_tfs=("5m",))
assert len(sc) == 1 and sc[0]["exit"]["style"] == "fixed" and len(sc[0]["exit"]["targets"]) == 1 and sc[0]["exit"]["partial"] is None, sc
assert run({**agree, "5m": view("5m", B), "4h": view("4h", S), "1d": view("1d", N)}, mode="scalp", trigger_tfs=("5m",)) == []
# 4) filters: school, min points, min stars
assert run(agree, mode="conf", schools=["Elliott wave"]) == []
assert run(agree, mode="conf", schools=["Fibonacci"]) != []
assert run(agree, mode="conf", min_points=10**6) == []
assert run({**agree, "1h": view("1h", B, stars=1), "15m": view("15m", B, stars=1)}, mode="conf") == []

# 5) sessions (New York clock): London kill zone at 03:00 NY = 08:00 UTC; Asia KZ 20-24 NY
c = D.session_clock("2026-11-06T08:00:00Z")
assert "London" in c["active"] and c["kill_zone"] == "London Open KZ", c
c2 = D.session_clock("2026-11-06T16:00:00Z")
assert set(c2["active"]) == {"London", "New York"} and c2["kill_zone"] is None and c2["next_kz"] and c2["next_kz_in_min"] > 0, c2
assert D.session_label(c, ar=False).startswith("NOW") and "التالي" in D.session_label(c2, ar=True)

# 6) points per instrument
assert D.point_size("HL:xyz:GOLD") == 0.1 and D.point_size("BTC-USDT") == 1.0 and D.point_size("Y:EURUSD=X") == 0.0001 and D.point_size("Y:USDJPY=X") == 0.01 and D.point_size("FOO", 150.0) == 0.01

# 7) exits: long, entry 100, stop 98 (R = 2), TP1 103, TP3 110. Fixed vs partial + trailing
plan = {"entry": 100.0, "stop_loss": 98.0, "take_profits": [103.0, 106.0, 110.0]}
ex_conf = D.exit_plan(plan, "conf", atr=1.0, point=0.1, trail_start_points=100)   # 100 points = 10 -> be_at = min(1R = 2, 10) = 2
assert ex_conf["partial"]["at"] == 103.0 and ex_conf["be_at"] == 2.0 and ex_conf["trail_atr"] == 1.5
ex_fix = D.exit_plan(plan, "scalp", atr=1.0, point=0.1)
def bars(rows):
    return pd.DataFrame(rows, columns=["high", "low", "close"])
# path A: runs to 108 then pulls back: conf takes half at 103 (+1.5R*0.5 = 0.75R), trails the rest and gets out above entry
path = bars([(101, 99.5, 100.8), (103.2, 100.5, 103.0), (106.5, 103.0, 106.2), (108.0, 105.5, 107.0), (107.0, 105.0, 105.2)])
a = D.simulate_exit(path, "bullish", 100.0, 98.0, ex_conf, atr=1.0)
assert a["closed"] and a["r"] > 1.5 and any(e[1] == "partial" for e in a["events"]) and any(e[1] == "breakeven" for e in a["events"]), a
f = D.simulate_exit(path, "bullish", 100.0, 98.0, ex_fix, atr=1.0)
assert f["closed"] and abs(f["r"] - 1.5) < 1e-9 and f["events"][-1][1] == "target", f   # fixed: the single target 103 = +1.5R
# path B: tags TP1 (best 103.5), then falls: the trailing stop (1.5 ATR behind = 102.0) takes the runner out in profit: 0.75R (half at TP1) + 0.5R = 1.25R
pathb = bars([(103.5, 100.2, 103.0), (103.0, 99.0, 99.5)])
b = D.simulate_exit(pathb, "bullish", 100.0, 98.0, ex_conf, atr=1.0)
assert b["closed"] and abs(b["r"] - 1.25) < 1e-9 and b["events"][-1][1] == "stop", b
# path C: straight to the stop = -1R for both modes; same candle touches stop and target -> stop first (conservative)
pc = bars([(100.5, 97.5, 98.0)])
assert D.simulate_exit(pc, "bullish", 100.0, 98.0, ex_conf, atr=1.0)["r"] == -1.0 and D.simulate_exit(bars([(110.5, 97.9, 100)]), "bullish", 100.0, 98.0, ex_fix)["r"] == -1.0
# short mirror
ps = {"entry": 100.0, "stop_loss": 102.0, "take_profits": [97.0, 94.0, 90.0]}
exs = D.exit_plan(ps, "conf", atr=1.0, point=0.1)
sh = D.simulate_exit(bars([(99.8, 96.5, 97.0), (97.5, 93.5, 94.0), (97.0, 92.0, 96.5)]), "bearish", 100.0, 102.0, exs, atr=1.0)
assert sh["r"] > 1.5 and any(e[1] == "partial" for e in sh["events"]), sh

# 8) Telegram text + dedupe
txt = D.format_telegram(plans, ar=True)
assert "خطة اليوم" in txt and "HL:xyz:GOLD" in txt and "1D▲" in txt and len(txt) < 3900
assert "Day plan" in D.format_telegram([], ar=False) or "Nothing" in D.format_telegram([], ar=False)
sent, box = {}, []
n, err = D.dispatch(plans, sent, lambda t: box.append(t) or None, top_n=3, now=1000.0)
n2, _ = D.dispatch(plans, sent, lambda t: box.append(t) or None, top_n=3, now=1500.0)
assert n == len(plans) and n2 == 0 and len(box) == n
n3, _ = D.dispatch(plans, sent, lambda t: None, top_n=3, now=1000.0 + 5 * 3600)
assert n3 == len(plans)
print("ok day plan:", len(plans), "plans; exit A", a["r"], "B", b["r"])
