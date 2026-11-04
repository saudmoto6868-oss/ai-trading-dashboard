"""
PROP FIRMS TRACKER
==================
Renders the "Prop Firms" page (PAGE == 10) in the 6868 X dashboard.

Features
--------
- One card per account with: direct link, inactivity countdown, days since last
  trade, max loss / daily loss / rules, firm colour.
- Warning when inactivity is within 7 days of the limit; DANGER when <= 3 days.
- Each card has a "tab" row: Overview | Rules | Calendar stub | Equity stub.
- Add / edit / delete accounts stored in Streamlit's session_state (JSON-serialisable
  dict) so they persist across reruns within the same session; can be backed up / restored
  as JSON by the user.
- AI helper: given a firm name or URL, it fetches the page (server-side) and
  extracts the main rules automatically, filling the account form.
  Requires GUIDE_PROVIDER=claude and ANTHROPIC_API_KEY *or* GEMINI_API_KEY.
  Falls back gracefully (manual form) when no key is available.

Data model (each account dict)
-------------------------------
{
  "id": str,              # uuid4
  "name": str,            # display name, e.g. "Vanguard 100K"
  "firm": str,            # firm name, e.g. "Upcomers"
  "account_url": str,     # direct link to the account page
  "firm_url": str,        # firm home / rules page
  "account_type": str,    # "Instant" | "Challenge (1-step)" | "Challenge (2-step)"
  "size": str,            # "100K", "10K" etc.
  "currency": str,        # "USD"
  "purchase_date": str,   # ISO date string "YYYY-MM-DD"
  "last_trade_date": str, # ISO date string or "" (never traded)
  "inactivity_limit": int,# days (default 35)
  "max_loss_pct": float,  # overall max loss % (e.g. 10)
  "daily_loss_pct": float,# daily max loss % (e.g. 5)
  "profit_target_pct": float, # profit target % for challenge (0 for Instant)
  "min_trading_days": int,
  "consistency_rule": str,# free text, e.g. "No day > 50% of total profit"
  "other_rules": str,     # free text
  "status": str,          # "active" | "closed" | "failed" | "passed"
  "color": str,           # hex accent colour
  "notes": str,
}
"""

from __future__ import annotations

import json
import uuid
from datetime import date, datetime, timedelta
from typing import Any

import streamlit as st

# ── i18n helpers ────────────────────────────────────────────────────────────
try:
    from modules.i18n import L
except Exception:
    def L(x: str) -> str:  # noqa: E731
        return x

def _xl(ar: str, en: str) -> str:
    """Return Arabic or English depending on session language."""
    return ar if st.session_state.get("ws_lang", "en") == "ar" else en


