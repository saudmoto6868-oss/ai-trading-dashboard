"""Checks for modules/chart_explain.py (synthetic candles; runs as a script or under pytest)."""
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules import chart_explain as X  # noqa: E402


def _df(rows):
    """rows: (open, high, low, close); a flat 20-candle lead-in with 1-point bodies sets the average body."""
    lead = [(100 + (i % 2), 101.5, 99.5, 100 + ((i + 1) % 2)) for i in range(20)]
    return pd.DataFrame(lead + rows, columns=["open", "high", "low", "close"])


def test_engulfing_and_hammer():
    d = _df([(100, 100.5, 98, 98.5), (99, 99.2, 97, 97.5), (97.5, 97.6, 96, 96.2), (96.5, 96.6, 95.5, 96), (96, 96.2, 95.4, 95.6),
             (95.8, 95.9, 95.0, 95.2), (95.2, 95.3, 94.6, 94.8), (94.8, 94.9, 94.0, 94.3), (94.0, 97.0, 93.9, 96.8)])
    assert "bull_engulf" in X.candles(d)
    h = _df([(100, 100.2, 98, 98.5), (98.5, 98.6, 97, 97.2), (97.2, 97.3, 96, 96.3), (96.3, 96.4, 95, 95.4), (95.4, 95.5, 94.2, 94.5),
             (94.5, 94.6, 93.5, 93.8), (93.6, 93.95, 90.5, 93.9)])
    assert "hammer" in X.candles(h)


def test_doji_inside_and_texts():
    d = _df([(100, 102, 98, 100.05), (100.2, 101, 99, 100.1)])
    out = X.candles(d)
    assert "inside" in out
    d3 = pd.concat([d] * 3, ignore_index=True)
    en = X.explain(d3, ["cp_hs", "tl_up", "rsi_lt30"])   # default language is English
    assert [p[0] for p in en["patterns"]] == ["Head and shoulders", "Falling trendline broken upward"]
    import re
    assert not re.search("[؀-ۿ]", repr(en)) and all(k in X.CANDLE_EN for k in out)
    ex = X.explain(d3, ["cp_hs", "tl_up", "rsi_lt30"], ar=True)
    assert [p[0] for p in ex["patterns"]] == ["رأس وكتفين", "كسر خط الترند الهابط لفوق"]
    assert ex["ema"] and all(isinstance(s, str) for s in ex["ema"])
    assert all(k in X.CANDLE_AR for k in out)


if __name__ == "__main__":
    test_engulfing_and_hammer(); test_doji_inside_and_texts(); print("ok chart_explain")
