"""The trading floor (OmniDesk structure from the research conversation + Saud's framework).

  Head of desk      plans, assigns markets, synthesises a proposal, takes the final call
  10 specialists    Wyckoff · ICT/SMC · COT · OrderFlow · Sentiment · Macro · Seasonality ·
                    News · Risk · Debate (Bull + Bear)  — run in parallel per market
  Auditor           checks every number against the evidence ledger (code) + logic (model)
  Reviewer          checks the proposal against the framework's rules (model)
  Gate              deterministic hard vetoes; the models can never override it
"""
from __future__ import annotations

import asyncio
import json
import time

from .. import config, journal, risk
from ..config import GATE, UNIVERSE
from . import tools as T
from .runtime import Agent, Room, run_agent

REPORT = ('{"symbol": "...", "stance": "bullish|bearish|neutral", "confidence": 0-100, '
          '"summary": "سطرين", "evidence": [{"claim": "...", "value": رقم من الأداة, "tool": "اسم الأداة"}], '
          '"warnings": ["..."]}')

AGENTS: dict[str, Agent] = {a.id: a for a in [
    Agent("head", "رئيس المكتب", "يوزع الأسواق على الفريق، يجمع آراءهم، يكتب الاقتراح، ويأخذ القرار مع البوابة.", "🎩", "#e2e8f0",
          ["macro", "structure", "risk"], ["watchlist", "risk_regime", "currency_strength", "calendar_risk", "timing", "fibonacci", "structure", "topdown"],
          "بتفكر زي رئيس مكتب ماكرو منضبط: الصورة الكبيرة الأول، ومش بتدخل إلا لما أكتر من مدرسة تأكد.", 6, "lead"),
    Agent("wyckoff", "Wyckoff", "يقرا التجميع والتوزيع والـ Spring والجهد مقابل النتيجة.", "🏛️", "#a78bfa",
          ["structure"], ["wyckoff", "topdown"], "مدرستك وايكوف: السبب والنتيجة، الجهد والنتيجة، العرض والطلب.", 4),
    Agent("ict", "ICT/SMC", "يقرا الهيكل: BOS/CHoCH، Order Block، FVG، السيولة، Unicorn، OTE، SMT.", "🧩", "#60a5fa",
          ["ict", "fibonacci", "structure"], ["topdown", "structure", "fibonacci", "smt"], "بتقرا الهيكل الخام قبل أي مؤشر.", 5),
    Agent("cot", "COT", "يقرا تموضع المؤسسات من تقرير CFTC ويحدد التطرف.", "🏦", "#34d399",
          ["cot"], ["cot"], "بتشوف المؤسسات بتعمل إيه، وبتحذر من الحشد المزدحم.", 3),
    Agent("orderflow", "OrderFlow", "يقرا الـ Delta والـ Footprint والحوائط والامتصاص.", "🌊", "#fbbf24",
          ["orderflow"], ["orderflow"], "بتأكد بس، عمرك ما بتدي إشارة دخول لوحدك.", 3),
    Agent("sentiment", "Sentiment", "يقرا معنويات الحشد كإشارة عكسية.", "🎭", "#f472b6",
          ["sentiment"], ["sentiment", "news"], "الحشد المتطرف غالباً غلطان عند النهايات. وبتقول بصراحة إن الداتا تقريبية.", 3),
    Agent("macro", "Macro", "يقرا الفائدة والبنوك المركزية ومزاج المخاطرة وقوة العملات والانحياز المركب.", "🌐", "#38bdf8",
          ["macro"], ["risk_regime", "currency_strength", "rate_differentials", "smart_bias"], "الفلوس بتروح فين على المدى المتوسط؟", 5),
    Agent("seasonality", "Seasonality", "يقرا الأنماط التاريخية للشهر الحالي.", "📅", "#94a3b8",
          [], ["seasonality"], "الموسمية عامل مساعد بوزن صغير، مش سبب للدخول.", 2),
    Agent("news", "News", "يصنف الأحداث والعناوين ويحدد لو في خبر يمنع الدخول.", "📰", "#f87171",
          [], ["news", "calendar_risk"], "خبر عالي التأثير خلال 12 ساعة = لا دخول جديد.", 3),
    Agent("risk", "Risk", "يحسب الحجم لكل حساب، يتأكد من الحدود، ويوزع على الحسابات حسب المستوى، وله حق الرفض.", "🛡️", "#22c55e",
          ["risk"], ["accounts", "position_size"], "بتحمي الحسابات قبل ما تفكر في الربح.", 4, "control"),
    Agent("bull", "Bull", "يقدم أقوى حجة للشراء من تقارير الفريق.", "🐂", "#16a34a",
          [], ["structure", "fibonacci", "timing"], "محامي الشراء: هات أقوى حجة صاعدة بأرقام.", 3, "debate"),
    Agent("bear", "Bear", "يقدم أقوى حجة للبيع ويهاجم الشراء.", "🐻", "#dc2626",
          ["skeptic"], ["structure", "fibonacci", "timing", "cot"], "محامي البيع والمشكك: هات أقوى حجة هابطة واهدم الفكرة.", 3, "debate"),
    Agent("auditor", "المدقق", "يراجع كل رقم في كل تقرير مقابل نتايج الأدوات، ويتأكد من اتساق الاتجاه والمستويات.", "🔍", "#facc15",
          ["auditor"], [], "أنت مش محلل. أنت بتراجع شغل غيرك وبس.", 1, "control"),
    Agent("reviewer", "المراجع", "يطابق الاقتراح على قواعد الفريم ورك (3 أسباب من قسمين، سيناريوهات، تأكيد الشارت، المستويات).", "📋", "#c084fc",
          ["skeptic", "risk"], ["watchlist", "structure"], "بتسأل: هل الصفقة دي ماشية على قواعدنا المكتوبة؟", 3, "control"),
]}

