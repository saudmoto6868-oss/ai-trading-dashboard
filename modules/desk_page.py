"""AI Desk page (Learn & AI hub, owner order 2026-11-15: "one brain", ai-desk folded into the dashboard).

The engine is the ai-desk project (6868-group/ai-desk) copied as the package `modules/desk_brain/`:
- Agent floor: real LLM agents (Head, 8 specialists, Bull/Bear, Risk, Auditor, Reviewer) in a ReAct loop with tools.
  A fixed rules gate has the last word; the LLM never overrides it. Paper only: nothing here places an order.
- Watchlist engine: every market's best side, 3+ reasons from 2+ departments, stars.
- Accounts: the three prop accounts (floors, room today, risk per trade) and lot size per account.

LLM: the free Gemini key first (GEMINI_API_KEY in Secrets, same as the Guide). With no key the floor button is
off and says why; Watchlist and Accounts work without any key. Keys are read from env / Streamlit Secrets only.
Token budget (CLAUDE.md "after launch" rule): DESK_FLOOR_DAILY_CAP runs per day (default 3).
"""
from __future__ import annotations

import asyncio
import os
import tempfile
import threading
import time
from datetime import datetime, timezone

import streamlit as st

_ENV_KEYS = ("LLM_BASE_URL", "LLM_API_KEY", "LLM_MODEL", "LLM_FALLBACKS", "AGENT_MODELS", "AGENT_CONCURRENCY",
             "AGENT_MAX_CANDIDATES", "LLM_RPM", "ALPHAVANTAGE_API_KEY", "DESK_DATA_MODE", "DESK_FLOOR_DAILY_CAP")


def _secret(name: str) -> str:
    v = os.environ.get(name, "")
    if not v:
        try:
            v = str(st.secrets.get(name, "") or "")
        except Exception:
            v = ""
    return v


def setup_env() -> None:
    """Copy the brain's settings from Streamlit Secrets into the environment BEFORE desk_brain.config is imported
    (it reads os.environ once). Nothing is written to disk."""
    for k in _ENV_KEYS:
        v = _secret(k)
        if v and not os.environ.get(k):
            os.environ[k] = v
    if not os.environ.get("GEMINI_API_KEY"):
        try:
            from modules.ai_provider import gemini_key
            gk = gemini_key()
        except Exception:
            gk = ""
        if gk:
            os.environ["GEMINI_API_KEY"] = gk
    os.environ.setdefault("DESK_DATA_DIR", os.path.join(tempfile.gettempdir(), "desk_brain"))


def daily_cap() -> int:
    try:
        return max(0, int(os.environ.get("DESK_FLOOR_DAILY_CAP", "3")))
    except ValueError:
        return 3


class FloorRun:
    """One shared floor for the whole app (st.cache_resource): runs in a background thread, the page only reads it."""

    def __init__(self) -> None:
        self.events: list[dict] = []
        self.result: dict | None = None
        self.error: str | None = None
        self.thread: threading.Thread | None = None
        self.started = 0.0
        self.day = ""
        self.runs_today = 0
        self.lock = threading.Lock()

    @property
    def running(self) -> bool:
        return bool(self.thread and self.thread.is_alive())

    def can_start(self, cap: int) -> tuple[bool, str]:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if self.day != today:
            self.day, self.runs_today = today, 0
        if self.running:
            return False, "running"
        if self.runs_today >= cap:
            return False, "cap"
        return True, ""

    def start(self, floor_factory) -> bool:
        with self.lock:
            if self.running:
                return False
            self.events, self.result, self.error = [], None, None
            self.started = time.time()
            self.runs_today += 1

            async def emit(ev: dict) -> None:
                self.events.append(ev)
                del self.events[:-1500]

            def work() -> None:
                try:
                    self.result = asyncio.run(floor_factory().run(emit))
                except Exception as e:   # shown on the page, never raised into Streamlit
                    self.error = f"{type(e).__name__}: {e}"[:400]

            self.thread = threading.Thread(target=work, name="desk-floor", daemon=True)
            self.thread.start()
            return True


@st.cache_resource
def _floor_run() -> FloorRun:
    return FloorRun()


