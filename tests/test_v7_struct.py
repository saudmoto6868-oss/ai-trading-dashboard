"""Parity test for modules/v7_live_struct.js against independent Python definitions.
Requires Node.js and numpy. CI must fail if either dependency is absent; a skipped parity
check must never be reported as a successful test. Synthetic data only; no profitability claim."""
import json
import os
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = os.path.join(ROOT, "modules", "v7_live_struct.js")


def _bars(n=500, seed=11):
    import numpy as np
    r = np.random.default_rng(seed)
    c = 100 + np.cumsum(r.normal(0, 0.8, n))
    o = np.r_[c[0], c[:-1]]
    h = np.maximum(o, c) + np.abs(r.normal(0, 0.4, n))
    l = np.minimum(o, c) - np.abs(r.normal(0, 0.4, n))
    t = 1_700_000_000 + 900 * np.arange(n)
    return [dict(time=int(a), open=float(b), high=float(d), low=float(e), close=float(f))
            for a, b, d, e, f in zip(t, o, h, l, c)]


def _swings(b, L=3):
    H, Lo = [], []
    for i in range(L, len(b) - L):
        if all(b[i]["high"] > b[i - j]["high"] and b[i]["high"] >= b[i + j]["high"] for j in range(1, L + 1)):
            H.append((i, b[i]["high"]))
        if all(b[i]["low"] < b[i - j]["low"] and b[i]["low"] <= b[i + j]["low"] for j in range(1, L + 1)):
            Lo.append((i, b[i]["low"]))
    return H, Lo


def _atr(b):
    s = 0.0
    for i in range(len(b) - 14, len(b)):
        s += max(b[i]["high"] - b[i]["low"],
                 abs(b[i]["high"] - b[i - 1]["close"]),
                 abs(b[i]["low"] - b[i - 1]["close"]))
    return s / 14


def _events(b, H, Lo, L=3):
    ev, trend, sh, sl = [], None, None, None
    for i in range(len(b)):
        for k, p in H:
            if k + L == i:
                sh = (k, p)
        for k, p in Lo:
            if k + L == i:
                sl = (k, p)
        if sh and b[i]["close"] > sh[1]:
            ev.append((i, "CHoCH" if trend == "down" else "BOS", "up", sh[1]))
            trend, sh = "up", None
        elif sl and b[i]["close"] < sl[1]:
            ev.append((i, "CHoCH" if trend == "up" else "BOS", "down", sl[1]))
            trend, sl = "down", None
    return ev, trend


def _ny_session_day(sec):
    dt = datetime.fromtimestamp(sec, timezone.utc).astimezone(ZoneInfo("America/New_York"))
    if dt.hour >= 18:
        dt += timedelta(days=1)
    return dt.date().isoformat()


def _prev_day(b):
    if not b:
        return None
    today = _ny_session_day(b[-1]["time"])
    prior, hi, lo = None, float("-inf"), float("inf")
    for x in reversed(b):
        key = _ny_session_day(x["time"])
        if key == today:
            continue
        if prior is None:
            prior = key
        if key != prior:
            break
        hi, lo = max(hi, x["high"]), min(lo, x["low"])
    return None if prior is None else {"hi": hi, "lo": lo, "sessionDate": prior}


def _sessions(b):
    windows = (("Asia", 19, 2), ("London", 2, 9), ("NY", 8, 17))
    ny = ZoneInfo("America/New_York")
    out = []
    for name, start, end in windows:
        run = None
        for i, x in enumerate(b):
            dt = datetime.fromtimestamp(x["time"], timezone.utc).astimezone(ny)
            minute = dt.hour * 60 + dt.minute
            inside = (start * 60 <= minute < end * 60) if start < end else (minute >= start * 60 or minute < end * 60)
            if inside:
                if run is None:
                    run = {"name": name, "i0": i, "i1": i, "hi": x["high"], "lo": x["low"]}
                else:
                    run["i1"] = i
                    run["hi"] = max(run["hi"], x["high"])
                    run["lo"] = min(run["lo"], x["low"])
            elif run is not None:
                out.append(run)
                run = None
        if run is not None:
            out.append(run)
    return sorted(out, key=lambda x: x["i0"])[-9:]


