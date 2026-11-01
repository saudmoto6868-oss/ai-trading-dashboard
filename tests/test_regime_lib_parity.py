"""modules/regime_lib.label (per-candle series used by the hub tabs) and modules/regime.classify (latest candle, Radar / Workspace chip) are ONE definition:
on candles without volume both give the same label at every bar (HiVol == Hi-Vol). If one changes, this fails."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np, pandas as pd
from modules.regime import classify
from modules.regime_lib import label, TO_RADAR

checked = 0
for seed in range(40):
    g = np.random.default_rng(seed); n = 420
    cl = 100 + np.cumsum(g.normal(0, 0.4, n)); sp = np.abs(g.normal(0.3, 0.15, n))
    if seed % 3 == 0:
        cl[300:] += np.cumsum(g.normal(0.2, 0.3, n - 300))
    df = pd.DataFrame({"high": cl + sp, "low": cl - sp, "close": cl})
    lab = label(df.high, df.low, df.close)
    for i in range(240, n, 7):
        r, l = classify(df.iloc[:i + 1])["regime"], TO_RADAR.get(lab[i], lab[i])
        assert r == l, (seed, i, r, l)
        checked += 1
assert checked > 1000
print("regime_lib == regime.classify on", checked, "bars: OK")
