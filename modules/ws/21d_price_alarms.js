/* ---------------- price alarms (owner 2026-11-20: "exactly like TradingView": a + beside the price on the axis, the same
   alert dialog and options, and the alarm reaches the phone: Telegram message / Telegram call / WhatsApp / push) ----------------
   Checked in THIS browser every few seconds while the Workspace is open (TradingView checks on its servers: a closed tab here
   means no check). Channels are the owner's own accounts, typed in the dialog and kept in this browser only (never in the repo):
   ntfy.sh topic (phone push, free app, priority 5 = alarm), CallMeBot (Telegram text / Telegram voice call / WhatsApp, free),
   any webhook URL. No key of the app is used. */
/* PALARM-PURE-START (tests/test_price_alarms.js evaluates this block alone) */
const PALARM_CONDS = [["cross","Crossing","تقاطع"],["up","Crossing Up","تقاطع لأعلى"],["down","Crossing Down","تقاطع لأسفل"],
  ["gt","Greater Than","أكبر من"],["lt","Less Than","أقل من"],["enter","Entering Channel","دخول القناة"],["exit","Exiting Channel","خروج من القناة"],
  ["inside","Inside Channel","داخل القناة"],["outside","Outside Channel","خارج القناة"],["mup","Moving Up","تحرك لأعلى"],
  ["mdn","Moving Down","تحرك لأسفل"],["mupp","Moving Up %","تحرك لأعلى %"],["mdnp","Moving Down %","تحرك لأسفل %"]];
const PALARM_TRIG = [["once","Only Once","مرة واحدة"],["bar","Once Per Bar","مرة لكل شمعة"],["close","Once Per Bar Close","مرة عند إغلاق الشمعة"],
  ["min","Once Per Minute","مرة كل دقيقة"]];
const PALARM_CH = new Set(["enter","exit","inside","outside"]), PALARM_MOVE = new Set(["mup","mdn","mupp","mdnp"]);
function palarmHit(a, p0, p1, closes){   // a.v = price (or amount / % for moving), a.v2 = second channel price, a.n = bars back
  const lo = Math.min(a.v, a.v2 == null ? a.v : a.v2), hi = Math.max(a.v, a.v2 == null ? a.v : a.v2), ins = p => p >= lo && p <= hi;
  switch (a.cond){
    case "cross": return p0 != null && ((p0 < a.v && p1 >= a.v) || (p0 > a.v && p1 <= a.v));
    case "up": return p0 != null && p0 < a.v && p1 >= a.v;
    case "down": return p0 != null && p0 > a.v && p1 <= a.v;
    case "gt": return p1 > a.v;
    case "lt": return p1 < a.v;
    case "enter": return p0 != null && !ins(p0) && ins(p1);
    case "exit": return p0 != null && ins(p0) && !ins(p1);
    case "inside": return ins(p1);
    case "outside": return !ins(p1);
  }
  if (PALARM_MOVE.has(a.cond)){ const n = Math.max(1, a.n | 0), c = closes || []; if (c.length <= n) return false;
    const ref = c[c.length - 1 - n], d = p1 - ref, pct = ref ? d / ref * 100 : 0;
    return a.cond === "mup" ? d >= a.v : a.cond === "mdn" ? -d >= a.v : a.cond === "mupp" ? pct >= a.v : -pct >= a.v; }
  return false;
}
function palarmCheck(a, st, now){   // st = {p0, p1, curT, rows:[{t,c}] oldest..newest incl. the running bar} -> trigger price or null; updates a
  if (!a.on) return null;
  if (a.exp && now > a.exp){ a.on = false; a.status = "expired"; return null; }
  const rows = st.rows || [], closes = rows.map(r => r.c);
  let px = null;
  if (a.trig === "close"){   // judged on closed bars only, once per newly closed bar
    const cl = rows.slice(0, -1), last = cl[cl.length - 1]; if (!last || a.lastClose === last.t) return null;
    const first = a.lastClose == null; a.lastClose = last.t; if (first) return null;   // the bar that was already closed when the alarm was made does not count
    if (palarmHit(a, cl.length > 1 ? cl[cl.length - 2].c : null, last.c, cl.map(r => r.c))) px = last.c;
  } else {
    if (st.p1 == null || !palarmHit(a, st.p0, st.p1, closes)) return null;
    if (a.trig === "bar" && a.lastBar === st.curT) return null;
    if (a.trig === "min" && a.lastT && now - a.lastT < 60000) return null;
    px = st.p1; a.lastBar = st.curT;
  }
  if (px == null) return null;
  a.lastT = now; a.fired = (a.fired || 0) + 1;
  if (a.trig === "once"){ a.on = false; a.status = "triggered"; }
  return px;
}
function palarmText(a, px){   // TradingView-style placeholders in the message
  const cond = (PALARM_CONDS.find(c => c[0] === a.cond) || ["", a.cond])[1];
  const def = a.sym + " " + cond + " " + a.v + (a.v2 != null && PALARM_CH.has(a.cond) ? " / " + a.v2 : "");
  return String(a.msg || def).replace(/\{\{ticker\}\}/g, a.sym).replace(/\{\{close\}\}/g, px).replace(/\{\{interval\}\}/g, a.tf || "")
    .replace(/\{\{time\}\}/g, new Date().toISOString().slice(0, 16).replace("T", " ") + " UTC");
}
/* PALARM-PURE-END */

