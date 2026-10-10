"""Economic calendar: ForexFactory's public weekly JSON feed (unofficial mirror at faireconomy.media)."""
from __future__ import annotations

from datetime import datetime

import requests

URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"


def parse_calendar(rows: list) -> list[dict]:
    out = []
    for e in rows or []:
        try:
            ts = int(datetime.fromisoformat(str(e["date"])).timestamp() * 1000)
        except Exception:
            continue
        imp = str(e.get("impact", "")).title()
        if imp not in ("High", "Medium"):
            continue
        out.append({"title": str(e.get("title", "")), "country": str(e.get("country", "")), "ts": ts, "impact": imp,
                    "forecast": str(e.get("forecast", "")), "previous": str(e.get("previous", ""))})
    return sorted(out, key=lambda x: x["ts"])


def fetch_calendar() -> list[dict]:
    r = requests.get(URL, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    return parse_calendar(r.json())
