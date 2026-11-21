"""Tests for modules/x77_store.py (phase 1). Run: python3 -I tests/test_x77_store.py"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from modules import x77_store as s  # noqa: E402


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


with tempfile.TemporaryDirectory() as t:
    base = Path(t) / "x77"
    img = Path(t) / "a.png"
    img.write_bytes(b"\x89PNG-test-bytes")
    dup = Path(t) / "b.png"
    dup.write_bytes(b"\x89PNG-test-bytes")

    a = s.add_item("text", text="  Double bottom on EURUSD  ", tags=("Pattern", "pattern "), base=base)
    check(a["id"] == "x77-00001", "first id")
    check(a["text"] == "Double bottom on EURUSD", "text stripped")
    check(a["tags"] == ["pattern"], "tags deduped and lowered")

    b = s.add_item("image", file=str(img), base=base)
    c = s.add_item("image", file=str(dup), base=base)
    check(b["media"] == c["media"], "same bytes stored once")
    check(Path(b["media"]).is_file(), "media copied")
    check(len(list(Path(base / "media").iterdir())) == 1, "one media file")

    l = s.add_item("link", url="https://example.com/x", base=base)
    check(l["url"].startswith("https://"), "link kept")
    check(len(s.list_items(base=base)) == 4, "four items")
    check(len(s.list_items("image", base=base)) == 2, "filter by kind")

    for bad in [dict(kind="nope", text="x"), dict(kind="link", url="ftp://x"),
                dict(kind="text"), dict(kind="doc", file=str(Path(t) / "missing.pdf"))]:
        try:
            s.add_item(**bad, base=base)
        except ValueError:
            continue
        raise AssertionError(f"should reject {bad}")

    exe = Path(t) / "run.exe"
    exe.write_bytes(b"MZ")
    try:
        s.add_item("doc", file=str(exe), base=base)
        raise AssertionError("should reject .exe")
    except ValueError:
        pass
print("x77_store: all checks passed")
