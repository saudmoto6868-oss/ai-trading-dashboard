"""TIA workspace gets the desk's general news (mock feed, no network).
Run: PYTHONPATH=. python3 tests/test_tia_news_context.py"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from modules import news_feed  # noqa: E402

ITEM = {"headline": "TIA_TEST_HEADLINE_123", "source": "Mock", "url": "https://example.invalid/a", "datetime": 1768000000, "summary": "x", "category": "general", "id": 1, "image": ""}
news_feed.get_latest_news = lambda category="general", limit=10: [ITEM]

from modules import tia_workspace as TW  # noqa: E402
rows = TW._tia_news.__wrapped__() if hasattr(TW._tia_news, "__wrapped__") else TW._tia_news()
assert rows and rows[0]["headline"] == "TIA_TEST_HEADLINE_123", rows
print("ok TIA news from the desk feed")

# a failing feed never breaks the TIA page: empty list
def boom(*a, **k):
    raise RuntimeError("feed down")
news_feed.get_latest_news = boom
rows = TW._tia_news.__wrapped__() if hasattr(TW._tia_news, "__wrapped__") else TW._tia_news()
assert rows == [], rows
print("ok feed failure -> empty list")

from modules.workspace import build_workspace_html  # noqa: E402
doc = build_workspace_html(symbols=["BTC-USDT"], news=[ITEM], lang="en", asset_cls="Crypto", ui_theme="gold", ui_mat="steel")
assert "TIA_TEST_HEADLINE_123" in doc, "news item must reach the workspace HTML"
print("ok news item reaches the workspace HTML")
print("ALL OK")
