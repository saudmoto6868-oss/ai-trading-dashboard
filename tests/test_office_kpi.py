"""Checks for modules/office_kpi.py (runs as a script or under pytest)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules import office_kpi as K  # noqa: E402


def _row(key, tf, n, avg, base=0.0, t=None, school="X", **kw):
    r = {"key": key, "school": school, "tf": tf, "side": "all", "n": n, "avgR": avg, "base_avgR": base, "edge": False}
    if t is not None:
        r["t"] = t
    r.update(kw)
    return r


def test_net_and_gate():
    assert K.net({"avgR": 0.357}) == 0.257
    assert not K.passes_gate(_row("a", "1d", 115, 0.357))                   # no t from the lab -> not evidence
    assert K.passes_gate(_row("a", "1d", 150, 0.3, t=3.5, is_avgR=0.2, oos_avgR=0.25))
    assert not K.passes_gate(_row("a", "1d", 150, 0.3, t=3.5, is_avgR=0.05, oos_avgR=0.25))   # in-sample under the cost
    assert not K.passes_gate(_row("a", "1d", 99, 0.9, t=9))                  # too few trades
    assert not K.passes_gate(_row("a", "1d", 500, 0.08, t=5))                # positive before costs, negative after


def test_summary_and_styles():
    d = {"meta": {"built": 0, "symbols": ["A", "B"]}, "rows": [
        _row("liqline", "all", 2000, 0.01), _row("liqline", "1d", 115, 0.357, base=0.151),
        _row("ob", "all", 1500, -0.07), _row("ob", "1h", 400, -0.05),
        _row("judas", "1m", 532, 0.118),
        {"key": "*CHAIN*", "school": "Chain", "tf": "all", "side": "grade A+++", "n": 514, "avgR": 0.114, "t": 2.48, "is_avgR": 0.047, "oos_avgR": 0.165},
    ]}
    s = K.summary(d)
    assert s["detectors"] == 3 and s["off"] == ["ob"] and s["passed"] == 0 and s["symbols"] == 2
    assert s["best"]["key"] == "liqline" and s["best"]["net"] == 0.257 and s["best"]["vs_random"] == 0.206
    st = {x["style"]: x for x in K.styles(d)}
    assert st["Scalp"]["key"] == "judas" and st["Swing"]["key"] == "liqline" and st["Day"]["key"] == "ob"
    assert K.summary({}) == {}


def test_journal_and_top_rows():
    j = K.journal_kpis([2, -1, -1, 3, -1, float("nan")])
    assert j["n"] == 5 and j["win"] == 0.4 and j["avgR"] == 0.4 and j["net"] == 0.3
    assert j["pf"] == 1.67 and j["maxdd"] == -2.0 and j["total"] == 2.0
    assert K.journal_kpis([]) == {"n": 0} and K.journal_kpis([1, 2])["pf"] is None
    d = {"rows": [_row("a", "1d", 150, 0.3, t=3.5), _row("b", "1h", 400, 0.05), _row("c", "1m", 50, 0.9), _row("a", "all", 900, 0.1)]}
    top = K.top_rows(d)
    assert [r["key"] for r in top] == ["a", "b"] and top[0]["gate"] and not top[1]["gate"]
    d["rows"].append(_row("b", "all", 600, -0.08))
    assert K.evidence(d, "a", "1d")["tf"] == "1d" and K.evidence(d, "a", "1w")["tf"] == "1d"
    assert K.evidence(d, "a", "4h")["tf"] == "all" and K.evidence(d, "zz", "1h") is None
    assert K.evidence(d, "b", "1h")["off"] and not K.evidence(d, "a", "1d")["off"]
    d["rows"].pop()
    assert K.lab_avg(d) == round((150 * 0.3 + 400 * 0.05 + 50 * 0.9) / 600, 3)


def test_real_lab_file_loads():
    s = K.summary(K.load())
    if s:   # the repo ships data/strategy_lab.json
        assert s["detectors"] > 10 and s["best"] is not None


if __name__ == "__main__":
    test_net_and_gate(); test_summary_and_styles(); test_journal_and_top_rows(); test_real_lab_file_loads()
    print("ok office_kpi", K.summary(K.load()).get("best"))
