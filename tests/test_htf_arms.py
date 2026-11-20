"""research/htf_arms: HTF state has no look-ahead, arms are assigned as pre-registered, bootstrap sanity. Plain script."""
import numpy as np
import pandas as pd

from research.htf_arms.run_htf_arms import arm, bootstrap, htf_state, tag

# arms
assert arm(1, 1, .5) == "W" and arm(-1, -1, .9) == "W"
assert arm(1, -1, .2) == "A_ext" and arm(-1, 1, .8) == "A_ext"     # against, long in discount / short in premium
assert arm(1, -1, .6) == "A_mid" and arm(-1, 1, .4) == "A_mid"
assert arm(1, 0, .1) == "F"

# HTF state: steady uptrend -> trend +1, close at the top of the range
t = pd.date_range("2026-01-01", periods=60, freq="D")
c = np.linspace(100, 160, 60)
htf = pd.DataFrame({"time": t, "open": c - .5, "high": c + 1, "low": c - 1, "close": c})
st = htf_state(htf)
assert (st["trend"] == 1).all() and st["pos"].iloc[-1] > .9

# no look-ahead: a signal inside day k is tagged with the bar that CLOSED before it (day k-1), never day k
flip = htf.copy(); flip.loc[59, ["open", "high", "low", "close"]] = [40, 41, 39, 40]   # the last day crashes
st2 = htf_state(flip)
inside_last_day = int(pd.Timestamp("2026-03-01 12:00").value // 10**6)   # t[59] = 2026-03-01, still open at 12:00
ev = [{"ts": inside_last_day, "d": 1}]
tag(ev, None, st2, "h")
assert ev[0]["h"] == "W", ev   # the crash bar is not closed yet at 12:00, so the uptrend state is used

# bootstrap: positive edge -> positive median; higher risk -> deeper drawdown
rs = np.r_[np.full(60, 1.5), np.full(40, -1.0)]
lo, hi = bootstrap(rs, .0025), bootstrap(rs, .005)
assert lo["median_ret_pct"] > 0 and hi["mdd_p95_pct"] > lo["mdd_p95_pct"]
assert bootstrap(rs[:10], .005) is None   # under 30 trades: not evidence
print("ok htf_arms")
