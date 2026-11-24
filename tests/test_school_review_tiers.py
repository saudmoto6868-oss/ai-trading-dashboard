"""School review tiers: free first (Gemini + OpenRouter free models), paid only when asked; the daily-calls topic reads our review files. No network."""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pathlib import Path
from modules import school_review as sr

assert sr.providers_for("calls_review", "free") == ["gemini", "openrouter"]
assert sr.providers_for("calls_review", "paid") == ["gemini", "openrouter", "deepseek"]
assert "deepseek" not in sr.providers_for("schools")                 # default tier is free
p = sr.calls_review_prompt()
assert "sceptical reviewer" in p and "n >= 100" in p and "No price predictions" in p

calls = []
fake = {"gemini": lambda q: calls.append(("gemini", q)) or "g-answer", "openrouter": lambda q: calls.append(("openrouter", q)) or "",
        "deepseek": lambda q: calls.append(("deepseek", q)) or "d-answer"}
old_providers, old_out = sr.PROVIDERS, sr.OUT
try:
    sr.PROVIDERS = fake
    sr.OUT = Path(tempfile.mkdtemp())
    done = sr.run(["calls_review"], log=lambda *a: None, tier="free")
    assert [c[0] for c in calls] == ["gemini", "openrouter"] and len(done) == 1        # openrouter gave no text: skipped, nothing saved
    assert (sr.OUT / "calls_review-gemini.md").read_text(encoding="utf-8").startswith("# calls_review - gemini")
    calls.clear()
    sr.run(["calls_review"], log=lambda *a: None, tier="paid")
    assert [c[0] for c in calls] == ["gemini", "openrouter", "deepseek"]
finally:
    sr.PROVIDERS, sr.OUT = old_providers, old_out
print("test_school_review_tiers: OK")
