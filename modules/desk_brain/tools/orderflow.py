"""Order flow for crypto, from Binance public market data (free, no key).

Why crypto only: order flow needs to know whether each trade hit the bid or lifted the ask.
Binance publishes that for every trade. Spot FX has no central tape at all, and futures
tick data (CME) is paid, so for FX / gold / indices this tool reports "not available"
instead of inventing numbers.

  delta     = aggressive buy volume − aggressive sell volume
              (1-minute klines field 9 "taker buy base volume": delta = 2·takerBuy − volume)
  CVD       = cumulative delta over the window
  footprint = recent aggTrades bucketed by price: buy vs sell volume at each level
  walls     = largest resting bid/ask sizes in the order book (depth snapshot)
  absorption= a 1-minute bar with ≥2× average volume, heavily one-sided delta, but a body
              under 25% of the average range: aggressive orders were absorbed by passive ones

Spoofing: a single snapshot cannot show it, so we keep a small ring buffer of recent book
snapshots per symbol and run a conservative heuristic (detect_spoofing) over them. It is a
heuristic on sampled snapshots (one per ~30 s fetch), not proof; reliable detection needs a
real WebSocket @depth stream.
"""
from __future__ import annotations

import logging
import time
import zlib
from collections import deque
from statistics import median

import numpy as np
import pandas as pd
import requests

from ..config import DATA_MODE, UNIVERSE
from ..data.cache import cached

log = logging.getLogger("desk.orderflow")
HOSTS = ["https://api.binance.com", "https://data-api.binance.vision"]


_SNAP_MAX = 60
_SNAPS: dict[str, deque] = {}
_TRADES: dict[str, deque] = {}
_TRADE_IDS: dict[str, set] = {}


def _record(sym: str, book: dict, agg: list, ts: float | None = None) -> None:
    """Append a book snapshot (deduped vs the previous one) and any new aggTrades for sym."""
    ts = time.time() if ts is None else ts
    snap = {"ts": ts, "bids": [list(x) for x in book["bids"]], "asks": [list(x) for x in book["asks"]]}
    buf = _SNAPS.setdefault(sym, deque(maxlen=_SNAP_MAX))
    if not buf or buf[-1]["bids"] != snap["bids"] or buf[-1]["asks"] != snap["asks"]:
        buf.append(snap)
    tb, seen = _TRADES.setdefault(sym, deque(maxlen=5000)), _TRADE_IDS.setdefault(sym, set())
    for x in agg:
        if x["a"] in seen:
            continue
        seen.add(x["a"])
        tb.append({"ts": x["T"] / 1000.0, "price": float(x["p"]), "qty": float(x["q"]),
                   "side": "sell" if x["m"] else "buy", "id": x["a"]})
    if len(seen) > 20000:  # bound memory: keep only ids still in the trade buffer
        seen.clear()
        seen.update(t["id"] for t in tb)


def detect_spoofing(snapshots: list[dict], trades: list[dict], mid_band_pct: float = 0.5) -> dict:
    """Conservative spoof heuristic over time-ordered book snapshots. See module note."""
    note = ("Heuristic on sampled book snapshots, not proof: walls pulled between samples, or "
            "quotes that never rest long enough to be sampled, are invisible. A real depth "
            "stream (WebSocket @depth) is needed for reliable detection.")
    snaps = [s for s in snapshots if s.get("bids") and s.get("asks")]
    if len(snaps) < 3:
        return {"candidates": [], "flicker": 0, "verdict": "insufficient", "note": "needs more book snapshots"}
    band = mid_band_pct / 100.0
    # per snapshot: mid, {(side, price): qty} of walls, full qty maps
    info = []
    for s in snaps:
        mid = (max(p for p, _ in s["bids"]) + min(p for p, _ in s["asks"])) / 2
        qtys = {"bid": {float(p): float(q) for p, q in s["bids"]}, "ask": {float(p): float(q) for p, q in s["asks"]}}
        allq = list(qtys["bid"].values()) + list(qtys["ask"].values())
        med = median(allq) if allq else 0.0
        walls = {}
        for side in ("bid", "ask"):
            for p, q in qtys[side].items():
                if med > 0 and q >= 5 * med and abs(p - mid) / mid <= band:
                    walls[(side, p)] = q
        info.append({"ts": float(s["ts"]), "mid": mid, "qtys": qtys, "walls": walls})
    keys = {k for i in info for k in i["walls"]}
    candidates, flicker = [], 0
    for side, price in sorted(keys):
        runs, cur = [], None
        for idx, i in enumerate(info):
            if (side, price) in i["walls"]:
                if cur is None:
                    cur = [idx, idx]
                    runs.append(cur)
                else:
                    cur[1] = idx
            else:
                cur = None
        if len(runs) >= 2:
            flicker += len(runs) - 1
        for a, b in runs:
            if b - a + 1 < 2 or b + 1 >= len(info):
                continue  # too short, or still standing at the end (not removed)
            size = max(info[j]["walls"][(side, price)] for j in range(a, b + 1))
            after = info[b + 1]["qtys"][side].get(price, 0.0)
            if after > 0.2 * size:
                continue  # not pulled (drop <= 80%)
            t0, t1 = info[a]["ts"], info[b + 1]["ts"]
            near = min(abs(price - info[j]["mid"]) / info[j]["mid"] for j in range(a, b + 2))
            if near > 0.001:
                continue  # price never approached the wall: nothing to bait
            want = "sell" if side == "bid" else "buy"  # aggressors that would eat the wall
            filled = sum(float(t["qty"]) for t in trades
                         if t0 <= float(t["ts"]) <= t1 and t.get("side") == want
                         and (float(t["price"]) <= price if side == "bid" else float(t["price"]) >= price))
            pct = filled / size
            if pct < 0.2:
                candidates.append({"side": side, "price": price, "size": round(size, 6),
                                   "lived_s": round(info[b]["ts"] - t0, 1), "filled_pct": round(pct * 100, 1),
                                   "ts_removed": t1})
    if len(candidates) >= 2 or (candidates and flicker >= 2):
        verdict = "likely"
    elif candidates or flicker >= 3:
        verdict = "possible"
    else:
        verdict = "none"
    return {"candidates": candidates, "flicker": flicker, "verdict": verdict, "note": note}


