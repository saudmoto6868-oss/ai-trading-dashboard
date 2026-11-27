/* LEDGER-OF (owner 2026-11-27: "order flow needs review"): every LIVE absorption / sweep mark from Panel.syncMarks goes to the signal ledger as a
   DIRECTION TEST, so its real hit rate can be measured. The order flow itself gives no stop, so the test rule is fixed and stated on every record:
   entry = the event price, stop = 1 ATR(14 candles) the other way, target = 1.5 ATR (the absorption mark's own target). Not a trade plan.
   Forward only: marks on the two newest candles. src "orderflow", sub "absorb" / "sweep". */
{ const P = Panel.prototype, f = P.syncMarks;
  if (typeof f === "function") P.syncMarks = function(...a){ const r = f.apply(this, a);
    try { const ch = this.chart, d = ch && ch.data; if (!d || d.length < 15 || !ch.marks) return r;
      const rows = d.slice(-14), atr = rows.reduce((s, k) => s + (k.h - k.l), 0)/rows.length || 0; if (!(atr > 0)) return r;
      const n = d.length, sec = ch.secMs();
      ch.marks.forEach(m => { if (!(m.t >= d[n-2].t) || !(m.p > 0)) return;
        let j = n - 1; while (j > 0 && d[j].t > m.t) j--;   // the candle the event happened in
        const dir = m.dir > 0 ? "long" : "short", stop = m.p - m.dir*atr, tgt = m.p + m.dir*1.5*atr;
        ch.ledgerAdd({src:"orderflow", sub:m.kind, tBar:d[j].t, ms:sec, dir, entry:m.p, sl:stop, tps:[tgt],
          why:["test rule: stop 1 ATR, target 1.5 ATR (order flow gives no stop)", "events " + (m.n || 1)]}); });
    } catch(e){}
    return r; };
}
/* LEDGER-OF-END */
