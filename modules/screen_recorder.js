/* XPiX screen recorder + quick video editor (runs in the PARENT page, so it survives every Streamlit page switch: Workspace, Radar, Technical Office, Academy ...).
   Injected once by modules/screen_recorder.py (singleton: window.__xpixRec). Everything stays in this browser: no upload, no keys.
   Record: the browser's own screen / window / tab share (getDisplayMedia), the real pixels, up to 8K at 60 fps, best codec (H.264 MP4 first, then VP9 / VP8), bitrate follows the real size.
   Controls (always on screen, draggable): red dot = record, pause / continue, flag (mark a moment), stop. Clips tray: edit / save / delete.
   Editor: trim (in / out), several segments joined, speed-up (1-16x), flags to jump to, frame -> PNG, export (real time re-encode, high quality). */
(() => {
  if (window.__xpixRec && window.__xpixRec.v >= 1) return;
  const D = document, LSK = "xpix_rec_";
  const ls = { get(k, d){ try { const v = localStorage.getItem(LSK + k); return v == null ? d : JSON.parse(v); } catch(e){ return d; } }, set(k, v){ try { localStorage.setItem(LSK + k, JSON.stringify(v)); } catch(e){} } };
  const S = { v: 1, rec: null, stream: null, chunks: [], t0: 0, paused: false, pausedMs: 0, pAt: 0, flags: [], clips: [], q: ls.get("q", "max"), auto: ls.get("auto", true), fmt: null, subs: [], seq: 0 };
  const Q = { max: { h264: .40, vp9: .25, cap: 300e6, min: 24e6, name: "Max" }, high: { h264: .20, vp9: .12, cap: 120e6, min: 12e6, name: "High" }, bal: { h264: .08, vp9: .05, cap: 40e6, min: 8e6, name: "Balanced" } };
  const ok = t => { try { return !!window.MediaRecorder && MediaRecorder.isTypeSupported(t); } catch(e){ return false; } };
  const pick = () => [["video/mp4;codecs=avc1.640034", "mp4", "h264"], ["video/mp4;codecs=avc1.640033", "mp4", "h264"], ["video/mp4;codecs=avc1", "mp4", "h264"], ["video/webm;codecs=vp9", "webm", "vp9"], ["video/webm;codecs=vp8", "webm", "vp9"], ["video/webm", "webm", "vp9"]].find(x => ok(x[0])) || ["", "webm", "vp9"];
  const opts = (w, h, fps, q) => { const m = pick(), Z = Q[q || S.q] || Q.max; return { mime: m[0], ext: m[1], bps: Math.round(Math.max(Z.min || 12e6, Math.min(Z.cap, w * h * fps * Z[m[2]]))) }; };
  const fmtT = ms => { const s = Math.max(0, Math.floor(ms / 1000)), m = Math.floor(s / 60); return String(m).padStart(2, "0") + ":" + String(s % 60).padStart(2, "0"); };
  const stamp = () => new Date().toISOString().slice(0, 19).replace(/[:T]/g, "-");
  const emit = () => { S.subs.forEach(f => { try { f(api.state()); } catch(e){} }); render(); };
  const save = (blob, name) => { const u = URL.createObjectURL(blob), a = D.createElement("a"); a.href = u; a.download = name; D.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(u), 15000); };
  const el = (tag, css, txt) => { const e = D.createElement(tag); if (css) e.style.cssText = css; if (txt != null) e.textContent = txt; return e; };

  /* ---------- recording ---------- */
  const elapsed = () => S.rec ? (S.paused ? S.pAt : Date.now()) - S.t0 - S.pausedMs : 0;
  async function start(){
    if (S.rec) return { ok: false, err: "already recording" };
    if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia || !window.MediaRecorder){ const touch = (navigator.maxTouchPoints || 0) > 0 && !/Windows|Macintosh.*Chrome/.test(navigator.userAgent) || /iPad|iPhone|Android/i.test(navigator.userAgent);
      alert(touch ? "Phones and tablets do not let a web page record the screen. Use the device's own recorder (it is the best quality there): iPhone / iPad: Control Center > Screen Recording (the red dot); Android: Quick Settings > Screen record. The clip lands in Photos / Gallery, and the editor here can open it from your files later." : "This browser cannot record the screen (no getDisplayMedia / MediaRecorder). Use desktop Chrome, Edge or Firefox."); return { ok: false, err: "unsupported" }; }
    let stream; try { stream = await navigator.mediaDevices.getDisplayMedia({ video: { cursor: "always", frameRate: { ideal: 60, max: 60 }, width: { ideal: 7680 }, height: { ideal: 4320 } }, audio: false }); } catch(e){ return { ok: false, err: String(e && e.name || e) }; }   // the browser gives the real pixels of what you pick, never upscaled
    const vt = stream.getVideoTracks()[0], st = vt && vt.getSettings ? vt.getSettings() : {}; try { if (vt) vt.contentHint = "detail"; } catch(e){}   // charts / text, not film: keep edges sharp
    const w = st.width || 1920, h = st.height || 1080, fps = st.frameRate || 30, o = opts(w, h, fps);
    let rec; try { rec = new MediaRecorder(stream, Object.assign({ videoBitsPerSecond: o.bps }, o.mime ? { mimeType: o.mime } : {})); } catch(e){ stream.getTracks().forEach(t => t.stop()); alert("Recording is not supported with these settings in this browser"); return { ok: false, err: "recorder" }; }
    S.chunks = []; S.flags = []; S.pausedMs = 0; S.paused = false; S.stream = stream; S.rec = rec; S.fmt = { w, h, fps, ext: o.ext, mime: o.mime || "video/webm", bps: o.bps }; S.t0 = Date.now();
    rec.ondataavailable = e => { if (e.data && e.data.size) S.chunks.push(e.data); };
    rec.onstop = () => { const f = S.fmt, blob = new Blob(S.chunks, { type: (f.mime || "video/webm").split(";")[0] }), dur = elapsed(); const clip = { id: ++S.seq, name: "xpix-" + stamp(), ext: f.ext, blob, dur, w: f.w, h: f.h, fps: f.fps, bps: f.bps, flags: S.flags.slice(), kind: "recording" };
      stream.getTracks().forEach(t => t.stop()); S.rec = null; S.stream = null; S.paused = false; S.chunks = []; S.clips.unshift(clip); if (S.auto) save(blob, clip.name + "." + clip.ext); emit(); S.openTray = true; render(); };
    if (vt) vt.onended = () => { if (S.rec && S.rec.state !== "inactive") api.stop(); };   // the browser's own "Stop sharing" bar
    rec.start(1000); emit(); return { ok: true, w, h, fps, mime: o.mime, bps: o.bps };
  }
  const api = {
    v: 1, S,
    start, toggle(){ return S.rec ? api.stop() : start(); },
    pause(){ if (S.rec && !S.paused && S.rec.state === "recording"){ S.rec.pause(); S.paused = true; S.pAt = Date.now(); emit(); } return api.state(); },
    resume(){ if (S.rec && S.paused){ S.rec.resume(); S.pausedMs += Date.now() - S.pAt; S.paused = false; emit(); } return api.state(); },
    flag(label){ if (S.rec){ S.flags.push({ t: elapsed(), label: label || "flag " + (S.flags.length + 1) }); emit(); } return api.state(); },
    stop(){ if (S.rec && S.rec.state !== "inactive"){ if (S.paused) api.resume(); S.rec.stop(); } return api.state(); },
    state(){ return { recording: !!S.rec, paused: S.paused, ms: elapsed(), flags: S.flags.length, clips: S.clips.map(c => ({ id: c.id, name: c.name, ext: c.ext, dur: c.dur, size: c.blob.size, w: c.w, h: c.h, fps: c.fps, kind: c.kind })), quality: S.q, autosave: S.auto, fmt: S.fmt }; },
    quality(q){ if (Q[q]){ S.q = q; ls.set("q", q); emit(); } return S.q; },
    clip(id){ return S.clips.find(c => c.id === id); },
    edit(id){ const c = api.clip(id || (S.clips[0] && S.clips[0].id)); if (c) openEditor(c); return !!c; },
    remove(id){ S.clips = S.clips.filter(c => c.id !== id); emit(); },
    on(f){ S.subs.push(f); return () => { S.subs = S.subs.filter(x => x !== f); }; },
    opts, pick
  };
  window.__xpixRec = api;

  /* ---------- the always-on-screen control (a red dot; while recording: lamp + time + pause + flag + stop) ---------- */
  const root = el("div", "position:fixed;z-index:2147483000;font:12px/1.2 -apple-system,Segoe UI,Roboto,sans-serif;color:#e6edf3;user-select:none;-webkit-user-select:none"); root.id = "xpix-rec";
  const pos = ls.get("pos", { r: 16, b: 16 }); root.style.right = pos.r + "px"; root.style.bottom = pos.b + "px";
  D.body.append(root);
  const style = el("style", null, "@keyframes xprec{0%,100%{opacity:1}50%{opacity:.25}}#xpix-rec button{font:inherit;color:inherit;border:0;background:transparent;cursor:pointer;padding:4px 7px;border-radius:6px}#xpix-rec button:hover{background:rgba(255,255,255,.14)}#xpix-rec .xp{background:rgba(17,22,28,.94);border:1px solid #2c3641;border-radius:999px;box-shadow:0 4px 18px rgba(0,0,0,.5);display:flex;align-items:center;gap:2px;padding:3px 5px}#xpix-rec .xpl{display:inline-block;width:11px;height:11px;border-radius:50%;background:#ff3b30;margin:0 5px}#xpix-rec .xpl.rec{animation:xprec 1s infinite}#xpix-rec .xpl.pz{background:#f0b90b}#xpix-rec .xpb{background:rgba(17,22,28,.97);border:1px solid #2c3641;border-radius:10px;box-shadow:0 8px 28px rgba(0,0,0,.6);padding:8px;margin-bottom:8px;min-width:300px;max-width:380px;max-height:50vh;overflow:auto}#xpix-rec .xpr{display:flex;align-items:center;gap:6px;padding:4px 2px;border-bottom:1px solid #222b34}#xpix-rec .xpr:last-child{border-bottom:0}");
  D.head.append(style);
  let drag = null;
  root.addEventListener("pointerdown", e => { if (e.target.closest("button,select,input,.xpb")) return; const r = root.getBoundingClientRect(); drag = { x: e.clientX, y: e.clientY, r: innerWidth - r.right, b: innerHeight - r.bottom }; root.setPointerCapture(e.pointerId); });
  root.addEventListener("pointermove", e => { if (!drag) return; root.style.right = Math.max(0, drag.r - (e.clientX - drag.x)) + "px"; root.style.bottom = Math.max(0, drag.b - (e.clientY - drag.y)) + "px"; });
  root.addEventListener("pointerup", () => { if (drag){ ls.set("pos", { r: parseInt(root.style.right), b: parseInt(root.style.bottom) }); drag = null; } });
  const btn = (txt, title, fn) => { const b = el("button", null, txt); b.title = title; b.onclick = e => { e.stopPropagation(); fn(); }; return b; };
  let tick = null;
  function render(){
    root.innerHTML = ""; const wrap = el("div", "display:flex;flex-direction:column;align-items:flex-end");
    if (S.openTray && S.clips.length){ const box = el("div", null); box.className = "xpb"; box.append(el("div", "font-weight:700;margin-bottom:4px", "Clips (this session)"));
      S.clips.forEach(c => { const r = el("div"); r.className = "xpr"; const nm = el("span", "flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap", c.name + "  " + fmtT(c.dur) + "  " + (c.blob.size / 1048576).toFixed(0) + " MB  " + c.w + "x" + c.h);
        r.append(nm, btn("✂", "Edit this clip (trim, join, speed-up, frame)", () => openEditor(c)), btn("⬇", "Save to disk", () => save(c.blob, c.name + "." + c.ext)), btn("✕", "Delete from this session", () => api.remove(c.id))); box.append(r); });
      const set = el("div", "margin-top:6px;display:flex;gap:6px;align-items:center;flex-wrap:wrap"); const qs = el("select", "background:#0b0e11;color:inherit;border:1px solid #2c3641;border-radius:6px;padding:2px"); Object.keys(Q).forEach(k => { const o = el("option", null, "Quality: " + Q[k].name); o.value = k; qs.append(o); }); qs.value = S.q; qs.onchange = () => api.quality(qs.value);
      const au = el("label", "display:flex;gap:4px;align-items:center"); const cb = el("input"); cb.type = "checkbox"; cb.checked = S.auto; cb.onchange = () => { S.auto = cb.checked; ls.set("auto", S.auto); }; au.append(cb, document.createTextNode("save file when I stop")); set.append(qs, au); box.append(set); wrap.append(box); }
    const pill = el("div"); pill.className = "xp";
    if (S.rec){ const lamp = el("span"); lamp.className = "xpl " + (S.paused ? "pz" : "rec"); const t = el("span", "min-width:40px;font-variant-numeric:tabular-nums;font-weight:700", fmtT(elapsed())); t.id = "xpix-rec-t";
      pill.append(lamp, t, btn(S.paused ? "▶" : "⏸", S.paused ? "Continue recording" : "Pause (the clip skips the pause)", () => S.paused ? api.resume() : api.pause()), btn("🚩", "Flag this moment (jump to it in the editor)", () => api.flag()), btn("⏹", "Stop and keep the clip", () => api.stop()));
      if (S.flags.length) pill.append(el("span", "opacity:.7;padding:0 4px", "🚩" + S.flags.length)); }
    else { const rb = btn("", "Record the screen: it follows you to every page (Workspace, Radar, Technical Office, Academy ...)", () => start()); const dot = el("span"); dot.className = "xpl"; rb.append(dot, document.createTextNode("REC")); pill.append(rb);
      pill.append(btn(Q[S.q].name, "Quality (click to change): Max = highest bitrate, High, Balanced = small files", () => { const q = Object.keys(Q); api.quality(q[(q.indexOf(S.q) + 1) % q.length]); }));
      if (S.clips.length) pill.append(btn("🎞 " + S.clips.length, "Clips: edit / save", () => { S.openTray = !S.openTray; render(); })); }
    wrap.append(pill); root.append(wrap);
    clearInterval(tick); if (S.rec && !S.paused) tick = setInterval(() => { const t = D.getElementById("xpix-rec-t"); if (t) t.textContent = fmtT(elapsed()); }, 500);
  }

  /* ---------- editor ---------- */
  function openEditor(clip){
    const ov = el("div", "position:fixed;inset:0;z-index:2147483100;background:rgba(5,8,12,.96);color:#e6edf3;font:13px -apple-system,Segoe UI,Roboto,sans-serif;display:flex;flex-direction:column;padding:12px;gap:8px"); ov.id = "xpix-edit";
    const url = URL.createObjectURL(clip.blob), v = el("video", "flex:1;min-height:0;max-height:62vh;background:#000;border-radius:8px;width:100%;object-fit:contain"); v.src = url; v.controls = true; v.playsInline = true; v.muted = true;
    const dur = () => isFinite(v.duration) && v.duration > 0 ? v.duration : clip.dur / 1000;
    let a = 0, b = null, segs = [], busy = false;   // a / b = in / out seconds of the pending range
    const bar = el("div", "position:relative;height:34px;background:#141a21;border:1px solid #2c3641;border-radius:6px;cursor:pointer"), sel = el("div", "position:absolute;top:0;bottom:0;background:rgba(240,185,11,.28);border-left:3px solid #f0b90b;border-right:3px solid #f0b90b"), head = el("div", "position:absolute;top:-2px;bottom:-2px;width:2px;background:#fff"), segsBox = el("div", "position:absolute;inset:0;pointer-events:none");
    bar.append(segsBox, sel, head); (clip.flags || []).forEach(f => { const m = el("div", "position:absolute;top:0;bottom:0;width:2px;background:#ff3b30", ""); m.dataset.t = f.t / 1000; m.title = f.label; m.style.pointerEvents = "none"; bar.append(m); });
    const pct = t => (100 * t / dur()) + "%", layout = () => { const B = b == null ? dur() : b; sel.style.left = pct(a); sel.style.width = (100 * Math.max(0, B - a) / dur()) + "%"; head.style.left = pct(v.currentTime || 0);
      segsBox.innerHTML = ""; segs.forEach(s => { const d = el("div", "position:absolute;top:0;bottom:0;background:rgba(14,203,129,.35)"); d.style.left = pct(s[0]); d.style.width = (100 * (s[1] - s[0]) / dur()) + "%"; segsBox.append(d); });
      info.textContent = "In " + a.toFixed(2) + "s · Out " + (b == null ? dur() : b).toFixed(2) + "s · clip " + dur().toFixed(1) + "s · segments: " + segs.length + (segs.length ? " (" + segs.reduce((s, x) => s + (x[1] - x[0]), 0).toFixed(1) + "s)" : "") + (busy ? "" : ""); list.innerHTML = "";
      segs.forEach((s, i) => { const r = el("div", "display:flex;gap:6px;align-items:center"); r.append(el("span", null, (i + 1) + ". " + s[0].toFixed(2) + " → " + s[1].toFixed(2) + "s"), mk("▶", "Play this segment", () => { v.currentTime = s[0]; v.play(); }), mk("✕", "Remove segment", () => { segs.splice(i, 1); layout(); })); list.append(r); }); };
    const mk = (txt, title, fn) => { const x = el("button", "background:#1d2630;color:inherit;border:1px solid #2c3641;border-radius:6px;padding:5px 9px;cursor:pointer;font:inherit", txt); x.title = title; x.onclick = fn; return x; };
    const seek = e => { const r = bar.getBoundingClientRect(); v.currentTime = Math.max(0, Math.min(dur(), (e.clientX - r.left) / r.width * dur())); };
    bar.onpointerdown = e => { seek(e); const mv = ev => seek(ev), up = () => { removeEventListener("pointermove", mv); removeEventListener("pointerup", up); }; addEventListener("pointermove", mv); addEventListener("pointerup", up); };
    v.ontimeupdate = layout; v.onloadedmetadata = () => { if (v.duration === Infinity){ v.currentTime = 1e101; v.ontimeupdate = () => { v.ontimeupdate = layout; v.currentTime = 0; layout(); }; } else layout(); };   // MediaRecorder WebM has no duration header: seeking far makes the browser compute it
    const info = el("div", "opacity:.85"), list = el("div", "display:flex;flex-direction:column;gap:2px;max-height:90px;overflow:auto"), status = el("div", "color:#f0b90b;min-height:16px");
    const row1 = el("div", "display:flex;gap:6px;flex-wrap:wrap;align-items:center");
    const spd = el("select", "background:#0b0e11;color:inherit;border:1px solid #2c3641;border-radius:6px;padding:4px"); [1, 2, 4, 8, 16].forEach(x => { const o = el("option", null, "Speed ×" + x); o.value = x; spd.append(o); });
    const flagsSel = el("select", "background:#0b0e11;color:inherit;border:1px solid #2c3641;border-radius:6px;padding:4px"); flagsSel.append(Object.assign(el("option", null, "🚩 flags (" + (clip.flags || []).length + ")"), { value: "" })); (clip.flags || []).forEach(f => { const o = el("option", null, fmtT(f.t) + " " + f.label); o.value = f.t / 1000; flagsSel.append(o); }); flagsSel.onchange = () => { if (flagsSel.value !== "") v.currentTime = +flagsSel.value; };
    row1.append(mk("[ In", "Set the start of the range to the playhead", () => { a = v.currentTime; if (b != null && b <= a) b = null; layout(); }), mk("] Out", "Set the end of the range to the playhead", () => { b = Math.max(a + .05, v.currentTime); layout(); }),
      mk("+ Add segment", "Keep the In→Out range (add several to join them)", () => { const B = b == null ? dur() : b; if (B - a > .05){ segs.push([a, B]); a = B; b = null; layout(); } }), mk("Clear segments", "Remove all segments", () => { segs = []; layout(); }), flagsSel, spd,
      mk("◀ -1s", "Back one second", () => { v.currentTime = Math.max(0, v.currentTime - 1); }), mk("+1s ▶", "Forward one second", () => { v.currentTime = Math.min(dur(), v.currentTime + 1); }), mk("📸 Frame", "Save the current frame as PNG (full resolution)", () => { const c = el("canvas"); c.width = v.videoWidth; c.height = v.videoHeight; c.getContext("2d").drawImage(v, 0, 0); c.toBlob(bl => bl && save(bl, clip.name + "-" + v.currentTime.toFixed(1) + "s.png"), "image/png"); }));
    const row2 = el("div", "display:flex;gap:6px;flex-wrap:wrap;align-items:center");
    async function exportEdited(){
      if (busy) return; const ranges = segs.length ? segs.slice() : [[a, b == null ? dur() : b]]; const total = ranges.reduce((s, x) => s + (x[1] - x[0]), 0); if (total < .1){ status.textContent = "Pick a range first (In / Out)"; return; }
      const sp = +spd.value || 1, W = v.videoWidth, H = v.videoHeight, fps = Math.max(30, Math.min(60, clip.fps || 30)), o = opts(W, H, fps), cv = el("canvas"); cv.width = W; cv.height = H; const cx = cv.getContext("2d"); cx.imageSmoothingEnabled = false;
      const stream = cv.captureStream(fps); let rec; try { rec = new MediaRecorder(stream, Object.assign({ videoBitsPerSecond: o.bps }, o.mime ? { mimeType: o.mime } : {})); } catch(e){ status.textContent = "Export is not supported in this browser"; return; }
      const ch = []; rec.ondataavailable = e => { if (e.data && e.data.size) ch.push(e.data); }; const done = new Promise(res => { rec.onstop = res; }); busy = true; v.pause(); v.muted = true; rec.start(500); let doneT = 0, stop = false;
      const cancel = mk("Cancel", "Stop the export", () => { stop = true; }); row2.append(cancel);
      try { for (const [s0, s1] of ranges){ if (stop) break; v.currentTime = s0; await new Promise(r => { v.onseeked = () => { v.onseeked = null; r(); }; }); v.playbackRate = sp; await v.play();
          await new Promise(res => { const step = () => { if (stop || v.currentTime >= s1 - .02 || v.ended){ v.pause(); res(); return; } cx.drawImage(v, 0, 0, W, H); status.textContent = "Exporting " + Math.round(100 * (doneT + Math.max(0, v.currentTime - s0)) / total) + " %  (real time ÷ speed; keep this tab visible)"; (v.requestVideoFrameCallback ? v.requestVideoFrameCallback.bind(v) : requestAnimationFrame)(step); }; step(); });
          doneT += s1 - s0; } } finally { v.playbackRate = 1; rec.state !== "inactive" && rec.stop(); await done; stream.getTracks().forEach(t => t.stop()); cancel.remove(); busy = false; }
      if (stop){ status.textContent = "Cancelled"; return; }
      const blob = new Blob(ch, { type: (o.mime || "video/webm").split(";")[0] }), nc = { id: ++S.seq, name: clip.name + "-edit", ext: o.ext, blob, dur: Math.round(total / sp * 1000), w: W, h: H, fps, bps: o.bps, flags: [], kind: "edit" }; S.clips.unshift(nc); save(blob, nc.name + "." + nc.ext); status.textContent = "Saved " + nc.name + "." + nc.ext + " (" + (blob.size / 1048576).toFixed(0) + " MB)"; emit();
    }
    row2.append(mk("⬇ Export edited", "Cut + join + speed, re-encoded at high quality (real time) and saved", exportEdited), mk("⬇ Save original", "Save the untouched recording", () => save(clip.blob, clip.name + "." + clip.ext)), mk("Close", "Close the editor", () => { v.pause(); URL.revokeObjectURL(url); ov.remove(); }));
    ov.append(el("div", "font-weight:700", "Edit: " + clip.name + "  (" + clip.w + "x" + clip.h + ", " + (clip.blob.size / 1048576).toFixed(0) + " MB)"), v, bar, info, row1, list, row2, status);
    D.body.append(ov); layout();
  }
  render();
})();
