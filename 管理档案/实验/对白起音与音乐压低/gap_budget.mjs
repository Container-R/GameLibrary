import assert from 'node:assert/strict';

function budget(gap, release, attack, depth) {
  assert(gap >= 0 && release > 0 && attack > 0 && depth > 0);
  const turnAt = Math.max(0, gap - attack);
  const highestDb = -depth + depth * Math.min(1, turnAt / release);
  return {gap, highestDb, unityHoldMs: Math.max(0, turnAt - release),
          reachesUnity: turnAt >= release};
}
const rows = [140,220,260].map(gap=>budget(gap,160,60,7.5));
assert.deepEqual(rows, [
  {gap:140,highestDb:-3.75,unityHoldMs:0,reachesUnity:false},
  {gap:220,highestDb:0,unityHoldMs:0,reachesUnity:true},
  {gap:260,highestDb:0,unityHoldMs:40,reachesUnity:true}
]);
console.log(JSON.stringify(rows,null,2));
