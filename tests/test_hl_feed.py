"""Hyperliquid TradFi feed (server side) with a mocked API: market list, categories, candles, asset-class lists, scanner.
Run: python tests/test_hl_feed.py"""
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules import asset_classes, hl_feed, market_cache  # noqa: E402

# numbers from the live xyz dex (Coinversa Pulse connector, 2026-10-17); xyz:DEAD has no volume and no OI -> hidden
LIVE = [("xyz:XYZ100", 29199, 30009, 3.18e8, 3.17e8), ("xyz:GOLD", 4165.5, 4173.2, 4.9e7, 2.9e8), ("xyz:SILVER", 57.067, 57.774, 1.23e8, 1.6e8),
        ("xyz:CL", 99.322, 95.824, 2.27e8, 1.56e8), ("xyz:SP500", 7646.9, 7756, 2.59e8, 3.39e8), ("xyz:EUR", 1.1244, 1.123, 2.7e6, 2.67e7),
        ("xyz:TSLA", 352.36, 374.25, 1.86e8, 7.3e7), ("xyz:TLT", 79.93, 80.046, 4.7e5, 5.5e6), ("xyz:DEAD", 1, 1, 0, 0)]
calls = []


class R:
    def __init__(self, data, code=200):
        self.status_code, self._d = code, data

    def json(self):
        return self._d


def fake_post(url, json=None, timeout=None):
    calls.append(json)
    if json["type"] == "metaAndAssetCtxs":
        assert json.get("dex") == "xyz"
        return R([{"universe": [{"name": m[0]} for m in LIVE]}, [{"midPx": str(m[1]), "prevDayPx": str(m[2]), "dayNtlVlm": str(m[3]), "openInterest": str(m[4] / m[1])} for m in LIVE]])
    if json["type"] == "candleSnapshot":
        q = json["req"]; ms = hl_feed.MS[q["interval"]]; n = int((q["endTime"] - q["startTime"]) // ms)
        t0 = (q["startTime"] // ms) * ms
        rng = np.random.default_rng(1); c = 4100 + np.cumsum(rng.standard_normal(n) * 5)
        return R([{"t": int(t0 + i * ms), "o": str(c[i] - 1), "h": str(c[i] + 4), "l": str(c[i] - 4), "c": str(c[i]), "v": "12", "n": 3} for i in range(n)][::-1])
    return R({}, 400)


hl_feed.requests.post = fake_post
rows = hl_feed.markets()
ids = [r["id"] for r in rows]
assert "HL:xyz:DEAD" not in ids and ids[0] == "HL:xyz:XYZ100", ids          # sorted by 24h volume
assert {r["id"]: r["cls"] for r in rows}["HL:xyz:GOLD"] == "Metals"
assert hl_feed.category("HL:xyz:CL") == "Oil & Gas" and hl_feed.category("HL:xyz:EUR") == "Forex" and hl_feed.category("HL:xyz:TSLA") == "Stocks"
assert hl_feed.symbols("Indices") == ["HL:xyz:XYZ100", "HL:xyz:SP500"] and hl_feed.symbols("Bonds") == ["HL:xyz:TLT"]
assert hl_feed.tv_symbol("HL:xyz:GOLD") == "OANDA:XAUUSD" and hl_feed.tv_symbol("HL:xyz:TSLA") == "TSLA"
n0 = len(calls); hl_feed.markets(); assert len(calls) == n0, "market list must be cached"

df = hl_feed.get_klines("HL:xyz:GOLD", "1h", 120)
assert len(df) == 120 and list(df.columns) == ["time", "open", "high", "low", "close", "volume"] and df["time"].is_monotonic_increasing
assert calls[-1]["req"]["coin"] == "xyz:GOLD" and calls[-1]["req"]["interval"] == "1h"
try:
    hl_feed.get_klines("HL:xyz:GOLD", "13m")
    raise AssertionError("13m must be refused")
except ValueError:
    pass

# market_cache routes HL: symbols to the Hyperliquid feed
d2 = market_cache.get_klines("HL:xyz:GOLD", "4h", 100)
assert len(d2) == 100 and calls[-1]["req"]["interval"] == "4h"

# asset-class lists put Hyperliquid first and still work when OKX is down
asset_classes._load = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("OKX down"))
syms, note = asset_classes.class_symbols("Metals", [], top=5, mtype="SWAP")
assert syms[:2] == ["HL:xyz:SILVER", "HL:xyz:GOLD"], (syms, note)
asset_classes._load = lambda *a, **k: [{"id": "XAU-USDT-SWAP", "cls": "Metals", "vol": 5.0}]
syms, note = asset_classes.class_symbols("Metals", [], top=5, mtype="SWAP")
assert syms == ["HL:xyz:SILVER", "HL:xyz:GOLD", "XAU-USDT-SWAP"], syms
assert "Bonds" in asset_classes.CLASSES

# the multi-timeframe scanner runs on a Hyperliquid symbol end to end
from modules.scorer import fetch_tfs, scan_symbol  # noqa: E402
frames, errs = market_cache.fetch_frames(["HL:xyz:GOLD"], fetch_tfs("1h"))
assert not errs, errs
res = scan_symbol("HL:xyz:GOLD", frames["HL:xyz:GOLD"], "1h")
assert res.get("symbol", "HL:xyz:GOLD") == "HL:xyz:GOLD" and "direction" in res, list(res)
from modules.arabic import tv_link  # noqa: E402
assert "OANDA:XAUUSD" in tv_link("HL:xyz:GOLD", "1h")
print("test_hl_feed: all passed")
