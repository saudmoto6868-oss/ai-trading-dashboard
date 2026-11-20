"""modules/v7_live_ind.js against the Python reference of the CFX v7 research (research/cfx/cfx_osc_combo.py) on synthetic random-walk candles.
Needs node + pandas + numpy; skips (says so) when one is missing. Checks the maths only, NOT the live chart in a browser and NOT any market claim."""
import json, os, shutil, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research", "cfx"))
IND = os.path.join(ROOT, "modules", "v7_live_ind.js")


def _bars(n=700, seed=7):
    import numpy as np
    r = np.random.default_rng(seed); c = 100 + np.cumsum(r.normal(0, 0.6, n)); o = np.r_[c[0], c[:-1]]
    h = np.maximum(o, c) + np.abs(r.normal(0, 0.3, n)); l = np.minimum(o, c) - np.abs(r.normal(0, 0.3, n))
    return [{"open": float(a), "high": float(b), "low": float(d), "close": float(e)} for a, b, d, e in zip(o, h, l, c)]


def _ref_signals(df, look=3):
    import numpy as np
    k, d, rsi, macd = (df[x].to_numpy(float) for x in ("st_k", "st_d", "rsi14", "macd")); out = []
    for i in range(2, len(df)):
        if not all(np.isfinite(x) for x in (k[i], k[i-1], d[i], d[i-1], rsi[i], rsi[i-1], macd[i], macd[i-1])):
            continue
        a = max(0, i - look)
        os_ = any(np.isfinite(k[j]) and k[j] <= 15 for j in range(a, i + 1)); ob = any(np.isfinite(k[j]) and k[j] >= 85 for j in range(a, i + 1))
        up = k[i-1] <= d[i-1] and k[i] > d[i]; dn = k[i-1] >= d[i-1] and k[i] < d[i]
        if up and os_ and rsi[i] > rsi[i-1] and macd[i] > macd[i-1]: out.append((i, "buy"))
        elif dn and ob and rsi[i] < rsi[i-1] and macd[i] < macd[i-1]: out.append((i, "sell"))
    return out


def test_js_matches_python_reference():
    if not shutil.which("node"):
        print("skip: node not installed"); return
    try:
        import numpy, pandas  # noqa: F401
        from cfx_osc_combo import add_combo_oscillators
    except Exception as e:  # noqa: BLE001
        print("skip: reference not importable:", type(e).__name__, e); return
    import pandas as pd, numpy as np
    bars = _bars(); df = add_combo_oscillators(pd.DataFrame(bars))
    js = "const I=require(%s);const b=JSON.parse(process.argv[1]);const x=I.compute(b);const s=I.signalsB(x,b.length-1);console.log(JSON.stringify({x,s}))" % json.dumps(IND)
    res = json.loads(subprocess.run(["node", "-e", js, json.dumps(bars)], capture_output=True, text=True, check=True).stdout)
    for jk, pk in (("k", "st_k"), ("d", "st_d"), ("rsi", "rsi14"), ("macd", "macd"), ("sma77", "sma77"), ("sma144", "sma144")):
        a = np.array([np.nan if v is None else v for v in res["x"][jk]], float); b = df[pk].to_numpy(float)
        assert np.array_equal(np.isnan(a), np.isnan(b)), (jk, "NaN pattern differs")
        m = ~np.isnan(b)
        assert np.allclose(a[m], b[m], atol=1e-6, rtol=1e-9), (jk, float(np.max(np.abs(a[m] - b[m]))))
    ref = _ref_signals(df); got = [(s["i"], s["side"]) for s in res["s"]]
    assert got == ref, (got[:5], ref[:5])
    print("ok JS == Python reference; signals:", len(got))


if __name__ == "__main__":
    test_js_matches_python_reference()
    print("V7 LIVE INDICATOR TESTS DONE")