const PAlarm = {
  list: store.get(LS+"_palarms", []), log: store.get(LS+"_palog", []), prev: {}, subs: new Set(), _iv: null, _snd: null,
  save(){ store.set(LS+"_palarms", this.list); this.subs.forEach(f => { try { f(); } catch(e){} }); },
  cfg(){ return Object.assign({ntfy:"", tg:"", wa:"", waKey:"", hook:""}, store.get(LS+"_notify", {})); },
  forSym(sym){ return this.list.filter(a => a.sym === sym); },
  upsert(a){ const i = this.list.findIndex(x => x.id === a.id); if (i >= 0) this.list[i] = a; else this.list.unshift(a); this.save(); this.start(); },
  del(id){ this.list = this.list.filter(a => a.id !== id); this.save(); },
  start(){ if (this._iv || typeof window === "undefined") return; this._iv = setInterval(() => this.tick(), 5000); this.tick(); },
  async tick(){
    const on = this.list.filter(a => a.on); if (!on.length) return; const now = Date.now(), groups = {};
    on.forEach(a => { const k = a.sym+"|"+(a.tf || "1m"); (groups[k] = groups[k] || []).push(a); });
    let dirty = false;
    for (const k in groups){
      const [sym, tf] = k.split("|"); let rows;
      try { rows = await candlesTf(sym, tf, false); } catch(e){ continue; }
      if (!rows || !rows.length) continue;
      const cur = rows[rows.length - 1], st = {p0: this.prev[k], p1: cur.c, curT: cur.t, rows}; this.prev[k] = cur.c;
      groups[k].forEach(a => { const was = JSON.stringify([a.on, a.lastClose, a.lastBar]); const px = palarmCheck(a, st, now);
        if (px != null) this.fire(a, px); if (px != null || was !== JSON.stringify([a.on, a.lastClose, a.lastBar])) dirty = true; });
    }
    if (dirty) this.save();
  },
  fire(a, px){
    const msg = palarmText(a, px), title = "⏰ " + (a.name || a.sym);
    this.log.unshift({t: Date.now(), id: a.id, sym: a.sym, px, msg}); this.log = this.log.slice(0, 100); store.set(LS+"_palog", this.log);
    this.send(a.ch || {}, title, msg, a.snd, a.rep);
  },
  send(ch, title, msg, snd, rep){   // every channel is fire-and-forget: one failing channel never blocks the others
    const C = this.cfg(), enc = encodeURIComponent, nc = {mode: "no-cors"};
    if (ch.popup !== false) this.popup(title, msg);
    if (ch.sound !== false) this.sound(snd || "alarm", !!rep);
    if (ch.desk && typeof Notification !== "undefined" && Notification.permission === "granted"){ try { new Notification(title, {body: msg}); } catch(e){} }
    if (ch.push && C.ntfy) fetch("https://ntfy.sh/" + enc(C.ntfy), {method: "POST", body: msg, headers: {Title: title.replace(/[^\x20-\x7e]/g, "").trim() || "Alarm", Priority: "5", Tags: "rotating_light"}}).catch(() => {});
    if (ch.tg && C.tg) fetch("https://api.callmebot.com/text.php?user=" + enc(C.tg) + "&text=" + enc(title + "\n" + msg), nc).catch(() => {});
    if (ch.call && C.tg) fetch("https://api.callmebot.com/start.php?user=" + enc(C.tg) + "&text=" + enc(msg) + "&lang=" + (lang === "ar" ? "ar-XA-Standard-A" : "en-US-Standard-B") + "&rpt=2", nc).catch(() => {});
    if (ch.wa && C.wa && C.waKey) fetch("https://api.callmebot.com/whatsapp.php?phone=" + enc(C.wa) + "&text=" + enc(title + "\n" + msg) + "&apikey=" + enc(C.waKey), nc).catch(() => {});
    if (ch.hook && C.hook) fetch(C.hook, {method: "POST", mode: "no-cors", headers: {"Content-Type": "text/plain"}, body: JSON.stringify({title, message: msg, t: Date.now()})}).catch(() => {});
  },
  sound(kind, rep){
    try { const AC = window.AudioContext || window.webkitAudioContext; if (!AC) return; const ac = this._ac || (this._ac = new AC());
      const pat = {alarm: [[880,.15],[0,.08],[880,.15],[0,.08],[880,.15]], beep: [[1000,.25]], bell: [[660,.6],[990,.6]]}[kind] || [[880,.2]];
      const play = () => { let t = ac.currentTime; pat.forEach(([f, d]) => { if (f){ const o = ac.createOscillator(), g = ac.createGain(); o.frequency.value = f; o.type = "square"; g.gain.setValueAtTime(.12, t); g.gain.exponentialRampToValueAtTime(.001, t + d); o.connect(g).connect(ac.destination); o.start(t); o.stop(t + d); } t += d; }); };
      play(); if (rep){ clearInterval(this._snd); let k = 0; this._snd = setInterval(() => { if (++k > 30) return this.stopSound(); play(); }, 2000); } } catch(e){}
  },
  stopSound(){ clearInterval(this._snd); this._snd = null; },
  popup(title, msg){
    let box = document.getElementById("palarmPop"); if (!box){ box = el("div"); box.id = "palarmPop"; box.style.cssText = "position:fixed;top:12px;right:12px;z-index:2147483002;display:flex;flex-direction:column;gap:6px;max-width:320px"; document.body.append(box); }
    const p = el("div", null, "<b>"+esc(title)+"</b><div style='margin:4px 0;white-space:pre-wrap'>"+esc(msg)+"</div><small style='color:#848e9c'>"+new Date().toLocaleTimeString()+"</small> ");
    p.style.cssText = "background:#1e2329;color:#eaecef;border:1px solid #f0b90b;border-radius:6px;padding:8px 10px;font:12px sans-serif;box-shadow:0 4px 18px #0008";
    const ok = el("button", null, Lg("OK, stop sound","تمام، وقف الصوت")); ok.style.cssText = "float:right;background:#f0b90b;border:0;border-radius:4px;padding:2px 8px;cursor:pointer";
    ok.onclick = () => { this.stopSound(); p.remove(); }; p.append(ok); box.prepend(p);
  }
};

