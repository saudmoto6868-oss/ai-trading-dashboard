"""HUB TAB 7 - KILL FUNNEL: of every rule the lab tried, how many survive each honest test, in order?

Stages are applied one after another to the SAME pool, so each count is a subset of the one above:
  Tested        every lab row
  Testable      has a t-stat
  Enough trades n >= 100
  Gross edge    average R > 0
  Net edge      average R after the planning cost (0.10R) > 0
  Both halves   in-sample AND out-of-sample average R > 0
  t >= 3        t-stat above the Harvey-Liu-Zhu hurdle (positive side only)
  Bonferroni    t above the bar for ALL trials counted by the Truth Court
The last stage is the survivor list. The headline is the kill rate: the share of tested rules that died. It also shows the
break-even win rate for each reward:risk (pure target/stop trades: p = (1 + cost) / (RR + 1)) next to what the lab measured, because
the lab's 'win' counts any trade with R > 0 (time exits can win less than the target), so win% alone cannot be turned into R.
Tests no hypothesis itself (n_trials = 0). Identity: orange, glyph "▼". Pure Python; render() takes st so the module imports without streamlit."""
from __future__ import annotations

import json
from pathlib import Path

from modules import hub_core

SPEC = hub_core.TabSpec(
    id="funnel", title="Kill Funnel", glyph="▼", accent="#F76808",
    purpose="Shows how many lab rules die at each honest test, and why a win rate alone does not pay.",
    consumes=("truth",),
)
LAB_FILE = Path(__file__).resolve().parent.parent / "data" / "strategy_lab.json"
COST_R = 0.10
MIN_N = hub_core.MIN_N
MIN_T = hub_core.MIN_T
STAGE_NAMES = ("Tested", "Testable", "Enough trades", "Gross edge", "Net edge", "Both halves", "t >= 3", "Bonferroni")


def _net(r: dict) -> float:
    return r["net"] if r.get("net") is not None else (r.get("avgR") or 0.0) - COST_R


def _passes(r: dict, bonf_t: float) -> list:
    """Booleans for each stage, cumulative: a rule that fails one stage fails all later ones."""
    t = r.get("t")
    raw = [True,
           t is not None and (r.get("n") or 0) > 0,
           (r.get("n") or 0) >= MIN_N,
           (r.get("avgR") or 0.0) > 0,
           _net(r) > 0,
           r.get("is_avgR") is not None and r.get("oos_avgR") is not None and r["is_avgR"] > 0 and r["oos_avgR"] > 0,
           t is not None and t >= MIN_T,
           t is not None and t >= bonf_t]
    out, alive = [], True
    for ok in raw:
        alive = alive and bool(ok)
        out.append(alive)
    return out


def funnel(rows: list, bonf_t: float | None = None) -> dict:
    """Stage counts, per-school survivors and the kill rate. bonf_t defaults to the bar for the lab's own testable count."""
    n_testable = sum(1 for r in rows if r.get("t") is not None and (r.get("n") or 0) > 0)
    bonf = bonf_t if bonf_t is not None else hub_core.bonferroni_t(max(1, n_testable))
    flags = [(_r, _passes(_r, bonf)) for _r in rows]
    stages, prev = [], len(rows)
    for i, name in enumerate(STAGE_NAMES):
        n = sum(1 for _r, f in flags if f[i])
        stages.append({"name": name, "n": n, "killed": prev - n if i else 0, "pct_of_tested": round(100 * n / len(rows), 1) if rows else 0.0})
        prev = n
    schools: dict = {}
    for r, f in flags:
        s = schools.setdefault(r.get("school") or "?", [0] * len(STAGE_NAMES))
        for i, ok in enumerate(f):
            s[i] += 1 if ok else 0
    survivors = [{"key": r.get("key"), "school": r.get("school"), "tf": r.get("tf"), "side": r.get("side"), "n": r.get("n"), "t": r.get("t"), "net": round(_net(r), 3)}
                 for r, f in flags if f[-1]]
    last = stages[-1]["n"] if stages else 0
    both = STAGE_NAMES.index("Both halves")
    closest = sorted(({"key": r.get("key"), "school": r.get("school"), "tf": r.get("tf"), "side": r.get("side"), "n": r.get("n"), "t": r.get("t"), "net": round(_net(r), 3)}
                      for r, f in flags if f[both] and not f[-1]), key=lambda x: -(x["t"] or 0))[:10]
    verdict_stages = stages[2:]   # "Testable" only says a row had no t-stat (missing data), not that the rule failed a test
    untested = sorted(k for k, v in schools.items() if v[0] > 0 and v[1] == 0)   # schools where NO row has a t-stat: the funnel cannot judge them at all
    return {"untested_schools": untested, "closest": closest, "stages": stages, "schools": schools, "survivors": survivors, "bonferroni_t": round(bonf, 2),
            "tested": len(rows), "survived": last, "kill_rate": round(100 * (1 - last / len(rows)), 1) if rows else None,
            "biggest_kill": max(verdict_stages, key=lambda s: s["killed"])["name"] if verdict_stages and any(s["killed"] for s in verdict_stages) else None}


def breakeven_win(rr: float, cost_r: float = COST_R) -> float:
    """Win rate that makes a pure target/stop trade pay nothing: p*RR - (1-p) - cost = 0."""
    return (1 + cost_r) / (rr + 1)


