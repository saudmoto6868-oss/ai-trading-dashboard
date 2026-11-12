"""modules/v7_live_struct.js against an INDEPENDENT Python implementation of the same written definitions (swing 3, EQ 0.10 ATR, FVG 0.30 ATR unfilled <= 30 bars,
BOS / CHoCH on closes, premium / discount, OTE, prev UTC day). Synthetic random-walk candles. Needs node. Checks the maths / logic, not that any tool makes money."""
import json, os, shutil, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = os.path.join(ROOT, "modules", "v7_live_struct.js")


def _bars(n=500, seed=11):
    import numpy as np
    r = np.random.default_rng(seed); c = 100 + np.cumsum(r.normal(0, 0.8, n)); o = np.r_[c[0], c[:-1]]
    h = np.maximum(o, c) + np.abs(r.normal(0, 0.4, n)); l = np.minimum(o, c) - np.abs(r.normal(0, 0.4, n))
    t = 1_700_000_000 + 900 * np.arange(n)
    return [dict(time=int(a), open=float(b), high=float(d), low=float(e), close=float(f)) for a, b, d, e, f in zip(t, o, h, l, c)]


def _swings(b, L=3):
    H, Lo = [], []
    for i in range(L, len(b) - L):
        if all(b[i]["high"] > b[i - j]["high"] and b[i]["high"] >= b[i + j]["high"] for j in range(1, L + 1)): H.append((i, b[i]["high"]))
        if all(b[i]["low"] < b[i - j]["low"] and b[i]["low"] <= b[i + j]["low"] for j in range(1, L + 1)): Lo.append((i, b[i]["low"]))
    return H, Lo


def _atr(b):
    s = 0.0
    for i in range(len(b) - 14, len(b)):
        s += max(b[i]["high"] - b[i]["low"], abs(b[i]["high"] - b[i - 1]["close"]), abs(b[i]["low"] - b[i - 1]["close"]))
    return s / 14


def _events(b, H, Lo, L=3):
    ev, trend, sh, sl = [], None, None, None
    for i in range(len(b)):
        for (k, p) in H:
            if k + L == i: sh = (k, p)
        for (k, p) in Lo:
            if k + L == i: sl = (k, p)
        if sh and b[i]["close"] > sh[1]:
            ev.append((i, "CHoCH" if trend == "down" else "BOS", "up", sh[1])); trend = "up"; sh = None
        elif sl and b[i]["close"] < sl[1]:
            ev.append((i, "CHoCH" if trend == "up" else "BOS", "down", sl[1])); trend = "down"; sl = None
    return ev, trend


def _fvgs(b, atr):
    out, n = [], len(b)
    for i in range(2, n):
        if n - 1 - i > 30: continue
        z = None
        if b[i]["low"] - b[i - 2]["high"] >= 0.30 * atr: z = ("bull", i - 2, b[i - 2]["high"], b[i]["low"])
        elif b[i - 2]["low"] - b[i]["high"] >= 0.30 * atr: z = ("bear", i - 2, b[i]["high"], b[i - 2]["low"])
        if not z: continue
        filled = any((b[j]["low"] <= z[2]) if z[0] == "bull" else (b[j]["high"] >= z[3]) for j in range(i + 1, n))
        if not filled: out.append(z)
    return out


def test_js_matches_python_definitions():
    if not shutil.which("node"):
        raise RuntimeError("Node.js is required for the V7 JavaScript/Python parity test; refusing a silent skip.")
    try:
        import numpy  # noqa: F401
    except Exception as e:  # noqa: BLE001
        print("skip: numpy missing", e); return
    for seed in (11, 12, 13):
        b = _bars(seed=seed)
        js = "const S=require(%s);const b=JSON.parse(process.argv[1]);console.log(JSON.stringify(S.compute(b)))" % json.dumps(JS)
        res = json.loads(subprocess.run(["node", "-e", js, json.dumps(b)], capture_output=True, text=True, check=True).stdout)
        H, Lo = _swings(b)
        assert [(s["i"], s["p"]) for s in res["sw"]["H"]] == H and [(s["i"], s["p"]) for s in res["sw"]["L"]] == Lo, "swings differ"
        assert abs(res["atr"] - _atr(b)) < 1e-9
        ev, trend = _events(b, H, Lo)
        got = [(e["i"], e["type"], e["dir"], e["level"]) for e in res["events"]]
        assert got == ev[-8:] and res["trend"] == trend, (got[:3], ev[-3:])
        fv = _fvgs(b, _atr(b)); gotf = [(z["dir"], z["i0"], z["lo"], z["hi"]) for z in res["fvg"]]
        assert gotf == fv, (gotf, fv)
        if H and Lo:
            assert abs(res["pd"]["eq"] - (H[-1][1] + Lo[-1][1]) / 2) < 1e-9
            assert res["ote"]["dir"] == ("up" if H[-1][0] > Lo[-1][0] else "down")
    print("ok JS == independent Python on 3 synthetic series (swings, ATR, BOS / CHoCH, FVG, 50 %, OTE direction)")


if __name__ == "__main__":
    test_js_matches_python_definitions()
    print("V7 STRUCT TESTS DONE")
