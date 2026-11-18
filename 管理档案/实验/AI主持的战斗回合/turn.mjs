import assert from "node:assert/strict";
const initial = { turn: 17, active: "brin", controller: "A", action: true, move: 6, bonus: true, advanced: 0 };
const events = [
  { source:"model", kind:"action", turn:17, active:"brin" },
  { source:"model", kind:"end", turn:17, active:"brin" }, // normalized proposal after a question
  { source:"model", kind:"move", turn:17, active:"brin", distance:2 },
  { source:"player-control", actor:"B", kind:"end", turn:17, active:"brin" },
  { source:"player-control", actor:"A", kind:"end", turn:17, active:"brin" },
  { source:"player-control", actor:"A", kind:"end", turn:17, active:"brin" }
];
function reduce(s, e, guarded) {
  if(e.turn !== s.turn || e.active !== s.active) return [s, "stale"];
  if(e.kind === "end"){
    if(guarded && !(e.source === "player-control" && e.actor === s.controller)) return [s, "not-confirmed"];
    return [{turn:18, active:"kara", controller:"B", action:true, move:5, bonus:true, advanced:s.advanced+1}, "advance"];
  }
  if(e.source === "model" && e.kind === "action" && s.action) return [{...s, action:false}, "action"];
  if(e.source === "model" && e.kind === "move" && e.distance > 0 && e.distance <= s.move) return [{...s, move:s.move-e.distance}, "move"];
  return [s, "ignored"];
}
function run(guarded){
  let s=initial;
  return events.map(e=>{
    let result;
    [s,result]=reduce(s,e,guarded);
    return [result,s.turn,s.active,s.action,s.move,s.bonus,s.advanced];
  });
}
const guarded=run(true), baseline=run(false);
assert.deepEqual(guarded.map(x=>x[0]),["action","not-confirmed","move","not-confirmed","advance","stale"]);
assert.deepEqual(guarded[2],["move",17,"brin",false,4,true,0]);
assert.deepEqual(guarded[5],["stale",18,"kara",true,5,true,1]);
assert.deepEqual(baseline.map(x=>x[0]),["action","advance","stale","stale","stale","stale"]);
console.log(JSON.stringify({baseline,guarded},null,2));
