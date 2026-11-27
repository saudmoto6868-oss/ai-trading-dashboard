"""modules/v7_live_cfx.js (batch 1: order blocks with MIT + volume %, sweeps, CISD (+HTF), trend line, liquidity pools, Fibonacci, divergences, candidate tracking)
against an INDEPENDENT Python implementation of the written definitions. Synthetic candles with volume. Needs node + numpy; fails (never skips) if Node is missing.
Checks the logic only, not that any setup makes money."""
import json, os, shutil, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_v7_extra as X
import test_v7_smc as M
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFX = os.path.join(ROOT, "modules", "v7_live_cfx.js")
STRUCT = os.path.join(ROOT, "modules", "v7_live_struct.js")


def _color(x):
    return -1 if x["close"] < x["open"] else 1 if x["close"] > x["open"] else 0


def _obs_all(b, ev):
    out = []
    for i, typ, d, frm in ev:
        j = M._ob_idx(b, d, frm, i)
        if j is None: continue
        mit = next((q for q in range(i + 1, len(b)) if (b[q]["close"] < b[j]["low"] if d == "up" else b[q]["close"] > b[j]["high"])), -1)
        s = sum(b[q]["volume"] for q in range(j, i + 1))
        out.append((d, j, b[j]["high"], b[j]["low"], mit, (100 * b[j]["volume"] / s) if s > 0 else None))
    return out[-6:]


def _sweeps(b, levels):
    out = []
    for kind, p, frm, side in levels:
        for i in range(max(0, frm), len(b)):
            if side == "high":
                if b[i]["high"] > p and b[i]["close"] < p: out.append((i, kind, p, side)); break
                if b[i]["close"] > p: break
            else:
                if b[i]["low"] < p and b[i]["close"] > p: out.append((i, kind, p, side)); break
                if b[i]["close"] < p: break
    return sorted(out, key=lambda z: z[0])[-8:]


def _cisd(b):
    out, n, i = [], len(b), 0
    while i < n:
        col = _color(b[i])
        if col == 0: i += 1; continue
        j = i
        while j + 1 < n and _color(b[j + 1]) == col: j += 1
        if j - i + 1 >= 2:
            lv = b[i]["open"]
            for k in range(j + 1, min(n - 1, j + 10) + 1):
                if (b[k]["close"] > lv) if col < 0 else (b[k]["close"] < lv): out.append(("up" if col < 0 else "down", i, k, lv)); break
        i = j + 1
    return out[-6:]


def _cisd_htf(b, sec):
    ag, key = [], None
    for i, x in enumerate(b):
        k = x["time"] // sec
        if k != key: key = k; ag.append(dict(time=k * sec, open=x["open"], high=x["high"], low=x["low"], close=x["close"], first=i))
        else: a = ag[-1]; a["high"] = max(a["high"], x["high"]); a["low"] = min(a["low"], x["low"]); a["close"] = x["close"]
    ag = ag[:-1]
    if len(ag) < 4: return []
    return [(d, ag[i0]["first"], ag[i1]["first"], lv) for d, i0, i1, lv in _cisd(ag)]


def _pools(b, H, Lo, atr):
    tol, out = 0.10 * atr, []
    for kind, arr in (("high", H), ("low", Lo)):
        s = sorted(arr, key=lambda z: z[1]); cur = []
        def flush():
            nonlocal cur
            if len(cur) >= 2:
                top, bot, last = max(c[1] for c in cur), min(c[1] for c in cur), max(c[0] for c in cur)
                swept = any((b[i]["high"] > top) if kind == "high" else (b[i]["low"] < bot) for i in range(last + 1, len(b)))
                if not swept: out.append((kind, sum(c[1] for c in cur) / len(cur), len(cur), last, min(c[0] for c in cur)))
            cur = []
        for z in s:
            if cur and z[1] - cur[-1][1] > tol: flush()
            cur.append(z)
        flush()
    return sorted(out, key=lambda z: z[3])[-8:]


def _fib(H, Lo):
    if not H or not Lo: return None
    h, l = H[-1], Lo[-1]; r = h[1] - l[1]
    if not r > 0: return None
    up = h[0] > l[0]
    return ("up" if up else "down", [(k, h[1] - k * r if up else l[1] + k * r) for k in (0.236, 0.382, 0.5, 0.618, 0.705, 0.786)], [(k, h[1] + (k - 1) * r if up else l[1] - (k - 1) * r) for k in (1.272, 1.618)])