# ── Default account list (Saud's current accounts) ──────────────────────────
_DEFAULT_ACCOUNTS: list[dict] = [
    {
        "id": "upcomers-ignite-100k",
        "name": "Ignite 100K",
        "firm": "Upcomers",
        "account_url": "https://app.upcomers.com",
        "firm_url": "https://app.upcomers.com",
        "account_type": "Instant",
        "size": "100K",
        "currency": "USD",
        "purchase_date": "",
        "last_trade_date": "",
        "inactivity_limit": 35,
        "max_loss_pct": 10.0,
        "daily_loss_pct": 5.0,
        "profit_target_pct": 0.0,
        "min_trading_days": 0,
        "consistency_rule": "",
        "other_rules": "35-day inactivity rule (from purchase date). No weekend holding for certain instruments.",
        "status": "active",
        "color": "#f0b429",
        "notes": "Active — Upcomers Instant account",
    },
    {
        "id": "upcomers-phoenix-100k",
        "name": "Phoenix 100K",
        "firm": "Upcomers",
        "account_url": "https://app.upcomers.com",
        "firm_url": "https://app.upcomers.com",
        "account_type": "Instant",
        "size": "100K",
        "currency": "USD",
        "purchase_date": "",
        "last_trade_date": "",
        "inactivity_limit": 35,
        "max_loss_pct": 10.0,
        "daily_loss_pct": 5.0,
        "profit_target_pct": 0.0,
        "min_trading_days": 0,
        "consistency_rule": "",
        "other_rules": "35-day inactivity rule. CFD/MT5 account.",
        "status": "active",
        "color": "#f0b429",
        "notes": "Active — Upcomers Instant account",
    },
    {
        "id": "upcomers-vanguard-100k",
        "name": "Vanguard 100K #689771",
        "firm": "Upcomers",
        "account_url": "https://app.upcomers.com",
        "firm_url": "https://app.upcomers.com",
        "account_type": "Instant",
        "size": "100K",
        "currency": "USD",
        "purchase_date": "2026-09-12",
        "last_trade_date": "",
        "inactivity_limit": 35,
        "max_loss_pct": 10.0,
        "daily_loss_pct": 5.0,
        "profit_target_pct": 0.0,
        "min_trading_days": 0,
        "consistency_rule": "",
        "other_rules": "CFD/MT5. 35-day inactivity rule (closed 2026-10-23). Appeal sent ticket #152349628.",
        "status": "closed",
        "color": "#ef4444",
        "notes": "Closed for inactivity 2026-10-23. Appeal pending.",
    },
    {
        "id": "upcomers-vanguard-10k",
        "name": "Vanguard 10K #689772",
        "firm": "Upcomers",
        "account_url": "https://app.upcomers.com",
        "firm_url": "https://app.upcomers.com",
        "account_type": "Instant",
        "size": "10K",
        "currency": "USD",
        "purchase_date": "2026-09-12",
        "last_trade_date": "",
        "inactivity_limit": 35,
        "max_loss_pct": 10.0,
        "daily_loss_pct": 5.0,
        "profit_target_pct": 0.0,
        "min_trading_days": 0,
        "consistency_rule": "",
        "other_rules": "Perpetuals. Bonus account (10% extra on 100K purchase). Closed 2026-10-23.",
        "status": "closed",
        "color": "#ef4444",
        "notes": "Closed for inactivity 2026-10-23. Appeal pending.",
    },
]


# ── Session state helpers ────────────────────────────────────────────────────
def _load_accounts() -> list[dict]:
    if "prop_accounts" not in st.session_state:
        st.session_state["prop_accounts"] = json.loads(json.dumps(_DEFAULT_ACCOUNTS))
    return st.session_state["prop_accounts"]


def _save_accounts(accounts: list[dict]) -> None:
    st.session_state["prop_accounts"] = accounts


def _days_since(iso_date: str) -> int | None:
    """Days since the given ISO date string; None if empty/invalid."""
    if not iso_date:
        return None
    try:
        d = date.fromisoformat(iso_date)
        return (date.today() - d).days
    except Exception:
        return None


def _days_to_inactivity(acc: dict) -> int | None:
    """
    Days left before inactivity limit is hit.
    Timer starts from last_trade_date if ever traded, else from purchase_date.
    Returns None if we cannot compute.
    """
    limit = int(acc.get("inactivity_limit") or 35)
    ref_date = acc.get("last_trade_date") or acc.get("purchase_date") or ""
    since = _days_since(ref_date)
    if since is None:
        return None
    remaining = limit - since
    return remaining


