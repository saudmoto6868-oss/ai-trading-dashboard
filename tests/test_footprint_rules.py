"""Footprint reading rules (diagonal / stacked imbalance, POC, unfinished extremes) run in node on the real function text from workspace_app.html.
Rules are descriptions of one bar, never predictions. Skipped when node is not installed."""
import json
import os
import re
import shutil
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = open(os.path.join(ROOT, "modules", "workspace_app.html"), encoding="utf-8").read()


def _fn_text():
    i = H.index("fpAn(m, rows, step, OF){")
    j = H.index("\n  paintFp(c, py, dec, i0, i1, PB){", i)
    return H[i:j].rstrip().rstrip(",")


def _run(cases):
    node = shutil.which("node")
    if not node:
        return None
    js = "const O = {" + _fn_text() + "};\nconst cases = " + json.dumps(cases) + ";\n" + """
const out = cases.map(c => { const rows = new Map(c.rows.map(([k, b, s]) => [k, {b, s}])); const m = {b: c.rows.reduce((a, r) => a + r[1], 0), s: c.rows.reduce((a, r) => a + r[2], 0)};
  const an = O.fpAn(m, rows, 1, c.of); return {imb: [...an.imb.entries()], runs: an.runs, poc: an.poc, hiUnf: an.hiUnf, loUnf: an.loUnf}; });
console.log(JSON.stringify(out));"""
    r = subprocess.run([node, "-e", js], capture_output=True)
    assert r.returncode == 0, r.stderr.decode("utf-8", "replace")
    return json.loads(r.stdout.decode("utf-8"))


OF = {"fpImb": 3, "fpStk": 3, "fpMin": 10, "fpDiag": 1}   # the defaults of the page


def test_rules():
    # rows (price row, buy volume, sell volume), ascending
    stack = [(10, 5, 4), (11, 100, 8), (12, 100, 8), (13, 100, 8), (14, 100, 8)]   # buyers at 11..14 against the sellers one row below: 4 imbalanced rows in a row
    same_row = [(10, 50, 40), (11, 9, 100), (12, 50, 45)]                           # selling at 11 against the buyers one row ABOVE (12: 50 buy, no: 100 > 3*50 is false)
    thin = [(20, 1, 0), (21, 0, 1)]
    res = _run([{"rows": stack, "of": OF}, {"rows": same_row, "of": OF}, {"rows": thin, "of": dict(OF, fpMin=100)},
                {"rows": [(1, 10, 1), (2, 10, 1)], "of": dict(OF, fpStk=3)}, {"rows": stack, "of": dict(OF, fpImb=30)}])
    if res is None:
        return
    a, b, c, d, e = res
    assert [k for k, s in a["imb"] if s == "b"] == [11, 12, 13, 14]                  # 10 has no big buyer; the lowest row is not stacked with them
    assert a["runs"] == [{"side": "b", "k0": 11, "k1": 14}] and a["poc"] in (11, 12, 13, 14)
    assert b["runs"] == []                                                             # isolated imbalances do not make a stack
    assert c["imb"] == [] and c["runs"] == []                                          # the minimum-volume filter removes thin rows
    assert d["runs"] == []                                                             # 2 rows are fewer than the 3 asked for
    assert e["imb"] == [] and e["runs"] == []                                          # a higher ratio finds nothing
    assert a["hiUnf"] is True and a["loUnf"] is True                                   # both sides traded at both extremes of the first sample


def test_wired_into_the_painter():
    for k in ("this.fpAn(m, rows, step, OF)", "nPOC", "fpStack", "fpNaked", "fpAuc", "fpDelta", "an.runs.forEach", "fpMode", "fpRow", "step0*(OF.fpRow", "market/history-trades", "this.fpFill", "mm.part = true", "fpAdd(r, quiet)"):
        assert k in H, k


def test_linked_panels_and_forward_test():
    for k in ("flowLevels(ft)", "Ws.flowLevels = sym", "function flowTag(sym, p, tol)", "flowTag(opts && opts.sym", "flowTag(panel.state.sym, r.p", "flowTag(panel.state.sym, e.p",   # footprint levels shown in the DOM, tape and limit tracker
              "Ws.flowConf = sym", "const FlowTest = ", "Ws.ftPop = anchor", "l.kind === \"stack\"", "n >= 100 && t > 3 && m1 > 0 && m2 > 0",
              "this.fpSave = () =>", "this.fpLoad = () =>", "ch._fpLoadedMax && +r.id <= ch._fpLoadedMax", "svMax && +x.tradeId <= svMax"):   # the footprint survives a refresh and is shared by the tabs of one browser          # confluence v1 and its forward test with our own evidence gate
        assert k in H, k


if __name__ == "__main__":
    test_rules()
    test_wired_into_the_painter()
    test_linked_panels_and_forward_test()
    print("ok footprint rules")
