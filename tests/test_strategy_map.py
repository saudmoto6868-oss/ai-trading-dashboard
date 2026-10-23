"""Checks for modules/strategy_map.py: registry is consistent, rule blueprints are valid and fire on candles, redundancy warnings work."""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules import office_kpi as K, strategy_map as M, strategy_rules as SR  # noqa: E402


def test_registry_is_consistent():
    lab = K.load()
    keys = set(K.detector_keys(lab)) if lab else set()
    for cid, (_n, kind, cl, roles, src) in M.COMPONENTS.items():
        assert cl in M.CLUSTERS, cid
        assert set(roles) <= set(M.ROLES), cid
        if src[0] == "rule":
            assert src[1] in SR.INDICATORS, cid
        if src[0] == "lab" and keys and not src[1].startswith("chain:"):
            assert src[1] in keys, (cid, src)   # every lab detector named here really is in the weekly lab
    for b in M.BLUEPRINTS:
        for role, cid, _note in b["parts"]:
            assert role in M.ROLES and cid in M.COMPONENTS, (b["id"], role, cid)
        assert b["evidence"] in M.EVIDENCE and b["style"] in dict(K.STYLES)
        for k in b.get("lab", []):
            assert not keys or k in keys, (b["id"], k)


def test_rule_blueprints_validate_and_run():
    rng = np.random.default_rng(5)
    c = 100 + np.cumsum(rng.normal(0, 1, 600)); df = pd.DataFrame({"open": c, "high": c + 1, "low": c - 1, "close": c, "volume": rng.uniform(1, 9, 600)})
    for b in M.BLUEPRINTS:
        if b["rules"]:
            assert SR.validate(b["rules"]) == [], (b["id"], SR.validate(b["rules"]))
            assert len(SR.evaluate(b["rules"], df)) == 600
        else:
            assert b.get("needs"), b["id"]


def test_redundancy_check():
    assert M.check(M.BP["macd_ema200"]["parts"]) and "تكرار" in M.check(M.BP["macd_ema200"]["parts"])[0]   # ema + macd_hist: same cluster
    assert not [w for w in M.check(M.BP["connors_rsi2"]["parts"]) if "تكرار" in w]
    assert M.check([("context", "ema", "")])   # no trigger / setup


def test_lab_helpers():
    lab = K.load()
    if not lab:
        return
    assert M.cluster_best(lab, "trend_ma") is None or M.cluster_best(lab, "trend_ma")["best"]["n"] >= K.GATE_N
    assert M.agreement(lab, "vwap", "ma_cross") == M.agreement(lab, "ma_cross", "vwap")
    assert M.stacking(lab) and all(len(x) == 3 for x in M.stacking(lab))


if __name__ == "__main__":
    test_registry_is_consistent(); test_rule_blueprints_validate_and_run(); test_redundancy_check(); test_lab_helpers(); print("ok strategy_map")
