"""Server price alarms: modules/palarm_core.py gives the same answers as the browser's PALARM-PURE block (node), merge keeps the
right fired state, palarm_server.run() catches a cross between two runs and sends once, sync() stores the browser list. Plain script."""
import json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from modules import palarm_core as P   # noqa: E402
from modules import palarm_server as S   # noqa: E402

# 1) parity with the JS on the same cases (hit + check over a sequence of steps)
HITS = [({"cond": "cross"}, 99, 100, None), ({"cond": "cross"}, 101, 99.5, None), ({"cond": "cross"}, 99, 99.9, None), ({"cond": "cross"}, None, 101, None),
        ({"cond": "up"}, 99, 101, None), ({"cond": "down"}, 99, 101, None), ({"cond": "gt"}, None, 100, None), ({"cond": "lt"}, None, 99, None),
        ({"cond": "enter", "v2": 110}, 99, 105, None), ({"cond": "exit", "v2": 110}, 105, 111, None), ({"cond": "inside", "v2": 90}, None, 95, None),
        ({"cond": "outside", "v2": 110}, None, 95, None), ({"cond": "enter", "v": 110, "v2": 100}, 111, 108, None),
        ({"cond": "mup", "v": 5, "n": 2}, None, 106, [100, 101, 106]), ({"cond": "mup", "v": 5, "n": 2}, None, 104, [100, 101, 104]),
        ({"cond": "mdnp", "v": 2, "n": 1}, None, 97, [100, 97]), ({"cond": "mupp", "v": 2, "n": 5}, None, 120, [100, 120])]
rows = lambda t, c: [{"t": x, "c": c[i]} for i, x in enumerate(t)]   # noqa: E731
SEQS = [({"cond": "cross", "v": 100, "on": True, "trig": "once"}, [({"p0": 99, "p1": 101, "curT": 1, "rows": rows([1], [101])}, 1000), ({"p0": 99, "p1": 101, "curT": 2, "rows": []}, 2000)]),
        ({"cond": "gt", "v": 100, "on": True, "trig": "bar"}, [({"p0": 101, "p1": 102, "curT": 5, "rows": []}, 1), ({"p0": 102, "p1": 103, "curT": 5, "rows": []}, 2), ({"p0": 103, "p1": 104, "curT": 6, "rows": []}, 3)]),
        ({"cond": "gt", "v": 100, "on": True, "trig": "min"}, [({"p1": 101, "rows": []}, 1000), ({"p1": 101, "rows": []}, 30000), ({"p1": 101, "rows": []}, 62000)]),
        ({"cond": "up", "v": 100, "on": True, "trig": "close"}, [({"p1": 105, "rows": rows([1, 2, 3], [98, 99, 105])}, 1), ({"p1": 99, "rows": rows([1, 2, 3, 4], [98, 99, 101, 99])}, 2),
                                                               ({"p1": 99, "rows": rows([1, 2, 3, 4], [98, 99, 101, 99])}, 3)]),
        ({"cond": "gt", "v": 100, "on": True, "trig": "bar", "exp": 500}, [({"p1": 101, "rows": []}, 1000)])]
TXT = [({"sym": "BTC-USDT", "cond": "cross", "v": 100, "tf": "1H", "msg": "{{ticker}} at {{close}} on {{interval}}"}, 101.5),
       ({"sym": "ETH-USDT", "cond": "enter", "v": 1, "v2": 2}, 1.5)]


def py_side():
    hits = [P.hit({"v": 100, **a}, p0, p1, c) for a, p0, p1, c in HITS]
    seqs = []
    for a0, steps in SEQS:
        a = dict(a0)
        seqs.append([P.check(a, st, now) for st, now in steps] + [a.get("on"), a.get("status")])
    return {"hits": hits, "seqs": seqs, "txt": [P.text(a, px) for a, px in TXT]}


