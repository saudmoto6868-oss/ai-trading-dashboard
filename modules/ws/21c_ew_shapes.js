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
