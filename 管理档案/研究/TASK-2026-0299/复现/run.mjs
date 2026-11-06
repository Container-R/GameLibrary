import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';
import { DragModel } from './model.mjs';
const here = fileURLToPath(new URL('.', import.meta.url));
const data = JSON.parse(readFileSync(resolve(here, 'model-inputs.json'), 'utf8'));
const rows = [];
for (const c of data.cases) {
  const probes = [];
  const down = c.steps.find(e => e.type === 'down');
  const m = new DragModel(c.hooks === 'reenter' ? {
    cleanup(m, old) {
      m.finish(old, 'up', { hit: 'label-B' }); m.input(down);
      probes.push({ at: 'cleanup', commits: m.commits, active: m.active?.id ?? null });
    },
    notify(m, old) {
      m.finish(old, 'up', { hit: 'label-B' }); m.input(down);
      m.input({ type: 'capture-result', pointerId: 7, ok: true });
      m.cleanup(old); // repeat cleanup must not erase new preview
      probes.push({ at: 'notify', commits: m.commits, active: m.active?.id ?? null,
        previewOwner: m.previewOwner });
    }
  } : {});
  const trace=[];
  for (const e of c.steps) { m.input(e); trace.push({ input: e, state: m.snapshot() }); }
  const end=m.snapshot();
  assert.equal(end.commits, end.results.filter(r => r.status==='accepted').length);
  assert.equal(new Set(end.results.map(r=>r.attemptId)).size,end.results.length);
  assert.equal(end.cleanups,end.results.length);
  rows.push({ id:c.id, name:c.name, end, probes, trace });
}
// Explicit author checks. These check the authored algorithm, not browser conformance.
for (const r of rows) {
  const accepted=['R01','R05','M04'].includes(r.id);
  assert.equal(r.end.commits, accepted ? 1 : 0, r.id);
  assert.equal(r.end.itemSlot, accepted ? 'B' : r.id==='R09' ? 'C' : 'A', r.id);
}
assert.equal(rows.find(r=>r.id==='R10').end.active.attemptId,102);
assert.equal(rows.find(r=>r.id==='R10').end.ignoredCallbacks,1);
assert.deepEqual(rows.find(r=>r.id==='M04').probes,[
  {at:'cleanup',commits:1,active:null},
  {at:'notify',commits:1,active:102,previewOwner:102}]);
// A direct premature completion must not bypass capture setup.
const early = new DragModel();
early.input(data.cases[0].steps[0]);
early.finish(early.active, 'up', { hit: 'label-B' });
assert.equal(early.commits, 0);
assert.equal(early.active.phase, 'starting');
// Two intentionally wrong policies, only for the contrasts claimed by the article.
const wrong=[];
for (const id of ['R01','R02','R04','R07','R08']) {
  const c=data.cases.find(c=>c.id===id); let targetCalls=0,cached=null,cachedCalls=0,rollbacks=0;
  for (const e of c.steps) {
    if(e.type==='up' && /^(label|slot)-[ABC]$/.test(e.eventTarget??'')) targetCalls++;
    if(e.type==='lost') rollbacks++;
    if(e.type==='move' && /^label-[ABC]$/.test(e.hit??'')) cached=e.hit;
    if(['up','cancel','lost'].includes(e.type) && cached) cachedCalls++;
  }
  wrong.push({id,targetBasedMoveCalls:targetCalls,unconditionalRollbackCalls:rollbacks,
    cachedCandidateMoveCalls:cachedCalls});
}
const out=resolve(process.argv[2] ?? resolve(here,'run-01'));
mkdirSync(out,{recursive:true});
writeFileSync(resolve(out,'output.json'),JSON.stringify({kind:'pure-application-model',runtime:process.version,rows,wrongPolicies:wrong},null,2)+'\n');
const lines=rows.map(r=>`${r.id}: item=${r.end.itemSlot}; commits=${r.end.commits}; cleanup=${r.end.cleanups}; active=${r.end.active?.attemptId??'-'}; reason=${r.end.results.map(x=>x.reason).join(',')||'-'}`);
writeFileSync(resolve(out,'summary.txt'),lines.join('\n')+'\n');
console.log(lines.join('\n')); console.log('Author assertions passed; no browser was run.');
