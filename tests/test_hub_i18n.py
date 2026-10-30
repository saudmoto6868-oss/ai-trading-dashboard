"""Every text the Research Hub shows through L() has an Arabic entry, templates keep their placeholders, and the computed verdicts translate
(plain script). A missing entry would silently stay English, so this guards it."""
import sys, os, ast, glob, re, tempfile, json
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules import i18n, hub_ui, hub_core, hub_truth, hub_trail, hub_consensus, hub_decay, hub_funnel
AR = i18n.AR
ar = lambda s: AR.get(s, s)

def calls():
    for f in sorted(glob.glob("modules/hub_*.py")):
        for n in ast.walk(ast.parse(open(f, encoding="utf-8").read())):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "L" and n.args:
                yield f, n.lineno, n.args[0]

# 1) no f-string goes through L() (an interpolated string can never match a dictionary key); static and two-way strings must be translated
missing, fstr = [], []
def consts(a):
    if isinstance(a, ast.Constant) and isinstance(a.value, str): return [a.value]
    if isinstance(a, ast.IfExp): return consts(a.body) + consts(a.orelse)
    return None
for f, ln, a in calls():
    if isinstance(a, ast.JoinedStr): fstr.append((f, ln))
    cs = consts(a)
    if cs:
        missing += [(f, ln, c) for c in cs if c not in AR]
assert not fstr, fstr
assert not missing, missing

# 2) tab names, purposes, funnel stage names, chip/diagram texts
for tid, title, *_ in hub_ui.TABS:
    assert title in AR and AR[title] != title or title == "Bonferroni", title
for mod in (hub_truth, hub_ui):
    pass
import importlib
for name in ("truth", "plateau", "regime", "trail", "decay", "consensus", "funnel"):
    spec = importlib.import_module(f"modules.hub_{name}").SPEC
    assert spec.title in AR and spec.purpose in AR, name
for st in hub_funnel.STAGE_NAMES: assert st in AR, st
for k in ("reads", "not run yet", "How the tabs help each other (arrows = reads the published snapshot)", "nobody reads the regime yet", "Research Hub"): assert k in AR, k

# 3) placeholders: each Arabic template carries exactly the same {fields} as its English key
for k, v in AR.items():
    fk, fv = sorted(re.findall(r"\{(\w*)\}", k)), sorted(re.findall(r"\{(\w*)\}", v))
    if fk or fv:
        assert fk == fv, (k, v)

# 4) computed verdicts: every pattern has an Arabic template, and tr() fills the numbers in
for rx, key in hub_ui._PATTERNS:
    assert key in AR, key
en = lambda s: s
L_ar = lambda s: ar(s)
assert hub_ui.tr(en, "no decay signal (this is not proof of an edge)") == "no decay signal (this is not proof of an edge)"   # English stays English
assert hub_ui.tr(L_ar, "CUSUM 10.6 > 4.0 and rolling t -4.08 < -2") == "CUSUM 10.6 > 4.0 وt المتحرك -4.08 < -2"
assert hub_ui.tr(L_ar, "CUSUM 10.6 > 4.0") == "CUSUM 10.6 > 4.0"
assert hub_ui.tr(L_ar, "8 live trades < 30: no verdict") == "8 صفقة حية < 30: مفيش حكم"
assert hub_ui.tr(L_ar, "rolling t -inf < -1").startswith("t المتحرك -inf")
assert "3.24" in hub_ui.tr(L_ar, "best positive t=3.24 beats the luck level (~3.13): still needs the OOS half and a second window") and "~3.13" in hub_ui.tr(L_ar, "best positive t=3.24 beats the luck level (~3.13): still needs the OOS half and a second window")
assert hub_ui.tr(L_ar, "something we never wrote") == "something we never wrote"
# the real producers' sentences all match a pattern (otherwise they would show English in an Arabic page)
produced = []
produced += [hub_truth.judge([])["luck_verdict"],
             hub_truth._luck_verdict(None, 3.0), hub_truth._luck_verdict({"t": 2.0}, 3.1), hub_truth._luck_verdict({"t": 3.9}, 3.1)]
produced += [hub_trail.analyse([], publish=False)["summary"]["verdict"]]
produced += [hub_trail.analyse([{"t": 1, "dir": "bullish", "entry": 100, "stop": 98, "tp1": 104, "out": "tp", "r": 2.0, "t_out": 2}], publish=False)["summary"]["verdict"]]
big = [{"t": i, "dir": "bullish", "entry": 100, "stop": 98, "tp1": 104, "out": "tp", "r": 2.0, "t_out": i + 1} for i in range(1, 121)]
produced += [hub_trail.analyse(big, publish=False)["summary"]["verdict"]]
produced += [hub_consensus.confluence_verdict({})["verdict"], hub_consensus.confluence_verdict({"a": {"n": 500, "avgR": -0.1}})["verdict"],
             hub_consensus.confluence_verdict({"4 families": {"n": 500, "avgR": 0.25}})["verdict"]]
for xs in ([1.0] * 10, [-1.0] * 60, [0.6, -1.0, 0.6, 0.6, -1.0, 0.6] * 8 + [0.6] * 6, [0.8, -0.4] * 40 + [-0.9, 0.3] * 10, [-1.0] * 15 + [1.0] * 60):
    produced.append(hub_decay.status(xs, 0.25 if len(xs) == 100 else 0.0)["why"])
for text in produced:
    assert any(rx.match(text) for rx, _k in hub_ui._PATTERNS), f"no translation pattern for: {text}"

# 5) overview cards and header translate end to end
tmp = Path(tempfile.mkdtemp())
hub_core.publish("truth", [], 564, extra={"bonferroni_t": 3.92, "expected_max_null_t": 3.09, "n_promotable": 0}, root=tmp)
hub_core.publish("funnel", [], 0, extra={"tested": 1175, "survived": 0, "kill_rate": 100.0, "biggest_kill": "Gross edge"}, root=tmp)
cs = {c[1]: c for c in hub_ui.overview_cards(tmp, L_ar)}
assert "محكمة الحقيقة" in cs and cs["محكمة الحقيقة"][3] == "المطلوب t ≥ 3.92 · الحظ ~3.09 · عدّى 0"
assert cs["قمع القتل"][2] == "100.0% ماتت" and cs["مراقبة التآكل"][3] == "لسه ما اشتغلش"
h = hub_ui.header(hub_truth.SPEC, ar(hub_truth.SPEC.purpose), ar(hub_truth.SPEC.title), L_ar)
assert "محكمة الحقيقة" in h and ">بيقرا<" not in h            # Truth Court reads nothing: no 'reads' chip
assert "بيقرا" in hub_ui.header(hub_trail.SPEC, "x", "y", L_ar) and "محكمة الحقيقة" in hub_ui.header(hub_trail.SPEC, "x", "y", L_ar)
assert "إزاي التابات بتساعد بعض" in hub_ui.flow(L=L_ar) and "رادار الأنظمة" in hub_ui.flow(L=L_ar)
assert "مكرر (نفس الفكرة مرتين)" in hub_ui.graph([("a", "b", 0.9, "REDUNDANT")], L=L_ar)
print("test_hub_i18n: all passed")
