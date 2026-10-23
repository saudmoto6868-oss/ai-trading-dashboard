"""Logo of a symbol, as an HTML <img> (owner 2026-10-23: every symbol shows its logo next to its name, as big as the text).
- crypto coins: the open cryptocurrency-icons set (jsDelivr);
- forex: the flag of the currency (flagcdn.com), two flags for a pair;
- indices: the flag of the country the index belongs to;
- stocks / ETFs: the company's own icon (Google's favicon service for its website), when the ticker is known;
- metals and energy: a small drawn badge (element symbol / oil): there is no official logo for a commodity.
Anything that fails to load falls back to a coloured letter badge. A flag is not an index provider's logo and a favicon is not always the brand mark."""
from __future__ import annotations

import html
import zlib

CDN = "https://cdn.jsdelivr.net/gh/spothq/cryptocurrency-icons@master/32/color/{}.png"
FLAG = "https://flagcdn.com/w80/{}.png"
FAV = "https://www.google.com/s2/favicons?domain={}&sz=64"

CUR_CC = {"USD": "us", "EUR": "eu", "GBP": "gb", "JPY": "jp", "CHF": "ch", "CAD": "ca", "AUD": "au", "NZD": "nz", "CNH": "cn", "CNY": "cn", "KRW": "kr", "MXN": "mx",
          "TRY": "tr", "INR": "in", "BRL": "br", "SAR": "sa", "EGP": "eg", "ZAR": "za", "SEK": "se", "NOK": "no", "DKK": "dk", "HKD": "hk", "SGD": "sg", "PLN": "pl",
          "AED": "ae", "RUB": "ru", "THB": "th", "ILS": "il", "KWD": "kw", "QAR": "qa"}
_FX_BASES = set(CUR_CC)
_METAL = {"XAU": ("Au", "#f0b90b"), "GOLD": ("Au", "#f0b90b"), "XAG": ("Ag", "#aab2bd"), "SILVER": ("Ag", "#aab2bd"), "XPT": ("Pt", "#8fa3b5"), "PLATINUM": ("Pt", "#8fa3b5"),
          "XPD": ("Pd", "#9aa7b3"), "GC": ("Au", "#f0b90b"), "SI": ("Ag", "#aab2bd"), "HG": ("Cu", "#b87333"), "PL": ("Pt", "#8fa3b5"), "PA": ("Pd", "#9aa7b3"), "PALLADIUM": ("Pd", "#9aa7b3"), "COPPER": ("Cu", "#b87333"), "XCU": ("Cu", "#b87333"), "ALUMINIUM": ("Al", "#9aa0a6")}
_ENERGY = {"CL", "WTI", "BRENT", "BZ", "OIL", "NG", "NATGAS", "USOIL", "UKOIL", "XTI", "XBR", "GAS"}
_INDEX_CC = {"SPX": "us", "SP500": "us", "US500": "us", "GSPC": "us", "NDX": "us", "XYZ100": "us", "US100": "us", "IXIC": "us", "DJI": "us", "US30": "us", "RUT": "us", "VIX": "us",
             "SPY": "us", "QQQ": "us", "IWM": "us", "DIA": "us", "DAX": "de", "GER40": "de", "GDAXI": "de", "FTSE": "gb", "UK100": "gb", "HSI": "hk", "N225": "jp", "JP225": "jp",
             "DX": "us", "KR200": "kr", "CAC40": "fr", "FCHI": "fr", "CASE30": "eg", "TASI": "sa"}
# ticker -> website (for the company icon); only well known listings, everything else gets the letter badge
_STOCK_DOMAIN = {"AAPL": "apple.com", "MSFT": "microsoft.com", "NVDA": "nvidia.com", "TSLA": "tesla.com", "AMZN": "amazon.com", "GOOGL": "google.com", "GOOG": "google.com",
                 "META": "meta.com", "AMD": "amd.com", "INTC": "intel.com", "MU": "micron.com", "MRVL": "marvell.com", "NET": "cloudflare.com", "CRWD": "crowdstrike.com",
                 "MSTR": "strategy.com", "COIN": "coinbase.com", "MRNA": "modernatx.com", "CRCL": "circle.com", "NBIS": "nebius.com", "CRWV": "coreweave.com", "BE": "bloomenergy.com",
                 "SNDK": "sandisk.com", "WDC": "westerndigital.com", "AAOI": "ao-inc.com", "LITE": "lumentum.com", "SMSN": "samsung.com", "SAMSUNG": "samsung.com",
                 "SKHX": "skhynix.com", "SKHY": "skhynix.com", "SKHYNIX": "skhynix.com", "UNITREE": "unitree.com", "CXMT": "cxmt.com", "ZHIPU": "zhipuai.cn", "NFLX": "netflix.com",
                 "PLTR": "palantir.com", "HOOD": "robinhood.com", "ORCL": "oracle.com", "AVGO": "broadcom.com", "TSM": "tsmc.com", "BABA": "alibaba.com", "UBER": "uber.com",
                 "DRAM": "roundhillinvestments.com", "SOXL": "direxion.com", "SOXS": "direxion.com", "TLT": "ishares.com", "SPCX": "spacex.com", "EWY": "ishares.com",
                 "KORU": "direxion.com"}
