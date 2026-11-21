"use strict";
const assert = (ok, context) => { if (!ok) throw Error(context); };
const points = [["exit", [4, 0]], ["lower", [4, -.35]]];
const samples = [
  ["air", [4, .12], null],
  ["lower shelf", [4, -.35], "shelf"],
  ["unbaked lip", [4.35, 0], "deck"],
  ["separate plate", [4, .08], "plate"],
  ["deck", [4, 0], "deck"],
];
const rows = samples.map(([name, [x, y], support]) => {
  const [d, owner] = points.map(([owner, [a, b]]) => [Math.hypot(x - a, y - b), owner])
    .sort((a, b) => a[0] - b[0])[0];
  const near = d <= .50;
  const onDeck = support === "deck";
  const exitAttached = near && owner === "exit" && d <= .15;
  return { name, distance: +d.toFixed(3), owner, support, basic: support !== null && near,
    onDeck, exitAttached, accept: onDeck && exitAttached };
});
assert(JSON.stringify(rows.map(x => [x.basic,x.onDeck,x.exitAttached,x.accept])) ===
  JSON.stringify([[false,false,true,false],[true,false,false,false],[true,true,false,false],
    [true,false,true,false],[true,true,true,true]]), "landing controls");
class Action {
  constructor() {
    Object.assign(this, {phase:"follow", sequence:0, active:null, path:1, pending:null, commits:[]});
  }
  enter(routeGen, enabled) {
    if (this.phase !== "follow") return null;
    if (routeGen !== this.path || !enabled) { this.phase = "replan"; return null; }
    this.active = ++this.sequence;
    this.phase = "cross";
    return this.active;
  }
  changeTarget(gen) {
    if (this.phase === "cross") this.pending = gen;
    else { this.path = gen; this.phase = "replan"; }
  }
  land(token, result) {
    if (this.phase !== "cross" || token !== this.active) return "ignore";
    if (result.support === null) return "wait";
    this.active = null;
    if (!result.accept) { this.phase = "recover"; return "reject"; }
    this.commits.push(token);
    this.phase = "follow";
    if (this.pending !== null) {
      this.path = this.pending; this.pending = null; this.phase = "replan";
    }
    return "complete";
  }
}
const [air, lower, lip, plate, right] = rows;
const blocked = new Action();
assert(blocked.enter(1, false) === null && blocked.phase === "replan" && !blocked.commits.length, "disabled");
const changed = new Action(), jump = changed.enter(1, true);
changed.changeTarget(2);
assert(changed.phase === "cross" && changed.path === 1 && changed.pending === 2, "don't release in air");
assert(changed.land(jump, right) === "complete" && changed.phase === "replan" &&
  changed.path === 2 && changed.commits.length === 1, "land before replan");
assert(changed.land(jump, right) === "ignore" && changed.commits.length === 1, "duplicate callback");
const midair = new Action(), inflight = midair.enter(1, true);
assert(midair.land(inflight, air) === "wait" && midair.phase === "cross" &&
  midair.active === inflight && midair.commits.length === 0, "early callback while airborne");
assert(midair.land(inflight, right) === "complete", "land after early callback");
for (const fail of [lower, lip, plate]) {
  const flow = new Action(), first = flow.enter(1, true);
  assert(flow.land(first, right) === "complete", "positive first landing");
  const second = flow.enter(1, true);
  assert(flow.land(first, right) === "ignore" && flow.active === second, "old takeoff token");
  assert(flow.land(second, fail) === "reject" && flow.phase === "recover" &&
    flow.commits.length === 1, "cannot advance on unsupported exit");
}
console.log(JSON.stringify({rows, control:["disabled: replan without completion","new target: cross then complete once and replan","airborne: remain in cross","wrong grounded landings: recover","duplicate and old callbacks: ignore"]}, null, 2));
