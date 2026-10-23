"""Small icon for a symbol, as an HTML <img> with a coloured-letter fallback (owner 2026-10-23: every symbol shows its icon next to its name).
Crypto coins use the open cryptocurrency-icons set from jsDelivr; forex / metals / stocks / indices use an emoji badge by class (no logo data is claimed)."""
from __future__ import annotations

import html
import zlib

CDN = "https://cdn.jsdelivr.net/gh/spothq/cryptocurrency-icons@master/32/color/{}.png"
_METAL = {"XAU": "🥇", "GOLD": "🥇", "XAG": "🥈", "SILVER": "🥈", "XPT": "⚪", "PLATINUM": "⚪", "XPD": "⚪", "COPPER": "🟠", "PALLADIUM": "⚪"}
_ENERGY = {"CL", "WTI", "BRENT", "OIL", "NG", "NATGAS", "USOIL", "UKOIL", "XTI", "XBR"}
_INDEX = {"SPX", "SP500", "US500", "NDX", "XYZ100", "US100", "DJI", "US30", "DAX", "GER40", "FTSE", "UK100", "HSI", "N225", "JP225", "KR200", "VIX", "SPY", "QQQ", "IWM", "DIA"}


def base_of(sym: str) -> str:
    s = sym.split(":")[-1] if ":" in sym else sym
    s = s.replace("=X", "").replace("^", "")
    return s.split("-")[0].upper()


def kind_of(sym: str) -> str:
    b = base_of(sym)
    if sym.startswith("Y:") and sym.endswith("=X") or (len(b) == 6 and b.endswith(("USD", "JPY", "EUR", "GBP", "CHF")) and sym.startswith("Y:")):
        return "fx"
    if b in _METAL:
        return "metal"
    if b in _ENERGY:
        return "energy"
    if b in _INDEX:
        return "index"
    if sym.startswith(("HL:", "Y:")):
        return "fx" if b in {"JPY", "EUR", "GBP", "CHF", "CAD", "AUD", "NZD", "CNH", "KRW", "MXN", "TRY", "INR", "BRL"} else "stock"
    return "crypto"


def icon(sym: str, size: int = 16) -> str:
    b = base_of(sym)
    k = kind_of(sym)
    st = f"width:{size}px;height:{size}px;border-radius:50%;vertical-align:-3px;margin-right:4px"
    if k == "crypto":
        col = "#%06x" % (zlib.crc32(b.encode()) & 0xFFFFFF | 0x404040)
        fb = f"<span style=\'{st};display:inline-block;background:{col};color:#fff;font:700 {size - 6}px/{size}px sans-serif;text-align:center\'>{html.escape(b[:1])}</span>"
        return (f"<img src='{CDN.format(b.lower())}' style='{st}' alt='' loading='lazy' "
                f"onerror=\"this.outerHTML='{fb}'\"/>")
    em = {"fx": "💱", "metal": _METAL.get(b, "🪙"), "energy": "🛢️", "index": "📊", "stock": "🏢"}[k]
    return f"<span style='display:inline-block;width:{size + 2}px;text-align:center;margin-right:3px;font-size:{size - 2}px'>{em}</span>"
