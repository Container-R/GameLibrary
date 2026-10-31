import sys,json,hashlib
from pathlib import Path
if sys.flags.optimize: raise RuntimeError('requires assertions')
root=Path(__file__).resolve().parent/'fixture';out=root/'results'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((out/'summary.json').read_text());inv=json.loads((out/'invocation.json').read_text())
assert s['status']==inv['status']=='PASS' and s['invocation_id']==inv['invocation_id']
assert s['engine_processes']==inv['engine_processes_started']==2
assert h(Path(s['engine_path']))==s['binary_sha256']
assert all(h(root/n)==v for n,v in s['source_sha256'].items())
for label,mode,shared,active in [('ignore',0,True,[0,0,1,1]),('ignore-deep',3,False,[1,0,0,1])]:
 lines=(out/(label+'.stdout.txt')).read_text().splitlines()
 records=[json.loads(x[12:]) for x in lines if x.startswith('RESULT_JSON=')]
 req=[json.loads(x[13:]) for x in lines if x.startswith('REQUEST_JSON=')]
 assert len(records)==len(req)==1
 r=records[0];b=r['before'];a=r['after'];i=r['initial']
 assert r['case']==label and r['mode']==mode and req[0]['return']==0
 assert req[0]['initial']==i and i['point_count']==2 and i['color']==[1,0,0,1]
 assert b['active_color']==b['candidate_color']==[1,0,0,1]
 assert a['active_color']==a['held_gradient_color']==active
 assert a['candidate_color']==[0,0,1,1]
 for k in ['active_root_id','candidate_root_id','active_gradient_id','candidate_gradient_id']:
  assert type(b[k]) is int and b[k]!=0 and a[k]==b[k]
 assert b['active_root_id']!=b['candidate_root_id']
 assert (b['active_gradient_id']==b['candidate_gradient_id'])==shared
 assert i['root_id']==b['active_root_id']==r['initial_active_id']
 assert i['gradient_id']==b['active_gradient_id']
 assert r['statuses'][-1]==3 and all(x==1 for x in r['statuses'][:-1])
 assert r['frames']==len(r['statuses']) and r['get_count']==r['request_count']==1 and r['use_sub_threads'] is False
 disk=json.loads((out/(label+'.disk.json')).read_text())
 assert disk['before']==disk['after']=={n:h(root/n) for n in ['project.godot','main.gd','gradient.tres','candidate.tres']}
 assert json.loads((out/(label+'.command.json')).read_text())['returncode']==0
 assert not (out/(label+'.stderr.txt')).read_text()
 print(label, 'literal alias/color/identity/disk oracle PASS',r['statuses'])
print('PASS independent raw checks; no author code imports')
