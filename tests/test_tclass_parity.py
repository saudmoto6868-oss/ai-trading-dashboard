"""modules/tclass.py (server, Telegram) == the Workspace Trade Classes engine (JS TCLASS block + SR.compute) on the same candles.
Synthetic candles only: proves the port is exact, not that bounces make money. Run: python3 tests/test_tclass_parity.py"""
import json
import math
import os
import random
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from modules import tclass as P  # noqa: E402

html = open(os.path.join(ROOT, "modules", "workspace_app.html"), encoding="utf8").read()
blk = re.search(r"/\* TCLASS-BEGIN.*?\*/\n(.*?)/\* TCLASS-END \*/", html, re.S).group(1)
sr = re.search(r"\nconst SR = \{\n(.*?)\n\};\n", html, re.S)
assert sr, "SR block not found"
sr_js = "const SR = {\n" + sr.group(1) + "\n};\n"


def rows_from(close, seed):
    rnd, out, prev = random.Random(seed), [], close[0]
    for c in close:
        o = prev
        w = abs(c) * 0.002 * (0.5 + rnd.random())
        out.append({"o": o, "h": max(o, c) + w, "l": min(o, c) - w, "c": c})
        prev = c
    return out


cases = {}
cases["range"] = rows_from([105 + 5 * math.sin(2 * math.pi * i / 40 - math.pi / 2) + 0.15 * math.sin(i * 12.9898) for i in range(400)], 1)
for s in range(6):
    r = random.Random(100 + s); x = 100.0; cl = []
    for i in range(300):
        x *= math.exp(r.gauss(0.0003 * (s - 2), 0.01)); cl.append(x)
    cases[f"walk{s}"] = rows_from(cl, s)
cases["btc"] = rows_from([60000 + 800 * math.sin(i / 7) + 30 * i for i in range(300)], 9)
bias_rows = rows_from([100 + 0.2 * i + 2 * math.sin(i / 3.0) for i in range(200)], 3)

# random deliberation contexts (judge) + structure on every series
rj = random.Random(42); ctxs = []
for q in range(300):
    side = rj.choice([1, -1]); e = 100.0; st_ = e - side * rj.uniform(0.3, 3); t1 = e + side * rj.uniform(0.2, 8)
    if q % 4 == 0:   # strong cases too, so A+ gets exercised
        st_ = e - side * 1; t1 = e + side * rj.uniform(2.5, 4)
    idea = {"det": rj.choice(["bounce", "struct", "elliott", "vwap", "harmonic"]), "side": side, "entry": e, "stop": st_, "tps": [t1, t1 + side * rj.uniform(-1, 4)], "now": rj.random() < 0.7, "level": e - side * rj.uniform(0, 1)}
    lv = [{"p": e + rj.uniform(-8, 8), "src": rj.choice(["support", "resistance", "VP HVN"])} for _ in range(rj.randint(0, 5))]
    ctx = {"tf": {"bias": "1H", "setup": "15m", "entry": "5m"}, "ps": rj.choice([1, 0.1, 0.01]), "atr": rj.uniform(0.3, 2), "levels": lv,
           "bias": rj.choice([{"available": False}, {"available": True, "bias": "bull"}, {"available": True, "bias": "bear"}, {"available": True, "bias": "neutral"}]),
           "setupB": rj.choice([{"available": True, "bias": "bull"}, {"available": True, "bias": "bear"}, {"available": False}]),
           "trig": rj.choice(["", "rejection candle", "BOS 5m"]), "confl": rj.sample(["VP", "SMT", "Elliott", "Harmonic"], rj.randint(0, 4)), "vpAt": rj.choice(["", "POC", "HVN"]),
           "hist": rj.choice([{"n": 0}, {"n": rj.randint(1, 60), "hitPct": rj.random(), "p75": rj.uniform(0, 6)}]), "late": rj.choice([0, rj.uniform(0.4, 1)]),
           "regime": rj.choice([None, "trend", "chop", "hivol", "crash"]), "regime_bad": rj.random() < 0.3, "news": rj.choice(["", "", "USD CPI"]), "openSame": rj.random() < 0.1, "openOpp": rj.random() < 0.1,
           "classOpen": rj.randint(0, 3), "jr": rj.choice([None, {"done": rj.randint(0, 30), "avgR": rj.uniform(-1, 1)}]), "scalp": rj.random() < 0.5, "ses": rj.choice(["off-KZ", "London KZ", "Asia", ""])}
    ctxs.append([idea, ctx])