SPECIALISTS = ["wyckoff", "ict", "cot", "orderflow", "sentiment", "macro", "seasonality", "news"]


def roster() -> list[dict]:
    return [a.card() for a in AGENTS.values()]


def _dir_word(d: int) -> str:
    return "شراء" if d > 0 else "بيع"


# ------------------------------------------------------------------ deterministic audit
def audit_numbers(reports: dict[str, dict], ledger: list[dict], symbol: str) -> dict:
    """Every evidence value must appear in a tool result (±0.5% or display rounding)."""
    nums = []
    for e in ledger:  # only evidence gathered for this market (or market-wide tools) counts
        if (e.get("args") or {}).get("symbol") in (None, symbol):
            nums += T.numbers_in(e["result"])
    pool = [n for n in nums if n == n]
    bad, checked = [], 0

    def found(v: float) -> bool:
        dec = len(str(v).split(".")[1]) if "." in str(v) else 0
        tol_round = 0.5 * 10 ** -dec if dec else 0.5
        return any(abs(n - v) <= max(0.005 * abs(n), tol_round) for n in pool)

    for agent, rep in reports.items():
        for ev in (rep or {}).get("evidence", []) or []:
            v = ev.get("value") if isinstance(ev, dict) else None
            if isinstance(v, str):
                try:
                    v = float(v.replace(",", "").replace("%", ""))
                except ValueError:
                    v = None
            if not isinstance(v, (int, float)) or isinstance(v, bool):
                continue
            checked += 1
            if not found(float(v)):
                bad.append({"agent": agent, "claim": ev.get("claim"), "value": v, "tool": ev.get("tool")})
    return {"checked": checked, "unverified": bad, "ok": not bad}


