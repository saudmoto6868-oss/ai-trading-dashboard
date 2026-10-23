"""modules/academy.py: the shipped lessons are valid, and bad lessons are dropped."""
import json, os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules import academy as A  # noqa: E402


def test_shipped_and_filters():
    ls = A.load()
    assert len(ls) >= 4 and all(l["status"] == "draft" for l in ls)            # nothing is approved before the owner says so
    assert any(l["verdict"] == "contradicted" for l in ls)                       # the claim check is there
    s = A.summary(ls); assert s["n"] == len(ls) and sum(s["topic"].values()) == len(ls)
    assert A.search(ls, topic="Sessions") and not A.search(ls, q="zzzz")
    assert all(u.startswith("https://") for l in ls for u in l["sources"])


def test_bad_lessons_dropped():
    good = {"id": "a", "topic": "t", "title": "x", "source": "s", "status": "draft", "verdict": "consistent", "verdict_note": "n", "summary": "m"}
    bad = [dict(good, id="b", status="nope"), dict(good, id="c", verdict="nope"), {k: v for k, v in good.items() if k != "summary"}, dict(good)]
    p = os.path.join(tempfile.mkdtemp(), "x.json"); open(p, "w", encoding="utf-8").write(json.dumps({"lessons": [good] + bad}))
    assert [l["id"] for l in A.load(p)] == ["a"]
    assert A.load(os.path.join(tempfile.mkdtemp(), "missing.json")) == []


if __name__ == "__main__":
    test_shipped_and_filters(); test_bad_lessons_dropped(); print("ok academy")


def test_schools_and_helpers():
    sc = A.schools()
    if not sc:                         # docs/academy only exists once Grok's folder is on the branch
        return
    assert len(sc) >= 9 and all(s["visual"] and s["title"] for s in sc)
    t, b = A.badges("![x](https://img.shields.io/badge/الدور-Primary_مرشح-22c55e) نص")
    assert b == [("الدور: Primary مرشح", "#22c55e")] and "shields" not in t
    t, ch = A.chains("a\n```mermaid\nflowchart LR\n  A[\"x\"] --> B[\"y z\"]\n```\nb")
    assert ch == [["x", "y z"]] and "mermaid" not in t


if __name__ == "__main__":
    test_schools_and_helpers()
