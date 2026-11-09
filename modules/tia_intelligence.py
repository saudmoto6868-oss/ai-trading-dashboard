"""TIA unified market catalog and deterministic Intelligence Director.

The Director does not invent missing feeds or claim AI certainty. It combines
available OHLCV, market-flow and options evidence, records provenance/freshness,
and explicitly reports unavailable modules. Human remains in control.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

MARKET_CLASSES = (
    "Crypto", "Forex", "Metals", "Oil & Gas", "Indices", "Stocks", "Bonds",
    "Options", "Meme coins", "Egypt (EGX)", "Saudi (Tadawul)",
)
CRYPTO_SEED = ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "BNB-USDT", "DOGE-USDT", "ADA-USDT", "AVAX-USDT"]


def market_catalog(top: int = 60) -> dict[str, dict[str, Any]]:
    """Return every configured asset class with its discovered symbols and source notes."""
    from modules.asset_classes import class_symbols
    out = {}
    for cls in MARKET_CLASSES:
        try:
            syms, note = class_symbols(cls, CRYPTO_SEED, top=top, mtype="SPOT", wide=(cls == "Crypto"))
            # Keep order, remove duplicates, never fabricate a fallback symbol.
            syms = list(dict.fromkeys(str(s) for s in syms if s))
            out[cls] = {"symbols": syms, "count": len(syms), "note": note or "",
                        "available": bool(syms), "kind": "options" if cls == "Options" else "market"}
        except Exception as exc:
            out[cls] = {"symbols": [], "count": 0, "note": f"{type(exc).__name__}: {str(exc)[:140]}",
                        "available": False, "kind": "options" if cls == "Options" else "market"}
    return out


def _rsi(close, period: int = 14):
    import numpy as np
    a = np.asarray(close, dtype=float)
    if len(a) <= period:
        return None
    d = np.diff(a)
    up = np.maximum(d, 0.0)
    dn = np.maximum(-d, 0.0)
    # Wilder-style rolling average over the latest period; intentionally descriptive, not a signal by itself.
    ag, al = float(up[-period:].mean()), float(dn[-period:].mean())
    if al == 0:
        return 100.0 if ag > 0 else 50.0
    return round(100 - 100 / (1 + ag / al), 1)


def _technical(df):
    import numpy as np
    if df is None or len(df) < 30:
        return {"status": "insufficient", "bars": 0 if df is None else len(df)}
    c = df["close"].to_numpy(float)
    h = df["high"].to_numpy(float)
    l = df["low"].to_numpy(float)
    last = float(c[-1])
    sma20, sma50 = float(np.mean(c[-20:])), float(np.mean(c[-50:])) if len(c) >= 50 else None
    ret20 = (last / float(c[-21]) - 1) * 100 if c[-21] else 0.0
    tr = np.maximum(h[-14:] - l[-14:], np.maximum(np.abs(h[-14:] - c[-15:-1]), np.abs(l[-14:] - c[-15:-1])))
    atr = float(np.mean(tr))
    return {"status": "ok", "bars": len(c), "last": last, "sma20": sma20, "sma50": sma50,
            "rsi14": _rsi(c), "return20_pct": round(ret20, 3), "atr14": atr,
            "trend": "bullish" if last > sma20 and (sma50 is None or sma20 > sma50) else
                     "bearish" if last < sma20 and (sma50 is None or sma20 < sma50) else "mixed",
            "last_bar": str(df["time"].iloc[-1]) if "time" in df else None}


def analyze_symbol(symbol: str, asset_class: str, timeframes=("15m", "1h", "4h", "1d")) -> dict:
    """Collect available evidence for one symbol and produce a transparent cross-module synthesis."""
    from modules.market_cache import get_klines
    from modules import spot_flow
    result = {"symbol": symbol, "asset_class": asset_class, "asof_utc": datetime.now(timezone.utc).isoformat(),
              "sources": {}, "technical": {}, "flow": {}, "options": None, "warnings": [], "score": 0,
              "stance": "UNCONFIRMED", "confidence": "LOW", "director_summary": ""}
    for tf in timeframes:
        try:
            df = get_klines(symbol, tf, 180)
            result["technical"][tf] = _technical(df)
            result["sources"][f"ohlcv:{tf}"] = {"status": "available", "bars": len(df),
                                                   "last_bar": result["technical"][tf].get("last_bar")}
        except Exception as exc:
            result["technical"][tf] = {"status": "unavailable", "reason": str(exc)[:160]}
            result["sources"][f"ohlcv:{tf}"] = {"status": "unavailable", "reason": str(exc)[:160]}
    # Flow is instrument/provider-specific; don't label a Yahoo candle proxy as exchange order flow.
    try:
        if symbol.startswith("HL:"):
            fl = spot_flow.hyperliquid(symbol.split(":")[-1])
        elif symbol.endswith("-USDT") and not symbol.startswith("Y:"):
            fl = spot_flow.crypto(symbol.split("-")[0])
        else:
            fl = {"src": "none", "tape": {"ok": False, "why": "No verified order-book / tape adapter for this symbol"}}
        result["flow"] = fl
        result["sources"]["order_flow"] = {"status": "available" if any((fl.get(k) or {}).get("ok") for k in ("tape", "book", "deriv", "taker")) else "unavailable",
                                            "provider": fl.get("src", "none")}
    except Exception as exc:
        result["flow"] = {"src": "none", "error": str(exc)[:160]}
        result["sources"]["order_flow"] = {"status": "unavailable", "reason": str(exc)[:160]}
    # Options context is only attached where a supported underlying is known.
    base = symbol.split("-")[0].upper()
    if base in ("BTC", "ETH") and asset_class in ("Crypto", "Meme coins"):
        try:
            from modules import options_desk
            rows = options_desk.fetch(base, ttl=120, timeout=8)
            result["options"] = options_desk.summarize(rows)
            result["sources"]["options"] = {"status": "available", "provider": "Deribit public API"}
        except Exception as exc:
            result["sources"]["options"] = {"status": "unavailable", "reason": str(exc)[:160]}
    else:
        result["sources"]["options"] = {"status": "not_applicable", "reason": "No verified options chain adapter for this underlying"}
    # Evidence votes: one vote per timeframe, plus order-flow only when a real adapter returned valid measurements.
    votes = []
    for tf, tech in result["technical"].items():
        if tech.get("status") == "ok":
            votes.append(1 if tech["trend"] == "bullish" else -1 if tech["trend"] == "bearish" else 0)
    flow_votes = []
    for key, metric in (("tape", "buy_share"), ("book", "imbalance")):
        f = result["flow"].get(key) or {}
        if f.get("ok") and metric in f:
            v = f[metric]
            flow_votes.append(1 if (v > .55 if key == "tape" else v > .15) else
                              -1 if (v < .45 if key == "tape" else v < -.15) else 0)
    votes.extend(flow_votes)
    result["score"] = round(sum(votes) / len(votes), 3) if votes else 0
    if votes and result["score"] >= .35:
        result["stance"] = "BULLISH BIAS"
    elif votes and result["score"] <= -.35:
        result["stance"] = "BEARISH BIAS"
    elif votes:
        result["stance"] = "MIXED / WAIT"
    if len(votes) >= 4 and len([v for v in votes if v]) >= 3:
        result["confidence"] = "MODERATE"
    if len(set(v for v in votes if v)) > 1:
        result["warnings"].append("Technical and/or flow evidence conflict; reduce conviction.")
    if not flow_votes:
        result["warnings"].append("No verified live order-flow confirmation for this instrument.")
    if not any(v.get("status") == "ok" for v in result["technical"].values()):
        result["warnings"].append("No usable candle data; directional conclusion is unavailable.")
    available = sum(1 for v in result["sources"].values() if v.get("status") == "available")
    result["director_summary"] = (f"{symbol}: {result['stance']} from {len(votes)} usable evidence votes; "
                                  f"{available} source groups available. This is a research bias, not an execution instruction.")
    return result


def director_report(symbol: str, asset_class: str) -> dict:
    """Safe UI wrapper: always returns a structured status instead of breaking the page."""
    try:
        return analyze_symbol(symbol, asset_class)
    except Exception as exc:
        return {"symbol": symbol, "asset_class": asset_class, "stance": "UNAVAILABLE", "confidence": "LOW",
                "score": 0, "director_summary": "Director could not complete analysis.",
                "warnings": [f"{type(exc).__name__}: {str(exc)[:180]}"], "technical": {}, "flow": {},
                "sources": {}, "options": None}


def symbols_for_class(asset_class: str, top: int = 60) -> dict[str, Any]:
    """Discover the selected tab's actual symbols without forcing every provider/class to load."""
    from modules.asset_classes import class_symbols
    if asset_class == "Options":
        # The options chain itself is a separate panel; charts use its supported underlyings.
        return {"symbols": ["BTC-USDT", "ETH-USDT"], "note": "Options chains are shown in the Options Desk; chart symbols are the supported BTC/ETH underlyings.", "kind": "options"}
    try:
        syms, note = class_symbols(asset_class, CRYPTO_SEED, top=top, mtype="SPOT", wide=(asset_class == "Crypto"))
        syms = list(dict.fromkeys(str(x) for x in syms if x))
        return {"symbols": syms, "note": note or "", "kind": "market"}
    except Exception as exc:
        return {"symbols": [], "note": f"{type(exc).__name__}: {str(exc)[:160]}", "kind": "market"}
