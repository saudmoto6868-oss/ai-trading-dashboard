"""modules/zone_eval.py: loading exported zone logs and the gate (planted effect found, coin flips are not)."""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules import zone_eval as Z  # noqa: E402


def _rec(t, zout, cout, strength=3):
    return {"t": t, "strength": strength, "z": {"touchT": 1, "out": zout}, "c": {"touchT": 1, "out": cout}}


def test_planted_effect_passes_and_random_does_not():
    rng = random.Random(1)
    good = [_rec(i, "hold", "hold" if rng.random() < .3 else "break") for i in range(300)]
    j = Z.judge(Z.load([{"sym": "BTC-USDT", "recs": good}]))
    assert j["paired"] == 300 and j["diff"] > 0.4 and j["t"] > 3 and j["pass"] and j["half1"] > 0 and j["half2"] > 0
    coin = [_rec(i, rng.choice(["hold", "break"]), rng.choice(["hold", "break"])) for i in range(400)]
    j = Z.judge(Z.load([{"sym": "ETH-USDT", "recs": coin}]))
    assert not j["pass"] and abs(j["t"]) < 3.5


def test_gate_needs_n_and_both_halves():
    j = Z.judge([_rec(i, "hold", "break") for i in range(40)])
    assert j["diff"] == 1.0 and not j["pass"]                                    # perfect but only 40 pairs: not evidence
    recs = [_rec(i, "hold", "break") for i in range(100)] + [_rec(100 + i, "break", "hold") for i in range(100)]
    j = Z.judge(recs)
    assert j["half1"] == 1.0 and j["half2"] == -1.0 and not j["pass"]            # good first half, reversed second half
    assert Z.judge([])["paired"] == 0 and Z.judge([])["t"] == 0.0


def test_unresolved_and_untouched_are_ignored():
    recs = [_rec(1, "hold", None), {"t": 2, "z": {"touchT": 0, "out": None}, "c": {"touchT": 0, "out": None}}, _rec(3, "hold", "break")]
    j = Z.judge(recs)
    assert j["zones"] == 3 and j["paired"] == 1 and j["zone_touched"] == 2


if __name__ == "__main__":
    test_planted_effect_passes_and_random_does_not(); test_gate_needs_n_and_both_halves(); test_unresolved_and_untouched_are_ignored(); print("ok zone_eval")
