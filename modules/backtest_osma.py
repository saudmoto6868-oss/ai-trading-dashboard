"""Does the 'RSI(2) + OsMA(1000,2,2000)' bar rule (MT5 indicator window 1) actually work?
Rule as the user defined it: the OsMA bar sits on the same 0-100 scale as the RSI; a bar at/under the 10 line = UP,
a bar above it = DOWN (bars <= 0 are off the pane in MT5 and are ignored). A signal is the first bar of a new state.
Each variant is scored on the next H closes (win = price moved the signalled way):
  base          the rule as defined
  inverse       the same signals with the direction flipped (a bar > 10 = oversold RSI = bounce?)
  base+trend    base, but UP only when close > SMA(trend) and DOWN only when close < SMA(trend)
  inverse+trend inverse, same trend filter (UP = with-trend dip buy, as in Connors' RSI(2) work)
Run:  python -m modules.backtest_osma            (OKX candles -> data/osma_stats.json; needs network)
No result is meaningful until it has been run on REAL candles - the numbers are never invented."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent.parent / "data" / "osma_stats.json"
LV, HORIZONS, TREND = 10.0, (3, 5, 10), 50


def _rsi(close, n=2):
    c = np.asarray(close, float); out = np.full(len(c), 50.0); ag = al = 0.0
    for i in range(1, len(c)):
        d = c[i] - c[i-1]; g, l = max(d, 0.0), max(-d, 0.0)
        if i <= n: ag += g/n; al += l/n
        else: ag = (ag*(n-1) + g)/n; al = (al*(n-1) + l)/n
        out[i] = 50.0 if i < n else (100.0 if al == 0 else 100 - 100/(1 + ag/al))
    return out


def osma_bars(close, rsi_n=2, fast=1000, slow=2, sig=2000):
    """MT5 'Moving Average of Oscillator' applied to RSI data: EMA(fast)-EMA(slow), minus SMA(that, sig)."""
    r = _rsi(close, rsi_n); kf, ks = 2/(fast+1), 2/(slow+1); ef = es = r[0]; mac = np.empty(len(r))
    for i, v in enumerate(r):
        ef = v*kf + ef*(1-kf); es = v*ks + es*(1-ks); mac[i] = ef - es
    cs = np.cumsum(mac); n = np.minimum(np.arange(1, len(mac)+1), sig)
    sg = (cs - np.concatenate([np.zeros(sig), cs[:-sig]])[:len(cs)]) / n if len(cs) > sig else cs / n
    return mac - sg


def signals(df, trend=TREND):
    """-> list of (index, 'up'|'down') : the first bar of each state."""
    o = osma_bars(df["close"].values); out, prev = [], None
    for i, v in enumerate(o):
        st = "up" if 0 < v <= LV else "down" if v > LV else None
        if st and st != prev: out.append((i, st))
        prev = st if st else prev if v > 0 else None
    return out


def evaluate(df, trend=TREND):
    """-> {variant: {H: {n, win, avg}}}"""
    c = df["close"].values; sma = pd.Series(c).rolling(trend).mean().values; sg = signals(df)
    res = {}
    for name, flip, filt in (("base", False, False), ("inverse", True, False), ("base+trend", False, True), ("inverse+trend", True, True)):
        res[name] = {}
        for H in HORIZONS:
            rets = []
            for i, d in sg:
                if i + H >= len(c) or np.isnan(sma[i]): continue
                if flip: d = "down" if d == "up" else "up"
                if filt and not ((d == "up" and c[i] > sma[i]) or (d == "down" and c[i] < sma[i])): continue
                r = (c[i+H]/c[i] - 1)*100; rets.append(r if d == "up" else -r)
            n = len(rets)
            res[name][H] = {"n": n, "win": round(100*sum(x > 0 for x in rets)/n, 1) if n else None, "avg": round(float(np.mean(rets)), 4) if n else None}
    return res


def significant(win, n):
    """win rate clearly away from 50% (95% binomial band)? Needs n >= 30."""
    return bool(n and n >= 30 and win is not None and abs(win - 50) > 196*np.sqrt(.25/n))


def main(symbols=("BTC-USDT", "ETH-USDT", "SOL-USDT"), tfs=("15m", "1h", "1d")):
    from modules.backtest_tf import _BAR, fetch_long
    _BAR.setdefault("15m", "15m")
    out = {}
    for s in symbols:
        for tf in tfs:
            try: df = fetch_long(s, tf, bars=1000)
            except Exception as e: out[f"{s}|{tf}"] = {"error": str(e)}; continue
            if df is not None and len(df) > 200: out[f"{s}|{tf}"] = evaluate(df)
    OUT.parent.mkdir(exist_ok=True); OUT.write_text(json.dumps(out, indent=1)); print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
