"""HUB TAB 6 - CONSENSUS MAP: when several detectors agree, is that several confirmations or one idea counted twice?

From the lab's own conflict table (bars where two detectors fire together, and how often they point opposite ways) it works out:
  agreement   rho = 1 - 2*opposite/together     +1 = always the same way, 0 = independent coin flips, -1 = always opposed
  significance  z-test of 'opposite' against 50% (what independent detectors would give), Bonferroni over every pair tested
  class       REDUNDANT (rho > +0.10 and significant), OPPOSED (rho < -0.10 and significant), else INDEPENDENT
  effective votes   n^2 / sum(rho_ij) for a chosen set of detectors (negative rho clipped to 0, unmeasured pairs counted as 0
                    and reported): 6 redundant detectors can be worth ~1 vote.
  proven votes      how many of them the Truth Court has actually promoted (today usually none).
It also reads the lab's confluence table (does more families agreeing raise net R?). It claims no edge: it says how much
independent information a 'consensus' really holds. Identity: cyan, glyph "✦". Pure Python; render() takes st."""
from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import NormalDist

from modules import hub_core

SPEC = hub_core.TabSpec(
    id="consensus", title="Consensus Map", glyph="✦", accent="#18B6C9",
    purpose="Measures how much independent information a multi-detector consensus holds, and how many of its votes are proven.",
    consumes=("truth",),
)
LAB_FILE = Path(__file__).resolve().parent.parent / "data" / "strategy_lab.json"
EFFECT_MIN = 0.10      # |rho| below this is called independent however many bars there are
COST_R = 0.10          # same planning cost as the lab; confluence avgR rows are gross
MIN_N = hub_core.MIN_N
_Z = NormalDist()


def pair_stats(conflicts: list, alpha: float = 0.05) -> list:
    """One dict per detector pair with rho, z, p, Bonferroni-significance and a class. Rows with together < 1 are skipped."""
    rows = [c for c in conflicts if (c.get("together") or 0) >= 1]
    k = len(rows)
    out = []
    for c in rows:
        n, opp = int(c["together"]), int(c["opposite"])
        rho = 1 - 2 * opp / n
        z = (opp - 0.5 * n) / (0.5 * math.sqrt(n))        # opposite rate against the 50% independent detectors give
        p = 2 * (1 - _Z.cdf(abs(z)))
        sig = p < alpha / max(1, k)
        cls = "REDUNDANT" if (rho > EFFECT_MIN and sig) else "OPPOSED" if (rho < -EFFECT_MIN and sig) else "INDEPENDENT"
        out.append({"a": c["a"], "b": c["b"], "together": n, "opposite": opp, "rho": round(rho, 3), "z": round(z, 2),
                    "p": p, "significant": sig, "class": cls})
    return out


def effective_votes(names: list, pairs: list) -> dict:
    """n^2 / sum(rho_ij) over the chosen detectors. rho_ii = 1; unmeasured pairs count as 0 (independent) and are listed."""
    names = list(dict.fromkeys(names))
    n = len(names)
    if n == 0:
        return {"n": 0, "effective": 0.0, "unmeasured": []}
    rho = {}
    for p in pairs:
        rho[frozenset((p["a"], p["b"]))] = max(0.0, p["rho"])      # clip: opposition must not inflate the count
    total, unmeasured = float(n), []
    for i in range(n):
        for j in range(i + 1, n):
            key = frozenset((names[i], names[j]))
            if key in rho:
                total += 2 * rho[key]
            else:
                unmeasured.append((names[i], names[j]))
    return {"n": n, "effective": round(n * n / total, 2), "unmeasured": unmeasured}


def proven_count(names: list, proven: set) -> int:
    return sum(1 for x in dict.fromkeys(names) if str(x).lower() in proven)


