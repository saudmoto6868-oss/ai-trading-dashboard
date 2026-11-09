"""Adapters from existing trusted providers into TIA's evidence contract.

These adapters do not fetch data and do not invent missing values. Provider
fetching, caching and credentials remain owned by the existing modules.
"""
from __future__ import annotations

from datetime import date, datetime, time, timezone
from typing import Iterable, Optional

from modules.tia_evidence import EvidenceQuality, MetricEvidence


def _fred_observation_timestamp(value: str) -> str:
    """Represent FRED's date-only observation as UTC midnight, explicitly noting its precision."""
    day = date.fromisoformat(value)
    return datetime.combine(day, time.min, tzinfo=timezone.utc).isoformat()


def fred_evidence(rows: Iterable[dict]) -> list[MetricEvidence]:
    """Convert non-missing FRED rows; source dates remain observation dates, not fetch times."""
    specs = {
        "CPI (YoY %)": ("macro.us_cpi_yoy", "%", "CPIAUCSL"),
        "Fed funds %": ("macro.us_fed_funds", "%", "FEDFUNDS"),
        "US 10Y yield %": ("macro.us_10y_yield", "%", "DGS10"),
        "Unemployment %": ("macro.us_unemployment", "%", "UNRATE"),
    }
    result = []
    for row in rows or []:
        label = row.get("label")
        spec = specs.get(label)
        value = row.get("value")
        observed_date = row.get("date")
        if not spec or value is None or not observed_date:
            continue
        metric_id, unit, symbol = spec
        try:
            observed_at = _fred_observation_timestamp(observed_date)
            numeric = float(value)
        except (TypeError, ValueError):
            continue
        result.append(MetricEvidence(
            metric_id=metric_id, value=numeric, unit=unit, source="FRED",
            observed_at=observed_at, coverage="US national macro series",
            quality=EvidenceQuality.VERIFIED, provider_symbol=symbol,
            notes="FRED observation date; exact publication time is not supplied by this adapter.",
        ))
    return result


def cmc_evidence(payload: dict, *, fetched_at: Optional[datetime] = None) -> list[MetricEvidence]:
    """Convert CoinMarketCap global metrics; fetch timestamp is supplied by the caller."""
    if not isinstance(payload, dict) or not payload.get("ok"):
        return []
    global_data = payload.get("global") or {}
    observed = fetched_at or datetime.now(timezone.utc)
    if observed.tzinfo is None:
        raise ValueError("fetched_at must include a timezone")
    observed_at = observed.astimezone(timezone.utc).isoformat()
    specs = (
        ("mcap", "crypto.global_market_cap_usd", "USD", "Global crypto market capitalization"),
        ("vol", "crypto.global_volume_24h_usd", "USD/24h", "Global crypto 24-hour volume"),
        ("btc_dom", "crypto.btc_dominance", "%", "Bitcoin share of total crypto market capitalization"),
        ("eth_dom", "crypto.eth_dominance", "%", "Ethereum share of total crypto market capitalization"),
    )
    result = []
    for field, metric_id, unit, coverage in specs:
        value = global_data.get(field)
        if value is None:
            continue
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            continue
        result.append(MetricEvidence(
            metric_id=metric_id, value=numeric, unit=unit, source="CoinMarketCap",
            observed_at=observed_at, coverage=coverage,
            quality=EvidenceQuality.VERIFIED,
            notes="Provider snapshot; timestamp is the local fetch time, not an exchange event time.",
        ))
    return result
