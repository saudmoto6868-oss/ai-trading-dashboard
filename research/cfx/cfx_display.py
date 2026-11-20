#!/usr/bin/env python3
"""Display helpers for CFX: curated CISD, oscillator dots, school markers, stories."""
from __future__ import annotations

import numpy as np
import pandas as pd

from cfx_lib import cairo, cairo_label, session_flags

MAX_CISD_SPAN = 32          # 15m bars (~8h) — longer is a walk-back artifact
MAX_SWEEP_TO_CONF = 40      # confirm should follow the sweep, not come days later
SWEEP_LEAD = 16             # origin may start a bit before the sweep wick
DEDUP_ATR = 0.30


def curate_cisd_events(raw, vis_start, vis_end, last_i, atr, tf="15m"):
    """Keep every valid compact CISD that overlaps the visible window.

    Rejects walk-backs whose origin is days before the sweep/confirm (those
    painted a chart-wide line and hid the real, short CISDs).
    Dedupes same-side events whose level sits within 0.3 ATR and whose
    origin→confirm spans overlap — keeps the shorter (tighter) one.
    """
    evs = []
    for ev in raw or []:
        row = dict(ev)
        s = row.get("start_i")
        cf = row.get("conf_i")
        sw = row.get("sweep_i")
        if s is None or cf is None:
            continue
        s, cf = int(s), int(cf)
        span = cf - s
        if span < 0 or span > MAX_CISD_SPAN:
            continue
        if sw is not None:
            sw = int(sw)
            if s < sw - SWEEP_LEAD:
                continue
            if cf - sw > MAX_SWEEP_TO_CONF:
                continue
        if cf < vis_start or s > vis_end:
            continue
        row["start_i"] = s
        row["conf_i"] = cf
        row["sweep_i"] = sw
        row["span"] = span
        row["age"] = int(last_i - cf)
        row["tf"] = tf
        evs.append(row)

    evs.sort(key=lambda e: (e["conf_i"], e["span"]))
    kept = []
    for ev in evs:
        replaced = False
        drop = False
        for i, k in enumerate(kept):
            if ev["side"] != k["side"]:
                continue
            if abs(float(ev["level"]) - float(k["level"])) > DEDUP_ATR * max(atr, 1e-6):
                continue
            if ev["conf_i"] < k["start_i"] or ev["start_i"] > k["conf_i"]:
                continue
            if ev["span"] < k["span"] or (ev["span"] == k["span"] and ev["conf_i"] >= k["conf_i"]):
                kept[i] = ev
                replaced = True
            else:
                drop = True
            break
        if not replaced and not drop:
            kept.append(ev)
    kept.sort(key=lambda e: e["conf_i"])
    return kept


