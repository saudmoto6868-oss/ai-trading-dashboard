"""TIA's isolated interactive workspace shell.

Uses the existing browser-side chart/widget engine with a TIA-only storage namespace.
Original Workspace layouts, drawings and preferences remain untouched.
"""
from __future__ import annotations
import streamlit.components.v1 as components
from modules.workspace import build_workspace_html

_OPT_CACHE: dict = {}   # (time, payload, errors): the Deribit snapshot is reused for 3 minutes, so a re-render never waits on the network again (failures are cached too)


def render_tia_workspace(height: int = 980, universe: str = "Crypto", symbols: list[str] | None = None, ctrl: dict | None = None):
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
    # Funded accounts: rule limits from the Prop Firms page (server session data) are handed to the iframe; the live balance is NOT read.
    funded = {"accounts": [], "error": ""}
    try:
        from modules import prop_firms as _pf
        _keys = ("id", "name", "firm", "status", "size", "max_loss_pct", "daily_loss_pct", "profit_target_pct", "inactivity_limit", "consistency_rule", "color")
        for _a in _pf._load_accounts():
            _row = {k: _a.get(k) for k in _keys}
            _row["days_left"] = _pf._days_left(_a)
            funded["accounts"].append(_row)
    except Exception as _e:
        funded["error"] = str(_e)[:120]
    doc = doc.replace("</head>", "<script>const TIA_FUNDED = " + json.dumps(funded, default=str, separators=(",", ":")).replace("</", "<\\/") + ";</script></head>", 1)
    # Toolbar controls (market | symbol | Run TIA Director) built INTO the workspace's own #bar, so they look and size like the other toolbar options.
    # They talk to the Streamlit page through URL parameters of the parent window (tia_mkt / tia_sym / tia_run), the same way the Guide changes pages.
    if ctrl:
        tia_bar_js = r'''
(function(){
  const C = window.TIA_CTRL; if (!C) return;
  const go = (k, v, drop) => { try { const P = window.parent, u = new URL(P.location.href); (drop || []).forEach(x => u.searchParams.delete(x)); u.searchParams.set(k, v); P.location.href = u.href; } catch(e){ console.warn('tia ctl', e); } };
  const sel = (opts, cur, fn, w) => { const s = document.createElement('select'); s.style.maxWidth = w + 'px'; opts.forEach(o => { const e = document.createElement('option'); e.value = o; e.textContent = o; if (o === cur) e.selected = true; s.append(e); }); s.onchange = () => fn(s.value); return s; };
  const mk = () => { const bar = document.getElementById('bar'); if (!bar) return false; if (bar.querySelector('.tiactl')) return true;
    const g = document.createElement('span'); g.className = 'tiactl'; g.style.cssText = 'display:inline-flex;gap:4px;align-items:center;margin-left:8px';
    g.append(sel(C.markets, C.market, v => go('tia_mkt', v, ['tia_sym', 'tia_run']), 110), sel(C.symbols, C.selected, v => go('tia_sym', v, ['tia_run']), 150));
    const b = document.createElement('button'); b.textContent = 'Run TIA Director'; b.onclick = () => go('tia_run', String(Date.now())); g.append(b); bar.append(g); return true; };
  setInterval(mk, 800);   // buildBar() empties #bar at start-up and on every language / layout rebuild: the controls are put back whenever they are missing
})();
'''
        doc = doc.replace("</head>", "<script>window.TIA_CTRL = " + json.dumps(ctrl, default=str, separators=(",", ":")).replace("</", "<\\/") + ";</script><script>" + tia_bar_js + "</script></head>", 1)
    # Trade Plan card (owner 2026-11-10, docs/TIA_VISUAL_BRIEF_2026-11-10.md P1-1). It invents nothing: it shows the best live setup that the Workspace
    # scanner / Trade-class engine already produced for the selected symbol (Alerts.list), the price ladder, R:R, and the unified risk policy.
    tia_plan_panel = r'''
Panel.prototype.build_tiaplan = function(){
  const wrap=el('div');wrap.style.cssText='padding:8px;overflow:auto;height:100%;font-size:11px';
  const out=el('div');wrap.append(out);this.body.append(wrap);
  let last=null,dead=false;this.unsubs.push(()=>{dead=true;});
  const sym0=()=>(SYMS&&SYMS[0])||'';
  const fp=v=>!Number.isFinite(+v)?'-':(+v>=1000?(+v).toFixed(1):+v>=1?(+v).toFixed(3):(+v).toPrecision(4));
  const sv=(tag,at,txt)=>{const e=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const k in at)e.setAttribute(k,at[k]);if(txt!=null)e.textContent=txt;return e;};
  const okPlan=c=>{const p=c&&c.plan;if(!p||!Array.isArray(p.tps)||!p.tps.length)return false;const e=+p.entry,s=+p.stop,t=+p.tps[0];if(!(e>0&&s>0&&t>0))return false;return c.direction==='bullish'?(s<e&&e<t):(s>e&&e>t);};
  const pick=()=>{let L=[];try{L=(Alerts.list||[]).filter(a=>a&&a.card&&a.card.symbol===sym0()&&okPlan(a.card));}catch(e){}
    if(!L.length)return null;const sc=a=>{try{return wScore(a.card);}catch(e){return a.card.score/Math.max(1,a.card.max||1);}};L.sort((a,b)=>sc(b)-sc(a));return L[0].card;};
  const row=(box,k,v,col)=>{const r=el('div');r.style.cssText='display:flex;justify-content:space-between;gap:8px;padding:1px 0';const a=el('span','m',k),b=el('span',null,v);b.style.cssText='font-family:ui-monospace,Menlo,monospace'+(col?';color:'+col:'');r.append(a,b);box.append(r);};
  const draw=()=>{if(dead)return;out.replaceChildren();const S=sym0(),c=pick();
    const head=el('div',null,S||'-');head.style.cssText='font-weight:700;font-size:13px;margin-bottom:4px';out.append(head);
    if(!c){const m=el('div','m','NO PLAN for this symbol right now (scanner + trade-class engines produced no valid entry / stop / target). Nothing is invented.');m.style.cssText='font-size:11px;margin-bottom:6px';out.append(m);
      let O=[];try{O=(Alerts.list||[]).filter(a=>a&&a.card&&okPlan(a.card)&&a.card.symbol!==S);}catch(ex){}
      const sc=a=>{try{return wScore(a.card);}catch(ex){return a.card.score/Math.max(1,a.card.max||1);}};O.sort((a,b)=>sc(b)-sc(a));
      const h2=el('div','m','Live setups on other symbols ('+O.length+')');h2.style.cssText='font-size:10px;margin-bottom:3px';out.append(h2);
      O.slice(0,5).forEach(a=>{const k=a.card,p=k.plan,e0=+p.entry,s0=+p.stop,t0=+p.tps[0],rr0=Math.abs(t0-e0)/Math.abs(e0-s0),lg=k.direction==='bullish';
        const r=el('div');r.style.cssText='display:flex;justify-content:space-between;gap:6px;padding:3px 0;border-bottom:1px solid var(--line);cursor:pointer';
        const l=el('span',null,k.symbol+' '+(lg?'LONG':'SHORT')),x=el('span','m',String(k.ttype||'')+' · R:R 1:'+rr0.toFixed(1)+' · '+String(k.verdict||''));l.style.color=lg?'var(--grn)':'var(--red)';
        r.title='Open '+k.symbol+' in TIA';r.onclick=()=>{try{const C=window.TIA_CTRL;if(!C||(C.symbols||[]).indexOf(k.symbol)<0)return;const P=window.parent,u=new URL(P.location.href);u.searchParams.delete('tia_run');u.searchParams.set('tia_sym',k.symbol);P.location.href=u.href;}catch(e2){}};
        r.append(l,x);out.append(r);});
      return;}
    const pl=c.plan,long_=c.direction==='bullish',e=+pl.entry,s=+pl.stop,tps=pl.tps.map(Number).filter(v=>v>0),risk=Math.abs(e-s),rr=risk>0?Math.abs(tps[0]-e)/risk:0;
    let minRR=2;try{if(DESK&&DESK.RULES&&+DESK.RULES.minRR>0)minRR=+DESK.RULES.minRR;}catch(x){}
    let rp=0.25;try{rp=DESK.riskFor(null,0,false);}catch(x){}
    const vd=String(c.verdict||'').toUpperCase(),blocked=rr<minRR,state=blocked?'BLOCKED: R:R below 1:'+minRR:vd==='TAKE'?'TAKE':vd==='WAIT'?'WAIT':vd==='SKIP'?'SKIP':'REVIEW';
    const scol=blocked||vd==='SKIP'?'var(--red)':vd==='TAKE'?'var(--grn)':'var(--gold)';
    const top=el('div');top.style.cssText='display:flex;align-items:center;gap:8px;margin-bottom:6px;flex-wrap:wrap';
    const side=el('span',null,long_?'LONG':'SHORT');side.style.cssText='font-weight:700;padding:1px 6px;border:1px solid '+(long_?'var(--grn)':'var(--red)')+';color:'+(long_?'var(--grn)':'var(--red)');
    const st=el('span',null,state);st.style.cssText='font-weight:700;color:'+scol;const tt=el('span','m',String(c.ttype||'')+' · score '+(c.score||0)+'/'+(c.max||10));top.append(side,st,tt);out.append(top);
    const px=[e,s].concat(tps);if(last!=null)px.push(last);const lo=Math.min(...px),hi=Math.max(...px),pad=(hi-lo)*0.08||1,A=lo-pad,B=hi+pad,H=120,W=250,Y=v=>H-6-(v-A)/(B-A)*(H-12);
    const svg=sv('svg',{viewBox:'0 0 '+W+' '+H,width:'100%',height:String(H)});svg.style.cssText='display:block;background:var(--panel0);border:1px solid var(--line);margin-bottom:6px';
    svg.append(sv('rect',{x:'0',y:String(Math.min(Y(e),Y(s))),width:'150',height:String(Math.abs(Y(e)-Y(s))),fill:'rgba(230,106,103,.14)'}));
    svg.append(sv('rect',{x:'0',y:String(Math.min(Y(e),Y(tps[tps.length-1]))),width:'150',height:String(Math.abs(Y(e)-Y(tps[tps.length-1]))),fill:'rgba(49,196,141,.12)'}));
    const ln=(v,col,lab,dash)=>{svg.append(sv('line',{x1:'0',x2:'150',y1:String(Y(v)),y2:String(Y(v)),stroke:col,'stroke-width':'1.5','stroke-dasharray':dash||''}));svg.append(sv('text',{x:'156',y:String(Y(v)+3),'font-size':'9',fill:col},lab+' '+fp(v)));};
    tps.slice(0,3).forEach((t,i)=>ln(t,'#31c48d','TP'+(i+1),i?'3 3':''));ln(e,'#78a9d1','ENTRY');ln(s,'#e66a67','STOP');if(last!=null)ln(last,'#d6ad62','NOW','2 2');
    out.append(svg);
    const tb=el('div');row(tb,'Entry',fp(e));row(tb,'Stop',fp(s)+' ('+(risk/e*100).toFixed(2)+'%)','var(--red)');
    tps.slice(0,3).forEach((t,i)=>row(tb,'TP'+(i+1),fp(t)+' ('+(Math.abs(t-e)/risk).toFixed(2)+' R)','var(--grn)'));
    row(tb,'R:R (TP1)','1:'+rr.toFixed(2),blocked?'var(--red)':null);row(tb,'Risk policy',rp+'% of equity per trade (automatic, no manual selector)');
    if(last!=null)row(tb,'Price vs entry',((last-e)/e*100).toFixed(2)+'%');out.append(tb);
    const sg=(c.ana&&c.ana.sig)||[];if(sg.length){const ev=el('div');ev.style.cssText='margin-top:6px;border-top:1px solid var(--line);padding-top:4px';const h=el('div','m','Why / why not (from the engine)');h.style.fontSize='10px';ev.append(h);
      sg.slice(0,7).forEach(t=>{const d=el('div',null,String(t));d.style.cssText='font-size:10px;padding:1px 0';ev.append(d);});out.append(ev);}
    let ti='';try{ti=tfTxt(c);}catch(x){}if(ti){const d=el('div','m','Walk-forward history on this timeframe: '+ti);d.style.cssText='font-size:10px;margin-top:4px';out.append(d);}
    let nj=0;try{nj=((Journal&&Journal.list)||[]).filter(t=>t.status==='tp'||t.status==='sl').length;}catch(x){}
    const f=el('div','m','Information, not an order and not a proven edge. Position size = risk % of equity divided by the stop distance (set equity in the Order Flow Desk). Closed journal trades: '+nj+(nj<30?' (under 30: not evidence)':'')+'. Source: live scanner / trade-class engine in this browser session.');f.style.cssText='font-size:10px;margin-top:6px';out.append(f);};
  let off=null;try{off=Hub.sub('tickers','TIA_PLAN',data=>{const q=data&&data[sym0()];last=q&&Number.isFinite(+q.last)?+q.last:null;draw();});}catch(x){}
  if(off)this.unsubs.push(off);
  draw();const iv=setInterval(()=>{if(!document.hidden)draw();},4000);this.unsubs.push(()=>clearInterval(iv));
};
'''
    # Multi-timeframe confidence (docs/TIA_VISUAL_BRIEF_2026-11-10.md P1-2): real OKX candles, closed bars only, descriptive.
    tia_conf_panel = r'''
Panel.prototype.build_tiaconf = function(){
  const wrap=el('div');wrap.style.cssText='padding:6px;overflow:auto;height:100%;font-size:11px';
  const out=el('div');wrap.append(out);this.body.append(wrap);
  let dead=false;this.unsubs.push(()=>{dead=true;});
  const sym=()=>(SYMS&&SYMS[0])||'';
  const sv=(tag,at,txt)=>{const e=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const k in at)e.setAttribute(k,at[k]);if(txt!=null)e.textContent=txt;return e;};
  const TF=[['15m','15m'],['1H','1H'],['4H','4H'],['1D','1D']];
  const sma=(a,n)=>a.length<n?null:a.slice(-n).reduce((s,v)=>s+v,0)/n;
  const rsi=(c,n)=>{if(c.length<n+1)return null;let g=0,l=0;for(let i=c.length-n;i<c.length;i++){const d=c[i]-c[i-1];if(d>0)g+=d;else l-=d;}return g+l===0?50:100-100/(1+g/(l||1e-12));};
  const analyse=c=>{const p=c[c.length-1],m20=sma(c,20),m50=sma(c,50),r=rsi(c,14),ret=c.length>21?(p/c[c.length-21]-1)*100:null;
    if(m20==null||m50==null||r==null)return null;
    const tr=p>m20&&m20>m50?'UP':p<m20&&m20<m50?'DOWN':'RANGE';return {tr,rsi:r,ret};};
  const col=t=>t==='UP'?'#31c48d':t==='DOWN'?'#e66a67':'#d6ad62';
  const draw=(res,when)=>{out.replaceChildren();
    const ok=res.filter(x=>x.a),up=ok.filter(x=>x.a.tr==='UP').length,dn=ok.filter(x=>x.a.tr==='DOWN').length;
    const verdict=!ok.length?'NO DATA':up>=3&&dn===0?'ALIGNED UP':dn>=3&&up===0?'ALIGNED DOWN':(up>0&&dn>0)?'CONFLICT':'MIXED / RANGE';
    const vc=verdict==='ALIGNED UP'?'#31c48d':verdict==='ALIGNED DOWN'?'#e66a67':verdict==='CONFLICT'?'#e66a67':'#d6ad62';
    const S=120,C=S/2,R=44,svg=sv('svg',{viewBox:'0 0 '+S+' '+S,width:'100%',height:'110'});svg.style.cssText='display:block;margin:0 auto 4px;max-width:150px';
    res.forEach((x,i)=>{const a0=(-90+i*90+5)*Math.PI/180,a1=(-90+(i+1)*90-5)*Math.PI/180;
      svg.append(sv('path',{d:'M '+(C+R*Math.cos(a0))+' '+(C+R*Math.sin(a0))+' A '+R+' '+R+' 0 0 1 '+(C+R*Math.cos(a1))+' '+(C+R*Math.sin(a1)),fill:'none',stroke:x.a?col(x.a.tr):'#555','stroke-width':'9','stroke-linecap':'round'}));
      const am=(-90+i*90+45)*Math.PI/180;svg.append(sv('text',{x:C+(R+0)*Math.cos(am),y:C+R*Math.sin(am)+3,'text-anchor':'middle','font-size':'7',fill:'#0d0c0a','font-weight':'700'},x.tf));});
    svg.append(sv('text',{x:C,y:C-2,'text-anchor':'middle','font-size':'9',fill:vc,'font-weight':'700'},verdict));
    svg.append(sv('text',{x:C,y:C+10,'text-anchor':'middle','font-size':'7',fill:'#a99d89'},up+' up / '+dn+' down of '+ok.length));
    const top=el('div');top.style.cssText='display:flex;gap:8px;align-items:center';const rowsBox=el('div');rowsBox.style.cssText='flex:1;min-width:0';
    svg.style.cssText='flex:0 0 108px;width:108px;height:108px;display:block';top.append(svg,rowsBox);out.append(top);
    res.forEach(x=>{const row=el('div');row.style.cssText='margin:3px 0';
      const h=el('div');h.style.cssText='display:flex;justify-content:space-between;font-size:10px';
      const l=el('span',null,x.tf+' '+(x.a?x.a.tr:'-')),r=el('span','m',x.a?('RSI '+x.a.rsi.toFixed(0)+(x.a.ret!=null?' · '+(x.a.ret>0?'+':'')+x.a.ret.toFixed(1)+'%':'')):'no data');l.style.color=x.a?col(x.a.tr):'var(--mut)';h.append(l,r);
      const bar=el('div');bar.style.cssText='position:relative;height:6px;background:var(--panel2);border:1px solid var(--line)';
      if(x.a){const z=(a,b,c2)=>{const d=el('div');d.style.cssText='position:absolute;top:0;bottom:0;left:'+a+'%;width:'+(b-a)+'%;background:'+c2;bar.append(d);};z(0,30,'rgba(49,196,141,.18)');z(70,100,'rgba(230,106,103,.18)');
        const dot=el('div');dot.style.cssText='position:absolute;top:-2px;width:8px;height:8px;border-radius:50%;background:'+col(x.a.tr)+';left:calc('+Math.max(0,Math.min(100,x.a.rsi))+'% - 4px)';bar.append(dot);}
      row.append(h,bar);rowsBox.append(row);});
    const f=el('div','m','Trend = close vs SMA20 / SMA50. RSI(14) = simple average of the last 14 changes (not Wilder smoothing). Closed candles only. OKX public API · '+when+' UTC. Descriptive; not a signal or an order.');f.style.cssText='font-size:9px;margin-top:5px';out.append(f);};
  const load=async()=>{const s=sym();
    if(!/^[A-Z0-9]+-USDT$/.test(s)){out.textContent='Needs a crypto USDT pair as the selected symbol (OKX candles).';return;}
    out.textContent='Loading candles...';
    const res=await Promise.all(TF.map(async([tf,bar])=>{try{const r=await fetch('https://www.okx.com/api/v5/market/candles?instId='+s+'&bar='+bar+'&limit=120');const j=await r.json();
      if(!(j&&j.code==='0'&&Array.isArray(j.data)))return {tf,a:null};const c=j.data.filter(k=>k[8]==='1').reverse().map(k=>+k[4]).filter(v=>v>0);return {tf,a:analyse(c)};}catch(e){return {tf,a:null};}}));
    if(dead)return;draw(res,new Date().toISOString().slice(0,16));};
  load();const iv=setInterval(()=>{if(!document.hidden)load();},300000);this.unsubs.push(()=>clearInterval(iv));
};
'''
    # Source health (docs/TIA_VISUAL_BRIEF_2026-11-10.md P1-4): real probes from the browser, one small request per source per 60 s.
    tia_health_panel = r'''
Panel.prototype.build_tiahealth = function(){
  const wrap=el('div');wrap.style.cssText='padding:6px;overflow:auto;height:100%;font-size:11px';
  const out=el('div');wrap.append(out);this.body.append(wrap);
  let dead=false;this.unsubs.push(()=>{dead=true;});
  const H={};
  const J=(u,o)=>fetch(u,o).then(r=>r.json());
  const P=[
    ['OKX REST',()=>J('https://www.okx.com/api/v5/public/time').then(j=>j&&j.code==='0'?'ok':'bad reply')],
    ['Hyperliquid',()=>J('https://api.hyperliquid.xyz/info',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({type:'allMids'})}).then(j=>j&&typeof j==='object'&&Object.keys(j).length>5?'ok':'bad reply')],
    ['Deribit',()=>J('https://www.deribit.com/api/v2/public/get_time').then(j=>j&&j.result>0?'ok':'bad reply')],
    ['Binance klines',()=>J('https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1w&limit=2').then(j=>Array.isArray(j)&&j.length&&j[0].length>=10&&isFinite(+j[0][9])?'taker-buy volume field present':'reachable, but no taker field / bad reply')]
  ];
  const probe=async([name,fn])=>{const t0=performance.now(),rec=H[name]||(H[name]={hist:[]});
    try{const note=await Promise.race([fn(),new Promise((_,rej)=>setTimeout(()=>rej(new Error('timeout 8 s')),8000))]);
      rec.ok=!/bad reply|no taker/.test(note);rec.note=note;rec.ms=performance.now()-t0;rec.t=Date.now();rec.hist.push(rec.ms);}
    catch(e){rec.ok=false;rec.note=/Failed to fetch|NetworkError/i.test(String(e&&e.message))?'blocked or offline (CORS / region / network)':String((e&&e.message)||e).slice(0,50);rec.ms=null;rec.hist.push(null);}
    if(rec.hist.length>14)rec.hist.shift();};
  const draw=()=>{if(dead)return;out.replaceChildren();
    P.forEach(([name])=>{const r=H[name];const row=el('div');row.style.cssText='padding:4px 0;border-bottom:1px solid var(--line)';
      const h=el('div');h.style.cssText='display:flex;justify-content:space-between;gap:6px;align-items:center';
      const dot=el('span',null,'● ');dot.style.color=!r?'var(--mut)':r.ok?'var(--grn)':'var(--red)';
      const l=el('span',null,name);l.style.cssText='flex:1;font-weight:700';l.prepend(dot);
      const ms=el('span','m',!r?'...':r.ms==null?'FAIL':Math.round(r.ms)+' ms');ms.style.cssText='font-family:ui-monospace,Menlo,monospace';h.append(l,ms);
      const bars=el('div');bars.style.cssText='display:flex;gap:1px;align-items:flex-end;height:12px;margin:2px 0';
      ((r&&r.hist)||[]).forEach(v=>{const b=el('span');b.style.cssText='width:5px;display:inline-block;background:'+(v==null?'var(--red)':'var(--gold)')+';height:'+(v==null?12:Math.max(2,Math.min(12,v/60)))+'px';bars.append(b);});
      const n=el('div','m',r?(r.note+(r.t?' · '+Math.round((Date.now()-r.t)/1000)+' s ago':'')):'probing...');n.style.fontSize='9px';
      row.append(h,bars,n);out.append(row);});
    const f=el('div','m','Measured from THIS browser (CORS, region and network included): one small request per source every 60 s. Latency of a probe, not a feed guarantee. Binance row = feasibility check for real taker-volume delta on big timeframes.');f.style.cssText='font-size:9px;margin-top:5px';out.append(f);};
  const run=async()=>{await Promise.all(P.map(probe));draw();};
  draw();run();const iv=setInterval(()=>{if(!document.hidden)run();},60000);this.unsubs.push(()=>clearInterval(iv));
};
'''
    tia_agents_panel = r'''
Panel.prototype.build_tiaagents = function(){
  const wrap=el('div');wrap.style.cssText='padding:6px;overflow:auto;height:100%;font-size:11px';
  const C=(typeof TIA_CTRL!=='undefined'&&TIA_CTRL)||{},A=C.agents||{};
  const note=el('div','m','Seven specialist responsibilities, not seven separate AI instances. Each card says where its evidence appears in this workspace; nothing here is an order or a signal.');note.style.cssText='font-size:10px;margin-bottom:6px';
  const grid=el('div');grid.style.cssText='display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:5px';
  const D=[['1 · Intelligence Director','Synthesises the evidence and states what conflicts.',A.ran?('Last report: '+(A.stance||'UNAVAILABLE')):'Not run yet: press Run TIA Director'],
    ['2 · Market Intelligence','Macro, news, catalysts, sessions.','Evidence: news ticker, Options, Session Ring, Pulse'],
    ['3 · Technical Intelligence','Price action, structure, multi-timeframe.','Evidence: Chart, Level scanner (Order Flow Desk)'],
    ['4 · Order Flow & Liquidity','Footprint, delta, DOM, tape, resting liquidity.','Evidence: chart order-flow map, Order Flow Desk; + Widget: DOM, Tape'],
    ['5 · Strategy & Innovation Lab','Research and strategy discovery.','Evidence: Lab and Research Hub pages (not shown here)'],
    ['6 · Quant Validation & Risk','Out-of-sample validation, costs, portfolio risk.','Evidence: Portfolio, Funded, Correlation, Radial'],
    ['7 · Trade Review & Decision','Challenges the plan and ranks it.','Evidence: Order Flow Desk skeptic, journal results in Portfolio']];
  D.forEach(([t,r,e],i)=>{const c=el('div');c.style.cssText='border:1px solid var(--line);border-top:2px solid var(--gold);padding:6px 7px';const a=el('div',null,t);a.style.cssText='font-weight:700;font-size:11px';const b=el('div','m',r);b.style.cssText='font-size:10px;margin:2px 0';const d=el('div',null,e);d.style.cssText='font-size:10px;color:'+(i===0&&A.ran?'var(--grn)':'var(--mut)');c.append(a,b,d);grid.append(c);});
  if(A.ran){const S=A.sources||{},nm=Object.keys(S),okn=nm.filter(n=>S[n]==='ok').length,T=A.tech||{},tf=Object.keys(T).filter(t=>T[t]&&T[t].status==='ok'),cnt={};tf.forEach(t=>{const k=String(T[t].trend||'?');cnt[k]=(cnt[k]||0)+1;});const agree=Object.values(cnt).length?Math.max(...Object.values(cnt)):0;
    const steps=[['Sources asked',nm.length,nm.length],['Sources returned data',okn,nm.length],['Timeframes with data',tf.length,Object.keys(T).length],['Timeframes sharing the most common trend',agree,Object.keys(T).length]];
    const fn=el('div');fn.style.cssText='border:1px solid var(--line);padding:5px 7px;margin-bottom:6px';
    const hd=el('div',null,'Evidence funnel · stance: '+(A.stance||'UNAVAILABLE'));hd.style.cssText='font-weight:700;font-size:11px;margin-bottom:3px';fn.append(hd);
    steps.forEach(([k,v,mx])=>{const r=el('div');r.style.cssText='display:flex;align-items:center;gap:6px;font-size:10px;margin:2px 0';const l=el('span','m',k);l.style.cssText='flex:0 0 130px';const b=el('div');b.style.cssText='flex:1;height:7px;background:var(--panel2);border:1px solid var(--line)';const f=el('div');f.style.cssText='height:100%;background:var(--gold);width:'+(mx>0?Math.round(100*v/mx):0)+'%';b.append(f);const n=el('span',null,v+'/'+mx);n.style.fontFamily='ui-monospace,Menlo,monospace';r.append(l,b,n);fn.append(r);});
    (A.warnings||[]).slice(0,3).forEach(w=>{const d=el('div',null,'⚠ '+w);d.style.cssText='font-size:9px;color:var(--red);margin-top:2px';fn.append(d);});
    wrap.append(fn);}
  wrap.append(note,grid);this.body.append(wrap);
};
'''
    tia_funded_panel = r'''
Panel.prototype.build_tiafunded = function(){
  const wrap=el('div');wrap.style.cssText='padding:8px;overflow:auto;height:100%;font-size:11px';
  const note=el('div','m','Prop-firm account rules from the Prop Firms page. Rule limits only: the live balance is not read here, so distance to a limit is NOT shown.');note.style.cssText='font-size:10px;margin-bottom:6px';
  const out=el('div');wrap.append(note,out);this.body.append(wrap);
  const F=(typeof TIA_FUNDED!=='undefined'&&TIA_FUNDED)||{},A=F.accounts||[];
  if(!A.length){out.textContent=F.error?('Prop accounts unavailable: '+F.error):'No prop accounts configured.';return;}
  const money=s=>{const m=String(s||'').match(/([\d.]+)\s*([KkMm]?)/);if(!m)return null;const u=m[2].toLowerCase();return +m[1]*(u==='k'?1e3:u==='m'?1e6:1);};
  const usd=v=>v==null?'':' ($'+Math.round(v).toLocaleString()+')';
  A.forEach(a=>{const card=el('div');card.style.cssText='border:1px solid var(--line);border-left:3px solid '+(a.color||'#d6ad62')+';padding:7px 9px;margin-bottom:6px';
    const sz=money(a.size),active=a.status==='active';
    const head=el('div',null,(a.firm||'')+' · '+(a.name||a.id));head.style.cssText='font-weight:700;margin-bottom:3px';
    const st=el('span',null,' '+String(a.status||'').toUpperCase());st.style.cssText='font-weight:400;font-size:9px;color:'+(active?'var(--grn)':'var(--mut)');head.append(st);card.append(head);
    const row=(k,v,col)=>{const r=el('div');r.style.cssText='display:flex;justify-content:space-between;gap:8px;padding:1px 0';const l=el('span','m',k),x=el('span',null,v);x.style.cssText='font-family:ui-monospace,Menlo,monospace'+(col?';color:'+col:'');r.append(l,x);card.append(r);};
    const pct=(p)=>Number.isFinite(+p)&&+p>0?(+p).toFixed(1)+'%'+usd(sz==null?null:sz*p/100):'-';
    row('Max loss',pct(a.max_loss_pct));row('Daily loss',pct(a.daily_loss_pct));if(+a.profit_target_pct>0)row('Profit target',pct(a.profit_target_pct));
    if(a.inactivity_limit){const d=a.days_left;row('Inactivity ('+a.inactivity_limit+' d)',active?(d==null?'-':d+' d left'):'not active',active&&d!=null&&d<=7?'var(--red)':null);}
    if(a.consistency_rule)row('Consistency',String(a.consistency_rule));
    out.append(card);});
  const foot=el('div','m','Source: Prop Firms page data (session). Rules are as entered by you; verify them on the firm site.');foot.style.cssText='font-size:10px';out.append(foot);
};
'''
    tia_ring_panel = r'''
Panel.prototype.build_tiaring = function(){
  const wrap=el('div');wrap.style.cssText='padding:6px;overflow:auto;height:100%;font-size:11px';
  const out=el('div');const note=el('div','m','Session ring: average traded volume (bar length) and average high-low range (bar brightness) by UTC hour of day, from the last 300 OKX 1H candles of the centre pair. Session hours are conventional UTC approximations (Asia 00-08, London 07-16, New York 13-22), not exchange rules. About 12 samples per hour: descriptive, not a forecast.');note.style.cssText='font-size:10px;margin-top:4px';
  wrap.append(out,note);this.body.append(wrap);
  let dead=false;this.unsubs.push(()=>{dead=true;});
  const sym=(SYMS||[]).find(s=>/^[A-Z0-9]+-USDT$/.test(s));
  const sv=(tag,at,txt)=>{const e=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const k in at)e.setAttribute(k,at[k]);if(txt!=null)e.textContent=txt;return e;};
  const draw=(vol,rng,cnt)=>{out.replaceChildren();const S=340,C=S/2,r0=52,L=96;
    const svg=sv('svg',{viewBox:'0 0 '+S+' '+S,width:'100%',height:'100%'});svg.style.cssText='max-height:'+Math.max(240,(this.body.clientHeight||340)-70)+'px;display:block;margin:0 auto';
    const mv=Math.max(...vol)||1,mr=Math.max(...rng)||1;
    svg.append(sv('circle',{cx:C,cy:C,r:r0-4,fill:'none',stroke:'#51432c','stroke-dasharray':'3 5'}));
    for(let h=0;h<24;h++){const a=(-90+h*15)*Math.PI/180,len=6+L*vol[h]/mv,b=.25+.75*rng[h]/mr;
      svg.append(sv('line',{x1:C+r0*Math.cos(a),y1:C+r0*Math.sin(a),x2:C+(r0+len)*Math.cos(a),y2:C+(r0+len)*Math.sin(a),stroke:'rgba(214,173,98,'+b.toFixed(2)+')','stroke-width':'9','stroke-linecap':'round'}));
      svg.append(sv('text',{x:C+(r0-16)*Math.cos(a),y:C+(r0-16)*Math.sin(a)+3,'text-anchor':'middle','font-size':'8',fill:'#a99d89'},String(h)));}
    [['ASIA',0,8,'#78a9d1'],['LONDON',7,16,'#31c48d'],['NEW YORK',13,22,'#e66a67']].forEach(([n,a0,a1,col],i)=>{const m=(a0+a1+1)/2,a=(-90+m*15)*Math.PI/180,R=r0+L+22;
      svg.append(sv('text',{x:C+R*Math.cos(a),y:C+R*Math.sin(a)+3,'text-anchor':'middle','font-size':'9',fill:col,'font-weight':'700'},n));});
    svg.append(sv('text',{x:C,y:C-2,'text-anchor':'middle','font-size':'11',fill:'#f3dfb5','font-weight':'700'},sym.replace('-USDT','')));
    svg.append(sv('text',{x:C,y:C+11,'text-anchor':'middle','font-size':'8',fill:'#a99d89'},'UTC hours'));
    out.append(svg);const top=vol.map((v,h)=>[v,h]).sort((x,y)=>y[0]-x[0]).slice(0,3).map(x=>x[1]+':00').join(', ');
    const f=el('div','m','Busiest UTC hours by volume: '+top+' · '+cnt+' candles · source OKX public API · '+new Date().toISOString().slice(0,16)+' UTC');f.style.cssText='font-size:10px';out.append(f);};
  const load=async()=>{
    if(!sym){out.textContent='Needs a crypto USDT pair as the centre symbol.';return;}
    out.textContent='Loading candles...';
    try{const r=await fetch('https://www.okx.com/api/v5/market/candles?instId='+sym+'&bar=1H&limit=300');const j=await r.json();if(dead)return;
      if(!(j&&j.code==='0'&&Array.isArray(j.data)&&j.data.length>=96)){out.textContent='Not enough candle data returned (feed unavailable).';return;}
      const sv_=new Array(24).fill(0),sr=new Array(24).fill(0),n=new Array(24).fill(0);
      j.data.forEach(c=>{const h=new Date(+c[0]).getUTCHours(),o=+c[1],hi=+c[2],lo=+c[3],v=+c[5];if(!(o>0)||!Number.isFinite(v))return;sv_[h]+=v;sr[h]+=(hi-lo)/o*100;n[h]++;});
      const vol=sv_.map((x,h)=>n[h]?x/n[h]:0),rng=sr.map((x,h)=>n[h]?x/n[h]:0);
      draw(vol,rng,j.data.length);}catch(e){if(!dead)out.textContent='Candle feed error: '+String(e).slice(0,80);}};
  load();const iv=setInterval(()=>{if(!document.hidden)load();},900000);this.unsubs.push(()=>clearInterval(iv));
};
'''
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

    # TIA data widgets (owner 2026-11-10; TIA_FOUNDATION.md: heatmaps + portfolio analytics). Real data only: OKX public candles, the workspace's own Journal.
    tia_extra_panels = r'''
Panel.prototype.build_tiacorr = function(){
  const wrap=el('div');wrap.style.cssText='padding:8px;overflow:auto;height:100%;font-size:11px';
  const note=el('div','m','Correlation of hourly log returns, last 100 OKX 1H candles, crypto USDT pairs only. Correlation is not causation; it moves with the window.');note.style.cssText='font-size:10px;margin-bottom:6px';
  const out=el('div');wrap.append(note,out);this.body.append(wrap);
  let dead=false;this.unsubs.push(()=>{dead=true;});
  const syms=(SYMS||[]).filter(s=>/^[A-Z0-9]+-USDT$/.test(s)).slice(0,10);
  const corr=(x,y)=>{const n=Math.min(x.length,y.length);if(n<20)return null;const a=x.slice(-n),b=y.slice(-n);const ma=a.reduce((s,v)=>s+v,0)/n,mb=b.reduce((s,v)=>s+v,0)/n;let sab=0,saa=0,sbb=0;for(let i=0;i<n;i++){const da=a[i]-ma,db=b[i]-mb;sab+=da*db;saa+=da*da;sbb+=db*db;}return saa>0&&sbb>0?sab/Math.sqrt(saa*sbb):null;};
  const draw=(series,names,n)=>{out.replaceChildren();const tbl=el('table');tbl.style.cssText='border-collapse:collapse;font:10px ui-monospace,Menlo,monospace';
    const hr=el('tr');hr.append(el('th'));names.forEach(s=>{const th=el('th',null,s.replace('-USDT',''));th.style.cssText='padding:3px 4px;color:var(--mut)';hr.append(th);});tbl.append(hr);
    names.forEach(a=>{const tr=el('tr');const th=el('th',null,a.replace('-USDT',''));th.style.cssText='padding:3px 6px;text-align:right;color:var(--mut)';tr.append(th);
      names.forEach(b=>{const c=a===b?1:corr(series[a],series[b]);const td=el('td',null,c==null?'-':c.toFixed(2));const mag=c==null?0:Math.min(1,Math.abs(c));
        td.style.cssText='padding:5px 6px;text-align:center;border:1px solid var(--line);background:'+(c==null?'rgba(130,130,130,.1)':c>=0?'rgba(49,196,141,'+(.08+.5*mag)+')':'rgba(230,106,103,'+(.08+.5*mag)+')');tr.append(td);});tbl.append(tr);});
    out.append(tbl);const f=el('div','m','Source: OKX public API · '+n+' aligned hourly returns · '+new Date().toISOString().slice(0,16)+' UTC');f.style.cssText='font-size:10px;margin-top:6px';out.append(f);};
  const load=async()=>{
    if(syms.length<2){out.textContent='Needs at least two USDT pairs in the symbol list.';return;}
    out.textContent='Loading candles...';const raw={};
    await Promise.all(syms.map(async s=>{try{const r=await fetch('https://www.okx.com/api/v5/market/candles?instId='+s+'&bar=1H&limit=100');const j=await r.json();if(j&&j.code==='0'&&Array.isArray(j.data)){const m=new Map();j.data.forEach(c=>m.set(+c[0],+c[4]));raw[s]=m;}}catch(e){}}));
    if(dead)return;const names=syms.filter(s=>raw[s]&&raw[s].size>=30);
    if(names.length<2){out.textContent='No candle data returned for enough pairs (feed unavailable).';return;}
    let ts=[...raw[names[0]].keys()];names.slice(1).forEach(s=>{ts=ts.filter(t=>raw[s].has(t));});ts.sort((a,b)=>a-b);
    if(ts.length<25){out.textContent='Too few aligned candles to compute correlation.';return;}
    const series={};names.forEach(s=>{const c=ts.map(t=>raw[s].get(t));const r=[];for(let i=1;i<c.length;i++)if(c[i]>0&&c[i-1]>0)r.push(Math.log(c[i]/c[i-1]));series[s]=r;});
    draw(series,names,ts.length-1);};
  load();const iv=setInterval(()=>{if(!document.hidden)load();},600000);this.unsubs.push(()=>clearInterval(iv));
};
Panel.prototype.build_tiaport = function(){
  const wrap=el('div');wrap.style.cssText='padding:8px;overflow:auto;height:100%;font-size:11px';
  const out=el('div');wrap.append(out);this.body.append(wrap);
  const draw=()=>{out.replaceChildren();let J=[];try{J=(Journal&&Journal.list)||[];}catch(e){}
    const done=J.filter(t=>(t.status==='tp'||t.status==='sl')&&Number.isFinite(+t.r)).sort((a,b)=>((+a.t1||+a.t0||0)-(+b.t1||+b.t0||0)));
    const n=done.length;
    if(!n){out.append(el('div','m','No closed journal trades yet. Nothing is estimated: these numbers come only from the closed trades in this workspace journal.'));return;}
    const rs=done.map(t=>+t.r),sum=rs.reduce((s,v)=>s+v,0),wins=rs.filter(v=>v>0),loss=rs.filter(v=>v<0);
    const gw=wins.reduce((s,v)=>s+v,0),gl=-loss.reduce((s,v)=>s+v,0);
    let cum=0,peak=0,dd=0;rs.forEach(v=>{cum+=v;if(cum>peak)peak=cum;if(peak-cum>dd)dd=peak-cum;});
    const fmt=(v,d)=>Number.isFinite(v)?v.toFixed(d==null?2:d):'-';
    const cards=[['TRADES',String(n)],['WIN RATE',fmt(100*wins.length/n,0)+'%'],['EXPECTANCY',fmt(sum/n,3)+' R'],['PROFIT FACTOR',gl>0?fmt(gw/gl):'-'],['TOTAL',fmt(sum)+' R'],['MAX DRAWDOWN',fmt(dd)+' R']];
    const grid=el('div');grid.style.cssText='display:grid;grid-template-columns:repeat(auto-fit,minmax(96px,1fr));gap:6px;margin-bottom:8px';
    cards.forEach(([k,v])=>{const c=el('div');c.style.cssText='padding:7px;border:1px solid var(--line)';const a=el('div','m',k);a.style.fontSize='9px';const b=el('div',null,v);b.style.cssText='font:700 15px ui-monospace,Menlo,monospace;margin-top:4px';c.append(a,b);grid.append(c);});out.append(grid);
    const by={};done.forEach(t=>{const k=String(t.symbol||'?');(by[k]=by[k]||{n:0,r:0});by[k].n++;by[k].r+=+t.r;});
    const tbl=el('table');tbl.style.cssText='width:100%;border-collapse:collapse;font:11px ui-monospace,Menlo,monospace';
    const h=el('tr');['SYMBOL','N','TOTAL R'].forEach(x=>{const th=el('th',null,x);th.style.cssText='text-align:right;padding:4px;border-bottom:1px solid var(--line);color:var(--mut)';h.append(th);});tbl.append(h);
    Object.entries(by).sort((a,b)=>b[1].r-a[1].r).slice(0,12).forEach(([k,v])=>{const tr=el('tr');[k.replace(/^HL:xyz:|^Y:|-USDT.*$/g,''),String(v.n),fmt(v.r)].forEach((x,i)=>{const td=el('td',null,x);td.style.cssText='text-align:right;padding:4px;border-bottom:1px solid var(--line)';if(i===2)td.style.color=v.r>=0?'var(--grn)':'var(--red)';tr.append(td);});tbl.append(tr);});out.append(tbl);
    const foot=el('div','m',(n<30?'Under 30 closed trades: this is not evidence. ':'')+'R-multiples from the journal; costs and slippage are whatever the journal recorded. Funded-account limits are not modelled here.');foot.style.cssText='font-size:10px;margin-top:8px';out.append(foot);};
  draw();const iv=setInterval(()=>{if(!document.hidden)draw();},5000);this.unsubs.push(()=>clearInterval(iv));
};
'''
    # Radial correlation (TIA_FOUNDATION: radial geometry = central asset + measured relationships with metric, sample and window).
    tia_radial_panel = r'''
Panel.prototype.build_tiaradial = function(){
  const wrap=el('div');wrap.style.cssText='padding:6px;overflow:auto;height:100%;font-size:11px';
  const out=el('div');const note=el('div','m','Radial correlation: centre = the selected pair, spokes = the other USDT pairs. Hourly log returns, last 100 OKX 1H candles. Line width = |correlation|; green positive, red negative. Lead-lag is the lag (-3..+3 h) with the largest |correlation|: a descriptive measure on a small sample, not a trading signal; correlation is not causation.');note.style.cssText='font-size:10px;margin-top:4px';
  wrap.append(out,note);this.body.append(wrap);
  let dead=false;this.unsubs.push(()=>{dead=true;});
  const syms=(SYMS||[]).filter(s=>/^[A-Z0-9]+-USDT$/.test(s)).slice(0,11);
  const pear=(x,y)=>{const n=x.length;if(n<20)return null;const mx=x.reduce((s,v)=>s+v,0)/n,my=y.reduce((s,v)=>s+v,0)/n;let sxy=0,sxx=0,syy=0;for(let i=0;i<n;i++){const dx=x[i]-mx,dy=y[i]-my;sxy+=dx*dy;sxx+=dx*dx;syy+=dy*dy;}return sxx>0&&syy>0?sxy/Math.sqrt(sxx*syy):null;};
  const lagged=(a,b,k)=>{const x=[],y=[];for(let i=0;i<a.length;i++){const j=i+k;if(j>=0&&j<b.length){x.push(a[i]);y.push(b[j]);}}return pear(x,y);};
  const sv=(tag,at,txt)=>{const e=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const k in at)e.setAttribute(k,at[k]);if(txt!=null)e.textContent=txt;return e;};
  const draw=(series,names,n)=>{out.replaceChildren();const c0=names[0],others=names.slice(1),S=360,C=S/2,R=128;
    const svg=sv('svg',{viewBox:'0 0 '+S+' '+S,width:'100%',height:'100%'});svg.style.cssText='max-height:'+Math.max(240,(this.body.clientHeight||360)-60)+'px;display:block;margin:0 auto';
    svg.append(sv('circle',{cx:C,cy:C,r:R,fill:'none',stroke:'#51432c','stroke-dasharray':'3 5'}));
    others.forEach((s,i)=>{const ang=-Math.PI/2+2*Math.PI*i/others.length,x=C+R*Math.cos(ang),y=C+R*Math.sin(ang),cr=pear(series[c0],series[s]);
      let best=null;for(let k=-3;k<=3;k++){const v=lagged(series[c0],series[s],k);if(v!=null&&(best==null||Math.abs(v)>Math.abs(best.v)))best={k,v};}
      const mag=cr==null?0:Math.min(1,Math.abs(cr)),col=cr==null?'#848e9c':cr>=0?'#31c48d':'#e66a67';
      svg.append(sv('line',{x1:C,y1:C,x2:x,y2:y,stroke:col,'stroke-width':String(1+6*mag),opacity:String(.35+.55*mag)}));
      svg.append(sv('circle',{cx:x,cy:y,r:'17',fill:'#141311',stroke:col,'stroke-width':'2'}));
      svg.append(sv('text',{x:x,y:y-1,'text-anchor':'middle','font-size':'9',fill:'#eee6d7','font-weight':'700'},s.replace('-USDT','')));
      svg.append(sv('text',{x:x,y:y+9,'text-anchor':'middle','font-size':'8',fill:col},cr==null?'-':cr.toFixed(2)));
      const lx=C+(R+34)*Math.cos(ang),ly=C+(R+34)*Math.sin(ang);
      svg.append(sv('text',{x:lx,y:ly,'text-anchor':'middle','font-size':'7',fill:'#a99d89'},best&&best.k!==0&&best.v!=null?('lag '+(best.k>0?'+':'')+best.k+'h '+best.v.toFixed(2)):''));});
    svg.append(sv('circle',{cx:C,cy:C,r:'26',fill:'#201d18',stroke:'#d6ad62','stroke-width':'2'}));
    svg.append(sv('text',{x:C,y:C+3,'text-anchor':'middle','font-size':'10',fill:'#f3dfb5','font-weight':'700'},c0.replace('-USDT','')));
    out.append(svg);const f=el('div','m','Source: OKX public API · '+n+' aligned hourly returns · '+new Date().toISOString().slice(0,16)+' UTC · lag text shown only when the best lag is not 0');f.style.cssText='font-size:10px';out.append(f);};
  const load=async()=>{
    if(syms.length<3){out.textContent='Needs at least three USDT pairs in the symbol list.';return;}
    out.textContent='Loading candles...';const raw={};
    await Promise.all(syms.map(async s=>{try{const r=await fetch('https://www.okx.com/api/v5/market/candles?instId='+s+'&bar=1H&limit=100');const j=await r.json();if(j&&j.code==='0'&&Array.isArray(j.data)){const m=new Map();j.data.forEach(c=>m.set(+c[0],+c[4]));raw[s]=m;}}catch(e){}}));
    if(dead)return;const names=syms.filter(s=>raw[s]&&raw[s].size>=30);
    if(names.length<3||names[0]!==syms[0]){out.textContent='No candle data for the centre pair or too few pairs (feed unavailable).';return;}
    let ts=[...raw[names[0]].keys()];names.slice(1).forEach(s=>{ts=ts.filter(t=>raw[s].has(t));});ts.sort((a,b)=>a-b);
    if(ts.length<25){out.textContent='Too few aligned candles.';return;}
    const series={};names.forEach(s=>{const c=ts.map(t=>raw[s].get(t));const r=[];for(let i=1;i<c.length;i++)r.push(c[i]>0&&c[i-1]>0?Math.log(c[i]/c[i-1]):0);series[s]=r;});
    draw(series,names,ts.length-1);};
  load();const iv=setInterval(()=>{if(!document.hidden)load();},600000);this.unsubs.push(()=>clearInterval(iv));
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
    doc = doc.replace("const WGROUPS = () => [", tia_panels + tia_new_panels + tia_extra_panels + tia_radial_panel + tia_funded_panel + tia_ring_panel + tia_agents_panel + tia_plan_panel + tia_conf_panel + tia_health_panel + "\nconst WGROUPS = () => [");
    doc = doc.replace('[Lg("Settings","الإعدادات"), "#9aa3ad", ["settings"]]', '[Lg("TIA Intelligence","استخبارات TIA"), "#d6ad62", ["tiapulse","tiasources","tiaheat","tiaoptions","tiacorr","tiaradial","tiaport","tiafunded","tiaring","tiaagents","tiaplan","tiaconf","tiahealth"]], [Lg("Settings","الإعدادات"), "#9aa3ad", ["settings"]]');
    doc = doc.replace('settings:"SET", "@std"', 'settings:"SET", tiapulse:"PULSE", tiasources:"SRC", tiaheat:"HEAT", tiaoptions:"OPT", tiacorr:"CORR", tiaradial:"RADIAL", tiafunded:"FUND", tiaring:"RING", tiaagents:"AGENTS", tiaplan:"PLAN", tiaconf:"CONF", tiahealth:"HEALTH", tiaport:"PORT", "@std"');
    # Isolate all localStorage/sessionStorage keys from the original Workspace.
    # tia_ws_v2: a fresh key, so browsers that already saved the old Workspace-copy layout (v1) start from the TIA layout below.
    doc = doc.replace("ai_ws_v5", "tia_ws_v6")
    # Owner 2026-11-10: on 1H / 1D / 1W the order-flow map was a thin line, because it shared the chart's (huge) price range while the book only covers about +-0.6 %.
    # In TIA the map starts with its OWN price scale (auto range around the current price; shift+wheel / drag on it still adjusts). The Workspace default is untouched.
    doc = doc.replace("this.colWide = 0; this.colOwn = false;", "this.colWide = 0; this.colOwn = true;", 1)
    # TIA's own start layout (owner 2026-11-10: use the Workspace widget engine, but show TIA's data, not a Workspace copy):
    # heatmap + pulse on top, ONE chart with the order-flow column + the Order Flow Desk in the middle, options + feed health at the bottom.
    # Every other widget stays one click away in + Widget. The Workspace standard stays untouched (renamed, never deleted).
    tia_layout = r'''
