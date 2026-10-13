"""Walk-forward comparison: the signal detectors with the Group-A quality filters ON vs OFF
(Strict SMC, order-block volume, breakout volume/delta - see sig_filters.py), plus Donchian ensemble / Session AMD / ORB.
Same method as backtest_signals.walk (detector sees only candles up to each bar; outcome = move over the next H bars in the
signal's direction, next to a random-direction BASELINE with the same entries - a number only counts if it beats the baseline).
Run on a machine with network:   python -m modules.backtest_filters  [BTC-USDT ETH-USDT ...]
Output: data/filter_compare.json + a Markdown table printed (paste it into STRATEGIES.md).
No candles -> no result. Win/avg here is a HIT-RATE OF DIRECTION, not a trading P&L (no costs, stops or targets)."""
import json
import os
import sys
from pathlib import Path

from modules.backtest_signals import walk

OUT = Path(__file__).resolve().parent.parent / "data" / "filter_compare.json"
KEYS = ("donch", "sess_amd", "orb", "ob", "breaker", "unicorn", "breakout", "liqline", "kzs", "po3")
FLAGS = ("SIGF_STRICT_SMC", "SIGF_OB_VOL", "SIGF_BO_VOL")


def _set(on: bool):
    for f in FLAGS:
        os.environ[f] = "1" if on else "0"


def compare(df, keys=KEYS, H=10, stride=3):
    """-> {key: {'on': stats, 'off': stats}} for horizon H (stats = walk()[H])."""
    out = {}
    saved = {f: os.environ.get(f) for f in FLAGS}
    try:
        for k in keys:
            row = {}
            for name, on in (("off", False), ("on", True)):
                _set(on)
                row[name] = walk(df, key=k, stride=stride, horizons=(H,))[H]
            out[k] = row
    finally:
        for f, v in saved.items():
            if v is None:
                os.environ.pop(f, None)
            else:
                os.environ[f] = v
    return out


def table(res: dict, H=10) -> str:
    lines = [f"| series | signal | filters | n | win % | avg % (H={H}) | base win % |", "|---|---|---|---|---|---|---|"]
    for series, per in res.items():
        if "error" in per:
            lines.append(f"| {series} | - | - | - | - | error: {per['error'][:60]} | - |")
            continue
        for k, row in per.items():
            for name in ("off", "on"):
                s = row[name]
                lines.append(f"| {series} | {k} | {name} | {s['n']} | {s['win']} | {s['avg']} | {s['base_win']} |")
    return "\n".join(lines)


def main(symbols=("BTC-USDT", "ETH-USDT", "SOL-USDT"), tfs=("15m", "1h")):
    from modules.backtest_tf import _BAR, fetch_long
    _BAR.setdefault("15m", "15m")
    res = {}
    for s in symbols:
        for tf in tfs:
            try:
                df = fetch_long(s, tf, bars=1000)
            except Exception as e:
                res[f"{s}|{tf}"] = {"error": str(e)}
                continue
            if df is None or len(df) < 300:
                continue
            res[f"{s}|{tf}"] = compare(df)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(res, indent=1))
    print(table(res))


if __name__ == "__main__":
    main(tuple(sys.argv[1:]) or ("BTC-USDT", "ETH-USDT", "SOL-USDT"))
