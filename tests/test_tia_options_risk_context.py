from datetime import date
from types import SimpleNamespace

import pandas as pd

from modules import tia_options_risk_context as ctx


def test_deribit_context_uses_existing_adapter_and_labels_forward_proxy(monkeypatch):
    monkeypatch.setattr("modules.options_desk.fetch", lambda currency: [{"x": 1}])
    monkeypatch.setattr("modules.options_desk.summarize", lambda rows, today=None: {
        "spot": 101.5, "totals": {"oi": 1000, "pc_oi": 0.8, "vol": 250},
        "expiries": [{"exp": date(2026, 11, 20), "days": 11, "iv": 55,
                      "skew10": 3, "pc_vol": 0.9, "max_pain": 100,
                      "walls": [(100, "C", 500)]}],
    })
    monkeypatch.setattr("modules.options_desk.dvol", lambda currency: [(date(2026, 1, 1), 50)] * 35)
    monkeypatch.setattr("modules.options_desk.iv_rank", lambda values: {
        "now": 50, "rank": 40, "percentile": 30, "days": len(values)})
    result = ctx.build_options_risk_context("BTC", "crypto")
    assert result.status == "AVAILABLE_WITH_LIMITATIONS"
    assert result.metrics["spot_proxy"] == 101.5
    assert result.metrics["nearest_expiry_max_pain"] == 100
    assert result.metrics["dvol_iv_rank"]["rank"] == 40
    assert any("forward proxy" in item for item in result.limitations)


def test_deribit_empty_and_failed_feeds_are_not_zero(monkeypatch):
    monkeypatch.setattr("modules.options_desk.fetch", lambda currency: [])
    monkeypatch.setattr("modules.options_desk.summarize", lambda rows, today=None: {
        "spot": 0, "totals": {}, "expiries": []})
    monkeypatch.setattr("modules.options_desk.dvol", lambda currency: [])
    result = ctx.build_options_risk_context("ETH", "crypto")
    assert result.metrics["spot_proxy"] == 0
    assert result.metrics["total_open_interest"] is None
    assert "option_book_empty" in result.unavailable
    assert "dvol_history_empty" in result.unavailable


def test_cboe_and_gex_context_uses_existing_modules(monkeypatch):
    chain = pd.DataFrame({"expiry": [pd.Timestamp("2026-12-18")],
                          "type": ["C"], "strike": [500.0], "oi": [10]})
    monkeypatch.setattr("modules.cboe_options.fetch", lambda symbol: (505.0, chain))
    monkeypatch.setattr("modules.cboe_options.summary", lambda frame, px: {
        "pc_vol": 0.7, "pc_oi": 0.8, "expiry": pd.Timestamp("2026-12-18"),
        "max_pain": 500.0, "px": px})
    monkeypatch.setattr("modules.gex.levels", lambda frame, px, today: {
        "call_wall": 510, "put_wall": 490, "gamma_flip": 502,
        "net_gex": 1000, "regime": "positive", "n_contracts": 1})
    result = ctx.build_options_risk_context("SPY", "equity", today=date(2026, 11, 9))
    assert result.status == "AVAILABLE_WITH_LIMITATIONS"
    assert result.metrics["estimated_gex"]["gamma_flip"] == 502
    assert any("dealer inventory" in item for item in result.limitations)


def test_unsupported_assets_do_not_fall_back_to_another_market():
    result = ctx.build_options_risk_context("XRP", "crypto")
    assert result.status == "UNSUPPORTED_ASSET"
    assert result.metrics == {}


def test_non_finite_values_are_rejected():
    assert ctx._finite(float("nan")) is None
    assert ctx._finite(float("inf")) is None
    assert ctx._finite(True) is None
