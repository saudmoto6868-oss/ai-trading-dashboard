"""Yahoo disk cache: fresh copy served without a fetch, stale copy used when Yahoo fails, no network. Plain script."""
import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pandas as pd  # noqa: E402
from modules import yahoo_feed as Y  # noqa: E402

tmp = Path(tempfile.mkdtemp())
Y.CACHE_DIR = tmp / "yc"
calls = {"n": 0, "fail": False}


def fake_fetch(sym, tf, limit=300):
    calls["n"] += 1
    if calls["fail"]:
        raise RuntimeError("Yahoo unreachable (test)")
    t0 = pd.Timestamp("2026-11-20", tz=None)
    return pd.DataFrame({"time": [t0 + pd.Timedelta(minutes=i) for i in range(limit)],
                         "open": [1.0] * limit, "high": [2.0] * limit, "low": [0.5] * limit,
                         "close": [1.5] * limit, "volume": [10.0] * limit})


Y._fetch_yahoo = fake_fetch
sym, tf = "Y:COMI.CA", "5m"

df1 = Y.get_yahoo_klines(sym, tf, limit=50)
assert calls["n"] == 1 and len(df1) == 50, calls
df2 = Y.get_yahoo_klines(sym, tf, limit=50)
assert calls["n"] == 1 and len(df2) == 50, "fresh copy must not refetch"

# stale (older than TTL, younger than 6 x TTL) and Yahoo down -> stale copy, not an error
p = Y._cache_path(sym, tf)
ttl = 30  # market_cache TTL for 5m
os.utime(p, (time.time() - ttl * 2, time.time() - ttl * 2))
calls["fail"] = True
df3 = Y.get_yahoo_klines(sym, tf, limit=50)
assert len(df3) == 50 and calls["n"] == 2, calls

# too old and Yahoo down -> error surfaces
os.utime(p, (time.time() - ttl * 10, time.time() - ttl * 10))
try:
    Y.get_yahoo_klines(sym, tf, limit=50)
    raise AssertionError("expected error when cache too old")
except RuntimeError:
    pass

# no cache directory writes escape the temp dir
assert str(p).startswith(str(tmp)), p
print("ALL OK yahoo cache")