@st.cache_data(ttl=300, show_spinner=False)
def _watchlist_rows() -> dict:
    from modules.desk_brain.views import watchlist
    w = watchlist(None)
    rows = [{"symbol": r["symbol"], "direction": r.get("direction"), "stars": r.get("stars"), "score": r.get("score"),
             "promoted": r.get("promoted"), "departments": r.get("departments"), "blocked": r.get("blocked"),
             "reasons": [x.get("text") if isinstance(x, dict) else str(x) for x in (r.get("reasons") or [])]} for r in w["rows"]]
    return {"rows": rows, "source": w.get("source") or []}


def _side(d) -> str:
    return "BUY" if d == 1 else ("SELL" if d == -1 else "-")


def ideas_table(ideas: list[dict]) -> list[dict]:
    """Gate decisions -> table rows (pure; tested)."""
    out = []
    for i in ideas or []:
        out.append({"Symbol": i.get("symbol"), "Status": i.get("status"), "Side": _side(i.get("direction")),
                    "Entry": i.get("entry"), "Stop": i.get("stop"), "T1": i.get("t1"), "R:R": i.get("rr"),
                    "Conf %": i.get("confidence"), "Gate vetoes": "; ".join(i.get("vetoes") or []),
                    "Notes": "; ".join(i.get("notes") or []), "Demo data": bool(i.get("demo"))})
    return out


def feed_lines(events: list[dict], limit: int = 60) -> list[str]:
    """Floor events -> short readable lines, newest last (pure; tested)."""
    out = []
    for e in events:
        t = e.get("type")
        if t == "phase":
            out.append(f"### {e.get('title', '')}")
        elif t == "bus":
            sym = f" [{e['symbol']}]" if e.get("symbol") else ""
            out.append(f"**{e.get('from')} → {e.get('to')}**{sym}: {e.get('text', '')}")
        elif t == "agent_tool":
            out.append(f"`{e.get('agent')}` opens `{e.get('tool')}` {e.get('symbol') or ''}".rstrip())
        elif t == "agent_state" and e.get("state") == "error":
            out.append(f"`{e.get('agent')}` error: {e.get('text', '')}")
        elif t == "floor_error":
            out.append(f"Floor error: {e.get('text', '')}")
    return out[-limit:]


def _render_floor(L) -> None:
    from modules.desk_brain import config
    from modules.desk_brain.agent import llm
    from modules.desk_brain.agents.team import Floor, roster
    run = _floor_run()
    cap = daily_cap()
    has_llm = llm.available()
    ok, why = run.can_start(cap)
    c1, c2 = st.columns([3, 2])
    with c1:
        st.caption(L("Real LLM agents: Head, 8 specialists, Bull / Bear, Risk, Auditor, Reviewer. "
                     "A fixed rules gate has the final veto. Paper only - nothing here places an order."))
    with c2:
        st.caption(f"{L('Model')}: {config.LLM_MODEL or '-'} · {L('Runs today')}: {run.runs_today}/{cap}")
    if not has_llm:
        st.info(L("No model key yet. Add GEMINI_API_KEY (free) in Secrets to run the floor. Watchlist and Accounts work without it."))
    label = L("Floor is running...") if run.running else L("Run the floor")
    if st.button(label, type="primary", disabled=not (has_llm and ok), key="dk_run"):
        run.start(Floor)
        st.rerun()
    if why == "cap" and not run.running:
        st.caption(L("Daily cap reached (DESK_FLOOR_DAILY_CAP). It resets at 00:00 UTC."))
    if run.running:
        try:
            from streamlit_autorefresh import st_autorefresh
            st_autorefresh(interval=4000, key="dk_poll")
        except ImportError:
            st.button(L("Refresh"), key="dk_refresh")
        st.caption(f"{L('Running for')} {int(time.time() - run.started)}s · {len(run.events)} {L('events')}")
    if run.error:
        st.error(run.error)
    if run.result:
        res = run.result
        st.markdown(f"**{L('Decisions')}** · {res.get('seconds', 0)}s · {L('LLM calls')}: {(res.get('usage') or {}).get('calls', 0)}")
        rows = ideas_table(res.get("ideas") or [])
        if rows:
            st.dataframe(rows, hide_index=True, width="stretch")
        else:
            st.caption(L("No market worth a trade this run. Waiting is a decision."))
        for i in res.get("ideas") or []:
            if i.get("bull") or i.get("bear"):
                with st.expander(f"{i.get('symbol')} · Bull vs Bear"):
                    st.markdown(f"**Bull:** {i.get('bull') or '-'}\n\n**Bear:** {i.get('bear') or '-'}")
                    if i.get("accounts"):
                        st.caption(L("Lots per account (Risk agent)") + f": {i['accounts']}")
    lines = feed_lines(run.events)
    if lines:
        with st.expander(L("Floor log"), expanded=run.running):
            st.markdown("\n\n".join(lines))
    with st.expander(L("Team")):
        st.dataframe([{"Agent": a["name"], "Role": a["role"], "Tools": ", ".join(a["tools"])} for a in roster()],
                     hide_index=True, width="stretch")


