"use strict";
const assert = require("node:assert/strict");
// All numbers are fictional milliseconds on one monotonic time origin.
const chartBeat = 2000;
const played = {when:3000, song:2000, rate:1, epoch:7, begin:2950};
const render = {when:3000,song:2060,rate:1,epoch:7}; // queued 60 ms ahead of output.
const taps = [
  {event:3010,frame:3030,epoch:7},
  {event:3055,frame:3060,epoch:7},
  {event:2982,frame:3060,epoch:7}
];
const calibration=10;
const errorAt=(anchor,t)=>anchor.song+(t-anchor.when)*anchor.rate-chartBeat;
const classify=e=>Math.abs(e)<=30?"hit":e<0?"early":"late";
const output=taps.map(t=>{
  const scoring = errorAt(played,t.event-calibration);
  return {event:t.event,frame:t.frame,
          renderClock: errorAt(render,t.event-calibration),
          deliveredFrame: errorAt(played,t.frame-calibration),
          scoring,
          verdict: classify(scoring)};
});
assert.deepEqual(output.map(t=>[t.renderClock,t.deliveredFrame,t.scoring,t.verdict]),
  [[60,20,0,"hit"],[105,50,45,"late"],[32,50,-28,"hit"]]);
// Arrival frame alone cannot distinguish the last two, whose signed errors differ.
assert.equal(output[1].frame,output[2].frame);
const score=(anchor,tap)=>{
  const corrected=tap.event-calibration;
  return anchor.ready!==false&&anchor.epoch===tap.epoch&&corrected>=anchor.begin?errorAt(anchor,corrected):null;
};
assert.equal(score({...played,epoch:8},taps[0]),null);
const stageComparison={exactBoundaries:[-31,-30,30,31].map(classify),wrongSignedOffset:errorAt(played,taps[0].event+calibration),staleAfterSeek:score({...played,epoch:8},taps[0])};
assert.deepEqual(stageComparison.exactBoundaries,["early","hit","hit","late"]);
assert.equal(stageComparison.wrongSignedOffset,20);
const newAnchor={when:3080,song:2000,rate:1,epoch:8,begin:3080};
const switchedTap={event:3090,frame:3100,epoch:8};
const switched={
 oldMapping:errorAt(played,switchedTap.event-calibration),
 missingAnchor:score({epoch:8,ready:false},switchedTap),
 newMapping:score(newAnchor,switchedTap),
 correctedBeforeValidSegment:score(newAnchor,{...switchedTap,event:3084})
};
assert.deepEqual(switched,{oldMapping:80,missingAnchor:null,newMapping:0,correctedBeforeValidSegment:null});
// One unassigned note, two events that reach the same frame: consider by logical event time, not array order.
const batch=taps.slice(1).sort((a,b)=>a.event-b.event);
const batchInWindow=batch.filter(t=>classify(score(played,t))==="hit").map(t=>t.event);
assert.deepEqual(batchInWindow,[2982]);
const latestCorrected=played.when+(chartBeat+30-played.song)/played.rate;
const latestReport=latestCorrected+calibration;
const queueGrace=25;
const finalization={latestCorrected,latestReport,earliestFinalAfterDrain:latestReport+queueGrace};
assert.deepEqual(finalization,{latestCorrected:3030,latestReport:3040,earliestFinalAfterDrain:3065});
console.log(JSON.stringify({chartBeat,calibration,played,render,output,stageComparison,switched,batchInWindow,finalization},null,2));
