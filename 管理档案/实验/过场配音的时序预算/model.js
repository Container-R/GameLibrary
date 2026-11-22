"use strict";
const assert = require("node:assert/strict");

// Authored anchors in scene-clock milliseconds. Only marked pauses are elastic.
const start = 600;
const hardCue = 6500;
const preferred = Object.freeze({reaction:750, afterB:550});
const minimum = Object.freeze({reaction:450, afterB:400});
function schedule(a, b) {
  for (const clip of [a,b]) {
    assert(Number.isSafeInteger(clip.occupiedMs) && clip.occupiedMs > 0);
    assert(Number.isSafeInteger(clip.speechEndMs) && clip.speechEndMs >= 0 && clip.speechEndMs <= clip.occupiedMs);
  }
  let tail = preferred.afterB, reaction = preferred.reaction;
  const fixed = a.occupiedMs + b.occupiedMs;
  const window = hardCue-start;
  const takeFromTail = Math.min(Math.max(0,fixed+tail+reaction-window),tail-minimum.afterB);
  tail -= takeFromTail;
  const takeFromReaction = Math.min(Math.max(0,fixed+tail+reaction-window),reaction-minimum.reaction);
  reaction -= takeFromReaction;
  const overflow = Math.max(0, fixed+tail+reaction-window);
  if (overflow) return {ok:false, overflow, hardCue, minimumPlan:{aStart:start,aEnd:start+a.occupiedMs,bStart:start+a.occupiedMs+reaction,bEnd:start+a.occupiedMs+reaction+b.occupiedMs,finish:hardCue+overflow}};
  const aEnd = start + a.occupiedMs;
  const bStart = aEnd + reaction, bEnd = bStart + b.occupiedMs;
  return {ok:true, dialogueA:{start,speechEnd:start+a.speechEndMs, sectionEnd:aEnd}, dialogueB:{start:bStart,speechEnd:bStart+b.speechEndMs,sectionEnd:bEnd},reaction,afterB:tail,neutralHold:hardCue-(bEnd+tail),hardCue};
}
const cite = {
  reference: [{occupiedMs:2050,speechEndMs:1900},{occupiedMs:1550,speechEndMs:1480}],
  stretch: [{occupiedMs:3130,speechEndMs:2850},{occupiedMs:1810,speechEndMs:1690}],
  impossible: [{occupiedMs:3430,speechEndMs:3150},{occupiedMs:1800,speechEndMs:1690}],
};
const out = Object.fromEntries(Object.entries(cite).map(([k,clips]) => [k,schedule(...clips)]));
out.copyOldBStart = {bStart:out.reference.dialogueB.start, aSectionEnd:out.stretch.dialogueA.sectionEnd, overlap:out.stretch.dialogueA.sectionEnd-out.reference.dialogueB.start};
assert.equal(out.copyOldBStart.overlap,330);
assert.equal(out.reference.neutralHold,1000);
assert.equal(out.stretch.dialogueB.start,4290);
assert.deepEqual([out.stretch.reaction,out.stretch.afterB,out.stretch.neutralHold],[560,400,0]);
assert.deepEqual(out.impossible,{ok:false,overflow:180,hardCue:6500,minimumPlan:{aStart:600,aEnd:4030,bStart:4480,bEnd:6280,finish:6680}});
// A false green result if one schedules against the last phoneme instead of the occupied section.
assert.equal(schedule(...cite.impossible.map(v=>({occupiedMs:v.speechEndMs,speechEndMs:v.speechEndMs}))).ok,true);
for (const x of [out.reference,out.stretch]) {
  assert.equal(x.dialogueB.sectionEnd+x.afterB+x.neutralHold,hardCue);
  assert(x.dialogueA.speechEnd <= x.dialogueA.sectionEnd);
}
console.log(JSON.stringify(out,null,2));
