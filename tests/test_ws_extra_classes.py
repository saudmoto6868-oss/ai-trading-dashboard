"""The Workspace scan adds a few liquid markets of the other classes (Hyperliquid) so the class filter has setups to show (plain script)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules.asset_classes import WS_EXTRA, CLASSES
d = dict(WS_EXTRA)
assert all(c in CLASSES for c in d), d
assert {"Metals", "Indices", "Forex", "Oil & Gas", "Stocks", "Bonds"} <= set(d), d              # every class except Crypto (chosen), Options (no candles), EGX / Tadawul (no feed)
assert "Options" not in d and "Crypto" not in d
assert sum(d.values()) <= 16, "keep the extra scan small (rate limits)"
src = open(os.path.join(os.path.dirname(__file__), "..", "main.py"), encoding="utf-8").read()
assert "for cls, n in WS_EXTRA:" in src and "from modules.asset_classes import WS_EXTRA" in src
print("PASS: ws extra classes", d)
