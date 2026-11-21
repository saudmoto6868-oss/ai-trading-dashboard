"""TIA holdings from the spot ledger (read-only). Fake store, no network.
Run: PYTHONPATH=. python3 tests/test_tia_holdings.py"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from modules import spot_core as C, spot_store, tia_intelligence as T  # noqa: E402


class FakeStore:
    def __init__(self, txs):
        self.txs = txs

    def load(self):
        return {"txs": self.txs}


def use(txs):
    spot_store.get_store = lambda: FakeStore(txs)
    T._HOLD_CACHE.update(t=0.0, txs=[])


# 1. no ledger rows -> not held, no error
use([])
h = T._holdings("BTC-USDT")
assert h == {"held": False, "asset": "BTC"}, h
print("ok not held")

# 2. one buy in the ledger -> held with qty and average cost
buy = C.new_tx(asset="BTC", side="buy", qty=0.5, unit="oz", price=60000, currency="USD", fx=50, date="2026-11-01")
use([buy])
h = T._holdings("BTC-USDT")
assert h["held"] is True and h["asset"] == "BTC" and abs(float(h["qty"]) - 0.5) < 1e-9, h
print("ok held:", h["qty"], "BTC avg", h["avg_usd"])

# 3. another asset does not leak into BTC
use([C.new_tx(asset="ETH", side="buy", qty=2, unit="oz", price=3000, currency="USD", fx=50, date="2026-11-01")])
assert T._holdings("BTC-USDT")["held"] is False
print("ok other assets ignored")

# 4. the 5-minute cache: a second call does not reread the store
calls = {"n": 0}
class Counting(FakeStore):
    def load(self):
        calls["n"] += 1
        return {"txs": self.txs}
spot_store.get_store = lambda: Counting([buy])
T._HOLD_CACHE.update(t=0.0, txs=[])
T._holdings("BTC-USDT"); T._holdings("BTC-USDT")
assert calls["n"] == 1, calls
print("ok cached read")
print("ALL OK")
