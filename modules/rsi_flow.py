"""Order flow snapshot for the RSI Heatmap table (server side, public REST, no keys).

Reuses the tested parsers in modules/spot_flow.py:
  OKX (crypto spot -USDT / perp -USDT-SWAP): last 500 prints -> aggressor buy share, CVD, big prints;
      order book 200 levels -> bid/ask imbalance within 1 %; perp funding (crowding).
  Hyperliquid (HL:xyz:* metals / oil / indices / stocks): recent prints + l2 book (+-0.5 %).
Other feeds (Yahoo, EGX, Tadawul) have no public prints -> 'no flow feed', never invented.
This is a snapshot of the last few minutes, not the Workspace's live WebSocket footprint.
"""
from __future__ import annotations

FLOW_TOP_N = 20          # only the best-ranked symbols get a flow snapshot (OKX public rate limits)
BUY, SELL = 0.55, 0.45   # aggressor buy share thresholds (same as spot_flow.reading)
BOOK = 0.15              # book imbalance threshold
CROWDED_LONG, CROWDED_SHORT = 0.03, -0.01   # funding % per 8 h (same as spot_flow.reading)


def feed_of(symbol: str):
    s = str(symbol)
    if s.startswith("HL:"):
        return "hl", s[3:]
    if s.endswith("-USDT-SWAP"):
        return "okx", s
    if s.endswith("-USDT") and ":" not in s:
        return "okx", s
    return None, None


def fetch_flow(symbol: str) -> dict:
    """Never raises: {'ok': False, 'why': ...} when the market has no prints feed or the call fails."""
    from modules.spot_flow import OKX, _get, _safe, parse_book, parse_trades
    kind, inst = feed_of(symbol)
    if kind is None:
        return {"ok": False, "why": "no flow feed"}
    out = {"ok": True, "src": kind}
    if kind == "okx":
        out["tape"] = _safe(lambda: parse_trades(_get(f"{OKX}/market/trades", {"instId": inst, "limit": 500}, timeout=6)["data"]))

        def book():
            d = _get(f"{OKX}/market/books", {"instId": inst, "sz": 200}, timeout=6)["data"][0]
            return parse_book(d["bids"], d["asks"])
        out["book"] = _safe(book)

        def funding():
            swap = inst if inst.endswith("-SWAP") else inst + "-SWAP"
            fr = _get(f"{OKX}/public/funding-rate", {"instId": swap}, timeout=6)["data"]
            return {"ok": True, "funding": float(fr[0]["fundingRate"]) * 100} if fr else {"ok": False, "why": "no perp"}
        out["deriv"] = _safe(funding)
    else:
        from modules.hl_feed import _post
        out["tape"] = _safe(lambda: parse_trades([
            {"px": r["px"], "sz": r["sz"], "side": "buy" if r.get("side") == "B" else "sell", "ts": r.get("time")}
            for r in _post({"type": "recentTrades", "coin": inst}, timeout=6)]))

        def book():
            lv = _post({"type": "l2Book", "coin": inst}, timeout=6)["levels"]
            return parse_book([[x["px"], x["sz"]] for x in lv[0]], [[x["px"], x["sz"]] for x in lv[1]], band=0.005)
        out["book"] = _safe(book)
        out["deriv"] = {"ok": False, "why": "n/a"}
    if not any((out.get(k) or {}).get("ok") for k in ("tape", "book", "deriv")):
        return {"ok": False, "why": (out.get("tape") or {}).get("why", "flow unavailable")}
    return out


def flow_read(fl: dict | None) -> dict:
    """-> {'vote': -1/0/+1, 'text': short table cell, 'parts': {...}}. Pure (tests feed dicts)."""
    if not fl or not fl.get("ok"):
        return {"vote": 0, "text": "—" if not fl else f"— {fl.get('why', '')}".strip(), "parts": {}}
    v, bits, parts = 0, [], {}
    tp = fl.get("tape") or {}
    if tp.get("ok"):
        bs = tp["buy_share"]
        parts["buy_share"] = bs
        v += 1 if bs > BUY else -1 if bs < SELL else 0
        bits.append(f"buy {bs * 100:.0f}%")
        if tp.get("big_n"):
            bits.append(f"big {tp['big_buy']}/{tp['big_sell']}")
    bk = fl.get("book") or {}
    if bk.get("ok"):
        im = bk["imbalance"]
        parts["imbalance"] = im
        v += 1 if im > BOOK else -1 if im < -BOOK else 0
        bits.append(f"book {im * 100:+.0f}%")
    dv = fl.get("deriv") or {}
    if dv.get("ok") and dv.get("funding") is not None:
        fr = dv["funding"]
        parts["funding"] = fr
        v += -1 if fr > CROWDED_LONG else 1 if fr < CROWDED_SHORT else 0
        bits.append(f"fund {fr:+.3f}%")
    vote = (v > 0) - (v < 0)
    icon = "🟢" if vote > 0 else "🔴" if vote < 0 else "⚪"
    return {"vote": vote, "text": f"{icon} " + " · ".join(bits) if bits else "—", "parts": parts}
