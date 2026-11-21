"""Candles for markets OKX does not list (forex majors, Nasdaq / US indices, EGX, Tadawul) from Yahoo Finance's
public chart endpoint. UNOFFICIAL and keyless: it can change or throttle without notice, and EGX / Tadawul quotes may be
delayed ~15 min. Symbols are written "Y:<yahoo symbol>" so the rest of the code can tell them from OKX instrument ids.
Frames match the OKX ones: columns time (naive UTC), open, high, low, close, volume."""
from __future__ import annotations

import os
import re
import time
from pathlib import Path

import pandas as pd
import requests

from modules.data_fetcher import aggregate_frame

PREFIX = "Y:"
URL = "https://{host}/v8/finance/chart/{sym}"
HDR = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36", "Accept": "application/json"}
HOSTS = ["query1.finance.yahoo.com", "query2.finance.yahoo.com"]
# our tf -> (yahoo interval, range, bars to merge)
TF = {"1m": ("1m", "7d", 1), "5m": ("5m", "60d", 1), "15m": ("15m", "60d", 1), "30m": ("30m", "60d", 1),
      "1h": ("60m", "730d", 1), "4h": ("60m", "730d", 4), "1d": ("1d", "5y", 1), "1w": ("1wk", "10y", 1),
      "1mo": ("1mo", "max", 1)}   # monthly (Spot desk, 2026-11-06): full history for gold / silver / copper futures