# ── CSS ──────────────────────────────────────────────────────────────────────
_CSS = """
<style>
.pf-grid{display:flex;flex-wrap:wrap;gap:14px;margin-top:4px}
.pf-card{
  background:#161a1e;border:1px solid #2b3139;border-radius:10px;
  padding:0;overflow:hidden;
  flex:1 1 320px;min-width:300px;max-width:520px;
  box-shadow:0 2px 8px #0005;
}
.pf-card-header{
  display:flex;align-items:center;gap:10px;
  padding:10px 14px;border-bottom:1px solid #2b3139;
}
.pf-card-dot{width:11px;height:11px;border-radius:50%;flex-shrink:0}
.pf-card-title{font-size:14px;font-weight:600;color:#e2e8f0}
.pf-card-badge{
  margin-left:auto;font-size:10px;padding:2px 7px;border-radius:4px;
  font-weight:600;text-transform:uppercase;letter-spacing:.04em
}
.badge-active{background:#166534;color:#bbf7d0}
.badge-closed{background:#7f1d1d;color:#fecaca}
.badge-failed{background:#78350f;color:#fde68a}
.badge-passed{background:#1e3a5f;color:#bae6fd}
.pf-timer{
  display:flex;align-items:center;gap:8px;
  padding:8px 14px;border-bottom:1px solid #1e2328;
}
.pf-timer-ok{color:#2dd4bf;font-size:13px;font-weight:600}
.pf-timer-warn{color:#f0b429;font-size:13px;font-weight:600}
.pf-timer-danger{color:#ef4444;font-size:13px;font-weight:600;animation:pfpulse 1s infinite}
@keyframes pfpulse{0%,100%{opacity:1}50%{opacity:.5}}
.pf-timer-na{color:#64748b;font-size:13px}
.pf-tabs{display:flex;border-bottom:1px solid #2b3139}
.pf-tab{
  padding:6px 12px;font-size:11px;color:#64748b;cursor:pointer;
  border-bottom:2px solid transparent;white-space:nowrap;
}
.pf-tab.active{color:#e2e8f0;border-bottom-color:#f0b429}
.pf-body{padding:10px 14px;font-size:12px;color:#94a3b8;min-height:70px}
.pf-rule{display:flex;gap:6px;margin-bottom:4px;align-items:flex-start}
.pf-rule-label{color:#64748b;min-width:90px;flex-shrink:0}
.pf-rule-val{color:#cbd5e1}
.pf-link-btn{
  display:inline-block;margin-top:8px;padding:4px 12px;border-radius:5px;
  background:#1e293b;color:#93c5fd;font-size:11px;text-decoration:none;
  border:1px solid #334155;
}
.pf-link-btn:hover{background:#1d4ed8;color:#fff}
.pf-add-btn{
  background:#1d4ed8;color:#fff;border:none;padding:6px 16px;
  border-radius:6px;cursor:pointer;font-size:12px;
}
</style>
"""

# ── Status badge helper ──────────────────────────────────────────────────────
def _badge(status: str) -> str:
    cls = {"active": "badge-active", "closed": "badge-closed",
           "failed": "badge-failed", "passed": "badge-passed"}.get(status, "badge-active")
    label = {"active": _xl("نشط", "Active"), "closed": _xl("مغلق", "Closed"),
             "failed": _xl("فشل", "Failed"), "passed": _xl("اجتاز", "Passed")}.get(status, status)
    return f'<span class="pf-card-badge {cls}">{label}</span>'


# ── Timer display ────────────────────────────────────────────────────────────
def _timer_html(acc: dict) -> str:
    if acc.get("status") in ("closed", "failed", "passed"):
        return f'<span class="pf-timer-na">— {_xl("لا يوجد عداد", "No timer")}</span>'

    days_left = _days_to_inactivity(acc)
    days_since_trade = _days_since(acc.get("last_trade_date") or "")
    limit = int(acc.get("inactivity_limit") or 35)

    parts = []
    if days_since_trade is not None:
        parts.append(_xl(f"آخر صفقة: {days_since_trade} يوم", f"Last trade: {days_since_trade}d ago"))
    else:
        parts.append(_xl("لم يتم التداول بعد", "No trades yet"))

    if days_left is None:
        cls, msg = "pf-timer-na", _xl("تاريخ الشراء غير محدد", "Purchase date unknown")
    elif days_left <= 0:
        cls, msg = "pf-timer-danger", _xl(f"🚨 تجاوز الـ {limit} يوم!", f"🚨 Over {limit}-day limit!")
    elif days_left <= 3:
        cls, msg = "pf-timer-danger", _xl(f"🚨 {days_left} أيام متبقية!", f"🚨 {days_left} day(s) left!")
    elif days_left <= 7:
        cls, msg = "pf-timer-warn", _xl(f"⚠️ {days_left} أيام متبقية", f"⚠️ {days_left} days left")
    else:
        cls, msg = "pf-timer-ok", _xl(f"✓ {days_left} يوم متبق", f"✓ {days_left} days left")

    summary = " · ".join(parts)
    return (
        f'<div style="display:flex;flex-direction:column;gap:2px">'
        f'<span class="{cls}">{msg}</span>'
        f'<span style="font-size:10px;color:#475569">{summary}</span>'
        f'</div>'
    )


