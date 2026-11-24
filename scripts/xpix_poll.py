"""XPiX poller for GitHub Actions (every 5 min). Reads new Telegram messages, answers the owner chat only.

Env: XPIX_BOT_TOKEN, XPIX_OWNER_CHAT_ID (GitHub Secrets), ANTHROPIC_API_KEY (optional, for free-text answers),
XPIX_MODEL (default claude-haiku-5-5), XPIX_STATE (offset file, restored by actions/cache).
Read + reply only: no orders, no repo writes, no pushes. Messages from any other chat are dropped.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import requests

TG = "https://api.telegram.org/bot{token}/{method}"
ANTHROPIC = "https://api.anthropic.com/v1/messages"
MAX_PER_RUN = 10          # daily-cost cap per run; the rest waits for the next run
SYSTEM = ("You are the XPiX assistant for the owner. Reply briefly in Egyptian Arabic. "
          "You cannot place trades, give personal financial advice, or change the repo.")


def state_path() -> Path:
    return Path(os.environ.get("XPIX_STATE", "data/xpix_poll_state.json"))


def load_offset() -> int:
    try:
        return int(json.loads(state_path().read_text(encoding="utf-8"))["offset"])
    except Exception:
        return 0


def save_offset(value: int) -> None:
    p = state_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"offset": value}), encoding="utf-8")


def owner_text(update: dict, owner: str) -> str | None:
    """Text of a message from the owner chat, else None (other chats are ignored)."""
    m = update.get("message") or {}
    if str((m.get("chat") or {}).get("id", "")) != str(owner):
        return None
    t = (m.get("text") or "").strip()
    return t or None


def answer(text: str) -> str:
    if text == "/status":
        return "XPiX poller شغال. commit: " + os.environ.get("GITHUB_SHA", "")[:7]
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        return "ANTHROPIC_API_KEY مش موجود، بس /status شغال."
    r = requests.post(ANTHROPIC, timeout=60, headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                                                      "content-type": "application/json"},
                      json={"model": os.environ.get("XPIX_MODEL", "claude-haiku-5-5"), "max_tokens": 400,
                            "system": SYSTEM, "messages": [{"role": "user", "content": text}]})
    r.raise_for_status()
    out = "".join(b.get("text", "") for b in r.json().get("content", []) if b.get("type") == "text")
    return out or "(رد فاضي)"


def send(token: str, chat: str, text: str) -> None:
    requests.post(TG.format(token=token, method="sendMessage"), timeout=20,
                  json={"chat_id": chat, "text": text[:4000]}).raise_for_status()


def diagnose(token: str) -> None:
    """Log which bot this token is and whether updates are waiting (token itself is never printed)."""
    try:
        me = requests.get(TG.format(token=token, method="getMe"), timeout=10).json().get("result", {})
        hook = requests.get(TG.format(token=token, method="getWebhookInfo"), timeout=10).json().get("result", {})
        print(f"bot @{me.get('username')} webhook={bool(hook.get('url'))} pending={hook.get('pending_update_count')}")
    except Exception as exc:
        print(f"diagnose failed: {type(exc).__name__}")


def run() -> int:
    token = os.environ.get("XPIX_BOT_TOKEN", "")
    owner = os.environ.get("XPIX_OWNER_CHAT_ID", "")
    if not token or not owner:
        sys.exit("missing XPIX_BOT_TOKEN / XPIX_OWNER_CHAT_ID")
    diagnose(token)
    off = load_offset()
    params = {"timeout": 0, "limit": 100}
    if off:
        params["offset"] = off + 1
    r = requests.post(TG.format(token=token, method="getUpdates"), json=params, timeout=30)
    r.raise_for_status()
    done = 0
    for upd in r.json().get("result", []):
        if done >= MAX_PER_RUN:
            break
        text = owner_text(upd, owner)
        if text:
            try:
                reply = answer(text)
            except Exception as exc:   # one bad call must not block the queue
                reply = f"خطأ في الرد: {type(exc).__name__}"
            send(token, owner, reply)
            done += 1
        save_offset(upd["update_id"])   # consumed (owner or not), so it is never answered twice
    print(f"handled {done} owner message(s)")
    return 0


if __name__ == "__main__":
    sys.exit(run())
