"""Options desk (owner 2026-10-22: options need no charts): what the crypto option market says, from Deribit's public
`get_book_summary_by_currency` (free, no key, the whole BTC / ETH option book in one call).

Per expiry: put / call ratio by open interest and by volume, max pain, ATM implied volatility, a +-10 % skew proxy, and the
strikes with the most open interest (the 'walls'). Across expiries: the IV term structure.

Honest limits (shown in the UI too): open interest and volume do not say whether a trade OPENED or CLOSED a position, or whether
it was a hedge or a bet, so put/call ratio and 'walls' are CONTEXT, not a trade signal. Max pain is a theory about pinning near
expiry, with weak evidence outside the last day or two. IV level alone says little; IV RANK needs history we do not store yet.
DVOL (Deribit's 30-day implied-volatility index, free daily history) gives the IV history, so IV rank and percentile need no
snapshot job of ours. Pure functions on the payload; cached fetches."""
from __future__ import annotations

import re
import time
from datetime import datetime, timezone

import requests

URL = "https://www.deribit.com/api/v2/public/get_book_summary_by_currency"
DVOL_URL = "https://www.deribit.com/api/v2/public/get_volatility_index_data"
_NAME = re.compile(r"^([A-Z]+)-(\d{1,2}[A-Z]{3}\d{2})-(\d+(?:\.\d+)?)-([CP])$")
_cache: dict = {}


def fetch(currency: str = "BTC", ttl: int = 120, timeout: int = 15) -> list:
    """Raw option book summary rows for BTC / ETH (cached `ttl` s). Raises on network / API errors."""
    hit = _cache.get(currency)
    if hit and time.time() - hit[0] < ttl:
        return hit[1]
    r = requests.get(URL, params={"currency": currency, "kind": "option"}, timeout=timeout)
    r.raise_for_status()
    rows = r.json().get("result") or []
    _cache[currency] = (time.time(), rows)
    return rows


def dvol(currency: str = "BTC", days: int = 365, ttl: int = 1800, timeout: int = 20) -> list:
    """Daily DVOL candles [(date, close)] for the last `days` days (cached `ttl` s). Raises on network / API errors."""
    key = f"dvol-{currency}-{days}"
    hit = _cache.get(key)
    if hit and time.time() - hit[0] < ttl:
        return hit[1]
    end = int(time.time() * 1000)
    r = requests.get(DVOL_URL, params={"currency": currency, "start_timestamp": end - days * 86400_000, "end_timestamp": end, "resolution": "1D"}, timeout=timeout)
    r.raise_for_status()
    out = [(datetime.fromtimestamp(c[0] / 1000, timezone.utc).date(), float(c[4])) for c in (r.json().get("result") or {}).get("data", []) if len(c) >= 5]
    _cache[key] = (time.time(), out)
    return out


def iv_rank(series: list) -> dict | None:
    """IV rank / percentile of the LAST value against the series (needs >= 30 values): rank = (now - min) / (max - min), percentile =
    share of earlier days with a lower value. Both are 0-100; a short or flat series gives None."""
    v = [x for x in series if x is not None]
    if len(v) < 30:
        return None
    now, lo, hi = v[-1], min(v), max(v)
    if hi <= lo:
        return None
    prior = v[:-1]
    return {"now": round(now, 1), "min": round(lo, 1), "max": round(hi, 1), "rank": round((now - lo) / (hi - lo) * 100, 0),
            "percentile": round(sum(1 for x in prior if x < now) / len(prior) * 100, 0), "days": len(v)}


def parse(name: str):
    """'BTC-27NOV26-73000-P' -> (expiry date, strike, 'C' | 'P') or None."""
    m = _NAME.match(name or "")
    if not m:
        return None
    try:
        exp = datetime.strptime(m.group(2).title(), "%d%b%y").replace(tzinfo=timezone.utc).date()
    except ValueError:
        return None
    return exp, float(m.group(3)), m.group(4)


def _book(rows: list) -> list:
    out = []
    for r in rows or []:
        p = parse(r.get("instrument_name"))
        if not p:
            continue
        out.append({"exp": p[0], "k": p[1], "cp": p[2], "oi": float(r.get("open_interest") or 0), "vol": float(r.get("volume") or 0),
                    "iv": r.get("mark_iv"), "px": float(r.get("underlying_price") or 0)})
    return out


