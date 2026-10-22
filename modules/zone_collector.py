"""Unattended collector for the confluence-zone forward test (owner 2026-10-23: 'find the best way to get data faster so we can judge').

The Workspace logs zones only while a chart is open in a visible browser tab (about one zone a minute per symbol). This collector runs the SAME
logic headless on OKX public data, for several symbols at once, and writes logs in the same export format that modules/zone_eval.py judges:

  python modules/zone_collector.py 7200 BTC-USDT,ETH-USDT,SOL-USDT,XRP-USDT     # seconds, symbols  -> .zone_log_<SYMBOL>.json (updated every minute)
  python modules/zone_eval.py                                                    # judge whatever is on disk

Port of FlowRead (update, zonesOf) and ZoneLog from modules/workspace_app.html; keep them in step. Differences, stated: the ladder is OKX
books-full (2000 levels a side, one request per 2 s for the whole IP, so each symbol is polled every 2 x n_symbols s); trades come from
/market/trades (last 100) so a very fast tape can be truncated; the 'tape' source (absorption-like) uses a fixed 2 bp price row instead of the
chart's row height. Records carry 'src': 'collector'. Nothing is traded; public endpoints only."""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RBP, TOUCH, TTL, DEDUP = 6.0, 1.5, 900_000, 300_000      # = ZoneLog constants in the page (ms)
BASE = "https://www.okx.com/api/v5/market"


def _med(a):
    if not a:
        return 0.0
    s = sorted(a); m = len(s) // 2
    return s[m] if len(s) % 2 else (s[m - 1] + s[m]) / 2


def _tick(ps):
    s = sorted(set(ps)); t = math.inf
    for i in range(1, len(s)):
        d = s[i] - s[i - 1]
        if 1e-12 < d < t:
            t = d
    return 0.0 if t == math.inf else t


class Engine:
    """FlowRead.update: wall life-cycle PLACED / PULLED / FILLED / REFILL from consecutive book snapshots (times in ms)."""

    def __init__(self, big=5.0, rel=0.25):
        self.walls, self.prev_t, self.prev, self.mids, self.big, self.rel, self.ev = {}, 0, None, [], big, rel, []

    def update(self, t, bids, asks, trades):
        """bids / asks = [(price, size)], trades = [{'t','p','q','side'}] -> list of events (dicts: t, kind, side, p, q, age, dist, near, ratio...)."""
        if not bids or not asks:
            return []
        bb, ba = max(p for p, _ in bids), min(p for p, _ in asks)
        if not bb < ba:
            return []
        mid = (bb + ba) / 2; allp = [p for p, _ in bids + asks]; m = _med([q for _, q in bids + asks]); lo, hi = min(allp), max(allp)
        tk = _tick(allp) or mid * 1e-4
        size = {}
        for p, q in bids + asks:
            size[p] = size.get(p, 0.0) + q
        tr = [x for x in trades if self.prev_t < x["t"] <= t + 1000]
        self.mids.append((t, mid))
        while self.mids and t - self.mids[0][0] > 60_000:
            self.mids.pop(0)

        def mid_ago(ms):
            r = self.mids[0][1] if self.mids else mid
            for tt, mm in self.mids:
                if t - tt >= ms:
                    r = mm
                else:
                    break
            return r

        def traded_at(p):
            return sum(x["q"] for x in tr if abs(x["p"] - p) <= tk * 0.6)
        mx = max([q for p, q in bids + asks if abs(p - mid) / mid <= 0.005] or [0.0])
        thr = max(self.big * m, self.rel * mx)
        cur = {}
        for side, arr in (("bid", bids), ("ask", asks)):
            for p, q in arr:
                if m > 0 and q >= thr:
                    cur[(side, p)] = q
        events, pw = [], self.prev

        def ev(kind, w, q, **extra):
            dist = abs(w["p"] - mid) / mid; d0 = abs(w["p"] - mid_ago(10_000)) / mid_ago(10_000)
            e = {"t": t, "kind": kind, "side": w["side"], "p": w["p"], "q": q, "age": t - w["first"], "dist": dist, "near": d0 > dist * 1.25}
            e.update(extra); events.append(e)
        for (side, p), q in cur.items():
            w = self.walls.get((side, p))
            if w is None:
                seen = pw is not None and pw["lo"] <= p <= pw["hi"]     # the previous snapshot covered this price: a genuinely new order
                nw = {"side": side, "p": p, "first": t, "last": t, "q": q, "qmax": q, "refills": 0, "last_refill": 0}
                self.walls[(side, p)] = nw
                if seen:
                    ev("PLACED", nw, q)
                continue
            ex = traded_at(w["p"])
            if q < 0.6 * w["q"]:
                drop = w["q"] - q; ratio = ex / drop
                ev("FILLED" if ratio >= 0.5 else "PULLED", w, drop, ratio=round(ratio, 2), partial=True)
            elif ex >= 0.5 * w["q"] and q >= 0.8 * w["q"] and t - w["last_refill"] > 10_000:
                w["refills"] += 1; w["last_refill"] = t; ev("REFILL", w, ex, refills=w["refills"])
            w["q"] = q; w["qmax"] = max(w["qmax"], q); w["last"] = t
        for key in list(self.walls):
            if key in cur:
                continue
            w = self.walls[key]
            if w["p"] < lo or w["p"] > hi:
                del self.walls[key]; continue
            now_ = size.get(w["p"], 0.0)
            if now_ >= 0.6 * w["q"]:
                if now_ < thr * 0.7:
                    del self.walls[key]
                else:
                    w["q"] = now_
                continue
            drop = w["q"] - now_; ratio = traded_at(w["p"]) / drop
            ev("FILLED" if ratio >= 0.5 else "PULLED", w, drop, ratio=round(ratio, 2)); del self.walls[key]
        self.prev = {"lo": lo, "hi": hi, "t": t}; self.prev_t = t; self.ev += events; self.ev = self.ev[-300:]
        return events


