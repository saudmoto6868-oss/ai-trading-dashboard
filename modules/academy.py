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


# ---- the school curricula written by Grok (docs/academy) ------------------------------------------------------------------------------------

import re

ROOT = Path(__file__).resolve().parent.parent / "docs" / "academy"
ICON = {"levels": "📏", "trend": "📈", "sessions": "🕒", "smc": "🧱", "elliott": "🌊", "gann": "🔭", "harmonic": "🦋", "orderflow": "💧", "meanrev": "↔️"}
LAB_NOTE = ("في معمل المشروع لحد دلوقتي ولا كاشف عدّى البوابة الإحصائية (n ≥ 100، t > 3، صافي بعد التكلفة موجب، النصفين موجبين). "
            "كلمة «مرشح» أو primary_candidate في المحتوى معناها قيد الاختبار، مش دليل.")


def _read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except OSError:
        return ""


def schools(root: Path = ROOT) -> list:
    """-> [{id, n, icon, title, visual, ai, curriculum}] from docs/academy/visual/NN-*.md (+ ai/NN-*.json.md and the long curriculum file NN-*.md)."""
    out = []
    for f in sorted((root / "visual").glob("[0-9][0-9]-*.md")):
        n, sid = f.name[:2], f.stem[3:]
        vis = _read(f)
        title = next((ln.lstrip("# ").strip() for ln in vis.splitlines() if ln.startswith("# ")), sid)
        ai = next(iter(sorted((root / "ai").glob(f"{n}-*.md"))), None)
        cur = next(iter(sorted(root.glob(f"{n}-*.md"))), None)
        out.append({"id": sid, "n": n, "icon": ICON.get(sid, "📘"), "title": title, "visual": vis, "ai": _read(ai) if ai else "", "curriculum": _read(cur) if cur else ""})
    return out


def badges(md: str) -> tuple:
    """Split shields.io badge images off a lesson: -> (text without them, [(label, #hex)]). The labels carry the school's role and lab status."""
    out = [(m.group(1).replace("_", " ").replace("-", ": ", 1), "#" + m.group(2)) for m in re.finditer(r"!\[[^\]]*\]\(https://img\.shields\.io/badge/([^)]*?)-([0-9a-fA-F]{6})\)", md)]
    return re.sub(r"!\[[^\]]*\]\(https://img\.shields\.io/badge/[^)]*\)\s*", "", md), out


def chains(md: str) -> tuple:
    """Turn ```mermaid flowcharts into step lists (Streamlit cannot draw mermaid): -> (text with the diagrams removed, [[step, ...], ...])."""
    found = []

    def take(m):
        steps = []
        for lab in re.findall(r'\[\s*"?([^\]"]+?)"?\s*\]', m.group(1)):
            if lab not in steps:
                steps.append(lab.strip())
        if steps:
            found.append(steps)
        return ""
    return re.sub(r"```mermaid\n(.*?)```", take, md, flags=re.S), found


def evidence(root: Path = ROOT) -> str:
    return _read(root / "BACKTEST_EVIDENCE.md")


def examples(root: Path = ROOT) -> str:
    return _read(root / "EXAMPLES_MULTI.md")


# ---- the learning path (data/academy_path.json): ordered levels, lessons with a diagram, steps, bullish / bearish setups, quiz ---------------------

PATH = Path(__file__).resolve().parent.parent / "data" / "academy_path.json"
GRADE = {"قوي": "#0ecb81", "متوسط": "#f0b90b", "ضعيف": "#f6465d", "تعليمي": "#8d97a5"}
LESSON_REQ = ("id", "level", "title", "grade", "grade_note", "arts", "idea", "steps", "refs", "quiz")


def learning_path(path: Path = PATH) -> dict:
    """-> {'levels': [...], 'lessons': [...]} in teaching order. A lesson missing a field, with an unknown diagram, a bad level, or a quiz whose answer index is
    out of range is dropped, so the page never shows a half-built lesson."""
    from modules import academy_art as ART
    try:
        d = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"levels": [], "lessons": []}
    levels = [lv for lv in d.get("levels", []) if lv.get("id") and lv.get("title")]
    ids, out, seen = {lv["id"] for lv in levels}, [], set()
    for ls in d.get("lessons", []):
        if not all(ls.get(k) for k in LESSON_REQ) or ls["level"] not in ids or ls["grade"] not in GRADE or ls["id"] in seen:
            continue
        if any(a not in ART.ART for a in ls["arts"]):
            continue
        if any(not (isinstance(q.get("opts"), list) and len(q["opts"]) >= 2 and isinstance(q.get("a"), int) and 0 <= q["a"] < len(q["opts"]) and q.get("q")) for q in ls["quiz"]):
            continue
        seen.add(ls["id"])
        out.append({**ls, "mistakes": list(ls.get("mistakes", [])), "platform": list(ls.get("platform", [])), "bull": ls.get("bull", ""), "bear": ls.get("bear", ""), "school": ls.get("school", "")})
    out.sort(key=lambda x: (x["level"], [y["id"] for y in d["lessons"]].index(x["id"])))
    return {"levels": levels, "lessons": out}
