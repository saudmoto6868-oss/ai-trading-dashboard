"""US equity / index option chains from Cboe's public delayed-quotes JSON (the data behind cboe.com's "Delayed Quotes" pages).
Free, keyless, ~15 minutes DELAYED, and UNOFFICIAL: Cboe does not document it as a product, so paths / field names can change
without notice. Indices use a leading underscore (SPX -> _SPX, VIX -> _VIX, NDX -> _NDX).
Field names below come from community examples (OpenBB discussion, GitHub scripts), not from Cboe docs, so the parser reads the
OCC option symbol itself for expiry / type / strike and accepts a few spellings for the numbers. NOT reached from the build
sandbox (egress proxy) - tested with a mock payload only."""
from __future__ import annotations

import re
import threading
import time

import pandas as pd
import requests

URL = "https://cdn.cboe.com/api/global/delayed_quotes/options/{sym}.json"
HDR = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
       "Accept": "application/json"}
INDEXES = {"SPX", "NDX", "RUT", "VIX", "XSP", "DJX", "OEX"}
_OCC = re.compile(r"^([A-Z.]{1,6})(\d{6})([CP])(\d{8})$")
_FIELDS = {"bid": ("bid",), "ask": ("ask",), "last": ("last_trade_price", "last", "last_price"), "iv": ("iv", "implied_volatility"),
           "oi": ("open_interest", "oi"), "vol": ("volume",), "delta": ("delta",), "gamma": ("gamma",)}
_cache: dict = {}
_lock = threading.Lock()
TTL = 300   # the data is 15 min delayed anyway; one request per symbol per 5 minutes is plenty (community advice: <= 1 req/s)


def cboe_symbol(sym: str) -> str:
    s = sym.strip().upper().lstrip("^_")
    return "_" + s if s in INDEXES else s


def parse_occ(code: str):
    """'SPY261017C00500000' -> (root, Timestamp expiry, 'C'/'P', strike 500.0); None if it is not an OCC code."""
    m = _OCC.match(str(code).strip().upper().replace(" ", ""))
    if not m:
        return None
    root, ymd, cp, k = m.groups()
    return root, pd.Timestamp("20" + ymd[:2] + "-" + ymd[2:4] + "-" + ymd[4:]), cp, int(k) / 1000.0


def _num(row: dict, key: str):
    for k in _FIELDS[key]:
        v = row.get(k)
        if v is not None and v != "":
            try:
                return float(v)
            except (TypeError, ValueError):
                return None
    return None


def parse(payload: dict) -> tuple[float | None, pd.DataFrame]:
    """Cboe JSON -> (underlying price, chain frame with columns expiry, type, strike, bid, ask, last, iv, oi, vol, delta, gamma)."""
    data = (payload or {}).get("data") or {}
    opts = data.get("options") or []
    if not opts:
        raise ValueError("Cboe: no options in the response")
    px = None
    for k in ("current_price", "close", "last_trade_price", "price"):
        if data.get(k) not in (None, ""):
            px = float(data[k])
            break
    rows = []
    for o in opts:
        occ = parse_occ(o.get("option") or o.get("symbol") or "")
        if not occ:
            continue
        _, exp, cp, k = occ
        rows.append({"expiry": exp, "type": cp, "strike": k, **{f: _num(o, f) for f in _FIELDS}})
    if not rows:
        raise ValueError("Cboe: option codes not recognised (format changed?)")
    return px, pd.DataFrame(rows).sort_values(["expiry", "strike", "type"]).reset_index(drop=True)


def fetch(sym: str, timeout: int = 15):
    """-> (underlying price, chain). Cached for TTL seconds per symbol; raises with a clear message on failure."""
    s = cboe_symbol(sym)
    now = time.time()
    with _lock:
        hit = _cache.get(s)
    if hit and now - hit[0] < TTL:
        return hit[1]
    r = requests.get(URL.format(sym=s), headers=HDR, timeout=timeout)
    if r.status_code == 403:
        raise RuntimeError("Cboe refused the request (HTTP 403)")
    if r.status_code == 404:
        raise ValueError(f"Cboe: no option chain for {sym}")
    if r.status_code != 200:
        raise RuntimeError(f"Cboe HTTP {r.status_code}")
    out = parse(r.json())
    with _lock:
        _cache[s] = (now, out)
    return out


def summary(chain: pd.DataFrame, px: float | None, expiry=None) -> dict:
    """Put/call ratios (volume, open interest) over the whole chain + the max-pain strike of one expiry (default: nearest).
    Max pain = the expiry price at which option holders' total intrinsic value is smallest (a positioning statistic, not a forecast)."""
    c, p = chain[chain.type == "C"], chain[chain.type == "P"]
    sv = lambda d, k: float(d[k].fillna(0).sum())
    out = {"pc_vol": sv(p, "vol") / sv(c, "vol") if sv(c, "vol") else None, "pc_oi": sv(p, "oi") / sv(c, "oi") if sv(c, "oi") else None}
    exps = sorted(chain.expiry.unique())
    e = pd.Timestamp(expiry) if expiry is not None else (exps[0] if exps else None)
    out["expiry"] = e
    one = chain[chain.expiry == e]
    ks = sorted(one.strike.unique())
    if ks and one.oi.notna().any():
        cc, pp = one[one.type == "C"], one[one.type == "P"]
        pain = [(float((cc.oi.fillna(0) * (k - cc.strike).clip(lower=0)).sum() + (pp.oi.fillna(0) * (pp.strike - k).clip(lower=0)).sum()), k) for k in ks]
        out["max_pain"] = min(pain)[1]
    else:
        out["max_pain"] = None
    out["px"] = px
    return out


def near_money(chain: pd.DataFrame, px: float | None, expiry=None, n: int = 10) -> pd.DataFrame:
    """Calls and puts side by side for the n strikes closest to the price, one expiry (default: nearest)."""
    exps = sorted(chain.expiry.unique())
    e = pd.Timestamp(expiry) if expiry is not None else exps[0]
    one = chain[chain.expiry == e]
    ks = pd.Series(sorted(one.strike.unique()))
    if px:
        ks = ks.iloc[(ks - px).abs().argsort()[:n]].sort_values()
    else:
        ks = ks.iloc[: n]
    cols = ["bid", "ask", "last", "iv", "oi", "vol", "delta"]
    c = one[one.type == "C"].set_index("strike")[cols].add_prefix("C ")
    p = one[one.type == "P"].set_index("strike")[cols].add_prefix("P ")
    return c.join(p, how="outer").loc[lambda d: d.index.isin(ks)].reset_index()
