"""Static regression checks for the Order Flow REST cache policy.

Run with: python tests/test_orderflow_cache_policy.py
These checks validate source policy only; they do not simulate network timing or prove live-feed freshness.
"""
from pathlib import Path
import re

SOURCE = Path(__file__).resolve().parents[1] / "modules" / "workspace_app.html"
text = SOURCE.read_text(encoding="utf-8")

def require(pattern: str, message: str) -> None:
    if not re.search(pattern, text):
        raise AssertionError(message)

# Live book/trade REST paths must have a dedicated short TTL.
require(
    r"liveFlow\s*=\s*/\\/market\\/\(\?:books\(\?:-full\)\?\|trades\)\\\?/",
    "Live book/trade endpoint matcher is missing or changed.",
)
require(
    r"liveFlow\s*\?\s*1200\s*:\s*10000",
    "Live flow TTL should be 1200 ms while ordinary REST TTL stays 10000 ms.",
)
require(
    r"rub\s*\?\s*120000",
    "Rubik statistics cache TTL should remain 120000 ms.",
)

print("PASS: live Order Flow cache policy is present (static source check only).")
