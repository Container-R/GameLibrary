import assert from 'node:assert/strict';

// Example controller, not a claim about a middleware API.
// Time is illustrative mixer samples. Exact intervals are half-open.
class Occupancy {
  #requests = new Map();
  #latest = new Map();

  schedule(id, seq, start, end, attenuation) {
    if (!Number.isSafeInteger(start) || !Number.isSafeInteger(end) || end <= start ||
        !Number.isFinite(attenuation) || attenuation < 0) throw new Error('invalid request');
    if (seq <= (this.#latest.get(id) ?? -1)) return false;
    this.#latest.set(id, seq);
    this.#requests.set(id, {seq, start, end, attenuation});
    return true;
  }
  stop(id, seq) {
    const current=this.#requests.get(id);
    if (current?.seq !== seq) return false;
    this.#requests.delete(id);
    return true;
  }
  sample(at) {
    const active=[...this.#requests].filter(([, r])=>r.start<=at&&at<r.end);
    // Strongest request wins; adding dB would double-dip on overlaps.
    return {active:active.map(([id])=>id), targetDb:-Math.max(0,...active.map(([,r])=>r.attenuation))};
  }
}

const q=new Occupancy();
q.schedule('A',1,175,460,5);
q.schedule('B',1,425,680,7.5);
q.schedule('C',1,400,650,12);
assert.equal(q.stop('C',1),true);
const results=[390,410,430,460,470,680,690].map(at=>({at,...q.sample(at)}));
assert.deepEqual(results.map(x=>x.active),[['A'],['A'],['A','B'],['B'],['B'],[],[]]);
assert.deepEqual(results.map(x=>x.targetDb),[-5,-5,-7.5,-7.5,-7.5,-0,-0]);
assert.equal(q.schedule('C',1,400,650,12),false);  // late replay can't resurrect C
q.schedule('B',2,700,900,4);                       // updated onset; same logical ID
assert.equal(q.stop('B',1),false);                 // stale callback can't clear new request
assert.deepEqual(q.sample(710),{active:['B'],targetDb:-4});
console.log(JSON.stringify({results, delayedOnset:q.sample(710)},null,2));
