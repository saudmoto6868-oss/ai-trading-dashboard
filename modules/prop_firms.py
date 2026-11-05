"""
PROP FIRMS TRACKER  (rewrite 2026-11-04)
=========================================
PAGE 10 in 6868 X dashboard.

Navigation model
----------------
- List view  : compact cards, one per account.  Click → Account detail view.
- Detail view: 5 tabs (Overview / Live / Rules / Calendar / Equity).
  "Live" tab opens the account URL in the same browser tab (window.location) OR
  shows an iframe attempt.  A prominent "Open in browser" button always present.
- Back button returns to list.

Data stored in st.session_state["prop_accounts"] (JSON-safe dicts).
"""

from __future__ import annotations

import json
import uuid
from datetime import date
from typing import Any

import streamlit as st


# ── Bookmarklet JS (minified template) ───────────────────────────────────────
# Injected into the page at app.upcomers.com to scrape visible data and
# store it in localStorage under key "pf_scraped_<account_id>".
# The dashboard reads it back via a small HTML component.

_BOOKMARKLET_TEMPLATE = r"""
(function(){{
  var accId="{acc_id}";
  var d={{}};
  // Total PnL
  var pnlEl=document.querySelector('[class*="pnl"],[class*="balance"],[class*="equity"]');
  d.total_pnl=(pnlEl&&pnlEl.innerText.trim())||"";
  // Last trade line
  var els=document.querySelectorAll('*');
  for(var i=0;i<els.length;i++){{
    var t=els[i].childNodes;
    for(var j=0;j<t.length;j++){{
      if(t[j].nodeType===3){{
        var tx=t[j].textContent;
        if(tx.match(/last trade/i)){{d.last_trade_line=tx.trim();break;}}
        if(tx.match(/no closed trades/i)){{d.last_trade_line=tx.trim();break;}}
      }}
    }}
    if(d.last_trade_line)break;
  }}
  // Win rates by session
  var wr={{}};
  document.querySelectorAll('[class*="session"],[class*="win"]').forEach(function(el){{
    var txt=el.innerText||"";
    var m=txt.match(/(Asia|Night|London|NY PM|NY AM)[^\d]*(\d+\.?\d*)\s*%/gi);
    if(m)m.forEach(function(s){{
      var p=s.match(/(Asia|Night|London|NY PM|NY AM)[^\d]*(\d+\.?\d*)/i);
      if(p)wr[p[1]]=parseFloat(p[2]);
    }});
  }});
  d.win_rates=wr;
  // Account cards
  var cards=[];
  document.querySelectorAll('[class*="account-card"],[class*="accountCard"],[class*="account_card"]').forEach(function(c){{
    cards.push(c.innerText.replace(/\s+/g,' ').trim().slice(0,200));
  }});
  d.account_cards=cards;
  // Raw page text snapshot (first 3000 chars)
  d.page_text=document.body.innerText.slice(0,3000);
  d.url=location.href;
  d.scraped_at=new Date().toISOString();
  localStorage.setItem("pf_scraped_"+accId, JSON.stringify(d));
  alert("✅ Upcomers data saved for account "+accId+".\nReturn to your dashboard and click Refresh.");
}})();
"""


def _bookmarklet_href(acc_id: str) -> str:
    """Return a javascript: href for the bookmarklet."""
    code = _BOOKMARKLET_TEMPLATE.format(acc_id=acc_id)
    # Remove newlines for href
    flat = code.replace("\n", "").replace("  ", " ")
    import urllib.parse
    return "javascript:" + urllib.parse.quote(flat, safe="(){}[];:.,!?'\"/=+-*&|<>@#$%^~`\\ ")


def _read_local_storage(acc_id: str) -> dict | None:
    """
    Inject a small HTML component that reads localStorage["pf_scraped_<acc_id>"]
    and posts it to Streamlit via a query-param trick.
    Returns None if not yet available in this run.
    """
    key = f"pf_scraped_{acc_id}"
    # We store the result in session_state once read
    ss_key = f"pf_live_{acc_id}"
    # Render a tiny iframe that reads localStorage and renders JSON in the page
    # Streamlit components can't directly return values without bi-directional JS;
    # we use st.query_params workaround: component writes to a hidden input that
    # the user copies, OR we just display the data inline via innerHTML.
    # Simplest: render HTML that reads localStorage and displays it; we also
    # let the user click "Load" to push into session_state via a form.
    html = f"""
<div id="pf_ls_root_{acc_id}" style="font-size:11px;color:#94a3b8">
  <span id="pf_ls_status">Loading from local storage…</span>
</div>
<script>
(function(){{
  var key="{key}";
  var raw=null;
  try{{raw=localStorage.getItem(key);}}catch(e){{}}
  var el=document.getElementById("pf_ls_status");
  if(!raw){{
    el.innerHTML='<span style="color:#475569">No scraped data yet — use the bookmarklet on the Upcomers page first.</span>';
    return;
  }}
  var d=JSON.parse(raw);
  var html='<div style="background:#0f1217;border:1px solid #1e2530;border-radius:6px;padding:8px 10px;margin-top:4px">';
  html+='<div style="color:#2dd4bf;font-weight:600;margin-bottom:4px">📊 Last scraped: '+d.scraped_at+'</div>';
  if(d.total_pnl)html+='<div><span style="color:#475569">Total PnL: </span><span style="color:#10b981;font-weight:700">'+d.total_pnl+'</span></div>';
  if(d.last_trade_line)html+='<div><span style="color:#475569">Last trade: </span>'+d.last_trade_line+'</div>';
  if(d.win_rates&&Object.keys(d.win_rates).length){{
    html+='<div style="margin-top:4px;color:#64748b">Win rates by session:</div>';
    Object.entries(d.win_rates).forEach(function(kv){{
      html+='<div style="margin-left:8px"><span style="color:#475569">'+kv[0]+': </span><span style="color:#a3e635">'+kv[1]+'%</span></div>';
    }});
  }}
  html+='</div>';
  el.innerHTML=html;
}})();
</script>
"""
    import streamlit.components.v1 as _comp
    _comp.html(html, height=220, scrolling=False)
    return None

