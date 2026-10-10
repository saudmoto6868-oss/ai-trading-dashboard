"""Official site icons for the slim links bar, fetched once from each site's own
/favicon.ico and cached (so the page does not depend on a third-party icon
service). If a site blocks the request the bar shows a small letter chip."""

from __future__ import annotations

import base64
from functools import lru_cache

import requests


@lru_cache(maxsize=64)
def site_icon_b64(domain: str) -> str:
    try:
        r = requests.get(f"https://{domain}/favicon.ico", timeout=4,
                         headers={"User-Agent": "Mozilla/5.0 (compatible; 6868X/1.0)"})
        if r.ok and 100 < len(r.content) < 60000 and "text/html" not in r.headers.get("content-type", ""):
            return base64.b64encode(r.content).decode("ascii")
    except Exception:
        pass
    return ""
