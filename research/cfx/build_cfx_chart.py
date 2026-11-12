#!/usr/bin/env python3
"""Render the real-data CFX chart and the settings panel. Research only."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle
from matplotlib.collections import LineCollection

from cfx_lib import (
    DISPLAY_SESSIONS, XPIX_EXT, cairo, cairo_label, build_bundle, session_segments,
)
from cfx_pipeline import summarize_backtest, SESS_WINDOWS, NEWS_FEED, RR1_MIN, SPREAD_USD

OUT = Path("/workspace/cfx")
BG, PANEL, GRID = "#000000", "#0b0b0b", "#1c1c1c"
TEAL, RED, GOLD = "#26a69a", "#ef5350", "#d4af37"
ORANGE, GREEN, WHITE, DIM = "#ff9800", "#4caf50", "#e6e6e6", "#8a8a8a"
BLUE, MAROON, PURPLE = "#64b5f6", "#c62828", "#ce93d8"
OB_BULL = "#1b5e20"
OB_BEAR = "#7f1d1d"


def draw_candles(ax, df):
    n = len(df)
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    up = c >= o
    cols = np.where(up, TEAL, RED)
    ax.vlines(np.arange(n), l, h, color=cols, linewidth=0.7, zorder=3)
    w = 0.62
    for i in range(n):
        bottom = min(o[i], c[i])
        height = max(abs(c[i] - o[i]), (h[i] - l[i]) * 0.04 + 1e-4)
        ax.add_patch(Rectangle((i - w / 2, bottom), w, height,
                               facecolor=cols[i], edgecolor=cols[i], lw=0.15, zorder=4))


def draw_cisd_span(ax, x0, x1, level, col, tag, atr):
    """Short origin→confirm line only (change b vs v2's right-edge CISD rays)."""
    x0, x1 = float(x0), float(x1)
    if x1 < x0:
        x0, x1 = x1, x0
    if x1 - x0 < 0.85:
        x1 = x0 + 0.85
    cap = max(float(atr) * 0.12, 0.9)
    ax.plot([x0, x1], [level, level], color=col, lw=1.55, solid_capstyle="butt", zorder=8, alpha=0.95)
    ax.plot([x0, x0], [level - cap, level + cap], color=col, lw=1.15, zorder=8)
    ax.plot([x1, x1], [level - cap, level + cap], color=col, lw=1.15, zorder=8)
    ax.text((x0 + x1) / 2.0, level + cap * 0.4, tag, color=col, fontsize=5.6,
            ha="center", va="bottom", zorder=9, clip_on=True)


class RightTags:
    """Keep right-edge labels from stacking on top of each other."""
    def __init__(self, gap):
        self.used = []
        self.gap = gap

    def place(self, y):
        # Nudge upward only, with a hard iteration cap, so labels cannot oscillate.
        y2 = float(y)
        for _ in range(80):
            hit = next((u for u in self.used if abs(y2 - u) < self.gap), None)
            if hit is None:
                break
            y2 = hit + self.gap
        self.used.append(y2)
        return y2


def draw_position(ax, t, faded, xa, xb, tags, atr):
    xb = max(xb, xa + 5)
    a_fill = 0.12 if faded else 0.28
    a_edge = 0.35 if faded else 0.95
    sl_lo, sl_hi = min(t.entry, t.sl), max(t.entry, t.sl)
    tp_far = t.tp2 if abs(t.tp2 - t.entry) >= abs(t.tp1 - t.entry) else t.tp1
    tp_lo, tp_hi = min(t.entry, tp_far), max(t.entry, tp_far)
    ax.add_patch(Rectangle((xa, sl_lo), xb - xa, sl_hi - sl_lo,
                           facecolor=RED, alpha=a_fill, edgecolor=RED, lw=0.8,
                           linestyle="-" if not faded else "--", zorder=4))
    ax.add_patch(Rectangle((xa, tp_lo), xb - xa, tp_hi - tp_lo,
                           facecolor=GREEN, alpha=a_fill, edgecolor=GREEN, lw=0.8,
                           linestyle="-" if not faded else "--", zorder=4))
    ax.plot([xa, xb], [t.entry, t.entry], color=WHITE, lw=0.9, alpha=a_edge, zorder=6)
    if abs(t.tp2 - t.tp1) > 0.05:
        ax.plot([xa, xb], [t.tp1, t.tp1], color=GREEN, lw=0.6, ls="--", alpha=a_edge, zorder=6)
    labs = [
        (t.entry, WHITE, f"IN {t.entry:.1f}"),
        (t.sl, RED, f"SL {t.sl:.1f}"),
        (t.tp1, GREEN, f"TP1 {t.tp1:.1f}  {t.rr1:.1f}R {getattr(t, 'tp1_name', '')}"),
    ]
    if abs(t.tp2 - t.tp1) > 0.05:
        labs.append((t.tp2, GREEN, f"TP2 {t.tp2:.1f}  {t.rr2:.1f}R {getattr(t, 'tp2_name', '')}"))
    for y, col, lab in labs:
        yy = tags.place(y)
        ax.text(xb + 0.6, yy, lab, color=col, fontsize=6.2, va="center", alpha=a_edge, zorder=8)
    mid_tp = (t.entry + t.tp1) / 2
    ax.text((xa + xb) / 2, mid_tp, f"{t.side.upper()}  {t.rr1:.1f}R",
            color=WHITE, fontsize=6.5, ha="center", va="center", alpha=a_edge, zorder=7,
            fontweight="bold")
    if faded:
        ax.text((xa + xb) / 2, t.sl if t.side == "sell" else (t.entry + t.sl) / 2,
                t.outcome, color=WHITE, fontsize=6.5, ha="center", va="center",
                alpha=0.45, fontweight="bold", zorder=7)


def render_chart(B):
    d15 = B["d15"]
    vis_start, vis_end = B["vis_start"], B["vis_end"]
    vis = d15.iloc[vis_start:vis_end + 1]
    nvis = len(vis)
    last_close, last_atr = B["last_close"], B["last_atr"]
    last_i = B["last_i"]

    def vx(i):
        return i - vis_start

    pad_right = XPIX_EXT + 10
    x_max = nvis - 1 + pad_right
    tags = RightTags(gap=max(2.2, last_atr * 0.35))

    plt.rcParams["font.family"] = "DejaVu Sans"
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100, facecolor=BG)
    ax = fig.add_axes([0.035, 0.275, 0.75, 0.680])
    axo = fig.add_axes([0.035, 0.048, 0.75, 0.208], sharex=ax)
    side = fig.add_axes([0.795, 0.05, 0.195, 0.905])
    ax.set_facecolor(BG)
    for a in (ax, axo):
        a.set_facecolor(BG)
        a.tick_params(colors=DIM, labelsize=6.5)
        for sp in a.spines.values():
            sp.set_color("#222")
        a.grid(True, color=GRID, lw=0.35)

    # (a) sessions: v2 full-height bands → light time × high/low boxes, small label
    SESS_COL = {"asia": "#64b5f6", "london": "#ff9800", "ny": "#26a69a"}
    SESS_NAME = {"asia": "Asia", "london": "London", "ny": "NY"}
    for box in B.get("sess_boxes") or []:
        col = SESS_COL[box["key"]]
        x0, x1 = vx(box["start"]), vx(box["end"])
        w = max(1.0, (x1 - x0) + 1.0)
        ax.add_patch(Rectangle((x0 - 0.45, box["low"]), w, max(0.4, box["high"] - box["low"]),
                               facecolor=col, alpha=0.045, edgecolor="none", lw=0, zorder=1))
        ax.add_patch(Rectangle((x0 - 0.45, box["low"]), w, max(0.4, box["high"] - box["low"]),
                               facecolor="none", edgecolor=col, lw=0.6, linestyle=":",
                               alpha=0.30, zorder=1))
        ax.text(x0 + 0.15, box["high"], SESS_NAME[box["key"]], color=col, fontsize=5.4,
                va="bottom", ha="left", zorder=6, alpha=0.55, clip_on=True)

    draw_candles(ax, vis)

    sma77 = d15["close"].rolling(77, min_periods=77).mean().iloc[vis_start:vis_end + 1].to_numpy(float)
    sma144 = d15["close"].rolling(144, min_periods=144).mean().iloc[vis_start:vis_end + 1].to_numpy(float)
    xs_ma = np.arange(nvis)
    ax.plot(xs_ma, sma144, color=RED, lw=1.05, ls="--", zorder=5, alpha=0.9)
    ax.plot(xs_ma, sma77, color=ORANGE, lw=1.05, ls="--", zorder=5, alpha=0.9)
    if np.isfinite(sma144[-1]):
        ax.text(nvis - 1 + 0.4, sma144[-1], "SMA 144", color=RED, fontsize=5.6, va="bottom", zorder=8)
    if np.isfinite(sma77[-1]):
        ax.text(nvis - 1 + 0.4, sma77[-1], "SMA 77", color=ORANGE, fontsize=5.6, va="top", zorder=8)

    y_extras = []

    # unfilled FVGs (recent, max 6)
    for g in B["fvgs_unfilled"][-8:]:
        x0, x1 = vx(g["i"] - 2), nvis - 1
        if x1 < 0 or x0 > x_max:
            continue
        col = TEAL if g["side"] == "bull" else RED
        ax.add_patch(Rectangle((x0, g["lo"]), x1 - x0, g["hi"] - g["lo"],
                               facecolor=col, alpha=0.13, edgecolor=col, lw=0.6, zorder=2))
        ax.text(x0 + 0.3, (g["lo"] + g["hi"]) / 2, "FVG", color=col, fontsize=5.8,
                va="center", zorder=6, alpha=0.9)
        y_extras += [g["lo"], g["hi"]]

    # IFVG
    for g in B["ifvgs"][-6:]:
        x0, x1 = vx(g["i"] - 2), nvis - 1
        if x1 < 0:
            continue
        col = PURPLE
        ax.add_patch(Rectangle((x0, g["lo"]), x1 - x0, g["hi"] - g["lo"],
                               facecolor=col, alpha=0.12, edgecolor=col, lw=0.7, ls="--", zorder=2))
        ax.text(x0 + 0.3, (g["lo"] + g["hi"]) / 2, "IFVG", color=col, fontsize=5.8, va="center", zorder=6)
        y_extras += [g["lo"], g["hi"]]

    # Order blocks — nearest 6, bull/bear labeled; mitigated ones faint + MIT
    obs_sorted = sorted(B["obs"], key=lambda z: min(abs(last_close - z["lo"]), abs(last_close - z["hi"])))[:6]
    for ob in obs_sorted:
        x0, x1 = vx(ob["i"]), nvis - 1
        if x1 < 0:
            continue
        mitigated = ob.get("mitigated_i") is not None
        col = TEAL if ob["side"] == "bull" else RED
        ax.add_patch(Rectangle((x0, ob["lo"]), max(4, x1 - x0), ob["hi"] - ob["lo"],
                               facecolor=col, alpha=0.07 if mitigated else 0.16,
                               edgecolor=col, lw=0.7, ls=":" if mitigated else "-", zorder=2))
        vol_k = ob["vol"] / 1000.0
        side_lab = "bull" if ob["side"] == "bull" else "bear"
        lab = f"OB {side_lab} {vol_k:.1f}K"
        if mitigated:
            lab += " MIT"
        yy = tags.place((ob["lo"] + ob["hi"]) / 2)
        ax.text(nvis - 0.2, yy, lab, color=col, fontsize=5.8, va="center", zorder=8, alpha=0.7 if mitigated else 1)
        if mitigated and vis_start <= ob["mitigated_i"] <= vis_end:
            ax.text(vx(ob["mitigated_i"]), (ob["lo"] + ob["hi"]) / 2, "MIT",
                    color=DIM, fontsize=5.2, ha="center", zorder=7)
        y_extras += [ob["lo"], ob["hi"]]

    # Breakers — up to 6 nearest, with mitigation
    brks = sorted(B["breakers"], key=lambda z: min(abs(last_close - z["lo"]), abs(last_close - z["hi"])))[:6]
    for b in brks:
        x0, x1 = vx(b["i"]), nvis - 1
        if x1 < 0:
            continue
        mitigated = b.get("mitigated_i") is not None
        col = ORANGE
        ax.add_patch(Rectangle((x0, b["lo"]), max(4, x1 - x0), b["hi"] - b["lo"],
                               facecolor=col, alpha=0.06 if mitigated else 0.12,
                               edgecolor=col, lw=0.7, ls="--", zorder=2))
        yy = tags.place((b["lo"] + b["hi"]) / 2)
        lab = "BRK MIT" if mitigated else "BRK"
        ax.text(nvis - 0.2, yy, lab, color=col, fontsize=5.8, va="center", zorder=8)
        y_extras += [b["lo"], b["hi"]]

    # premium/discount midline
    if B["pd_mid"]:
        mid = B["pd_mid"]["mid"]
        ax.plot([-0.5, nvis - 1 + 12], [mid, mid], color=GOLD, lw=0.6, ls=":", zorder=2, alpha=0.75)
        yy = tags.place(mid)
        ax.text(nvis + 12.2, yy, f"EQ 50%  {mid:.1f}  ({B['pd_mid']['zone']})", color=GOLD,
                fontsize=6.2, va="center", zorder=8)
        y_extras.append(mid)

    # VP levels — thin, only if in view-ish
    if B["vp"]:
        for lvl, lab, col in ((B["vp"]["poc"], "POC", GOLD),
                              (B["vp"]["vah"], "VAH", DIM),
                              (B["vp"]["val"], "VAL", DIM)):
            ax.plot([nvis - 16, nvis - 1 + 8], [lvl, lvl], color=col, lw=0.55, ls="-.", zorder=2, alpha=0.7)
            yy = tags.place(lvl)
            ax.text(nvis + 8.2, yy, f"{lab} {lvl:.1f}", color=col, fontsize=5.8, va="center", zorder=8)
            y_extras.append(lvl)

    # VWAP last value (session)
    if B["vwap_now"] is not None:
        # plot visible vwap
        ser = B["vwap_series"][vis_start:vis_end + 1]
        xs = np.arange(nvis)
        mask = np.isfinite(ser)
        if mask.any():
            ax.plot(xs[mask], np.asarray(ser)[mask], color="#7e57c2", lw=0.8, alpha=0.8, zorder=5)
        yy = tags.place(B["vwap_now"])
        ax.text(nvis + 0.4, yy, f"VWAP {B['vwap_now']:.1f}", color="#b39ddb", fontsize=5.8, va="center", zorder=8)
        y_extras.append(B["vwap_now"])

    # BOS / CHoCH — short line at the broken swing (swing → break bar), all in window
    ev_vis = [e for e in B["events"] if vis_start <= e["i"] <= vis_end]
    used_lbl = []
    for e in ev_vis:
        x1 = vx(e["i"])
        x0 = vx(e.get("swing_i", e["i"]))
        if x1 < x0:
            x0, x1 = x1, x0
        if x1 - x0 < 0.8:
            x1 = x0 + 0.8
        lvl = float(e["level"])
        if e["kind"] == "CHoCH":
            col = TEAL if e["dir"] == 1 else MAROON
        else:
            col = GREEN if e["dir"] == 1 else RED
        ax.plot([x0, x1], [lvl, lvl], color=col, lw=1.15, zorder=7, alpha=0.9)
        ax.plot([x1, x1], [lvl - last_atr * 0.08, lvl + last_atr * 0.08], color=col, lw=0.9, zorder=7)
        mid = (x0 + x1) / 2
        if any(abs(mid - u[0]) < 4 and abs(lvl - u[1]) < last_atr * 0.35 for u in used_lbl):
            continue
        va = "bottom" if e["dir"] == -1 else "top"
        off = last_atr * (0.12 if e["dir"] == -1 else -0.12)
        ax.text(mid, lvl + off, e["kind"], color=col, fontsize=5.8, ha="center", va=va,
                fontweight="bold", zorder=8, clip_on=True)
        used_lbl.append((mid, lvl))
        y_extras.append(lvl)

    # confirmed swings (small)
    for i in B["sh3"]:
        if vis_start <= i <= vis_end and i + 3 <= last_i:
            ax.scatter([vx(i)], [float(d15["high"].iloc[i])], marker="v", s=12, color=RED, zorder=5, lw=0)
    for i in B["sl3"]:
        if vis_start <= i <= vis_end and i + 3 <= last_i:
            ax.scatter([vx(i)], [float(d15["low"].iloc[i])], marker="^", s=12, color=TEAL, zorder=5, lw=0)

    # Fib — only a live retracement; light dotted; clipped away from position boxes
    fib = B["impulse"]
    trade_boxes = []
    for t in B.get("shown") or []:
        xa = vx(t.fill_i)
        xb = vx(t.close_i) if t.close_i is not None else nvis - 1
        ys = [t.entry, t.sl, t.tp1, t.tp2]
        trade_boxes.append((min(xa, xb), max(xa, xb), min(ys), max(ys)))
    if fib and fib.get("in_ote") and fib.get("levels"):
        lv_ote = fib["levels"]
        y0, y1 = lv_ote.get(0.62, lv_ote.get(0.618)), lv_ote.get(0.79, lv_ote.get(0.786))
        if y0 is not None and y1 is not None:
            xa, xb = vx(fib["i0"]), nvis - 1
            lo, hi = min(y0, y1), max(y0, y1)
            ax.add_patch(Rectangle((min(xa, xb), lo), abs(xb - xa), hi - lo,
                                   facecolor=GOLD, alpha=0.07, edgecolor=GOLD, lw=0.6, ls=":", zorder=2))
            ax.text(min(xa, xb) + 0.4, (lo + hi) / 2, "OTE", color=GOLD, fontsize=6.0, va="center", zorder=7)
            y_extras += [lo, hi]
    if fib and fib.get("live"):
        lv = fib["levels"]
        x0, x1 = vx(fib["i0"]), vx(fib["i1"])
        if x1 >= -2 and x0 <= x_max:
            x_tag = min(x0, x1) - 0.4
            specs = [
                (0.382, "0.382", DIM),
                (0.5, "0.5", DIM),
                (0.618, "0.618 GP", ORANGE),
                (0.65, "0.65 GP", ORANGE),
                (0.705, "0.705", GOLD),
                (0.786, "0.786", GOLD),
                (0.79, "0.79", GOLD),
                (0.886, "0.886", DIM),
            ]
            for key, lab, col in specs:
                if key not in lv:
                    continue
                y = lv[key]
                xa, xb = min(x0, x1), max(x0, x1) + 3
                for bx0, bx1, by0, by1 in trade_boxes:
                    if by0 <= y <= by1 and xa < bx1 and xb > bx0:
                        xb = min(xb, bx0 - 0.5)
                if xb > xa:
                    ax.plot([xa, xb], [y, y], color=col, lw=0.65, ls=":", zorder=3, alpha=0.8)
                    ax.text(x_tag, y, lab, color=col, fontsize=5.5, ha="right", va="center", zorder=7)
                    y_extras.append(y)
            exts = fib.get("extensions") or {}
            for key, lab in ((-0.27, "-0.27"), (-0.62, "-0.62"), (-1.0, "-1.0")):
                y = exts.get(key)
                if y is None:
                    continue
                xa, xb = max(x0, x1), max(x0, x1) + 8
                skip = any(by0 <= y <= by1 and xa < bx1 and xb > bx0 for bx0, bx1, by0, by1 in trade_boxes)
                if skip:
                    continue
                ax.plot([xa, xb], [y, y], color=DIM, lw=0.55, ls=":", zorder=3, alpha=0.7)
                ax.text(xb + 0.2, y, lab, color=DIM, fontsize=5.3, va="center", zorder=7)
                y_extras.append(y)

    # trend line thin
    if B["trend"]:
        tr = B["trend"]
        x1, x2 = vx(tr["x1"]), vx(tr["x2"])
        if x2 != x1:
            slope = (tr["y2"] - tr["y1"]) / (x2 - x1)
            xe = nvis + 8
            ye = tr["y2"] + slope * (xe - x2)
            ax.plot([x1, xe], [tr["y1"], ye], color=(TEAL if tr["dir"] == "bull" else RED),
                    lw=0.8, alpha=0.7, zorder=5)
            y_extras += [tr["y1"], tr["y2"], ye]

    # SMT line
    smt = B["smt"]
    if smt and (smt.get("bull") or smt.get("bear")) and "x1" in smt:
        ax.plot([vx(smt["x1"]), vx(smt["x2"])], [smt["y1"], smt["y2"]],
                color=PURPLE, lw=1.0, ls="--", zorder=6)
        ax.text(vx(smt["x2"]) + 0.4, smt["y2"], "SMT", color=PURPLE, fontsize=6.2, va="bottom", zorder=8)

    # EQH/EQL — engine pair plus other near-equal swings in view
    def mark_dollar(xi, yi):
        ax.text(xi, yi, "$", color=GOLD, fontsize=8.0, ha="center", va="center",
                fontweight="bold", zorder=11, clip_on=True)

    eq_drawn = []
    def draw_eq(ev, name, col):
        lvl = ev["level"]
        if any(abs(lvl - u) < 0.4 for u in eq_drawn):
            return
        ax.plot([vx(ev["i1"]), nvis - 1 + 8], [lvl, lvl], color=col, lw=0.8, zorder=5, alpha=0.85)
        yy = tags.place(lvl)
        ax.text(nvis + 8.2, yy, f"{name} {lvl:.1f}", color=col, fontsize=6.2, va="center",
                fontweight="bold", zorder=8)
        if ev.get("swept") and ev.get("sweep_i") is not None:
            xi = vx(ev["sweep_i"])
            mark_dollar(xi, lvl)
            ax.text(xi + 0.6, lvl, "sweep", color=GOLD, fontsize=5.4, va="bottom", zorder=9)
        eq_drawn.append(lvl)
        y_extras.append(lvl)

    for key, col, name in (("eqh", MAROON, "EQH"), ("eql", TEAL, "EQL")):
        ev = (B.get("eq") or {}).get(key)
        if ev:
            draw_eq(ev, name, col)
    hi_arr = d15["high"].to_numpy(float)
    lo_arr = d15["low"].to_numpy(float)
    hs = [i for i in B.get("sh3") or [] if vis_start - 25 <= i <= vis_end]
    ls_ = [i for i in B.get("sl3") or [] if vis_start - 25 <= i <= vis_end]
    for a, b in zip(hs, hs[1:]):
        if abs(hi_arr[a] - hi_arr[b]) <= 0.10 * last_atr:
            lvl = float(max(hi_arr[a], hi_arr[b]))
            sw = next((j for j in range(max(a, b) + 1, last_i + 1) if hi_arr[j] > lvl), None)
            draw_eq({"level": lvl, "i1": a, "i2": b, "swept": sw is not None, "sweep_i": sw}, "EQH", MAROON)
    for a, b in zip(ls_, ls_[1:]):
        if abs(lo_arr[a] - lo_arr[b]) <= 0.10 * last_atr:
            lvl = float(min(lo_arr[a], lo_arr[b]))
            sw = next((j for j in range(max(a, b) + 1, last_i + 1) if lo_arr[j] < lvl), None)
            draw_eq({"level": lvl, "i1": a, "i2": b, "swept": sw is not None, "sweep_i": sw}, "EQL", TEAL)

    # PDH / PDL — show if near, or if swept (marker)
    pdhl = B["pdhl"]
    if pdhl.get("pdh") is not None:
        if (not pdhl["pdh_swept"] and pdhl["pdh_near"]) or pdhl["pdh_swept"]:
            lvl = pdhl["pdh"]
            ax.plot([nvis - 12, nvis - 1 + 8], [lvl, lvl], color=ORANGE, lw=0.7, zorder=5)
            yy = tags.place(lvl)
            ax.text(nvis + 8.2, yy, f"PDH {lvl:.1f}", color=ORANGE, fontsize=6.0, va="center", zorder=8)
            y_extras.append(lvl)
    if pdhl.get("pdl") is not None:
        if (not pdhl["pdl_swept"] and pdhl["pdl_near"]) or pdhl["pdl_swept"]:
            lvl = pdhl["pdl"]
            ax.plot([nvis - 12, nvis - 1 + 8], [lvl, lvl], color=ORANGE, lw=0.7, zorder=5)
            yy = tags.place(lvl)
            tag = f"PDL {lvl:.1f}" + ("  swept" if pdhl["pdl_swept"] else "")
            ax.text(nvis + 8.2, yy, tag, color=ORANGE, fontsize=6.0, va="center", zorder=8)
            if pdhl["pdl_swept"]:
                # sweep on today's low bar
                lows = vis["low"].to_numpy(float)
                if len(lows):
                    xi = int(np.argmin(lows))
                    mark_dollar(xi, lvl)
            y_extras.append(lvl)

    # session H/L stubs and session-open rays removed (v7): sessions are the light boxes only.

    # (b) CISD: short origin→confirm span using the curated v4 list (all valid, no rays)
    CISD_BULL, CISD_BEAR = "#26a69a", "#ef5350"
    for ev in (B.get("cisd_draw") or []):
        start = ev.get("start_i", ev.get("sweep_i", ev["conf_i"]))
        x0, x1 = vx(start), vx(ev["conf_i"])
        col = CISD_BULL if ev["side"] == "bull" else CISD_BEAR
        draw_cisd_span(ax, x0, x1, ev["level"], col, f"CISD {ev.get('tf', '15m')}", last_atr)
        y_extras.append(ev["level"])
        sw_i, sw_lv = ev.get("sweep_i"), ev.get("sweep_lvl")
        if sw_i is not None and vis_start <= sw_i <= vis_end and sw_lv is not None:
            mark_dollar(vx(sw_i), float(sw_lv))
    for bx in B.get("htf_boxes") or []:
        if bx.get("i0") is None:
            continue
        x0 = vx(bx["i0"])
        x1 = vx(bx["i1"] if bx.get("i1") is not None else last_i)
        col = CISD_BULL if bx.get("side") == "bull" else CISD_BEAR
        draw_cisd_span(ax, x0, x1, bx["level"], col, "CISD 4H", last_atr)
        y_extras.append(bx["level"])
    crt = B.get("crt")
    if crt and crt.get("i0") is not None:
        x0 = vx(crt["i0"])
        x1 = vx(crt["i1"] if crt.get("i1") is not None else last_i)
        ax.add_patch(Rectangle((x0, crt["low"]), max(1.2, x1 - x0), crt["high"] - crt["low"],
                               facecolor=GOLD, alpha=0.05, edgecolor=GOLD, lw=0.8, ls="--", zorder=1))
        ax.text(x0, crt["high"], "CRT start", color=GOLD, fontsize=5.4, va="bottom", zorder=8)
        ax.text(x1, crt["high"], "CRT end", color=GOLD, fontsize=5.4, va="bottom", ha="right", zorder=8)
        y_extras += [crt["high"], crt["low"]]

    # divergence glowing dots
    for d in B["divs"]:
        x = vx(d["i"])
        if not (0 <= x <= nvis - 1):
            continue
        y = d["p2"]
        col = TEAL if d["side"] == "bull" else RED
        ax.scatter([x], [y], s=90, color=col, alpha=0.18, zorder=7, linewidths=0)
        ax.scatter([x], [y], s=22, color=col, edgecolors="white", linewidths=0.4, zorder=8)
        va = "bottom" if d["side"] == "bear" else "top"
        off = last_atr * (0.18 if d["side"] == "bear" else -0.18)
        ax.text(x, y + off, d["name"], color=col, fontsize=5.8, ha="center", va=va, zorder=9)

    # trades — TV position tool, at most 2, closed faded
    shown = B["shown"]
    if shown:
        if len(shown) == 2:
            pairs = [(shown[0], True), (shown[1], shown[1].outcome != "open")]
        else:
            pairs = [(shown[0], shown[0].outcome != "open")]
        for t, faded in pairs:
            xa, xb = vx(t.fill_i), (vx(t.close_i) if t.close_i is not None else nvis - 1)
            draw_position(ax, t, faded, xa, xb, tags, last_atr)
            y_extras += [t.entry, t.sl, t.tp1, t.tp2]
    if not any(t.outcome == "open" for t in shown):
        ax.text(0.50, 0.965, "No active setup", transform=ax.transAxes,
                color=DIM, fontsize=9.5, ha="center", va="top", zorder=10, fontstyle="italic")

    # XPIX
    for key, edge in B["xpix"].items():
        x0, x1 = nvis - 1, nvis - 1 + XPIX_EXT
        px, col = edge["price"], (ORANGE if key == "15m" else GREEN)
        ax.plot([x0, x1], [px, px], color=col, lw=2.0, zorder=8, solid_capstyle="butt")
        ax.scatter([x1], [px], marker=">", s=26, color=col, zorder=9)
        txt = f"{px:.1f} | {edge['tag']}"
        tc = "#111" if key == "15m" else WHITE
        ax.text(x1 + 0.8, px, txt, color=tc, fontsize=7.2, va="center", fontweight="bold", zorder=10,
                bbox=dict(boxstyle="round,pad=0.18", facecolor=col, edgecolor=col, alpha=0.95))
        y_extras.append(px)

    # last price
    ax.axhline(last_close, color=GOLD, lw=0.45, alpha=0.35, zorder=2)
    ax.text(nvis - 1 + 0.3, last_close, f"{last_close:.1f}", color=GOLD, fontsize=7.5,
            va="bottom", fontweight="bold", zorder=8)

    # limits
    vis_lo, vis_hi = float(vis["low"].min()), float(vis["high"].max())
    extra = [e for e in y_extras if np.isfinite(e) and vis_lo - 40 <= e <= vis_hi + 40]
    ylo = min([vis_lo] + extra)
    yhi = max([vis_hi] + extra)
    pad = (yhi - ylo) * 0.06
    ax.set_ylim(ylo - pad, yhi + pad * 1.25)
    ax.set_xlim(-0.8, x_max)
    ax.set_ylabel("GC=F  USD / oz", color=DIM, fontsize=8)

    # x ticks Cairo
    tick_pos, tick_lab, last_day = [], [], None
    for i, ts in enumerate(vis.index):
        d = cairo(ts).date()
        if d != last_day:
            tick_pos.append(i)
            tick_lab.append(cairo(ts).strftime("%a %d %b\n%H:%M"))
            last_day = d
    tick_pos.append(nvis - 1)
    tick_lab.append(cairo(vis.index[-1]).strftime("%a %d %b\n%H:%M"))
    ax.set_xticks(tick_pos)
    ax.set_xticklabels([])
    axo.set_xticks(tick_pos)
    axo.set_xticklabels(tick_lab, color=DIM, fontsize=6.5)

    # One oscillator pane: Stoch(5,3,3 Low/High SMA) main, confirmed by RSI(14) + MACD(12,26,1)
    from cfx_osc_combo import add_combo_oscillators, collect_combo_dots, STOCH_OS, STOCH_OB, STOCH_MID
    d_osc = add_combo_oscillators(d15)
    viso = d_osc.iloc[vis_start:vis_end + 1]
    xs = np.arange(nvis)
    dots = collect_combo_dots(d_osc, vis_start, vis_end, variant="B")
    B["mt5_dots"] = dots
    B["mt5_osc"] = d_osc
    B["osc_variant"] = "B"

    axo.axhline(STOCH_OS, color=TEAL, lw=0.7, zorder=1)
    axo.axhline(STOCH_OB, color=RED, lw=0.7, zorder=1)
    axo.axhline(STOCH_MID, color="#555", lw=0.45, zorder=1)
    axo.axhline(10, color="#1976d2", lw=0.35, ls=":", zorder=1, alpha=0.6)
    axo.axhline(90, color="#c62828", lw=0.35, ls=":", zorder=1, alpha=0.6)
    axo.plot(xs, viso["st_k"].to_numpy(float), color="#42a5f5", lw=1.15, zorder=4, label="%K 5,3,3")
    axo.plot(xs, viso["st_d"].to_numpy(float), color="#ef9a9a", lw=0.95, zorder=3, label="%D")
    axo.plot(xs, viso["rsi14"].to_numpy(float), color="#b39ddb", lw=0.7, alpha=0.65, zorder=3, label="RSI 14")
    axo.set_ylim(-2, 102)
    axo.set_ylabel("Stoch 5,3,3", color=DIM, fontsize=7)
    axo.set_xlim(-0.8, x_max)
    axo.text(0.01, 0.90,
             "Stoch(5,3,3 Low/High SMA)  15/85/50   •   confirm RSI(14) turn + MACD(12,26,1) main slope   •   variant B",
             transform=axo.transAxes, color=DIM, fontsize=5.6, va="top")
    axo.legend(loc="lower left", fontsize=5.4, facecolor="#111", labelcolor=WHITE,
               framealpha=0.7, ncol=3, borderpad=0.25)

    for d in dots:
        xi = d["i"] - vis_start
        col = TEAL if d["side"] == "buy" else RED
        lab = "BUY" if d["side"] == "buy" else "SELL"
        y = d.get("st_k") if d.get("st_k") is not None else 50
        axo.scatter([xi], [y], marker="o", s=28, color=col, edgecolors="white", lw=0.35, zorder=6)
        va = "bottom" if d["side"] == "buy" else "top"
        off = 6 if d["side"] == "buy" else -6
        axo.text(xi, np.clip(y + off, 2, 98), lab, color=col, fontsize=5.4,
                 ha="center", va=va, zorder=7)
    n_buy = sum(1 for d in dots if d["side"] == "buy")
    n_sell = sum(1 for d in dots if d["side"] == "sell")

    # badge
    bias, bcol = B["bias4h"], (TEAL if B["bias4h"] == "BULL" else RED if B["bias4h"] == "BEAR" else GOLD)
    badge = f"CFX  •  GC=F gold futures 15m  •  4H {bias}  D {B.get('bias_d', '?')}"
    ax.text(0.01, 0.985, badge, transform=ax.transAxes, color=bcol, fontsize=10.5,
            fontweight="bold", va="top", zorder=12,
            bbox=dict(boxstyle="round,pad=0.32", facecolor="#111", edgecolor=bcol, lw=1.0, alpha=0.92))

    legend = [
        Line2D([0], [0], color=ORANGE, lw=2, label="XPIX 15M"),
        Line2D([0], [0], color=GREEN, lw=2, label="XPIX 1H"),
        Line2D([0], [0], color=RED, lw=1, ls="--", label="SMA 144"),
        Line2D([0], [0], color=ORANGE, lw=1, ls="--", label="SMA 77"),
        Line2D([0], [0], color=GOLD, lw=1, ls=":", label="Fib (light)"),
        mpatches.Patch(facecolor=RED, alpha=0.3, label="SL box"),
        mpatches.Patch(facecolor=GREEN, alpha=0.3, label="TP box"),
        mpatches.Patch(facecolor=TEAL, alpha=0.35, label="Bull FVG/OB"),
        mpatches.Patch(facecolor=RED, alpha=0.35, label="Bear FVG/OB"),
        Line2D([0], [0], color=PURPLE, lw=1, ls="--", label="SMT / IFVG"),
        mpatches.Patch(facecolor="#64b5f6", alpha=0.3, label="Asia 19:00–02:00 NY"),
        mpatches.Patch(facecolor="#ff9800", alpha=0.3, label="London 02:00–09:00 NY"),
        mpatches.Patch(facecolor="#26a69a", alpha=0.3, label="NY 08:00–17:00 NY"),
    ]
    ax.legend(handles=legend, loc="lower left", facecolor="#111", edgecolor="#333",
              labelcolor=WHITE, fontsize=5.8, framealpha=0.85, ncol=4, borderpad=0.35)

    start_c, last_c = cairo(vis.index[0]), cairo(vis.index[-1])
    fig.text(0.035, 0.008,
             f"Window: {start_c.strftime('%a %d %b %Y %H:%M')} → {last_c.strftime('%a %d %b %Y %H:%M')} Africa/Cairo"
             f"   •   Last {last_close:.1f}   •   yfinance GC=F 15m / 1H / 4H (4H resampled, CME 18:00 ET)"
             f"   •   Research only, no edge claimed   •   {DISPLAY_SESSIONS} sessions   •   news {B.get('news_feed', 'manual')}",
             color=DIM, fontsize=6.2)

    # ── Schools & Options side panel ──
    side.set_facecolor("#0d0d0d")
    for sp in side.spines.values():
        sp.set_color(GOLD)
        sp.set_linewidth(0.7)
    side.set_xticks([])
    side.set_yticks([])
    side.set_xlim(0, 1)
    side.set_ylim(0, 1)
    side.text(0.05, 0.985, "REASONING  &  SCHOOLS", color=GOLD, fontsize=8.2, fontweight="bold", va="top")
    if B.get("candidate"):
        hdr = f"Confirm {B['n_conf']}   Against {B['n_against']}   vs {B['candidate'].side.upper()}"
    else:
        hdr = f"No trade   watch {B.get('n_no_trade', 0)}   computed {B['n_computed']}/21"
    side.text(0.05, 0.958, hdr, color=WHITE, fontsize=6.0, va="top")

    def wrap(s, w=32):
        words, lines, cur = s.split(), [], ""
        for w0 in words:
            trial = (cur + " " + w0).strip()
            if len(trial) > w:
                if cur:
                    lines.append(cur)
                cur = w0
            else:
                cur = trial
        if cur:
            lines.append(cur)
        return lines

    y = 0.935
    side.text(0.05, y, "Why", color=GOLD, fontsize=6.4, fontweight="bold", va="top")
    y -= 0.016
    for ln in wrap(B["why"], 34)[:3]:
        side.text(0.05, y, ln, color=WHITE, fontsize=5.5, va="top")
        y -= 0.014
    for raw in (B.get("why_lines") or [])[:5]:
        for ln in wrap(raw, 34)[:1]:
            side.text(0.05, y, "· " + ln, color="#cfd8dc", fontsize=5.1, va="top")
            y -= 0.013
    if B.get("named_targets"):
        y -= 0.002
        side.text(0.05, y, "Targets", color=GOLD, fontsize=6.2, fontweight="bold", va="top")
        y -= 0.015
        for tg in B["named_targets"][:3]:
            side.text(0.05, y, tg, color="#a5d6a7", fontsize=5.4, va="top")
            y -= 0.014
    y -= 0.002
    side.text(0.05, y, "Invalidation", color=GOLD, fontsize=6.2, fontweight="bold", va="top")
    y -= 0.015
    for ln in wrap(B["inv"], 34)[:2]:
        side.text(0.05, y, ln, color="#ef9a9a", fontsize=5.4, va="top")
        y -= 0.014
    if B.get("weak_alt"):
        y -= 0.002
        side.text(0.05, y, "Weak alt", color=GOLD, fontsize=6.2, fontweight="bold", va="top")
        y -= 0.015
        for ln in wrap(B["weak_alt"], 34)[:3]:
            side.text(0.05, y, ln, color="#ffe082", fontsize=5.3, va="top")
            y -= 0.013

    y -= 0.008
    side.plot([0.05, 0.95], [y + 0.006, y + 0.006], color="#333", lw=0.5, transform=side.transAxes, clip_on=False)
    # school rows
    state_col = {"confirm": "#66bb6a", "against": "#ef5350", "neutral": "#bdbdbd",
                 "no trade": "#9e9e9e", "n/a (not computed)": "#616161",
                 "n/a (experimental, off)": "#616161"}
    state_short = {"confirm": "CONFIRM", "against": "AGAINST", "neutral": "NEUTRAL",
                   "no trade": "—", "n/a (not computed)": "n/a",
                   "n/a (experimental, off)": "n/a"}
    # remaining space
    y0 = y - 0.01
    row_h = (y0 - 0.015) / 21
    for i, s in enumerate(B["schools"]):
        yy = y0 - i * row_h
        is_na = str(s["state"]).startswith("n/a")
        side.add_patch(FancyBboxPatch((0.04, yy - row_h * 0.72), 0.10, row_h * 0.62,
                                      boxstyle="round,pad=0.008,rounding_size=0.01",
                                      facecolor="#424242" if is_na else "#1b5e20",
                                      edgecolor="#9e9e9e" if is_na else "#66bb6a", lw=0.4,
                                      transform=side.transAxes, clip_on=False))
        side.text(0.09, yy - row_h * 0.40, "n/a" if is_na else "ON",
                  color="#eeeeee" if is_na else "#c8e6c9", fontsize=4.8, ha="center", va="center",
                  fontweight="bold", transform=side.transAxes)
        side.text(0.16, yy - row_h * 0.40, s["name"], color=WHITE, fontsize=5.7, va="center",
                  transform=side.transAxes)
        sc = state_col.get(s["state"], "#9e9e9e")
        side.text(0.97, yy - row_h * 0.28, state_short.get(s["state"], s["state"]), color=sc, fontsize=5.2,
                  ha="right", va="center", fontweight="bold", transform=side.transAxes)
        if s["note"]:
            note = s["note"][:36]
            side.text(0.16, yy - row_h * 0.68, note, color=DIM, fontsize=4.6, va="center",
                      transform=side.transAxes)

    out = OUT / "cfx_chart_real_v7.png"
    fig.savefig(out, dpi=100, facecolor=fig.get_facecolor())
    plt.close(fig)
    return out, start_c, last_c, n_buy, n_sell


