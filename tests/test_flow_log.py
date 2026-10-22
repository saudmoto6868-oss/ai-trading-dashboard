"""Checks for modules/flow_log.py: features, forward labelling, and the judge (random data = no edge, planted edge = found)."""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules import flow_log as F  # noqa: E402


def test_features():
    prev = {"bids": [["100", "5"]] + [["99", "1"]] * 4, "asks": [["101", "5"]] + [["102", "1"]] * 4}
    book = {"bids": [["100", "8"]] + [["99", "1"]] * 4, "asks": [["101", "2"]] + [["102", "1"]] * 4}
    tr = [{"px": "100", "sz": "3", "side": "buy"}, {"px": "100", "sz": "1", "side": "sell"}]
    f = F.features(book, prev, tr, 2.0)
    assert f["mid"] == 100.5 and f["spread_bps"] == round(1 / 100.5 * 1e4, 3)
    assert f["imb"] > 0 and f["ofi"] > 0                      # more bid size, less ask size: pressure up
    assert f["cvd"] == 0.5 and f["speed"] == 1.0              # (300-100)/(300+100), 2 trades / 2 s
    assert F.features({"bids": [], "asks": [["1", "1"]]}, None, [], 1) is None
    assert F.features({"bids": [["2", "1"]], "asks": [["1", "1"]]}, None, [], 1) is None   # crossed


def _rows(n=4000, edge=0.0, seed=1):
    """A random-walk mid every second; imb is constant inside 60 s blocks (a persistent book pressure); with edge > 0 the mid drifts
    by edge * imb bps per second inside the same block, so a signal at second t sees the push continue."""
    rng = random.Random(seed)
    blocks = [rng.uniform(-1, 1) for _ in range(n // 60 + 1)]
    mid, rows = 100.0, []
    for i in range(n):
        imb = blocks[i // 60]
        mid *= 1 + (rng.gauss(0, 0.2) + edge * imb) / 1e4
        rows.append({"t": float(i), "sym": "X", "mid": mid, "imb": imb, "ofi": 0.0, "cvd": 0.0, "speed": 1.0})
    return rows


def test_label_and_horizons():
    rows = F.label(_rows(200), horizons=(5, 30))
    assert rows[0]["ret_5"] is not None and rows[-1]["ret_5"] is None and rows[-3]["ret_30"] is None
    assert abs(rows[0]["ret_5"] - (rows[5]["mid"] / rows[0]["mid"] - 1) * 1e4) < 0.01


def test_judge_random_has_no_edge_and_planted_edge_is_found():
    j = F.judge(_rows(20000, 0.0, seed=2), cost_bps=1.0)
    assert not [r for r in j["results"] if r["rule"].startswith("imb") and r["horizon"] == 30 and r["pass"]]
    k = F.judge(_rows(20000, 0.3, seed=3), cost_bps=1.0)
    hit = [r for r in k["results"] if r["rule"] == "imb_with" and r["horizon"] == 30][0]
    assert hit["n"] >= 100 and hit["net_bps"] > 0 and hit["t"] > 3 and hit["pass"], hit
    assert k["trials"] == len(F.RULES) * len(F.HORIZONS)
    inv = [r for r in k["results"] if r["rule"] == "imb_against" and r["horizon"] == 30][0]
    assert inv["net_bps"] < 0 and not inv["pass"]                       # the opposite rule loses on the same data


def test_costs_kill_a_small_edge():
    rows = _rows(20000, 0.3, seed=4)
    cheap = F.judge(rows, cost_bps=0.0); dear = F.judge([dict(r) for r in rows], cost_bps=50.0)
    a = [r for r in cheap["results"] if r["rule"] == "imb_with" and r["horizon"] == 30][0]
    b = [r for r in dear["results"] if r["rule"] == "imb_with" and r["horizon"] == 30][0]
    assert a["net_bps"] > b["net_bps"] and not b["pass"]


if __name__ == "__main__":
    test_features(); test_label_and_horizons(); test_judge_random_has_no_edge_and_planted_edge_is_found(); test_costs_kill_a_small_edge(); print("ok flow_log")
