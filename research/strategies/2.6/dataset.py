"""Task 3 (CLAUDE_TASKS.md): dataset contract + manifest for 2.6 research data (IMPLEMENTATION_PLAN.md section 5).

The bars themselves are validated by event_study.load_bars (ISO-8601 with offset, finite, positive, OHLC
integrity, strictly increasing = no duplicates, >= 100 bars). This module adds what a reproducible run needs:
file checksum, UTC date range, gap scan against the timeframe (weekend closes reported apart), explicit cost
metadata and provenance. A futures proxy (GC=F) can never be labelled as spot XAUUSD.

Usage: python3 dataset.py FILE.csv --provider "Broker X" --symbol XAUUSD --timeframe 5m --spread 0.30 [--write]
No data is downloaded or committed by this module.
"""
import argparse
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

from event_study import _parse_timestamp, load_bars

TF_SECONDS = {"1m": 60, "5m": 300, "15m": 900, "30m": 1800, "1h": 3600, "4h": 14400, "1d": 86400}
FUTURES_PROXIES = {"GC=F", "GC", "MGC", "SI=F"}
ASSET_CLASSES = {"spot_metal", "fx", "futures_proxy", "index_cfd", "crypto"}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _weekend_close(a, b):
    """True when the gap a -> b spans the FX / metals weekend close (Fri >= 20:00 UTC to Sun / Mon open)."""
    return a.weekday() == 4 and a.hour >= 20 and (b - a).total_seconds() <= 3.5 * 86400 and b.weekday() in (6, 0)


def scan_gaps(bars, timeframe):
    """Gaps larger than one timeframe step, split into weekend closes and other (holidays, outages, missing data)."""
    step = TF_SECONDS[timeframe]
    ts = [_parse_timestamp(b.dt).astimezone(timezone.utc) for b in bars]
    weekend, other = 0, []
    for a, b in zip(ts, ts[1:]):
        d = (b - a).total_seconds()
        if d % step and timeframe != "1d":
            other.append({"after": a.isoformat(), "seconds": d, "note": "off-grid"})
        elif d > step:
            if _weekend_close(a, b):
                weekend += 1
            else:
                other.append({"after": a.isoformat(), "seconds": d})
    return {"weekend_closes": weekend, "other_gaps": len(other), "largest_other": sorted(other, key=lambda g: -g["seconds"])[:10]}


def _cost(name, value):
    if value is None or not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be a finite number >= 0 (price units per filled event)")
    return float(value)


def build_manifest(path, provider, symbol, timeframe, asset_class="spot_metal", spread=None, commission=0.0,
                   slippage=0.0, price_precision=None, contract_size=None, source_timezone="as in file", downloaded=None):
    if timeframe not in TF_SECONDS:
        raise ValueError(f"timeframe must be one of {sorted(TF_SECONDS)}")
    if asset_class not in ASSET_CLASSES:
        raise ValueError(f"asset_class must be one of {sorted(ASSET_CLASSES)}")
    if not provider or not str(provider).strip():
        raise ValueError("provider / broker is required (provenance)")
    if symbol.upper() in FUTURES_PROXIES and asset_class != "futures_proxy":
        raise ValueError(f"{symbol} is a futures proxy, not spot: use asset_class='futures_proxy'")
    if asset_class == "futures_proxy" and symbol.upper() == "XAUUSD":
        raise ValueError("XAUUSD is spot; a futures proxy needs its own symbol (e.g. GC=F)")
    costs = {"spread": _cost("spread", spread), "commission": _cost("commission", commission), "slippage": _cost("slippage", slippage)}
    bars = load_bars(path)
    first = _parse_timestamp(bars[0].dt).astimezone(timezone.utc); last = _parse_timestamp(bars[-1].dt).astimezone(timezone.utc)
    return {
        "file": Path(path).name, "sha256": sha256(path), "bars": len(bars),
        "provider": str(provider).strip(), "symbol": symbol, "asset_class": asset_class, "timeframe": timeframe,
        "source_timezone": source_timezone, "utc_first": first.isoformat(), "utc_last": last.isoformat(),
        "price_precision": price_precision, "contract_size": contract_size,
        "costs": costs, "cost_per_event": round(sum(costs.values()), 10), "cost_units": "price units per filled event",
        "gaps": scan_gaps(bars, timeframe), "duplicates": 0,
        "downloaded": downloaded, "manifest_built": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def verify(path, manifest):
    """Raise unless the file still matches its manifest (same bytes); returns the bars."""
    got = sha256(path)
    if got != manifest["sha256"]:
        raise ValueError(f"{path}: checksum {got[:12]} != manifest {manifest['sha256'][:12]} (file changed)")
    return load_bars(path)


def main(argv=None):
    p = argparse.ArgumentParser(description="Validate a 2.6 OHLC CSV and print / write its manifest")
    p.add_argument("csv"); p.add_argument("--provider", required=True); p.add_argument("--symbol", required=True)
    p.add_argument("--timeframe", required=True, choices=sorted(TF_SECONDS)); p.add_argument("--asset-class", default="spot_metal")
    p.add_argument("--spread", type=float, required=True); p.add_argument("--commission", type=float, default=0.0)
    p.add_argument("--slippage", type=float, default=0.0); p.add_argument("--precision", type=int)
    p.add_argument("--contract-size", type=float); p.add_argument("--tz", default="as in file"); p.add_argument("--downloaded")
    p.add_argument("--write", action="store_true", help="write FILE.manifest.json next to the CSV")
    a = p.parse_args(argv)
    m = build_manifest(a.csv, a.provider, a.symbol, a.timeframe, a.asset_class, a.spread, a.commission, a.slippage,
                       a.precision, a.contract_size, a.tz, a.downloaded)
    text = json.dumps(m, indent=2)
    if a.write:
        Path(a.csv + ".manifest.json").write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
