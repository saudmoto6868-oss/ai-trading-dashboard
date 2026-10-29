"""HUB TAB 5 - DECAY WATCH: is the live edge fading, and may a challenger replace the champion?

Reads the live R series the Decision Trail publishes (never its code) and applies two rules that are FIXED IN ADVANCE:
  Decay      CUSUM on net R against a baseline mu0 (hub_core.decay_cusum, k=0.5 sigma, h=4 sigma) plus the rolling t-stat of
             the last 30 trades.   ALARM now AND rolling t < -2 -> RETIRE (size x0)   ALARM now -> SHRINK (size x0.5)
             rolling t < -1 -> WATCH   fewer than 30 live trades -> TOO FEW (no verdict, never "OK").
  Champion   one live rule at a time. A challenger must pass hub_core.promote() AGAINST the champion out of sample, AND clear the
             Bonferroni t for (Truth Court N + every challenger ever tried + 1), AND not come within 30 days of the last
             promotion. EVERY challenge, passed or failed, is written to the registry: the failures are what keeps N honest.
It tests no trading idea itself; each challenger counts as one trial for the Truth Court.
Identity: red, glyph "↘". Pure Python; render() takes st so the module imports without streamlit."""
from __future__ import annotations

import math
import time

from modules import hub_core

SPEC = hub_core.TabSpec(
    id="decay", title="Decay Watch", glyph="↘", accent="#E5484D",
    purpose="Warns when a live edge fades, shrinks or retires it by a rule fixed in advance, and gates champion changes.",
    consumes=("trail", "truth"),
)
MIN_LIVE = 30
ROLL_WIN = 30
PROMO_COOLDOWN_S = 30 * 86400
SIZE = {"OK": 1.0, "WATCH": 1.0, "SHRINK": 0.5, "RETIRE": 0.0, "TOO FEW": None}


def cusum_path(xs: list, mu0: float, sigma: float, k: float = hub_core.DECAY_K) -> list:
    """The CUSUM statistic after every trade (same formula as hub_core.decay_cusum, one value per step)."""
    s, out = 0.0, []
    for x in xs:
        s = max(0.0, s + (mu0 - x) / sigma - k) if sigma > 0 else 0.0
        out.append(round(s, 4))
    return out


def rolling_t(xs: list, win: int = ROLL_WIN) -> float | None:
    seg = xs[-win:]
    n = len(seg)
    if n < 3:
        return None
    m = sum(seg) / n
    var = sum((x - m) ** 2 for x in seg) / (n - 1)
    if var <= 0:   # identical results every time: no spread, so the sign of the mean is the whole story
        return None if m == 0 else math.copysign(math.inf, m)
    return m / math.sqrt(var / n)


def _sigma(xs: list) -> float:
    n = len(xs)
    if n < 2:
        return 0.0
    m = sum(xs) / n
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))


def status(live_r: list, mu0: float = 0.0, h: float = hub_core.DECAY_H) -> dict:
    """Verdict on a live net-R series. mu0 = the edge we believe it should have (default 0 = break-even after costs)."""
    n = len(live_r)
    if n < MIN_LIVE:
        return {"state": "TOO FEW", "n": n, "size": None, "cusum": None, "rolling_t": rolling_t(live_r), "first_alarm_at": None,
                "why": f"{n} live trades < {MIN_LIVE}: no verdict"}
    sigma = _sigma(live_r) or 1.0   # all-identical results: fall back to 1R (one stop) as the scale
    base = hub_core.decay_cusum(live_r, mu0, sigma, h=h)
    path = cusum_path(live_r, mu0, sigma)
    now = path[-1] > h
    rt = rolling_t(live_r)
    if now and rt is not None and rt < -2:
        st, why = "RETIRE", f"CUSUM {path[-1]:.1f} > {h} and rolling t {rt:.2f} < -2"
    elif now:
        st, why = "SHRINK", f"CUSUM {path[-1]:.1f} > {h}"
    elif rt is not None and rt < -1:
        st, why = "WATCH", f"rolling t {rt:.2f} < -1"
    else:
        st, why = "OK", "no decay signal (this is not proof of an edge)"
    return {"state": st, "n": n, "size": SIZE[st], "cusum": path[-1], "cusum_path": path, "rolling_t": rt,
            "first_alarm_at": base["at"], "sigma": round(sigma, 4), "mu0": mu0, "why": why}


def challenge(registry: dict, cand: dict, truth_n: int = 0, now: float | None = None) -> dict:
    """Decide whether `cand` ({id, n, t, is_avgR, oos_avgR, net_avgR}) replaces the champion. Mutates `registry`
    (events list + champion) and returns the decision. A failed challenge is still recorded and still counts as a trial."""
    now = now or time.time()
    events = registry.setdefault("events", [])
    tried = sum(1 for e in events if e["kind"] == "challenge")
    need_t = hub_core.bonferroni_t(truth_n + tried + 1)
    ok, why = hub_core.promote(cand, registry.get("champion"))
    if ok and abs(cand.get("t") or 0) < need_t:
        ok, why = False, why + [f"|t| {abs(cand.get('t') or 0):.2f} < Bonferroni {need_t:.2f} for N={truth_n + tried + 1}"]
    last = registry.get("last_promotion_ts")
    if ok and last is not None and now - last < PROMO_COOLDOWN_S:
        ok, why = False, why + [f"cooldown: last promotion {(now - last) / 86400:.0f} days ago (< 30)"]
    events.append({"ts": int(now), "kind": "challenge", "id": cand.get("id"), "passed": ok, "reasons": why,
                   "cand": {k: cand.get(k) for k in ("n", "t", "is_avgR", "oos_avgR", "net_avgR")}})
    if ok:
        registry["champion"] = {"id": cand.get("id"), **{k: cand.get(k) for k in ("n", "t", "is_avgR", "oos_avgR", "net_avgR")}, "since": int(now)}
        registry["last_promotion_ts"] = int(now)
    return {"promoted": ok, "reasons": why, "need_t": round(need_t, 2), "n_challenges": tried + 1}


