"""HUB TAB 1 - TRUTH COURT: of everything the lab tried, how much could be luck?

The lab tests hundreds of rules. Test enough rules and some "win" by chance. This tab counts every trial (N), computes how big
the best t-stat must be to beat N coin-flips, and runs each row through hub_core.promote(). Nothing here is estimated by an
AI: it reads data/strategy_lab.json and does arithmetic. Identity: amber, glyph "§".
Method (Bailey & Lopez de Prado; Harvey-Liu-Zhu): Bonferroni and Benjamini-Hochberg on two-sided normal p-values from the t-stats,
and E[max of N null t-stats] ~ (1-g)*Z(1-1/N) + g*Z(1-1/(N*e)), g = Euler-Mascheroni."""
from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import NormalDist

from modules import hub_core

SPEC = hub_core.TabSpec(
    id="truth", title="Truth Court", glyph="§", accent="#E0A526",
    purpose="Counts every lab trial and says which results survive luck, costs and the OOS half.",
)
LAB_FILE = Path(__file__).resolve().parent.parent / "data" / "strategy_lab.json"
COST_R = 0.10   # same planning cost as kpi.py / strategy_lab.py
_Z = NormalDist()
_G = 0.5772156649


def _p_two_sided(t: float) -> float:
    return 2.0 * (1.0 - _Z.cdf(abs(t)))


def expected_max_null_t(n_trials: int) -> float:
    """Expected largest |t| from n_trials pure-noise rules (one-sided approximation)."""
    if n_trials < 2:
        return 0.0
    return (1 - _G) * _Z.inv_cdf(1 - 1 / n_trials) + _G * _Z.inv_cdf(1 - 1 / (n_trials * math.e))


bonferroni_t = hub_core.bonferroni_t   # one shared implementation (hub_core), kept under this name for the tab and its tests


def benjamini_hochberg(pvals: list, q: float = 0.05) -> list:
    """Booleans: which hypotheses survive BH at false-discovery rate q (same order as pvals)."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    cut = -1
    for rank, i in enumerate(order, 1):
        if pvals[i] <= q * rank / m:
            cut = rank
    keep = [False] * m
    for rank, i in enumerate(order, 1):
        if rank <= cut:
            keep[i] = True
    return keep


OTHER_TABS = ("plateau", "regime", "decay", "consensus")   # tabs whose published n_trials add to the honest N (the trail tests nothing)


def judge(rows: list, min_n: int = hub_core.MIN_N, extra_trials: int = 0) -> dict:
    """rows = strategy_lab.json 'rows'. extra_trials = hypotheses the OTHER hub tabs looked at (hub_core.total_trials): they raise the bar too.
    Returns the court's file: counts, thresholds, per-row verdicts (testable rows only)."""
    testable = [r for r in rows if r.get("t") is not None and (r.get("n") or 0) > 0]
    n_trials = len(testable)
    pvals = [_p_two_sided(r["t"]) for r in testable]
    bh = benjamini_hochberg(pvals) if testable else []
    n_all = n_trials + max(0, int(extra_trials))
    bonf = bonferroni_t(n_all)
    exp_max = expected_max_null_t(n_all)
    verdicts = []
    for r, p, keep in zip(testable, pvals, bh):
        net = r.get("net", (r.get("avgR") or 0.0) - COST_R)
        cand = {"n": r.get("n"), "t": r.get("t"), "is_avgR": r.get("is_avgR"), "oos_avgR": r.get("oos_avgR"), "net_avgR": net}
        ok, why = hub_core.promote(cand, min_n=min_n)
        survives_luck = abs(r["t"]) >= bonf
        verdicts.append({
            "key": r.get("key"), "school": r.get("school"), "tf": r.get("tf"), "side": r.get("side"),
            "n": r.get("n"), "avgR": r.get("avgR"), "net": round(net, 3), "t": r.get("t"), "p": round(p, 5),
            "bh": keep, "beats_bonferroni": survives_luck, "promote": ok and survives_luck,
            "why_not": why + ([] if survives_luck else [f"|t| < Bonferroni {bonf:.2f} for N={n_all}"]),
        })
    best = max(testable, key=lambda r: abs(r["t"]), default=None)
    positives = [v for v in verdicts if v["t"] > 0]
    best_pos = max(positives, key=lambda v: v["t"], default=None)
    return {
        "n_rows": len(rows), "n_trials": n_trials, "n_total": n_all, "n_untestable": len(rows) - n_trials,
        "bonferroni_t": round(bonf, 2), "expected_max_null_t": round(exp_max, 2),
        "best_abs_t": None if best is None else best["t"],
        "best_positive": best_pos,
        "n_bh_survivors": sum(1 for v in verdicts if v["bh"] and v["t"] > 0),
        "n_promotable": sum(1 for v in verdicts if v["promote"]),
        "luck_verdict": _luck_verdict(best_pos, exp_max),
        "verdicts": verdicts,
    }


