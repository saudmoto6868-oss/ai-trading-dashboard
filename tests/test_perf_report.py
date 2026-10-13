"""Run: python tests/test_perf_report.py"""
import os, sys, io
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from modules.perf_report import returns_from_trades, perf_stats

CSV = """time,symbol,side,tf,r
2026-10-01T10:00:00.000Z,BTC,long,1h,2.0
2026-10-01T10:00:00.000Z,ETH,short,1h,-1.0
2026-10-02T12:00:00.000Z,BTC,long,1h,-1.0
2026-10-03T09:30:00.000Z,SOL,long,4h,1.5
2026-10-04T09:30:00.000Z,BTC,short,1h,-1.0
2026-10-05T09:30:00.000Z,BTC,long,1h,2.5
2026-10-06T09:30:00.000Z,BTC,long,1h,-1.0
"""


def test_returns():
    r = returns_from_trades(pd.read_csv(io.StringIO(CSV)), 1.0)
    assert len(r) == 6                                    # the two trades closing together are summed
    assert abs(r.iloc[0] - 0.01) < 1e-12                  # +2R and -1R at 1% risk = +1%
    assert r.index.is_monotonic_increasing


def test_stats():
    r = returns_from_trades(pd.read_csv(io.StringIO(CSV)), 1.0)
    s = perf_stats(r)
    assert s["n"] == 6 and s["max_drawdown"] < 0 and 0 < s["win_rate"] < 1, s


def test_bad_columns():
    try:
        returns_from_trades(pd.DataFrame({"a": [1], "b": [2]}))
    except ValueError:
        return
    raise AssertionError("expected ValueError")


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn(); print("ok", name)
