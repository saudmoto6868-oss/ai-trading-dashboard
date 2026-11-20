"""Regression: the prop firm rule extractor must not default to a retired Claude model (mock, no network).
Run: PYTHONPATH=. python3 tests/test_prop_firms_model.py"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(ROOT, "modules", "prop_firms.py"), encoding="utf-8").read()
RETIRED = ["claude-3-5-haiku-20241022", "claude-3-haiku", "claude-2"]
for m in RETIRED:
    assert m not in src, f"retired model still referenced: {m}"
assert '"claude-haiku-4-5-20251001"' in src, "default should be the cheapest current Haiku"
print("ok prop firms default model is not retired")
print("ALL OK")
