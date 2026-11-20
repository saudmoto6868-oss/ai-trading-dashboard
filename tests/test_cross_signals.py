"""Where else + watch out (owner 2026-11-20): Radar <-> Spot board cross-check. Plain script: python3 tests/test_cross_signals.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules import cross_signals as X

assert X.base_of("BTC-USDT") == "BTC" and X.base_of("BTC-USDT-SWAP") == "BTC" and X.base_of("HL:xyz:GOLD") == "GOLD" and X.base_of("ETH") == "ETH"
assert X.market_of("BTC-USDT-SWAP") == "futures" and X.market_of("HL:xyz:GOLD") == "futures" and X.market_of("BTC-USDT") == "spot"

r = X.radar_index([("BTC-USDT-SWAP", "Double top", "sell", {"rsi": 75, "regime": "Down trend"}), ("ETH-USDT", "Double bottom", "buy", {"rsi": 72})], "4h")
s = X.spot_index([{"asset": "BTC", "name": "Discount", "side": "buy", "tf": "1d", "school": "SMC", "ev_label": "كان أسوأ من العادي"},
                  {"asset": "ETH", "name": "Breakout", "side": "buy", "tf": "1w", "school": "Classic", "ev_label": ""}])
n = X.notes("BTC", r, s, "en", here="radar")
assert "Radar 4h: sell (Double top)" in n["where"] and "Spot: buy 1d (Discount)" in n["where"], n
w = " | ".join(n["watch"])
assert "disagree" in w and "futures chart" in w and "worse than normal" in w and "Buy signal inside a down regime" in w, w
e = X.notes("ETH", r, s, "en", here="spot")
assert "agree" in " ".join(e["watch"]) and any("RSI 72" in x for x in e["watch"]), e
assert any("not scanned" in x for x in X.notes("ETH", r, None, "en", here="radar")["watch"])
assert any("not opened" in x for x in X.notes("ETH", None, s, "en", here="spot")["watch"])
assert "الرادار والسبوت مختلفين" in " ".join(X.notes("BTC", r, s, "ar")["watch"])
assert X.notes("SOL", r, s, "en") == {"where": "", "watch": []}
print("cross signals: OK")
