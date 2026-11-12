/* V7 live indicators: the exact settings of research/cfx/cfx_osc_combo.py (Stoch 5,3,3 Low/High SMA, RSI 14 Wilder, MACD 12,26 (signal period 1), SMA 77 / 144)
   and the research rule "variant B". Pure functions, no DOM: tested against the Python reference in tests/test_v7_live.py. Research only, not an edge. */
(function (root) {
  const fin = Number.isFinite;
  function rollMean(a, n) { return a.map((_, i) => { if (i < n - 1) return NaN; let s = 0; for (let j = i - n + 1; j <= i; j++) { if (!fin(a[j])) return NaN; s += a[j]; } return s / n; }); }
  function rollMax(a, n) { return a.map((_, i) => { if (i < n - 1) return NaN; let m = -Infinity; for (let j = i - n + 1; j <= i; j++) { if (!fin(a[j])) return NaN; if (a[j] > m) m = a[j]; } return m; }); }
  function rollMin(a, n) { return a.map((_, i) => { if (i < n - 1) return NaN; let m = Infinity; for (let j = i - n + 1; j <= i; j++) { if (!fin(a[j])) return NaN; if (a[j] < m) m = a[j]; } return m; }); }
  function ema(a, n) { const k = 2 / (n + 1), o = new Array(a.length).fill(NaN); let p = NaN; for (let i = 0; i < a.length; i++) { p = i === 0 ? a[0] : a[i] * k + p * (1 - k); o[i] = p; } return o; }
  function stochKD(h, l, c, kp, dp, slow) {
    const ll = rollMin(l, kp), hh = rollMax(h, kp);
    const raw = c.map((v, i) => { const r = hh[i] - ll[i]; return r === 0 || !fin(r) ? NaN : 100 * (v - ll[i]) / r; });
    const K = rollMean(raw, slow); return { k: K, d: rollMean(K, dp) };
  }
  function rsiWilder(c, n) {
    const o = new Array(c.length).fill(NaN), a = 1 / n; let g = NaN, l = NaN;
    for (let i = 1; i < c.length; i++) {
      const d = c[i] - c[i - 1], gi = d > 0 ? d : 0, li = d < 0 ? -d : 0;
      if (i === 1) { g = gi; l = li; } else { g = gi * a + g * (1 - a); l = li * a + l * (1 - a); }
      if (i >= n) { let v = l === 0 ? 100 : 100 - 100 / (1 + g / l); if (g === 0) v = 0; o[i] = v; }
    }
    return o;
  }
  function compute(bars) {
    const h = bars.map(b => b.high), l = bars.map(b => b.low), c = bars.map(b => b.close);
    const st = stochKD(h, l, c, 5, 3, 3), e12 = ema(c, 12), e26 = ema(c, 26);
    return { k: st.k, d: st.d, rsi: rsiWilder(c, 14), macd: e12.map((v, i) => v - e26[i]), sma77: rollMean(c, 77), sma144: rollMean(c, 144) };
  }
  /* variant B: %K crosses %D after %K touched <=15 (>=85) within the last 3 bars, RSI turning the same way, MACD main line moving the same way. */
  function signalsB(ind, last) {
    const { k, d, rsi, macd } = ind, out = [], end = Math.min(last, k.length - 1);
    for (let i = 2; i <= end; i++) {
      if (![k[i], k[i - 1], d[i], d[i - 1], rsi[i], rsi[i - 1], macd[i], macd[i - 1]].every(fin)) continue;
      const a = Math.max(0, i - 3); let os = false, ob = false;
      for (let j = a; j <= i; j++) { if (fin(k[j]) && k[j] <= 15) os = true; if (fin(k[j]) && k[j] >= 85) ob = true; }
      const up = k[i - 1] <= d[i - 1] && k[i] > d[i], dn = k[i - 1] >= d[i - 1] && k[i] < d[i];
      if (up && os && rsi[i] > rsi[i - 1] && macd[i] > macd[i - 1]) out.push({ i, side: 'buy' });
      else if (dn && ob && rsi[i] < rsi[i - 1] && macd[i] < macd[i - 1]) out.push({ i, side: 'sell' });
    }
    return out;
  }
  /* ---- Day plan (rule-based "Director"): top-down bias, location, session, momentum -> WAIT / WATCH, with what agrees, what conflicts, what we wait for.
     It never prints an entry, stop or target: research context only. Risk shown is the platform policy (0.25 % base, R:R >= 2). ---- */
  function nyMinutes(ms) { const p = new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', hour: '2-digit', minute: '2-digit', hour12: false }).formatToParts(new Date(ms)); return (+p.find(x => x.type === 'hour').value % 24) * 60 + (+p.find(x => x.type === 'minute').value); }
  function sessionNow(ms) {
    const t = nyMinutes(ms), inW = (a, b) => (a < b ? (t >= a * 60 && t < b * 60) : (t >= a * 60 || t < b * 60));
    const kz = inW(2, 5) ? 'London kill zone' : inW(7, 10) ? 'NY AM kill zone' : inW(20, 24) ? 'Asia kill zone' : '';
    return { asia: inW(19, 2), london: inW(2, 9), ny: inW(8, 17), kz, nyMinutes: t };
  }
  function closedBars(b) { return b.length && b[b.length - 1].closed === false ? b.slice(0, -1) : b; }
  function trendOf(c) {
    const m20 = rollMean(c, 20), m50 = rollMean(c, 50), n = c.length - 1;
    if (n < 49 || !fin(m20[n]) || !fin(m50[n])) return null;
    return c[n] > m20[n] && m20[n] > m50[n] ? 'UP' : c[n] < m20[n] && m20[n] < m50[n] ? 'DOWN' : 'RANGE';
  }
  function atr14(b) { const n = b.length; if (n < 15) return NaN; let s = 0; for (let i = n - 14; i < n; i++) s += Math.max(b[i].high - b[i].low, Math.abs(b[i].high - b[i - 1].close), Math.abs(b[i].low - b[i - 1].close)); return s / 14; }
  function dayPlan(f, nowMs) {
    const ses = sessionNow(nowMs), agree = [], conflict = [], waiting = [], C = {};
    ['d1', 'h4', 'h1', 'm15'].forEach(k => { C[k] = closedBars(f[k] || []); });
    const T = {}; ['d1', 'h4', 'h1', 'm15'].forEach(k => { T[k] = trendOf(C[k].map(b => b.close)); });
    const out = { state: 'WAIT', dir: null, trends: T, session: ses, agree, conflict, waiting, levels: null, risk: { basePct: 0.25, minRR: 2 } };
    if (!T.d1 || !T.h4) { out.state = 'NO DATA'; conflict.push('not enough daily / 4H candles to read the bias'); return out; }
    const pd = C.d1[C.d1.length - 1], px = (f.m15 && f.m15.length ? f.m15[f.m15.length - 1].close : C.h1[C.h1.length - 1].close), rng = pd.high - pd.low, pos = rng > 0 ? (px - pd.low) / rng : NaN, a = atr14(C.m15);
    out.levels = { pdh: pd.high, pdl: pd.low, px, pos: fin(pos) ? pos : null, atr15: fin(a) ? a : null };
    if (T.d1 !== 'RANGE' && T.h4 !== 'RANGE' && T.d1 !== T.h4) { out.state = 'CONFLICT'; conflict.push('1D is ' + T.d1 + ' but 4H is ' + T.h4); return out; }
    const dir = T.d1 !== 'RANGE' ? T.d1 : T.h4 !== 'RANGE' ? T.h4 : null;
    if (!dir) { out.state = 'WAIT'; waiting.push('1D and 4H are both ranging: no directional bias'); return out; }
    out.dir = dir; const up = dir === 'UP';
    agree.push('1D ' + T.d1 + (T.h4 === dir ? ' and 4H ' + T.h4 + ' agree' : ' (4H ranging)'));
    if (T.h1 === dir) agree.push('1H ' + T.h1 + ' agrees'); else if (T.h1 && T.h1 !== 'RANGE') conflict.push('1H is ' + T.h1 + ' against the bias'); else waiting.push('1H not trending with the bias yet');
    if (fin(pos)) { const fits = up ? pos < 0.5 : pos > 0.5; if (fits) agree.push('price in ' + (up ? 'discount' : 'premium') + ' of the previous daily range (' + Math.round(pos * 100) + '%)'); else waiting.push('price in ' + (up ? 'premium' : 'discount') + ' of the previous daily range (' + Math.round(pos * 100) + '%): wait for a pullback'); }
    const ind = compute(C.m15), n = C.m15.length - 1, k = ind.k, d = ind.d, w = k.slice(-6).filter(fin);
    if (n >= 20 && w.length) { const turn = up ? (k[n] >= d[n] && Math.min(...w) <= 20) : (k[n] <= d[n] && Math.max(...w) >= 80); if (turn) agree.push('15m Stoch turning ' + (up ? 'up from oversold' : 'down from overbought')); else waiting.push('15m Stoch has not turned ' + (up ? 'up from <= 20' : 'down from >= 80') + ' yet'); }
    if (ses.kz) agree.push('inside the ' + ses.kz); else waiting.push('outside a kill zone (London 02-05, NY AM 07-10, Asia 20-24, New York time)');
    out.state = (T.h1 === dir && agree.length >= 4) ? 'WATCH ' + (up ? 'LONG' : 'SHORT') : 'WAIT';
    return out;
  }
  const api = { rollMean, ema, stochKD, rsiWilder, compute, signalsB, sessionNow, trendOf, dayPlan };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.V7IND = api;
})(typeof window !== 'undefined' ? window : globalThis);
