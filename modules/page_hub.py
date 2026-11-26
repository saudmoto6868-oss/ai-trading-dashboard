"""Research Hub page (index 9): tabs that read each other only through data/hub snapshots. Moved from main.py unchanged (maintenance plan M7 / 4.2)."""

import streamlit as st

from modules.i18n import L
from modules.page_kit import kit_theme as _kit_theme, xl as _xl


def render_page():   # Research Hub (owner 2026-10-29): separate tabs that read each other only through data/hub snapshots (docs/RESEARCH_HUB.md)
    global _HUB_TABS, _hi, _hub_exc, _hub_fn, _hub_mod, _hub_tab, _hub_ui, _il_hub   # module-level names, as in main.py before (M7)
    try:
        import importlib as _il_hub
        from modules import hub_ui as _hub_ui
        _hub_ui.set_theme(*_kit_theme())   # hub tabs follow the Theme menu like Radar / Technical Office
        _HUB_TABS = {"Command Center": [("hub_ui", "render_overview")],   # 2026-11-09: 8 tabs -> 4 (owner approved); each group runs its parts one under the other
                     "Truth, funnel & consensus": [("hub_truth", "render"), ("hub_funnel", "render"), ("hub_consensus", "render")],
                     "Plateau & regime": [("hub_plateau", "render"), ("hub_regime", "render")],
                     "Trail & decay": [("hub_trail", "render"), ("hub_decay", "render")]}   # the trail publishes the live R series the decay watch reads
        if st.session_state.get("hub_tab") not in _HUB_TABS:
            st.session_state.pop("hub_tab", None)
        _hub_tab = st.segmented_control(" ", list(_HUB_TABS), default="Command Center", format_func=L, key="hub_tab", label_visibility="collapsed") or "Command Center"
        for _hi, (_hub_mod, _hub_fn) in enumerate(_HUB_TABS[_hub_tab]):   # only the open group is imported and run
            if _hi:
                st.divider()
            getattr(_il_hub.import_module("modules." + _hub_mod), _hub_fn)(st, L)
    except Exception as _hub_exc:
        st.error(_xl("Research Hub: ", "Research Hub: ") + str(_hub_exc))
    st.stop()
