"""News helpers: title-normalised de-duplication and Cairo-time display. No network, no keys."""
from __future__ import annotations

import re
import unicodedata
from datetime import datetime, timezone

try:
    from zoneinfo import ZoneInfo
    _CAIRO = ZoneInfo("Africa/Cairo")
except Exception:   # no tz database on this host: fall back to labelled UTC, never guess an offset
    _CAIRO = None

_NON_WORD = re.compile(r"[^\w]+", re.UNICODE)


def norm_title(title: str) -> str:
    """Case / punctuation / spacing-insensitive key; Arabic diacritics (tashkeel) are dropped."""
    t = unicodedata.normalize("NFKC", str(title or "")).casefold()
    t = "".join(c for c in t if not unicodedata.combining(c))
    return _NON_WORD.sub(" ", t).strip()


def dedupe(items: list, key: str = "headline") -> list:
    """Keep the first item per normalised title (input order decides the winner; each kept item is unchanged).
    Items with an empty title are kept as-is."""
    seen, out = set(), []
    for it in items:
        k = norm_title(it.get(key, ""))
        if k:
            if k in seen:
                continue
            seen.add(k)
        out.append(it)
    return out


def cairo_str(ts) -> str:
    """Unix seconds -> 'YYYY-MM-DD HH:MM Cairo' ('' when ts is missing / 0). Falls back to '... UTC' without tz data."""
    try:
        ts = int(ts)
    except (TypeError, ValueError):
        return ""
    if ts <= 0:
        return ""
    if _CAIRO is None:
        return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return datetime.fromtimestamp(ts, _CAIRO).strftime("%Y-%m-%d %H:%M Cairo")
