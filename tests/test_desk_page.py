"""AI Desk page (modules/desk_page.py + modules/desk_brain). Plain script: python3 tests/test_desk_page.py
Mock-tested only: demo data, fake LLM; the real model and live sources are NOT exercised here."""
import asyncio
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DESK_DATA_MODE"] = "demo"
os.environ.setdefault("DESK_DATA_DIR", tempfile.mkdtemp(prefix="desk_brain_test_"))
for k in ("GEMINI_API_KEY", "LLM_BASE_URL", "LLM_MODEL"):
    os.environ.pop(k, None)

from modules import desk_page as P


def test_brain_imports_without_key():
    from modules.desk_brain.agent import llm
    from modules.desk_brain.agents.team import AGENTS, roster
    assert not llm.available()
    ids = {a["id"] for a in roster()}
    assert {"head", "auditor", "reviewer", "risk", "bull", "bear"} <= ids, ids
    assert len(AGENTS) >= 14
    print("ok test_brain_imports_without_key")


def test_watchlist_engine_demo():
    from modules.desk_brain.views import watchlist
    w = watchlist(None)
    assert w["rows"] and "demo" in w["source"]
    r = w["rows"][0]
    for k in ("symbol", "direction", "stars", "score", "promoted", "departments"):
        assert k in r, k
    print("ok test_watchlist_engine_demo")


def test_accounts_and_size():
    from modules.desk_brain import risk
    s = risk.state()
    assert len(s["accounts"]) == 3
    z = risk.size("EURUSD", 1.1000, 1.0980)
    assert z["stop_pips"] == 20.0 and len(z["accounts"]) == 3
    assert all(a["lots"] >= 0 for a in z["accounts"])
    print("ok test_accounts_and_size")


def test_ideas_table_and_feed():
    rows = P.ideas_table([{"symbol": "EURUSD", "status": "WATCH", "direction": -1, "entry": 1.1, "stop": 1.102, "t1": 1.096,
                           "rr": 2.0, "vetoes": ["news"], "notes": [], "demo": True}])
    assert rows[0]["Side"] == "SELL" and rows[0]["Gate vetoes"] == "news" and rows[0]["Demo data"] is True
    lines = P.feed_lines([{"type": "phase", "title": "1"}, {"type": "bus", "from": "head", "to": "team", "text": "x", "symbol": "XAUUSD"},
                          {"type": "agent_tool", "agent": "ict", "tool": "structure", "symbol": "XAUUSD"}, {"type": "agent_thought"}])
    assert len(lines) == 3 and "XAUUSD" in lines[1]
    print("ok test_ideas_table_and_feed")


def test_daily_cap_and_single_run():
    run = P.FloorRun()
    ok, _ = run.can_start(1)
    assert ok

    class FakeFloor:
        async def run(self, emit):
            await emit({"type": "phase", "title": "t"})
            await asyncio.sleep(0.05)
            return {"ideas": [], "seconds": 0.05, "usage": {"calls": 0}}

    assert run.start(FakeFloor)
    assert not run.start(FakeFloor)        # one run at a time
    run.thread.join(2)
    assert run.result and run.result["ideas"] == [] and run.events
    ok, why = run.can_start(1)
    assert not ok and why == "cap"         # daily cap reached
    print("ok test_daily_cap_and_single_run")


def test_gate_still_vetoes_with_fake_model():
    """Full floor with a scripted fake model: the fixed gate, not the model, decides (no unverified numbers pass)."""
    from modules.desk_brain.agents import runtime, team
    calls = {"n": 0}

    def fake_chat_tools(msgs, tools=None, model=None):
        calls["n"] += 1
        sysmsg = msgs[0]["content"]
        if "[agent:head]" in sysmsg and "ابدأ اليوم" in msgs[1]["content"]:
            return {"content": '{"summary":"s","candidates":[{"symbol":"EURUSD","direction":1,"why":"w"}]}', "tool_calls": []}
        if "[agent:head]" in sysmsg:
            return {"content": '{"symbol":"EURUSD","decision":"propose","direction":1,"entry":1.23456,"stop":1.2,"t1":1.3,'
                               '"order":"market","confidence":80,"thesis":"t","confirmations":{}}', "tool_calls": []}
        return {"content": '{"stance":"neutral","confidence":50,"summary":"ok","verdict":"pass"}', "tool_calls": []}

    orig = runtime.llm.chat_tools
    runtime.llm.chat_tools = fake_chat_tools
    try:
        events = []

        async def emit(ev):
            events.append(ev)
        res = asyncio.run(team.Floor().run(emit))
    finally:
        runtime.llm.chat_tools = orig
    idea = res["ideas"][0]
    assert idea["status"] == "WATCH", idea      # invented levels / few confirmations -> gate blocks READY
    assert idea["vetoes"] or idea["notes"]
    assert "journal_id" not in idea             # never journaled
    print("ok test_gate_still_vetoes_with_fake_model")


def test_journal_accounts_text():
    from modules.desk_brain.journal import _accounts_text
    assert _accounts_text({"acc2": 0.5, "acc1": 0, "acc3": None}) == "acc2"
    assert _accounts_text(None) == "" and _accounts_text(["acc1", "acc2"]) == "acc1,acc2"
    print("ok test_journal_accounts_text")


def test_page_renders_in_apptest():
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_string("from modules.desk_page import render\nrender()", default_timeout=120)
    at.run()
    assert not at.exception, at.exception
    assert any("GEMINI_API_KEY" in i.value for i in at.info)       # no key: says how to enable, button off
    assert at.button(key="dk_run").disabled
    at.segmented_control(key="dk_tab").set_value("Watchlist engine").run()
    assert not at.exception, at.exception
    assert at.dataframe and any("DEMO" in w.value for w in at.warning)
    at.segmented_control(key="dk_tab").set_value("Accounts & size").run()
    assert not at.exception, at.exception and at.dataframe
    print("ok test_page_renders_in_apptest")


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
    print("all desk_page tests passed")
