"""XPiX poller: owner-only filter, offset save/load, and one run with a mocked Telegram API."""
import json
import os
import sys
import tempfile
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts import xpix_poll as P  # noqa: E402

OWNER = "123"
assert P.owner_text({"message": {"chat": {"id": 123}, "text": " hi "}}, OWNER) == "hi"
assert P.owner_text({"message": {"chat": {"id": 999}, "text": "hi"}}, OWNER) is None   # other chat dropped
assert P.owner_text({"message": {"chat": {"id": 123}, "text": "  "}}, OWNER) is None

tmp = tempfile.mkdtemp()
os.environ["XPIX_STATE"] = os.path.join(tmp, "state.json")
assert P.load_offset() == 0
P.save_offset(42)
assert P.load_offset() == 42 and json.loads(open(os.environ["XPIX_STATE"]).read())["offset"] == 42

# one run: 3 updates (owner, stranger, owner) -> 2 replies, offset ends at last update id
os.environ.update(XPIX_BOT_TOKEN="t", XPIX_OWNER_CHAT_ID=OWNER, GITHUB_SHA="abcdef123")
updates = [
    {"update_id": 43, "message": {"chat": {"id": 123}, "text": "/status"}},
    {"update_id": 44, "message": {"chat": {"id": 999}, "text": "spam"}},
    {"update_id": 45, "message": {"chat": {"id": 123}, "text": "/status"}},
]
sent = []


def fake_post(url, json=None, timeout=None, **kw):   # noqa: A002
    resp = mock.Mock()
    if url.endswith("/getUpdates"):
        resp.json.return_value = {"result": updates}
    else:
        sent.append(json["text"])
    resp.raise_for_status.return_value = None
    return resp


with mock.patch.object(P.requests, "post", side_effect=fake_post):
    assert P.run() == 0
assert len(sent) == 2 and sent[0].startswith("XPiX poller شغال") and P.load_offset() == 45
print("test_xpix_poll OK")
