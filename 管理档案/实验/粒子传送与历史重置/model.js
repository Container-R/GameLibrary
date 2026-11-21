"use strict";
const assert=require("node:assert/strict");
function sample(start,end,carry,step=.5){
 const dist=Math.abs(end-start), dir=Math.sign(end-start), n=Math.floor((dist+carry)/step);
 return {positions:Array.from({length:n},(_,i)=>start+dir*((i+1)*step-carry)),carry:dist+carry-n*step};
}
function relocate({resetPose=false,skipDistance=false,breakTrail=false}={}){
 const from=0,to=100,local=1,world=from+local,alpha=.5;
 const previousTransform=resetPose?to:from;
 const emitted=sample(skipDistance?to:from,to,0);
 const segments=breakTrail?[[from],[to]]:[[from,to]];
 const edges=segments.flatMap(p=>p.slice(1).map((v,i)=>[p[i],v]));
 return {world_old:world,local_old:to+local,interpolated_emitter:previousTransform*(1-alpha)+to*alpha,
   spawned:emitted.positions.length,first_spawn:emitted.positions.at(0)??null,
   last_spawn:emitted.positions.at(-1)??null,trail_edges:edges};
}
const histories={
 no_resets:relocate(),
 rebase_distance:relocate({skipDistance:true}),
 rebase_and_reset_pose:relocate({skipDistance:true,resetPose:true}),
 all_three:relocate({skipDistance:true,resetPose:true,breakTrail:true}),
};
const ticks=x=>{const a=sample(100,100.25,x);return [a,sample(100.25,100.5,a.carry)];};
const phase={continuing:ticks(.25),fresh:ticks(0)};
assert.deepEqual(Object.values(histories).map(x=>[x.world_old,x.local_old,x.interpolated_emitter,x.spawned,x.trail_edges]),[
 [1,101,50,200,[[0,100]]],[1,101,50,0,[[0,100]]],[1,101,100,0,[[0,100]]],[1,101,100,0,[]]
]);
assert.deepEqual([histories.no_resets.first_spawn,histories.no_resets.last_spawn],[.5,100]);
assert.deepEqual(phase.continuing,[{positions:[100.25],carry:0},{positions:[],carry:.25}]);
assert.deepEqual(phase.fresh,[{positions:[],carry:.25},{positions:[100.5],carry:0}]);
console.log(JSON.stringify({scope:"deterministic history-policy model, not a renderer or stock emitter",histories,phase},null,2));
