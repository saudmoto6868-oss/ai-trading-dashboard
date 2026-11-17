"""Mock test (no network): market_cache negative cache, source circuit breaker and no-retry while paused.
Run: PYTHONPATH=. python3 tests/test_market_cache_breaker.py"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import pandas as pd  # noqa: E402
import requests  # noqa: E402
from modules import market_cache as mc  # noqa: E402

CLOCK = {"t": 1000.0}
mc._now = lambda: CLOCK["t"]
CALLS = {"okx": 0}
DEAD = {"on": True}


def fake_okx(symbol, interval="1h", limit=300):
    CALLS["okx"] += 1
    if DEAD["on"]:
        raise requests.exceptions.ConnectionError("no route")
    return pd.DataFrame({"close": [1.0, 2.0]})


mc.get_binance_klines = fake_okx


def reset():
    mc._cache.clear(); mc._neg.clear(); mc._src.clear(); CALLS["okx"] = 0
    DEAD["on"] = True


def raises(fn):
    try:
        fn()
    except Exception:
        return True
    return False


# 1. negative cache: the same dead key is not re-requested within NEG_TTL
reset()
assert raises(lambda: mc.get_klines("BTC-USDT", "1h"))
assert raises(lambda: mc.get_klines("BTC-USDT", "1h"))
assert CALLS["okx"] == 1, CALLS
CLOCK["t"] += mc.NEG_TTL + 1
assert raises(lambda: mc.get_klines("BTC-USDT", "1h"))
assert CALLS["okx"] == 2, CALLS
print("ok negative cache")

# 2. breaker: BREAK_AFTER transport failures on different symbols pause OKX; the next symbol makes no request
reset()
for s in ["A-USDT", "B-USDT", "C-USDT"]:
    assert raises(lambda s=s: mc.get_klines(s, "1h"))
assert CALLS["okx"] == 3 and mc.source_paused("OKX"), (CALLS, mc._src)
assert raises(lambda: mc.get_klines("D-USDT", "1h"))
assert CALLS["okx"] == 3, "paused source must not be called"
print("ok breaker opens after", mc.BREAK_AFTER, "transport failures")

# 3. after BREAK_FOR the source is tried again; a success closes the breaker
CLOCK["t"] += mc.BREAK_FOR + 1
DEAD["on"] = False
df = mc.get_klines("E-USDT", "1h")
assert len(df) == 2 and CALLS["okx"] == 4 and not mc.source_paused("OKX") and mc._src["OKX"][0] == 0
print("ok breaker re-opens after pause and resets on success")

# 4. non-transport errors (bad symbol, parse error) do not pause the source
reset()
def bad(symbol, interval="1h", limit=300):
    raise ValueError("bad symbol")
mc.get_binance_klines = bad
for s in ["X1", "X2", "X3", "X4"]:
    assert raises(lambda s=s: mc.get_klines(s, "1h"))
assert not mc.source_paused("OKX"), mc._src
mc.get_binance_klines = fake_okx
print("ok bad-symbol errors do not trip the breaker")

# 5. stale copy is still served when a refresh fails
reset()
DEAD["on"] = False
mc.get_klines("S-USDT", "1h")
CLOCK["t"] += mc.TTL["1h"] + 1
DEAD["on"] = True
df = mc.get_klines("S-USDT", "1h")
assert len(df) == 2
print("ok stale copy served on failure")

# 6. fetch_frames does not sleep or retry for a paused source
reset()
sleeps = []
mc.time.sleep = lambda s: sleeps.append(s)
for s in ["P1", "P2", "P3"]:
    raises(lambda s=s: mc.get_klines(s, "1h"))
assert mc.source_paused("OKX")
frames, errors = mc.fetch_frames(["P4", "P5"], ["1h", "4h"], workers=2)
assert frames["P4"] == {} and "P4" in errors and sleeps == [], (sleeps, errors)
print("ok fetch_frames skips backoff while paused")

print("ALL OK")
