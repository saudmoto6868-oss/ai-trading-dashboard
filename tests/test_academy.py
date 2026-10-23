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



def test_schools_and_helpers():
    sc = A.schools()
    if not sc:                         # docs/academy only exists once Grok's folder is on the branch
        return
    assert len(sc) >= 9 and all(s["visual"] and s["title"] for s in sc)
    t, b = A.badges("![x](https://img.shields.io/badge/الدور-Primary_مرشح-22c55e) نص")
    assert b == [("الدور: Primary مرشح", "#22c55e")] and "shields" not in t
    t, ch = A.chains("a\n```mermaid\nflowchart LR\n  A[\"x\"] --> B[\"y z\"]\n```\nb")
    assert ch == [["x", "y z"]] and "mermaid" not in t



def test_learning_path_and_art():
    from modules import academy_art as ART
    lp = A.learning_path()
    ls, lv = lp["lessons"], {x["id"] for x in lp["levels"]}
    assert len(ls) >= 17 and len(lv) == 5
    assert [x["level"] for x in ls] == sorted(x["level"] for x in ls)                 # teaching order: level 1 first
    for x in ls:
        assert x["refs"] and x["steps"] and x["quiz"] and x["bull"] and x["bear"], x["id"]
        for a in x["arts"]:
            for side in ("bull", "bear"):
                s = ART.art(a, side)
                assert "<style" not in s, "a <style> inside the SVG makes the page hide the element"; assert s.startswith("<svg") and s.endswith("</svg>") and "NaN" not in s and "Infinity" not in s and "nan" not in s.replace("an", ""), (x["id"], a, side)
    ids = [x["id"] for x in ls]
    assert len(ids) == len(set(ids))


def test_path_validation_drops_bad():
    good = {"id": "a", "level": 1, "title": "t", "grade": "قوي", "grade_note": "n", "arts": ["candles"], "idea": "i", "steps": ["s"], "refs": ["r"], "quiz": [{"q": "q", "opts": ["x", "y"], "a": 1}]}
    bad = [dict(good, id="b", arts=["nope"]), dict(good, id="c", quiz=[{"q": "q", "opts": ["x", "y"], "a": 5}]), dict(good, id="d", level=9), dict(good, id="e", grade="؟")]
    p = os.path.join(tempfile.mkdtemp(), "p.json")
    open(p, "w", encoding="utf-8").write(json.dumps({"levels": [{"id": 1, "title": "L"}], "lessons": [good] + bad}))
    assert [x["id"] for x in A.learning_path(p)["lessons"]] == ["a"]


def test_refs_loader():
    R = A.refs()
    assert len(R["sources"]) >= 6 and len(R["glossary"]) >= 12
    assert any(x["id"] == "chatgpt" for x in R["sources"])                       # the missing ChatGPT conversation is tracked, not forgotten
    assert all(u.startswith("https://") for c in R["claims"] for u in c["urls"])
    p = os.path.join(tempfile.mkdtemp(), "r.json")
    open(p, "w", encoding="utf-8").write(json.dumps({"sources": [{"id": "a", "title": "t"}], "glossary": [{"their": "x"}], "claims": [{"id": "c", "claim": "k", "verdict": "bogus"}, {"id": "d", "claim": "k", "verdict": "idea", "urls": ["http://no", "https://ok"]}]}))
    R2 = A.refs(p)
    assert R2["sources"] == [] and R2["glossary"] == [] and [c["id"] for c in R2["claims"]] == ["d"] and R2["claims"][0]["urls"] == ["https://ok"]


if __name__ == "__main__":
    test_shipped_and_filters(); test_bad_lessons_dropped(); test_schools_and_helpers(); test_learning_path_and_art(); test_path_validation_drops_bad(); test_refs_loader(); print("ok academy")