const PALARM_CSS = "position:fixed;inset:0;z-index:2147483001;background:#0009;display:flex;align-items:center;justify-content:center;font:12px sans-serif";
function palarmField(lbl, inner){ return "<label style='display:flex;align-items:center;gap:8px;margin:6px 0'><span style='width:110px;color:#848e9c'>"+lbl+"</span>"+inner+"</label>"; }
function palarmOpts(list, cur){ return list.map(o => "<option value='"+o[0]+"'"+(o[0] === cur ? " selected" : "")+">"+esc(Lg(o[1], o[2]))+"</option>").join(""); }
function palarmDialog(init, onDone){   // the TradingView "Create alert" dialog: Settings + Notifications tabs
  const a = Object.assign({id: Date.now() + "" + Math.random().toString(36).slice(2, 6), on: true, cond: "cross", trig: "once", tf: "1m", n: 10,
    exp: Date.now() + 30*86400000, ch: {popup: true, sound: true}, snd: "alarm", rep: true}, init), C = PAlarm.cfg();
  const ov = el("div"); ov.style.cssText = PALARM_CSS;
  const inp = "style='flex:1;background:#0b0e11;color:#eaecef;border:1px solid #2b3139;border-radius:4px;padding:4px'";
  const expV = a.exp ? new Date(a.exp - new Date().getTimezoneOffset()*60000).toISOString().slice(0, 16) : "";
  const cb = (k, lbl, on) => "<label style='display:block;margin:5px 0'><input type=checkbox data-ch='"+k+"'"+(on ? " checked" : "")+"> "+lbl+"</label>";
  ov.innerHTML = "<div style='background:#1e2329;color:#eaecef;border:1px solid #2b3139;border-radius:8px;width:min(440px,94vw);max-height:92vh;overflow:auto;padding:14px'>"
    + "<div style='display:flex;justify-content:space-between'><b>"+(init && init.fired != null ? Lg("Edit alert on ","تعديل تنبيه ") : Lg("Create alert on ","تنبيه جديد على "))+esc(a.sym)+"</b><span data-x style='cursor:pointer'>✕</span></div>"
    + "<div style='display:flex;gap:14px;margin:10px 0;border-bottom:1px solid #2b3139'><a data-tab=s style='cursor:pointer;padding-bottom:4px;border-bottom:2px solid #f0b90b'>"+Lg("Settings","الإعدادات")+"</a><a data-tab=n style='cursor:pointer;padding-bottom:4px'>"+Lg("Notifications","الإشعارات")+"</a></div>"
    + "<div data-pane=s>"
    + palarmField(Lg("Condition","الشرط"), "<select data-k=cond "+inp+">"+palarmOpts(PALARM_CONDS, a.cond)+"</select>")
    + palarmField(Lg("Value","القيمة"), "<input data-k=v type=number step=any value='"+(a.v ?? "")+"' "+inp+">")
    + "<div data-show=ch>"+palarmField(Lg("Lower / upper","الحد التاني"), "<input data-k=v2 type=number step=any value='"+(a.v2 ?? "")+"' "+inp+">")+"</div>"
    + "<div data-show=mv>"+palarmField(Lg("In bars","خلال شمعات"), "<input data-k=n type=number min=1 value='"+a.n+"' "+inp+">")+"</div>"
    + palarmField(Lg("Interval","الفريم"), "<input data-k=tf value='"+esc(a.tf)+"' "+inp+">")
    + palarmField(Lg("Trigger","التكرار"), "<select data-k=trig "+inp+">"+palarmOpts(PALARM_TRIG, a.trig)+"</select>")
    + palarmField(Lg("Expiration","ينتهي"), "<input data-k=exp type=datetime-local value='"+expV+"' "+inp+"><label><input data-k=open type=checkbox"+(a.exp ? "" : " checked")+"> "+Lg("Open-ended","مفتوح")+"</label>")
    + palarmField(Lg("Alert name","الاسم"), "<input data-k=name value='"+esc(a.name || "")+"' "+inp+">")
    + "<div style='color:#848e9c;margin-top:6px'>"+Lg("Message","الرسالة")+" <small>{{ticker}} {{close}} {{interval}} {{time}}</small></div><textarea data-k=msg rows=3 style='width:100%;box-sizing:border-box;background:#0b0e11;color:#eaecef;border:1px solid #2b3139;border-radius:4px'>"+esc(a.msg || "")+"</textarea>"
    + "</div><div data-pane=n style='display:none'>"
    + cb("popup", Lg("Notify in app (popup)","تنبيه جوه التطبيق"), a.ch.popup !== false)
    + cb("sound", Lg("Play sound","صوت")+" <select data-k=snd>"+palarmOpts([["alarm","Alarm clock","منبّه"],["beep","Beep","بيب"],["bell","Bell","جرس"]], a.snd)+"</select> <label><input data-k=rep type=checkbox"+(a.rep ? " checked" : "")+"> "+Lg("repeat until OK","يكرر لحد ما توقفه")+"</label>", a.ch.sound !== false)
    + cb("desk", Lg("Desktop notification","إشعار الكمبيوتر"), a.ch.desk)
    + cb("push", Lg("Push to phone (ntfy app, rings as an alarm)","إشعار على الموبايل (تطبيق ntfy، بيرن زي المنبّه)"), a.ch.push)
    + cb("tg", Lg("Telegram message","رسالة تليجرام"), a.ch.tg) + cb("call", Lg("Telegram voice CALL","مكالمة تليجرام"), a.ch.call)
    + cb("wa", Lg("WhatsApp message","رسالة واتساب"), a.ch.wa) + cb("hook", Lg("Webhook URL","Webhook"), a.ch.hook)
    + "<details style='margin-top:8px'><summary style='cursor:pointer;color:#f0b90b'>"+Lg("Phone channels setup (once, kept in this browser only)","إعداد قنوات الموبايل (مرة واحدة، بيتحفظ في المتصفح ده بس)")+"</summary>"
    + palarmField("ntfy topic", "<input data-c=ntfy value='"+esc(C.ntfy)+"' placeholder='my-secret-topic-123' "+inp+">")
    + palarmField("Telegram @user", "<input data-c=tg value='"+esc(C.tg)+"' placeholder='@username' "+inp+">")
    + palarmField("WhatsApp +phone", "<input data-c=wa value='"+esc(C.wa)+"' placeholder='+20...' "+inp+">")
    + palarmField("WhatsApp apikey", "<input data-c=waKey value='"+esc(C.waKey)+"' "+inp+">")
    + palarmField("Webhook", "<input data-c=hook value='"+esc(C.hook)+"' placeholder='https://...' "+inp+">")
    + "<small style='color:#848e9c;display:block;line-height:1.5'>"+Lg("Push: install the ntfy app, subscribe to a long random topic, type it here. Telegram text / call: send /start to @CallMeBot_txtbot, type your @username. WhatsApp: add +34 644 66 32 62 and send \"I allow callmebot to send me messages\" to get the apikey.",
      "الإشعار: نزّل تطبيق ntfy واشترك في اسم طويل عشوائي واكتبه هنا. رسالة/مكالمة تليجرام: ابعت /start لـ @CallMeBot_txtbot واكتب اليوزر بتاعك. واتساب: ضيف +34 644 66 32 62 وابعتله \"I allow callmebot to send me messages\" هيرد عليك بالـ apikey.")+"</small>"
    + "<button data-test style='margin-top:6px'>"+Lg("Send a test","جرّب")+"</button></details></div>"
    + "<div style='display:flex;justify-content:flex-end;gap:8px;margin-top:12px'><button data-x>"+Lg("Cancel","إلغاء")+"</button><button data-ok style='background:#f0b90b;border:0;border-radius:4px;padding:5px 14px;font-weight:bold'>"+(init && init.fired != null ? Lg("Save","حفظ") : Lg("Create","إنشاء"))+"</button></div></div>";
  const $ = s => ov.querySelector(s), $$ = s => ov.querySelectorAll(s);
  const vis = () => { const c = $("[data-k=cond]").value; $("[data-show=ch]").style.display = PALARM_CH.has(c) ? "" : "none"; $("[data-show=mv]").style.display = PALARM_MOVE.has(c) ? "" : "none"; };
  $("[data-k=cond]").onchange = vis; vis();
  $$("[data-tab]").forEach(t => t.onclick = () => { $$("[data-tab]").forEach(x => x.style.borderBottom = x === t ? "2px solid #f0b90b" : ""); $$("[data-pane]").forEach(p => p.style.display = p.dataset.pane === t.dataset.tab ? "" : "none"); });
  const saveCfg = () => { const c = {}; $$("[data-c]").forEach(i => c[i.dataset.c] = i.value.trim()); store.set(LS+"_notify", c); };
  const chans = () => { const ch = {}; $$("[data-ch]").forEach(i => ch[i.dataset.ch] = i.checked); return ch; };
  $("[data-ch=desk]").onchange = e => { if (e.target.checked && typeof Notification !== "undefined" && Notification.permission === "default") Notification.requestPermission(); };
  $("[data-test]").onclick = () => { saveCfg(); PAlarm.send(chans(), "⏰ Test", a.sym + ": " + Lg("test alert from 6868 X","تنبيه تجريبي من 6868 X"), $("[data-k=snd]").value, false); };
  const close = () => ov.remove();
  $$("[data-x]").forEach(b => b.onclick = close); ov.onclick = e => { if (e.target === ov) close(); };
  $("[data-ok]").onclick = () => {
    const g = k => $("[data-k="+k+"]"), num = k => { const v = parseFloat(g(k).value); return isFinite(v) ? v : null; };
    a.cond = g("cond").value; a.v = num("v"); a.v2 = PALARM_CH.has(a.cond) ? num("v2") : null; a.n = Math.max(1, parseInt(g("n").value) || 1);
    a.tf = g("tf").value.trim() || "1m"; a.trig = g("trig").value; a.name = g("name").value.trim(); a.msg = g("msg").value.trim();
    a.exp = g("open").checked || !g("exp").value ? 0 : new Date(g("exp").value).getTime(); a.snd = g("snd").value; a.rep = g("rep").checked; a.ch = chans();
    if (a.v == null || (PALARM_CH.has(a.cond) && a.v2 == null)){ g(a.v == null ? "v" : "v2").style.borderColor = "#f6465d"; return; }
    a.on = true; a.status = "active"; delete a.lastClose; delete a.lastBar; a.fired = a.fired || 0;
    saveCfg(); PAlarm.upsert(a); close(); onDone && onDone(a);
  };
  document.body.append(ov);
}
function palarmManager(sym, onChange){   // the alert list: status, edit, pause / restart, delete, last triggers
  const ov = el("div"); ov.style.cssText = PALARM_CSS;
  const render = () => {
    const rows = PAlarm.list.map(a => { const cond = (PALARM_CONDS.find(c => c[0] === a.cond) || ["", a.cond, a.cond]);
      const st = a.on ? "🟢 "+Lg("active","شغال") : a.status === "triggered" ? "🔔 "+Lg("triggered","اشتغل") : a.status === "expired" ? "⌛ "+Lg("expired","انتهى") : "⏸ "+Lg("paused","موقوف");
      return "<tr><td>"+esc(a.name || a.sym)+"<br><small style='color:#848e9c'>"+esc(a.sym+" · "+Lg(cond[1], cond[2])+" "+a.v+(a.v2 != null ? "/"+a.v2 : "")+" · "+a.tf)+"</small></td><td>"+st+"</td><td style='white-space:nowrap'>"
        +"<button data-e='"+a.id+"'>✎</button> <button data-p='"+a.id+"'>"+(a.on ? "⏸" : "▶")+"</button> <button data-d='"+a.id+"'>🗑</button></td></tr>"; }).join("");
    const log = PAlarm.log.slice(0, 15).map(l => "<div><small style='color:#848e9c'>"+new Date(l.t).toLocaleString()+"</small> "+esc(l.msg)+"</div>").join("");
    ov.innerHTML = "<div style='background:#1e2329;color:#eaecef;border:1px solid #2b3139;border-radius:8px;width:min(520px,94vw);max-height:90vh;overflow:auto;padding:14px'>"
      + "<div style='display:flex;justify-content:space-between'><b>⏰ "+Lg("Alerts","التنبيهات")+" ("+PAlarm.list.length+")</b><span data-x style='cursor:pointer'>✕</span></div>"
      + (sym ? "<button data-new style='margin:8px 0'>+ "+Lg("New alert on ","تنبيه جديد على ")+esc(sym)+"</button>" : "")
      + "<table style='width:100%;border-collapse:collapse'>"+(rows || "<tr><td style='color:#848e9c'>"+Lg("No alerts yet","مفيش تنبيهات")+"</td></tr>")+"</table>"
      + "<div style='margin-top:10px;color:#848e9c'>"+Lg("Log","السجل")+"</div>"+(log || "<small style='color:#848e9c'>–</small>")
      + "<small style='display:block;margin-top:8px;color:#848e9c'>"+Lg("Checked every few seconds while this Workspace is open.","بيتشيّك كل كام ثانية طول ما الـWorkspace مفتوح.")+"</small></div>";
    ov.querySelector("[data-x]").onclick = () => ov.remove();
    const nb = ov.querySelector("[data-new]"); if (nb) nb.onclick = () => { ov.remove(); palarmDialog({sym}, onChange); };
    ov.querySelectorAll("[data-e]").forEach(b => b.onclick = () => { const a = PAlarm.list.find(x => x.id === b.dataset.e); ov.remove(); palarmDialog(a, onChange); });
    ov.querySelectorAll("[data-p]").forEach(b => b.onclick = () => { const a = PAlarm.list.find(x => x.id === b.dataset.p); a.on = !a.on; a.status = a.on ? "active" : "paused"; if (a.on){ delete a.lastClose; delete a.lastBar; } PAlarm.save(); PAlarm.start(); render(); onChange && onChange(); });
    ov.querySelectorAll("[data-d]").forEach(b => b.onclick = () => { PAlarm.del(b.dataset.d); render(); onChange && onChange(); });
  };
  render(); ov.onclick = e => { if (e.target === ov) ov.remove(); }; document.body.append(ov);
}

