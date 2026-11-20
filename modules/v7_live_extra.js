/* V7 live extra tools (pure functions, browser + node). Research display only, none of this is a signal.
   Definitions (all on the candles on screen; volume = the exchange candle volume, so VWAP / profile are ESTIMATES from candle data, not tape):
   NY session day = New York clock, the day rolls at 18:00 (same as v7_live_struct prevDay); week = Monday-based NY session week.
   sessionVwap  = running sum(typical*vol)/sum(vol), typical=(h+l+c)/3, reset when the NY session day changes (NaN while volume is 0).
   volumeProfile = last `look` bars, price range split into `bins`; each bar's volume spread equally over the bins its high-low touches; POC = max bin (lowest on ties);
                   value area = 70 % of volume grown from the POC, each step adding the larger neighbour bin (ties: upper).
   opens        = open of the first bar of the current NY session day / week; prevWeek = high/low of the previous NY session week.
   killzones    = New York clock 20-24 (Asia), 02-05 (London), 07-10 (NY AM) runs.
   swingLabels  = each confirmed swing high is HH if above the previous swing high else LH; each swing low HL if above the previous swing low else LL.
   orderBlocks  = for every BOS / CHoCH (close through a swing): impulse start = lowest low (up break) / highest high (down break) between the broken swing and the break bar;
                  the OB is the last opposite-colour candle at or before the impulse start (searched back 5 bars); mitigated once a later close is beyond the far side. Unmitigated, last 3.
   filterSignals = keeps a research dot only if it passes the chosen filters (trend: close vs SMA144 same side; killzone: bar inside a kill zone). */
