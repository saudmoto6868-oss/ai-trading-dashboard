"""TIA's isolated interactive workspace shell.

Uses the existing browser-side chart/widget engine with a TIA-only storage namespace.
Original Workspace layouts, drawings and preferences remain untouched.
"""
from __future__ import annotations
import streamlit.components.v1 as components
from modules.workspace import build_workspace_html

_OPT_CACHE: dict = {}   # (time, payload, errors): the Deribit snapshot is reused for 3 minutes, so a re-render never waits on the network again (failures are cached too)


def render_tia_workspace(height: int = 980, universe: str = "Crypto", symbols: list[str] | None = None):
    symbols = list(dict.fromkeys(symbols or ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT"]))
    asset_class = universe
    doc = build_workspace_html(symbols=symbols, news=[], lang="en", asset_cls=asset_class,
                               ui_theme="gold", ui_mat="steel")

    # Snapshot public options context server-side (cached 3 min); the iframe receives only the derived, non-sensitive payload.
    import json
    import time as _time
    _hit = _OPT_CACHE.get("v")
    if _hit and _time.time() - _hit[0] < 180:
        options_payload, options_errors = _hit[1], _hit[2]
    else:
        options_payload = {}
        options_errors = {}
        try:
            from modules import options_desk as _od
            from datetime import datetime, timezone
            for _ccy in ("BTC", "ETH"):
                try:
                    _rows = _od.fetch(_ccy, ttl=120, timeout=8)
                    _summary = _od.summarize(_rows)
                    _expiries = []
                    for _e in _summary.get("expiries", [])[:8]:
                        _levels = _od.strikes(_rows, _e["exp"], _summary.get("spot") or 0, span=0.15)
                        _expiries.append({**_e, "exp": _e["exp"].isoformat(), "levels": _levels[:80]})
                    _dvol = _od.dvol(_ccy, days=365, ttl=1800, timeout=8)
                    _rank = _od.iv_rank([x[1] for x in _dvol])
                    options_payload[_ccy] = {"summary": _summary, "expiries": _expiries, "dvol": _rank,
                                             "asof": datetime.now(timezone.utc).isoformat(), "source": "Deribit public API"}
                except Exception as _e:
                    options_errors[_ccy] = str(_e)[:180]
        except Exception as _e:
            options_errors["provider"] = str(_e)[:180]
        _OPT_CACHE["v"] = (_time.time(), options_payload, options_errors)
    doc = doc.replace("</head>", "<script>const TIA_OPTIONS = " + json.dumps(options_payload, default=str, separators=(",", ":")) + "; const TIA_OPTIONS_ERRORS = " + json.dumps(options_errors) + ";</script></head>", 1)
    tia_new_panels = r'''
Panel.prototype.build_tiaheat = function(){
  const wrap=el("div");wrap.style.cssText="padding:8px;overflow:auto;height:100%";
  const note=el("div","m","24h change heatmap · provider-reported ticker snapshots");note.style.cssText="font-size:11px;margin-bottom:8px";
  const grid=el("div");grid.style.cssText="display:grid;grid-template-columns:repeat(auto-fit,minmax(112px,1fr));gap:6px";wrap.append(note,grid);this.body.append(wrap);
  const draw=data=>{grid.replaceChildren();(SYMS||[]).slice(0,40).forEach(sym=>{const q=data&&data[sym],pct=q&&q.open>0?(q.last/q.open-1)*100:null;
    const tile=el("div");const mag=pct==null?0:Math.min(1,Math.abs(pct)/5);const bg=pct==null?"rgba(130,130,130,.10)":pct>=0?"rgba(49,196,141,"+(.10+.30*mag)+")":"rgba(230,106,103,"+(.10+.30*mag)+")";
    tile.style.cssText="padding:9px 7px;border:1px solid var(--line);border-radius:4px;background:"+bg+";min-height:58px";
    const name=el("div",null,sym);name.style.cssText="font-size:11px;color:var(--mut);overflow-wrap:anywhere";
    const val=el("div",null,pct==null?(q?"—":"NO DATA"):(pct>0?"+":"")+pct.toFixed(2)+"%");val.style.cssText="font:700 17px ui-monospace,Menlo,monospace;margin-top:5px";
    const state=el("div","m",q?(q.stale?"STALE":"LIVE"):"NO FEED");state.style.fontSize="9px";tile.append(name,val,state);grid.append(tile);
  });};
  const off=Hub.sub("tickers","TIA_HEAT",draw);this.unsubs.push(off);
};
Panel.prototype.build_tiaoptions = function(){
  const wrap=el("div");wrap.style.cssText="padding:9px;overflow:auto;height:100%;font-size:12px";
  const bar=el("div","tb");const cur=el("select");["BTC","ETH"].forEach(x=>cur.append(Object.assign(el("option"),{value:x,textContent:x})));bar.append(cur);
  const exp=el("select");bar.append(exp);const content=el("div");wrap.append(bar,content);this.body.append(wrap);
  const fmt=v=>v==null||!Number.isFinite(Number(v))?"—":Number(v).toLocaleString(undefined,{maximumFractionDigits:2});
  const render=()=>{const d=TIA_OPTIONS[cur.value];content.replaceChildren();exp.replaceChildren();
    if(!d){const msg=el("div","m","Options snapshot unavailable: "+(TIA_OPTIONS_ERRORS[cur.value]||"no provider data"));content.append(msg);return;}
    d.expiries.forEach((x,i)=>exp.append(Object.assign(el("option"),{value:String(i),textContent:x.exp+" · "+x.days+"d"})));
    const metrics=el("div");metrics.style.cssText="display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));gap:6px;margin:9px 0";
    const cards=[["UNDERLYING PROXY",d.summary.spot],["TOTAL OI",d.summary.totals.oi],["PUT/CALL OI",d.summary.totals.pc_oi],["DVOL IV RANK",d.dvol&&d.dvol.rank!=null?d.dvol.rank+"%":null]];
    cards.forEach(([k,v])=>{const c=el("div");c.style.cssText="padding:8px;border:1px solid var(--line)";const a=el("div","m",k);a.style.fontSize="9px";const b=el("div",null,fmt(v));b.style.cssText="font:700 15px ui-monospace,Menlo,monospace;margin-top:5px";c.append(a,b);metrics.append(c);});content.append(metrics);
    const detail=el("div","m","Deribit public option book · snapshot "+d.asof+" · underlying is the nearest-expiry forward proxy, not a spot quote.");detail.style.cssText="font-size:10px;margin:5px 0 10px";content.append(detail);
    const draw=()=>{const x=d.expiries[Number(exp.value)||0];if(!x)return;const stats=el("div");stats.style.cssText="display:flex;flex-wrap:wrap;gap:12px;margin:8px 0";
      [["PCR VOL",x.pc_vol],["ATM IV",x.iv],["10% SKEW",x.skew10],["MAX PAIN",x.max_pain]].forEach(([k,v])=>{const z=el("span",null,k+": "+fmt(v));stats.append(z);});content.append(stats);
      const cv=el("canvas");cv.width=640;cv.height=220;cv.style.cssText="width:100%;height:220px;background:var(--panel0);border:1px solid var(--line)";content.append(cv);
      const ctx=cv.getContext("2d"),ls=x.levels||[],mx=Math.max(1,...ls.flatMap(a=>[a[1],a[2]]));ctx.font="10px ui-monospace";ctx.fillStyle="#d6ad62";ctx.fillText("CALL OI",12,14);ctx.fillStyle="#78a9d1";ctx.fillText("PUT OI",90,14);
      const w=(cv.width-36)/Math.max(1,ls.length);ls.forEach((a,i)=>{const xx=18+i*w,bh=(a[1]/mx)*160,ph=(a[2]/mx)*160;ctx.fillStyle="#d6ad62";ctx.fillRect(xx,190-bh,Math.max(1,w*.42),bh);ctx.fillStyle="#78a9d1";ctx.fillRect(xx+w*.46,190-ph,Math.max(1,w*.42),ph);});
      const foot=el("div","m","Open interest is not directional positioning; it does not reveal opening/closing flow or dealer inventory. Max pain is descriptive, not a forecast.");foot.style.cssText="font-size:10px;margin-top:7px";content.append(foot);
    };draw();};
  cur.onchange=render;exp.onchange=()=>{const old=content.querySelector("canvas");if(old){const idx=Number(exp.value)||0;const x=TIA_OPTIONS[cur.value].expiries[idx];const ctx=old.getContext("2d");ctx.clearRect(0,0,old.width,old.height);const ls=x.levels||[],mx=Math.max(1,...ls.flatMap(a=>[a[1],a[2]])),w=(old.width-36)/Math.max(1,ls.length);ctx.font="10px ui-monospace";ctx.fillStyle="#d6ad62";ctx.fillText("CALL OI",12,14);ctx.fillStyle="#78a9d1";ctx.fillText("PUT OI",90,14);ls.forEach((a,i)=>{const xx=18+i*w;ctx.fillStyle="#d6ad62";ctx.fillRect(xx,190-a[1]/mx*160,Math.max(1,w*.42),a[1]/mx*160);ctx.fillStyle="#78a9d1";ctx.fillRect(xx+w*.46,190-a[2]/mx*160,Math.max(1,w*.42),a[2]/mx*160);});const stats=content.querySelector("div[style*='display: flex']");if(stats){stats.replaceChildren();[["PCR VOL",x.pc_vol],["ATM IV",x.iv],["10% SKEW",x.skew10],["MAX PAIN",x.max_pain]].forEach(([k,v])=>stats.append(el("span",null,k+": "+fmt(v))));}}};
  render();
};
'''

    # Add TIA-native panels to the existing draggable/resizable panel system.
    tia_panels = r'''
Panel.prototype.build_tiapulse = function(){
  const box = el("div"); box.style.cssText = "padding:8px;overflow:auto;height:100%;";
  const note = el("div","m", "Live ticker snapshot · provider coverage only"); note.style.cssText += "margin-bottom:8px;font-size:11px";
  const table = el("table"); table.style.cssText = "width:100%;border-collapse:collapse;font:12px ui-monospace,Menlo,monospace";
  const head = el("tr"); ["SYMBOL","LAST","24H %","FEED"].forEach(x=>{const th=el("th",null,x);th.style.cssText="text-align:right;padding:6px;border-bottom:1px solid var(--line)";head.append(th);}); table.append(head);
  const rows = new Map();
  const fmt = v => Number.isFinite(v) ? v.toLocaleString(undefined,{maximumFractionDigits:6}) : "—";
  const render = data => {
    const symbols = (SYMS||[]).slice(0,40);
    symbols.forEach(sym=>{
      const q=data && data[sym]; let tr=rows.get(sym);
      if(!tr){ tr=el("tr"); rows.set(sym,tr); for(let i=0;i<4;i++){const td=el("td");td.style.cssText="padding:7px 5px;text-align:right;border-bottom:1px solid var(--line);white-space:nowrap";tr.append(td);} table.append(tr); }
      const pct=q && q.open>0 ? (q.last/q.open-1)*100 : null;
      tr.children[0].textContent=sym; tr.children[1].textContent=q?fmt(q.last):"—";
      tr.children[2].textContent=pct==null?"—":(pct>0?"+":"")+pct.toFixed(2)+"%";
      tr.children[2].style.color=pct==null?"var(--mut)":pct>=0?"var(--grn)":"var(--red)";
      tr.children[3].textContent=!q?"NO DATA":q.stale?"STALE":"LIVE";
      tr.children[3].style.color=!q||q.stale?"var(--mut)":"var(--grn)";
    });
  };
  box.append(note,table); this.body.append(box);
  const off=Hub.sub("tickers","TIA_PULSE",render); this.unsubs.push(off);
};
Panel.prototype.build_tiasources = function(){
  const box=el("div"); box.style.cssText="padding:10px;overflow:auto;height:100%;font-size:12px";
  const intro=el("div","m","Connection health from this browser session; not a broker-account status."); intro.style.marginBottom="10px";
  const body=el("div"); box.append(intro,body); this.body.append(box);
  const draw=()=>{
    body.replaceChildren();
    const keys=Object.keys(Hub.subs||{}).filter(k=>Hub.subs[k]&&Hub.subs[k].size);
    if(!keys.length){body.textContent="No active feed subscriptions yet.";return;}
    keys.forEach(k=>{const line=el("div");line.style.cssText="display:flex;justify-content:space-between;gap:8px;padding:7px 2px;border-bottom:1px solid var(--line)";
      const left=el("span",null,k.replace("|"," · ")); const last=Hub.last[k];
      const right=el("span",null,last&& !last.error ? "ACTIVE" : "WAITING / ERROR"); right.style.color=last&&!last.error?"var(--grn)":"var(--mut)";
      line.append(left,right);body.append(line);
    });
  };
  draw(); this._tiaSourceTimer=setInterval(draw,2000); this.unsubs.push(()=>clearInterval(this._tiaSourceTimer));
};
''';
    doc = doc.replace("const WGROUPS = () => [", tia_panels + tia_new_panels + "\nconst WGROUPS = () => [");
    doc = doc.replace('[Lg("Settings","الإعدادات"), "#9aa3ad", ["settings"]]', '[Lg("TIA Intelligence","استخبارات TIA"), "#d6ad62", ["tiapulse","tiasources","tiaheat","tiaoptions"]], [Lg("Settings","الإعدادات"), "#9aa3ad", ["settings"]]');
    doc = doc.replace('settings:"SET", "@std"', 'settings:"SET", tiapulse:"PULSE", tiasources:"SRC", tiaheat:"HEAT", tiaoptions:"OPT", "@std"');
    # Isolate all localStorage/sessionStorage keys from the original Workspace.
    # tia_ws_v2: a fresh key, so browsers that already saved the old Workspace-copy layout (v1) start from the TIA layout below.
    doc = doc.replace("ai_ws_v5", "tia_ws_v2")
    # TIA's own start layout (owner 2026-11-10: use the Workspace widget engine, but show TIA's data, not a Workspace copy):
    # heatmap + pulse on top, ONE chart with the order-flow column + the Order Flow Desk in the middle, options + feed health at the bottom.
    # Every other widget stays one click away in + Widget. The Workspace standard stays untouched (renamed, never deleted).
    tia_layout = r'''
Ws.builtinStandard = () => {
  const W = Math.max(600, Ws.el.clientWidth || 1200), H = Math.max(500, Math.min((Ws.el.clientHeight || 760) - 8, 960)), r = v => Math.round(v), g = 6, S0 = SYMS[0];
  const h1 = r(H*0.28), h2 = r(H*0.44), y2 = h1 + g, y3 = y2 + h2 + g, h3 = H - y3, w1 = r((W - g)*0.6), w2 = W - w1 - g, w3 = r((W - g)*0.56), w4 = W - w3 - g;
  const OF = {dcol:true, dom:true, bub:true}, E = {9:true, 21:true, 50:false};
  return [
    ["tiaheat", {x:0, y:0, w:w1, h:h1}, {group:1}],
    ["tiapulse", {x:w1 + g, y:0, w:w2, h:h1}, {group:1}],
    ["chart", {x:0, y:y2, w:w3, h:h2}, Object.assign({sym:S0, group:1, tf:"15m", ema:E}, OF)],
    ["ofdesk", {x:w3 + g, y:y2, w:w4, h:h2}, {group:1}],
    ["tiaoptions", {x:0, y:y3, w:w1, h:h3}, {group:1}],
    ["tiasources", {x:w1 + g, y:y3, w:w2, h:h3}, {group:1}],
  ]; };
'''
    _marker = "/* the older layout (signals strip, 15 s + 5 m charts, scanner ...): phones, first visit only */"
    if _marker in doc:
        doc = doc.replace("Ws.builtinStandard = () => {", "Ws.builtinStandardWorkspace = () => {", 1)
        doc = doc.replace(_marker, tia_layout + _marker, 1)
    doc = doc.replace("<title>6868 X</title>", "<title>TIA Command Workspace</title>")
    doc = doc.replace(
        ":root{--panel0:#0e1114;--dot:#1b2027;--bg:#0b0e11;--panel:#161a1e;--panel2:#1e2329;--line:#2b3139;--txt:#eaecef;--mut:#848e9c;--grn:#0ecb81;--red:#f6465d;--gold:#f0b90b;--blue:#4aa3ff;--vio:#b57cff}",
        ":root{--panel0:#0d0c0a;--dot:#282117;--bg:#090a0c;--panel:#141311;--panel2:#201d18;--line:#51432c;--txt:#eee6d7;--mut:#a99d89;--grn:#31c48d;--red:#e66a67;--gold:#d6ad62;--blue:#78a9d1;--vio:#b59acb}"
    )
    components.html(doc, height=height, scrolling=False)
