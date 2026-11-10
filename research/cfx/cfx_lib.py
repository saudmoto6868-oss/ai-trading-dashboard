#!/usr/bin/env python3
"""CFX compute library — real values only, no fabrication."""
from __future__ import annotations

import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "/workspace/indicator_research/fused_osc")
sys.path.insert(0, "/workspace/cfx")
from fused_oscillator import (
    COOLDOWN_BARS_15M,
    GOLDEN_POCKET,
    HTF_FAST,
    HTF_SLOW,
    MIN_LEG_ATR,
    OTE,
    SWING_L,
    add_oscillators,
    build_location_and_div,
    confirmed_swings,
    ema,
    flatten_yf,
    in_killzone,
    wilder_atr,
)
from cfx_pipeline import (
    ELLIOTT_DRAW,
    FVG_MAX_AGE as PIPE_FVG_MAX_AGE,
    NEWS_FEED,
    RR1_MIN as PIPE_RR1_MIN,
    SPREAD_USD,
    detect_cisd_all,
    detect_htf_zones,
    merge_momentum_hook,
    recast_ob_volume_share,
    run_pipeline,
    session_cairo_hint,
    session_flags as ny_session_flags,
    summarize_backtest,
    zigzag_elliott,
)

DATA = Path("/workspace/cfx/data")
CAIRO = "Africa/Cairo"
NY = "America/New_York"

# Display sessions: see cfx_pipeline.SESS_WINDOWS (America/New_York).
SWING_STRUCT = 3
EQ_TOL_ATR = 0.10
EQ_CONFIRM = 3
LIQ_NEAR_ATR = 2.0
SL_BUF_ATR = 0.15
RR1_MIN = 1.5  # gate only; matches cfx_pipeline.RR1_MIN
XPIX_HIDE_ATR = 15.0
XPIX_EXT = 30
FVG_MIN_ATR = 0.30
FVG_MAX_AGE = 30
OB_DISP_ATR = 1.50
OB_MAX_AGE = 80
IFVG_MAX_AGE = 50
BRK_MAX_AGE = 80
DIV_LOOK = 80
DISPLAY_SESSIONS = 3  # readable window; history still used for indicators


def load_csv(name: str) -> pd.DataFrame:
    df = pd.read_csv(DATA / name, index_col=0, parse_dates=True)
    df.index = pd.to_datetime(df.index, utc=True).tz_convert(NY)
    df = df.rename(columns=str.lower)
    df = df[~df.index.duplicated(keep="last")].sort_index()
    return df


def resample_4h(df1h: pd.DataFrame) -> pd.DataFrame:
    agg = {"open": "first", "high": "max", "low": "min", "close": "last"}
    if "volume" in df1h.columns:
        agg["volume"] = "sum"
    return df1h.resample("4h", offset="2h", label="left", closed="left").agg(agg).dropna(subset=["open", "close"])


def session_date_et(ts: pd.Timestamp) -> pd.Timestamp:
    t = ts.tz_convert(NY)
    return (t + pd.Timedelta(days=1)).normalize() if t.hour >= 18 else t.normalize()


def cairo(ts: pd.Timestamp) -> pd.Timestamp:
    return ts.tz_convert(CAIRO)


def cairo_label(ts: pd.Timestamp) -> str:
    return cairo(ts).strftime("%d %b %H:%M")


def last_n_session_start(df: pd.DataFrame, n: int) -> pd.Timestamp:
    dates = [session_date_et(t) for t in df.index]
    uniq = list(dict.fromkeys(dates))
    cut = uniq[-n] if len(uniq) > n else uniq[0]
    for t, d in zip(df.index, dates):
        if d >= cut:
            return t
    return df.index[0]


def htf_bias_frame(htf: pd.DataFrame) -> pd.DataFrame:
    x = htf.copy()
    x["ema_f"] = ema(x["close"], HTF_FAST)
    x["ema_s"] = ema(x["close"], HTF_SLOW)
    x["bull"] = (x["close"].shift(1) > x["ema_s"].shift(1)) & (x["ema_f"].shift(1) > x["ema_s"].shift(1))
    x["bear"] = (x["close"].shift(1) < x["ema_s"].shift(1)) & (x["ema_f"].shift(1) < x["ema_s"].shift(1))
    return x


def attach_htf(d15: pd.DataFrame, d1h: pd.DataFrame, d4h: pd.DataFrame, d1d: pd.DataFrame | None = None) -> pd.DataFrame:
    out = d15.copy()
    a1 = htf_bias_frame(d1h)[["bull", "bear"]].reindex(out.index, method="ffill")
    a4 = htf_bias_frame(d4h)[["bull", "bear"]].reindex(out.index, method="ffill")
    out["htf_1h_bull"] = a1["bull"].fillna(False)
    out["htf_1h_bear"] = a1["bear"].fillna(False)
    out["htf_4h_bull"] = a4["bull"].fillna(False)
    out["htf_4h_bear"] = a4["bear"].fillna(False)
    if d1d is not None and len(d1d):
        ad = htf_bias_frame(d1d)[["bull", "bear"]].reindex(out.index, method="ffill")
        out["htf_d_bull"] = ad["bull"].fillna(False)
        out["htf_d_bear"] = ad["bear"].fillna(False)
    else:
        out["htf_d_bull"] = False
        out["htf_d_bear"] = False
    # Veto only when daily AND 4H are both against the candidate side.
    out["veto_buy"] = out["htf_d_bear"] & out["htf_4h_bear"]
    out["veto_sell"] = out["htf_d_bull"] & out["htf_4h_bull"]
    # Alignment flag (not a veto): 4H + 1H + current EMA stack.
    ef, es = ema(out["close"], HTF_FAST), ema(out["close"], HTF_SLOW)
    out["m15_bull"] = (out["close"] > es) & (ef > es)
    out["m15_bear"] = (out["close"] < es) & (ef < es)
    out["htf_bull"] = out["htf_4h_bull"] & out["htf_1h_bull"] & out["m15_bull"]
    out["htf_bear"] = out["htf_4h_bear"] & out["htf_1h_bear"] & out["m15_bear"]
    return out


def last_closed_bar(df: pd.DataFrame, now: pd.Timestamp, minutes: int):
    if df.empty:
        return None
    ts, row = df.index[-1], df.iloc[-1]
    if now < ts + pd.Timedelta(minutes=minutes):
        if len(df) < 2:
            return None
        ts, row = df.index[-2], df.iloc[-2]
    return {"ts": ts, "high": float(row["high"]), "low": float(row["low"]),
            "open": float(row["open"]), "close": float(row["close"])}


def xpix_edge(hi, lo, close, atr, prev=0):
    rng = hi - lo
    if rng <= 0 or not np.isfinite(atr) or atr <= 0:
        return None
    if abs(close - hi) > XPIX_HIDE_ATR * atr and abs(close - lo) > XPIX_HIDE_ATR * atr:
        return None
    side = prev
    if side == 0:
        side = 1 if abs(close - hi) <= abs(close - lo) else -1
    elif side == 1:
        if close < lo + 0.30 * rng:
            side = -1
    else:
        if close > lo + 0.70 * rng:
            side = 1
    return {"side": side, "price": hi if side == 1 else lo, "high": hi, "low": lo}


def session_flags(ts: pd.Timestamp) -> dict:
    """Single clock: America/New_York windows from cfx_pipeline.SESS_WINDOWS."""
    return ny_session_flags(ts)


