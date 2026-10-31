#!/usr/bin/env python3
import hashlib,json,pathlib,subprocess,sys,tempfile
ROOT=pathlib.Path(__file__).resolve().parent
OUT=ROOT/'results';OUT.mkdir(exist_ok=True);(OUT/'summary.json').unlink(missing_ok=True)
if not __debug__:raise SystemExit('Refusing -O')
# Fresh directory per batch preserves any prior database/journal pair after failures.
DBS=pathlib.Path(tempfile.mkdtemp(prefix='databases-',dir=OUT))
def check(ok,msg):
    if not ok:raise RuntimeError(msg)
def decode(x):return x.decode('utf-8',errors='replace') if isinstance(x,bytes) else (x or '')
runs=[]; meta=None

def invoke(mode,db,label,expected=0):
    global meta
    cmd=[sys.executable,str(ROOT/'worker.py'),mode,str(DBS/db)]
    try:p=subprocess.run(cmd,text=True,capture_output=True,timeout=20)
    except subprocess.TimeoutExpired as e:
        (OUT/(label+'.stdout.txt')).write_text(decode(e.stdout));(OUT/(label+'.stderr.txt')).write_text(decode(e.stderr))
        (OUT/(label+'.command.json')).write_text(json.dumps({'command':cmd,'timeout':e.timeout,'returncode':None}));raise
    (OUT/(label+'.stdout.txt')).write_text(p.stdout);(OUT/(label+'.stderr.txt')).write_text(p.stderr)
    command={'command':cmd,'returncode':p.returncode,'expected_exit':expected};(OUT/(label+'.command.json')).write_text(json.dumps(command,indent=2)+'\n')
    check(p.returncode==expected and not p.stderr.strip(),label+' subprocess')
    config=[json.loads(x[7:]) for x in p.stdout.splitlines() if x.startswith('CONFIG=')];check(len(config)==1,label+' config')
    check(config[0]['config']=={'journal_mode':'delete','synchronous':3,'autocommit':-1,'isolation_level':None},label+' pragmas')
    if meta is None:meta=config[0]['metadata']
    check(meta==config[0]['metadata'],label+' runtime identity')
    payload=[json.loads(x[12:]) for x in p.stdout.splitlines() if x.startswith('RESULT_JSON=')]
    marks=[json.loads(x[11:]) for x in p.stdout.splitlines() if x.startswith('CHECKPOINT=')]
    check(len(payload)==(1 if expected==0 else 0),label+' acknowledgement')
    if expected:
        check(len(marks)==1,label+' checkpoint')
        if expected==41:check(marks[0]=={'phase':'before_commit','in_transaction':True,'local_balance':125,'local_receipt':1},'precommit witness')
        if expected==42:check(marks[0]=={'phase':'committed_before_ack','in_transaction':False},'postcommit witness')
    result={'command':command,'config':config[0],'payload':payload,'checkpoints':marks}
    (OUT/(label+'.json')).write_text(json.dumps(result,indent=2)+'\n');runs.append({'label':label,**command})
    return payload[0] if payload else None

def validate(p,balance,has_reward):
    s=p['snapshot']; expected=[['opening',100,'opening',100]]+([['reward-1',25,'quest',125]] if has_reward else [])
    check(s=={'balance':balance,'receipts':expected,'sum_delta':balance,'reward_count':int(has_reward),'integrity':[['ok']]},'exact persistent snapshot')
for db in ['before.db','after.db']:validate(invoke('init',db,'init-'+db),100,False)
invoke('before','before.db','before-exit',41)
validate(invoke('read','before.db','before-reopen'),100,False)
invoke('after','after.db','after-exit',42)
validate(invoke('read','after.db','after-reopen'),125,True)
p=invoke('retry_same','after.db','retry-same');validate(p,125,True);check(p['outcome']=={'outcome':'duplicate','balance_after':125},'same-payload idempotency')
validate(invoke('read','after.db','same-reopen'),125,True)
p=invoke('retry_changed','after.db','retry-changed');validate(p,125,True);check(p['outcome']=={'outcome':'payload_conflict'},'changed-payload conflict')
validate(invoke('read','after.db','changed-reopen'),125,True)
summary={'status':'PASS','metadata':meta,'runs':runs,'source_sha256':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ['worker.py','run.py']},'database_directory':str(DBS),'database_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in DBS.iterdir() if p.is_file()}}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print('PASS four transaction boundary scenarios across ten actual subprocesses')