FOREX = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", "USDCHF=X", "NZDUSD=X", "EURGBP=X", "EURJPY=X", "GBPJPY=X", "USDEGP=X", "USDSAR=X", "GC=F", "SI=F", "DX-Y.NYB"]
INDICES = ["^IXIC", "^NDX", "^GSPC", "^DJI", "^RUT", "^VIX", "^GDAXI", "^FTSE", "^N225", "^HSI"]
EGX = [
    "^CASE30", "EKHO.CA", "COMI.CA", "SWDY.CA", "ETEL.CA", "TMGH.CA", "EGAL.CA", "QNBE.CA", "HDBK.CA", "MFPC.CA",
    "EAST.CA", "ABUK.CA", "ALCN.CA", "ORAS.CA", "EFIH.CA", "BQDC.CA", "EMFD.CA", "ADIB.CA", "FWRY.CA", "CANA.CA",
    "EFID.CA", "GPPL.CA", "SCTS.CA", "VLMRA.CA", "VLMR.CA", "ORHD.CA", "HRHO.CA", "JUFO.CA", "HALN.CA", "PHDC.CA",
    "BIOC.CA", "FAIT.CA", "FAITA.CA", "OCDI.CA", "CIEB.CA", "HELI.CA", "EXPA.CA", "FERC.CA", "RAYA.CA", "SCEM.CA",
    "ARCC.CA", "GBCO.CA", "CCAP.CA", "BTFH.CA", "IRON.CA", "CIRA.CA", "CLHO.CA", "EGCH.CA", "VALU.CA", "TAQA.CA",
    "MBSC.CA", "EGSA.CA", "PHAR.CA", "MOIL.CA", "MCQE.CA", "SAUD.CA", "AMOC.CA", "ORWE.CA", "SKPC.CA", "UBEE.CA",
    "EFIC.CA", "NIPH.CA", "MTIE.CA", "TALM.CA", "EGBE.CA", "MASR.CA", "POUL.CA", "EGTS.CA", "ATQA.CA", "MHOT.CA",
    "BINV.CA", "CSAG.CA", "RMDA.CA", "ISPH.CA", "CICH.CA", "NAPR.CA", "AMES.CA", "MIPH.CA", "AMIA.CA", "MPRC.CA",
    "CPCI.CA", "MOIN.CA", "OIH.CA", "OLFI.CA", "IFAP.CA", "MPCI.CA", "BONY.CA", "PHTV.CA", "SUGR.CA", "AXPH.CA",
    "EGAS.CA", "DOMT.CA", "PRDC.CA", "ISMQ.CA", "ZMID.CA", "SPHT.CA", "ARAB.CA", "GOUR.CA", "ENGC.CA", "AJWA.CA",
    "ELEC.CA", "SPIN.CA", "ACAP.CA", "MICH.CA", "OCPH.CA", "GSSC.CA", "CNFN.CA", "MCRO.CA", "AFMC.CA", "NINH.CA",
    "SAIB.CA", "KORA.CA", "SDTI.CA", "SVCE.CA", "KABO.CA", "DSCW.CA", "WCDF.CA", "ACGC.CA", "AMER.CA", "UEFM.CA",
    "UNIT.CA", "OFH.CA", "MFSC.CA", "KZPC.CA", "INFI.CA", "LCSW.CA", "ADCI.CA", "ALRA.CA", "ICFC.CA", "GDWA.CA",
    "ELKA.CA", "CFGH.CA", "NAHO.CA", "GPIM.CA", "ZEOT.CA", "ETRS.CA", "ELSH.CA", "ACTF.CA", "ACAMD.CA", "CRST.CA",
    "EDFM.CA", "ATLC.CA", "ASCM.CA", "SMFR.CA", "DAPH.CA", "MPCO.CA", "GTWL.CA", "SNFC.CA", "ISMA.CA", "PHGC.CA",
    "CEFM.CA", "MOSC.CA", "MENA.CA", "ICID.CA", "NARE.CA", "EALR.CA", "IDRE.CA", "RACC.CA", "AALR.CA", "ECAP.CA",
    "MILS.CA", "WKOL.CA", "DEIN.CA", "ADPC.CA", "NCCW.CA", "EHDR.CA", "GGRN.CA", "SCFM.CA", "KRDI.CA", "MAAL.CA",
    "DTPP.CA", "SIPC.CA", "AIHC.CA", "NDRL.CA", "ASPI.CA", "ODIN.CA", "GGCC.CA", "CAED.CA", "SEIG.CA", "SEIGA.CA",
    "CERA.CA", "UEGC.CA", "MBEG.CA", "GTEX.CA", "POCO.CA", "IEEC.CA", "NHPS.CA", "PRCL.CA", "OBRI.CA", "LUTS.CA",
    "COSG.CA", "MEPA.CA", "ALUM.CA", "RUBX.CA", "TANM.CA", "PRMH.CA", "EBSC.CA", "ICLE.CA", "MEGM.CA", "AIDC.CA",
    "AFDI.CA", "RTVC.CA", "TWSA.CA", "UNIP.CA", "APSW.CA", "TYCN.CA", "RAKT.CA", "AMII.CA", "RREI.CA", "EASB.CA",
    "KWIN.CA", "ROTO.CA", "SPMD.CA", "EEII.CA", "FCMD.CA", "MOED.CA", "CCRS.CA", "AREH.CA", "EPCO.CA", "GRCA.CA",
    "ELNA.CA", "TRTO.CA", "GIHD.CA", "MMAT.CA", "ELWA.CA", "DGTZ.CA", "DCCC.CA", "NEDA.CA", "EPPK.CA", "GMCI.CA",
    "EOSB.CA", "CPME.CA", "COPR.CA",
]
TADAWUL = [
    "^TASI.SR", "2222.SR", "1120.SR", "1180.SR", "1211.SR", "7010.SR", "2010.SR", "2082.SR", "1010.SR", "4013.SR",
    "1060.SR", "1150.SR", "5110.SR", "2020.SR", "4280.SR", "1050.SR", "7203.SR", "7020.SR", "2280.SR", "1080.SR",
    "4030.SR", "2380.SR", "1140.SR", "4325.SR", "6015.SR", "4190.SR", "7202.SR", "4300.SR", "8210.SR", "8010.SR",
    "4250.SR", "2382.SR", "2290.SR", "1030.SR", "2223.SR", "4142.SR", "1020.SR", "4263.SR", "1111.SR", "4100.SR",
    "4164.SR", "1303.SR", "2083.SR", "4002.SR", "4200.SR", "8313.SR", "1212.SR", "8230.SR", "2381.SR", "2310.SR",
    "2250.SR", "4090.SR", "4015.SR", "7030.SR", "7200.SR", "2350.SR", "2050.SR", "4264.SR", "4017.SR", "4004.SR",
    "4321.SR", "4310.SR", "4220.SR", "2330.SR", "2270.SR", "1322.SR", "4020.SR", "4072.SR", "2230.SR", "4005.SR",
    "4084.SR", "4161.SR", "4003.SR", "1810.SR", "1321.SR", "4018.SR", "3040.SR", "8200.SR", "2060.SR", "4291.SR",
    "2080.SR", "6004.SR", "1830.SR", "3020.SR", "4031.SR", "4210.SR", "3030.SR", "4150.SR", "4322.SR", "4007.SR",
    "4001.SR", "6010.SR", "2283.SR", "2320.SR", "4163.SR", "4165.SR", "4019.SR", "2070.SR", "4162.SR", "2190.SR",
    "4260.SR", "2081.SR", "7040.SR", "4071.SR", "4050.SR", "4327.SR", "4009.SR", "4016.SR", "1320.SR", "3050.SR",
    "3092.SR", "2284.SR", "6019.SR", "4146.SR", "4340.SR", "2286.SR", "2285.SR", "3080.SR", "2040.SR", "3060.SR",
    "4192.SR", "7211.SR", "1831.SR", "9557.SR", "6017.SR", "1834.SR", "6022.SR", "8030.SR", "3010.SR", "2300.SR",
    "1833.SR", "2170.SR", "1304.SR", "9540.SR", "4083.SR", "7204.SR", "4326.SR", "8250.SR", "9523.SR", "1302.SR",
    "2084.SR", "3003.SR", "4323.SR", "8060.SR", "4320.SR", "2110.SR", "2240.SR", "4240.SR", "4012.SR", "4040.SR",
    "2370.SR", "2282.SR", "4344.SR", "1183.SR", "4292.SR", "2150.SR", "4143.SR", "1202.SR", "6014.SR", "4261.SR",
    "1323.SR", "3004.SR", "4262.SR", "2200.SR", "1820.SR", "4193.SR", "9601.SR", "6070.SR", "6018.SR", "2281.SR",
    "4081.SR", "4110.SR", "1835.SR", "4144.SR", "9541.SR", "4230.SR", "9618.SR", "8070.SR", "4328.SR", "4080.SR",
    "6001.SR", "6002.SR", "9517.SR", "3002.SR", "4014.SR", "9521.SR", "1182.SR", "9559.SR", "9510.SR", "4145.SR",
    "9583.SR", "2140.SR", "2120.SR", "4147.SR", "7205.SR", "9649.SR", "2030.SR", "4330.SR", "4290.SR", "2340.SR",
    "1324.SR", "1210.SR", "9544.SR", "4148.SR", "2288.SR", "4191.SR", "4170.SR", "4180.SR", "8012.SR", "4265.SR",
    "4194.SR", "1214.SR", "8120.SR", "4324.SR", "9640.SR", "9655.SR", "2287.SR", "3007.SR", "8240.SR", "8300.SR",
    "4082.SR", "8280.SR", "9527.SR", "8040.SR", "4333.SR", "4008.SR", "9637.SR", "3005.SR", "3090.SR", "9610.SR",
    "1325.SR", "9546.SR", "4051.SR", "9634.SR", "9628.SR", "1301.SR", "4011.SR", "9596.SR", "2130.SR", "9552.SR",
    "9543.SR", "3091.SR", "2210.SR", "8020.SR", "4006.SR", "9514.SR", "9560.SR", "9568.SR", "9575.SR", "4336.SR",
    "2160.SR", "2180.SR", "9611.SR", "2100.SR", "4130.SR", "9607.SR", "1832.SR", "9639.SR", "4140.SR", "7201.SR",
    "9580.SR", "6050.SR", "4061.SR", "9627.SR", "4070.SR", "9530.SR", "9614.SR", "6060.SR", "4021.SR", "9613.SR",
    "2090.SR", "8160.SR", "2220.SR", "9625.SR", "6016.SR", "9548.SR", "6090.SR", "6020.SR", "2001.SR", "9594.SR",
    "9564.SR", "1213.SR", "9550.SR", "9574.SR", "8100.SR", "4270.SR", "4335.SR", "9600.SR", "9641.SR", "9566.SR",
    "9631.SR", "1201.SR", "8180.SR", "6040.SR", "8170.SR", "9585.SR", "4141.SR", "9576.SR", "3008.SR", "9602.SR",
    "9650.SR", "9569.SR", "9598.SR", "8310.SR", "6013.SR", "9545.SR", "9603.SR", "9563.SR", "9592.SR", "8311.SR",
    "9648.SR", "2360.SR", "9604.SR", "8050.SR", "4160.SR", "9570.SR", "9516.SR", "8150.SR", "9593.SR", "9532.SR",
    "9636.SR", "9591.SR", "9558.SR", "9615.SR", "9551.SR", "9547.SR", "8190.SR", "9624.SR", "9612.SR", "9626.SR",
    "9542.SR", "9538.SR", "9581.SR", "4331.SR", "9588.SR", "9606.SR", "9549.SR", "9644.SR", "9555.SR", "6012.SR",
    "9635.SR", "9522.SR", "9584.SR", "8260.SR", "9619.SR", "9608.SR", "9587.SR", "9651.SR", "9609.SR", "9524.SR",
    "9645.SR", "9537.SR", "9589.SR", "9622.SR", "9515.SR", "9579.SR", "9578.SR", "9562.SR", "9623.SR", "9586.SR",
    "9597.SR", "9539.SR", "9599.SR", "9632.SR", "9571.SR", "9647.SR", "9605.SR", "9620.SR", "9630.SR", "9567.SR",
    "9536.SR", "9595.SR", "9621.SR", "9616.SR", "9633.SR", "9561.SR", "9572.SR", "9533.SR", "9617.SR", "9653.SR",
    "9565.SR", "9577.SR", "9642.SR", "9553.SR",
]
BONDS = ["^TNX", "^TYX", "^FVX", "^IRX", "IEF", "IEI", "SHY", "TLH", "AGG", "BND", "HYG", "LQD", "TIP", "EMB", "MUB", "ZN=F", "ZB=F"]   # 10y / 30y / 5y / 13w yields, Treasury ETFs + futures, core / high-yield / investment-grade / TIPS / EM / muni ETFs
BY_CLASS = {"Forex": FOREX, "Indices": INDICES, "Bonds": BONDS, "Egypt (EGX)": EGX, "Saudi (Tadawul)": TADAWUL}


