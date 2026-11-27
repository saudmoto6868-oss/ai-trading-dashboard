"""Read-only options risk context using the Dashboard's existing adapters.

Options positioning and estimated gamma exposure are descriptive context only.
They are not directional forecasts, execution instructions, or risk-limit inputs.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any


@dataclass(frozen=True)
class OptionsRiskContext:
    asset: str
    asset_class: str
    provider: str
    status: str
    collected_at: str
    metrics: dict[str, Any]
    limitations: tuple[str, ...]
    unavailable: tuple[str, ...]


def _finite(value: Any) -> float | None:
    import math
    if value is None or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if math.isfinite(number) else None


def _error(exc: Exception) -> str:
    # Preserve a useful diagnostic without exposing response bodies or secrets.
    message = str(exc).strip().replace("\n", " ")
    return f"{type(exc).__name__}: {message[:240]}" if message else type(exc).__name__


def build_options_risk_context(
    asset: str,
    asset_class: str,
    *,
    today: date | None = None,
) -> OptionsRiskContext:
    """Collect existing crypto or US listed-options context; never places orders."""
    symbol = str(asset).strip().upper()
    kind = str(asset_class).strip().lower()
    collected = datetime.now(timezone.utc).isoformat()
    metrics: dict[str, Any] = {}
    unavailable: list[str] = []
    limitations: list[str] = [
        "Open interest and volume do not identify opening versus closing trades, dealer inventory, or hedging intent.",
        "Put/call ratios, max pain, walls and gamma estimates are context, not directional or entry signals.",
        "No metric in this module changes quantity, leverage, stops, order permissions or risk-policy limits.",
    ]

    if kind in {"crypto", "cryptocurrency"}:
        if symbol not in {"BTC", "ETH"}:
            return OptionsRiskContext(symbol, kind, "Deribit", "UNSUPPORTED_ASSET",
                collected, {}, tuple(limitations), ("Deribit public options coverage is limited here to BTC and ETH.",))
        from modules import options_desk

        try:
            rows = options_desk.fetch(symbol)
            summary = options_desk.summarize(rows, today=today)
            totals = summary.get("totals") or {}
            expiries = summary.get("expiries") or []
            nearest = expiries[0] if expiries else {}
            metrics.update({
                "spot_proxy": _finite(summary.get("spot")),
                "total_open_interest": _finite(totals.get("oi")),
                "put_call_oi_ratio": _finite(totals.get("pc_oi")),
                "total_option_volume": _finite(totals.get("vol")),
                "nearest_expiry": str(nearest.get("exp")) if nearest.get("exp") else None,
                "nearest_expiry_days": _finite(nearest.get("days")),
                "nearest_expiry_atm_iv": _finite(nearest.get("iv")),
                "nearest_expiry_skew_10": _finite(nearest.get("skew10")),
                "nearest_expiry_put_call_volume": _finite(nearest.get("pc_vol")),
                "nearest_expiry_max_pain": _finite(nearest.get("max_pain")),
                "nearest_expiry_open_interest_walls": nearest.get("walls", []),
                "expiry_count": len(expiries),
            })
            if not rows:
                unavailable.append("option_book_empty")
        except Exception as exc:
            unavailable.append("option_book: " + _error(exc))

        try:
            history = options_desk.dvol(symbol)
            values = [_finite(item[1]) for item in history if isinstance(item, (tuple, list)) and len(item) >= 2]
            values = [value for value in values if value is not None]
            rank = options_desk.iv_rank(values)
            metrics["dvol_history_observations"] = len(values)
            metrics["dvol_iv_rank"] = rank
            metrics["dvol_latest"] = _finite(values[-1]) if values else None
            if not values:
                unavailable.append("dvol_history_empty")
            elif rank is None:
                unavailable.append("dvol_iv_rank_requires_at_least_30_non_flat_observations")
        except Exception as exc:
            unavailable.append("dvol: " + _error(exc))

        limitations.extend((
            "Deribit spot field is the nearest-expiry underlying/forward proxy, not a separately verified index spot.",
            "Deribit public options context covers BTC/ETH only; it is not a proxy for other crypto assets.",
            "DVOL rank/percentile is based on the returned daily history and is unavailable for short or flat samples.",
        ))
        status = "AVAILABLE_WITH_LIMITATIONS" if metrics else "UNAVAILABLE"
        return OptionsRiskContext(symbol, kind, "Deribit public API", status, collected,
                                  metrics, tuple(limitations), tuple(unavailable))

    if kind in {"stock", "equity", "index", "us_options"}:
        from modules import cboe_options, gex
        try:
            px, chain = cboe_options.fetch(symbol)
            base = cboe_options.summary(chain, px)
            metrics.update({
                "underlying_price": _finite(px),
                "put_call_volume_ratio": _finite(base.get("pc_vol")),
                "put_call_open_interest_ratio": _finite(base.get("pc_oi")),
                "nearest_expiry": str(base.get("expiry")) if base.get("expiry") is not None else None,
                "nearest_expiry_max_pain": _finite(base.get("max_pain")),
                "option_contract_rows": int(len(chain)),
            })
            if px is None or _finite(px) is None or _finite(px) <= 0:
                unavailable.append("gex_requires_valid_underlying_price")
            elif chain.empty:
                unavailable.append("gex_requires_nonempty_option_chain")
            else:
                levels = gex.levels(chain, float(px), today or date.today())
                metrics["estimated_gex"] = {
                    "call_wall": _finite(levels.get("call_wall")),
                    "put_wall": _finite(levels.get("put_wall")),
                    "gamma_flip": _finite(levels.get("gamma_flip")),
                    "net_gex_per_1pct_move": _finite(levels.get("net_gex")),
                    "regime_assumption": levels.get("regime"),
                    "contract_rows_used": int(levels.get("n_contracts") or 0),
                }
        except Exception as exc:
            unavailable.append("cboe_options: " + _error(exc))
        limitations.extend((
            "Cboe delayed-quotes data is approximately 15 minutes delayed and uses an undocumented public endpoint; availability and fields may change.",
            "Cboe open interest is not necessarily intraday and cannot reveal dealer positioning.",
            "Estimated GEX assumes calls positive and puts negative; actual dealer inventory/sign is unknown.",
            "GEX uses the existing US-options contract multiplier of 100 and is not validated for every instrument.",
        ))
        status = "AVAILABLE_WITH_LIMITATIONS" if metrics else "UNAVAILABLE"
        return OptionsRiskContext(symbol, kind, "Cboe delayed quotes + dashboard GEX estimator",
                                  status, collected, metrics, tuple(limitations), tuple(unavailable))

    return OptionsRiskContext(symbol, kind, "none", "UNSUPPORTED_ASSET_CLASS",
        collected, {}, tuple(limitations), ("No existing Dashboard options adapter is mapped to this asset class.",))
