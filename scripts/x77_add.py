"""Save one chart picture (or a text note) into the X77 library with its schools, from the terminal.

Owner workflow (2026-11-21): the owner sends a chart picture in chat; Claude reads it, writes what it shows in Arabic,
picks the X77 schools, and saves it here. The school tags feed the Workspace widget and the chart indicator
("في المكتبة: n"). A saved picture is an example, not evidence: a new setup idea still needs pre-registration.

  python3 scripts/x77_add.py --file shot.png --schools S_SMC_ICT,S_FIB --sym XAUUSD --tf 1h --text "سويب تحت القاع ثم OTE"
  python3 scripts/x77_add.py --text "ملاحظة بدون صورة" --schools S_ELLIOTT
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import os  # noqa: E402
os.environ.setdefault("X77_DATA_DIR", str(ROOT / "data" / "x77" / "store"))   # same store the app reads when run from the repo root

from modules import x77_store as store  # noqa: E402
from modules.x77_detect import SCHOOLS  # noqa: E402

IMG = (".png", ".jpg", ".jpeg", ".webp", ".gif")


def main(argv=None) -> dict:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--file", help="picture / video / pdf path")
    ap.add_argument("--text", default="", help="what the picture shows (Arabic is fine)")
    ap.add_argument("--schools", default="", help="comma separated: " + ",".join(SCHOOLS))
    ap.add_argument("--sym", default="")
    ap.add_argument("--tf", default="")
    ap.add_argument("--kind", default="", help="default: image for a picture, else lesson")
    ap.add_argument("--tags", default="", help="extra tags, comma separated")
    ap.add_argument("--source", default="chat", help="where it came from (chat, telegram, youtube ...)")
    a = ap.parse_args(argv)
    schools = [s.strip().upper() for s in a.schools.split(",") if s.strip()]
    bad = [s for s in schools if s not in SCHOOLS]
    if bad:
        raise SystemExit(f"unknown school(s) {bad}; use: {', '.join(SCHOOLS)}")
    kind = a.kind or ("image" if a.file and Path(a.file).suffix.lower() in IMG else "lesson")
    tags = tuple(schools) + tuple(t for t in (a.sym, a.tf, a.source) if t) + tuple(t for t in a.tags.split(",") if t.strip())
    item = store.add_item(kind, text=a.text, file=a.file, tags=tags)
    print(f"saved {item['id']} kind={kind} tags={','.join(item['tags'])}")
    return item


if __name__ == "__main__":
    main()