def confluence_verdict(confluence: dict) -> dict:
    """Does more families agreeing raise net R? Gross avgR rows minus the lab's planning cost; rows with n < 100 are not used."""
    rows = []
    for name, v in confluence.items():
        if v.get("n") is None or v.get("avgR") is None:
            continue
        rows.append({"level": name, "n": v["n"], "avgR": v["avgR"], "net": round(v["avgR"] - COST_R, 3), "evidence": v["n"] >= MIN_N})
    usable = [r for r in rows if r["evidence"]]
    positive = [r for r in usable if r["net"] > 0]
    if not usable:
        text = "no confluence level has n >= 100: no verdict"
    elif not positive:
        text = f"none of the {len(usable)} usable confluence levels has positive net R: more agreeing families did not add measured edge"
    else:
        text = "positive net R at: " + ", ".join(r["level"] for r in positive) + " (still needs the OOS half and the Truth Court)"
    return {"rows": rows, "verdict": text, "n_positive": len(positive)}


def promoted(root=None) -> set:
    snap = hub_core.read("truth", root)
    return {str(f.get("key")).lower() for f in (snap or {}).get("findings", []) if f.get("promote")}


def run(lab_path: Path | None = None, root=None, publish: bool = True) -> dict | None:
    try:
        data = json.loads((lab_path or LAB_FILE).read_text())
    except (FileNotFoundError, ValueError, OSError):
        return None
    pairs = pair_stats(data.get("conflicts", []))
    conf = confluence_verdict(data.get("confluence", {}))
    counts = {c: sum(1 for p in pairs if p["class"] == c) for c in ("REDUNDANT", "OPPOSED", "INDEPENDENT")}
    out = {"pairs": pairs, "confluence": conf, "counts": counts}
    if publish:
        hub_core.publish(SPEC.id, [{"a": p["a"], "b": p["b"], "rho": p["rho"], "class": p["class"]} for p in pairs], len(pairs),
                         extra={"counts": counts, "confluence_verdict": conf["verdict"]}, root=root)   # one z-test per pair
    return out


def render(st, L=lambda s: s) -> None:
    from modules import hub_ui
    hub_ui.show(st, hub_ui.header(SPEC, L(SPEC.purpose), L(SPEC.title)))
    res = run()
    if res is None:
        st.info(L("No lab file yet (data/strategy_lab.json). Run the lab first."))
        return
    pairs = res["pairs"]
    k = res["counts"]
    hub_ui.show(st, hub_ui.cards([
        ("P", L("Pairs tested"), len(pairs), L("Bonferroni over all pairs"), "", None),
        ("=", L("Redundant"), k["REDUNDANT"], L("same idea counted twice"), "warn" if k["REDUNDANT"] else "", 100 * k["REDUNDANT"] / max(1, len(pairs))),
        ("x", L("Opposed"), k["OPPOSED"], L("point opposite ways"), "", 100 * k["OPPOSED"] / max(1, len(pairs))),
        ("~", L("Independent"), k["INDEPENDENT"], L("real separate information"), "up", 100 * k["INDEPENDENT"] / max(1, len(pairs)))]) +
        hub_ui.graph([(p["a"], p["b"], p["rho"], p["class"]) for p in pairs], title=L("Detector map: who agrees, who fights")))
    st.dataframe([{k: p[k] for k in ("a", "b", "together", "opposite", "rho", "z", "class")} for p in sorted(pairs, key=lambda p: -abs(p["rho"]))],
                 hide_index=True, use_container_width=True)
    st.markdown("**" + L("How many votes is your consensus really worth?") + "**")
    names = sorted({x for p in pairs for x in (p["a"], p["b"])})
    pick = st.multiselect(L("Detectors in the consensus"), names, default=names[:4], key="hc_pick")
    ev = effective_votes(pick, pairs)
    pc = proven_count(pick, promoted())
    m = st.columns(3)
    m[0].metric(L("Detectors"), ev["n"])
    m[1].metric(L("Effective independent votes"), ev["effective"])
    m[2].metric(L("Proven votes (Truth Court)"), pc)
    if ev["unmeasured"]:
        st.caption(L(f"{len(ev['unmeasured'])} pair(s) have no lab measurement and are counted as independent: the real number may be lower."))
    st.markdown("**" + L("Does more agreement help?") + "**")
    conf = res["confluence"]
    (st.success if conf["n_positive"] else st.warning)(L(conf["verdict"]))
    st.dataframe([{**r, "evidence": "n>=100" if r["evidence"] else "not evidence"} for r in conf["rows"]], hide_index=True, use_container_width=True)
