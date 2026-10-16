"""MULTI-TIMEFRAME FRAMEWORK for swing / position trades: Weekly (bias) -> Daily (setup) -> 4H (timing).
Per timeframe: swing structure (last two swing highs / lows: HH+HL = up, LH+LL = down, else range) and the side of the
50-EMA. Bias = structure (+1/-1) + EMA side (+1/-1): both agree = strong, one = weak, 0 = neutral.
Coherence of a trade: 'aligned' = every available timeframe backs the side, 'conflict' = the weekly or daily bias is
AGAINST it, 'partial' = anything else. It is context shown next to the stars and used to rank alerts - it is not a
proven edge (no real-data backtest yet)."""
from __future__ import annotations

import pandas as pd

from modules.signals import fractal_pivots

MTF_TFS = ("1w", "1d", "4h")                   # bias, setup, timing
ROLE = {"1w": "bias", "1d": "setup", "4h": "timing"}
SWING_TYPES = ("Swing", "Position")
MIN_BARS = 60


def tf_state(df) -> dict:
    """-> {'trend','ema','bias','strength','hi','lo'} for one candle frame (needs >= 60 bars)."""
    if df is None or len(df) < MIN_BARS:
        return {"available": False}
    d = df.reset_index(drop=True)
    piv = fractal_pivots(d, 3)
    hs = [p for _, p, k in piv if k == "H"][-2:]
    ls = [p for _, p, k in piv if k == "L"][-2:]
    trend = "range"
    if len(hs) == 2 and len(ls) == 2:
        if hs[1] > hs[0] and ls[1] > ls[0]:
            trend = "up"
        elif hs[1] < hs[0] and ls[1] < ls[0]:
            trend = "down"
    ema = d["close"].ewm(span=50, adjust=False).mean()
    px = float(d["close"].iloc[-1])
    side = "above" if px > float(ema.iloc[-1]) else "below"
    score = (1 if trend == "up" else -1 if trend == "down" else 0) + (1 if side == "above" else -1)
    return {"available": True, "trend": trend, "ema": side, "bias": "bull" if score > 0 else "bear" if score < 0 else "neutral",
            "strength": abs(score), "hi": hs[-1] if hs else None, "lo": ls[-1] if ls else None}


def framework(frames: dict, trigger_tf: str | None = None, trigger_df=None) -> list[dict]:
    """Rows for the tfs in MTF_TFS (frames = {tf: df}); the trigger frame is used for its own tf if `frames` lacks it."""
    rows = []
    for tf in MTF_TFS:
        df = frames.get(tf)
        if df is None and trigger_tf == tf:
            df = trigger_df
        rows.append({"tf": tf, "role": ROLE[tf], **tf_state(df)})
    return rows


def coherence(direction: str, rows: list[dict]) -> dict:
    """-> {'status': aligned|partial|conflict|unknown, 'agree': n, 'of': m}"""
    want = {"bullish": "bull", "bearish": "bear"}.get(direction)
    av = [r for r in rows if r.get("available")]
    if not want or len(av) < 2:
        return {"status": "unknown", "agree": 0, "of": len(av)}
    agree = sum(1 for r in av if r["bias"] == want)
    against = {r["tf"] for r in av if r["bias"] not in (want, "neutral")}
    if against & {"1w", "1d"}:
        status = "conflict"
    elif agree == len(av):
        status = "aligned"
    else:
        status = "partial"
    return {"status": status, "agree": agree, "of": len(av)}


def analyse(frames: dict, direction: str, trigger_tf: str, trigger_df=None) -> dict | None:
    rows = framework(frames, trigger_tf, trigger_df)
    if sum(1 for r in rows if r.get("available")) < 2:
        return None
    return {"rows": rows, **coherence(direction, rows)}


_TR = {"up": "صاعد", "down": "هابط", "range": "عرضي"}
_BI = {"bull": "شراء", "bear": "بيع", "neutral": "محايد"}
_ST = {"aligned": "متوافقة ✓", "partial": "توافق جزئي", "conflict": "تعارض ✗", "unknown": "غير واضح"}


def lines_ar(m: dict | None) -> list[str]:
    """Short Arabic lines for the Setup Card / Telegram: one per timeframe + the verdict."""
    if not m:
        return []
    from modules.arabic import TF_AR
    out = []
    for r in m["rows"]:
        label = TF_AR.get(r["tf"], r["tf"])
        role = {"bias": "الاتجاه العام", "setup": "السيت اب", "timing": "التوقيت"}[r["role"]]
        out.append(f"{label} ({role}): " + ("لا توجد بيانات" if not r.get("available") else
                   f"{_TR[r['trend']]}، السعر {'فوق' if r['ema'] == 'above' else 'تحت'} EMA50 → {_BI[r['bias']]}"))
    out.append(f"توافق الفريمات: {_ST[m['status']]} ({m['agree']}/{m['of']})")
    return out
