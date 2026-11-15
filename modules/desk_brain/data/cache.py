"""Tiny TTL cache (memory + pickle on disk) so repeated scans don't hammer free sources.

Single-flight: when several threads ask for the same missing key at once (the scan, the
dashboard and the agents often do), only one fetches and the others wait for its result.
`keep(value)` returning False caches the value briefly in memory only (used for demo
fallbacks, so a temporary outage does not pin demo data for an hour)."""
from __future__ import annotations

import hashlib
import pickle
import threading
import time
from typing import Any, Callable

from ..config import DATA_DIR

_mem: dict[str, tuple[float, Any]] = {}      # key -> (expires_at, value)
_lock = threading.Lock()
_inflight: dict[str, threading.Lock] = {}
_CACHE_DIR = DATA_DIR / "cache"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)
SHORT_TTL = 60.0


def _path(key: str):
    return _CACHE_DIR / (hashlib.sha1(key.encode()).hexdigest() + ".pkl")


def _fresh(key: str, ttl_s: float, disk: bool):
    now = time.time()
    with _lock:
        hit = _mem.get(key)
        if hit and now < hit[0]:
            return True, hit[1]
    path = _path(key)
    if disk and path.exists() and now - path.stat().st_mtime < ttl_s:
        try:
            val = pickle.loads(path.read_bytes())
            with _lock:
                _mem[key] = (path.stat().st_mtime + ttl_s, val)
            return True, val
        except Exception:
            pass
    return False, None


def cached(key: str, ttl_s: float, fn: Callable[[], Any], disk: bool = True,
           keep: Callable[[Any], bool] | None = None) -> Any:
    ok, val = _fresh(key, ttl_s, disk)
    if ok:
        return val
    with _lock:
        flight = _inflight.setdefault(key, threading.Lock())
    with flight:
        ok, val = _fresh(key, ttl_s, disk)   # another thread may have filled it meanwhile
        if ok:
            return val
        val = fn()
        good = keep(val) if keep else True
        with _lock:
            _mem[key] = (time.time() + (ttl_s if good else SHORT_TTL), val)
        if disk and good:
            try:
                _path(key).write_bytes(pickle.dumps(val))
            except Exception:
                pass
        return val


def last_good(key: str) -> Any:
    """The last value written to disk for a key, however old (None if never)."""
    path = _path(key)
    if path.exists():
        try:
            return pickle.loads(path.read_bytes())
        except Exception:
            return None
    return None


def clear() -> None:
    with _lock:
        _mem.clear()
    for p in _CACHE_DIR.glob("*.pkl"):
        p.unlink(missing_ok=True)
