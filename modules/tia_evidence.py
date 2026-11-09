"""Evidence contracts for TIA metrics.

A metric is displayable only when provenance, time, unit, coverage and quality
are explicit. This module deliberately contains no market-data provider logic.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from math import isfinite
from typing import Optional


class EvidenceQuality(str, Enum):
    VERIFIED = "verified"
    PARTIAL = "partial"
    ESTIMATED = "estimated"
    STALE = "stale"
    MOCK = "mock"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class MetricEvidence:
    metric_id: str
    value: float
    unit: str
    source: str
    observed_at: str
    coverage: str
    quality: EvidenceQuality
    provider_symbol: Optional[str] = None
    notes: Optional[str] = None

    def validation_errors(self, *, now: Optional[datetime] = None,
                          max_age_seconds: Optional[int] = None) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.metric_id.strip():
            errors.append("metric_id is required")
        if not isfinite(self.value):
            errors.append("value must be finite")
        if not self.unit.strip():
            errors.append("unit is required")
        if not self.source.strip():
            errors.append("source is required")
        if not self.coverage.strip():
            errors.append("coverage is required")
        try:
            observed = datetime.fromisoformat(self.observed_at.replace("Z", "+00:00"))
            if observed.tzinfo is None:
                errors.append("observed_at must include a timezone")
            elif now is not None and max_age_seconds is not None:
                reference = now
                if reference.tzinfo is None:
                    errors.append("validation clock must include a timezone")
                elif (reference - observed).total_seconds() > max_age_seconds:
                    errors.append("evidence exceeds max_age_seconds")
        except (TypeError, ValueError):
            errors.append("observed_at must be an ISO-8601 timestamp")
        return tuple(errors)

    def is_displayable(self, *, now: Optional[datetime] = None,
                       max_age_seconds: Optional[int] = None) -> bool:
        if self.quality in {EvidenceQuality.MOCK, EvidenceQuality.STALE,
                            EvidenceQuality.UNAVAILABLE}:
            return False
        return not self.validation_errors(now=now, max_age_seconds=max_age_seconds)


def metric_status(evidence: Optional[MetricEvidence], *,
                  now: Optional[datetime] = None,
                  max_age_seconds: Optional[int] = None) -> str:
    """Return a safe UI status; never silently convert missing evidence to zero."""
    if evidence is None:
        return "unavailable"
    if not evidence.is_displayable(now=now, max_age_seconds=max_age_seconds):
        return "not_displayable"
    return evidence.quality.value
