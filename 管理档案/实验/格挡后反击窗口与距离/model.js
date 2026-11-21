"use strict";
const assert=require("node:assert/strict");
// Synthetic rules: defender acts now (tick 0). If contact and guard coincide,
// guard is legal and blocks. Distance denotes gap between original facing
// reference and exposed target hurtbox, not distance between root centers.
function test({ready=8,delay=0,distance=1.4,reach,firstActive,lastActive=firstActive,step={}}){
 let result={tick:null,outcome:"whiff"};
 for(let t=delay+firstActive-1;t<=delay+lastActive-1;t++){
  const localTick=t-delay;
  const gap=typeof distance==="function" ? distance(t) : distance;
  if((step[localTick]??0)+reach>=gap){
   result={tick:t,outcome:t<ready?"punish":"blocked"};break;
  }
 }
 return result;
}
const fast={reach:.95,firstActive:4};
const long={reach:1.5,firstActive:8};
const advance={reach:.95,firstActive:6,lastActive:9,step:{5:.3,6:.4,7:.44,8:.5}};
const rows={
 close_fast:test({...fast,distance:.9}),
 tip_fast:test(fast),
 tip_long:test(long),
 tip_long_one_tick_late:test({...long,delay:1}),
 tip_first_active_misses_later_touch:test(advance),
 alternate_branch_guards_earlier:test({...long,ready:6}),
};
assert.deepEqual(Object.values(rows),[
 {tick:3,outcome:"punish"},{tick:null,outcome:"whiff"},{tick:7,outcome:"punish"},
 {tick:8,outcome:"blocked"},{tick:8,outcome:"blocked"},{tick:7,outcome:"blocked"}
]);
// The gap only closes briefly. Immediate and one-tick-late probes do
// not exhaust all timings; this deliberately compares the whole window.
const oneTickHurtbox=Array.from({length:5},(_,delay)=>({
 delay,...test({...fast,delay,distance:t=>t===5 ? .9 : 1.4})
}));
assert.deepEqual(oneTickHurtbox.filter(x=>x.outcome==="punish"),[{delay:2,tick:5,outcome:"punish"}]);
console.log(JSON.stringify({window8:rows,oneTickHurtbox},null,2));
