"""modules/v7_live_ind2.js against an independent numpy implementation (SMA, EMA, Bollinger, Donchian, ATR, Keltner, Supertrend, Ichimoku, ADX, OBV, CCI, Williams %R).
Synthetic candles. Needs node + numpy. Fails (never skips) if Node is missing."""
import json, os, shutil, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_v7_extra as X
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = os.path.join(ROOT, "modules", "v7_live_ind2.js")


def _np(b):
    import numpy as np
    return [np.array([x[k] for x in b], dtype=float) for k in ("open", "high", "low", "close", "volume")]


def _sma(v, n):
    import numpy as np
    o = np.full(len(v), np.nan); c = np.cumsum(np.r_[0, v])
    o[n - 1:] = (c[n:] - c[:-n]) / n; return o


def _ema(v, n):
    import numpy as np
    o = np.full(len(v), np.nan); e = v[:n].mean(); o[n - 1] = e
    for i in range(n, len(v)): e = 2 / (n + 1) * v[i] + (1 - 2 / (n + 1)) * e; o[i] = e
    return o


def _tr(h, l, c):
    import numpy as np
    t = h - l; t[1:] = np.maximum(h[1:] - l[1:], np.maximum(abs(h[1:] - c[:-1]), abs(l[1:] - c[:-1]))); return t


def _atr(h, l, c, n):
    import numpy as np
    t = _tr(h, l, c); o = np.full(len(h), np.nan); a = t[1:n + 1].mean(); o[n] = a
    for i in range(n + 1, len(h)): a = (a * (n - 1) + t[i]) / n; o[i] = a
    return o


def _eq(a, b, tol=1e-7):
    import numpy as np
    a = np.array(a, dtype=float); b = np.array([np.nan if x is None else x for x in b], dtype=float)
    assert a.shape == b.shape, (a.shape, b.shape)
    both = np.isnan(a) & np.isnan(b); assert np.all(both | (abs(a - b) <= tol * (1 + abs(b)))), "arrays differ"


