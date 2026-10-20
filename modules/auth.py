"""Item 22: optional login gate. OFF unless the owner sets APP_PASSWORD (one shared password) or APP_USERS
("name:password,name2:password2") in Streamlit Secrets / env - so nothing locks the owner out by surprise.
Passwords are compared in constant time; after 5 wrong tries a session must wait 60 s. The login lasts for the browser
session (Streamlit session state); closing the tab logs out. Not a full user system: no sign-up, no password reset, no
per-user data. For Google / Microsoft sign-in Streamlit's st.login (OIDC) can replace this later."""
from __future__ import annotations

import hmac
import os
import time

MAX_TRIES, LOCK_S = 5, 60


def _secret(name: str) -> str:
    v = os.environ.get(name, "")
    if not v:
        try:
            import streamlit as st
            v = str(st.secrets.get(name, "") or "")
        except Exception:
            v = ""
    return v.strip()


def users() -> dict:
    """{name: password}; '' is the name for the single shared APP_PASSWORD. Empty dict = gate off."""
    out = {}
    for pair in _secret("APP_USERS").split(","):
        pair = pair.strip()
        if ":" in pair:
            n, p = pair.split(":", 1)
            if n.strip() and p:
                out[n.strip().lower()] = p
    pw = _secret("APP_PASSWORD")
    if pw:
        out[""] = pw
    return out


def check(name: str, password: str, table: dict) -> bool:
    want = table.get((name or "").strip().lower()) if (name or "").strip() else table.get("")
    if want is None and "" in table:          # a name typed but only a shared password exists
        want = table[""]
    return bool(want) and hmac.compare_digest(password.encode(), want.encode())


def gate(L=lambda s: s) -> bool:
    """Call right after st.set_page_config. Returns True when the page may render; otherwise draws the login form."""
    import streamlit as st
    table = users()
    if not table or st.session_state.get("auth_ok"):
        return True
    ss = st.session_state
    st.markdown("### 🔒 6868 X")
    wait = ss.get("auth_lock", 0) - time.time()
    if wait > 0:
        st.error(L("Too many wrong tries - wait") + f" {int(wait) + 1} s")
        return False
    with st.form("login"):
        name = st.text_input(L("User name"), key="auth_name") if any(k for k in table) else ""
        pw = st.text_input(L("Password"), type="password", key="auth_pw")
        ok = st.form_submit_button(L("Log in"))
    if ok:
        if check(name, pw, table):
            ss["auth_ok"], ss["auth_user"], ss["auth_fails"] = True, (name or "owner"), 0
            st.rerun()
        ss["auth_fails"] = ss.get("auth_fails", 0) + 1
        if ss["auth_fails"] >= MAX_TRIES:
            ss["auth_lock"], ss["auth_fails"] = time.time() + LOCK_S, 0
        st.error(L("Wrong user name or password."))
    return False
