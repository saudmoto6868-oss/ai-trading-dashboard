"""TIA walls panel: the JS live-threshold rule (modules/tia_walls_block.js, twLiveWalls) gives the SAME walls as the
Python reference of the same rule on random books (node, no browser). Run: python3 tests/test_tia_walls_js.py"""
import json, os, random, re, subprocess, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(ROOT, "modules", "tia_walls_block.js"), encoding="utf8").read()
core = re.search(r"/\* TIAWALLS-CORE-BEGIN \*/\n(.*?)/\* TIAWALLS-CORE-END \*/", src, re.S).group(1)


def py_walls(snaps, tick, k, pctl, window):
    """Reference: same rule as tia.analytics.walls (rolling quantile over `window` snapshots, strict >, floor k x median)."""
    last = snaps[-1]
    mid = (last["bids"][0][0] + last["asks"][0][0]) / 2
    out = []
    frm = max(0, len(snaps) - window)
    for side, key in (("bid", "bids"), ("ask", "asks")):
        pool = sorted(q for s in snaps[frm:] for _, q in s[key])
        med = pool[len(pool) // 2]
        if med <= 0:
            continue
        thr = max(k * med, pool[min(len(pool) - 1, int(pctl * len(pool)))])
        out += [(side, p, q) for p, q in last[key] if q > thr]
    return sorted(out)


def random_snaps(seed, n=150):
    r = random.Random(seed); snaps = []
    for i in range(n):
        ask0 = 100 + r.randint(1, 3)
        bids = [[ask0 - 1 - j, r.choice([0.01, 0.5, 2, 5, 40]) if r.random() < 0.9 else 0.02] for j in range(10)]
        asks = [[ask0 + j, r.choice([0.01, 0.5, 2, 5, 40]) if r.random() < 0.9 else 0.02] for j in range(10)]
        if i > n - 5:
            asks[3][1] = 900
        snaps.append({"bids": bids, "asks": asks})
    return snaps


def main():
    if not shutil.which("node"):
        print("SKIP: node not installed"); return
    cases = [random_snaps(s) for s in (1, 2, 3)]
    script = "const SNAPS=JSON.parse(require('fs').readFileSync(0,'utf8'));" + core + \
             "const out=SNAPS.map(c=>twLiveWalls(c.s,1,6,0.99,120).walls.map(w=>[w.side,w.price,w.q]).sort());console.log(JSON.stringify(out));"
    payload = [{"s": [{"bids": [{"p": a, "q": b} for a, b in s["bids"]], "asks": [{"p": a, "q": b} for a, b in s["asks"]]} for s in c]} for c in cases]
    got = json.loads(subprocess.run(["node", "-e", script], input=json.dumps(payload), capture_output=True, text=True, check=True).stdout)
    for c, g in zip(cases, got):
        want = py_walls([{"bids": s["bids"], "asks": s["asks"]} for s in c], 1, 6, 0.99, 120)
        assert [tuple(x) for x in g] == [(a, float(b), float(q)) for a, b, q in want], (g, want)
    print("OK: JS walls == Python reference on", len(cases), "random books; walls per case:", [len(g) for g in got])


if __name__ == "__main__":
    main()