def audit_levels(p: dict, ledger: list[dict], symbol: str) -> list[str]:
    errs = []
    d = p.get("direction")
    e, s, t1 = p.get("entry"), p.get("stop"), p.get("t1")
    if not all(isinstance(x, (int, float)) for x in (e, s, t1)) or d not in (1, -1):
        return ["الاقتراح ناقص: الدخول أو الوقف أو الهدف أو الاتجاه"]
    if d > 0 and not (s < e < t1):
        errs.append("شراء لكن الوقف مش تحت الدخول أو الهدف مش فوقه")
    if d < 0 and not (s > e > t1):
        errs.append("بيع لكن الوقف مش فوق الدخول أو الهدف مش تحته")
    prices = [x for l in ledger if (l["args"] or {}).get("symbol") == symbol for x in T.numbers_in(l["result"].get("data", {})) if x > 0]
    if not prices:   # no tool returned prices for this market: the levels came from the model, not from data
        errs.append("مفيش أداة رجعت أسعار للسوق ده، فالمستويات مش متأكدة")
    else:
        ref = [x for x in prices if 0.5 * e < x < 1.5 * e]
        if not ref:
            errs.append("مستوى الدخول مش قريب من أي سعر رجعته الأدوات")
    return errs


# ------------------------------------------------------------------ the floor
class Floor:
    def __init__(self) -> None:
        self.running = False
        self.history: list[dict] = []
        self.last: dict = {}

    async def run(self, emit) -> dict:
        if self.running:
            return {"error": "running"}
        self.running = True
        self.history = []

        async def keep(ev):
            self.history.append(ev)
            self.history = self.history[-1500:]
            await emit(ev)
        try:
            return await self._run(Room(keep))
        except Exception as e:
            await keep({"type": "floor_error", "text": str(e)[:400], "ts": time.time()})
            raise
        finally:
            self.running = False

    async def _run(self, room: Room) -> dict:
        t0 = time.time()
        await room.say({"type": "floor_start", "agents": roster(), "model": config.LLM_MODEL,
                        "concurrency": config.AGENT_CONCURRENCY})
        await room.say({"type": "phase", "phase": "plan", "title": "1 · التخطيط", "text": "رئيس المكتب بيقرا السوق وبيختار الأسواق ويوزع المهام."})
        # ---------------------------------------------------------- 1 plan
        plan = await run_agent(room, AGENTS["head"],
            f"ابدأ اليوم. افتح watchlist ومزاج المخاطرة والأجندة، واختار أهم {config.AGENT_MAX_CANDIDATES} أسواق (أو أقل) تستاهل الفريق يحللها، "
            "مع الاتجاه المبدئي. فضّل الأسواق المترقّية في الـ watchlist واللي مفيش عليها خبر. "
            'رد JSON: {"summary": "...", "regime": "...", "candidates": [{"symbol": "...", "direction": 1 أو -1, "why": "..."}], '
            '"evidence": [{"claim": "...", "value": رقم, "tool": "..."}]}')
        cands = [c for c in (plan.get("candidates") or []) if isinstance(c, dict) and c.get("symbol") in UNIVERSE][:config.AGENT_MAX_CANDIDATES]
        for c in cands:
            c["direction"] = 1 if int(c.get("direction", 1) or 1) >= 0 else -1
        if not cands:
            await room.bus("head", "all", "decision", "مفيش سوق يستاهل النهارده. أحسن قرار إننا نستنى.")
            return await self._finish(room, [], t0, plan)
        for c in cands:
            await room.bus("head", "team", "assign", f"{c['symbol']} ({_dir_word(c['direction'])} مبدئياً): {c.get('why', '')}", c["symbol"])

        # ---------------------------------------------------------- 2 specialists in parallel
        await room.say({"type": "phase", "phase": "analysis", "title": "2 · التحليل بالتوازي",
                        "text": f"{len(SPECIALISTS)} متخصصين × {len(cands)} أسواق شغالين في نفس الوقت."})

        async def specialist(aid: str, c: dict) -> tuple[str, str, dict]:
            s = c["symbol"]
            if aid == "orderflow" and not UNIVERSE[s].get("binance"):
                rep = {"symbol": s, "stance": "neutral", "confidence": 0, "summary": "مفيش شريط صفقات مجاني للسوق ده، فمش هقدر أأكد.",
                       "evidence": [], "warnings": ["لا Order Flow لغير الكريبتو"], "_meta": {"agent": aid, "skipped": True, "tools": []}}
                await room.say({"type": "agent_state", "agent": aid, "state": "done", "symbol": s, "text": "لا داتا لهذا السوق"})
                await room.say({"type": "agent_report", "agent": aid, "symbol": s, "report": rep})
                return aid, s, rep
            rep = await run_agent(room, AGENTS[aid],
                f"السوق: {s}. الاتجاه المبدئي من رئيس المكتب: {_dir_word(c['direction'])}. حلل من مدرستك بس، "
                f"واستخدم أدواتك. لو مدرستك بتقول عكس الاتجاه قولها بصراحة. رد JSON: {REPORT}", s)
            await room.bus(aid, "head", "report", f"{s}: {rep.get('stance', '?')} ({rep.get('confidence', '?')}%): {rep.get('summary', '')}", s)
            return aid, s, rep

        results = await asyncio.gather(*(specialist(a, c) for c in cands for a in SPECIALISTS))
        reports: dict[str, dict[str, dict]] = {c["symbol"]: {} for c in cands}
        for aid, s, rep in results:
            reports[s][aid] = rep

        # ---------------------------------------------------------- 3 debate (bull vs bear in parallel)
        await room.say({"type": "phase", "phase": "debate", "title": "3 · النقاش Bull ضد Bear", "text": "كل سوق عليه محامي شراء ومحامي بيع في نفس الوقت."})

        def brief(s):
            return json.dumps({a: {k: r.get(k) for k in ("stance", "confidence", "summary", "warnings", "evidence")} for a, r in reports[s].items()},
                              ensure_ascii=False, default=str)[:9000]

        async def debate(c):
            s = c["symbol"]
            fmt = ('رد JSON: {"symbol": "...", "argument": "أقوى حجة في 3 سطور", "points": ["..."], '
                   '"confidence": 0-100, "evidence": [{"claim": "...", "value": رقم, "tool": "..."}]}')
            bull, bear = await asyncio.gather(
                run_agent(room, AGENTS["bull"], f"السوق {s}. تقارير الفريق:\n{brief(s)}\nقدم أقوى حجة للشراء. {fmt}", s),
                run_agent(room, AGENTS["bear"], f"السوق {s}. تقارير الفريق:\n{brief(s)}\nقدم أقوى حجة للبيع واهدم فكرة الشراء. {fmt}", s))
            await room.bus("bull", "bear", "debate", f"{s}: {bull.get('argument', '')}", s)
            await room.bus("bear", "bull", "debate", f"{s}: {bear.get('argument', '')}", s)
            return s, bull, bear

        deb = {s: (b, br) for s, b, br in await asyncio.gather(*(debate(c) for c in cands))}

        # ---------------------------------------------------------- 4 head proposal
        await room.say({"type": "phase", "phase": "proposal", "title": "4 · الاقتراح", "text": "رئيس المكتب بيجمع الآراء ويكتب الصفقة أو يرفضها."})

        async def propose(c):
            s = c["symbol"]
            rep = await run_agent(room, AGENTS["head"],
                f"السوق {s}. تقارير المتخصصين:\n{brief(s)}\nالنقاش:\nBull: {json.dumps(deb[s][0], ensure_ascii=False, default=str)[:2500]}\n"
                f"Bear: {json.dumps(deb[s][1], ensure_ascii=False, default=str)[:2500]}\n"
                "قرر: هل في صفقة؟ لو أيوة افتح timing (وممكن fibonacci وstructure) وخد المستويات منها. "
                'رد JSON: {"symbol": "...", "decision": "propose أو pass", "direction": 1 أو -1, "entry": رقم, "stop": رقم, "t1": رقم, "t2": رقم, '
                '"order": "market أو limit", "confidence": 0-100, "thesis": "...", '
                '"confirmations": {"wyckoff": "agree|disagree|neutral", "ict": "...", "cot": "...", "orderflow": "...", "sentiment": "...", "macro": "...", "seasonality": "...", "news": "..."}, '
                '"evidence": [{"claim": "...", "value": رقم, "tool": "..."}]}', s)
            rep["symbol"] = s
            await room.say({"type": "proposal", "symbol": s, "proposal": rep})
            await room.bus("head", "control", "propose",
                           f"{s}: {'اقتراح ' + _dir_word(rep.get('direction', 1)) if rep.get('decision') == 'propose' else 'لا صفقة'} · {rep.get('thesis', '')}", s)
            return s, rep

        props = dict(await asyncio.gather(*(propose(c) for c in cands)))

        # ---------------------------------------------------------- 5 control: risk + auditor + reviewer in parallel
        await room.say({"type": "phase", "phase": "control", "title": "5 · الرقابة بالتوازي", "text": "Risk والمدقق والمراجع بيراجعوا كل اقتراح في نفس الوقت."})

        async def control(s):
            p = props[s]
            if p.get("decision") != "propose":
                return s, None, None, None
            pj = json.dumps({k: p.get(k) for k in ("direction", "entry", "stop", "t1", "t2", "order", "confidence", "thesis", "confirmations")}, ensure_ascii=False, default=str)
            nums = audit_numbers({**reports[s], "bull": deb[s][0], "bear": deb[s][1], "head": p}, room.ledger, s)
            lv = audit_levels(p, room.ledger, s)
            await room.say({"type": "agent_state", "agent": "auditor", "state": "thinking", "symbol": s,
                            "text": f"راجع {nums['checked']} رقم بالكود: {len(nums['unverified'])} مش موجودين في الأدوات"})
            risk_r, aud_r, rev_r = await asyncio.gather(
                run_agent(room, AGENTS["risk"], f"اقتراح على {s}: {pj}\nافتح accounts وposition_size. حدد الحسابات المؤهلة حسب المستوى وحجم اللوت، وارفض لو في خطر. "
                          'رد JSON: {"symbol": "...", "verdict": "approve أو veto", "accounts": {"acc2": لوت, "acc1": لوت, "acc3": لوت}, "reason": "...", "summary": "...", '
                          '"evidence": [{"claim": "...", "value": رقم, "tool": "..."}]}', s),
                run_agent(room, AGENTS["auditor"], f"اقتراح على {s}: {pj}\nنتيجة التدقيق الآلي للأرقام: {json.dumps(nums, ensure_ascii=False, default=str)[:3000]}\n"
                          f"أخطاء المستويات: {lv}\nتقارير الفريق المختصرة:\n{brief(s)[:5000]}\n"
                          'راجع الاتساق والمنطق. رد JSON: {"symbol": "...", "verdict": "pass أو fail", "issues": ["..."], "summary": "..."}', s),
                run_agent(room, AGENTS["reviewer"], f"اقتراح على {s}: {pj}\nراجعه على قواعد الفريم ورك (Watchlist 3 أسباب من قسمين، سيناريوهات، تأكيد الشارت، الأهداف عند سيولة). "
                          'رد JSON: {"symbol": "...", "verdict": "pass أو fail", "checklist": [{"rule": "...", "ok": true}], "summary": "..."}', s))
            aud_r["numbers"] = nums
            aud_r["levels"] = lv
            for who, r in (("risk", risk_r), ("auditor", aud_r), ("reviewer", rev_r)):
                await room.bus(who, "head", "control", f"{s}: {r.get('verdict', '?')}: {r.get('summary') or r.get('reason') or ''}", s)
            return s, risk_r, aud_r, rev_r

        ctrl = {s: (r, a, v) for s, r, a, v in await asyncio.gather(*(control(c["symbol"]) for c in cands))}

        # ---------------------------------------------------------- 6 gate
        await room.say({"type": "phase", "phase": "decision", "title": "6 · القرار والبوابة", "text": "البوابة الثابتة ليها الكلمة الأخيرة، مهما قال الـ Agents."})
        ideas = []
        lock = risk.discipline()
        from ..tools.macro import calendar_risk
        blocked = calendar_risk()["data"]["blocked"]
        for c in cands:
            s = c["symbol"]
            p = props[s]
            r, a, v = ctrl[s]
            if p.get("decision") != "propose":
                ideas.append({"symbol": s, "status": "PASS", "reason": p.get("thesis", ""), "proposal": p})
                await room.say({"type": "decision", "symbol": s, "status": "PASS", "vetoes": [], "proposal": p})
                continue
            vetoes, notes = [], []
            m = UNIVERSE[s]
            if any(x in blocked for x in (m["base"], m["quote"])):
                vetoes.append("خبر عالي التأثير خلال 12 ساعة")
            if lock["locked"]:
                vetoes.append("التداول مقفول اليوم (قفل الانضباط)")
            if a and not a["numbers"]["ok"]:
                vetoes.append(f"المدقق: {len(a['numbers']['unverified'])} رقم مش موجود في أي أداة")
            if a and a.get("levels"):
                vetoes += [f"المدقق: {x}" for x in a["levels"]]
            if a and a.get("verdict") == "fail":
                notes.append("المدقق رفض المنطق")
            if r and r.get("verdict") == "veto":
                vetoes.append(f"Risk رفض: {r.get('reason', '')}")
            if v and v.get("verdict") == "fail":
                notes.append("المراجع: مش ماشية على قواعد الفريم ورك")
            tim = room.ctx.cache.get(f"timing:{s}:{p.get('direction')}")
            room_r = tim["data"]["room_r"] if tim else None
            if room_r is not None and room_r < 1:
                vetoes.append(f"عائق قريب جداً ({room_r}R)")
            demo = config.DATA_MODE == "demo" or any("demo" in (l["result"].get("source") or []) for l in room.ledger if (l["args"] or {}).get("symbol") == s)
            agrees = sum(1 for x in (p.get("confirmations") or {}).values() if x == "agree")
            if agrees < 3:
                notes.append(f"تأكيدات قليلة ({agrees} من 8)")
            status = "WATCH" if vetoes else ("WATCH" if len(notes) >= 2 else ("READY" if p.get("order") == "market" else "PENDING"))
            idea = {"symbol": s, "direction": p.get("direction"), "status": status, "order": p.get("order", "limit"),
                    "entry": p.get("entry"), "stop": p.get("stop"), "t1": p.get("t1"), "t2": p.get("t2") or p.get("t1"),
                    "rr": round(abs(p["t1"] - p["entry"]) / abs(p["entry"] - p["stop"]), 2) if p.get("entry") and p.get("stop") and p.get("t1") and p["entry"] != p["stop"] else None,
                    "confidence": p.get("confidence"), "thesis": p.get("thesis"), "confirmations": p.get("confirmations") or {},
                    "vetoes": vetoes, "notes": notes, "demo": demo, "accounts": (r or {}).get("accounts"),
                    "bull": deb[s][0].get("argument"), "bear": deb[s][1].get("argument")}
            if status in ("READY", "PENDING") and not demo and idea["rr"]:
                idea["journal_id"] = journal.add({**idea, "bias": 0, "components": idea["confirmations"],
                                                  "doubts": vetoes + notes, "source": ["agents"], "rationale": idea["thesis"] or "",
                                                  "stars": agrees, "reasons": [idea["bull"] or ""], "scenarios": []})
            ideas.append(idea)
            await room.say({"type": "decision", "symbol": s, "status": status, "vetoes": vetoes, "notes": notes, "idea": idea})
            await room.bus("gate", "all", "decision", f"{s}: {status}" + (f" · {'؛ '.join(vetoes)}" if vetoes else ""), s)
        return await self._finish(room, ideas, t0, plan)

    async def _finish(self, room: Room, ideas: list, t0: float, plan: dict) -> dict:
        self.last = {"time": time.time(), "ideas": ideas, "plan": plan, "seconds": round(time.time() - t0, 1),
                     "usage": room.usage}
        await room.say({"type": "floor_done", "seconds": self.last["seconds"], "ideas": ideas, "usage": room.usage})
        return self.last
