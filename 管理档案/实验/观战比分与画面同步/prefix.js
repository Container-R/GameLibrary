"use strict";
// Synthetic batches carry all scoring events for (start, through].
const base={tick:100,score:[1,1]};
const a={match:"A",start:100,through:130,events:[[120,"R2",0]]};
const b={match:"A",start:130,through:150,events:[[140,"B2",1]]};
let batches=new Map();
function ingest(batch){if(batch.match==="A"&&!batches.has(batch.start))batches.set(batch.start,batch);}
function prefix(){
  let through=base.tick, selected=[];
  while(batches.has(through)){
    const batch=batches.get(through);
    if(batch.through<=through)throw Error("bad range");
    selected.push(...batch.events); through=batch.through;
  }
  return {through,selected};
}
function stateAt(frame,mayProvisional){
  if(frame<base.tick)throw Error("no suitable snapshot");
  const {through,selected}=prefix();
  if(frame>through&&!mayProvisional)return {completeThrough:through,status:"wait"};
  const events=frame<=through?selected:[...batches.values()].flatMap(x=>x.events);
  const score=base.score.slice(),seen=new Set();
  for(const [tick,id,side] of events){
    if(tick>base.tick&&tick<=frame&&!seen.has(id)){ seen.add(id); score[side]++; }
  }
  return {completeThrough:through,status:frame<=through?"exact":"provisional",score};
}
const obs=[];function record(step,t){obs.push({step,frame:t,strict:stateAt(t,false),provisional:stateAt(t,true)});}
ingest(b);ingest(b);ingest({...a,match:"B"});
record("later batch, earlier interval missing",145);
ingest(a);record("gap repaired while frame is paused",145);
record("ready after seek into buffered history",125);
record("no events arrived after 150 does not prove completeness",151);
ingest({match:"A",start:150,through:170,events:[]});
record("authoritative empty batch covers the quiet interval",151);
const want=[
  [100,"wait","provisional",[1,2]],
  [150,"exact","exact",[2,2]],
  [150,"exact","exact",[2,1]],
  [150,"wait","provisional",[2,2]],
  [170,"exact","exact",[2,2]]
];
const got=obs.map(x=>[x.strict.completeThrough,x.strict.status,x.provisional.status,x.provisional.score]);
if(JSON.stringify(got)!==JSON.stringify(want))throw Error(JSON.stringify(obs));
console.log(JSON.stringify(obs,null,2));
