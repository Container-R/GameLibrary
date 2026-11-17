// A single already-submitted footstep, corrected twice by the same source proof.
// This model records decisions only; no playback, networking or engine calls.
import assert from "node:assert/strict";
const id = "3/41/footstep";
const old = {id, tick:10, material:"metal", cell:5, state:"submitted"};
const next = {id, tick:11, material:"stone", cell:6};
function compare(history, replay) {
  if (!history) return ["add", "submit"];
  const changed = history.material !== replay.material || history.cell !== replay.cell || history.tick !== replay.tick;
  if (!changed) return ["keep", "do not submit"];
  return ["replace record", history.state === "submitted" ? "do not submit" : "update waiting request"];
}
const cases = {
 sameTickKeyAlreadySeen: new Set([`10/${id}`]).has(`10/${id}`) ? ["submit metal"] : [],
 moveToNextTickKeyNotSeen: !new Set([`10/${id}`]).has(`11/${id}`) ? ["submit metal","submit stone"] : [],
 idOnlyAlreadySeen: new Set([id]).has(next.id) ? ["submit metal"] : [],
 withOldWindow: compare(old,next),
 withOldWindowAndSecondCorrection: compare({...next,state:"submitted"},next),
 croppedOldWindow: compare(old.tick < next.tick ? undefined : old,next),
 secondCorrectionAfterLosingLedger: compare(undefined,next)
};
assert.deepEqual(Object.values(cases),[
 ["submit metal"],["submit metal","submit stone"],["submit metal"],
 ["replace record","do not submit"],["keep","do not submit"],
 ["add","submit"],["add","submit"]
]);
for(const [name,v] of Object.entries(cases)) console.log(`${name}: ${v.join(" | ")}`);
