"""XPiX Telegram bot: a CHANNEL between the owner's Telegram group and Claude Code on the Mac (docs/XPIX_BOT_BRIEF.md).

Read + view + draw only. No orders, no trading, no broker/TradingView logins, no keys in code.
  XPIX_BOT_TOKEN      bot token (own bot, NOT Hermes). Env only, Mac only.
  XPIX_OWNER_CHAT_ID  the only chat the bot answers; every other chat is ignored silently.
  XPIX_URL            platform URL (default http://localhost:8501)
  XPIX_PROFILE        Chromium profile dir (default ~/.xpix_bot_profile) - keeps the layout/drawings between runs
Run: python scripts/xpix_bot.py
Commands: /plan | /smt | /help | /shot SYMBOL TF | /today SYMBOL | /signals | /alerts | /deep <text> (Opus) | any other text -> Claude Code (Sonnet, read-only tools).
Spot desk (modules/spot_query.py, needs SPOT_GH_TOKEN + SPOT_GH_REPO in the env): /spot | /inv <no / shop / date> | /find <text> | /spotalerts | /spotxl
Spot analyzer: /spotchart GOLD (image of the analyzer) | /outlook GOLD (weekly Arabic briefing + image)
Platform: /panel tape|dom|ofm|limits|liq|signals|posn | /ind ew|gann|smt|div|harm|kz|vp|rsi|macd on|off | /help
Arabic free text is routed by modules/bot_router.py ("ابعتلي صورة الدهب على الأسبوعي مع اليوت"); anything else -> Claude.
Weekly briefing on its own: XPIX_OUTLOOK_SYMS (default GOLD,BTC), XPIX_OUTLOOK_DAY (0=Mon .. 6=Sun, default 6),
XPIX_OUTLOOK_HOUR (Mac local time, default 20); state in ~/.xpix_bot_state.json (sent once per ISO week).
HONESTY: nothing here has been run against Telegram unless the owner says so; the XCMD part was tested live (tests/browser/xcmd_live.py)."""
import os, subprocess, sys, time, json, pathlib
import requests
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
TOKEN = os.environ.get("XPIX_BOT_TOKEN", "")
OWNER = os.environ.get("XPIX_OWNER_CHAT_ID", "")
URL = os.environ.get("XPIX_URL", "http://localhost:8501")
PROFILE = os.path.expanduser(os.environ.get("XPIX_PROFILE", "~/.xpix_bot_profile"))
API = f"https://api.telegram.org/bot{TOKEN}"
CACHE_S = 3600          # same symbol+tf is not re-analysed within the hour
RULES = ("You are the brain of the XPiX Telegram channel. READ-ONLY: never place/suggest executing orders, never touch broker, "
         "TradingView or any credentials, never write keys. Never invent prices. Say 'mock-tested only' if untested live and "
         "'n<30 is not evidence'. Answer briefly in the owner's language.")
_cache = {}


def tg(method, **kw):
    r = requests.post(f"{API}/{method}", timeout=70, **kw)
    return r.json()


def say(text, html=False):
    d = {"chat_id": OWNER, "text": text[:4000]}
    if html:
        d["parse_mode"] = "HTML"
        d["disable_web_page_preview"] = True
    tg("sendMessage", data=d)


def send_doc(name, data, caption=""):
    tg("sendDocument", data={"chat_id": OWNER, "caption": caption[:900]}, files={"document": (name, data)})


def send_photo(path, caption=""):
    with open(path, "rb") as f:
        tg("sendPhoto", data={"chat_id": OWNER, "caption": caption[:900]}, files={"photo": f})


