"""The Telegram bot's /plan and /smt (scripts/xpix_bot.py) with fake data, no network, no Telegram. Run: PYTHONPATH=. python tests/test_xpix_bot_plan.py"""
import os, sys, types
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.modules.setdefault("playwright", types.ModuleType("playwright")); pa = types.ModuleType("playwright.sync_api"); pa.sync_playwright = lambda: None; sys.modules["playwright.sync_api"] = pa
import xpix_bot as B
from modules import day_plan as D, intermarket as IM
sent = []
B.tg = lambda method, **kw: sent.append((method, kw)) or {}
B.OWNER = "1"
seen = {}
D.scan = lambda syms, fetch, mode="conf", **kw: seen.update(syms=syms, mode=mode, kw=kw) or []
B.handle(None, "/plan scalp 5m gold-usdt")
assert seen["mode"] == "scalp" and seen["kw"]["trigger_tfs"] == ("5m",) and seen["syms"] == ["GOLD-USDT"], seen
assert sent[-1][0] == "sendMessage" and sent[-1][1]["data"]["parse_mode"] == "HTML" and "خطة اليوم" in sent[-1][1]["data"]["text"], sent[-1]
B.handle(None, "/plan")
assert seen["mode"] == "conf" and "BTC-USDT" in seen["syms"] and "HL:xyz:GOLD" in seen["syms"]
IM.scan_pairs = lambda fetch, **k: []
B.handle(None, "/smt")
assert "No clear SMT" in sent[-1][1]["data"]["text"]
B.handle(None, "/help")
assert "/plan" in sent[-1][1]["data"]["text"] and "/smt" in sent[-1][1]["data"]["text"]
print("ok bot /plan /smt /help")