def _equal(sw, atr, n, max_back=150):
    out, tol = [], 0.10 * atr
    for a in range(len(sw)):
        for c in range(a + 1, len(sw)):
            if sw[a][0] >= n - max_back and sw[c][0] >= n - max_back and abs(sw[a][1] - sw[c][1]) <= tol:
                out.append({"i1": sw[a][0], "i2": sw[c][0], "p": (sw[a][1] + sw[c][1]) / 2})
    return out[-6:]


def _fvgs(b, atr):
    out, n = [], len(b)
    for i in range(2, n):
        if n - 1 - i > 30:
            continue
        z = None
        if b[i]["low"] - b[i - 2]["high"] >= 0.30 * atr:
            z = ("bull", i - 2, b[i - 2]["high"], b[i]["low"])
        elif b[i - 2]["low"] - b[i]["high"] >= 0.30 * atr:
            z = ("bear", i - 2, b[i]["high"], b[i - 2]["low"])
        if not z:
            continue
        filled = any((b[j]["low"] <= z[2]) if z[0] == "bull" else (b[j]["high"] >= z[3])
                     for j in range(i + 1, n))
        if not filled:
            out.append(z)
    return out


def test_js_matches_python_definitions():
    if not shutil.which("node"):
        raise RuntimeError("Node.js is required for the V7 structure parity test")
    import numpy  # noqa: F401

    for seed in (11, 12, 13):
        b = _bars(seed=seed)
        js = "const S=require(%s);const b=JSON.parse(process.argv[1]);console.log(JSON.stringify(S.compute(b)))" % json.dumps(JS)
        res = json.loads(subprocess.run(
            ["node", "-e", js, json.dumps(b)], capture_output=True, text=True, check=True
        ).stdout)
        H, Lo = _swings(b)
        assert [(s["i"], s["p"]) for s in res["sw"]["H"]] == H
        assert [(s["i"], s["p"]) for s in res["sw"]["L"]] == Lo
        assert abs(res["atr"] - _atr(b)) < 1e-9
        ev, trend = _events(b, H, Lo)
        got = [(e["i"], e["type"], e["dir"], e["level"]) for e in res["events"]]
        assert got == ev[-8:] and res["trend"] == trend, (got[-3:], ev[-3:])
        fv = _fvgs(b, _atr(b))
        gotf = [(z["dir"], z["i0"], z["lo"], z["hi"]) for z in res["fvg"]]
        assert gotf == fv, (gotf, fv)
        if H and Lo:
            assert abs(res["pd"]["eq"] - (H[-1][1] + Lo[-1][1]) / 2) < 1e-9
            assert res["ote"]["dir"] == ("up" if H[-1][0] > Lo[-1][0] else "down")
            span = H[-1][1] - Lo[-1][1]
            expected = ([H[-1][1] - q * span for q in (0.62, 0.705, 0.79)]
                        if H[-1][0] > Lo[-1][0]
                        else [Lo[-1][1] + q * span for q in (0.62, 0.705, 0.79)])
            assert all(abs(res["ote"][k] - v) < 1e-9 for k, v in zip(("p62", "p705", "p79"), expected))
        assert res["prevDay"] == _prev_day(b)
        assert res["sessions"] == _sessions(b)
        for key, swings in (("eqh", H), ("eql", Lo)):
            actual = [{"i1": x["i1"], "i2": x["i2"], "p": x["p"]} for x in res[key]]
            assert actual == _equal(swings, _atr(b), len(b)), (key, actual, _equal(swings, _atr(b), len(b)))


if __name__ == "__main__":
    test_js_matches_python_definitions()
    print("ok JS == independent Python on 3 synthetic series (swings, ATR, BOS / CHoCH, FVG, 50 %, OTE direction)")
    print("V7 STRUCT TESTS DONE")
