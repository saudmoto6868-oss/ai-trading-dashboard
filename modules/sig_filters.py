"""
GROUP A - quality filters on the EXISTING detectors (no new signals).

Each filter works on the BULLISH frame (the bearish side is the same code on the
price-inverted copy, see signals.detect_all) and only ever REMOVES signals that
fail an extra condition, so it can make the scanner quieter, never noisier.

  strict_smc : order block / breaker / unicorn must come from a *real* structure
               break - a candle CLOSE beyond a confirmed swing high by a margin
               with a displacement (big-body) candle, first break of that swing
               (idea from the Synvoya "strict SMC" option).
  ob_volume  : an order block must have been built with above-normal volume
               (idea from Volumized Order Blocks). Needs real volume.
  bo_volume  : a breakout must come with above-average volume AND buying
               pressure (idea from Breakout Volume Delta). Needs real volume.
               Delta is ESTIMATED from candles (volume x close location in the
               range), not tick data - a proxy, labelled as such in the text.

Volume filters switch themselves off when the candles carry no usable volume
(forex / indices from Yahoo have none), so only markets with real volume
(crypto, stocks) are filtered. Everything is configurable below or via env
(SIGF_STRICT_SMC=0, SIGF_OB_VOL=0, SIGF_BO_VOL=0, SIGF_OB_VOL_MULT=1.2 ...).
Nothing here is a proven edge - run modules/backtest_signals.py with the
switches on and off on real data before trusting the numbers.
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd

OB_KEYS = ("ob", "breaker", "unicorn")
BREAKOUT_KEYS = ("breakout", "liqline", "ohl_break", "orb")


def _env_bool(name: str, default: bool) -> bool:
    v = os.environ.get(name)
    return default if v is None else v.strip().lower() not in ("0", "false", "no", "off", "")


def _env_num(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, default))
    except ValueError:
        return default


def options() -> dict:
    return {
        "strict_smc": _env_bool("SIGF_STRICT_SMC", True),
        "ob_volume": _env_bool("SIGF_OB_VOL", True),
        "bo_volume": _env_bool("SIGF_BO_VOL", True),
        "strict_margin_atr": _env_num("SIGF_STRICT_MARGIN", 0.1),   # close must clear the swing high by this many ATR
        "strict_body_atr": _env_num("SIGF_STRICT_BODY", 1.0),       # break candle (or the leg) body, in ATR
        "ob_vol_mult": _env_num("SIGF_OB_VOL_MULT", 1.0),           # OB volume vs normal 3-bar volume
        "bo_vol_mult": _env_num("SIGF_BO_VOL_MULT", 1.2),           # breakout bar volume vs 20-bar average
        "bo_min_delta": _env_num("SIGF_BO_DELTA", 0.1),             # share of volume that must be net buying
        "max_age": int(_env_num("SIGF_MAX_AGE", 80)),
    }


def has_volume(df: pd.DataFrame) -> bool:
    """Real volume = a volume column where almost every candle has some."""
    if "volume" not in df.columns or len(df) < 30:
        return False
    v = df["volume"].values.astype(float)
    return bool((np.nan_to_num(v) > 0).mean() >= 0.9)


def _atr(df: pd.DataFrame, n: int = 14) -> np.ndarray:
    pc = df["close"].shift(1)
    tr = pd.concat([df["high"] - df["low"], (df["high"] - pc).abs(), (df["low"] - pc).abs()], axis=1).max(axis=1)
    return tr.rolling(n, min_periods=1).mean().values


def strict_breaks(df: pd.DataFrame, opt: dict | None = None) -> list[dict]:
    """Bullish structure breaks that pass the strict test. -> [{'j','level','pivot','body_atr'}]"""
    from modules.signals import structure_breaks   # local import: signals imports this module

    opt = opt or options()
    atr = _atr(df)
    o, c = df["open"].values, df["close"].values
    out = []
    for b in structure_breaks(df, lookback=opt["max_age"]):
        j, lvl, i = b["j"], b["level"], b["pivot"]
        if c[j] - lvl < opt["strict_margin_atr"] * atr[j]:
            continue                                    # a close that barely clears the level = not a real break
        legs = slice(max(i, j - 2), j + 1)              # the break candle or one of the 2 before it carried the move
        body = np.max(np.abs(c[legs] - o[legs])) / max(atr[j], 1e-12)
        if body < opt["strict_body_atr"]:
            continue                                    # no displacement
        out.append({**b, "body_atr": float(body)})
    return out


def _bar_of_zone(df: pd.DataFrame, zone, upto: int | None = None, span: int = 200) -> int | None:
    """Index of the candle whose low/high are exactly the zone (order blocks are one candle)."""
    lo, hi = df["low"].values, df["high"].values
    end = len(df) if upto is None else upto
    for k in range(end - 1, max(end - span, -1), -1):
        if abs(lo[k] - zone[0]) <= 1e-9 * max(1.0, abs(zone[0])) and abs(hi[k] - zone[1]) <= 1e-9 * max(1.0, abs(zone[1])):
            return k
    return None


def ob_volume_ratio(df: pd.DataFrame, k: int) -> float | None:
    """Volume of the order-block candle + the 2 after it, vs the typical 3-bar volume before it."""
    v = df["volume"].values.astype(float)
    if k < 53 or k + 1 >= len(v):
        return None
    cur = v[k:k + 3].sum()
    base = pd.Series(v[:k]).rolling(3).sum().iloc[-50:].median()
    return float(cur / base) if base and base > 0 else None


def breakout_delta(df: pd.DataFrame, bars: int = 3) -> tuple[float, float]:
    """(volume of the best recent bar / 20-bar average, net-buying share of the last `bars` bars' volume).
    Delta per bar = volume x (close - open position inside the range) -> a candle-based ESTIMATE."""
    v = df["volume"].values.astype(float)
    o, h, l, c = (df[x].values for x in ("open", "high", "low", "close"))
    rng = np.where(h - l > 0, h - l, np.nan)
    loc = np.nan_to_num((c - o) / rng)                  # -1..+1: where the bar closed relative to its open, in range units
    delta = v * loc
    avg = pd.Series(v).rolling(20).mean().shift(bars).iloc[-1]
    ratio = float(v[-bars:].max() / avg) if avg and avg > 0 else 0.0
    tot = v[-bars:].sum()
    share = float(delta[-bars:].sum() / tot) if tot > 0 else 0.0
    return ratio, share


def apply(df: pd.DataFrame, sigs: list[dict], opt: dict | None = None) -> list[dict]:
    """Filter the raw (bullish-frame) detector output; annotate survivors with the measured values."""
    if not sigs:
        return sigs
    opt = opt or options()
    vol_ok = has_volume(df)
    breaks = strict_breaks(df, opt) if opt["strict_smc"] and any(s["key"] in OB_KEYS for s in sigs) else None
    kept = []
    for s in sigs:
        key = s["key"]
        if key in OB_KEYS:
            if breaks is not None:
                # the zone must have formed right before one of the strict breaks (its swing is the zone's origin)
                zone = s.get("zone")
                k = _bar_of_zone(df, zone) if zone else None
                ok = any(k is None or (b["pivot"] <= k <= b["j"]) for b in breaks) if zone else bool(breaks)
                if not ok:
                    continue
                s["_v"] = {**s["_v"], "strict": 1}
            if opt["ob_volume"] and vol_ok and s.get("zone") and key == "ob":
                k = _bar_of_zone(df, s["zone"])
                r = ob_volume_ratio(df, k) if k is not None else None
                if r is not None:
                    if r < opt["ob_vol_mult"]:
                        continue
                    s["_v"] = {**s["_v"], "obvol": round(r, 2)}
        elif key in BREAKOUT_KEYS and opt["bo_volume"] and vol_ok:
            ratio, share = breakout_delta(df)
            if ratio < opt["bo_vol_mult"] or share < opt["bo_min_delta"]:
                continue
            s["_v"] = {**s["_v"], "bovol": round(ratio, 2), "bodelta": round(share, 2)}
        kept.append(s)
    return kept
