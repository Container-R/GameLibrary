"""Independent bounded model QA. No sockets, engine, physics, real timing or third-party code."""
from pathlib import Path
from fractions import Fraction as F
import random, hashlib, json, types, sys, argparse
ROOT=Path(__file__).resolve().parents[1]

def load(rel, mutation=None):
    p=ROOT/rel; source=p.read_text()
    if mutation:
        old,new=mutation
        assert old in source
        source=source.replace(old,new)
    name='qa_model_'+str(len(sys.modules));m=types.ModuleType(name);sys.modules[name]=m
    exec(compile(source,str(p),'exec'),m.__dict__)
    return m

def prediction(m, seed):
    rng=random.Random(seed); c=m.Client(history_limit=128);s=m.Server()
    axes=[rng.choice((-1,0,1)) for _ in range(96)]
    commands=[c.issue(a) for a in axes]
    snapshots=[]; authority_offset=0; window_rejects=0
    initial_effects=list(c.effects)
    def accept(snapshot):
        before=(c.last_tick,c.ack,c.x,list(c.pending),list(c.effects))
        stale=snapshot.tick<=c.last_tick
        result=c.reconcile(snapshot)
        if stale:
            assert result is False
            assert (c.last_tick,c.ack,c.x,list(c.pending),list(c.effects))==before
        else:
            assert c.x==snapshot.x+sum(axes[snapshot.ack:]), ('client replay',seed,c.x,snapshot.x+sum(axes[snapshot.ack:]))
            assert [x.seq for x in c.pending]==list(range(c.ack+1,97))
        assert list(c.effects)==initial_effects, ('replayed effects',seed)
    def step():
        snap=s.step();snapshots.append(snap)
        assert s.x==sum(axes[:s.ack])+authority_offset,('server prefix',seed,s.ack,s.x)
        assert 0<=s.ack<=min(s.tick,96), ('ack skipped prefix/rate bound',seed,s.tick,s.ack)
        assert len(s.pending)<=32
    # Finite adversarial phase: independent delivery loss, duplicates, disorder,
    # beyond-window commands, and stale snapshot re-delivery.
    for _ in range(180):
        # Inject an abstract authoritative correction, not simulated physics.
        if rng.random()<.1:
            kick=rng.randrange(-5,6); authority_offset+=kick; s.x+=kick
        for _ in range(rng.randrange(8)):
            command=rng.choice(commands)
            if rng.random()<.25: continue
            if command.seq>s.ack+32: window_rejects+=1
            s.receive(command)
            if rng.random()<.3:s.receive(command)
        step()
        if rng.random()<.7: accept(rng.choice(snapshots))
    # Explicit eventual-delivery suffix, NOT a probabilistic reliability claim:
    # every still-unacknowledged command is retransmitted every tick. Server's
    # bounded window may reject future entries; repeated later sends recover them.
    for _ in range(96):
        batch=commands[s.ack:];rng.shuffle(batch)
        for command in batch:s.receive(command)
        step()
        if s.ack==96:break
    assert s.ack==96,('eventual delivery',seed,s.ack)
    accept(snapshots[-1])
    for snapshot in rng.sample(snapshots,min(10,len(snapshots))):accept(snapshot)
    assert c.pending==[] and c.x==s.x==sum(axes)+authority_offset
    return window_rejects

def fixed(m, seed):
    rng=random.Random(seed)
    inputs={i:rng.randrange(-3,4) for i in range(400)}
    # Independent integer clock quantum 1/600 sec; generated partition total is
    # shared by second partition; exact fractions exclude numerical integration.
    parts=[rng.randrange(0,41) for _ in range(100)]
    r=m.Runner(inputs); elapsed=F(0)
    def frame(t,b):
        nonlocal elapsed
        old=r.tick;elapsed+=t
        steps,alpha,view=r.frame(t,b)
        assert 0<=steps<=b and r.tick-old==steps
        assert r.tick+r.accumulator==elapsed*60,('lost time debt',seed)
        assert r.position==sum(inputs.get(i,0) for i in range(r.tick)),('state',seed)
        assert r.events==[(i,inputs[i]) for i in range(r.tick) if inputs.get(i,0)],('events',seed)
        assert 0<=alpha<=1
        assert min(r.previous,r.position)<=view<=max(r.previous,r.position)
    for q in parts:frame(F(q,600),rng.randrange(1,9))
    while r.accumulator>=1:frame(F(0),rng.randrange(1,9))
    # Same canonical tick-input stream + same elapsed, different partition/budget.
    other=m.Runner(inputs)
    for _ in range(sum(parts)):other.frame(F(1,600),1)
    assert (r.tick,r.accumulator,r.position,r.events)==(other.tick,other.accumulator,other.position,other.events)
    return r.tick

def main():
    global ROOT
    if sys.flags.optimize:
        raise SystemExit('Refusing optimized Python: assertions are required for QA')
    parser=argparse.ArgumentParser()
    parser.add_argument('--model-root', type=Path, default=ROOT)
    ROOT=parser.parse_args().model_root.resolve()
    paths={'prediction':'client-prediction/test_prediction.py','fixed':'fixed-step/test_fixed_step.py'}
    output={'scope':'Pure discrete Python models; deterministic schedules; no engine/network claims',
            'seeds':list(range(200)), 'model_sha256':{k:hashlib.sha256((ROOT/v).read_bytes()).hexdigest() for k,v in paths.items()}}
    p=load(paths['prediction']); f=load(paths['fixed'])
    output['prediction']={'schedules_passed':200,'commands_per_schedule':96,'beyond_window_attempts':sum(prediction(p,s) for s in range(200))}
    output['fixed']={'schedules_passed':200,'total_drained_ticks':sum(fixed(f,s) for s in range(200))}
    mutants=[('prediction_reemit',paths['prediction'],prediction,('        # Replaying simulation never emits one-shot presentation effects.',"        self.effects.extend((c.epoch,c.seq,'step') for c in self.pending)")),
             ('prediction_skip_gap',paths['prediction'],prediction,('self.pending.pop(self.ack + 1, None)','self.pending.pop(max(self.pending), None) if self.pending else None')),
             ('fixed_discard_backlog',paths['fixed'],fixed,('        # Keep backlog;', '        self.accumulator %= 1\n        # Keep backlog;')),
             ('fixed_double_effect',paths['fixed'],fixed,('self.events.append((self.tick, self.inputs[self.tick]))','self.events.extend([(self.tick, self.inputs[self.tick])]*2)'))]
    output['mutations']={}
    for name,path,check,mutation in mutants:
        try:check(load(path,mutation),0)
        except AssertionError as e:output['mutations'][name]={'detected':True,'evidence':str(e)}
        else:output['mutations'][name]={'detected':False}
    assert all(x['detected'] for x in output['mutations'].values())
    print(json.dumps(output,indent=2))
if __name__=='__main__':main()
