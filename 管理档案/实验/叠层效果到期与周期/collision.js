"use strict";
// One periodic due time collides with the two-layer shared group deadline.
function atBoundary(order){
  const ledger=[], s={count:2,end:8,nextPulse:8};
  const at=8;
  for(const stage of order){
    if(stage==="expire"&&s.end===at){s.count=0;ledger.push({event:"expiry",remaining:0});}
    if(stage==="pulse"&&s.nextPulse===at&&s.count){ledger.push({event:"pulse",contributingLayers:s.count});}
  }
  return ledger;
}
const byTime=["expire","pulse"], byPulse=["pulse","expire"];
const out={expiryFirst:atBoundary(byTime),pulseFirst:atBoundary(byPulse)};
if(out.expiryFirst.length!==1||out.pulseFirst[0].contributingLayers!==2||out.pulseFirst.at(-1).remaining!==0)
  throw Error(JSON.stringify(out));
console.log(JSON.stringify(out,null,2));
