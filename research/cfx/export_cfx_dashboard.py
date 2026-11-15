#!/usr/bin/env python3
"""Export CFX bundle to a standalone interactive dashboard (local files only)."""
from __future__ import annotations

import sys
sys.path.insert(0, '/workspace/cfx')
sys.path.insert(0, '/workspace/indicator_research/fused_osc')

import json
from pathlib import Path

import numpy as np
import pandas as pd

from cfx_lib import cairo, cairo_label, load_csv, session_flags
from cfx_display import session_name_at
from cfx_osc_combo import add_combo_oscillators, collect_combo_dots

OUT = Path("/workspace/cfx/dashboard")


def _unix(ts):
    t = pd.Timestamp(ts)
    if t.tzinfo is None:
        t = t.tz_localize("America/New_York")
    return int(t.tz_convert("UTC").timestamp())


def _ohlc(df):
    rows = []
    for ts, r in df.iterrows():
        rows.append({
            "time": _unix(ts),
            "open": round(float(r["open"]), 3),
            "high": round(float(r["high"]), 3),
            "low": round(float(r["low"]), 3),
            "close": round(float(r["close"]), 3),
            "volume": int(r["volume"]) if "volume" in r and np.isfinite(r["volume"]) else 0,
        })
    return rows



def _safe_idx(d15, i):
    i = int(i)
    if i < 0 or i >= len(d15):
        return None
    return i


def _smt_payload(B, d15):
    smt = B.get("smt") or {}
    i1, i2 = _safe_idx(d15, smt.get("x1", -1)), _safe_idx(d15, smt.get("x2", -1))
    if i1 is None or i2 is None:
        return None
    return {
        "t1": _unix(d15.index[i1]), "t2": _unix(d15.index[i2]),
        "y1": round(float(smt["y1"]), 3), "y2": round(float(smt["y2"]), 3),
        "note": smt.get("note"),
    }


def _crt_payload(B, d15):
    crt = B.get("crt") or {}
    i0, i1 = _safe_idx(d15, crt.get("i0", -1) if crt.get("i0") is not None else -1), \
             _safe_idx(d15, crt.get("i1", -1) if crt.get("i1") is not None else -1)
    if i0 is None or i1 is None:
        return None
    return {
        "start": _unix(d15.index[i0]), "end": _unix(d15.index[i1]),
        "high": round(float(crt["high"]), 3), "low": round(float(crt["low"]), 3),
    }


def _level_payload(B):
    levels = []
    vp = B.get("vp") or {}
    if vp.get("poc") is not None:
        levels.append({"name": f"POC {vp['poc']:.1f}", "price": round(float(vp["poc"]), 3), "color": "#d4af37"})
    if vp.get("vah") is not None:
        levels.append({"name": f"VAH {vp['vah']:.1f}", "price": round(float(vp["vah"]), 3), "color": "#8a8a8a"})
    if vp.get("val") is not None:
        levels.append({"name": f"VAL {vp['val']:.1f}", "price": round(float(vp["val"]), 3), "color": "#8a8a8a"})
    if B.get("vwap_now") is not None:
        levels.append({"name": f"VWAP {B['vwap_now']:.1f}", "price": round(float(B["vwap_now"]), 3), "color": "#b39ddb"})
    mid = (B.get("pd_mid") or {})
    if mid.get("mid") is not None:
        zone = mid.get("zone") or ""
        levels.append({"name": f"EQ 50% {mid['mid']:.1f}  ({zone})",
                       "price": round(float(mid["mid"]), 3), "color": "#d4af37"})
    pdhl = B.get("pdhl") or {}
    if pdhl.get("pdh") is not None and (pdhl.get("pdh_near") or pdhl.get("pdh_swept")):
        levels.append({"name": f"PDH {pdhl['pdh']:.1f}", "price": round(float(pdhl["pdh"]), 3), "color": "#ff9800"})
    if pdhl.get("pdl") is not None and (pdhl.get("pdl_near") or pdhl.get("pdl_swept")):
        tag = f"PDL {pdhl['pdl']:.1f}" + ("  swept" if pdhl.get("pdl_swept") else "")
        levels.append({"name": tag, "price": round(float(pdhl["pdl"]), 3), "color": "#ff9800"})
    # session H/L stubs intentionally omitted (v7): sessions are boxes only
    return levels