def _rsi(c, n=14):
    import numpy as np
    o = np.full(len(c), np.nan); d = np.diff(c); g = np.where(d > 0, d, 0.0); ls = np.where(d < 0, -d, 0.0)
    ag, al = g[:n].mean(), ls[:n].mean(); o[n] = 100 if al == 0 else 100 - 100 / (1 + ag / al)
    for i in range(n + 1, len(c)):
        ag = (ag * (n - 1) + g[i - 1]) / n; al = (al * (n - 1) + ls[i - 1]) / n; o[i] = 100 if al == 0 else 100 - 100 / (1 + ag / al)
    return o


def _divs(H, Lo, ser, gap):
    import math
    out = []
    ok = lambda i: not (ser[i] is None or math.isnan(ser[i]))
    for k in range(1, len(H)):
        a, c = H[k - 1], H[k]
        if c[0] - a[0] <= gap and ok(a[0]) and ok(c[0]) and c[1] > a[1] and ser[c[0]] < ser[a[0]]: out.append(("bear", a[0], c[0]))
    for k in range(1, len(Lo)):
        a, c = Lo[k - 1], Lo[k]
        if c[0] - a[0] <= gap and ok(a[0]) and ok(c[0]) and c[1] < a[1] and ser[c[0]] > ser[a[0]]: out.append(("bull", a[0], c[0]))
    return sorted(out, key=lambda z: z[2])[-4:]


def _track(b, c, t0):
    long = c["dir"] == "up"; st, i_fill, i_end, cnt, oc = "pending", -1, -1, 0, 0
    for k, x in enumerate(b):
        if x["time"] <= t0: continue
        cnt += 1
        if st == "pending":
            if (x["low"] <= c["entry"]) if long else (x["high"] >= c["entry"]): st, i_fill, oc = "open", k, 0; continue
            if cnt > 48: st, i_end = "expired", k; break
            continue
        oc += 1
        if (x["low"] <= c["sl"]) if long else (x["high"] >= c["sl"]): st, i_end = "sl", k; break
        if (x["high"] >= c["tp1"]) if long else (x["low"] <= c["tp1"]): st, i_end = "tp1", k; break
        if oc > 96: st, i_end = "timeout", k; break
    return st, i_fill, i_end, (c["rr1"] if st == "tp1" else -1 if st == "sl" else None)


