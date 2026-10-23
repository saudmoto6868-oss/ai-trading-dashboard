"""Mock-only checks for the optional OpenAI text provider. Run: python tests/test_openai_provider.py."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import requests
from modules import guide_ai

class FakeResponse:
    def __init__(self, payload, status_code=200):
        self.payload, self.status_code = payload, status_code
    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(response=self)
    def json(self):
        return self.payload

def main():
    original = (guide_ai._cfg, guide_ai.openai_key, guide_ai.gemini_key, guide_ai.api_key, requests.post)
    settings = {"GUIDE_PROVIDER":"openai", "OPENAI_MODEL":"gpt-4.1-mini"}
    calls = {}
    try:
        guide_ai._cfg = lambda name, default="": settings.get(name, default)
        guide_ai.openai_key = lambda: "mock-not-a-real-key"
        guide_ai.gemini_key = lambda: "mock-gemini-key"
        guide_ai.api_key = lambda: "mock-anthropic-key"
        assert guide_ai.provider() == "openai"
        settings["GUIDE_PROVIDER"] = "gemini"; assert guide_ai.provider() == "gemini"
        settings["GUIDE_PROVIDER"] = "claude"; assert guide_ai.provider() == "claude"
        settings["GUIDE_PROVIDER"] = "openai"
        expected = {"say":"Mock answer", "go":"chart", "page":"none"}
        def fake_post(url, headers, json, timeout):
            calls.update(url=url, headers=headers, body=json, timeout=timeout)
            return FakeResponse({"choices":[{"message":{"content":__import__("json").dumps(expected)}}]})
        requests.post = fake_post
        out = guide_ai._openai("Question", '{"sym":"XAUUSD"}', [{"q":"old","a":"prior"}], "gpt-4.1-mini")
        assert out == expected
        assert calls["url"] == "https://api.openai.com/v1/chat/completions"
        assert calls["headers"]["Authorization"] == "Bearer mock-not-a-real-key"
        assert calls["body"]["response_format"]["json_schema"]["strict"] is True
        assert calls["body"]["messages"][-2]["role"] == "assistant"
        def fake_refusal(url, headers, json, timeout):
            return FakeResponse({"choices":[{"message":{"refusal":"refused","content":None}}]})
        requests.post = fake_refusal
        out = guide_ai._openai("Question", "{}", [], "gpt-4.1-mini")
        assert out.get("err") == "refused"
        print("test_openai_provider: PASS (mock-only; no real API call)")
    finally:
        guide_ai._cfg, guide_ai.openai_key, guide_ai.gemini_key, guide_ai.api_key, requests.post = original

if __name__ == "__main__":
    main()
