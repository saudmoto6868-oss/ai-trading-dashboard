import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.rsi_heatmap import rsi_wilder, rsi_zone, _measure, _alignment, rsi_band, BANDS, board_html, _next_close_ms


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


def test_board_html_embeds_data_safely():
    item = {"sym": "BTC", "full": "BTC-USDT", "rank": 1, "price": 1.0, "rsi": {"4h": 55.0}, "rsi_map": 55.0,
            "state": "x</script><b>", "speed": "", "regime": "Trend", "next_close": None, "flow": None,
            "verdict": "Long setup", "dir": 1, "conv": 44, "votes": None, "plan": None, "fresh": None}
    html = board_html([item], "4h", ["4h"])
    assert "__DATA__" not in html and "x<\\/script>" in html and '"avg": 55.0' in html


def test_next_close_from_last_closed_candle():
    assert _next_close_ms("2026-11-15 08:00:00", "4h") == 1794729600000 + 2 * 4 * 3600 * 1000
    assert _next_close_ms("18", "4h") is None


if __name__ == "__main__":   # CI runs plain `python3 tests/x.py`; without this nothing executes
    _tests = [f for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    for _t in _tests:
        _t()
    print(f"ok rsi heatmap ({len(_tests)} tests)")
