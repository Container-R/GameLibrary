"use strict";
const assert = require("node:assert/strict");
const fee = gross => gross * 3n / 100n;

function replay(events) {
  // One fictional sell order and one already-funded buyer. Not a database simulation.
  const order = {initial:100n, remaining:100n, gross:0n, paid:0n, closed:false};
  const seen = new Map(), fees = [];
  let buyer = 100n, seller = 0n, treasury = 0n;
  for (const [id, gross] of events) {
    if (id === "cancel") {
      order.closed = true;
      continue;
    }
    if (seen.has(id)) {
      assert.equal(seen.get(id), gross, "conflicting duplicate");
      continue;
    }
    if (order.closed || gross <= 0n || gross > order.remaining) throw Error("invalid fill");
    const before = order.gross, after = before + gross;
    const delta = fee(after) - fee(before);
    order.gross = after;
    order.paid += delta;
    order.remaining -= gross;
    buyer -= gross;
    seller += gross - delta;
    treasury += delta;
    seen.set(id, gross);
    fees.push(delta);
    assert.equal(buyer + seller + treasury, 100n);
    assert.equal(order.paid, fee(order.gross));
    assert.equal(order.gross + order.remaining, order.initial);
  }
  return {fees, gross:order.gross, buyer, seller, treasury};
}

const full = replay([["a",17n],["b",17n],["b",17n],["c",17n],["d",17n],["e",16n],["f",16n]]);
assert.deepEqual(full,{fees:[0n,1n,0n,1n,0n,1n],gross:100n,buyer:0n,seller:97n,treasury:3n});
const partial = replay([["a",17n],["b",17n],["cancel"],["b",17n]]);
assert.deepEqual(partial,{fees:[0n,1n],gross:34n,buyer:66n,seller:33n,treasury:1n});
assert.throws(()=>replay([["a",17n],["cancel"],["b",17n]]), /invalid fill/);
assert.throws(()=>replay([["a",17n],["a",16n]]), /conflicting duplicate/);
let partitions = 0;
for(let a=1n;a<99n;a++) for(let b=1n;b<100n-a;b++){
  const res = replay([["a",a],["b",b],["c",100n-a-b]]);
  assert.equal(res.treasury,3n);
  partitions++;
}
console.log(JSON.stringify({full,partial,partitions},(_,x)=>typeof x==="bigint"?String(x):x,2));
