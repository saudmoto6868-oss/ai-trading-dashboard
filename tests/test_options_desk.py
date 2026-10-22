"""Checks for modules/options_desk.py with a hand-made Deribit-shaped payload (no network)."""
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules import options_desk as O  # noqa: E402


def _r(name, oi, vol=0, iv=50.0, px=100.0):
    return {"instrument_name": name, "open_interest": oi, "volume": vol, "mark_iv": iv, "underlying_price": px}


ROWS = [_r("BTC-27NOV26-90-P", 10, 2, 60), _r("BTC-27NOV26-100-P", 30, 5, 50), _r("BTC-27NOV26-100-C", 20, 8, 50),
        _r("BTC-27NOV26-110-C", 40, 4, 45), _r("BTC-27NOV26-110-P", 5, 0, 52),
        _r("BTC-25DEC26-100-C", 10, 1, 55), _r("BTC-25DEC26-100-P", 10, 1, 55), _r("BTC-01JAN20-100-C", 99, 1, 40),
        {"instrument_name": "BTC-PERPETUAL", "open_interest": 1}]


def test_parse():
    assert O.parse("BTC-27NOV26-73000-P") == (date(2026, 11, 27), 73000.0, "P")
    assert O.parse("BTC-PERPETUAL") is None and O.parse("") is None and O.parse(None) is None


def test_max_pain_and_summary():
    s = O.summarize(ROWS, today=date(2026, 10, 22))
    assert [e["exp"] for e in s["expiries"]] == [date(2026, 11, 27), date(2026, 12, 25)]   # the 2020 expiry and the perpetual are dropped
    e = s["expiries"][0]
    assert e["days"] == 36 and e["oi"] == 105 and e["pc_oi"] == round(45 / 60, 2) and e["pc_vol"] == round(7 / 12, 2)
    assert e["max_pain"] == 100.0   # at 100: calls pay 40*0 + 20*0, puts pay 10*(90-100)->0 ... lowest total
    assert e["iv"] == 50.0 and e["walls"][0] == (110.0, "C", 40.0)
    assert s["totals"]["oi"] == 125 and s["spot"] == 100.0
    assert e["skew10"] == round(60 - 45, 1)   # 90 put IV minus 110 call IV


def test_strikes():
    k = O.strikes(ROWS, date(2026, 11, 27), 100.0, 0.15)
    assert k == [(90.0, 0.0, 10.0), (100.0, 20.0, 30.0), (110.0, 40.0, 5.0)]


if __name__ == "__main__":
    test_parse(); test_max_pain_and_summary(); test_strikes(); print("ok options_desk")
