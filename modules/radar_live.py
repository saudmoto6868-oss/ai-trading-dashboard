"""Live Radar chart card (owner 2026-11-16): a moving chart per symbol, drawn in the browser.

What the card does
- History: OKX public REST candles for the chosen timeframe (the timeframe is a dropdown inside the card).
- Live: OKX public websocket, the current candle and the last price update as trades come in.
- Own price axis and time axis on every card, plus a last-price line and a live price label.
- Only OKX spot symbols ("BASE-USDT") get the live card. Yahoo ("Y:") and Hyperliquid ("HL:") symbols keep the
  server-side picture (see main.py), because they have no OKX feed.

Nothing here places an order. The page is a plain HTML document shown with st.components.v1.html."""
from __future__ import annotations

import html
import json
import re

# OKX public endpoints (no key). Used from the browser, so the page works without server access to the exchange.
OKX_REST = "https://www.okx.com/api/v5/market/candles"
OKX_WS = "wss://ws.okx.com:8443/ws/v5/public"
# lightweight-charts 4.2.1 (open source, released before this change); pinned version from jsDelivr
LWC_URL = "https://cdn.jsdelivr.net/npm/lightweight-charts@4.2.1/dist/lightweight-charts.standalone.production.js"

# Radar timeframe (lower case, as the app uses) -> OKX bar name
OKX_BAR = {"1m": "1m", "3m": "3m", "5m": "5m", "13m": "3m", "15m": "15m", "30m": "30m", "1h": "1H", "2h": "2H",
           "3h": "1H", "4h": "4H", "6h": "6H", "7h": "1H", "8h": "2H", "12h": "12H", "1d": "1D", "3d": "1D",
           "1w": "1W", "1mo": "1M"}
LIVE_TFS = ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "1d", "1w"]   # the choices offered inside the card


def is_okx_spot(sym: str) -> bool:
    """True for OKX spot instIds such as BTC-USDT (not Yahoo 'Y:' or Hyperliquid 'HL:' symbols, not options/swaps)."""
    return bool(re.fullmatch(r"[A-Z0-9]{2,12}-[A-Z]{2,6}", sym or ""))