def breakeven_table(rows: list, cost_r: float = COST_R, rrs=(0.5, 1.0, 1.5, 2.0, 3.0, 5.0)) -> list:
    """Per reward:risk: break-even win rate, and (when the lab has a plain rrX exit row) the measured win%, measured net R and a warning
    when win% is above break-even yet net R is not positive (winners are smaller than the target, so win% cannot be converted to R)."""
    lab = {r["side"]: r for r in rows if r.get("key") == "*VAR*" and r.get("tf") == "all" and str(r.get("side", "")).startswith("rr") and "_" not in r["side"]}
    out = []
    for rr in rrs:
        be = breakeven_win(rr, cost_r)
        m = lab.get(f"rr{rr:.1f}")
        row = {"rr": rr, "breakeven_win_pct": round(100 * be, 1), "lab_win_pct": None, "lab_net_r": None, "lab_n": None, "note": "no lab row at this R:R"}
        if m:
            net = _net(m)
            row.update({"lab_win_pct": m.get("win"), "lab_net_r": round(net, 3), "lab_n": m.get("n")})
            above = m.get("win") is not None and m["win"] / 100 > be
            row["note"] = ("win% above break-even but net R <= 0: winners pay less than the target" if above and net <= 0 else
                           "win% below break-even" if not above else "above break-even and net R positive")
        out.append(row)
    return out


def run(lab_path: Path | None = None, root=None, publish: bool = True) -> dict | None:
    try:
        data = json.loads((lab_path or LAB_FILE).read_text())
    except (FileNotFoundError, ValueError, OSError):
        return None
    truth = hub_core.read("truth", root) or {}
    res = funnel(data.get("rows", []), truth.get("bonferroni_t"))
    res["breakeven"] = breakeven_table(data.get("rows", []))
    res["used_truth_bar"] = truth.get("bonferroni_t") is not None
    if publish:
        hub_core.publish(SPEC.id, res["survivors"][:50], 0, extra={"untested_schools": res["untested_schools"], "stages": res["stages"], "kill_rate": res["kill_rate"], "tested": res["tested"],
                                                                   "survived": res["survived"], "biggest_kill": res["biggest_kill"]}, root=root)
    return res


def render(st, L=lambda s: s) -> None:
    from modules import hub_ui
    hub_ui.show(st, hub_ui.header(SPEC, L(SPEC.purpose), L(SPEC.title), L))
    res = run()
    if res is None:
        st.info(L("No lab file yet (data/strategy_lab.json). Run the lab first."))
        return
    s = res["stages"]
    hub_ui.show(st, hub_ui.cards([
        ("T", L("Rules tested"), res["tested"], L("every lab row"), "", None),
        ("x", L("Kill rate"), f"{res['kill_rate']}%", L("biggest cut: {b}").format(b=res["biggest_kill"]) if res["biggest_kill"] else "", "warn" if res["survived"] == 0 else "", res["kill_rate"]),
        ("OK", L("Survivors"), res["survived"], L("past t >= {t} (Bonferroni)").format(t=res["bonferroni_t"]), "up" if res["survived"] else "warn", None)]) +
        hub_ui.funnel([{**x, "name": L(x["name"])} for x in s], SPEC.accent, L("Survivors after each test, in order")))
    if not res["used_truth_bar"]:
        st.caption(L("The Bonferroni bar here uses the lab's own count; open the Truth Court once to use the count of all tabs."))
    if res["untested_schools"]:
        st.error(L("Not judged at all (no row has a t-stat): ") + ", ".join(res["untested_schools"]) +
                 L(". The lab file is older than the t-stat change; re-run the Strategy lab so these schools can be tested."))
    both_n = res["stages"][STAGE_NAMES.index("Both halves")]["n"]
    t3_n = res["stages"][STAGE_NAMES.index("t >= 3")]["n"]
    if res["survived"]:
        st.success(L("{k} of {n} rules survive every stage.").format(k=res["survived"], n=res["tested"]))
    else:
        st.warning(L("No rule survives every stage. {b} rules have positive net R in both halves, {t} of them reach t >= 3.").format(b=both_n, t=t3_n)
                   + L(" None clears the bar for all trials." if t3_n else " Those few are too weak to tell from luck."))
    if res["closest"]:
        st.markdown("**" + L("Closest candidates (positive net R in both halves)") + "**")
        st.dataframe(res["closest"], hide_index=True, use_container_width=True)
    st.markdown("**" + L("Survivors by school at each stage") + "**")
    st.dataframe([{"school": k, **dict(zip(STAGE_NAMES, v))} for k, v in sorted(res["schools"].items(), key=lambda kv: -kv[1][0])], hide_index=True, use_container_width=True)
    st.markdown("**" + L("Break-even win rate by reward:risk (pure target/stop trades, 0.10R cost)") + "**")
    st.dataframe([{"R:R": b["rr"], "break-even win %": b["breakeven_win_pct"], "lab win %": b["lab_win_pct"], "lab net R": b["lab_net_r"], "n": b["lab_n"], "reading": b["note"]}
                  for b in res["breakeven"]], hide_index=True, use_container_width=True)
    st.caption(L("The lab's 'win' is any trade with R > 0, so a time exit can count as a win while paying less than the target. Trust the measured net R, not win% alone."))
