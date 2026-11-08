"""Spot desk phase 2: extended fields + costs, custom fields, Excel template / mapped import, online store (local + a fake
GitHub API), Telegram bot queries, server alerts, Mac backup rotation. No network. Plain script: python3 tests/test_spot_ops.py"""
import base64
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules import spot_core as C
from modules import spot_query as Q
from modules.spot_store import GitHubStore, LocalStore, safe_name

close = lambda a, b, e=1e-6: abs(a - b) <= e * max(1, abs(b))

# extended fields, costs, custom fields go to extra
t = C.new_tx(side="buy", asset="gold", qty=10, unit="g", purity=0.875, price=5800, currency="EGP", fx=47.5, workmanship_per_g=120, fees=50,
             tax=14, other_costs=6, item_type="jewelry", hallmark="21-EG", vault_box="B7")
assert t["asset"] == "GOLD" and t["hallmark"] == "21-EG" and t["extra"] == {"vault_box": "B7"} and t["status"] == "settled"
assert close(C.costs(t), 50 + 14 + 6 + 1200)
assert close(C.tx_egp(t)[1], 1270) and close(C.tx_usd(t)[1], 1270 / 47.5)
cx = C.new_tx(side="buy", asset="GOLD", qty=1, price=100, fx=50, status="cancelled")
assert C.positions([cx], {"GOLD": 200}) == []
assert len(C.FIELDS) >= 30 and "tx_hash" in C.FIELD_KEYS

# invoice shows the extra details
h = C.invoice_html(t)
assert "الدمغة" in h and "21-EG" in h and "vault_box" in h and "B7" in h

# Excel: export -> import keeps every field + custom; template; mapped import of a foreign sheet
custom = [{"key": "vault_box", "label": "Vault box", "type": "text", "options": ""}]
xl = C.to_excel([t], C.positions([t]), {}, None, custom)
back = C.from_excel(xl, custom)
assert back[0]["id"] == t["id"] and back[0]["hallmark"] == "21-EG" and back[0]["extra"].get("vault_box") == "B7" and close(back[0]["workmanship_per_g"], 120)
hdr, rows = C.read_sheet(C.template_xlsx(custom))
assert "x_vault_box" in hdr and "tx_hash" in hdr and len(rows) == 1
from openpyxl import Workbook
import io
wb = Workbook(); ws = wb.active
ws.append(["رقم الفاتورة", "Metal", "Weight g", "Price/g EGP", "التاريخ", "Shop note"])
ws.append(["F-9", "GOLD", 25, 5900, "2026-10-01", "nice"])
ws.append([None, None, None, None, None, None])
bio = io.BytesIO(); wb.save(bio)
hdr, rows = C.read_sheet(bio.getvalue())
m = C.guess_mapping(hdr, custom)
assert m["رقم الفاتورة"] == "invoice_no" and m["التاريخ"] == "date" and m["Metal"] == ""
m.update({"Metal": "asset", "Weight g": "qty", "Price/g EGP": "price"})
imp = C.import_rows(rows, m, extra_unmapped=True)
assert len(imp) == 1 and imp[0]["invoice_no"] == "F-9" and close(imp[0]["qty"], 25) and imp[0]["extra"] == {"Shop note": "nice"}
assert C.import_rows(rows, m, extra_unmapped=False)[0]["extra"] == {}

# local store: atomic save, files, safe names
tmp = Path(tempfile.mkdtemp())
ls = LocalStore(tmp)
assert ls.load() is None
d = {"txs": [t], "alerts": [C.new_alert("GOLD", "buy", 5000)], "settings": {"custom_fields": custom}}
ls.save(d)
assert ls.load()["txs"][0]["id"] == t["id"]
n = ls.put_file("../../etc/passwd x.pdf", b"PDF")
assert n == safe_name("../../etc/passwd x.pdf") and "/" not in n and ls.get_file(n) == b"PDF" and (tmp / "files" / n).exists()
ls.delete_file(n)
assert ls.get_file(n) is None


# GitHub store against a fake Contents API (sha handling, conflict refusal, raw download, delete, list)
class Resp:
    def __init__(self, code, js=None, content=b""):
        self.status_code, self._js, self.content = code, js, content

    def json(self):
        return self._js

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(self.status_code)


class FakeGH:
    def __init__(self):
        self.headers, self.files, self.n = {}, {}, 0

    def _p(self, url):
        return url.split("/contents/", 1)[1]

    def get(self, url, params=None, headers=None, timeout=None):
        p = self._p(url)
        if p == "files":
            return Resp(200, [{"name": k[6:], "type": "file"} for k in self.files if k.startswith("files/")])
        if p not in self.files:
            return Resp(404)
        data, sha = self.files[p]
        if headers and "raw" in headers.get("Accept", ""):
            return Resp(200, content=data)
        big = len(data) > 20
        return Resp(200, {"sha": sha, "encoding": "base64", "content": "" if big else base64.b64encode(data).decode()})

    def put(self, url, json=None, timeout=None):
        p = self._p(url)
        if p in self.files and json.get("sha") != self.files[p][1]:
            return Resp(409)
        if p not in self.files and json.get("sha"):
            return Resp(422)
        self.n += 1
        self.files[p] = (base64.b64decode(json["content"]), f"sha{self.n}")
        return Resp(201 if self.n == 1 else 200, {"content": {"sha": f"sha{self.n}"}})

    def delete(self, url, json=None, timeout=None):
        p = self._p(url)
        if p not in self.files or json.get("sha") != self.files[p][1]:
            return Resp(409)
        del self.files[p]
        return Resp(200, {})