def _render_watchlist(L) -> None:
    st.caption(L("Every market's best side. Promoted = 3+ reasons from 2+ departments. A ranking of evidence, not a win rate."))
    try:
        with st.spinner(L("Scanning the markets (first load can take a minute)")):
            w = _watchlist_rows()
    except Exception as e:
        st.error(f"Watchlist: {type(e).__name__}: {e}")
        return
    if "demo" in w["source"]:
        st.warning(L("Some data is DEMO (the live sources were not reachable). Do not trade on it."))
    rows = sorted(w["rows"], key=lambda r: (not r["promoted"], -(r["stars"] or 0), -(r["score"] or 0)))
    st.dataframe([{"Symbol": r["symbol"], "Side": _side(r["direction"]), "Stars": r["stars"], "Score": r["score"],
                   "Promoted": r["promoted"], "Depts": r["departments"], "News block": r["blocked"],
                   "Reasons": " · ".join(r["reasons"][:4])} for r in rows], hide_index=True, width="stretch")
    st.caption(L("Sources") + ": " + ", ".join(w["source"]))


def _render_accounts(L) -> None:
    from modules.desk_brain import risk
    from modules.desk_brain.config import UNIVERSE
    s = risk.state()
    st.caption(L("Three prop accounts. Risk per trade = the smaller of risk %, the cap, and today's room above the personal floor (half the firm's daily limit)."))
    if s["discipline"]["locked"]:
        st.error(L("Trading locked today") + f": {s['discipline'].get('reason')}")
    st.dataframe([{"Account": a["name"], "Tier": a["tier"], "Balance": a["balance"], "Personal floor": a["personal_floor"],
                   "Room today": a["room_today"], "Risk / trade": a["risk_per_trade"], "Trades left": a["trades_left_today"],
                   "Stopped": a["stopped_today"], "Rule": a["tier_rule"]} for a in s["accounts"]], hide_index=True, width="stretch")
    st.markdown(f"**{L('Lot size')}**")
    a, b, c = st.columns(3)
    sym = a.selectbox(L("Symbol"), list(UNIVERSE), key="dk_sz_sym")
    entry = b.number_input(L("Entry"), value=0.0, format="%.5f", key="dk_sz_e")
    stop = c.number_input(L("Stop"), value=0.0, format="%.5f", key="dk_sz_s")
    if entry and stop and entry != stop:
        z = risk.size(sym, float(entry), float(stop))
        st.caption(f"{L('Stop')}: {z['stop_pips']} pips ({z['pip_rule']})")
        st.dataframe([{"Account": x["name"], "Risk $": x["risk"], "Lots": x["lots"], "Blocked": x["stopped"]} for x in z["accounts"]],
                     hide_index=True, width="stretch")


def render(L=lambda s: s) -> None:
    setup_env()
    tabs = ["Agent floor", "Watchlist engine", "Accounts & size"]
    pick = st.segmented_control(L("AI Desk"), tabs, default=tabs[0], format_func=L, key="dk_tab", label_visibility="collapsed")
    if pick == "Watchlist engine":
        _render_watchlist(L)
    elif pick == "Accounts & size":
        _render_accounts(L)
    else:
        _render_floor(L)