# ──────────────────── Settings panel ────────────────────
# Only options that are actually wired in Python and/or cfx.pine.

SETTINGS_GROUPS = [
    ("Structure", [
        ("Swing length (internal)", "3"),
        ("EQH/EQL tolerance (ATR)", "0.10"),
        ("EQH/EQL confirm bars", "3"),
        ("Show BOS / CHoCH", "ON"),
        ("Show confirmed swings", "ON"),
        ("Sweep markers", "ON"),
    ]),
    ("FVG / OB / Breaker", [
        ("FVG min width (ATR)", "0.30"),
        ("FVG max age (bars)", "30"),
        ("Show unfilled FVG", "ON"),
        ("Show IFVG", "ON"),
        ("OB displacement min (ATR)", "1.50"),
        ("OB max age (bars)", "80"),
        ("Mitigation", "close"),
        ("OB volume label", "share of visible OBs"),
        ("Show order blocks", "ON"),
        ("Show breaker blocks", "ON"),
    ]),
    ("CISD / CHoCH", [
        ("CISD lookback", "40"),
        ("HTF CISD max age (4H bars)", "6"),
        ("CHoCH/CISD require body close", "ON"),
        ("Show HTF CISD / CRT zones", "ON"),
        ("HTF for CISD/CRT", "4H"),
    ]),
    ("Trend filter (Pine VWMA / HA)", [
        ("Enable VWMA-HA trend gate (Pine)", "ON"),
        ("VWMA length", "120"),
        ("Trend ATR band (wired)", "20 / 0.5"),
        ("HA source for the filter only", "ON"),
    ]),
    ("Risk / RR", [
        ("ATR length", "14"),
        ("SL buffer (ATR)", "0.15"),
        ("Hard gate: RR1 minimum", "1.5"),
        ("Spread model", "0.30 USD"),
        ("Reject if cost_R >", "0.20"),
        ("Max trades on chart", "2"),
        ("Fade closed trades", "ON"),
        ("News blackout hook", "manual / no feed"),
    ]),
    ("Killzones (America/New_York)", [
        ("Require killzone for new signals", "ON"),
        ("Asia", "20:00–00:00"),
        ("London", "02:00–05:00"),
        ("New York AM", "07:00–10:00"),
    ]),
    ("Sessions (one NY clock)", [
        ("Session shading", "ON"),
        ("Session high / low", "ON"),
        ("Asia", "19:00–02:00 NY"),
        ("London", "02:00–09:00 NY"),
        ("New York", "08:00–17:00 NY"),
    ]),
    ("Multi-timeframe", [
        ("Daily + 4H veto (both against → WAIT)", "ON"),
        ("4H + 1H + current alignment (computed)", "ON"),
        ("HTF for CISD/CRT boxes", "4H"),
    ]),
    ("SMT / trend line", [
        ("Show trend line", "ON"),
        ("Show SMT line", "ON"),
        ("SMT correlated symbol", "DXY"),
        ("Invert SMT symbol (DXY vs gold)", "ON"),
    ]),
    ("XPIX MTF liquidity levels", [
        ("15M high/low (also on 15m chart)", "ON  •  #ff9800"),
        ("1H high/low", "ON  •  #4caf50"),
        ("5M / 4H / D1 / W1", "OFF"),
        ("Nearer edge only + 70% hysteresis", "ON"),
        ("Hide if both edges > 15 ATR", "ON"),
        ("Line length (bars right)", "30"),
        ("Lookahead", "off + last closed bar"),
    ]),
    ("Fibonacci (live retracement only)", [
        ("Draw only if 0 < ret < 1", "ON"),
        ("Style", "thin dotted, clipped from boxes"),
        ("OTE zone", "0.62–0.79  (mark 0.705)"),
        ("Golden pocket", "0.618–0.65"),
        ("Sweep then displacement then OTE", "AND"),
        ("Extra levels", "0.382 / 0.786 / 0.886"),
        ("ICT extensions (targets)", "-0.27 / -0.62 / -1"),
        ("Min impulse length", "1.5 ATR"),
    ]),
    ("Sequential engine + oscillator", [
        ("Pipeline", "veto → POI → sweep → CISD/CHoCH → limit"),
        ("Limit fill", "FVG/OB mid (CE)"),
        ("Merged hook (counts as 1)", "4-stoch AND RSI(1) MACD AND RSI(1) Stoch"),
        ("Stoch sets", "(1,9,8) (1,6,3) (1,5,7) (1,8,8)"),
        ("Dots", "only when the pipeline fills"),
        ("Adaptive zones", "lookback 200, q 0.15 / 0.85"),
        ("ATR band vs median", "0.55–2.20"),
        ("Cooldown (15m)", "8 bars"),
    ]),
    ("Display", [
        ("Arabic labels (Pine)", "ON"),
        ("Show premium / discount 50%", "ON"),
        ("Show VP POC / VAH / VAL", "ON  •  OHLCV estimate"),
        ("Show session VWAP", "ON"),
        ("Divergence dots (RSI / MACD / Vol)", "ON  •  one shared function"),
        ("Chart", "standalone CFX, not the TIA tab"),
    ]),
    ("Schools", [
        ("SMC / ICT / CRT-CISD / SMT", "ON"),
        ("Dow / Fibonacci / VP / VWAP", "ON"),
        ("Pivots / Ichimoku / MAs / S&D", "ON"),
        ("PA / Patterns / Momentum / Sessions", "ON"),
        ("Intermarket (DXY)", "ON"),
        ("Elliott zigzag labeler", "OFF  •  experimental"),
        ("Gann", "not implemented"),
        ("Harmonic", "not implemented"),
        ("Wyckoff", "not implemented"),
        ("School score vs", "candidate trade, or no trade"),
    ]),
]