def set_champion(registry: dict, cand: dict, now: float | None = None) -> None:
    """Record the incumbent (first one needs no challenge: it is already live). Logged as an event, not hidden."""
    now = int(now or time.time())
    registry["champion"] = {"id": cand.get("id"), **{k: cand.get(k) for k in ("n", "t", "is_avgR", "oos_avgR", "net_avgR")}, "since": now}
    registry.setdefault("events", []).append({"ts": now, "kind": "champion_set", "id": cand.get("id"), "passed": True, "reasons": [], "cand": {}})


def load_registry(root=None) -> dict:
    snap = hub_core.read(SPEC.id, root) or {}
    return snap.get("registry") or {"events": []}


def run(root=None, mu0: float = 0.0, registry: dict | None = None, publish: bool = True) -> dict:
    """Read the Decision Trail's live R series, judge it, publish status + registry for the other tabs."""
    trail = hub_core.read("trail", root) or {}
    live = trail.get("live_r") or []
    st = status(live, mu0)
    reg = registry if registry is not None else load_registry(root)
    tried = sum(1 for e in reg.get("events", []) if e["kind"] == "challenge")
    if publish:
        hub_core.publish(SPEC.id, [{"state": st["state"], "size": st["size"], "n": st["n"], "why": st["why"]}], tried,
                         extra={"registry": reg}, root=root)
    return {"status": st, "registry": reg, "has_trail": bool(trail)}


def render(st, L=lambda s: s) -> None:
    import pandas as pd
    st.markdown(f"<div style='border-left:4px solid {SPEC.accent};padding-left:10px'><b>{SPEC.glyph} {L(SPEC.title)}</b><br>"
                f"<span style='opacity:.75'>{L(SPEC.purpose)}</span></div>", unsafe_allow_html=True)
    mu0 = st.number_input(L("Baseline net R per trade we believe in (0 = break-even after costs)"), value=0.0, step=0.05, key="hd_mu0")
    res = run(mu0=mu0)
    s = res["status"]
    if not res["has_trail"]:
        st.info(L("The Decision Trail has not published a live R series yet. Open that tab with a signal log first."))
    box = {"OK": st.success, "WATCH": st.warning, "SHRINK": st.warning, "RETIRE": st.error, "TOO FEW": st.info}[s["state"]]
    box(f"{s['state']} - {L(s['why'])}" + ("" if s["size"] is None else f"  |  size x{s['size']}"))
    c = st.columns(3)
    c[0].metric(L("Live trades"), s["n"])
    c[1].metric(L("CUSUM (alarm above 4)"), "n/a" if s["cusum"] is None else s["cusum"])
    c[2].metric(L("Rolling t (last 30)"), "n/a" if s["rolling_t"] is None else round(s["rolling_t"], 2))
    if s.get("cusum_path"):
        st.line_chart(pd.DataFrame({"CUSUM": s["cusum_path"]}))
    st.markdown("**" + L("Champion / challenger registry") + "**")
    reg = res["registry"]
    ch = reg.get("champion")
    st.caption(L("Champion: ") + (f"{ch['id']} (since {ch['since']})" if ch else L("none set")))
    with st.form("hd_challenge"):
        f = st.columns(3)
        cid = f[0].text_input(L("Rule id"), key="hd_id")
        n = f[1].number_input("n", min_value=0, value=0, step=10, key="hd_n")
        t = f[2].number_input("t", value=0.0, step=0.1, key="hd_t")
        g = st.columns(3)
        isr = g[0].number_input("IS avgR", value=0.0, step=0.01, key="hd_is")
        oos = g[1].number_input("OOS avgR", value=0.0, step=0.01, key="hd_oos")
        net = g[2].number_input("net avgR (after costs)", value=0.0, step=0.01, key="hd_net")
        as_champ = st.checkbox(L("Record as the current live champion (no challenge)"), key="hd_champ")
        go = st.form_submit_button(L("Submit"))
    if go and cid:
        cand = {"id": cid, "n": int(n), "t": float(t), "is_avgR": float(isr), "oos_avgR": float(oos), "net_avgR": float(net)}
        if as_champ:
            set_champion(reg, cand)
            d = None
        else:
            truth = hub_core.read("truth") or {}
            d = challenge(reg, cand, int(truth.get("n_trials", 0)))
        run(registry=reg)
        if d is not None:
            (st.success if d["promoted"] else st.error)(L("Promoted" if d["promoted"] else "Rejected: ") + "; ".join(d["reasons"]) + f"  (N={d['n_challenges']}, need t>={d['need_t']})")
    if reg.get("events"):
        st.dataframe([{"time": e["ts"], "kind": e["kind"], "id": e["id"], "passed": e["passed"], "why not": "; ".join(e["reasons"])}
                      for e in reversed(reg["events"][-50:])], hide_index=True, use_container_width=True)