def symbols(cls: str) -> list[str]:
    return [PREFIX + s for s in BY_CLASS.get(cls, [])]


_DEAD: set = set()   # symbols Yahoo answered "unknown symbol" for: skipped for the rest of this server run (each one costs retries)


def mark_dead(sym: str) -> None:
    _DEAD.add(sym[len(PREFIX):] if is_yahoo(sym) else sym)


def _universe_file() -> dict:
    import json
    import pathlib
    try:
        return json.loads((pathlib.Path(__file__).resolve().parent.parent / "data" / "universe_yahoo.json").read_text(encoding="utf-8"))
    except Exception:
        return {}


def universe(cls: str) -> list[str]:
    """Every listed symbol of a Yahoo-only market (EGX / Tadawul), biggest first, index first, minus symbols Yahoo does not know.
    Falls back to the short list when data/universe_yahoo.json is missing. Other classes: the same as symbols()."""
    d = _universe_file()
    if cls == "Egypt (EGX)" and d.get("egx"):
        raw = ["^CASE30"] + [t + ".CA" for t in d["egx"]]
    elif cls == "Saudi (Tadawul)" and d.get("tadawul"):
        raw = ["^TASI.SR"] + [t + ".SR" for t in d["tadawul"]]
    else:
        raw = BY_CLASS.get(cls, [])
    return [PREFIX + s for s in raw if s not in _DEAD]