def session_segments(index, key):
    runs, start = [], None
    for i, ts in enumerate(index):
        on = session_flags(ts)[key]
        if on and start is None:
            start = i
        elif not on and start is not None:
            runs.append((start, i - 1))
            start = None
    if start is not None:
        runs.append((start, len(index) - 1))
    return runs


def latest_session_hl(df, vis_start, vis_end, key):
    runs = session_segments(df.index[vis_start:vis_end + 1], key)
    if not runs:
        return None
    a, b = runs[-1]
    a, b = a + vis_start, b + vis_start
    sl = df.iloc[a:b + 1]
    return {
        "start": a, "end": b,
        "high": float(sl["high"].max()), "low": float(sl["low"].min()),
        "hi_i": int(a + sl["high"].values.argmax()),
        "lo_i": int(a + sl["low"].values.argmin()),
        "open": float(sl["open"].iloc[0]),
    }


def all_session_boxes(df, vis_start, vis_end):
    """Every Asia/London/NY run in the visible window, as time × high/low boxes."""
    out = []
    for key in ("asia", "london", "ny"):
        for a, b in session_segments(df.index[vis_start:vis_end + 1], key):
            a2, b2 = a + vis_start, b + vis_start
            sl = df.iloc[a2:b2 + 1]
            if sl.empty:
                continue
            out.append({
                "key": key,
                "start": int(a2),
                "end": int(b2),
                "high": float(sl["high"].max()),
                "low": float(sl["low"].min()),
                "hi_i": int(a2 + sl["high"].values.argmax()),
                "lo_i": int(a2 + sl["low"].values.argmin()),
                "open": float(sl["open"].iloc[0]),
            })
    return out


def session_hl_swept(df, box, last_i):
    """True when price traded beyond that session's high/low after the session ended."""
    after = df.iloc[int(box["end"]) + 1: last_i + 1]
    if after.empty:
        return {"high": False, "low": False, "active": True}
    return {
        "high": bool(float(after["high"].max()) > box["high"]),
        "low": bool(float(after["low"].min()) < box["low"]),
        "active": False,
    }


