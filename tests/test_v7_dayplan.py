"""V7 Day plan (rule-based Director) in modules/v7_live_ind.js: deterministic logic on synthetic candles. Plain script; needs node. It tests the RULES behave as written, NOT that the plan makes money."""
import datetime, json, os, shutil, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IND = os.path.join(ROOT, "modules", "v7_live_ind.js")


def _frame(n, slope, start=100.0, step=3600):
    out, c = [], start
    for i in range(n):
        o = c; c = c + slope; h = max(o, c) + 0.3; l = min(o, c) - 0.3
        out.append({"time": 1_700_000_000 + i * step, "open": o, "high": h, "low": l, "close": c, "closed": True})
    return out


def _run(expr):
    js = "const I=require(%s);%s" % (json.dumps(IND), expr)
    return json.loads(subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True).stdout)


def test_day_plan_rules():
    if not shutil.which("node"):
        print("skip: node not installed"); return
    frames = {k: _frame(120, 1.0) for k in ("d1", "h4", "h1", "m15")}
    now = 1_794_126_600_000   # 2026-11-12 08:30 UTC = 03:30 New York (EST): London kill zone
    up = _run("const f=%s;console.log(JSON.stringify(I.dayPlan(f,%d)))" % (json.dumps(frames), now))
    assert up["trends"]["d1"] == "UP" and up["dir"] == "UP", up
    assert up["state"] in ("WAIT", "WATCH LONG") and up["risk"] == {"basePct": 0.25, "minRR": 2}
    assert "entry" not in json.dumps(up).lower() and "stop" not in up and "target" not in json.dumps(up).lower(), "the plan must not print entries / stops / targets"
    conf = dict(frames); conf["h4"] = _frame(120, -1.0, start=400)
    c = _run("const f=%s;console.log(JSON.stringify(I.dayPlan(f,%d)))" % (json.dumps(conf), now))
    assert c["state"] == "CONFLICT" and c["conflict"], c
    nodata = _run("console.log(JSON.stringify(I.dayPlan({d1:[],h4:[],h1:[],m15:[]},%d)))" % now)
    assert nodata["state"] == "NO DATA"
    print("ok day plan rules")


def test_sessions_new_york_clock():
    if not shutil.which("node"):
        print("skip: node not installed"); return
    cases = {"2026-11-12T08:30:00+00:00": ("London kill zone", True, False),   # 03:30 NY
             "2026-11-12T13:00:00+00:00": ("NY AM kill zone", True, True),      # 08:00 NY (EST)
             "2026-11-12T22:30:00+00:00": ("", False, False)}                   # 17:30 NY: no session
    for iso, (kz, ldn, ny) in cases.items():
        ms = int(datetime.datetime.fromisoformat(iso).timestamp() * 1000)
        s = _run("console.log(JSON.stringify(I.sessionNow(%d)))" % ms)
        assert s["kz"] == kz and s["london"] == ldn and s["ny"] == ny, (iso, s)
    summer = _run("console.log(JSON.stringify(I.sessionNow(%d)))" % int(datetime.datetime(2026, 7, 15, 7, 30, tzinfo=datetime.timezone.utc).timestamp() * 1000))
    assert summer["kz"] == "London kill zone", summer   # 03:30 NY (EDT): the same NY clock in summer
    print("ok sessions on the New York clock")


if __name__ == "__main__":
    test_day_plan_rules(); test_sessions_new_york_clock()
    print("V7 DAY PLAN TESTS DONE")
