const RETIRED = {ready:"signals", ticker:null, links:null, video:null};   // owner OK 2026-10-17: duplicates / not part of the trading decision
Ws.build = list => { Ws.hist.mute++; try { list.map(([t,r,s]) => [t in RETIRED ? RETIRED[t] : t, r, s]).filter(([t]) => t).forEach(([t,r,s]) => new Panel(t, r, s)); } finally { Ws.hist.mute--; } Ws.checkEmpty(); };
Ws.cascade = 0;
Ws.add = type => {
  const o = (Ws.cascade++ % 8)*30 + 20;
  new Panel(type, {x:o,y:o,w:type==="chart"?560:340,h:type==="chart"?340:300}, {sym:SYMS[0], group:0});
  Ws.save();
};

/* XPiX Guide: a presenter on a small stage in the bottom-left corner of the visible screen. He comes on by himself after start-up
   (✕ sends him off, the side tab brings him back), talks in Egyptian Arabic, and points at the part of the screen he is explaining.
   Answers: built-in offline guide + Claude / Gemini through modules/guide_ai.py. New presenters = one more entry in GUIDE_CHARS. */
const GUIDE_ICON = '<svg width="18" height="18" style="display:block" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><rect x="0" y="0" width="200" height="200" rx="46" fill="#d4a537"/><g transform="translate(0,-20) translate(100,120) scale(.78) translate(-100,-120)"><rect x="80.00" y="52" width="8.5" height="68" fill="#0a0a0a"/><rect x="69.00" y="78" width="8.5" height="42" fill="#0a0a0a"/><rect x="58.00" y="94" width="8.5" height="26" fill="#0a0a0a"/><rect x="47.00" y="104" width="8.5" height="16" fill="#0a0a0a"/><rect x="36.00" y="110" width="8.5" height="10" fill="#0a0a0a"/><rect x="25.00" y="114" width="8.5" height="6" fill="#0a0a0a"/><rect x="111.50" y="120" width="8.5" height="52" fill="#0a0a0a"/><rect x="122.50" y="120" width="8.5" height="32" fill="#0a0a0a"/><rect x="133.50" y="120" width="8.5" height="20" fill="#0a0a0a"/><rect x="144.50" y="120" width="8.5" height="12" fill="#0a0a0a"/><rect x="155.50" y="120" width="8.5" height="8" fill="#0a0a0a"/><rect x="92" y="38" width="8" height="160" fill="#0a0a0a"/><rect x="101.5" y="15" width="8" height="160" fill="#f2f2f2"/></g></svg>';
const GUIDE_CHARS = [
  {id:"mrx", name:"Mr X", ar:"مستر X", female:false, video:"mrx", skin:"#c4895f", skin2:"#9c6440", hair:"#0e0c0b", suit:"#23272e", suit2:"#14171b", shirt:"#f4f5f6", tie:"#b8912e", trousers:"#1a1d22", shoe:"#0a0a0b", hairStyle:"short"},
  {id:"saad", name:"Saad", ar:"سعد", female:false, skin:"#d6a27c", skin2:"#b98060", hair:"#1f1712", suit:"#1c2633", suit2:"#121922", shirt:"#f1f3f5", tie:"#c9a227", trousers:"#161e28", shoe:"#0d0f12", hairStyle:"short"},
  {id:"noor", name:"Noor", ar:"نور", female:true, skin:"#e0b08c", skin2:"#c48f6c", hair:"#3a2418", suit:"#3d2c5c", suit2:"#2a1e40", shirt:"#ece6f5", tie:"", trousers:"#221a33", shoe:"#151018", hairStyle:"long"},
  {id:"capt", name:"Captain", ar:"الكابتن", female:false, skin:"#c58f68", skin2:"#a8734f", hair:"#121212", suit:"#123b2e", suit2:"#0b281f", shirt:"#123b2e", tie:"", trousers:"#2b2f36", shoe:"#111", hairStyle:"cap"}
];
function presenterSvg(C){
  const m = x => 200 - x, armL = '<path d="M50 132 Q43 178 45 212 L60 214 Q62 180 67 142 Z" fill="url(#gSuit)"/><path d="M45 208 Q43 252 47 290 L60 290 Q61 250 60 212 Z" fill="url(#gSuit)"/><rect x="45.5" y="284" width="15" height="6" rx="2" fill="'+C.shirt+'"/><ellipse cx="53" cy="300" rx="7.5" ry="11" fill="url(#gSkin)"/>';
  const armR = armL.replace(/M(\d+) (\d+) Q(\d+) (\d+) (\d+) (\d+) L(\d+) (\d+) Q(\d+) (\d+) (\d+) (\d+) Z/g, (s, a,b,c,d,e,f,g,h,i,j,k,l) => "M"+m(+a)+" "+b+" Q"+m(+c)+" "+d+" "+m(+e)+" "+f+" L"+m(+g)+" "+h+" Q"+m(+i)+" "+j+" "+m(+k)+" "+l+" Z")
    .replace('x="45.5"', 'x="139.5"').replace('cx="53"', 'cx="147"');
  const hairBack = C.hairStyle === "long" ? '<path d="M71 62 Q66 20 100 19 Q134 20 129 62 L134 128 Q124 138 116 118 L118 74 Q100 46 82 74 L84 118 Q76 138 66 128 Z" fill="'+C.hair+'"/>' : "";
  const hairFront = C.hairStyle === "cap" ? '<path d="M72 52 Q73 22 100 21 Q127 22 128 52 Z" fill="'+C.suit+'"/><path d="M122 49 Q140 50 146 56 L124 56 Z" fill="'+C.suit2+'"/><rect x="72" y="48" width="56" height="6" rx="3" fill="'+C.tie.replace(/^$/, "#e0a95a")+'"/>'
    : C.hairStyle === "long" ? '<path d="M73 58 Q74 26 100 25 Q126 26 127 58 Q118 40 100 42 Q84 41 73 58 Z" fill="'+C.hair+'"/>'
    : '<path d="M73 60 Q71 27 100 25 Q129 27 127 60 Q124 43 115 39 Q100 33 85 39 Q76 45 73 60 Z" fill="'+C.hair+'"/>';
  const neckwear = C.tie ? '<path d="M96.5 128 L103.5 128 L106 137 L102 202 L100 208 L98 202 L94 137 Z" fill="'+C.tie+'"/><path d="M96.5 128 L103.5 128 L102 136 L98 136 Z" fill="#00000033"/>'
    : C.female ? '<path d="M90 126 Q100 146 110 126" stroke="#e0c27a" stroke-width="1.4" fill="none"/><circle cx="100" cy="146" r="2.4" fill="#e0c27a"/>' : '<path d="M90 124 L100 140 L110 124" stroke="#ffffff55" stroke-width="2" fill="none"/>';
  return '<svg viewBox="0 0 200 520" preserveAspectRatio="xMidYMax meet"><defs>'
    + '<radialGradient id="gSkin" cx="45%" cy="40%" r="70%"><stop offset="0" stop-color="'+C.skin+'"/><stop offset="1" stop-color="'+C.skin2+'"/></radialGradient>'
    + '<linearGradient id="gSuit" x1="0" x2="1"><stop offset="0" stop-color="'+C.suit2+'"/><stop offset=".45" stop-color="'+C.suit+'"/><stop offset="1" stop-color="'+C.suit2+'"/></linearGradient>'
    + '<linearGradient id="gPants" x1="0" x2="1"><stop offset="0" stop-color="'+C.trousers+'"/><stop offset=".5" stop-color="'+C.trousers+'cc"/><stop offset="1" stop-color="'+C.trousers+'"/></linearGradient></defs>'
    + '<ellipse cx="100" cy="508" rx="48" ry="7" fill="#000" opacity=".45"/>'
    + '<g class="g-legL"><path d="M71 266 L99 266 L96 498 L77 498 Z" fill="url(#gPants)"/><path d="M70 496 Q86 492 99 498 L99 506 L68 506 Q66 500 70 496 Z" fill="'+C.shoe+'"/></g>'
    + '<g class="g-legR"><path d="M101 266 L129 266 L123 498 L104 498 Z" fill="url(#gPants)"/><path d="M101 498 Q114 492 130 496 Q134 500 132 506 L101 506 Z" fill="'+C.shoe+'"/></g>'
    + '<g class="g-body">' + hairBack
    + '<path d="M89 94 L111 94 L113 128 Q100 134 87 128 Z" fill="url(#gSkin)"/><path d="M89 104 Q100 112 111 104 L111 98 L89 98 Z" fill="#00000026"/>'
    + '<path d="M54 130 Q100 112 146 130 L151 192 Q147 240 137 284 L63 284 Q53 240 49 192 Z" fill="url(#gSuit)"/>'
    + '<path d="M87 121 L100 168 L113 121 Z" fill="'+C.shirt+'"/>' + neckwear
    + '<path d="M87 121 L100 170 L83 152 L77 129 Z" fill="'+C.suit2+'"/><path d="M113 121 L100 170 L117 152 L123 129 Z" fill="'+C.suit2+'"/>'
    + '<circle cx="100" cy="222" r="2.2" fill="'+C.suit2+'"/><circle cx="100" cy="248" r="2.2" fill="'+C.suit2+'"/>'
    + '<g class="g-armL">'+armL+'</g><g class="g-armR">'+armR+'</g>'
    + '<g class="g-head"><ellipse cx="74" cy="67" rx="4.5" ry="8" fill="'+C.skin2+'"/><ellipse cx="126" cy="67" rx="4.5" ry="8" fill="'+C.skin2+'"/>'
    + '<path d="M74 58 Q73 96 100 103 Q127 96 126 58 Q126 30 100 30 Q74 30 74 58 Z" fill="url(#gSkin)"/>'
    + '<path d="M80 84 Q100 106 120 84 Q116 100 100 103 Q84 100 80 84 Z" fill="#00000018"/>' + hairFront
    + '<path d="M84 53 Q90 49 96 52" stroke="'+C.hair+'" stroke-width="2.4" fill="none" stroke-linecap="round"/><path d="M104 52 Q110 49 116 53" stroke="'+C.hair+'" stroke-width="2.4" fill="none" stroke-linecap="round"/>'
    + '<ellipse cx="90" cy="62" rx="5.2" ry="3.2" fill="#fbfbf8"/><ellipse cx="110" cy="62" rx="5.2" ry="3.2" fill="#fbfbf8"/>'
    + '<circle class="g-iris" cx="90.5" cy="62" r="2.5" fill="#4a3324"/><circle class="g-iris" cx="110.5" cy="62" r="2.5" fill="#4a3324"/><circle cx="90.5" cy="62" r="1.1" fill="#111"/><circle cx="110.5" cy="62" r="1.1" fill="#111"/>'
    + '<g class="g-lid"><rect x="84" y="57.5" width="12.5" height="9" fill="'+C.skin+'"/><rect x="103.5" y="57.5" width="12.5" height="9" fill="'+C.skin+'"/></g>'
    + '<path d="M100 61 Q98 73 94.5 78 Q100 81.5 105.5 78" stroke="'+C.skin2+'" stroke-width="1.6" fill="none" stroke-linecap="round"/>'
    + '<ellipse class="g-mo" cx="100" cy="89" rx="6" ry="3.2" fill="#3a1410"/><path class="g-lip" d="M92 88.5 Q100 92.5 108 88.5" stroke="#9a5040" stroke-width="2" fill="none" stroke-linecap="round"/>'
    + (C.female ? "" : '<path d="M80 80 Q84 98 100 102 Q116 98 120 80 Q116 96 100 99 Q84 96 80 80 Z" fill="'+C.hair+'" opacity=".16"/>')
    + '</g></g></svg>';
}
const GVoice = {   // Egyptian voice first; long answers are spoken in short pieces (one long utterance gets cut off in some browsers)
  timer:0,
  pick(isAr, female){ if (!Voice.ok) return null; const vs = speechSynthesis.getVoices(), ar = vs.filter(v => /^ar/i.test(v.lang)), eg = ar.filter(v => /ar[-_]EG/i.test(v.lang)), pool = isAr ? (eg.length ? eg : ar) : vs.filter(v => /^en/i.test(v.lang));
    const g = female ? /Salma|Zariyah|Hoda|Laila|Amira|Female|female/ : /Shakir|Hamed|Maged|Tarik|Naayf|Male\b|male\b/, nat = v => /Natural|Online|Neural|Google/.test(v.name);
    return pool.find(v => g.test(v.name) && nat(v)) || pool.find(nat) || pool.find(v => g.test(v.name)) || pool[0] || null; },
  say(text, female, onStart, onEnd){ if (!Voice.ok) { onEnd && onEnd(); return; } this.stop(); const t = Voice.clean(text); if (!t){ onEnd && onEnd(); return; }
    const isAr = /[؀-ۿ]/.test(t), v = this.pick(isAr, female), parts = t.match(/[^.!?؟\n،,]+[.!?؟\n،,]*/g) || [t], ch = []; let cur = "";
    parts.forEach(p => { if (cur && (cur + p).length > 150){ ch.push(cur); cur = p; } else cur += p; }); if (cur.trim()) ch.push(cur);
    ch.forEach((c, i) => { const u = new SpeechSynthesisUtterance(c.trim()); if (v){ u.voice = v; u.lang = v.lang; } else u.lang = isAr ? "ar-EG" : "en-US"; u.rate = +store.get(LS+"_grate", "1") || 1; u.pitch = female ? 1.05 : .95;
      if (!i) u.onstart = () => onStart && onStart(); if (i === ch.length - 1) u.onend = () => { this.stop(true); onEnd && onEnd(); };
      u.onerror = e => { this.stop(true); onEnd && onEnd(e && e.error); }; speechSynthesis.speak(u); });
    if (v && /Google/.test(v.name)) this.timer = setInterval(() => { if (!speechSynthesis.speaking) return clearInterval(this.timer); speechSynthesis.pause(); speechSynthesis.resume(); }, 9000); },
  stop(keep){ clearInterval(this.timer); if (!keep && Voice.ok) speechSynthesis.cancel(); }
};
/* Gemini Live: a real voice call with Mr X - microphone streamed as 16 kHz PCM, his voice played back as 24 kHz PCM, the model hears and answers
   at the same time and stops when you talk over him (barge-in). The server hands out a one-use token (modules/guide_ai.py live_token); the key never comes here. */
