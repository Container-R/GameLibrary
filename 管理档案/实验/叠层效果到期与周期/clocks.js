"use strict";
// Selected toy rule: expire, accept new unique actions, then evaluate periodic ticks.
function run(kind,{phase="keep", allowAtCap=false, applications=[]}={}){
  const dur=5, interval=5, cap=2;
  let expiries=[], count=0, end=null, next=null;
  const seen=new Set(), out=[];
  for(let t=0;t<=13;t++){
    if(kind==="perLayer") expiries=expiries.filter(x=>x>t);
    else if(end===t){
      if(kind==="dropOne"&&count>1){count--;end=t+dur;}
      else {count=0;end=null;}
    }
    const before=()=>kind==="perLayer"?expiries.length:count;
    if(!before())next=null;
    const applied=[];
    for(const [when,id] of applications.filter(x=>x[0]===t)){
      if(seen.has(id)){applied.push("duplicate");continue;}
      seen.add(id);
      const old=before();
      if(old===cap){
        if(allowAtCap&&kind!=="perLayer"){end=t+dur; if(phase==="reset")next=t+interval;applied.push("refresh-only");}
        else applied.push("rejected-cap");
        continue;
      }
      if(kind==="perLayer")expiries.push(t+dur);
      else {count++;end=t+dur;}
      if(old===0||phase==="reset")next=t+interval;
      applied.push("added");
    }
    const pulse=next===t?before():0;
    if(next===t)next+=interval;
    out.push({t,count:before(),expiry:kind==="perLayer"?expiries.slice():end,pulse,applied});
  }
  return out;
}
const base=[[0,"A0"],[3,"B3"],[4,"B3"]];
const outcomes={
 independent:run("perLayer",{applications:base}),
 shared:run("clear",{applications:base}),
 dropOne:run("dropOne",{applications:base}),
 reset:run("clear",{phase:"reset",applications:base}),
 rejectedCap:run("clear",{applications:[...base,[4,"new-C"]]}),
 refreshCap:run("clear",{allowAtCap:true,applications:[...base,[4,"new-C"]]})
};
const counts=n=>[4,5,8,9,13].map(t=>outcomes[n][t].count);
const checks={
  independent:counts("independent"),shared:counts("shared"),dropOne:counts("dropOne"),
  resetPulseAt5And8:[outcomes.reset[5].pulse,outcomes.reset[8].pulse],
  keepPulseAt5:outcomes.shared[5].pulse,
  cap:[outcomes.rejectedCap[4].expiry,outcomes.refreshCap[4].expiry],
  repeat:outcomes.shared[4].applied
};
const expected={independent:[2,1,0,0,0],shared:[2,2,0,0,0],dropOne:[2,2,1,1,0],resetPulseAt5And8:[0,0],keepPulseAt5:2,cap:[8,9],repeat:["duplicate"]};
if(JSON.stringify(checks)!==JSON.stringify(expected))throw Error(JSON.stringify(checks));
console.log(JSON.stringify({checks,outcomes},null,2));