def collect_osc_dots(df, trades, vis_start, vis_end):
    """Merged MT5 hook dots at the hook bar — not at the pipeline fill.

    BUY: 4-stoch leaving adaptive OS + turning up AND RSI(1) MACD OS/leaving 18
    AND RSI(1) Stoch <= 25. Extra guard: median still on the lower half and rising.
    SELL: the mirror on the upper half.
    'Agreement with pipeline': drop a hook that fires while an opposite-side
    pipeline trade is being signaled/filled, or while the HTF veto blocks that side.
    Future price is logged only — never used as a filter (no lookahead).
    """
    dots = []
    rejected = []
    n = len(df)
    med = df["stoch_med"].to_numpy(dtype=float)

    def after_text(i, side, px):
        nxt = df.iloc[i + 1: i + 9]
        if nxt.empty:
            return "no further bars"
        if side == "buy":
            return (f"next8 high {float(nxt['high'].max()) - px:+.1f} / "
                    f"low {float(nxt['low'].min()) - px:+.1f}")
        return (f"next8 low {float(nxt['low'].min()) - px:+.1f} / "
                f"high {float(nxt['high'].max()) - px:+.1f}")

    opposite = []
    for t in trades or []:
        a, b = int(t.signal_i), int(t.fill_i if t.fill_i is not None else t.signal_i)
        if a > b:
            a, b = b, a
        opposite.append((t.side, a, b))

    for i in range(max(1, vis_start), min(vis_end, n - 1) + 1):
        buy = bool(df["mom_hook_buy"].iloc[i]) if "mom_hook_buy" in df else False
        sell = bool(df["mom_hook_sell"].iloc[i]) if "mom_hook_sell" in df else False
        if buy == sell:
            continue
        side = "buy" if buy else "sell"
        osc = float(med[i]) if np.isfinite(med[i]) else float("nan")
        prev = float(med[i - 1]) if np.isfinite(med[i - 1]) else osc
        px = float(df["close"].iloc[i])
        ts = cairo_label(df.index[i])
        why_bad = None
        if side == "buy":
            if not (np.isfinite(osc) and osc < 50 and osc > prev):
                why_bad = f"not oversold-turn-up (osc={osc:.1f} prev={prev:.1f})"
            elif bool(df["veto_buy"].iloc[i]) if "veto_buy" in df else False:
                why_bad = "daily+4H veto blocks buys (pipeline disagree)"
        else:
            if not (np.isfinite(osc) and osc > 50 and osc < prev):
                why_bad = f"not overbought-turn-down (osc={osc:.1f} prev={prev:.1f})"
            elif bool(df["veto_sell"].iloc[i]) if "veto_sell" in df else False:
                why_bad = "daily+4H veto blocks sells (pipeline disagree)"
        if why_bad is None:
            for tside, a, b in opposite:
                if tside != side and a - 2 <= i <= b + 2:
                    why_bad = f"conflicts with pipeline {tside} {a}-{b}"
                    break
        rec = {
            "i": int(i), "side": side, "osc": None if not np.isfinite(osc) else round(osc, 2),
            "price": round(px, 2), "time": ts, "after": after_text(i, side, px),
            "rsi1": round(float(df["rsi1_smooth"].iloc[i]), 2) if "rsi1_smooth" in df else None,
            "stoch_k": round(float(df["rsi1_stoch_k"].iloc[i]), 2) if "rsi1_stoch_k" in df else None,
        }
        if why_bad:
            rec["reject"] = why_bad
            rejected.append(rec)
        else:
            # does a same-side pipeline signal sit nearby? (logged, not required)
            rec["pipeline_agree"] = any(
                t.side == side and abs(int(t.signal_i) - i) <= 8 for t in (trades or [])
            )
            dots.append(rec)

    misplaced = []
    if "sig_buy" in df:
        for i in range(vis_start, vis_end + 1):
            if bool(df["sig_buy"].iloc[i]) or bool(df["sig_sell"].iloc[i]):
                side = "buy" if bool(df["sig_buy"].iloc[i]) else "sell"
                osc = float(med[i]) if np.isfinite(med[i]) else float("nan")
                zone = "OS" if osc <= 30 else ("OB" if osc >= 70 else "MID")
                misplaced.append({
                    "i": int(i), "side": side, "osc": None if not np.isfinite(osc) else round(osc, 2),
                    "time": cairo_label(df.index[i]), "zone": zone,
                    "price": round(float(df["close"].iloc[i]), 2),
                    "why": "pipeline fill bar — not an MT5 hook (often mid-range)",
                })
    return dots, rejected, misplaced


def session_name_at(ts):
    fl = session_flags(ts)
    if fl.get("asia"):
        return "Asia"
    if fl.get("london"):
        return "London"
    if fl.get("ny"):
        return "NY"
    return "off-session"


def collect_school_markers(B):
    """Small per-school tags when a school/indicator points at a setup or trade."""
    d15 = B["d15"]
    vis_start, vis_end = B["vis_start"], B["last_i"]
    last_atr = B["last_atr"]
    out = []

    def add(i, school, tag, side, y, kind="event"):
        if i is None or not (vis_start <= int(i) <= vis_end):
            return
        out.append({
            "i": int(i), "school": school, "tag": tag, "side": side,
            "y": float(y), "kind": kind,
        })

    for e in B.get("events") or []:
        if e.get("kind") != "CHoCH":
            continue
        side = "buy" if e["dir"] == 1 else "sell"
        y = float(d15["low"].iloc[e["i"]]) - 0.25 * last_atr if side == "buy" else float(d15["high"].iloc[e["i"]]) + 0.25 * last_atr
        add(e["i"], "SMC", "SMC", side, y, "structure")

    for ev in B.get("cisd_draw") or []:
        side = "buy" if ev["side"] == "bull" else "sell"
        y = float(ev["level"])
        add(ev["conf_i"], "CRT/CISD", "CISD", side, y, "cisd")

    smt = B.get("smt") or {}
    if smt.get("bull") or smt.get("bear"):
        side = "buy" if smt.get("bull") else "sell"
        if "x2" in smt:
            add(smt["x2"], "SMT", "SMT", side, float(smt["y2"]), "smt")

    for d in B.get("divs") or []:
        side = "buy" if d["side"] == "bull" else "sell"
        add(d["i"], "Momentum", f"Div {d['name']}", side, float(d["p2"]), "div")

    for t in B.get("trades_all") or []:
        if t.fill_i < vis_start and t.signal_i < vis_start:
            continue
        if t.signal_i > vis_end:
            continue
        side = t.side
        y = float(t.entry)
        poi = getattr(t, "poi_kind", "") or ""
        if poi == "OTE":
            add(t.signal_i, "ICT", "ICT OTE", side, y, "trade")
            add(t.signal_i, "Fibonacci", "Fib", side, y, "trade")
        elif poi == "FVG":
            add(t.signal_i, "ICT", "FVG", side, y, "trade")
        elif poi == "OB":
            add(t.signal_i, "SMC", "OB", side, y, "trade")
        elif poi == "BRK":
            add(t.signal_i, "SMC", "BRK", side, y, "trade")
        add(t.signal_i, "SMC", "Sweep", side, y, "trade")
        add(t.signal_i, "CRT/CISD", "CISD", side, y, "trade")
        sess = session_name_at(d15.index[t.fill_i])
        if sess != "off-session":
            add(t.fill_i, "Session Opens", sess, side, y, "trade")
        # momentum hook near the signal?
        lo, hi = max(0, t.signal_i - 6), min(len(d15) - 1, t.signal_i + 2)
        col = "mom_hook_buy" if side == "buy" else "mom_hook_sell"
        if col in d15 and bool(d15[col].iloc[lo:hi + 1].any()):
            add(t.signal_i, "Momentum", "Mom", side, y, "trade")

    # collapse exact duplicate tags at the same bar+school+tag
    seen, uniq = set(), []
    for m in out:
        k = (m["i"], m["school"], m["tag"], m["side"])
        if k in seen:
            continue
        seen.add(k)
        uniq.append(m)
    return uniq


