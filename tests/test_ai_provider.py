"""modules/ai_provider.py + the ChatGPT path of the backtest agent and the guide: offline, the network is faked (no key, no cost)."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests  # noqa: E402

from modules import ai_provider as AP, strategy_agent as A  # noqa: E402


class _R:
    def __init__(self, code, body):
        self.status_code, self._b = code, body
        self.text = json.dumps(body) if not isinstance(body, str) else body

    def json(self):
        return self._b

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(str(self.status_code))


def _ok(obj):
    return _R(200, {"choices": [{"message": {"content": json.dumps(obj)}}]})


def _with_post(fn, run):
    old = requests.post
    requests.post = fn
    try:
        return run()
    finally:
        requests.post = old


def test_pick_order():
    keep = {k: os.environ.pop(k, None) for k in ("OPENAI_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY", "GEMINI_KEY", "AI_PROVIDER")}
    try:
        assert AP.pick() == ("", "")
        os.environ["GEMINI_API_KEY"] = "g"; assert AP.pick() == ("gemini", "g")
        os.environ["OPENAI_API_KEY"] = "o"; assert AP.pick() == ("openai", "o")           # ChatGPT wins when its key exists
        os.environ["AI_PROVIDER"] = "gemini"; assert AP.pick() == ("gemini", "g")        # unless Gemini is forced
    finally:
        for k, v in keep.items():
            os.environ.pop(k, None)
            if v is not None:
                os.environ[k] = v


def test_describe_lowercases_types():
    d = json.loads(AP.describe(A.SCHEMA))
    assert d["type"] == "object" and d["properties"]["reply"]["type"] == "string" and d["properties"]["rules"]["items"]["type"] == "object"


def test_chat_json_fallbacks_and_params():
    calls = []

    def post(url, headers=None, json=None, timeout=None):
        calls.append(dict(json))
        m = json["model"]
        if m == "gpt-gone":
            return _R(404, {"error": "model not found"})
        if "max_tokens" in json:
            return _R(400, "Unsupported parameter: max_tokens, use max_completion_tokens")
        return _ok({"reply": "hi"})
    out = _with_post(post, lambda: AP.chat_json("sys", [{"role": "user", "content": "x"}], "{}", key="k", model="gpt-gone"))
    assert out == {"reply": "hi"}
    assert calls[0]["model"] == "gpt-gone" and calls[-1]["model"] == "gpt-4o-mini" and "max_completion_tokens" in calls[-1] and "temperature" not in calls[-1]
    assert calls[-1]["messages"][0]["role"] == "system" and "ONE JSON object" in calls[-1]["messages"][0]["content"]
    try:
        _with_post(lambda *a, **k: _R(401, "bad key"), lambda: AP.chat_json("s", [], "{}", key="k"))
        raise SystemExit("a rejected key must raise")
    except requests.HTTPError:
        pass
    assert _with_post(lambda *a, **k: _R(200, {"choices": [{"message": {"content": "not json"}}]}), lambda: AP.chat_json("s", [], "{}", key="k")) == {}
    try:
        AP.chat_json("s", [], "{}", key="")
        raise SystemExit("no key must raise")
    except RuntimeError:
        pass


def test_agent_uses_chatgpt():
    ans = {"reply": "ok", "ready": True, "name": "rsi bounce", "side": "long", "logic": "AND", "assumptions": [], "questions": [],
           "rules": [{"indicator": "rsi", "period": 14, "op": "<", "compare": "number", "number": 30}]}
    seen = {}

    def post(url, headers=None, json=None, timeout=None):
        seen["url"], seen["auth"], seen["n"] = url, headers["Authorization"], len(json["messages"])
        return _ok(ans)
    out = _with_post(post, lambda: A.ask("buy when rsi < 30", [{"q": "a", "a": "b"}], "sk-test", provider="openai"))
    assert seen["url"].startswith("https://api.openai.com") and seen["auth"] == "Bearer sk-test" and seen["n"] == 4   # system + 1 history turn (2) + the new question
    assert out["errors"] == [] and out["strategy"]["rules"][0]["value"] == 30.0


if __name__ == "__main__":
    test_pick_order(); test_describe_lowercases_types(); test_chat_json_fallbacks_and_params(); test_agent_uses_chatgpt(); print("ok ai_provider")
