"""Trade Classes -> Telegram (GitHub Actions, next to modules/tg_cron.py; runs without the dashboard open).

    python -m modules.tclass_cron          # scan, send the strongest fresh bounce trades
    python -m modules.tclass_cron --dry    # print what WOULD be sent (no Telegram call)

Env: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID. Optional: TC_STYLES="Day Trade,Swing" (the job runs every 30 min, too slow for Scalp)
TC_MIN=4 (strength out of 6) TC_TOP=3 TC_SYMBOLS="BTC-USDT,ETH-USDT" (default: config.CRYPTO_SYMBOLS) TC_TARGET=0 (points, 0 = auto).
Only trades with price AT the zone now are sent. Already-sent trades are remembered in .tc_sent.json (actions/cache); a trade is
re-sent only after 12 h. The log prints counts only."""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

STATE = Path(os.environ.get("TC_STATE", ".tc_sent.json"))
RESEND_S = 12 * 3600


def key(c: dict) -> str:
    return f"{c['symbol']}|{c['direction']}|{c['style']}|{c['level']:.6g}"


def load_state() -> dict:
    try:
        return json.loads(STATE.read_text())
    except Exception:
        return {}


def save_state(sent: dict):
    now = time.time()
    STATE.write_text(json.dumps({k: v for k, v in sent.items() if now - v < 3 * 86400}))


def pick(cands: list[dict], sent: dict, min_score: int, top: int, now: float | None = None) -> list[dict]:
    now = now or time.time()
    ok = [c for c in cands if c["now"] and c["score"] >= min_score and now - sent.get(key(c), 0) > RESEND_S]
    ok.sort(key=lambda c: (-c["score"], -c["rr"]))
    return ok[:max(1, top)]


def main(argv=None) -> int:
    from modules import tclass as TC
    from modules import telegram_alerts as T
    from modules.market_cache import get_klines
    dry = "--dry" in (argv if argv is not None else sys.argv[1:])
    styles = [s.strip() for s in os.environ.get("TC_STYLES", "Day Trade,Swing").split(",") if s.strip() in TC.STYLES]
    if os.environ.get("TC_SYMBOLS"):
        syms = [s.strip() for s in os.environ["TC_SYMBOLS"].split(",") if s.strip()]
    else:
        from config import CRYPTO_SYMBOLS
        syms = list(CRYPTO_SYMBOLS)
    min_s, top, tgt = int(os.environ.get("TC_MIN", "4")), int(os.environ.get("TC_TOP", "3")), float(os.environ.get("TC_TARGET", "0"))
    cands, errs = [], 0
    for st in styles:
        for s in syms:
            try:
                cands += TC.scan(s, st, get_klines, target_pts=tgt)
            except Exception:
                errs += 1
    sent = load_state()
    best = pick(cands, sent, min_s, top)
    print(f"trade classes: {len(syms)} symbols x {styles}: {len(cands)} candidates, {len(best)} to send, {errs} errors")
    if dry:
        for c in best:
            print(TC.fmt(c), "\n---")
        return 0
    n, err = 0, None
    for c in best:
        err = T.send(TC.fmt(c))
        if err:
            break
        sent[key(c)] = time.time(); n += 1
    save_state(sent)
    print(f"sent {n}" + (f"; Telegram error: {err}" if err else ""))
    return 1 if err else 0


if __name__ == "__main__":
    sys.exit(main())