class Platform:
    """Chromium + the platform iframe that exposes window.XCMD."""
    def __init__(self, pw):
        self.ctx = pw.chromium.launch_persistent_context(PROFILE, headless=True, viewport={"width": 1600, "height": 950})
        self.page = self.ctx.pages[0] if self.ctx.pages else self.ctx.new_page()
        self.page.goto(URL, wait_until="domcontentloaded")
        self.frame = self._find(90)
        if not self.frame:
            raise RuntimeError("XCMD iframe not found - is the platform running at " + URL + " ?")
        time.sleep(6)
        if not self.x("XCMD.state().panels.some(p=>p.type==='chart')"):   # fresh profile = empty workspace
            self.x("XCMD.addPanel('chart')"); time.sleep(6)

    def _find(self, timeout):
        t0 = time.time()
        while time.time() - t0 < timeout:
            for f in self.page.frames:
                try:
                    if f.evaluate("typeof window.XCMD === 'object'"):
                        return f
                except Exception:
                    pass
            time.sleep(1)

    def x(self, js):
        try:
            return self.frame.evaluate(js)
        except Exception:                       # Streamlit re-render replaced the iframe: find it again
            self.frame = self._find(30)
            return self.frame.evaluate(js)

    def sym(self, s):
        s = s.upper()
        syms = self.x("XCMD.state().sym")
        for c in (s, s + "-USDT"):
            if c in syms:
                return c

    def panel(self, typ):
        """Open a widget once (Time & Sales, DOM, order-flow map, limit tracking ...)."""
        have = [q["type"] for q in self.x("XCMD.state()")["panels"]]
        if typ in have:
            return {"ok": True, "already": True}
        r = self.x(f"XCMD.addPanel({json.dumps(typ)})")
        time.sleep(3)
        return r

    def ind(self, ind_id, on=True):
        return self.x(f"XCMD.toggle({json.dumps(ind_id)}, {str(bool(on)).lower()})")

    def shot(self, sym=None, tf=None, out="/tmp/xpix_shot.png"):
        if sym:
            r = self.x(f"XCMD.setSymbol({json.dumps(sym)})")
            if not r["ok"]:
                return None, r["err"]
        if tf:
            r = self.x(f"XCMD.setTf({json.dumps(tf)})")
            if not r["ok"]:
                return None, r["err"]
        time.sleep(5)                            # let candles load
        self.page.screenshot(path=out)
        return out, None


def cmd_signals(alerts_only=False):
    from modules import signal_log
    recs = signal_log.load()
    if not recs:
        return "No logged signals on this Mac (.signal_log.jsonl missing/empty). Nothing to report."
    if alerts_only:
        last = sorted(recs, key=lambda r: r.get("t", 0))[-8:]
        return "Latest logged alerts:\n" + "\n".join(f"{time.strftime('%m-%d %H:%M', time.gmtime(r['t']))} {r['symbol']} {r['dir']} {r['tf']} {r.get('out', 'open')}" for r in last)
    return signal_log.format_stats(signal_log.stats(recs))


def cmd_today(p, s):
    sym = p.sym(s)
    if not sym:
        return None, "unknown symbol"
    key = ("today", sym)
    if key in _cache and time.time() - _cache[key][0] < CACHE_S:
        return _cache[key][1]
    png, err = p.shot(sym, "1H", "/tmp/xpix_today.png")
    if err:
        return None, err
    st = p.x("XCMD.state()")["panels"]
    ch = next((q for q in st if q["type"] == "chart"), {})
    from modules import signal_log
    day = [r for r in signal_log.load() if r.get("symbol", "").startswith(sym.split("-")[0]) and time.time() - r.get("t", 0) < 86400]
    txt = (f"{sym} 1H | last {ch.get('last')} | {ch.get('bars')} bars loaded\n"
           f"Logged signals in last 24h: {len(day)}" + ("" if day else " (none)") + "\n"
           "Chart only, no trade advice. n<30 is not evidence.")
    _cache[key] = (time.time(), (png, txt))
    return _cache[key][1]


def cmd_plan(a):
    """/plan [scalp|conf] [5m|15m|1h] [SYMBOL ...] : today's trades by timeframe confluence (standard) or a scalp on one timeframe (modules/day_plan.py)."""
    from modules import day_plan as D
    from modules.market_cache import get_klines
    mode, trig, syms = "conf", None, []
    for x in a:
        lx = x.lower()
        if lx in ("scalp", "conf"):
            mode = lx
        elif lx in ("5m", "15m", "1h"):
            trig = (lx,)
        else:
            syms.append(x.upper() if "-" in x or ":" in x else x.upper() + "-USDT")
    syms = syms or [x for x in os.environ.get("DAY_SYMBOLS", "BTC-USDT,ETH-USDT,SOL-USDT,HL:xyz:GOLD,HL:xyz:SILVER,HL:xyz:SP500,HL:xyz:XYZ100,HL:xyz:CL,Y:EURUSD=X,Y:GBPUSD=X").split(",") if x]
    plans = D.scan(syms, lambda s_, t_: get_klines(s_, t_, 300), mode=mode, trigger_tfs=trig)
    return D.format_telegram(plans, ar=True)


def cmd_smt():
    """/smt : SMT between the correlated pairs right now (modules/intermarket.py)."""
    from modules import intermarket as IM
    from modules.market_cache import get_klines
    ev = IM.scan_pairs(lambda s_, t_: get_klines(s_, t_, 300))
    if not ev:
        return "No clear SMT between the correlated pairs right now."
    return "SMT now:\n" + "\n".join(f"• {c['label']} · {c['session']} · {c['bars_ago']} bars" for c in IM.chips(ev, ar=False, limit=15))