Object.assign(CandleChart.prototype, {
  paintPlus(c, m, PR, PB, dec){   // TradingView's + beside the price under the cursor (on the price axis side) -> alert menu
    this._plusB = null; if (!m || m.y >= PB || this.tool !== "cur" || !this.sym) return;
    const ax = this.W - this.axw, p = this.py2p(m.y); if (!isFinite(p)) return;
    if (m.x >= PR){ c.fillStyle = "#2b3139"; c.fillRect(ax+1, m.y-8, this.axw-2, 16); c.fillStyle = "#eaecef"; c.textAlign = "left"; c.fillText(p.toFixed(dec), ax+5, m.y); }
    const b = {x: ax - 17, y: m.y - 8, w: 16, h: 16, p}, hov = m.x >= b.x && m.x <= b.x + b.w && Math.abs(m.y - (b.y + 8)) <= 8;
    c.fillStyle = hov ? "#f0b90b" : "#2b3139"; c.fillRect(b.x, b.y, b.w, b.h); c.strokeStyle = hov ? "#000" : "#eaecef"; c.lineWidth = 1.5;
    c.beginPath(); c.moveTo(b.x+4, b.y+8); c.lineTo(b.x+12, b.y+8); c.moveTo(b.x+8, b.y+4); c.lineTo(b.x+8, b.y+12); c.stroke(); c.lineWidth = 1; this._plusB = b;
  },
  paintAlarms(c, py, PR, PB, dec){   // every alert of this symbol as a dashed orange line with a bell tag on the axis
    this._alHits = []; if (!this.sym) return; const ax = this.W - this.axw;
    PAlarm.forSym(this.sym).forEach(a => { if (PALARM_MOVE.has(a.cond)) return;
      [a.v].concat(PALARM_CH.has(a.cond) && a.v2 != null ? [a.v2] : []).forEach((v, i) => { const y = py(v); if (!(y > 0 && y < PB)) return;
        c.globalAlpha = a.on ? 1 : .45; c.strokeStyle = "#ff9800"; c.setLineDash([6,4]); c.beginPath(); c.moveTo(0, y+.5); c.lineTo(PR, y+.5); c.stroke(); c.setLineDash([]);
        c.fillStyle = "#ff9800"; c.fillRect(ax+1, y-8, this.axw-2, 16); c.fillStyle = "#000"; c.textAlign = "left"; c.fillText("⏰"+v.toFixed(dec), ax+3, y); c.globalAlpha = 1;
        const k = i ? "v2" : "v"; this._alHits.push({x: ax, y: y-8, w: this.axw, h: 16, a, k}, {x: 0, y: y-4, w: PR, h: 8, a, k}); }); });   // tag on the axis + the line itself
  },
  alarmDown(e){   // click on the + (alert menu) or on an alert tag (edit it); true = handled
    const r = this.cv.getBoundingClientRect(), mx = (e.clientX - r.left)/this.S, my = (e.clientY - r.top)/this.S, inB = b => b && mx >= b.x && mx <= b.x + b.w && my >= b.y && my <= b.y + b.h;
    const tag = (this._alHits || []).find(inB); if (tag){ this.alDrag = {a: tag.a, k: tag.k, y: e.clientY, mv: false}; try { this.cv.setPointerCapture(e.pointerId); } catch(_){} return true; }   // press on a line / tag: drag moves it, a click opens it (alarmUp)
    const b = this._plusB; if (!inB(b)) return false;
    document.querySelectorAll(".ctxm").forEach(x => x.remove());
    const menu = el("div", "ctxm"); menu.style.cssText = "position:fixed;z-index:2147483001;left:"+(e.clientX - 200)+"px;top:"+e.clientY+"px";
    const item = (label, fn) => { const bt = el("button", null, esc(label)); bt.onclick = () => { menu.remove(); fn(); }; menu.append(bt); };
    const p = +b.p.toFixed(8);
    item("⏰ "+Lg("Add alert on ","تنبيه على ")+this.sym+" "+Lg("at","عند")+" "+fmtP(p), () => palarmDialog({sym: this.sym, tf: this.tf, v: p}, () => this.draw()));
    item(Lg("Draw horizontal line at ","خط أفقي عند ")+fmtP(p), () => { const d = {id: Date.now()+Math.random(), type: "hline", pts: [{t: this.i2t(this.idx(b.x)), p}]}; this.draws.push(d); this.sel = d; this.saveDraws(); this.draw(); });
    item("⏰ "+Lg("Alerts","التنبيهات")+" ("+PAlarm.list.length+")", () => palarmManager(this.sym, () => this.draw()));
    document.body.append(menu);
    const off = ev => { if (ev && menu.contains(ev.target)) return; menu.remove(); document.removeEventListener("pointerdown", off, true); }; setTimeout(() => document.addEventListener("pointerdown", off, true), 0);
    return true;
  },
  alarmMove(e){   // dragging an alert line: its price follows the cursor (TradingView); true = handled
    const D = this.alDrag; if (!D) return false;
    if (!D.mv && Math.abs(e.clientY - D.y) < 4) return true; D.mv = true; this.cv.style.cursor = "ns-resize";
    const p = this.py2p(Math.max(0, Math.min(this.PB, this.mouse.y))); if (isFinite(p)) D.a[D.k] = +p.toFixed(8);
    this.drawSoon(); return true;
  },
  alarmUp(){   // end of a press on an alert: moved = save the new price, not moved = open the alert
    const D = this.alDrag; if (!D) return false; this.alDrag = null;
    if (D.mv){ delete D.a.lastClose; delete D.a.lastBar; PAlarm.save(); this.draw(); } else palarmDialog(D.a, () => this.draw());
    return true;
  }
});
if (typeof window !== "undefined") PAlarm.start();
