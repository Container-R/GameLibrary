"use strict";
const assert = require("node:assert/strict");
const build = "arena-07";
const scope = "lane-crossing";
const cell = "bridge";
const regions = ["lower", "upper", "connector", "unknown", "unused"];
const regionOf = (event) => {
  if (event.entryRoutePhase === "connector") return "connector";
  if (event.entrySupport === "stone-floor") return "lower";
  if (event.entrySupport === "bridge-deck") return "upper";
  return "unknown";
};
const base = {build, scope, cell, x: 8, y: 5};
// Each traversal enters one marked test region; metadata is frozen at entry.
const visit = (id, entrySupport, failed, more = {}) => ({
  ...base, id, eventId: "visit:" + id, entrySupport, failed,
  terminal: true, eligible: true, ...more
});
const main = [
  ...Array.from({length:200}, (_,i) => visit("lower-"+i, "stone-floor", i<10)),
  ...Array.from({length:10}, (_,i) => visit("upper-"+i, "bridge-deck", i<4))
];
const extras = [
  main[0], // identical transport retry
  visit("old-build", "bridge-deck", true, {build:"arena-06"}),
  visit("no-terminal-yet", "bridge-deck", undefined, {terminal:false}),
  visit("turned-back", "bridge-deck", undefined, {otherEnding:"turned-back"}),
  visit("ineligible", "bridge-deck", false, {eligible:false}),
  visit("stair", "stone-floor", true, {entryRoutePhase:"connector", z:1.9}),
  visit("airborne", null, false, {z:2, exitSupport:"stone-floor"})
];
const row = () => ({failed: 0, exposure: 0});
const result = (counts) => ({...counts, risk:counts.exposure ? counts.failed/counts.exposure : null});
function aggregate(events) {
  const byRegion = Object.fromEntries(regions.map(k => [k,row()]));
  const exclusions = {oldOrOutOfScope:0,ineligible:0,open:0,retry:0};
  const otherEndingByRegion = Object.fromEntries(regions.map(k => [k,0]));
  const openByRegion = Object.fromEntries(regions.map(k => [k,0]));
  const seen = new Map();
  const attempts = new Set();
  for (const e of events) {
    if (e.build !== build || e.scope !== scope || e.cell !== cell) { ++exclusions.oldOrOutOfScope; continue; }
    const prior = seen.get(e.eventId);
    if (prior) {
      assert.deepEqual(prior,e,"conflicting payload for event id");
      ++exclusions.retry;
      continue;
    }
    seen.set(e.eventId,e);
    if (!e.eligible) { ++exclusions.ineligible; continue; }
    assert(!attempts.has(e.id),"duplicate materialized traversal");
    attempts.add(e.id);
    const region = regionOf(e);
    if (!e.terminal) { ++exclusions.open; ++openByRegion[region]; continue; }
    if (e.otherEnding) {
      assert.equal(e.failed, undefined, "an alternate ending cannot also be a binary result");
      ++otherEndingByRegion[region];
      continue;
    }
    assert.equal(typeof e.failed,"boolean");
    const r = byRegion[region];
    ++r.exposure;
    r.failed += Number(e.failed);
  }
  const collapsedWithoutConnectorsOrUnknown = row();
  for (const k of ["lower","upper"]) {
    collapsedWithoutConnectorsOrUnknown.exposure += byRegion[k].exposure;
    collapsedWithoutConnectorsOrUnknown.failed += byRegion[k].failed;
  }
  return {byRegion:Object.fromEntries(regions.map(k=>[k,result(byRegion[k])])),collapsedWithoutConnectorsOrUnknown:result(collapsedWithoutConnectorsOrUnknown),openByRegion,otherEndingByRegion,exclusions};
}
const output = aggregate([...main,...extras]);
assert.deepEqual(output.byRegion.lower,{failed:10,exposure:200,risk:0.05});
assert.deepEqual(output.byRegion.upper,{failed:4,exposure:10,risk:0.4});
assert.deepEqual(output.byRegion.connector,{failed:1,exposure:1,risk:1});
assert.deepEqual(output.byRegion.unknown,{failed:0,exposure:1,risk:0});
assert.deepEqual(output.byRegion.unused,{failed:0,exposure:0,risk:null});
assert.deepEqual(output.collapsedWithoutConnectorsOrUnknown,{failed:14,exposure:210,risk:14/210});
assert.deepEqual(output.openByRegion,{lower:0,upper:1,connector:0,unknown:0,unused:0});
assert.deepEqual(output.otherEndingByRegion,{lower:0,upper:1,connector:0,unknown:0,unused:0});
assert.deepEqual(output.exclusions,{oldOrOutOfScope:1,ineligible:1,open:1,retry:1});
assert.throws(() => aggregate([main[0],{...main[0],failed:false}]), /conflicting payload/);
assert.throws(() => aggregate([main[0],{...main[0],eventId:"another"}]), /duplicate materialized traversal/);
assert.throws(() => aggregate([extras[2],{...extras[2],eventId:"open-again"}]), /duplicate materialized traversal/);
assert.throws(() => aggregate([extras[2],{...extras[2],eventId:"finished",terminal:true,failed:false}]), /duplicate materialized traversal/);
console.log(JSON.stringify(output,null,2));
