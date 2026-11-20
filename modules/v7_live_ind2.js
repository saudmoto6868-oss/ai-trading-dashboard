/* V7 standard indicators (pure functions, browser + node), checked against an independent Python implementation (tests/test_v7_ind2.py).
   All arrays align with the candle array; NaN where the indicator is not defined yet. Standard textbook definitions:
   sma, ema (seed = SMA of the first n closes, alpha 2/(n+1)), bollinger (SMA +- k population sd), donchian (n-bar HH / LL incl. the current bar), atr (Wilder, seed = mean TR of bars 1..n),
   keltner (EMA +- m * ATR), supertrend (ATR bands with carry-over, flips on a close beyond the active band), ichimoku (9/26/52, cloud shifted 26 bars forward),
   adx (Wilder, +DI / -DI / ADX), obv, cci (typical price, mean deviation, 0.015), williamsR, volume. Display only. */
(function (root) {
  const N = NaN, fin = Number.isFinite, arr = n => new Array(n).fill(N);
  function sma(v, n) { const o = arr(v.length); let s = 0; for (let i = 0; i < v.length; i++) { s += v[i]; if (i >= n) s -= v[i - n]; if (i >= n - 1) o[i] = s / n; } return o; }
  function ema(v, n) { const o = arr(v.length); if (v.length < n) return o; let e = 0; for (let i = 0; i < n; i++) e += v[i]; e /= n; o[n - 1] = e; const a = 2 / (n + 1); for (let i = n; i < v.length; i++) { e = a * v[i] + (1 - a) * e; o[i] = e; } return o; }
  function bollinger(c, n, k) { const m = sma(c, n), up = arr(c.length), lo = arr(c.length); for (let i = n - 1; i < c.length; i++) { let s = 0; for (let j = i - n + 1; j <= i; j++) s += (c[j] - m[i]) * (c[j] - m[i]); const sd = Math.sqrt(s / n); up[i] = m[i] + k * sd; lo[i] = m[i] - k * sd; } return { mid: m, up, lo }; }
  function donchian(h, l, n) { const up = arr(h.length), lo = arr(h.length), mid = arr(h.length); for (let i = n - 1; i < h.length; i++) { let a = -Infinity, b = Infinity; for (let j = i - n + 1; j <= i; j++) { a = Math.max(a, h[j]); b = Math.min(b, l[j]); } up[i] = a; lo[i] = b; mid[i] = (a + b) / 2; } return { up, lo, mid }; }
  function trueRange(h, l, c) { return h.map((x, i) => i === 0 ? x - l[i] : Math.max(x - l[i], Math.abs(x - c[i - 1]), Math.abs(l[i] - c[i - 1]))); }
  function atr(h, l, c, n) { const tr = trueRange(h, l, c), o = arr(h.length); if (h.length <= n) return o; let a = 0; for (let i = 1; i <= n; i++) a += tr[i]; a /= n; o[n] = a; for (let i = n + 1; i < h.length; i++) { a = (a * (n - 1) + tr[i]) / n; o[i] = a; } return o; }
  function keltner(h, l, c, n, an, m) { const mid = ema(c, n), a = atr(h, l, c, an); return { mid, up: mid.map((x, i) => x + m * a[i]), lo: mid.map((x, i) => x - m * a[i]) }; }
  function supertrend(h, l, c, n, m) {
    const a = atr(h, l, c, n), line = arr(h.length), dir = arr(h.length); let fu = N, fl = N, tr = 1;
    for (let i = 0; i < h.length; i++) {
      if (!fin(a[i])) continue; const hl = (h[i] + l[i]) / 2, bu = hl + m * a[i], bl = hl - m * a[i];
      if (!fin(fu)) { fu = bu; fl = bl; tr = 1; } else { const pu = fu, pl = fl; fu = (bu < pu || c[i - 1] > pu) ? bu : pu; fl = (bl > pl || c[i - 1] < pl) ? bl : pl; if (tr === 1 && c[i] < fl) tr = -1; else if (tr === -1 && c[i] > fu) tr = 1; }
      line[i] = tr === 1 ? fl : fu; dir[i] = tr;
    }
    return { line, dir };
  }
  function ichimoku(h, l, c) {
    const mid = n => { const o = arr(h.length); for (let i = n - 1; i < h.length; i++) { let a = -Infinity, b = Infinity; for (let j = i - n + 1; j <= i; j++) { a = Math.max(a, h[j]); b = Math.min(b, l[j]); } o[i] = (a + b) / 2; } return o; };
    const t = mid(9), k = mid(26), b52 = mid(52), n = h.length, sa = arr(n + 26), sb = arr(n + 26);
    for (let i = 0; i < n; i++) { if (fin(t[i]) && fin(k[i])) sa[i + 26] = (t[i] + k[i]) / 2; if (fin(b52[i])) sb[i + 26] = b52[i]; }
    return { tenkan: t, kijun: k, spanA: sa, spanB: sb };
  }
  function adx(h, l, c, n) {
    const L = h.length, pdi = arr(L), mdi = arr(L), ax = arr(L); if (L <= 2 * n) return { adx: ax, pdi, mdi };
    const tr = trueRange(h, l, c), pdm = arr(L).fill(0), mdm = arr(L).fill(0);
    for (let i = 1; i < L; i++) { const up = h[i] - h[i - 1], dn = l[i - 1] - l[i]; pdm[i] = up > dn && up > 0 ? up : 0; mdm[i] = dn > up && dn > 0 ? dn : 0; }
    let st = 0, sp = 0, sm = 0; for (let i = 1; i <= n; i++) { st += tr[i]; sp += pdm[i]; sm += mdm[i]; }
    const dx = arr(L);
    for (let i = n; i < L; i++) { if (i > n) { st = st - st / n + tr[i]; sp = sp - sp / n + pdm[i]; sm = sm - sm / n + mdm[i]; } pdi[i] = 100 * sp / st; mdi[i] = 100 * sm / st; const s = pdi[i] + mdi[i]; dx[i] = s === 0 ? 0 : 100 * Math.abs(pdi[i] - mdi[i]) / s; }
    let a = 0; for (let i = n; i < 2 * n; i++) a += dx[i]; a /= n; ax[2 * n - 1] = a; for (let i = 2 * n; i < L; i++) { a = (a * (n - 1) + dx[i]) / n; ax[i] = a; }
    return { adx: ax, pdi, mdi };
  }
  function obv(c, v) { const o = arr(c.length); let s = 0; o[0] = 0; for (let i = 1; i < c.length; i++) { s += c[i] > c[i - 1] ? v[i] : c[i] < c[i - 1] ? -v[i] : 0; o[i] = s; } return o; }
  function cci(h, l, c, n) { const tp = h.map((x, i) => (x + l[i] + c[i]) / 3), m = sma(tp, n), o = arr(c.length); for (let i = n - 1; i < c.length; i++) { let d = 0; for (let j = i - n + 1; j <= i; j++) d += Math.abs(tp[j] - m[i]); d /= n; o[i] = d === 0 ? 0 : (tp[i] - m[i]) / (0.015 * d); } return o; }
  function williamsR(h, l, c, n) { const o = arr(c.length); for (let i = n - 1; i < c.length; i++) { let a = -Infinity, b = Infinity; for (let j = i - n + 1; j <= i; j++) { a = Math.max(a, h[j]); b = Math.min(b, l[j]); } o[i] = a === b ? -50 : -100 * (a - c[i]) / (a - b); } return o; }
  const api = { sma, ema, bollinger, donchian, atr, keltner, supertrend, ichimoku, adx, obv, cci, williamsR };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.V7IND2 = api;
})(typeof window !== 'undefined' ? window : globalThis);
