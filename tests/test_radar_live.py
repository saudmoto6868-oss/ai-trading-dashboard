"""Live Radar card (modules/radar_live.py): symbol gate, timeframe mapping, the page is well formed and its script parses.
Plain script: python3 tests/test_radar_live.py"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules import radar_live as R

# only OKX spot instIds get a live card
assert R.is_okx_spot("BTC-USDT") and R.is_okx_spot("SUI-USDT")
assert not R.is_okx_spot("Y:EURUSD=X") and not R.is_okx_spot("HL:xyz:GOLD") and not R.is_okx_spot("BTC-USDT-SWAP")
assert R.live_card_html("HL:xyz:GOLD", "1h") is None
# Radar timeframes map to OKX bar names
assert R.OKX_BAR["1h"] == "1H" and R.OKX_BAR["1d"] == "1D" and R.OKX_BAR["4h"] == "4H" and R.OKX_BAR["1w"] == "1W"

doc = R.live_card_html("BTC-USDT", "4h", 300)
assert doc and doc.startswith("<!doctype html>")
assert "lightweight-charts@4.2.1" in doc and "wss://ws.okx.com:8443/ws/v5/public" in doc
assert "option value='4h' selected" in doc and "option value='1d'" in doc
assert "chart library not loaded" in doc            # the page degrades with a message when the library is offline
assert "<script" in doc and "</script>" in doc

# the page script must parse
node = shutil.which("node")
if node:
    scripts = re.findall(r"<script(?![^>]*src)[^>]*>(.*?)</script>", doc, re.S)
    tmp = tempfile.mkdtemp()
    path = os.path.join(tmp, "card.js")
    open(path, "w", encoding="utf-8").write("\n;\n".join(scripts))
    r = subprocess.run([node, "--check", path], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
print("radar live tests: OK")
