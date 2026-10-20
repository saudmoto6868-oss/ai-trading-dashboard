"""Mock test: Biquote fallback parsing + market_cache fallback order (no network)."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules import biquote_feed as bf, market_cache as mc, yahoo_feed as yf

assert bf.symbol_for("Y:EURUSD=X") == "EURUSD" and bf.symbol_for("Y:GC=F") == "XAUUSD" and bf.symbol_for("Y:^GSPC") is None

class Fake:
    def __init__(self, fail4h=False): self.calls = []; self.fail4h = fail4h
    def ohlc(self, s, interval="1h", limit=500):
        self.calls.append((s, interval))
        if interval == "4h" and self.fail4h: raise RuntimeError("bad interval")
        t0 = 1_700_000_000 - 1_700_000_000 % 3600
        return [{"time": t0 + 3600 * i, "open": 1 + i * .001, "high": 1.01 + i * .001, "low": .99 + i * .001, "close": 1.005 + i * .001} for i in range(200)]

df = bf.get_klines("Y:EURUSD=X", "1h", 100, client=Fake())
assert len(df) == 100 and list(df.columns[:5]) == ["time", "open", "high", "low", "close"] and (df.volume == 0).all()
bf._cache.clear(); f = Fake(fail4h=True)
d4 = bf.get_klines("Y:GC=F", "4h", 50, client=f)
assert len(d4) <= 50 and ("XAUUSD", "1h") in f.calls and len(d4) > 10
try: bf.parse_ohlc([{"x": 1}]); raise SystemExit("should fail")
except ValueError: pass

# market_cache: Yahoo fails -> Biquote answers
yf.get_yahoo_klines = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("Yahoo rate limit (429)"))
bf.get_klines = lambda s, tf, limit=300, client=None: df
mc._cache.clear()
out = mc.get_klines("Y:EURUSD=X", "15m", 50)
assert out is df
# nothing can serve an index -> original error surfaces
mc._cache.clear()
try: mc.get_klines("Y:^GSPC", "15m", 50); raise SystemExit("should raise")
except RuntimeError as e: assert "429" in str(e)
print("biquote tests OK")
