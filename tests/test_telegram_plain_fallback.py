"""telegram_alerts.send: when Telegram rejects the HTML ("can't parse entities"), the alert is resent once as plain text
instead of being lost (2026-11-25: raw "n<30" dropped every brain setup alert). Mock only, no network.
Run: PYTHONPATH=. python3 tests/test_telegram_plain_fallback.py"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules import telegram_alerts as T  # noqa: E402


class R:
    def __init__(self, code, desc=""):
        self.status_code, self._d = code, desc

    def json(self):
        return {"description": self._d}


calls = []


def post(url, json=None, timeout=None):
    calls.append(json)
    if "parse_mode" in json and "<30" in json["text"]:
        return R(400, "Bad Request: can't parse entities: Unsupported start tag \"30\" at byte offset 9")
    return R(200)


T.requests.post = post
assert T.send("<b>x</b> n<30 &amp; y", "T", "C") is None and len(calls) == 2, calls
assert "parse_mode" not in calls[1] and calls[1]["text"] == "x n<30 & y", calls[1]
calls.clear()
assert T.send("<b>ok</b>", "T", "C") is None and len(calls) == 1, "valid HTML goes out once, unchanged"
T.requests.post = lambda url, json=None, timeout=None: R(403, "Forbidden: the bot can't send messages to the bot")
e = T.send("<b>x</b>", "T", "C")
assert e.startswith("HTTP 403") and "TELEGRAM_CHAT_ID is a bot id" in e, e
print("ok plain-text fallback")
print("ALL OK")
