"""
THE RISK MANAGER
Turns a scored signal into a full trade plan: entry, stop loss, and 3
staged take-profits, using the nearest liquidity/support-resistance levels
and the RR rules from the framework doc (default 0.5% risk, partial-profit-
then-runner approach via staged RR multiples).

T3 (MEETING_ALERTS_SETUP.md): stop/entry/TP now depend on setup type.
Three books, chosen from signal keys present in score_result["signals"]:

  LEVELS book  (OB / FVG / SR zone retest)
    entry  = limit at zone edge (not market)
    stop   = beyond zone + 0.5 ATR buffer
    TP1    = nearest mid-level, TP2 = liquidity above/below, TP3 = structure target

  TREND book   (MA cross / SMA200 / Turtle breakout)
    entry  = market / breakout close
    stop   = last swing low/high (not SR)
    TP1/2/3 = ATR multiples (trailing logic implied)

  REVERSAL book (MSB-OB / liquidity sweep / Unicorn)
    entry  = close past BOS / after sweep wick
    stop   = behind the sweep candle + 0.3 ATR
    TP1    = nearest FVG, TP2 = OTE mid, TP3 = prior structure

When signals are mixed, REVERSAL > LEVELS > TREND in priority.
If no book matches, fall back to the original SR-based plan.
"""

from config import RR_TARGETS

# ── signal-key → book classification ─────────────────────────────────────────
_REVERSAL_KEYS  = frozenset({"msb_ob", "kzs", "liq_sweep", "sweep_high",
                              "sweep_low", "unicorn"})
_LEVELS_KEYS    = frozenset({"fib_ote", "fib_ext", "sr_bounce", "sr_break",
                              "vwap_reclaim", "vwap_reject"})
_TREND_KEYS     = frozenset({"ma_cross", "ma_slope", "sma200_cross",
                              "ema_stack", "ew_r3_v"})


def _detect_book(signals: list) -> str:
    """Return 'reversal', 'levels', 'trend', or 'fallback'."""
    keys = {s.get("key") for s in signals}
    if keys & _REVERSAL_KEYS:
        return "reversal"
    if keys & _LEVELS_KEYS:
        return "levels"
    if keys & _TREND_KEYS:
        return "trend"
    return "fallback"


def _atr_estimate(score_result: dict) -> float:
    """Rough ATR estimate from price when no candle data is available."""
    price = score_result.get("price", 1.0)
    return price * 0.005   # 0.5 % of price as ATR fallback


