"""Screen recorder + quick editor that follows the user to EVERY page (Workspace, Radar, Technical Office, Academy ...).

Why here and not inside the Workspace frame: that frame is destroyed every time a page is switched, and the recorder with it. This injects modules/screen_recorder.js
once into the PARENT page (same origin as the component iframe), where it lives until the browser tab is closed. Everything stays in the browser: no upload, no keys.
"""
from __future__ import annotations

import json
from pathlib import Path

_JS_PATH = Path(__file__).with_name("screen_recorder.js")


def injector_html() -> str:
    """The tiny HTML document the zero-height component runs: it puts the recorder script into the parent page (once)."""
    code = _JS_PATH.read_text(encoding="utf-8")
    lit = json.dumps(code).replace("</", "<\\/")   # a literal </script> inside the string would end the tag
    return (
        "<script>(function(){try{var p=window.parent;if(p.__xpixRec)return;"
        "var s=p.document.createElement('script');s.textContent=" + lit + ";p.document.head.appendChild(s);}catch(e){}})();</script>"
    )


def render() -> None:
    """Call once per run, after the page bar. A hidden container: the component adds no visible gap."""
    import streamlit as st
    from streamlit.components.v1 import html as _html

    with st.container(key="xpix_rec_host"):
        st.markdown("<style>.st-key-xpix_rec_host{display:none!important}</style>", unsafe_allow_html=True)
        _html(injector_html(), height=0)
