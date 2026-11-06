"""Order flow for the Spot brain (owner 2026-11-06: 'use Time & Sales, order flow, footprint'). Public REST, no keys.

Crypto (OKX):   last 500 prints (T&S) -> aggressor buy share, CVD, big prints; 24 h taker buy / sell volume by hour (OKX
                rubik) -> CVD trend; order book 400 levels -> bid / ask imbalance within 1 % and the biggest walls; perp open
                interest change, funding, long / short account ratio (crowding); Coinbase premium (US spot demand).
Metals / oil (Hyperliquid xyz perps): recent prints + l2 book + funding + open interest (thinner than OKX: says so).
Footprint-lite: volume profile of the last 7 days of 1H candles -> POC (most traded price) and the 70 % value area.
Every parse_* is pure (tests feed JSON); fetch_* never raise (they return {'ok': False, 'why': ...})."""
from __future__ import annotations

import numpy as np
import requests

OKX = "https://www.okx.com/api/v5"
CB = "https://api.exchange.coinbase.com"
HL_COIN = {"GOLD": "xyz:GOLD", "SILVER": "xyz:SILVER", "COPPER": "xyz:COPPER", "OIL": "xyz:CL", "PLATINUM": "xyz:PLATINUM"}


def _get(url, params=None, timeout=10):
    r = requests.get(url, params=params, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    return r.json()


# ---------------------------------------------------------------- pure parsers
def parse_trades(rows: list[dict]) -> dict:
    """rows: [{'px','sz','side' ('buy'|'sell' = taker), 'ts'}] newest first or any order."""
    t = sorted(({"px": float(r["px"]), "sz": float(r["sz"]), "buy": str(r["side"]).lower() in ("buy", "b"), "ts": int(r.get("ts") or r.get("time") or 0)}
                for r in rows if r.get("px") and r.get("sz")), key=lambda x: x["ts"])
    if not t:
        return {"ok": False, "why": "no prints"}
    notional = np.array([x["px"] * x["sz"] for x in t])
    sign = np.array([1 if x["buy"] else -1 for x in t])
    cvd = np.cumsum(sign * notional)
    big_thr = float(np.percentile(notional, 95)) if len(notional) >= 20 else float(notional.max())
    big = [x for x, n in zip(t, notional) if n >= big_thr]
    buy_share = float(notional[sign > 0].sum() / notional.sum()) if notional.sum() else 0.5
    big_buy = sum(1 for x in big if x["buy"])
    return {"ok": True, "n": len(t), "buy_share": buy_share, "cvd": cvd.tolist(), "cvd_end": float(cvd[-1]), "big_n": len(big), "big_buy": big_buy,
            "big_sell": len(big) - big_buy, "big_thr": big_thr, "span_min": (t[-1]["ts"] - t[0]["ts"]) / 60000 if t[-1]["ts"] else None}


def parse_taker(rows: list) -> dict:
    """OKX rubik taker-volume rows [ts, sellVol, buyVol] (newest first) -> hourly delta + 24 h CVD."""
    rr = sorted(([int(r[0]), float(r[1]), float(r[2])] for r in rows), key=lambda x: x[0])[-24:]
    if not rr:
        return {"ok": False, "why": "no taker data"}
    delta = [b - s for _, s, b in rr]
    cvd = np.cumsum(delta)
    tot = sum(s + b for _, s, b in rr)
    return {"ok": True, "delta": delta, "cvd": cvd.tolist(), "buy_share": sum(b for _, _, b in rr) / tot if tot else 0.5,
            "slope": float(np.polyfit(range(len(cvd)), cvd, 1)[0]) if len(cvd) > 2 else 0.0}


def parse_book(bids: list, asks: list, band: float = 0.01) -> dict:
    """bids / asks: [[px, sz, ...], ...] best first -> imbalance inside +- band of the mid, biggest wall each side."""
    b = [(float(x[0]), float(x[1])) for x in bids]
    a = [(float(x[0]), float(x[1])) for x in asks]
    if not b or not a:
        return {"ok": False, "why": "empty book"}
    mid = (b[0][0] + a[0][0]) / 2
    bv = sum(p * s for p, s in b if p >= mid * (1 - band))
    av = sum(p * s for p, s in a if p <= mid * (1 + band))
    wb = max(b, key=lambda x: x[0] * x[1])
    wa = max(a, key=lambda x: x[0] * x[1])
    return {"ok": True, "mid": mid, "bid_usd": bv, "ask_usd": av, "imbalance": (bv - av) / (bv + av) if bv + av else 0.0,
            "wall_bid": wb[0], "wall_bid_usd": wb[0] * wb[1], "wall_ask": wa[0], "wall_ask_usd": wa[0] * wa[1]}


def volume_profile(df, bins: int = 40) -> dict:
    """Footprint-lite: each candle's volume spread evenly over its high-low range -> POC + 70 % value area."""
    if df is None or len(df) < 10:
        return {"ok": False, "why": "not enough 1H candles"}
    lo, hi = float(df["low"].min()), float(df["high"].max())
    if hi <= lo:
        return {"ok": False, "why": "flat"}
    edges = np.linspace(lo, hi, bins + 1)
    vol = np.zeros(bins)
    for h, l, v in zip(df["high"].to_numpy(float), df["low"].to_numpy(float), df["volume"].to_numpy(float)):
        i0, i1 = np.searchsorted(edges, l, "right") - 1, np.searchsorted(edges, h, "left")
        i0, i1 = max(0, i0), min(bins, max(i1, i0 + 1))
        vol[i0:i1] += v / (i1 - i0)
    poc = int(vol.argmax())
    order = np.argsort(vol)[::-1]
    keep, acc = [], 0.0
    for i in order:
        keep.append(i)
        acc += vol[i]
        if acc >= 0.7 * vol.sum():
            break
    mids = (edges[:-1] + edges[1:]) / 2
    return {"ok": True, "poc": float(mids[poc]), "vah": float(edges[max(keep) + 1]), "val": float(edges[min(keep)]), "profile": vol.tolist(),
            "mids": mids.tolist()}


# ---------------------------------------------------------------- fetchers (network)
def _safe(fn, *a):
    try:
        return fn(*a)
    except Exception as e:
        return {"ok": False, "why": f"{type(e).__name__}"}


def crypto(base: str) -> dict:
    inst, swap = f"{base}-USDT", f"{base}-USDT-SWAP"
    out = {"src": "OKX"}
    out["tape"] = _safe(lambda: parse_trades(_get(f"{OKX}/market/trades", {"instId": inst, "limit": 500})["data"]))
    out["taker"] = _safe(lambda: parse_taker(_get(f"{OKX}/rubik/stat/taker-volume", {"ccy": base, "instType": "SPOT", "period": "1H"})["data"]))

    def book():
        d = _get(f"{OKX}/market/books", {"instId": inst, "sz": 400})["data"][0]
        return parse_book(d["bids"], d["asks"])
    out["book"] = _safe(book)

    def deriv():
        oi = _get(f"{OKX}/rubik/stat/contracts/open-interest-volume", {"ccy": base, "period": "1D"})["data"]
        ls = _get(f"{OKX}/rubik/stat/contracts/long-short-account-ratio", {"ccy": base, "period": "1D"})["data"]
        fr = _get(f"{OKX}/public/funding-rate", {"instId": swap})["data"]
        oi = sorted(oi, key=lambda r: int(r[0]))
        o_now, o_wk = float(oi[-1][1]), float(oi[-8][1]) if len(oi) >= 8 else float(oi[0][1])
        return {"ok": True, "oi_chg_7d": (o_now / o_wk - 1) * 100 if o_wk else None, "ls_ratio": float(sorted(ls, key=lambda r: int(r[0]))[-1][1]) if ls else None,
                "funding": float(fr[0]["fundingRate"]) * 100 if fr else None}
    out["deriv"] = _safe(deriv)

    def premium():
        if base not in ("BTC", "ETH", "SOL"):
            return {"ok": False, "why": "Coinbase premium only for BTC / ETH / SOL"}
        cb = float(_get(f"{CB}/products/{base}-USD/ticker")["price"])
        okx = float(_get(f"{OKX}/market/ticker", {"instId": inst})["data"][0]["last"])
        return {"ok": True, "premium_pct": (cb / okx - 1) * 100}
    out["premium"] = _safe(premium)

    def vp():
        from modules.market_cache import get_klines
        return volume_profile(get_klines(inst, "1h", 168))
    out["vp"] = _safe(vp)
    return out


def hyperliquid(asset: str) -> dict:
    coin = HL_COIN.get(asset)
    if not coin:
        return {"src": "none", "tape": {"ok": False, "why": "no order-flow feed for this market (Yahoo has no prints)"}}
    from modules.hl_feed import _post, markets
    out = {"src": "Hyperliquid (perp, thinner than OKX)"}
    out["tape"] = _safe(lambda: parse_trades([{"px": r["px"], "sz": r["sz"], "side": "buy" if r.get("side") == "B" else "sell", "ts": r.get("time")}
                                              for r in _post({"type": "recentTrades", "coin": coin})]))

    def book():
        lv = _post({"type": "l2Book", "coin": coin})["levels"]
        return parse_book([[x["px"], x["sz"]] for x in lv[0]], [[x["px"], x["sz"]] for x in lv[1]], band=0.005)
    out["book"] = _safe(book)

    def deriv():
        meta, ctxs = _post({"type": "metaAndAssetCtxs", "dex": "xyz"})
        for u, c in zip(meta.get("universe", []), ctxs):
            if u.get("name") == coin:
                return {"ok": True, "funding": float(c.get("funding") or 0) * 100, "oi": float(c.get("openInterest") or 0), "oi_chg_7d": None, "ls_ratio": None}
        return {"ok": False, "why": "market not listed"}
    out["deriv"] = _safe(deriv)

    def vp():
        from modules.market_cache import get_klines
        return volume_profile(get_klines("HL:" + coin, "1h", 168))
    out["vp"] = _safe(vp)
    out["taker"] = {"ok": False, "why": "no hourly taker history on Hyperliquid"}
    out["premium"] = {"ok": False, "why": "n/a"}
    return out


def fetch(asset: str, cls: str) -> dict:
    return crypto(asset) if cls == "crypto" else hyperliquid(asset)


def _p(x):
    ax = abs(x)
    return f"{x:,.0f}" if ax >= 1000 else f"{x:,.2f}" if ax >= 1 else f"{x:.4f}"


def reading(fl: dict) -> dict:
    """Vote + Arabic lines from the flow: aggressors, CVD trend, book, crowding, premium, value area."""
    v, lines = 0, []
    tp = fl.get("tape") or {}
    if tp.get("ok"):
        bs = tp["buy_share"]
        v += 1 if bs > 0.55 else -1 if bs < 0.45 else 0
        lines.append(f"التايم آند سيلز: المشترين بالسوق {bs * 100:.0f}% من آخر {tp['n']} صفقة · الصفقات الكبيرة {tp['big_buy']} شراء / {tp['big_sell']} بيع")
    tk = fl.get("taker") or {}
    if tk.get("ok"):
        v += 1 if tk["slope"] > 0 else -1
        lines.append(f"CVD 24 ساعة {'طالع (شراء بالسوق غالب)' if tk['slope'] > 0 else 'نازل (بيع بالسوق غالب)'} · شراء {tk['buy_share'] * 100:.0f}%")
    bk = fl.get("book") or {}
    if bk.get("ok"):
        im = bk["imbalance"]
        v += 1 if im > 0.15 else -1 if im < -0.15 else 0
        lines.append(f"الدفتر: {'طلبات الشراء أتقل' if im > 0 else 'عروض البيع أتقل'} ({im * 100:+.0f}%) · أكبر حيطة شراء {_p(bk['wall_bid'])} وبيع {_p(bk['wall_ask'])}")
    dv = fl.get("deriv") or {}
    if dv.get("ok"):
        fr, ls = dv.get("funding"), dv.get("ls_ratio")
        if fr is not None:
            crowd = fr > 0.03
            v -= 1 if crowd else 0
            lines.append(f"التمويل {fr:+.4f}%" + (" - اللونج زحمة (خطر تصفية)" if crowd else " - مش زحمة" if fr > -0.01 else " - الشورت زحمة (وقود طلوع)"))
            if fr < -0.01:
                v += 1
        if ls is not None:
            lines.append(f"نسبة الحسابات لونج/شورت {ls:.2f}" + (" - الأغلبية لونج (عكسي سلبي)" if ls > 2 else ""))
        if dv.get("oi_chg_7d") is not None:
            lines.append(f"الأوبن إنترست {dv['oi_chg_7d']:+.1f}% في أسبوع")
    pr = fl.get("premium") or {}
    if pr.get("ok"):
        p = pr["premium_pct"]
        v += 1 if p > 0.05 else -1 if p < -0.05 else 0
        lines.append(f"بريميوم كوين بيس {p:+.3f}% - " + ("طلب أمريكي/مؤسسي أقوى" if p > 0 else "طلب أمريكي أضعف"))
    vp = fl.get("vp") or {}
    if vp.get("ok"):
        lines.append(f"الفوت برينت (بروفايل 7 أيام): POC {_p(vp['poc'])} · منطقة القيمة {_p(vp['val'])} - {_p(vp['vah'])}")
    if not lines:
        lines.append("مفيش داتا أوردر فلو للسوق ده دلوقتي.")
    return {"vote": int(np.sign(v)), "raw": v, "lines": lines}