def build_trade_stories(trades, d15):
    stories = []
    for n, t in enumerate(trades or []):
        sess = session_name_at(d15.index[t.fill_i])
        poi = getattr(t, "poi_kind", "") or ""
        schools = []
        if poi == "OTE":
            schools += ["ICT OTE", "Fibonacci"]
        elif poi == "FVG":
            schools.append("ICT FVG")
        elif poi == "OB":
            schools.append("SMC OB")
        elif poi == "BRK":
            schools.append("SMC breaker")
        schools.append("SMC sweep")
        schools.append("CRT/CISD")
        if sess != "off-session":
            schools.append(f"Session {sess}")
        ar_side = "شراء" if t.side == "buy" else "بيع"
        stories.append({
            "id": n,
            "side": t.side,
            "side_ar": ar_side,
            "signal_i": int(t.signal_i),
            "fill_i": int(t.fill_i),
            "close_i": None if t.close_i is None else int(t.close_i),
            "signal_time": cairo_label(d15.index[t.signal_i]),
            "fill_time": cairo_label(d15.index[t.fill_i]),
            "close_time": None if t.close_i is None else cairo_label(d15.index[t.close_i]),
            "entry": float(t.entry), "sl": float(t.sl),
            "tp1": float(t.tp1), "tp2": float(t.tp2),
            "rr1": float(t.rr1), "rr2": float(t.rr2),
            "tp1_name": getattr(t, "tp1_name", ""),
            "tp2_name": getattr(t, "tp2_name", ""),
            "poi": poi, "session": sess,
            "reason": t.reason,
            "invalidation": t.invalidation,
            "weak_alt": getattr(t, "weak_alt", ""),
            "outcome": t.outcome,
            "schools": schools,
            "title": f"{t.side.upper()} {cairo_label(d15.index[t.fill_i])}",
            "title_ar": f"صفقة {ar_side}",
            "story": (
                f"{t.side.upper()} opened {cairo_label(d15.index[t.fill_i])} "
                f"(signal {cairo_label(d15.index[t.signal_i])}) via {poi or 'POI'} "
                f"in {sess}. {t.reason}. Schools: {', '.join(schools)}. "
                f"IN {t.entry:.1f}  SL {t.sl:.1f}  "
                f"TP1 {getattr(t, 'tp1_name', '')} {t.tp1:.1f} ({t.rr1:.1f}R)  "
                f"TP2 {getattr(t, 'tp2_name', '')} {t.tp2:.1f} ({t.rr2:.1f}R). "
                f"Outcome {t.outcome}."
            ),
        })
    return stories


SCHOOL_STYLE = {
    "SMC": "#26a69a",
    "ICT": "#ff9800",
    "CRT/CISD": "#4fc3f7",
    "CISD": "#4fc3f7",
    "SMT": "#ce93d8",
    "Fibonacci": "#d4af37",
    "Momentum": "#f48fb1",
    "Session Opens": "#64b5f6",
    "Session": "#64b5f6",
}
