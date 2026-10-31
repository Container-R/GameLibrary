#!/usr/bin/env python3
import hashlib,json,os,pathlib,subprocess,tempfile,sys,platform
if not __debug__: raise SystemExit('Refusing -O')
ROOT=pathlib.Path(__file__).resolve().parent
OUT=ROOT/'results'; OUT.mkdir(exist_ok=True)
(OUT/'summary.json').unlink(missing_ok=True)
ENGINE=pathlib.Path('/usr/local/bin/godot')
CASES=['seek_cross','advance_cross','seek_exact','seek_exact_update_only','seek_two_cross','advance_two_cross']
def check(ok,msg):
    if not ok: raise RuntimeError(msg)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args,label):
    with tempfile.TemporaryDirectory(prefix='animation-env-') as t:
        env=dict(os.environ,HOME=t,XDG_CACHE_HOME=t+'/cache',XDG_CONFIG_HOME=t+'/config',XDG_DATA_HOME=t+'/data')
        for name in ('cache','config','data'): pathlib.Path(t,name).mkdir()
        cmd=[str(ENGINE),*args]
        r=subprocess.run(cmd,env=env,text=True,capture_output=True,timeout=30)
        (OUT/(label+'.stdout.txt')).write_text(r.stdout); (OUT/(label+'.stderr.txt')).write_text(r.stderr)
        (OUT/(label+'.command.json')).write_text(json.dumps({'command':cmd,'returncode':r.returncode,'isolation':'fresh temporary HOME/XDG_CACHE_HOME/XDG_CONFIG_HOME/XDG_DATA_HOME'},indent=2))
        check(r.returncode==0,label+' exit'); check(not r.stderr.strip(),label+' unexpected stderr')
        return r.stdout
version=run(['--headless','--version'],'version').strip()
check(version=='4.6.3.stable.official.7d41c59c4','version mismatch')
results=[]
for case in CASES:
    output=run(['--headless','--path',str(ROOT),'--',case],case)
    traces=[json.loads(x[6:]) for x in output.splitlines() if x.startswith('TRACE ')]
    config=[json.loads(x[7:]) for x in output.splitlines() if x.startswith('CONFIG ')]
    check(len(config)==1,'config count'); cfg=config[0]
    check((cfg['process_mode'],cfg['method_mode'],cfg['loop'],cfg['length'],cfg['key_time'])==(2,1,0,1,0.25 if 'two' in case else 0.5),'configuration')
    check(cfg['key_value']=={'method':'marker','args':['A'] if 'two' in case else []} and cfg['method_path']=='.' and cfg['value_path']=='.:sample','track declaration')
    check(traces[0]['kind']=='initialized' and traces[0]['hits']==0 and traces[0]['finishes']==0 and abs(traces[0]['sample'])<1e-6,'initial')
    after=[x for x in traces if x['kind']=='after']
    expected_hits=0 if case=='seek_exact_update_only' else (2 if case=='advance_two_cross' else 1)
    check(len(after)==(2 if case.endswith('cross') else 1),'after count')
    first=after[0]; target=0.75 if case.endswith('cross') else 0.5
    check(abs(first['sample']-target)<1e-6 and abs(first['position']-target)<1e-6,'first sampling')
    check(first['hits']==expected_hits and first['finishes']==0,'first event outcome')
    if len(after)==2:
        last=after[-1]
        check(abs(last['sample']-1)<1e-6 and abs(last['position']-1)<1e-6,'end sampling')
        check(last['hits']==(2 if case in ('seek_cross','seek_two_cross') else expected_hits) and last['finishes']==(1 if case in ('advance_cross','advance_two_cross') else 0),'end event outcome')
    check(sum(t['kind']=='method' for t in traces)==(2 if case in ('seek_cross','seek_two_cross') else expected_hits),'actual method trace')
    check(sum(t['kind']=='finished' for t in traces)==(1 if case in ('advance_cross','advance_two_cross') else 0),'actual signal trace')
    expected_labels=[] if case=='seek_exact_update_only' else (['A','B'] if case=='advance_two_cross' else (['B','B'] if case=='seek_two_cross' else (['single','single'] if case=='seek_cross' else ['single'])))
    check(traces[-1]['labels']==expected_labels,'delivered label sequence')
    expected_keys=[{'time':0.25,'value':{'method':'marker','args':['A']}},{'time':0.6,'value':{'method':'marker','args':['B']}}] if 'two' in case else [{'time':0.5,'value':{'method':'marker','args':[]}}]
    check(cfg['keys']==expected_keys,'declared keys')
    payloads=[json.loads(x.removeprefix('RESULT_JSON=')) for x in output.splitlines() if x.startswith('RESULT_JSON=')]
    check(len(payloads)==1 and payloads[0]=={'case':case,'config':cfg,'traces':traces},'payload and trace consistency')
    (OUT/(case+'.json')).write_text(json.dumps(payloads[0],indent=2)+'\n')
    results.append({'case':case,'command':[str(ENGINE),'--headless','--path',str(ROOT),'--',case],'exit_code':0,'checks':'passed'})
summary={'version':version,'binary_sha256':sha(ENGINE),'source_sha256':{n:sha(ROOT/n) for n in ['main.gd','main.tscn','project.godot','run.py']},'runs':results,'platform':platform.platform(),'python':platform.python_version(),'status':'PASS'}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print('PASS 6 fresh-process cases; source/binary hashes and raw logs retained')
