import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.rsi_flow import feed_of, fetch_flow, flow_read


def test_feed_of():
    assert feed_of("BTC-USDT") == ("okx", "BTC-USDT")
    assert feed_of("ETH-USDT-SWAP") == ("okx", "ETH-USDT-SWAP")
    assert feed_of("HL:xyz:GOLD") == ("hl", "xyz:GOLD")
    assert feed_of("Y:GC=F") == (None, None)
    assert feed_of("COMI.CA") == (None, None)


def test_no_feed_is_explicit_not_invented():
    assert fetch_flow("Y:^GSPC") == {"ok": False, "why": "no flow feed"}
    assert flow_read({"ok": False, "why": "no flow feed"})["vote"] == 0


def test_flow_read_votes():
    bull = {"ok": True, "tape": {"ok": True, "buy_share": 0.62, "big_n": 5, "big_buy": 4, "big_sell": 1},
            "book": {"ok": True, "imbalance": 0.2}, "deriv": {"ok": True, "funding": 0.005}}
    r = flow_read(bull)
    assert r["vote"] == 1 and r["text"].startswith("🟢") and "buy 62%" in r["text"] and "book +20%" in r["text"]
    crowded = {"ok": True, "tape": {"ok": True, "buy_share": 0.5}, "book": {"ok": False},
               "deriv": {"ok": True, "funding": 0.05}}
    assert flow_read(crowded)["vote"] == -1     # crowded longs lean bearish (spot_flow.reading rule)
    assert flow_read(None)["text"] == "—"


if __name__ == "__main__":   # CI runs plain `python3 tests/x.py`
    _tests = [f for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    for _t in _tests:
        _t()
    print(f"ok rsi flow ({len(_tests)} tests)")
