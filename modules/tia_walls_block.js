/* TIAWALLS-CORE-BEGIN */
// Live wall threshold rule, same as tia.analytics.walls (rolling quantile + k x median, strict >). Stateless: one snapshot.
function twLiveWalls(snaps, tick, k, pctl, window){
  const last=snaps[snaps.length-1];
  if(!last||!last.bids.length||!last.asks.length) return {mid:null,walls:[]};
  const mid=(last.bids[0].p+last.asks[0].p)/2, walls=[], from=Math.max(0,snaps.length-window);
  for(const side of ['bid','ask']){
    const pool=[];
    for(let i=from;i<snaps.length;i++) for(const x of (side==='ask'?snaps[i].asks:snaps[i].bids)) pool.push(x.q);
    if(!pool.length) continue;
    pool.sort((a,b)=>a-b);
    const med=pool[Math.floor(pool.length/2)];
    if(!(med>0)) continue;
    const thr=Math.max(k*med, pool[Math.min(pool.length-1, Math.floor(pctl*pool.length))]);
    for(const x of (side==='ask'?last.asks:last.bids))
      if(x.q>thr) walls.push({side:side, price:x.p, q:x.q, xmed:x.q/med, ticks:Math.round((x.p-mid)/tick)});
  }
  return {mid:mid, walls:walls};
}
/* TIAWALLS-CORE-END */

Panel.prototype.build_tiawalls = function(){
  const wrap=el('div'); wrap.style.cssText='padding:8px;overflow:auto;height:100%;font-size:12px';
  const head=el('div','m','Live walls · OKX book ~1 s · rolling p99 and 6x median · a description, not a verdict');
  head.style.marginBottom='8px';
  const body=el('div'); wrap.append(head,body); this.body.append(wrap);
  const sym=(SYMS&&SYMS[0])||''; const snaps=[]; let dead=false;
  const draw=()=>{
    body.replaceChildren();
    const last=snaps[snaps.length-1];
    if(!last){body.textContent='Waiting for book snapshots…';return;}
    const tick=last.asks.length>1?(last.asks[1].p-last.asks[0].p):0;
    if(!(tick>0)){body.textContent='Book too thin to read a tick size.';return;}
    const r=twLiveWalls(snaps,tick,6,0.99,120);
    const meta=el('div','m',snaps.length+'/120 snapshots · tick '+tick+' · mid '+(r.mid==null?'—':r.mid));
    meta.style.marginBottom='6px'; body.append(meta);
    if(!r.walls.length){body.append(el('div','m','No level above threshold right now.'));return;}
    const near=r.walls.reduce((a,b)=>Math.abs(b.ticks)<Math.abs(a.ticks)?b:a);
    const mg=el('div',null,'Nearest wall: '+(near.side==='ask'?'resistance':'support')+' at '+near.price+' ('+near.ticks+' ticks)');
    mg.style.cssText='margin-bottom:6px;color:var(--gold,#d6ad62)'; body.append(mg);
    const t=el('table'); t.style.cssText='width:100%;border-collapse:collapse;font:12px ui-monospace,Menlo,monospace';
    const hr=el('tr'); ['SIDE','PRICE','SIZE','x MEDIAN','TICKS'].forEach(x=>{const th=el('th',null,x);th.style.cssText='text-align:right;padding:5px;border-bottom:1px solid var(--line)';hr.append(th);}); t.append(hr);
    r.walls.slice().sort((a,b)=>a.price-b.price).forEach(w=>{
      const tr=el('tr'); [w.side==='ask'?'RES':'SUP', w.price, w.q, w.xmed.toFixed(1), w.ticks].forEach(v=>{const td=el('td',null,String(v));td.style.cssText='text-align:right;padding:5px;border-bottom:1px solid var(--line)';tr.append(td);});
      t.append(tr);
    });
    body.append(t);
  };
  const off=Hub.sub('book',sym,b=>{
    if(dead||!b||b.error||!b.bids||!b.asks) return;
    snaps.push({bids:b.bids,asks:b.asks}); if(snaps.length>120) snaps.shift(); draw();
  });
  this.unsubs.push(()=>{dead=true;}); this.unsubs.push(off);
  draw();
};