def test_js_matches_python():
    import numpy as np
    if not shutil.which("node"): raise RuntimeError("Node.js is required for the V7 indicator parity test")
    for seed in (5, 6, 7):
        b = X._bars(n=400, seed=seed); o, h, l, c, v = _np(b)
        js = ("const I=require(@J@);const b=JSON.parse(require('fs').readFileSync(0,'utf8'));const h=b.map(x=>x.high),l=b.map(x=>x.low),c=b.map(x=>x.close),v=b.map(x=>x.volume);"
              "console.log(JSON.stringify({sma:I.sma(c,20),ema:I.ema(c,21),bb:I.bollinger(c,20,2),dc:I.donchian(h,l,20),atr:I.atr(h,l,c,14),kc:I.keltner(h,l,c,20,10,2),st:I.supertrend(h,l,c,10,3),"
              "ich:I.ichimoku(h,l,c),adx:I.adx(h,l,c,14),obv:I.obv(c,v),cci:I.cci(h,l,c,20),wr:I.williamsR(h,l,c,14)}))").replace("@J@", json.dumps(JS))
        r = json.loads(subprocess.run(["node", "-e", js], input=json.dumps(b), capture_output=True, text=True, check=True).stdout)
        _eq(_sma(c, 20), r["sma"]); _eq(_ema(c, 21), r["ema"])
        m = _sma(c, 20); sd = np.array([np.nan] * 19 + [c[i - 19:i + 1].std() for i in range(19, len(c))]); _eq(m + 2 * sd, r["bb"]["up"]); _eq(m - 2 * sd, r["bb"]["lo"])
        hh = np.array([np.nan] * 19 + [h[i - 19:i + 1].max() for i in range(19, len(c))]); ll = np.array([np.nan] * 19 + [l[i - 19:i + 1].min() for i in range(19, len(c))]); _eq(hh, r["dc"]["up"]); _eq(ll, r["dc"]["lo"])
        a14 = _atr(h, l, c, 14); _eq(a14, r["atr"]); e20 = _ema(c, 20); a10 = _atr(h, l, c, 10); _eq(e20 + 2 * a10, r["kc"]["up"]); _eq(e20 - 2 * a10, r["kc"]["lo"])
        # supertrend, independent loop
        fu = fl = None; tr = 1; line = np.full(len(c), np.nan)
        for i in range(len(c)):
            if np.isnan(a10[i]): continue
            hl = (h[i] + l[i]) / 2; bu, bl = hl + 3 * a10[i], hl - 3 * a10[i]
            if fu is None: fu, fl, tr = bu, bl, 1
            else:
                pu, pl = fu, fl; fu = bu if (bu < pu or c[i - 1] > pu) else pu; fl = bl if (bl > pl or c[i - 1] < pl) else pl
                if tr == 1 and c[i] < fl: tr = -1
                elif tr == -1 and c[i] > fu: tr = 1
            line[i] = fl if tr == 1 else fu
        _eq(line, r["st"]["line"])
        def mid(n):
            return np.array([np.nan] * (n - 1) + [(h[i - n + 1:i + 1].max() + l[i - n + 1:i + 1].min()) / 2 for i in range(n - 1, len(c))])
        t9, k26, b52 = mid(9), mid(26), mid(52); sa = np.full(len(c) + 26, np.nan); sb = np.full(len(c) + 26, np.nan)
        sa[26:] = (t9 + k26) / 2; sb[26:] = b52
        _eq(t9, r["ich"]["tenkan"]); _eq(k26, r["ich"]["kijun"]); _eq(sa, r["ich"]["spanA"]); _eq(sb, r["ich"]["spanB"])
        # ADX
        n = 14; tr_ = _tr(h, l, c); up = np.r_[0, h[1:] - h[:-1]]; dn = np.r_[0, l[:-1] - l[1:]]
        pdm = np.where((up > dn) & (up > 0), up, 0.0); mdm = np.where((dn > up) & (dn > 0), dn, 0.0); pdm[0] = mdm[0] = 0
        st, sp, sm = tr_[1:n + 1].sum(), pdm[1:n + 1].sum(), mdm[1:n + 1].sum(); dx = np.full(len(c), np.nan); pd_ = np.full(len(c), np.nan)
        for i in range(n, len(c)):
            if i > n: st = st - st / n + tr_[i]; sp = sp - sp / n + pdm[i]; sm = sm - sm / n + mdm[i]
            p, q = 100 * sp / st, 100 * sm / st; pd_[i] = p; dx[i] = 0 if p + q == 0 else 100 * abs(p - q) / (p + q)
        adx = np.full(len(c), np.nan); a = dx[n:2 * n].mean(); adx[2 * n - 1] = a
        for i in range(2 * n, len(c)): a = (a * (n - 1) + dx[i]) / n; adx[i] = a
        _eq(adx, r["adx"]["adx"]); _eq(pd_, r["adx"]["pdi"])
        ob = np.zeros(len(c)); ob[1:] = np.cumsum(np.where(c[1:] > c[:-1], v[1:], np.where(c[1:] < c[:-1], -v[1:], 0))); _eq(ob, r["obv"])
        tp = (h + l + c) / 3; ma = _sma(tp, 20); cc = np.full(len(c), np.nan)
        for i in range(19, len(c)): d = abs(tp[i - 19:i + 1] - ma[i]).mean(); cc[i] = 0 if d == 0 else (tp[i] - ma[i]) / (0.015 * d)
        _eq(cc, r["cci"]); wr = np.array([np.nan] * 13 + [-100 * (h[i - 13:i + 1].max() - c[i]) / (h[i - 13:i + 1].max() - l[i - 13:i + 1].min()) for i in range(13, len(c))]); _eq(wr, r["wr"])


if __name__ == "__main__":
    test_js_matches_python()
    print("ok V7 indicators: JS == independent numpy on 3 synthetic series (SMA, EMA, Bollinger, Donchian, ATR, Keltner, Supertrend, Ichimoku, ADX, OBV, CCI, Williams %R)")