def _spoofing(sym: str, src: str, book: dict) -> dict:
    if src == "demo":  # deterministic, never touches the live buffer
        snaps = [{"ts": 1000.0 + 30 * i, **book} for i in range(5)]
        out = detect_spoofing(snaps, [])
        out["note"] = "DEMO: synthetic static snapshots, not real market data. " + out["note"]
        return out
    snaps = list(_SNAPS.get(sym, ()))
    if len(snaps) < 3:
        return {"verdict": "insufficient", "note": "needs more book snapshots"}
    return detect_spoofing(snaps, list(_TRADES.get(sym, ())))


def _get(path: str, params: dict):
    last = None
    for h in HOSTS:
        try:
            r = requests.get(h + path, params=params, timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception as e:  # geo-block, rate limit, network
            last = e
    raise RuntimeError(last)


def _demo(sym: str) -> tuple[pd.DataFrame, list, dict]:
    rng = np.random.default_rng(zlib.crc32(sym.encode()))
    n = 240
    base = 90000.0 if sym.startswith("BTC") else 3200.0
    close = base * np.exp(np.cumsum(rng.normal(0, 0.0008, n)))
    vol = rng.gamma(2, 5, n)
    buy = vol * rng.uniform(0.3, 0.7, n)
    idx = pd.date_range(end=pd.Timestamp.now(tz="UTC").floor("min"), periods=n, freq="1min")
    k = pd.DataFrame({"Open": np.r_[close[0], close[:-1]], "High": close * 1.0006, "Low": close * 0.9994,
                      "Close": close, "Volume": vol, "TakerBuy": buy}, index=idx)
    px = close[-1]
    trades = [(px * (1 + rng.normal(0, 0.0007)), rng.gamma(1.5, 0.05), bool(rng.random() < 0.5)) for _ in range(1000)]
    book = {"bids": [[px * (1 - i * 0.0002), rng.gamma(2, 2)] for i in range(1, 200)],
            "asks": [[px * (1 + i * 0.0002), rng.gamma(2, 2)] for i in range(1, 200)]}
    return k, trades, book


def _fetch(sym: str) -> tuple[pd.DataFrame, list, dict, str]:
    def go():
        if DATA_MODE != "demo":
            try:
                kl = _get("/api/v3/klines", {"symbol": sym, "interval": "1m", "limit": 240})
                k = pd.DataFrame({"Open": [float(x[1]) for x in kl], "High": [float(x[2]) for x in kl],
                                  "Low": [float(x[3]) for x in kl], "Close": [float(x[4]) for x in kl],
                                  "Volume": [float(x[5]) for x in kl], "TakerBuy": [float(x[9]) for x in kl]},
                                 index=pd.to_datetime([x[0] for x in kl], unit="ms", utc=True))
                at = _get("/api/v3/aggTrades", {"symbol": sym, "limit": 1000})
                trades = [(float(x["p"]), float(x["q"]), bool(x["m"])) for x in at]  # m=True → seller was aggressor
                book = _get("/api/v3/depth", {"symbol": sym, "limit": 500})
                book = {s: [[float(p), float(q)] for p, q in book[s]] for s in ("bids", "asks")}
                try:
                    _record(sym, book, at)
                except Exception as e:  # never let bookkeeping break the tool
                    log.warning("snapshot record failed for %s: %s", sym, e)
                return k, trades, book, "binance"
            except Exception as e:
                log.warning("binance failed for %s: %s", sym, e)
        k, t, b = _demo(sym)
        return k, t, b, "demo"
    return cached(f"of:{sym}:{DATA_MODE}", 30, go)


def orderflow_tool(symbol: str) -> dict:
    m = UNIVERSE.get(symbol, {})
    sym = m.get("binance")
    if not sym:
        return {"tool": "orderflow", "title": f"Order Flow · {symbol}", "source": ["n/a"],
                "data": {"symbol": symbol, "ok": False},
                "look_at": "لا يوجد شريط صفقات مجاني لهذا السوق (الفوركس بلا بورصة مركزية، وبيانات CME مدفوعة). "
                           "استخدم Bookmap أو ATAS على العقود الآجلة للتأكيد اليدوي."}
    k, trades, book, src = _fetch(sym)
    k = k.copy()
    k["Delta"] = 2 * k["TakerBuy"] - k["Volume"]
    k["CVD"] = k["Delta"].cumsum()
    last = float(k["Close"].iloc[-1])
    tot = float(k["Volume"].sum())
    cvd_pct = float(k["Delta"].sum() / tot * 100) if tot else 0.0
    rec = k.iloc[-30:]
    rec_pct = float(rec["Delta"].sum() / rec["Volume"].sum() * 100) if rec["Volume"].sum() else 0.0
    # absorption
    avg_v, avg_r = k["Volume"].rolling(60).mean(), (k["High"] - k["Low"]).rolling(60).mean()
    absorption = None
    for ts, b in k.iloc[-30:].iterrows():
        if b["Volume"] >= 2 * avg_v[ts] and abs(b["Close"] - b["Open"]) <= 0.25 * avg_r[ts]:
            share = b["Delta"] / b["Volume"] if b["Volume"] else 0
            if abs(share) >= 0.3:  # sellers hit hard but price held → buyers absorbing (bullish), and vice versa
                absorption = {"time": int(ts.timestamp()), "price": float(b["Close"]), "dir": -int(np.sign(share)),
                              "delta_share": round(float(share) * 100)}
    # footprint
    prices = np.array([t[0] for t in trades])
    step = max(last * 0.0002, 0.01)
    fp = {}
    for p, q, seller in trades:
        b = round(round(p / step) * step, 2)
        row = fp.setdefault(b, [0.0, 0.0])
        row[0 if seller else 1] += q  # [sell, buy]
    footprint = sorted(({"price": p, "sell": round(v[0], 4), "buy": round(v[1], 4), "delta": round(v[1] - v[0], 4)}
                        for p, v in fp.items()), key=lambda r: -r["price"])
    poc = max(footprint, key=lambda r: r["buy"] + r["sell"])["price"] if footprint else None
    # walls within 1% of price
    def walls(side):
        lv = [x for x in book[side] if abs(x[0] - last) / last <= 0.01]
        if not lv:
            return []
        avg = np.mean([q for _, q in lv])
        return [{"price": p, "size": round(q, 3), "x_avg": round(q / avg, 1)} for p, q in sorted(lv, key=lambda x: -x[1])[:3]]
    bid_w, ask_w = walls("bids"), walls("asks")
    bias = int(np.sign(rec_pct)) if abs(rec_pct) >= 5 else 0
    look = (f"آخر 30 دقيقة: الـ Delta {rec_pct:+.0f}% من الحجم ({'مشترون عدوانيون' if rec_pct > 0 else 'بائعون عدوانيون'}). "
            f"أكبر حائط شراء {bid_w[0]['price']:.2f} ({bid_w[0]['x_avg']}× المتوسط)، " if bid_w else "")
    look += f"أكبر حائط بيع {ask_w[0]['price']:.2f} ({ask_w[0]['x_avg']}× المتوسط). " if ask_w else ""
    if absorption:
        look += f"امتصاص عند {absorption['price']:.2f}: {'البائعون ضربوا والسعر صمد (إيجابي)' if absorption['dir'] > 0 else 'المشترون ضربوا والسعر لم يتحرك (سلبي)'}. "
    look += "الحائط وحده لا يكفي: الدخول فقط بعد تأكيد الشارت."
    return {"tool": "orderflow", "title": f"Order Flow · Delta/Footprint · {symbol}", "source": [src],
            "data": {"symbol": symbol, "ok": True, "pair": sym, "last": last, "cvd_pct": round(cvd_pct, 1),
                     "recent_delta_pct": round(rec_pct, 1), "delta_bias": bias, "absorption": absorption,
                     "poc": poc, "spoofing": _spoofing(sym, src, book), "footprint": [r for r in footprint if abs(r["price"] - last) / last < 0.004][:40],
                     "walls": {"bid": bid_w, "ask": ask_w},
                     "chart": {"t": [int(x.timestamp()) for x in k.index], "o": k["Open"].tolist(), "h": k["High"].tolist(),
                               "l": k["Low"].tolist(), "c": k["Close"].tolist(), "delta": k["Delta"].round(4).tolist(),
                               "cvd": k["CVD"].round(4).tolist()}},
            "look_at": look}
