"""TIA stock fundamentals: only for the Stocks universe, and only alphabetic tickers (first 10). Mock, no network.
Run: PYTHONPATH=. python3 tests/test_tia_stock_gate.py"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from modules import context_feeds as CF  # noqa: E402
from modules import tia_workspace as TW  # noqa: E402

calls = []
CF.stock_fund = lambda tickers: calls.append(tuple(tickers)) or {"mock": True}

assert TW._stock(("AAPL-USD", "MSFT-USD", "BTC-USDT")) == {"mock": True}
assert calls[-1] == ("AAPL", "MSFT", "BTC"), calls[-1]
print("ok stock helper keeps alphabetic tickers")

n_before = len(calls)
assert TW._stock(("1INCH-USDT",)) is None and len(calls) == n_before, "no call for a numeric-led ticker"
print("ok numeric-led symbols are skipped")

src = open(os.path.join(ROOT, "modules", "tia_workspace.py"), encoding="utf-8").read()
assert 'if asset_class == "Stocks" else None' in src, "stock fundamentals must be gated on the Stocks universe"
print("ok gate on the Stocks universe is in place")
print("ALL OK")
