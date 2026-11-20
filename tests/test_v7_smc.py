"""modules/v7_live_smc.js (S/R zones, breaker blocks, inverse FVG, research trade candidate) against an INDEPENDENT Python implementation of the written definitions.
Synthetic candles. Needs node + numpy. Fails (never skips) if Node is missing. Checks the logic, not that any setup makes money."""
import json, os, shutil, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_v7_extra as X
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SMC = os.path.join(ROOT, "modules", "v7_live_smc.js")
EXTRA = os.path.join(ROOT, "modules", "v7_live_extra.js")
STRUCT = os.path.join(ROOT, "modules", "v7_live_struct.js")


def _atr(b):
    s = 0.0
    for i in range(len(b) - 14, len(b)): s += max(b[i]["high"] - b[i]["low"], abs(b[i]["high"] - b[i - 1]["close"]), abs(b[i]["low"] - b[i - 1]["close"]))
    return s / 14


def _sr(b, H, Lo, atr, count=6):
    pts = sorted([p for _, p in H] + [p for _, p in Lo]); zones, cur = [], []
    for p in pts:
        if cur and p - cur[-1] > 0.30 * atr: zones.append(cur); cur = []
        cur.append(p)
    if cur: zones.append(cur)
    last = b[-1]["close"]; out = []
    for z in zones:
        if len(z) < 2: continue
        c = sum(z) / len(z); out.append((z[0], z[-1], c, len(z), "support" if c < last else "resistance"))
    return sorted(out, key=lambda q: abs(q[2] - last))[:count]


def _ob_idx(b, d, frm, i):
    k, ext = frm, (float("inf") if d == "up" else float("-inf"))
    for q in range(frm, i + 1):
        if (b[q]["low"] < ext) if d == "up" else (b[q]["high"] > ext): ext = b[q]["low"] if d == "up" else b[q]["high"]; k = q
    return next((q for q in range(k, max(0, k - 5) - 1, -1) if (b[q]["close"] < b[q]["open"] if d == "up" else b[q]["close"] > b[q]["open"])), None)


def _breakers(b, ev):
    out = []
    for i, typ, d, frm in ev:
        j = _ob_idx(b, d, frm, i)
        if j is None: continue
        m = next((q for q in range(i + 1, len(b)) if (b[q]["close"] < b[j]["low"] if d == "up" else b[q]["close"] > b[j]["high"])), None)
        if m is None: continue
        nd = "down" if d == "up" else "up"
        dead = any((b[q]["close"] > b[j]["high"]) if nd == "down" else (b[q]["close"] < b[j]["low"]) for q in range(m + 1, len(b)))
        if not dead: out.append((nd, j, m, b[j]["high"], b[j]["low"]))
    return out[-3:]


def _ifvg(b, atr):
    out, n = [], len(b)
    for i in range(max(2, n - 80), n):
        g = None
        if b[i]["low"] - b[i - 2]["high"] >= 0.30 * atr: g = ("bull", b[i - 2]["high"], b[i]["low"])
        elif b[i - 2]["low"] - b[i]["high"] >= 0.30 * atr: g = ("bear", b[i]["high"], b[i - 2]["low"])
        if not g: continue
        m = next((j for j in range(i + 1, n) if (b[j]["close"] < g[1] if g[0] == "bull" else b[j]["close"] > g[2])), None)
        if m is None: continue
        nd = "bear" if g[0] == "bull" else "bull"
        dead = any((b[j]["close"] > g[2]) if nd == "bear" else (b[j]["close"] < g[1]) for j in range(m + 1, n))
        if not dead: out.append((nd, i - 2, m, g[1], g[2]))
    return out[-4:]


def _fvgs(b, atr):
    out, n = [], len(b)
    for i in range(2, n):
        if n - 1 - i > 30: continue
        z = None
        if b[i]["low"] - b[i - 2]["high"] >= 0.30 * atr: z = ("bull", i - 2, b[i - 2]["high"], b[i]["low"])
        elif b[i - 2]["low"] - b[i]["high"] >= 0.30 * atr: z = ("bear", i - 2, b[i]["high"], b[i - 2]["low"])
        if not z: continue
        if not any((b[j]["low"] <= z[2]) if z[0] == "bull" else (b[j]["high"] >= z[3]) for j in range(i + 1, n)): out.append(z)
    return out


