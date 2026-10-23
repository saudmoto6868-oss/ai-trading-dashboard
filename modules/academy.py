"""Academy tab data (owner 2026-10-23): lessons written from the team's research (first batch: Grok's conversation of 2026-10-22), each with a status
and a review verdict so nothing is shown as evidence before it is checked. Lessons live in data/academy.json; this module loads and validates them."""
from __future__ import annotations

import json
from pathlib import Path

PATH = Path(__file__).resolve().parent.parent / "data" / "academy.json"
STATUS = {"draft": ("مسودة", "#f0b90b"), "reviewed": ("اتراجع", "#2dd4bf"), "approved": ("معتمد من المالك", "#0ecb81")}
VERDICT = {"consistent": ("متوافق مع مشروعنا", "#2dd4bf"), "hypothesis": ("فرضية للاختبار", "#f0b90b"),
           "unverified": ("غير متحقق منه", "#8d97a5"), "contradicted": ("بيتعارض مع بياناتنا", "#f6465d")}
REQUIRED = ("id", "topic", "title", "source", "status", "verdict", "verdict_note", "summary")


def load(path: Path = PATH) -> list:
    """-> lessons; a lesson missing a required field or with an unknown status / verdict is dropped (never shown half-formed)."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    out, seen = [], set()
    for ls in data.get("lessons", []):
        if not all(ls.get(k) for k in REQUIRED) or ls["status"] not in STATUS or ls["verdict"] not in VERDICT or ls["id"] in seen:
            continue
        seen.add(ls["id"])
        out.append({**ls, "points": list(ls.get("points", [])), "caveats": list(ls.get("caveats", [])),
                    "sources": [u for u in ls.get("sources", []) if str(u).startswith("https://")], "uses": list(ls.get("uses", []))})
    return out


def summary(lessons: list) -> dict:
    by_status, by_verdict, by_topic = {}, {}, {}
    for ls in lessons:
        by_status[ls["status"]] = by_status.get(ls["status"], 0) + 1
        by_verdict[ls["verdict"]] = by_verdict.get(ls["verdict"], 0) + 1
        by_topic[ls["topic"]] = by_topic.get(ls["topic"], 0) + 1
    return {"n": len(lessons), "status": by_status, "verdict": by_verdict, "topic": by_topic}


def search(lessons: list, q: str = "", topic: str = "", verdict: str = "") -> list:
    q = (q or "").strip().lower()
    return [ls for ls in lessons
            if (not topic or ls["topic"] == topic) and (not verdict or ls["verdict"] == verdict)
            and (not q or q in " ".join([ls["title"], ls["summary"], ls["topic"], " ".join(ls["points"])]).lower())]
