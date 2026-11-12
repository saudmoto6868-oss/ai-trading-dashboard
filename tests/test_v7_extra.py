"""modules/v7_live_extra.js against an INDEPENDENT Python implementation (session VWAP, volume profile / value area, NY day+week opens, previous week H/L, kill zones,
HH/HL/LH/LL labels, order blocks, signal filters). Synthetic candles with volume across ~15 NY days. Needs node + numpy + tzdata (fails, never skips, if Node is missing)."""
import json, os, shutil, subprocess
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = os.path.join(ROOT, "modules", "v7_live_extra.js")
STRUCT = os.path.join(ROOT, "modules", "v7_live_struct.js")
NY = ZoneInfo("America/New_York")


def _bars(n=1500, seed=5):
    import numpy as np
    r = np.random.default_rng(seed); c = 100 + np.cumsum(r.normal(0, 0.6, n)); o = np.r_[c[0], c[:-1]]
    h = np.maximum(o, c) + np.abs(r.normal(0, 0.3, n)); l = np.minimum(o, c) - np.abs(r.normal(0, 0.3, n))
    v = np.abs(r.normal(100, 40, n)); v[::37] = 0.0
    t = 1_700_000_000 + 900 * np.arange(n)
    return [dict(time=int(a), open=float(b), high=float(d), low=float(e), close=float(f), volume=float(g)) for a, b, d, e, f, g in zip(t, o, h, l, c, v)]


def _ny(sec): return datetime.fromtimestamp(sec, timezone.utc).astimezone(NY)
def _day(sec):
    d = _ny(sec); return (d + timedelta(days=1) if d.hour >= 18 else d).date()
def _week(sec):
    d = _day(sec); return d - timedelta(days=d.weekday())


def _vwap(b):
    out, key, pv, v = [], None, 0.0, 0.0
    for x in b:
        k = _day(x["time"])
        if k != key: key, pv, v = k, 0.0, 0.0
        pv += (x["high"] + x["low"] + x["close"]) / 3 * x["volume"]; v += x["volume"]
        out.append(pv / v if v > 0 else None)
    return out


