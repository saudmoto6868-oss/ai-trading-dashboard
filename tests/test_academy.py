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


def test_ordered_schools():
    sc = A.ordered_schools()
    if not sc:
        return
    assert [x["id"] for x in sc][:9] == A.SCHOOL_ORDER and [x["pos"] for x in sc][:9] == list(range(1, 10))
    assert all(x["why"] and x["arts"] for x in sc[:9])
    from modules import academy_art as ART
    assert all(a in ART.ART for x in sc[:9] for a in x["arts"])
    byid = {x["id"]: x for x in sc}
    assert byid["trend"]["evidence"].startswith("## 1)") and byid["trend"]["examples"]
    assert byid["orderflow"]["review"] and byid["sessions"]["review"]                  # our review sits next to the school it is about
    assert A.sections("a\n## X\nb\n## Y\nc") == {"": "a", "X": "b", "Y": "c"}


def test_deep_lessons():
    d = A.deep()
    assert set(d) == set(A.SCHOOL_ORDER)                                               # all nine schools have a full lesson
    for sid, x in d.items():
        assert len(x["parts"]) >= 3 and len(x["exercises"]) >= 3 and x["faq"] and x["glossary"], sid
        assert sum(len(p["b"]) for p in x["parts"]) > 900, sid                          # a real explanation, not a stub
        assert len(x["bull_story"]) > 80 and len(x["bear_story"]) > 30 and len(x["platform"]) >= 3, sid


# ---- one language at a time (owner 2026-10-23): English mode shows no Arabic, Arabic mode keeps the Arabic content exactly as it was --------------------------------------------------

import contextlib, re  # noqa: E402
AR_RE = re.compile("[؀-ۿ]")


@contextlib.contextmanager
def lang_as(code):
    from modules import i18n
    old = i18n.lang
    i18n.lang = lambda: code
    try:
        yield
    finally:
        i18n.lang = old


def _strings(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for k, v in o.items():
            yield from _strings(k); yield from _strings(v)
    elif isinstance(o, (list, tuple)):
        for v in o:
            yield from _strings(v)


def _snap(code):
    with lang_as(code):
        return {"path": A.learning_path(), "deep": A.deep(), "refs": A.refs(), "lessons": A.load(), "schools": A.ordered_schools(), "lab": A.lab_note()}


def test_english_mode_has_no_arabic():
    from modules import academy_art as ART
    en = _snap("en")
    for name, part in en.items():
        bad = [s for s in _strings(part) if AR_RE.search(s)]
        assert not bad, (name, bad[:3])
    with lang_as("en"):
        for a in ART.ART:
            for side in ("bull", "bear"):
                svg = ART.art(a, side)
                assert not AR_RE.search(svg), (a, side, AR_RE.findall(svg)[:5])
        assert "Strong" in {x["grade_label"] for x in A.learning_path()["lessons"]}
        assert A.status_label("draft")[0] == "Draft" and A.verdict_label("contradicted")[0] == "Contradicts our data" and A.claim_verdict_label("partial")[0] == "Partial"
        assert A.origin_label("primary") == "Primary source" and A.origin_label("Grok") == "Grok"


def test_english_matches_arabic_shape_and_honesty():
    en, ar = _snap("en"), _snap("ar")
    assert any(AR_RE.search(x["title"]) for x in ar["path"]["lessons"]) and any(AR_RE.search(x["what"]) for x in ar["deep"].values())   # Arabic mode keeps the Arabic
    assert [x["id"] for x in en["path"]["lessons"]] == [x["id"] for x in ar["path"]["lessons"]] and len(en["path"]["levels"]) == len(ar["path"]["levels"]) == 5
    for e_, a_ in zip(en["path"]["lessons"], ar["path"]["lessons"]):
        assert (e_["level"], e_["grade"], e_["arts"], e_["school"]) == (a_["level"], A.GRADE_EN[a_["grade"]], a_["arts"], a_["school"]), e_["id"]
        for k in ("steps", "mistakes", "platform", "refs", "quiz"):
            assert len(e_[k]) == len(a_[k]), (e_["id"], k)
        assert [(q["a"], len(q["opts"])) for q in e_["quiz"]] == [(q["a"], len(q["opts"])) for q in a_["quiz"]], e_["id"]
        assert e_["bull"] and e_["bear"] and e_["grade_note"] and e_["idea"]
    assert set(en["deep"]) == set(ar["deep"]) == set(A.SCHOOL_ORDER)                                               # all nine schools have a full English deep lesson
    for sid, x in en["deep"].items():
        y = ar["deep"][sid]
        for k in ("parts", "exercises", "faq", "platform", "mistakes", "glossary"):
            assert len(x[k]) == len(y[k]), (sid, k)
        assert sum(len(p["b"]) for p in x["parts"]) > 900 and len(x["bull_story"]) > 80 and len(x["bear_story"]) > 30, sid
    assert [len(en["refs"][k]) for k in ("sources", "glossary", "claims")] == [len(ar["refs"][k]) for k in ("sources", "glossary", "claims")]
    assert {c["id"]: c["verdict"] for c in en["refs"]["claims"]} == {c["id"]: c["verdict"] for c in ar["refs"]["claims"]}      # a claim keeps its verdict: preliminary stays preliminary
    assert [(l["id"], l["status"], l["verdict"]) for l in en["lessons"]] == [(l["id"], l["status"], l["verdict"]) for l in ar["lessons"]]
    assert [(x["id"], x["pos"]) for x in en["schools"]] == [(x["id"], x["pos"]) for x in ar["schools"]]
    assert all(x["visual"] and x["why"] and x["examples"] and x["evidence"] for x in en["schools"][:9])
    assert [bool(x["review"]) for x in en["schools"]] == [bool(x["review"]) for x in ar["schools"]]
    assert "candidate" in en["lab"] and "not evidence" in en["lab"]
    assert not [s for s in list(_strings(en["deep"]) ) if re.search(r"risk-free|will make (you )?(money|profit)|guaranteed (profit|return)|sure profit", s, re.I)]   # no promise of profit


if __name__ == "__main__":
    test_english_mode_has_no_arabic(); test_english_matches_arabic_shape_and_honesty(); print("ok academy english")


if __name__ == "__main__":
    test_shipped_and_filters(); test_bad_lessons_dropped(); test_schools_and_helpers(); test_learning_path_and_art(); test_path_validation_drops_bad(); test_refs_loader(); test_ordered_schools(); test_deep_lessons(); print("ok academy")
