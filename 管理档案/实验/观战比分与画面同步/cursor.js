const run=()=>{
"use strict";
const events=new Map(), log=[];
const checkpoint={key:[100,0],score:{R:1,B:1}};
const cmp=(a,b)=>a[0]-b[0]||a[1]-b[1];
let cursor=[110,9], seek=0, pending=false;
const receive=(e)=>{if(e.match==="A"&&!events.has(e.id))events.set(e.id,e)};
const scoreAt=(t)=>{
  const score={...checkpoint.score};
  for(const e of events.values())if(cmp(e.key,checkpoint.key)>0&&cmp(e.key,t)<=0)score[e.side]++;
  return score;
};
const capture=(step,toasts=[])=>log.push([step,cursor[0],...Object.values(scoreAt(cursor)),toasts]);
const ask=()=>{pending=true;return ++seek};
function present(tag,t,step){
  if(tag!==seek)return capture(step);
  const toasts=pending?[]:[...events.values()].filter(e=>cmp(e.key,cursor)>0&&cmp(e.key,t)<=0)
    .sort((a,b)=>cmp(a.key,b.key)).map(e=>e.id);
  cursor=t;pending=false;capture(step,toasts);
}
const red={match:"A",id:"red2",key:[120,1],side:"R"};
const blue={match:"A",id:"blue2",key:[140,1],side:"B"};
receive(red); receive(blue); receive(red);
receive({match:"A",id:"already-in-snapshot",key:[100,0],side:"B"});
receive({match:"other",id:"not-our-match",key:[101,1],side:"B"});
receive({match:"A",id:"same-tick-after-snapshot",key:[100,1],side:"R"});
capture("arrived but not presented");
const old=ask(),next=ask();
capture("requests do not change display");
present(next,[115,9],"latest seek landed");
present(old,[150,9],"old completion ignored");
present(next,[125,9],"normal playback crosses red2");
receive({match:"A",id:"lateSameTick",key:[120,2],side:"B"});
capture("late committed event repairs state without toast");
present(next,[125,9],"paused");
present(next,[145,9],"normal playback crosses blue2");
const pass=ask();present(pass,[110,9],"explicit rewind clears future score");
present(pass,[125,9],"intentional replay crosses both");
const expected=[
 ["arrived but not presented",110,1,1,[]],["requests do not change display",110,1,1,[]],
 ["latest seek landed",115,1,1,[]],["old completion ignored",115,1,1,[]],
 ["normal playback crosses red2",125,2,1,["red2"]],
 ["late committed event repairs state without toast",125,2,2,[]],["paused",125,2,2,[]],
 ["normal playback crosses blue2",145,2,3,["blue2"]],
 ["explicit rewind clears future score",110,1,1,[]],
 ["intentional replay crosses both",125,2,2,["red2","lateSameTick"]]
];
for(const row of expected)row[2]++;
if(JSON.stringify(log)!==JSON.stringify(expected))throw Error(JSON.stringify(log));
return log;
};
console.log(JSON.stringify(run()));
