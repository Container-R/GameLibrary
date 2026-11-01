"""Independent observed-layout archive replay; stdlib only, no author imports."""
import sys,json,hashlib,math
from pathlib import Path

def need(x,m):
 if not x:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def eq(a,b):return json.dumps(a,sort_keys=True)==json.dumps(b,sort_keys=True)
def vec(a,b):need(len(a)==3 and all(type(x) in (int,float) and math.isfinite(x) and abs(x-y)<=1e-5 for x,y in zip(a,b)),'vector')
def main(src,out):
 s=Path(src);o=Path(out);r=json.loads((o/'receipt.json').read_text())
 need(r['status']=='PASS' and r['uuid']==o.name,'receipt')
 need(r['source_sha256']==r['source_after']=={n:sha(s/n) for n in r['source_sha256']},'source identity')
 need(r['binary_before']==r['binary_after']=='f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3','binary identity')
 need(len(r['processes'])==2,'process count')
 for p,name in zip(r['processes'],['version','behavior']):
  need(p['name']==name and p['status']=='RETURNED' and type(p['returncode']) is int and p['returncode']==0,'process')
  for field in ['stdout','stderr']:need(sha(o/(name+'.'+field))==p[field+'_sha256'],'stream hash')
  need((o/(name+'.stderr')).read_bytes()==b'','stderr')
 need((o/'version.stdout').read_text().strip()=='4.6.3.stable.official.7d41c59c4','version')
 lines=[x for x in (o/'behavior.stdout').read_text().splitlines() if x]
 need(len(lines)==2 and lines[0]=='Godot Engine v4.6.3.stable.official.7d41c59c4 - https://godotengine.org' and lines[1].startswith('RESULT_JSON='),'raw envelope')
 d=json.loads(lines[1][12:]);need(eq(d,json.loads((o/'behavior.json').read_text())) and sha(o/'behavior.json')==r['parsed_sha256'],'parsed binding')
 ids=d['identities'];need(len({d['root_id'],*[x[k] for x in ids for k in ['agent_id','parent_id']]})==5,'node identities')
 need(d['steps']==17 and len(d['events'])==337,'observed layout')
 events=d['events'];position=[[2,0,2],[2,0,2]];counts=[0,0];targets=[[],[]];finishes=[[],[]];all_snaps=[];lastframe=-1
 calls=['get_next_path_position','is_navigation_finished','is_target_reachable','get_final_position']
 for step in range(1,18):
  group=[e for e in events if e['step']==step];frames={e['frame'] for e in group};need(len(frames)==1 and next(iter(frames))>lastframe,'callback frames');lastframe=next(iter(frames))
  moved=False;snaps={}
  for e in group:
   i=e['agent'];need(type(i) is int and i in [0,1],'agent index');need(e['agent_id']==ids[i]['agent_id'] and e['parent_id']==ids[i]['parent_id'],'event identity')
   if e['kind']=='position_assigned':
    moved=True;need(not finishes[i],'move after terminal');old=position[i][:];vec(e['old'],old)
    n=snaps[i]['next'];dist=math.dist(old,n);f=min(1,.5/dist) if dist else 0;new=[x+(y-x)*f for x,y in zip(old,n)]
    vec(e['next'],n);vec(e['computed'],new);vec(e['position'],new);position[i]=new;counts[i]+=1;need(e['phase']=='movement','move phase')
   else:
    need(not moved and e['phase']=='queries','query after move');vec(e['position'],position[i])
    if e['kind']=='signal':
     if e['signal']=='target_reached':targets[i].append((step,e['frame']));need(i==0 and not finishes[i],'target order')
     if e['signal']=='navigation_finished':finishes[i].append((step,e['frame']));need(i==1 or len(targets[i])==1,'finish order')
    if e['kind']=='after_queries':snaps[i]=e['snapshot'];all_snaps.append(e['snapshot'])
  active=[0,1] if step<=13 else [1]
  need(list(snaps)==active,'active agents')
  for i in active:
   q=[e for e in group if e['agent']==i and e['kind'] in ['call_enter','call_return']]
   need([(e['kind'],e['call']) for e in q]==[(kind,c) for c in calls for kind in ['call_enter','call_return']],'call order')
   row=snaps[i];terminal=step==[13,17][i];need(row['finished'] is terminal and row['reachable'] is (i==0) and row['reached'] is (i==0 and terminal),'state')
   vec(row['final'],[[8,0,2],[10,0,2]][i]);vec(row['next'],q[1]['value']);need(eq(row['finished'],q[3]['value']) and eq(row['reachable'],q[5]['value']),'return association');vec(row['final'],q[7]['value'])
   need(row['step']==step and row['frame']==lastframe,'snapshot frame');vec(row['parent'],[2+.5*min(step-1,[12,16][i]),0,2])
   vec(row['path'][0],[2,0,2]);vec(row['path'][-1],[[8,0,2],[10,0,2]][i]);need(abs(row['distance']-math.dist(row['parent'],[[8,0,2],[22,0,2]][i]))<=1e-5,'distance')
 need(counts==[12,16] and [len(x) for x in targets]==[1,0] and [len(x) for x in finishes]==[1,1],'counts');need(eq(all_snaps,d['snapshots']),'snapshot association')
 vec(position[0],[8,0,2]);vec(position[1],[10,0,2])
 return {'uuid':r['uuid'],'status':'ACCEPTED_OBSERVED_LAYOUT','driver_callbacks':17,'events':337,'moves':counts,'target_counts':[1,0],'finish_counts':[1,1],'terminal_positions':position,'target_steps':targets,'finish_steps':finishes,'scope':'independent finite raw replay; author consumer complements full config/ABI/env/strict JSON checks; not authenticated source or collision motion'}
if __name__=='__main__':print(json.dumps(main(*sys.argv[1:]),indent=2))
