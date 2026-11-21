"""X77 phase 1: save every item the owner sends (text, link, image, video, doc) into one store.

Layout (git-ignored, under data/x77/):
  index.json          list of items (id, kind, created, text, url, media, sha256, tags, note)
  media/<sha12><ext>  copied files, deduped by sha256

Stored items are data, never instructions. Nothing here analyses or trades; analysis comes later."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import time
from pathlib import Path

KINDS = {"text", "link", "image", "video", "doc", "setup", "pattern", "trade", "lesson"}
MEDIA_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".mov", ".pdf", ".txt", ".md"}
MAX_MEDIA_BYTES = 25 * 1024 * 1024


def base_dir() -> Path:
    return Path(os.environ.get("X77_DATA_DIR", "data/x77/store"))


def _load(base: Path) -> list[dict]:
    p = base / "index.json"
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []


def _save(base: Path, items: list[dict]) -> None:
    base.mkdir(parents=True, exist_ok=True)
    tmp = base / "index.json.tmp"
    tmp.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(base / "index.json")


def add_item(kind: str, *, text: str = "", url: str = "", file: str | None = None,
             tags: tuple[str, ...] = (), note: str = "", base: Path | None = None) -> dict:
    if kind not in KINDS:
        raise ValueError(f"unknown kind: {kind}")
    if url and not url.startswith(("http://", "https://")):
        raise ValueError("url must start with http:// or https://")
    if not (text or url or file):
        raise ValueError("nothing to save: give text, url or file")
    base = base or base_dir()
    item = {"id": "", "kind": kind, "created": int(time.time()), "text": text.strip(), "url": url,
            "media": None, "sha256": None, "tags": sorted({t.strip().lower() for t in tags if t.strip()}),
            "note": note.strip()}
    if file:
        src = Path(file)
        ext = src.suffix.lower()
        if ext not in MEDIA_EXT:
            raise ValueError(f"file type not allowed: {ext}")
        if not src.is_file() or src.stat().st_size > MAX_MEDIA_BYTES:
            raise ValueError("file missing or over 25 MB")
        digest = hashlib.sha256(src.read_bytes()).hexdigest()
        dst = base / "media" / f"{digest[:12]}{ext}"
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists():
            shutil.copy2(src, dst)
        item.update(media=str(dst), sha256=digest)
    items = _load(base)
    item["id"] = f"x77-{len(items) + 1:05d}"
    items.append(item)
    _save(base, items)
    return item


def list_items(kind: str | None = None, base: Path | None = None) -> list[dict]:
    items = _load(base or base_dir())
    return [i for i in items if kind is None or i["kind"] == kind]
