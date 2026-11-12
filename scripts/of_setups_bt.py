#!/usr/bin/env python3
"""Run the Order Flow Desk setups backtest on real trades (Binance spot aggTrades from data.binance.vision: free, no key).

  python3 scripts/of_setups_bt.py --symbol BTCUSDT --days 30 --bar 300 [--cost 0.1] [--out data/of_setups_bt.csv]

Downloads one zip per day (~20-80 MB each for BTC), builds footprint bars, finds the 5 setups (modules/of_setups_bt.py),
simulates them and prints the table. Run it on a machine with internet (the Mac, a CI runner); the build sandbox cannot.
Under 30 trades per setup = not evidence. Costs default to 0.1 R per trade.
"""
import argparse
import io
import os
import sys
import zipfile
from datetime import date, timedelta

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules import of_setups_bt as B  # noqa: E402

URL = "https://data.binance.vision/data/spot/daily/aggTrades/{s}/{s}-aggTrades-{d}.zip"


def day_trades(sym: str, d: date) -> pd.DataFrame:
    r = requests.get(URL.format(s=sym, d=d.isoformat()), timeout=120)
    r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    df = pd.read_csv(z.open(z.namelist()[0]), header=None, usecols=[1, 2, 5, 6], names=["p", "q", "t", "buyer_maker"])
    for c in ("p", "q", "t"):         # some files carry a header row: drop anything that is not a number
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["p", "q", "t"]).astype({"t": "int64"})
    if df.t.iloc[0] > 1e14:          # newer files are in microseconds
        df["t"] = df.t // 1000
    df["buyer_maker"] = df.buyer_maker.astype(str).str.lower().eq("true")
    return df


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default="BTCUSDT"); ap.add_argument("--days", type=int, default=30); ap.add_argument("--bar", type=int, default=300)
    ap.add_argument("--cost", type=float, default=0.1); ap.add_argument("--out", default="")
    a = ap.parse_args(argv)
    end = date.today() - timedelta(days=1)
    bars = []
    for k in range(a.days, 0, -1):
        d = end - timedelta(days=k - 1)
        try:
            bars.append(B.bars(day_trades(a.symbol, d), a.bar))
            print("ok", d, file=sys.stderr)
        except Exception as e:
            print("skip", d, type(e).__name__, file=sys.stderr)
    if not bars:
        print("no data downloaded"); return 1
    df = pd.concat(bars, ignore_index=True)
    tr = B.simulate(df, B.signals(df), cost_r=a.cost)
    rep = B.report(tr)
    print(f"{a.symbol} {a.days} days, {a.bar}s bars, {len(df)} bars, cost {a.cost} R per trade")
    print(rep.to_string(index=False))
    if a.out:
        tr.to_csv(a.out, index=False); print("trades ->", a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