def render_settings():
    plt.rcParams["font.family"] = "DejaVu Sans"
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100, facecolor=BG)
    fig.text(0.025, 0.965, "CFX   •   Settings", color=GOLD, fontsize=18, fontweight="bold", va="top")
    fig.text(0.025, 0.932, "Confluence X  —  standalone overlay (not the TIA tab)  •  only wired options  •  research draft, no edge claimed",
             color=DIM, fontsize=8.5, va="top")

    groups = SETTINGS_GROUPS
    by_name = {g[0]: g for g in groups}
    col_groups = [
        [by_name[k] for k in ("Structure", "FVG / OB / Breaker", "CISD / CHoCH", "Trend filter (Pine VWMA / HA)")],
        [by_name[k] for k in ("Risk / RR", "Killzones (America/New_York)", "Sessions (one NY clock)", "Multi-timeframe")],
        [by_name[k] for k in ("SMT / trend line", "XPIX MTF liquidity levels", "Fibonacci (live retracement only)", "Display")],
        [by_name[k] for k in ("Sequential engine + oscillator", "Schools")],
    ]

    lefts = [0.02, 0.265, 0.51, 0.755]
    width = 0.23
    top = 0.90
    bottom = 0.04

    for c, glist in enumerate(col_groups):
        units = sum(1.35 + 0.52 * len(g[1]) for g in glist) + 0.4 * (len(glist) - 1)
        y = top
        avail = top - bottom
        scale = avail / units
        for title, rows in glist:
            h = (1.35 + 0.52 * len(rows)) * scale
            x = lefts[c]
            ax = fig.add_axes([x, y - h, width, h])
            ax.set_facecolor("#101010")
            for sp in ax.spines.values():
                sp.set_color("#3a3a3a")
                sp.set_linewidth(0.6)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.add_patch(Rectangle((0, 0.92), 1, 0.08, facecolor="#1a1508", transform=ax.transAxes, zorder=0))
            ax.text(0.04, 0.96, title, color=GOLD, fontsize=7.2, fontweight="bold", va="center", transform=ax.transAxes)
            n = len(rows)
            for i, (k, v) in enumerate(rows):
                yy = 0.90 - (i + 0.5) * (0.86 / n)
                ax.text(0.04, yy, k, color="#cfcfcf", fontsize=5.8, va="center", transform=ax.transAxes)
                on = str(v).startswith("ON")
                off = str(v).startswith("OFF") or str(v).startswith("not implemented")
                col = "#81c784" if on else ("#e57373" if off else GOLD)
                ax.text(0.96, yy, v, color=col, fontsize=5.8, va="center", ha="right", transform=ax.transAxes)
            y = y - h - 0.012

    fig.text(0.025, 0.018, "Only inputs wired in cfx.pine and/or the Python engine. Elliott is implemented as an experimental zigzag (off). Gann / Harmonic / Wyckoff are not implemented.",
             color=DIM, fontsize=6.5)
    out = OUT / "cfx_settings_v7.png"
    fig.savefig(out, dpi=100, facecolor=fig.get_facecolor())
    plt.close(fig)
    return out




