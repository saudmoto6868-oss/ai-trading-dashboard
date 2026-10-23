"""Static regression checks for the Order Flow REST cache policy.

Run with: python tests/test_orderflow_cache_policy.py
These checks validate source policy only; they do not simulate network timing or prove live-feed freshness.
"""
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "modules" / "workspace_app.html"
source = SOURCE.read_text(encoding="utf-8")

checks = {
    "dedicated live-flow endpoint matcher": "const liveFlow =" ,
    "book and trade endpoint coverage": "(?:books(?:-full)?|trades)",
    "short live-flow TTL and unchanged ordinary TTL": "ttl = rub ? 120000 : liveFlow ? 1200 : 10000",
    "request cache lookup preserved": "hit = OKX_CACHE[path]",
    "Rubik cache TTL preserved": "rub ? 120000",
}
for label, expected in checks.items():
    if expected not in source:
        raise AssertionError(f"Missing expected source fragment: {label}")

print("PASS: Order Flow cache policy source checks (static only; no network simulation).")
