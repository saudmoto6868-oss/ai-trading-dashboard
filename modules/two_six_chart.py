"""2.6 on a chart: H1 retracement and H2 liquidity setups with entry / stop / targets.

Entries come from the research engine (research/strategies/2.6). Stop and targets
are PROVISIONAL house rules until the creator's rules are confirmed. With
u = leg range / ratio:
  H1 BUY  (low -> high leg):  entry = high - u, stop = entry - u, TP1 = high, TP2 = high + u
  H1 SELL (high -> low leg):  entry = low + u,  stop = entry + u, TP1 = low,  TP2 = low - u
  H2 SELL (equal highs swept): entry = pool + u, stop = entry + u, TP1 = pool, TP2 = pool - u
  H2 BUY  (equal lows swept):  entry = pool - u, stop = entry - u, TP1 = pool, TP2 = pool + u
So TP1 = 1R and TP2 = 2R everywhere. A bar touching stop and a target counts as stop.
"""
import importlib.util
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE = os.path.join(ROOT, "research", "strategies", "2.6")
LIB = os.path.join(ROOT, "research", "cfx", "dashboard", "vendor", "lightweight-charts.standalone.production.js")


def _load(name, file):
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, os.path.join(ENGINE, file))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
    return sys.modules[name]


es = _load("event_study", "event_study.py")
h2 = _load("two_six_h2", "h2_liquidity.py")


def bars_from_df(df):
    return [es.Bar(str(i), float(r.open), float(r.high), float(r.low), float(r.close))
            for i, r in enumerate(df.itertuples(index=False))]


def _play(bars, kind, side, known, entry, stop, tp1, tp2, wait, anchors):
    n = len(bars)
    s = {"kind": kind, "side": side, "known": known, "entry": entry, "stop": stop, "tp1": tp1,
         "tp2": tp2, "anchors": anchors, "fill": None, "exit": None, "tp1_hit": False}
    fill, price = es.find_fill(bars, side, entry, known + 1, min(n - 1, known + wait))
    if fill is None:
        s["status"] = "waiting" if known + wait >= n - 1 else "expired"
        s["exit"] = None if s["status"] == "waiting" else known + wait   # chart lines stop at expiry
        return s
    s["fill"], s["entry"] = fill, price
    buy = side == "BUY"
    for i in range(fill + 1, n):
        b = bars[i]
        if (b.low <= stop) if buy else (b.high >= stop):
            s["status"], s["exit"] = ("TP1 then stop" if s["tp1_hit"] else "stopped"), i
            return s
        if (b.high >= tp2) if buy else (b.low <= tp2):
            s["status"], s["exit"] = "TP2", i
            return s
        if (b.high >= tp1) if buy else (b.low <= tp1):
            s["tp1_hit"] = True
    s["status"] = "open (TP1 hit)" if s["tp1_hit"] else "open"
    return s


def setups(bars, ratio=2.6, left=3, right=3, wait=80, eq_tol=0.0005, use_h1=True, use_h2=True):
    """Every H1 / H2 setup in the bars, oldest first, each with its provisional trade plan."""
    pivots = es.confirmed_pivots(bars, left, right)
    legs = [(side, a, b, span, max(a.known_at, b.known_at))
            for side, a, b, span in es.make_legs(pivots) if span > 0]
    out = []
    if use_h1:
        for side, a, b, span, known in legs:
            if known >= len(bars) - 1:
                continue
            u = span / ratio
            sgn = 1 if side == "BUY" else -1
            entry = b.price - sgn * u
            out.append(_play(bars, "H1", side, known, entry, entry - sgn * u, b.price, b.price + sgn * u,
                             wait, [a.idx, b.idx]))
    if use_h2:
        seen = set()
        for kind, level, p1, p2, known in h2.liquidity_pools(bars, pivots, eq_tol):
            sweep = h2.find_sweep(bars, kind, level, known, 200)
            if sweep is None or (kind, sweep) in seen:
                continue
            seen.add((kind, sweep))
            side = "SELL" if kind == "H" else "BUY"
            prior = [leg for leg in legs if leg[0] == side and leg[4] <= sweep]
            if not prior:
                continue
            _, a, b, span, _ = max(prior, key=lambda leg: (leg[4], leg[2].idx))
            u = span / ratio
            sgn = 1 if side == "BUY" else -1
            entry = level - sgn * u
            out.append(_play(bars, "H2", side, sweep, entry, entry - sgn * u, level, level + sgn * u,
                             wait, [p1.idx, p2.idx, sweep, a.idx, b.idx]))
    out.sort(key=lambda s: s["known"])
    return out


