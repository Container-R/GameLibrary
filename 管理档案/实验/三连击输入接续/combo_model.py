"""Original finite application model; no engine calls."""
import json

class Combo:
    def __init__(self):
        self.stage=0; self.start=0; self.generation=0; self.attack_id=0
        self.pending=None; self.seen=set(); self.consumed=[]; self.starts=[]
        self.effects=set(); self.last=-1
    def enter(self,t,stage,request):
        self.stage=stage; self.start=t; self.attack_id+=1
        self.starts.append([t,stage,request]); self.consumed.append(request)
    def tick(self,t,requests=(),interrupt=False):
        if t != self.last+1: raise ValueError('ticks must be contiguous')
        self.last=t
        if interrupt:
            self.generation+=1; self.stage=0; self.pending=None
            self.seen.update(requests)
            return
        if self.pending and t>=self.pending[1]: self.pending=None
        if self.stage and t-self.start>=6:
            self.stage=0; self.pending=None
        for request in requests:
            if request in self.seen: continue
            self.seen.add(request)
            if self.stage==0: self.enter(t,1,request)
            elif self.stage<3 and self.pending is None:
                self.pending=(request,t+2)
        if self.stage in (1,2) and 3<=t-self.start<5 and self.pending:
            request,_=self.pending; self.pending=None
            self.enter(t,self.stage+1,request)
    def notify(self,generation,attack_id,marker):
        if self.stage==0 or (generation,attack_id)!=(self.generation,self.attack_id):
            return False
        key=(generation,attack_id,marker)
        if key in self.effects: return False
        self.effects.add(key)
        return True

def run(inputs,interrupts=(),trace=()):
    c=Combo()
    for t in range(13):
        c.tick(t,inputs.get(t,()),t in interrupts)
        if t==2:
            for marker in trace: c.notify(c.generation,c.attack_id,marker)
        if t==4:
            c.notify(0,1,'stale'); c.notify(0,1,'stale')
    return c

def check(ok,message):
    if not ok: raise RuntimeError(message)

if __name__=='__main__':
    expected=[[0,1,'A'],[3,2,'B'],[6,3,'C']]
    # Labels copied from prior finite native outputs, not a new engine run.
    traces={'advance':['early','late'],'deferred_seek':[],
            'immediate_seek':['late'],'update_only':[]}
    results={}
    for name,trace in traces.items():
        c=run({0:['A'],2:['B'],5:['C']},trace=trace)
        check(c.starts==expected and c.consumed==['A','B','C'] and c.stage==0,name)
        results[name]=c.starts
    for name,inputs in [('expired',{0:['A'],1:['B']}),('window_closed',{0:['A'],5:['B']})]:
        c=run(inputs); check(c.starts==[[0,1,'A']],name); results[name]=c.starts
    c=run({0:['A'],2:['B'],3:['X'],4:['D']},interrupts={3})
    check(c.starts==[[0,1,'A'],[4,1,'D']] and c.generation==1,'interrupt')
    check((0,1,'stale') not in c.effects,'stale effect')
    results['interrupt']=c.starts
    c=run({0:['A'],2:['B'],3:['B']})
    check(c.starts==[[0,1,'A'],[3,2,'B']] and c.consumed==['A','B'],'duplicate')
    results['duplicate']=c.starts
    c=Combo(); c.tick(0,['A']);
    check(c.notify(0,1,'hit') and not c.notify(0,1,'hit'),'effect dedup')
    check(c.consumed==['A'],'effect cannot consume')
    print(json.dumps({'scope':'original application model, no engine execution','results':results},ensure_ascii=False,indent=2))
