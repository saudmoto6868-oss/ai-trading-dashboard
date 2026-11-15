import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.rsi_heatmap import rsi_wilder, rsi_zone, _measure, _alignment, rsi_band, heatmap_points, heatmap_spec, BANDS


def test_rsi_flat_market_is_neutral():
    assert rsi_wilder([100] * 20) == 50.0


def test_rsi_all_gains_is_100():
    assert rsi_wilder(list(range(20))) == 100.0


def test_rsi_all_losses_is_zero():
    assert rsi_wilder(list(range(20, 0, -1))) == 0.0


def test_rsi_needs_more_than_period_observations():
    assert rsi_wilder(list(range(14)), 14) is None


def test_rsi_zone_boundaries():
    assert rsi_zone(70) == "Overbought"
    assert rsi_zone(30) == "Oversold"
    assert rsi_zone(50) == "Neutral"


def test_measure_uses_only_closed_candles():
    import pandas as pd
    frame = pd.DataFrame({"time": range(20), "close": list(range(100, 120))})
    measured = _measure(frame)
    assert measured is not None
    assert measured["price"] == 118.0
    assert measured["last_closed"] == "18"


def test_alignment_requires_all_selected_timeframes():
    data = {"15m": {"trend": "Bullish"}, "1h": {"trend": "Bullish"}, "4h": {"trend": "Bullish"}}
    assert _alignment(data, ["15m", "1h", "4h"]) == "Bullish alignment"
    assert _alignment(data, ["15m", "1h", "4h", "1d"]) == "Partial"
    data["4h"]["trend"] = "Bearish"
    assert _alignment(data, ["15m", "1h", "4h"]) == "Mixed"


def test_rsi_band_five_coinglass_zones():
    assert [rsi_band(v) for v in (85, 70, 65, 60, 50, 40, 35, 30, 10)] == [
        "Overbought", "Overbought", "Strong", "Strong", "Neutral", "Weak", "Weak", "Oversold", "Oversold"]
    assert rsi_band(None) == "Unavailable"
    assert [b[0] for b in BANDS] == ["Overbought", "Strong", "Neutral", "Weak", "Oversold"]


def test_heatmap_points_keep_rank_and_skip_missing():
    detail = {"BTC-USDT": {"4h": {"rsi": 72.0, "price": 1.0}, "1d": {"rsi": 55.0, "price": 1.0}},
              "ETH-USDT": {"1d": {"rsi": 40.0, "price": 2.0}},
              "Y:GC=F": {"4h": {"rsi": 25.0, "price": 3.0}}}
    pts = heatmap_points(detail, ["BTC-USDT", "ETH-USDT", "Y:GC=F"], "4h", ["4h", "1d"])
    assert [(p["rank"], p["symbol"], p["band"]) for p in pts] == [(1, "BTC", "Overbought"), (3, "GC=F", "Oversold")]
    assert pts[0]["RSI 1d"] == 55.0 and pts[1]["RSI 1d"] is None


def test_heatmap_spec_average_and_layers():
    pts = [{"rank": 1, "symbol": "A", "full": "A", "rsi": 80.0, "band": "Overbought", "price": 1.0},
           {"rank": 2, "symbol": "B", "full": "B", "rsi": 20.0, "band": "Oversold", "price": 1.0}]
    spec, avg = heatmap_spec(pts, "4h", ["4h"])
    assert avg == 50.0
    marks = [l["mark"]["type"] for l in spec["layer"]]
    assert marks.count("rect") == 1 and "circle" in marks and marks.count("rule") == 2
    empty, none_avg = heatmap_spec([], "4h", ["4h"])
    assert none_avg is None


if __name__ == "__main__":   # CI runs plain `python3 tests/x.py`; without this nothing executes
    _tests = [f for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    for _t in _tests:
        _t()
    print(f"ok rsi heatmap ({len(_tests)} tests)")
