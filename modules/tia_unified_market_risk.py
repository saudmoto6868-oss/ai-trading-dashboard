"""Non-scoring composition of TIA's existing market and options context.

Components remain separate: unlike units and methodologies are never added into
a synthetic confidence score or silently promoted to an entry signal.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class UnifiedMarketRiskContext:
    asset: str
    asset_class: str
    flow_context: Any
    options_context: Any
    synthesis_status: str
    observations: tuple[str, ...]
    policy_effect: str = "NONE_CONTEXT_ONLY"


def compose_market_risk_context(flow_context, options_context) -> UnifiedMarketRiskContext:
    asset = getattr(flow_context, "asset", None) or getattr(options_context, "asset", "")
    asset_class = getattr(flow_context, "asset_class", None) or getattr(options_context, "asset_class", "")
    observations = []
    flow_direction = getattr(flow_context, "directional_read", None)
    option_metrics = getattr(options_context, "metrics", {}) or {}

    # Options positioning is deliberately not assigned a bullish/bearish vote.
    if flow_direction == "MIXED_FLOW":
        observations.append("Executed-flow and/or displayed-book components disagree; retain the mixed reading.")
    elif flow_direction == "INSUFFICIENT_DIRECTIONAL_EVIDENCE":
        observations.append("Order-flow evidence is insufficient; options context cannot fill that directional gap.")
    elif flow_direction in {"BUY_PRESSURE_CONSENSUS", "SELL_PRESSURE_CONSENSUS"}:
        observations.append(f"Order-flow components report {flow_direction}; this remains venue-specific context, not an entry signal.")

    if option_metrics:
        observations.append("Options positioning/volatility context is available but is not a directional confirmation.")
    else:
        observations.append("No usable options metrics are available; absence is not a neutral or zero reading.")

    f_status = getattr(flow_context, "execution_risk_status", "UNKNOWN")
    o_status = getattr(options_context, "status", "UNKNOWN")
    statuses = {str(f_status), str(o_status)}
    synthesis = "REVIEW_REQUIRED" if "REVIEW_REQUIRED" in statuses else (
        "CONTEXT_AVAILABLE" if option_metrics or f_status not in {"UNAVAILABLE", "UNKNOWN"} else "INSUFFICIENT_EVIDENCE"
    )
    return UnifiedMarketRiskContext(
        asset=str(asset), asset_class=str(asset_class),
        flow_context=flow_context, options_context=options_context,
        synthesis_status=synthesis, observations=tuple(observations),
    )
