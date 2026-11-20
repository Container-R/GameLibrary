"use strict";
// Synthetic times share one elapsed-second coordinate. Build each stream by event time,
// clip each to supplied day endpoints, then union per account. This is not measured play.
const H=20,G=30,DAY=[0,86400],NEXT=[86400,172800];
function event(id,at,kind,device="A",epoch=1,arrival=at,order=0,account="player",eligible=true){
 return {id,at,kind,device,epoch,arrival,order,account,eligible};
}
const E=event;
const baseline=[
 E("a0",0,"resume"),E("a20",20,"beat"),E("a40",40,"beat"),E("a60",60,"stop"),
 E("a80bg",80,"beat","A",1,300),E("a180",180,"resume"),E("a200",200,"beat"),E("a220",220,"beat"),
 E("b190",190,"start","B"),E("b210",210,"beat","B"),E("b230",230,"beat","B"),
 E("a40",40,"beat","A",1,340),E("a50",50,"beat","A",1,400),E("b250",250,"beat","B",1,500)
];
const short=[E("s0",0,"start"),E("s10",10,"beat"),E("s12",12,"stop"),E("s20",20,"resume"),E("s25",25,"beat"),E("s27",27,"stop")];
const gap=[E("g10",10,"start"),E("g30",30,"beat"),E("g100",100,"beat"),E("g120",120,"beat"),E("g125",125,"stop")];
const cross=[E("d0",86380,"start"),E("d1",86400,"beat"),E("d2",86420,"beat"),E("d3",86430,"stop")];
const epochs=[E("p0",0,"start"),E("p10",10,"beat","A",1,45),E("p12",12,"stop"),
 E("q15",15,"beat","A",2),E("q20",20,"resume","A",2),E("q30",30,"beat","A",2)];
const exactThreshold=[E("t0",0,"start"),E("t30",30,"beat"),E("t61",61,"beat")];
function union(points){
 const ans=[];
 for(const [lo,hi] of points.slice().sort((a,b)=>a[0]-b[0]||a[1]-b[1])){
   if(lo>=hi)continue;
   const last=ans.at(-1);
   if(last&&lo<=last[1])last[1]=Math.max(last[1],hi);
   else ans.push([lo,hi]);
 }
 return ans;
}
const duration=xs=>xs.reduce((s,[a,b])=>s+b-a,0);
function estimate(events,arrivalCutoff,observeUntil,window,tail){
 const seen=new Map(),streams=new Map(),duplicate=[],ignored=[];
 for(const r of events.filter(x=>x.arrival<=arrivalCutoff&&x.at<=observeUntil).sort((a,b)=>a.arrival-b.arrival)){
  const {arrival,...payload}=r;
  if(r.at>arrival)throw Error("wrong fixture time");
  const id=JSON.stringify([r.account,r.id]), encoded=JSON.stringify(payload);
  if(seen.has(id)){
   if(seen.get(id)!==encoded)throw Error("conflicting event ID");
   duplicate.push(r.id);continue;
  }
  seen.set(id,encoded);
  const k=JSON.stringify([r.account,r.device,r.epoch]);
  if(!streams.has(k))streams.set(k,[]);
  streams.get(k).push(r);
 }
 const streamsClipped={},accounts=new Map();
 for(const [k,rows] of streams){
  const out=[];
  let front=false,start=null,last=null,previous=null;
  function end(bound,stop=false){
   if(start!==null){
    // Fully close a short interval only when an explicit stop is present.
    const endAt=stop&&bound-last<=G?bound:last+(tail?H:0);
    out.push([start,Math.min(endAt,bound,observeUntil)]);
   }
   start=last=null;
  }
  rows.sort((a,b)=>a.at-b.at||a.order-b.order);
  for(const r of rows){
   if(previous&&previous.at===r.at&&previous.order===r.order)throw Error("ambiguous order");
   previous=r;
   if(r.kind==="stop"||r.kind==="retire"){end(r.at,r.kind==="stop");front=false;continue;}
   if(r.kind==="start"||r.kind==="resume"){end(r.at);front=true;}
   else if(r.kind!=="beat")throw Error("bad kind");
   if(!front||!r.eligible){ignored.push(r.id);continue;}
   if(last!==null&&r.at-last>G)end(r.at);
   if(start===null)start=r.at;
   last=r.at;
  }
  end(Infinity);
  const clipped=union(out.map(([a,b])=>[Math.max(a,window[0]),Math.min(b,window[1])]));
  streamsClipped[k]=clipped;
  const {account:id,device}=rows[0];
  if(!accounts.has(id))accounts.set(id,new Map());
  const byDevice=accounts.get(id);
  byDevice.set(device,(byDevice.get(device)||[]).concat(clipped));
 }
 const account={};
 const physicalDevices={};
 for(const [k,byDevice] of accounts){
  const mergedDevices=Array.from(byDevice,([id,intervals])=>[id,union(intervals)]);
  for(const [id,intervals] of mergedDevices)physicalDevices[JSON.stringify([k,id])]=intervals;
  const x=mergedDevices.flatMap(([,intervals])=>intervals);
  const windows=union(x);
  account[k]={windows,seconds:duration(windows),device_seconds_sum:duration(x)};
 }
 return {arrivalCutoff,observeUntil,account,streamsClipped,physicalDevices,duplicate,ignored};
}
const horizon=[E("h90",90,"resume")];
const longStop=[E("l10",10,"start"),E("l30",30,"beat"),E("l100",100,"stop")];
const explicitReplacement=[E("v0",0,"start"),E("v10",10,"beat"),E("v12",12,"retire","A",1,40),
 E("w12",12,"start","A",2),E("w18",18,"beat","A",2),E("v15",15,"beat","A",1,50)];
