"""Run: python tests/test_confirm_only.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.scorer import aggregate

S = lambda fam, key, d="bullish": {"family": fam, "key": key, "direction": d, "name": key}


def test_msb_alone_starts_nothing():
    a = aggregate([S("MSB-OB", "msb_ob")])
    assert a["direction"] == "neutral" and a["stars"] == 0, a


def test_msb_confirms_existing_setup():
    a = aggregate([S("Liquidity", "sweep"), S("MSB-OB", "msb_ob")])
    assert a["direction"] == "bullish" and a["stars"] == 2, a          # sweep (primary) + MSB confirmation


def test_order_block_still_counts_alone():
    a = aggregate([S("MSB-OB", "ob")])
    assert a["direction"] == "bullish" and a["stars"] == 1, a          # plain order block is not a direct signal


def test_msb_against_nothing_does_not_flip():
    a = aggregate([S("Liquidity", "sweep", "bearish"), S("MSB-OB", "msb_ob", "bullish")])
    assert a["direction"] == "bearish", a


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn(); print("ok", name)