def build_trade_plan(score_result: dict) -> dict:
    """
    Build a setup-aware trade plan (T3).
    Returns entry, stop_loss, take_profits, risk_distance, direction, book.
    """
    price       = score_result["price"]
    bias        = score_result["trend_bias"]
    supports    = score_result.get("supports", [])
    resistances = score_result.get("resistances", [])
    signals     = score_result.get("signals", [])
    long        = (bias == "bullish")
    atr         = _atr_estimate(score_result)

    book = _detect_book(signals)

    # ── gather levels ─────────────────────────────────────────────────────────
    sup_below  = sorted([s for s in supports    if s < price], reverse=True)   # nearest first
    res_above  = sorted([r for r in resistances if r > price])                  # nearest first

    # Collect price points from signal metadata (zone edges, OTE etc.)
    sig_prices = {}
    for s in signals:
        sig_prices.update(s.get("prices", {}))
    zone_lo = sig_prices.get("lo") or sig_prices.get("ob_lo")
    zone_hi = sig_prices.get("hi") or sig_prices.get("ob_hi")
    swing_ref = sig_prices.get("inv") or sig_prices.get("start")

    # ── LEVELS book ───────────────────────────────────────────────────────────
    if book == "levels":
        if long:
            # entry = bottom of zone (limit); stop = below zone + atr buffer
            entry    = zone_lo if zone_lo else price
            stop_ref = (zone_lo - atr * 0.5) if zone_lo else price * 0.995
            mid_lvl  = res_above[0] if res_above else entry + atr * 2
            liq_lvl  = res_above[1] if len(res_above) > 1 else mid_lvl + atr * 2
        else:
            entry    = zone_hi if zone_hi else price
            stop_ref = (zone_hi + atr * 0.5) if zone_hi else price * 1.005
            mid_lvl  = sup_below[0] if sup_below else entry - atr * 2
            liq_lvl  = sup_below[1] if len(sup_below) > 1 else mid_lvl - atr * 2
        risk_distance = abs(entry - stop_ref) or atr
        if long:
            take_profits = [mid_lvl, liq_lvl, entry + risk_distance * RR_TARGETS[2]]
        else:
            take_profits = [mid_lvl, liq_lvl, entry - risk_distance * RR_TARGETS[2]]

    # ── TREND book ────────────────────────────────────────────────────────────
    elif book == "trend":
        entry = price   # market / breakout
        if long:
            # stop = last swing low (from signals) or nearest support
            stop_ref = swing_ref if (swing_ref and swing_ref < price) else (sup_below[0] if sup_below else price * 0.99)
            risk_distance = price - stop_ref
            take_profits  = [entry + risk_distance * rr for rr in RR_TARGETS]
        else:
            stop_ref = swing_ref if (swing_ref and swing_ref > price) else (res_above[0] if res_above else price * 1.01)
            risk_distance = stop_ref - price
            take_profits  = [entry - risk_distance * rr for rr in RR_TARGETS]

    # ── REVERSAL book ─────────────────────────────────────────────────────────
    elif book == "reversal":
        entry = price   # close past BOS / after sweep wick
        if long:
            stop_ref = (swing_ref - atr * 0.3) if (swing_ref and swing_ref < price) else price - atr * 1.5
            risk_distance = price - stop_ref
            fvg_target = res_above[0] if res_above else entry + risk_distance * 1.5
            ote_mid    = res_above[1] if len(res_above) > 1 else fvg_target + risk_distance
            structure  = res_above[2] if len(res_above) > 2 else ote_mid + risk_distance
            take_profits = [fvg_target, ote_mid, structure]
        else:
            stop_ref = (swing_ref + atr * 0.3) if (swing_ref and swing_ref > price) else price + atr * 1.5
            risk_distance = stop_ref - price
            fvg_target = sup_below[0] if sup_below else entry - risk_distance * 1.5
            ote_mid    = sup_below[1] if len(sup_below) > 1 else fvg_target - risk_distance
            structure  = sup_below[2] if len(sup_below) > 2 else ote_mid - risk_distance
            take_profits = [fvg_target, ote_mid, structure]

    # ── FALLBACK (original SR-based plan) ────────────────────────────────────
    else:
        entry = price
        if long:
            stop_ref      = sup_below[0] if sup_below else price * 0.995
            risk_distance = price - stop_ref
            take_profits  = [entry + risk_distance * rr for rr in RR_TARGETS]
        else:
            stop_ref      = res_above[0] if res_above else price * 1.005
            risk_distance = stop_ref - price
            take_profits  = [entry - risk_distance * rr for rr in RR_TARGETS]

    # ── direction sanity ──────────────────────────────────────────────────────
    stop_loss = stop_ref
    if risk_distance <= 0:
        risk_distance = atr
        stop_loss = entry - atr if long else entry + atr
        take_profits = [entry + atr * rr if long else entry - atr * rr for rr in RR_TARGETS]

    return {
        "entry":         round(entry, 5),
        "stop_loss":     round(stop_loss, 5),
        "take_profits":  [round(tp, 5) for tp in take_profits],
        "risk_distance": round(risk_distance, 5),
        "direction":     "Long" if long else "Short",
        "book":          book,   # T3: which playbook was used
    }


BARS_PER_YEAR = {"1m": 525600, "5m": 105120, "15m": 35040, "30m": 17520, "1h": 8760, "4h": 2190, "1d": 365, "1w": 52, "13m": 40431, "2h": 4380, "3h": 2920, "6h": 1460, "7h": 1251, "8h": 1095, "12h": 730, "3d": 122, "1mo": 12}


def vol_target_weight(df, tf: str, target: float = 0.25, lookback: int = 60) -> dict | None:
    """Volatility-based position size: the share of the capital set aside for this trade so that the position's
    annualised volatility equals `target` (default 25%, this dashboard's choice). Capped at 100% (no leverage)."""
    import numpy as np
    try:
        c = df["close"].astype(float).values
        r = np.diff(np.log(c[-(lookback + 1):]))
        if len(r) < 20:
            return None
        bpy = BARS_PER_YEAR.get(tf)
        if not bpy:
            step = (df["time"].iloc[-1] - df["time"].iloc[-2]).total_seconds()
            bpy = 31_536_000 / step if step > 0 else 8760
        vol = float(np.std(r, ddof=1) * np.sqrt(bpy))
        if vol <= 0 or not np.isfinite(vol):
            return None
        return {"ann_vol": round(vol, 4), "target": target, "weight": round(min(1.0, target / vol), 4)}
    except Exception:
        return None
