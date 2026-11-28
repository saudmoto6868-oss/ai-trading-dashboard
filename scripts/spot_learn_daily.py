"""Daily Spot learning job (owner 2026-11-15): run the brain on the markets, log verdicts + setups, score matured rows,
send an Arabic report to Telegram. GitHub Actions: .github/workflows/spot-learn.yml. By hand: python scripts/spot_learn_daily.py

Env (all optional):
  SPOT_LEARN_SYMS   comma list of assets to run the brain on (default: the whole spot universe)
  SPOT_LEARN_LOG    path of the JSONL log (default data/spot/brain_log.jsonl; CI restores it from the Actions cache)
  TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID  (same secrets as spot-ideas; never printed)
Read-only towards markets: no orders, no weight changes. Exit code 0 even if a market fails (failures go in the report)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from modules import spot_learn as L
from modules import spot_learn_job as J


def main(argv=None) -> int:
    from modules import spot_brain, spot_data, spot_ideas
    from modules.telegram_alerts import send

    path = Path(os.environ.get("SPOT_LEARN_LOG") or L.LOG)
    syms = [x.strip().upper() for x in os.environ.get("SPOT_LEARN_SYMS", "").split(",") if x.strip()]
    universe = [u for u in spot_ideas.UNIVERSE if not syms or u[0] in syms]
    brains, failed = [], []
    for asset, cls, name in universe:
        try:
            brains.append(spot_brain.run(asset, cls, name))
        except Exception as e:                           # one market down must not stop the others
            failed.append(f"{asset}: {type(e).__name__}")
    # Bars for every asset in the log (old rows of markets not run today still get scored), daily closes, 400 bars.
    assets = {b.get("asset") for b in brains} | {r.get("asset") for r in L.load(path)}
    bars = {}
    for a in sorted(x for x in assets if x):
        try:
            bars[a] = J.bars_from_df(spot_data.candles(spot_data.history_symbol(a), "1d", 400))
        except Exception as e:
            failed.append(f"bars {a}: {type(e).__name__}")
    out = J.cycle(brains, path, bars)
    text = out["text"]
    if failed:
        text += "\n⚠️ ما اشتغلش: " + ", ".join(failed)[:300]
    print(text)
    print("send:", send(text[:4000]) or "sent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
