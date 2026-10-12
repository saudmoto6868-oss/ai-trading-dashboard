"""Headless Telegram alerts for GitHub Actions (free, runs without the dashboard open).

    python -m modules.tg_cron            # scan, rank, send the best fresh alerts
    python -m modules.tg_cron --dry      # scan + print what WOULD be sent (no Telegram call)

Env: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID (GitHub Secrets). Optional: TG_TFS="1h,1d"  TG_TOP=3  TG_MIN_Q=60  TG_MIN_STARS=4.
What was already sent is remembered in .tg_sent.json (kept between runs by actions/cache). The log prints counts only."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from config import CRYPTO_SYMBOLS
from modules import telegram_alerts as T
from modules.arabic import scan_entry
from modules.market_cache import fetch_frames, get_klines
from modules.scorer import CONTEXT_TFS, scan_symbol

STATE = Path(os.environ.get("TG_STATE", ".tg_sent.json"))


def load_state() -> dict:
    try:
        return {k: tuple(v) for k, v in json.loads(STATE.read_text()).items()}
    except Exception:
        return {}


def save_state(sent: dict, keep_s: float = 24 * 3600):
    import time
    now = time.time()
    STATE.write_text(json.dumps({k: list(v) for k, v in sent.items() if now - v[0] < keep_s}))


def scan_alerts(symbols, tfs, min_stars: int) -> tuple[list[dict], list[str]]:
    out, errs = [], []
    for tf in tfs:
        try:
            frames, _ = fetch_frames(symbols, [tf] + CONTEXT_TFS.get(tf, []))
        except Exception as ex:
            errs.append(f"{tf}: {type(ex).__name__}")
            continue
        for sym in symbols:
            try:
                r = scan_symbol(sym, frames[sym], tf)
                if r["direction"] not in ("bullish", "bearish") or r["score"] < min_stars:
                    continue
                e = scan_entry(r, get_klines(sym, tf, 300))
                if not e:
                    continue
                e["q"], e["qwhy"] = T.quality(r, e)
                out.append(e)
            except Exception as ex:   # a coin with a short history etc. - skipped
                if "not enough" not in str(ex):
                    errs.append(f"{sym} {tf}: {type(ex).__name__}")
    return out, errs


def main(argv=None) -> int:
    dry = "--dry" in (argv if argv is not None else sys.argv[1:])
    tfs = [t.strip() for t in os.environ.get("TG_TFS", "1h,1d").split(",") if t.strip()]
    top, min_q, min_stars = int(os.environ.get("TG_TOP", "3")), int(os.environ.get("TG_MIN_Q", "60")), int(os.environ.get("TG_MIN_STARS", "4"))
    alerts, errs = scan_alerts(list(CRYPTO_SYMBOLS), tfs, min_stars)
    print(f"scanned {len(CRYPTO_SYMBOLS)} symbols x {tfs}: {len(alerts)} alerts, {len(errs)} errors")
    for e in errs[:5]:
        print("  err:", e)
    best = T.select(alerts, top, min_q)
    if dry:
        for a in best:
            print(T.fmt(a), "\n---")
        return 0
    sent = load_state()
    n, err = T.dispatch(best, sent, top, min_q)
    save_state(sent)
    print(f"sent {n} of {len(best)} candidate(s)" + (f"; Telegram error: {err}" if err else ""))
    return 1 if err else 0


if __name__ == "__main__":
    sys.exit(main())
