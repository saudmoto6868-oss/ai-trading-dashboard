"""Spot desk (page 11): units, EGP split, ledger, ladder, alerts, Excel round trip, plan engine on synthetic candles,
and the page rendering in Streamlit AppTest with the network blocked. Plain script: python3 tests/test_spot.py"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
import pandas as pd

from modules import spot_core as C

close = lambda a, b, e=1e-6: abs(a - b) <= e * max(1, abs(b))

# units / karats
assert close(C.base_qty("GOLD", C.OZ_G, "g"), 1.0)
assert close(C.base_qty("GOLD", 100, "g", 0.875), 100 * 0.875 / C.OZ_G)
assert close(C.base_qty("COPPER", 1, "kg"), 1 / C.LB_KG)
assert close(C.base_qty("COPPER", 2, "lb"), 2)
assert close(C.base_qty("BTC", 0.5, "coin"), 0.5)
g = C.per_unit_prices("GOLD", 3110.34768, fx=50)
assert [r["purity"] for r in g] == ["24K", "21K", "18K"]
assert close(g[0]["usd_g"], 100) and close(g[1]["usd_g"], 87.5) and close(g[0]["egp_g"], 5000)
cu = C.per_unit_prices("COPPER", 5.0, None)[0]
assert close(cu["usd_kg"], 5 / C.LB_KG) and "egp_g" not in cu
assert close(C.local_gap(100, 103), 3.0) and C.local_gap(0, 5) is None

# ledger: two gold buys at different rates, one partial sell
t1 = C.new_tx(side="buy", asset="GOLD", qty=1, unit="oz", price=2000, currency="USD", fx=30, date="2025-01-01")
t2 = C.new_tx(side="buy", asset="gold", qty=1, unit="oz", price=150000, currency="EGP", fx=50, date="2025-06-01")   # = 3000 USD
t3 = C.new_tx(side="sell", asset="GOLD", qty=0.5, unit="oz", price=4000, currency="USD", fx=50, fees=10, date="2025-09-01")
pos = C.positions([t3, t1, t2], {"GOLD": 4000}, fx_now=50)
p = pos[0]
assert p["asset"] == "GOLD" and close(p["qty"], 1.5)
assert close(p["avg_usd"], 2500)                       # (2000 + 3000) / 2
assert close(p["realized_usd"], 2000 - 10 - 1250)       # 0.5 x 4000 - fees - 0.5 x 2500
assert close(p["cost_egp"], (60000 + 150000) * 0.75)
assert close(p["unreal_usd"], 1.5 * 4000 - 3750)
assert close(p["metal_part_egp"] + p["fx_part_egp"], p["unreal_egp"])   # split adds up exactly
assert close(p["metal_part_egp"], (4000 - 2500) * 1.5 * 50)
# EGP row with no rate -> USD unknown, nothing crashes
bad = C.new_tx(side="buy", asset="SILVER", qty=1, price=1500, currency="EGP", fx=None)
assert math.isnan(C.tx_usd(bad)[0])
C.positions([bad], {"SILVER": 30}, 50)
tt = C.totals(pos)
assert close(tt["value_usd"], 6000)

# ladder
lad = C.ladder([90, 100, 80, 70], 1000)
assert [r["price"] for r in lad] == [100, 90, 80] and close(sum(r["usd"] for r in lad), 1000) and close(lad[0]["usd"], 300)
assert C.ladder([], 100) == [] and C.ladder_avg([]) is None

# alerts
al = [C.new_alert("GOLD", "buy", 3900), C.new_alert("GOLD", "sell", 4100), C.new_alert("BTC", "stop", 50000)]
hits = C.check_alerts(al, {"GOLD": 3850, "BTC": 60000})
assert [h["kind"] for h in hits] == ["buy"]
assert "وقت شراء" in C.alert_text(hits[0], True) and "Buy zone" in C.alert_text(hits[0], False)

# Excel round trip
xl = C.to_excel([t1, t2, t3], pos, {"GOLD": 4000}, 50)
back = C.from_excel(xl)
assert [b["id"] for b in back] == [t1["id"], t2["id"], t3["id"]] and close(back[1]["price"], 150000) and back[2]["side"] == "sell"

# invoice
h = C.invoice_html(C.new_tx(side="buy", asset="GOLD", qty=10, unit="g", purity=0.875, price=4000, currency="EGP", fx=50, invoice_no="A-1"))
assert "21K" in h and "A-1" in h and "window.print" in h

# plan engine on one consistent synthetic series (daily -> weekly / monthly by resampling)
from modules import spot_data, spot_plan
rng = np.random.default_rng(3)
n = 2600
c = 100 * np.exp(np.cumsum(rng.normal(0.0006, 0.02, n)))
o = np.r_[c[0], c[:-1]]
day = pd.DataFrame({"time": pd.date_range("2018-01-01", periods=n, freq="D"), "open": o, "high": np.maximum(o, c) * 1.01, "low": np.minimum(o, c) * 0.99,
                    "close": c, "volume": 1.0})
def rs(rule):
    x = day.set_index("time").resample(rule).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}).dropna().reset_index()
    return x
mo = rs("MS")
fr = {"1d": day.tail(300).reset_index(drop=True), "1w": rs("W").tail(300).reset_index(drop=True), "1mo": mo}
pl = spot_plan.plan(fr, spot_data.yearly(mo))
assert pl["ok"] and -100 <= pl["score"] <= 100 and pl["action"] in spot_plan.ACTION_TXT
assert len(pl["buys"]) == 3 and all(b < pl["price"] for b in pl["buys"]) and pl["buys"] == sorted(pl["buys"], reverse=True)
assert all(s > pl["price"] for s in pl["sells"]) and 0 < pl["invalidation"] < min(pl["buys"])
assert len(spot_data.yearly(mo)) == 8
assert not spot_plan.plan({"1d": day.head(20)})["ok"]

# page renders with the network blocked (AppTest)
import requests
from unittest import mock
from streamlit.testing.v1 import AppTest


def boom(*a, **k):
    raise requests.ConnectionError("blocked in test")


import tempfile
from modules import spot_page
spot_page.ROOT = __import__("pathlib").Path(tempfile.mkdtemp())
spot_page.DB, spot_page.FILES = spot_page.ROOT / "ledger.json", spot_page.ROOT / "files"
with mock.patch("requests.get", boom), mock.patch("requests.post", boom):
    at = AppTest.from_string("""
