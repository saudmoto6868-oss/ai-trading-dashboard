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
  tail(p){   // same order as Python classify_tail
    const n = p.length;
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
      double_combo:["combo (W-X-Y)","مركب (W-X-Y)"]}[name];
    return T ? Lg("Shape: "+T[0], "الشكل: "+T[1]) : null;
  }
});