Ws.builtinStandard = () => {
  const W = Math.max(600, Ws.el.clientWidth || 1200), H = Math.max(500, Math.min((Ws.el.clientHeight || 760) - 8, 960)), r = v => Math.round(v), g = 6, S0 = SYMS[0];
  const h1 = r(H*0.24), h2 = r(H*0.50), y2 = h1 + g, y3 = y2 + h2 + g, h3 = H - y3, w1 = r((W - g)*0.6), w2 = W - w1 - g, w3 = r((W - g)*0.56), w4 = W - w3 - g;
  const OF = {dcol:true, dom:true, bub:true}, E = {9:true, 21:true, 50:false};
  const ta = r((W - 3*g)*0.26), tb = r((W - 3*g)*0.22), tcf = r((W - 3*g)*0.20), tc = W - ta - tb - tcf - 3*g, ba = r((W - 4*g)*0.26), bb = r((W - 4*g)*0.22), bd = r((W - 4*g)*0.22), bh = r((W - 4*g)*0.14), bc = W - ba - bb - bd - bh - 4*g;
  return [
    ["tiaheat", {x:0, y:0, w:ta, h:h1}, {group:1}],
    ["tiaplan", {x:ta + g, y:0, w:tb, h:h1}, {group:1}],
    ["tiaconf", {x:ta + tb + 2*g, y:0, w:tcf, h:h1}, {group:1}],
    ["tiaagents", {x:ta + tb + tcf + 3*g, y:0, w:r(tc*0.62), h:h1}, {group:1}],
    ["tiafunded", {x:ta + tb + tcf + 4*g + r(tc*0.62), y:0, w:tc - r(tc*0.62) - g, h:h1}, {group:1}],
    ["chart", {x:0, y:y2, w:w3, h:h2}, Object.assign({sym:S0, group:1, tf:"15m", ema:E}, OF)],
    ["ofdesk", {x:w3 + g, y:y2, w:w4, h:h2}, {group:1}],
    ["tiaoptions", {x:0, y:y3, w:ba, h:h3}, {group:1}],
    ["tiacorr", {x:ba + g, y:y3, w:bb, h:h3}, {group:1}],
    ["tiaradial", {x:ba + bb + 2*g, y:y3, w:bd, h:h3}, {group:1}],
    ["tiahealth", {x:ba + bb + bd + 3*g, y:y3, w:bh, h:h3}, {group:1}],
    ["tiaport", {x:ba + bb + bd + bh + 4*g, y:y3, w:bc, h:h3}, {group:1}],
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