def is_yahoo(sym: str) -> bool:
    return isinstance(sym, str) and sym.startswith(PREFIX)


def parse_chart(d: dict) -> pd.DataFrame:
    """Yahoo v8 chart JSON -> OHLCV frame (rows with a missing OHLC value are dropped)."""
    res = ((d or {}).get("chart") or {}).get("result") or []
    if not res:
        err = ((d or {}).get("chart") or {}).get("error") or {}
        raise ValueError(err.get("description") or "no data")
    r = res[0]
    ts, q = r.get("timestamp") or [], ((r.get("indicators") or {}).get("quote") or [{}])[0]
    if not ts or not q.get("close"):
        raise ValueError("no candles")
    df = pd.DataFrame({"time": pd.to_datetime(pd.Series(ts, dtype="int64"), unit="s"), "open": q.get("open"), "high": q.get("high"),
                       "low": q.get("low"), "close": q.get("close"), "volume": q.get("volume") or [0] * len(ts)})
    df = df.dropna(subset=["open", "high", "low", "close"]).copy()
    df["volume"] = df["volume"].fillna(0).astype(float)
    for c in ("open", "high", "low", "close"):
        df[c] = df[c].astype(float)
    return df.reset_index(drop=True)


# Disk cache: a restart no longer refetches every symbol (600+ series). Fresh = younger than the market_cache TTL for the
# timeframe; if Yahoo fails, a copy up to MAX_STALE_FACTOR x TTL old is used instead of an error.
CACHE_DIR = Path(os.environ.get("YAHOO_CACHE_DIR", "data/cache/yahoo"))


