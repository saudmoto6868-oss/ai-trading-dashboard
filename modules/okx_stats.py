"""Server-side OKX rubik stats (open interest, long/short ratio, taker volume) for the Workspace.

The browser page cannot read these endpoints (CORS, and OKX rate limits per IP), so the server fetches them and
hands them to the page as CFG['rubik'], keyed by the exact request path the page uses. The page checks that map
before it calls OKX itself. If the server cannot reach OKX, the map stays empty and the page behaves as before.
Owner console, 2026-10-19: rubik calls failed with CORS / ERR_FAILED from the browser.
"""
from __future__ import annotations

import time

import requests

OKX = "https://www.okx.com/api/v5"
TTL_SECONDS = 300          # rubik stats move slowly; one fetch per symbol per 5 minutes is enough
DOWN_SECONDS = 600         # after a connection failure, do not try again for 10 minutes (no slow page loads)
MAX_SYMBOLS = 6            # each symbol costs 7 requests; keep the load small

_cache: dict = {}          # path -> (fetched_at, data)
_down_until = 0.0


def paths_for(base: str) -> list[str]:
    """The exact paths the Workspace asks for, for one base currency (BTC, ETH, ...)."""
    sw = base + "-USDT-SWAP"
    return [
        f"/rubik/stat/contracts/open-interest-volume?ccy={base}&period=1H",
        f"/rubik/stat/contracts/open-interest-volume?ccy={base}&period=5m",
        f"/rubik/stat/contracts/long-short-account-ratio?ccy={base}&period=1H",
        f"/rubik/stat/taker-volume?ccy={base}&instType=CONTRACTS&period=1H",
        f"/rubik/stat/contracts/open-interest-history?instId={sw}&period=1H&limit=48",
        f"/rubik/stat/contracts/long-short-account-ratio-contract?instId={sw}&period=1H&limit=48",
        f"/rubik/stat/taker-volume-contract?instId={sw}&period=1H&limit=48",
    ]


def _get(path: str, timeout: float = 8.0):
    global _down_until
    hit = _cache.get(path)
    if hit and time.time() - hit[0] < TTL_SECONDS:
        return hit[1]
    if time.time() < _down_until:
        raise ConnectionError("OKX stats paused after a connection failure")
    try:
        r = requests.get(OKX + path, timeout=timeout, headers={"User-Agent": "XPiX-Dashboard/1"})
    except requests.RequestException:
        _down_until = time.time() + DOWN_SECONDS
        raise
    if r.status_code != 200:
        raise RuntimeError(f"OKX HTTP {r.status_code}")
    j = r.json()
    if str(j.get("code")) != "0":
        raise RuntimeError(j.get("msg") or "OKX error")
    _cache[path] = (time.time(), j.get("data"))
    return j.get("data")


def rubik_for(symbols) -> dict:
    """{path: data} for the watchlist's base currencies. Missing paths are simply left out."""
    bases: list[str] = []
    for s in symbols or []:
        b = str(s).split("-")[0].upper()
        if b.isalnum() and b not in bases:
            bases.append(b)
    out: dict = {}
    for b in bases[:MAX_SYMBOLS]:
        for p in paths_for(b):
            try:
                out[p] = _get(p)
            except Exception:
                continue
    return out
