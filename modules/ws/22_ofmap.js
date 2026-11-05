
/* ORDER FLOW MAP (owner 2026-11-05: "a big price area like Bookmap"): its own panel. X = time, Y = price (+-0.25 % ... +-5 % around the market), colour = resting size of the order book at that price and time
   (the wide book: OKX up to 2000 levels a side, Hyperliquid stitched by hlWideBook), the mid price as a line, trade prints as bubbles, and the CURRENT book as bars on the right. Reads the same Hub "book" and
   "trades" feeds as the other panels (no extra requests). Description of what rests in the book, never a signal. Snapshots are kept per panel in memory only (max 30 min). */
const OFM = {
  NB: 800, SPAN: 0.05, AX: 64, DP: 74, TB: 18,
  RANGES: [[0.0025, "±0.25%"], [0.005, "±0.5%"], [0.01, "±1%"], [0.02, "±2%"], [0.05, "±5%"]],
  WINS: [[120000, "2m"], [300000, "5m"], [900000, "15m"], [1800000, "30m"]],
  PAL: (() => { const st = [[0, 8, 12, 22], [.12, 14, 40, 92], [.3, 18, 96, 170], [.5, 30, 190, 190], [.68, 120, 220, 90], [.82, 245, 200, 40], [.93, 240, 90, 40], [1, 255, 245, 235]], out = new Uint8Array(256*3);
    for (let i = 0; i < 256; i++){ const t = i/255; let k = 0; while (k < st.length-2 && t > st[k+1][0]) k++; const a = st[k], b = st[k+1], u = Math.max(0, Math.min(1, (t - a[0])/(b[0] - a[0]))); for (let c = 0; c < 3; c++) out[i*3+c] = Math.round(a[c+1] + (b[c+1] - a[c+1])*u); } return out; })(),
  snap(b){   // Hub book payload -> {t, mid, bb, ba, base, step, arr}; sizes summed into NB buckets covering mid +-SPAN
    const bids = (b.deep && b.deep.bids) || b.bids || [], asks = (b.deep && b.deep.asks) || b.asks || []; if (!bids.length || !asks.length) return null;
    const bb = bids[0].p, ba = asks[0].p, mid = (bb + ba)/2; if (!(mid > 0)) return null; const base = mid*(1 - OFM.SPAN), step = mid*2*OFM.SPAN/OFM.NB, arr = new Float32Array(OFM.NB);
    const put = x => { if (!(x.q > 0)) return; const i = Math.floor((x.p - base)/step); if (i >= 0 && i < OFM.NB) arr[i] += x.q; }; bids.forEach(put); asks.forEach(put);
    const cov = (Math.max(...asks.map(x => x.p), ba) - Math.min(...bids.map(x => x.p), bb))/mid*100/2;
    return {t:nowS(), mid, bb, ba, base, step, arr, cov}; },
  build(p){
    const S = p.state; S.omR = S.omR != null ? S.omR : 0.01; S.omW = S.omW != null ? S.omW : 300000; S.omB = S.omB !== false;
    p.body.style.cssText = "display:flex;flex-direction:column;overflow:hidden"; p.om = {snaps:[], trades:[], raf:0};
    const tb = el("div","tb"); p.symSel = p.symSelect(); const rs = el("select"), ws = el("select"), bl = el("label"), bx = el("input"); rs.title = Lg("Price range around the market","نطاق السعر حوالين السوق"); ws.title = Lg("Time window","النافذة الزمنية");
    OFM.RANGES.forEach(([v, l]) => { const o = el("option"); o.value = v; o.textContent = l; rs.append(o); }); OFM.WINS.forEach(([v, l]) => { const o = el("option"); o.value = v; o.textContent = l; ws.append(o); });
    rs.value = S.omR; ws.value = S.omW; bx.type = "checkbox"; bx.checked = S.omB; bl.append(bx, document.createTextNode(" "+Lg("Trades","صفقات"))); bl.style.cssText = "font-size:11px;color:#9aa4b2;display:flex;align-items:center;gap:2px";
    rs.onchange = () => { S.omR = +rs.value; Ws.save(); OFM.draw(p); }; ws.onchange = () => { S.omW = +ws.value; Ws.save(); OFM.draw(p); }; bx.onchange = () => { S.omB = bx.checked; Ws.save(); OFM.draw(p); };
    tb.append(p.symSel, rs, ws, bl); const wrap = el("div"); wrap.style.cssText = "position:relative;flex:1;min-height:0"; const cv = el("canvas"); cv.style.cssText = "position:absolute;inset:0;width:100%;height:100%;display:block"; wrap.append(cv); p.ofmCv = cv;
    p.body.append(tb, wrap); const ro = new ResizeObserver(() => OFM.draw(p)); ro.observe(wrap); const iv = setInterval(() => { if (!document.hidden) OFM.draw(p); }, 1000);
    p.destroy = () => { ro.disconnect(); clearInterval(iv); cancelAnimationFrame(p.om.raf); }; p.resub(); },
  resub(p, sym){
    p.om.snaps = []; p.om.trades = []; p.setTitle();
    p.unsubs.push(Hub.sub("book", sym, b => { if (!b || b.error) return; const s = OFM.snap(b); if (!s) return; const o = p.om; o.snaps.push(s); const cut = nowS() - 1900000; while (o.snaps.length > 2 && o.snaps[0].t < cut || o.snaps.length > 1600) o.snaps.shift(); OFM.later(p); }));
    p.unsubs.push(Hub.sub("trades", sym, t => { if (!t || t.error || !t.rows) return; const o = p.om, seen = o.seen = o.seen || new Set(); t.rows.forEach(r => { const id = r.id != null ? r.id : r.t+"|"+r.p+"|"+r.q; if (seen.has(id)) return; seen.add(id); o.trades.push({t:r.t, p:r.p, q:r.q, side:r.side}); });
      if (seen.size > 6000){ seen.clear(); } const cut = nowS() - 1900000; while (o.trades.length && (o.trades[0].t < cut || o.trades.length > 3000)) o.trades.shift(); OFM.later(p); })); },
  later(p){ if (p.om.raf) return; p.om.raf = requestAnimationFrame(() => { p.om.raf = 0; OFM.draw(p); }); },
  nice(span, n){ const raw = span/n, mag = Math.pow(10, Math.floor(Math.log10(raw))), f = raw/mag; return (f < 1.5 ? 1 : f < 3.5 ? 2 : f < 7.5 ? 5 : 10)*mag; },
  draw(p){
    const cv = p.ofmCv; if (!cv || !cv.isConnected) return; const W = Math.floor(cv.clientWidth), H = Math.floor(cv.clientHeight); if (W < 120 || H < 80) return; if (cv.width !== W || cv.height !== H){ cv.width = W; cv.height = H; }
    const c = cv.getContext("2d"), o = p.om, S = p.state; c.fillStyle = "#0b0e11"; c.fillRect(0, 0, W, H); c.font = "10px ui-monospace,Menlo,Consolas,monospace";
    const last = o.snaps[o.snaps.length-1]; if (!last){ c.fillStyle = "#6b7684"; c.fillText(Lg("waiting for the order book…","بانتظار دفتر الأوامر…"), 12, 22); return; }
    const AX = OFM.AX, DP = OFM.DP, TB = OFM.TB, pw = W - AX - DP, ph = H - TB; if (pw < 40 || ph < 40) return;
    const R = Math.min(OFM.SPAN, S.omR || 0.01), mid = last.mid, lo = mid*(1 - R), hi = mid*(1 + R), win = S.omW || 300000, t1 = nowS(), t0 = t1 - win, snaps = o.snaps;
    const pr = y => hi - (y + .5)/ph*(hi - lo), yOf = v => (hi - v)/(hi - lo)*ph, xOf = t => (t - t0)/win*pw;
    const val = (s, price) => { const i = Math.floor((price - s.base)/s.step); return i >= 0 && i < OFM.NB ? s.arr[i] : 0; };
    const sample = []; for (let yy = 2; yy < ph; yy += 6){ const price = pr(yy); for (let k = Math.max(0, snaps.length - 60); k < snaps.length; k += 5){ const v = val(snaps[k], price); if (v > 0) sample.push(v); } }   // scale from the recent book, 97th percentile (a few giant walls must not turn the rest black)
    sample.sort((a, b) => a - b); const vmax = sample.length ? sample[Math.min(sample.length - 1, Math.floor(sample.length*0.97))] : 1;
    const img = c.createImageData(pw, ph), d = img.data, PAL = OFM.PAL, inv = vmax > 0 ? 1/vmax : 1; let j = 0;
    for (let x = 0; x < pw; x++){ const tc = t0 + (x + .5)/pw*win; while (j + 1 < snaps.length && snaps[j+1].t <= tc) j++; const s = snaps[j], ok = s && s.t <= tc && tc - s.t < 9000;
      for (let y = 0; y < ph; y++){ const o4 = (y*pw + x)*4; let ci = 0; if (ok){ const v = val(s, pr(y)); if (v > 0){ const u = Math.sqrt(Math.min(1, v*inv)); ci = Math.max(1, Math.round(u*255)); } }
        d[o4] = PAL[ci*3]; d[o4+1] = PAL[ci*3+1]; d[o4+2] = PAL[ci*3+2]; d[o4+3] = 255; } }
    c.putImageData(img, 0, 0);
    // axes: price (right of the plot), time (bottom)
    c.fillStyle = "#0b0e11"; c.fillRect(pw, 0, W - pw, H); c.fillRect(0, ph, W, TB); const st = OFM.nice(hi - lo, 8), dec = st >= 1 ? 0 : Math.min(6, Math.ceil(-Math.log10(st))); c.fillStyle = "#9aa4b2"; c.strokeStyle = "rgba(255,255,255,.07)"; c.textBaseline = "middle"; c.textAlign = "left";
    for (let v = Math.ceil(lo/st)*st; v <= hi; v += st){ const y = yOf(v); c.beginPath(); c.moveTo(0, y + .5); c.lineTo(pw, y + .5); c.stroke(); c.fillText(v.toFixed(dec), pw + 4, y); }
    c.textAlign = "center"; c.textBaseline = "top"; for (let k = 0; k <= 4; k++){ const x = pw*k/4, tt = new Date(t0 + win*k/4); c.fillStyle = "#6b7684"; c.fillText(String(tt.getHours()).padStart(2, "0")+":"+String(tt.getMinutes()).padStart(2, "0")+":"+String(tt.getSeconds()).padStart(2, "0"), Math.min(pw - 24, Math.max(24, x)), ph + 4); }
    // mid-price line + last price tag
    c.strokeStyle = "rgba(255,255,255,.9)"; c.lineWidth = 1.2; c.beginPath(); let started = false; snaps.forEach(s => { if (s.t < t0 - 10000) return; const x = xOf(s.t), y = yOf(s.mid); if (y < -50 || y > ph + 50) return; started ? c.lineTo(x, y) : c.moveTo(x, y); started = true; }); c.stroke();
    // trades as bubbles
    if (S.omB !== false){ const tr = o.trades.filter(r => r.t >= t0 && r.p >= lo && r.p <= hi), qs = tr.map(r => r.q).sort((a, b) => a - b), med = qs.length ? qs[Math.floor(qs.length/2)] || 1e-9 : 1;
      tr.forEach(r => { const x = xOf(r.t), y = yOf(r.p), rad = Math.max(2, Math.min(15, 2.2 + 2.6*Math.sqrt(r.q/med))), buy = /buy/i.test(r.side); c.fillStyle = buy ? "rgba(14,203,129,.55)" : "rgba(246,70,93,.55)"; c.strokeStyle = buy ? "#0ecb81" : "#f6465d"; c.lineWidth = 1; c.beginPath(); c.arc(x, y, rad, 0, 6.3); c.fill(); c.stroke(); }); }
    const ym = yOf(mid); c.fillStyle = "#f0b90b"; c.fillRect(pw, ym - 8, AX, 16); c.fillStyle = "#0b0e11"; c.textAlign = "left"; c.textBaseline = "middle"; c.fillText(mid.toFixed(dec + (st < 1 ? 0 : 1)), pw + 4, ym);
    // current book as bars on the right
    const bx0 = pw + AX, bw = DP - 8; c.fillStyle = "#0b0e11"; c.fillRect(bx0 - 2, 0, DP + 2, ph); let pm = 0; const rowsV = []; for (let y = 0; y < ph; y += 2){ const v = val(last, pr(y)); rowsV.push(v); if (v > pm) pm = v; } const pn = vmax*1.5 > 0 ? vmax*1.5 : pm || 1;
    rowsV.forEach((v, k) => { if (!(v > 0)) return; const y = k*2, w = Math.min(bw, v/pn*bw); c.fillStyle = pr(y) < mid ? "rgba(14,203,129,.7)" : "rgba(246,70,93,.7)"; c.fillRect(bx0, y, w, 2); });
    c.fillStyle = "#9aa4b2"; c.textAlign = "left"; c.textBaseline = "top"; c.fillText(Lg("book ±"+last.cov.toFixed(2)+"% · scale 97th pct", "الدفتر ±"+last.cov.toFixed(2)+"% · أقصى لون = 97%"), 6, 5);
    const age = Math.round((nowS() - last.t)/1000); if (age > 8){ c.fillStyle = "#f6465d"; c.fillText("⚠ "+Lg("book last updated "+age+" s ago", "آخر تحديث للدفتر من "+age+" ث"), 6, 19); }
  }
};
