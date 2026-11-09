"""TIA market-risk context derived from existing dashboard order-flow adapters.

Descriptive risk overlay only: not an entry signal or position-size multiplier.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from modules.tia_market_evidence import MarketEvidenceSnapshot, collect_existing_orderflow


def _finite(value: Any) -> float | None:
    """Parse a finite metric; reject booleans, NaN, infinity and malformed values."""
    if value is None or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if math.isfinite(number) else None


@dataclass(frozen=True)
class MarketRiskThresholds:
    book_imbalance_abs: float = 0.15
    crowded_positive_funding_pct: float = 0.03
    crowded_long_short_ratio: float = 2.0
    thin_book_usd: float = 0.0

    def __post_init__(self):
        for name in ("book_imbalance_abs", "crowded_positive_funding_pct", "crowded_long_short_ratio"):
            value = getattr(self, name)
            parsed = _finite(value)
            if not isinstance(value, (int, float)) or isinstance(value, bool) or parsed is None or parsed <= 0:
                raise ValueError(f"{name} must be a finite numeric value and positive")
        value = self.thin_book_usd
        parsed = _finite(value)
        if not isinstance(value, (int, float)) or isinstance(value, bool) or parsed is None or parsed < 0:
            raise ValueError("thin_book_usd must be a finite numeric value and non-negative")


@dataclass(frozen=True)
class RiskFlag:
    code: str
    severity: str
    detail: str
    source: str


@dataclass(frozen=True)
class MarketRiskContext:
    asset: str
    asset_class: str
    source: str
    collected_at: str
    freshness: str
    directional_read: str
    flags: tuple[RiskFlag, ...]
    available_components: tuple[str, ...]
    unavailable_components: tuple[str, ...]
    execution_risk_status: str
    sizing_impact: str
    limitations: tuple[str, ...]


def _ok(raw: dict[str, Any], key: str) -> dict[str, Any] | None:
    value = raw.get(key)
    return value if isinstance(value, dict) and value.get("ok") is True else None


def build_market_risk_context(
    asset: str,
    asset_class: str,
    *,
    thresholds: MarketRiskThresholds | None = None,
    snapshot: MarketEvidenceSnapshot | None = None,
) -> MarketRiskContext:
    """Build transparent context from a supplied replay snapshot or existing feed."""
    limits = thresholds or MarketRiskThresholds()
    snap = snapshot or collect_existing_orderflow(asset, asset_class)
    raw = snap.evidence
    source = snap.collection_source
    flags: list[RiskFlag] = []
    available, unavailable = [], []

    for key in ("tape", "taker", "book", "deriv", "premium", "vp"):
        if _ok(raw, key) is None:
            unavailable.append(key)
        else:
            available.append(key)

    tape, taker, book, deriv = (_ok(raw, key) for key in ("tape", "taker", "book", "deriv"))
    directional_votes = []
    invalid_metrics = []

    def metric(container, key, label):
        value = _finite(container.get(key)) if container is not None else None
        if container is not None and container.get(key) is not None and value is None:
            invalid_metrics.append(label)
        return value

    share = metric(tape, "buy_share", "tape.buy_share")
    if share is not None:
        if share > 0.55:
            directional_votes.append(1)
        elif share < 0.45:
            directional_votes.append(-1)

    slope = metric(taker, "slope", "taker.slope")
    if slope is not None:
        if slope > 0:
            directional_votes.append(1)
        elif slope < 0:
            directional_votes.append(-1)

    imbalance = metric(book, "imbalance", "book.imbalance")
    if imbalance is not None:
        if imbalance > limits.book_imbalance_abs:
            directional_votes.append(1)
        elif imbalance < -limits.book_imbalance_abs:
            directional_votes.append(-1)

    if directional_votes and all(v > 0 for v in directional_votes):
        directional = "BUY_PRESSURE_CONSENSUS"
    elif directional_votes and all(v < 0 for v in directional_votes):
        directional = "SELL_PRESSURE_CONSENSUS"
    elif directional_votes:
        directional = "MIXED_FLOW"
    else:
        directional = "INSUFFICIENT_DIRECTIONAL_EVIDENCE"

    src = str(raw.get("src") or source)
    if book and imbalance is not None and abs(imbalance) >= limits.book_imbalance_abs:
        flags.append(RiskFlag(
            "ORDER_BOOK_IMBALANCE", "CAUTION",
            f"Snapshot imbalance {imbalance:+.3f}; displayed depth can cancel or change and is venue-specific.", src,
        ))
    if book and limits.thin_book_usd > 0:
        bid, ask = metric(book, "bid_usd", "book.bid_usd"), metric(book, "ask_usd", "book.ask_usd")
        if bid is not None and ask is not None:
            depth = bid + ask
            if depth < limits.thin_book_usd:
                flags.append(RiskFlag(
                    "THIN_DISPLAYED_BOOK", "HIGH",
                    f"Displayed depth inside the adapter band is {depth:.2f}, below configured review threshold {limits.thin_book_usd:.2f}.", src,
                ))
        else:
            invalid_metrics.append("book.depth_usd")

    if deriv:
        funding = metric(deriv, "funding", "deriv.funding")
        if funding is not None and funding >= limits.crowded_positive_funding_pct:
            flags.append(RiskFlag(
                "POSITIVE_FUNDING_CROWDING", "CAUTION",
                f"Funding {funding:+.4f}% meets/exceeds the configured positive-funding review threshold; this alone does not prove liquidation risk.", src,
            ))
        ratio = metric(deriv, "ls_ratio", "deriv.ls_ratio")
        if ratio is not None and ratio >= limits.crowded_long_short_ratio:
            flags.append(RiskFlag(
                "LONG_ACCOUNT_CROWDING", "CAUTION",
                f"Long/short account ratio {ratio:.3f} meets/exceeds the configured threshold; account count is not position size.", src,
            ))
        oi_change = metric(deriv, "oi_chg_7d", "deriv.oi_chg_7d")
        if oi_change is not None:
            flags.append(RiskFlag(
                "OPEN_INTEREST_CONTEXT", "INFO",
                f"Reported open-interest change over seven days: {oi_change:+.2f}%. Direction and price context are required for interpretation.", src,
            ))

    if invalid_metrics:
        flags.append(RiskFlag(
            "INVALID_PROVIDER_METRIC", "CAUTION",
            "Ignored non-finite or malformed metrics: " + ", ".join(sorted(set(invalid_metrics))),
            src,
        ))
    if not book and not tape:
        flags.append(RiskFlag(
            "ORDER_FLOW_UNAVAILABLE", "INFO",
            "Neither a valid book snapshot nor recent trade tape is available; do not infer liquidity or aggressor pressure.", src,
        ))
    if snap.freshness != "VERIFIED":
        flags.append(RiskFlag(
            "PROVIDER_TIMESTAMP_UNVERIFIED", "CAUTION",
            f"Freshness state is {snap.freshness}; local collection time is not a substitute for provider event time.", source,
        ))

    status = "REVIEW_REQUIRED" if flags else ("CONTEXT_ONLY" if available else "UNAVAILABLE")
    limitations = tuple(snap.limitations) + (
        "Thresholds are review heuristics, not validated predictive limits.",
        "No score or flag changes quantity, stop distance, leverage or order permissions.",
        "A public venue snapshot is not consolidated/global liquidity and may be cancelled.",
        "The existing volume-profile approximation is not exchange-level bid/ask footprint delta.",
        "Malformed, boolean, NaN and infinite provider metrics are ignored rather than converted to zero.",
    )
    return MarketRiskContext(
        asset=snap.asset, asset_class=snap.asset_class, source=src,
        collected_at=snap.collected_at.isoformat(), freshness=snap.freshness,
        directional_read=directional, flags=tuple(flags),
        available_components=tuple(available), unavailable_components=tuple(unavailable),
        execution_risk_status=status, sizing_impact="NONE_MARKET_CONTEXT_ONLY",
        limitations=limitations,
    )