def _cache_path(sym: str, tf: str) -> Path:
    return CACHE_DIR / (re.sub(r"[^A-Za-z0-9._-]", "_", sym) + "_" + tf + ".pkl")


def get_yahoo_klines(sym: str, tf: str, limit: int = 300) -> pd.DataFrame:
    from modules.market_cache import MAX_STALE_FACTOR, TTL
    ttl = TTL.get(tf, 60)
    p = _cache_path(sym, tf)
    age = time.time() - p.stat().st_mtime if p.exists() else None
    if age is not None and age < ttl:
        try:
            df = pd.read_pickle(p)
            if len(df) >= limit:
                return df.tail(limit).reset_index(drop=True)
        except Exception:
            pass
    try:
        df = _fetch_yahoo(sym, tf, limit)
    except Exception:
        if age is not None and age < ttl * MAX_STALE_FACTOR:
            try:
                return pd.read_pickle(p).tail(limit).reset_index(drop=True)
            except Exception:
                pass
        raise
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".tmp")
        df.to_pickle(tmp)
        os.replace(tmp, p)
    except OSError:
        pass   # cache is best effort: the fresh data is still returned
    return df


def _fetch_yahoo(sym: str, tf: str, limit: int = 300) -> pd.DataFrame:
    if tf not in TF:
        raise ValueError(f"Yahoo feed: timeframe {tf} not supported")
    if tf in ("1h", "4h"):   # both come from the same 60m download: one request per symbol, the second job waits for the first
        df = _raw_60m(sym)
        if tf == "4h":
            df = aggregate_frame(df, 4, 60)
        return df.tail(limit).reset_index(drop=True)
    return _download(sym, tf, limit)


_RAW60: dict = {}   # symbol -> (time, frame)
_RAW60_LOCKS: dict = {}


