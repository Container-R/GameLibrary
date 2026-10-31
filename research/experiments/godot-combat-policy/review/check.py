import hashlib,json, pathlib, shutil, subprocess,sys
R=pathlib.Path(__file__).resolve().parent
F=R/'fixture'
(R/'negative-results.json').unlink(missing_ok=True)
def need(c,m):
 if not c: raise RuntimeError(m)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((F/'results/summary.json').read_text())
need(sha(pathlib.Path('/usr/local/bin/godot'))==s['binary_sha256'],'binary')
for n,h in s['source_sha256'].items(): need(sha(F/n)==h,'source '+n)
for mode in ['immediate','staged']:
 for first,second in [('A','B'),('B','A')]:
  name=mode+'-'+first
  lines=(F/'results'/f'{name}.stdout').read_text().splitlines()
  rs=[json.loads(x[len('RESULT_JSON='):]) for x in lines if x.startswith('RESULT_JSON=')]
  ts=[json.loads(x[len('TRACE_JSON='):]) for x in lines if x.startswith('TRACE_JSON=')]
  need(len(rs)==1 and len(ts)==4,'record cardinality')
  r=rs[0]
  need(r['tree_order']==['Begin','A','B','End'],'actual tree child order')
  need(r['trace']==ts and [x['label'] for x in ts]==['Begin',first,second,'End'],'actual callbacks')
  need(len(set(x['frame'] for x in ts))==1,'one frame')
  need([x['priority'] for x in ts]==[-100,0,10,100],'priorities')
  need(all(x['group']==0 for x in ts) and r['root_group']==0,'inherited groups')
  hp={'A':0,'B':0} if mode=='staged' else {'A':int(first=='A'),'B':int(first=='B')}
  need(r['hp']==hp and r['snapshot']=={'A':1,'B':1},'literal hp')
  attacks=[first,second] if mode=='staged' else [first]
  need([x['attacker'] for x in r['intents']]==attacks,'intents')
  need(sorted((x['attacker'],x['target'],x['amount']) for x in r['events'] if x['kind']=='damage')==sorted((a,'B' if a=='A' else 'A',1) for a in attacks),'damage')
  need(sorted(x['actor'] for x in r['events'] if x['kind']=='death')==sorted('B' if a=='A' else 'A' for a in attacks),'death')
  need(len(r['events'])==2*len(attacks),'extra events')
  need(ts[1]['eligible'] is True and ts[2]['eligible'] is (mode=='staged'),'eligibility')
  need([x['hp_before'] for x in ts]==([{'A':1,'B':1}]*4 if mode=='staged' else [{'A':1,'B':1}]*2+[hp]*2),'entry states')
  need((F/'results'/f'{name}.stderr').read_text()=='','stderr')
  need(json.loads((F/'results'/f'{name}.status.json').read_text())['returncode']==0,'status')
observations=[]
for name in ['optimized','spawn-failure','missing-result']:
 d=R/name
 if d.exists(): shutil.rmtree(d)
 shutil.copytree(F,d,ignore=shutil.ignore_patterns('results','.godot'))
 (d/'results').mkdir(); (d/'results/summary.json').write_text('{"old":"PASS"}')
 if name=='spawn-failure':
  # Existing readable nonexecutable contract passes hash step, then actual exec fails.
  p=d/'run.py'; p.write_text(p.read_text().replace('BINARY = Path("/usr/local/bin/godot")','BINARY = ROOT / "contract.md"'))
 if name=='missing-result':
  p=d/'run.py'; p.write_text(p.read_text().replace('BINARY = Path("/usr/local/bin/godot")','BINARY = Path("/usr/bin/true")'))
 cmd=[sys.executable]+(['-O'] if name=='optimized' else [])+[str(d/'run.py')]
 p=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
 (d/'probe.stdout').write_text(p.stdout);(d/'probe.stderr').write_text(p.stderr)
 need(p.returncode!=0 and not (d/'results/summary.json').exists(),'freshness '+name)
 if name=='spawn-failure': need('spawn_error' in json.loads((d/'results/immediate-A.status.json').read_text()),'spawn receipt')
 observations.append({'name':name,'command':cmd,'returncode':p.returncode,'prior_summary_removed':True,'modified_runner':name!='optimized'})
(R/'negative-results.json').write_text(json.dumps(observations,indent=2)+'\n')
print(json.dumps({'status':'PASS','actual_engine_processes':4,'startup_negatives':3,'binary_sha256':s['binary_sha256'],'source_sha256':s['source_sha256']},indent=2))
