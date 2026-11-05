"""modules.workspace._build_id: a short hex commit id (git, or .git/HEAD when git is missing) or '' - never an exception, never anything but hex (it goes into the page)."""
import re, subprocess
from unittest import mock
from modules import workspace as w

v = w._build_id()
assert v == "" or re.fullmatch(r"[0-9a-f]{6,40}", v), v
with mock.patch.object(subprocess, "run", side_effect=FileNotFoundError("no git")):   # no git binary: falls back to .git/HEAD
    v2 = w._build_id()
assert v2 == "" or re.fullmatch(r"[0-9a-f]{6,40}", v2), v2
with mock.patch.object(subprocess, "run", return_value=mock.Mock(returncode=0, stdout="<script>alert(1)</script>\n")):   # junk output is refused
    v3 = w._build_id()
assert "<" not in v3, v3
print("ok build id:", repr(v), repr(v2), repr(v3))
