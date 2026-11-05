
/* XCMD: a small, SAFE command layer for outside drivers (the XPiX Telegram bot through Playwright, tests, a human in the console). docs/XPIX_BOT_BRIEF.md.
   Read + view + draw only: it never places or changes an order, never opens an outside page, never touches keys. Every call returns {ok:true,...} or {ok:false,err}. */
const XCMD = (() => {
  const OK = o => Object.assign({ok:true}, o || {}), ERR = m => ({ok:false, err:String(m)});
  const NOPEN = ["web","video","tvc"];   // panels that load outside pages are not opened by commands
  const chartPanel = id => id ? Ws.panels.find(p => p.id === id && p.chart) : (Ws.panels.find(p => p.type === "chart" && p.chart && !p.min) || Ws.panels.find(p => p.chart));
  const price = (ch, v) => Number.isFinite(+v) ? +v : null;
  const lastT = ch => ch.data.length ? ch.data[ch.data.length-1].t : Date.now();
  const pt = (ch, q) => { const p = price(ch, q && q.p != null ? q.p : q && q.price); if (p == null) return null; const t = q && Number.isFinite(+q.t) ? +q.t : lastT(ch); return {t, p}; };
  const api = {
    version: 1,
    state(){ return OK({sym:SYMS.slice(), tfs:Object.keys(TFSEC), panels:Ws.panels.map(p => ({id:p.id, type:p.type, sym:p.state.sym, tf:p.state.tf || null, min:!!p.min,
      ind: p.indItems ? p.indItems.filter(i => { try { return !!(i.get && i.get()); } catch(e){ return false; } }).map(i => i.id) : [],
      bars: p.chart ? p.chart.data.length : null, last: p.chart && p.chart.data.length ? p.chart.data[p.chart.data.length-1].c : null, draws: p.chart ? p.chart.draws.length : null}))}); },
    setSymbol(sym, panelId){ const p = chartPanel(panelId); if (!p) return ERR("no chart panel"); if (!SYMS.includes(sym)) return ERR("unknown symbol (see state().sym)"); Ws.broadcast(p, sym); return OK({id:p.id, sym}); },
    setTf(tf, panelId){ const p = chartPanel(panelId); if (!p) return ERR("no chart panel"); if (!(tf in TFSEC)) return ERR("unknown timeframe (see state().tfs)"); p.setTf(tf); return OK({id:p.id, tf}); },
    addPanel(type){ if (!/^[a-z]+$/.test(String(type)) || NOPEN.includes(type) || typeof Panel.prototype["build_"+type] !== "function") return ERR("panel type not allowed"); const n = Ws.panels.length; Ws.add(type); const p = Ws.panels[Ws.panels.length-1]; return Ws.panels.length > n ? OK({id:p.id, type}) : ERR("not added"); },
    closePanel(id){ const p = Ws.panels.find(x => x.id === id); if (!p) return ERR("no such panel"); p.close(); return OK({id}); },
    toggle(ind, on, panelId){ const p = chartPanel(panelId); if (!p || !p.indItems) return ERR("no chart panel"); const it = p.indItems.find(i => i.id === ind); if (!it || !it.set) return ERR("unknown indicator (see list())");
      try { it.set(!!on); p.chart.draw(); Ws.save(); } catch(e){ return ERR(e.message || e); } return OK({id:p.id, ind, on:!!on}); },
    list(panelId){ const p = chartPanel(panelId); return p && p.indItems ? OK({id:p.id, ind:p.indItems.filter(i => i.set).map(i => i.id)}) : ERR("no chart panel"); },
    draw(o, panelId){ o = o || {}; const p = chartPanel(panelId || o.panelId); if (!p) return ERR("no chart panel"); const ch = p.chart, kind = o.kind, id = Date.now()+Math.random(); let d;
      if (kind === "hline" || kind === "vline"){ const a = pt(ch, o.points ? o.points[0] : o); if (!a) return ERR("hline needs price"); d = {id, type:kind, pts:[a]}; }
      else if (kind === "trend" || kind === "rect"){ const a = pt(ch, o.points && o.points[0]), b = pt(ch, o.points && o.points[1]); if (!a || !b) return ERR(kind+" needs 2 points {t,p}"); d = {id, type:kind, pts:[a, b]}; }
      else if (kind === "text"){ const a = pt(ch, o.points ? o.points[0] : o); if (!a) return ERR("text needs price"); d = {id, type:"text", txt:String(o.text || o.label || "").slice(0, 80), pts:[a]}; }
      else return ERR("kind must be hline | vline | trend | rect | text");
      if (/^#[0-9a-fA-F]{6}$/.test(o.color || "")) d.color = o.color; if (kind !== "text" && o.label) d.label = String(o.label).slice(0, 40);
      ch.draws.push(d); ch.saveDraws(); ch.draw(); return OK({id:p.id, drawId:d.id, n:ch.draws.length}); },
    clearDrawings(panelId){ const p = chartPanel(panelId); if (!p) return ERR("no chart panel"); const n = p.chart.draws.length; p.chart.draws = []; p.chart.sel = null; p.chart.saveDraws(); p.chart.draw(); return OK({id:p.id, removed:n}); },
    // ---- indicator settings (the same fields as the gear panel) + layouts (step 2 of the XPiX Agent) ----
    params(ind, panelId){ const p = chartPanel(panelId); if (!p || !p.indItems) return ERR("no chart panel"); const it = p.indItems.find(i => i.id === ind); if (!it) return ERR("unknown indicator (see list())"); if (!it.sty) return OK({id:p.id, ind, sty:null, params:[]});
      const st = p.chart.st[it.sty] || {}, defs = (it.params || []).filter(d => !d.sep).map(d => ({key:d.key, label:d.label, type: d.opts ? "select" : d.bool ? "bool" : d.color ? "color" : d.text ? "text" : "number", min:d.min, max:d.max, step:d.step, opts:d.opts ? d.opts.map(o => o[0]) : undefined, value:st[d.key]}));
      const base = [["color","color"],["color2","color"],["w","number"],["dash","text"]].filter(([k]) => k in st).map(([k, t]) => ({key:k, label:k, type:t, value:st[k]}));
      return OK({id:p.id, ind, sty:it.sty, params:base.concat(defs)}); },
    setParam(ind, key, value, panelId){ const p = chartPanel(panelId); if (!p || !p.indItems) return ERR("no chart panel"); const it = p.indItems.find(i => i.id === ind); if (!it || !it.sty) return ERR("indicator has no settings (see params())");
      const st = p.chart.st[it.sty], d = (it.params || []).find(x => x.key === key), common = ["color","color2","w","dash"].includes(key) && key in st; if (!d && !common) return ERR("unknown setting (see params())");
      let v = value;
      if (common){ if (key === "color" || key === "color2"){ if (!/^#[0-9a-fA-F]{6}$/.test(v)) return ERR("color must be #rrggbb"); } else if (key === "w"){ v = +v; if (!(v >= 0.5 && v <= 6)) return ERR("w must be 0.5-6"); } else { v = String(v); if (!/^[0-9, ]*$/.test(v)) return ERR("dash like 4,3"); } }
      else if (d.opts){ const ok = d.opts.find(o => String(o[0]) === String(v)); if (!ok) return ERR("must be one of "+d.opts.map(o => o[0]).join(",")); v = isNaN(+ok[0]) || ok[0] === "" ? ok[0] : +ok[0]; }
      else if (d.bool){ v = (v === true || v === 1 || /^(1|true|on|yes)$/i.test(String(v))) ? 1 : 0; }
      else if (d.color){ if (!/^#[0-9a-fA-F]{6}$/.test(v)) return ERR("color must be #rrggbb"); }
      else if (d.text){ v = String(v).trim().slice(0, 60); }
      else { v = +v; if (!Number.isFinite(v)) return ERR("number expected"); if (!d.free){ if (v < d.min || v > d.max) return ERR("range "+d.min+" .. "+d.max); } else v = Math.max(0, v); }
      st[key] = v; p.state.st = JSON.parse(JSON.stringify(p.chart.st)); try { p.chart.calcEma(); p.chart.resize(); } catch(e){} Ws.save(); return OK({id:p.id, ind, key, value:v}); },
    layout(name){ if (name === "standard" || name === "trading"){ Ws.clear(); Ws.build(Ws.defaults()); Ws.save(); return OK({layout:"standard", panels:Ws.panels.length}); }
      if (name === "blank"){ Ws.clear(); Ws.save(); return OK({layout:"blank", panels:0}); }
      if (name === "save"){ try { store.set(LS+"_std", {v:7, panels: Ws.panels.map(p => ({type:p.type, rect: p.max && p.prev ? p.prev : p.rect, state:p.state}))}); } catch(e){ return ERR(e.message || e); } return OK({layout:"saved-as-standard", panels:Ws.panels.length}); }
      return ERR("layout must be standard | blank | save"); },
    async shot(scale){ try { const c = await Snap.shot(scale || 1); return OK({png:c.toDataURL("image/png"), w:c.width, h:c.height}); } catch(e){ return ERR(e.message || e); } }
  };
  return Object.freeze(api);
})();
window.XCMD = XCMD;
