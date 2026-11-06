"""Spot alerts checked on the server (GitHub Actions, every 30 min with the Telegram alerts job), page open or not.

Reads the ONLINE ledger (spot_store github backend: SPOT_GH_TOKEN + SPOT_GH_REPO), checks the active buy / sell / stop
alerts against live prices, sends each hit ONCE to Telegram (TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID), marks it fired and
saves. With no online store configured it does nothing (the local disk of a CI runner is empty). Run: python -m modules.spot_alerts_cron"""
from __future__ import annotations

import sys
from datetime import datetime, timezone

from modules import spot_core as C


def run(store=None, prices=None, send=None, log=print) -> int:
    from modules.spot_store import get_store
    st = store or get_store()
    if st.kind != "github" and store is None:
        log("spot alerts: no online store (SPOT_GH_TOKEN / SPOT_GH_REPO not set) - skipped")
        return 0
    d = st.load() or {}
    alerts = d.get("alerts", [])
    if not any(a.get("active") for a in alerts):
        log("spot alerts: none active")
        return 0
    if prices is None:
        from modules.spot_query import _live
        prices, _ = _live()
    if send is None:
        from modules.telegram_alerts import send
    sent = 0
    for h in C.check_alerts(alerts, prices):
        err = send("XPiX Spot · " + C.alert_text(h, True))
        if err:
            log(f"spot alerts: telegram error {err}")
            break
        for a in alerts:
            if a["id"] == h["id"]:
                a["active"], a["fired_at"] = False, datetime.now(timezone.utc).isoformat(timespec="minutes")
        sent += 1
    if sent:
        st.save(d, f"spot: {sent} alert(s) fired")
    log(f"spot alerts: {sent} sent")
    return sent


if __name__ == "__main__":
    try:
        run()
    except Exception as e:   # never fail the whole alerts job because of the spot desk
        print(f"spot alerts: {type(e).__name__}: {e}")
    sys.exit(0)