py = py_side()
assert py["hits"] == [True, True, False, False, True, False, False, True, True, True, True, True, True, True, False, True, False], py["hits"]
if shutil.which("node"):
    src = open(os.path.join(ROOT, "modules", "ws", "21d_price_alarms.js"), encoding="utf-8").read()
    pure = re.search(r"/\* PALARM-PURE-START.*?\*/(.*?)/\* PALARM-PURE-END \*/", src, re.S).group(1)
    js = pure + "\nconst D = " + json.dumps({"HITS": HITS, "SEQS": SEQS, "TXT": TXT}) + r""";
const hits = D.HITS.map(([a, p0, p1, c]) => palarmHit(Object.assign({v:100}, a), p0, p1, c));
const seqs = D.SEQS.map(([a0, steps]) => { const a = Object.assign({}, a0); const r = steps.map(([st, now]) => palarmCheck(a, st, now)); return r.concat([a.on, a.status === undefined ? null : a.status]); });
console.log(JSON.stringify({hits, seqs, txt: D.TXT.map(([a, px]) => palarmText(a, px))}));"""
    r = subprocess.run([shutil.which("node"), "-e", js], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert json.loads(r.stdout) == py, (r.stdout, py)
    print("ok palarm parity with the browser")
else:
    print("skip parity (no node)")

# server range: a cross between two runs is caught from the high / low since the last check
assert P.hit({"cond": "up", "v": 100}, 99, 98, hi=100.5) and not P.hit({"cond": "up", "v": 100}, 99, 98)
assert P.hit({"cond": "down", "v": 100}, 101, 102, lo=99.9) and P.hit({"cond": "cross", "v": 100}, 101, 102, lo=99.9)
assert P.tf_server("1H") == "1h" and P.tf_server("4H") == "4h" and P.tf_server("1D") == "1d" and P.tf_server("5m") == "5m" and P.tf_server("") == "1m"

# 2) merge: browser owns settings; the later fire owns fired state; an edit after the fire wins; junk dropped
srv = [{"id": "a", "v": 1, "on": False, "status": "triggered", "lastT": 500}, {"id": "b", "v": 2, "on": False, "lastT": 500}]
cli = [{"id": "a", "v": 1.5, "on": True, "lastT": 100, "editT": 200}, {"id": "b", "v": 2, "on": True, "editT": 900}, {"id": "c"}, "x", {"v": 3}]
m = {a["id"]: a for a in P.merge(srv, cli)}
assert set(m) == {"a", "b"} and m["a"]["on"] is False and m["a"]["v"] == 1.5 and m["a"]["status"] == "triggered"
assert m["b"]["on"] is True   # re-enabled after the server fired it


# 3) run(): fake store / candles / telegram / http
class Store:
    kind = "github"

    def __init__(self, d=None):
        self.d, self.puts = d, 0

    def get_json(self, name):
        return json.loads(json.dumps(self.d)) if self.d is not None else None

    def put_json(self, name, d, msg=""):
        self.d, self.puts = json.loads(json.dumps(d)), self.puts + 1


class Http:
    def __init__(self):
        self.calls = []

    def post(self, url, **k):
        self.calls.append(("post", url))

    def get(self, url, **k):
        self.calls.append(("get", url, k.get("params", {}).get("user")))


NOW = 10_000_000_000
m1 = [{"t": NOW - (60 - i) * 60000, "h": 99.5, "l": 99, "c": 99.2} for i in range(60)]
m1[40]["h"] = 100.4   # touched 100 twenty minutes ago, back under it now
feeds = {"1m": m1, "1h": [{"t": NOW - 3600000, "h": 100.4, "l": 98, "c": 99}, {"t": NOW, "h": 99.5, "l": 99, "c": 99.2}]}
st = Store({"alarms": [{"id": "u", "sym": "BTC-USDT", "cond": "up", "v": 100, "tf": "1H", "on": True, "trig": "once", "editT": NOW - 7200000, "ch": {"push": True, "call": True}},
                       {"id": "off", "sym": "BTC-USDT", "cond": "gt", "v": 1, "on": False}],
            "notify": {"ntfy": "topic-x", "tg": "@me"}})
sent, http = [], Http()
n = S.run(store=st, rows=lambda s, tf: feeds[tf], send=lambda t: sent.append(t), http=http, now=NOW, log=lambda *a: None)
assert n == 1 and len(sent) == 1 and "BTC-USDT Crossing Up 100" in sent[0], sent
assert ("post", "https://ntfy.sh/topic-x") in http.calls and ("get", "https://api.callmebot.com/start.php", "@me") in http.calls
assert st.puts == 1 and st.d["alarms"][0]["on"] is False and st.d["alarms"][0]["status"] == "triggered"
assert S.run(store=st, rows=lambda s, tf: feeds[tf], send=lambda t: sent.append(t), http=http, now=NOW + 1800000, log=lambda *a: None) == 0 and len(sent) == 1
# no price data -> nothing fires, nothing saved
st2 = Store({"alarms": [{"id": "g", "sym": "X", "cond": "gt", "v": 1, "on": True, "trig": "bar"}]})
assert S.run(store=st2, rows=lambda s, tf: [], send=lambda t: sent.append(t), http=http, now=NOW, log=lambda *a: None) == 0 and st2.puts == 0
print("ok palarm server run")

# 4) sync(): stores the merged list + only the topic / user (no keys), answers with kind=palarms
st3 = Store({"alarms": [{"id": "a", "v": 1, "on": False, "lastT": 500}]})
ans = S.sync({"id": "pa1", "kind": "palarms", "list": [{"id": "a", "v": 1, "on": True, "lastT": 100}, {"bad": 1}], "notify": {"ntfy": "t", "tg": "@u", "waKey": "SECRET"}}, store=st3)
assert ans["ok"] and ans["kind"] == "palarms" and ans["id"] == "pa1" and ans["list"][0]["on"] is False
assert st3.d["notify"] == {"ntfy": "t", "tg": "@u"} and "SECRET" not in json.dumps(st3.d)
assert S.sync({"id": "pa2", "list": ans["list"], "notify": {"ntfy": "t", "tg": "@u"}}, store=st3)["ok"] and st3.puts == 1   # nothing changed: no write
print("ok palarm sync")
