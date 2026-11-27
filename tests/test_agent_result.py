"""Shared agent result (modules/agent_result.py): builder, validator, summary. No network."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules import agent_result as A

ok = A.make("level_scanner", "grok", "HL:xyz:GOLD", "bullish", [{"what": "swept PDL and closed back", "value": 12, "unit": "pts"}], source="Hyperliquid", quality="live", n=40, coverage="1H x 3")
assert A.validate(ok) == [] and ok["evidence_ok"] is True
small = A.make("skeptic", "claude", "BTC-USDT", "info", source="lab", quality="delayed", n=7)
assert A.validate(small) == [] and small["evidence_ok"] is False          # n < 30 is flagged, not hidden
assert "missing symbol" in A.validate({**ok, "symbol": ""})
assert any("unknown verdict" in p for p in A.validate({**ok, "verdict": "buy"}))
assert any("unknown stream" in p for p in A.validate({**ok, "stream": "gemini"}))
assert any("needs evidence" in p for p in A.validate(A.make("x", "tia", "S", "bearish", [], "OKX", "live")))
assert any("non-live source" in p for p in A.validate({**ok, "source": "mock"}))
assert any("evidence_ok" in p for p in A.validate({**ok, "n": 5}))          # claims evidence with n=5
assert any("secret" in p for p in A.validate({**ok, "api_key": "x"}))
assert any("probabilities" in p for p in A.validate({**ok, "win_rate": 0.7}))
assert A.validate("nope") == ["not an object"]
s = A.summarize([ok, small, {"agent": "bad"}])
assert s["by_agent"] == {"level_scanner": {"bullish": 1}, "skeptic": {"info": 1}} and len(s["invalid"]) == 1, s
print("ok agent_result")
