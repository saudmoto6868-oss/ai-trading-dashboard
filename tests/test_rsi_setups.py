import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd
from modules.rsi_setups import rsi_phase, speed_dots, read_setup


def test_phase_reversals_and_momentum():
    assert rsi_phase(65, 74) == "rev_down"
    assert rsi_phase(35, 25) == "rev_up"
    assert rsi_phase(80, 72) == "ext_up"
    assert rsi_phase(75, 82) == "stall_ob"
    assert rsi_phase(20, 28) == "ext_dn"
    assert rsi_phase(62, 55) == "mom_up"
    assert rsi_phase(38, 45) == "mom_dn"
    assert rsi_phase(50, 52, "Squeeze") == "squeeze"
    assert rsi_phase(50, 52, "Trend") == "drift"
    assert rsi_phase(None, None) == "drift"


def test_speed_dots():
    assert speed_dots(70, 50) == "●●"
    assert speed_dots(60, 51) == "●"
    assert speed_dots(55, 52) == ""
    assert speed_dots(None, 50) == ""


def _ohlcv(close):
    close = np.asarray(close, float)
    return pd.DataFrame({"time": range(len(close)), "open": close, "high": close * 1.002,
                         "low": close * 0.998, "close": close, "volume": np.full(len(close), 100.0)})


def test_read_setup_on_rally_is_overbought_and_ranked():
    rng = np.random.default_rng(1)
    up = 100 * np.exp(np.cumsum(np.r_[rng.normal(0, 0.003, 200), np.full(20, 0.01)]))
    s = read_setup(_ohlcv(up))
    assert s["group"] == "Extended" and s["phase"] in ("ext_up", "stall_ob")


def test_read_setup_rejects_short_or_missing():
    assert read_setup(None) is None
    assert read_setup(_ohlcv([1.0] * 10)) is None


if __name__ == "__main__":   # CI runs plain `python3 tests/x.py`
    _tests = [f for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    for _t in _tests:
        _t()
    print(f"ok rsi setups ({len(_tests)} tests)")
