"""One loud banner for the research pages that run on invented numbers (owner rule: no invented number may look like a result)."""
from __future__ import annotations

_BANNER = ('<div style="position:sticky;top:0;z-index:99;background:#7a1f1f;color:#fff;font:600 13px/1.5 system-ui,sans-serif;padding:8px 14px;'
           'border-bottom:2px solid #f0b90b;text-align:center" id="demo-banner">'
           '⚠ DEMO · أرقام مخترعة، مش دليل ومش نتيجة حقيقية — {note}<br>'
           'DEMO · invented numbers, not evidence and not a real result — {note_en}</div>')


def with_demo_banner(html: str, note: str = "الألوان والأرقام للشكل فقط", note_en: str = "colours and numbers show the layout only") -> str:
    """Insert the banner right after <body ...>; the page is unchanged otherwise."""
    banner = _BANNER.format(note=note, note_en=note_en)
    i = html.find("<body")
    if i < 0:
        return banner + html
    j = html.find(">", i)
    return html[:j + 1] + banner + html[j + 1:]
