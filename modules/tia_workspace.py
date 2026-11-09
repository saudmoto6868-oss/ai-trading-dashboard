"""TIA's isolated interactive workspace shell.

Uses the existing browser-side chart/widget engine with a TIA-only storage namespace.
Original Workspace layouts, drawings and preferences remain untouched.
"""
from __future__ import annotations
import streamlit.components.v1 as components
from modules.workspace import build_workspace_html


def render_tia_workspace(height: int = 980, universe: str = "Crypto"):
    if universe == "Crypto":
        symbols = ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT"]
        asset_class = "Crypto"
    else:
        symbols = ["HL:xyz:GOLD", "HL:xyz:SILVER", "HL:xyz:SP500",
                   "HL:xyz:XYZ100", "HL:xyz:EUR", "HL:xyz:GBP",
                   "HL:xyz:CL", "HL:xyz:BRENTOIL", "HL:xyz:JP225"]
        asset_class = "TradFi"
    doc = build_workspace_html(symbols=symbols, news=[], lang="en", asset_cls=asset_class,
                               ui_theme="gold", ui_mat="steel")
    # Add TIA-native panels to the existing draggable/resizable panel system.
    tia_panels = r'''
Panel.prototype.build_tiapulse = function(){
  const box = el("div"); box.style.cssText = "padding:8px;overflow:auto;height:100%;";
  const note = el("div","m", "Live ticker snapshot · provider coverage only"); note.style.cssText += "margin-bottom:8px;font-size:11px";
  const table = el("table"); table.style.cssText = "width:100%;border-collapse:collapse;font:12px ui-monospace,Menlo,monospace";
  const head = el("tr"); ["SYMBOL","LAST","24H %","FEED"].forEach(x=>{const th=el("th",null,x);th.style.cssText="text-align:right;padding:6px;border-bottom:1px solid var(--line)";head.append(th);}); table.append(head);
  const rows = new Map();
  const fmt = v => Number.isFinite(v) ? v.toLocaleString(undefined,{maximumFractionDigits:6}) : "—";
  const render = data => {
    const symbols = (SYMS||[]).slice(0,40);
    symbols.forEach(sym=>{
      const q=data && data[sym]; let tr=rows.get(sym);
      if(!tr){ tr=el("tr"); rows.set(sym,tr); for(let i=0;i<4;i++){const td=el("td");td.style.cssText="padding:7px 5px;text-align:right;border-bottom:1px solid var(--line);white-space:nowrap";tr.append(td);} table.append(tr); }
      const pct=q && q.open>0 ? (q.last/q.open-1)*100 : null;
      tr.children[0].textContent=sym; tr.children[1].textContent=q?fmt(q.last):"—";
      tr.children[2].textContent=pct==null?"—":(pct>0?"+":"")+pct.toFixed(2)+"%";
      tr.children[2].style.color=pct==null?"var(--mut)":pct>=0?"var(--grn)":"var(--red)";
      tr.children[3].textContent=!q?"NO DATA":q.stale?"STALE":"LIVE";
      tr.children[3].style.color=!q||q.stale?"var(--mut)":"var(--grn)";
    });
  };
  box.append(note,table); this.body.append(box);
  const off=Hub.sub("tickers","TIA_PULSE",render); this.unsubs.push(off);
};
Panel.prototype.build_tiasources = function(){
  const box=el("div"); box.style.cssText="padding:10px;overflow:auto;height:100%;font-size:12px";
  const intro=el("div","m","Connection health from this browser session; not a broker-account status."); intro.style.marginBottom="10px";
  const body=el("div"); box.append(intro,body); this.body.append(box);
  const draw=()=>{
    body.replaceChildren();
    const keys=Object.keys(Hub.subs||{}).filter(k=>Hub.subs[k]&&Hub.subs[k].size);
    if(!keys.length){body.textContent="No active feed subscriptions yet.";return;}
    keys.forEach(k=>{const line=el("div");line.style.cssText="display:flex;justify-content:space-between;gap:8px;padding:7px 2px;border-bottom:1px solid var(--line)";
      const left=el("span",null,k.replace("|"," · ")); const last=Hub.last[k];
      const right=el("span",null,last&& !last.error ? "ACTIVE" : "WAITING / ERROR"); right.style.color=last&&!last.error?"var(--grn)":"var(--mut)";
      line.append(left,right);body.append(line);
    });
  };
  draw(); this._tiaSourceTimer=setInterval(draw,2000); this.unsubs.push(()=>clearInterval(this._tiaSourceTimer));
};
''';
    doc = doc.replace("const WGROUPS = () => [", tia_panels + "\\nconst WGROUPS = () => [");
    doc = doc.replace('[Lg("Settings","الإعدادات"), "#9aa3ad", ["settings"]]', '[Lg("TIA Intelligence","استخبارات TIA"), "#d6ad62", ["tiapulse","tiasources"]], [Lg("Settings","الإعدادات"), "#9aa3ad", ["settings"]]');
    doc = doc.replace('settings:"SET", "@std"', 'settings:"SET", tiapulse:"PULSE", tiasources:"SRC", "@std"');
    # Isolate all localStorage/sessionStorage keys from the original Workspace.
    doc = doc.replace("ai_ws_v5", "tia_ws_v1")
    doc = doc.replace("<title>6868 X</title>", "<title>TIA Command Workspace</title>")
    doc = doc.replace(
        ":root{--panel0:#0e1114;--dot:#1b2027;--bg:#0b0e11;--panel:#161a1e;--panel2:#1e2329;--line:#2b3139;--txt:#eaecef;--mut:#848e9c;--grn:#0ecb81;--red:#f6465d;--gold:#f0b90b;--blue:#4aa3ff;--vio:#b57cff}",
        ":root{--panel0:#0d0c0a;--dot:#282117;--bg:#090a0c;--panel:#141311;--panel2:#201d18;--line:#51432c;--txt:#eee6d7;--mut:#a99d89;--grn:#31c48d;--red:#e66a67;--gold:#d6ad62;--blue:#78a9d1;--vio:#b59acb}"
    )
    components.html(doc, height=height, scrolling=False)
