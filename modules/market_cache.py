"""
THE DATA RUNNER
Fetches candles for many (symbol, timeframe) pairs in parallel and keeps them
in a small shared in-memory cache, so the auto-refreshing dashboard does not
hammer the exchange API. Plain Python (no Streamlit) so it is thread-safe and
easy to test. If a fetch fails but an older copy exists, the old copy is used.

Speed guards (2026-11-17, shared by Radar, Spot desk and TIA):
- negative cache: a (symbol, tf) that just failed is not re-requested for NEG_TTL seconds,
  so every Streamlit rerun no longer repeats the same dead requests;
- source circuit breaker: after BREAK_AFTER consecutive transport errors (timeout / connection)
  a source (OKX, YAHOO, HL) is skipped for BREAK_FOR seconds;
- fetch_frames does not back off and retry while the source is paused (it used to sleep ~1.8 s per job).
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor

import requests

from modules.data_fetcher import get_binance_klines  # name kept; talks to OKX now

# how long a candle set stays fresh, per timeframe (seconds)
TTL = {"1m": 15, "5m": 30, "15m": 60, "1h": 60, "4h": 180, "1d": 300, "1w": 900,
       "13m": 60, "2h": 120, "3h": 180, "6h": 300, "7h": 300, "8h": 300, "12h": 600, "3d": 900, "1mo": 1800}
MAX_STALE_FACTOR = 6
NEG_TTL = 30        # seconds a failed (symbol, tf, limit) is not retried
BREAK_AFTER = 3     # consecutive transport errors of one source -> the source pauses
BREAK_FOR = 120     # seconds a paused source is skipped

_now = time.time    # injectable clock (tests replace it)
_cache: dict = {}
_neg: dict = {}     # key -> (retry_after, message)
_src: dict = {}     # source -> [consecutive transport failures, paused_until]
_lock = threading.Lock()
_TRANSPORT = (requests.exceptions.ConnectionError, requests.exceptions.Timeout)


def _source(symbol: str) -> str:
    if symbol.startswith("HL:"):
        return "HL"
    if symbol.startswith("Y:"):
        return "YAHOO"
    return "OKX"


def source_paused(src: str) -> bool:
    with _lock:
        st = _src.get(src)
    return bool(st and st[1] > _now())


def _note(src: str, ok: bool, exc: BaseException | None = None) -> None:
    """Count only transport errors: a bad symbol or a parse error must not pause a whole source."""
    with _lock:
        st = _src.setdefault(src, [0, 0.0])
        if ok:
            st[0], st[1] = 0, 0.0
        elif exc is not None and isinstance(exc, _TRANSPORT):
            st[0] += 1
            if st[0] >= BREAK_AFTER:
                st[0], st[1] = 0, _now() + BREAK_FOR


def _fetch_raw(symbol: str, tf: str, limit: int):
    src = _source(symbol)
    if symbol.startswith("HL:"):   # Hyperliquid TradFi perps (gold, oil, S&P 500, EUR ...): public API, no key
        if source_paused(src):
            raise RuntimeError("Hyperliquid paused after repeated failures")
        from modules.hl_feed import get_klines as _hl
        try:
            df = _hl(symbol, tf, limit)
        except Exception as e:
            _note(src, False, e)
            raise
        _note(src, True)
        return df
    if symbol.startswith("Y:"):   # forex / Nasdaq / EGX / Tadawul: Yahoo feed (OKX does not list them)
        from modules import av_feed, biquote_feed
        errs = []
        if not source_paused(src):
            from modules.yahoo_feed import get_yahoo_klines
            try:
                df = get_yahoo_klines(symbol, tf, limit)
                _note(src, True)
                return df
            except Exception as ye:   # Yahoo down / throttled: fall back below
                _note(src, False, ye)
                errs.append(str(ye))
        else:
            errs.append("Yahoo paused after repeated failures")
        df = None
        if biquote_feed.symbol_for(symbol):   # forex / gold / silver: keyless Biquote feed first
            try:
                df = biquote_feed.get_klines(symbol, tf, limit)
            except Exception as be:
                errs.append(str(be))
        if df is None and tf in ("1d", "1w") and av_feed.pair(symbol):
            try:
                df = av_feed.get_fx_klines(symbol, tf, limit)
            except Exception as ae:
                errs.append(str(ae))
        if df is None:
            raise RuntimeError(" | ".join(errs))
        return df
    # crypto: OKX
    if source_paused(src):
        raise RuntimeError("OKX paused after repeated failures")
    try:
        df = get_binance_klines(symbol, interval=tf, limit=limit)
    except Exception as e:
        _note(src, False, e)
        raise
    _note(src, True)
    return df


def get_klines(symbol: str, tf: str, limit: int = 300):
    """-> DataFrame. Raises only if there is no usable copy at all."""
    key = (symbol, tf, limit)
    ttl = TTL.get(tf, 60)
    now = _now()
    with _lock:
        hit = _cache.get(key)
        neg = _neg.get(key)
    if hit and now - hit[0] < ttl:
        return hit[1]
    stale_ok = bool(hit and now - hit[0] < ttl * MAX_STALE_FACTOR)
    if neg and now < neg[0]:   # failed a moment ago: do not repeat the request on every rerun
        if stale_ok:
            return hit[1]
        raise RuntimeError(neg[1])
    try:
        df = _fetch_raw(symbol, tf, limit)
    except Exception as e:
        with _lock:
            _neg[key] = (now + NEG_TTL, str(e)[:300])
        if stale_ok:
            return hit[1]
        raise
    with _lock:
        _cache[key] = (now, df)
        _neg.pop(key, None)
    return df


def fetch_frames(symbols, tfs, limit: int = 300, workers: int = 4):
    """-> (frames, errors); frames[symbol][tf] = DataFrame, errors[symbol] = text."""
    jobs = [(s, tf) for s in symbols for tf in tfs]
    frames = {s: {} for s in symbols}
    errors: dict = {}

    def run(job):
        s, tf = job
        err = None
        for attempt in range(3):   # rate-limit / transient failures: retry with a short back-off
            try:
                return s, tf, get_klines(s, tf, limit), None
            except Exception as e:
                err = f"{tf}: {e}"
                if source_paused(_source(s)):   # a paused source will not answer in a second: stop now
                    break
                time.sleep(0.6 * (attempt + 1))
        return s, tf, None, err

    with ThreadPoolExecutor(max_workers=workers) as ex:
        for s, tf, df, err in ex.map(run, jobs):
            if df is not None:
                frames[s][tf] = df
            else:
                errors[s] = (errors.get(s, "") + " " + err).strip()
    return frames, errors
