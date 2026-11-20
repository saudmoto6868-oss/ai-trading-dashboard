"""Gamma exposure (GEX) levels from an option chain: call wall, put wall, gamma flip.

Input: the chain frame from modules/cboe_options.py (columns expiry, type C/P, strike, iv, oi, gamma ...),
the underlying price and today's date. Cboe data is ~15 min delayed and OI is from the previous close.

HONEST LIMITS (see also modules/flow_manual.py, options section):
- This is the common *naive* estimate: it assumes dealers are long the calls and short the puts the public holds.
  Public data cannot tell who is long or short, so the sign is an assumption, not a fact.
- Providers disagree on GEX; the provider itself says GEX does not predict direction. Use as CONTEXT
  (agent 2 "context monitor"), never as an entry signal. Not tested against live data.

Units: GEX per 1 % move, in money = gamma * OI * multiplier * S^2 * 0.01 (calls +, puts -).
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

MULT = 100          # US equity / index options: 100 shares per contract (Deribit crypto options: 1 coin -> pass mult=1)
MIN_T = 1.0 / 365   # floor time to expiry at one day so 0DTE gamma does not blow up


def bs_gamma(S, K, T, iv, r: float = 0.0):
    """Black-Scholes gamma (same for calls and puts). Vectorised over numpy arrays."""
    S, K, T, iv = (np.asarray(x, dtype=float) for x in (S, K, T, iv))
    with np.errstate(divide="ignore", invalid="ignore"):
        sd = iv * np.sqrt(T)
        d1 = (np.log(S / K) + (r + 0.5 * iv * iv) * T) / sd
        g = np.exp(-0.5 * d1 * d1) / (math.sqrt(2 * math.pi) * S * sd)
    return np.where(np.isfinite(g), g, 0.0)


def _prep(chain: pd.DataFrame, today, max_days: int | None) -> pd.DataFrame:
    df = chain.copy()
    today = pd.Timestamp(today).normalize()
    df["T"] = ((pd.to_datetime(df["expiry"]) - today).dt.days.clip(lower=0) / 365.0).clip(lower=MIN_T)
    df = df[pd.to_datetime(df["expiry"]) >= today]
    if max_days is not None:
        df = df[df["T"] <= max_days / 365.0 + 1e-12]
    df["oi"] = pd.to_numeric(df["oi"], errors="coerce").fillna(0.0)
    df["iv"] = pd.to_numeric(df.get("iv"), errors="coerce").astype(float)   # float: whole-number IVs (Deribit sends 50) would make an int column
    # Cboe sometimes sends iv as a percent (25) instead of a fraction (0.25)
    df.loc[df["iv"] > 3, "iv"] = df.loc[df["iv"] > 3, "iv"] / 100.0
    df["sign"] = np.where(df["type"].astype(str).str.upper().str.startswith("C"), 1.0, -1.0)
    return df[df["oi"] > 0]


def _gex_at(df: pd.DataFrame, S: float, use_feed_gamma: bool, mult: float = MULT) -> np.ndarray:
    if use_feed_gamma and "gamma" in df and df["gamma"].notna().any():
        g = pd.to_numeric(df["gamma"], errors="coerce").to_numpy()
        fill = bs_gamma(S, df["strike"], df["T"], df["iv"].fillna(0))
        g = np.where(np.isfinite(g), g, fill)
    else:
        g = bs_gamma(S, df["strike"], df["T"], df["iv"].fillna(0))
    return g * df["oi"].to_numpy() * mult * S * S * 0.01 * df["sign"].to_numpy()


def by_strike(chain: pd.DataFrame, spot: float, today, max_days: int | None = None, mult: float = MULT) -> pd.DataFrame:
    """-> frame indexed by strike: call_gex (+), put_gex (-), net_gex. Uses the feed's gamma at the current spot."""
    df = _prep(chain, today, max_days)
    if df.empty:
        return pd.DataFrame(columns=["call_gex", "put_gex", "net_gex"])
    df = df.assign(gex=_gex_at(df, float(spot), use_feed_gamma=True, mult=mult))
    calls = df[df.sign > 0].groupby("strike")["gex"].sum()
    puts = df[df.sign < 0].groupby("strike")["gex"].sum()
    out = pd.DataFrame({"call_gex": calls, "put_gex": puts}).fillna(0.0).sort_index()
    out["net_gex"] = out.call_gex + out.put_gex
    return out


def gamma_flip(chain: pd.DataFrame, spot: float, today, max_days: int | None = None,
               width: float = 0.15, steps: int = 121, mult: float = MULT) -> float | None:
    """Spot level where total GEX changes sign, nearest to the current spot.

    Re-prices every contract's gamma (Black-Scholes, its own iv) on a grid spot*(1 +/- width).
    None when GEX keeps one sign on the whole grid or no contract has an iv.
    """
    df = _prep(chain, today, max_days)
    df = df[df["iv"].notna() & (df["iv"] > 0)]
    if df.empty:
        return None
    grid = np.linspace(spot * (1 - width), spot * (1 + width), steps)
    tot = np.array([_gex_at(df, s, use_feed_gamma=False, mult=mult).sum() for s in grid])
    flips = []
    for i in range(len(grid) - 1):
        a, b = tot[i], tot[i + 1]
        if a == 0:
            flips.append(grid[i])
        elif a * b < 0:
            flips.append(grid[i] + (grid[i + 1] - grid[i]) * (-a) / (b - a))   # linear interpolation
    if not flips:
        return None
    return float(min(flips, key=lambda x: abs(x - spot)))


def levels(chain: pd.DataFrame, spot: float, today, max_days: int | None = None, mult: float = MULT) -> dict:
    """-> {call_wall, put_wall, gamma_flip, net_gex, regime, n_contracts}.

    call_wall = strike with the largest call GEX, put_wall = strike with the largest (absolute) put GEX.
    regime: 'positive' (dealers dampen moves, ranges more likely) / 'negative' (moves can extend) - context only.
    """
    tbl = by_strike(chain, spot, today, max_days, mult)
    if tbl.empty:
        return {"call_wall": None, "put_wall": None, "gamma_flip": None, "net_gex": 0.0,
                "regime": None, "n_contracts": 0}
    net = float(tbl.net_gex.sum())
    return {
        "call_wall": float(tbl.call_gex.idxmax()) if (tbl.call_gex > 0).any() else None,
        "put_wall": float(tbl.put_gex.idxmin()) if (tbl.put_gex < 0).any() else None,
        "gamma_flip": gamma_flip(chain, spot, today, max_days, mult=mult),
        "net_gex": net,
        "regime": "positive" if net > 0 else "negative" if net < 0 else None,
        "n_contracts": int(len(_prep(chain, today, max_days))),
    }
