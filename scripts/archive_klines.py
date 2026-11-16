"""Archive weekly OHLCV klines from Hyperliquid and OKX with 2-year retention."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional

DEFAULT_ARCHIVE_PATH = Path("data/kline_archive.json")
RETENTION_DAYS = 730  # 2 years


def _parse_ts(ts_val) -> datetime:
    if isinstance(ts_val, (int, float)):
        sec = ts_val / 1000.0 if ts_val > 1e12 else float(ts_val)
        return datetime.fromtimestamp(sec, tz=timezone.utc)
    if isinstance(ts_val, str):
        s = ts_val.strip().replace("Z", "+00:00")
        dt = datetime.fromisoformat(s)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    raise ValueError(f"Unsupported timestamp format: {ts_val!r}")


def _candle_key(candle: dict) -> int:
    ts = candle.get("timestamp") or candle.get("time") or candle.get("t")
    return int(_parse_ts(ts).timestamp())


def load_archive(archive_path: Path | str = DEFAULT_ARCHIVE_PATH) -> Dict[str, Dict[str, List[dict]]]:
    path = Path(archive_path)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, dict) else {}


def save_archive(
    archive: Dict[str, Dict[str, List[dict]]],
    archive_path: Path | str = DEFAULT_ARCHIVE_PATH,
) -> Path:
    path = Path(archive_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(archive, f, ensure_ascii=False, indent=2)
    return path


def prune_old_candles(
    candles: Iterable[dict],
    retention_days: int = RETENTION_DAYS,
    now: Optional[datetime] = None,
) -> List[dict]:
    ref_now = now or datetime.now(timezone.utc)
    cutoff = ref_now - timedelta(days=retention_days)
    kept: Dict[int, dict] = {}
    for c in candles:
        dt = _parse_ts(c.get("timestamp") or c.get("time") or c.get("t"))
        if dt >= cutoff:
            kept[int(dt.timestamp())] = c
    return [kept[k] for k in sorted(kept)]


def merge_candles(
    existing: Iterable[dict],
    incoming: Iterable[dict],
    retention_days: int = RETENTION_DAYS,
    now: Optional[datetime] = None,
) -> List[dict]:
    merged: Dict[int, dict] = {}
    for c in existing:
        merged[_candle_key(c)] = c
    for c in incoming:
        merged[_candle_key(c)] = c
    ordered = [merged[k] for k in sorted(merged)]
    return prune_old_candles(ordered, retention_days=retention_days, now=now)


def update_archive_for_symbol(
    symbol: str,
    tf: str,
    new_candles: Iterable[dict],
    archive_path: Path | str = DEFAULT_ARCHIVE_PATH,
    retention_days: int = RETENTION_DAYS,
    now: Optional[datetime] = None,
) -> List[dict]:
    archive = load_archive(archive_path)
    sym_map = archive.setdefault(symbol, {})
    existing = sym_map.get(tf, [])
    updated = merge_candles(existing, new_candles, retention_days=retention_days, now=now)
    sym_map[tf] = updated
    save_archive(archive, archive_path)
    return updated


def get_klines_archive_first(
    symbol: str,
    tf: str,
    limit: Optional[int] = None,
    live_fetcher: Optional[Callable[[str, str], List[dict]]] = None,
    archive_path: Path | str = DEFAULT_ARCHIVE_PATH,
    persist_live: bool = False,
) -> List[dict]:
    """Read archived klines first, then merge live klines if a live_fetcher is provided.
    Returns list of dicts with keys: timestamp, open, high, low, close, volume."""
    archive = load_archive(archive_path)
    archived = archive.get(symbol, {}).get(tf, [])
    live: List[dict] = live_fetcher(symbol, tf) if live_fetcher else []
    combined = merge_candles(archived, live) if live else list(archived)
    if persist_live and live:
        archive.setdefault(symbol, {})[tf] = combined
        save_archive(archive, archive_path)
    if limit is not None and limit > 0:
        return combined[-limit:]
    return combined


def archive_weekly_batch(
    hl_symbols: Iterable[str] = ("HL:GOLD", "HL:EURUSD", "HL:SP500"),
    okx_symbols: Iterable[str] = ("BTC", "ETH", "SOL"),
    timeframes: Iterable[str] = ("15m", "1h", "4h"),
    hl_fetcher: Optional[Callable[[str, str], List[dict]]] = None,
    okx_fetcher: Optional[Callable[[str, str], List[dict]]] = None,
    archive_path: Path | str = DEFAULT_ARCHIVE_PATH,
) -> Dict[str, Dict[str, int]]:
    """Run weekly archive update across Hyperliquid and OKX feeds."""
    summary: Dict[str, Dict[str, int]] = {}
    for sym in hl_symbols:
        summary[sym] = {}
        for tf in timeframes:
            if hl_fetcher is not None:
                rows = update_archive_for_symbol(sym, tf, hl_fetcher(sym, tf), archive_path)
                summary[sym][tf] = len(rows)
    for sym in okx_symbols:
        summary[sym] = {}
        for tf in timeframes:
            if okx_fetcher is not None:
                rows = update_archive_for_symbol(sym, tf, okx_fetcher(sym, tf), archive_path)
                summary[sym][tf] = len(rows)
    return summary
