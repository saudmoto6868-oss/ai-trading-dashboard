// Spot desk widget (owner 2026-11-15: bring Spot into the Workspace; each school keeps its own method).
// Reads ONLY CFG.spot = docs/spot/snapshot.json (written daily by the spot workflow). Read-only: no orders, no fetches.
// Views: Ideas (the desk's plans), Brain (4 horizons with reasons), Setups (live library with t / n), Markets, Log.
Panel.prototype.build_spot = function(){
  const S = this.state.sp = Object.assign({asset:"", view:"ideas", cls:"", hz:"all"}, this.state.sp || {});
  // horizons from the Spot desk (owner 2026-11-20): the desk works on daily / weekly / monthly / yearly; no scalp timeframe exists in Spot data
  const HZ_OPTS = [["all", "الكل"], ["day", "يومي (4H)"], ["week", "أسبوعي (1D)"], ["month", "شهري (1W)"], ["year", "سنوي (1M)"]];
  const HZ_OF_TF = {"4H":"day","4h":"day","1D":"week","1d":"week","1W":"month","1w":"month","1M":"year","1mo":"year","1Mutc":"year"};
  const snap = (typeof CFG !== "undefined" && CFG.spot) || {};
  if (!document.getElementById("spCss")){ const st = el("style"); st.id = "spCss"; st.textContent =
    ".spw .tb{display:flex;flex-wrap:wrap;gap:4px;align-items:center}.spw .tb select{font-size:12px}"
    +".spw .sum{font-size:12px;padding:5px 6px;margin:4px 0;border:1px solid var(--line);border-radius:6px;line-height:1.5}"
    +".spw .cd{border:1px solid var(--line);border-inline-start:4px solid var(--vc,#888);border-radius:7px;padding:7px 9px;margin:6px 2px;font-size:12px;line-height:1.5}"
    +".spw .hd{display:flex;flex-wrap:wrap;gap:7px;align-items:center}.spw .vb{font-weight:800;font-size:11px;padding:1px 8px;border-radius:4px;color:#fff;background:var(--vc,#888)}"
    +".spw .mut{color:var(--mut,#888);font-size:11px}.spw ul{margin:3px 0 0;padding-inline-start:16px}.spw .ev{color:#f0b90b;font-size:11px}"
    +".spw table{width:100%;border-collapse:collapse;font-size:12px}.spw td,.spw th{border-bottom:1px solid var(--line);padding:3px 5px;text-align:start}";
    document.head.appendChild(st); }
  const wrap = el("div", "spw"); wrap.style.cssText = "height:100%;overflow:auto;padding:6px"; this.body.innerHTML = ""; this.body.appendChild(wrap);
  wrap.classList.add("spw");
  const brains = snap.brains || [], ideas = snap.ideas || [], setups = [];
  brains.forEach(b => (b.setups || []).forEach(s => setups.push(Object.assign({asset:b.asset}, s))));
  const assets = [...new Set([...brains.map(b => b.asset), ...ideas.map(i => i.asset), ...(snap.markets || []).map(m => m.asset)].filter(Boolean))];
  const ar = lang === "ar";
  const CLS = snap.classes || {}, clsOf = a => CLS[a] || (snap.markets || []).find(m => m.asset === a)?.cls || "";
  const CLS_OPTS = [["", ar ? "كل الفئات" : "All classes"], ["crypto", ar ? "كريبتو" : "Crypto"], ["metals", ar ? "معادن" : "Metals"], ["energy", ar ? "طاقة" : "Energy"], ["forex", ar ? "فوركس" : "Forex"]];
  const cls = el("select"); cls.innerHTML = CLS_OPTS.map(([v, t]) => `<option value="${v}">${esc(t)}</option>`).join(""); cls.value = S.cls;
  cls.onchange = () => { S.cls = cls.value; if (S.asset && cls.value && clsOf(S.asset) !== cls.value) S.asset = ""; this.build_spot(); };
  const shown = assets.filter(a => !S.cls || clsOf(a) === S.cls);
  const sel = el("select"); sel.innerHTML = `<option value="">${ar ? "كل الأسواق" : "All markets"}</option>` + shown.map(a => `<option value="${esc(a)}">${esc(a)}</option>`).join("");
  sel.value = shown.includes(S.asset) ? S.asset : ""; S.asset = sel.value; sel.onchange = () => { S.asset = sel.value; build(); };
  const vsel = el("select"); const VIEWS = [["ideas", ar ? "الأفكار" : "Ideas"], ["brain", ar ? "العقل (4 مدد)" : "Brain (4 horizons)"], ["setups", ar ? "السيتابات + الدليل" : "Setups + evidence"], ["markets", ar ? "الأسواق" : "Markets"], ["log", ar ? "سجل التفكير" : "Thinking log"]];
  vsel.innerHTML = VIEWS.map(([v, t]) => `<option value="${v}">${esc(t)}</option>`).join(""); vsel.value = S.view; vsel.onchange = () => { S.view = vsel.value; build(); };
  const hsel = el("select"); hsel.innerHTML = HZ_OPTS.map(([v, t]) => `<option value="${v}">${esc(t)}</option>`).join(""); hsel.value = S.hz;
  hsel.onchange = () => { S.hz = hsel.value; build(); };
  const tb = el("div", "tb"); tb.append(cls, sel, hsel, vsel); wrap.appendChild(tb);
  const scalpNote = el("div", "mut"); scalpNote.textContent = ar ? "سكالب (دقايق / ساعة) مش موجود في داتا السبوت: أقل فريم 4 ساعات" : "Scalp (minutes / 1H) is not in Spot data: the lowest frame is 4H"; wrap.appendChild(scalpNote);
  // the brain's one-line verdict stays on top, whatever view is open (owner 2026-11-15)
  const headBar = el("div", "sum"); wrap.appendChild(headBar);
  const heads = (A => A ? brains.filter(b => b.asset === A) : brains.filter(b => !S.cls || clsOf(b.asset) === S.cls))(S.asset);
  const riskTxt = snap.risk_off ? ` <span class="ev">${ar ? "تحذير: مخاطرة تحت الضغط" : "risk-off signal"}</span>` : "";
  headBar.innerHTML = heads.length ? heads.slice(0, 4).map(b => `<div><b>${ar ? "العقل المدبر" : "Brain"} - ${esc(b.asset)}:</b> ${esc(b.head || "")}</div>`).join("") + riskTxt
    : `<span class="mut">${ar ? "العقل المدبر: مفيش قراءة للفئة دي" : "Brain: no reading for this class"}</span>`;
  const meta = el("div", "mut"); meta.textContent = snap.generated ? (ar ? "آخر تحديث: " : "Updated: ") + snap.generated + (ar ? " - قراءة فقط، مفيش أوامر" : " - read only, no orders") : (ar ? "مفيش لقطة لسه: شغّل ورك فلو السبوت مرة" : "No snapshot yet: run the Spot ideas workflow once");
  wrap.appendChild(meta);
  const body = el("div"); wrap.appendChild(body);
  const sc = v => { const n = Number(v); return Number.isFinite(n) ? (n >= 0 ? "#2ea043" : "#f85149") : "#888"; };
  const fp = v => (v == null || v === "") ? "-" : (typeof v === "number" ? fmtP(v) : esc(v));
  const list = a => Array.isArray(a) && a.length ? "<ul>" + a.slice(0, 8).map(x => `<li>${esc(typeof x === "object" ? (x.text || x.label || JSON.stringify(x)) : x)}</li>`).join("") + "</ul>" : "";
  const tg = a => Array.isArray(a) ? a.map(fp).join(" / ") : fp(a);
  function build(){
    const A = S.asset; let h = "";
    if (S.view === "ideas"){
      const L = ideas.filter(i => (!A || i.asset === A) && (!S.cls || clsOf(i.asset) === S.cls));
      h = L.length ? L.map(i => `<div class="cd" style="--vc:${i.kind === "avoid" ? "#f85149" : "#2ea043"}"><div class="hd"><b>${esc(i.name || i.asset)}</b><span class="vb">${esc(i.title || i.kind || "")}</span><span class="mut">${esc(i.conf || "")}</span></div>`
        + `<div>${ar ? "دخول" : "Entry"}: ${tg(i.entry)} | ${ar ? "وقف" : "Stop"}: ${fp(i.stop)} | ${ar ? "أهداف" : "Targets"}: ${tg(i.targets)} | R:R ${fp(i.rr)}</div>`
        + list(i.pros || i.why) + list(i.cons || i.against) + "</div>").join("")
        : `<div class="mut">${ar ? "مفيش أفكار للسوق ده دلوقتي (الديسك بيقول كده بصراحة)" : "No ideas for this market right now (the desk says so openly)"}</div>`;
    } else if (S.view === "brain"){
      const B = brains.filter(b => (!A || b.asset === A) && (!S.cls || clsOf(b.asset) === S.cls));
      const HK = S.hz === "all" ? null : S.hz;
      h = B.length ? B.map(b => `<div class="cd"><div class="hd"><b>${esc(b.asset)}</b><span class="mut">${fp(b.price)}</span></div><div class="sum">${esc(b.head || "")}</div>`
        + `<table><tr><th>${ar ? "المدة" : "Horizon"}</th><th>TF</th><th>${ar ? "الحكم" : "Verdict"}</th><th>${ar ? "النقاط" : "Score"}</th></tr>`
        + Object.entries(b.horizons || {}).filter(([k]) => !HK || k === HK).map(([k, z]) => `<tr style="${HK && k === HK ? "font-weight:700" : ""}"><td>${esc(z.label || "")}</td><td>${esc(z.tf || "")}</td><td style="color:${sc(z.score)}">${esc(z.verdict_ar || z.verdict || "")}</td><td>${fp(z.score)}</td></tr>`).join("")
        + `</table>${list(Object.entries(b.horizons || {}).filter(([k]) => !HK || k === HK).flatMap(([k, z]) => (z.reasons || []).slice(0, 2)))}`
        + (b.news ? `<div class="mut">${ar ? "نبرة الأخبار" : "News tilt"}: ${fp(b.news.score)}</div>` : "") + `</div>`).join("")
        : `<div class="mut">${ar ? "مفيش عقل محسوب للسوق ده" : "No brain reading for this market"}</div>`;
    } else if (S.view === "setups"){
      const L = setups.filter(s => (!A || s.asset === A) && (!S.cls || clsOf(s.asset) === S.cls) && (S.hz === "all" || HZ_OF_TF[s.tf] === S.hz));
      h = L.length ? `<table><tr><th>${ar ? "الأصل" : "Asset"}</th><th>${ar ? "المدرسة" : "School"}</th><th>${ar ? "السيتاب" : "Setup"}</th><th>${ar ? "الجهة" : "Side"}</th><th>TF</th><th>${ar ? "الدليل" : "Evidence"}</th></tr>`
        + L.map(s => `<tr><td>${esc(s.asset)}</td><td>${esc(s.school_ar || "")}</td><td>${esc(s.name || "")}</td><td>${esc(s.side || "")}</td><td>${esc(s.tf || "")}</td><td class="${s.ev_label ? "ev" : "mut"}">${esc(s.ev_label || (ar ? "لسه ماتقاسش - مش دليل" : "not tested - not evidence"))}</td></tr>`).join("") + "</table>"
        : `<div class="mut">${ar ? "مفيش سيتابات حية دلوقتي" : "No live setups right now"}</div>`;
    } else if (S.view === "markets"){
      const M = (snap.markets || []).filter(m => (!A || m.asset === A) && (!S.cls || clsOf(m.asset) === S.cls));
      h = M.length ? `<table><tr><th>${ar ? "السوق" : "Market"}</th><th>${ar ? "السعر" : "Price"}</th><th>${ar ? "أسبوع %" : "Week %"}</th><th>${ar ? "الدرجة" : "Score"}</th><th>${ar ? "المنطقة" : "Zone"}</th><th>${ar ? "أفكار" : "Ideas"}</th></tr>`
        + M.map(m => `<tr><td>${esc(m.name || m.asset)}</td><td>${fp(m.price)}</td><td style="color:${sc(m.wk)}">${Number(m.wk).toFixed(1)}</td><td>${fp(m.score)}</td><td>${esc(m.zone || "")}</td><td>${fp(m.n_ideas)}</td></tr>`).join("") + "</table>"
        : `<div class="mut">${ar ? "مفيش بيانات أسواق" : "No market data"}</div>`;
    } else {
      h = list(snap.log || []) || `<div class="mut">${ar ? "السجل فاضي" : "Log is empty"}</div>`;
    }
    body.innerHTML = h;
  }
  build();
};