# ── i18n ─────────────────────────────────────────────────────────────────────
try:
    from modules.i18n import L
except Exception:
    def L(x: str) -> str:
        return x

def _xl(ar: str, en: str) -> str:
    return ar if st.session_state.get("ws_lang", "en") == "ar" else en


# ── Default accounts ──────────────────────────────────────────────────────────
_DEFAULT_ACCOUNTS: list[dict] = [
    {
        "id": "upcomers-ignite-100k",
        "name": "Ignite 1 Step 100K",
        "firm": "Upcomers",
        "account_url": "https://app.upcomers.com/en/accounts/699789",
        "firm_url": "https://app.upcomers.com",
        "account_type": "Challenge (1-step)",
        "size": "100K", "currency": "USD",
        "purchase_date": "", "last_trade_date": "2026-11-02",
        "inactivity_limit": 35,
        "max_loss_pct": 10.0, "daily_loss_pct": 5.0, "profit_target_pct": 8.0,
        "min_trading_days": 0, "consistency_rule": "",
        "other_rules": "35-day inactivity rule. CFD · cTrader. Account #699789.",
        "status": "active", "color": "#10b981",
        "notes": "Active Challenge — balance $102,061.97 (2026-11-04)",
    },
    {
        "id": "upcomers-phoenix-100k",
        "name": "Phoenix 2 Step LEGACY 100K",
        "firm": "Upcomers",
        "account_url": "https://app.upcomers.com/en/accounts/675580",
        "firm_url": "https://app.upcomers.com",
        "account_type": "Challenge (2-step)",
        "size": "100K", "currency": "USD",
        "purchase_date": "", "last_trade_date": "2026-11-02",
        "inactivity_limit": 35,
        "max_loss_pct": 10.0, "daily_loss_pct": 5.0, "profit_target_pct": 8.0,
        "min_trading_days": 0, "consistency_rule": "",
        "other_rules": "35-day inactivity rule. CFD · MT5. Account #675580.",
        "status": "active", "color": "#a855f7",
        "notes": "Active Challenge — balance $99,419.41 (2026-11-04)",
    },
    {
        "id": "upcomers-vanguard-100k",
        "name": "Vanguard 100K #689771",
        "firm": "Upcomers",
        "account_url": "https://app.upcomers.com/en/accounts/689771",
        "firm_url": "https://app.upcomers.com",
        "account_type": "Instant",
        "size": "100K", "currency": "USD",
        "purchase_date": "2026-09-12", "last_trade_date": "",
        "inactivity_limit": 35,
        "max_loss_pct": 10.0, "daily_loss_pct": 5.0, "profit_target_pct": 0.0,
        "min_trading_days": 0, "consistency_rule": "",
        "other_rules": "CFD/MT5. Appeal ticket #152349628.",
        "status": "closed", "color": "#ef4444",
        "notes": "Closed for inactivity 2026-10-23. Appeal pending.",
    },
    {
        "id": "upcomers-vanguard-10k",
        "name": "Vanguard 10K #689772",
        "firm": "Upcomers",
        "account_url": "https://app.upcomers.com/en/accounts/689772",
        "firm_url": "https://app.upcomers.com",
        "account_type": "Instant",
        "size": "10K", "currency": "USD",
        "purchase_date": "2026-09-12", "last_trade_date": "",
        "inactivity_limit": 35,
        "max_loss_pct": 10.0, "daily_loss_pct": 5.0, "profit_target_pct": 0.0,
        "min_trading_days": 0, "consistency_rule": "",
        "other_rules": "Perpetuals. Bonus account. Closed 2026-10-23.",
        "status": "closed", "color": "#ef4444",
        "notes": "Closed for inactivity 2026-10-23. Appeal pending.",
    },
]


# ── Session helpers ───────────────────────────────────────────────────────────
def _load_accounts() -> list[dict]:
    if "prop_accounts" not in st.session_state:
        st.session_state["prop_accounts"] = json.loads(json.dumps(_DEFAULT_ACCOUNTS))
    return st.session_state["prop_accounts"]

