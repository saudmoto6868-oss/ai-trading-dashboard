"""Claude Code PostToolUse hook: one line per tool call in docs/ACTIVITY_LOG_AUTO.md.

Logs the tool name, the file path or a short, redacted command head, and the outcome.
Never logs file contents, tool output, or anything that looks like a secret.
Stays silent on any error so it can never block the session.
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG = Path(__file__).resolve().parent.parent / "docs" / "ACTIVITY_LOG_AUTO.md"
SECRET = re.compile(r"(?i)(token|key|secret|password|passwd|auth|bearer)\S*[=:]\s*\S+|gh[pousr]_\w{10,}|sk-\w{10,}|AIza\w{10,}")


def main() -> None:
    try:
        data = json.load(sys.stdin)
        tool = str(data.get("tool_name", "?"))
        inp = data.get("tool_input") or {}
        target = inp.get("file_path") or inp.get("path") or inp.get("pattern") or ""
        if not target and "command" in inp:
            target = " ".join(str(inp["command"]).split()[:4])
        target = SECRET.sub("[redacted]", str(target))[:120].replace("|", "/")
        resp = data.get("tool_response")
        failed = isinstance(resp, dict) and bool(resp.get("is_error") or resp.get("error"))
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        if not LOG.exists():
            LOG.write_text("# سجل تلقائي (hook)\n\n| الوقت (UTC) | الأداة | الهدف | النتيجة |\n|---|---|---|---|\n", encoding="utf-8")
        with LOG.open("a", encoding="utf-8") as f:
            f.write(f"| {now} | {tool} | {target} | {'فشل' if failed else 'نجح'} |\n")
    except Exception:
        pass


if __name__ == "__main__":
    main()
