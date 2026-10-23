"""modules/market_map.apply_filters: every heat-map filter really changes the result."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd  # noqa: E402
from modules.market_map import apply_filters as F, board  # noqa: E402


def _df():
    rows = [{"id": "xyz:GOLD", "cls": "Metals", "px": 110, "prev": 100, "vol": 500}, {"id": "xyz:SILVER", "cls": "Metals", "px": 97, "prev": 100, "vol": 200},
            {"id": "xyz:META", "cls": "Stocks", "px": 102, "prev": 100, "vol": 900}, {"id": "xyz:EUR", "cls": "Forex", "px": 100.2, "prev": 100, "vol": 100}]
    return board(rows)


def test_filters():
    d = _df()
    assert len(F(d)) == 4
    assert set(F(d, ["Metals"])["cls"]) == {"Metals"} and len(F(d, ["Metals"])) == 2
    assert list(F(d, top_n=2)["name"]) == ["META", "GOLD"] or set(F(d, top_n=2)["name"]) == {"META", "GOLD"}
    assert all(F(d, direction="up")["chg"] > 0) and all(F(d, direction="down")["chg"] < 0)
    assert all(F(d, min_abs=2)["chg"].abs() >= 2) and len(F(d, min_abs=2)) == 3
    assert list(F(d, q="gol")["name"]) == ["GOLD"]
    assert F(d, sort="chg")["chg"].is_monotonic_decreasing and F(d, sort="chg_abs").iloc[0]["name"] == "GOLD" and F(d, sort="vol").iloc[0]["name"] == "META"
    assert F(d, ["Forex"], q="zzz").empty and F(pd.DataFrame(columns=d.columns)).empty
    assert len(F(d, ["Metals"], 0, "up", 5)) == 1                                # combined: only GOLD (+10%)


if __name__ == "__main__":
    test_filters(); print("ok market_map filters")
