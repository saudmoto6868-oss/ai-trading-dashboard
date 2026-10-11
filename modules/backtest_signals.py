"""Walk-forward check of the two new confirmations: 'Trendline break' (family TL) and 'Sweep + CISD'.
At every `stride`-th candle the detector sees ONLY the candles up to that moment; the outcome is what price did over the next
H bars in the signal's direction (win = moved the signalled way; avg = mean return %), next to a BASELINE (the same number
of random entries on the same series, direction random) so a number is only 'good' if it beats the baseline.
Run:  python -m modules.backtest_signals     (OKX candles -> data/signal_stats.json; needs network)
Nothing here is invented: with no real candles there is no result."""
import json
from pathlib import Path

import numpy as np

from modules.signals import detect_all, BULL

OUT = Path(__file__).resolve().parent.parent / "data" / "signal_stats.json"
HORIZONS = (5, 10, 20)


def walk(df, key=None, family=None, stride=3, warm=120, horizons=HORIZONS, seed=0, cooldown=12):
    """-> {H: {n, win, avg, base_win, base_avg}} for signals matching key / family."""
    c = df["close"].values; rng = np.random.RandomState(seed); res = {H: [] for H in horizons}; base = {H: [] for H in horizons}
    last = -10**9   # one event = one sample: after a counted signal skip `cooldown` bars (the same setup stays 'live' for several candles)
    for i in range(warm, len(df) - max(horizons), stride):
        if i - last < cooldown:
            continue
        sigs, _ = detect_all(df.iloc[:i + 1].reset_index(drop=True))
        hit = [s for s in sigs if (key is None or s["key"] == key) and (family is None or s["family"] == family)]
        if not hit:
            continue
        last = i
        d = 1 if hit[0]["direction"] == BULL else -1
        rd = 1 if rng.rand() < .5 else -1
        for H in horizons:
            r = (c[i + H] / c[i] - 1) * 100
            res[H].append(d * r); base[H].append(rd * r)
    out = {}
    for H in horizons:
        x, b = np.array(res[H]), np.array(base[H]); n = len(x)
        out[H] = {"n": n, "win": round(100 * float((x > 0).mean()), 1) if n else None, "avg": round(float(x.mean()), 4) if n else None,
                  "base_win": round(100 * float((b > 0).mean()), 1) if n else None, "base_avg": round(float(b.mean()), 4) if n else None,
                  "edge": bool(n >= 30 and abs(100 * (x > 0).mean() - 50) > 196 * np.sqrt(.25 / n) and x.mean() > 0)}
    return out


def main(symbols=("BTC-USDT", "ETH-USDT", "SOL-USDT"), tfs=("15m", "1h")):
    from modules.backtest_tf import _BAR, fetch_long
    _BAR.setdefault("15m", "15m"); out = {}
    for s in symbols:
        for tf in tfs:
            try: df = fetch_long(s, tf, bars=1000)
            except Exception as e: out[f"{s}|{tf}"] = {"error": str(e)}; continue
            if df is None or len(df) < 300: continue
            out[f"{s}|{tf}"] = {"trendline_break": walk(df, key="tlbreak"), "sweep_cisd": walk(df, key="cisd")}
    OUT.parent.mkdir(exist_ok=True); OUT.write_text(json.dumps(out, indent=1)); print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