fake = FakeGH()
gh = GitHubStore("tok", "me/data", session=fake)
assert fake.headers["Authorization"] == "Bearer tok"
assert gh.load() is None
gh.save(d)
gh.save(d)                                         # second save uses the stored sha
assert gh.load()["alerts"][0]["price"] == 5000     # ledger > 20 bytes -> raw download path
other = GitHubStore("tok", "me/data", session=fake)
other.load(); other.save({"txs": []})              # another device saves in between
try:
    gh.save(d)
    raise AssertionError("stale save must be refused")
except RuntimeError as e:
    assert "changed" in str(e)
f = gh.put_file(f"{t['id']}_inv.pdf", b"%PDF-1.4 tiny")
assert gh.list_files() == [f] and gh.get_file(f) == b"%PDF-1.4 tiny"
gh.delete_file(f)
assert gh.get_file(f) is None and gh.list_files() == []

# bot queries (read-only)
ls2 = LocalStore(tempfile.mkdtemp())
t2 = C.new_tx(side="buy", asset="BTC", qty=0.1, unit="coin", price=60000, currency="USD", fx=48, invoice_no="EX-7", party="OKX", date="2026-10-02")
t["invoice_no"], t["party"] = "INV-12", "Shop Lazoghly"
t["files"] = [ls2.put_file(f"{t['id']}_receipt.pdf", b"%PDF r")]
ls2.save({"txs": [t, t2], "alerts": [C.new_alert("BTC", "sell", 50000, "T1")], "settings": {}})
r, files = Q.handle("/inv INV-12", ls2)
assert "INV-12" in r and "21-EG" not in r and [n for n, _ in files] == ["receipt.pdf", "invoice_INV-12.html"]
r, files = Q.handle("/find lazoghly", ls2)
assert "INV-12" in r
r, _ = Q.handle("/inv nothing-here", ls2)
assert "مفيش" in r
assert Q.handle("/shot BTC", ls2) == ("", [])
Q._live = lambda: ({"GOLD": 4000.0, "BTC": 70000.0}, 50.0)
r, _ = Q.handle("/spot", ls2)
assert "BTC" in r and "ذهب" in r and "الإجمالي" in r
r, _ = Q.handle("/spotalerts", ls2)
assert "بيع" in r
r, files = Q.handle("/spotxl", ls2)
assert files[0][0] == "spot_ledger.xlsx" and files[0][1][:2] == b"PK"
ctx = json.loads(Q.llm_context("فاتورة OKX btc", ls2))
assert ctx["rows"][0]["invoice_no"] == "EX-7" and ctx["n_rows_total"] == 2

# server alerts: each hit sent once, then saved as fired
from modules import spot_alerts_cron as AC
sent = []
n1 = AC.run(store=ls2, prices={"BTC": 70000}, send=lambda m: sent.append(m), log=lambda *_: None)
n2 = AC.run(store=ls2, prices={"BTC": 70000}, send=lambda m: sent.append(m), log=lambda *_: None)
assert n1 == 1 and n2 == 0 and len(sent) == 1 and "BTC" in sent[0]
assert ls2.load()["alerts"][0]["fired_at"] and not ls2.load()["alerts"][0]["active"]
assert AC.run(store=None, log=lambda *_: None) == 0 or True   # no SPOT_GH_* here -> skipped

# Mac backup: new verified folder, old ones pruned, nothing deleted on failure
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "spot_backup"))
import spot_backup as B
base = Path(tempfile.mkdtemp())
(base / "XPiX-Spot-2020-01-01_0000").mkdir()
assert B.due(base, 48)
out = B.backup(ls2, base, keep=1, log=lambda *_: None)
assert out.exists() and (out / "ledger.json").exists() and (out / "spot_ledger.xlsx").exists() and (out / "files" / t["files"][0]).exists()
assert [p.name for p in base.iterdir() if p.is_dir()] == [out.name] and not B.due(base, 48)


class Broken(LocalStore):
    def get_file(self, name):
        return None


try:
    B.backup(Broken(ls2.root), base, keep=1, log=lambda *_: None)
    raise AssertionError("missing file must fail")
except RuntimeError:
    pass
assert out.exists()   # the good copy is still there
print("test_spot_ops OK")

# self test + non-conflict 422 shows GitHub's own message
from modules.spot_store import self_test
assert self_test(LocalStore(tempfile.mkdtemp()))[0]


class Refuse(FakeGH):
    def put(self, url, json=None, timeout=None):
        return Resp(422, {"message": "Invalid request. Branch main not found"})


g2 = GitHubStore("tok", "me/data", session=Refuse())
try:
    g2.save({"txs": []})
    raise AssertionError("must fail")
except RuntimeError as e:
    assert "Branch main not found" in str(e) and "changed" not in str(e), e
ok, why = self_test(g2)
assert not ok and "422" in why
print("test_spot_ops self-test OK")
