"""TIA market-evidence bridge to data sources already present in AI Trading Dashboard.

This bridge reuses existing provider modules; it does not create a second feed stack.
Market evidence is context for risk review, never an account-balance substitute.
Collection time is not misrepresented as provider event time.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class SourceDescriptor:
    source_id: str
    provider: str
    coverage: tuple[str, ...]
    access: str
    known_limitations: tuple[str, ...]


SOURCE_CATALOG = (
    SourceDescriptor(
        "okx_public_market", "OKX",
        ("spot candles", "spot trades", "order book snapshots", "taker volume",
         "perpetual open interest", "funding", "long/short account ratio"),
        "public REST; no account authentication",
        ("single venue only", "book endpoint is a snapshot, not a full event replay",
         "public market endpoints do not expose the user's account balance or positions"),
    ),
    SourceDescriptor(
        "hyperliquid_xyz", "Hyperliquid",
        ("xyz perpetual prices", "candles", "order book", "recent trades",
         "funding", "open interest"),
        "public info API; no account authentication",
        ("perpetual oracle price can differ from the underlying cash market",
         "thinner coverage than OKX", "public market data is not user account data"),
    ),
    SourceDescriptor(
        "deribit_options", "Deribit",
        ("BTC options", "ETH options", "book summaries", "DVOL history"),
        "public API; no account authentication",
        ("market context only", "open interest and volume do not identify opening versus closing trades"),
    ),
    SourceDescriptor(
        "cboe_delayed_options", "Cboe",
        ("US equity and index option chains",),
        "public delayed quotes",
        ("approximately 15-minute delay", "unofficial endpoint in current adapter",
         "reuse terms and endpoint stability not confirmed"),
    ),
    SourceDescriptor(
        "finnhub_news", "Finnhub",
        ("general and category news",),
        "API key required; configured through existing dashboard secrets",
        ("fallbacks may use Alpha Vantage or RSS", "headline availability does not establish price impact"),
    ),
    SourceDescriptor(
        "dashboard_workspace", "AI Trading Dashboard",
        ("chart candles", "footprint calculations", "order-flow confluence",
         "levels", "journal records", "news context"),
        "existing in-app state and modules",
        ("chart/footprint coverage depends on the selected chart and enabled feeds",
         "journal is not a broker-confirmed statement"),
    ),
)


@dataclass(frozen=True)
class FeedHealth:
    key: str
    available: bool
    source: str
    reason: str = ""


@dataclass(frozen=True)
class MarketEvidenceSnapshot:
    asset: str
    asset_class: str
    collected_at: datetime
    collection_source: str
    provider_event_time: None
    freshness: str
    evidence: dict[str, Any]
    health: tuple[FeedHealth, ...]
    limitations: tuple[str, ...]


def collect_existing_orderflow(asset: str, asset_class: str) -> MarketEvidenceSnapshot:
    """Collect through the dashboard's existing spot_flow.fetch adapter.

    asset_class accepts the existing adapter's 'crypto' or 'metals' routing.
    The adapter catches provider errors and reports per-feed ok/why values.
    """
    if not isinstance(asset, str) or not asset.strip():
        raise ValueError("asset is required")
    cls = str(asset_class).strip().lower()
    if cls not in ("crypto", "metals"):
        raise ValueError("existing order-flow adapter supports crypto or metals")
    from modules import spot_flow

    raw = spot_flow.fetch(asset.strip().upper(), cls)
    if not isinstance(raw, dict):
        raise ValueError("spot_flow.fetch returned an unexpected payload")
    source = str(raw.get("src") or ("OKX" if cls == "crypto" else "Hyperliquid"))
    health = []
    for key, value in raw.items():
        if key == "src":
            continue
        ok = isinstance(value, dict) and value.get("ok") is True
        reason = "" if ok else str(value.get("why") or "feed unavailable or payload not validated")
        health.append(FeedHealth(key=key, available=ok, source=source, reason=reason))
    limitations = [
        "collection time is recorded locally; provider event timestamps are not normalized by the existing adapter",
        "market evidence is not broker account state and must not be used as balance, equity, margin or fill evidence",
        "single-venue order flow is partial market coverage",
    ]
    if cls == "metals":
        limitations.append("Hyperliquid xyz instruments are perpetual contracts, not the underlying cash-market feed")
    return MarketEvidenceSnapshot(
        asset=asset.strip().upper(),
        asset_class=cls,
        collected_at=datetime.now(timezone.utc),
        collection_source="modules.spot_flow.fetch",
        provider_event_time=None,
        freshness="UNVERIFIED_PROVIDER_TIMESTAMP",
        evidence=raw,
        health=tuple(health),
        limitations=tuple(limitations),
    )


def account_data_capabilities() -> dict[str, str]:
    """State honestly what current dashboard market adapters can prove about an account."""
    return {
        "balance": "UNAVAILABLE_NO_AUTHENTICATED_BROKER_ACCOUNT_ADAPTER",
        "equity": "UNAVAILABLE_NO_AUTHENTICATED_BROKER_ACCOUNT_ADAPTER",
        "used_margin": "UNAVAILABLE_NO_AUTHENTICATED_BROKER_ACCOUNT_ADAPTER",
        "free_margin": "UNAVAILABLE_NO_AUTHENTICATED_BROKER_ACCOUNT_ADAPTER",
        "pending_orders": "UNAVAILABLE_NO_AUTHENTICATED_BROKER_ACCOUNT_ADAPTER",
        "broker_fills": "UNAVAILABLE_NO_AUTHENTICATED_BROKER_ACCOUNT_ADAPTER",
        "broker_fees": "UNAVAILABLE_NO_AUTHENTICATED_BROKER_ACCOUNT_ADAPTER",
        "broker_funding": "UNAVAILABLE_NO_AUTHENTICATED_BROKER_ACCOUNT_ADAPTER",
        "market_prices_and_orderflow": "AVAILABLE_THROUGH_EXISTING_PUBLIC_ADAPTERS_SUBJECT_TO_FEED_HEALTH",
    }