def export_dashboard(B) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    d15 = B["d15"]
    vis_start, vis_end = B["vis_start"], B["vis_end"]
    vis = d15.iloc[vis_start:vis_end + 1]
    t0, t1 = vis.index[0], vis.index[-1]

    # 5m / 1h aligned to the same window
    try:
        d5 = load_csv("gc_5m.csv")
        d5 = d5[(d5.index >= t0) & (d5.index <= t1 + pd.Timedelta(minutes=14))]
    except Exception:
        d5 = pd.DataFrame()
    d1h = B.get("raw1h")
    if d1h is None or getattr(d1h, "empty", True):
        d1h = load_csv("gc_1h.csv")
    d1h = d1h[(d1h.index >= t0) & (d1h.index <= t1)]

    def _line(series):
        rows = []
        for ts, v in series.items():
            rows.append({"time": _unix(ts),
                         "value": None if not np.isfinite(v) else round(float(v), 3)})
        return rows

    d15o = add_combo_oscillators(d15)
    vis_o = d15o.iloc[vis_start:vis_end + 1]
    osc15 = _line(vis_o["st_k"])
    osc_st_k = _line(vis_o["st_k"])
    osc_st_d = _line(vis_o["st_d"])
    osc_rsi = _line(vis_o["rsi14"])
    sma77 = _line(vis_o["sma77"])
    sma144 = _line(vis_o["sma144"])

    osc5 = []
    osc5_extra = {}
    if len(d5) > 30:
        try:
            d5o = add_combo_oscillators(d5.copy())
            osc5 = _line(d5o["st_k"])
            osc5_extra = {
                "st_k": _line(d5o["st_k"]),
                "st_d": _line(d5o["st_d"]),
                "rsi": _line(d5o["rsi14"]),
            }
        except Exception as exc:
            print("5m osc skip", exc)

    def cisd_payload(ev, tf):
        s, c = ev.get("start_i"), ev.get("conf_i")
        if s is None or c is None:
            return None
        if s >= len(d15) or c >= len(d15):
            return None
        return {
            "tf": tf, "side": ev["side"], "level": round(float(ev["level"]), 3),
            "start": _unix(d15.index[int(s)]), "end": _unix(d15.index[int(c)]),
            "startLabel": cairo_label(d15.index[int(s)]),
            "endLabel": cairo_label(d15.index[int(c)]),
            "span": int(c) - int(s),
        }

    cisd = [c for ev in (B.get("cisd_draw") or []) if (c := cisd_payload(ev, ev.get("tf", "15m")))]
    for bx in B.get("htf_boxes") or []:
        if bx.get("i0") is None or bx.get("i1") is None:
            continue
        cisd.append({
            "tf": "4H", "side": bx.get("side"), "level": round(float(bx["level"]), 3),
            "start": _unix(d15.index[int(bx["i0"])]), "end": _unix(d15.index[int(bx["i1"])]),
            "startLabel": cairo_label(d15.index[int(bx["i0"])]),
            "endLabel": cairo_label(d15.index[int(bx["i1"])]),
        })

    sessions = []
    for box in B.get("sess_boxes") or []:
        sessions.append({
            "key": box["key"],
            "name": {"asia": "Asia", "london": "London", "ny": "NY"}[box["key"]],
            "start": _unix(d15.index[int(box["start"])]),
            "end": _unix(d15.index[int(box["end"])]),
            "high": round(float(box["high"]), 3),
            "low": round(float(box["low"]), 3),
        })

    def zone_payload(z, kind):
        i0 = int(z.get("i", z.get("start", vis_start)))
        i0 = max(vis_start, min(i0, vis_end))
        return {
            "kind": kind, "side": z.get("side"),
            "lo": round(float(z["lo"]), 3), "hi": round(float(z["hi"]), 3),
            "start": _unix(d15.index[i0]),
            "end": _unix(d15.index[vis_end]),
        }

    fvgs = [zone_payload(g, "FVG") for g in (B.get("fvgs_unfilled") or [])[:6]]
    obs = [zone_payload(z, "OB") for z in (B.get("obs") or [])]
    brks = [zone_payload(z, "BRK") for z in (B.get("breakers") or [])]

    stories = B.get("trade_stories") or []
    trades = []
    for i, st in enumerate(stories):
        rec = dict(st)
        rec["id"] = i
        rec["signalTs"] = _unix(d15.index[st["signal_i"]])
        rec["fillTs"] = _unix(d15.index[st["fill_i"]])
        rec["closeTs"] = None if st["close_i"] is None else _unix(d15.index[st["close_i"]])
        trades.append(rec)

    dots = []
    for d in collect_combo_dots(d15o, vis_start, vis_end, variant="B"):
        val = d.get("st_k")
        dots.append({
            "time": _unix(d15.index[d["i"]]), "side": d["side"],
            "value": None if val is None else round(float(val), 3),
            "price": d["price"], "label": cairo_label(d15.index[d["i"]]),
            "after": d.get("after"), "fired": d.get("fired") or [],
        })

    struct = []
    for e in B.get("events") or []:
        if not (vis_start <= e["i"] <= vis_end):
            continue
        sw = e.get("swing_i", e["i"])
        if sw < 0 or sw >= len(d15):
            continue
        struct.append({
            "kind": e["kind"], "dir": int(e["dir"]), "level": round(float(e["level"]), 3),
            "end": _unix(d15.index[int(e["i"])]),
            "start": _unix(d15.index[int(sw)]),
        })

    markers = []
    for m in B.get("school_markers") or []:
        if not (vis_start <= m["i"] <= vis_end):
            continue
        markers.append({
            "time": _unix(d15.index[m["i"]]),
            "school": m["school"], "tag": m["tag"], "side": m["side"],
            "kind": m.get("kind"), "y": m["y"],
        })

    alerts = []
    for st in trades:
        alerts.append({
            "time": st["fill_time"], "ts": st["fillTs"],
            "type": "trade", "tradeId": st["id"],
            "title": st["title"], "title_ar": st["title_ar"],
            "body": st["story"], "side": st["side"], "outcome": st["outcome"],
        })
    for ev in (B.get("cisd_draw") or [])[-8:]:
        alerts.append({
            "time": cairo_label(d15.index[ev["conf_i"]]),
            "ts": _unix(d15.index[ev["conf_i"]]),
            "type": "cisd", "tradeId": None,
            "title": f"CISD {ev['side']} {ev['level']:.1f}",
            "title_ar": "تغيّر حالة التسليم",
            "body": f"{ev['side']} CISD {ev['level']:.1f} from {cairo_label(d15.index[ev['start_i']])} to {cairo_label(d15.index[ev['conf_i']])}",
            "side": "buy" if ev["side"] == "bull" else "sell",
        })

    last_ts = vis.index[-1]
    sess_now = session_name_at(last_ts)
    payload = {
        "meta": {
            "symbol": "GC=F",
            "label": "Gold futures",
            "last": round(float(B["last_close"]), 3),
            "atr": round(float(B["last_atr"]), 3),
            "bias4h": B.get("bias4h"),
            "bias_d": B.get("bias_d"),
            "struct": B.get("struct_dir"),
            "session": sess_now,
            "sessionHint": B.get("sess_hint"),
            "windowStart": cairo_label(t0),
            "windowEnd": cairo_label(t1),
            "windowStartTs": _unix(t0),
            "windowEndTs": _unix(t1),
            "xpix": {k: {"price": round(float(v["price"]), 3), "tag": v.get("tag", k)}
                     for k, v in (B.get("xpix") or {}).items()},
            "pdh": None if not B.get("pdhl") else B["pdhl"].get("pdh"),
            "pdl": None if not B.get("pdhl") else B["pdhl"].get("pdl"),
            "note": "Research only. No edge claimed. yfinance GC=F gold futures, not spot XAUUSD.",
        },
        "candles": {
            "5m": _ohlc(d5) if len(d5) else [],
            "15m": _ohlc(vis),
            "1H": _ohlc(d1h) if len(d1h) else [],
        },
        "osc": {
            "15m": osc15, "5m": osc5, "dots": dots,
            "st_k": osc_st_k, "st_d": osc_st_d, "rsi": osc_rsi,
            "5m_extra": osc5_extra, "variant": "B",
        },
        "sma77": sma77, "sma144": sma144,
        "struct": struct,
        "cisd": cisd,
        "sessions": sessions,
        "fvgs": fvgs, "obs": obs, "breakers": brks,
        "trades": trades,
        "markers": markers,
        "alerts": alerts,
        "schools": B.get("schools") or [],
        "smt": _smt_payload(B, d15),
        "crt": _crt_payload(B, d15),
        "levels": _level_payload(B),
    }

    data_js = OUT / "data.js"
    data_js.write_text("window.CFX_DATA = " + json.dumps(payload, ensure_ascii=False) + ";\n")
    print("DASH_DATA", data_js, data_js.stat().st_size,
          "cisd", len(cisd), "trades", len(trades), "dots", len(dots), "markers", len(markers))
    return OUT / "index.html"


if __name__ == "__main__":
    from cfx_lib import build_bundle
    B = build_bundle()
    print(export_dashboard(B))
