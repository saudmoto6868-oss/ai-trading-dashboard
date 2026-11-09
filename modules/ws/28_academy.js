/* Academy Intelligence widget — read-only view of the shared server snapshot.
   Source content is rendered as text; external references open in a new tab. */
Panel.prototype.build_academy = function(){
  const rows = Array.isArray(CFG.academy) ? CFG.academy : [];
  const wrap = el("div"); wrap.style.cssText = "height:100%;overflow:auto;padding:8px;display:flex;flex-direction:column;gap:8px";
  const bar = el("div","tb"), search = el("input"), status = el("select"), count = el("span","m");
  search.type = "search"; search.placeholder = Lg("Search knowledge, school, topic…","ابحث في المعرفة أو المدرسة أو الموضوع…"); search.style.cssText = "min-width:120px;flex:1";
  [["",Lg("All states","كل الحالات")],["inbox",Lg("Inbox","الوارد")],["review",Lg("In review","قيد المراجعة")],["accepted",Lg("Accepted","مقبول")],["rejected",Lg("Rejected","مرفوض")]].forEach(([v,t]) => status.append(Object.assign(el("option"),{value:v,textContent:t})));
  bar.append(search,status,count); wrap.append(bar); const list = el("div"); list.style.cssText = "display:flex;flex-direction:column;gap:7px"; wrap.append(list); this.body.append(wrap);
  const safeLink = u => typeof u === "string" && /^https?:\/\//i.test(u);
  const render = () => {
    const q = search.value.trim().toLowerCase(), st = status.value;
    const found = rows.filter(r => (!st || r.status === st) && (!q || [r.title,r.summary,r.topic,r.school,r.asset,r.timeframe,r.claim_type].join(" ").toLowerCase().includes(q)));
    count.textContent = found.length+" / "+rows.length;
    list.innerHTML = "";
    if (!rows.length){ const empty=el("div","m",Lg("No indexed Academy records yet. Add research through the intake pipeline.","لا توجد سجلات مفهرسة بعد. أضف الأبحاث من مسار الاستقبال.")); empty.style.padding="12px"; list.append(empty); return; }
    if (!found.length){ const empty=el("div","m",Lg("No records match this filter.","لا توجد نتائج مطابقة.")); empty.style.padding="12px"; list.append(empty); return; }
    found.forEach(r => {
      const card=el("article"); card.style.cssText="border:1px solid var(--line);border-radius:7px;padding:9px;background:var(--panel2);display:flex;flex-direction:column;gap:5px";
      const head=el("div"); head.style.cssText="display:flex;align-items:flex-start;gap:8px;flex-wrap:wrap";
      const title=el("b",null,r.title || "Untitled"); title.style.cssText="flex:1;min-width:150px;font-size:13px"; head.append(title);
      const tag=el("span","m",String(r.status||"inbox")+" · "+String(r.evidence_grade||"unreviewed")); tag.style.cssText="font-size:10px;border:1px solid var(--line);border-radius:10px;padding:2px 6px"; head.append(tag); card.append(head);
      const meta=el("div","m", [r.topic,r.school,r.asset,r.timeframe].filter(Boolean).join(" · ")); card.append(meta);
      const summary=el("div",null,r.summary||""); summary.style.cssText="white-space:pre-wrap;line-height:1.5"; card.append(summary);
      const claims=el("div","m",Lg("Claim: ","نوع الادعاء: ")+(r.claim_type||"interpretation")); card.append(claims);
      (r.caveats||[]).slice(0,3).forEach(c => { const caveat=el("div","m","⚠ "+c); caveat.style.cssText="white-space:pre-wrap;color:var(--mut)"; card.append(caveat); });
      const refs=[...(r.source_url?[r.source_url]:[]),...(r.references||[])].filter((u,i,a)=>safeLink(u)&&a.indexOf(u)===i).slice(0,4);
      if(refs.length){const links=el("div"); links.style.cssText="display:flex;gap:8px;flex-wrap:wrap"; refs.forEach((u,i)=>{const a=el("a",null,Lg("Source "+(i+1),"المصدر "+(i+1)));a.href=u;a.target="_blank";a.rel="noopener noreferrer";a.style.color="var(--blue)";links.append(a);});card.append(links);}
      list.append(card);
    });
  };
  search.oninput=render; status.onchange=render; render();
};
