"""Thin top strip rendered as ONE iframe: logo | links | news ticker (click = dropdown) | Cairo + New York clocks | World map."""
from __future__ import annotations

import json
from pathlib import Path

_TEMPLATE = Path(__file__).with_name("header_bar.html")


def build_header_html(logo: str, links: list, news: list, no_news: str = "No news yet") -> str:
    cfg = {
        "logo": logo, "links": links, "noNews": no_news,
        "news": [{"headline": str(n.get("headline", "")), "source": str(n.get("source", "")), "url": str(n.get("url", "")),
                  "datetime": str(n.get("datetime", ""))} for n in (news or []) if n.get("headline")],
    }
    payload = json.dumps(cfg, ensure_ascii=False).replace("</", "<\\/")
    return _TEMPLATE.read_text(encoding="utf-8").replace("__CONFIG__", payload, 1)


def render_header_bar(logo: str, links: list, news: list, height: int = 54):
    import streamlit.components.v1 as components

    components.html(build_header_html(logo, links, news), height=height, scrolling=False)