const GLive = {
  ws:null, on:false, ctxIn:null, ctxOut:null, src:null, proc:null, stream:null, nextT:0, playing:[], said:"", heard:"", an:null,
  b64(buf){ let s = ""; const u = new Uint8Array(buf); for (let i = 0; i < u.length; i += 0x8000) s += String.fromCharCode.apply(null, u.subarray(i, i + 0x8000)); return btoa(s); },
  async token(){ const b = Guide.bridge(); if (!b || !b.live) return {err:"nokey-live"}; const id = "L" + Date.now().toString(36);
    return await new Promise(res => { const to = setTimeout(() => { window.__xpixGuideAnswer = null; res({err:"timeout"}); }, 20000);
      window.__xpixGuideAnswer = a => { if (a.id !== id) return; clearTimeout(to); window.__xpixGuideAnswer = null; res(a); }; b.ask({id, live:true}); }); },
  async start(o){ o = o || {mic:true}; if (this.on) return; const G = Guide; G.speak(o.mic ? G.G("Connecting the call…", "بوصّل المكالمة…") : G.G("One sec…", "ثانية…"), null, true);
    let mic = null; if (o.mic){ try { mic = await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:true, noiseSuppression:true, autoGainControl:true, channelCount:1}}); }
      catch(e){ G.speak(G.G("I can't hear you: allow the microphone for this site (lock icon next to the address).", "مش سامعك: اسمح للميكروفون للموقع ده (من القفل جنب العنوان)."), null, true); return false; } }
    const t = await this.token(); if (!t || !t.token){ mic && mic.getTracks().forEach(x => x.stop()); G.speak(this.errText(t), null, true); return false; }
    this.stream = mic; this._text = o.text || ""; this.on = true; this.said = ""; this.heard = ""; this.poke();   // no mic = "voice" mode: typed questions answered with Gemini's own voice
    const url = "wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContentConstrained?access_token=" + encodeURIComponent(t.token);
    const ws = this.ws = new WebSocket(url);
    ws.onopen = () => ws.send(JSON.stringify({setup:{model:"models/" + t.model}}));
    ws.onmessage = async ev => { let m; try { m = JSON.parse(typeof ev.data === "string" ? ev.data : await ev.data.text()); } catch(e){ return; } this.msg(m); };
    ws.onclose = ev => { const was = this.on, call = !!this.stream; this.stop(true); if (was && (call || ev.code !== 1000)) G.speak(ev.code === 1000 ? G.G("Call ended. Tap Live to call again.", "المكالمة خلصت. دوس «مكالمة» عشان تكلمني تاني.") : G.G("The call dropped (" + ev.code + (ev.reason ? " " + ev.reason : "") + ").", "المكالمة وقعت (" + ev.code + (ev.reason ? " " + ev.reason : "") + ")."), null, true); };
    ws.onerror = () => {};
    return true; },
  errText(t){ const G = Guide, e = (t && t.err) || "";
    return e === "nokey-live" ? G.G("Live calls need GEMINI_API_KEY in Secrets.", "المكالمة الحية محتاجة GEMINI_API_KEY في Secrets.") : e === "cap" ? G.G("Today's call limit is reached.", "خلصت مكالمات النهارده.")
      : G.G("Couldn't start the call (" + e + (t && t.msg ? ": " + t.msg : "") + ").", "معرفتش أبدأ المكالمة (" + e + (t && t.msg ? ": " + t.msg : "") + ")."); },
  poke(){ clearTimeout(this._idle); if (!this.stream) this._idle = setTimeout(() => { if (this.on && !this.stream && !this.playing.length) this.stop(true); }, 120000); },   // voice mode closes after 2 quiet minutes
  async text(q){ if (this.on && this.ws && this.ws.readyState === 1){ this.poke(); this.said = ""; this.send({clientContent:{turns:[{role:"user", parts:[{text:q}]}], turnComplete:true}}); return true; }
    if (this.on) return false; return await this.start({mic:false, text:q}); },
  outInit(){ const C = window.AudioContext || window.webkitAudioContext; if (!this.ctxOut || this.ctxOut.state === "closed"){ this.ctxOut = new C({sampleRate:24000}); this.an = null; }
    try { this.ctxOut.resume(); } catch(e){} if (!this.an){ this.an = this.ctxOut.createAnalyser(); this.an.fftSize = 512; this.an.connect(this.ctxOut.destination); } this.lip(); },
  micOn(){ const C = window.AudioContext || window.webkitAudioContext; this.ctxIn = new C({sampleRate:16000});
    this.src = this.ctxIn.createMediaStreamSource(this.stream); this.proc = this.ctxIn.createScriptProcessor(2048, 1, 1);
    this.proc.onaudioprocess = e => { if (!this.ws || this.ws.readyState !== 1) return; const f = e.inputBuffer.getChannelData(0), pcm = new Int16Array(f.length);
      for (let i = 0; i < f.length; i++){ const v = Math.max(-1, Math.min(1, f[i])); pcm[i] = v < 0 ? v*0x8000 : v*0x7fff; }
      this.ws.send(JSON.stringify({realtimeInput:{audio:{data:this.b64(pcm.buffer), mimeType:"audio/pcm;rate=16000"}}})); };
    const mute = this.ctxIn.createGain(); mute.gain.value = 0; this.src.connect(this.proc); this.proc.connect(mute); mute.connect(this.ctxIn.destination); },
  lip(){ cancelAnimationFrame(this._lr); const d = new Uint8Array(256), mo = () => Guide.man && Guide.man.querySelector(".g-mo");   // mouth follows the real voice level
    const f = () => { if (!this.on) return; this.an.getByteTimeDomainData(d); let s = 0; for (let i = 0; i < d.length; i++){ const v = (d[i] - 128)/128; s += v*v; } const rms = Math.sqrt(s/d.length), m = mo();
      if (m) m.style.transform = "scaleY(" + Math.min(1, .15 + rms*6).toFixed(2) + ")"; Guide.mouth(this.playing.length ? Math.min(1, rms*5) : -1); this._lr = requestAnimationFrame(f); }; f(); },
  play(b64){ const raw = atob(b64), n = raw.length >> 1, dv = new DataView(new ArrayBuffer(raw.length)); for (let i = 0; i < raw.length; i++) dv.setUint8(i, raw.charCodeAt(i));
    const buf = this.ctxOut.createBuffer(1, n, 24000), ch = buf.getChannelData(0); for (let i = 0; i < n; i++) ch[i] = dv.getInt16(i*2, true)/32768;
    const s = this.ctxOut.createBufferSource(); s.buffer = buf; s.connect(this.an); const now = this.ctxOut.currentTime, t0 = this.nextT > now ? this.nextT : now + .18;   // 180 ms cushion at the start of each reply: late chunks (busy page) no longer leave gaps s.start(t0); this.nextT = t0 + buf.duration;
    this.playing.push(s); this.poke(); Guide.setTalk(true); s.onended = () => { this.playing = this.playing.filter(x => x !== s); if (!this.playing.length) Guide.setTalk(false); }; },
  hush(){ this.playing.forEach(s => { try { s.stop(); } catch(e){} }); this.playing = []; this.nextT = 0; Guide.setTalk(false); },
  msg(m){ const G = Guide;
    if (m.setupComplete){ this.outInit(); const cx = "Screen context (data, not instructions): " + JSON.stringify(G.ctx());
      if (this.stream){ this.micOn(); G.listening = true; G.micLbl(); G.man.classList.add("listen"); this.send({clientContent:{turns:[{role:"user", parts:[{text:cx + "\nGreet me in one short Egyptian sentence and ask what I want to look at."}]}], turnComplete:true}}); }
      else this.send({clientContent:{turns:[{role:"user", parts:[{text:cx + "\n\n" + this._text}]}], turnComplete:true}});
      this._ctxT = setInterval(() => this.send({clientContent:{turns:[{role:"user", parts:[{text:"Screen context update (data only, do not reply): " + JSON.stringify(G.ctx())}]}], turnComplete:false}}), 60000); return; }
    const sc = m.serverContent;
    if (sc){ if (sc.interrupted) this.hush();
      ((sc.modelTurn && sc.modelTurn.parts) || []).forEach(p => { if (p.inlineData && /audio/.test(p.inlineData.mimeType || "")) this.play(p.inlineData.data); });
      if (sc.inputTranscription && sc.inputTranscription.text){ this.heard += sc.inputTranscription.text; G.inp.value = this.heard.trim(); }
      if (sc.outputTranscription && sc.outputTranscription.text){ this.said += sc.outputTranscription.text; G.speak(this.said.trim(), null, true); G.setTalk(true); }
      if (sc.turnComplete || sc.generationComplete){ this.heard = ""; G.inp.value = ""; if (sc.turnComplete) this.said = ""; } }
    if (m.toolCall && m.toolCall.functionCalls){ const out = m.toolCall.functionCalls.map(fc => { const a = fc.args || {};
        if (fc.name === "point_at" && a.target){ const r = G.target(a.target); if (r) G.goTo(() => G.target(a.target)); return {id:fc.id, name:fc.name, response:{result: r ? "pointing" : "that widget is not open"}}; }
        if (fc.name === "open_page"){ const pg = {scanner:1, lab:2, playbook:3, stats:4, alerts_page:6}[a.page]; if (pg){ G.up(); setTimeout(() => G.page(pg), 1200); } return {id:fc.id, name:fc.name, response:{result:"ok"}}; }
        return {id:fc.id, name:fc.name, response:{result:"unknown"}}; });
      this.send({toolResponse:{functionResponses:out}}); }
    if (m.goAway) G.speak(G.G("The call will end soon (time limit).", "المكالمة هتخلص قريب (حد الوقت)."), null, true); },
  send(o){ try { if (this.ws && this.ws.readyState === 1) this.ws.send(JSON.stringify(o)); } catch(e){} },
  stop(quiet){ const was = this.on; this.on = false; clearInterval(this._ctxT); clearTimeout(this._idle); cancelAnimationFrame(this._lr);
    try { this.ws && this.ws.readyState <= 1 && this.ws.close(1000); } catch(e){} this.ws = null; this.hush();
    try { this.proc && this.proc.disconnect(); this.src && this.src.disconnect(); this.ctxIn && this.ctxIn.close(); } catch(e){} this.proc = this.src = this.ctxIn = null;
    if (this.stream){ this.stream.getTracks().forEach(t => t.stop()); this.stream = null; }
    if (Guide.man){ Guide.man.classList.remove("live"); const mo = Guide.man.querySelector(".g-mo"); if (mo) mo.style.transform = ""; }
    if (was || !quiet){ Guide.listening = false; Guide.man && Guide.man.classList.remove("listen"); Guide.micLbl && Guide.micLbl(); Guide.bot && Guide.bot(); } }
};
const Guide = {
  on:false, busy:0,
  chr(){ const id = store.get(LS+"_gchar", "mrx"); return GUIDE_CHARS.find(c => c.id === id) || GUIDE_CHARS[0]; },
  talkAr(){ return store.get(LS+"_glang", "ar") !== "en"; },   // Egyptian Arabic first (owner), English only when picked
  voiceOn(){ return store.get(LS+"_gvoice2", true) !== false; },
  G(a, b){ return this.talkAr() ? b : a; },
  init(){
    if (this.root) return; const r = this.root = el("div"); r.id = "guide";
    r.innerHTML = '<div class="g-tab"></div><div class="g-stage"><div class="g-light"></div><div class="g-floor"></div><div class="g-eback"></div><svg class="g-stairs" viewBox="0 0 200 100" preserveAspectRatio="none"></svg><div class="g-man"></div>'
      + '<div class="g-efront"><div class="g-ind"><i>▼</i><b>27</b></div><div class="g-dl"></div><div class="g-dr"></div></div><div class="g-lift"></div><div class="g-tag"></div><button class="g-x" type="button">✕</button></div>'
      + '<svg class="g-beam"></svg><div class="g-bub"><div class="g-hd"><span class="g-ic">'+GUIDE_ICON+'</span><b class="g-nm"></b><span class="g-sp"></span><button type="button" class="g-sm" data-d="-1">A−</button><button type="button" class="g-sm" data-d="1">A+</button><button type="button" class="g-opt">⚙</button><button type="button" class="g-fold">▾</button></div>'
      + '<div class="g-bd"><div class="g-say"></div><div class="g-acts"></div><form class="g-ask"><button type="button" class="g-mic"></button><input placeholder=""><button type="submit">↵</button></form><div class="g-bot"></div></div></div>';
    document.body.append(r);
    r.querySelector(".g-opt").onclick = () => { this.bub.classList.toggle("opts"); this.placeBub(); };
    r.querySelector(".g-fold").onclick = () => { const f = !this.bub.classList.contains("fold"); this.bub.classList.toggle("fold", f); store.set(LS+"_gfold", f); this.placeBub(); };
    r.querySelectorAll(".g-sm").forEach(b => b.onclick = () => { const z = Math.max(0, Math.min(2, (+store.get(LS+"_gbsz", 0)) + (+b.dataset.d))); store.set(LS+"_gbsz", z); this.look(); });
    this.mic = r.querySelector(".g-mic"); this.mic.onclick = () => { const br = this.bridge(); if (br && br.live){ if (GLive.on && GLive.stream) GLive.stop(); else { if (GLive.on) GLive.stop(true); GVoice.stop(); this.man.classList.add("live"); GLive.start().then(() => this.bot()); } this.bot(); return; } this.listening ? this.stopListen(true) : this.listen(); }; this.stage = r.querySelector(".g-stage"); this.tab = r.querySelector(".g-tab"); this.man = r.querySelector(".g-man"); this.bub = r.querySelector(".g-bub"); this.say_ = r.querySelector(".g-say"); this.acts = r.querySelector(".g-acts"); this.beam = r.querySelector(".g-beam");
    this.inp = r.querySelector(".g-ask input"); r.querySelector(".g-ask").onsubmit = e => { e.preventDefault(); const q = this.inp.value.trim(); if (q){ this.inp.value = ""; this.ask(q); } };
    this.man.onclick = () => this.bub.classList.toggle("hide"); this.tab.onclick = () => this.open(); r.querySelector(".g-x").onclick = () => this.close();
    this.paint(); this.bot(); this.look(); this.life(); window.addEventListener("resize", () => this.dock());
    let q = 0; const onSc = () => { if (q) return; q = requestAnimationFrame(() => { q = 0; this.dock(); }); };   // the stage stays in the visible corner while the page scrolls
    try { window.parent.addEventListener("scroll", onSc, true); window.parent.addEventListener("resize", onSc); } catch(e){} this.dock(); setTimeout(() => this.dock(), 800);
    document.addEventListener("pointerdown", () => { if (this._pending){ const t = this._pending; this._pending = ""; this.voice(t); } }, true);   // browsers only allow speech after the first tap: say the greeting then
  },
  async media(c){   // real presenter: static/<id>/idle.mp4 + talk.mp4 (or photo.jpg) served by Streamlit (enableStaticServing); checked once per presenter
    if (!c.video) return null; this._media = this._media || {}; if (c.video in this._media) return this._media[c.video];
    const bases = []; try { const L = window.parent.location; bases.push(new URL("app/static/" + c.video + "/", L.href).href, L.origin + "/app/static/" + c.video + "/", L.origin + "/~/+/app/static/" + c.video + "/"); } catch(e){ return this._media[c.video] = null; }
    const img = u => new Promise(res => { const i = new Image(), to = setTimeout(() => res(false), 8000); i.onload = () => { clearTimeout(to); res(i.naturalWidth > 10); }; i.onerror = () => { clearTimeout(to); res(false); }; i.src = u; });   // a real picture loads; an HTML error page does not
    const vid = async u => { try { const r = await fetch(u, {cache:"no-store"}); const ok = r.ok && /^video\//.test(r.headers.get("content-type") || ""); try { r.body && r.body.cancel(); } catch(e){} return ok; } catch(e){ return false; } };
    for (const base of [...new Set(bases)]){   // Streamlit Cloud serves the app under another path than a local run: try each address
      const [idle, photo] = await Promise.all([vid(base + "idle.mp4"), img(base + "photo.jpg")]);
      if (idle){ const talk = await vid(base + "talk.mp4"); return this._media[c.video] = {idle:base+"idle.mp4", talk:talk ? base+"talk.mp4" : base+"idle.mp4"}; }
      if (photo){ const [mid, open, blink] = await Promise.all(["mid.jpg", "open.jpg", "blink.jpg"].map(f => img(base + f)));
        return this._media[c.video] = {photo:base+"photo.jpg", mid:mid ? base+"mid.jpg" : "", open:open ? base+"open.jpg" : "", blink:blink ? base+"blink.jpg" : ""}; } }
    const E = CFG.mrx || {}; if (c.video === "mrx" && E.photo) return this._media[c.video] = {photo:E.photo, mid:E.mid || "", open:E.open || "", blink:E.blink || ""};   // fallback: small copies sent inside the page
    return this._media[c.video] = null; },
  mouth(lvl){   // real photo + mouth frames: closed / mid / open picked from the live voice level (0..1), or -1 = idle
    const f = this.man.querySelector(".g-face"); if (!f) return; const k = lvl < 0 ? "photo" : lvl < .1 ? "photo" : lvl < .32 ? "mid" : "open";
    if (f.dataset.k !== k && !f.classList.contains("blinking")){ f.dataset.k = k; f.querySelectorAll("img").forEach(i => i.classList.toggle("on", i.dataset.k === k || (i.dataset.k === "photo" && !f.querySelector('img[data-k="'+k+'"]')))); } },
  faceLife(){ clearTimeout(this._fb); clearInterval(this._fm); const f = this.man.querySelector(".g-face"); if (!f) return;
    const bl = f.querySelector('img[data-k="blink"]'); if (bl){ const go = () => { this._fb = setTimeout(() => { if (!this.man.querySelector(".g-face")) return; f.classList.add("blinking"); f.querySelectorAll("img").forEach(i => i.classList.toggle("on", i === bl)); setTimeout(() => { f.classList.remove("blinking"); f.dataset.k = ""; this.mouth(-1); go(); }, 140); }, 2800 + Math.random()*3500); }; go(); }
    this._fm = setInterval(() => { if (GLive.on) return; if (this.man.classList.contains("talk")) this.mouth(Math.random()); else this.mouth(-1); }, 115); },   // no live voice level (browser voice / text): plausible mouth movement while talking
  setTalk(on){ this.man.classList.toggle("talk", !!on); const t = this.man.querySelector(".g-v-talk"), i = this.man.querySelector(".g-v-idle");
    if (t && i && t.src !== i.src){ try { if (on){ t.currentTime = 0; const pr = t.play(); pr && pr.catch(() => {}); } else t.pause(); } catch(e){} } },
  idb(mode, fn){ return new Promise(res => { try { const rq = indexedDB.open("xpix_media", 1); rq.onupgradeneeded = () => rq.result.createObjectStore("f");
      rq.onsuccess = () => { try { const tx = rq.result.transaction("f", mode), st = tx.objectStore("f"), r = fn(st); tx.oncomplete = () => res(r && r.result !== undefined ? r.result : true); tx.onerror = () => res(null); } catch(e){ res(null); } }; rq.onerror = () => res(null); } catch(e){ res(null); } }); },
  async myVid(){ if (!store.get(LS+"_gvid", false)) return null; if (this._myVid) return this._myVid; const idle = await this.idb("readonly", st => st.get("idle")), talk = await this.idb("readonly", st => st.get("talk"));
    if (!(idle instanceof Blob)) return null; return this._myVid = {idle:URL.createObjectURL(idle), talk:talk instanceof Blob ? URL.createObjectURL(talk) : URL.createObjectURL(idle)}; },
  myFace(){ const f = store.get(LS+"_gface", null); return f && f.photo ? f : null; },   // photos picked with "Mr X photos" (kept in this browser only)
  pickFace(){ const inp = el("input"); inp.type = "file"; inp.accept = "image/*,video/*"; inp.multiple = true;
    inp.onchange = async () => { const vids = [...inp.files].filter(f => /^video\//.test(f.type)).slice(0, 2);
      if (vids.length){ const t = vids.find(f => /talk|كلام|speak/i.test(f.name)) || vids[1], i = vids.find(f => f !== t) || vids[0];   // videos (ProMoat / Veo...): idle loop + talking loop, kept in this browser (IndexedDB)
        await this.idb("readwrite", st => { st.put(i, "idle"); if (t) st.put(t, "talk"); else st.delete("talk"); }); store.set(LS+"_gvid", true); this._myVid = null; store.set(LS+"_gchar", "mrx"); await this.paint(); this.bot(); this.speak(this.G("Done - that's me now.", "تمام، ده شكلي دلوقتي."), null, true); return; }
      const fs = [...inp.files].slice(0, 4); if (!fs.length) return;
      const shrink = f => new Promise(res => { const im = new Image(), u = URL.createObjectURL(f); im.onload = () => { const k = Math.min(1, 900/Math.max(im.width, im.height)), cv = document.createElement("canvas"); cv.width = Math.round(im.width*k); cv.height = Math.round(im.height*k); cv.getContext("2d").drawImage(im, 0, 0, cv.width, cv.height); URL.revokeObjectURL(u); res(cv.toDataURL("image/jpeg", .82)); }; im.onerror = () => res(""); im.src = u; });
      const named = await Promise.all(fs.map(async f => [f.name.toLowerCase(), await shrink(f)])), out = {};
      const role = n => /blink|eye|عين/.test(n) ? "blink" : /open|aa|مفتوح/.test(n) ? "open" : /mid|half|نص/.test(n) ? "mid" : "";
      named.forEach(([n, d]) => { const r = role(n); if (r && !out[r]) out[r] = d; }); named.forEach(([n, d]) => { if (!Object.values(out).includes(d)){ const r = ["photo", "mid", "open", "blink"].find(k => !out[k]); if (r) out[r] = d; } });
      try { store.set(LS+"_gface", out); } catch(e){ this.speak(this.G("Photos too big for this browser.", "الصور كبيرة على المتصفح.")); return; }
      store.set(LS+"_gchar", "mrx"); this._media = {}; await this.paint(); this.bot(); this.speak(this.G("Done - that's me now.", "تمام، ده شكلي دلوقتي."), null, true); };
    inp.click(); },
  async paint(){ const c = this.chr(), mv = c.video ? await this.myVid() : null, mf = !mv && c.video ? this.myFace() : null, md = mv || (mf ? {photo:mf.photo, mid:mf.mid || "", open:mf.open || "", blink:mf.blink || ""} : await this.media(c)); this.man.classList.toggle("real", !!md);
    this.man.innerHTML = md && md.idle ? '<div class="g-vid"><video class="g-v-idle" src="'+md.idle+'" muted loop playsinline autoplay></video><video class="g-v-talk" src="'+md.talk+'" muted loop playsinline preload="auto"></video></div>'
      : md && md.photo ? '<div class="g-vid g-face" data-k="photo">' + [["photo", md.photo], ["mid", md.mid], ["open", md.open], ["blink", md.blink]].filter(x => x[1]).map(([k, u], i) => '<img class="g-v-photo'+(i ? "" : " on")+'" data-k="'+k+'" src="'+u+'" alt="">').join("") + '</div>' : presenterSvg(c); this.faceLife(); this.root.querySelector(".g-tag").textContent = this.G(c.name, c.ar);
    this.tab.textContent = this.G(c.name, c.ar); this.root.querySelector(".g-nm").textContent = this.G(c.name, c.ar); this.micLbl(); this.inp.placeholder = this.G("Ask me anything… what is the profile? where is the lab?", "اسألني أي حاجة… البروفيل ده إيه؟ فين اللاب؟"); },
  bot(){ const b = this.root.querySelector(".g-bot"); b.innerHTML = "";
    const cs = el("select"); GUIDE_CHARS.forEach(c => cs.append(Object.assign(el("option"), {value:c.id, textContent:this.G(c.name, c.ar)}))); cs.value = this.chr().id; cs.title = this.G("Presenter", "المذيع");
    cs.onchange = () => { store.set(LS+"_gchar", cs.value); this.paint(); this.hi(); };
    const lb = el("button", null, this.talkAr() ? "EN" : "ع"); lb.title = this.G("Answer language", "لغة الرد"); lb.onclick = () => { store.set(LS+"_glang", this.talkAr() ? "en" : "ar"); this.paint(); this.bot(); this.hi(); };
    const vb = el("button", null, this.voiceOn() ? this.G("Voice on", "الصوت شغال") : this.G("Voice off", "الصوت مقفول")); vb.onclick = () => { store.set(LS+"_gvoice2", !this.voiceOn()); GVoice.stop(); this.bot(); };
    const tb = el("button", null, this.G("Tour", "جولة")); tb.onclick = () => this.tour();
    const br = this.bridge(), live = !!(br && br.live), cb = live ? el("button", GLive.on && GLive.stream ? "on" : null, GLive.on && GLive.stream ? this.G("● Live call (end)", "● مكالمة حية (إنهاء)") : this.G("Live call", "مكالمة حية"))
      : el("button", this.chat ? "on" : null, this.chat ? this.G("Chat mode: on", "وضع الدردشة: شغال") : this.G("Chat mode", "وضع الدردشة"));
    cb.title = live ? this.G("Talk to Mr X like a phone call: he hears you while he talks, interrupt him any time (Gemini Live)", "كلّم مستر X زي مكالمة: بيسمعك وهو بيتكلم وتقدر تقاطعه في أي وقت (Gemini Live)") : this.G("Hands-free: after each answer he listens again", "من غير إيدك: بعد كل رد يسمعك تاني");
    cb.onclick = () => { if (live){ if (GLive.on && GLive.stream) GLive.stop(); else { if (GLive.on) GLive.stop(true); GVoice.stop(); this.man.classList.add("live"); GLive.start().then(() => this.bot()); } this.bot(); return; }
      this.chat = !this.chat; this.bot(); if (this.chat){ if (!this.voiceOn()) store.set(LS+"_gvoice2", true); this.bot(); this.listen(); } else this.stopListen(true); };
    const row = (label, ...els) => { const d = el("label", "g-row"); d.append(el("span", null, label), ...els); return d; };
    const sel = (key, def, opts, after) => { const x = el("select"); opts.forEach(([v, t]) => x.append(Object.assign(el("option"), {value:v, textContent:t}))); x.value = String(store.get(LS+key, def)); x.onchange = () => { store.set(LS+key, x.value); after && after(); }; return x; };
    const tog = (key, def, after) => { const x = el("input"); x.type = "checkbox"; x.checked = store.get(LS+key, def) !== false; x.onchange = () => { store.set(LS+key, x.checked); after && after(); }; return x; };
    const sz = sel("_gpsz", "m", [["s", this.G("Small", "صغير")], ["m", this.G("Medium", "وسط")], ["l", this.G("Large", "كبير")]], () => this.look());
    const rt = sel("_grate", "1", [[".85", this.G("Slow", "بطيء")], ["1", this.G("Normal", "عادي")], ["1.15", this.G("Fast", "سريع")]]);
    const clr = el("button", null, this.G("New chat", "محادثة جديدة")); clr.onclick = () => { const br = this.bridge(); if (br) br.ask({id:"r"+Date.now(), reset:true}); this.speak(this.G("Fresh start. What's on your mind?", "صفحة جديدة. في دماغك إيه؟")); };
    b.append(el("div", "g-btns"), row(this.G("Presenter", "المذيع"), cs), row(this.G("Presenter size", "حجم المذيع"), sz), row(this.G("Show presenter", "إظهار المذيع"), tog("_gstage", true, () => this.look())),
      row(this.G("Voice speed", "سرعة الصوت"), rt), row(this.G("Mr X photos / videos", "صور / فيديو مستر X"), Object.assign(el("button", null, (this.myFace() || store.get(LS+"_gvid", false)) ? this.G("Change", "تغيير") : this.G("Upload", "رفع")), {onclick:() => this.pickFace()}), ...((this.myFace() || store.get(LS+"_gvid", false)) ? [Object.assign(el("button", null, "✕"), {title:this.G("Back to the drawing", "رجوع للرسم"), onclick:() => { store.set(LS+"_gface", null); store.set(LS+"_gvid", false); this._myVid = null; this.idb("readwrite", st => st.clear()); this._media = {}; this.paint(); this.bot(); }})] : [])), row(this.G("Come on by himself at start", "يطلع لوحده مع التشغيل"), tog("_gon", true)));
    b.firstChild.append(lb, vb, cb, tb, clr); },
  life(){ clearTimeout(this._lt); this._lt = setTimeout(() => { if (this.on && !this._fx && !this.man.classList.contains("talk") && !this.listening){ const h = this.man.querySelector(".g-head");
      if (h) h.animate([{transform:"rotate(0)"}, {transform:"rotate(" + (Math.random() < .5 ? -5 : 4) + "deg)", offset:.3}, {transform:"rotate(0)"}], {duration:2600, easing:"ease-in-out"}); } this.life(); }, 7000 + Math.random()*7000); },
  look(){ if (!this.root) return; const z = +store.get(LS+"_gbsz", 0); this.bub.dataset.sz = z; this.bub.classList.toggle("fold", !!store.get(LS+"_gfold", false));
    this.root.classList.toggle("nostage", store.get(LS+"_gstage", true) === false); this.dock(); this.placeBub(); },
  SR(){ return window.SpeechRecognition || window.webkitSpeechRecognition || null; },
  micLbl(){ if (!this.mic) return; const ok = !!this.SR(); this.mic.disabled = !ok; this.mic.textContent = GLive.on && GLive.stream ? this.G("● On call", "● في مكالمة") : this.listening ? this.G("● Listening", "● بسمعك") : this.G("Talk", "اتكلم");
    this.mic.classList.toggle("on", !!this.listening); this.mic.title = ok ? this.G("Speak your question (Chrome / Edge; the browser sends the audio to its speech service)", "قول سؤالك بصوتك (كروم أو إيدج؛ المتصفح بيبعت الصوت لخدمة التعرّف بتاعته)") : this.G("This browser can't listen - use Chrome or Edge", "المتصفح ده مش بيسمع - استخدم كروم أو إيدج"); },
  listen(){ const SR = this.SR(); if (!SR || this.listening) return; GVoice.stop(); this.setTalk(false);
    const r = this._rec = new SR(); r.lang = this.talkAr() ? "ar-EG" : "en-US"; r.interimResults = true; r.continuous = false; r.maxAlternatives = 1; let fin = "";
    r.onresult = e => { let t = ""; for (let i = e.resultIndex; i < e.results.length; i++){ const x = e.results[i]; if (x.isFinal) fin += x[0].transcript; else t += x[0].transcript; } this.inp.value = (fin + t).trim(); };
    r.onerror = e => { this._recErr = e.error; };
    r.onend = () => { this.listening = false; this.man.classList.remove("listen"); this.micLbl(); const q = (fin || this.inp.value).trim();
      if (q){ this.inp.value = ""; this._quiet = 0; this.ask(q); }
      else if (this._recErr === "not-allowed" || this._recErr === "service-not-allowed"){ this.chat = false; this.bot(); this.speak(this.G("I can't hear you: allow the microphone for this site (the lock icon next to the address).", "مش سامعك: اسمح للميكروفون للموقع ده (من القفل اللي جنب العنوان)."), null, true); }
      else if (this.chat && ++this._quiet < 3 && this.on) setTimeout(() => this.listen(), 400);   // silence: keep listening a couple of times, then rest
      else if (this.chat){ this.chat = false; this.bot(); } this._recErr = ""; };
    try { r.start(); this.listening = true; this.man.classList.add("listen"); this.micLbl(); this.bub.classList.remove("hide"); this.placeBub(); this.bub.classList.add("show"); } catch(e){ this.listening = false; this.micLbl(); } },
  stopListen(manual){ if (manual) this.chat = false; try { this._rec && this._rec.abort(); } catch(e){} this.listening = false; this.man.classList.remove("listen"); this.micLbl(); if (manual) this.bot(); },
  wait(ms){ return new Promise(r => setTimeout(r, ms)); },
  view(){ try { const fe = window.frameElement; if (fe){ const r = fe.getBoundingClientRect(), H = window.parent.innerHeight; return {t:Math.max(0, -r.top), b:Math.max(160, Math.min(innerHeight, H - r.top))}; } } catch(e){} return {t:0, b:innerHeight}; },   // the workspace frame is very tall (3400 px): only this slice is on screen
  scroller(){ try { let e = window.frameElement; while (e && (e = e.parentElement)){ const o = window.parent.getComputedStyle(e).overflowY; if (/(auto|scroll)/.test(o) && e.scrollHeight > e.clientHeight + 20) return e; } } catch(e){} return null; },
  async reveal(r){ const v = this.view(); if (!r || (r.top >= v.t && r.top + Math.min(r.height, 200) <= v.b)) return r; const sc = this.scroller(), dy = r.top - v.t - 90;   // bring a target below / above the fold onto the screen
    try { sc ? sc.scrollBy({top:dy, behavior:"smooth"}) : window.parent.scrollBy({top:dy, behavior:"smooth"}); } catch(e){ return r; } await this.wait(550); this.dock(); return null; },
  dims(){ const v = this.view(), vh = v.b - v.t, f = {s:.7, m:1, l:1.25}[store.get(LS+"_gpsz", "m")] || 1, h = Math.round(Math.max(150, Math.min((MOB ? 260 : 400)*f, vh*.48*f))); return {h, w:Math.round(h*.62), top:v.b - h - (MOB && MT5 ? 60 : 6), v}; },
  dock(){ if (!this.stage) return; const d = this.dims(); Object.assign(this.stage.style, {top:d.top+"px", height:d.h+"px", width:d.w+"px"}); this.tab.style.top = (d.v.b - 120)+"px"; if (this.bub.classList.contains("show")) this.placeBub(); },
  placeBub(){ const d = this.dims(), bw = Math.min(this.bub.offsetWidth || 260, innerWidth - 12), ns = this.root.classList.contains("nostage");
    if (ns){ Object.assign(this.bub.style, {left:"8px", top:"", bottom:(innerHeight - d.v.b + 8)+"px"}); return; } const side = innerWidth - (8 + d.w + 10) >= bw;
    if (side){ Object.assign(this.bub.style, {left:(8 + d.w + 8)+"px", top:"", bottom:(innerHeight - (d.top + d.h*.55))+"px"}); this.bub.classList.add("side"); }
    else { Object.assign(this.bub.style, {left:"6px", top:"", bottom:(innerHeight - d.top + 4)+"px"}); this.bub.classList.remove("side"); } },
  async open(){ this.init(); if (this.on || this._fx) return; this.on = true; store.set(LS+"_gon", true); this.dock(); this.root.classList.add("on");
    await this.fx(true); this.hi(); },
  async close(){ if (!this.on || this._fx) return; GLive.stop(true); this.stopListen(true); this.bub.classList.remove("show"); this.beam.classList.remove("on"); GVoice.stop();
    await this.fx(false); this.root.classList.remove("on"); this.on = false; store.set(LS+"_gon", false); },
  /* entrances like an executive arriving on the trading floor: private elevator, staircase or stage lift - a different one each time */
  async fx(enter){ const kinds = ["elev", "stairs", "lift"], n = +store.get(LS+"_gfx", 0), k = kinds[n % 3]; if (!enter) store.set(LS+"_gfx", n + 1);
    const m = this.man, st = this.stage, reduce = matchMedia("(prefers-reduced-motion: reduce)").matches; this._fx = 1;
    const A = (el, kf, o) => el.animate(kf, Object.assign({duration:900, easing:"cubic-bezier(.3,.1,.25,1)", fill:"forwards"}, o)).finished.catch(() => {});
    try {
      if (reduce){ await A(m, enter ? [{opacity:0}, {opacity:1}] : [{opacity:1}, {opacity:0}], {duration:300}); return; }
      if (k === "elev"){ const ind = st.querySelector(".g-ind b"), dl = st.querySelector(".g-dl"), dr = st.querySelector(".g-dr"); st.classList.add("fx-elev");
        const floors = enter ? ["27","21","14","8","3","G"] : ["G","3","8","14","21","27"], arrow = st.querySelector(".g-ind i"); arrow.textContent = enter ? "▼" : "▲";
        if (enter){ m.getAnimations().forEach(a => a.cancel()); m.style.opacity = 1; m.style.transform = "scale(.9) translateY(-1%)"; dl.style.transform = dr.style.transform = ""; }
        await A(st.querySelector(".g-efront"), [{opacity:0}, {opacity:1}], {duration:450}); st.querySelector(".g-eback").style.opacity = 1;
        if (enter){ for (const f of floors){ ind.textContent = f; await this.wait(170); } st.classList.add("ding"); await this.wait(250); }
        await Promise.all([A(dl, [{transform:"translateX(0)"}, {transform:"translateX(-100%)"}], {duration:850}), A(dr, [{transform:"translateX(0)"}, {transform:"translateX(100%)"}], {duration:850})]);
        m.classList.add("walk"); await A(m, enter ? [{transform:"scale(.9) translateY(-1%)"}, {transform:"scale(1) translateY(0)"}] : [{transform:"scale(1)"}, {transform:"scale(.9) translateY(-1%)"}], {duration:900}); m.classList.remove("walk");
        await Promise.all([A(dl, [{transform:"translateX(-100%)"}, {transform:"translateX(0)"}], {duration:850}), A(dr, [{transform:"translateX(100%)"}, {transform:"translateX(0)"}], {duration:850})]);
        if (!enter){ m.style.opacity = 0; for (const f of floors){ ind.textContent = f; await this.wait(150); } }
        st.classList.remove("ding"); st.querySelector(".g-eback").style.opacity = 0; await A(st.querySelector(".g-efront"), [{opacity:1}, {opacity:0}], {duration:450});
        st.classList.remove("fx-elev"); m.style.transform = ""; if (enter) m.style.opacity = 1;
      } else if (k === "stairs"){ const sv = st.querySelector(".g-stairs"); const N = 7, R = 6.5, T = 9, X0 = 55; let d = ""; for (let i = N - 1; i >= 0; i--){ const x = X0 + i*T, y = 100 - (i+1)*R; d += '<rect x="'+x+'" y="'+y+'" width="'+(200-x)+'" height="'+((i+1)*R)+'" fill="url(#gStep)" stroke="rgba(240,185,11,.4)" stroke-width=".35"/>'; }   // units = % of the stage, so his feet land on each tread
        sv.innerHTML = '<defs><linearGradient id="gStep" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a414b"/><stop offset="1" stop-color="#14181d"/></linearGradient></defs>' + d;
        await A(sv, [{opacity:0, transform:"translateX(12%)"}, {opacity:1, transform:"none"}], {duration:500});
        const pos = i => i < 0 ? [0, 0, 1] : [X0 + i*T + T/2 - 50, -(i+1)*R, 1 - .025*(i+1)], tf = ([x, y, sc], lift) => ({transform:"translate("+x+"%,"+(y - (lift || 0))+"%) scale("+sc+")"}), kf = [tf(pos(N-1))];
        for (let i = N - 2; i >= -1; i--){ const a = pos(i+1), b = pos(i), o = (N - 1 - i)/N; kf.push(Object.assign(tf([(a[0]+b[0])/2, Math.min(a[1], b[1]), (a[2]+b[2])/2], 2), {offset:o - .5/N}), Object.assign(tf(b), {offset:o})); }   // one step = lift, move, land
        m.style.opacity = 1; m.classList.add("walk"); await A(m, enter ? kf : kf.slice().reverse().map((f, i, a) => Object.assign({}, f, f.offset != null ? {offset:1 - f.offset} : {})), {duration:2300, easing:"linear"}); m.classList.remove("walk");
        if (!enter) m.style.opacity = 0; await A(sv, [{opacity:1}, {opacity:0}], {duration:500}); m.getAnimations().forEach(a => a.cancel()); m.style.transform = "";
      } else {   // stage lift: a glowing platform brings him up through the floor
        const lf = st.querySelector(".g-lift"); await A(lf, [{opacity:0}, {opacity:1}], {duration:350}); m.style.opacity = 1;
        const dn = {transform:"translateY(100%)", clipPath:"inset(0 0 100% 0)"}, up = {transform:"translateY(0)", clipPath:"inset(0 0 0% 0)"};
        await Promise.all([A(m, enter ? [dn, up] : [up, dn], {duration:1700, easing:"cubic-bezier(.45,.05,.35,1)"}), A(lf, enter ? [{transform:"translateY(40%)"}, {transform:"translateY(0)"}] : [{transform:"translateY(0)"}, {transform:"translateY(40%)"}], {duration:1700})]);
        await A(lf, [{opacity:1}, {opacity:0}], {duration:450}); m.getAnimations().forEach(a => a.cancel()); m.style.transform = ""; m.style.opacity = enter ? 1 : 0;
      }
    } finally { this._fx = 0; } },
  voice(text){ if (!this.voiceOn()) return; const c = this.chr(), br = this.bridge(); if (br && br.live) return;   // with Gemini available the robotic browser voice is never used
    GVoice.say(text, c.female, () => this.setTalk(true), err => { this.setTalk(false); if (err === "not-allowed") this._pending = text; else if (this.chat && this.on && !this._busyAsk) setTimeout(() => this.listen(), 350); }); },
  speak(text, acts, quiet){ quiet = quiet || GLive.on; this.say_.textContent = text;   // during a live call only Gemini's own voice talks this.acts.innerHTML = ""; (acts || []).forEach(([t, f]) => { const b = el("button", null, t); b.onclick = f; this.acts.append(b); });
    this.placeBub(); this.bub.classList.remove("hide"); this.bub.classList.add("show");
    if (!quiet && this.voiceOn() && Voice.ok) this.voice(text);
    else { GVoice.stop(); this.setTalk(true); clearTimeout(this._tt); this._tt = setTimeout(() => this.setTalk(false), Math.min(6000, 55*text.length)); } },
  hi(){ const c = this.chr(); this.speak(this.G("Hi, I'm "+c.name+". Ask me about anything on the screen and I'll show you where it is and explain it.",
    "أهلًا، أنا "+c.ar+". اسألني عن أي حاجة في الشاشة، وأنا أوريك مكانها وأشرحهالك.") + (this.bridge() && this.bridge().ai ? this.G(" (AI on)", " (الذكاء شغال)") : "")); },
  point(r){ if (!r || !this.on) return; const svg = this.man.querySelector("svg");
    if (!svg){ const mr = this.man.getBoundingClientRect(), hx = mr.left + mr.width*.78, hy = mr.top + mr.height*.42, tx = r.left + r.width/2, ty = r.top + Math.min(r.height/2, 140);   // real presenter (video / photo): the beam starts at his side
      this.beam.setAttribute("width", innerWidth); this.beam.setAttribute("height", innerHeight);
      this.beam.innerHTML = '<line x1="'+hx+'" y1="'+hy+'" x2="'+tx+'" y2="'+ty+'" stroke="#f0b90b" stroke-width="2" stroke-dasharray="6 6" stroke-linecap="round"><animate attributeName="stroke-dashoffset" from="24" to="0" dur=".6s" repeatCount="indefinite"/></line><circle cx="'+tx+'" cy="'+ty+'" r="7" fill="none" stroke="#f0b90b" stroke-width="2"><animate attributeName="r" values="5;11;5" dur="1.2s" repeatCount="indefinite"/></circle>';
      this.beam.classList.add("on"); clearTimeout(this._pt); this._pt = setTimeout(() => this.beam.classList.remove("on"), 6000); return; } const sr = svg.getBoundingClientRect(), k = sr.height/520, ox = sr.left + (sr.width - 200*k)/2,
      sx = ox + 142*k, sy = sr.top + 134*k, tx = r.left + r.width/2, ty = r.top + Math.min(r.height/2, 140), th = Math.atan2(ty - sy, tx - sx)*180/Math.PI, phi = Math.max(-172, Math.min(-12, th - 90));
    const arm = this.man.querySelector(".g-armR"); arm.style.transform = "rotate("+phi+"deg)"; this.man.classList.add("pointing");
    const a = (phi + 90)*Math.PI/180, hx = sx + Math.cos(a)*170*k, hy = sy + Math.sin(a)*170*k;   // hand tip after the arm turns
    this.beam.setAttribute("width", innerWidth); this.beam.setAttribute("height", innerHeight);
    this.beam.innerHTML = '<line x1="'+hx+'" y1="'+hy+'" x2="'+tx+'" y2="'+ty+'" stroke="#f0b90b" stroke-width="2" stroke-dasharray="6 6" stroke-linecap="round"><animate attributeName="stroke-dashoffset" from="24" to="0" dur=".6s" repeatCount="indefinite"/></line><circle cx="'+tx+'" cy="'+ty+'" r="7" fill="none" stroke="#f0b90b" stroke-width="2"><animate attributeName="r" values="5;11;5" dur="1.2s" repeatCount="indefinite"/></circle>';
    this.beam.classList.add("on"); clearTimeout(this._pt); this._pt = setTimeout(() => { arm.style.transform = ""; this.man.classList.remove("pointing"); this.beam.classList.remove("on"); }, 6000); },
  panel(type){ return Ws.panels.find(p => p.type === type && !p.min) || Ws.panels.find(p => p.type === type); },
  chart(){ const p = this.panel("chart"); return p && p.chart ? p : null; },
  async goTo(get){ let r = get(); if (!r) return null; if (!(await this.reveal(r))) r = get(); if (r){ this.point(r); this.flash(r); } return r; },   // scroll the target on screen if needed, point at it, spotlight it
  up(){ this.point(new DOMRect(innerWidth/2, this.view().t, 10, 10)); },
  flash(r){ if (!r) return; const f = el("div", "g-spot"); Object.assign(f.style, {left:r.left+"px", top:r.top+"px", width:r.width+"px", height:r.height+"px"}); this.root.append(f); setTimeout(() => f.remove(), 2600); },
  page(i, name){ try { const ls = window.parent.document.querySelectorAll(".st-key-page label"); if (ls[i]){ ls[i].click(); return true; } } catch(e){} return false; },
  live: {
    chart(g){ const p = g.chart(); if (!p) return ""; const c = p.chart, d = c.data[c.data.length-1]; return d ? g.G(" Now: "+p.state.sym+" "+(p.state.tf || c.tf || "")+" at "+d.c+".", " دلوقتي: "+p.state.sym+" "+(p.state.tf || c.tf || "")+" على "+d.c+".") : ""; },
    vp(g){ const p = g.chart(); if (!p || !p.chart._vp2) return g.G(" Turn it on from Indicators > Volume profile.", " شغّله من المؤشرات ← Volume profile."); const v = p.chart._vp2, tb = v.f.dl.reduce((a,b) => a+b, 0);
      return g.G(" Right now: POC "+v.v.poc.toFixed(2)+", total delta "+(tb >= 0 ? "+" : "")+fmtV(tb)+" ("+(v.real ? "real trades" : "estimated")+").", " دلوقتي: الـPOC عند "+v.v.poc.toFixed(2)+" والدلتا الإجمالية "+(tb >= 0 ? "+" : "−")+fmtV(Math.abs(tb))+" ("+(v.real ? "من صفقات حقيقية" : "تقديرية")+")."); }
  },
  KB: [
    {kw:/profile|بروف|بروفايل|فوليوم|poc|vah|val/i, to:"vp", en:"This column is the volume profile: the length of each row is how much traded at that price, the colour is who won there (green buyers, red sellers; darker = more one-sided). The thin strip on its left edge is resting limit orders from the order book. The gold mark is the POC, the most traded price.", ar:"العمود ده الفوليوم بروفيل: طول كل صف = اتداول قد إيه عند السعر ده، واللون = مين كسب هناك (أخضر الشاري، أحمر البايع، وكل ما يغمق يبقى السيطرة أكبر). الشريط الرفيع على حافته = أوامر الليميت المستنية في الأوردر بوك. العلامة الدهبي = الـPOC أكتر سعر اتداول."},
    {kw:/delta|دلتا/i, to:"vp", en:"Delta = market buys minus market sells. Positive means buyers were more aggressive at that price.", ar:"الدلتا = الشراء بالماركت ناقص البيع بالماركت. لو موجبة يبقى الشاريين كانوا أشرس عند السعر ده."},
    {kw:/order ?flow|اوردر ?فلو|أوردر ?فلو|heat|هيت|bookmap|بوك ?ماب/i, to:"of", en:"The order-flow column shows the order book as a heat map over time: bright = big resting orders. Bubbles are big trades, the sync card under it says when book, tape and limits agree.", ar:"عمود الأوردر فلو بيوري الأوردر بوك كخريطة حرارية مع الوقت: المنوّر = أوامر كبيرة مستنية. الفقاعات = صفقات كبيرة، وكارت الـSync تحته بيقولك امتى البوك والتايب والليميت متفقين."},
    {kw:/\bdom\b|دوم|عمق|depth|ladder/i, to:"dom", en:"The DOM is the price ladder: bids on one side, asks on the other, with their sizes right now.", ar:"الـDOM هو سلّم الأسعار: طلبات الشراء في ناحية والبيع في ناحية، بأحجامها دلوقتي."},
    {kw:/tape|تايب|time ?(and|&) ?sales|تايم|صفقات ?لحظ/i, to:"tape", en:"The tape (time & sales) lists every trade as it happens: green = buyer hit the ask, red = seller hit the bid. Whales and absorption are highlighted.", ar:"التايب (التايم آند سيلز) بيعرض كل صفقة لحظة ما تحصل: أخضر = شاري ضرب على البيع، أحمر = بايع ضرب على الشراء. الحيتان والامتصاص متعلّمين."},
    {kw:/limit|ليميت|حائط|حوائط|wall|spoof|سبوف/i, to:"limits", en:"Limit tracking watches big orders in the book: PLACED, PULLED (removed before price got there, maybe spoofing) or FILLED (price traded through them).", ar:"تتبّع الليميت بيراقب الأوامر الكبيرة في البوك: اتحطت، اتسحبت (اتشالت قبل ما السعر يوصلها، ممكن سبوف) أو اتنفذت (السعر عدّى عليها)."},
    {kw:/setup|سيتاب|كارت|card|entry|دخول|صفق/i, to:"setup", en:"The Setup Card gathers one trade idea: entry, stop, targets, the reasons for and against, and how sure the signals are. It is an idea to check, not a promise.", ar:"كارت السيتاب بيجمع فكرة صفقة واحدة: الدخول والستوب والأهداف، والأسباب مع وضد، وقد إيه الإشارات متأكدة. دي فكرة تراجعها مش وعد."},
    {kw:/signal|اشار|إشار/i, to:"signals", en:"Signals lists what the scanner found per symbol and timeframe, with a score.", ar:"الإشارات بتعرض اللي السكانر لقاه لكل رمز وفريم، ومعاه درجة."},
    {kw:/alert|تنبيه|منبه/i, to:"alerts", en:"Alerts shows the alarms that fired and follows each trade until target or stop.", ar:"التنبيهات بتعرض اللي ضرب، وبتتابع كل صفقة لحد الهدف أو الستوب."},
    {kw:/watch|قائمة|ووتش|متابعة/i, to:"watch", en:"The watchlist: your symbols with last price and 24h change. Click one to load it in linked widgets.", ar:"قايمة المتابعة: رموزك بآخر سعر وتغيير 24 ساعة. دوس على أي واحد يفتح في الويدجتس المربوطة."},
    {kw:/risk|مخاطر|لوت|lot|position size|حجم الصفقة/i, to:"risk", en:"The risk widget sizes the position from your account, risk % and stop distance.", ar:"ويدجت المخاطرة بيحسبلك حجم الصفقة من حسابك ونسبة المخاطرة ومسافة الستوب."},
    {kw:/tradingview|تريدنج|تريدينج/i, to:"tvc", en:"This is TradingView's own live chart, it follows the linked symbol.", ar:"ده شارت تريدنج فيو نفسه لايف، وبيمشي ورا الرمز المربوط."},
    {kw:/widget|ويدجت|اضيف|أضيف|add/i, to:"bar", en:"Use '+ Widget' up here to add any widget; drag its title to move it and any edge or corner to resize.", ar:"من '+ Widget' هنا تضيف أي ويدجت؛ اسحبه من عنوانه عشان تحركه، ومن أي حافة أو ركن عشان تكبّره."},
    {kw:/zoom|تكبير|تصغير|حجم الواجهة/i, to:"zoom", en:"These − / + buttons scale the whole interface; click the number to reset.", ar:"زراير − و + دول بيكبّروا ويصغّروا الواجهة كلها؛ دوس على الرقم يرجع زي ما كان."},
    {kw:/chart|شارت|شموع|candle/i, to:"chart", en:"The chart: candles, your indicators from 'Indicators', drawing tools on the left. Scroll to zoom, drag the price scale to stretch.", ar:"الشارت: الشموع، والمؤشرات من 'Indicators'، وأدوات الرسم على الشمال. اللف بالماوس يكبّر، واسحب سكيل السعر عشان تمطّه."},
    {kw:/lab|لاب|معمل|backtest|باك ?تست/i, page:2, en:"The Lab tests strategies on history with an out-of-sample check. Taking you there.", ar:"اللاب بيختبر الاستراتيجيات على التاريخ وبيتأكد على بيانات متشافتش قبل كده. هوديك هناك."},
    {kw:/scanner|سكانر|سكنر/i, page:1, en:"The Scanner page ranks symbols by setups. Taking you there.", ar:"صفحة السكانر بترتّب الرموز حسب الفرص. هوديك هناك."},
    {kw:/playbook|بلاي ?بوك|خطة/i, page:3, en:"The Playbook keeps your trading rules. Taking you there.", ar:"البلاي بوك فيه قواعدك في التداول. هوديك هناك."},
    {kw:/stats|احصائ|إحصائ|performance|أداء|اداء|journal|جورنال/i, page:4, en:"Stats shows your journal and performance. Taking you there.", ar:"الإحصائيات فيها الجورنال والأداء بتاعك. هوديك هناك."},
    {kw:/win|اكسب|أكسب|هكسب|guarantee|مضمون|ضمان/i, en:"Nobody can promise a win. Every result here is tested and shown with its sample size; under 30 trades it is not evidence.", ar:"محدش يقدر يوعدك بمكسب. كل نتيجة هنا متجرّبة ومكتوب جنبها عدد الصفقات؛ أقل من 30 صفقة يبقى مش دليل."},
    {kw:/^(hi|hello|hey)\b|ازيك|إزيك|سلام|اهلا|أهلا|صباح|مساء/i, en:"Hi! Ask me about any part of the screen.", ar:"أهلًا يا معلم! اسألني عن أي حتة في الشاشة."},
    {kw:/who|انت مين|إنت مين|اسمك/i, en:"I'm your XPiX guide. Short keywords use my built-in guide; real questions go to Claude when the app owner has switched AI on.", ar:"أنا مساعد XPiX. الكلمات القصيرة برد عليها من الدليل المدمج، والأسئلة الحقيقية بتروح لـClaude لو صاحب البرنامج شغّل الذكاء."}
  ],
  target(to){
    if (to === "bar"){ const s = document.querySelector("#bar select"); return s && s.getBoundingClientRect(); }
    if (to === "zoom"){ const b = [...document.querySelectorAll("#bar button")].find(x => x.textContent === "+"); return b && b.getBoundingClientRect(); }
    if (to === "vp" || to === "of"){ const p = this.chart(); if (!p) return null; const r = p.chart.cv.getBoundingClientRect(), PR = p.chart.PR || r.width - 60, w = to === "vp" ? Math.max(48, Math.min(170, PR*.1)) : r.width*.18;
      return to === "vp" ? new DOMRect(r.left + PR - w, r.top + 20, w, r.height*.75) : new DOMRect(r.left + PR - w*2.2, r.top + 20, w, r.height*.75); }
    const p = this.panel(to); return p ? p.root.getBoundingClientRect() : null;
  },
  bridge(){ let fs = []; try { fs = Array.from(window.parent.frames); } catch(e){} for (const f of fs){ try { if (f.__xpixBridge) return f.__xpixBridge; } catch(e){} } return null; },
  ctx(){ const p = this.chart(), c = p && p.chart, d = c && c.data[c.data.length-1], o = {lang:this.talkAr() ? "ar" : "en", widgets:[...new Set(Ws.panels.filter(x => !x.min).map(x => x.type))].join(",")};
    if (c && d){ o.sym = p.state.sym; o.tf = p.state.tf || c.tf; o.price = d.c; o.chg_pct = c.data.length > 1 ? +((d.c/c.data[c.data.length-2].c - 1)*100).toFixed(2) : 0;
      if (c._vp2){ const v = c._vp2; o.poc = +v.v.poc.toFixed(6); o.vah = +v.v.vah.toFixed(6); o.val = +v.v.val.toFixed(6); o.delta_total = Math.round(v.f.dl.reduce((a,b) => a+b, 0)*100)/100; o.delta_src = v.real ? "trades" : "estimated"; }
      if (c.lastBook && c.lastBook.bids && c.lastBook.bids[0] && c.lastBook.asks[0]) o.spread = +(c.lastBook.asks[0].p - c.lastBook.bids[0].p).toFixed(6); }
    const sp = this.panel("setup"); if (sp && !sp.min) o.setup = (sp.root.innerText || "").replace(/\s+/g, " ").slice(0, 400);   // the short Setup Card text, never raw candles
    return o; },
  async askAI(q){ const b = this.bridge(); if (!b || !b.ai) return false; const id = Date.now().toString(36)+Math.random().toString(36).slice(2, 6);
    this.speak(this.G("One sec, thinking…", "ثانية بفكر…"), null, true); this.man.classList.add("think");
    const ans = await new Promise(res => { const to = setTimeout(() => { window.__xpixGuideAnswer = null; res(null); }, 35000); window.__xpixGuideAnswer = a => { if (a.id !== id) return; clearTimeout(to); window.__xpixGuideAnswer = null; res(a); }; b.ask({id, q, ctx:this.ctx()}); });
    this.man.classList.remove("think");
    if (ans && ans.err && ans.err !== "cap" && ans.err !== "nokey"){ const c = (ans.err.match(/\d{3}/) || [""])[0];   // say why the AI did not answer instead of failing silently
      this._aiErr = c === "429" ? this.G("AI daily limit reached (provider).", "حد الذكاء المجاني خلص النهارده.") : c === "400" || c === "401" || c === "403" ? this.G("The AI key was rejected - check it in Secrets.", "مفتاح الذكاء مرفوض، راجعه في Secrets.") : this.G("AI not answering right now ("+ans.err+").", "الذكاء مش بيرد دلوقتي ("+ans.err+")."); } else this._aiErr = "";
    if (!ans || ans.err){ if (ans && ans.err === "cap") { this.speak(this.G("I've hit today's question limit. Built-in answers still work.", "خلّصت عدد أسئلة النهارده. الإجابات الجاهزة لسه شغالة.")); return true; } return false; }
    const pg = {scanner:1, lab:2, playbook:3, stats:4, alerts_page:6}[ans.page];
    if (pg){ this.up(); this.speak(ans.say); await this.wait(1600); this.page(pg); return true; }
    if (ans.go && ans.go !== "none"){ const r = this.target(ans.go); if (r) await this.goTo(() => this.target(ans.go), ans.go === "vp" ? "left" : null); }
    this.speak(ans.say); return true; },
  async ask(q){ if (GLive.on){ GLive.text(q); return; }   // a session is open (call or voice): he answers in Gemini's own voice
    { const br = this.bridge(); if (br && br.live && this.voiceOn() && await GLive.text(q)) return; }   // typed question + voice on: Gemini's natural voice instead of the browser's robotic one
    const k = this.KB.find(e => e.kw.test(q)); this._busyAsk = 1; let used = false;
    try { used = await this.askAI(q); } finally { this._busyAsk = 0; }
    if (used){ if (this.chat && !this.voiceOn()) setTimeout(() => this.listen(), 600); return; }   // the AI answers everything when it is on (a real conversation); the built-in guide is the fallback   // Claude answers real questions; one or two keywords stay on the free built-in guide
    if (!k && this._aiErr){ this.speak(this._aiErr); this._aiErr = ""; return; }
    if (!k){ this.speak(this.G("I don't know that one yet. Try: profile, delta, order flow, DOM, tape, limits, setup, alerts, chart, lab, scanner.", "لسه معرفش دي. جرّب: البروفيل، الدلتا، الأوردر فلو، الدوم، التايب، الليميت، السيتاب، التنبيهات، الشارت، اللاب، السكانر.")); return; }
    const txt = this.G(k.en, k.ar);
    if (k.page != null){ this.up(); this.speak(txt); await this.wait(1400); this.page(k.page); return; }
    if (k.to){ const ty = k.to === "vp" || k.to === "of" ? "chart" : k.to, r = this.target(k.to);
      if (!r){ this.speak(this.G("That widget is not open. Open it?", "الويدجت ده مش مفتوح. أفتحهولك؟"), [[this.G("Open it", "افتحه"), () => { Ws.add(ty); setTimeout(() => this.ask(q), 500); }]]); return; }
      await this.goTo(() => this.target(k.to), k.to === "vp" ? "left" : null); const lf = this.live[k.to]; this.speak(txt + (lf ? lf(this) : "")); return; }
    this.speak(txt); },
  async tour(){ const seen = new Set(), stops = Ws.panels.filter(p => !p.min && !seen.has(p.type) && seen.add(p.type)).slice(0, 6);
    for (const p of stops){ if (!this.on) return; const k = this.KB.find(e => e.to === p.type); if (!k) continue; await this.goTo(() => p.root.getBoundingClientRect()); this.speak(this.G(k.en, k.ar)); await this.wait(Math.min(9000, 2500 + 45*k.en.length)); }
    if (this.on){ this.speak(this.G("That's the tour. Ask me anything else.", "كده خلصنا الجولة. اسألني في أي حاجة تانية.")); } }
};

/* ---- phones, MetaTrader 5 layout: a copy of MT5 mobile (dark): Quotes / Chart / Trade / History / Messages tabs, ☰ side menu, chart top bar
   (symbol, crosshair, indicators, objects, timeframe, new order) and the round menu that opens when you tap the chart (9 timeframes around it).
   XPiX is not connected to a broker: the order screen shows prices and sizes but sends nothing; Trade / History list the journal's tracked setups. ---- */
const M5TF = [["1m","M1"],["5m","M5"],["15m","M15"],["30m","M30"],["1H","H1"],["4H","H4"],["1D","D1"],["1W","W1"],["1M","MN"]];
const M5TH = {bg:"#000000", grid:"#151515", pane:"#000000", mut:"#8e8e93", line:"#2c2c2e", up:"#26a69a", dn:"#ef5350", txt:"#e5e5ea"};
const M5I = {   // line icons (no emoji), MT5 style
  quotes:'<path d="M7 4v14M7 4l-3 3M7 4l3 3M17 20V6M17 20l-3-3M17 20l3-3"/>', chart:'<path d="M5 6v12M5 9h0M9 4v10M13 8v12M17 5v9M20 20H3"/><rect x="3.5" y="9" width="3" height="5"/><rect x="11.5" y="11" width="3" height="5"/>',
  trade:'<path d="M3 17l5-6 4 3 8-9M15 5h5v5"/>', history:'<circle cx="12" cy="12" r="8.5"/><path d="M12 7v5l3.5 2"/>', msg:'<path d="M4 5h16v11H9l-5 4z"/>',
  menu:'<path d="M3 6h18M3 12h18M3 18h18"/>', plus:'<path d="M12 4v16M4 12h16"/>', cross:'<path d="M12 3v18M3 12h18"/><circle cx="12" cy="12" r="3"/>', fx:'<path d="M14 4c-3 0-3 3-3.5 6S9 20 6 20M7 10h7M14 13l5 6M19 13l-5 6"/>',
  obj:'<path d="M4 20L20 4"/><rect x="13" y="13" width="7" height="7"/><circle cx="7" cy="7" r="3"/>', sym:'<path d="M12 3v18M16.5 7.5C16 5.5 14.3 5 12 5s-4.5 1-4.5 3 2 2.6 4.5 3 4.5 1 4.5 3.3-2 3-4.5 3-4.3-.8-4.8-2.8"/>',
  back:'<path d="M15 5l-7 7 7 7"/>', close:'<path d="M6 6l12 12M18 6L6 18"/>', edit:'<path d="M4 20h4L19 9l-4-4L4 16z"/>'};
const m5i = (k, s) => '<svg viewBox="0 0 24 24" width="'+(s || 22)+'" height="'+(s || 22)+'" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">'+M5I[k]+'</svg>';
const M5 = {
  scr:"quotes", prev:{}, th0:null,
  on(){ return MOB && MT5; },
  vis(){ const v = (typeof Guide !== "undefined" && Guide.view) ? Guide.view() : {t:0, b:innerHeight}; document.documentElement.style.setProperty("--vt", v.t+"px"); document.documentElement.style.setProperty("--vb", v.b+"px"); },
  build(){
    if (!this.th0) this.th0 = Object.assign({}, TH); Object.assign(TH, M5TH);
    let r = document.getElementById("m5"); if (!r){ r = el("div"); r.id = "m5"; document.body.append(r); }
    let n = document.getElementById("m5nav"); if (!n){ n = el("div"); n.id = "m5nav"; document.body.append(n); }
    n.innerHTML = ""; [["quotes","quotes",["Quotes","الأسعار"]], ["chart","chart",["Chart","الرسم البياني"]], ["trade","trade",["Trade","التداول"]], ["history","history",["History","السجل"]], ["messages","msg",["Messages","الرسائل"]]]
      .forEach(([k, ic, lb]) => { const b = el("button", null, m5i(ic)+'<span>'+Lg(lb[0], lb[1])+'</span>'); b.dataset.k = k; b.onclick = () => this.show(k); n.append(b); });
    if (!this._sc){ this._sc = 1; let q = 0; const f = () => { if (q) return; q = requestAnimationFrame(() => { q = 0; this.vis(); }); }; try { window.parent.addEventListener("scroll", f, true); window.parent.addEventListener("resize", f); } catch(e){} addEventListener("resize", f); }
    if (!this._tk){ this._tk = Hub.sub("tickers", "all", () => { if (this.on() && this.scr === "quotes") this.quotes(); }); }
    this.vis(); this.show(store.get(LS+"_m5scr", "chart"));
  },
  destroy(){ ["m5","m5nav","m5ctop","m5rad","m5sheet","m5drw"].forEach(id => { const x = document.getElementById(id); if (x) x.remove(); }); if (this.th0) Object.assign(TH, this.th0); this.th0 = null;
    document.body.classList.remove("m5chart"); Ws.panels.forEach(p => { p.root.classList.remove("mact"); p.chart && (p.chart.onTap = null, p.chart.xMode = false); }); },
  show(k, panel){ this.scr = k; if (k !== "panel") store.set(LS+"_m5scr", k); this.closeAll(); document.querySelectorAll("#m5nav button").forEach(b => b.classList.toggle("on", b.dataset.k === (k === "panel" ? "" : k)));
    const r = document.getElementById("m5"), isPanel = k === "chart" || k === "panel"; document.body.classList.toggle("m5chart", isPanel); r.style.display = isPanel ? "none" : "";
    if (k === "chart"){ let p = Ws.panels.find(q => q.type === "chart"); if (!p){ Ws.add("chart"); p = Ws.panels[Ws.panels.length - 1]; } this.cp = p; Ws.mshow(p); this.chartTop(p); this.hook(p); return; }
    if (k === "panel"){ Ws.mshow(panel); this.panelTop(panel); return; }
    const t = document.getElementById("m5ctop"); if (t) t.remove(); Ws.panels.forEach(q => q.root.classList.remove("mact"));
    this[k](); },
  top(title, left, right){ return '<div class="m5top"><button class="m5ib" data-a="'+(left || "menu")+'">'+m5i(left || "menu")+'</button><b>'+title+'</b><span class="sp"></span>'+(right || []).map(a => '<button class="m5ib" data-a="'+a+'">'+m5i(a)+'</button>').join("")+'</div>'; },
  wire(root, acts){ root.querySelectorAll("[data-a]").forEach(b => b.onclick = e => { e.stopPropagation(); const a = b.dataset.a; (acts[a] || (a === "menu" ? () => this.drawer() : () => {}))(b); }); },
  tick(){ const t = Hub.last["tickers|all"]; return t && !t.error ? t : {}; },
  syms(){ return [...new Set(SYMS.concat([...(Hub.extra || [])]))]; },
  px(v, cls){ if (v == null || !isFinite(v)) return '<span class="'+(cls || "")+'">—</span>'; const s = fmtP(v); if (s.length < 4) return '<span class="'+(cls || "")+'">'+s+'</span>';
    return '<span class="'+(cls || "")+'">'+s.slice(0, -3)+'<big>'+s.slice(-3, -1)+'</big><sup>'+s.slice(-1)+'</sup></span>'; },
  quotes(){ const r = document.getElementById("m5"), T_ = this.tick(), now = new Date(nowS()), hh = now.toTimeString().slice(0, 8);
    let h = this.top(Lg("Quotes","الأسعار"), "menu", ["plus","edit"]) + '<div class="m5list">';
    this.syms().forEach(s => { const q = T_[s] || {}, bid = q.bid || q.last, ask = q.ask || q.last, pv = this.prev[s], dir = pv == null || bid == null ? "" : bid > pv ? "up" : bid < pv ? "dn" : (this["d_"+s] || "");
      if (bid != null) { this["d_"+s] = dir; this.prev[s] = bid; }
      const dec = ((fmtP(bid || 0).split(".")[1]) || "").length, sp = q.bid && q.ask ? Math.round((q.ask - q.bid)*Math.pow(10, dec)) : null, ch = q.open ? (100*(q.last/q.open - 1)) : null;
      h += '<div class="m5row" data-s="'+esc(s)+'"><div class="m5l"><b>'+esc(s.replace(/-SWAP$/, "").replace(/-/g, ""))+'</b><small>'+hh+(sp != null ? '  ↔ '+sp : "")+(ch != null ? '  <i class="'+(ch >= 0 ? "up" : "dn")+'">'+(ch >= 0 ? "+" : "")+ch.toFixed(2)+'%</i>' : "")+'</small></div>'
        + '<div class="m5p">'+this.px(bid, dir)+'<small>L: '+(q.lo ? fmtP(q.lo) : "—")+'</small></div><div class="m5p">'+this.px(ask, dir)+'<small>H: '+(q.hi ? fmtP(q.hi) : "—")+'</small></div></div>'; });
    r.innerHTML = h + '</div>'; this.wire(r, {plus:() => this.symSheet(s => { Hub.extra = Hub.extra || new Set(); Hub.extra.add(s); this.quotes(); }), edit:() => this.toast(Lg("Edit the list from the Watchlist widget (☰ > Watchlist).", "عدّل القايمة من ويدجت قايمة المتابعة (☰ ← قايمة المتابعة)."))});
    r.querySelectorAll(".m5row").forEach(x => x.onclick = () => { const s = x.dataset.s; this.sheet(s.replace(/-/g, ""), [[Lg("Trade","تداول"), () => this.order(s)], [Lg("Chart","الرسم البياني"), () => { this.show("chart"); this.cp && this.cp.setSymbol(s); }],
      [Lg("Depth of Market","عمق السوق"), () => { let p = Ws.panels.find(q => q.type === "dom"); if (!p){ Ws.add("dom"); p = Ws.panels[Ws.panels.length - 1]; } p.setSymbol && p.setSymbol(s); this.show("panel", p); }],
      [Lg("Properties","الخصائص"), () => this.props(s)]]); }); },
  props(s){ const q = this.tick()[s] || {}; this.sheet(s, [[Lg("Last","آخر سعر")+": "+(q.last != null ? fmtP(q.last) : "—")], ["Bid: "+(q.bid ? fmtP(q.bid) : "—")+"   Ask: "+(q.ask ? fmtP(q.ask) : "—")], [Lg("24h high / low","أعلى / أقل 24س")+": "+(q.hi ? fmtP(q.hi) : "—")+" / "+(q.lo ? fmtP(q.lo) : "—")], [Lg("24h change","تغيير 24س")+": "+(q.open ? (100*(q.last/q.open - 1)).toFixed(2)+"%" : "—")]]); },
  chartTop(p){ let t = document.getElementById("m5ctop"); if (!t){ t = el("div"); t.id = "m5ctop"; document.body.append(t); }
    const tf = (M5TF.find(x => x[0] === p.state.tf) || [0, p.state.tf])[1];
    t.innerHTML = '<button class="m5ib" data-a="menu">'+m5i("menu")+'</button><button class="m5ib" data-a="sym">'+m5i("sym")+'</button><button class="m5ib'+(p.chart.xMode ? " on" : "")+'" data-a="cross">'+m5i("cross")+'</button><button class="m5ib" data-a="fx">'+m5i("fx")+'</button><button class="m5ib" data-a="obj">'+m5i("obj")+'</button><button class="m5tf" data-a="tf">'+tf+'</button><span class="sp"></span><button class="m5ib" data-a="plus">'+m5i("plus")+'</button>'
      + '<div class="m5cap"><b>'+esc(String(p.state.sym || "").replace(/-/g, ""))+', '+tf+'</b></div>';
    this.wire(t, {sym:() => this.symSheet(s => { p.setSymbol(s); this.chartTop(p); }), cross:() => this.cross(p), fx:() => this.ind(p), obj:() => this.objects(p), tf:b => { const r = b.getBoundingClientRect(); this.radial(r.left + r.width/2, r.bottom + 120, p); }, plus:() => this.order(p.state.sym)}); },
  panelTop(p){ let t = document.getElementById("m5ctop"); if (!t){ t = el("div"); t.id = "m5ctop"; document.body.append(t); }
    t.innerHTML = '<button class="m5ib" data-a="back">'+m5i("back")+'</button><b class="m5pt">'+esc(T(p.type))+'</b><span class="sp"></span>'; this.wire(t, {back:() => this.show(store.get(LS+"_m5scr", "quotes"))}); },
  hook(p){ const c = p.chart; if (!c) return; c.onTap = (x, y) => { const r = c.cv.getBoundingClientRect(); this.radial(r.left + x, r.top + y, p); }; },
  cross(p){ const c = p.chart; c.xMode = !c.xMode; if (!c.xMode){ c.mouse = null; c.draw(); } else this.toast(Lg("Crosshair: drag on the chart", "الكروس هير: اسحب على الشارت")); this.chartTop(p); },
  ind(p){ if (p.indBtn) p.indBtn.onclick({stopPropagation(){}}); },
  objects(p){ const k = {cur:Lg("Cursor","المؤشر"), trend:Lg("Trendline","خط ترند"), hline:Lg("Horizontal Line","خط أفقي"), rect:Lg("Rectangle","مستطيل"), channel:Lg("Equidistant Channel","قناة متوازية"), text:Lg("Text","نص"), fib:Lg("Fibonacci Retracement","فيبوناتشي"), wave:Lg("Elliott Wave","موجات إليوت"), long:Lg("Long position","صفقة شراء"), short:Lg("Short position","صفقة بيع")};
    this.sheet(Lg("Objects","الكائنات"), Object.keys(p.toolBtns || {}).map(t => [k[t] || t, () => p.toolBtns[t].click()]).concat([[Lg("Delete all objects","حذف كل الكائنات"), () => { const b = [...p.root.querySelectorAll(".dt button")].find(x => x.textContent === "🗑"); b && b.click(); }]])); },
  radial(x, y, p){ this.closeAll(); const R = 92, w = el("div"); w.id = "m5rad"; const cx = Math.max(R + 34, Math.min(innerWidth - R - 34, x)), v = this.vt(), cy = Math.max(v.t + R + 60, Math.min(v.b - R - 70, y));
    let h = '<div class="m5rc" style="left:'+cx+'px;top:'+cy+'px">'; const cur = p.state.tf;
    M5TF.forEach(([tf, l], i) => { const a = -Math.PI/2 + i*2*Math.PI/M5TF.length; h += '<button class="m5rt'+(tf === cur ? " on" : "")+'" data-tf="'+tf+'" style="transform:translate('+(Math.cos(a)*R)+'px,'+(Math.sin(a)*R)+'px)">'+l+'</button>'; });
    [["cross", -135], ["fx", -45], ["obj", 45], ["plus", 135]].forEach(([k, d]) => { const a = d*Math.PI/180; h += '<button class="m5ri" data-a="'+k+'" style="transform:translate('+(Math.cos(a)*44)+'px,'+(Math.sin(a)*44)+'px)">'+m5i(k, 20)+'</button>'; });
    w.innerHTML = h + '<button class="m5rx" data-a="close">'+m5i("close", 18)+'</button></div>'; document.body.append(w);
    w.style.pointerEvents = "none"; setTimeout(() => { w.style.pointerEvents = ""; }, 420);   // the tap that opened it also fires a late click (it would hit the centre ✕): ignore it
    w.onclick = e => { if (e.target === w) this.closeAll(); };
    w.querySelectorAll("[data-tf]").forEach(b => b.onclick = e => { e.stopPropagation(); p.setTf(b.dataset.tf); this.closeAll(); this.chartTop(p); });
    this.wire(w, {cross:() => { this.closeAll(); this.cross(p); }, fx:() => { this.closeAll(); this.ind(p); }, obj:() => { this.closeAll(); this.objects(p); }, plus:() => { this.closeAll(); this.order(p.state.sym); }, close:() => this.closeAll()}); },
  vt(){ return (typeof Guide !== "undefined" && Guide.view) ? Guide.view() : {t:0, b:innerHeight}; },
  sheet(title, items){ this.closeAll(); const s = el("div"); s.id = "m5sheet"; let h = '<div class="m5sh"><div class="m5shh">'+esc(title)+'</div>';
    items.forEach((it, i) => { h += '<button class="m5si'+(it[1] ? "" : " ro")+'" data-i="'+i+'">'+esc(it[0])+'</button>'; }); s.innerHTML = h + '<button class="m5si m5cancel">'+Lg("Cancel","إلغاء")+'</button></div>'; document.body.append(s);
    s.style.pointerEvents = "none"; setTimeout(() => { s.style.pointerEvents = ""; }, 420); s.onclick = e => { if (e.target === s || e.target.classList.contains("m5cancel")) this.closeAll(); };
    s.querySelectorAll("[data-i]").forEach(b => b.onclick = () => { const f = items[+b.dataset.i][1]; if (!f) return; this.closeAll(); f(); }); },
  symSheet(cb){ this.sheet(Lg("Symbols","الرموز"), this.syms().map(s => [s, () => cb(s)])); },
  closeAll(){ ["m5rad","m5sheet","m5drw"].forEach(id => { const x = document.getElementById(id); if (x) x.remove(); }); },
  toast(t){ const x = el("div", "m5toast", esc(t)); document.body.append(x); setTimeout(() => x.remove(), 3200); },
  order(sym){ const q = this.tick()[sym] || {}, s = el("div"); this.closeAll(); s.id = "m5sheet"; let vol = +store.get(LS+"_m5vol", 0.01) || 0.01;
    const draw = () => { s.innerHTML = '<div class="m5ord">'+this.top(esc(String(sym).replace(/-/g, "")), "back", [])+'<div class="m5ot">'+Lg("Market Execution","تنفيذ فوري")+'</div>'
      + '<div class="m5vol"><button data-v="-0.1">-0.1</button><button data-v="-0.01">-0.01</button><b>'+vol.toFixed(2)+'</b><button data-v="0.01">+0.01</button><button data-v="0.1">+0.1</button></div>'
      + '<div class="m5bq">'+this.px(q.bid || q.last, "dn")+this.px(q.ask || q.last, "up")+'</div><label>Stop Loss<input inputmode="decimal" placeholder="—"></label><label>Take Profit<input inputmode="decimal" placeholder="—"></label>'
      + '<div class="m5ob"><button class="sell">'+Lg("SELL BY MARKET","بيع بسعر السوق")+'</button><button class="buy">'+Lg("BUY BY MARKET","شراء بسعر السوق")+'</button></div>'
      + '<p class="m5note">'+Lg("XPiX is not connected to a broker: no order is sent. Use this screen to plan, then place the trade in your MetaTrader.", "XPiX مش متوصل بحساب عند وسيط: مفيش أمر بيتبعت. استخدم الشاشة دي للتخطيط، ونفّذ الصفقة من الميتاتريدر بتاعك.")+'</p></div>';
      s.querySelectorAll("[data-v]").forEach(b => b.onclick = () => { vol = Math.max(0.01, Math.round((vol + +b.dataset.v)*100)/100); store.set(LS+"_m5vol", vol); draw(); });
      s.querySelectorAll(".m5ob button").forEach(b => b.onclick = () => this.toast(Lg("Not sent - XPiX has no broker connection.", "متبعتش - XPiX مش متوصل بوسيط.")));
      this.wire(s, {back:() => this.closeAll()}); };
    draw(); document.body.append(s); },
  trades(st){ return Journal.list.filter(t => st === "open" ? t.status === "open" : t.status !== "open").slice().reverse(); },
  trade(){ const r = document.getElementById("m5"), op = this.trades("open"), T_ = this.tick();
    let h = this.top(Lg("Trade","التداول"), "menu", ["plus"]) + '<div class="m5acc"><div><span>'+Lg("Tracked setups","صفقات متابَعة")+'</span><b>'+op.length+'</b></div><div><span>'+Lg("Account","الحساب")+'</span><b>'+Lg("not connected","غير متصل")+'</b></div></div>'
      + '<div class="m5sec">'+Lg("Positions (journal, not real orders)","الصفقات (من الجورنال، مش أوامر حقيقية)")+'</div><div class="m5list">';
    if (!op.length) h += '<div class="m5empty">'+Lg("No open tracked setups.","مفيش صفقات مفتوحة بتتابَع.")+'</div>';
    op.forEach(t => { const px = (T_[t.symbol] || {}).last || t.last, L = t.dir === "bullish", rr = px != null ? ((L ? px - t.entry : t.entry - px)/Math.max(1e-12, Math.abs(t.entry - t.sl))) : null;
      h += '<div class="m5row m5tr"><div class="m5l"><b>'+esc(t.symbol.replace(/-/g, ""))+', <i class="'+(L ? "up" : "dn")+'">'+(L ? "buy" : "sell")+'</i></b><small>'+fmtP(t.entry)+' → '+(px != null ? fmtP(px) : "—")+'</small><small>S/L '+fmtP(t.sl)+'  T/P '+fmtP(t.tp1)+'</small></div><div class="m5pr '+(rr == null ? "" : rr >= 0 ? "up" : "dn")+'">'+(rr == null ? "—" : (rr >= 0 ? "+" : "")+rr.toFixed(2)+" R")+'</div></div>'; });
    r.innerHTML = h + '</div>'; this.wire(r, {plus:() => this.order((this.cp && this.cp.state.sym) || SYMS[0])}); },
  history(){ const r = document.getElementById("m5"), cl = this.trades("closed").filter(t => t.status === "tp" || t.status === "sl"), n = cl.length, sumR = cl.reduce((a, t) => a + (t.r || 0), 0), w = cl.filter(t => t.r > 0).length;
    let h = this.top(Lg("History","السجل"), "menu", []) + '<div class="m5acc"><div><span>'+Lg("Profit","الربح")+'</span><b class="'+(sumR >= 0 ? "up" : "dn")+'">'+(sumR >= 0 ? "+" : "")+sumR.toFixed(2)+' R</b></div><div><span>'+Lg("Trades","الصفقات")+'</span><b>'+n+'</b></div><div><span>'+Lg("Win rate","نسبة الكسب")+'</span><b>'+(n ? Math.round(100*w/n)+"%" : "—")+'</b></div></div>'
      + (n < 30 ? '<div class="m5warn">'+Lg("Under 30 trades: not evidence yet.","أقل من 30 صفقة: لسه مش دليل.")+'</div>' : "") + '<div class="m5list">';
    if (!n) h += '<div class="m5empty">'+Lg("No closed tracked setups yet.","لسه مفيش صفقات مقفولة.")+'</div>';
    cl.slice(0, 200).forEach(t => { const L = t.dir === "bullish"; h += '<div class="m5row m5tr"><div class="m5l"><b>'+esc(t.symbol.replace(/-/g, ""))+', <i class="'+(L ? "up" : "dn")+'">'+(L ? "buy" : "sell")+'</i></b><small>'+fmtP(t.entry)+' → '+(t.status === "tp" ? fmtP(t.tp1) : fmtP(t.sl))+'</small><small>'+new Date(t.t1 || t.t0).toLocaleString()+'</small></div><div class="m5pr '+(t.r >= 0 ? "up" : "dn")+'">'+(t.r >= 0 ? "+" : "")+(t.r || 0).toFixed(2)+' R</div></div>'; });
    r.innerHTML = h + '</div>'; this.wire(r, {}); },
  messages(){ const r = document.getElementById("m5"), al = (Alerts.list || []).slice(0, 60), nw = (CFG.news || []).slice(0, 30);
    let h = this.top(Lg("Messages","الرسائل"), "menu", []) + '<div class="m5list">';
    if (!al.length && !nw.length) h += '<div class="m5empty">'+Lg("No messages.","مفيش رسايل.")+'</div>';
    al.forEach(a => { const c = a.card || {}; h += '<div class="m5msg"><b>XPiX '+Lg("Alert","تنبيه")+'</b><small>'+(a.t ? new Date(a.t).toLocaleString() : "")+'</small><p>'+esc((c.symbol || a.symbol || "")+" "+(c.direction || a.dir || "")+" "+(a.text || a.msg || c.ttype || ""))+'</p></div>'; });
    nw.forEach(x => { h += '<div class="m5msg"><b>'+esc(x.source || "News")+'</b><small>'+esc(x.time || x.published || "")+'</small><p>'+esc(x.title || x.headline || "")+'</p></div>'; });
    r.innerHTML = h + '</div>'; this.wire(r, {}); },
  drawer(){ this.closeAll(); const d = el("div"); d.id = "m5drw"; const used = ["chart","watch"]; let h = '<div class="m5dp"><div class="m5dh"><span class="gbi">'+(typeof GUIDE_ICON !== "undefined" ? GUIDE_ICON : "")+'</span><b>XPiX</b><small>MetaTrader 5 '+Lg("layout","واجهة")+'</small></div>';
    Ws.panels.filter(p => !used.includes(p.type)).forEach((p, i) => { h += '<button data-p="'+Ws.panels.indexOf(p)+'">'+esc(T(p.type))+'</button>'; });
    h += '<button data-a="add">+ '+Lg("Add widget","إضافة ويدجت")+'</button><button data-a="guide">Mr X</button><button data-a="exit">'+Lg("Leave MetaTrader layout","الخروج من واجهة الميتاتريدر")+'</button></div>';
    d.innerHTML = h; document.body.append(d); d.onclick = e => { if (e.target === d) this.closeAll(); };
    d.querySelectorAll("[data-p]").forEach(b => b.onclick = () => { const p = Ws.panels[+b.dataset.p]; this.closeAll(); this.show("panel", p); });
    this.wire(d, {add:() => { this.closeAll(); const kinds = ["setup","signals","alerts","dom","tape","limits","risk","tvc","scanner","news"]; this.sheet(Lg("Add widget","إضافة ويدجت"), kinds.map(k => [T(k), () => { Ws.add(k); this.show("panel", Ws.panels[Ws.panels.length - 1]); }])); },
      guide:() => { this.closeAll(); Guide.on ? Guide.close() : Guide.open(); }, exit:() => { this.closeAll(); MT5 = false; store.set(LS+"_mt5", false); document.body.classList.remove("mt5"); this.destroy(); Ws.mjump(); Ws.panels.forEach(p => p.apply()); setTimeout(() => Ws.panels.forEach(p => { try { p.chart && (p.chart.resize(), p.chart.draw()); } catch(_){} }), 60); buildBar(); }}); }
};

/* welcome: widgets materialise one after another with a gold scan line (once per page load; skipped for reduced motion) */
function welcome(){
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) return; const v = (typeof Guide !== "undefined" && Guide.view) ? Guide.view() : {t:0, b:innerHeight};
  const line = el("div"); line.style.cssText = "position:fixed;left:0;right:0;height:2px;z-index:8999;pointer-events:none;background:linear-gradient(90deg,transparent,#f0b90b 20%,#fff3c4 50%,#f0b90b 80%,transparent);box-shadow:0 0 18px 4px rgba(240,185,11,.45)";
  document.body.append(line); line.animate([{top:v.t+"px", opacity:0}, {opacity:1, offset:.12}, {top:(v.b - 4)+"px", opacity:.9, offset:.85}, {top:(v.b - 4)+"px", opacity:0}], {duration:1500, easing:"cubic-bezier(.4,0,.2,1)"}).finished.then(() => line.remove(), () => line.remove());
  [...document.querySelectorAll("#bar > *")].forEach((b, i) => b.animate([{opacity:0, transform:"translateY(-8px)"}, {opacity:1, transform:"none"}], {duration:450, delay:60 + i*45, easing:"cubic-bezier(.2,.7,.2,1)", fill:"backwards"}));
  Ws.panels.slice().sort((a, b) => (a.rect.y - b.rect.y) || (a.rect.x - b.rect.x)).forEach((p, i) => p.root.animate([
    {opacity:0, transform:"translateY(22px) scale(.97)", filter:"blur(6px) brightness(1.8)", boxShadow:"0 0 0 1px rgba(240,185,11,.9), 0 0 30px rgba(240,185,11,.5)"},
    {opacity:1, filter:"blur(0) brightness(1.15)", boxShadow:"0 0 0 1px rgba(240,185,11,.6), 0 0 18px rgba(240,185,11,.3)", offset:.6},
    {opacity:1, transform:"none", filter:"none", boxShadow:"0 0 0 0 transparent"}], {duration:900, delay:200 + i*110, easing:"cubic-bezier(.2,.7,.2,1)", fill:"backwards"}));
}
/* toolbar */
// Workspace capture. Desktop: the browser's own screen share (getDisplayMedia) records the real pixels. Tablets / phones have NO screen share API (iPadOS Safari, Android Chrome),
// so the workspace is rebuilt from the page itself: DOM -> SVG foreignObject -> canvas (every chart canvas is copied as an image; a TradingView frame is a labelled box because the browser
// never lets a page read a cross-origin frame), and the video is that picture with the live chart canvases drawn over it. Same file as the desktop one (WebM, or MP4 on Safari).