def _profile(b, look=200, bins=40):
    a = b[-look:]; lo = min(x["low"] for x in a); hi = max(x["high"] for x in a); step = (hi - lo) / bins
    idx = lambda p: min(bins - 1, max(0, int((p - lo) // step)))
    vol = [0.0] * bins; tot = 0.0
    for x in a:
        if not x["volume"]: continue
        i0, i1 = idx(x["low"]), idx(x["high"]); n = i1 - i0 + 1
        for i in range(i0, i1 + 1): vol[i] += x["volume"] / n
        tot += x["volume"]
    poc = max(range(bins), key=lambda i: (vol[i], -i)); l = h = poc; acc = vol[poc]
    while acc < 0.7 * tot and (l > 0 or h < bins - 1):
        up = vol[h + 1] if h < bins - 1 else -1; dn = vol[l - 1] if l > 0 else -1
        if up >= dn: h += 1; acc += vol[h]
        else: l -= 1; acc += vol[l]
    return dict(poc=lo + (poc + .5) * step, vah=lo + (h + 1) * step, val=lo + l * step)


def _opens(b):
    dk, wk = _day(b[-1]["time"]), _week(b[-1]["time"])
    d = next((i for i, x in enumerate(b) if _day(x["time"]) == dk), None); w = next((i for i, x in enumerate(b) if _week(x["time"]) == wk), None)
    pk, ph, pl = None, float("-inf"), float("inf")
    for x in reversed(b):
        k = _week(x["time"])
        if k == wk: continue
        if pk is None: pk = k
        if k != pk: break
        ph, pl = max(ph, x["high"]), min(pl, x["low"])
    return d, w, (ph, pl, pk)


def _kz(b):
    out = []
    for name, a, z in (("Asia KZ", 20, 24), ("London KZ", 2, 5), ("NY AM KZ", 7, 10)):
        run = None
        for i, x in enumerate(b):
            inside = a <= _ny(x["time"]).hour < z
            if inside:
                if run is None: run = [name, i, i]
                else: run[2] = i
            elif run: out.append(tuple(run)); run = None
        if run: out.append(tuple(run))
    return sorted(out, key=lambda r: r[1])[-9:]


def _swings(b, L=3):
    H, Lo = [], []
    for i in range(L, len(b) - L):
        if all(b[i]["high"] > b[i - j]["high"] and b[i]["high"] >= b[i + j]["high"] for j in range(1, L + 1)): H.append((i, b[i]["high"]))
        if all(b[i]["low"] < b[i - j]["low"] and b[i]["low"] <= b[i + j]["low"] for j in range(1, L + 1)): Lo.append((i, b[i]["low"]))
    return H, Lo


def _events(b, H, Lo, L=3):
    ev, trend, sh, sl = [], None, None, None
    for i in range(len(b)):
        for k, p in H:
            if k + L == i: sh = (k, p)
        for k, p in Lo:
            if k + L == i: sl = (k, p)
        if sh and b[i]["close"] > sh[1]: ev.append((i, "CHoCH" if trend == "down" else "BOS", "up", sh[0])); trend, sh = "up", None
        elif sl and b[i]["close"] < sl[1]: ev.append((i, "CHoCH" if trend == "up" else "BOS", "down", sl[0])); trend, sl = "down", None
    return ev[-8:]


def _ob(b, ev):
    out = []
    for i, typ, d, frm in ev:
        k, ext = frm, (float("inf") if d == "up" else float("-inf"))
        for q in range(frm, i + 1):
            if (b[q]["low"] < ext) if d == "up" else (b[q]["high"] > ext): ext = b[q]["low"] if d == "up" else b[q]["high"]; k = q
        j = next((q for q in range(k, max(0, k - 5) - 1, -1) if (b[q]["close"] < b[q]["open"] if d == "up" else b[q]["close"] > b[q]["open"])), None)
        if j is None: continue
        mit = any((b[q]["close"] < b[j]["low"]) if d == "up" else (b[q]["close"] > b[j]["high"]) for q in range(i + 1, len(b)))
        if not mit: out.append((d, j, b[j]["high"], b[j]["low"]))
    return out[-3:]


def test_js_matches_python():
    if not shutil.which("node"): raise RuntimeError("Node.js is required for the V7 extra-tools parity test")
    import numpy  # noqa: F401
    for seed in (5, 6, 7):
        b = _bars(seed=seed)
        js = ("const E=require(@E@),S=require(@S@);const b=JSON.parse(require('fs').readFileSync(0,'utf8'));const c=S.compute(b);"
              "const sma=b.map((x,i)=>i<143?NaN:b.slice(i-143,i+1).reduce((s,y)=>s+y.close,0)/144);"
              "const sig=b.map((x,i)=>({i,side:i%2?'buy':'sell'})).filter(s=>s.i>150);"
              "console.log(JSON.stringify({vwap:E.sessionVwap(b),vp:E.volumeProfile(b),op:E.opens(b),kz:E.killzones(b),lab:E.swingLabels(c.sw),ob:E.orderBlocks(b,c.events),ev:c.events,"
              "f1:E.filterSignals(sig,b,sma,{trend:true,kz:false}).length,f2:E.filterSignals(sig,b,sma,{trend:false,kz:true}).length,sma:sma,sig:sig.length}))").replace("@E@", json.dumps(JS)).replace("@S@", json.dumps(STRUCT))
        r = json.loads(subprocess.run(["node", "-e", js], input=json.dumps(b), capture_output=True, text=True, check=True).stdout)
        pv = _vwap(b)
        assert all((a is None and q is None) or (a is not None and q is not None and abs(a - q) < 1e-9) for a, q in zip(pv, r["vwap"])), "vwap"
        vp = _profile(b); assert all(abs(vp[k] - r["vp"][k]) < 1e-9 for k in ("poc", "vah", "val")), (vp, r["vp"])
        d, w, (ph, pl, pk) = _opens(b)
        assert r["op"]["day"]["i"] == d and r["op"]["week"]["i"] == w and abs(r["op"]["prevWeek"]["hi"] - ph) < 1e-9 and abs(r["op"]["prevWeek"]["lo"] - pl) < 1e-9 and r["op"]["prevWeek"]["weekStart"] == pk.isoformat()
        assert [(k["name"], k["i0"], k["i1"]) for k in r["kz"]] == _kz(b), "killzones"
        H, Lo = _swings(b)
        lab = []; ph_, pl_ = None, None
        for i, p in H: lab.append((i, "H", "H" if ph_ is None else "HH" if p > ph_ else "LH")); ph_ = p
        for i, p in Lo: lab.append((i, "L", "L" if pl_ is None else "HL" if p > pl_ else "LL")); pl_ = p
        assert [(x["i"], x["side"], x["label"]) for x in r["lab"]] == sorted(lab, key=lambda z: z[0])[-12:], "labels"
        ev = _events(b, H, Lo); assert [(e["i"], e["type"], e["dir"], e["from"]) for e in r["ev"]] == ev
        assert [(o["dir"], o["i0"], o["hi"], o["lo"]) for o in r["ob"]] == _ob(b, ev), (r["ob"], _ob(b, ev))
        sma = r["sma"]; sig = [(i, "buy" if i % 2 else "sell") for i in range(151, len(b))]
        t1 = [s for s in sig if sma[s[0]] is None or not (b[s[0]]["close"] < sma[s[0]] if s[1] == "buy" else b[s[0]]["close"] > sma[s[0]])]
        assert len(t1) == r["f1"], (len(t1), r["f1"])
        kz = _kz(b); t2 = [s for s in sig if any(a <= s[0] <= z for _, a, z in kz)]; assert len(t2) == r["f2"], (len(t2), r["f2"])


if __name__ == "__main__":
    test_js_matches_python()
    print("ok V7 extra tools: JS == independent Python on 3 synthetic series (VWAP, volume profile, NY day / week opens, prev week H/L, kill zones, HH/HL/LH/LL, order blocks, signal filters)")
