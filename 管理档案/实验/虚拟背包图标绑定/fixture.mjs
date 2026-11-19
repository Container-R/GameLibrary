import assert from 'node:assert/strict';
// Original deterministic application model. No Unity, network, textures or timers.
// All state changes and queued completions run serially; rendering is not modeled.
let sequence = 0;
const transcript = [];
class Loader {
  requests = []; queue = []; leases = [];
  start(input, done, synchronous = false) {
    const r = {input: {...input}, done, canceled: false, completed: false};
    this.requests.push(r);
    if (synchronous) this.complete(r);
    return r;
  }
  cancel(r) { if (r) r.canceled = true; } // Deliberately advisory: callbacks may still arrive.
  complete(r, error = false) {
    assert.equal(r.completed, false); r.completed = true;
    let lease = null;
    if (!error) {
      lease = {image: r.input.icon, releases: 0};
      this.leases.push(lease);
    }
    this.queue.push(() => r.done({error, lease}));
  }
  pump() { while (this.queue.length) this.queue.shift()(); }
  release(lease) { if (lease) { lease.releases++; assert.equal(lease.releases, 1); } }
  closed() { assert.ok(this.leases.every(x => x.releases === 1)); }
}
class Cell {
  constructor(loader, mode = 'safe') {
    this.loader = loader; this.mode = mode; this.active = false;
    this.ticket = null; this.target = null; this.image = 'EMPTY';
    this.lease = null; this.request = null; this.index = null;
  }
  unbind() {
    this.active = false; this.ticket = null;
    this.loader.cancel(this.request); this.request = null;
    this.loader.release(this.lease); this.lease = null;
    this.target = null; this.image = 'EMPTY';
  }
  bind(item, index = 0, synchronous = false) {
    // Reset on every bind, including repeated bind with no intervening unbind.
    const previousImage = this.image;
    this.unbind();
    this.active = true; this.index = index;
    this.target = {...item}; this.ticket = ++sequence;
    this.image = this.mode === 'no-clear' ? previousImage : 'LOADING';
    const r = {ticket: this.ticket, target: {...item}, index};
    this.request = this.loader.start(r.target, result => {
      let valid = this.active;
      if (this.mode === 'safe' || this.mode === 'no-clear')
        valid &&= this.ticket === r.ticket && this.target.id === r.target.id &&
          this.target.rev === r.target.rev && this.target.icon === r.target.icon;
      else if (this.mode === 'id-only') valid &&= this.target.id === r.target.id;
      else if (this.mode === 'index-only') valid &&= this.index === r.index;
      // 'cancel-only' requests cancellation but has no result-ownership gate.
      if (!valid) { this.loader.release(result.lease); return; }
      this.loader.release(this.lease); this.lease = result.lease;
      this.image = result.error ? 'ERROR' : result.lease.image;
    }, synchronous);
    return this.request;
  }
}
const A = {id:'item-17', rev:1, icon:'icons/sword-v1'};
const B = {id:'item-42', rev:1, icon:'icons/herb-v1'};
function test(name, fn) { fn(); transcript.push({name, status:'PASS'}); }
function finish(loader, ...cells) { cells.forEach(c=>c.unbind()); loader.closed(); }

test('recycle: B finishes before stale A; cancellation alone fails', () => {
  const output = {};
  for (const mode of ['safe','cancel-only']) {
    const l=new Loader(), c=new Cell(l,mode);
    const a=c.bind(A), b=c.bind(B);
    assert.equal(a.canceled,true);
    l.complete(b);l.pump();assert.equal(c.image,B.icon);
    l.complete(a);l.pump();output[mode]=c.image;
    assert.equal(c.image,mode==='safe'?B.icon:A.icon);finish(l,c);
  }
  transcript.push({case:'recycle',output});
});
test('same id and icon rebound: old failure must not erase new success', () => {
  const output={};
  for(const mode of ['safe','id-only']) {
    const l=new Loader(),c=new Cell(l,mode);
    const a1=c.bind(A);c.bind(B);const a2=c.bind(A);
    l.complete(a2);l.pump();l.complete(a1,true);l.pump();output[mode]=c.image;
    assert.equal(c.image,mode==='safe'?A.icon:'ERROR');
    l.complete(l.requests[1]);l.pump();finish(l,c);
  }
  transcript.push({case:'same-key',output});
});
test('placeholder is checked BEFORE the replacement result',()=>{
  for(const mode of ['safe','no-clear']) {
    const l=new Loader(),c=new Cell(l,mode);const a=c.bind(A);
    l.complete(a);l.pump();const b=c.bind(B);
    assert.equal(c.image,mode==='safe'?'LOADING':A.icon);
    l.complete(b);l.pump();assert.equal(c.image,B.icon);finish(l,c);
  }
});
test('unbound/closed cell ignores late completion and releases lease',()=>{
  const l=new Loader(),c=new Cell(l);const a=c.bind(A);c.unbind();
  l.complete(a);l.pump();assert.equal(c.image,'EMPTY');l.closed();
});
test('live reorder rebinds both visible cells; index-only accepts old owners',()=>{
  for(const mode of ['safe','index-only']) {
    const l=new Loader(),left=new Cell(l,mode),right=new Cell(l,mode);
    let items=[A,B];const old=[left.bind(items[0],0),right.bind(items[1],1)];
    items=[B,A]; // application refresh and rebind are part of the transaction
    const next=[left.bind(items[0],0),right.bind(items[1],1)];
    next.forEach(r=>l.complete(r));l.pump();old.forEach(r=>l.complete(r));l.pump();
    assert.deepEqual([left.image,right.image],mode==='safe'?[B.icon,A.icon]:[A.icon,B.icon]);
    finish(l,left,right);
  }
});
test('same item changes icon revision: model notification triggers fresh bind',()=>{
  const l=new Loader(),c=new Cell(l);const a=c.bind(A);
  const upgraded={...A,rev:2,icon:'icons/sword-v2'};const v2=c.bind(upgraded);
  l.complete(v2);l.pump();l.complete(a);l.pump();assert.equal(c.image,upgraded.icon);finish(l,c);
});
test('current failure stays error; stale success cannot become fallback',()=>{
  const l=new Loader(),c=new Cell(l);const a=c.bind(A),b=c.bind(B);
  l.complete(b,true);l.pump();assert.equal(c.image,'ERROR');
  l.complete(a);l.pump();assert.equal(c.image,'ERROR');finish(l,c);
});
test('synchronous cache completion is queued; old queued success loses qualification',()=>{
  const l=new Loader(),c=new Cell(l);c.bind(A,0,true);const b=c.bind(B);
  l.pump();assert.equal(c.image,'LOADING');l.complete(b);l.pump();
  assert.equal(c.image,B.icon);finish(l,c);
});
test('late callback keeps old cell object, never writes replacement cell',()=>{
  const l=new Loader(),old=new Cell(l);const a=old.bind(A);old.unbind();
  const replacement=new Cell(l);const b=replacement.bind(B);
  l.complete(b);l.pump();l.complete(a);l.pump();
  assert.equal(old.image,'EMPTY');assert.equal(replacement.image,B.icon);finish(l,old,replacement);
});
console.log(JSON.stringify({runtime:process.version,scope:'serial application model, manual completions',tests:9,transcript},null,2));
