"""FRED macro regime (modules/fred_regime.py) on synthetic series. Plain script: python3 tests/test_fred_regime.py
Mock data only - FRED is not reachable from the build sandbox."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

from modules import fred_regime as FR

IDX = pd.bdate_range("2021-01-01", "2025-12-31")


def calm(seed, base, noise):
    r = np.random.default_rng(seed)
    return pd.Series(base + r.normal(0, noise, len(IDX)), index=IDX)


def frames(stress_from=None):
    f = {"BAMLH0A0HYM2": calm(1, 4.0, 0.1), "VIXCLS": calm(2, 16, 1.0), "T10Y2Y": calm(3, 0.5, 0.05)}
    wk = pd.date_range("2021-01-01", "2025-12-31", freq="W-FRI")
    r = np.random.default_rng(4)
    f["NFCI"] = pd.Series(-0.4 + r.normal(0, 0.03, len(wk)), index=wk)
    f["STLFSI4"] = pd.Series(-0.5 + r.normal(0, 0.05, len(wk)), index=wk)
    if stress_from is not None:
        for k, bump in (("BAMLH0A0HYM2", 2.0), ("VIXCLS", 15), ("NFCI", 0.5), ("STLFSI4", 1.5)):
            s = f[k].copy(); s[s.index >= stress_from] += bump; f[k] = s
        s = f["T10Y2Y"].copy(); s[s.index >= stress_from] -= 0.6; f["T10Y2Y"] = s
    return f


def test_parse_csv_with_missing_dots():
    s = FR.parse_csv("observation_date,VIXCLS\n2025-01-02,17.9\n2025-01-03,.\n2025-01-06,16.1\n")
    assert list(s.values) == [17.9, 16.1] and str(s.index[0].date()) == "2025-01-02"
    s = FR.parse_csv("DATE,T10Y2Y\n2025-01-02,0.3\n")   # older FRED header
    assert s.iloc[0] == 0.3
    print("ok test_parse_csv_with_missing_dots")


def test_calm_is_neutral_stress_is_risk_off():
    r = FR.regime_at(frames(), "2025-06-30")
    assert r["n"] == 5 and r["regime"] == "neutral", r["score"]
    r = FR.regime_at(frames(pd.Timestamp("2025-06-02")), "2025-06-30")
    assert r["regime"] == "risk-off" and r["score"] > 2, r["score"]
    print("ok test_calm_is_neutral_stress_is_risk_off", round(r["score"], 2))


def test_no_look_ahead():
    when = pd.Timestamp("2025-06-02")                       # the stress starts that very day
    a = FR.regime_at(frames(), when)
    b = FR.regime_at(frames(when), when)
    assert abs(a["score"] - b["score"]) < 1e-12, (a["score"], b["score"])   # values dated today are not public yet (lag >= 1 day)
    c = FR.regime_at(frames(when), when + pd.Timedelta(days=1))
    assert c["score"] > a["score"] + 0.5                     # one day later the daily series show it
    wk = {k: v for k, v in frames(when).items() if k in ("NFCI", "STLFSI4")}
    assert FR.regime_at(wk, when + pd.Timedelta(days=4))["score"] == FR.regime_at({k: v for k, v in frames().items() if k in ("NFCI", "STLFSI4")}, when + pd.Timedelta(days=4))["score"]
    print("ok test_no_look_ahead")


def test_history_walk_forward_matches_point_calls():
    f = frames(pd.Timestamp("2025-06-02"))
    h = FR.history(f, start="2025-05-01", end="2025-07-31")
    assert len(h) and set(h.regime) >= {"neutral", "risk-off"}
    row = h.iloc[len(h) // 2]
    assert abs(row.score - FR.regime_at(f, row.date)["score"]) < 1e-12
    print("ok test_history_walk_forward_matches_point_calls", dict(h.regime.value_counts()))


def test_missing_series_and_fetch_errors():
    f = frames(); f.pop("VIXCLS")
    assert FR.regime_at(f, "2025-06-30")["n"] == 4
    assert FR.regime_at({}, "2025-06-30")["regime"] is None

    class R:
        status_code = 200
        text = "observation_date,X\n2025-01-02,1\n"
        def raise_for_status(self): pass

    def get(url, params=None, timeout=None):
        if params["id"] == "VIXCLS":
            raise ConnectionError("blocked")
        return R()
    FR._cache.clear()
    out, errs = FR.load_all(get=get)
    assert "VIXCLS" not in out and len(out) == 4 and errs == ["VIXCLS: ConnectionError"]
    FR._cache.clear()
    print("ok test_missing_series_and_fetch_errors")


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
