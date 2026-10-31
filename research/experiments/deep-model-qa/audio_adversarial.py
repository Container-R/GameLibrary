"""Independent bounded lifecycle probe; pure fake API, no middleware."""
import sys, random, json, importlib.util, hashlib
from pathlib import Path
if sys.flags.optimize:raise SystemExit('Assertions required')
p=Path(__file__).resolve().parents[1]/'audio-lifecycle/model.py'
source_hash=hashlib.sha256(p.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('audio_probe_model',p);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
class Port(m.FakePort):
    def __init__(self):super().__init__();self.results=[]
    def emit(self,*args):
        result=super().emit(*args);self.results.append((args,result));return result
count=0
for seed in range(200):
    rng=random.Random(seed);p=Port();a=m.Adapter(p);receipts=[];tickets=[];serial=0
    def check():
        released=set();started=set();latest={}
        for call,ok in p.results:
            op,g,h,*args=call
            assert (g,h) in receipts,('unknown ownership',seed,call)
            if op=='mode':
                assert h not in released
                if ok:latest[h]=args[1]
            elif op=='start':
                assert h not in released and h not in started
                assert h in latest,('start without successful parameter',seed,call)
                started.add(h)
            elif op=='stop':assert h in started and h not in released
            elif op=='release':
                assert h not in released
                released.add(h)
        if a.handle is not None:
            assert a.handle not in released
            assert a.submitted is None or a.submitted==latest.get(a.handle)
        if a.state=='Active':assert a.handle in started
    for step in range(150):
        op=rng.randrange(9)
        if op==0 and a.state=='Stopped':a.begin(rng.choice(['Explore','Combat']))
        elif op==1 and a.generation:
            g=rng.randint(1,a.generation);serial+=1;h=f'h{serial}';receipts.append((g,h));a.ready(g,h)
        elif op==2:a.exit()
        elif op==3 and a.state in ('Starting','Active'):
            p.fail_next_mode=rng.choice([True,False]);tickets.append(a.intent(rng.choice(['Explore','Tension','Combat'])))
        elif op==4 and tickets:a.retry(rng.choice(tickets))
        elif op==5:a.invalidate_external_write()
        elif op==6 and receipts:
            g,h=rng.choice(receipts)
            if h in a.started:a.outcome(g,h,rng.choice(['started','start_failed','stopped']))
        elif op==7 and receipts:
            g,h=rng.choice(receipts);a.ready(g,h)
        elif op==8 and a.state in ('Starting','Active'):
            tickets.append(m.Ticket(a.generation,a.revision))
        check()
    a.exit();check()
    assert {h for g,h in receipts}=={call[2] for call,ok in p.results if call[0]=='release'},('unreleased after final exit',seed)
    count+=len(p.calls)
print(json.dumps({'seed_range_inclusive':[0,199],'model_sha256':source_hash,'schedules':200,'actions_per_schedule':150,'calls_checked':count,'all_passed':True,'scope':'Pure fake calls; trusted inputs and unique handles; final exit imposed; no liveness guarantee'},indent=2))
