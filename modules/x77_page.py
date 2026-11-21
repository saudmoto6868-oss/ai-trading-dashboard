"""X77 page (Streamlit): see everything saved in the X77 store, add text / link / file. Saves only; no analysis yet."""
from __future__ import annotations

from pathlib import Path

import streamlit as st

from modules import x77_store as store

KIND_CHOICES = ["text", "link", "image", "video", "doc", "setup", "pattern", "trade", "lesson"]
IMG_EXT = (".png", ".jpg", ".jpeg", ".webp", ".gif")


def _tags(raw: str) -> tuple[str, ...]:
    return tuple(t for t in raw.split(",") if t.strip())


def render() -> None:
    st.subheader("X77")
    st.caption("Saves what you send (text, link, image, video, document). Nothing here analyses or trades yet.")

    with st.form("x77_add", clear_on_submit=True):
        kind = st.selectbox("Kind", KIND_CHOICES, index=0)
        text = st.text_area("Text", height=80)
        url = st.text_input("Link (https://...)")
        tags = st.text_input("Tags (comma separated)")
        up = st.file_uploader("File", type=["png", "jpg", "jpeg", "webp", "gif", "mp4", "mov", "pdf", "txt", "md"])
        ok = st.form_submit_button("Save to X77")
    if ok:
        try:
            if up is not None:
                tmp = store.base_dir() / "_upload" / up.name
                tmp.parent.mkdir(parents=True, exist_ok=True)
                tmp.write_bytes(up.getvalue())
                try:
                    saved = store.add_item(kind, text=text, url=url, file=str(tmp), tags=_tags(tags))
                finally:
                    tmp.unlink(missing_ok=True)
            else:
                saved = store.add_item(kind, text=text, url=url, tags=_tags(tags))
            st.success(f"Saved {saved['id']}")
        except ValueError as exc:
            st.error(str(exc))

    filt = st.segmented_control("Show", ["all"] + KIND_CHOICES, default="all", key="x77_filter")
    items = store.list_items(None if filt in (None, "all") else filt)
    st.caption(f"{len(items)} item(s)")
    for it in reversed(items[-200:]):
        with st.container(border=True):
            st.markdown(f"**{it['id']}** · `{it['kind']}` · tags: {', '.join(it['tags']) or '-'}")
            if it.get("text"):
                st.write(it["text"])
            if it.get("url"):
                st.write(it["url"])
            if it.get("media"):
                p = Path(it["media"])
                if p.suffix.lower() in IMG_EXT and p.is_file():
                    st.image(str(p), width=360)
                else:
                    st.caption(p.name)
