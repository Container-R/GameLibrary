// Original application-state teaching model. No DOM, CSS engine or browser dispatch.
export function initialModel(epoch = 20) {
  return { open: true, epoch,
    slots: { A: { item: 'sword-17', enabled: true, accepts: ['weapon'] },
      B: { item: null, enabled: true, accepts: ['weapon'] },
      C: { item: null, enabled: true, accepts: ['potion'] } },
    items: { 'sword-17': { slot: 'A', version: 5, type: 'weapon' } } };
}

export class DragModel {
  constructor(hooks = {}) {
    this.model = initialModel(); this.active = null; this.nextId = 100;
    this.finishing = false; this.previewOwner = null; this.commits = 0;
    this.cleanups = 0; this.results = []; this.ignoredCallbacks = 0;
    this.hooks = hooks;
  }
  sourceValid(s) {
    const m = this.model, item = m.items[s.itemId];
    return m.open && m.epoch === s.epoch && item?.slot === s.sourceId &&
      item.version === s.sourceVersion && m.slots[s.sourceId]?.item === s.itemId;
  }
  // hit is an injected label, not an elementFromPoint result obtained here.
  slotAt(s, hit, hitEpoch = this.model.epoch) {
    if (hitEpoch !== s.epoch) return null;
    const id = /^(?:label|slot)-([ABC])$/.exec(hit ?? '')?.[1];
    return id && this.model.slots[id] ? id : null;
  }
  rejection(s, targetId) {
    if (!this.sourceValid(s)) return 'source-invalid';
    if (!targetId) return 'no-target';
    if (targetId === s.sourceId) return 'same-slot';
    const target = this.model.slots[targetId];
    if (!target || !target.enabled) return 'target-disabled';
    if (target.item !== null) return 'target-occupied';
    if (!target.accepts.includes(this.model.items[s.itemId].type)) return 'type-rejected';
    return null;
  }
  refresh(hit, hitEpoch) {
    const s = this.active;
    if (!s || s.phase !== 'dragging') return;
    if (!this.sourceValid(s)) return this.finish(s, 'source-invalid');
    const id = this.slotAt(s, hit, hitEpoch);
    s.candidate = this.rejection(s, id) ? null : id;
    s.lastHit = hit;
  }
  finish(s, reason, input = {}) {
    if (this.active !== s || !['starting', 'dragging'].includes(s.phase)) return;
    if (reason === 'up' && s.phase !== 'dragging') return;
    s.phase = 'settling'; this.finishing = true;
    let result = { attemptId: s.id, epoch: s.epoch, status: 'canceled', reason };
    // Trusted synchronous plain-data work: no await, hooks, rendering or getters.
    if (reason === 'up') {
      const targetId = this.slotAt(s, input.hit, input.hitEpoch);
      const failure = this.rejection(s, targetId);
      if (failure) result.reason = failure;
      else {
        const m = this.model, item = m.items[s.itemId];
        const next = { ...m, slots: { ...m.slots,
          [s.sourceId]: { ...m.slots[s.sourceId], item: null },
          [targetId]: { ...m.slots[targetId], item: s.itemId } },
          items: { ...m.items, [s.itemId]: { ...item, slot: targetId, version: item.version + 1 } } };
        this.model = next; this.commits++;
        result = { ...result, status: 'accepted', reason: 'up', targetId };
      }
    }
    s.phase = 'ended'; s.result = result; this.active = null;
    this.results.push(result);
    try { this.cleanup(s); } finally { this.finishing = false; }
    // No old-session cleanup after this callback, which may start another attempt.
    this.hooks.notify?.(this, s);
  }
  cleanup(s) {
    if (s.cleaned) return;
    s.cleaned = true; this.cleanups++;
    if (this.previewOwner === s.id) this.previewOwner = null;
    this.hooks.cleanup?.(this, s); // inject a reentrant application call, not a browser event
  }
  input(e) {
    if (e.type === 'down') {
      if (this.active || this.finishing || !this.model.open ||
          e.pointerType !== 'mouse' || e.button !== 0 || e.buttons !== 1 ||
          e.handle !== 'sword-17') return;
      const item = this.model.items[e.handle];
      if (!item || this.model.slots[item.slot]?.item !== e.handle) return;
      this.active = { id: ++this.nextId, epoch: this.model.epoch, pointerId: e.pointerId,
        itemId: e.handle, sourceId: item.slot, sourceVersion: item.version,
        phase: 'starting', candidate: null, lastPoint: [e.x, e.y] };
      return;
    }
    if (e.type === 'close') {
      this.model = { ...this.model, open: false };
      if (this.active) this.finish(this.active, 'closed');
      return;
    }
    if (e.type === 'reopen') { this.model = initialModel(e.epoch); return; }
    if (e.type === 'disable-B') {
      this.model = { ...this.model, slots: { ...this.model.slots,
        B: { ...this.model.slots.B, enabled: false } } };
      return this.refresh(e.hit);
    }
    if (e.type === 'replace-source') {
      const m = this.model;
      this.model = { ...m, slots: { ...m.slots,
        A: { ...m.slots.A, item: 'sword-18' }, C: { ...m.slots.C, item: 'sword-17' } },
        items: { ...m.items, 'sword-17': { ...m.items['sword-17'], slot: 'C', version: 6 },
          'sword-18': { slot: 'A', version: 1, type: 'weapon' } } };
      return this.refresh(e.hit);
    }
    if (e.type === 'refresh') return this.refresh(e.hit, e.hitEpoch);
    if (e.type === 'old-callback') {
      if (!this.active || this.active.id !== e.attemptId || this.active.epoch !== e.epoch)
        this.ignoredCallbacks++;
      return; // payload deliberately has no effect in this finite example
    }
    const s = this.active;
    if (!s || e.pointerId !== s.pointerId) return;
    if (e.type === 'capture-result' && s.phase === 'starting') {
      if (!e.ok) return this.finish(s, 'capture-failed');
      s.phase = 'dragging'; this.previewOwner = s.id; return;
    }
    if (e.type === 'cancel' || e.type === 'lost') return this.finish(s, e.type);
    if (s.phase !== 'dragging') return;
    if (e.type === 'move') {
      if (e.pointerType !== 'mouse' || e.buttons !== 1) return this.finish(s, 'buttons-changed');
      s.lastPoint = [e.x, e.y]; return this.refresh(e.hit, e.hitEpoch);
    }
    if (e.type === 'up') {
      if (e.pointerType !== 'mouse' || e.button !== 0 || e.buttons !== 0)
        return this.finish(s, 'buttons-changed');
      return this.finish(s, 'up', e);
    }
  }
  snapshot() {
    return { active: this.active ? { attemptId: this.active.id, epoch: this.active.epoch,
      phase: this.active.phase, candidate: this.active.candidate } : null,
      itemSlot: this.model.items['sword-17'].slot,
      slots: Object.fromEntries(Object.entries(this.model.slots).map(([k,v]) => [k,v.item])),
      commits: this.commits, cleanups: this.cleanups, previewOwner: this.previewOwner,
      ignoredCallbacks: this.ignoredCallbacks, results: this.results.slice() };
  }
}
