"""Bonds list (Yahoo yields / ETFs / futures) and one instrument per coin for OKX lists (Meme coins). No network.
Run: python tests/test_bonds_meme.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules import asset_classes as ac
from modules import yahoo_feed as yf

b = yf.symbols("Bonds")
assert len(b) >= 15 and "Y:^TNX" in b and "Y:ZN=F" in b and "Y:HYG" in b, b
assert len(set(b)) == len(b) and "Y:TLT" not in b   # TLT is the Hyperliquid one, not listed twice
assert yf.is_yahoo(b[0]) and yf.universe("Bonds") == b

rows = [{"id": "DOGE-USDC", "vol": 9}, {"id": "DOGE-USDT", "vol": 8}, {"id": "PEPE-USDT", "vol": 7}, {"id": "DOGE-TRY", "vol": 6},
        {"id": "PEPE-TRY", "vol": 5}, {"id": "WIF-TRY", "vol": 4}, {"id": "BONK-USDT", "vol": 3}]
out = [r["id"] for r in ac.one_per_base(rows)]
assert out == ["DOGE-USDT", "PEPE-USDT", "WIF-TRY", "BONK-USDT"], out   # USDT pair wins, order = first appearance, a coin with no USDT pair keeps its pair
assert [r["id"] for r in ac.one_per_base([])] == []
assert [r["id"] for r in ac.one_per_base([{"id": "BTC-USDT-SWAP"}, {"id": "BTC-USD-SWAP"}])] == ["BTC-USDT-SWAP"]
print("bonds + meme tests ok")