def render_osc_closeup(B):
    """Larger single-pane close-up of Stoch(5,3,3) + RSI(14) + MACD slope context."""
    from cfx_osc_combo import add_combo_oscillators, collect_combo_dots, STOCH_OS, STOCH_OB, STOCH_MID
    from cfx_lib import cairo
    d15 = B["mt5_osc"] if B.get("mt5_osc") is not None else add_combo_oscillators(B["d15"])
    vis_start, vis_end = B["vis_start"], B["vis_end"]
    viso = d15.iloc[vis_start:vis_end + 1]
    nvis = len(viso)
    xs = np.arange(nvis)
    dots = B.get("mt5_dots") or collect_combo_dots(d15, vis_start, vis_end, variant="B")
    fig, ax = plt.subplots(figsize=(19.2, 6.4), dpi=100, facecolor=BG)
    ax.set_facecolor(BG)
    ax.tick_params(colors=DIM, labelsize=7)
    for sp in ax.spines.values():
        sp.set_color("#222")
    ax.grid(True, color=GRID, lw=0.35)
    ax.set_ylim(-2, 102)
    ax.set_xlim(-0.8, nvis - 0.2)

    ax.axhline(STOCH_OS, color=TEAL, lw=0.9, label="15")
    ax.axhline(STOCH_OB, color=RED, lw=0.9, label="85")
    ax.axhline(STOCH_MID, color="#555", lw=0.5)
    ax.axhline(10, color="#1976d2", lw=0.4, ls=":", alpha=0.7)
    ax.axhline(90, color="#c62828", lw=0.4, ls=":", alpha=0.7)
    ax.plot(xs, viso["st_k"].to_numpy(float), color="#42a5f5", lw=1.4, label="Stoch %K (5,3,3 Low/High SMA)")
    ax.plot(xs, viso["st_d"].to_numpy(float), color="#ef9a9a", lw=1.15, label="Stoch %D")
    ax.plot(xs, viso["rsi14"].to_numpy(float), color="#b39ddb", lw=0.9, alpha=0.75, label="RSI(14)")
    # MACD main is in price units — show sign as a thin histogram scaled into 40–60
    macd = viso["macd"].to_numpy(float)
    macd_s = np.clip(50.0 + macd * 2.0, 0, 100)  # display-only, not used for signals
    ax.plot(xs, macd_s, color="#9e9e9e", lw=0.8, ls="-.", alpha=0.7, label="MACD(12,26,1) main (scaled view)")
    ax.legend(loc="upper right", fontsize=7, facecolor="#111", labelcolor=WHITE, ncol=3, framealpha=0.75)
    ax.set_ylabel("0–100", color=DIM, fontsize=8)
    ax.set_title("CFX oscillator  •  Stoch(5,3,3) confirmed by RSI(14) + MACD(12,26,1)  •  variant B  •  no edge claimed",
                 color=GOLD, fontsize=11, loc="left")

    vis = B["d15"].iloc[vis_start:vis_end + 1]
    for d in dots:
        xi = d["i"] - vis_start
        col = TEAL if d["side"] == "buy" else RED
        lab = "BUY" if d["side"] == "buy" else "SELL"
        y = d.get("st_k") if d.get("st_k") is not None else 50
        ax.scatter([xi], [y], marker="o", s=36, color=col, edgecolors="white", lw=0.4, zorder=6)
        ax.text(xi, 4 if d["side"] == "sell" else 96, lab, color=col, fontsize=6.2,
                ha="center", va="bottom" if d["side"] == "buy" else "top", zorder=7)

    tick_pos, tick_lab, last_day = [], [], None
    for i, ts in enumerate(vis.index):
        day = cairo(ts).date()
        if day != last_day:
            tick_pos.append(i)
            tick_lab.append(cairo(ts).strftime("%a %d %b\n%H:%M"))
            last_day = day
    ax.set_xticks(tick_pos)
    ax.set_xticklabels(tick_lab, color=DIM, fontsize=7)
    fig.text(0.04, 0.015,
             "BUY = Stoch %K crosses above %D after touching ≤15 in the last 3 bars, RSI(14) turning up, MACD main rising.   "
             "SELL = %K crosses below %D after touching ≥85 in the last 3 bars, RSI turning down, MACD main falling.   "
             "MACD signal period is 1 so histogram ≈ 0; slope of the main line is the confirmation.   "
             "yfinance GC=F 15m  •  Research only, no edge claimed",
             color=DIM, fontsize=6.6)
    out = OUT / "cfx_osc_v7.png"
    fig.savefig(out, dpi=100, facecolor=fig.get_facecolor())
    plt.close(fig)
    return out