def _save_accounts(accounts: list[dict]) -> None:
    st.session_state["prop_accounts"] = accounts


# ── Date math ─────────────────────────────────────────────────────────────────
def _days_since(iso: str) -> int | None:
    if not iso:
        return None
    try:
        return (date.today() - date.fromisoformat(iso)).days
    except Exception:
        return None

def _days_left(acc: dict) -> int | None:
    limit = int(acc.get("inactivity_limit") or 35)
    ref = acc.get("last_trade_date") or acc.get("purchase_date") or ""
    since = _days_since(ref)
    return None if since is None else limit - since


# ── CSS ───────────────────────────────────────────────────────────────────────
_CSS = """
<style>
/* ── compact card list ── */
.pfc-grid{display:flex;flex-wrap:wrap;gap:10px;margin-top:6px}
.pfc-card{
  background:#0f1217;border:1px solid #1e2530;border-radius:8px;
  padding:10px 12px;cursor:pointer;transition:border-color .15s;
  flex:1 1 240px;min-width:220px;max-width:340px;
  box-shadow:0 1px 4px #0004;
}
.pfc-card:hover{border-color:#334155}
.pfc-card-top{display:flex;align-items:center;gap:8px;margin-bottom:6px}
.pfc-dot{width:9px;height:9px;border-radius:50%;flex-shrink:0}
.pfc-name{font-size:13px;font-weight:600;color:#e2e8f0}
.pfc-badge{
  margin-left:auto;font-size:9px;padding:1px 6px;border-radius:3px;
  font-weight:700;text-transform:uppercase;letter-spacing:.05em
}
.pfc-b-active{background:#14532d;color:#bbf7d0}
.pfc-b-closed{background:#450a0a;color:#fecaca}
.pfc-b-failed{background:#431407;color:#fed7aa}
.pfc-b-passed{background:#0c1a2e;color:#bae6fd}
.pfc-meta{font-size:11px;color:#475569;margin-bottom:4px}
.pfc-timer-ok{color:#2dd4bf;font-size:11px;font-weight:600}
.pfc-timer-warn{color:#f0b429;font-size:11px;font-weight:600}
.pfc-timer-danger{color:#ef4444;font-size:11px;font-weight:600;animation:pfpls 1s infinite}
.pfc-timer-na{color:#334155;font-size:11px}
@keyframes pfpls{0%,100%{opacity:1}50%{opacity:.4}}

/* ── detail view ── */
.pfd-header{
  display:flex;align-items:center;gap:10px;
  padding:10px 0 8px;border-bottom:1px solid #1e2530;margin-bottom:10px
}
.pfd-title{font-size:16px;font-weight:700;color:#e2e8f0}
.pfd-sub{font-size:11px;color:#64748b;margin-top:1px}
.pfd-open-btn{
  margin-left:auto;background:#1d4ed8;color:#fff;border:none;
  padding:5px 14px;border-radius:5px;font-size:11px;font-weight:600;
  cursor:pointer;text-decoration:none;display:inline-block
}
.pfd-open-btn:hover{background:#1e40af}
.pfd-row{display:flex;gap:6px;margin-bottom:3px;align-items:flex-start;font-size:11px}
.pfd-lbl{color:#475569;min-width:100px;flex-shrink:0}
.pfd-val{color:#cbd5e1}
.pfd-val-hi{color:#e2e8f0;font-weight:600}
.pfd-sep{border:none;border-top:1px solid #1e2530;margin:6px 0}
.pfd-warn{background:#451a03;color:#fdba74;border-radius:5px;padding:5px 9px;font-size:11px;margin-bottom:6px}
.pfd-danger{background:#450a0a;color:#fca5a5;border-radius:5px;padding:5px 9px;font-size:11px;animation:pfpls 1.2s infinite;margin-bottom:6px}
</style>
"""


# ── Badge & timer helpers ─────────────────────────────────────────────────────
def _badge_html(status: str) -> str:
    cls = {"active":"pfc-b-active","closed":"pfc-b-closed","failed":"pfc-b-failed","passed":"pfc-b-passed"}.get(status,"pfc-b-active")
    lbl = {"active":_xl("نشط","Active"),"closed":_xl("مغلق","Closed"),"failed":_xl("فشل","Failed"),"passed":_xl("اجتاز","Passed")}.get(status,status)
    return f'<span class="pfc-badge {cls}">{lbl}</span>'

def _timer_text(acc: dict) -> tuple[str, str]:
    """Returns (css_class, display_text)."""
    if acc.get("status") in ("closed","failed","passed"):
        return "pfc-timer-na", _xl("— مغلق","— closed")
    dl = _days_left(acc)
    if dl is None:
        return "pfc-timer-na", _xl("لا تاريخ","no date")
    if dl <= 0:
        return "pfc-timer-danger", _xl(f"🚨 تجاوز {abs(dl)}ي",f"🚨 {abs(dl)}d over limit")
    if dl <= 3:
        return "pfc-timer-danger", _xl(f"🚨 {dl} أيام",f"🚨 {dl}d left")
    if dl <= 7:
        return "pfc-timer-warn", _xl(f"⚠️ {dl} أيام",f"⚠️ {dl}d left")
    return "pfc-timer-ok", _xl(f"✓ {dl} يوم",f"✓ {dl}d left")


