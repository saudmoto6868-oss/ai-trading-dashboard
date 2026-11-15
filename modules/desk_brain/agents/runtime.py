"""Agent runtime: a real ReAct loop. The model thinks, chooses which tool to call, reads the
result, decides the next tool, and writes a JSON report. Every step is streamed to the UI.

Nothing here is scripted: which tools get called and what the report says is the model's
choice. The code only enforces the tool allow-list, step limits, the evidence ledger and the
JSON shape of the final report.
"""
from __future__ import annotations

import asyncio
import json
import re
import time
from dataclasses import dataclass, field
from typing import Awaitable, Callable

from .. import config
from ..agent import llm
from . import tools as T

Emit = Callable[[dict], Awaitable[None]]

BASE_RULES = """قواعد ثابتة لكل الفريق:
- اكتب بالعربي (عامية مصرية بسيطة مقبولة).
- ممنوع تخترع أي رقم. كل رقم تكتبه لازم يكون من نتيجة أداة ناديتها في المهمة دي. المدقق هيراجع.
- لو الأداة رجعت source = demo، قول إن البيانات تجريبية.
- لو المعلومة مش متاحة، قول مش متاحة. ماتخمنش.
- استخدم الأدوات بنفسك: ابدأ بالعام وبعدين المتخصص (Progressive Disclosure).
- مفيش تنفيذ صفقات حقيقية. كله ورقي، وبوابة القواعد ليها الكلمة الأخيرة.
- في الآخر رد بـ JSON بس، من غير أي كلام قبله أو بعده، بالشكل المطلوب في المهمة."""


@dataclass
class Agent:
    id: str
    name: str            # display name
    role: str            # one-line job description (Arabic)
    emoji: str
    color: str
    skills: list[str]
    tools: list[str]
    persona: str         # how this agent thinks
    max_steps: int = 6
    group: str = "analyst"
    model: str | None = None

    def system(self) -> str:
        sk = llm.skills_text(self.skills) if self.skills else ""
        return (f"[agent:{self.id}]\nأنت «{self.name}» في مكتب تداول. وظيفتك: {self.role}\n{self.persona}\n\n"
                f"{BASE_RULES}\n\nمهاراتك (SKILL.md):\n{sk}")

    def card(self) -> dict:
        return {"id": self.id, "name": self.name, "role": self.role, "emoji": self.emoji, "color": self.color,
                "skills": self.skills, "tools": self.tools, "group": self.group,
                "model": self.model or config.AGENT_MODELS.get(self.id) or config.LLM_MODEL or None}


@dataclass
class Room:
    """One run of the trading floor: shared emit, tool cache, evidence ledger, concurrency."""
    emit: Emit
    ctx: T.Ctx = field(default_factory=T.Ctx)
    ledger: list[dict] = field(default_factory=list)
    sem: asyncio.Semaphore = field(default_factory=lambda: asyncio.Semaphore(config.AGENT_CONCURRENCY))
    usage: dict = field(default_factory=lambda: {"calls": 0, "tools": 0})

    async def say(self, ev: dict) -> None:
        ev["ts"] = time.time()
        await self.emit(ev)

    async def bus(self, frm: str, to: str, kind: str, text: str, symbol: str | None = None) -> None:
        await self.say({"type": "bus", "from": frm, "to": to, "kind": kind, "text": text[:600], "symbol": symbol})


def parse_json(text: str) -> dict | None:
    if not text:
        return None
    t = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    try:
        return json.loads(t)
    except Exception:
        pass
    m = re.search(r"\{.*\}", t, re.S)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            return None
    return None


async def run_agent(room: Room, agent: Agent, task: str, symbol: str | None = None) -> dict:
    """ReAct loop for one agent. Returns its parsed JSON report (with _meta)."""
    model = agent.model or config.AGENT_MODELS.get(agent.id) or config.LLM_MODEL
    msgs = [{"role": "system", "content": agent.system()}, {"role": "user", "content": task}]
    schema = T.schema(agent.tools)
    used = []
    async with room.sem:
        await room.say({"type": "agent_state", "agent": agent.id, "state": "thinking", "symbol": symbol, "text": "بيقرا المهمة"})
        for step in range(agent.max_steps + 1):
            last = step == agent.max_steps
            try:
                room.usage["calls"] += 1
                msg = await asyncio.to_thread(llm.chat_tools, msgs, None if last else schema, model)
            except Exception as e:
                await room.say({"type": "agent_state", "agent": agent.id, "state": "error", "symbol": symbol, "text": f"فشل الاتصال بالنموذج: {e}"[:300]})
                return {"_meta": {"agent": agent.id, "error": str(e), "tools": used}}
            if msg["content"] and msg["tool_calls"]:
                await room.say({"type": "agent_thought", "agent": agent.id, "symbol": symbol, "text": msg["content"][:800]})
            if msg["tool_calls"] and not last:
                msgs.append({"role": "assistant", "content": msg["content"] or None, "tool_calls": msg["tool_calls"]})
                for tc in msg["tool_calls"]:
                    name = tc["function"]["name"]
                    try:
                        args = json.loads(tc["function"].get("arguments") or "{}")
                    except Exception:
                        args = {}
                    await room.say({"type": "agent_state", "agent": agent.id, "state": "tool", "symbol": symbol, "text": f"بيفتح {name}"})
                    await room.say({"type": "agent_tool", "agent": agent.id, "tool": name, "args": args, "symbol": symbol})
                    if name not in agent.tools:
                        out = {"error": f"الأداة {name} مش من أدواتك. أدواتك: {', '.join(agent.tools)}"}
                    else:
                        try:
                            slim, full = await asyncio.to_thread(T.call, room.ctx, name, args)
                            room.usage["tools"] += 1
                            used.append(name)
                            room.ledger.append({"agent": agent.id, "tool": name, "args": args, "result": slim})
                            out = slim
                            await room.say({"type": "agent_tool_done", "agent": agent.id, "tool": name, "args": args,
                                            "symbol": symbol, "summary": slim.get("summary"), "source": slim.get("source"),
                                            "result": full})
                        except Exception as e:
                            out = {"error": str(e)}
                    msgs.append({"role": "tool", "tool_call_id": tc.get("id", name), "content": T.dumps(out)[:12000]})
                await room.say({"type": "agent_state", "agent": agent.id, "state": "thinking", "symbol": symbol, "text": "بيفكر في النتيجة"})
                continue
            report = parse_json(msg["content"])
            if report is None and not last:
                msgs.append({"role": "assistant", "content": msg["content"]})
                msgs.append({"role": "user", "content": "رد بـ JSON صحيح بس، بالشكل المطلوب."})
                continue
            report = report or {"summary": (msg["content"] or "")[:500], "unparsed": True}
            report["_meta"] = {"agent": agent.id, "tools": used, "model": model, "steps": step + 1}
            await room.say({"type": "agent_state", "agent": agent.id, "state": "done", "symbol": symbol,
                            "text": str(report.get("summary") or report.get("verdict") or "خلص")[:200]})
            await room.say({"type": "agent_report", "agent": agent.id, "symbol": symbol, "report": report})
            return report
    return {"_meta": {"agent": agent.id, "error": "no report", "tools": used}}