def main():
    print("Computing CFX on cached GC=F …")
    B = build_bundle()
    chart, start_c, last_c, n_buy, n_sell = render_chart(B)
    osc = render_osc_closeup(B)
    settings = render_settings()

    def td(t):
        d15 = B["d15"]
        return {
            "side": t.side,
            "signal_cairo": cairo_label(d15.index[t.signal_i]),
            "fill_cairo": cairo_label(d15.index[t.fill_i]),
            "close_cairo": cairo_label(d15.index[t.close_i]) if t.close_i is not None else None,
            "entry": t.entry, "sl": t.sl, "tp1": t.tp1, "tp2": t.tp2,
            "tp1_name": getattr(t, "tp1_name", ""), "tp2_name": getattr(t, "tp2_name", ""),
            "rr1": t.rr1, "rr2": t.rr2, "atr": t.atr, "cost_R": getattr(t, "cost_R", None),
            "outcome": t.outcome, "reason": t.reason,
            "poi_kind": getattr(t, "poi_kind", ""),
            "invalidation": t.invalidation,
            "weak_alt": getattr(t, "weak_alt", ""),
        }

    bt = summarize_backtest(B["trades_all"], B["d15"].index[0], B["d15"].index[-1])
    meta = {
        "chart": str(chart),
        "osc_closeup": str(osc),
        "mt5_dots": B.get("mt5_dots"),
        "mt5_sanity": B.get("mt5_sanity"),
        "cisd_draw": B.get("cisd_draw"),
        "settings": str(settings),
        "window_start_cairo": str(start_c),
        "window_end_cairo": str(last_c),
        "last_price": B["last_close"],
        "last_atr": B["last_atr"],
        "forming": B["forming"],
        "bias4h": B["bias4h"],
        "bias_d": B.get("bias_d"),
        "struct_dir": B["struct_dir"],
        "xpix": {k: {kk: (str(vv) if hasattr(vv, "isoformat") else vv) for kk, vv in v.items()}
                 for k, v in B["xpix"].items()},
        "impulse": None if not B["impulse"] else {k: ({str(a): b for a, b in v.items()} if k in ("levels", "extensions") else v)
                                                  for k, v in B["impulse"].items()},
        "eq": B["eq"],
        "pdhl": {k: B["pdhl"].get(k) for k in ("pdh", "pdl", "pdh_swept", "pdl_swept", "pdh_near", "pdl_near")},
        "fvgs_unfilled": B["fvgs_unfilled"],
        "ifvgs": B["ifvgs"],
        "obs": B["obs"],
        "breakers": B["breakers"],
        "divs": B["divs"],
        "cisd": B["cisd"],
        "crt": B["crt"],
        "htf_boxes": B.get("htf_boxes"),
        "smt": B["smt"],
        "pd_mid": B["pd_mid"],
        "vp": B["vp"],
        "vwap": B["vwap_now"],
        "ichi": B["ichi"],
        "elliott": B.get("elliott"),
        "pipeline_signals_in_window": {"buys": n_buy, "sells": n_sell},
        "trades_shown": [td(t) for t in B["shown"]],
        "trades_all": [td(t) for t in B["trades_all"]],
        "backtest": bt,
        "why": B["why"],
        "why_lines": B.get("why_lines"),
        "named_targets": B.get("named_targets"),
        "inv": B["inv"],
        "weak_alt": B.get("weak_alt"),
        "schools": B["schools"],
        "n_conf": B["n_conf"],
        "n_against": B["n_against"],
        "n_computed": B["n_computed"],
        "n_no_trade": B.get("n_no_trade"),
        "news_feed": B.get("news_feed"),
        "data": "yfinance GC=F gold futures (not spot XAUUSD)",
    }
    (OUT / "cfx_chart_meta_v7.json").write_text(json.dumps(meta, indent=2, default=str))
    print("CHART", chart, chart.stat().st_size)
    print("SETTINGS", settings, settings.stat().st_size)
    print("window", start_c, "->", last_c)
    print("last", B["last_close"], "bias4h", B["bias4h"], "biasD", B.get("bias_d"))
    print("trades shown", [td(t) for t in B["shown"]])
    print("why", B["why"])
    print("conf", B["n_conf"], "against", B["n_against"], "no_trade", B.get("n_no_trade"))
    print("BACKTEST", json.dumps(bt, indent=2))
    print("n_all_trades", len(B["trades_all"]))


if __name__ == "__main__":
    main()
