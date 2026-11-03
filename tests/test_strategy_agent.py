"""Offline checks for modules/strategy_agent.py (no network: the model answer is given by hand)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules import strategy_agent as A  # noqa: E402


def test_number_and_indicator_rules():
    ans = {"reply": "ok", "ready": True, "name": "RSI bounce / trend", "side": "long", "logic": "AND", "assumptions": [], "questions": [],
           "rules": [{"indicator": "rsi", "period": 14, "op": "<", "compare": "number", "number": 30},
                     {"indicator": "close", "op": ">", "compare": "ema", "compare_period": 200}]}
    out = A.finish(ans)
    s = out["strategy"]
    assert out["errors"] == [], out["errors"]
    assert s["rules"][0] == {"indicator": "rsi", "op": "<", "period": 14, "value": 30.0}
    assert s["rules"][1] == {"indicator": "close", "op": ">", "value": {"indicator": "ema", "period": 200}}
    assert s["name"] == "RSI bounce  trend"


def test_contradiction_and_empty_are_reported():
    bad = A.finish({"name": "x", "side": "long", "logic": "AND", "rules": [
        {"indicator": "rsi", "period": 14, "op": ">", "compare": "number", "number": 70},
        {"indicator": "rsi", "period": 14, "op": "<", "compare": "number", "number": 30}]})
    assert bad["errors"]
    assert A.finish({"name": "x", "rules": []})["errors"] == ["no testable rule yet"]


def test_daily_cap_and_text_limit():
    os.environ["AGENT_DAILY_CAP"] = "2"
    A._DAY.update(day="", n=0)
    assert A._spend_ok() and A._spend_ok() and not A._spend_ok()          # the third call of the day is refused
    A._DAY.update(day="2000-01-01", n=99)                                  # a new day resets the counter
    assert A._spend_ok() and A._DAY["n"] == 1
    os.environ["AGENT_DAILY_CAP"] = "oops"                                 # a bad value falls back to the default, never crashes
    A._DAY.update(day="", n=0)
    assert A._spend_ok()
    os.environ["AGENT_DAILY_CAP"] = "0"; A._DAY.update(day="", n=0)
    try:
        A.ask("x" * 10, [], "key")
        raise AssertionError("ask must refuse when the cap is 0")
    except RuntimeError as e:
        assert "AGENT_DAILY_CAP" in str(e)
    os.environ.pop("AGENT_DAILY_CAP"); assert A.MAX_TEXT == 4000


if __name__ == "__main__":
    test_number_and_indicator_rules(); test_contradiction_and_empty_are_reported(); test_daily_cap_and_text_limit(); print("ok strategy_agent")