def _cand(b, atr, ev, ob, fv, levels):
    if not ev: return None, "no_structure"
    i, typ, d, frm = ev[-1]; long = d == "up"; px = b[-1]["close"]
    zs = [o for o in ob if o[0] == d and ((o[2] <= px) if long else (o[3] >= px))]   # ob tuples (dir,i0,hi,lo)
    edge = (lambda o: o[2]) if long else (lambda o: o[3])
    zone = min(zs, key=lambda o: abs(edge(o) - px)) if zs else None
    if zone is None:
        fs = [z for z in fv if z[0] == ("bull" if long else "bear") and ((z[3] <= px) if long else (z[2] >= px))]
        fe = (lambda z: z[3]) if long else (lambda z: z[2])
        zone = min(fs, key=lambda z: abs(fe(z) - px)) if fs else None
        if zone is None: return None, "no_zone"
        lo, hi = zone[2], zone[3]
    else:
        hi, lo = zone[2], zone[3]
    entry = hi if long else lo; sl = lo - 0.15 * atr if long else hi + 0.15 * atr; risk = abs(entry - sl)
    tg = sorted([p for p in levels if (p > entry if long else p < entry)], reverse=not long)
    ok = [p for p in tg if abs(p - entry) / risk >= 2]
    if not ok: return None, "rr_below_2"
    return (d, entry, sl, ok[0], ok[1] if len(ok) > 1 else None), "ok"


def test_js_matches_python():
    if not shutil.which("node"): raise RuntimeError("Node.js is required for the V7 SMC parity test")
    import numpy  # noqa: F401
    n_cand = 0
    for seed in range(5, 17):
        b = X._bars(n=600, seed=seed); H, Lo = X._swings(b); ev = X._events(b, H, Lo); atr = _atr(b)
        js = ("const S=require(@S@),E=require(@E@),M=require(@M@);const b=JSON.parse(require('fs').readFileSync(0,'utf8'));const c=S.compute(b),ob=E.orderBlocks(b,c.events);"
              "const lv=c.sw.H.slice(-12).map(s=>s.p).concat(c.sw.L.slice(-12).map(s=>s.p));"
              "console.log(JSON.stringify({sr:M.srZones(b,c.sw,c.atr,6),br:M.breakers(b,c.events),ifv:M.inverseFvg(b,c.atr),ob:ob,fvg:c.fvg,lv:lv,cand:M.tradeCandidate(b,c.atr,c.events,ob,c.fvg,lv)}))"
              ).replace("@S@", json.dumps(STRUCT)).replace("@E@", json.dumps(EXTRA)).replace("@M@", json.dumps(SMC))
        r = json.loads(subprocess.run(["node", "-e", js], input=json.dumps(b), capture_output=True, text=True, check=True).stdout)
        sr = _sr(b, H, Lo, atr); assert [(z["lo"], z["hi"], z["touches"], z["kind"]) for z in r["sr"]] == [(q[0], q[1], q[3], q[4]) for q in sr], ("sr", seed)
        assert [(z["dir"], z["i0"], z["im"], z["hi"], z["lo"]) for z in r["br"]] == _breakers(b, ev), ("breakers", seed)
        assert [(z["dir"], z["i0"], z["im"], z["lo"], z["hi"]) for z in r["ifv"]] == _ifvg(b, atr), ("ifvg", seed)
        ob = [(o["dir"], o["i0"], o["hi"], o["lo"]) for o in r["ob"]]; fv = _fvgs(b, atr)
        cand, why = _cand(b, atr, ev, ob, fv, r["lv"]); jc = r["cand"]
        assert jc["reason"] == why, (seed, jc["reason"], why)
        if cand:
            n_cand += 1; c = jc["cand"]
            assert (c["dir"], c["entry"], c["sl"], c["tp1"], c["tp2"]) == cand and c["rr1"] >= 2 - 1e-9, (seed, c, cand)
    print("candidates found on", n_cand, "of 12 series")


if __name__ == "__main__":
    test_js_matches_python()
    print("ok V7 SMC: JS == independent Python on 12 synthetic series (S/R zones, breakers, inverse FVG, research trade candidate incl. R:R >= 2 gate)")