def chart_html(df, plays, height=560):
    """Self-contained Lightweight Charts page: candles, measured legs, entry / stop / TP lines, markers."""
    times = [int(t.timestamp()) for t in df["time"]]
    candles = [{"time": t, "open": float(o), "high": float(h), "low": float(lo), "close": float(c)}
               for t, o, h, lo, c in zip(times, df["open"], df["high"], df["low"], df["close"])]
    with open(LIB, encoding="utf-8") as f:
        lib = f.read().replace("</script", "<\\/script")
    data = json.dumps({"c": candles, "t": times, "p": plays}).replace("</", "<\\/")
    return """<div id="c" style="width:100%;height:{h}px"></div><script>{lib}</script><script>
const D={data},T=D.t,el=document.getElementById('c');
const ch=LightweightCharts.createChart(el,{{width:el.clientWidth,height:{h},layout:{{background:{{color:'#0e1117'}},textColor:'#ccc'}},
 grid:{{vertLines:{{color:'#1c2030'}},horzLines:{{color:'#1c2030'}}}},timeScale:{{timeVisible:true}}}});
const cs=ch.addCandlestickSeries({{upColor:'#26a69a',downColor:'#ef5350',borderVisible:false,wickUpColor:'#26a69a',wickDownColor:'#ef5350'}});
cs.setData(D.c);
const seg=(i,j,v,color,style)=>{{if(j<=i)return;const s=ch.addLineSeries({{color,lineWidth:style===2?1:2,lineStyle:style||0,
 priceLineVisible:false,lastValueVisible:false,crosshairMarkerVisible:false}});s.setData([{{time:T[i],value:v}},{{time:T[j],value:v}}]);}};
const mk=[],last=T.length-1;
D.p.forEach(p=>{{const buy=p.side==='BUY',end=p.exit??last,a=p.anchors;
 const leg=ch.addLineSeries({{color:'#8888ff',lineWidth:1,lineStyle:2,priceLineVisible:false,lastValueVisible:false}});
 const li=p.kind==='H1'?[a[0],a[1]]:[a[3],a[4]];
 leg.setData([{{time:T[li[0]],value:buy?D.c[li[0]].low:D.c[li[0]].high}},{{time:T[li[1]],value:buy?D.c[li[1]].high:D.c[li[1]].low}}]);
 if(p.kind==='H2'){{seg(a[0],a[2],p.tp1,'#f0b429',2);mk.push({{time:T[a[2]],position:buy?'belowBar':'aboveBar',color:'#f0b429',shape:'circle',text:'sweep'}});}}
 seg(p.known,end,p.entry,buy?'#26a69a':'#ef5350');seg(p.known,end,p.stop,'#ff4d4f',2);
 seg(p.known,end,p.tp1,'#4da3ff',2);seg(p.known,end,p.tp2,'#4da3ff',2);
 if(p.fill!=null)mk.push({{time:T[p.fill],position:buy?'belowBar':'aboveBar',color:buy?'#26a69a':'#ef5350',shape:buy?'arrowUp':'arrowDown',text:p.kind+' '+p.side}});
 if(p.exit!=null&&p.fill!=null)mk.push({{time:T[p.exit],position:buy?'aboveBar':'belowBar',color:p.status==='TP2'?'#4da3ff':'#ff4d4f',shape:'square',text:{{'TP2':'TP2','stopped':'SL','TP1 then stop':'TP1→SL'}}[p.status]||p.status}});
}});
mk.sort((x,y)=>x.time-y.time);cs.setMarkers(mk);const first=D.p.length?Math.min(...D.p.map(p=>p.kind==='H1'?p.anchors[0]:p.anchors[3])):0;
ch.timeScale().setVisibleLogicalRange({{from:Math.max(0,Math.min(first-10,last-120)),to:last+5}});
addEventListener('resize',()=>ch.applyOptions({{width:el.clientWidth}}));
</script>""".format(h=height, lib=lib, data=data)
