import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd
from modules.rsi_confluence import SCHOOLS, conviction, school_of, school_votes, trade_plan, verdict


def test_keys_map_to_schools():
    assert school_of({"key": "fvg"}) == "Imbalance"
    assert school_of({"key": "breaker"}) == "Structure"
    assert school_of({"key": "sweep"}) == "Liquidity"
    assert school_of({"key": "other", "family": "Elliott"}) == "Elliott"
    assert len(SCHOOLS) == 9


def test_votes_and_conviction_count_schools():
    sigs = [{"key": "fvg", "direction": "bullish", "name": "FVG", "vals": {"ago": 2}},
            {"key": "ob", "direction": "bullish", "name": "OB"},
            {"key": "ma_cross", "direction": "bearish", "name": "EMA cross"}]
    v = school_votes(sigs, harmonics=[{"name": "Gartley", "dir": "bull"}], patterns=[("Channel up", "buy")],
                     phase="rev_up", flow_vote=-1)
    assert v["Imbalance"]["vote"] == 1 and v["Imbalance"]["ago"] == 2
    assert v["Trend"]["vote"] == -1 and v["Order flow"]["vote"] == -1 and v["Fib/Harmonic"]["vote"] == 1
    c = conviction(v)
    assert (c["bull"], c["bear"], c["dir"]) == (5, 2, 1) and c["conv"] == round(100 * 3 / 9)
    assert verdict(c) == "Bullish build-up"
    assert verdict(conviction(school_votes([], phase="ext_up")), "ext_up") == "Leaning up"


def test_verdict_topping_and_squeeze():
    c = {"dir": -1, "conv": 22, "bull": 1, "bear": 3}
    assert verdict(c, "stall_ob") == "Topping: overbought, sellers building"
    assert verdict({"dir": 0, "conv": 0, "bull": 0, "bear": 0}, "squeeze", "Squeeze").startswith("Coiling")


def test_trade_plan_uses_levels_and_atr():
    c = np.linspace(100, 110, 60)
    df = pd.DataFrame({"open": c, "high": c + 0.5, "low": c - 0.5, "close": c})
    p = trade_plan(df, 1, levels=([115.0], [105.0]))
    assert p["entry"] == 110 and p["stop"] < 105 and p["target"] == 115 and p["rr"] > 0
    q = trade_plan(df, -1, levels=([], []))   # no levels -> 1.5 ATR stop, 2R target
    assert q["stop"] > 110 and abs(q["rr"] - 2.0) < 1e-9
    assert trade_plan(df, 0) is None


if __name__ == "__main__":   # CI runs plain `python3 tests/x.py`
    _tests = [f for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    for _t in _tests:
        _t()
    print(f"ok rsi confluence ({len(_tests)} tests)")