# ── Overview tab body ────────────────────────────────────────────────────────
def _overview_html(acc: dict) -> str:
    rows = [
        (_xl("الشركة", "Firm"), acc.get("firm", "—")),
        (_xl("النوع", "Type"), acc.get("account_type", "—")),
        (_xl("الحجم", "Size"), f'{acc.get("size","—")} {acc.get("currency","USD")}'),
        (_xl("تاريخ الشراء", "Purchased"), acc.get("purchase_date") or "—"),
        (_xl("آخر صفقة", "Last trade"), acc.get("last_trade_date") or _xl("لا يوجد", "none")),
    ]
    if acc.get("notes"):
        rows.append((_xl("ملاحظات", "Notes"), acc["notes"]))
    r = "".join(
        f'<div class="pf-rule"><span class="pf-rule-label">{k}</span>'
        f'<span class="pf-rule-val">{v}</span></div>'
        for k, v in rows
    )
    link_html = ""
    if acc.get("account_url"):
        link_html = (
            f'<a class="pf-link-btn" href="{acc["account_url"]}" target="_blank" rel="noopener">'
            f'🔗 {_xl("فتح الحساب", "Open account")}</a> '
        )
    if acc.get("firm_url") and acc.get("firm_url") != acc.get("account_url"):
        link_html += (
            f'<a class="pf-link-btn" href="{acc["firm_url"]}" target="_blank" rel="noopener">'
            f'📋 {_xl("قواعد الشركة", "Firm rules")}</a>'
        )
    return r + link_html


# ── Rules tab body ───────────────────────────────────────────────────────────
def _rules_html(acc: dict) -> str:
    rows = [
        (_xl("الحد الأقصى للخسارة", "Max drawdown"), f'{acc.get("max_loss_pct", 0):.1f}%'),
        (_xl("خسارة اليوم", "Daily loss limit"), f'{acc.get("daily_loss_pct", 0):.1f}%'),
        (_xl("هدف الربح", "Profit target"), f'{acc.get("profit_target_pct", 0):.1f}%' if acc.get("profit_target_pct") else _xl("لا يوجد (Instant)", "None (Instant)")),
        (_xl("أيام تداول دنيا", "Min trading days"), str(acc.get("min_trading_days", 0)) or "—"),
        (_xl("قاعدة الاتساق", "Consistency rule"), acc.get("consistency_rule") or "—"),
        (_xl("قواعد أخرى", "Other rules"), acc.get("other_rules") or "—"),
        (_xl("الخمول", "Inactivity limit"), f'{acc.get("inactivity_limit", 35)} {_xl("يوم", "days")}'),
    ]
    return "".join(
        f'<div class="pf-rule"><span class="pf-rule-label">{k}</span>'
        f'<span class="pf-rule-val">{v}</span></div>'
        for k, v in rows
    )


# ── Calendar stub ────────────────────────────────────────────────────────────
def _calendar_html(acc: dict) -> str:
    today = date.today()
    # Show a 2-week mini calendar with today highlighted + purchase/last trade markers
    out = [f'<div style="color:#64748b;font-size:11px">{_xl("تقويم PNL غير متاح بدون ربط API الشركة.", "PNL calendar requires firm API integration.")}</div>']
    if acc.get("last_trade_date"):
        out.append(f'<div style="margin-top:6px;color:#94a3b8">{_xl("آخر صفقة:", "Last trade:")} <b style="color:#e2e8f0">{acc["last_trade_date"]}</b></div>')
    return "".join(out)


# ── Equity stub ─────────────────────────────────────────────────────────────
def _equity_html(acc: dict) -> str:
    return (
        f'<div style="color:#64748b;font-size:11px">'
        f'{_xl("منحنى الأسهم غير متاح بدون ربط API الشركة.", "Equity curve requires firm API integration.")}'
        f'</div>'
    )


