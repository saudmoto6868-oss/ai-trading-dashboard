/* V7 live structure tools, computed in the browser from the candles on screen. Definitions (CFX settings image: swing length 3, EQ tolerance 0.10 ATR, FVG min 0.30 ATR, max age 30):
   swing = fractal of length 3; EQH/EQL = two swings within 0.10 ATR; FVG = 3-bar gap >= 0.30 ATR still unfilled, <= 30 bars old; BOS / CHoCH = a CLOSE through the last
   swing (same direction as the running trend = BOS, against it = CHoCH); premium / discount = 50 % of the last swing high-low; OTE = 0.62-0.79 retracement of the last impulse;
   sessions = New York clock windows (Asia 19-02, London 02-09, NY 08-17). Pure functions; tested against an independent Python implementation (tests/test_v7_struct.py).
   Research display only: none of this is a signal. */
(function (root) {
  const fin = Number.isFinite;
  function swings(b, L) {
    L = L || 3; const H = [], Lo = [];
    for (let i = L; i < b.length - L; i++) {
      let hi = true, lo = true;
      for (let j = 1; j <= L; j++) {
        if (!(b[i].high > b[i - j].high) || !(b[i].high >= b[i + j].high)) hi = false;
        if (!(b[i].low < b[i - j].low) || !(b[i].low <= b[i + j].low)) lo = false;
      }
      if (hi) H.push({ i, p: b[i].high, conf: i + L }); if (lo) Lo.push({ i, p: b[i].low, conf: i + L });
    }
    return { H, L: Lo };
  }
  function atr14(b) { const n = b.length; if (n < 15) return NaN; let s = 0; for (let i = n - 14; i < n; i++) s += Math.max(b[i].high - b[i].low, Math.abs(b[i].high - b[i - 1].close), Math.abs(b[i].low - b[i - 1].close)); return s / 14; }
  function equal(sw, atr, key, maxBack, n) {
    const out = [], tol = 0.10 * atr; if (!fin(tol)) return out;
    for (let a = 0; a < sw.length; a++) for (let c = a + 1; c < sw.length; c++) if (sw[a].i >= n - maxBack && sw[c].i >= n - maxBack && Math.abs(sw[a].p - sw[c].p) <= tol) out.push({ type: key, i1: sw[a].i, i2: sw[c].i, p: (sw[a].p + sw[c].p) / 2 });
    return out.slice(-6);
  }
  function fvgs(b, atr, maxAge) {
    const out = [], n = b.length, min = 0.30 * atr; if (!fin(min)) return out;
    for (let i = 2; i < n; i++) {
      if (n - 1 - i > (maxAge || 30)) continue;
      let z = null;
      if (b[i].low - b[i - 2].high >= min) z = { dir: 'bull', i0: i - 2, lo: b[i - 2].high, hi: b[i].low };
      else if (b[i - 2].low - b[i].high >= min) z = { dir: 'bear', i0: i - 2, lo: b[i].high, hi: b[i - 2].low };
      if (!z) continue;
      let filled = false; for (let j = i + 1; j < n; j++) { if (z.dir === 'bull' ? b[j].low <= z.lo : b[j].high >= z.hi) { filled = true; break; } }
      if (!filled) out.push(z);
    }
    return out;
  }
  function structure(b, sw) {
    const ev = []; let trend = null, sh = null, sl = null, hi = 0, li = 0;
    const H = sw.H.slice().sort((x, y) => x.conf - y.conf), Lo = sw.L.slice().sort((x, y) => x.conf - y.conf);
    for (let i = 0; i < b.length; i++) {
      while (hi < H.length && H[hi].conf <= i) { sh = H[hi]; hi++; }
      while (li < Lo.length && Lo[li].conf <= i) { sl = Lo[li]; li++; }
      if (sh && b[i].close > sh.p) { ev.push({ i, type: trend === 'down' ? 'CHoCH' : 'BOS', dir: 'up', level: sh.p, from: sh.i }); trend = 'up'; sh = null; }
      else if (sl && b[i].close < sl.p) { ev.push({ i, type: trend === 'up' ? 'CHoCH' : 'BOS', dir: 'down', level: sl.p, from: sl.i }); trend = 'down'; sl = null; }
    }
    return { events: ev, trend };
  }
  function premDisc(sw) {
    const h = sw.H[sw.H.length - 1], l = sw.L[sw.L.length - 1]; if (!h || !l) return null;
    return { hi: h.p, lo: l.p, eq: (h.p + l.p) / 2, iFrom: Math.min(h.i, l.i) };
  }
  function ote(sw) {
    const h = sw.H[sw.H.length - 1], l = sw.L[sw.L.length - 1]; if (!h || !l) return null;
    const r = h.p - l.p; if (!(r > 0)) return null;
    if (h.i > l.i) return { dir: 'up', end: h.i, p62: h.p - 0.62 * r, p705: h.p - 0.705 * r, p79: h.p - 0.79 * r, hi: h.p, lo: l.p };   // impulse up, buy-side OTE
    return { dir: 'down', end: l.i, p62: l.p + 0.62 * r, p705: l.p + 0.705 * r, p79: l.p + 0.79 * r, hi: h.p, lo: l.p };
  }
  function nyMin(ms) { const p = new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', hour: '2-digit', minute: '2-digit', hour12: false }).formatToParts(new Date(ms)); return (+p.find(x => x.type === 'hour').value % 24) * 60 + (+p.find(x => x.type === 'minute').value); }
  function sessions(b) {
    const W = [['Asia', 19, 2], ['London', 2, 9], ['NY', 8, 17]], out = [];
    W.forEach(([name, a, z]) => {
      let run = null;
      b.forEach((x, i) => {
        const t = nyMin(x.time * 1000), inside = a < z ? (t >= a * 60 && t < z * 60) : (t >= a * 60 || t < z * 60);
        if (inside) { if (!run) run = { name, i0: i, i1: i, hi: x.high, lo: x.low }; else { run.i1 = i; run.hi = Math.max(run.hi, x.high); run.lo = Math.min(run.lo, x.low); } }
        else if (run) { out.push(run); run = null; }
      });
      if (run) out.push(run);
    });
    return out.slice(-9);
  }
  function nySessionDay(sec) {
    const p = new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', hour12: false }).formatToParts(new Date(sec * 1000));
    const v = k => +(p.find(x => x.type === k) || {}).value;
    const d = new Date(Date.UTC(v('year'), v('month') - 1, v('day') + (v('hour') >= 18 ? 1 : 0)));
    return d.toISOString().slice(0, 10);
  }
  function prevDay(b) {
    if (!b.length) return null;
    const today = nySessionDay(b[b.length - 1].time); let d = null, hi = -Infinity, lo = Infinity;
    for (let i = b.length - 1; i >= 0; i--) {
      const k = nySessionDay(b[i].time); if (k === today) continue;
      if (d === null) d = k; if (k !== d) break;
      hi = Math.max(hi, b[i].high); lo = Math.min(lo, b[i].low);
    }
    return d === null ? null : { hi, lo, sessionDate: d };
  }
  function compute(b) {
    const n = b.length, sw = swings(b, 3), atr = atr14(b), st = structure(b, sw);
    return { sw, atr, eqh: equal(sw.H, atr, 'EQH', 150, n), eql: equal(sw.L, atr, 'EQL', 150, n), fvg: fvgs(b, atr, 30), events: st.events.slice(-8), trend: st.trend, pd: premDisc(sw), ote: ote(sw), sessions: sessions(b), prevDay: prevDay(b) };
  }
  const api = { swings, atr14, equal, fvgs, structure, premDisc, ote, sessions, prevDay, compute };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.V7STRUCT = api;
})(typeof window !== 'undefined' ? window : globalThis);