import modules.spot_page as sp, pathlib, tempfile
sp.ROOT = pathlib.Path(tempfile.mkdtemp()); sp.DB = sp.ROOT / 'ledger.json'; sp.FILES = sp.ROOT / 'files'
sp.render()
""", default_timeout=60)
    at.run()
    assert not at.exception, at.exception
    assert len(at.tabs) >= 5
    for lang in ("ar",):
        at.session_state["ws_lang"] = lang
        at.run()
        assert not at.exception, at.exception

# page with mocked live data: plan, metals table, ledger with a record, alerts hit
at = AppTest.from_string("""
import modules.spot_page as sp, modules.spot_data as sd, modules.spot_core as C, pathlib, tempfile, numpy as np, pandas as pd
sp.ROOT = pathlib.Path(tempfile.mkdtemp()); sp.DB = sp.ROOT / 'ledger.json'; sp.FILES = sp.ROOT / 'files'
rng = np.random.default_rng(5); n = 2600
c = 4000 * np.exp(np.cumsum(rng.normal(0.0004, 0.012, n))); o = np.r_[c[0], c[:-1]]
day = pd.DataFrame({'time': pd.date_range('2018-01-01', periods=n, freq='D'), 'open': o, 'high': np.maximum(o, c) * 1.01, 'low': np.minimum(o, c) * 0.99, 'close': c, 'volume': 1.0})
def rs(r): return day.set_index('time').resample(r).agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'}).dropna().reset_index()
F = {'1d': day.tail(300).reset_index(drop=True), '1w': rs('W').tail(300).reset_index(drop=True), '1mo': rs('MS')}
sd.candles = lambda sym, tf, limit=300: sd.yearly(F['1mo']) if tf == '1y' else F[tf]
sd.crypto_tickers = lambda base_url=None: [{'sym': 'BTC-USDT', 'base': 'BTC', 'last': 90000.0, 'chg24': 1.2, 'vol_usd': 1e9}, {'sym': 'ETH-USDT', 'base': 'ETH', 'last': 3000.0, 'chg24': -0.5, 'vol_usd': 5e8}]
sd.metal_prices = lambda: {a: {'px': v, 'prev': v * 0.99, 'src': 'mock'} for a, v in {'GOLD': 4040.0, 'SILVER': 48.0, 'PLATINUM': 1500.0, 'PALLADIUM': 1400.0, 'COPPER': 6.2}.items()}
sd.usd_egp = lambda: {'rate': 47.5, 'time': '2026-11-06 00:00', 'src': 'mock'}
if 'spot_db' not in __import__('streamlit').session_state:
    d = sp._empty(); d['txs'].append(C.new_tx(side='buy', asset='GOLD', qty=10, unit='g', purity=0.875, price=5800, currency='EGP', fx=47.0, invoice_no='INV-1'))
    d['alerts'].append(C.new_alert('GOLD', 'buy', 4100)); __import__('streamlit').session_state['spot_db'] = d
sp.render()
""", default_timeout=120)
at.run()
assert not at.exception, at.exception
txt = " ".join(m.value for m in at.markdown) + " ".join(str(x.value) for x in at.metric) + " ".join(w.value for w in at.warning)
assert "Buy zone" in txt, txt[:500]
assert len(at.dataframe) >= 5, len(at.dataframe)
at.session_state["ws_lang"] = "ar"; at.run()
assert not at.exception, at.exception
print("test_spot OK")