def _raw_60m(sym: str) -> pd.DataFrame:
    import threading
    import time
    lock = _RAW60_LOCKS.setdefault(sym, threading.Lock())
    with lock:
        hit = _RAW60.get(sym)
        if hit and time.time() - hit[0] < 90:
            if isinstance(hit[1], Exception):
                raise hit[1]
            return hit[1]
        try:
            df = _download(sym, "1h", 100000)
        except ValueError as e:   # unknown symbol / no candles: remember it so the 4h job does not ask again (429 / network errors are not cached: those are retried)
            _RAW60[sym] = (time.time(), e)
            raise
        _RAW60[sym] = (time.time(), df)
        return df


def _download(sym: str, tf: str, limit: int) -> pd.DataFrame:
    iv, rg, n = TF[tf]
    ysym = requests.utils.quote(sym[len(PREFIX):] if is_yahoo(sym) else sym, safe="")
    r = None
    for host in HOSTS:   # second host as a fallback when one is throttled
        try:
            r = requests.get(URL.format(host=host, sym=ysym), params={"interval": iv, "range": rg}, headers=HDR, timeout=12)
        except requests.RequestException as e:
            r = None
            err = type(e).__name__
            continue
        if r.status_code == 200:
            break
    if r is None:
        raise requests.exceptions.ConnectionError(f"Yahoo unreachable ({err})")   # a ConnectionError so market_cache's breaker counts it
    if r.status_code == 429:
        raise RuntimeError("Yahoo rate limit (429)")
    if r.status_code == 404:
        raise ValueError("Yahoo: unknown symbol")
    if r.status_code != 200:
        raise RuntimeError(f"Yahoo HTTP {r.status_code}")
    df = parse_chart(r.json())
    if n > 1:
        df = aggregate_frame(df, n, 60)
    return df.tail(limit).reset_index(drop=True)


_TV = {"^IXIC": "NASDAQ:IXIC", "^NDX": "NASDAQ:NDX", "^GSPC": "SP:SPX", "^DJI": "DJ:DJI", "^RUT": "TVC:RUT", "^VIX": "CBOE:VIX",
       "^GDAXI": "XETR:DAX", "^FTSE": "TVC:UKX", "^N225": "TVC:NI225", "^HSI": "TVC:HSI", "^CASE30": "EGX:EGX30", "^TASI.SR": "TADAWUL:TASI"}


def tv_symbol(sym: str) -> str:
    """"Y:..." -> TradingView symbol for the embedded chart."""
    y = sym[len(PREFIX):]
    if y in _TV:
        return _TV[y]
    if y.endswith("=X"):
        return "FX:" + y[:-2]
    if y.endswith(".CA"):
        return "EGX:" + y[:-3]
    if y.endswith(".SR"):
        return "TADAWUL:" + y[:-3]
    return y


EMBED_TFS = ("15m", "1h", "4h", "1d")


def embed(symbols, bars: int = 200, frames: dict | None = None) -> dict:
    """{ "Y:SYM": {"15m": [[ms,o,h,l,c,v], ...oldest first], "1h": ..., "4h": ..., "1d": ...} } for the browser Workspace
    (its page cannot call Yahoo itself - CORS - so the candles are handed over inside the page). Failed symbols are left out.
    frames = candles already downloaded by the caller ({sym: {tf: DataFrame}}): used as they are, nothing is fetched."""
    from modules.market_cache import fetch_frames
    ys = [x for x in symbols if is_yahoo(x)]
    if not ys:
        return {}
    if frames is None:
        frames, _errs = fetch_frames(ys, list(EMBED_TFS), limit=bars, workers=8)
    out = {}
    for sym in ys:
        d = {}
        for tf, df in (frames.get(sym) or {}).items():
            if df is not None and len(df):
                df = df.tail(bars)
                d[tf] = [[int(t.timestamp() * 1000), round(o, 6), round(h, 6), round(l, 6), round(c, 6), round(v, 2)]
                         for t, o, h, l, c, v in zip(df["time"], df["open"], df["high"], df["low"], df["close"], df["volume"])]
        if d:
            out[sym] = d
    return out
