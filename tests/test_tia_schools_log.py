"""TIA: desk schools block (spot_plan engine on 1D/1W/1M) and the Director run log. Mock candles, no network.
Run: PYTHONPATH=. python3 tests/test_tia_schools_log.py"""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from modules import market_cache as mc, tia_intelligence as T  # noqa: E402


def candles(n=300, seed=1):
    rng = np.random.default_rng(seed)
    close = 100 + np.cumsum(rng.normal(0.1, 1.0, n))
    df = pd.DataFrame({"open": close, "high": close + 1, "low": close - 1, "close": close, "volume": 1000.0})
    df["ts"] = pd.date_range("2020-01-01", periods=n, freq="D")
    return df


# 1. schools block: the desk engine runs on candles from market_cache
mc.get_klines = lambda symbol, tf, limit=300: candles()
sch = T._schools("BTC-USDT")
assert sch["ok"] and sch["rows"] and "score" in sch and "action" in sch, sch
assert {r["tf"] for r in sch["rows"]} <= {"1d", "1w", "1mo"}, sch["rows"]
print("ok schools from desk engine:", sch["action"], "score", sch["score"], "rows", len(sch["rows"]))

# 2. no candles -> the block says why, it does not raise
mc.get_klines = lambda symbol, tf, limit=300: (_ for _ in ()).throw(RuntimeError("no data"))
sch = T._schools("BTC-USDT")
assert sch["ok"] is False and "why" in sch
print("ok schools unavailable is reported:", sch["why"][:60])

# 3. Director run is logged as one JSON line
path = os.path.join(tempfile.mkdtemp(), "log.jsonl")
T.LOG_PATH = path
T.log_report({"asof_utc": "2026-11-17T00:00:00+00:00", "symbol": "BTC-USDT", "asset_class": "Crypto", "stance": "MIXED / WAIT",
              "score": 0.0, "confidence": "LOW", "schools": {"score": 10, "action": "wait"}})
rows = [json.loads(l) for l in open(path, encoding="utf-8")]
assert len(rows) == 1 and rows[0]["symbol"] == "BTC-USDT" and rows[0]["schools_action"] == "wait", rows
print("ok director run logged")

# 4. logging failure never raises
T.LOG_PATH = "/proc/forbidden/x.jsonl"
T.log_report({"symbol": "X"})
print("ok log failure is silent")
print("ALL OK")