def test_js_matches_python():
    import numpy as np
    if not shutil.which("node"): raise RuntimeError("Node.js is required for the V7 CFX parity test")
    seen = dict(ob=0, mit=0, sw=0, cisd=0, htf=0, pool=0, div=0, trk={})
    for seed in range(5, 13):
        b = X._bars(n=1500, seed=seed); H, Lo = X._swings(b); ev = X._events(b, H, Lo); atr = M._atr(b)
        c_ = [x["close"] for x in b]; rsi = _rsi(np.array(c_))
        levels = [("EQH", p, i + 1, "high") for i, p in H[-10:]] + [("EQL", p, i + 1, "low") for i, p in Lo[-10:]]
        js = ("const C=require(@C@),S=require(@S@);const b=JSON.parse(require('fs').readFileSync(0,'utf8'));const c=S.compute(b),d=b._d;"
              "console.log(JSON.stringify({ob:C.obAll(b.bars,c.events),sw:C.sweeps(b.bars,b.levels),ci:C.cisd(b.bars),ch:C.cisdHtf(b.bars,14400),tu:C.trendLine(c.sw,'up'),td:C.trendLine(c.sw,'down'),pl:C.pools(b.bars,c.sw,c.atr),fb:C.fibLevels(c.sw),dv:C.divergences(c.sw,b.rsi,80)}))"
              ).replace("@C@", json.dumps(CFX)).replace("@S@", json.dumps(STRUCT)).replace("const c=S.compute(b),d=b._d;", "const c=S.compute(b.bars);")
        inp = dict(bars=b, levels=[dict(kind=k, p=p, **{"from": f}, side=s) for k, p, f, s in levels], rsi=[None if np.isnan(v) else float(v) for v in rsi])
        r = json.loads(subprocess.run(["node", "-e", js], input=json.dumps(inp), capture_output=True, text=True, check=True).stdout)
        ob = _obs_all(b, ev); got = [(o["dir"], o["i0"], o["hi"], o["lo"], o["mit"], o["volPct"]) for o in r["ob"]]
        assert len(got) == len(ob) and all(g[:5] == q[:5] and ((g[5] is None and q[5] is None) or abs(g[5] - q[5]) < 1e-9) for g, q in zip(got, ob)), ("ob", seed)
        seen["ob"] += len(ob); seen["mit"] += sum(1 for q in ob if q[4] >= 0)
        sw = _sweeps(b, levels); assert [(s["i"], s["kind"], s["p"], s["side"]) for s in r["sw"]] == sw, ("sweeps", seed); seen["sw"] += len(sw)
        ci = _cisd(b); assert [(e["dir"], e["i0"], e["i1"], e["level"]) for e in r["ci"]] == ci, ("cisd", seed); seen["cisd"] += len(ci)
        ch = _cisd_htf(b, 14400); assert [(e["dir"], e["i0"], e["i1"], e["level"]) for e in r["ch"]] == ch, ("cisd htf", seed); seen["htf"] += len(ch)
        for key, tr in (("tu", "up"), ("td", "down")):
            a = Lo if tr == "up" else H
            exp = None
            if len(a) >= 2 and ((a[-1][1] > a[-2][1]) if tr == "up" else (a[-1][1] < a[-2][1])): exp = (a[-2][0], a[-2][1], a[-1][0], a[-1][1])
            got_t = r[key]; assert (None if got_t is None else (got_t["i1"], got_t["p1"], got_t["i2"], got_t["p2"])) == exp, ("trend", key, seed)
        pl = _pools(b, H, Lo, atr); jp = r["pl"]   # the pool price is a mean: compare it with a tolerance (summation order), everything else exactly
        assert len(jp) == len(pl) and all((p["kind"], p["touches"], p["iLast"], p["i0"]) == (q[0], q[2], q[3], q[4]) and abs(p["p"] - q[1]) < 1e-9 for p, q in zip(jp, pl)), ("pools", seed); seen["pool"] += len(pl)
        fb = _fib(H, Lo); jf = r["fb"]
        assert (fb is None) == (jf is None)
        if fb: assert jf["dir"] == fb[0] and all(abs(x["p"] - q[1]) < 1e-9 and x["k"] == q[0] for x, q in zip(jf["retr"], fb[1])) and all(abs(x["p"] - q[1]) < 1e-9 for x, q in zip(jf["ext"], fb[2])), ("fib", seed)
        dv = _divs(H, Lo, [None if np.isnan(v) else float(v) for v in rsi], 80); assert [(d["dir"], d["i1"], d["i2"]) for d in r["dv"]] == dv, ("div", seed); seen["div"] += len(dv)
    # candidate tracking on many random candidates
    rng = np.random.default_rng(3); b = X._bars(n=600, seed=21); atr = M._atr(b)
    cases = []
    for _ in range(300):
        k = int(rng.integers(50, 450)); px = b[k]["close"]; long = bool(rng.integers(0, 2)); a = float(rng.uniform(0.5, 2.0)) * atr
        entry = px - (0.3 * a if long else -0.3 * a); sl = entry - a if long else entry + a; rr = float(rng.uniform(2, 4)); tp1 = entry + rr * a if long else entry - rr * a
        cases.append(dict(dir="up" if long else "down", entry=entry, sl=sl, tp1=tp1, rr1=rr, t0=b[k]["time"]))
    js2 = ("const C=require(@C@);const j=JSON.parse(require('fs').readFileSync(0,'utf8'));console.log(JSON.stringify(j.cases.map(c=>C.trackCandidate(j.bars,c,c.t0))))").replace("@C@", json.dumps(CFX))
    r2 = json.loads(subprocess.run(["node", "-e", js2], input=json.dumps(dict(bars=b, cases=cases)), capture_output=True, text=True, check=True).stdout)
    for c, g in zip(cases, r2):
        e = _track(b, c, c["t0"]); assert (g["status"], g["iFill"], g["iEnd"], g["R"]) == e, (c, g, e); seen["trk"][e[0]] = seen["trk"].get(e[0], 0) + 1
    assert seen["ob"] and seen["mit"] and seen["sw"] and seen["cisd"] and seen["htf"] and seen["pool"] and seen["div"], seen
    assert {"pending", "open", "tp1", "sl"} <= set(seen["trk"]) | {"pending", "open"} and "tp1" in seen["trk"] and "sl" in seen["trk"], seen
    print("coverage (non-empty comparisons):", seen)


if __name__ == "__main__":
    test_js_matches_python()
    print("ok V7 CFX batch 1: JS == independent Python (OB + MIT + volume %, sweeps, CISD, HTF CISD, trend line, liquidity pools, Fibonacci, divergences, candidate tracking)")