# ── Compact list card ─────────────────────────────────────────────────────────
def _list_card_html(acc: dict) -> str:
    color = acc.get("color","#f0b429")
    t_cls, t_txt = _timer_text(acc)
    ds = _days_since(acc.get("last_trade_date") or "")
    trade_note = _xl(f"آخر صفقة: {ds}ي","f{ds}d since trade") if ds is not None else _xl("لا صفقات","no trades")
    size_txt = f'{acc.get("size","?")} {acc.get("currency","USD")}'
    return (
        f'<div class="pfc-card-top">'
        f'  <div class="pfc-dot" style="background:{color}"></div>'
        f'  <span class="pfc-name">{acc.get("name","Account")}</span>'
        f'  {_badge_html(acc.get("status","active"))}'
        f'</div>'
        f'<div class="pfc-meta">{acc.get("firm","?")} · {size_txt}</div>'
        f'<div class="pfc-meta">{trade_note}</div>'
        f'<div class="{t_cls}">{t_txt}</div>'
    )


# ── Detail view tabs content ──────────────────────────────────────────────────
def _detail_overview(acc: dict) -> None:
    rows = [
        (_xl("الشركة","Firm"), acc.get("firm","—")),
        (_xl("النوع","Type"), acc.get("account_type","—")),
        (_xl("الحجم","Size"), f'{acc.get("size","—")} {acc.get("currency","USD")}'),
        (_xl("تاريخ الشراء","Purchased"), acc.get("purchase_date") or "—"),
        (_xl("آخر صفقة","Last trade"), acc.get("last_trade_date") or _xl("لا يوجد","none")),
        (_xl("ملاحظات","Notes"), acc.get("notes","—")),
    ]
    html = "".join(
        f'<div class="pfd-row"><span class="pfd-lbl">{k}</span><span class="pfd-val">{v}</span></div>'
        for k, v in rows if v and v != "—"
    )
    st.markdown(html, unsafe_allow_html=True)

def _detail_live(acc: dict) -> None:
    url = acc.get("account_url","")
    acc_id = acc.get("id","unknown")
    if not url:
        st.info(_xl("لا يوجد رابط للحساب","No account URL set — add it via Edit"))
        return

    # ── Open button ──
    st.markdown(
        f'<a href="{url}" target="_blank" rel="noopener"'
        f' style="display:inline-block;background:#1d4ed8;color:#fff;padding:7px 18px;'
        f'border-radius:6px;font-size:12px;font-weight:600;text-decoration:none;margin-bottom:12px">'
        f'🔗 {_xl("فتح صفحة الحساب","Open account page")}</a>',
        unsafe_allow_html=True,
    )

    # ── Bookmarklet section ──
    import urllib.parse as _up
    bm_code = _BOOKMARKLET_TEMPLATE.format(acc_id=acc_id).replace("\n","").replace("  "," ")
    bm_href = "javascript:" + _up.quote(bm_code, safe="(){}[];:.,!?'\"/=+-*&|<>@#$%^~`\\ ")

    st.markdown(
        f"""
<div style="background:#0f1217;border:1px solid #1e2530;border-radius:8px;padding:12px 14px;margin-bottom:12px">
  <div style="font-size:12px;font-weight:600;color:#2dd4bf;margin-bottom:6px">
    📌 {_xl("بوكماركلت — سحب بيانات الحساب","Bookmarklet — Scrape account data")}
  </div>
  <div style="font-size:11px;color:#94a3b8;margin-bottom:8px">
    {_xl(
      "1. افتح صفحة الحساب في المتصفح (الزرار فوق)<br>2. في نفس الوقت افتح الـ Bookmarks bar<br>3. اسحب الرابط ده للـ Bookmarks bar أو اعمل bookmark جديد وحط الكود كـ URL<br>4. لما تكون على صفحة الحساب، اضغط الـ bookmarklet — هيسحب البيانات ويحفظها هنا",
      "1. Open the account page (button above)<br>2. Open your browser's Bookmarks bar<br>3. Drag this link to the Bookmarks bar, or create a new bookmark and paste the code as URL<br>4. While on the account page, click the bookmarklet — it scrapes data and saves it here"
    )}
  </div>
  <a href="{bm_href}"
     style="display:inline-block;background:#1e3a5f;color:#38bdf8;padding:5px 14px;
            border-radius:5px;font-size:11px;font-weight:600;text-decoration:none;
            border:1px solid #1e4976;cursor:pointer">
    🔖 {_xl(f"Scrape: {acc.get('name',acc_id)}", f"Scrape: {acc.get('name',acc_id)}")}
  </a>
  <span style="font-size:10px;color:#475569;margin-left:10px">
    {_xl("اسحب هنا للـ bookmarks bar","Drag to bookmarks bar")} ↑
  </span>
</div>
        """,
        unsafe_allow_html=True,
    )

    # ── Scraped data display (reads localStorage) ──
    st.markdown(
        f'<div style="font-size:11px;font-weight:600;color:#64748b;margin-bottom:4px">'
        f'{_xl("آخر بيانات مسحوبة","Last scraped data")}</div>',
        unsafe_allow_html=True,
    )
    _read_local_storage(acc_id)

