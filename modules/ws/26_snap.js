const Snap = {
  PROPS: (() => { const sd = ["top","right","bottom","left"], o = ["display","position","top","right","bottom","left","width","height","min-width","min-height","max-width","max-height","box-sizing","z-index","float","clear","overflow-x","overflow-y",
      "visibility","opacity","transform","transform-origin","flex-grow","flex-shrink","flex-basis","flex-direction","flex-wrap","align-items","align-self","align-content","justify-content","order","gap","row-gap","column-gap",
      "grid-template-columns","grid-template-rows","grid-column-start","grid-column-end","grid-row-start","grid-row-end","color","background-color","background-image","background-size","background-position","background-repeat",
      "font-family","font-size","font-weight","font-style","line-height","letter-spacing","text-align","text-transform","text-decoration-line","text-overflow","text-indent","white-space","word-break","overflow-wrap","direction","vertical-align",
      "border-top-left-radius","border-top-right-radius","border-bottom-left-radius","border-bottom-right-radius","box-shadow","fill","stroke","stroke-width","filter","object-fit","list-style-type","table-layout","border-collapse","border-spacing"];
    sd.forEach(d => o.push("margin-"+d, "padding-"+d, "border-"+d+"-width", "border-"+d+"-style", "border-"+d+"-color")); return o; })(),
  async dom(scale){   // -> canvas with the whole page (scale 1 = CSS pixels)
    const root = document.body, vw = Math.max(1, document.documentElement.clientWidth), vh = Math.max(1, document.documentElement.clientHeight), clone = root.cloneNode(true);
    const src = [root, ...root.querySelectorAll("*")], dst = [clone, ...clone.querySelectorAll("*")], swap = [], PR = Snap.PROPS;
    for (let k = 0; k < src.length; k++){ const a = src[k], b = dst[k], tag = a.tagName; if (tag === "SCRIPT" || tag === "STYLE" || tag === "LINK"){ swap.push([b, null]); continue; }
      const cs = getComputedStyle(a); if (cs.display === "none"){ swap.push([b, null]); continue; }
      let st = ""; for (let m = 0; m < PR.length; m++){ const v = cs.getPropertyValue(PR[m]); if (v) st += PR[m]+":"+v+";"; }
      if (tag === "CANVAS"){ const r = a.getBoundingClientRect(), im = document.createElement("img"); try { im.setAttribute("src", a.toDataURL("image/png")); } catch(e){} im.setAttribute("style", st+"width:"+r.width+"px;height:"+r.height+"px"); swap.push([b, im]); continue; }
      if (tag === "IFRAME"){ const r = a.getBoundingClientRect(), bx = document.createElement("div"); bx.setAttribute("style", st+"width:"+r.width+"px;height:"+r.height+"px;display:flex;align-items:center;justify-content:center;background:#131722;color:#8a9099;font:12px sans-serif");
        bx.textContent = Lg("TradingView (a page cannot capture another site's frame)","TradingView (المتصفح مش بيسمح بتصوير فريم موقع تاني)"); swap.push([b, bx]); continue; }
      b.setAttribute("style", st);
      if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT"){ if (tag === "TEXTAREA") b.textContent = a.value; else if (tag === "SELECT"){ [...b.options].forEach((o, n) => { if (a.options[n] && a.options[n].selected) o.setAttribute("selected", "selected"); else o.removeAttribute("selected"); }); } else b.setAttribute("value", a.value); } }
    swap.forEach(([o, n]) => { try { n ? o.replaceWith(n) : o.remove(); } catch(e){} });
    clone.setAttribute("style", (clone.getAttribute("style") || "")+";width:"+vw+"px;height:"+vh+"px;margin:0;overflow:hidden");
    const xml = new XMLSerializer().serializeToString(clone).replace(/#/g, "%23");
    const svg = '<svg xmlns="http://www.w3.org/2000/svg" width="'+vw+'" height="'+vh+'"><foreignObject x="0" y="0" width="100%" height="100%">'+xml+'</foreignObject></svg>';
    const img = new Image(); img.decoding = "sync"; await new Promise((res, rej) => { img.onload = res; img.onerror = () => rej(new Error("svg")); img.src = "data:image/svg+xml;charset=utf-8,"+encodeURIComponent(svg).replace(/%2523/g, "%23"); });
    const c = document.createElement("canvas"), sc = scale || Math.min(2, window.devicePixelRatio || 1); c.width = Math.round(vw*sc); c.height = Math.round(vh*sc); const x = c.getContext("2d"); x.fillStyle = "#0b0e11"; x.fillRect(0, 0, c.width, c.height); x.drawImage(img, 0, 0, c.width, c.height); return c; },
  comp(scale){   // fallback when the DOM picture is refused: panel boxes with titles + the chart canvases (always works)
    const vw = Math.max(1, document.documentElement.clientWidth), vh = Math.max(1, document.documentElement.clientHeight), sc = scale || 1, c = document.createElement("canvas"); c.width = Math.round(vw*sc); c.height = Math.round(vh*sc);
    const x = c.getContext("2d"); x.scale(sc, sc); x.fillStyle = "#0b0e11"; x.fillRect(0, 0, vw, vh); x.font = "12px sans-serif"; x.textBaseline = "middle";
    document.querySelectorAll(".panel").forEach(pn => { const r = pn.getBoundingClientRect(); if (r.width < 4 || r.height < 4 || getComputedStyle(pn).display === "none") return; x.fillStyle = "#161a1e"; x.fillRect(r.left, r.top, r.width, r.height); x.strokeStyle = "#2b3139"; x.strokeRect(r.left + .5, r.top + .5, r.width - 1, r.height - 1);
      const t = pn.querySelector(".ph"); x.fillStyle = "#eaecef"; x.fillText(t ? t.textContent.trim().slice(0, 60) : "", r.left + 8, r.top + 13); });
    document.querySelectorAll("canvas").forEach(cv => { const r = cv.getBoundingClientRect(); if (r.width < 4 || r.height < 4 || r.bottom < 0 || r.top > vh) return; try { x.drawImage(cv, r.left, r.top, r.width, r.height); } catch(e){} });
    return c; },
  async shot(scale){ try { return await Snap.dom(scale); } catch(e){ return Snap.comp(scale); } },
  async save(blob, name){   // tablets: the share sheet ("Save image / Save to Files"), else a normal download
    try { const f = new File([blob], name, {type: blob.type}); if (TCH && navigator.canShare && navigator.canShare({files:[f]})){ await navigator.share({files:[f]}); return; } } catch(e){ if (e && e.name === "AbortError") return; }
    const u = URL.createObjectURL(blob), a = document.createElement("a"); a.href = u; a.download = name; document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(u), 8000); },
  mime(){ if (!window.MediaRecorder) return ""; return ["video/webm;codecs=vp9", "video/webm", "video/mp4"].find(m => { try { return MediaRecorder.isTypeSupported(m); } catch(e){ return false; } }) || ""; },
  /* HIGH QUALITY video settings for a stream: the best codec this browser can record (H.264 MP4 first: hardware encoder on Mac / Windows and QuickTime / editors open it; then VP9 WebM, VP8),
     and a bitrate that follows the REAL size and frame rate of the video track (about 0.16 bit per pixel per frame for H.264, 0.10 for VP9), 12 .. 120 Mbps: 4K at 60 fps is ~80 Mbps (it used to be a fixed 6-8 Mbps VP8, which is why recordings looked soft). */
  hq(stream, fb){
    const vt = stream && stream.getVideoTracks && stream.getVideoTracks()[0], st = vt && vt.getSettings ? vt.getSettings() : {}, w = st.width || (fb && fb.w) || 1920, h = st.height || (fb && fb.h) || 1080, fps = st.frameRate || (fb && fb.fps) || 30;
    try { if (vt) vt.contentHint = "detail"; } catch(e){}   // tell the encoder the picture is text / lines (charts), not film: it keeps edges sharp
    const ok = t => { try { return !!window.MediaRecorder && MediaRecorder.isTypeSupported(t); } catch(e){ return false; } };
    const L = [["video/mp4;codecs=avc1.640034", "mp4", .40], ["video/mp4;codecs=avc1.640033", "mp4", .40], ["video/mp4;codecs=avc1", "mp4", .40], ["video/webm;codecs=vp9", "webm", .25], ["video/webm;codecs=vp8", "webm", .2], ["video/webm", "webm", .2]];
    const m = L.find(x => ok(x[0])) || ["", "webm", .2];
    return {mime: m[0], ext: m[1], bps: Math.round(Math.max(24e6, Math.min(300e6, w*h*fps*m[2]))), w, h, fps};
  }
};
function wsShotBtn(){
  const b = el("button", null, "📸"); b.title = Lg("Screenshot of the whole workspace (PNG). Works on tablets too; a TradingView frame shows as a box", "لقطة شاشة لمساحة العمل كلها (PNG). بتشتغل على التابلت كمان؛ فريم تريدنج فيو بيظهر كمربع");
  b.onclick = async () => { if (b._busy) return; b._busy = true; b.classList.add("on");
    try { const c = await Snap.shot(); c.toBlob(bl => { if (!bl){ alert(Lg("The screenshot could not be made","ماقدرتش أعمل اللقطة")); return; } Snap.save(bl, "workspace-"+new Date().toISOString().slice(0, 19).replace(/[:T]/g, "-")+".png"); }, "image/png"); }
    catch(e){ alert(Lg("The screenshot could not be made: ","ماقدرتش أعمل اللقطة: ")+(e && e.message || e)); } finally { b._busy = false; b.classList.remove("on"); } };
  return b;
}
function wsRecBtn(){
  const b = el("button", null, "🖥"); let rec = null, chunks = [], timer = null, kill = null;
  b.title = Lg("Record the whole workspace as a video. Desktop: the browser asks which tab / screen to share. Tablet / phone: the page is recorded from inside (charts live; other widgets refresh every few seconds). Click again to stop and save",
    "سجّل مساحة العمل كلها فيديو. الكمبيوتر: المتصفح يسألك أي تاب/شاشة. التابلت/الموبايل: الصفحة بتتسجل من جوه (الشارتات لايف والويدجتس التانية بتتحدّث كل كام ثانية). اضغط تاني للإيقاف والحفظ");
  const finish = stream => { try { stream && stream.getTracks().forEach(tr => tr.stop()); } catch(e){} };
  const attach = (stream, q) => {
    const mime = q.mime, ext = q.ext; chunks = []; try { rec = new MediaRecorder(stream, Object.assign({videoBitsPerSecond: q.bps}, mime ? {mimeType: mime} : {})); } catch(e){ finish(stream); rec = null; alert(Lg("Recording is not supported in this browser","التسجيل مش مدعوم في المتصفح ده")); return false; }
    rec.ondataavailable = e => { if (e.data && e.data.size) chunks.push(e.data); };
    rec.onstop = () => { finish(stream); clearInterval(timer); if (kill) kill(); const type = (mime || "video/webm").split(";")[0]; if (chunks.length) Snap.save(new Blob(chunks, {type}), "workspace-"+Date.now()+"."+ext); rec = null; b.classList.remove("on"); b.textContent = "🖥"; };
    rec.start(1000); b.classList.add("on"); b.textContent = "⏹"; return true; };
  const inside = async () => {   // no screen share API (tablets / phones): draw the page into a canvas and record that
    const mime = Snap.mime(); if (!mime || !HTMLCanvasElement.prototype.captureStream){ alert(Lg("This browser cannot record video from the page (no MediaRecorder / captureStream). Use the 📸 screenshot, or record the tablet with its own screen recorder","المتصفح ده مش بيسجّل فيديو من الصفحة. استخدم 📸 للقطة، أو سجّل بمسجل شاشة التابلت نفسه")); return; }
    const vw = Math.max(1, document.documentElement.clientWidth), vh = Math.max(1, document.documentElement.clientHeight), sc = Math.min(1.5, 1920/vw), out = document.createElement("canvas"); out.width = Math.round(vw*sc); out.height = Math.round(vh*sc);
    const x = out.getContext("2d"); let base = null, busy = false; const refresh = async () => { if (busy) return; busy = true; try { base = await Snap.shot(sc); } catch(e){} busy = false; };
    await refresh(); const frame = () => { x.fillStyle = "#0b0e11"; x.fillRect(0, 0, out.width, out.height); if (base) x.drawImage(base, 0, 0, out.width, out.height);
      document.querySelectorAll("canvas").forEach(cv => { if (cv === out) return; const r = cv.getBoundingClientRect(); if (r.width < 4 || r.height < 4 || r.bottom < 0 || r.top > vh) return; try { x.drawImage(cv, r.left*sc, r.top*sc, r.width*sc, r.height*sc); } catch(e){} }); };
    frame(); const fi = setInterval(frame, 40), ri = setInterval(refresh, 4000), stopT = setTimeout(() => { if (rec && rec.state !== "inactive") rec.stop(); }, 10*60*1000);   // 25 fps, widgets every 4 s, 10 minutes at most
    kill = () => { clearInterval(fi); clearInterval(ri); clearTimeout(stopT); kill = null; };
    const stream = out.captureStream(25), q = Snap.hq(stream, {w:out.width, h:out.height, fps:25}); if (!attach(stream, q)) kill(); };
  const G = () => { try { return window.parent && window.parent.__xpixRec; } catch(e){ return null; } };   // the page-wide recorder (modules/screen_recorder.js): it keeps recording when you change page
  { const sync = () => { const g = G(); if (g){ const st = g.state(); b.classList.toggle("on", st.recording); b.textContent = st.recording ? "⏹" : "🖥"; } }; setInterval(sync, 700); }
  b.onclick = async () => {
    { const g = G(); if (g){ g.toggle(); return; } }
    if (rec){ rec.stop(); return; }
    const gdm = navigator.mediaDevices && navigator.mediaDevices.getDisplayMedia; if (!gdm){ await inside(); return; }
    let stream; try { stream = await navigator.mediaDevices.getDisplayMedia({video:{cursor:"always", frameRate:{ideal:60, max:60}, width:{ideal:7680}, height:{ideal:4320}}, audio:false}); }
    catch(e){ if (e && /Security|TypeError|NotSupported/i.test(e.name || "")) await inside(); return; }   // blocked inside this frame (permissions policy): record from inside; a cancelled picker just returns
    if (!attach(stream, Snap.hq(stream))) return;
    const vt = stream.getVideoTracks()[0]; if (vt) vt.onended = () => { if (rec && rec.state !== "inactive") rec.stop(); };
  };
  return b;
}
function buildBar(){
  const bar = document.getElementById("bar"); bar.innerHTML = "";
  if (CFG.build){ const bld = el("span", "bld", "build "+CFG.build); bld.title = Lg("The commit of the code that is running now (after a merge the app needs a few minutes and a Reboot from Streamlit Cloud)", "رقم الكومت اللي شغال دلوقتي (بعد أي دمج التطبيق بياخد كام دقيقة ومحتاج Reboot من Streamlit Cloud)"); bld.style.cssText = "order:99;margin-left:auto;font:10px ui-monospace,Menlo,Consolas,monospace;color:#6b7684;padding:0 8px;white-space:nowrap;align-self:center"; bar.append(bld); }   // which build is live
  const sel = el("select"); sel.append(Object.assign(el("option"), {textContent:T("add"), value:""}));
  [[Lg("Decision","القرار"), ["chart","setup","signals","alerts"]], [Lg("Execution / order flow","التنفيذ والأوردر فلو"), ["dom","tape","limits","risk"]], [Lg("Markets","الأسواق"), ["tvc","scanner","watch","valuelv","rsihm","fundhm","posn","liq","web"]], [Lg("Context (fundamental)","السياق (الأساسي)"), ["fund","macrof","stockf","cmc","news"]], [Lg("Review","المراجعة"), ["journal","notes"]], [Lg("Settings","الإعدادات"), ["settings"]]]
    .forEach(([g, ts]) => { const og_ = Object.assign(el("optgroup"), {label:g}); ts.forEach(t => og_.append(Object.assign(el("option"), {textContent:T(t), value:t}))); sel.append(og_); });
  const og = Object.assign(el("optgroup"), {label: lang === "ar" ? "التخطيط" : "Layout"}); [["@std",Lg("Standard: 4 charts + order flow","الستاندر: ٤ شارتس + أوردر فلو")],["@save",Lg("Save current layout as my standard","احفظ التخطيط الحالي كستاندر بتاعي")],["@trading",T("trading")],["@blank",T("blank")]].forEach(([v,t]) => og.append(Object.assign(el("option"), {textContent:t, value:v}))); sel.append(og);
  sel.onchange = () => { const v = sel.value; if (v === "@trading" || v === "@std"){ Ws.clear(); Ws.build(Ws.defaults()); Ws.save(); } else if (v === "@save"){ try { store.set(LS+"_std", { v:7, panels: Ws.panels.map(p => ({type:p.type, rect: p.max && p.prev ? p.prev : p.rect, state:p.state})) }); alert(Lg("Saved: this layout is now your standard (it opens first, and \"Standard\" restores it).", "اتحفظ: التخطيط ده بقى الستاندر بتاعك (بيفتح أول حاجة، و«الستاندر» بيرجّعه).")); } catch(e){} } else if (v === "@blank"){ Ws.clear(); Ws.save(); } else if (v) Ws.add(v); sel.value = ""; };
  const ub = el("button", null, "↶"), rb = el("button", null, "↷"); ub.id = "undoB"; rb.id = "redoB"; ub.onclick = () => Ws.undo(); rb.onclick = () => Ws.redo(); ub.style.cssText = rb.style.cssText = "padding:2px 8px;font-size:14px";
  const zKey = LS+"_us_"+(CFG.ui || "classic"), zDef = {lux:1.06, hud:1.04}[CFG.ui] || 1, zSet = v => { v = Math.max(.5, Math.min(1.4, Math.round(v*100)/100)); document.documentElement.style.setProperty("--us", v); CHART_S = Math.max(.5, Math.min(1.4, v/zDef)); store.set(zKey, v); zLbl.textContent = Math.round(v*100)+"%"; setTimeout(() => { try { Ws.panels.forEach(p => p.chart && (p.chart.resize ? p.chart.resize() : 0, p.chart.draw())); } catch(e){} }, 320); };
  const zm = el("button", null, "−"), zp = el("button", null, "+"), zLbl = el("span"); zm.title = Lg("Smaller interface","تصغير الواجهة"); zp.title = Lg("Bigger interface","تكبير الواجهة"); zLbl.style.cssText = "color:var(--mut);min-width:34px;text-align:center;cursor:pointer"; zLbl.title = Lg("Back to the theme's size","رجوع لحجم الثيم");
  zm.onclick = () => zSet((+store.get(zKey, zDef)) - .05); zp.onclick = () => zSet((+store.get(zKey, zDef)) + .05); zLbl.onclick = () => zSet(zDef);
zSet(+store.get(zKey, zDef));   // the saved size applies from the start, so the charts open at it too
const gb = el("button", null, '<span class="gbi">'+GUIDE_ICON+'</span><b>Mr X</b>'); gb.id = "guideB"; gb.title = Lg("Your guide: walks to any part of the screen and explains it","المساعد: يروح لأي حتة في الشاشة ويشرحها"); gb.onclick = () => { Guide.init(); Guide.on ? Guide.close() : Guide.open(); };
if (!CFG.mrxOn) gb.hidden = true;   // Mr X is in development: the button stays hidden until the official launch
if (!MOB){ bar.append(sel, ub, rb, zm, zLbl, zp, gb, wsShotBtn(), wsRecBtn(), el("span","sp")); }
  else {   // phones: a settings button keeps the bar short - the MT5 layout switch and the interface size live under it
    const gear = el("button", null, "⚙"), menu = el("div"); menu.id = "mset"; gear.title = Lg("Settings","الإعدادات");
    const mt = el("button"), mtLbl = () => { mt.textContent = (MT5 ? "✓ " : "○ ")+Lg("MetaTrader layout","واجهة ميتاتريدر"); };
    mt.onclick = () => { MT5 = !MT5; store.set(LS+"_mt5", MT5); document.body.classList.toggle("mt5", MT5); mtLbl(); menu.classList.remove("on");   // switch live, no reload
      Ws.panels.forEach(p => p.apply()); Ws.mjump(); if (!MT5 && Ws.panels[0]) Ws.el.scrollTop = 0;
      setTimeout(() => Ws.panels.forEach(p => { try { p.chart && (p.chart.resize ? p.chart.resize() : 0, p.chart.draw()); } catch(_){} }), 60); };
    mtLbl();
    const zr = el("div"); zr.style.cssText = "display:flex;align-items:center;gap:6px;padding:8px 12px"; zr.append(el("span", null, Lg("Size","الحجم")), zm, zLbl, zp);
    const cap = el("div"); cap.style.cssText = "display:flex;align-items:center;gap:8px;padding:8px 12px"; cap.append(el("span", null, Lg("Capture","التصوير")), wsShotBtn(), wsRecBtn());
    menu.append(mt, zr, cap); gear.onclick = e => { e.stopPropagation(); menu.classList.toggle("on"); }; document.addEventListener("click", e => { if (!menu.contains(e.target)) menu.classList.remove("on"); });
    bar.append(sel, ub, rb, gb, el("span","sp"), gear); document.body.append(menu); }
  zSet(+store.get(zKey, zDef)); Ws.histUI();
  const d = el("span"); d.id = "dot"; bar.append(d);
}
function applyLang(rebuild){
  document.documentElement.lang = lang; document.body.classList.toggle("rtl", lang === "ar");
  buildBar();
  if (rebuild){ const snap = Ws.panels.map(p => [p.type, p.max && p.prev ? p.prev : p.rect, p.state]); Ws.clear(); Ws.build(snap); Ws.save(); }
  Ws.checkEmpty();
}
(function init(){
  let saved = null; try { const own = sessionStorage.getItem(LS+"_tab"); if (own) saved = JSON.parse(own); } catch(e){}
  if (!saved) saved = store.get(LS, null);   // task 54: a reloaded tab keeps its own layout
  lang = CFG.lang || (saved && saved.lang) || "en";
  document.documentElement.lang = lang; document.body.classList.toggle("rtl", lang === "ar"); document.body.classList.toggle("mob", MOB); document.body.classList.toggle("tch", TCH); document.body.classList.toggle("tab", TAB); document.body.classList.toggle("mt5", MT5); buildBar();
  if (MOB) document.addEventListener("click", e => { const b = e.target.closest(".dt > :first-child"); if (b) b.parentElement.classList.toggle("open"); }, true);
  if (saved && saved.v >= 7 && Array.isArray(saved.panels)) Ws.build(saved.panels.map(p => [p.type, p.rect, p.state]));
  else if (MOB){ const keep = ["chart","setup","signals","watch","alerts","tape"]; Ws.build(Ws.defaultsMobile().filter(([t, , st]) => keep.includes(t) && !(t === "chart" && st.tf === "15s")).sort((a, b) => keep.indexOf(a[0]) - keep.indexOf(b[0]))); Ws.save(); }   // phone, first visit: a short stacked set instead of an empty screen
  else if (/[?&]blank=1\b/.test(location.search)) Ws.build([]);   // ?blank=1 (the mock tests build their own layouts) keeps the old empty start
  else { Ws.build(Ws.defaults()); Ws.save(); }   // first visit / a fresh browser / any automation: the STANDARD layout (watch list + 4 charts with order flow + DOM / limits / tape), never an empty workspace; "Blank" in the Layout menu still gives a blank canvas
  if (CFG.mat && CFG.mat !== "none") document.body.classList.add("mat-" + CFG.mat);
  try { welcome(); } catch(e){}
  if (CFG.mrxOn) try { Guide.init(); if (store.get(LS+"_gon", true) !== false) setTimeout(() => Guide.open(), 1500); } catch(e){ console.error(e); }   // off until the official launch (MRX_LIVE=1): no presenter on screen, no photo in the DOM   // the presenter comes on stage by himself after start-up unless he was sent off (✕)
  window.__ws = Ws; Ws.histPush(); setTimeout(() => { try { localStorage.removeItem(LS + "_boot"); } catch(e){} }, 5000);   // a freeze while drawing blocks this timer, so the flag stays
  if (window.__wsSafeBoot){ const n = document.createElement("div"); n.style.cssText = "position:fixed;left:50%;top:44px;transform:translateX(-50%);z-index:9999;background:#2b2410;color:#f0b90b;border:1px solid #f0b90b;border-radius:6px;padding:6px 12px;font:12px sans-serif";
    n.textContent = Lg("The Workspace did not load last time, so its saved layout was reset (journal kept). Add widgets with + Widget.", "الورك سبيس ما فتحش آخر مرة، فاتعمل reset للترتيب المحفوظ (الجورنال محفوظ). ضيف الويدجتات من + Widget.");
    document.body.appendChild(n); setTimeout(() => n.remove(), 12000); }
})();
// table columns (team tasks 11 + 12): drag a header's edge to resize (ellipsis + min width), drag a header onto another to reorder.
// Saved per table "shape" (the header texts in their default order), so tables of the same kind share their layout. Mouse only (no touch drag yet).
(function(){
  const LS = "xpix_cols_v1"; let st = {}; try { st = JSON.parse(localStorage.getItem(LS) || "{}") || {}; } catch(e){}
  const save = () => { try { localStorage.setItem(LS, JSON.stringify(st)); } catch(e){} };
  const movePerm = (perm, from, to) => { const p = perm.slice(); p.splice(to, 0, p.splice(from, 1)[0]); return p; };
  const hdr = tb => (tb.tHead && tb.tHead.rows[0]) || tb.rows[0];
  const flat = r => Array.from(r.cells).every(c => c.colSpan === 1);
  const applyPerm = (r, perm, key) => { const cs = Array.from(r.cells); if (cs.length !== perm.length || !flat(r)){ r._cx = "skip"; return; } perm.forEach(i => r.appendChild(cs[i])); r._cx = key; };
  let drag = null, busy = false, queued = false, obs = null;
  const sync = tb => {
    const h = hdr(tb); if (!h || h.cells.length < 2) return;
    if (h._cx === undefined){   // new header row: read the default-order signature, then apply the saved order
      if (!flat(h)){ tb._cx = null; h._cx = "skip"; return; }
      const n = h.cells.length, sig = Array.from(h.cells).map(c => (c.textContent || "").trim()).join("|"), s = st[sig];
      const perm = s && s.perm && s.perm.length === n ? s.perm.slice() : Array.from({length:n}, (_, i) => i);
      tb._cx = {sig, perm, n, key: perm.join(",")}; tb.classList.add("colx");
    }
    const cx = tb._cx; if (!cx) return;
    Array.from(tb.rows).forEach(r => { if (r._cx === undefined && r.cells.length === cx.n) applyPerm(r, cx.perm, cx.key); });
    const s = st[cx.sig], w = s && s.w;
    Array.from(h.cells).forEach((c, p) => {
      if (w && w[cx.perm[p]] && !c.style.width){ c.style.width = w[cx.perm[p]] + "px"; tb.classList.add("fx"); }
      if (!c.querySelector(".cx-h")){ const g = document.createElement("span"); g.className = "cx-h"; g.draggable = false; c.appendChild(g); }
      c.draggable = true;
    });
  };
  const run = () => { queued = false; busy = true; document.querySelectorAll("table.rdt, table.wt").forEach(tb => { try { sync(tb); } catch(e){} }); if (obs) obs.takeRecords(); busy = false; };
  const sched = () => { if (busy || queued) return; queued = true; setTimeout(run, 150); };   // setTimeout, not rAF: rAF never fires while the page is hidden / not painting
  const tableOf = n => n && n.closest && n.closest("table.colx");
  document.addEventListener("pointerdown", e => {   // resize: drag the right edge handle of a header cell
    const g = e.target.closest && e.target.closest(".cx-h"), th = g && g.parentElement, tb = tableOf(th); if (!tb || !tb._cx) return;
    e.preventDefault(); e.stopPropagation(); const cx = tb._cx, h = hdr(tb), cells = Array.from(h.cells), idx = cells.indexOf(th);
    cells.forEach(c => { c.style.width = c.offsetWidth + "px"; }); tb.classList.add("fx");
    const sx = e.clientX, sw = th.offsetWidth, dir = getComputedStyle(tb).direction === "rtl" ? -1 : 1; th.draggable = false;
    const mv = ev => { th.style.width = Math.max(28, sw + (ev.clientX - sx) * dir) + "px"; };
    const up = () => { document.removeEventListener("pointermove", mv, true); document.removeEventListener("pointerup", up, true); th.draggable = true;
      const w = {}; cells.forEach((c, p) => { w[cx.perm[p]] = Math.round(c.offsetWidth); }); (st[cx.sig] = st[cx.sig] || {perm: cx.perm.slice()}).w = w; save(); };
    document.addEventListener("pointermove", mv, true); document.addEventListener("pointerup", up, true);
  }, true);
  document.addEventListener("dragstart", e => { const th = e.target.closest && e.target.closest("th"), tb = tableOf(th); if (!tb || !tb._cx || e.target.closest(".cx-h")){ return; }
    drag = {tb, from: Array.from(hdr(tb).cells).indexOf(th)}; try { e.dataTransfer.effectAllowed = "move"; e.dataTransfer.setData("text/plain", ""); } catch(x){} });
  document.addEventListener("dragover", e => { const th = e.target.closest && e.target.closest("th"); if (drag && th && tableOf(th) === drag.tb){ e.preventDefault(); document.querySelectorAll("th.cx-over").forEach(x => x.classList.remove("cx-over")); th.classList.add("cx-over"); } });
  document.addEventListener("drop", e => { const th = e.target.closest && e.target.closest("th"); document.querySelectorAll("th.cx-over").forEach(x => x.classList.remove("cx-over"));
    if (!drag || !th || tableOf(th) !== drag.tb){ drag = null; return; } e.preventDefault();
    const tb = drag.tb, cx = tb._cx, from = drag.from, to = Array.from(hdr(tb).cells).indexOf(th); drag = null; if (from < 0 || to < 0 || from === to) return;
    busy = true; Array.from(tb.rows).forEach(r => { if (r._cx === cx.key && r.cells.length === cx.n){ const cs = Array.from(r.cells); r.insertBefore(cs[from], to > from ? cs[to].nextSibling : cs[to]); } });
    cx.perm = movePerm(cx.perm, from, to); cx.key = cx.perm.join(","); Array.from(tb.rows).forEach(r => { if (r._cx !== undefined && r._cx !== "skip") r._cx = cx.key; });
    (st[cx.sig] = st[cx.sig] || {}).perm = cx.perm.slice(); save(); if (obs) obs.takeRecords(); busy = false; });
  document.addEventListener("dragend", () => { drag = null; document.querySelectorAll("th.cx-over").forEach(x => x.classList.remove("cx-over")); });
  document.addEventListener("mouseover", e => { const c = e.target.closest && e.target.closest("table.colx.fx td"); if (c && !c.title) c.title = (c.textContent || "").trim(); });
  // only react when a table (or a row/header inside one) was added: the page re-renders its live data many times a second
  obs = new MutationObserver(recs => { for (const r of recs){ for (const n of r.addedNodes){ if (n.nodeType === 1 && (n.tagName === 'TABLE' || n.tagName === 'TR' || n.tagName === 'THEAD' || (n.querySelector && n.querySelector('table')))) { sched(); return; } } } });
  obs.observe(document.body, {childList:true, subtree:true}); sched();
  window.__xpixCols = {movePerm};   // for tests
})();

/* Tablet: the workspace frame is much taller than the screen and a finger on a chart moves the chart, so there was nothing to scroll the page with.
   A small handle (⇕) on the right edge of the VISIBLE part: drag it up / down and the page scrolls. Touch screens only; hidden when the frame fits the screen. */
(() => {
  if (!TCH || MOB) return; let fe = null; try { fe = window.frameElement; } catch(e){} if (!fe) return;
  const rail = document.createElement("div"); rail.id = "xrail"; rail.textContent = "⇕"; rail.title = "Drag up / down to scroll the page";
  rail.style.cssText = "position:absolute;right:4px;width:38px;height:104px;border-radius:19px;background:rgba(240,185,11,.30);border:1px solid rgba(240,185,11,.7);color:#f0b90b;display:none;align-items:center;justify-content:center;font:bold 20px sans-serif;z-index:99999;touch-action:none;user-select:none;-webkit-user-select:none";
  document.body.append(rail);
  const scroller = () => { try { let e = fe; while (e && (e = e.parentElement)){ const o = window.parent.getComputedStyle(e).overflowY; if (/(auto|scroll)/.test(o) && e.scrollHeight > e.clientHeight + 20) return e; } } catch(e){} return null; };
  const place = () => { try { const r = fe.getBoundingClientRect(), H = window.parent.innerHeight, top = Math.max(0, -r.top), bot = Math.min(innerHeight, H - r.top);
    if (innerHeight < H + 120){ rail.style.display = "none"; return; }   // the frame fits on the screen: nothing to scroll
    rail.style.display = "flex"; rail.style.top = Math.round(top + (bot - top)/2 - 52)+"px"; } catch(e){} };
  let sy = null; rail.addEventListener("pointerdown", e => { sy = e.screenY; rail.setPointerCapture(e.pointerId); e.preventDefault(); e.stopPropagation(); });
  rail.addEventListener("pointermove", e => { if (sy == null) return; const dy = (e.screenY - sy)*2.2; sy = e.screenY; try { const sc = scroller(); sc ? sc.scrollBy({top:dy}) : window.parent.scrollBy({top:dy}); } catch(e){} });
  const end = () => { sy = null; }; rail.addEventListener("pointerup", end); rail.addEventListener("pointercancel", end);
  let q = 0; const sched = () => { if (q) return; q = requestAnimationFrame(() => { q = 0; place(); }); };
  try { window.parent.addEventListener("scroll", sched, true); window.parent.addEventListener("resize", sched); } catch(e){} setInterval(place, 1500); place();
  window.__xpixRail = {place, rail};   // for tests
})();