def absorb_events(trades, now, mid, row_bp=2.0):
    """'tape' source: lots of volume at ONE price row (2 bp high) in the last 45 s, >= 4 prints and >= 3x the median row = absorption-like."""
    step = mid * row_bp / 1e4; g = {}
    for x in trades:
        if now - x["t"] > 45_000:
            continue
        o = g.setdefault(round(x["p"] / step), {"sum": 0.0, "n": 0, "buy": 0.0, "sell": 0.0})
        o["sum"] += x["q"]; o["n"] += 1
        o["buy" if x["side"] == "Buy" else "sell"] += x["q"]
    sums = sorted(o["sum"] for o in g.values()); med = sums[len(sums) // 2] if sums else 0.0
    return [{"t": now, "kind": "ABSORB", "side": "ask" if o["buy"] >= o["sell"] else "bid", "p": k * step, "q": o["sum"]}
            for k, o in g.items() if o["n"] >= 4 and len(sums) >= 4 and o["sum"] >= 3 * max(med, 1e-12)]


def zones_of(eng, now, mid, tk, evs, trades):
    """FlowRead.zonesOf: 2+ independent sources (book / limits / tape / prints) at one price in the last 2 minutes."""
    tol = max(3 * tk, mid * 0.0003); pts = []
    for w in eng.walls.values():
        if now - w["first"] >= 15_000 and abs(w["p"] - mid) / mid <= 0.005:
            pts.append({"p": w["p"], "src": "book", "side": w["side"], "q": w["q"]})
    for e in evs:
        if e["kind"] == "ABSORB":
            pts.append({"p": e["p"], "src": "tape", "side": e["side"], "q": e["q"]})
        elif e["kind"] in ("REFILL", "FILLED") or (e["kind"] == "PULLED" and e["age"] >= 8000):
            pts.append({"p": e["p"], "src": "limits", "side": e["side"], "q": e["q"], "kind": e["kind"]})
    mq = _med([x["q"] for x in trades])
    for x in trades:
        if now - x["t"] <= 60_000 and mq > 0 and x["q"] >= 6 * mq:
            pts.append({"p": x["p"], "src": "prints", "side": "ask" if x["side"] == "Buy" else "bid", "q": x["q"]})
    pts.sort(key=lambda a: a["p"]); groups = []
    for x in pts:
        g = groups[-1] if groups else None
        if g and x["p"] - g["hi"] <= tol and x["p"] - g["lo"] <= 2 * tol:
            g["items"].append(x); g["hi"] = max(g["hi"], x["p"])
        else:
            groups.append({"lo": x["p"], "hi": x["p"], "items": [x]})
    out = []
    for g in groups:
        srcs = sorted({i["src"] for i in g["items"]}); qs = sum(i["q"] for i in g["items"]) or 1.0
        z = {"p": sum(i["p"] * i["q"] for i in g["items"]) / qs, "lo": g["lo"], "hi": g["hi"], "srcs": srcs, "strength": len(srcs), "items": g["items"]}
        if z["strength"] >= 2:
            out.append(z)
    return sorted(out, key=lambda z: (-z["strength"], -len(z["items"])))[:3]


class ZoneLog:
    """ZoneLog of the page: log a zone once per 5 min with a mirror-price control, follow the price, resolve hold / break."""

    def __init__(self):
        self.recs = []

    def add(self, z, mid, now):
        if any(now - r["t"] < DEDUP and abs(r["p"] - z["p"]) / mid * 1e4 <= 4 for r in self.recs):
            return None
        r = {"t": now, "p": z["p"], "strength": z["strength"], "srcs": list(z["srcs"]), "mid0": mid, "from": 1 if mid > z["p"] else -1, "ctl": 2 * mid - z["p"],
             "z": {"touchT": 0, "out": None}, "c": {"touchT": 0, "out": None}, "last": mid, "src": "collector"}
        self.recs.append(r); self.recs = self.recs[-300:] if len(self.recs) > 300 else self.recs
        return r

    @staticmethod
    def _one(r, tr, L, frm, mid):
        if tr["out"]:
            return
        bp = lambda x: x / mid * 1e4
        if not tr["touchT"]:
            crossed = (r["last"] - L) * (mid - L) <= 0
            if abs(bp(mid - L)) <= TOUCH or crossed:
                tr["touchT"] = 1
            else:
                return
        d = bp((mid - L) * frm)
        if d >= RBP:
            tr["out"] = "hold"
        elif d <= -RBP:
            tr["out"] = "break"

    def step(self, mid, now):
        for r in self.recs:
            if r.get("done"):
                continue
            if now - r["t"] > TTL:
                r["done"] = True; continue
            self._one(r, r["z"], r["p"], r["from"], mid); self._one(r, r["c"], r["ctl"], -r["from"], mid); r["last"] = mid


# ---- OKX polling -------------------------------------------------------------------------------------------------------------------------

def _get(path, params, timeout=12):
    import requests
    r = requests.get(BASE + path, params=params, timeout=timeout)
    r.raise_for_status(); j = r.json()
    if j.get("code") != "0":
        raise RuntimeError(j.get("msg") or "okx error")
    return j["data"]


def poll(sym):
    """-> (t_ms, bids, asks, trades) for one symbol; the book request is the slow one (about 2 s, 114 kB)."""
    b = _get("/books-full", {"instId": sym, "sz": 2000})[0]
    tr = _get("/trades", {"instId": sym, "limit": 100})
    bids = [(float(x[0]), float(x[1])) for x in b["bids"]]; asks = [(float(x[0]), float(x[1])) for x in b["asks"]]
    trades = [{"t": int(x["ts"]), "p": float(x["px"]), "q": float(x["sz"]), "side": "Buy" if x["side"] == "buy" else "Sell", "id": int(x["tradeId"])} for x in tr]
    return int(b["ts"]), bids, asks, trades


def run(symbols, seconds, out_dir=ROOT, log=print, fetch=poll, sleep=time.sleep, clock=time.time):
    """Poll round-robin (one books-full request per 2 s overall), keep one engine + zone log per symbol, save the logs every minute."""
    st = {s: {"eng": Engine(), "zl": ZoneLog(), "seen": 0, "trades": []} for s in symbols}
    end, last_save, polls, bad = clock() + seconds, clock(), 0, 0

    def save():
        for s, o in st.items():
            (Path(out_dir) / f".zone_log_{s}.json").write_text(json.dumps({"sym": s, "built": int(clock() * 1000), "rbp": RBP, "ttl": TTL, "src": "collector", "recs": o["zl"].recs}), encoding="utf-8")
    while clock() < end:
        for s in symbols:
            t0 = clock()
            try:
                t, bids, asks, trades = fetch(s)
            except Exception as e:
                bad += 1; log(f"{s}: {type(e).__name__}: {e}"); sleep(2); continue
            o = st[s]; new = [x for x in trades if x["id"] > o["seen"]] if o["seen"] else []
            o["seen"] = max([x["id"] for x in trades] + [o["seen"]]); o["trades"] = (o["trades"] + new)[-600:]
            eng = o["eng"]; evs = eng.update(t, bids, asks, o["trades"])
            mid = (max(p for p, _ in bids) + min(p for p, _ in asks)) / 2; tk = _tick([p for p, _ in bids + asks]) or mid * 1e-4
            ab = absorb_events(o["trades"], t, mid)
            window = [e for e in eng.ev if t - e["t"] <= 120_000] + ab
            for z in zones_of(eng, t, mid, tk, window, [x for x in o["trades"] if t - x["t"] <= 120_000]):
                o["zl"].add(z, mid, t)
            o["zl"].step(mid, t); polls += 1
            sleep(max(0.0, 2.0 - (clock() - t0)))        # books-full is limited to one request per 2 s
        if clock() - last_save > 60:
            save(); last_save = clock()
            log("saved: " + ", ".join(f"{s} {len(o['zl'].recs)} zones" for s, o in st.items()) + f" · {polls} polls, {bad} failed")
    save()
    return {s: o["zl"].recs for s, o in st.items()}


if __name__ == "__main__":
    secs = int(sys.argv[1]) if len(sys.argv) > 1 else 3600
    syms = sys.argv[2].split(",") if len(sys.argv) > 2 else ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT"]
    run(syms, secs)