def _detail_rules(acc: dict) -> None:
    rows = [
        (_xl("الحد الأقصى للخسارة","Max drawdown"), f'{acc.get("max_loss_pct",0):.1f}%'),
        (_xl("خسارة اليوم","Daily loss limit"), f'{acc.get("daily_loss_pct",0):.1f}%'),
        (_xl("هدف الربح","Profit target"),
         f'{acc.get("profit_target_pct",0):.1f}%' if acc.get("profit_target_pct") else _xl("لا يوجد (Instant)","None (Instant)")),
        (_xl("أيام تداول دنيا","Min trading days"), str(acc.get("min_trading_days",0)) or "—"),
        (_xl("قاعدة الاتساق","Consistency"), acc.get("consistency_rule") or "—"),
        (_xl("قواعد أخرى","Other rules"), acc.get("other_rules") or "—"),
        (_xl("حد الخمول","Inactivity limit"), f'{acc.get("inactivity_limit",35)} {_xl("يوم","days")}'),
    ]
    html = "".join(
        f'<div class="pfd-row"><span class="pfd-lbl">{k}</span><span class="pfd-val">{v}</span></div>'
        for k, v in rows
    )
    st.markdown(html, unsafe_allow_html=True)

def _detail_calendar(acc: dict) -> None:
    st.caption(_xl(
        "التقويم بيحتاج API بتاع الشركة — مش متاح دلوقتي.",
        "Calendar requires firm API — not available yet."
    ))
    if acc.get("last_trade_date"):
        st.markdown(f'**{_xl("آخر صفقة","Last trade")}:** `{acc["last_trade_date"]}`')
    if acc.get("purchase_date"):
        st.markdown(f'**{_xl("تاريخ الشراء","Purchase date")}:** `{acc["purchase_date"]}`')

def _detail_equity(acc: dict) -> None:
    st.caption(_xl(
        "منحنى الأسهم بيحتاج API بتاع الشركة — مش متاح دلوقتي.",
        "Equity curve requires firm API — not available yet."
    ))


