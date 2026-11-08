"""LEVEL SWEEPS: price took a prior high / low (day, week, month, or the Asian range) and closed back inside = the liquidity grab that often reverses (owner 2026-11-06).

Small ones: the previous day's and the Asian range's high / low. Big ones: the previous week's and month's. A sweep is a REVERSAL HINT toward the side it came back from, never an entry by itself;
the alert carries the level, the size class and the 1H close that came back. Fresh only: the sweep candle must be one of the last 3 1H candles (the job runs every 30 minutes).

Needs: 1H candles (the sweep and the reclaim), 1D (previous day, and the month by grouping), 1W (previous week), 15m optional (Asian range). New York clock for the Asian range (19:00-03:00)."""
from __future__ import annotations

import pandas as pd

LOOKBACK = 3   # last N hourly candles


def _idx(df):
    t = pd.to_datetime(df["time"])
    return t.dt.tz_convert("UTC").dt.tz_localize(None) if getattr(t.dt, "tz", None) is not None else t


def _prior_levels(d1: pd.DataFrame, w1: pd.DataFrame | None):
    """{'PDH','PDL','PWH','PWL','PMH','PML'} from COMPLETED periods (the last row of each frame is the running one)."""
    lv = {}
    if d1 is not None and len(d1) >= 3:
        p = d1.iloc[-2]
        lv["PDH"], lv["PDL"] = float(p["high"]), float(p["low"])
        t = _idx(d1)
        cur_m = t.iloc[-1].to_period("M")
        prev = d1[t.dt.to_period("M") == (cur_m - 1)]
        if len(prev) >= 10:
            lv["PMH"], lv["PML"] = float(prev["high"].max()), float(prev["low"].min())
    if w1 is not None and len(w1) >= 3:
        p = w1.iloc[-2]
        lv["PWH"], lv["PWL"] = float(p["high"]), float(p["low"])
    return lv


def _asian_range(m15: pd.DataFrame | None):
    """High / low of the last COMPLETE Asian session (19:00-03:00 New York) in the 15m frame, plus when London (03:00 NY) started after it."""
    if m15 is None or len(m15) < 40:
        return None
    t = pd.to_datetime(m15["time"])
    t = t.dt.tz_localize("UTC") if getattr(t.dt, "tz", None) is None else t.dt.tz_convert("UTC")
    ny = t.dt.tz_convert("America/New_York")
    mins = ny.dt.hour * 60 + ny.dt.minute
    asia = (mins >= 19 * 60) | (mins < 3 * 60)
    last_london = ny[(mins >= 3 * 60) & (mins < 8 * 60)]
    if last_london.empty:
        return None
    day = last_london.iloc[-1].normalize()
    start = day - pd.Timedelta(hours=5)       # 19:00 of the evening before
    end = day + pd.Timedelta(hours=3)         # 03:00
    sel = m15[(ny >= start) & (ny < end) & asia]
    if len(sel) < 8:
        return None
    return {"hi": float(sel["high"].max()), "lo": float(sel["low"].min()), "after": end.tz_convert("UTC").tz_localize(None)}


def find(symbol: str, h1: pd.DataFrame, d1=None, w1=None, m15=None) -> list:
    """[{id, symbol, level_name, level, size, direction, side_swept, close, when}] direction = the reversal hint (bearish after a high is swept and rejected, bullish after a low)."""
    if h1 is None or len(h1) < LOOKBACK + 5:
        return []
    out = []
    levels = {k: (v, "big" if k[1] in "WM" else "small") for k, v in _prior_levels(d1, w1).items()}
    ar = _asian_range(m15)
    t1 = _idx(h1)
    if ar:
        for nm, key in (("ASIA-H", "hi"), ("ASIA-L", "lo")):
            # only meaningful after the Asian session ended
            if t1.iloc[-1] > ar["after"]:
                levels[nm] = (ar[key], "small")
    last = h1.iloc[-LOOKBACK:]
    lt = t1.iloc[-LOOKBACK:]
    for nm, (lvl, size) in levels.items():
        is_high = nm.endswith("H")
        for i in range(len(last)):
            row = last.iloc[i]
            hi, lo, cl = float(row["high"]), float(row["low"]), float(row["close"])
            swept = hi > lvl and cl < lvl if is_high else lo < lvl and cl > lvl
            if swept:
                out.append({"id": f"sweep|{symbol}|{nm}|{lt.iloc[i]:%Y%m%d%H}", "symbol": symbol, "level_name": nm, "level": lvl, "size": size, "direction": "bearish" if is_high else "bullish",
                            "side_swept": "high" if is_high else "low", "close": cl, "extreme": hi if is_high else lo, "when": str(lt.iloc[i])})
                break
    out.sort(key=lambda a: (a["size"] != "big", a["when"]))
    return out


def scan(symbols, fetch) -> list:
    res = []
    for s in symbols:
        try:
            res += find(s, fetch(s, "1h"), fetch(s, "1d"), fetch(s, "1w"), fetch(s, "15m"))
        except Exception:
            continue
    return res


NAMES = {"PDH": ("previous day high", "قمة أمس"), "PDL": ("previous day low", "قاع أمس"), "PWH": ("previous WEEK high", "قمة الأسبوع اللي فات"), "PWL": ("previous WEEK low", "قاع الأسبوع اللي فات"),
         "PMH": ("previous MONTH high", "قمة الشهر اللي فات"), "PML": ("previous MONTH low", "قاع الشهر اللي فات"), "ASIA-H": ("Asian range high", "قمة نطاق آسيا"), "ASIA-L": ("Asian range low", "قاع نطاق آسيا")}


def format_sweep(a: dict, ar: bool = True) -> str:
    import html
    esc = html.escape
    nm = NAMES.get(a["level_name"], (a["level_name"], a["level_name"]))[0 if not ar else 1]
    up = a["direction"] == "bullish"
    big = a["size"] == "big"
    return (f"💧 <b>{'سحب سيولة' if ar else 'Liquidity sweep'} {'كبير' if (big and ar) else 'big' if big else ('صغير' if ar else 'small')}</b> {'🟢' if up else '🔴'} <b>{esc(a['symbol'])}</b>\n"
            f"{'السعر سحب' if ar else 'Price swept'} {esc(nm)} ({a['level']:.6g}) {'ورجع قفل جواه' if ar else 'and closed back inside'} ({a['close']:.6g}) → "
            f"{'تلميح انعكاس ' + ('صاعد' if up else 'هابط') if ar else 'reversal hint: ' + ('up' if up else 'down')}\n"
            f"<i>{'تلميح مش إشارة دخول؛ استنى تأكيد (CISD / كسر هيكل).' if ar else 'A hint, not an entry: wait for confirmation (CISD / structure break).'}</i>")