def max_pain(opts: list):
    """Strike where option holders collectively lose the most at expiry (writers pay the least). opts = one expiry's rows."""
    ks = sorted({o["k"] for o in opts})
    if not ks:
        return None
    def pay(x):
        return sum(o["oi"] * (max(0.0, x - o["k"]) if o["cp"] == "C" else max(0.0, o["k"] - x)) for o in opts)
    return min(ks, key=pay)


def _atm_iv(opts: list, px: float):
    near = sorted((o for o in opts if o["iv"]), key=lambda o: abs(o["k"] - px))[:4]
    ivs = [o["iv"] for o in near if abs(o["k"] - near[0]["k"]) < 1e-9] if near else []
    return round(sum(ivs) / len(ivs), 1) if ivs else None


def _iv_at(opts: list, px: float, moneyness: float, cp: str):
    """IV of the `cp` option whose strike is nearest px * (1 + moneyness); None when it is further than 5 % from the target."""
    tgt = px * (1 + moneyness)
    c = [o for o in opts if o["cp"] == cp and o["iv"]]
    if not c:
        return None
    o = min(c, key=lambda o: abs(o["k"] - tgt))
    return o["iv"] if abs(o["k"] - tgt) <= 0.05 * px else None


def summarize(rows: list, today=None) -> dict:
    """-> {'spot', 'expiries': [per expiry dict], 'totals'}. Expiries already past are dropped."""
    today = today or datetime.now(timezone.utc).date()
    book = [o for o in _book(rows) if o["exp"] >= today]
    by = {}
    for o in book:
        by.setdefault(o["exp"], []).append(o)
    px = (sum(o["px"] for o in book if o["px"]) / max(1, sum(1 for o in book if o["px"]))) if book else 0.0
    ex = []
    for d, opts in sorted(by.items()):
        s = next((o["px"] for o in opts if o["px"]), px) or px
        c_oi = sum(o["oi"] for o in opts if o["cp"] == "C"); p_oi = sum(o["oi"] for o in opts if o["cp"] == "P")
        c_v = sum(o["vol"] for o in opts if o["cp"] == "C"); p_v = sum(o["vol"] for o in opts if o["cp"] == "P")
        top = sorted(opts, key=lambda o: -o["oi"])[:3]
        pi, ci = _iv_at(opts, s, -0.10, "P"), _iv_at(opts, s, 0.10, "C")
        ex.append({"exp": d, "days": (d - today).days, "oi": round(c_oi + p_oi, 1), "pc_oi": round(p_oi / c_oi, 2) if c_oi else None,
                   "vol": round(c_v + p_v, 1), "pc_vol": round(p_v / c_v, 2) if c_v else None, "max_pain": max_pain(opts), "iv": _atm_iv(opts, s),
                   "skew10": round(pi - ci, 1) if pi is not None and ci is not None else None,
                   "walls": [(o["k"], o["cp"], round(o["oi"], 1)) for o in top]})
    tot_c = sum(o["oi"] for o in book if o["cp"] == "C"); tot_p = sum(o["oi"] for o in book if o["cp"] == "P")
    return {"spot": round(px, 2), "expiries": ex,
            "totals": {"oi": round(tot_c + tot_p, 1), "pc_oi": round(tot_p / tot_c, 2) if tot_c else None,
                       "vol": round(sum(o["vol"] for o in book), 1)}}


def strikes(rows: list, expiry, spot: float, span: float = 0.25) -> list:
    """Open interest by strike (calls and puts) for one expiry, inside +-span of the spot: [(strike, call OI, put OI)]."""
    acc = {}
    for o in _book(rows):
        if o["exp"] == expiry and abs(o["k"] - spot) <= span * spot:
            a = acc.setdefault(o["k"], [0.0, 0.0]); a[0 if o["cp"] == "C" else 1] += o["oi"]
    return [(k, round(v[0], 1), round(v[1], 1)) for k, v in sorted(acc.items())]