def ask_claude(text, deep=False):
    cmd = ["claude", "-p", text, "--model", "opus" if deep else "sonnet", "--allowedTools", "Read,Grep,Glob",
           "--append-system-prompt", RULES]
    try:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=300)
        return (r.stdout or r.stderr or "(no answer)").strip()
    except Exception as e:
        return f"Claude Code call failed: {e}"


HELP_AR = """أوامر XPiX (قراية وعرض بس - مفيش أي أمر تداول):
• اكتب عادي بالعربي: «ابعتلي صورة الدهب على الأسبوعي مع اليوت» · «افتح التايم اند سيلز للبيتكوين» · «الدهب هيطلع الأسبوع الجاي؟» · «وريني المحلل للفضة» · «هات فاتورة INV-12»
• /shot BTC 4H · /panel tape|dom|ofm|limits|liq|signals · /ind ew|gann|smt|div|harm on|off
• /spotchart GOLD (صورة المحلل) · /outlook GOLD (تقرير الأسبوع + صورة)
• /spot · /inv رقم · /find نص · /spotalerts · /spotxl
• /plan [scalp|conf] [5m|15m|1h] [SYMBOL...] خطة اليوم (ترابط الفريمات) · /smt الـ SMT بين الأزواج
• /signals · /alerts · /today BTC · /deep سؤال"""
TF_AR = {"1M": "الشهري", "1W": "الأسبوعي", "1D": "اليومي", "4H": "الـ 4 ساعات", "1H": "الساعة", "15m": "الربع ساعة", "5m": "الـ 5 دقايق"}
IND_AR = {"ew": "اليوت", "gann": "جان", "smt": "SMT", "div": "الدايفرجنس", "harm": "الهارمونيك", "kz": "الكيل زون", "vp": "بروفايل الفوليوم", "vwap": "VWAP",
          "rsi": "RSI", "macd": "MACD", "adx": "ADX", "fp": "الفوت برينت", "delta": "الدلتا", "ote": "OTE", "msb": "MSB"}
PANEL_AR = {"tape": "التايم اند سيلز", "dom": "عمق السوق", "ofm": "خريطة الأوردر فلو", "limits": "تتبع الأوامر", "liq": "التصفيات", "signals": "الإشارات",
            "posn": "التمركز", "rsihm": "خريطة RSI"}


def spot_image(p, asset, outlook=False):
    """Analyzer image (+ the Arabic weekly briefing) for one asset, rendered in the bot's own browser."""
    from modules import spot_dash, spot_outlook
    b, msg = spot_outlook.build(asset)
    if not any(r.get("ok") for r in b["reads"].values()):
        return say(f"مفيش شموع لـ {asset} دلوقتي ({', '.join(b.get('errors', []))}).")
    png = spot_dash.to_png(spot_dash.render(b, True), f"/tmp/xpix_spot_{asset}.png", ctx=p.ctx)
    send_photo(png, (msg if outlook else f"محلل السبوت - {asset} · الدرجة {b['conf']['score']:+d}")[:1000])
    if outlook and len(msg) > 1000:
        say(msg)


def run_actions(p, acts):
    """Execute router actions (whitelisted) and answer with one screenshot + an Arabic line of what was done."""
    from modules import bot_router
    done, shot = [], None
    for a in acts:
        c = a["cmd"]
        if c == "ledger":
            from modules import spot_query
            reply, files = spot_query.handle(a["text"])
            say(reply or "مفيش نتيجة.")
            for name, data in files:
                send_doc(name, data)
            return
        if c in ("outlook", "spotchart"):
            return spot_image(p, a["asset"], outlook=(c == "outlook"))
        if c == "panel":
            r = p.panel(a["type"])
            done.append(("فتحت " if r.get("ok") else "مقدرتش أفتح ") + PANEL_AR.get(a["type"], a["type"]))
        elif c == "ind":
            r = p.ind(a["id"], a["on"])
            done.append(("شغّلت " if a["on"] else "طفّيت ") + IND_AR.get(a["id"], a["id"]) + ("" if r.get("ok") else f" (مش متاح: {r.get('err')})"))
        elif c == "shot":
            shot = a
    if shot is not None:
        syms = p.x("XCMD.state()")["sym"]
        sym = bot_router.platform_symbols(shot.get("asset"), syms)
        if shot.get("asset") and not sym:
            return say(f"الرمز {shot['asset']} مش في قايمة المنصة.")
        png, err = p.shot(sym, shot.get("tf"))
        cap = " · ".join(done + [x for x in (sym, TF_AR.get(shot.get("tf"), shot.get("tf") or "")) if x])
        return send_photo(png, cap or "المنصة دلوقتي") if png else say(err)
    if done:
        say(" · ".join(done))


