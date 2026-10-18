"""Which timeframe works best for each strategy? Walk-forward test on OKX history:
at every Nth candle run the real scanner on the data available *at that moment*, build the real trade plan,
then follow the next candles until TP1 or SL (same candle = SL first, the conservative call).
Every strategy tag on the signal gets the outcome. Result: {strategy: {tf: {n, hit, tp, sl, exp}}}.

Run directly:  python -m modules.backtest_tf            (writes data/tf_stats.json)
The app also refreshes it in a background thread once a day."""
import json
import os
import time
from pathlib import Path

import pandas as pd
import requests

from config import OKX_CANDLES_URL
from modules.arabic import tag_for
from modules.risk_engine import build_trade_plan
from modules.scorer import scan_symbol

OUT = Path(__file__).resolve().parent.parent / "data" / "tf_stats.json"
TFS = ["1m", "1h", "1d", "1w"]
MIN_N = 8            # fewer resolved trades than this = "not enough data", never used for ranking
_BAR = {"1m": "1m", "1h": "1H", "1d": "1D", "1w": "1W"}
HORIZON = {"1m": 60, "1h": 48, "1d": 20, "1w": 8}   # bars to wait for TP1 before calling it expired


def fetch_long(symbol, tf, bars=1000, base_url=None, sleep=0.12):
    """Up to `bars` candles: newest 300 from /candles, older ones paged from /history-candles."""
    url = (base_url or OKX_CANDLES_URL)
    hist = url.replace("/market/candles", "/market/history-candles")
    rows, after = [], None
    for page in range(max(12, (bars - 300 + 99) // 100 + 1)):   # 300 newest + 100 per older page
        u, lim = (url, 300) if page == 0 else (hist, 100)
        params = {"instId": symbol, "bar": _BAR[tf], "limit": lim}
        if after:
            params["after"] = after
        r = requests.get(u, params=params, timeout=10)
        r.raise_for_status()
        data = r.json().get("data", [])
        if not data:
            break
        rows += data
        after = data[-1][0]
        if len(rows) >= bars:
            break
        time.sleep(sleep)
    if not rows:
        return None
    df = pd.DataFrame([x[:6] for x in rows], columns=["t", "open", "high", "low", "close", "volume"]).drop_duplicates("t")
    df["time"] = pd.to_datetime(df["t"].astype("int64"), unit="ms")
    for c in ("open", "high", "low", "close", "volume"):
        df[c] = df[c].astype(float)
    return df.sort_values("time").reset_index(drop=True)[["time", "open", "high", "low", "close", "volume"]]


def simulate(df, tf, stride=6, warm=120, min_score=1, scan=scan_symbol):
    """-> list of (tags, 'tp'|'sl'|'exp') for one candle series."""
    out, H = [], HORIZON[tf]
    hi, lo = df["high"].values, df["low"].values
    for i in range(warm, len(df) - 2, stride):
        try:
            r = scan("", {tf: df.iloc[:i + 1].reset_index(drop=True)}, tf)
        except Exception:
            continue
        if r["direction"] not in ("bullish", "bearish") or r["score"] < min_score:
            continue
        try:
            plan = build_trade_plan({**r, "trend_bias": r["direction"]})
        except Exception:
            continue
        entry, stop, tp1 = plan["entry"], plan["stop_loss"], plan["take_profits"][0]
        if not (entry and stop and tp1) or entry == stop:
            continue
        long_, res = r["direction"] == "bullish", "exp"
        for j in range(i + 1, min(len(df), i + 1 + H)):
            hit_sl = lo[j] <= stop if long_ else hi[j] >= stop
            hit_tp = hi[j] >= tp1 if long_ else lo[j] <= tp1
            if hit_sl:        # same candle touching both counts as a loss
                res = "sl"
                break
            if hit_tp:
                res = "tp"
                break
        tags = sorted({tag_for(s)[0] for s in r["signals"]}) + ["*"]   # "*" = every signal together
        out.append((tags, res))
    return out


def aggregate(results):
    """results: {tf: [(tags, res)]} -> {strategy: {tf: {n, hit, tp, sl, exp}}}"""
    stats = {}
    for tf, rows in results.items():
        for tags, res in rows:
            for g in tags:
                d = stats.setdefault(g, {}).setdefault(tf, {"tp": 0, "sl": 0, "exp": 0})
                d[res] += 1
    for g, per in stats.items():
        for tf, d in per.items():
            n = d["tp"] + d["sl"]
            d["n"] = n
            d["hit"] = round(d["tp"] / n, 3) if n else None
    return stats


def best_tf(stats):
    """-> {strategy: tf with the highest TP1 hit-rate among tfs with >= MIN_N resolved trades}"""
    out = {}
    for g, per in stats.items():
        ok = [(d["hit"], tf) for tf, d in per.items() if d["n"] >= MIN_N and d["hit"] is not None]
        if ok:
            out[g] = max(ok)[1]
    return out


def run(symbols, tfs=TFS, bars=1000, stride=6, base_url=None, fetch=fetch_long, scan=scan_symbol, progress=None):
    results = {tf: [] for tf in tfs}
    for sym in symbols:
        for tf in tfs:
            try:
                df = fetch(sym, tf, bars) if base_url is None else fetch(sym, tf, bars, base_url)
            except Exception:
                continue
            if df is None or len(df) < 200:
                continue
            results[tf] += simulate(df, tf, stride=stride, scan=scan)
            if progress:
                progress(sym, tf)
    stats = aggregate(results)
    return {"built": int(time.time()), "symbols": list(symbols), "min_n": MIN_N, "stats": stats, "best": best_tf(stats)}


def save(payload, path=OUT):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


def load(path=OUT, max_age=None):
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
        if max_age is not None and time.time() - d.get("built", 0) > max_age:
            return d, True     # (data, stale)
        return d, False
    except Exception:
        return None, True


if __name__ == "__main__":
    from config import CRYPTO_SYMBOLS
    p = run(CRYPTO_SYMBOLS[:8], progress=lambda s, t: print("done", s, t, flush=True))
    save(p)
    print(json.dumps(p["best"], ensure_ascii=False))
