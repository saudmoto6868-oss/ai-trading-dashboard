"""
THE DATA RUNNER
Fetches candles for many (symbol, timeframe) pairs in parallel and keeps them
in a small shared in-memory cache, so the auto-refreshing dashboard does not
hammer the exchange API. Plain Python (no Streamlit) so it is thread-safe and
easy to test. If a fetch fails but an older copy exists, the old copy is used.
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor

from modules.data_fetcher import get_binance_klines  # name kept; talks to OKX now

# how long a candle set stays fresh, per timeframe (seconds)
TTL = {"1m": 15, "5m": 30, "15m": 60, "1h": 60, "4h": 180, "1d": 300, "1w": 900,
       "13m": 60, "2h": 120, "3h": 180, "6h": 300, "7h": 300, "8h": 300, "12h": 600, "3d": 900, "1mo": 1800}
MAX_STALE_FACTOR = 6

_cache: dict = {}
_lock = threading.Lock()


def get_klines(symbol: str, tf: str, limit: int = 300):
    """-> DataFrame. Raises only if there is no usable copy at all."""
    key = (symbol, tf, limit)
    ttl = TTL.get(tf, 60)
    now = time.time()
    with _lock:
        hit = _cache.get(key)
    if hit and now - hit[0] < ttl:
        return hit[1]
    try:
        if symbol.startswith("HL:"):   # Hyperliquid TradFi perps (gold, oil, S&P 500, EUR ...): public API, no key
            from modules.hl_feed import get_klines as _hl
            df = _hl(symbol, tf, limit)
        elif symbol.startswith("Y:"):   # forex / Nasdaq / EGX / Tadawul: Yahoo feed (OKX does not list them)
            from modules.yahoo_feed import get_yahoo_klines
            try:
                df = get_yahoo_klines(symbol, tf, limit)
            except Exception as ye:   # Yahoo down / throttled: forex daily+weekly can come from Alpha Vantage instead
                from modules import av_feed, biquote_feed
                df = None
                errs = [str(ye)]
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
                    if len(errs) == 1:
                        raise
                    raise RuntimeError(" | ".join(errs))
        else:
            df = get_binance_klines(symbol, interval=tf, limit=limit)
        with _lock:
            _cache[key] = (now, df)
        return df
    except Exception:
        if hit and now - hit[0] < ttl * MAX_STALE_FACTOR:
            return hit[1]
        raise


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
                time.sleep(0.6 * (attempt + 1))
        return s, tf, None, err

    with ThreadPoolExecutor(max_workers=workers) as ex:
        for s, tf, df, err in ex.map(run, jobs):
            if df is not None:
                frames[s][tf] = df
            else:
                errors[s] = (errors.get(s, "") + " " + err).strip()
    return frames, errors
