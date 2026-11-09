/* XPIX Intelligence — unified market-reading workspace.
   Reuses the shared Hub. This first implementation is a linked analysis cockpit;
   it deliberately does not manufacture entry/stop/target levels from incomplete feeds. */
Panel.prototype.build_intel = function(){
  const P = this, S = this.state, ar = lang === "ar", L = (en, aa) => ar ? aa : en;
  S.sym = S.sym || SYMS[0]; S.tab = S.tab || "overview";
  P.ttl.textContent = L("XPIX Intelligence","XPIX Intelligence") + " · " + S.sym;
  const bar = el("div","tb"), symSel = P.symSelect(), tf = el("select"), tabs = el("div","seg");
  [["1m","1m"],["5m","5m"],["15m","15m"],["1H","1H"],["4H","4H"]].forEach(([v,l]) => tf.append(Object.assign(el("option"),{value:v,textContent:l})));
  tf.value = S.tf || "5m"; tf.onchange = () => { S.tf=tf.value; Ws.save(); render(); };
  const link = el("button",null,L("Link chart","ربط بالشارت")); link.title=L("Use this symbol on the chart","استخدم نفس الرمز على الشارت");
  link.onclick=()=>{ const c=Ws.panels.find(x=>x.type==="chart"); if(c) Ws.broadcast(c,S.sym); else { Ws.add("chart"); const n=Ws.panels[Ws.panels.length-1]; n.setSymbol(S.sym); } };
  bar.append(symSel,tf,link); P.body.append(bar,tabs);
  const content=el("div"); content.style.cssText="overflow:auto;min-height:0;flex:1;padding:8px";
  P.body.append(content); P.body.style.display="flex"; P.body.style.flexDirection="column";
  const definitions=[
    ["overview",L("Overview","نظرة عامة")],["flow",L("Order Flow","الأوردر فلو")],
    ["liquidity",L("Liquidity","السيولة")],["auction",L("Auction / Volume","المزاد والحجم")],
    ["setups",L("Setups","الفرص")],["indicators",L("Indicators","المؤشرات")]
  ];
  const open = type => { const p=Ws.panels.find(x=>x.type===type && x.state.sym===S.sym); if(p){p.front();return p;} Ws.add(type); const n=Ws.panels[Ws.panels.length-1]; if(n.setSymbol)n.setSymbol(S.sym); return n; };
  const enableFootprint = () => { let c=Ws.panels.find(x=>x.type==="chart" && x.state.sym===S.sym); if(!c){ Ws.add("chart"); c=Ws.panels[Ws.panels.length-1]; if(c.setSymbol)c.setSymbol(S.sym); } if(!c || !c.chart) return; c.state.tf=S.tf||c.state.tf||"5m"; c.state.fp=true; c.chart.fpOn=true; c.chart.draw(); Ws.save(); c.front(); if(c.resub)c.resub(); };
  const tile=(name,value,note)=>"<div style='padding:9px;border:1px solid #2b3139;border-radius:6px;min-width:0'><div class='m' style='font-size:10px'>"+name+"</div><b style='font-size:16px'>"+value+"</b><div class='m' style='font-size:10px'>"+note+"</div></div>";
  const render=()=>{
    P.ttl.textContent=L("XPIX Intelligence","XPIX Intelligence")+" · "+S.sym;
    tabs.innerHTML=""; definitions.forEach(([k,label])=>{const b=el("button",null,label);b.classList.toggle("on",S.tab===k);b.onclick=()=>{S.tab=k;Ws.save();render();};tabs.append(b);});
    const book=Hub.last["book|"+S.sym], tape=Hub.last["trades|"+S.sym], now=Date.now();
    const goodBook=book&&!book.error, goodTape=tape&&!tape.error;
    const age=x=>x&&(x.receivedAt||x.t)?Math.max(0,Math.round((now-(x.receivedAt||x.t))/1000))+"s "+L("since received","من وقت الاستلام"):L("timestamp unavailable","التوقيت غير متاح");
    const mid=goodBook&&book.bids?.length&&book.asks?.length?(book.bids[0].p+book.asks[0].p)/2:null;
    const buy=goodTape?(tape.rows||[]).filter(x=>x.side==="Buy").reduce((a,x)=>a+x.q,0):null;
    const sell=goodTape?(tape.rows||[]).filter(x=>x.side==="Sell").reduce((a,x)=>a+x.q,0):null;
    const delta=buy!=null&&sell!=null?buy-sell:null;
    const spread=goodBook&&book.bids?.length&&book.asks?.length?book.asks[0].p-book.bids[0].p:null;
    const spreadPct=spread!=null&&mid?spread/mid*100:null;
    const tapeStats=goodTape?tape.stats||{}:{};
    const bq=goodBook?(book.bids||[]).slice(0,10).reduce((a,x)=>a+x.q,0):null;
    const aq=goodBook?(book.asks||[]).slice(0,10).reduce((a,x)=>a+x.q,0):null;
    const fmt=x=>x==null?"—":fmtQ(x), status=(ok,x)=>ok?L("Receiving data","البيانات بتوصل"):(x&&x.capability==="unsupported"?L("Not supported by this feed","المصدر ده مش بيدعم البيانات دي"):L("Unavailable / error","غير متاح / فيه خطأ"));
    const explain={
      overview:L("This is the market evidence panel. Read source and freshness before trusting a value.","دي لوحة أدلة السوق. راجع المصدر وحداثة البيانات قبل ما تعتمد على أي رقم."),
      flow:L("Executed trades show aggressive buying/selling. Delta is buy volume minus sell volume; it is not a direction guarantee.","الصفقات المنفذة بتوضح الشراء والبيع العدواني. الدلتا = حجم الشراء ناقص البيع، ومش ضمان لاتجاه السعر."),
      liquidity:L("The visible book is resting liquidity, not executed volume. Orders can be cancelled; a wall alone is not a trade signal.","دفتر الأوامر سيولة معروضة ولسه ما اتنفذتش. الأوامر ممكن تتسحب؛ الحائط لوحده مش إشارة دخول."),
      auction:L("Auction / value analysis should be read with POC, VAH, VAL and session context from the chart's Volume Profile.","قراءة المزاد والقيمة تعتمد على POC وVAH وVAL وسياق الجلسة من Volume Profile."),
      setups:L("No automatic entry is issued here until the setup has validated trigger, invalidation, stop, target and data quality. WAIT is a valid decision.","مش هنصدر دخول تلقائي قبل التحقق من التريجر والإبطال والستوب والهدف وجودة البيانات. الانتظار قرار صحيح."),
      indicators:L("Add existing chart indicators here as context; they do not replace order-flow evidence or setup validation.","ضيف مؤشرات الشارت كسياق مساعد؛ لكنها مش بديل عن أدلة الأوردر فلو أو التحقق من السيت أب.")
    };
    let h="<div style='font-weight:700;margin-bottom:6px'>"+explain[S.tab]+"</div>";
    if(S.tab==="overview"){
      h+="<div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:6px'>"+
      tile(L("Mid price","السعر المتوسط"),mid==null?"—":fmtP(mid),L("Order book snapshot","لقطة دفتر الأوامر"))+
      tile(L("Tape delta","دلتا الصفقات"),fmt(delta),L("Buy volume − sell volume","حجم الشراء − البيع"))+
      tile(L("Top-10 bid size","حجم أفضل 10 طلبات"),fmt(bq),L("Resting bids","طلبات شراء معروضة"))+
      tile(L("Top-10 ask size","حجم أفضل 10 عروض"),fmt(aq),L("Resting asks","عروض بيع معروضة"))+"</div>";
      h+="<div style='margin-top:10px;padding:8px;border:1px solid #2b3139;border-radius:6px'><b>"+L("Data health","حالة البيانات")+"</b><div>"+L("Order book","دفتر الأوامر")+": "+status(goodBook,book)+" · "+age(book)+"</div><div>"+L("Time & Sales","الصفقات")+": "+status(goodTape,tape)+" · "+age(tape)+"</div><div class='m' style='font-size:10px'>"+L("Venue: OKX public feed when this symbol is an OKX instrument. This is not a consolidated/global order book.","المصدر: بيانات OKX العامة لو الرمز متاح عليها. ده مش دفتر أوامر موحد لكل السوق.")+"</div></div>";
      h+="<div style='display:flex;flex-wrap:wrap;gap:6px;margin-top:10px'>"+["ofm","dom","tape","limits","setup","risk"].map(k=>"<button data-open='"+k+"'>"+({ofm:"Heatmap / OFM",dom:"DOM",tape:"Time & Sales",limits:"Limit Tracker",setup:"Setup Card",risk:"Risk Manager"}[k])+"</button>").join("")+"</div>";
    } else if(S.tab==="flow"){
      h+="<div>"+tile(L("Aggressive buy volume","حجم شراء السوق"),fmt(buy),L("Trades in Hub snapshot","الصفقات في لقطة البيانات"))+tile(L("Aggressive sell volume","حجم بيع السوق"),fmt(sell),L("Trades in Hub snapshot","الصفقات في لقطة البيانات"))+tile(L("Net delta","صافي الدلتا"),fmt(delta),L("Positive = buy-led prints; negative = sell-led prints","الموجب شراء أكثر؛ السالب بيع أكثر"))+"</div><button data-enable-footprint>"+L("Enable Footprint on linked chart","فعّل Footprint على الشارت المرتبط")+"</button> <button data-open='tape'>"+L("Open full Time & Sales","افتح Time & Sales")+"</button>";
    } else if(S.tab==="liquidity"){
      const imb=bq!=null&&aq!=null&&bq+aq?(bq-aq)/(bq+aq)*100:null;
      const ladder=goodBook?Array.from({length:5},(_,i)=>"<tr><td style='color:#0ecb81'>"+(book.bids[i]?fmtQ(book.bids[i].q):"—")+"</td><td>"+(book.bids[i]?fmtP(book.bids[i].p):"—")+"</td><td>"+(book.asks[i]?fmtP(book.asks[i].p):"—")+"</td><td style='color:#f6465d'>"+(book.asks[i]?fmtQ(book.asks[i].q):"—")+"</td></tr>").join(""):"";
      h+="<div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:6px'>"+tile(L("Bid liquidity · top 10","سيولة الطلب · أفضل 10"),fmt(bq),L("Displayed size only","حجم معروض فقط"))+tile(L("Ask liquidity · top 10","سيولة العرض · أفضل 10"),fmt(aq),L("Displayed size only","حجم معروض فقط"))+tile(L("Book imbalance","اختلال الدفتر"),imb==null?"—":(imb>0?"+":"")+imb.toFixed(1)+"%",L("Top-10 displayed size; not a signal","حجم أفضل 10 مستويات معروضة؛ مش إشارة"))+"</div>";
      h+="<div style='margin-top:8px;overflow:auto'><table class='rdt'><tr><th>"+L("Bid size","حجم الطلب")+"</th><th>"+L("Bid price","سعر الطلب")+"</th><th>"+L("Ask price","سعر العرض")+"</th><th>"+L("Ask size","حجم العرض")+"</th></tr>"+ladder+"</table></div>";
      h+="<div class='m' style='font-size:10px;margin:5px 0'>"+(goodBook?L("Top 5 levels · OKX public venue snapshot","أفضل 5 مستويات · لقطة دفتر OKX العامة"):L("Order book unavailable or unsupported for this feed","دفتر الأوامر غير متاح أو غير مدعوم من المصدر"))+"</div><button data-open='ofm'>"+L("Open Liquidity Heatmap","افتح خريطة السيولة")+"</button> <button data-open='dom'>DOM</button> <button data-open='limits'>"+L("Limit Tracker","تتبع الأوامر")+"</button>";
    } else if(S.tab==="auction"){
      const vp=Ws.panels.find(x=>x.type==="valuelv"&&x.state.sym===S.sym), vd=vp&&vp.levelsData||{};
      const valueRows=Object.entries(vd).filter(([k,d])=>d&&d.vp).map(([k,d])=>"<tr><td>"+k+"</td><td>"+fmtP(d.vp.vah)+"</td><td>"+fmtP(d.vp.poc)+"</td><td>"+fmtP(d.vp.val)+"</td><td>"+(d.px>d.vp.vah?L("Above value","فوق القيمة"):d.px<d.vp.val?L("Below value","تحت القيمة"):L("Inside value","داخل القيمة"))+"</td></tr>").join("");
      h+="<div class='m' style='font-size:10px;margin-bottom:6px'>"+L("POC / VAH / VAL from the existing multi-timeframe Value Levels panel; values refresh with that panel.","POC / VAH / VAL من لوحة مستويات القيمة الحالية متعددة الفريمات؛ التحديث حسب اللوحة الأصلية.")+"</div>";
      h+="<div style='overflow:auto'><table class='rdt'><tr><th>TF</th><th>VAH</th><th>POC</th><th>VAL</th><th>"+L("Price vs value","السعر مقابل القيمة")+"</th></tr>"+(valueRows||"<tr><td colspan='5'>"+L("Open Value Levels to load this symbol's profile","افتح Value Levels لتحميل بروفايل الرمز")+"</td></tr>")+"</table></div>";
      h+="<button data-open='chart'>"+L("Open linked chart + Volume Profile","افتح الشارت المرتبط والـVolume Profile")+"</button> <button data-open='valuelv'>"+L("Open / refresh multi-timeframe value levels","افتح / حدّث مستويات القيمة")+"</button>";
    }
    else if(S.tab==="setups"){
      const chart=Ws.panels.find(x=>x.type==="chart"&&x.state.sym===S.sym), fpReady=!!(chart&&chart.chart&&chart.chart.fpOn), bookAge=book&&(book.receivedAt||book.t)?Math.max(0,Math.round((now-(book.receivedAt||book.t))/1000)):null, tapeAge=tape&&(tape.receivedAt||tape.t)?Math.max(0,Math.round((now-(tape.receivedAt||tape.t))/1000)):null;
      const packet=[ [L("Order book","دفتر الأوامر"),goodBook?L("Available","متاح"):L("Missing / unsupported","ناقص / غير مدعوم"),bookAge==null?"—":bookAge+"s"], [L("Time & Sales","الصفقات"),goodTape?L("Available","متاح"):L("Missing / unsupported","ناقص / غير مدعوم"),tapeAge==null?"—":tapeAge+"s"], [L("Footprint","الفوتبرنت"),fpReady?L("Enabled on linked chart","مفعّل على الشارت"):L("Not enabled","مش مفعّل"),"—"] ];
      h+="<div style='padding:10px;border:1px solid #d99b24;border-radius:6px'><b>"+L("WAIT — no ranked setup or trade plan is authorized yet","انتظار — مفيش ترتيب فرص أو خطة صفقة معتمدة لسه")+"</b><p class='m'>"+L("This is an evidence-readiness packet, not a BUY/SELL signal. A ranked setup requires a versioned rule, validated trigger, invalidation, stop, targets, expiry, risk and replay evidence. Missing or stale inputs block it.","دي بطاقة جاهزية أدلة، مش إشارة شراء أو بيع. ترتيب الفرص محتاج قاعدة بإصدار محدد وتريجر وإبطال وستوب وأهداف وصلاحية ومخاطرة وأدلة اختبار تاريخي. نقص البيانات أو قدمها يمنع التفعيل.")+"</p></div>";
      h+="<div style='overflow:auto'><table class='rdt'><tr><th>"+L("Evidence","الدليل")+"</th><th>"+L("Status","الحالة")+"</th><th>"+L("Age","العمر")+"</th></tr>"+packet.map(x=>"<tr><td>"+x[0]+"</td><td>"+x[1]+"</td><td>"+x[2]+"</td></tr>").join("")+"</table></div>";
      h+="<button data-open='setup'>"+L("Open existing Setup Card","افتح كارت الصفقات الحالي")+"</button>";
    }
    else {
      const chart=Ws.panels.find(x=>x.type==="chart"&&x.state.sym===S.sym), items=chart&&chart.indItems||[];
      const indRows=items.filter(it=>it&&it.label&&typeof it.get==="function").map(it=>"<tr><td>"+it.label+"</td><td>"+(it.get()?L("ON","مفعّل"):L("OFF","متوقف"))+"</td></tr>").join("");
      h+="<div class='m' style='font-size:10px;margin-bottom:6px'>"+L("Live status from the existing linked chart indicator registry. Settings and toggles remain owned by the chart.","حالة مباشرة من سجل مؤشرات الشارت المرتبط. الإعدادات والتفعيل يفضلوا تابعين للشارت الأصلي.")+"</div>";
      h+="<div style='overflow:auto'><table class='rdt'><tr><th>"+L("Indicator","المؤشر")+"</th><th>"+L("State","الحالة")+"</th></tr>"+(indRows||"<tr><td colspan='2'>"+L("Open the linked chart to load its indicator registry","افتح الشارت المرتبط لتحميل سجل المؤشرات")+"</td></tr>")+"</table></div>";
      h+="<button data-open='chart'>"+L("Open chart indicator settings","افتح إعدادات مؤشرات الشارت")+"</button>";
    }
    content.innerHTML=h;
    content.querySelectorAll("[data-open]").forEach(b=>b.onclick=()=>open(b.dataset.open));
    content.querySelectorAll("[data-enable-footprint]").forEach(b=>b.onclick=enableFootprint);
  };
  P.setSymbol = next => {S.sym=next;if(symSel.value!==next)symSel.value=next;P.setTitle();Ws.save();P.resub();};
  symSel.onchange=()=>{S.sym=symSel.value;P.setTitle();Ws.save();P.resub();};
  P.resub=()=>{P.clearSubs();P.unsubs.push(Hub.sub("book",S.sym,render),Hub.sub("trades",S.sym,render));render();};
  P.destroy=()=>P.clearSubs();
  P.resub(); render();
};
