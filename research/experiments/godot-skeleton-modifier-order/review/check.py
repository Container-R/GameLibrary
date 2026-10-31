"""Finite independent raw-pose oracle; no author imports or native launches."""
import json,math,hashlib,copy
from pathlib import Path
HERE=Path(__file__).resolve().parent
I=[[1,0,0],[0,1,0],[0,0,1]]
Y=[[0,0,-1],[0,1,0],[1,0,0]]
YM=[[0,0,1],[0,1,0],[-1,0,0]]
def req(v,msg):
 if not v:raise ValueError(msg)
def near(a,b):
 if isinstance(b,list):
  req(type(a)is list and len(a)==len(b),'shape')
  for x,y in zip(a,b):near(x,y)
 else:req(type(a)in(int,float) and math.isfinite(a) and abs(a-b)<=1e-5,'numeric')
def tf(t,b,o):
 near(t['basis'],b);near(t['origin'],o)
 for i in range(3):
  for j in range(3):near(sum(x*y for x,y in zip(t['basis'][i],t['basis'][j])),int(i==j))
def poses(p,pb,cb,cl):
 req(len(p)==2,'bones');tf(p[0]['global'],pb,[0,0,0]);tf(p[0]['local'],pb,[0,0,0]);tf(p[1]['global'],cb,[0,1,0]);tf(p[1]['local'],cl,[0,1,0])
def oracle(d):
 es=d['evaluations'];req(len(es)==2,'evaluations');base=es[0]['before']; mids=[x['id'] for x in base['modifiers']];tids=[x['id'] for x in base['targets']];ids=[base['skeleton_id']]+mids+tids
 req(len(ids)==5 and len(set(ids))==5 and all(type(x)is int and x!=0 for x in ids),'IDs')
 req(d['version']['hash']=='7d41c59c457bd5a245092b4e7eb2d833e3b3f8c3','self hash')
 for k,e in enumerate(es):
  order=[0,1] if k==0 else [1,0];req(type(e['index'])is int and e['index']==k,'index')
  for field in ['before','restored']:
   s=e[field];req(s['skeleton_id']==ids[0] and s['callback_mode']==2 and s['interpolation_mode']==2,'skeleton');tf(s['world'],I,[0,0,0]);poses(s['poses'],I,I,I)
   req(s['children']==[{'id':mids[i],'name':['P','C'][i]} for i in order],'child order')
   req(len(s['bones'])==len(s['targets'])==len(s['modifiers'])==2,'membership')
   for i in range(2):
    b=s['bones'][i];req(b['name']==['P','C'][i] and b['parent']==[-1,0][i],'bone binding');tf(b['rest'],I,[[0,0,0],[0,1,0]][i])
    t=s['targets'][i];req(t['id']==tids[i],'target');tf(t['world'],I,[[10,0,0],[0,1,10]][i])
    m=s['modifiers'][i];req(m['id']==mids[i] and m['bone']==i and m['bone_name']==['P','C'][i] and m['target_id']==tids[i] and m['target_path']==['../../TargetP','../../TargetC'][i],'bindings')
    for key,val in {'relative':False,'active':True,'use_angle_limitation':False,'use_secondary_rotation':True}.items():req(type(m[key])is bool and m[key]==val,'bool settings')
    for key,val in {'forward_axis':4,'primary_rotation_axis':1,'origin_from':0}.items():req(type(m[key])is int and m[key]==val,'enum settings')
    for key,val in {'duration':0,'influence':1,'origin_safe_margin':.1,'interpolation_remaining':0}.items():near(m[key],val)
    near(m['origin_offset'],[0,0,0]);req(type(m['interpolating'])is bool,'diagnostic type')
  expected=[(Y,Y,I),(Y,I,YM)] if k==0 else [(I,I,I),(Y,Y,I)]
  req(len(e['stages'])==2,'stages')
  for j,st in enumerate(e['stages']):
   req(st['kind']=='stage' and st['phase']=='armed' and st['evaluation']==k and st['emitter']==mids[order[j]] and st['bone']==order[j],'emitter');poses(st['poses'],*expected[j])
  final=e['final'];req(final['kind']=='skeleton_updated' and final['phase']=='armed' and final['evaluation']==k,'final');poses(final['poses'],*expected[-1]);near(final['poses'][1]['global']['basis'][2][2],1-k)
 # Exact archived setup chronology is observation, not claimed universal setup count.
 tr=d['trace'];req(len(tr)==17,'trace length');req([(x['kind'],x.get('phase'),x.get('evaluation')) for x in tr[:4]]==[('stage','setup',-1),('stage','setup',-1),('skeleton_updated','setup',-1),('drain_marker','setup',0)],'setup')
 for k,start in [(0,4),(1,11)]:
  seg=tr[start:start+6];req([x['kind'] for x in seg]==['advance_call','advance_return','stage','stage','skeleton_updated','deferred_restored'],'sequence');req(all(x['evaluation']==k for x in seg),'trace indices');req(seg[2:4]==es[k]['stages'] and seg[4]==es[k]['final'] and seg[5]['poses']==es[k]['restored']['poses'],'association')
 req(tr[10]=={'kind':'drain_marker','phase':'reconfigure','evaluation':1},'reconfigure drain')
 return True
if __name__=='__main__':
 p=HERE/'evidence/6703fd88-731a-4879-8a5d-6f2ac968b3e2';r=json.loads((p/'receipt.json').read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
 req(r['status']=='PASS' and [c['name'] for c in r['commands']]==['version','behavior'],'receipt');req(all(c['returncode']==0 and not c['timed_out'] for c in r['commands']),'outcomes')
 for n,h in r['source_sha256'].items():req(sha(HERE/'fixture'/n)==h,'source hash')
 for n,h in r['outputs_sha256'].items():req(sha(p/n)==h,'output hash')
 req(r['binary_sha256']==sha(Path('/usr/local/bin/godot'))=='f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3','binary bytes')
 req((p/'version.stdout').read_text()=='4.6.3.stable.official.7d41c59c4\n','version');req((p/'version.stderr').read_bytes()==(p/'behavior.stderr').read_bytes()==b'','stderr')
 lines=(p/'behavior.stdout').read_text().splitlines();req(sum(s.startswith('RESULT_JSON=') for s in lines)==1,'sole result');req(all(not s or s.startswith('Godot Engine v4.6.3.stable.official.7d41c59c4') or s.startswith('RESULT_JSON=') for s in lines),'stdout envelope');req(not any('ERROR' in s or 'WARNING' in s for s in lines),'diagnostics')
 d=json.loads(next(s[12:] for s in lines if s.startswith('RESULT_JSON=')));req(d==json.loads((p/'behavior.json').read_text()),'raw parsed');oracle(d)
 print(json.dumps({'status':'PASS','invocation_id':r['invocation_id'],'native_behavior_processes':1,'manual_evaluations':2,'version_commands':1,'observed_setup_tagged_events_including_drains':5,'source_sha256':r['source_sha256'],'oracle':'independent literal global/local bases, positions, IDs/settings, trace and restore; no author imports'},indent=2))