# ── Single card render ───────────────────────────────────────────────────────
def _render_card(acc: dict, idx: int) -> None:
    color = acc.get("color", "#f0b429")
    card_tab_key = f"pf_card_tab_{acc['id']}"
    if card_tab_key not in st.session_state:
        st.session_state[card_tab_key] = "overview"
    active_tab = st.session_state[card_tab_key]

    tab_labels = [
        ("overview", _xl("نظرة عامة", "Overview")),
        ("rules", _xl("القواعد", "Rules")),
        ("calendar", _xl("التقويم", "Calendar")),
        ("equity", _xl("منحنى الأسهم", "Equity curve")),
    ]
    tabs_html = "".join(
        f'<span class="pf-tab{" active" if t == active_tab else ""}" '
        f'data-tab="{t}">{lbl}</span>'
        for t, lbl in tab_labels
    )

    body_html = {
        "overview": _overview_html(acc),
        "rules": _rules_html(acc),
        "calendar": _calendar_html(acc),
        "equity": _equity_html(acc),
    }.get(active_tab, "")

    card_html = (
        f'<div class="pf-card">'
        f'  <div class="pf-card-header">'
        f'    <div class="pf-card-dot" style="background:{color}"></div>'
        f'    <span class="pf-card-title">{acc.get("name","Account")}</span>'
        f'    {_badge(acc.get("status","active"))}'
        f'  </div>'
        f'  <div class="pf-timer">{_timer_html(acc)}</div>'
        f'  <div class="pf-tabs">{tabs_html}</div>'
        f'  <div class="pf-body">{body_html}</div>'
        f'</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)

    # Tab switcher buttons (Streamlit-native, one row per card)
    cols = st.columns(len(tab_labels))
    for col, (t, lbl) in zip(cols, tab_labels):
        if col.button(lbl, key=f"pf_tab_btn_{acc['id']}_{t}",
                      use_container_width=True,
                      type="primary" if t == active_tab else "secondary"):
            st.session_state[card_tab_key] = t
            st.rerun()


# ── AI rules extractor ───────────────────────────────────────────────────────
def _ai_extract_rules(firm_name: str, firm_url: str) -> dict[str, Any]:
    """
    Try to fetch the firm's rules page and have Claude/Gemini extract them.
    Returns a partial account dict or {} on failure.
    """
    import os, re

    # 1) Fetch the page text (server-side)
    page_text = ""
    if firm_url:
        try:
            import urllib.request
            req = urllib.request.Request(
                firm_url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; 6868X/1.0; +https://github.com/saudmoto6868-oss/ai-trading-dashboard)"},
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                raw = resp.read(32_000).decode("utf-8", errors="ignore")
            # strip tags
            page_text = re.sub(r"<[^>]+>", " ", raw)
            page_text = re.sub(r"\s+", " ", page_text)[:6000]
        except Exception as e:
            page_text = f"(fetch failed: {e})"

    prompt = f"""You are helping a prop-trader extract account rules.
Firm: {firm_name}
URL: {firm_url}
Page text (first 6000 chars):
{page_text}

Extract the following fields as JSON (use null if not found):
{{
  "inactivity_limit": <int days>,
  "max_loss_pct": <float>,
  "daily_loss_pct": <float>,
  "profit_target_pct": <float>,
  "min_trading_days": <int>,
  "consistency_rule": "<string>",
  "other_rules": "<string>"
}}
Return ONLY valid JSON, no prose."""

    # 2) Try Claude first
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if anthropic_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=anthropic_key)
            msg = client.messages.create(
                model=os.environ.get("GUIDE_MODEL", "claude-haiku-5-5"),
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}],
            )
            raw_json = msg.content[0].text.strip()
            return json.loads(raw_json)
        except Exception:
            pass

    # 3) Try Gemini
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel(os.environ.get("GEMINI_MODEL", "gemini-2.0-flash"))
            resp = model.generate_content(prompt)
            raw_json = resp.text.strip()
            return json.loads(raw_json)
        except Exception:
            pass

    return {}


