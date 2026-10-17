"""Item 15c: cross-sectional (cross-sector) momentum - the hedge-fund relative-strength ranking.

Method (daily closes, 21 bars = 1 month):
  * 12-1 return  = close 21 bars ago / close 252 bars ago - 1  (the latest month is skipped: short-term reversal)
  * 6-1 return   = close 21 bars ago / close 126 bars ago - 1
  * 3-month      = last close / close 63 bars ago - 1
  * volatility   = annualised stdev of the last 63 daily returns
  * score        = 12-1 return / volatility (risk-adjusted), ranked high -> low
  * absolute filter (dual momentum): a market is a LONG CANDIDATE only if its 12-1 return > 0 AND the close is above SMA 200;
    the bottom of the ranking with a negative 12-1 return and below SMA 200 is flagged AVOID.
Crypto trades every day, so 252 bars there are ~8.3 calendar months, not 12 (stated in the UI).
A ranking, not a forecast: nothing here has been backtested in this project.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

M = 21
US_SECTORS = {"Y:XLK": "Technology", "Y:XLF": "Financials", "Y:XLE": "Energy", "Y:XLV": "Health care", "Y:XLY": "Consumer discretionary",
              "Y:XLP": "Consumer staples", "Y:XLI": "Industrials", "Y:XLB": "Materials", "Y:XLU": "Utilities", "Y:XLRE": "Real estate",
              "Y:XLC": "Communication"}
CRYPTO_MAJORS = {s: s.split("-")[0] for s in ("BTC-USDT", "ETH-USDT", "SOL-USDT", "BNB-USDT", "XRP-USDT", "DOGE-USDT", "ADA-USDT",
                                              "AVAX-USDT", "LINK-USDT", "DOT-USDT")}
UNIVERSES = {"US sectors (SPDR ETFs)": US_SECTORS, "Crypto majors": CRYPTO_MAJORS}
NEED = 12 * M + 1


def stats(close) -> dict | None:
    """Momentum numbers for one close series (oldest -> newest). None when there are fewer than 253 closes."""
    c = np.asarray(pd.Series(close).dropna(), dtype=float)
    if len(c) < NEED or (c <= 0).any():
        return None
    r = np.diff(c[-(3 * M + 1):]) / c[-(3 * M + 1):-1]
    vol = float(np.std(r, ddof=1) * math.sqrt(252))
    m12 = c[-1 - M] / c[-1 - 12 * M] - 1
    return {"ret_12_1": float(m12), "ret_6_1": float(c[-1 - M] / c[-1 - 6 * M] - 1), "ret_3m": float(c[-1] / c[-1 - 3 * M] - 1),
            "vol": vol, "score": float(m12 / vol) if vol > 0 else 0.0, "above_200": bool(c[-1] > c[-200:].mean())}


def rank(closes: dict, names: dict | None = None) -> pd.DataFrame:
    """closes = {symbol: close series}. -> one row per symbol with enough history, best score first."""
    rows = []
    for sym, cl in closes.items():
        st = stats(cl)
        if st is None:
            continue
        rows.append({"symbol": sym, "name": (names or {}).get(sym, sym), **st})
    if not rows:
        return pd.DataFrame(columns=["rank", "symbol", "name", "ret_12_1", "ret_6_1", "ret_3m", "vol", "score", "above_200", "call"])
    df = pd.DataFrame(rows).sort_values("score", ascending=False).reset_index(drop=True)
    df.insert(0, "rank", range(1, len(df) + 1))
    third = max(1, len(df) // 3)

    def call(r):
        if r["rank"] <= third and r["ret_12_1"] > 0 and r["above_200"]:
            return "LONG candidate"
        if r["rank"] > len(df) - third and r["ret_12_1"] < 0 and not r["above_200"]:
            return "AVOID"
        return "neutral"
    df["call"] = df.apply(call, axis=1)
    return df


def fetch_closes(universe: dict, get=None, limit: int = 300) -> tuple[dict, list]:
    """Daily closes for each symbol via market_cache (OKX, or Yahoo for 'Y:' symbols). -> (closes, errors)."""
    if get is None:
        from modules.market_cache import get_klines as get
    closes, errs = {}, []
    for sym in universe:
        try:
            df = get(sym, "1d", limit)
            closes[sym] = df["close"].astype(float).reset_index(drop=True)
        except Exception as e:  # one market failing must not hide the rest
            errs.append(f"{universe[sym]}: {e}")
    return closes, errs
