/* EWSHAPE-BEGIN Elliott correction shapes + diagonals as labels (same rules and numbers as modules/elliott_shapes.py; tests/test_ew_shapes_js_parity.py) */
const EWShape = {
  abc(a0, a1, a2, a3){   // zigzag / regular_flat / expanded_flat / running_flat, or null
    const A = a1 - a0; if (A === 0) return null;
    const s = A > 0 ? 1 : -1, lenA = Math.abs(A);
    const bRet = s*(a1 - a2)/lenA, bBeyond = bRet > 1.0, cBeyond = s*(a3 - a1) > 0;
    if (bRet <= 0 || bRet > 1.5) return null;
    if (!bBeyond && bRet >= 0.382 && bRet < 0.9 && cBeyond) return "zigzag";
    if (bRet >= 0.9 && bRet <= 1.05 && Math.abs(a3 - a1)/lenA <= 0.10) return "regular_flat";
    if (bBeyond && cBeyond) return "expanded_flat";
    if (bBeyond && !cBeyond) return "running_flat";
    return null;
  },
  impulse(p0, p1, p2, p3, p4, p5){   // impulse / ending_diagonal, or null
    const s = p1 > p0 ? 1 : -1;
    const w1 = s*(p1 - p0), w3 = s*(p3 - p2), w5 = s*(p5 - p4);
    if (Math.min(w1, w3, w5) <= 0) return null;
    if (s*(p2 - p0) <= 0 || s*(p3 - p1) <= 0 || s*(p5 - p3) <= 0) return null;
    const overlap4 = s*(p4 - p1) <= 0;
    if (!overlap4 && !(w3 < w1 && w3 < w5)) return "impulse";
    if (overlap4 && w5 < w3) return "ending_diagonal";
    return null;
  },
  tri(p0, p1, p2, p3, p4, p5){   // contracting / expanding, or null (leg lengths only)
    const legs = [Math.abs(p1-p0), Math.abs(p2-p1), Math.abs(p3-p2), Math.abs(p4-p3), Math.abs(p5-p4)];
    if (Math.min(...legs) <= 0) return null;
    if ([0,1,2,3].every(k => legs[k+1] <= legs[k]*0.95)) return "contracting";
    if ([0,1,2,3].every(k => legs[k+1] >= legs[k]*1.05)) return "expanding";
    return null;
  },
  wxy(p0, p1, p2, p3, p4, p5, p6, p7){   // double_zigzag / double_three / double_combo, or null
    const s = p1 > p0 ? 1 : -1, wLen = Math.abs(p3 - p0);
    if (wLen === 0) return null;
    const xRet = Math.abs(p4 - p3)/wLen;
    if (s*(p4 - p3) >= 0 || s*(p7 - p4) <= 0) return null;
    if (xRet < 0.382 || xRet > 1.0) return null;
    if (s*(p3 - p0) <= 0) return null;
    const w = this.abc(p0, p1, p2, p3), y = this.abc(p4, p5, p6, p7);
    if (!w || !y) return null;
    const wz = w === "zigzag", yz = y === "zigzag";
    if (wz && yz) return "double_zigzag";
    if (!wz && !yz) return "double_three";
    return "double_combo";
  },
  triple(p0, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11){   // triple_zigzag / triple_three / triple_combo, or null (same rules as triple_shape)
    const s = p1 > p0 ? 1 : -1, wL = Math.abs(p3 - p0), yL = Math.abs(p7 - p4);
    if (wL === 0 || yL === 0) return null;
    const x1 = Math.abs(p4 - p3)/wL, x2 = Math.abs(p8 - p7)/yL;
    if (x1 < 0.382 || x1 > 1.0 || x2 < 0.382 || x2 > 1.0) return null;
    if (s*(p4 - p3) >= 0 || s*(p8 - p7) >= 0) return null;
    if (s*(p7 - p4) <= 0 || s*(p11 - p8) <= 0) return null;
    const w = this.abc(p0, p1, p2, p3), y = this.abc(p4, p5, p6, p7), z = this.abc(p8, p9, p10, p11);
    if (!w || !y || !z) return null;
    const k = [w === "zigzag", y === "zigzag", z === "zigzag"];
    if (k.every(Boolean)) return "triple_zigzag";
    if (!k.some(Boolean)) return "triple_three";
    return "triple_combo";
  },
  tail(p){   // same order as Python classify_tail
    const n = p.length;
    if (n >= 12){ const t = this.triple(...p.slice(n-12)); if (t) return t; }
    if (n >= 8){ const w = this.wxy(...p.slice(n-8)); if (w) return w; }
    if (n >= 6){ const q = p.slice(n-6); const t = this.tri(...q) || this.impulse(...q); if (t) return t; }
    if (n >= 4){ const a = this.abc(...p.slice(n-4)); if (a) return a; }
    return null;
  }
};
/* EWSHAPE-END */
Object.assign(CandleChart.prototype, {
  ewShapeLabel(){   // newest shape label from the zigzag pivots (null when none)
    const z = harmZigzag(this.data, zzDev(this.data, 2.5, 0.001, 0.025), 3);
    const name = EWShape.tail(z.map(q => q.p)); if (!name) return null;
    const T = {zigzag:["zigzag (A-B-C)","زيجزاج (A-B-C)"], regular_flat:["regular flat","فلات عادي"], expanded_flat:["expanded flat","فلات ممتد"],
      running_flat:["running flat","فلات جاري"], impulse:["impulse 1-5","دافعة 1-5"], ending_diagonal:["ending diagonal","دياجونال نهائي"],
      contracting:["contracting triangle","مثلث متقارب"], expanding:["expanding triangle","مثلث متسع"],
      double_zigzag:["double zigzag (W-X-Y)","زيجزاج مزدوج (W-X-Y)"], double_three:["double three (W-X-Y)","ثلاثي مزدوج (W-X-Y)"],
      double_combo:["combo (W-X-Y)","مركب (W-X-Y)"], triple_zigzag:["triple zigzag (W-X-Y-X-Z)","زيجزاج ثلاثي (W-X-Y-X-Z)"],
      triple_three:["triple three (W-X-Y-X-Z)","ثلاثي ثلاثي (W-X-Y-X-Z)"], triple_combo:["triple combo (W-X-Y-X-Z)","ثلاثي مركب (W-X-Y-X-Z)"]}[name];
    return T ? Lg("Shape: "+T[0], "الشكل: "+T[1]) : null;
  }
});

