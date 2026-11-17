"""The existing Academy exposes one canonical, bilingual decision sequence."""
from modules import academy


def test_decision_sequence_has_stable_order_and_roles():
    steps = academy.decision_sequence()
    assert [step["id"] for step in steps] == [
        "regime", "htf_bias", "structure", "location", "trigger", "order_flow", "session_risk"
    ]
    assert all(step["title"] and step["detail"] for step in steps)
    assert len({step["id"] for step in steps}) == len(steps)


def test_decision_sequence_has_english_overlay(monkeypatch):
    monkeypatch.setattr(academy, "_en", lambda: True)
    steps = academy.decision_sequence()
    assert steps[0]["title"] == "Market regime"
    assert steps[-1]["id"] == "session_risk"
    assert "risk" in steps[-1]["title"].lower()
