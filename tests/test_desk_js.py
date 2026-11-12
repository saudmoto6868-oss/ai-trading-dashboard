"""Order Flow Desk widget engine (DESK-BEGIN..END in modules/ws/24c_desk.js) run with node on synthetic candles,
and checked against the Python risk manager (modules/desk_risk.py). Plain script: python3 tests/test_desk_js.py
Skipped when node is not installed. Mock data only."""
import json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from modules.desk_risk import DeskDay, DeskRules, position_size, reward_risk  # noqa: E402

SRC = open(os.path.join(ROOT, "modules", "ws", "24c_desk.js"), encoding="utf-8").read()
ENGINE = re.search(r"/\* DESK-BEGIN.*?\*/(.*?)/\* DESK-END \*/", SRC, re.S).group(1)
H = 3600000
DAY = 86400000


def node(js):
    r = subprocess.run([shutil.which("node"), "-e", ENGINE + "\n" + js], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def candles():
    # 3 UTC days of 1H candles starting Monday 2026-11-02 00:00 UTC; day 2 trades 100..110, day 3 (today) opens at 105
    t0 = 1793577600000   # 2026-11-02 00:00 UTC (a Monday)
    rows = []
    for i in range(72):
        d = i // 24
        base = {0: 90, 1: 100, 2: 104}[d]
        h, l = base + 6 + (i % 5), base - (i % 4)
        if d == 1:
            h, l = min(h, 110), max(l, 100)
        rows.append({"t": t0 + i * H, "o": base + 1, "h": h, "l": l, "c": base + 2, "v": 10 + (i % 7)})
    rows[48]["o"] = 105
    return rows


def test_levels_previous_day_and_open():
    out = node("const r = %s; const L = DESK.levels(r); const d = DESK.period(r, 86400000, 0);"
               "console.log(JSON.stringify({d, ks: L.list.map(x => x.k), px: L.px, above: L.above.map(x => x.k), below: L.below.map(x => x.k)}));" % json.dumps(candles()))
    assert out["d"]["hi"] == 110 and out["d"]["lo"] == 100 and out["d"]["open"] == 105, out["d"]
    for k in ("PDH", "PDL", "DO", "POC", "VAH", "VAL"):
        assert k in out["ks"], (k, out["ks"])
    assert "PWH" not in out["ks"]                      # no complete previous week in 3 days
    assert all(k in out["above"] + out["below"] + ["DO"] for k in out["ks"]) and out["px"] == 106
    print("ok test_levels_previous_day_and_open")


def test_volume_profile_value_area():
    rows = [{"t": i * H, "o": 100, "h": 101, "l": 99, "c": 100, "v": 100} for i in range(30)] + \
           [{"t": (30 + i) * H, "o": 120, "h": 121, "l": 119, "c": 120, "v": 1} for i in range(5)]
    v = node("console.log(JSON.stringify(DESK.vp(%s)))" % json.dumps(rows))
    assert 99 <= v["poc"] <= 101 and v["val"] <= 99.6 and v["vah"] <= 102, v
    print("ok test_volume_profile_value_area", {k: round(x, 2) for k, x in v.items()})


def test_size_and_rr_match_python():
    cases = [(10000, 100, 99, None, 0, False, 1, 0), (50000, 5000, 4990, None, 0, False, 50, 1),
             (250000, 5000, 4990, "A+", 30, True, 50, 1), (8000, 2000, 2030, None, 0, False, 1, 0.001)]
    js = node("console.log(JSON.stringify(%s.map(c => DESK.size(c[0],c[1],c[2],DESK.riskFor(c[3],c[4],c[5]),c[6],c[7]))))" % json.dumps(cases))
    for c, j in zip(cases, js):
        p = position_size(c[0], c[1], c[2], point_value=c[6], qty_step=c[7], grade=c[3], validation_n=c[4], validation_passed=c[5])
        assert abs(p["qty"] - j["qty"]) < 1e-9 and abs(p["actual_risk_pct"] - j["pct"]) < 1e-9, (c, p, j)
    rr = node("console.log(JSON.stringify([DESK.rr(100,99,102), DESK.rr(100,101,97), DESK.rr(100,99,98)]))")
    assert rr == [reward_risk(100, 99, 102), reward_risk(100, 101, 97), reward_risk(100, 99, 98)]
    print("ok test_size_and_rr_match_python")


def test_day_and_check_match_python():
    now = 1793750400000 + 12 * H   # 2026-11-04 12:00 UTC
    jr = [{"status": "sl", "r": -1, "t1": now - H}, {"status": "sl", "r": -1, "t1": now - 2 * H}, {"status": "tp", "r": 2, "t1": now - 3 * H},
          {"status": "sl", "r": -1, "t1": now - 2 * DAY}, {"status": "open", "r": 0, "t0": now - H}]
    out = node("const d = DESK.day(%s, %d); const a = DESK.check({entry:100, stop:99, target:103, riskPct:0.25}, d);"
               "const b = DESK.check({entry:100, stop:99, target:101.5, riskPct:0.8}, {n:0, stops:3, R:-3, lossPct:1.5}, null, true);"
               "console.log(JSON.stringify({d, a, b: b.why.map(w => w[0])}))" % (json.dumps(jr), now))
    assert out["d"] == {"n": 3, "stops": 2, "R": 0, "lossPct": 0}, out["d"]
    mixed = node("const d = DESK.day([{status:'sl',r:-1,riskPct:0.5,t1:1793750400000+11*3600000},{status:'tp',r:1,riskPct:0.25,t1:1793750400000+10*3600000}], 1793750400000+12*3600000); console.log(JSON.stringify(d));")
    assert mixed["lossPct"] == 0.25, mixed
    legacy = node("console.log(JSON.stringify(DESK.day([{status:'sl',r:-1,t1:1793750400000+11*3600000}], 1793750400000+12*3600000).lossPct))")
    assert legacy == 0.25, legacy
    assert out["a"]["ok"] and out["a"]["rr"] == 3
    assert set(out["b"]) == {"stops", "left", "rr", "cap", "dup"}, out["b"]
    qualified = node("console.log(JSON.stringify(DESK.check({entry:100,stop:99,target:103,riskPct:0.5,riskCapPct:0.5},{n:0,stops:0,R:0,lossPct:0},null,false)))")
    assert qualified["ok"], qualified
    rejected = node("console.log(JSON.stringify(DESK.check({entry:100,stop:99,target:103,riskPct:0.5},{n:0,stops:0,R:0,lossPct:0},null,false)))")
    assert not rejected["ok"] and any(w[0] == "cap" for w in rejected["why"]), rejected
    # the same day in the Python manager (equity 10 000, base 0.25% = 25 per R): 2 stops, net 0 -> still allowed
    d = DeskDay(10000)
    for r in (-1, -1, 2):
        d.record(r * 25)
    ok, why = d.check("BTC", "long", 100, 99, 103, 25)
    assert ok and d.stops == 2, why
    print("ok test_day_and_check_match_python")


def test_risk_policy_has_no_manual_input_and_matches_python():
    out = node("console.log(JSON.stringify([DESK.riskFor('A+',29,true), DESK.riskFor('A+',30,true), DESK.riskFor('A+',30.0,true), DESK.riskFor('A+',50,false), DESK.riskFor('A',50,true), DESK.riskFor('A+','30',true), DESK.riskFor('A+',30.9,true), DESK.riskFor('A+',true,true)]))")
    assert out == [0.25, 0.5, 0.5, 0.25, 0.25, 0.25, 0.25, 0.25], out
    assert "rkI" not in SRC and 'lab(Lg(\"risk %\"' not in SRC
    print("ok test_risk_policy_has_no_manual_input_and_matches_python")


def test_widget_is_registered():
    assert "Panel.prototype.build_ofdesk = function()" in SRC
    snap = open(os.path.join(ROOT, "modules", "ws", "26_snap.js"), encoding="utf-8").read()
    assert '"ofdesk","ofm","dom"' in snap and 'ofdesk:"OFD"' in snap and 'ofm:"MAP"' in snap   # the Bookmap-style map is in the menu too
    i18n = open(os.path.join(ROOT, "modules", "ws", "11_i18n_helpers_themes.js"), encoding="utf-8").read()
    assert i18n.count("ofdesk:") == 2                  # English + Arabic menu label
    print("ok test_widget_is_registered")


if __name__ == "__main__":
    if not shutil.which("node"):
        print("skip: node not installed")
        sys.exit(0)
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
