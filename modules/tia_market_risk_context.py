"""TIA market-risk context derived from existing dashboard order-flow adapters.

This is a descriptive risk overlay, not an entry signal and not an automatic
position-size multiplier. Thresholds are explicit, configurable review
thresholds; they are not calibrated risk limits or owner-approved policy.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from modules.tia_market_evidence import MarketEvidenceSnapshot, collect_existing_orderflow


@dataclass(frozen=True)
class MarketRiskThresholds:
    book_imbalance_abs: float = 0.15
    crowded_positive_funding_pct: float = 0.03
    crowded_long_short_ratio: float = 2.0
    thin_book_usd: float = 0.0

    def __post_init__(self):
        import math
        for name in ("book_imbalance_abs", "crowded_positive_funding_pct", "crowded_long_short_ratio"):
            value = float(getattr(self, name))
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be finite and positive")
        value = float(self.thin_book_usd)
        if not math.isfinite(value) or value < 0:
            raise ValueError("thin_book_usd must be finite and non-negative")


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
    """Build a transparent context from the dashboard's existing feed.

    A supplied snapshot is useful for deterministic tests and replay. Otherwise
    the existing OKX/Hyperliquid public adapter is called.
    """
    limits = thresholds or MarketRiskThresholds()
    snap = snapshot or collect_existing_orderflow(asset, asset_class)
    raw = snap.evidence
    source = snap.collection_source
    flags: list[RiskFlag] = []
    available, unavailable = [], []

    for key in ("tape", "taker", "book", "deriv", "premium", "vp"):
        item = _ok(raw, key)
        if item is None:
            unavailable.append(key)
        else:
            available.append(key)

    tape = _ok(raw, "tape")
    taker = _ok(raw, "taker")
    book = _ok(raw, "book")
    deriv = _ok(raw, "deriv")

    directional_votes = []
    if tape:
        share = float(tape.get("buy_share", 0.5))
        if share > 0.55:
            directional_votes.append(1)
        elif share < 0.45:
            directional_votes.append(-1)
    if taker:
        slope = float(taker.get("slope", 0.0))
        if slope > 0:
            directional_votes.append(1)
        elif slope < 0:
            directional_votes.append(-1)
    if book:
        imbalance = float(book.get("imbalance", 0.0))
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

    if book:
        imbalance = float(book.get("imbalance", 0.0))
        if abs(imbalance) >= limits.book_imbalance_abs:
            flags.append(RiskFlag(
                "ORDER_BOOK_IMBALANCE", "CAUTION",
                f"Snapshot imbalance {imbalance:+.3f}; displayed depth can cancel or change and is venue-specific.",
                str(raw.get("src") or source),
            ))
        if limits.thin_book_usd > 0:
            depth = float(book.get("bid_usd", 0.0)) + float(book.get("ask_usd", 0.0))
            if depth < limits.thin_book_usd:
                flags.append(RiskFlag(
                    "THIN_DISPLAYED_BOOK", "HIGH",
                    f"Displayed depth inside the adapter band is {depth:.2f}, below configured review threshold {limits.thin_book_usd:.2f}.",
                    str(raw.get("src") or source),
                ))

    if deriv:
        funding = deriv.get("funding")
        if funding is not None and float(funding) >= limits.crowded_positive_funding_pct:
            flags.append(RiskFlag(
                "POSITIVE_FUNDING_CROWDING", "CAUTION",
                f"Funding {float(funding):+.4f}% meets/exceeds the configured positive-funding review threshold; this alone does not prove liquidation risk.",
                str(raw.get("src") or source),
            ))
        ratio = deriv.get("ls_ratio")
        if ratio is not None and float(ratio) >= limits.crowded_long_short_ratio:
            flags.append(RiskFlag(
                "LONG_ACCOUNT_CROWDING", "CAUTION",
                f"Long/short account ratio {float(ratio):.3f} meets/exceeds the configured threshold; account count is not position size.",
                str(raw.get("src") or source),
            ))
        oi_change = deriv.get("oi_chg_7d")
        if oi_change is not None:
            flags.append(RiskFlag(
                "OPEN_INTEREST_CONTEXT", "INFO",
                f"Reported open-interest change over seven days: {float(oi_change):+.2f}%. Direction and price context are required for interpretation.",
                str(raw.get("src") or source),
            ))

    if not book and not tape:
        flags.append(RiskFlag(
            "ORDER_FLOW_UNAVAILABLE", "INFO",
            "Neither a valid book snapshot nor recent trade tape is available; do not infer liquidity or aggressor pressure.",
            str(raw.get("src") or source),
        ))

    if snap.freshness != "VERIFIED":
        flags.append(RiskFlag(
            "PROVIDER_TIMESTAMP_UNVERIFIED", "CAUTION",
            f"Freshness state is {snap.freshness}; local collection time is not a substitute for provider event time.",
            source,
        ))

    status = "REVIEW_REQUIRED" if flags else (
        "CONTEXT_ONLY" if available else "UNAVAILABLE"
    )
    return MarketRiskContext(
        asset=snap.asset,
        asset_class=snap.asset_class,
        source=str(raw.get("src") or source),
        collected_at=snap.collected_at.isoformat(),
        freshness=snap.freshness,
        directional_read=directional,
        flags=tuple(flags),
        available_components=tuple(available),
        unavailable_components=tuple(unavailable),
        execution_risk_status=status,
        sizing_impact="NONE_MARKET_CONTEXT_ONLY",
        limitations=tuple(snap.limitations) + (
            "Thresholds are review heuristics, not validated predictive limits.",
            "No score or flag changes quantity, stop distance, leverage or order permissions.",
            "A public venue snapshot is not consolidated/global liquidity and may be cancelled.",
            "The existing volume-profile approximation is not exchange-level bid/ask footprint delta.",
        ),
    )