Object.assign(CandleChart.prototype, {
  paintEWfib(c, py, w){   // Elliott Fibonacci zone of the newest full impulse: 0.5 / 0.618 / 0.764 / 0.854 from the wave-5 end over the wave-1 range (our measurement)
    if (!w || !w.pts || w.pts.length < 6) return;
    const p0 = w.pts[0].p, p1 = w.pts[1].p, p5 = w.pts[5], rng = p1 - p0; if (!rng) return;
    const x0 = this.x(p5.i), PR = this.PR, col = "#b57cff";
    c.save(); c.setLineDash([3,3]); c.strokeStyle = col; c.fillStyle = col; c.globalAlpha = .75; c.font = "10px sans-serif"; c.textAlign = "left"; c.textBaseline = "middle";
    for (const lvl of [0.5, 0.618, 0.764, 0.854]){
      const pr = p5.p - lvl*rng, y = py(pr); c.beginPath(); c.moveTo(x0, y); c.lineTo(PR, y); c.stroke();
      c.fillText(lvl.toFixed(3), Math.min(PR - 34, x0 + 4), y - 7);
    }
    c.restore();
  },
  paintGannOffset(c, py, i0, i1, PB){   // Gann offset lines (our definition): 15 / 45 / 60 deg from the last swing axis, 1 unit = ATR per bar
    const z = harmZigzag(this.data, zzDev(this.data, 2.5, 0.001, 0.025), 3); if (z.length < 2) return;
    const a = z[z.length-2], b = z[z.length-1]; const bars = b.i - a.i; if (!bars) return;
    const slope = (b.p - a.p)/bars, dir = slope >= 0 ? 1 : -1;
    const d = this.data.slice(Math.max(0, this.data.length - 14)); const unit = d.reduce((s, r) => s + (r.h - r.l), 0)/Math.max(1, d.length); if (!unit) return;
    const base = Math.atan2(Math.abs(slope), unit), PR = this.PR, col = "#f7b500";
    c.save(); c.setLineDash([5,4]); c.strokeStyle = col; c.globalAlpha = .7; c.lineWidth = 1; c.font = "10px sans-serif"; c.fillStyle = col;
    for (const off of [15, 45, 60]){
      const ang = base + off*Math.PI/180; if (ang >= Math.PI/2) continue;
      const x0 = this.x(b.i), y0 = py(b.p), bwPx = Math.max(1e-9, this.bw), barsToEdge = (PR - x0)/bwPx;
      const pEnd = b.p + dir*Math.tan(ang)*unit*barsToEdge;   // price at the right edge, same slope in scaled units
      c.beginPath(); c.moveTo(x0, y0); c.lineTo(PR, py(pEnd)); c.stroke();
      c.fillText(off+"°", Math.min(PR - 28, x0 + 6), y0 - 6);
    }
    c.restore();
  }
});
/* EWEXPL-BEGIN plain-language Elliott explainer: diagonal trendlines, wave-by-wave caption (labels only) */
const EW_WAVE_TEXT = {
  "0": ["start of the move", "بداية الحركة"],
  "1": ["wave 1: first push, often the smallest", "موجة 1: أول دفعة، غالباً الأصغر"],
  "2": ["wave 2: pullback, never goes past the start of wave 1", "موجة 2: تصحيح، ما تعديش بداية موجة 1"],
  "3": ["wave 3: usually the strongest, never the shortest", "موجة 3: غالباً الأقوى، ومش الأقصر"],
  "4": ["wave 4: pullback, stays out of wave 1's price area", "موجة 4: تصحيح، ما تدخلش منطقة موجة 1"],
  "5": ["wave 5: last push, often shows weakening momentum", "موجة 5: آخر دفعة، غالباً الزخم بيضعف"]
};
Object.assign(CandleChart.prototype, {
  paintEWdiag(c, py, w){   // ending diagonal: draw its two converging lines (highs 1-3-5, lows 0-2-4) and say what it is
    if (!w || !w.pts || w.pts.length < 6) return;
    const P = w.pts.map(q => ({x: this.x(q.i), y: py(q.p)})), shape = EWShape.impulse(...w.pts.map(q => q.p));
    if (shape !== "ending_diagonal") return;
    const PR = this.PR, col = w.up ? "#0ecb81" : "#f6465d";
    const line = (a, b) => { const dx = b.x - a.x || 1e-9, m = (b.y - a.y)/dx; c.beginPath(); c.moveTo(a.x, a.y); c.lineTo(PR, a.y + m*(PR - a.x)); c.stroke(); };
    c.save(); c.setLineDash([6,4]); c.strokeStyle = col; c.globalAlpha = .8; c.lineWidth = 1;
    line(P[1], P[3]); line(P[3], P[5]);   // upper trendline through the highs 1, 3, 5
    line(P[0], P[2]); line(P[2], P[4]);   // lower trendline through the lows 0, 2, 4
    c.restore();
    this.indNote(c, 5, Lg("Ending diagonal: lines converge, wave 5 is inside the wedge", "دياجونال نهائي: الخطوط بتتقارب، موجة 5 جوه الوتد"));
  },
  ewWaveCaption(c, w, n){   // one line per wave: what it is and what to expect (teaching text, not a forecast)
    if (!w || !w.pts || w.pts.length < 2) return;
    const k = String(w.pts.length - 1);
    const t = EW_WAVE_TEXT[k]; if (!t) return;
    this.indNote(c, n, Lg("Now: ", "دلوقتي: ") + Lg(t[0], t[1]));
  }
});
/* EWEXPL-END */
/* EWMTF-BEGIN compact multi-timeframe Elliott status, top-right corner (labels only; reuses ewCount / ewForming / EWShape on each frame's candles) */
const EW_MTF_FRAMES = ["1M","1W","1D","4H","1H","15m","5m","1m"];
Object.assign(CandleChart.prototype, {
  ewFrameSummary(rows, tf){   // one frame -> {tf, state, shape, next} (state text only; no forecast)
    const o = {data: rows, tf, ewForming: CandleChart.prototype.ewForming};
    const list = CandleChart.prototype.ewCount.call(o), f = o._ewf;
    const z = harmZigzag(rows, zzDev(rows, 2.5, 0.001, 0.025), 3);
    const shape = EWShape.tail(z.map(q => q.p));
    let state = "—", next = null;
    if (list.length){
      const top = list[0];
      if (top.pts.length >= 6 && top.abc.length >= 3) { state = Lg("impulse done, ABC done", "دافعة خلصت، والـ ABC خلص"); next = Lg("new impulse", "دافعة جديدة"); }
      else if (top.pts.length >= 6) { state = Lg("impulse 1-5 done", "دافعة 1-5 خلصت"); next = Lg("ABC next", "ABC جاي"); }
      else if (top.abc.length) { state = Lg("ABC forming", "ABC بيتكون"); next = Lg("ABC C next", "الموجة C جاية"); }
    }
    if (f){ state = Lg("forming, wave ", "بتتكون، موجة ") + f.next; next = Lg("wave ", "موجة ") + f.next; }
    return {tf, state, shape: shape ? (EWShape_AR_OR_EN(shape)) : "—", next: next || "—"};
  },
  ewMTFBox(c){   // top-right corner: one line per frame, newest frames first; cached 5 min per frame; drawn only when Elliott is on
    if (!this.sym) return;
    const store = this._ewMtf || (this._ewMtf = {}), rows = [];
    for (const H of EW_MTF_FRAMES){
      const k = this.sym+"|"+H, e = store[k];
      if (!e || (!e.busy && Date.now() - e.t > 300000)){
        store[k] = {t: Date.now(), v: e ? e.v : null, busy: true};
        candlesTf(this.sym, H, true, 200).then(r => { store[k] = {t: Date.now(), v: r && r.length > 30 ? this.ewFrameSummary(r, H) : null, busy: false}; this.draw(); })
          .catch(() => { store[k] = {t: Date.now(), v: null, busy: false}; });
      }
      if (store[k] && store[k].v) rows.push(store[k].v);
    }
    if (!rows.length) return;
    const PR = this.PR, lh = 12, W = 230, H = 16 + rows.length*lh;
    c.save(); c.globalAlpha = .85; c.fillStyle = "#0b0e11"; c.fillRect(PR - W - 6, 4, W, H); c.globalAlpha = 1;
    c.font = "bold 10px sans-serif"; c.fillStyle = "#f0b90b"; c.textAlign = "left"; c.textBaseline = "top";
    c.fillText(Lg("Elliott by frame", "إليوت حسب الفريم"), PR - W, 6);
    c.font = "9px ui-monospace,Menlo,Consolas,monospace"; c.fillStyle = "#c9d1d9";
    rows.forEach((r, i) => c.fillText(r.tf + "  " + r.state + "  ·  " + r.shape + "  ·  → " + r.next, PR - W, 20 + i*lh));
    c.restore();
  }
});
function EWShape_AR_OR_EN(name){ const AR = {zigzag:"زيجزاج ABC", regular_flat:"فلات عادي", expanded_flat:"فلات ممتد", running_flat:"فلات جاري", impulse:"دافعة 1-5", ending_diagonal:"دياجونال نهائي", contracting:"مثلث متقارب", expanding:"مثلث متسع", double_zigzag:"زيجزاج مزدوج", double_three:"ثلاثي مزدوج", double_combo:"مركب W-X-Y", triple_zigzag:"زيجزاج ثلاثي", triple_three:"ثلاثي ثلاثي", triple_combo:"ثلاثي مركب"}; return Lg(name.replace(/_/g," "), AR[name] || name); }
/* EWMTF-END */
