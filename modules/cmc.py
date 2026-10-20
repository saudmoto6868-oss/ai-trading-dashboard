"""CoinMarketCap panel data (Basic free plan: personal use, ~10k credits/month, no history).
Key: CMC_API_KEY in Streamlit secrets or env var - it stays on the server and never reaches the browser.
Two calls per refresh (listings + global metrics); callers must cache >= 15 min to stay inside the credits."""
from __future__ import annotations

import os

import requests

BASE = "https://pro-api.coinmarketcap.com"


def api_key() -> str:
    key = os.environ.get("CMC_API_KEY", "")
    if not key:
        try:
            import streamlit as st
            key = st.secrets.get("CMC_API_KEY", "")
        except Exception:
            key = ""
    return key


def parse(listings: dict, glob: dict) -> dict:
    coins = []
    for c in (listings or {}).get("data", []):
        q = (c.get("quote") or {}).get("USD") or {}
        coins.append({"rank": c.get("cmc_rank"), "sym": c.get("symbol"), "name": c.get("name"), "price": q.get("price"),
                      "mcap": q.get("market_cap"), "vol": q.get("volume_24h"), "h1": q.get("percent_change_1h"),
                      "d1": q.get("percent_change_24h"), "d7": q.get("percent_change_7d")})
    g = (glob or {}).get("data") or {}
    gq = (g.get("quote") or {}).get("USD") or {}
    return {"ok": True, "coins": coins, "global": {
        "mcap": gq.get("total_market_cap"), "vol": gq.get("total_volume_24h"), "btc_dom": g.get("btc_dominance"), "eth_dom": g.get("eth_dominance"),
        "mcap_ch": gq.get("total_market_cap_yesterday_percentage_change"), "vol_ch": gq.get("total_volume_24h_yesterday_percentage_change")}}


def fetch_cmc(key: str | None = None, limit: int = 100) -> dict:
    key = key or api_key()
    if not key:
        return {"ok": False, "err": "nokey"}
    h = {"X-CMC_PRO_API_KEY": key, "Accept": "application/json"}
    try:
        a = requests.get(BASE + "/v1/cryptocurrency/listings/latest", headers=h, params={"limit": limit, "convert": "USD"}, timeout=12)
        b = requests.get(BASE + "/v1/global-metrics/quotes/latest", headers=h, params={"convert": "USD"}, timeout=12)
        for r in (a, b):
            if r.status_code in (401, 403):
                return {"ok": False, "err": "badkey"}
            if r.status_code == 429:
                return {"ok": False, "err": "limit"}
            r.raise_for_status()
        return parse(a.json(), b.json())
    except Exception as e:   # never log the key
        return {"ok": False, "err": "net"}
