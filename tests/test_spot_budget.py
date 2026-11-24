"""Budget plan (Spot desk tab 'Budget plan', owner 2026-11-16): split, DCA schedule, position size, loss caps, journal
maths, and the tab rendering in AppTest with the network blocked. Plain script: python3 tests/test_spot_budget.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules import spot_budget as B

# split: 1000 at 60/25/15 -> 600 / 250 / 150; percentages are normalised when they do not add to 100
assert B.split_budget(1000, B.DEFAULT_SPLIT) == {"dca": 600.0, "swing": 250.0, "reserve": 150.0}
assert B.split_budget(1000, {"a": 30, "b": 30}) == {"a": 500.0, "b": 500.0}
assert B.split_budget(0, B.DEFAULT_SPLIT) == {"dca": 0.0, "swing": 0.0, "reserve": 0.0}
assert B.split_budget(-5, {"a": 1}) == {"a": 0.0}

# DCA: 600 over 12 weeks = 50 a week, 60% BTC / 40% ETH = 30 / 20
rows = B.dca_schedule(600, 12, {"BTC": 60, "ETH": 40})
assert len(rows) == 12 and rows[0]["total"] == 50.0 and rows[0]["BTC"] == 30.0 and rows[0]["ETH"] == 20.0
assert rows[-1]["week"] == 12
assert B.dca_schedule(600, 0, {"BTC": 1}) == [] and B.dca_schedule(0, 12, {"BTC": 1}) == []

# position size: risk 1% of 1000 = 10 USD; stop 5% below entry -> 200 USD position; loss at stop = 10
assert B.position_size(1000, 1.0, 5.0) == 200.0
assert B.loss_at_stop(200.0, 5.0) == 10.0
assert B.position_size(1000, 1.0, 0) == 0.0 and B.position_size(0, 1.0, 5) == 0.0

# stop distance and reward:risk for a long
assert B.stop_pct_from_prices(100.0, 95.0) == 5.0
assert B.stop_pct_from_prices(100.0, 105.0) is None          # stop above entry is not a long
assert B.reward_risk(100.0, 95.0, 110.0) == 2.0               # +10 vs -5
assert B.reward_risk(100.0, 95.0, 99.0) is None               # target below entry
assert B.reward_risk(100.0, 0, 110.0) is None

# monthly cap 5% of 1000 = 50
assert B.monthly_cap(1000, 5) == 50.0

# journal: open trades, month losses (only closed losses in that month count)
journal = [
    {"date": "2026-11-03", "asset": "BTC", "result": -12.5},
    {"date": "2026-11-10", "asset": "ETH", "result": 30.0},
    {"date": "2026-11-12", "asset": "ETH", "result": -20.0},
    {"date": "2026-10-28", "asset": "BTC", "result": -40.0},   # October, not counted in November
    {"date": "2026-11-14", "asset": "SOL", "result": None},    # open
    {"date": "2026-11-15", "asset": "", "result": None},       # empty row, ignored
]
assert B.month_loss(journal, "2026-11") == 32.5
assert B.month_loss(journal, "2026-10") == 40.0
assert B.open_count(journal) == 1
assert B.month_loss([{"date": "2026-11-01", "result": "x"}], "2026-11") == 0.0

# page renders with the network blocked (AppTest), budget tab present and no exception
import requests
from unittest import mock
from streamlit.testing.v1 import AppTest


def boom(*a, **k):
    raise requests.ConnectionError("blocked in test")


with mock.patch("requests.get", boom), mock.patch("requests.post", boom):
    at = AppTest.from_string("""
