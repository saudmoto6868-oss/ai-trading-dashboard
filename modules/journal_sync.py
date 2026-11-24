"""Browser -> server journal sync. The workspace (a static iframe) pushes trade snapshots through the hidden component in
modules/journal_bridge/; this module saves them to trade_journal (the one store) and acks them so nothing is lost on a rerun.

Idempotent: a snapshot re-sent after a rerun is merged again with no change. Bad snapshots are dropped, not saved."""
from __future__ import annotations

import os

import streamlit as st
import streamlit.components.v1 as components

from modules import trade_journal as TJ

_bridge = components.declare_component("xpix_journal_bridge", path=os.path.join(os.path.dirname(__file__), "journal_bridge"))
ACKS_KEY = "journal_acks"


def sync() -> int:
    """Call once per run on the page that hosts the workspace. Returns how many new snapshots were saved this run."""
    acks: dict = st.session_state.get(ACKS_KEY, {})
    val = _bridge(key="journal_bridge", default=None, acks=acks)
    if not isinstance(val, dict):
        return 0
    uid = str(val.get("uid") or "")
    events = val.get("events") or []
    if not uid or not isinstance(events, list):
        return 0
    last = int(acks.get(uid, 0))
    fresh = [ev for ev in sorted((e for e in events if isinstance(e, dict)), key=lambda e: int(e.get("seq") or 0))
             if int(ev.get("seq") or 0) > last]
    recs = [ev["rec"] for ev in fresh if isinstance(ev.get("rec"), dict)]
    sigs = [r for r in recs if r.get("kind") == "sig"]   # chart strategies' new plans -> the signal ledger (modules/signal_ledger.py), not the trade journal
    saved = TJ.apply_snapshots([r for r in recs if r.get("kind") != "sig"]) if recs else 0
    if sigs:
        try:
            from modules import signal_ledger as SL
            saved += sum(1 for x in SL.record_many(sigs) if x)
        except Exception:
            pass   # a ledger problem must never block the journal
    if fresh:
        last = int(fresh[-1].get("seq") or last)  # bad snapshots are skipped, not re-sent forever
    acks[uid] = last
    st.session_state[ACKS_KEY] = acks
    return saved
