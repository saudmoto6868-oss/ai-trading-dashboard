"""One-shot, repeatable migration of legacy Academy lesson cards into the Hub.

Run from the repository root:
    python -m scripts.import_academy_legacy
Set ACADEMY_DB_PATH to a persistent database path before production use.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from modules.academy_intelligence import initialize, import_legacy_lessons


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="data/academy.json")
    parser.add_argument("--database", default=None)
    args = parser.parse_args()
    source = Path(args.source)
    if not source.is_file():
        parser.error(f"Academy source file does not exist: {source}")
    initialize(args.database)
    count = import_legacy_lessons(args.database, source)
    print(f"Indexed {count} legacy Academy lessons into {args.database or 'ACADEMY_DB_PATH/default database'}.")
    print("Source JSON was read-only and left unchanged.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