_STOCK_BASES = set(_STOCK_DOMAIN) | {"SNXX", "ZHONGJI", "SKDD"}


def base_of(sym: str) -> str:
    s = sym.split(":")[-1] if ":" in sym else sym
    s = s.replace("=X", "").replace("=F", "").replace("^", "")
    return s.split("-")[0].upper()


def kind_of(sym: str) -> str:
    b = base_of(sym)
    if sym.startswith("Y:") and sym.endswith("=X") or (len(b) == 6 and b[:3] in _FX_BASES and b[3:] in _FX_BASES and sym.startswith("Y:")):
        return "fx"
    if b in _METAL:
        return "metal"
    if b in _ENERGY:
        return "energy"
    if b in _INDEX_CC:
        return "index"
    if b in _STOCK_BASES:
        return "stock"
    if sym.startswith(("HL:", "Y:")):
        return "fx" if b in _FX_BASES else "stock"
    return "crypto"


def _letter(b: str, size: int) -> tuple[str, str]:
    col = "#%06x" % (zlib.crc32(b.encode()) & 0xFFFFFF | 0x404040)
    return (b[:1], f"display:inline-block;width:{size}px;height:{size}px;border-radius:50%;background:{col};color:#fff;font:700 {max(8, size - 7)}px/{size}px sans-serif;"
                   f"text-align:center;vertical-align:middle;margin-inline-end:5px")


def _img(url: str, b: str, size: int, extra: str = "") -> str:
    ch, fst = _letter(b, size)
    st = f"width:{size}px;height:{size}px;border-radius:50%;object-fit:cover;vertical-align:middle;margin-inline-end:5px;{extra}"
    return (f"<img src='{html.escape(url, quote=True)}' style='{st}' alt='' loading='lazy' data-l='{html.escape(ch, quote=True)}' data-st='{html.escape(fst, quote=True)}' "
            "onerror=\"var s=document.createElement('span');s.textContent=this.dataset.l;s.style.cssText=this.dataset.st;this.replaceWith(s)\"/>")


def _badge(text: str, color: str, size: int) -> str:
    fs = max(8, int(size * (0.5 if len(text) > 1 else 0.62)))
    return (f"<span style='display:inline-block;width:{size}px;height:{size}px;border-radius:50%;background:{color};color:#111;font:800 {fs}px/{size}px sans-serif;"
            f"text-align:center;vertical-align:middle;margin-inline-end:5px'>{html.escape(text)}</span>")


def _pair(b: str, sym: str = "") -> tuple[str, str] | None:
    if len(b) == 6 and b[:3] in _FX_BASES and b[3:] in _FX_BASES:
        return (b[:3], b[3:])
    if sym.startswith("HL:") and b in _FX_BASES and b != "USD":   # Hyperliquid names the pair by its non-dollar currency
        return (b, "USD") if b in ("EUR", "GBP", "AUD", "NZD") else ("USD", b)
    return None


def icon(sym: str, size: int = 16) -> str:
    """HTML for the logo of `sym`, `size` px square (use the text's font size so it reads as part of the name)."""
    b = base_of(sym)
    k = kind_of(sym)
    if k == "crypto":
        return _img(CDN.format(b.lower()), b, size)
    if k == "fx":
        pr = _pair(b, sym)
        if pr:   # two overlapping flags: base in front-left, quote behind-right
            a, q = CUR_CC.get(pr[0]), CUR_CC.get(pr[1])
            if a and q:
                w = int(size * 1.5)
                return (f"<span style='display:inline-block;width:{w}px;height:{size}px;position:relative;vertical-align:middle;margin-inline-end:5px'>"
                        + _img(FLAG.format(q), pr[1], size, extra="position:absolute;right:0;top:0;margin:0;")
                        + _img(FLAG.format(a), pr[0], size, extra="position:absolute;left:0;top:0;margin:0;box-shadow:0 0 0 1.5px #0b0e11;") + "</span>")
        cc = CUR_CC.get(b)
        return _img(FLAG.format(cc), b, size) if cc else _badge(b[:1], "#4aa3ff", size)
    if k == "index":
        cc = _INDEX_CC.get(b)
        return _img(FLAG.format(cc), b, size) if cc else _badge(b[:1], "#4aa3ff", size)
    if k == "metal":
        t, c = _METAL.get(b, (b[:2].title(), "#aab2bd"))
        return _badge(t, c, size)
    if k == "energy":
        return _badge("◆", "#f0b90b", size).replace("color:#111", "color:#161a1e")
    dom = _STOCK_DOMAIN.get(b)
    return _img(FAV.format(dom), b, size) if dom else _badge(b[:1], "#4aa3ff", size)