# ── Add / Edit form ──────────────────────────────────────────────────────────
def _account_form(existing: dict | None = None) -> dict | None:
    """
    Renders an add/edit form in an expander.
    Returns the new/updated account dict when saved, None otherwise.
    """
    is_edit = existing is not None
    label = _xl("تعديل الحساب", "Edit account") if is_edit else _xl("➕ إضافة حساب جديد", "➕ Add new account")
    with st.expander(label, expanded=not is_edit):
        # AI helper row
        st.caption(_xl("مساعد الذكاء الاصطناعي لاستخراج القواعد تلقائياً", "AI helper — auto-extract rules from the firm page"))
        ai_col1, ai_col2 = st.columns([2, 1])
        ai_firm_name = ai_col1.text_input(_xl("اسم الشركة", "Firm name"), value=existing.get("firm", "") if existing else "", key=f"ai_firm_{'edit' if is_edit else 'add'}")
        ai_firm_url = ai_col1.text_input(_xl("رابط صفحة القواعد", "Rules page URL"), value=existing.get("firm_url", "") if existing else "", key=f"ai_url_{'edit' if is_edit else 'add'}")
        ai_result: dict = {}
        if ai_col2.button(_xl("🤖 استخرج القواعد", "🤖 Extract rules"), key=f"ai_btn_{'edit' if is_edit else 'add'}"):
            with st.spinner(_xl("جاري الاستخراج…", "Extracting…")):
                ai_result = _ai_extract_rules(ai_firm_name, ai_firm_url)
            if ai_result:
                st.success(_xl("تم الاستخراج — راجع الحقول أدناه", "Extracted — review fields below"))
            else:
                st.warning(_xl("لم يتم الاستخراج — أدخل القواعد يدوياً", "Could not extract — enter manually"))

        st.divider()
        c1, c2 = st.columns(2)
        def v(key: str, default: Any = "") -> Any:
            return ai_result.get(key) if ai_result.get(key) is not None else (existing.get(key, default) if existing else default)

        name       = c1.text_input(_xl("اسم الحساب", "Account name"), value=v("name", ""), key=f"pf_name_{'e' if is_edit else 'a'}")
        firm       = c1.text_input(_xl("الشركة", "Firm"), value=v("firm", ai_firm_name), key=f"pf_firm_{'e' if is_edit else 'a'}")
        acc_url    = c1.text_input(_xl("رابط الحساب", "Account URL"), value=v("account_url", ""), key=f"pf_aurl_{'e' if is_edit else 'a'}")
        firm_url   = c1.text_input(_xl("رابط الشركة / القواعد", "Firm/rules URL"), value=v("firm_url", ai_firm_url), key=f"pf_furl_{'e' if is_edit else 'a'}")
        acc_type   = c2.selectbox(_xl("نوع الحساب", "Account type"),
                                   ["Instant", "Challenge (1-step)", "Challenge (2-step)"],
                                   index=["Instant", "Challenge (1-step)", "Challenge (2-step)"].index(v("account_type", "Instant")),
                                   key=f"pf_type_{'e' if is_edit else 'a'}")
        size       = c2.text_input(_xl("الحجم", "Size (e.g. 100K)"), value=v("size", ""), key=f"pf_size_{'e' if is_edit else 'a'}")
        currency   = c2.text_input(_xl("العملة", "Currency"), value=v("currency", "USD"), key=f"pf_cur_{'e' if is_edit else 'a'}")
        status     = c2.selectbox(_xl("الحالة", "Status"), ["active", "closed", "failed", "passed"],
                                   index=["active", "closed", "failed", "passed"].index(v("status", "active")),
                                   key=f"pf_stat_{'e' if is_edit else 'a'}")
        color      = c2.color_picker(_xl("اللون", "Color"), value=v("color", "#f0b429"), key=f"pf_col_{'e' if is_edit else 'a'}")

        c3, c4 = st.columns(2)
        purchase_date   = c3.text_input(_xl("تاريخ الشراء (YYYY-MM-DD)", "Purchase date (YYYY-MM-DD)"), value=v("purchase_date", ""), key=f"pf_pd_{'e' if is_edit else 'a'}")
        last_trade_date = c3.text_input(_xl("آخر صفقة (YYYY-MM-DD)", "Last trade date (YYYY-MM-DD)"), value=v("last_trade_date", ""), key=f"pf_ltd_{'e' if is_edit else 'a'}")
        inactivity_limit = c3.number_input(_xl("حد الخمول (يوم)", "Inactivity limit (days)"), min_value=1, max_value=365, value=int(v("inactivity_limit", 35)), key=f"pf_il_{'e' if is_edit else 'a'}")
        max_loss_pct    = c4.number_input(_xl("ماكس لوس %", "Max loss %"), 0.0, 100.0, float(v("max_loss_pct", 10.0)), 0.5, key=f"pf_ml_{'e' if is_edit else 'a'}")
        daily_loss_pct  = c4.number_input(_xl("خسارة يومية %", "Daily loss %"), 0.0, 100.0, float(v("daily_loss_pct", 5.0)), 0.5, key=f"pf_dl_{'e' if is_edit else 'a'}")
        profit_target   = c4.number_input(_xl("هدف الربح %", "Profit target %"), 0.0, 100.0, float(v("profit_target_pct", 0.0)), 0.5, key=f"pf_pt_{'e' if is_edit else 'a'}")
        min_days        = c4.number_input(_xl("أيام تداول دنيا", "Min trading days"), 0, 100, int(v("min_trading_days", 0)), key=f"pf_md_{'e' if is_edit else 'a'}")

        consistency = st.text_area(_xl("قاعدة الاتساق", "Consistency rule"), value=v("consistency_rule", ""), key=f"pf_cr_{'e' if is_edit else 'a'}", height=60)
        other_rules = st.text_area(_xl("قواعد أخرى", "Other rules"), value=v("other_rules", ""), key=f"pf_or_{'e' if is_edit else 'a'}", height=80)
        notes       = st.text_area(_xl("ملاحظات", "Notes"), value=v("notes", ""), key=f"pf_nt_{'e' if is_edit else 'a'}", height=60)

        save_btn = st.button(_xl("💾 حفظ", "💾 Save"), key=f"pf_save_{'e' if is_edit else 'a'}", type="primary")
        if save_btn:
            if not name:
                st.error(_xl("يجب إدخال اسم الحساب", "Account name is required"))
                return None
            new_acc: dict = {
                "id": existing["id"] if is_edit else str(uuid.uuid4())[:8],
                "name": name, "firm": firm, "account_url": acc_url, "firm_url": firm_url,
                "account_type": acc_type, "size": size, "currency": currency,
                "purchase_date": purchase_date, "last_trade_date": last_trade_date,
                "inactivity_limit": int(inactivity_limit),
                "max_loss_pct": float(max_loss_pct), "daily_loss_pct": float(daily_loss_pct),
                "profit_target_pct": float(profit_target), "min_trading_days": int(min_days),
                "consistency_rule": consistency, "other_rules": other_rules,
                "status": status, "color": color, "notes": notes,
            }
            return new_acc
    return None