def live_card_html(sym: str, tf: str, height_px: int = 300) -> str | None:
    """Full HTML document for one live card, or None when the symbol has no OKX live feed."""
    if not is_okx_spot(sym):
        return None
    bar = OKX_BAR.get(tf, "1H")
    tfs = LIVE_TFS if tf in LIVE_TFS else [tf] + LIVE_TFS
    cfg = {"sym": sym, "bar": bar, "tf": tf, "tfs": [[t, OKX_BAR.get(t, "1H")] for t in tfs], "rest": OKX_REST, "ws": OKX_WS}
    opts = "".join(f"<option value='{html.escape(t)}'{' selected' if t == tf else ''}>{html.escape(t)}</option>" for t in tfs)
    return f"""<!doctype html><html><head><meta charset='utf-8'>
<meta name='viewport' content='width=device-width,initial-scale=1'>
<style>
html,body{{margin:0;background:#0b0e11;color:#c9d1d9;font:11px ui-monospace,Menlo,monospace;overflow:hidden}}
#bar{{display:flex;align-items:center;gap:8px;height:22px;padding:0 4px}}
#bar b{{color:#eaecef}} #px{{color:#eaecef;font-weight:700}} #chg{{font-weight:600}}
#dot{{width:7px;height:7px;border-radius:50%;background:#5e6673;display:inline-block}}
#dot.on{{background:#0ecb81}} #dot.off{{background:#f6465d}}
select{{background:#161a1e;color:#c9d1d9;border:1px solid #2b3139;border-radius:3px;font:10px ui-monospace,monospace;padding:1px 2px}}
#msg{{color:#848e9c;padding:4px}}
#c{{width:100%;height:{max(120, height_px - 26)}px}}
</style></head><body>
<div id='bar'><span id='dot' title='live feed'></span><b>{html.escape(sym)}</b>
<select id='tf' aria-label='timeframe'>{opts}</select>
<span id='px'>-</span><span id='chg'></span><span id='ts' style='color:#5e6673'></span></div>
<div id='c'></div><div id='msg'></div>
<script src='{LWC_URL}'></script>
<script>
const CFG = {json.dumps(cfg)};
const el = document.getElementById('c'), msg = document.getElementById('msg');
const dot = document.getElementById('dot'), pxEl = document.getElementById('px'), chgEl = document.getElementById('chg'), tsEl = document.getElementById('ts');
let chart = null, series = null, priceLine = null, ws = null, openPrice = null, lastBar = null, curBar = CFG.bar, reqId = 0;

function fmt(v) {{ const n = +v; if (!isFinite(n)) return '-'; const a = Math.abs(n);
  return n.toLocaleString('en-US', {{maximumFractionDigits: a >= 100 ? 2 : a >= 1 ? 4 : 8}}); }}
function setLive(on) {{ dot.className = on ? 'on' : 'off'; dot.title = on ? 'live' : 'offline'; }}
function paintPrice(p, ts) {{
  pxEl.textContent = fmt(p);
  if (openPrice) {{ const c = (p / openPrice - 1) * 100; chgEl.textContent = (c >= 0 ? '+' : '') + c.toFixed(2) + '%';
    chgEl.style.color = c >= 0 ? '#0ecb81' : '#f6465d'; }}
  if (ts) tsEl.textContent = new Date(ts).toISOString().replace('T', ' ').slice(0, 16) + ' UTC';
  if (priceLine) series.removePriceLine(priceLine);
  priceLine = series.createPriceLine({{price: p, color: '#f0b90b', lineWidth: 1, lineStyle: 2, axisLabelVisible: true, title: 'last'}});
}}
function ensureChart() {{
  if (chart) return;
  if (typeof LightweightCharts === 'undefined') {{ msg.textContent = 'chart library not loaded (offline?)'; return; }}
  chart = LightweightCharts.createChart(el, {{
    layout: {{background: {{color: '#0b0e11'}}, textColor: '#848e9c', fontSize: 10}},
    grid: {{vertLines: {{color: '#1b2026'}}, horzLines: {{color: '#1b2026'}}}},
    rightPriceScale: {{visible: true, borderColor: '#2b3139'}},
    timeScale: {{visible: true, timeVisible: true, secondsVisible: false, borderColor: '#2b3139'}},
    crosshair: {{mode: 1}}, handleScroll: true, handleScale: true,
  }});
  series = chart.addCandlestickSeries({{upColor: '#0ecb81', downColor: '#f6465d', borderVisible: false,
    wickUpColor: '#0ecb81', wickDownColor: '#f6465d'}});
  new ResizeObserver(() => chart.applyOptions({{width: el.clientWidth}})).observe(el);
}}
async function loadHistory(bar, id) {{
  const url = CFG.rest + '?instId=' + encodeURIComponent(CFG.sym) + '&bar=' + encodeURIComponent(bar) + '&limit=300';
  const r = await fetch(url); const j = await r.json();
  if (id !== reqId) return;   // a newer timeframe was picked meanwhile
  if (!j || j.code !== '0' || !Array.isArray(j.data)) throw new Error((j && j.msg) || 'no candles');
  const rows = j.data.slice().reverse().map(k => ({{time: Math.floor(+k[0] / 1000), open: +k[1], high: +k[2], low: +k[3], close: +k[4]}}));
  ensureChart();
  series.setData(rows);
  lastBar = rows[rows.length - 1];
  openPrice = rows[0] ? rows[0].open : null;
  chart.timeScale().fitContent();
  paintPrice(lastBar.close, lastBar.time * 1000);
  msg.textContent = '';
}}
function openWS(bar, id) {{
  if (ws) {{ try {{ ws.close(); }} catch (e) {{}} ws = null; }}
  let sock;
  try {{ sock = new WebSocket(CFG.ws); }} catch (e) {{ setLive(false); return; }}
  ws = sock;
  sock.onopen = () => {{ setLive(true);
    sock.send(JSON.stringify({{op: 'subscribe', args: [{{channel: 'candle' + bar, instId: CFG.sym}}, {{channel: 'tickers', instId: CFG.sym}}]}})); }};
  sock.onclose = () => setLive(false);
  sock.onerror = () => setLive(false);
  sock.onmessage = ev => {{
    if (id !== reqId) return;
    let m; try {{ m = JSON.parse(ev.data); }} catch (e) {{ return; }}
    if (!m.data || !m.arg) return;
    if (m.arg.channel === 'tickers') {{ const t = m.data[0]; if (t) paintPrice(+t.last, +t.ts); return; }}
    if (m.arg.channel === 'candle' + bar && series) {{
      const k = m.data[0]; const b = {{time: Math.floor(+k[0] / 1000), open: +k[1], high: +k[2], low: +k[3], close: +k[4]}};
      series.update(b); lastBar = b; paintPrice(b.close, b.time * 1000);
    }}
  }};
}}
async function start(tf) {{
  const id = ++reqId; const bar = CFG.tfs.find(x => x[0] === tf)[1];
  curBar = bar; msg.textContent = 'loading ' + tf + '...';
  if (ws) {{ try {{ ws.close(); }} catch (e) {{}} ws = null; }}
  try {{ await loadHistory(bar, id); if (id === reqId) openWS(bar, id); }}
  catch (e) {{ msg.textContent = 'history not available: ' + e.message; setLive(false); }}
}}
document.getElementById('tf').addEventListener('change', e => start(e.target.value));
start(CFG.tf);
</script></body></html>"""
