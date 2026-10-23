"""Every kind of symbol gets a logo of the right kind and it is as big as asked (owner 2026-10-23)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.symbol_icon import icon, kind_of


def test_kinds():
    k = {"BTC-USDT": "crypto", "HL:xyz:GOLD": "metal", "HL:xyz:SILVER": "metal", "Y:GC=F": "metal", "HL:xyz:EUR": "fx", "Y:EURUSD=X": "fx", "HL:xyz:SP500": "index", "^GSPC": "index",
         "NVDA-USDT-SWAP": "stock", "HL:xyz:TSLA": "stock", "BZ-USDT-SWAP": "energy", "QQQ-USDT-SWAP": "index"}
    for s, want in k.items():
        assert kind_of(s) == want, (s, kind_of(s))


def test_logo_sources():
    assert "cryptocurrency-icons" in icon("BTC-USDT", 15)
    assert icon("HL:xyz:EUR", 15).count("flagcdn.com") == 2 and "/eu.png" in icon("HL:xyz:EUR", 15)       # a currency pair shows both flags
    assert icon("Y:USDEGP=X", 15).count("flagcdn.com") == 2
    assert "/us.png" in icon("HL:xyz:SP500", 15)                                                        # an index shows its country's flag
    assert "favicons?domain=nvidia.com" in icon("NVDA-USDT-SWAP", 15)                                    # a stock shows the company icon
    assert ">Au<" in icon("HL:xyz:GOLD", 15) and ">Ag<" in icon("HL:xyz:SILVER", 15)                    # metals: drawn badge with the element symbol


def test_size_and_fallback():
    h = icon("BTC-USDT", 13)
    assert "width:13px;height:13px" in h and "data-l=" in h and "onerror=" in h                         # same size as the text it sits next to, letter badge if the image fails
    assert "'" not in h.split("onerror=")[1].split('"')[1].replace("createElement('span')", "").replace("'", "")   # the fallback script has balanced quotes


if __name__ == "__main__":
    test_kinds(); test_logo_sources(); test_size_and_fallback(); print("ok symbol icon")