# ── Main render entry point ──────────────────────────────────────────────────
def render_prop_firms() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)

    # Header
    st.markdown(
        f"<h2 style='margin:0 0 4px;font-size:20px;color:#e2e8f0'>"
        f"{'🏢 ' + _xl('حسابات بروب فيرم', 'Prop Firm Accounts')}</h2>"
        f"<p style='color:#64748b;font-size:12px;margin:0 0 12px'>"
        f"{_xl('تتبع الحسابات — العدادات، القواعد، والتنبيهات', 'Account tracker — timers, rules, and alerts')}"
        f"</p>",
        unsafe_allow_html=True,
    )

    accounts = _load_accounts()

    # Summary strip (active / expiring / closed)
    active = [a for a in accounts if a.get("status") == "active"]
    expiring = [a for a in active if (_days_to_inactivity(a) or 999) <= 7]
    closed = [a for a in accounts if a.get("status") in ("closed", "failed")]

    s1, s2, s3, s4 = st.columns(4)
    s1.metric(_xl("إجمالي", "Total"), len(accounts))
    s2.metric(_xl("نشطة", "Active"), len(active))
    s3.metric(_xl("تنتهي قريباً", "Expiring soon"), len(expiring), delta=None if not expiring else "⚠️")
    s4.metric(_xl("مغلقة", "Closed/failed"), len(closed))

    if expiring:
        st.warning(
            "⚠️ " + _xl(
                f"تنبيه: {', '.join(a['name'] for a in expiring)} قريبة من حد الخمول!",
                f"Warning: {', '.join(a['name'] for a in expiring)} nearing inactivity limit!"
            )
        )

    st.divider()

    # Filter bar
    fc1, fc2, fc3 = st.columns([2, 2, 2])
    filter_firm   = fc1.text_input(_xl("فلترة بالشركة", "Filter by firm"), key="pf_filter_firm", placeholder="Upcomers…")
    filter_status = fc2.selectbox(_xl("الحالة", "Status"), ["all", "active", "closed", "failed", "passed"],
                                   key="pf_filter_status",
                                   format_func=lambda s: _xl(
                                       {"all": "الكل", "active": "نشط", "closed": "مغلق", "failed": "فشل", "passed": "اجتاز"}.get(s, s),
                                       {"all": "All", "active": "Active", "closed": "Closed", "failed": "Failed", "passed": "Passed"}.get(s, s)))
    sort_by = fc3.selectbox(_xl("ترتيب بـ", "Sort by"),
                             ["name", "days_left", "status"],
                             format_func=lambda s: _xl(
                                 {"name": "الاسم", "days_left": "الأيام المتبقية", "status": "الحالة"}.get(s, s),
                                 {"name": "Name", "days_left": "Days left", "status": "Status"}.get(s, s)),
                             key="pf_sort")

    filtered = [a for a in accounts
                if (not filter_firm or filter_firm.lower() in a.get("firm", "").lower() or filter_firm.lower() in a.get("name", "").lower())
                and (filter_status == "all" or a.get("status") == filter_status)]

    if sort_by == "days_left":
        filtered.sort(key=lambda a: (_days_to_inactivity(a) or 9999) if a.get("status") == "active" else 9999)
    elif sort_by == "status":
        order = {"active": 0, "closed": 1, "failed": 2, "passed": 3}
        filtered.sort(key=lambda a: order.get(a.get("status", "active"), 9))
    else:
        filtered.sort(key=lambda a: a.get("name", ""))

    # Cards grid — 2-per-row on wide screens
    if not filtered:
        st.info(_xl("لا توجد حسابات تطابق الفلتر", "No accounts match the filter"))
    else:
        pairs = [filtered[i:i+2] for i in range(0, len(filtered), 2)]
        for pair in pairs:
            cols = st.columns(len(pair))
            for col, acc in zip(cols, pair):
                with col:
                    _render_card(acc, accounts.index(acc))
                    edit_key = f"pf_edit_btn_{acc['id']}"
                    del_key  = f"pf_del_btn_{acc['id']}"
                    ec, dc = st.columns(2)
                    if ec.button(_xl("✏️ تعديل", "✏️ Edit"), key=edit_key, use_container_width=True):
                        st.session_state[f"pf_editing_{acc['id']}"] = True
                    if dc.button(_xl("🗑 حذف", "🗑 Delete"), key=del_key, use_container_width=True):
                        accounts.remove(acc)
                        _save_accounts(accounts)
                        st.rerun()
                    if st.session_state.get(f"pf_editing_{acc['id']}"):
                        updated = _account_form(existing=acc)
                        if updated:
                            idx = next((i for i, a in enumerate(accounts) if a["id"] == acc["id"]), None)
                            if idx is not None:
                                accounts[idx] = updated
                                _save_accounts(accounts)
                                st.session_state.pop(f"pf_editing_{acc['id']}", None)
                                st.rerun()

    st.divider()

    # Add new account form
    new_acc = _account_form(existing=None)
    if new_acc:
        accounts.append(new_acc)
        _save_accounts(accounts)
        st.rerun()

    st.divider()

    # Backup / restore
    with st.expander(_xl("💾 نسخ احتياطي / استعادة", "💾 Backup / Restore")):
        st.download_button(
            _xl("⬇️ تنزيل JSON", "⬇️ Download JSON"),
            data=json.dumps(accounts, ensure_ascii=False, indent=2),
            file_name="prop_accounts.json",
            mime="application/json",
            key="pf_dl_btn",
        )
        uploaded = st.file_uploader(_xl("رفع JSON", "Upload JSON"), type=["json"], key="pf_upload")
        if uploaded:
            try:
                loaded = json.load(uploaded)
                if isinstance(loaded, list):
                    _save_accounts(loaded)
                    st.success(_xl("تم الاستعادة", "Restored"))
                    st.rerun()
                else:
                    st.error(_xl("ملف غير صالح", "Invalid file"))
            except Exception as e:
                st.error(str(e))

    st.caption(
        _xl(
            "ملاحظة: البيانات محفوظة في الجلسة (session state). للحفظ الدائم، استخدم زر التنزيل.",
            "Note: data is in session state. For persistence, use the download button.",
        )
    )
