"""Automatic copy of the ONLINE spot ledger to the owner's Mac (owner 2026-11-06).

launchd runs this every hour (and at login); it only works when the last good copy is older than SPOT_BACKUP_HOURS
(default 48). A new copy = a new folder with ledger.json + every invoice file + an Excel workbook. The OLD folders are
deleted only after the new one is complete and verified (SPOT_BACKUP_KEEP newest folders kept, default 1).
Offline / GitHub unreachable -> nothing is deleted, it tries again next hour.
Config: ~/.xpix_spot_backup.env (chmod 600), lines KEY=value:
  SPOT_GH_TOKEN=...   SPOT_GH_REPO=owner/xpix-spot-data   SPOT_BACKUP_DIR=~/XPiX-Spot-Backup
  SPOT_BACKUP_HOURS=48   SPOT_BACKUP_KEEP=1
Run by hand: python3 tools/spot_backup/spot_backup.py --now"""
from __future__ import annotations

import json
import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
CONF = Path.home() / ".xpix_spot_backup.env"


def read_conf(path: Path = CONF) -> None:
    if path.exists():
        for line in path.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"'))


def due(base: Path, hours: float) -> bool:
    stamp = base / ".last_ok"
    return not stamp.exists() or time.time() - stamp.stat().st_mtime >= hours * 3600


def backup(store, base: Path, keep: int = 1, log=print) -> Path:
    """Pull everything into a new folder, verify, then prune older folders. Raises on any failure (nothing deleted)."""
    from modules import spot_core as C
    base.mkdir(parents=True, exist_ok=True)
    d = store.load()
    if d is None:
        raise RuntimeError("online ledger not found")
    name = "XPiX-Spot-" + datetime.now().strftime("%Y-%m-%d_%H%M")
    tmp = base / (name + ".partial")
    shutil.rmtree(tmp, ignore_errors=True)
    (tmp / "files").mkdir(parents=True)
    (tmp / "ledger.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf8")
    want = sorted({f for t in d.get("txs", []) for f in t.get("files", [])})
    for f in want:
        b = store.get_file(f)
        if b is None:
            raise RuntimeError(f"file missing online: {f}")
        (tmp / "files" / f).write_bytes(b)
    (tmp / "spot_ledger.xlsx").write_bytes(C.to_excel(d.get("txs", []), C.positions(d.get("txs", [])), {}, None, d.get("settings", {}).get("custom_fields")))
    # verify before anything old is touched
    back = json.loads((tmp / "ledger.json").read_text(encoding="utf8"))
    assert len(back.get("txs", [])) == len(d.get("txs", [])) and all((tmp / "files" / f).exists() for f in want)
    final = base / name
    tmp.rename(final)
    olds = sorted([p for p in base.iterdir() if p.is_dir() and p.name.startswith("XPiX-Spot-") and not p.name.endswith(".partial") and p != final])
    for p in olds[:max(0, len(olds) - (keep - 1))]:
        shutil.rmtree(p, ignore_errors=True)
    (base / ".last_ok").write_text(final.name)
    log(f"backup ok: {final} ({len(d.get('txs', []))} records, {len(want)} files)")
    return final


def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    read_conf()
    base = Path(os.path.expanduser(os.environ.get("SPOT_BACKUP_DIR", "~/XPiX-Spot-Backup")))
    hours = float(os.environ.get("SPOT_BACKUP_HOURS", "48"))
    keep = max(1, int(os.environ.get("SPOT_BACKUP_KEEP", "1")))
    if "--now" not in argv and not due(base, hours):
        return 0
    from modules.spot_store import get_store
    st = get_store()
    if st.kind != "github":
        print("SPOT_GH_TOKEN / SPOT_GH_REPO missing in ~/.xpix_spot_backup.env")
        return 1
    try:
        backup(st, base, keep)
    except Exception as e:
        print(f"backup skipped ({type(e).__name__}: {e}); old copies kept")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
