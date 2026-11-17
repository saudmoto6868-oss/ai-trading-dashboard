"""Mr X can reuse one lesson from the canonical Academy without duplicating its curriculum."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.ai_page import _academy_lessons, _lesson_context


def test_ai_page_reads_the_existing_academy_path():
    lessons = _academy_lessons()
    assert len(lessons) >= 17
    assert len({x["id"] for x in lessons}) == len(lessons)


def test_lesson_context_is_bounded_and_keeps_evidence_caveat():
    lesson = {
        "id": "lesson-1",
        "title": "Existing lesson",
        "school": "orderflow",
        "grade": "ضعيف",
        "idea": "x" * 1000,
        "grade_note": "Evidence note",
        "refs": ["ref 1", "ref 2", "ref 3", "ref 4"],
        "steps": ["a" * 300, "step 2", "step 3", "step 4"],
    }
    ctx = _lesson_context(lesson)
    assert ctx["id"] == "lesson-1"
    assert len(ctx["concept"]) == 420
    assert ctx["evidence_note"] == "Evidence note"
    assert ctx["references"] == ["ref 1", "ref 2", "ref 3"]
    assert len(ctx["key_steps"]) == 3
    assert all(len(x) <= 120 for x in ctx["key_steps"])
    assert "not empirical validation" in ctx["caveat"]
    assert "raw_candles" not in ctx
