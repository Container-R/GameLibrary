import assert from "node:assert/strict";
const rows = [1,1,1,1,.70,.70,.70,.70,.70].map((scale, frame) => ({
  frame, scale, gpuMs: +(7+15*scale**2).toFixed(2),
}));
const availableDelay = 4; // teaching fixture, not an implementation of Unity
const logged = rows.slice(availableDelay).map(({frame: arrival, scale: current}) => ({
  arrival, current, produced: rows[arrival-availableDelay],
}));
const first = logged[0], validLow = logged.find(x => x.produced.scale===.70);
assert.deepEqual(first,{arrival:4,current:.70,produced:{frame:0,scale:1,gpuMs:22}});
assert.deepEqual(validLow,{arrival:8,current:.70,produced:{frame:4,scale:.70,gpuMs:14.35}});
assert.equal(logged.filter(x => x.current!==x.produced.scale).length,4);
const interval = (a,b)=>b-a;
const graphics=[0,8], compute=[4,10];
const sum = interval(...graphics)+interval(...compute);
const union = Math.max(graphics[1], compute[1])-Math.min(graphics[0], compute[0]);
assert.deepEqual([sum,union],[14,10]);
console.log(JSON.stringify({first,validLow,queueExample:{graphics,compute,sum,union}},null,2));