const overlappingEpochs=[E("o0",0,"start"),E("o20",20,"beat"),
 E("n15",15,"start","A",2),E("n35",35,"beat","A",2),E("n40",40,"stop","A",2)];
const separateCutoff=[E("c10",10,"start"),E("c30",30,"beat","A",1,50),E("c50",50,"beat","A",1,55)];
const lateStop=[E("z0",0,"start"),E("z20",20,"beat"),E("z25",25,"stop","A",1,100)];
const both=(events,arrivalCutoff,window=DAY,observeUntil=arrivalCutoff)=>({
 no_tail:estimate(events,arrivalCutoff,observeUntil,window,false),
 tail20:estimate(events,arrivalCutoff,observeUntil,window,true)});
const cases={baseline:both(baseline,350),late_a50:both(baseline,450),late_b250:both(baseline,550),
 short_background:both(short,200),long_gap:both(gap,200),
 cross_day_before:both(cross,87000),cross_day_after:both(cross,87000,NEXT),
 process_epoch:both(epochs,200),inclusive_threshold:both(exactThreshold,200),
 cutoff_tail_clamp:both(horizon,100),long_stop:both(longStop,200),explicit_replacement:both(explicitReplacement,200),
 overlapping_epochs_same_device:both(overlappingEpochs,100),
 independent_cutoff:both(separateCutoff,60,DAY,40),
 future_observation_horizon:both(separateCutoff,45,DAY,70),
 before_late_stop:both(lateStop,60,DAY,60),after_late_stop:both(lateStop,120,DAY,60)};
const seconds=p=>Object.values(p).map(x=>x.account.player.seconds);
const want=[[110,130],[110,130],[130,150],[19,19],[45,65],[20,20],[30,30],[22,42],[30,70],[0,10],[20,40],[16,38],[40,40],[20,30],[0,20],[20,40],[25,25]];
if(JSON.stringify(Object.values(cases).map(seconds))!==JSON.stringify(want))throw Error(JSON.stringify(Object.values(cases).map(seconds)));
if(cases.baseline.no_tail.account.player.device_seconds_sum!==140||
 cases.baseline.tail20.account.player.device_seconds_sum!==180)throw Error("device overlap");
if(cases.baseline.tail20.duplicate[0]!=="a40"||!cases.baseline.tail20.ignored.includes("a80bg")||
 !cases.process_epoch.tail20.ignored.includes("q15"))throw Error("qualification");
for(const p of Object.values(cases.overlapping_epochs_same_device)){
 if(p.account.player.device_seconds_sum!==40||Object.keys(p.physicalDevices).length!==1||
    Object.keys(p.streamsClipped).length!==2)throw Error("one device, two overlapping epochs");
}
const reversed=both(baseline.slice().reverse(),550);
if(JSON.stringify(seconds(reversed))!==JSON.stringify(seconds(cases.late_b250)))throw Error("arrival shuffle");
let conflict_rejected=false;
try{both(short.concat(E("s10",11,"beat","A",1,31)),200);}
catch(err){conflict_rejected=err.message==="conflicting event ID";}
if(!conflict_rejected)throw Error("conflicting ID accepted");
console.log(JSON.stringify({scope:"synthetic estimator, not exact activity/attention or validated uncertainty bound",
 H,G,fixtures:{baseline,short,gap,cross,epochs,exactThreshold,horizon,longStop,explicitReplacement,overlappingEpochs,separateCutoff,lateStop},cases,conflict_rejected}));