js = sr_js + blk + r"""
const C = JSON.parse(require('fs').readFileSync(0, 'utf8')), out = {};
out.__judge = C.ctxs.map(([i, c]) => TCE.judge(i, c));
for (const k of Object.keys(C.cases)){ const R = C.cases[k], lv = SR.compute(R);
  out[k] = {lv, st6:TCE.structure(R, 300), ev:TCE.events(R, {hold:16}), cand:TCE.candidates("BTC-USDT", R, lv, C.bias, R.slice(-60), {targetPts:0, hold:16}),
    cand100:TCE.candidates("Y:EURUSD=X", R, lv, C.bias, null, {targetPts:100, hold:20})}; }
process.stdout.write(JSON.stringify(out));
"""
r = subprocess.run(["node", "-e", js], input=json.dumps({"cases": cases, "bias": bias_rows, "ctxs": ctxs}), capture_output=True, text=True, timeout=120)
assert r.returncode == 0, r.stderr
J = json.loads(r.stdout)


def close(a, b, path):
    if isinstance(a, dict):
        for k in a:
            if k in ("lastBar",):
                continue
            if k in ("sideSt", "bias", "bias_"):   # JS-only extras
                continue
            assert k in b, f"{path}.{k} missing in python"
            close(a[k], b[k], f"{path}.{k}")
    elif isinstance(a, list):
        assert len(a) == len(b), f"{path}: len {len(a)} vs {len(b)}"
        for i, (x, y) in enumerate(zip(a, b)):
            close(x, y, f"{path}[{i}]")
    elif isinstance(a, float) or isinstance(b, float):
        assert a is not None and b is not None and abs(a - b) <= 1e-9 * max(1, abs(a)), f"{path}: {a} vs {b}"
    else:
        assert a == b, f"{path}: {a!r} vs {b!r}"


n_ev = n_c = 0
for k, R in cases.items():
    lv = P.sr_levels(R)
    close(J[k]["lv"], lv, f"{k}.levels")
    ev = P.events(R, hold=16)
    close(J[k]["ev"], ev, f"{k}.events")
    c1 = P.candidates("BTC-USDT", R, lv, bias_rows, R[-60:], target_pts=0, hold=16)
    close(J[k]["cand"], c1, f"{k}.cand")
    c2 = P.candidates("Y:EURUSD=X", R, lv, bias_rows, None, target_pts=100, hold=20)
    close(J[k]["cand100"], c2, f"{k}.cand100")
    n_ev += len(ev); n_c += len(c1) + len(c2)
    close(J[k]["st6"], P.structure(R, 300), f"{k}.structure")
assert n_ev > 20 and n_c >= 2, (n_ev, n_c)
vs = {}
for q, (idea, ctx) in enumerate(ctxs):
    pj = P.judge(idea, ctx)
    close(J["__judge"][q], pj, f"judge[{q}]")
    vs[pj["verdict"]] = vs.get(pj["verdict"], 0) + 1
    vs[pj["grade"]] = vs.get(pj["grade"], 0) + 1
assert all(k in vs for k in ('TAKE', 'WAIT', 'SKIP', 'A+', 'A', 'B', 'C')), vs
assert [P.point_size(s, p) for s, p in [("Y:EURUSD=X", 1.1), ("Y:USDJPY=X", 150), ("HL:xyz:GOLD", 2400), ("BTC-USDT", 6e4), ("HL:xyz:SP500", 5e3), ("DOGE-USDT", .15)]] == [0.0001, 0.01, 0.1, 1, 1, 0.00001]
import pandas as pd  # noqa: E402
rg = cases["range"]
fake = lambda sym, tf, limit=300: pd.DataFrame([{"open": r["o"], "high": r["h"], "low": r["l"], "close": r["c"], "volume": 1.0} for r in rg[-limit:]])
sc = P.scan("BTC-USDT", "Swing", fake)
assert sc and all(x["j"]["verdict"] in ("TAKE", "WAIT", "SKIP") for x in sc), sc[:1]
msg = P.fmt(sc[0])
assert "TRADE CLASSES" in msg and "نقطة" in msg and "ليه" in msg and len(msg) < 3900
print(f"ok tclass parity: {len(cases)} series, {n_ev} events, {n_c} candidates, {len(ctxs)} judgements {vs} identical in JS and Python")
