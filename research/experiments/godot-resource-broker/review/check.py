import sys,json,hashlib
from pathlib import Path
if sys.flags.optimize: raise RuntimeError('assertions required')
p=Path(__file__).resolve().parent/'fixture';o=p/'results'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((o/'summary.json').read_text());v=json.loads((o/'invocation.json').read_text())
assert s['status']==v['status']=='PASS' and s['invocation_id']==v['invocation_id']
assert s['engine_processes']==v['engine_spawn_attempts']==2
assert h(Path(s['engine_path']))==s['binary_sha256']
assert all(h(p/n)==x for n,x in s['source_sha256'].items())
for name,modes,same in [('reuse-then-deep',[1,3],True),('deep-then-reuse',[3,1],False)]:
 lines=(o/(name+'.stdout.txt')).read_text().splitlines()
 calls=[json.loads(x.split('=',1)[1]) for x in lines if x.startswith('CALL_JSON=')]
 records=[json.loads(x.split('=',1)[1]) for x in lines if x.startswith('RESULT_JSON=')]
 assert len(records)==1
 r=records[0];assert r['trace']==calls
 assert [r['first_mode'],r['second_mode']]==modes and r['case']==name
 polls=[x for x in calls if x.get('stage')=='first-poll']
 assert len(polls)==r['frames'] and polls[-1]['value']==3 and all(x['value']==1 for x in polls[:-1])
 assert calls[0]=={'op':'request','number':1,'mode':modes[0],'return':0}
 tail=calls[1+len(polls):]
 assert len(tail)==6
 assert tail[0]=={'op':'request','number':2,'mode':modes[1],'return':0}
 assert tail[1]=={'op':'status','stage':'after-second-request','value':3}
 assert tail[2]=={'op':'get','number':1,'resource':r['result1']}
 assert tail[3]=={'op':'status','stage':'after-first-get','value':3}
 assert tail[4]=={'op':'get','number':2,'resource':r['result2']}
 assert tail[5]=={'op':'status','stage':'after-second-get','value':0}
 assert r['request_count']==r['get_count']==2 and r['final_status']==0 and r['use_sub_threads'] is False
 for k in ['initial','active_after','result1','result2']:
  d=r[k];assert type(d['id']) is int and d['id']!=0
  assert d['colors']==[[1,0,0,1],[1,1,1,1]] and d['offsets']==[0,1] and d['type']=='Gradient'
 assert r['initial']==r['active_after'] and r['result1']==r['result2']
 assert (r['initial']['id']==r['result1']['id'])==same
 disk=json.loads((o/(name+'.disk.json')).read_text())
 assert disk['before']==disk['after']=={n:h(p/n) for n in ['project.godot','main.gd','gradient.tres']}
 assert json.loads((o/(name+'.command.json')).read_text())['returncode']==0
 assert not (o/(name+'.stderr.txt')).read_text()
 print(name,'independent literal raw trace/identity/state/disk PASS')
