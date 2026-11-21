"use strict";
// A-first only. This app fixture consumes a complete monotonic-time batch;
// it does not simulate late OS events, rollback, native input or accessibility testing.
const W=80;
const edge=(id,t,key,kind="down",device="pad1",epoch=1,seq=0,player="P1")=>
 ({id,t,seq,key,kind,device,epoch,player});
const switchAt=(id,t,seq=0)=>({id,t,seq,kind:"switch"});
const X=edge;
const cases={
 timeout:[X("a",0,"A")],
 before:[X("a",0,"A"),X("b",79,"B")],
 exact:[X("a",0,"A"),X("b",80,"B")],
 late:[X("a",0,"A"),X("b",81,"B")],
 release_then_b:[X("a",0,"A"),X("u",30,"A","up"),X("b",40,"B")],
 same_tick_release_before_b:[X("a",0,"A"),X("u",80,"A","up"),X("b",80,"B","down","pad1",1,1)],
 same_tick_b_before_release:[X("a",0,"A"),X("b",80,"B"),X("u",80,"A","up","pad1",1,1)],
 already_held_b:[X("held",0,"B"),X("a",10,"A"),X("b-repeat",40,"B","repeat")],
 first_a_repeat_and_retry:[X("a",0,"A"),X("r",20,"A","repeat"),X("second-down",40,"A"),X("a",0,"A")],
 context_cancels:[X("old",0,"A"),switchAt("switch",80),
   X("stale",81,"B","down","pad1",1),X("held-repeat",82,"A","repeat","pad1",2),
   X("held-down",83,"A","down","pad1",2),X("up-new",84,"A","up","pad1",2),
   X("new",90,"A","down","pad1",2),X("b-new",105,"B","down","pad1",2)],
 same_player_other_device:[X("a",0,"A"),X("other",20,"B","down","pad2")],
 other_player_same_device:[X("a",0,"A"),X("other",20,"B","down","pad1",1,0,"P2")],
 kept_held_after_chord:[X("a",0,"A"),X("b",20,"B"),X("br",21,"B","repeat"),
   X("bu",22,"B","up"),X("bd",23,"B"),X("au",24,"A","up"),X("an",25,"A")],
};
const act=(at,kind,attempt,device="pad1")=>({at,kind,attempt,device});
const expected={
 timeout:[act(80,"A","a")],before:[act(79,"A+B","a")],exact:[act(80,"A+B","a")],
 late:[act(80,"A","a")],release_then_b:[act(30,"A","a")],
 same_tick_release_before_b:[act(80,"A","a")],same_tick_b_before_release:[act(80,"A+B","a")],
 already_held_b:[act(90,"A","a")],first_a_repeat_and_retry:[act(80,"A","a")],
 context_cancels:[act(105,"A+B","new")],same_player_other_device:[act(80,"A","a")],
 other_player_same_device:[act(80,"A","a")],kept_held_after_chord:[act(20,"A+B","a"),act(105,"A","an")]
};
function run(events,horizon=250){
 const seen=new Map(),ordered=[],duplicates=[],ignored=[],canceled=[],actions=[];
 const pending=new Map(),held=new Map(),committed=new Set();
 let epoch=1;
 for(const e of events){
  const payload=JSON.stringify(e);
  if(seen.has(e.id)){
   if(seen.get(e.id)!==payload)throw Error("conflicting event identity");
   duplicates.push(e.id);continue;
  }
  seen.set(e.id,payload);ordered.push(e);
 }
 ordered.sort((a,b)=>a.t-b.t||a.seq-b.seq);
 function emit(channel,t,kind){
  const p=pending.get(channel);
  if(!p||committed.has(p.id))throw Error("duplicate commit or missing attempt");
  committed.add(p.id);pending.delete(channel);actions.push(act(t,kind,p.id,p.device));
 }
 function expire(t,inclusive){
  const due=[...pending.entries()].filter(([,p])=>p.deadline<t||(inclusive&&p.deadline===t));
  due.sort((a,b)=>a[1].deadline-b[1].deadline);
  for(const [k,v] of due)emit(k,v.deadline,"A"); // logical cutoff, not callback wall-clock measurement
 }
 function apply(e){
  if(e.kind==="switch"){
   ++epoch;
   for(const p of pending.values())canceled.push(p.id);
   pending.clear();
   return; // held physical edges remain held, but don't enter the new context as fresh presses
  }
  if(e.epoch!==epoch){ignored.push([e.id,"stale_context"]);return;}
  const k=JSON.stringify([e.player,e.device]);
  if(!held.has(k))held.set(k,new Set());
  const keys=held.get(k);
  if(e.kind==="repeat"){ignored.push([e.id,"repeat"]);return;}
  if(e.kind==="up"){
   keys.delete(e.key);
   if(e.key==="A"&&pending.has(k))emit(k,e.t,"A");
   return;
  }
  if(e.kind!=="down")throw Error("unknown event");
  if(keys.has(e.key)){ignored.push([e.id,"already_held"]);return;}
  keys.add(e.key);
  if(e.key==="A"){
   pending.set(k,{id:e.id,device:e.device,deadline:e.t+W});
  }else if(e.key==="B"&&keys.has("A")&&pending.has(k)){
   emit(k,e.t,"A+B");
  }
 }
 let i=0;
 while(i<ordered.length){
  const t=ordered[i].t;
  if(!Number.isInteger(t)||t<0||t>horizon)throw Error("outside timeline");
  expire(t,false);
  let lastSeq=-1;
  for(;i<ordered.length&&ordered[i].t===t;i++){
   const e=ordered[i];
   if(!Number.isInteger(e.seq)||e.seq<=lastSeq)throw Error("ambiguous tick order");
   lastSeq=e.seq;apply(e);
  }
  expire(t,true);
 }
 expire(horizon,true);
 return {actions,duplicates,ignored,canceled};
}
const observed=Object.fromEntries(Object.entries(cases).map(([k,v])=>[k,run(v)]));
for(const [name,want] of Object.entries(expected))
 if(JSON.stringify(observed[name].actions)!==JSON.stringify(want))throw Error(name+JSON.stringify(observed[name]));
const c=observed.context_cancels;
if(JSON.stringify(c.canceled)!=='["old"]'||JSON.stringify(c.ignored)!==
 '[["stale","stale_context"],["held-repeat","repeat"],["held-down","already_held"]]')throw Error("context");
const r=observed.first_a_repeat_and_retry;
if(JSON.stringify(r.duplicates)!=='["a"]'||JSON.stringify(r.ignored)!==
 '[["r","repeat"],["second-down","already_held"]]')throw Error("retries");
if(JSON.stringify(run(cases.exact.slice().reverse()).actions)!==JSON.stringify(expected.exact))throw Error("input order");
// ID re-use with conflicting payload and ambiguous order must not silently pick a winner.
let rejected=0;
for(const invalid of [[X("same",0,"A"),X("same",1,"B")],[X("a",0,"A"),X("b",0,"B")]]){
 try{run(invalid);}catch(e){if(!/conflicting|ambiguous/.test(e.message))throw e;++rejected;}
}
if(rejected!==2)throw Error("invalid accepted");
console.log(JSON.stringify({scope:"Synthetic app arbitration only, no engine/OS/human measurement",window_ms:W,
 cases,observed,invalid_inputs_rejected:rejected}));
