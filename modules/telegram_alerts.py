"""Optional Telegram alerts: only the best-ranked scanner alerts are sent.

IMPORTANT - what the rank is: an EVIDENCE score (0-100) built from how many independent strategy families agree (stars),
whether the daily bias / premium-discount / killzone agree with the side, conflicting signals, and the reward:risk of the
plan. It is NOT a measured win probability: no real-candle backtest has proven an edge yet (run modules.backtest_signals on
real OKX data for that). The message says so.

Keys (never committed): TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID in Streamlit Secrets / env vars."""
from __future__ import annotations

import html
import os
import time

import requests

API = "https://api.telegram.org/bot{token}/sendMessage"
RESEND_AFTER_S = 4 * 3600      # same symbol+side+timeframe is not repeated within 4 h ...
RESEND_IF_BETTER = 10          # ... unless its quality rose by this many points


def _secret(name: str) -> str:
    v = os.environ.get(name, "")
    if not v:
        try:
            import streamlit as st
            v = str(st.secrets.get(name, "") or "")
        except Exception:
            v = ""
    return v.strip()


def creds() -> tuple[str, str]:
    return _secret("TELEGRAM_BOT_TOKEN"), _secret("TELEGRAM_CHAT_ID")


def quality(r: dict, e: dict) -> tuple[int, list[str]]:
    """r = scanner result, e = scan_entry -> (0-100 evidence score, short reasons)."""
    mx = max(1, int(r.get("max_score") or e.get("max") or 1))
    q, why = 60.0 * int(r.get("score", 0)) / mx, []
    ag = ((r.get("context") or {}).get("agree")) or {}
    for key, good, bad, label in (("bias", 10, -12, "اتجاه اليوم"), ("pd", 8, -10, "بريميوم/ديسكاونت")):
        v = ag.get(key)
        if v is True:
            q += good; why.append("✓ " + label)
        elif v is False:
            q += bad; why.append("✗ " + label)
    if ag.get("window") is True:
        q += 6; why.append("✓ كيل زون")
    if ag.get("stand_aside"):
        q -= 10; why.append("⚠ تجميع (يفضل الانتظار)")
    m = r.get("mtf") or {}   # swing / position trades: do weekly + daily + 4H back the side?
    if m.get("status") and r.get("trade_type") in ("Swing", "Position"):
        if m["status"] == "aligned":
            q += 8; why.append("✓ فريمات السوينج متوافقة")
        elif m["status"] == "conflict":
            q -= 12; why.append("✗ الأسبوعي/اليومي ضد الاتجاه")
    ag_n = len(r.get("against") or [])
    if ag_n:
        q -= min(15, 5 * ag_n); why.append(f"⚠ {ag_n} إشارة عكسية")
    if r.get("mixed"):
        q -= 10
    p = e.get("plan") or {}
    try:
        risk = abs(p["entry"] - p["stop"]); rr = abs(p["tps"][0] - p["entry"]) / risk if risk else 0
        q += 8 if rr >= 1.5 else 4 if rr >= 1 else -8 if rr < 0.8 else 0
        why.append(f"R:R {rr:.1f}")
    except Exception:
        pass
    return int(max(0, min(100, round(q)))), why


def select(alerts: list[dict], top_n: int = 3, min_q: int = 60) -> list[dict]:
    ok = [a for a in alerts if isinstance(a.get("q"), (int, float)) and a["q"] >= min_q]
    return sorted(ok, key=lambda a: (-a["q"], -int(a.get("score", 0))))[:max(1, top_n)]


def fresh(a: dict, sent: dict, now: float | None = None) -> bool:
    """Not already sent recently (unless clearly better)."""
    now = now or time.time()
    k = f"{a['symbol']}|{a['direction']}|{a.get('tfk') or a.get('tfc')}"
    old = sent.get(k)
    return not old or now - old[0] > RESEND_AFTER_S or a["q"] >= old[1] + RESEND_IF_BETTER


def mark(a: dict, sent: dict, now: float | None = None):
    sent[f"{a['symbol']}|{a['direction']}|{a.get('tfk') or a.get('tfc')}"] = (now or time.time(), a["q"])


def fmt(a: dict) -> str:
    """The "Setup" message: same content as the dashboard's Setup Card (what fired, the plan, the context)."""
    esc = html.escape
    up = a["direction"] == "bullish"
    p = a.get("plan") or {}
    ana = a.get("ana") or {}
    tags = " · ".join(esc(str(t[0])) for t in (a.get("tags") or [])[:6] if t)   # tag = [abbr, bg, fg, tip]
    lines = [f"📋 <b>SETUP</b> {'🟢' if up else '🔴'} <b>{esc(a['symbol'])}</b> {'شراء ▲' if up else 'بيع ▼'} · {esc(str(a.get('tfk') or a.get('tfc')))} · {esc(str(a.get('trade', '')))}",
             f"الجودة: <b>{a['q']}/100</b> · النجوم {a.get('score')}/{a.get('max')}"]
    if p:
        try:
            risk = abs(p["entry"] - p["stop"]); rr = f" · R:R 1:{abs(p['tps'][0] - p['entry']) / risk:.1f}" if risk else ""
        except Exception:
            rr = ""
        lines.append(f"\n<b>الخطة</b>\nدخول {p.get('entry')} · وقف {p.get('stop')}\nأهداف {' / '.join(str(x) for x in p.get('tps', []))}{rr}")
    sig = [x for x in (ana.get("sig") or []) if x][:5]
    if sig:
        lines.append("\n<b>الشروط اللي اتحققت</b>\n" + "\n".join("• " + esc(str(x))[:170] for x in sig))
    elif tags:
        lines.append("\nالأدلة: " + tags)
    ctx = [x for x in (ana.get("ctx") or []) if x][:4]
    if ctx:
        lines.append("\n<b>السياق</b>\n" + "\n".join("• " + esc(str(x))[:150] for x in ctx))
    mt = [x for x in (ana.get("mtf") or []) if x]
    if mt and a.get("ttype") in ("Swing", "Position"):
        lines.append("\n<b>إطار الأسبوعي / اليومي / 4س</b>\n" + "\n".join("• " + esc(str(x))[:150] for x in mt))
    if ana.get("against"):
        lines.append("⚠ " + esc(str(ana["against"]))[:200])
    if a.get("qwhy"):
        lines.append("\n" + esc(" · ".join(a["qwhy"])))
    lines.append("\n<i>ترتيب بالأدلة مش نسبة نجاح مثبتة. مش نصيحة مالية.</i>")
    return "\n".join(lines)[:3900]


def send(text: str, token: str | None = None, chat: str | None = None) -> str | None:
    """-> None if sent, else a short error (never contains the token)."""
    t, c = (token, chat) if token and chat else creds()
    if not t or not c:
        return "no TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID in Secrets"
    try:
        r = requests.post(API.format(token=t), json={"chat_id": c, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}, timeout=12)
    except requests.RequestException as ex:
        return f"network: {type(ex).__name__}"
    if r.status_code == 200:
        return None
    try:
        d = r.json().get("description", "")
    except Exception:
        d = ""
    return f"HTTP {r.status_code}: {d[:100]}"


def dispatch(alerts: list[dict], sent: dict, top_n: int = 3, min_q: int = 60) -> tuple[int, str | None]:
    """Send the best fresh alerts. -> (how many sent, last error)."""
    n, err = 0, None
    for a in select(alerts, top_n, min_q):
        if not fresh(a, sent):
            continue
        err = send(fmt(a))
        if err:
            break
        mark(a, sent); n += 1
    return n, err
