import importlib.util,json,os,pathlib,subprocess,sys,hashlib
base=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('fixture',base/'fixture-v2.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
out=base/'probe-v2';out.mkdir(exist_ok=False)
results={}
for fault in ['EIO','ENOSPC']:
    store=out/fault;m.init(store)
    first=m.run_child(store,'save','B','A',fault=fault,log=out/(fault+'-first.jsonl'))
    before=m.snapshot(store)
    retry=m.run_child(store,'save','B','A',log=out/(fault+'-retry.jsonl'))
    after=m.snapshot(store)
    ops=[json.loads(s)['op'] for s in (out/(fault+'-retry.jsonl')).read_text().splitlines()]
    expected='observed_active' if fault=='EIO' else 'candidate_exists'
    results[fault]={'first':first,'retry':retry,'disk_unchanged':before==after,'snapshot':after,'retry_ops':ops,'passed':first['exit_code']==2 and retry['exit_code']==3 and retry['result']['status']==expected and before==after and all(op=='read' for op in ops)}
for name,flags,env in [('dash-O',['-O'],os.environ.copy()),('PYTHONOPTIMIZE',[],{**os.environ,'PYTHONOPTIMIZE':'1'})]:
    dest=out/name;cmd=[sys.executable,*flags,str(base/'fixture-v2.py'),'suite',str(dest)]
    r=subprocess.run(cmd,capture_output=True,text=True,env=env)
    results[name]={'command':cmd,'environment_override':{'PYTHONOPTIMIZE':'1'} if name=='PYTHONOPTIMIZE' else {},'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'output_exists':dest.exists(),'passed':r.returncode==4 and not dest.exists()}
results['metadata']={'fixture_sha256':hashlib.sha256((base/'fixture-v2.py').read_bytes()).hexdigest(),'revision_plan_sha256':hashlib.sha256((base/'revision-plan-v2.md').read_bytes()).hexdigest(),'probe_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()}
(out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps({k:v['passed'] for k,v in results.items() if 'passed'in v}))
sys.exit(0 if all(v['passed'] for v in results.values() if 'passed'in v) else 1)