# ── Full detail page ──────────────────────────────────────────────────────────
def _render_detail(acc: dict, accounts: list[dict]) -> None:
    color = acc.get("color","#f0b429")
    t_cls, t_txt = _timer_text(acc)
    url = acc.get("account_url","")

    # Back button
    if st.button(f"← {_xl('رجوع','Back')}", key="pf_back"):
        st.session_state.pop("pf_open_id", None)
        st.rerun()

    # Header
    open_btn = (
        f'<a href="{url}" target="_blank" rel="noopener" class="pfd-open-btn">'
        f'🔗 {_xl("فتح في المتصفح","Open in browser")}</a>'
        if url else ""
    )
    st.markdown(
        f'<div class="pfd-header">'
        f'  <div class="pfc-dot" style="background:{color};width:12px;height:12px"></div>'
        f'  <div>'
        f'    <div class="pfd-title">{acc.get("name","Account")}</div>'
        f'    <div class="pfd-sub">{acc.get("firm","?")} · {acc.get("size","?")} {acc.get("currency","USD")} · {acc.get("account_type","")}</div>'
        f'  </div>'
        f'  {_badge_html(acc.get("status","active"))}'
        f'  {open_btn}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Timer alert banner
    dl = _days_left(acc)
    if acc.get("status") == "active":
        if dl is not None and dl <= 0:
            st.markdown(f'<div class="pfd-danger">🚨 {_xl(f"تجاوزت حد الخمول بـ {abs(dl)} يوم!",f"Inactivity limit exceeded by {abs(dl)} day(s)!")}</div>', unsafe_allow_html=True)
        elif dl is not None and dl <= 7:
            st.markdown(f'<div class="pfd-warn">⚠️ {_xl(f"{dl} أيام متبقية قبل إغلاق الحساب بسبب الخمول.",f"{dl} day(s) left before inactivity close.")}</div>', unsafe_allow_html=True)

    # Stats strip — using plain HTML to avoid Streamlit Metric component import issues
    ds_trade = _days_since(acc.get("last_trade_date") or "")
    stats = [
        (_xl("فضل","Days left"),          f"{dl}d" if dl is not None else "—",   t_cls),
        (_xl("منذ آخر صفقة","Last trade"), f"{ds_trade}d" if ds_trade is not None else "—", ""),
        (_xl("حد الخسارة","Max loss"),     f'{acc.get("max_loss_pct",0):.0f}%',  ""),
        (_xl("خسارة يوم","Daily loss"),    f'{acc.get("daily_loss_pct",0):.0f}%', ""),
    ]
    stat_html = '<div style="display:flex;gap:12px;margin-bottom:8px">'
    for lbl, val, cls in stats:
        vc = "#ef4444" if cls == "pf-timer-red" else ("#f59e0b" if cls == "pf-timer-amber" else "#2dd4bf")
        stat_html += (
            f'<div style="flex:1;background:#0f1217;border:1px solid #1e2530;border-radius:6px;'
            f'padding:8px 10px;min-width:70px">'
            f'<div style="font-size:10px;color:#64748b;margin-bottom:2px">{lbl}</div>'
            f'<div style="font-size:18px;font-weight:700;color:{vc}">{val}</div>'
            f'</div>'
        )
    stat_html += '</div>'
    st.markdown(stat_html, unsafe_allow_html=True)

    st.divider()

    # Tabs
    t_overview, t_live, t_rules, t_cal, t_equity = st.tabs([
        _xl("نظرة عامة","Overview"),
        _xl("🔗 الحساب","🔗 Live"),
        _xl("القواعد","Rules"),
        _xl("التقويم","Calendar"),
        _xl("منحنى الأسهم","Equity"),
    ])
    with t_overview: _detail_overview(acc)
    with t_live:     _detail_live(acc)
    with t_rules:    _detail_rules(acc)
    with t_cal:      _detail_calendar(acc)
    with t_equity:   _detail_equity(acc)

    st.divider()

    # Edit / Delete
    ec, dc = st.columns([1,1])
    if ec.button(_xl("✏️ تعديل الحساب","✏️ Edit account"), key="pf_det_edit"):
        st.session_state["pf_editing_detail"] = True
    if dc.button(_xl("🗑 حذف","🗑 Delete"), key="pf_det_del", type="secondary"):
        st.session_state["pf_confirm_del"] = acc["id"]

    if st.session_state.get("pf_confirm_del") == acc["id"]:
        st.warning(_xl("متأكد؟ الحذف نهائي.","Confirm delete? This is permanent."))
        if st.button(_xl("آه احذف","Yes delete"), key="pf_det_del_confirm"):
            accounts.remove(acc)
            _save_accounts(accounts)
            st.session_state.pop("pf_open_id", None)
            st.session_state.pop("pf_confirm_del", None)
            st.rerun()
        if st.button(_xl("لا","Cancel"), key="pf_det_del_cancel"):
            st.session_state.pop("pf_confirm_del", None)
            st.rerun()

    if st.session_state.get("pf_editing_detail"):
        updated = _account_form(existing=acc)
        if updated is not None:
            idx = next((i for i,a in enumerate(accounts) if a["id"]==acc["id"]), None)
            if idx is not None:
                accounts[idx] = updated
                _save_accounts(accounts)
            st.session_state.pop("pf_editing_detail", None)
            st.rerun()


# ── Account form (add / edit) ─────────────────────────────────────────────────
def _account_form(existing: dict | None = None) -> dict | None:
    is_edit = existing is not None
    def v(k, default=""):
        return existing.get(k, default) if is_edit else default
    pfx = "pf_edit" if is_edit else "pf_add"

    with st.form(key=f"{pfx}_form"):
        st.markdown(f"**{_xl('تعديل الحساب','Edit account') if is_edit else _xl('إضافة حساب جديد','Add new account')}**")
        c1, c2 = st.columns(2)
        name       = c1.text_input(_xl("اسم الحساب","Account name"), value=v("name"), key=f"{pfx}_name")
        firm       = c2.text_input(_xl("اسم الشركة","Firm name"), value=v("firm","Upcomers"), key=f"{pfx}_firm")
        acc_url    = c1.text_input(_xl("رابط الحساب","Account URL"), value=v("account_url"), key=f"{pfx}_aurl")
        firm_url   = c2.text_input(_xl("رابط الشركة","Firm URL"), value=v("firm_url"), key=f"{pfx}_furl")
        acc_type   = c1.selectbox(_xl("نوع الحساب","Account type"),
                                   ["Instant","Challenge (1-step)","Challenge (2-step)"],
                                   index=["Instant","Challenge (1-step)","Challenge (2-step)"].index(v("account_type","Instant")),
                                   key=f"{pfx}_type")
        size       = c2.text_input(_xl("الحجم","Size"), value=v("size","100K"), key=f"{pfx}_size")
        pdate      = c1.text_input(_xl("تاريخ الشراء (YYYY-MM-DD)","Purchase date (YYYY-MM-DD)"), value=v("purchase_date"), key=f"{pfx}_pdate")
        tdate      = c2.text_input(_xl("آخر صفقة (YYYY-MM-DD)","Last trade (YYYY-MM-DD)"), value=v("last_trade_date"), key=f"{pfx}_tdate")
        inact      = c1.number_input(_xl("حد الخمول (يوم)","Inactivity limit (days)"), value=int(v("inactivity_limit",35)), min_value=1, max_value=365, key=f"{pfx}_inact")
        status     = c2.selectbox(_xl("الحالة","Status"),["active","closed","failed","passed"],
                                   index=["active","closed","failed","passed"].index(v("status","active")),
                                   key=f"{pfx}_status")
        max_loss   = c1.number_input(_xl("حد الخسارة %","Max loss %"), value=float(v("max_loss_pct",10.0)), key=f"{pfx}_ml")
        daily_loss = c2.number_input(_xl("خسارة اليوم %","Daily loss %"), value=float(v("daily_loss_pct",5.0)), key=f"{pfx}_dl")
        profit_tgt = c1.number_input(_xl("هدف الربح %","Profit target %"), value=float(v("profit_target_pct",0.0)), key=f"{pfx}_pt")
        min_days   = c2.number_input(_xl("أيام تداول دنيا","Min trading days"), value=int(v("min_trading_days",0)), min_value=0, key=f"{pfx}_md")
        color      = c1.color_picker(_xl("لون الحساب","Account color"), value=v("color","#f0b429"), key=f"{pfx}_col")
        cons_rule  = st.text_input(_xl("قاعدة الاتساق","Consistency rule"), value=v("consistency_rule"), key=f"{pfx}_cons")
        other      = st.text_area(_xl("قواعد أخرى","Other rules"), value=v("other_rules"), height=60, key=f"{pfx}_other")
        notes      = st.text_area(_xl("ملاحظات","Notes"), value=v("notes"), height=50, key=f"{pfx}_notes")

        submitted = st.form_submit_button(_xl("حفظ","Save"))
        if submitted:
            if not name.strip():
                st.error(_xl("اسم الحساب مطلوب","Account name required"))
                return None
            return {
                "id": v("id", str(uuid.uuid4())),
                "name": name.strip(), "firm": firm.strip(),
                "account_url": acc_url.strip(), "firm_url": firm_url.strip(),
                "account_type": acc_type, "size": size.strip(), "currency": "USD",
                "purchase_date": pdate.strip(), "last_trade_date": tdate.strip(),
                "inactivity_limit": int(inact), "status": status,
                "max_loss_pct": float(max_loss), "daily_loss_pct": float(daily_loss),
                "profit_target_pct": float(profit_tgt), "min_trading_days": int(min_days),
                "consistency_rule": cons_rule.strip(), "other_rules": other.strip(),
                "color": color, "notes": notes.strip(),
            }
    return None


# ── AI rules extractor ────────────────────────────────────────────────────────
def _ai_extract_rules(firm_name: str, firm_url: str) -> dict:
    """Fetch firm page and extract rules via Claude or Gemini. Returns partial dict."""
    import urllib.request, re as _re
    raw_text = ""
    if firm_url:
        try:
            req = urllib.request.Request(firm_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as r:
                html = r.read().decode("utf-8", errors="ignore")[:60000]
            raw_text = _re.sub(r"<[^>]+>", " ", html)
            raw_text = _re.sub(r"\s{3,}", "  ", raw_text)[:8000]
        except Exception:
            pass

    prompt = f"""Extract prop firm trading rules from this text.
Firm: {firm_name}
URL: {firm_url}
Text: {raw_text[:5000]}

Return ONLY valid JSON with these keys (numbers as floats/ints):
max_loss_pct, daily_loss_pct, profit_target_pct, min_trading_days,
consistency_rule, other_rules, inactivity_limit, account_type"""

    # Try Claude
    try:
        import anthropic
        api_key = st.secrets.get("ANTHROPIC_API_KEY","")
        if api_key:
            client = anthropic.Anthropic(api_key=api_key)
            resp = client.messages.create(
                model=st.secrets.get("GUIDE_MODEL","claude-haiku-4-5-20251001"),
                max_tokens=512,
                messages=[{"role":"user","content":prompt}],
            )
            import json as _json
            txt = resp.content[0].text
            m = __import__("re").search(r"\{.*\}", txt, __import__("re").DOTALL)
            if m:
                return _json.loads(m.group())
    except Exception:
        pass

    # Try Gemini
    try:
        import google.generativeai as genai
        api_key = st.secrets.get("GEMINI_API_KEY","")
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(st.secrets.get("GEMINI_MODEL","gemini-1.5-flash"))
            resp = model.generate_content(prompt)
            import json as _json, re as _re2
            m = _re2.search(r"\{.*\}", resp.text, _re2.DOTALL)
            if m:
                return _json.loads(m.group())
    except Exception:
        pass

    return {}


# ── Main render entry ─────────────────────────────────────────────────────────
def render_prop_firms() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
    accounts = _load_accounts()

    # ── Detail view ──────────────────────────────────────────────────────────
    open_id = st.session_state.get("pf_open_id")
    if open_id:
        acc = next((a for a in accounts if a["id"] == open_id), None)
        if acc:
            _render_detail(acc, accounts)
            return
        else:
            st.session_state.pop("pf_open_id", None)

    # ── List view ────────────────────────────────────────────────────────────

    # Header + summary strip
    active_lst   = [a for a in accounts if a.get("status") == "active"]
    expiring_lst = [a for a in active_lst if (_days_left(a) or 999) <= 7]
    closed_lst   = [a for a in accounts if a.get("status") in ("closed","failed")]

    h1, h2, h3 = st.columns([3,1,1])
    h1.markdown(
        f"<div style='font-size:17px;font-weight:700;color:#e2e8f0'>"
        f"🏢 {_xl('حسابات بروب فيرم','Prop Firm Accounts')}</div>"
        f"<div style='font-size:11px;color:#475569'>"
        f"{_xl('تتبع الحسابات — العدادات، القواعد، والتنبيهات','Account tracker — timers, rules, alerts')}"
        f"</div>",
        unsafe_allow_html=True,
    )
    h2.metric(_xl("نشطة","Active"), len(active_lst))
    h3.metric(_xl("تنتهي قريباً","Expiring ≤7d"), len(expiring_lst))

    if expiring_lst:
        st.error("🚨 " + _xl(
            f"{', '.join(a['name'] for a in expiring_lst)} — قريبة من حد الخمول!",
            f"{', '.join(a['name'] for a in expiring_lst)} — nearing inactivity limit!"
        ))

    st.divider()

    # Filter bar (compact)
    fc1, fc2, fc3 = st.columns([3,2,2])
    q          = fc1.text_input("", placeholder=_xl("بحث…","Search…"), key="pf_q", label_visibility="collapsed")
    f_status   = fc2.selectbox("", ["all","active","closed","failed","passed"], key="pf_fs",
                                label_visibility="collapsed",
                                format_func=lambda s: {"all":_xl("كل الحالات","All"),"active":_xl("نشط","Active"),
                                                        "closed":_xl("مغلق","Closed"),"failed":_xl("فشل","Failed"),
                                                        "passed":_xl("اجتاز","Passed")}.get(s,s))
    sort_opt   = fc3.selectbox("", ["timer","name","status"], key="pf_sort",
                                label_visibility="collapsed",
                                format_func=lambda s: {"timer":_xl("العداد","Timer"),"name":_xl("الاسم","Name"),
                                                        "status":_xl("الحالة","Status")}.get(s,s))

    filtered = [a for a in accounts
                if (not q or q.lower() in a.get("name","").lower() or q.lower() in a.get("firm","").lower())
                and (f_status == "all" or a.get("status") == f_status)]

    if sort_opt == "timer":
        filtered.sort(key=lambda a: (_days_left(a) or 9999) if a.get("status")=="active" else 9999)
    elif sort_opt == "name":
        filtered.sort(key=lambda a: a.get("name",""))
    else:
        filtered.sort(key=lambda a: ["active","passed","closed","failed"].index(a.get("status","active")))

    # Cards grid — 3 per row on wide screens, click → detail
    if not filtered:
        st.info(_xl("لا توجد حسابات","No accounts found"))
    else:
        # render in rows of 3
        rows = [filtered[i:i+3] for i in range(0, len(filtered), 3)]
        for row in rows:
            cols = st.columns(len(row))
            for col, acc in zip(cols, row):
                with col:
                    card_html = (
                        f'<div class="pfc-card">'
                        f'{_list_card_html(acc)}'
                        f'</div>'
                    )
                    st.markdown(card_html, unsafe_allow_html=True)
                    if st.button(
                        _xl("فتح ←","Open →"),
                        key=f"pf_open_{acc['id']}",
                        use_container_width=True,
                    ):
                        st.session_state["pf_open_id"] = acc["id"]
                        st.rerun()

    st.divider()

    # Add account
    with st.expander(_xl("➕ إضافة حساب جديد","➕ Add new account")):
        # Optional AI prefill
        ai_c1, ai_c2 = st.columns([2,1])
        ai_firm = ai_c1.text_input(_xl("اسم الشركة للاستخراج التلقائي","Firm name for AI extraction"), key="pf_ai_firm")
        ai_url  = ai_c2.text_input(_xl("رابط الشركة","Firm URL"), key="pf_ai_url")
        if st.button(_xl("🤖 استخراج القواعد تلقائياً","🤖 Extract rules with AI"), key="pf_ai_btn"):
            with st.spinner(_xl("جاري الاستخراج…","Extracting…")):
                res = _ai_extract_rules(ai_firm, ai_url)
            if res:
                st.session_state["pf_ai_prefill"] = res
                st.success(_xl("تم الاستخراج — اكمل الفورم","Extracted — fill in the form"))
            else:
                st.warning(_xl("ما اتعملش استخراج — اكتب يدوي","Nothing extracted — fill manually"))

        new_acc = _account_form(existing=st.session_state.pop("pf_ai_prefill", None))
        if new_acc is not None:
            accounts.append(new_acc)
            _save_accounts(accounts)
            st.rerun()

    # Backup / Restore
    with st.expander(_xl("💾 نسخ احتياطي","💾 Backup / Restore")):
        st.download_button(
            _xl("تحميل JSON","Download JSON"),
            data=json.dumps(accounts, ensure_ascii=False, indent=2),
            file_name="prop_firms_backup.json",
            mime="application/json",
        )
        up = st.file_uploader(_xl("استعادة من JSON","Restore from JSON"), type="json", key="pf_restore")
        if up:
            try:
                restored = json.loads(up.read())
                if isinstance(restored, list):
                    _save_accounts(restored)
                    st.success(_xl("تم الاستعادة","Restored"))
                    st.rerun()
            except Exception as e:
                st.error(str(e))