def weekly_due(now=None, state_path=os.path.expanduser("~/.xpix_bot_state.json")):
    """True once per ISO week, at/after XPIX_OUTLOOK_DAY + XPIX_OUTLOOK_HOUR (Mac local time)."""
    import datetime as _dt
    now = now or _dt.datetime.now()
    day, hour = int(os.environ.get("XPIX_OUTLOOK_DAY", "6")), int(os.environ.get("XPIX_OUTLOOK_HOUR", "20"))
    wk = "%d-W%02d" % now.isocalendar()[:2]
    try:
        st = json.load(open(state_path))
    except Exception:
        st = {}
    if st.get("outlook_week") == wk or now.weekday() != day or now.hour < hour:
        return False
    st["outlook_week"] = wk
    json.dump(st, open(state_path, "w"))
    return True


def handle(p, text):
    a = text.strip().split()
    c = a[0].lower().split("@")[0] if a else ""
    if c in ("/help", "/start", "مساعدة"):
        return say(HELP_AR)
    if c in ("/spotchart", "/outlook"):
        return spot_image(p, (a[1] if len(a) > 1 else "GOLD").upper(), outlook=(c == "/outlook"))
    if c == "/panel" and len(a) > 1:
        return run_actions(p, [{"cmd": "panel", "type": a[1].lower()}, {"cmd": "shot"}])
    if c == "/ind" and len(a) > 1:
        return run_actions(p, [{"cmd": "ind", "id": a[1].lower(), "on": (a[2].lower() != "off") if len(a) > 2 else True}, {"cmd": "shot"}])
    if c in ("/spot", "/inv", "/find", "/spotalerts", "/spotxl"):   # spot desk ledger (read-only)
        from modules import spot_query
        reply, files = spot_query.handle(text)
        say(reply)
        for name, data in files:
            send_doc(name, data)
        return None
    if c == "/shot":
        sym = p.sym(a[1]) if len(a) > 1 else None
        if len(a) > 1 and not sym:
            return say("unknown symbol")
        png, err = p.shot(sym, a[2] if len(a) > 2 else None)
        return send_photo(png, f"{sym or ''} {a[2] if len(a) > 2 else ''} live platform shot") if png else say(err)
    if c == "/today":
        r = cmd_today(p, a[1] if len(a) > 1 else "BTC")
        return (send_photo(r[0], r[1]) if r[0] else say(r[1]))
    if c == "/plan":
        return say(cmd_plan(a[1:]), html=True)
    if c == "/smt":
        return say(cmd_smt())
    if c == "/signals":
        return say(cmd_signals())
    if c == "/alerts":
        return say(cmd_signals(True))
    if c == "/deep":
        return say(ask_claude(" ".join(a[1:]), deep=True))
    if not c.startswith("/"):
        from modules import bot_router
        acts = bot_router.route(text)
        if acts:
            return run_actions(p, acts)
    return say(ask_claude(text))


def main():
    if not TOKEN or not OWNER:
        sys.exit("Set XPIX_BOT_TOKEN and XPIX_OWNER_CHAT_ID in the environment (never in the repo).")
    with sync_playwright() as pw:
        p = Platform(pw)
        off = 0
        while True:
            try:
                for u in tg("getUpdates", params={"timeout": 50, "offset": off}).get("result", []):
                    off = u["update_id"] + 1
                    m = u.get("message") or {}
                    if str(m.get("chat", {}).get("id")) != str(OWNER) or not m.get("text"):
                        continue                     # any other chat is ignored
                    try:
                        handle(p, m["text"])
                    except Exception as e:
                        say(f"error: {str(e)[:300]}")
            except requests.RequestException:
                time.sleep(5)
            try:                                     # weekly Arabic briefing (gold, bitcoin ...) with the analyzer image
                if weekly_due():
                    for asset in [x.strip().upper() for x in os.environ.get("XPIX_OUTLOOK_SYMS", "GOLD,BTC").split(",") if x.strip()]:
                        spot_image(p, asset, outlook=True)
            except Exception as e:
                say(f"weekly briefing error: {str(e)[:200]}")


if __name__ == "__main__":
    main()
