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
  const api = { rollMean, ema, stochKD, rsiWilder, compute, signalsB };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.V7IND = api;
})(typeof window !== 'undefined' ? window : globalThis);
