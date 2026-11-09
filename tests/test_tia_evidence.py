from datetime import datetime, timezone

from modules.tia_evidence import EvidenceQuality, MetricEvidence, metric_status


def sample(**overrides):
    fields = dict(
        metric_id="xauusd.last",
        value=2345.6,
        unit="USD/oz",
        source="provider:test",
        observed_at="2026-11-09T04:00:00+00:00",
        coverage="spot quote; top of book",
        quality=EvidenceQuality.VERIFIED,
    )
    fields.update(overrides)
    return MetricEvidence(**fields)


def test_verified_metric_with_provenance_is_displayable():
    assert sample().is_displayable()


def test_mock_values_are_never_displayable():
    assert not sample(quality=EvidenceQuality.MOCK).is_displayable()


def test_missing_source_unit_or_coverage_is_rejected():
    item = sample(source="", unit="", coverage="")
    assert not item.is_displayable()
    assert len(item.validation_errors()) == 3


def test_timestamp_requires_timezone():
    item = sample(observed_at="2026-11-09T04:00:00")
    assert "observed_at must include a timezone" in item.validation_errors()


def test_old_evidence_is_rejected_when_age_limit_is_set():
    item = sample()
    now = datetime(2026, 11, 9, 5, 0, tzinfo=timezone.utc)
    assert not item.is_displayable(now=now, max_age_seconds=60)


def test_non_finite_values_are_rejected():
    assert not sample(value=float("nan")).is_displayable()


def test_missing_metric_never_becomes_zero():
    assert metric_status(None) == "unavailable"
