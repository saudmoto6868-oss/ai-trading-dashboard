"""Daily spot ideas to Telegram (owner 2026-11-06): build the ideas desk, draw the board, send the picture + the Arabic text.
GitHub Actions (.github/workflows/spot-ideas.yml) or by hand: python scripts/spot_ideas_daily.py [--no-image]
Needs TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID. Read-only: no orders, nothing written to the repo."""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import requests

from modules import spot_board, spot_ideas
from modules.telegram_alerts import creds, send


def send_photo(path: str, caption: str = "") -> str | None:
    tok, chat = creds()
    if not tok or not chat:
        return "no TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID"
    with open(path, "rb") as f:
        r = requests.post(f"https://api.telegram.org/bot{tok}/sendPhoto", data={"chat_id": chat, "caption": caption[:1000]}, files={"photo": f}, timeout=60)
    return None if r.status_code == 200 else f"HTTP {r.status_code}"


def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    r = spot_ideas.desk()
    txt = spot_ideas.telegram_text(r)
    print(txt)
    if "--no-image" not in argv:
        try:
            from modules.spot_dash import to_png
            png = to_png(spot_board.render(r), "spot_ideas.png")
            print("photo:", send_photo(png, "🧠 مكتب أفكار السبوت - صورة اليوم") or "sent")
        except Exception as e:
            print(f"photo skipped: {type(e).__name__}: {e}")
    print("text:", send(txt[:4000]) or "sent")
    for asset in [x.strip().upper() for x in os.environ.get("SPOT_BRAIN_SYMS", "GOLD,BTC").split(",") if x.strip()]:
        try:
            from modules import spot_brain, spot_brain_view, spot_ideas as SI
            from modules.spot_dash import to_png
            cls, name = next(((c, n) for a, c, n in SI.UNIVERSE if a == asset), ("crypto", asset))
            br = spot_brain.run(asset, cls, name)
            bt = spot_brain.text_ar(br)
            print(bt)
            print("diag flow:", {k: (v.get("ok"), v.get("why")) for k, v in (br.get("raw_flow") or {}).items() if isinstance(v, dict)})
            print("diag cot:", (br.get("raw_cot") or {}).get("ok"), (br.get("raw_cot") or {}).get("why"))
            if "--no-image" not in argv:
                print("brain photo:", send_photo(to_png(spot_brain_view.render(br), f"brain_{asset}.png"), f"🧠 العقل المدبر - {name}") or "sent")
            print("brain text:", send(bt[:4000]) or "sent")
        except Exception as e:
            print(f"brain {asset} skipped: {type(e).__name__}: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
