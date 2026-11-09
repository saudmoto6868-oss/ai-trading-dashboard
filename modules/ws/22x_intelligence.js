/* XPIX Intelligence — unified market-reading workspace.
   Reuses the shared Hub. This first implementation is a linked analysis cockpit;
   it deliberately does not manufacture entry/stop/target levels from incomplete feeds. */
Panel.prototype.build_intel = function(){
  const P = this, S = this.state, ar = lang === "ar", L = (en, aa) => ar ? aa : en;
  S.sym = S.sym || SYMS[0]; S.tab = S.tab || "overview";
  P.ttl.textContent = L("XPIX Intelligence","XPIX Intelligence") + " · " + S.sym;
  const bar = el("div","tb"), sym = P.symSelect(), tf = el("select"), tabs = el("div","seg");
  [["1m","1m"],["5m","5m"],["15m","15m"],["1H","1H"],["4H","4H"]].forEach(([v,l]) => tf.append(Object.assign(el("option"),{value:v,textContent:l})));
  tf.value = S.tf || "5m"; tf.onchange = () => { S.tf=tf.value; Ws.save(); render(); };
  const link = el("button",null,L("Link chart","ربط بالشارت")); link.title=L("Use this symbol on the chart","استخدم نفس الرمز على الشارت");
  link.onclick=()=>{ const c=Ws.panels.find(x=>x.type==="chart"); if(c) Ws.broadcast(c,S.sym); else { Ws.add("chart"); const n=Ws.panels[Ws.panels.length-1]; n.setSymbol(S.sym); } };
  bar.append(sym,tf,link); P.body.append(bar,tabs);
  const content=el("div"); content.style.cssText="overflow:auto;min-height:0;flex:1;padding:8px";
  P.body.append(content); P.body.style.display="flex"; P.body.style.flexDirection="column";
  const definitions=[
    ["overview",L("Overview","نظرة عامة")],["flow",L("Order Flow","الأوردر فلو")],
    ["liquidity",L("Liquidity","السيولة")],["auction",L("Auction / Volume","المزاد والحجم")],
    ["setups",L("Setups","الفرص")],["indicators",L("Indicators","المؤشرات")]
  ];
  const open = type => { const p=Ws.panels.find(x=>x.type===type && x.state.sym===S.sym); if(p){p.front();return;} Ws.add(type); const n=Ws.panels[Ws.panels.length-1]; if(n.setSymbol)n.setSymbol(S.sym); };
  const tile=(name,value,note)=>"<div style='padding:9px;border:1px solid #2b3139;border-radius:6px;min-width:0'><div class='m' style='font-size:10px'>"+name+"</div><b style='font-size:16px'>"+value+"</b><div class='m' style='font-size:10px'>"+note+"</div></div>";
  const render=()=>{
    P.ttl.textContent=L("XPIX Intelligence","XPIX Intelligence")+" · "+S.sym;
    tabs.innerHTML=""; definitions.forEach(([k,label])=>{const b=el("button",null,label);b.classList.toggle("on",S.tab===k);b.onclick=()=>{S.tab=k;Ws.save();render();};tabs.append(b);});
    const book=Hub.last["book|"+S.sym], tape=Hub.last["trades|"+S.sym], now=Date.now();
    const goodBook=book&&!book.error, goodTape=tape&&!tape.error;
    const age=x=>x&&x.t?Math.max(0,Math.round((now-x.t)/1000))+"s":L("timestamp unavailable","التوقيت غير متاح");
    const mid=goodBook&&book.bids?.length&&book.asks?.length?(book.bids[0].p+book.asks[0].p)/2:null;
    const buy=goodTape?(tape.rows||[]).filter(x=>x.side==="Buy").reduce((a,x)=>a+x.q,0):null;
    const sell=goodTape?(tape.rows||[]).filter(x=>x.side==="Sell").reduce((a,x)=>a+x.q,0):null;
    const delta=buy!=null&&sell!=null?buy-sell:null;
    const bq=goodBook?(book.bids||[]).slice(0,10).reduce((a,x)=>a+x.q,0):null;
    const aq=goodBook?(book.asks||[]).slice(0,10).reduce((a,x)=>a+x.q,0):null;
    const fmt=x=>x==null?"—":fmtQ(x), status=(ok)=>ok?L("Receiving data","البيانات بتوصل"):L("Unavailable / error","غير متاح / فيه خطأ");
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
      h+="<div style='margin-top:10px;padding:8px;border:1px solid #2b3139;border-radius:6px'><b>"+L("Data health","حالة البيانات")+"</b><div>"+L("Order book","دفتر الأوامر")+": "+status(goodBook)+" · "+age(book)+"</div><div>"+L("Time & Sales","الصفقات")+": "+status(goodTape)+" · "+age(tape)+"</div><div class='m' style='font-size:10px'>"+L("Venue: OKX public feed when this symbol is an OKX instrument. This is not a consolidated/global order book.","المصدر: بيانات OKX العامة لو الرمز متاح عليها. ده مش دفتر أوامر موحد لكل السوق.")+"</div></div>";
      h+="<div style='display:flex;flex-wrap:wrap;gap:6px;margin-top:10px'>"+["ofm","dom","tape","limits","setup","risk"].map(k=>"<button data-open='"+k+"'>"+({ofm:"Heatmap / OFM",dom:"DOM",tape:"Time & Sales",limits:"Limit Tracker",setup:"Setup Card",risk:"Risk Manager"}[k])+"</button>").join("")+"</div>";
    } else if(S.tab==="flow"){
      h+="<div>"+tile(L("Aggressive buy volume","حجم شراء السوق"),fmt(buy),L("Trades in Hub snapshot","الصفقات في لقطة البيانات"))+tile(L("Aggressive sell volume","حجم بيع السوق"),fmt(sell),L("Trades in Hub snapshot","الصفقات في لقطة البيانات"))+tile(L("Net delta","صافي الدلتا"),fmt(delta),L("Positive = buy-led prints; negative = sell-led prints","الموجب شراء أكثر؛ السالب بيع أكثر"))+"</div><button data-open='tape'>"+L("Open full Time & Sales","افتح Time & Sales")+"</button>";
    } else if(S.tab==="liquidity"){
      h+="<div>"+tile(L("Bid liquidity · top 10","سيولة الطلب · أفضل 10"),fmt(bq),L("Displayed size only","حجم معروض فقط"))+tile(L("Ask liquidity · top 10","سيولة العرض · أفضل 10"),fmt(aq),L("Displayed size only","حجم معروض فقط"))+"</div><button data-open='ofm'>"+L("Open Liquidity Heatmap","افتح خريطة السيولة")+"</button> <button data-open='dom'>DOM</button> <button data-open='limits'>"+L("Limit Tracker","تتبع الأوامر")+"</button>";
    } else if(S.tab==="auction"){h+="<button data-open='chart'>"+L("Open linked chart + Volume Profile","افتح الشارت المرتبط والـVolume Profile")+"</button> <button data-open='valuelv'>"+L("Multi-timeframe value levels","مستويات القيمة على فريمات متعددة")+"</button>";}
    else if(S.tab==="setups"){h+="<div style='padding:10px;border:1px solid #d99b24;border-radius:6px'><b>"+L("WAIT — no verified trade plan from this panel yet","انتظار — مفيش خطة صفقة متحققة من اللوحة دي لسه")+"</b><p class='m'>"+L("A setup must state its evidence, trigger, invalidation, stop, targets, expiry and risk. Missing or stale data blocks the alert.","أي سيت أب لازم يوضح الأدلة والتريجر والإبطال والستوب والأهداف والصلاحية والمخاطرة. البيانات الناقصة أو القديمة توقف التنبيه.")+"</p></div><button data-open='setup'>"+L("Open existing Setup Card","افتح كارت الصفقات الحالي")+"</button>";}
    else {h+="<button data-open='chart'>"+L("Open chart indicators","افتح مؤشرات الشارت")+"</button><div class='m' style='margin-top:8px'>"+L("Indicator selection will be expanded after the chart indicator registry and saved settings are mapped into this panel.","هنوسع اختيار المؤشرات بعد ربط سجل مؤشرات الشارت وإعداداتها المحفوظة بالويدجت.")+"</div>";}
    content.innerHTML=h;
    content.querySelectorAll("[data-open]").forEach(b=>b.onclick=()=>open(b.dataset.open));
  };
  P.setSymbol = sym => {S.sym=sym;P.setTitle();sym.value=sym;Ws.save();render();};
  const oldSelect=sym.onchange; sym.onchange=()=>{S.sym=sym.value;P.setTitle();Ws.save();render();};
  P.resub=()=>{P.clearSubs();P.unsubs.push(Hub.sub("book",S.sym,render),Hub.sub("trades",S.sym,render));render();};
  P.destroy=()=>P.clearSubs();
  P.resub(); render();
};