import modules.spot_page as sp, tempfile
from modules.spot_store import LocalStore
sp.STORE = LocalStore(tempfile.mkdtemp())
sp.render()
""", default_timeout=90)
    at.run()
    assert not at.exception, at.exception
    # the page picks ONE tab with a segmented control (only the picked tab runs), not st.tabs: open the Budget plan tab
    opts = at.get("button_group")[0].options
    assert any("Budget plan" in o or "خطة الميزانية" in o for o in opts), opts
    at.session_state["sp_tab"] = opts.index(next(o for o in opts if "Budget plan" in o or "خطة الميزانية" in o))
    at.run()
    assert not at.exception, at.exception
    keys = {getattr(w, "key", None) for w in at.number_input}
    assert {"bp_entry", "bp_stop", "bp_target"} <= keys, keys
    # the swing sizer with a real setup: entry 100, stop 95, target 110 (budget 1000 -> size 200, capped at the 250 swing share)
    at.session_state["bp_entry"] = 100.0
    at.session_state["bp_stop"] = 95.0
    at.session_state["bp_target"] = 110.0
    at.run()
    assert not at.exception, at.exception
    at.session_state["ws_lang"] = "ar"
    at.run()
    assert not at.exception, at.exception
print("spot budget tests: OK")

# options added 2026-11-16: market mode, ladders, rebalance, breakeven, lab table
m = B.market_mode(13, 64656, 75000)
assert m["mode"] == "accumulate" and m["dca_mult"] == 1.5 and m["swing_ok"] is False
assert B.market_mode(50, 100, 90) == {"mode": "normal", "dca_mult": 1.0, "swing_ok": True, "above_200d": True, "fear_greed": 50.0}
assert B.market_mode(80, 100, 90)["mode"] == "defend" and B.market_mode(80, 100, 90)["dca_mult"] == 0.5
assert B.market_mode(None)["mode"] == "normal" and B.market_mode(None)["swing_ok"] is False     # unknown trend: no swing
bl = B.buy_ladder(64000, 150)
assert [r["usd"] for r in bl] == [45.0, 45.0, 60.0] and bl[0]["price"] == 57600.0 and B.buy_ladder(0, 150) == []
sl = B.sell_ladder(100, 1)
assert [r["price"] for r in sl] == [125.0, 150.0, 200.0] and sum(r["qty"] for r in sl) == 0.75
rb = {r["asset"]: r["action_usd"] for r in B.rebalance({"BTC": 700, "ETH": 100, "USDT": 200}, {"BTC": 50, "ETH": 20, "USDT": 30})}
assert rb == {"BTC": -200.0, "ETH": 100.0, "USDT": 100.0}
assert B.rebalance({"BTC": 52, "USDT": 48}, {"BTC": 50, "USDT": 50})[0]["action_usd"] == 0.0     # inside the 5% band
assert B.breakeven_gain_pct(70) == 233.3 and B.breakeven_gain_pct(100) is None
tb = B.strategy_table({"a|1d": {"school": "X", "side": "buy", "n": 40, "mean_pct": 2, "base_pct": 0, "t": 3.2},
                       "b|1w": {"school": "Y", "side": "exit", "n": 10, "mean_pct": 9, "base_pct": 0, "t": 5.0},
                       "c|1d": {"school": "Z", "side": "buy", "n": 50, "mean_pct": -5, "base_pct": 0, "t": -3.5}})
assert [r["setup"] for r in tb] == ["a", "c"] and tb[0]["verdict"] == "worked in the past" and tb[1]["verdict"] == "worse than normal"
print("spot budget options: OK")

# spot chart tab (2026-11-16): the Workspace document builds for the spot symbols, and the tab opens without an exception
from modules.workspace import build_workspace_html
import modules.spot_page as SP
doc = build_workspace_html(SP.CHART_SYMS, [], "en", asset_cls="Crypto")
assert len(doc) > 100000 and "BTC-USDT" in doc and "HL:xyz:GOLD" in doc
with mock.patch("requests.get", boom), mock.patch("requests.post", boom):
    at = AppTest.from_string("""
import modules.spot_page as sp, tempfile, streamlit as st
from modules.spot_store import LocalStore
sp.STORE = LocalStore(tempfile.mkdtemp())
st.session_state["spc_on"] = True
sp.render()
""", default_timeout=120)
    at.run()
    assert not at.exception, at.exception
    opts = at.get("button_group")[0].options          # the page's one-tab picker (segmented control), not st.tabs
    assert any("Spot chart" in o or "شارت السبوت" in o for o in opts), opts
    at.session_state["sp_tab"] = opts.index(next(o for o in opts if "Spot chart" in o or "شارت السبوت" in o))
    at.run()
    assert not at.exception, at.exception
print("spot chart tab: OK")

# strategies (2026-11-17): every split adds to 100; library + signals tabs exist; the board filter maps to real lab schools
for nm, v in B.STRATEGIES.items():
    assert abs(sum(v["split"].values()) - 100) < 1e-9 and v["en"] and v["ar"], nm
import json as _json
_ev = _json.load(open(os.path.join(os.path.dirname(__file__), "..", "data", "spot_setup_evidence.json"), encoding="utf8"))["setups"]
_schools = {v["school"] for v in _ev.values()}
for nm, (sch, side) in SP.SIGNAL_STRATEGIES.items():
    assert side in (None, "buy", "exit")
    for s_ in (sch or ()):
        assert any(str(k).startswith(s_) for k in _schools), (nm, s_)
with mock.patch("requests.get", boom), mock.patch("requests.post", boom):
    at = AppTest.from_string("""
import modules.spot_page as sp, tempfile, streamlit as st
from modules.spot_store import LocalStore
sp.STORE = LocalStore(tempfile.mkdtemp())
st.session_state["sg_on"] = True
sp.render()
""", default_timeout=180)
    at.run()
    assert not at.exception, at.exception
    labs = at.get("button_group")[0].options          # the page's one-tab picker (segmented control), not st.tabs
    assert any("Signals" in l for l in labs) and any("Setup library" in l for l in labs), labs
print("spot strategies + signals board: OK")
