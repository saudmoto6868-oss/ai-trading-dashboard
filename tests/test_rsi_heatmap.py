from modules.rsi_heatmap import rsi_wilder, rsi_zone, _measure, _alignment


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
