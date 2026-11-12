from modules.rsi_heatmap import rsi_wilder, rsi_zone


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
