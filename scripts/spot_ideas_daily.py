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
    return 0


if __name__ == "__main__":
    sys.exit(main())
