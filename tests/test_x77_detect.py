"""X77 detect: labels repo detector hits with schools. Synthetic candles only (mock-tested, not evidence).
Run: python3 -I tests/test_x77_detect.py"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from modules import x77_detect as X  # noqa: E402

rng = np.random.default_rng(7)
n = 400
c = 100 + np.cumsum(rng.normal(0.05, 1.0, n))
o = np.r_[c[0], c[:-1]]
h = np.maximum(o, c) + rng.uniform(0, 0.8, n)
lo = np.minimum(o, c) - rng.uniform(0, 0.8, n)
ts = pd.date_range("2026-01-01", periods=n, freq="h", tz="UTC")
df = pd.DataFrame({"time": ts, "open": o, "high": h, "low": lo, "close": c, "volume": rng.uniform(100, 1000, n)})

res = X.events(df)
assert set(res) == {"events", "patterns", "regime", "errors"}, res.keys()
for e in res["events"]:
    assert e["school"].startswith("S_") and e["event"] and e["side"] in ("bullish", "bearish"), e
assert isinstance(X.summary(res), dict)
assert X.events(df.head(10))["errors"] == ["not enough candles (need 60)"]
# every mapped key belongs to a known school prefix
assert all(s.startswith("S_") and ev for s, ev in X.KEY_MAP.values())
assert res["errors"] == [], res["errors"]
print(f"x77_detect: passed ({len(res['events'])} events, {len(res['patterns'])} patterns, regime={res['regime']}, errors={len(res['errors'])})")
