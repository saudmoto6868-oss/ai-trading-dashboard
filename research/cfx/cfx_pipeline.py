#!/usr/bin/env python3
"""CFX sequential entry engine.

Shared by trade boxes and oscillator dots. Research only — no edge claimed.
Source clocks are America/New_York (DST-safe). Cairo labels are derived.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from fused_oscillator import (
    COOLDOWN_BARS_15M,
    CONSENSUS,
    GOLDEN_POCKET,
    MIN_LEG_ATR,
    OTE,
    SPREAD_USD,
    in_killzone,
    hook_flags,
)

# ── Single session-clock definition (America/New_York) ──
# Display sessions (full windows). Killzones stay in fused_oscillator.KILLZONES.
SESS_WINDOWS = {
    "asia":   ((19, 0), (2, 0)),   # 19:00–02:00 NY
    "london": ((2, 0), (9, 0)),    # 02:00–09:00 NY
    "ny":     ((8, 0), (17, 0)),   # 08:00–17:00 NY
}
NY = "America/New_York"
CAIRO = "Africa/Cairo"

# Risk / cost
RR1_MIN = 1.5
SL_BUF_ATR = 0.15
COST_R_MAX = 0.20
NEWS_EVENTS: list[pd.Timestamp] = []  # empty = no calendar feed
NEWS_BEFORE_MIN = 30
NEWS_AFTER_MIN = 15
NEWS_FEED = "manual (no calendar feed connected)"

SWEEP_LOOK = 16
CISD_LTF_MAX_AGE = 12
CHOCH_MAX_AGE = 8
LIMIT_WAIT = 16
FVG_MAX_AGE = 30

ELLIOTT_DRAW = False  # off-by-default experimental zigzag labeler


def in_ny_window(ts: pd.Timestamp, start: tuple[int, int], end: tuple[int, int]) -> bool:
    t = ts.tz_convert(NY)
    minutes = t.hour * 60 + t.minute
    a = start[0] * 60 + start[1]
    b = end[0] * 60 + end[1]
    if a < b:
        return a <= minutes < b
    return minutes >= a or minutes < b


def session_flags(ts: pd.Timestamp) -> dict:
    return {k: in_ny_window(ts, a, b) for k, (a, b) in SESS_WINDOWS.items()}


def session_cairo_hint(sample: pd.Timestamp) -> dict[str, str]:
    """Derive Cairo clock labels for the sample date (handles US DST)."""
    out = {}
    day = sample.tz_convert(NY).normalize()
    for name, (start, end) in SESS_WINDOWS.items():
        a = day + pd.Timedelta(hours=start[0], minutes=start[1])
        b = day + pd.Timedelta(hours=end[0], minutes=end[1])
        if end[0] < start[0]:
            b = b + pd.Timedelta(days=1)
        # if start is 19:00, that session begins the previous calendar evening
        out[name] = (
            f"{start[0]:02d}:{start[1]:02d}–{end[0]:02d}:{end[1]:02d} NY / "
            f"{a.tz_convert(CAIRO).strftime('%H:%M')}–{b.tz_convert(CAIRO).strftime('%H:%M')} Cairo"
        )
    return out


def in_news_blackout(ts: pd.Timestamp, events: list[pd.Timestamp] | None = None) -> bool:
    evs = NEWS_EVENTS if events is None else events
    if not evs:
        return False
    for e in evs:
        e = pd.Timestamp(e)
        if e.tzinfo is None:
            e = e.tz_localize(NY)
        if e - pd.Timedelta(minutes=NEWS_BEFORE_MIN) <= ts <= e + pd.Timedelta(minutes=NEWS_AFTER_MIN):
            return True
    return False


def merge_momentum_hook(df: pd.DataFrame) -> pd.DataFrame:
    """One hook from the three MT5 oscillators. Counts as a single momentum confirmation."""
    out = hook_flags(df)
    r = out["rsi1_smooth"]
    was_os_r = r.shift(1) <= 18.0
    was_ob_r = r.shift(1) >= 82.0
    leaving_buy_r = was_os_r & (r > r.shift(1))
    leaving_sell_r = was_ob_r & (r < r.shift(1))
    rsi_macd_buy = (r <= 18.0) | leaving_buy_r
    rsi_macd_sell = (r >= 82.0) | leaving_sell_r

    sk = out["rsi1_stoch_k"]
    # screenshot zones: buy 18 / 25, sell 75 / 83, waiting 7 / 90
    rsi_stoch_buy = sk <= 25.0
    rsi_stoch_sell = sk >= 75.0

    out["rsi1_macd_buy"] = rsi_macd_buy.fillna(False)
    out["rsi1_macd_sell"] = rsi_macd_sell.fillna(False)
    out["rsi1_stoch_buy"] = rsi_stoch_buy.fillna(False)
    out["rsi1_stoch_sell"] = rsi_stoch_sell.fillna(False)
    out["mom_hook_buy"] = (out["hook_buy"] & out["rsi1_macd_buy"] & out["rsi1_stoch_buy"]).fillna(False)
    out["mom_hook_sell"] = (out["hook_sell"] & out["rsi1_macd_sell"] & out["rsi1_stoch_sell"]).fillna(False)
    return out


def detect_cisd_all(df: pd.DataFrame, sh, sl, left: int, last_i: int, lookback: int = 80):
    """Every CISD confirmation with conf_i <= last_i (no future bars in the rule)."""
    o, h, l, c = (df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    n = last_i + 1
    hs = [i for i in sh if i + left <= last_i]
    ls = [i for i in sl if i + left <= last_i]
    evs = []

    for li in ls:
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
                    "start_i": int(s0), "swing_i": int(li), "sweep_lvl": lvl})

    for hi in hs:
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
                    "start_i": int(s0), "swing_i": int(hi), "sweep_lvl": lvl})
    return evs


def detect_htf_zones(htf: pd.DataFrame, swing_len: int = 3, cisd_lookback: int = 40, cisd_max_age: int = 6):
    """Shared HTF CRT / CISD definition (default 4H): start/end boxes.

    CRT: prior completed HTF range; marked sweep+reclaim when the next HTF bar
    wicks beyond and closes back inside.
    CISD: sweep → delivery run → body close through the open of that run.
    """
    from cfx_lib import detect_bos_choch

    if htf is None or len(htf) < 8:
        return {"cisd_boxes": [], "crt_box": None}
    last_i = len(htf) - 1
    events, struct_dir, sh, sl = detect_bos_choch(htf, swing_len)
    raw = detect_cisd_all(htf, sh, sl, swing_len, last_i, lookback=cisd_lookback)
    boxes, seen = [], set()
    for ev in raw:
        age = last_i - ev["conf_i"]
        if age > cisd_max_age:
            continue
        key = (ev["side"], int(ev["start_i"]), int(ev["conf_i"]), round(float(ev["level"]), 2))
        if key in seen:
            continue
        seen.add(key)
        slc = htf.iloc[ev["start_i"]:ev["conf_i"] + 1]
        boxes.append({
            "kind": "CISD",
            "side": ev["side"],
            "start_ts": htf.index[ev["start_i"]],
            "end_ts": htf.index[ev["conf_i"]],
            "top": float(slc["high"].max()),
            "bot": float(slc["low"].min()),
            "level": ev["level"],
            "age": age,
        })

    crt = None
    if last_i >= 2:
        # last closed bar is -1 if the final bar may still be forming; caller should
        # pass a completed-bar frame. Use [-2] as range, [-1] as action.
        rng = htf.iloc[-2]
        act = htf.iloc[-1]
        rh, rl = float(rng["high"]), float(rng["low"])
        ah, al, ac = float(act["high"]), float(act["low"]), float(act["close"])
        sweep_lo = al < rl and ac > rl
        sweep_hi = ah > rh and ac < rh
        side = "bull" if sweep_lo else ("bear" if sweep_hi else None)
        crt = {
            "kind": "CRT",
            "tf": "4H",
            "side": side,
            "high": rh,
            "low": rl,
            "start_ts": htf.index[-2],
            "end_ts": htf.index[-1],
            "swept": bool(sweep_lo or sweep_hi),
        }
    return {"cisd_boxes": boxes, "crt_box": crt, "struct_dir": struct_dir}


def recast_ob_volume_share(obs: list[dict]) -> list[dict]:
    """Spec: vol_ob / sum(vol of displayed OBs) * 100."""
    tot = sum(float(ob.get("vol") or 0) for ob in obs)
    out = []
    for ob in obs:
        row = dict(ob)
        row["bar_pct"] = float(ob.get("pct") or 0.0)  # original 20-bar share
        row["pct"] = (100.0 * float(ob.get("vol") or 0) / tot) if tot > 0 else 0.0
        row["pct_label"] = "share of visible OBs"
        out.append(row)
    return out


def fvg_valid_at(g: dict, close: np.ndarray, i: int, max_age: int = FVG_MAX_AGE) -> bool:
    if g["i"] > i or (i - g["i"]) > max_age:
        return False
    fill_i = g.get("fill_i")
    if fill_i is not None and fill_i <= i:
        return False
    # fallback if fill_i missing
    if fill_i is None:
        c = close
        if g["side"] == "bull" and np.any(c[g["i"] + 1:i + 1] < g["lo"]):
            return False
        if g["side"] == "bear" and np.any(c[g["i"] + 1:i + 1] > g["hi"]):
            return False
    return True


def zone_valid_at(z: dict, i: int, birth_key: str = "break_i", max_age: int = 80) -> bool:
    birth = z.get(birth_key, z.get("mss_i", z.get("i", 0)))
    if birth > i:
        return False
    if i - birth > max_age:
        return False
    mit = z.get("mitigated_i")
    if mit is not None and mit <= i:
        return False
    return True


def recent_sweep(df, sh, sl, left, i, side: str, look: int = SWEEP_LOOK):
    h = df["high"].to_numpy(float)
    l = df["low"].to_numpy(float)
    c = df["close"].to_numpy(float)
    hs = [x for x in sh if x + left <= i]
    ls = [x for x in sl if x + left <= i]
    window = range(max(0, i - look), i + 1)
    if side == "buy" and ls:
        lvl = float(l[ls[-1]])
        for j in window:
            if l[j] < lvl and c[j] > lvl:
                return {"i": j, "level": lvl, "swing_i": ls[-1]}
    if side == "sell" and hs:
        lvl = float(h[hs[-1]])
        for j in window:
            if h[j] > lvl and c[j] < lvl:
                return {"i": j, "level": lvl, "swing_i": hs[-1]}
    return None


def pick_poi(side: str, i: int, close_px: float, atr: float, fvgs, obs, brks, impulse):
    """Nearest unmitigated FVG / OB / breaker, or OTE of a live opposite-side retracement.

    Buy POI: bullish FVG/OB/breaker, or OTE after a bullish impulse (price pulling back).
    """
    want = "bull" if side == "buy" else "bear"
    cands = []
    for g in fvgs:
        if g["side"] != want:
            continue
        mid = 0.5 * (g["lo"] + g["hi"])
        dist = min(abs(close_px - g["lo"]), abs(close_px - g["hi"]), abs(close_px - mid))
        cands.append({"kind": "FVG", "lo": g["lo"], "hi": g["hi"], "mid": mid, "dist": dist, "i": g["i"]})
    for ob in obs:
        if ob["side"] != want:
            continue
        mid = 0.5 * (ob["lo"] + ob["hi"])
        dist = min(abs(close_px - ob["lo"]), abs(close_px - ob["hi"]), abs(close_px - mid))
        cands.append({"kind": "OB", "lo": ob["lo"], "hi": ob["hi"], "mid": mid, "dist": dist, "i": ob["i"]})
    for b in brks:
        if b["side"] != want:
            continue
        mid = 0.5 * (b["lo"] + b["hi"])
        dist = min(abs(close_px - b["lo"]), abs(close_px - b["hi"]), abs(close_px - mid))
        cands.append({"kind": "BRK", "lo": b["lo"], "hi": b["hi"], "mid": mid, "dist": dist, "i": b["i"]})

    in_ote = False
    if impulse and impulse.get("live") and impulse.get("in_ote"):
        # OTE of a bull impulse is a BUY location (retracing a rally)
        if (side == "buy" and impulse["side"] == "bull") or (side == "sell" and impulse["side"] == "bear"):
            in_ote = True
            lv = impulse["levels"]
            lo, hi = (lv[0.618], lv[0.79]) if impulse["side"] == "bull" else (lv[0.79], lv[0.618])
            lo, hi = (min(lo, hi), max(lo, hi))
            mid = 0.5 * (lo + hi)
            dist = min(abs(close_px - lo), abs(close_px - hi), abs(close_px - mid))
            cands.append({"kind": "OTE", "lo": lo, "hi": hi, "mid": mid, "dist": dist, "i": impulse["i1"]})

    if not cands:
        return None, in_ote
    # Prefer zones the current close can still reach as a limit (not already far through)
    cands.sort(key=lambda z: z["dist"])
    best = cands[0]
    # discard absurdly far POIs (> 4 ATR)
    if atr > 0 and best["dist"] > 4.0 * atr:
        return None, in_ote
    return best, in_ote


def session_hl_at(df: pd.DataFrame, i: int) -> dict:
    """Session high/low using only bars up to i, current occurrence of each session."""
    out = {}
    for key in SESS_WINDOWS:
        start = None
        for j in range(i, -1, -1):
            on = session_flags(df.index[j])[key]
            prev = session_flags(df.index[j - 1])[key] if j > 0 else False
            if on and not prev:
                start = j
                break
            if not on and start is None and j < i:
                # session not active and we haven't found its start walking back
                if j == i or not session_flags(df.index[i])[key]:
                    # if current bar isn't in this session, find the most recent completed run
                    pass
        # find the run that contains i, or the last completed run before i
        runs_start = None
        in_run = False
        rs = None
        last_completed = None
        for j in range(0, i + 1):
            on = session_flags(df.index[j])[key]
            if on and not in_run:
                rs = j
                in_run = True
            elif not on and in_run:
                last_completed = (rs, j - 1)
                in_run = False
                rs = None
        if in_run and rs is not None:
            a, b = rs, i
        elif last_completed:
            a, b = last_completed
        else:
            continue
        sl = df.iloc[a:b + 1]
        out[key] = {
            "start": a, "end": b,
            "high": float(sl["high"].max()), "low": float(sl["low"].min()),
            "open": float(sl["open"].iloc[0]),
        }
    return out


def named_targets(side: str, entry: float, risk: float, atr: float,
                  eq: dict, pdhl: dict, sess_hl: dict, vp: dict | None,
                  impulse: dict | None) -> list[tuple[float, str]]:
    """Opposing liquidity first, then VP, then ICT extensions. rr1 gate applied by caller."""
    cands: list[tuple[float, str]] = []
    if side == "buy":
        if eq.get("eqh") and not eq["eqh"].get("swept") and eq["eqh"]["level"] > entry:
            cands.append((float(eq["eqh"]["level"]), "EQH"))
        if pdhl.get("pdh") and pdhl["pdh"] > entry:
            cands.append((float(pdhl["pdh"]), "PDH"))
        for name, info in (sess_hl or {}).items():
            if info and info["high"] > entry:
                tag = {"asia": "Asia H", "london": "Lon H", "ny": "NY H"}.get(name, f"{name} H")
                cands.append((float(info["high"]), tag))
        if vp:
            if vp["poc"] > entry:
                cands.append((float(vp["poc"]), "POC"))
            if vp.get("vah") and vp["vah"] > entry:
                cands.append((float(vp["vah"]), "VAH"))
        if impulse and impulse.get("extensions"):
            for key, lab in ((-0.27, "ext 1.27"), (-0.62, "ext 1.62"), (-1.0, "ext 2.0")):
                px = impulse["extensions"].get(key)
                if px is not None and px > entry:
                    cands.append((float(px), lab))
        cands = [(p, n) for p, n in cands if p > entry]
        cands.sort(key=lambda x: x[0])
    else:
        if eq.get("eql") and not eq["eql"].get("swept") and eq["eql"]["level"] < entry:
            cands.append((float(eq["eql"]["level"]), "EQL"))
        if pdhl.get("pdl") and pdhl["pdl"] < entry:
            cands.append((float(pdhl["pdl"]), "PDL"))
        for name, info in (sess_hl or {}).items():
            if info and info["low"] < entry:
                tag = {"asia": "Asia L", "london": "Lon L", "ny": "NY L"}.get(name, f"{name} L")
                cands.append((float(info["low"]), tag))
        if vp:
            if vp["poc"] < entry:
                cands.append((float(vp["poc"]), "POC"))
            if vp.get("val") and vp["val"] < entry:
                cands.append((float(vp["val"]), "VAL"))
        if impulse and impulse.get("extensions"):
            for key, lab in ((-0.27, "ext 1.27"), (-0.62, "ext 1.62"), (-1.0, "ext 2.0")):
                px = impulse["extensions"].get(key)
                if px is not None and px < entry:
                    cands.append((float(px), lab))
        cands = [(p, n) for p, n in cands if p < entry]
        cands.sort(key=lambda x: -x[0])

    # de-dupe levels within 0.15 ATR
    uniq = []
    for p, n in cands:
        if any(abs(p - q) <= max(0.15 * atr, 0.05) for q, _ in uniq):
            continue
        uniq.append((p, n))
    return uniq


def apply_rr_gate(cands: list[tuple[float, str]], side: str, entry: float, risk: float):
    if risk <= 0:
        return None, None
    ok = []
    for p, n in cands:
        rr = abs(p - entry) / risk
        if rr + 1e-9 >= RR1_MIN:
            ok.append((p, n, rr))
    if not ok:
        return None, None
    tp1 = ok[0]
    tp2 = ok[1] if len(ok) > 1 else ok[0]
    return tp1, tp2


def zigzag_elliott(df: pd.DataFrame, sh, sl, left: int, last_i: int) -> dict:
    """Experimental zigzag 5-wave / ABC labeler. Not a complete Elliott engine."""
    high = df["high"].to_numpy(float)
    low = df["low"].to_numpy(float)
    hs = [i for i in sh if i + left <= last_i]
    ls = [i for i in sl if i + left <= last_i]
    pivots = sorted([(i, "h", float(high[i])) for i in hs] + [(i, "l", float(low[i])) for i in ls])
    if len(pivots) < 4:
        return {"pattern": "unlabeled", "labels": [], "note": "experimental zigzag; too few pivots", "on": ELLIOTT_DRAW}
    # keep last 9, drop consecutive same-type (shouldn't happen often)
    piv = pivots[-9:]
    cleaned = [piv[0]]
    for p in piv[1:]:
        if p[1] == cleaned[-1][1]:
            # keep the more extreme
            if p[1] == "h" and p[2] >= cleaned[-1][2]:
                cleaned[-1] = p
            elif p[1] == "l" and p[2] <= cleaned[-1][2]:
                cleaned[-1] = p
        else:
            cleaned.append(p)
    piv = cleaned
    note = "experimental zigzag only; not a full Elliott count"
    # try 6-point impulse (L H L H L H or H L H L H L)
    if len(piv) >= 6:
        w = piv[-6:]
        kinds = [x[1] for x in w]
        px = [x[2] for x in w]
        if kinds == ["l", "h", "l", "h", "l", "h"]:
            leg1, leg3, leg5 = px[1] - px[0], px[3] - px[2], px[5] - px[4]
            w2 = (px[1] - px[2]) / leg1 if leg1 > 0 else 0
            w4 = (px[3] - px[4]) / leg3 if leg3 > 0 else 0
            if leg1 > 0 and leg3 > 0 and leg5 > 0 and px[3] > px[1] and px[2] > px[0] and px[4] > px[0]:
                shortest = min(leg1, leg3, leg5)
                if leg3 >= shortest - 1e-9 and 0.3 <= w2 <= 0.9 and 0.2 <= w4 <= 0.8:
                    labels = [{"i": w[k][0], "lab": str(k)} for k in range(6)]
                    return {"pattern": "5-wave up (experimental)", "labels": labels, "note": note, "on": ELLIOTT_DRAW,
                            "dir": 1}
        if kinds == ["h", "l", "h", "l", "h", "l"]:
            leg1, leg3, leg5 = px[0] - px[1], px[2] - px[3], px[4] - px[5]
            w2 = (px[2] - px[1]) / leg1 if leg1 > 0 else 0
            w4 = (px[4] - px[3]) / leg3 if leg3 > 0 else 0
            if leg1 > 0 and leg3 > 0 and leg5 > 0 and px[3] < px[1] and px[2] < px[0] and px[4] < px[0]:
                shortest = min(leg1, leg3, leg5)
                if leg3 >= shortest - 1e-9 and 0.3 <= w2 <= 0.9 and 0.2 <= w4 <= 0.8:
                    labels = [{"i": w[k][0], "lab": str(k)} for k in range(6)]
                    return {"pattern": "5-wave down (experimental)", "labels": labels, "note": note, "on": ELLIOTT_DRAW,
                            "dir": -1}
    if len(piv) >= 4:
        w = piv[-4:]
        kinds = [x[1] for x in w]
        px = [x[2] for x in w]
        if kinds == ["h", "l", "h", "l"] and px[2] < px[0] and px[3] > px[1]:
            return {"pattern": "ABC down (experimental)", "labels": [
                {"i": w[0][0], "lab": "0"}, {"i": w[1][0], "lab": "A"},
                {"i": w[2][0], "lab": "B"}, {"i": w[3][0], "lab": "C"},
            ], "note": note, "on": ELLIOTT_DRAW, "dir": -1}
        if kinds == ["l", "h", "l", "h"] and px[2] > px[0] and px[3] < px[1]:
            return {"pattern": "ABC up (experimental)", "labels": [
                {"i": w[0][0], "lab": "0"}, {"i": w[1][0], "lab": "A"},
                {"i": w[2][0], "lab": "B"}, {"i": w[3][0], "lab": "C"},
            ], "note": note, "on": ELLIOTT_DRAW, "dir": 1}
    return {"pattern": "unlabeled", "labels": [], "note": note, "on": ELLIOTT_DRAW}


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
    why_lines: list = field(default_factory=list)


def run_pipeline(df: pd.DataFrame, events, sh, sl, left: int,
                 fvgs, obs, brks, raw1d=None, make_impulse=None,
                 find_eq=None, prior_day_hl=None, volume_profile=None) -> tuple[list[Trade], pd.DataFrame]:
    """Sequential engine: daily+4H veto → POI → sweep → LTF CISD/CHoCH → LIMIT at FVG/OB."""
    n = len(df)
    o, h, l, c = (df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    atr = df["atr"].to_numpy(dtype=float)
    idx = df.index

    cisd_all = detect_cisd_all(df, sh, sl, left, n - 1, lookback=80)
    choch_buy = {e["i"] for e in events if e["kind"] == "CHoCH" and e["dir"] == 1}
    choch_sell = {e["i"] for e in events if e["kind"] == "CHoCH" and e["dir"] == -1}

    sig_buy = np.zeros(n, dtype=bool)
    sig_sell = np.zeros(n, dtype=bool)
    trades: list[Trade] = []
    last_fire = -10_000

    def known(t):
        return [i for i in sh if i + left <= t], [i for i in sl if i + left <= t]

    def trigger(i, side):
        age_ok_choch = False
        if side == "buy":
            age_ok_choch = any(0 <= i - b <= CHOCH_MAX_AGE for b in choch_buy if b <= i)
            age_ok_cisd = any(e["side"] == "bull" and e["conf_i"] <= i and 0 <= i - e["conf_i"] <= CISD_LTF_MAX_AGE
                              for e in cisd_all)
        else:
            age_ok_choch = any(0 <= i - b <= CHOCH_MAX_AGE for b in choch_sell if b <= i)
            age_ok_cisd = any(e["side"] == "bear" and e["conf_i"] <= i and 0 <= i - e["conf_i"] <= CISD_LTF_MAX_AGE
                              for e in cisd_all)
        return age_ok_choch or age_ok_cisd

    for i in range(left + 8, n - 2):
        if (i - last_fire) < COOLDOWN_BARS_15M:
            continue
        a = float(atr[i])
        if not np.isfinite(a) or a <= 0:
            continue
        if not bool(df["atr_ok"].iloc[i]):
            continue
        if not in_killzone(idx[i]):
            continue
        if in_news_blackout(idx[i]):
            continue

        for side in ("buy", "sell"):
            if side == "buy" and bool(df["veto_buy"].iloc[i]):
                continue
            if side == "sell" and bool(df["veto_sell"].iloc[i]):
                continue
            if not trigger(i, side):
                continue
            sw = recent_sweep(df, sh, sl, left, i, side)
            if not sw:
                continue
            # point-in-time POIs
            fv_now = [g for g in fvgs if fvg_valid_at(g, c, i)]
            ob_now = [z for z in obs if z["side"] == ("bull" if side == "buy" else "bear") and zone_valid_at(z, i, "break_i")]
            br_now = [z for z in brks if z["side"] == ("bull" if side == "buy" else "bear") and zone_valid_at(z, i, "mss_i")]
            impulse = make_impulse(df, sh, sl, left, i) if make_impulse else None
            poi, in_ote = pick_poi(side, i, float(c[i]), a, fv_now, ob_now, br_now, impulse)
            if poi is None:
                continue
            # story AND for OTE-only POIs: require sweep (already) + displacement (valid impulse) + OTE
            if poi["kind"] == "OTE" and not (impulse and impulse.get("live") and impulse.get("in_ote") and impulse.get("displaced", True)):
                continue

            limit = float(poi["mid"])
            hs, ls_ = known(i)
            if side == "buy":
                if not ls_:
                    continue
                sl_px = float(l[ls_[-1]]) - SL_BUF_ATR * a
                # structural: prefer the swept level if deeper
                if sw["level"] < float(l[ls_[-1]]):
                    sl_px = sw["level"] - SL_BUF_ATR * a
                if limit <= sl_px:
                    continue
            else:
                if not hs:
                    continue
                sl_px = float(h[hs[-1]]) + SL_BUF_ATR * a
                if sw["level"] > float(h[hs[-1]]):
                    sl_px = sw["level"] + SL_BUF_ATR * a
                if limit >= sl_px:
                    continue

            # wait for limit fill
            fill_i = None
            entry = None
            cancelled = False
            for j in range(i + 1, min(n, i + 1 + LIMIT_WAIT)):
                # cancel if POI mitigated before fill
                if side == "buy" and np.any(c[poi["i"] + 1:j + 1] < poi["lo"]) and poi["kind"] in ("FVG",):
                    cancelled = True
                    break
                if side == "sell" and np.any(c[poi["i"] + 1:j + 1] > poi["hi"]) and poi["kind"] in ("FVG",):
                    cancelled = True
                    break
                if side == "buy":
                    if l[j] <= limit:
                        entry = float(o[j]) if o[j] < limit else limit
                        fill_i = j
                        break
                    if l[j] <= sl_px:
                        cancelled = True
                        break
                else:
                    if h[j] >= limit:
                        entry = float(o[j]) if o[j] > limit else limit
                        fill_i = j
                        break
                    if h[j] >= sl_px:
                        cancelled = True
                        break
            if cancelled or fill_i is None or entry is None:
                continue

            # spread: worse effective entry
            if side == "buy":
                entry_eff = entry + SPREAD_USD / 2.0
                risk = entry_eff - sl_px
            else:
                entry_eff = entry - SPREAD_USD / 2.0
                risk = sl_px - entry_eff
            if risk <= 0:
                continue
            cost_R = SPREAD_USD / risk
            if cost_R > COST_R_MAX:
                continue

            eq = find_eq(df, sh, sl, left, i) if find_eq else {}
            pdhl = {}
            if prior_day_hl is not None and raw1d is not None:
                pdhl = prior_day_hl(df, raw1d, idx[i], i, a, float(c[i]))
            sess = session_hl_at(df, i)
            vp = None
            if volume_profile is not None:
                vp = volume_profile(df, max(0, i - 96), i)
            tps = named_targets(side, entry_eff, risk, a, eq, pdhl, sess, vp, impulse)
            tp1, tp2 = apply_rr_gate(tps, side, entry_eff, risk)
            if tp1 is None:
                continue
            tp1_px, tp1_name, rr1 = tp1
            tp2_px, tp2_name, rr2 = tp2

            outcome, close_i, hit_tp1 = "open", None, False
            for k in range(fill_i + 1, n):
                if side == "buy":
                    hit_sl, hit1, hit2 = l[k] <= sl_px, h[k] >= tp1_px, h[k] >= tp2_px
                else:
                    hit_sl, hit1, hit2 = h[k] >= sl_px, l[k] <= tp1_px, l[k] <= tp2_px
                if hit_sl and (hit1 or hit2):
                    outcome, close_i = "SL", k  # same-bar: conservative
                    break
                if hit_sl:
                    outcome, close_i = ("TP1 then SL" if hit_tp1 else "SL"), k
                    break
                if hit2:
                    outcome, close_i = "TP2", k
                    break
                if hit1:
                    hit_tp1 = True
                    # keep running toward TP2; if this is the last bar we will report TP1
                    if k == n - 1:
                        outcome, close_i = "TP1", k

            if hit_tp1 and outcome == "open":
                # reached end without TP2/SL after TP1
                outcome, close_i = "TP1", n - 1

            steps = [f"sweep {sw['level']:.1f}", f"{poi['kind']} limit {limit:.1f}", "CISD/CHoCH"]
            reason = ("Buy" if side == "buy" else "Sell") + " — " + ", ".join(steps)
            inv = (f"Close below {sl_px:.1f} (swing + {SL_BUF_ATR} ATR)"
                   if side == "buy" else f"Close above {sl_px:.1f} (swing + {SL_BUF_ATR} ATR)")
            if side == "buy":
                weak = f"Weak alt: a reclaim of the sweep {sw['level']:.1f} would negate the CISD/CHoCH long."
            else:
                weak = f"Weak alt: a reclaim of the sweep {sw['level']:.1f} would negate the CISD/CHoCH short."

            tr = Trade(
                signal_i=i, fill_i=fill_i, close_i=close_i, side=side,
                entry=round(entry_eff, 2), sl=round(sl_px, 2),
                tp1=round(tp1_px, 2), tp2=round(tp2_px, 2),
                rr1=round(rr1, 2), rr2=round(rr2, 2), atr=round(a, 3),
                outcome=outcome, reason=reason, schools=[], invalidation=inv,
                cost_R=round(cost_R, 3), tp1_name=tp1_name, tp2_name=tp2_name,
                limit=round(limit, 2), poi_kind=poi["kind"], weak_alt=weak,
            )
            trades.append(tr)
            if side == "buy":
                sig_buy[fill_i] = True
            else:
                sig_sell[fill_i] = True
            last_fire = i
            break  # one side per bar

    out = df.copy()
    out["sig_buy"] = sig_buy
    out["sig_sell"] = sig_sell
    return trades, out


def summarize_backtest(trades: list[Trade], start, end) -> dict:
    taken = [t for t in trades]
    decided = [t for t in taken if t.outcome in ("SL", "TP1", "TP2", "TP1 then SL")]
    tp1_first = [t for t in decided if t.outcome in ("TP1", "TP2")]
    sl_first = [t for t in decided if t.outcome == "SL"]
    tp1_then_sl = [t for t in decided if t.outcome == "TP1 then SL"]
    # first-exit R: TP1/TP2 → +rr1 - cost; SL → -1 - cost; TP1 then SL → +rr1 - cost
    rs = []
    for t in decided:
        if t.outcome == "SL":
            rs.append(-1.0 - t.cost_R)
        elif t.outcome in ("TP1", "TP2", "TP1 then SL"):
            rs.append(t.rr1 - t.cost_R)
    n = len(decided)
    hit_den = len(tp1_first) + len(sl_first) + len(tp1_then_sl)
    # hit rate at TP1 vs SL: TP1-or-better (incl. TP1 then SL) over decided
    hit_n = len(tp1_first) + len(tp1_then_sl)
    summary = {
        "window_start": str(start),
        "window_end": str(end),
        "n_taken": len(taken),
        "n_decided": n,
        "n_open": sum(1 for t in taken if t.outcome == "open"),
        "n_tp1_or_better": hit_n,
        "n_sl_first": len(sl_first),
        "n_tp2": sum(1 for t in decided if t.outcome == "TP2"),
        "n_tp1_then_sl": len(tp1_then_sl),
        "hit_rate_tp1_vs_sl": (round(hit_n / n, 4) if n else None),
        "avg_R_after_cost": (round(float(np.mean(rs)), 4) if rs else None),
        "spread_usd": SPREAD_USD,
        "rr1_min": RR1_MIN,
        "note": (
            "Research only. First-exit model: SL = -1R - cost_R; TP1/TP2/TP1-then-SL = +rr1 - cost_R. "
            "Same-bar SL+TP counted as SL. yfinance GC=F (gold futures), not spot XAUUSD. "
            "Show numbers only at n>=30; claim edge only at n>=100 and t>3 after costs."
        ),
    }
    if n < 30:
        summary["display"] = f"n={n} < 30 — rate shown for the log only, not as a performance figure."
    elif n < 100:
        summary["display"] = f"n={n} (>=30, <100) — may be shown; no edge claimed."
    else:
        summary["display"] = f"n={n} — no edge claimed unless t>3 after costs (not tested here)."
    return summary
