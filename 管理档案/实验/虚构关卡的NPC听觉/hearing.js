"use strict";
const assert = require("node:assert/strict");
const listen = {A:[-4,0],B:[4,0]};
const source = {tag:"prop_impact", eventId:"rattle/17", tick:100, position:[0,0], room:"workshop"};
const edges = [
  ["S","Left opening",4,0,"always"],["Left opening","A",4,0,"always"],
  ["S","B door",2,0,"open"],["B door","B",2,0,"open"],
  ["S","Hall mouth",9,0,"hall"],["Hall mouth","B hall exit",6,2,"hall"],["B hall exit","B",3,0,"hall"],
  ["S","Vent mouth",4,4,"vent"],["Vent mouth","B grate",2,4,"vent"],["B grate","B",1,0,"vent"],
];
const scenarios = [
  {revision:1,open:false,vent:false,hall:true,budget:10},
  {revision:2,open:true,vent:false,hall:true,budget:10},
  {revision:3,open:false,vent:false,hall:true,budget:20},
  {revision:4,open:false,vent:true,hall:true,budget:16},
];
function propagate(from,dest,scene) {
  const best=new Map([[from,{cost:0,path:[from],length:0,loss:0}]]),done=new Set();
  for (;;) {
    const row=[...best].filter(([n])=>!done.has(n)).sort((a,b)=>a[1].cost-b[1].cost)[0];
    if(!row) return null;
    const [n,x]=row;
    if(n===dest) return x;
    done.add(n);
    for (const [a,b,length,loss,rule] of edges) {
      if(rule!=="always"&&!scene[rule]) continue;
      const next=a===n?b:b===n?a:null;
      if(next===null||done.has(next)) continue;
      const cost=x.cost+length+loss;
      if(cost<(best.get(next)?.cost??Infinity))
        best.set(next,{cost,path:[...x.path,next],length:x.length+length,loss:x.loss+loss});
    }
  }
}
function sceneAtEmission(event,scene) {
  return Object.fromEntries(Object.entries(listen).map(([npc,p])=>{
    const distance=Math.hypot(p[0]-event.position[0],p[1]-event.position[1]);
    const path=propagate("S",npc,scene);
    const heard=path!==null&&path.cost<=scene.budget;
    return [npc,{distance,budget:scene.budget,path,heard,observation:heard?{
      eventId:event.eventId,tick:event.tick,tag:event.tag,
      estimatedRegion:npc==="A"?"left doorway":path.path.at(-2)==="B grate"?"vent-side alcove":
        path.path.at(-2)==="B door"?"workshop doorway":"hall arrival area"
    }:null}];
  }));
}
const output=scenarios.map(s=>({revision:s.revision,...sceneAtEmission(source,s)}));
assert(output.every(s=>s.A.distance===4&&s.B.distance===4&&s.A.path.cost===8));
assert.deepEqual(output.map(s=>[s.B.path.cost,s.B.heard]),[[20,false],[4,true],[20,true],[15,true]]);
assert.equal(output[3].B.path.path.at(-2),"B grate"); // acoustic-only; not in movement nav.
const isolated=sceneAtEmission(source,{revision:5,open:false,vent:false,hall:false,budget:100});
assert.equal(isolated.B.path,null);
assert.equal(isolated.B.heard,false);
assert.equal(isolated.B.observation,null);
const oldSnapshot=JSON.stringify(output[0]);
source.position=[200,200]; scenarios[0].open=true;
assert.equal(JSON.stringify(output[0]),oldSnapshot);
assert.equal(output[0].B.observation,null);
assert(!("position" in output[3].B.observation));
console.log(JSON.stringify(output,null,2));