def detect_bos_choch(df, left):
    n = len(df)
    high, low, close = (df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    sh, sl = confirmed_swings(high, low, left)
    conf_at = {}
    for i in sh:
        if i + left < n:
            conf_at.setdefault(i + left, []).append(("h", i))
    for i in sl:
        if i + left < n:
            conf_at.setdefault(i + left, []).append(("l", i))
    events, last_sh, last_sl, struct_dir = [], None, None, 0
    for t in range(n):
        for kind, i in conf_at.get(t, []):
            if kind == "h":
                last_sh = i
            else:
                last_sl = i
        if t == 0:
            continue
        if last_sh is not None and close[t] > high[last_sh] and close[t - 1] <= high[last_sh]:
            kind = "CHoCH" if struct_dir == -1 else "BOS"
            events.append({"i": t, "kind": kind, "dir": 1, "level": float(high[last_sh]), "swing_i": last_sh})
            struct_dir = 1
        elif last_sl is not None and close[t] < low[last_sl] and close[t - 1] >= low[last_sl]:
            kind = "CHoCH" if struct_dir == 1 else "BOS"
            events.append({"i": t, "kind": kind, "dir": -1, "level": float(low[last_sl]), "swing_i": last_sl})
            struct_dir = -1
    return events, struct_dir, sh, sl


def find_eq(df, sh, sl, left, last_i):
    high, low = df["high"].to_numpy(dtype=float), df["low"].to_numpy(dtype=float)
    close, atr = float(df["close"].iloc[last_i]), float(df["atr"].iloc[last_i])
    n = last_i + 1
    hs = [i for i in sh if i + left <= last_i]
    ls = [i for i in sl if i + left <= last_i]
    out = {"eqh": None, "eql": None}
    if not np.isfinite(atr) or atr <= 0:
        return out

    def sweep_bar(level, side, from_i):
        if side == "h":
            hits = np.where(high[from_i:n] > level)[0]
        else:
            hits = np.where(low[from_i:n] < level)[0]
        if len(hits) == 0:
            return None
        return int(from_i + hits[0])

    if len(hs) >= 2 and (last_i - hs[-1]) >= EQ_CONFIRM and abs(high[hs[-2]] - high[hs[-1]]) <= EQ_TOL_ATR * atr:
        lvl = float(max(high[hs[-2]], high[hs[-1]]))
        sw = sweep_bar(lvl, "h", max(hs[-2], hs[-1]) + 1)
        out["eqh"] = {"level": lvl, "i1": hs[-2], "i2": hs[-1], "swept": sw is not None,
                      "sweep_i": sw, "near": abs(close - lvl) <= LIQ_NEAR_ATR * atr}
    if len(ls) >= 2 and (last_i - ls[-1]) >= EQ_CONFIRM and abs(low[ls[-2]] - low[ls[-1]]) <= EQ_TOL_ATR * atr:
        lvl = float(min(low[ls[-2]], low[ls[-1]]))
        sw = sweep_bar(lvl, "l", max(ls[-2], ls[-1]) + 1)
        out["eql"] = {"level": lvl, "i1": ls[-2], "i2": ls[-1], "swept": sw is not None,
                      "sweep_i": sw, "near": abs(close - lvl) <= LIQ_NEAR_ATR * atr}
    return out


def prior_day_hl(df15, d1d, last_ts, last_i, atr, close):
    last_daily = None
    for ts, row in d1d.iterrows():
        if session_date_et(ts) < session_date_et(last_ts):
            last_daily = (ts, float(row["high"]), float(row["low"]), float(row["close"]))
    if last_daily is None:
        return {}
    _, pdh, pdl, pdc = last_daily
    sess = session_date_et(last_ts)
    day_hi = day_lo = None
    for j in range(last_i + 1):
        if session_date_et(df15.index[j]) == sess:
            h, l = float(df15["high"].iloc[j]), float(df15["low"].iloc[j])
            day_hi = h if day_hi is None else max(day_hi, h)
            day_lo = l if day_lo is None else min(day_lo, l)
    return {
        "pdh": pdh, "pdl": pdl, "pdc": pdc, "pdh_date": str(last_daily[0]),
        "pdh_swept": day_hi is not None and day_hi >= pdh,
        "pdl_swept": day_lo is not None and day_lo <= pdl,
        "pdh_near": abs(close - pdh) <= LIQ_NEAR_ATR * atr if atr > 0 else False,
        "pdl_near": abs(close - pdl) <= LIQ_NEAR_ATR * atr if atr > 0 else False,
        "day_hi": day_hi, "day_lo": day_lo,
        "pivot": (pdh + pdl + pdc) / 3.0,
    }


def latest_impulse(df, sh, sl, left, last_i):
    high, low = df["high"].to_numpy(dtype=float), df["low"].to_numpy(dtype=float)
    atr = float(df["atr"].iloc[last_i])
    hs = [i for i in sh if i + left <= last_i]
    ls = [i for i in sl if i + left <= last_i]
    if not hs or not ls or not np.isfinite(atr) or atr <= 0:
        return None
    last_h, last_l = hs[-1], ls[-1]
    if last_h > last_l:
        side, i0, i1 = "bull", last_l, last_h
        start, end = float(low[i0]), float(high[i1])
        leg = end - start
    elif last_l > last_h:
        side, i0, i1 = "bear", last_h, last_l
        start, end = float(high[i0]), float(low[i1])
        leg = start - end
    else:
        return None
    if leg < MIN_LEG_ATR * atr:
        return None
    px = float(df["close"].iloc[last_i])
    ratios = (0.0, 0.382, 0.5, 0.618, 0.65, 0.705, 0.786, 0.79, 0.886, 1.0)
    ext_r = (0.27, 0.62, 1.0)
    if side == "bull":
        ret = (end - px) / leg
        lvl = {r: end - r * leg for r in ratios}
        exts = {-r: end + r * leg for r in ext_r}
    else:
        ret = (px - end) / leg
        lvl = {r: end + r * leg for r in ratios}
        exts = {-r: end - r * leg for r in ext_r}
    live = 0.0 < ret < 1.0
    return {"side": side, "i0": i0, "i1": i1, "start": start, "end": end, "leg": leg,
            "retracement": ret, "levels": lvl, "extensions": exts,
            "live": live, "displaced": True,
            "in_ote": bool(live and OTE[0] <= ret <= OTE[1]),
            "in_pocket": bool(live and GOLDEN_POCKET[0] <= ret <= GOLDEN_POCKET[1])}


def detect_fvgs(df, last_i):
    h, l, c = (df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    atr = df["atr"].to_numpy(dtype=float)
    n = last_i + 1
    out = []
    for i in range(2, n):
        a = atr[i] if np.isfinite(atr[i]) else np.nan
        if not np.isfinite(a) or a <= 0:
            continue
        if l[i] > h[i - 2] and (l[i] - h[i - 2]) >= FVG_MIN_ATR * a:
            lo, hi = float(h[i - 2]), float(l[i])
            hits = np.where(c[i + 1:n] < lo)[0]
            fill_i = int(i + 1 + hits[0]) if len(hits) else None
            out.append({"i": i, "lo": lo, "hi": hi, "side": "bull", "filled": fill_i is not None,
                        "fill_i": fill_i, "age": n - 1 - i})
        elif h[i] < l[i - 2] and (l[i - 2] - h[i]) >= FVG_MIN_ATR * a:
            lo, hi = float(h[i]), float(l[i - 2])
            hits = np.where(c[i + 1:n] > hi)[0]
            fill_i = int(i + 1 + hits[0]) if len(hits) else None
            out.append({"i": i, "lo": lo, "hi": hi, "side": "bear", "filled": fill_i is not None,
                        "fill_i": fill_i, "age": n - 1 - i})
    return out


def detect_ifvg(fvgs, df, last_i):
    """A filled FVG that price later reclaimed — the zone flips (IFVG). Valid until closed through again."""
    c = df["close"].to_numpy(dtype=float)
    n = last_i + 1
    out = []
    for g in fvgs:
        if not g["filled"]:
            continue
        i, lo, hi, side = g["i"], g["lo"], g["hi"], g["side"]
        if n - 1 - i > IFVG_MAX_AGE:
            continue
        # fill bar: first close through
        if side == "bull":
            fills = np.where(c[i + 1:n] < lo)[0]
            if len(fills) == 0:
                continue
            fbar = i + 1 + int(fills[0])
            recs = np.where(c[fbar + 1:n] > hi)[0]  # reclaim back above = bull IFVG used? 
            # After bull FVG is filled down, it becomes bearish IFVG (resistance) until close back above hi
            if np.any(c[fbar + 1:n] > hi):
                continue  # re-invalidated
            out.append({"i": i, "lo": lo, "hi": hi, "side": "bear", "flip_i": fbar, "age": n - 1 - i, "src": "bull FVG"})
        else:
            fills = np.where(c[i + 1:n] > hi)[0]
            if len(fills) == 0:
                continue
            fbar = i + 1 + int(fills[0])
            if np.any(c[fbar + 1:n] < lo):
                continue
            out.append({"i": i, "lo": lo, "hi": hi, "side": "bull", "flip_i": fbar, "age": n - 1 - i, "src": "bear FVG"})
    return out


def detect_order_blocks(df, events, last_i):
    """Last opposite candle before a BOS/CHoCH, still valid (no close through)."""
    o, h, l, c, v = (df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close", "volume"))
    atr = df["atr"].to_numpy(dtype=float)
    n = last_i + 1
    obs = []
    for ev in events:
        j, direc = ev["i"], ev["dir"]
        # displacement check vs prior swing
        swing_i = ev.get("swing_i")
        if swing_i is None:
            continue
        if direc == 1:
            # bullish break: last down candle before the lowest low in pivot->break
            s = swing_i + int(np.argmin(l[swing_i:j + 1]))
            if c[j] - l[s] < OB_DISP_ATR * (atr[j] if np.isfinite(atr[j]) else 0):
                continue
            k = None
            for x in range(s, max(s - 8, -1), -1):
                if c[x] < o[x]:
                    k = x
                    break
            if k is None:
                k = s
            zlo, zhi = float(l[k]), float(h[k])
            hits = np.where(c[j + 1:n] < zlo)[0]
            mit = int(j + 1 + hits[0]) if len(hits) else None
        else:
            s = swing_i + int(np.argmax(h[swing_i:j + 1]))
            if h[s] - c[j] < OB_DISP_ATR * (atr[j] if np.isfinite(atr[j]) else 0):
                continue
            k = None
            for x in range(s, max(s - 8, -1), -1):
                if c[x] > o[x]:
                    k = x
                    break
            if k is None:
                k = s
            zlo, zhi = float(l[k]), float(h[k])
            hits = np.where(c[j + 1:n] > zhi)[0]
            mit = int(j + 1 + hits[0]) if len(hits) else None
        win = v[max(0, k - 19):k + 1]
        tot = float(win.sum()) if win.size else 0.0
        vol = float(v[k])
        pct = 100.0 * vol / tot if tot > 0 else 0.0
        touched = bool((l[j + 1:n] <= zhi).any() and (h[j + 1:n] >= zlo).any()) if j + 1 < n else False
        obs.append({"i": int(k), "break_i": int(j), "lo": zlo, "hi": zhi, "side": "bull" if direc == 1 else "bear",
                    "vol": vol, "pct": pct, "tested": touched, "age": n - 1 - j, "mitigated_i": mit})
    # unique by bar, keep latest
    seen, uniq = set(), []
    for ob in reversed(obs):
        if ob["i"] in seen:
            continue
        seen.add(ob["i"])
        uniq.append(ob)
    return list(reversed(uniq))


def detect_breakers(df, sh, sl, left, last_i):
    """Sweep -> MSS, last opposite-direction candle before the sweep. Valid if not closed through after MSS."""
    o, h, l, c = (df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    n = last_i + 1
    hs = [i for i in sh if i + left <= last_i]
    ls = [i for i in sl if i + left <= last_i]
    out = []
    # bullish breaker: sweep of a swing low, then close above prior swing high
    for li in ls:
        lvl = float(l[li])
        # first sweep bar after confirmation
        for j in range(li + left, n):
            if l[j] < lvl and c[j] > lvl:
                prior_h = [i for i in hs if i < j]
                if not prior_h:
                    break
                hh = float(h[prior_h[-1]])
                m = next((x for x in range(j + 1, n) if c[x] > hh), None)
                if m is None:
                    break
                k = next((x for x in range(j - 1, max(j - 16, -1), -1) if c[x] > o[x]), None)
                if k is None:
                    break
                blo, bhi = float(l[k]), float(h[k])
                hits = np.where(c[m + 1:n] < blo)[0]
                mit = int(m + 1 + hits[0]) if len(hits) else None
                out.append({"i": int(k), "sweep_i": j, "mss_i": m, "lo": blo, "hi": bhi, "side": "bull",
                            "sweep_lvl": lvl, "mitigated_i": mit})
                break
    for hi in hs:
        lvl = float(h[hi])
        for j in range(hi + left, n):
            if h[j] > lvl and c[j] < lvl:
                prior_l = [i for i in ls if i < j]
                if not prior_l:
                    break
                ll = float(l[prior_l[-1]])
                m = next((x for x in range(j + 1, n) if c[x] < ll), None)
                if m is None:
                    break
                k = next((x for x in range(j - 1, max(j - 16, -1), -1) if c[x] < o[x]), None)
                if k is None:
                    break
                blo, bhi = float(l[k]), float(h[k])
                hits = np.where(c[m + 1:n] > bhi)[0]
                mit = int(m + 1 + hits[0]) if len(hits) else None
                out.append({"i": int(k), "sweep_i": j, "mss_i": m, "lo": blo, "hi": bhi, "side": "bear",
                            "sweep_lvl": lvl, "mitigated_i": mit})
                break
    # last few unique
    seen, uniq = set(), []
    for b in reversed(out):
        key = (b["i"], b["side"])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(b)
    return list(reversed(uniq))


def rsi14(close: pd.Series) -> pd.Series:
    d = close.diff()
    au = d.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    ad = (-d).clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    rs = au / ad.replace(0, np.nan)
    return (100 - 100 / (1 + rs)).fillna(50.0)


def macd_line(close: pd.Series) -> pd.Series:
    return close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()


def detect_divergences(df, sh, sl, left, last_i):
    """Regular divergences at confirmed swings: RSI, MACD, Volume.

    Shared function for chart dots and any signal path that needs divergence.
    Oscillators: classic regular div (price LL + osc HL, or price HH + osc LH).
    Volume: lower second volume is non-confirmation on BOTH sides
    (price LL + smaller vol = bull vol-div; price HH + smaller vol = bear vol-div).
    """
    n = last_i + 1
    high, low, close = (df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    vol = df["volume"].to_numpy(dtype=float)
    rsi = rsi14(df["close"]).to_numpy(dtype=float)
    macd = macd_line(df["close"]).to_numpy(dtype=float)
    hs = [i for i in sh if i + left <= last_i]
    ls = [i for i in sl if i + left <= last_i]
    out = []

    def pair(idxs, price, osc, side, name, osc_name):
        recent = [i for i in idxs if last_i - i <= DIV_LOOK]
        if len(recent) < 2:
            return
        a, b = recent[-2], recent[-1]
        if b - a < 4:
            return
        p1, p2, o1, o2 = price[a], price[b], osc[a], osc[b]
        if not np.isfinite(o1) or not np.isfinite(o2):
            return
        # Volume: non-confirmation is a smaller second volume. Oscillators: classic regular div.
        vol = (osc_name == "Vol")
        if side == "bear" and p2 > p1 and o2 < o1:
            out.append({"i": b, "i1": a, "name": osc_name, "side": "bear", "p1": float(p1), "p2": float(p2)})
        if side == "bull" and p2 < p1 and ((o2 < o1) if vol else (o2 > o1)):
            out.append({"i": b, "i1": a, "name": osc_name, "side": "bull", "p1": float(p1), "p2": float(p2)})

    pair(hs, high, rsi, "bear", "rsi", "RSI")
    pair(ls, low, rsi, "bull", "rsi", "RSI")
    pair(hs, high, macd, "bear", "macd", "MACD")
    pair(ls, low, macd, "bull", "macd", "MACD")
    pair(hs, high, vol, "bear", "vol", "Vol")
    pair(ls, low, vol, "bull", "vol", "Vol")
    return out


def volume_profile(df, start, end, bins=40, va=0.70):
    """Session/window VP from OHLCV: uniform volume across each bar's range."""
    sl = df.iloc[start:end + 1]
    lo, hi = float(sl["low"].min()), float(sl["high"].max())
    if not np.isfinite(lo) or hi <= lo:
        return None
    edges = np.linspace(lo, hi, bins + 1)
    vol = np.zeros(bins)
    for _, r in sl.iterrows():
        a, b, v = float(r["low"]), float(r["high"]), float(r.get("volume", 0) or 0)
        if v <= 0 or b <= a:
            continue
        # distribute volume across overlapping bins
        i0, i1 = np.searchsorted(edges, a, side="right") - 1, np.searchsorted(edges, b, side="left") - 1
        i0, i1 = max(0, i0), min(bins - 1, max(i0, i1))
        share = v / (i1 - i0 + 1)
        vol[i0:i1 + 1] += share
    if vol.sum() <= 0:
        return None
    poc_i = int(vol.argmax())
    poc = 0.5 * (edges[poc_i] + edges[poc_i + 1])
    target = va * vol.sum()
    s, e = poc_i, poc_i
    acc = vol[poc_i]
    while acc < target and (s > 0 or e < bins - 1):
        left = vol[s - 1] if s > 0 else -1
        right = vol[e + 1] if e < bins - 1 else -1
        if right > left:
            e += 1
            acc += vol[e]
        else:
            s -= 1
            acc += vol[s]
    return {"poc": float(poc), "val": float(edges[s]), "vah": float(edges[e + 1]),
            "lo": lo, "hi": hi, "poc_vol": float(vol[poc_i])}


def session_vwap(df, last_i):
    sess = session_date_et(df.index[last_i])
    typ = (df["high"] + df["low"] + df["close"]) / 3.0
    pv = typ * df["volume"].replace(0, np.nan)
    num = den = 0.0
    series = np.full(last_i + 1, np.nan)
    for j in range(last_i + 1):
        if session_date_et(df.index[j]) != sess:
            continue
        v = float(df["volume"].iloc[j])
        if v <= 0:
            series[j] = num / den if den else np.nan
            continue
        num += float(typ.iloc[j]) * v
        den += v
        series[j] = num / den if den else np.nan
    return float(series[last_i]) if den else None, series


def ichimoku_state(df, last_i):
    c = df["close"]
    h, l = df["high"], df["low"]
    tenkan = (h.rolling(9).max() + l.rolling(9).min()) / 2
    kijun = (h.rolling(26).max() + l.rolling(26).min()) / 2
    span_a = (tenkan + kijun) / 2
    span_b = (h.rolling(52).max() + l.rolling(52).min()) / 2
    # cloud at now was formed 26 bars ago
    i = last_i - 26
    if i < 0 or not np.isfinite(span_a.iloc[i]) or not np.isfinite(span_b.iloc[i]):
        return None
    sa, sb = float(span_a.iloc[i]), float(span_b.iloc[i])
    px = float(c.iloc[last_i])
    cloud_top, cloud_bot = max(sa, sb), min(sa, sb)
    if px > cloud_top:
        pos = "above cloud"
        bias = "bull"
    elif px < cloud_bot:
        pos = "below cloud"
        bias = "bear"
    else:
        pos = "inside cloud"
        bias = "neutral"
    tk, kj = float(tenkan.iloc[last_i]), float(kijun.iloc[last_i])
    return {"pos": pos, "bias": bias, "span_a": sa, "span_b": sb, "tenkan": tk, "kijun": kj,
            "tk_kj": "bull" if tk > kj else ("bear" if tk < kj else "neutral")}


def detect_cisd(df, sh, sl, left, last_i, lookback=40):
    """Latest CISD events (both sides), even if a bit stale — used for school + optional thin level."""
    o, h, l, c = (df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    n = last_i + 1
    hs = [i for i in sh if i + left <= last_i]
    ls = [i for i in sl if i + left <= last_i]
    evs = []
    # bullish: sweep swing low, down-close series, body close above open of first down candle
    start0 = max(left + 1, n - lookback)
    # find most recent sweep of a low
    for li in reversed(ls):
        if li < n - lookback - 10:
            break
        lvl = float(l[li])
        j = next((b for b in range(li + left, n) if l[b] < lvl), None)
        if j is None:
            continue
        e = j + int(np.argmin(l[j:min(n, j + 8)])) if j < n else j
        m = e
        while m >= 0 and not c[m] < o[m]:
            m -= 1
        if m < 1:
            continue
        s0 = m
        while s0 - 1 >= 0 and c[s0 - 1] < o[s0 - 1]:
            s0 -= 1
        cl = float(o[s0])
        conf = next((b for b in range(e + 1, n) if c[b] > cl and c[b] > o[b]), None)
        if conf is None:
            continue
        evs.append({"side": "bull", "level": cl, "sweep_i": int(j), "conf_i": int(conf),
                    "start_i": int(s0), "age": n - 1 - conf})
        break
    for hi in reversed(hs):
        if hi < n - lookback - 10:
            break
        lvl = float(h[hi])
        j = next((b for b in range(hi + left, n) if h[b] > lvl), None)
        if j is None:
            continue
        e = j + int(np.argmax(h[j:min(n, j + 8)])) if j < n else j
        m = e
        while m >= 0 and not c[m] > o[m]:
            m -= 1
        if m < 1:
            continue
        s0 = m
        while s0 - 1 >= 0 and c[s0 - 1] > o[s0 - 1]:
            s0 -= 1
        cl = float(o[s0])
        conf = next((b for b in range(e + 1, n) if c[b] < cl and c[b] < o[b]), None)
        if conf is None:
            continue
        evs.append({"side": "bear", "level": cl, "sweep_i": int(j), "conf_i": int(conf),
                    "start_i": int(s0), "age": n - 1 - conf})
        break
    return evs


def detect_smt(df, dxy, sh, sl, left, last_i):
    if dxy is None or dxy.empty:
        return None
    al = dxy[["high", "low", "close"]].reindex(df.index, method="ffill")
    if al["high"].isna().all():
        return None
    hs = [i for i in sh if i + left <= last_i]
    ls = [i for i in sl if i + left <= last_i]
    out = {"bear": False, "bull": False, "note": None}
    if len(hs) >= 2:
        a, b = hs[-2], hs[-1]
        g_hh = float(df["high"].iloc[b]) > float(df["high"].iloc[a])
        # inverted: DXY lower-high or flat while gold HH is bearish SMT (DXY should confirm gold weakness with a higher high in DXY)
        d_hh = float(al["high"].iloc[b]) > float(al["high"].iloc[a])
        if g_hh and not d_hh:
            out["bear"] = True
            out["note"] = "Gold HH not confirmed by DXY HH"
            out["x1"], out["x2"] = a, b
            out["y1"], out["y2"] = float(df["high"].iloc[a]), float(df["high"].iloc[b])
    if len(ls) >= 2:
        a, b = ls[-2], ls[-1]
        g_ll = float(df["low"].iloc[b]) < float(df["low"].iloc[a])
        d_ll = float(al["low"].iloc[b]) < float(al["low"].iloc[a])
        if g_ll and not d_ll:
            out["bull"] = True
            # prefer most recent
            if not out["bear"] or b >= out.get("x2", 0):
                out["note"] = "Gold LL not confirmed by DXY LL"
                out["x1"], out["x2"] = a, b
                out["y1"], out["y2"] = float(df["low"].iloc[a]), float(df["low"].iloc[b])
    return out


@dataclass
class Trade:
    signal_i: int
    fill_i: int
    close_i: int | None
    side: str
    entry: float
    sl: float
    tp1: float
    tp2: float
    rr1: float
    rr2: float
    atr: float
    outcome: str
    reason: str
    schools: list
    invalidation: str
    cost_R: float = 0.0
    tp1_name: str = ""
    tp2_name: str = ""
    limit: float = 0.0
    poi_kind: str = ""
    weak_alt: str = ""
    why_lines: list = None


def _schools_at(df, i, side):
    r = df.iloc[i]
    S = []
    bull = side == "buy"
    def add(cond, name):
        if bool(cond):
            S.append(name)
    add(r.get("htf_4h_bull") if bull else r.get("htf_4h_bear"), "4H bias")
    add(r.get("htf_1h_bull") if bull else r.get("htf_1h_bear"), "1H bias")
    add(r.get("m15_bull") if bull else r.get("m15_bear"), "15m trend")
    add(r.get("in_ote"), "OTE")
    add(r.get("in_pocket"), "Golden pocket")
    add(r.get("near_fvg"), "FVG")
    add(r.get("after_sweep"), "Liquidity sweep")
    add(r.get("bull_div") if bull else r.get("bear_div"), "Osc divergence")
    add(r.get("hook_buy") if bull else r.get("hook_sell"), "Fused hook")
    add(r.get("stoch14_ok_buy") if bull else r.get("stoch14_ok_sell"), "Stoch(14) align")
    add(r.get("in_kz"), "Killzone")
    return S


def build_fused(d15):
    """Attach merged momentum hook + location flags. Signals themselves come from run_pipeline."""
    out = merge_momentum_hook(d15)
    out = build_location_and_div(out)
    kz = pd.Series([in_killzone(t) for t in out.index], index=out.index)
    out["in_kz"] = kz
    # Placeholder; overwritten by run_pipeline so dots match trades.
    if "sig_buy" not in out:
        out["sig_buy"] = False
        out["sig_sell"] = False
    return out


def build_trades(df, sh, sl, left, events=None, fvgs=None, obs=None, brks=None, raw1d=None):
    """Sequential pipeline wrapper. Prefer run_pipeline via build_bundle."""
    trades, out = run_pipeline(
        df, events or [], sh, sl, left,
        fvgs or [], obs or [], brks or [], raw1d=raw1d,
        make_impulse=latest_impulse, find_eq=find_eq,
        prior_day_hl=prior_day_hl, volume_profile=volume_profile,
    )
    return trades, out



def pa_candle(df, last_i):
    o, h, l, c = (float(df[k].iloc[last_i]) for k in ("open", "high", "low", "close"))
    atr = float(df["atr"].iloc[last_i])
    body = abs(c - o)
    rng = h - l
    if rng <= 0 or not np.isfinite(atr):
        return "neutral", "no range"
    upper, lower = h - max(c, o), min(c, o) - l
    if lower >= 0.6 * rng and body <= 0.3 * rng:
        return "bull", "pin / hammer"
    if upper >= 0.6 * rng and body <= 0.3 * rng:
        return "bear", "shooting star"
    if last_i >= 1:
        o1, c1 = float(df["open"].iloc[last_i - 1]), float(df["close"].iloc[last_i - 1])
        if c > o and c1 < o1 and c >= o1 and o <= c1:
            return "bull", "bullish engulfing"
        if c < o and c1 > o1 and c <= o1 and o >= c1:
            return "bear", "bearish engulfing"
    if c > o:
        return "bull", "bull close"
    if c < o:
        return "bear", "bear close"
    return "neutral", "doji"


def school_status(name, state, note=""):
    return {"name": name, "on": True, "state": state, "note": note}


def build_bundle():
    now = pd.Timestamp.now(tz=NY)
    raw15 = load_csv("gc_15m.csv")
    raw1h = load_csv("gc_1h.csv")
    raw1d = load_csv("gc_1d.csv")
    try:
        dxy = load_csv("dxy_15m.csv")
    except Exception:
        dxy = None
    raw4h = resample_4h(raw1h)

    d15 = add_oscillators(raw15)
    d15 = attach_htf(d15, raw1h, raw4h, raw1d)
    d15 = build_fused(d15)

    events, struct_dir, sh3, sl3 = detect_bos_choch(d15, SWING_STRUCT)
    sh5, sl5 = confirmed_swings(d15["high"].to_numpy(float), d15["low"].to_numpy(float), SWING_L)

    last_i = len(d15) - 1
    last_ts = d15.index[last_i]
    last_close = float(d15["close"].iloc[last_i])
    last_atr = float(d15["atr"].iloc[last_i])

    vis_start_ts = last_n_session_start(d15, DISPLAY_SESSIONS)
    vis_start = int(d15.index.get_indexer([vis_start_ts], method="nearest")[0])
    vis_end = last_i

    bias4h = "BULL" if bool(d15["htf_4h_bull"].iloc[last_i]) else ("BEAR" if bool(d15["htf_4h_bear"].iloc[last_i]) else "NEUTRAL")
    eq = find_eq(d15, sh3, sl3, SWING_STRUCT, last_i)
    pdhl = prior_day_hl(d15, raw1d, last_ts, last_i, last_atr, last_close)
    impulse = latest_impulse(d15, sh5, sl5, SWING_L, last_i)

    last15 = last_closed_bar(d15, now, 15)
    last1h = last_closed_bar(raw1h, now, 60)
    xpix = {}
    if last15:
        e = xpix_edge(last15["high"], last15["low"], last_close, last_atr)
        if e:
            e.update(tag="15M", closed_ts=str(last15["ts"]))
            xpix["15m"] = e
    if last1h:
        e = xpix_edge(last1h["high"], last1h["low"], last_close, last_atr)
        if e:
            e.update(tag="1H", closed_ts=str(last1h["ts"]))
            xpix["1h"] = e

    sess_hl = {k: latest_session_hl(d15, vis_start, vis_end, k) for k in ("asia", "london", "ny")}
    sess_boxes = all_session_boxes(d15, vis_start, vis_end)
    closed_i = last_i - 1 if (last15 and last15['ts'] != last_ts) else last_i
    fvgs_all = detect_fvgs(d15, closed_i)
    unfilled = [g for g in fvgs_all if (not g["filled"]) and g["age"] <= FVG_MAX_AGE and g["i"] >= vis_start - 5]
    ifvgs = [g for g in detect_ifvg(fvgs_all, d15, last_i) if g["i"] >= vis_start - 5]
    obs_all = detect_order_blocks(d15, events, last_i)
    brks_all = detect_breakers(d15, sh3, sl3, SWING_STRUCT, last_i)
    obs = [ob for ob in obs_all if ob["i"] >= vis_start - 20 and ob.get("mitigated_i") is None]
    obs = recast_ob_volume_share(obs)
    brks = [b for b in brks_all if b["i"] >= vis_start - 20 and b.get("mitigated_i") is None]
    divs = [d for d in detect_divergences(d15, sh3, sl3, SWING_STRUCT, last_i) if d["i"] >= vis_start]
    cisd = detect_cisd(d15, sh3, sl3, SWING_STRUCT, last_i)
    from cfx_display import curate_cisd_events
    raw_cisd = detect_cisd_all(d15, sh3, sl3, SWING_STRUCT, last_i, lookback=200)
    cisd_draw = curate_cisd_events(raw_cisd, vis_start, vis_end, last_i, last_atr, tf="15m")
    smt = detect_smt(d15, dxy, sh3, sl3, SWING_STRUCT, last_i)

    # dealing range / premium-discount: last confirmed swing high & low
    hs = [i for i in sh3 if i + SWING_STRUCT <= last_i]
    ls = [i for i in sl3 if i + SWING_STRUCT <= last_i]
    pd_mid = None
    if hs and ls:
        hi_i, lo_i = hs[-1], ls[-1]
        # use the more recent pair spanning a real range (max of last few)
        hi_i = max(hs[-3:], key=lambda i: float(d15["high"].iloc[i])) if len(hs) >= 2 else hs[-1]
        lo_i = min(ls[-3:], key=lambda i: float(d15["low"].iloc[i])) if len(ls) >= 2 else ls[-1]
        top, bot = float(d15["high"].iloc[hi_i]), float(d15["low"].iloc[lo_i])
        if top > bot:
            mid = 0.5 * (top + bot)
            pd_mid = {"high": top, "low": bot, "mid": mid, "hi_i": int(hi_i), "lo_i": int(lo_i),
                      "zone": "discount" if last_close < mid else ("premium" if last_close > mid else "equilibrium")}

    vp = volume_profile(d15, vis_start, vis_end)
    vwap_now, vwap_series = session_vwap(d15, last_i)
    ichi = ichimoku_state(d15, last_i)
    trades, d15 = run_pipeline(
        d15, events, sh3, sl3, SWING_STRUCT,
        fvgs_all, obs_all, brks_all, raw1d=raw1d,
        make_impulse=latest_impulse, find_eq=find_eq,
        prior_day_hl=prior_day_hl, volume_profile=volume_profile,
    )
    vis_tr = [t for t in trades if t.fill_i >= vis_start or (t.close_i and t.close_i >= vis_start) or (t.outcome == "open")]
    shown = vis_tr[-2:] if vis_tr else []

    # trend line
    use_lows = struct_dir == 1 or (struct_dir == 0 and bool(d15["m15_bull"].iloc[last_i]))
    trend = None
    if use_lows and len(ls) >= 2:
        i1, i2 = ls[-2], ls[-1]
        trend = {"x1": i1, "y1": float(d15["low"].iloc[i1]), "x2": i2, "y2": float(d15["low"].iloc[i2]), "dir": "bull"}
    elif (not use_lows) and len(hs) >= 2:
        i1, i2 = hs[-2], hs[-1]
        trend = {"x1": i1, "y1": float(d15["high"].iloc[i1]), "x2": i2, "y2": float(d15["high"].iloc[i2]), "dir": "bear"}

    # HTF (4H) CISD / CRT — wide age so events inside the visible window are kept
    htf_z = detect_htf_zones(raw4h, cisd_lookback=80, cisd_max_age=24)
    def _ts_i(ts):
        loc = d15.index.get_indexer([pd.Timestamp(ts)], method="ffill")
        return int(loc[0]) if len(loc) and loc[0] >= 0 else None
    htf_boxes, _seen_h = [], set()
    for bx in htf_z.get("cisd_boxes", []):
        key = (bx.get("side"), str(bx.get("start_ts")), str(bx.get("end_ts")), round(float(bx.get("level") or 0), 2))
        if key in _seen_h:
            continue
        _seen_h.add(key)
        i0, i1 = _ts_i(bx["start_ts"]), _ts_i(bx["end_ts"])
        # drop multi-day HTF walk-backs (e.g. Oct 30 → Nov 3)
        if i0 is not None and i1 is not None and (i1 - i0) > 16 * 6:
            continue
        if i1 is not None and i1 < vis_start:
            continue
        htf_boxes.append({**bx, "i0": i0, "i1": i1})
    crt = htf_z.get("crt_box")
    if crt:
        crt = {**crt, "i0": _ts_i(crt["start_ts"]), "i1": _ts_i(crt["end_ts"])}
    elliott = zigzag_elliott(d15, sh3, sl3, SWING_STRUCT, last_i)
    sess_hint = session_cairo_hint(last_ts)
    bias_d = "BULL" if bool(d15["htf_d_bull"].iloc[last_i]) else ("BEAR" if bool(d15["htf_d_bear"].iloc[last_i]) else "NEUTRAL")

    pa_state, pa_note = pa_candle(d15, last_i)
    rsi_now = float(rsi14(d15["close"]).iloc[last_i])
    macd_now = float(macd_line(d15["close"]).iloc[last_i])
    macd_sig = float(macd_line(d15["close"]).ewm(span=9, adjust=False).mean().iloc[last_i])
    ema20 = float(ema(d15["close"], 20).iloc[last_i])
    ema50 = float(ema(d15["close"], 50).iloc[last_i])

    # pivot levels
    piv = None
    if pdhl.get("pivot") is not None:
        p, h, l_ = pdhl["pivot"], pdhl["pdh"], pdhl["pdl"]
        piv = {"p": p, "r1": 2 * p - l_, "s1": 2 * p - h, "r2": p + (h - l_), "s2": p - (h - l_)}

    # school board — score against the candidate trade, or "no trade"
    open_trades = [t for t in shown if t.outcome == "open"]
    candidate = open_trades[-1] if open_trades else None
    side_ref = candidate.side if candidate else None
    have_trade = side_ref in ("buy", "sell")
    want = 1 if side_ref == "buy" else (-1 if side_ref == "sell" else 0)

    def agree(flag_bull, flag_bear):
        if not have_trade:
            return "no trade"
        if flag_bull and want == 1:
            return "confirm"
        if flag_bear and want == -1:
            return "confirm"
        if flag_bull or flag_bear:
            return "against"
        return "neutral"

    smc_bull = struct_dir == 1
    smc_bear = struct_dir == -1
    in_ote = bool(impulse and impulse.get("in_ote"))
    in_disc = pd_mid and pd_mid["zone"] == "discount"
    in_prem = pd_mid and pd_mid["zone"] == "premium"
    ict_bull = bool(in_ote and impulse and impulse["side"] == "bull") or bool(in_disc)
    ict_bear = bool(in_ote and impulse and impulse["side"] == "bear") or bool(in_prem)

    recent_cisd = [e for e in cisd if e["age"] <= 12]
    cisd_bull = any(e["side"] == "bull" for e in recent_cisd) or (crt and crt.get("side") == "bull")
    cisd_bear = any(e["side"] == "bear" for e in recent_cisd) or (crt and crt.get("side") == "bear")

    smt_st = "n/a (not computed)" if smt is None else (
        agree(smt.get("bull"), smt.get("bear")) if (smt.get("bull") or smt.get("bear")) else ("neutral" if have_trade else "no trade")
    )

    dow = "no trade" if not have_trade else "neutral"
    if len(hs) >= 2 and len(ls) >= 2:
        hh = float(d15["high"].iloc[hs[-1]]) > float(d15["high"].iloc[hs[-2]])
        hl = float(d15["low"].iloc[ls[-1]]) > float(d15["low"].iloc[ls[-2]])
        lh = float(d15["high"].iloc[hs[-1]]) < float(d15["high"].iloc[hs[-2]])
        ll = float(d15["low"].iloc[ls[-1]]) < float(d15["low"].iloc[ls[-2]])
        if hh and hl:
            dow = agree(True, False)
        elif lh and ll:
            dow = agree(False, True)

    fib_st = "no trade" if not have_trade else "neutral"
    if impulse and (impulse.get("in_ote") or impulse.get("in_pocket")):
        fib_st = agree(impulse["side"] == "bull", impulse["side"] == "bear")

    vp_st = "no trade" if not have_trade else "neutral"
    if vp:
        if last_close >= vp["vah"]:
            vp_st = agree(False, True)
        elif last_close <= vp["val"]:
            vp_st = agree(True, False)

    vwap_st = "n/a (not computed)" if vwap_now is None else (
        agree(last_close > vwap_now, last_close < vwap_now) if abs(last_close - vwap_now) > 0.15 * last_atr
        else ("neutral" if have_trade else "no trade")
    )
    piv_st = "no trade" if not have_trade else "neutral"
    if piv:
        if last_close > piv["r1"]:
            piv_st = agree(True, False)
        elif last_close < piv["s1"]:
            piv_st = agree(False, True)
    ichi_st = "n/a (not computed)" if ichi is None else (
        agree(ichi["bias"] == "bull", ichi["bias"] == "bear") if ichi["bias"] != "neutral"
        else ("neutral" if have_trade else "no trade")
    )
    stacked_up = last_close > ema20 > ema50
    stacked_dn = last_close < ema20 < ema50
    ma_st = agree(stacked_up, stacked_dn) if (stacked_up or stacked_dn) else ("neutral" if have_trade else "no trade")
    in_bull_ob = any(ob["side"] == "bull" and ob["lo"] <= last_close <= ob["hi"] for ob in obs)
    in_bear_ob = any(ob["side"] == "bear" and ob["lo"] <= last_close <= ob["hi"] for ob in obs)
    sd_st = agree(in_bull_ob, in_bear_ob) if (in_bull_ob or in_bear_ob) else ("neutral" if have_trade else "no trade")
    pa_st = agree(pa_state == "bull", pa_state == "bear") if pa_state != "neutral" else ("neutral" if have_trade else "no trade")
    mom_hook_b = bool(d15["mom_hook_buy"].iloc[max(0, last_i - 8):last_i + 1].any()) if "mom_hook_buy" in d15 else False
    mom_hook_s = bool(d15["mom_hook_sell"].iloc[max(0, last_i - 8):last_i + 1].any()) if "mom_hook_sell" in d15 else False
    mom_rsi = rsi_now > 55 and macd_now > macd_sig
    mom_rsi_dn = rsi_now < 45 and macd_now < macd_sig
    mom_st = agree(mom_hook_b or mom_rsi, mom_hook_s or mom_rsi_dn)
    if have_trade and not ((mom_hook_b or mom_rsi) or (mom_hook_s or mom_rsi_dn)):
        mom_st = "neutral"
    sess_st = "no trade" if not have_trade else "neutral"
    nyo = sess_hl.get("ny")
    if nyo:
        if last_close < nyo["open"] - 0.3 * last_atr:
            sess_st = agree(False, True)
        elif last_close > nyo["open"] + 0.3 * last_atr:
            sess_st = agree(True, False)
    inter = "n/a (not computed)"
    if dxy is not None and not dxy.empty:
        dxy_1h = None
        try:
            dxy_1h = load_csv("dxy_1h.csv")
        except Exception:
            pass
        if dxy_1h is not None and len(dxy_1h) > 60:
            de20, de50 = ema(dxy_1h["close"], 20), ema(dxy_1h["close"], 50)
            dxy_bull = float(dxy_1h["close"].iloc[-2]) > float(de50.iloc[-2]) and float(de20.iloc[-2]) > float(de50.iloc[-2])
            dxy_bear = float(dxy_1h["close"].iloc[-2]) < float(de50.iloc[-2]) and float(de20.iloc[-2]) < float(de50.iloc[-2])
            inter = agree(dxy_bear, dxy_bull) if (dxy_bull or dxy_bear) else ("neutral" if have_trade else "no trade")

    patt = "no trade" if not have_trade else "neutral"
    if eq.get("eqh") and not eq["eqh"]["swept"]:
        patt = agree(False, True)
    elif eq.get("eql") and not eq["eql"]["swept"]:
        patt = agree(True, False)

    if ELLIOTT_DRAW and elliott.get("pattern") not in ("unlabeled", None):
        ell_st = agree(elliott.get("dir") == 1, elliott.get("dir") == -1)
        ell_note = elliott["pattern"]
    else:
        ell_st = "n/a (experimental, off)"
        ell_note = f"{elliott.get('pattern', 'unlabeled')} — zigzag switch off"

    schools = [
        school_status("SMC", agree(smc_bull, smc_bear),
                      f"struct {'bull' if struct_dir==1 else 'bear' if struct_dir==-1 else 'n/a'}"),
        school_status("ICT", agree(bool(ict_bull), bool(ict_bear)),
                      ("OTE " if in_ote else "") + (pd_mid["zone"] if pd_mid else "")),
        school_status("CRT/CISD", agree(bool(cisd_bull), bool(cisd_bear)) if (cisd_bull or cisd_bear or crt) else ("neutral" if have_trade else "no trade"),
                      (f"CISD {recent_cisd[-1]['side']}" if recent_cisd else (f"CRT 4H {crt.get('side')}" if crt and crt.get('side') else "no fresh HTF event"))),
        school_status("SMT", smt_st, smt.get("note") if smt else "no DXY" if dxy is None else "no SMT"),
        school_status("Elliott", ell_st, ell_note),
        school_status("Gann", "n/a (not computed)", ""),
        school_status("Harmonic", "n/a (not computed)", "no pattern scan this pass"),
        school_status("Wyckoff", "n/a (not computed)", ""),
        school_status("Dow", dow, "HH/HL vs LH/LL"),
        school_status("Fibonacci", fib_st, (f"ret {impulse['retracement']:.2f} of {impulse['side']} impulse"
                                           + ("" if impulse.get("live") else " (not live)") if impulse else "no valid impulse")),
        school_status("Volume Profile", vp_st, (f"POC {vp['poc']:.1f} (OHLCV estimate)" if vp else "n/a")),
        school_status("VWAP", vwap_st, (f"sess {vwap_now:.1f}" if vwap_now else "no volume")),
        school_status("Pivots", piv_st, (f"P {piv['p']:.1f}" if piv else "")),
        school_status("Ichimoku", ichi_st, ichi["pos"] if ichi else ""),
        school_status("MAs", ma_st, f"EMA20 {ema20:.1f} / EMA50 {ema50:.1f}"),
        school_status("S&D", sd_st, f"{len(obs)} valid OB"),
        school_status("Price Action/Candles", pa_st, pa_note),
        school_status("Chart Patterns", patt, "EQH/EQL as double top/bottom only"),
        school_status("Momentum", mom_st, f"merged hook + RSI {rsi_now:.0f} MACD {macd_now:.2f}"),
        school_status("Session Opens", sess_st, "vs NY open" if nyo else "NY not started"),
        school_status("Intermarket", inter, "DXY 1H vs gold"),
    ]
    n_conf = sum(1 for s in schools if s["state"] == "confirm")
    n_against = sum(1 for s in schools if s["state"] == "against")
    n_computed = sum(1 for s in schools if not str(s["state"]).startswith("n/a"))
    n_no_trade = sum(1 for s in schools if s["state"] == "no trade")

    why_lines = []
    named_tgts = []
    weak_alt = ""
    if candidate:
        why = candidate.reason
        inv = candidate.invalidation
        weak_alt = candidate.weak_alt
        named_tgts = [
            f"TP1 {candidate.tp1_name} {candidate.tp1:.1f} ({candidate.rr1:.1f}R)",
            f"TP2 {candidate.tp2_name} {candidate.tp2:.1f} ({candidate.rr2:.1f}R)",
        ]
        for sc in schools:
            if sc["state"] == "confirm":
                why_lines.append(f"{sc['name']}: {sc['note'] or 'aligns with the trade'}")
            elif sc["state"] == "against":
                why_lines.append(f"{sc['name']} against: {sc['note']}")
    else:
        from cfx_pipeline import recent_sweep as _rsweep
        misses = []
        r = d15.iloc[last_i]
        if bool(r.get("veto_buy")) and bool(r.get("veto_sell")):
            misses.append("daily+4H veto both sides")
        sw_b = _rsweep(d15, sh3, sl3, SWING_STRUCT, last_i, "buy")
        sw_s = _rsweep(d15, sh3, sl3, SWING_STRUCT, last_i, "sell")
        if not sw_b and not sw_s:
            misses.append("no recent liquidity sweep")
        if not recent_cisd and not any(e["kind"] == "CHoCH" and last_i - e["i"] <= 8 for e in events):
            misses.append("no fresh LTF CISD/CHoCH")
        if not unfilled and not obs:
            misses.append("no unfilled FVG/OB POI nearby")
        if not bool(r.get("in_kz", False)):
            misses.append("outside killzone")
        if impulse is None or not impulse.get("live"):
            misses.append("no live fib retracement")
        why = "No active setup" + (" — " + ", ".join(misses[:4]) if misses else "")
        inv = "No setup to invalidate"
        weak_alt = ("Weak alt: 4H is " + bias4h + ", daily is " + bias_d
                    + "; wait for sweep then CISD/CHoCH into a POI.")
        why_lines = [f"{sc['name']}: {sc['note']}" for sc in schools if sc["note"] and sc["state"] == "no trade"][:6]

    from cfx_display import collect_osc_dots, collect_school_markers, build_trade_stories
    osc_dots, osc_rejected, osc_misplaced = collect_osc_dots(d15, trades, vis_start, vis_end)
    # Temporarily attach cisd_draw so markers see the curated set
    _bundle_partial = {"d15": d15, "vis_start": vis_start, "last_i": last_i, "last_atr": last_atr,
                       "events": events, "cisd_draw": cisd_draw, "smt": smt, "divs": divs,
                       "trades_all": trades}
    school_markers = collect_school_markers(_bundle_partial)
    trade_stories = build_trade_stories(trades, d15)
    vis_stories = [st for st in trade_stories if st["fill_i"] >= vis_start or st["signal_i"] >= vis_start]

    return {
        "now": now, "d15": d15, "raw1h": raw1h, "raw1d": raw1d, "dxy": dxy,
        "last_i": last_i, "last_ts": last_ts, "last_close": last_close, "last_atr": last_atr,
        "vis_start": vis_start, "vis_end": vis_end, "bias4h": bias4h, "bias_d": bias_d, "struct_dir": struct_dir,
        "events": events, "sh3": sh3, "sl3": sl3, "sh5": sh5, "sl5": sl5,
        "eq": eq, "pdhl": pdhl, "impulse": impulse, "xpix": xpix,
        "last15": last15, "last1h": last1h, "sess_hl": sess_hl, "sess_boxes": sess_boxes,
        "sess_hint": sess_hint,
        "fvgs_unfilled": unfilled, "ifvgs": ifvgs, "obs": obs, "breakers": brks,
        "divs": divs, "cisd": cisd, "cisd_draw": cisd_draw, "smt": smt, "pd_mid": pd_mid, "vp": vp,
        "osc_dots": osc_dots, "osc_rejected": osc_rejected, "osc_misplaced": osc_misplaced,
        "school_markers": school_markers, "trade_stories": vis_stories, "trade_stories_all": trade_stories,
        "vwap_now": vwap_now, "vwap_series": vwap_series, "ichi": ichi,
        "trades_all": trades, "shown": shown, "trend": trend, "crt": crt,
        "htf_boxes": htf_boxes, "elliott": elliott,
        "piv": piv, "ema20": ema20, "ema50": ema50, "rsi": rsi_now, "macd": macd_now,
        "schools": schools, "n_conf": n_conf, "n_against": n_against, "n_computed": n_computed,
        "n_no_trade": n_no_trade, "candidate": candidate,
        "why": why, "why_lines": why_lines, "named_targets": named_tgts,
        "inv": inv, "weak_alt": weak_alt, "pa_note": pa_note,
        "news_feed": NEWS_FEED, "forming": bool(last15 and last15["ts"] != last_ts),
    }