def _luck_verdict(best_pos: dict | None, exp_max: float) -> str:
    if best_pos is None:
        return "no positive rule among the testable trials"
    if best_pos["t"] <= exp_max:
        return f"best positive t={best_pos['t']:.2f} is at or below what pure luck gives from this many trials (~{exp_max:.2f}): not evidence"
    return f"best positive t={best_pos['t']:.2f} beats the luck level (~{exp_max:.2f}): still needs the OOS half and a second window"


def run(lab_path: Path | None = None, root: Path | None = None) -> dict | None:
    """Read the lab file, judge it, publish the snapshot for the other tabs. None if the lab file is missing."""
    try:
        data = json.loads((lab_path or LAB_FILE).read_text())
    except (FileNotFoundError, ValueError, OSError):
        return None
    res = judge(data.get("rows", []), extra_trials=hub_core.total_trials(list(OTHER_TABS), root))
    keep = [v for v in res["verdicts"] if v["promote"] or (v["bh"] and v["t"] > 0)][:50]
    hub_core.publish(SPEC.id, keep, res["n_trials"],
                     extra={k: res[k] for k in ("bonferroni_t", "expected_max_null_t", "n_promotable", "luck_verdict", "n_total")}, root=root)
    return res


def render(st, L=lambda s: s) -> None:
    """Streamlit page body. st is passed in so this module imports without streamlit."""
    from modules import hub_ui
    res = run()
    hub_ui.show(st, hub_ui.header(SPEC, L(SPEC.purpose), L(SPEC.title), L))
    if res is None:
        st.info(L("No lab file yet (data/strategy_lab.json). Run the lab first."))
        return
    others = res["n_total"] - res["n_trials"]
    best = res["best_positive"]
    hub_ui.show(st, hub_ui.cards([
        ("N", L("Trials counted"), res["n_total"], L("{a} lab + {b} from other tabs").format(a=res["n_trials"], b=others), "", None),
        ("t", L("t needed after N looks"), res["bonferroni_t"], L("Bonferroni, two-sided 5%"), "", None),
        ("~", L("t pure luck reaches"), res["expected_max_null_t"], L("expected best of N noise rules"), "", None),
        ("OK", L("Rules passing every gate"), res["n_promotable"], L("n, t, IS+OOS, costs, Bonferroni"), "up" if res["n_promotable"] else "warn", None)]) +
        hub_ui.ruler([(L("luck"), res["expected_max_null_t"], "#8B8D98"), (L("hurdle"), hub_core.MIN_T, "#F0B90B"),
                      (L("Bonferroni"), res["bonferroni_t"], SPEC.accent), (L("best rule"), None if best is None else best["t"], "#0ECB81" if best and best["promote"] else "#F6465D")],
                     lo=0, hi=max(5.0, (best["t"] if best else 0) + 1, res["bonferroni_t"] + 1), title=L("Where the best rule sits against luck and the hurdles")))
    (st.success if res["n_promotable"] else st.warning)(hub_ui.tr(L, res["luck_verdict"]))
    st.caption(L("{n} lab rows have no t-stat and are not counted as evidence. Costs: {c}R per trade (planning estimate, not measured).").format(n=res["n_untestable"], c=COST_R))
    rows = sorted(res["verdicts"], key=lambda v: -v["t"])[:25]
    st.dataframe([{k: v[k] for k in ("key", "school", "tf", "side", "n", "avgR", "net", "t", "bh", "promote")} | {"why_not": "; ".join(v["why_not"][:2])}
                  for v in rows], use_container_width=True, hide_index=True)