(function (root) {
  const fin = Number.isFinite;
  const FMT = new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hour12: false });
  function nyParts(sec) { const p = FMT.formatToParts(new Date(sec * 1000)), v = k => +(p.find(x => x.type === k) || {}).value; return { y: v('year'), m: v('month'), d: v('day'), h: v('hour') % 24, mi: v('minute') }; }
  function sessionDay(sec) { const q = nyParts(sec); return new Date(Date.UTC(q.y, q.m - 1, q.d + (q.h >= 18 ? 1 : 0))); }
  const dayKey = sec => sessionDay(sec).toISOString().slice(0, 10);
  function weekKey(sec) { const d = sessionDay(sec), wd = (d.getUTCDay() + 6) % 7; return new Date(d.getTime() - wd * 86400000).toISOString().slice(0, 10); }
  function sessionVwap(b) {
    const out = []; let key = null, pv = 0, v = 0;
    b.forEach(x => { const k = dayKey(x.time); if (k !== key) { key = k; pv = 0; v = 0; } const vol = +x.volume || 0; pv += (x.high + x.low + x.close) / 3 * vol; v += vol; out.push(v > 0 ? pv / v : NaN); });
    return out;
  }
  function volumeProfile(b, look, bins) {
    look = look || 200; bins = bins || 40; const a = b.slice(-look); if (a.length < 5) return null;
    let lo = Infinity, hi = -Infinity; a.forEach(x => { lo = Math.min(lo, x.low); hi = Math.max(hi, x.high); });
    const step = (hi - lo) / bins; if (!(step > 0)) return null;
    const idx = p => Math.min(bins - 1, Math.max(0, Math.floor((p - lo) / step))), vol = new Array(bins).fill(0); let tot = 0;
    a.forEach(x => { const v = +x.volume || 0; if (!v) return; const i0 = idx(x.low), i1 = idx(x.high), n = i1 - i0 + 1; for (let i = i0; i <= i1; i++) vol[i] += v / n; tot += v; });
    if (!(tot > 0)) return null;
    let poc = 0; for (let i = 1; i < bins; i++) if (vol[i] > vol[poc]) poc = i;
    let l = poc, h = poc, acc = vol[poc];
    while (acc < 0.7 * tot && (l > 0 || h < bins - 1)) { const up = h < bins - 1 ? vol[h + 1] : -1, dn = l > 0 ? vol[l - 1] : -1; if (up >= dn) { h++; acc += vol[h]; } else { l--; acc += vol[l]; } }
    return { poc: lo + (poc + 0.5) * step, vah: lo + (h + 1) * step, val: lo + l * step, lo, hi, bins: vol };
  }
  function opens(b) {
    if (!b.length) return null; const last = b[b.length - 1], dk = dayKey(last.time), wk = weekKey(last.time); let d = null, w = null;
    for (let i = 0; i < b.length; i++) { if (d === null && dayKey(b[i].time) === dk) d = { p: b[i].open, i }; if (w === null && weekKey(b[i].time) === wk) w = { p: b[i].open, i }; }
    let ph = -Infinity, pl = Infinity, pk = null;
    for (let i = b.length - 1; i >= 0; i--) { const k = weekKey(b[i].time); if (k === wk) continue; if (pk === null) pk = k; if (k !== pk) break; ph = Math.max(ph, b[i].high); pl = Math.min(pl, b[i].low); }
    return { day: d, week: w, prevWeek: pk === null ? null : { hi: ph, lo: pl, weekStart: pk } };
  }
  function killzones(b) {
    const W = [['Asia KZ', 20, 24], ['London KZ', 2, 5], ['NY AM KZ', 7, 10]], out = [];
    W.forEach(([name, a, z]) => { let run = null; b.forEach((x, i) => { const q = nyParts(x.time), inside = q.h >= a && q.h < z; if (inside) { if (!run) run = { name, i0: i, i1: i }; else run.i1 = i; } else if (run) { out.push(run); run = null; } }); if (run) out.push(run); });
    return out.sort((p, q) => p.i0 - q.i0).slice(-9);
  }
  function swingLabels(sw) {
    const out = []; let ph = null, pl = null;
    sw.H.forEach(s => { out.push({ i: s.i, p: s.p, side: 'H', label: ph === null ? 'H' : s.p > ph ? 'HH' : 'LH' }); ph = s.p; });
    sw.L.forEach(s => { out.push({ i: s.i, p: s.p, side: 'L', label: pl === null ? 'L' : s.p > pl ? 'HL' : 'LL' }); pl = s.p; });
    return out.sort((p, q) => p.i - q.i).slice(-12);
  }
  function orderBlocks(b, events) {
    const out = [];
    (events || []).forEach(e => {
      let k = e.from, ext = e.dir === 'up' ? Infinity : -Infinity;
      for (let i = e.from; i <= e.i; i++) { if (e.dir === 'up' ? b[i].low < ext : b[i].high > ext) { ext = e.dir === 'up' ? b[i].low : b[i].high; k = i; } }
      let j = -1; for (let i = k; i >= Math.max(0, k - 5); i--) { if (e.dir === 'up' ? b[i].close < b[i].open : b[i].close > b[i].open) { j = i; break; } }
      if (j < 0) return;
      let mit = false; for (let i = e.i + 1; i < b.length; i++) { if (e.dir === 'up' ? b[i].close < b[j].low : b[i].close > b[j].high) { mit = true; break; } }
      if (!mit) out.push({ dir: e.dir, i0: j, hi: b[j].high, lo: b[j].low, type: e.type });
    });
    return out.slice(-3);
  }
  function filterSignals(sig, b, sma144, opt) {
    const kz = killzones(b), inKz = i => kz.some(r => i >= r.i0 && i <= r.i1);
    return sig.filter(s => { const c = b[s.i].close, m = sma144[s.i]; if (opt.trend && fin(m) && (s.side === 'buy' ? c < m : c > m)) return false; if (opt.kz && !inKz(s.i)) return false; return true; });
  }
  const api = { sessionVwap, volumeProfile, opens, killzones, swingLabels, orderBlocks, filterSignals, dayKey, weekKey };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.V7EXTRA = api;
})(typeof window !== 'undefined' ? window : globalThis);
