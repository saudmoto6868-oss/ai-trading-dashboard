"""Spot ideas desk: news tagging (EN + AR), recipes (breakout + 1.5R target rule), ranking, Arabic Telegram text, board HTML,
and the bot's /ideas route. No network. Plain script: python3 tests/test_spot_ideas.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
import pandas as pd

from modules import bot_router, spot_board, spot_ideas, spot_news

# news tagging
tg = spot_news.tag([{"title": "Missile strike escalates conflict, gold jumps"}, {"headline": "تصعيد عسكري جديد والذهب يرتفع"},
                    {"title": "Fed signals rate cut"}, {"title": "OPEC+ output cut extended"}, {"title": "Exchange hack drains $200m"},
                    {"title": "Local football results"}])
assert len(tg) == 5 and tg[0]["push"]["GOLD"] == 1 and tg[0]["push"]["BTC"] == -1 and tg[1]["push"]["GOLD"] == 1 and tg[1]["title"]
assert tg[3]["push"] == {"OIL": 1} and tg[4]["push"]["BTC"] == -1 and tg[2]["push"]["EURUSD"] == 1
t = spot_news.tilt(tg, "GOLD")
assert t["up"] == 3 and t["down"] == 0 and t["score"] == 3 and spot_news.tilt(tg, "BTC")["score"] < 0

# a market that just broke its 55-week high -> breakout idea, targets >= 1.5 R
rng = np.random.default_rng(5)
n = 2600
c = np.r_[100 * np.exp(np.cumsum(rng.normal(0, 0.01, n - 60))), np.linspace(1, 1, 60)]
c[-60:] = c[-61] * np.r_[np.linspace(1.0, 0.92, 40), np.linspace(0.92, 0.95, 17), [0.96, 1.25, 1.27]]
o = np.r_[c[0], c[:-1]]
day = pd.DataFrame({"time": pd.date_range("2018-01-01", periods=n, freq="D"), "open": o, "high": np.maximum(o, c) * 1.004,
                    "low": np.minimum(o, c) * 0.996, "close": c, "volume": 1.0})
agg = {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}


def get(sym, tf, limit=300):
    d = day.set_index("time")
    if tf == "1mo":
        return d.resample("MS").agg(agg).dropna().reset_index()
    if tf == "1w":
        return d.resample("W").agg(agg).dropna().reset_index().tail(limit).reset_index(drop=True)
    return day.tail(limit).reset_index(drop=True)


r = spot_ideas.desk(get, [{"title": "Missile strike escalates conflict, gold jumps"}], universe=[("GOLD", "metals", "الدهب")])
assert r["markets"] and r["markets"][0]["asset"] == "GOLD" and r["log"][0].startswith("الدهب")
for i in r["ideas"]:
    if i["kind"] != "avoid":
        e = sum(i["entry"]) / 2
        assert i["stop"] < i["entry"][0] <= i["entry"][1] and (i["targets"][0] - e) / (e - i["stop"]) >= 1.5 - 1e-9 and i["rr"] >= 1.5 - 1e-9
        assert all(abs(a / b - 1) > 0.005 for k, a in enumerate(i["targets"]) for b in i["targets"][k + 1:])
assert any("اختراق" in x for x in r["log"])
txt = spot_ideas.telegram_text(r)
assert "أفكار السبوت النهارده" in txt and "مفيش أي أمر بيتنفذ" in txt and "مزاج الأخبار" in txt

# ranking: avoid cards last, then by agreement
fake = {"ideas": [{"kind": "avoid", "conf": 9, "rr": None}, {"kind": "discount", "conf": 2, "rr": 3}, {"kind": "breakout", "conf": 4, "rr": 1.6}]}
fake["ideas"].sort(key=lambda i: (i["kind"] != "avoid", i["conf"], i["rr"] or 0), reverse=True)
assert [i["kind"] for i in fake["ideas"]] == ["breakout", "discount", "avoid"]

# board HTML (reference style) + empty day
h = spot_board.render(r)
assert "مكتب أفكار السبوت" in h and "طريقة التفكير" in h and "<svg" in h and 'dir="rtl"' in h
h0 = spot_board.render({"ideas": [], "markets": [], "log": ["الدهب: مفيش شموع"], "news": [], "risk_off": 0})
assert "مفيش فكرة شراء النهارده" in h0

# bot route
assert bot_router.route("ابعتلي أفكار السبوت") == [{"cmd": "ideas"}] and bot_router.route("فيه فرص النهارده؟") == [{"cmd": "ideas"}]
print("test_spot_ideas OK")
