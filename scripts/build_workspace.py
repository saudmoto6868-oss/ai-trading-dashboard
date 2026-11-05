#!/usr/bin/env python3
"""Build modules/workspace_app.html from the parts in modules/ws/ (sorted by file name, joined byte for byte).

The parts are the SOURCE; workspace_app.html is the generated file (kept in git so the tests, the CI workflows and
modules/workspace.py keep reading one file). Edit a part, then run:  python3 scripts/build_workspace.py
Check only (exit 1 if the generated file is out of date):  python3 scripts/build_workspace.py --check
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / "modules" / "ws"
OUT = ROOT / "modules" / "workspace_app.html"


def assemble() -> bytes:
    files = sorted(p for p in PARTS.iterdir() if p.is_file() and not p.name.startswith("."))
    if not files:
        raise SystemExit("no parts in modules/ws/")
    return b"".join(p.read_bytes() for p in files)


def main(argv) -> int:
    data = assemble()
    if "--check" in argv:
        if OUT.read_bytes() != data:
            print("modules/workspace_app.html is out of date: edit the parts in modules/ws/ and run scripts/build_workspace.py")
            return 1
        print("ok: workspace_app.html matches modules/ws/ (%d parts)" % len(list(PARTS.iterdir())))
        return 0
    OUT.write_bytes(data)
    print("wrote %s (%d bytes)" % (OUT.relative_to(ROOT), len(data)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
