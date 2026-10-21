"""Model choice and prompt shape for the Grok digest (no network; plain script)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules.grok_digest import MAX_OUT, build_messages, pick_model

assert pick_model(["grok-4", "grok-3-mini", "grok-4-fast", "text-embed"]) == "grok-3-mini"
assert pick_model(["grok-4", "grok-2"]) == "grok-2"
assert pick_model(["other"]) == ""
msgs = build_messages("2026-10-21")
assert msgs[0]["role"] == "system" and "No buy or sell advice" in msgs[0]["content"]
assert "2026-10-21" in msgs[1]["content"] and "Trump" in msgs[1]["content"] and MAX_OUT <= 1000
print("test_grok_digest: all passed")
