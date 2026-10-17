"""Cboe delayed option chain parser + summary (mock payload) and the Finnhub browser-token wiring of the Workspace.
Run: python tests/test_live_feeds.py"""
import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules import cboe_options as cb, workspace  # noqa: E402

assert cb.cboe_symbol("spx") == "_SPX" and cb.cboe_symbol("^VIX") == "_VIX" and cb.cboe_symbol("SPY") == "SPY"
r, e, t, k = cb.parse_occ("SPY261017C00500000")
assert r == "SPY" and e == pd.Timestamp("2026-10-17") and t == "C" and k == 500.0
assert cb.parse_occ("junk") is None

opt = lambda code, **kw: dict({"option": code}, **kw)
payload = {"data": {"symbol": "SPY", "current_price": 502.0, "options": [
    opt("SPY261017C00495000", bid=8, ask=8.2, iv=0.18, open_interest=100, volume=50, delta=0.7),
    opt("SPY261017P00495000", bid=1, ask=1.1, iv=0.2, open_interest=300, volume=80, delta=-0.3),
    opt("SPY261017C00500000", bid=4, ask=4.1, iv=0.17, open_interest=500, volume=200, delta=0.55),
    opt("SPY261017P00500000", bid=2, ask=2.1, iv=0.19, open_interest=400, volume=100, delta=-0.45),
    opt("SPY261017C00505000", bid=1.5, ask=1.6, iv=0.16, open_interest=200, volume=60, delta=0.35),
    opt("SPY261017P00505000", bid=4.5, ask=4.7, iv=0.2, open_interest=100, volume=40, delta=-0.65),
    opt("SPY261024C00500000", bid=6, ask=6.2, iv=0.17, open_interest="", volume=None, delta=0.55),
    {"option": "BROKEN"},
]}}
px, ch = cb.parse(payload)
assert px == 502.0 and len(ch) == 7 and set(ch.type) == {"C", "P"}
assert ch.loc[(ch.strike == 500) & (ch.type == "C") & (ch.expiry == "2026-10-17"), "oi"].item() == 500
assert pd.isna(ch.loc[ch.expiry == "2026-10-24", "oi"]).all()
s = cb.summary(ch, px)
assert s["expiry"] == pd.Timestamp("2026-10-17")
assert abs(s["pc_vol"] - (80 + 100 + 40) / (50 + 200 + 60)) < 1e-9
# max pain by hand: k=495 -> calls 0 + puts (100*5 + 400*10... ) etc; smallest total pain is at 500
assert s["max_pain"] == 500.0, s
nm = cb.near_money(ch, px, n=2)
assert list(nm.strike) == [500.0, 505.0] and "C bid" in nm.columns and "P iv" in nm.columns
try:
    cb.parse({"data": {"options": []}})
    raise AssertionError("empty chain must raise")
except ValueError:
    pass

# Finnhub token: off by default, passed through when given, and the SERVER key never leaks into the page
os.environ["FINNHUB_API_KEY"] = "SERVER_SECRET_123"
html = workspace.build_workspace_html(["BTC-USDT"])
cfg = json.loads(html.split("const CFG = ", 1)[1].split(";\n", 1)[0])
assert cfg["fhToken"] == "" and "SERVER_SECRET_123" not in html
html = workspace.build_workspace_html(["BTC-USDT"], fh_token="BROWSER_KEY")
assert '"fhToken": "BROWSER_KEY"' in html and "SERVER_SECRET_123" not in html
os.environ["FINNHUB_WS_TOKEN"] = " ws_key "
assert workspace._fh_token() == "ws_key"
print("test_live_feeds: all passed")
