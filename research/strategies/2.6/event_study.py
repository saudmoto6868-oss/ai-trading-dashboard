#!/usr/bin/env python3
"""Causal event-study harness for the Matimatiki 2.6 hypothesis.
Input CSV: datetime,open,high,low,close; optional volume. No network calls.
Pivots become usable only after right_bars have closed. This is an event
study, NOT a complete P&L backtest: creator SL/TP rules remain unverified.
"""
import argparse, csv, json
from dataclasses import dataclass, asdict
from pathlib import Path

RATIOS=(2.5,2.6,2.618,1/0.382,2.7)
HORIZONS=(5,10,20,40)

@dataclass
class Bar:
    dt:str; open:float; high:float; low:float; close:float; volume:float=0.0
@dataclass
class Pivot:
    idx:int; kind:str; price:float; known_at:int
@dataclass
class Event:
    ratio:float; side:str; anchor_start:str; anchor_end:str
    confirmation_time:str; entry_time:str; entry:float; leg_range:float
    bars_to_fill:int; mfe_leg:float; mae_leg:float; returns_leg:dict

def load_bars(path):
    rows=[]
    with open(path,newline="",encoding="utf-8-sig") as f:
        rd=csv.DictReader(f); req={"datetime","open","high","low","close"}
        if not req.issubset(set(rd.fieldnames or [])):
            raise ValueError("CSV requires datetime,open,high,low,close")
        for r in rd:
            b=Bar(str(r["datetime"]),float(r["open"]),float(r["high"]),
                  float(r["low"]),float(r["close"]),float(r.get("volume") or 0))
            if not (b.low<=min(b.open,b.close)<=max(b.open,b.close)<=b.high):
                raise ValueError("Invalid OHLC at "+b.dt)
            rows.append(b)
    if len(rows)<100: raise ValueError("At least 100 bars required")
    if any(rows[i].dt>=rows[i+1].dt for i in range(len(rows)-1)):
        raise ValueError("Rows must be chronological and unique")
    return rows

def confirmed_pivots(bars,left=3,right=3):
    out=[]
    for i in range(left,len(bars)-right):
        w=bars[i-left:i+right+1]; h=bars[i].high; lo=bars[i].low
        if h>=max(x.high for x in w) and sum(x.high==h for x in w)==1:
            out.append(Pivot(i,"H",h,i+right))
        if lo<=min(x.low for x in w) and sum(x.low==lo for x in w)==1:
            out.append(Pivot(i,"L",lo,i+right))
    out.sort(key=lambda p:(p.known_at,p.idx,p.kind))
    clean=[]
    for p in out:
        if not clean or p.kind!=clean[-1].kind: clean.append(p); continue
        prev=clean[-1]; better=p.price>prev.price if p.kind=="H" else p.price<prev.price
        if better: clean[-1]=p
    return clean

def make_legs(pivots):
    for a,b in zip(pivots,pivots[1:]):
        if a.kind=="L" and b.kind=="H": yield "BUY",a,b,b.price-a.price
        elif a.kind=="H" and b.kind=="L": yield "SELL",a,b,a.price-b.price

def run_event_study(bars,ratios=RATIOS,left=3,right=3,wait_bars=80,
                    horizon_bars=40,cost=0.0):
    pivots=confirmed_pivots(bars,left,right); events=[]
    for side,a,b,span in make_legs(pivots):
        if span<=0 or b.known_at>=len(bars)-1: continue
        known=b.known_at
        for ratio in ratios:
            entry=b.price-span/ratio if side=="BUY" else b.price+span/ratio
            stop=min(len(bars)-1,known+wait_bars); fill=None
            for j in range(known+1,stop+1):
                if bars[j].low<=entry<=bars[j].high: fill=j; break
            if fill is None or fill+horizon_bars>=len(bars): continue
            win=bars[fill+1:fill+horizon_bars+1]; sign=1 if side=="BUY" else -1
            mfe=max((x.high-entry)*sign for x in win)
            mae=min((x.low-entry)*sign for x in win)
            ret={str(h):round((bars[fill+h].close-entry)*sign-cost,8)
                 for h in HORIZONS if fill+h<len(bars)}
            events.append(Event(float(ratio),side,bars[a.idx].dt,bars[b.idx].dt,
                bars[known].dt,bars[fill].dt,entry,span,fill-known,mfe/span,mae/span,ret))
    return events,pivots

def summarize(events):
    out={}
    for ratio in sorted({e.ratio for e in events}):
        g=[e for e in events if e.ratio==ratio]; cut=int(len(g)*.7)
        for label,items in (("all",g),("in_sample",g[:cut]),("out_of_sample",g[cut:])):
            vals=[e.returns_leg["20"] for e in items if "20" in e.returns_leg]
            out.setdefault(str(ratio),{})[label]={
                "n_filled":len(items),"n_20bar":len(vals),
                "positive_20bar_pct":round(100*sum(v>0 for v in vals)/len(vals),2) if vals else None,
                "mean_20bar_leg_units":round(sum(vals)/len(vals)/items[0].leg_range,5) if vals else None,
                "median_mfe_leg":round(sorted(e.mfe_leg for e in items)[len(items)//2],5) if items else None,
                "median_mae_leg":round(sorted(e.mae_leg for e in items)[len(items)//2],5) if items else None,
                "mean_bars_to_fill":round(sum(e.bars_to_fill for e in items)/len(items),2) if items else None}
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("csv"); ap.add_argument("--left",type=int,default=3)
    ap.add_argument("--right",type=int,default=3); ap.add_argument("--wait-bars",type=int,default=80)
    ap.add_argument("--horizon-bars",type=int,default=40); ap.add_argument("--cost",type=float,default=0.0)
    ap.add_argument("--out",default="research/strategies/2.6/output")
    a=ap.parse_args()
    if min(a.left,a.right,a.wait_bars,a.horizon_bars)<1 or a.cost<0: ap.error("invalid parameters")
    bars=load_bars(a.csv); events,pivots=run_event_study(bars,left=a.left,right=a.right,
        wait_bars=a.wait_bars,horizon_bars=a.horizon_bars,cost=a.cost)
    out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
    fields=list(Event.__dataclass_fields__)
    with (out/"events.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for e in events: w.writerow(asdict(e))
    report={"bars":len(bars),"pivots":len(pivots),"events":len(events),
      "parameters":{"ratios":list(RATIOS),"left":a.left,"right":a.right,
      "wait_bars":a.wait_bars,"horizon_bars":a.horizon_bars,"cost_absolute_price":a.cost},
      "metrics":summarize(events),
      "limitations":["event study only; no verified stop/target or position sizing",
      "not a profitability claim","chronological event-tail split is provisional",
      "reserve a separate untouched final holdout before tuning"]}
    (out/"report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps({"bars":len(bars),"pivots":len(pivots),"events":len(events)},indent=2))
if __name__=="__main__": main()
