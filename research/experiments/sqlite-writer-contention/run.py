#!/usr/bin/env python3
import base64,hashlib,json,pathlib,queue,subprocess,sys,tempfile,threading
ROOT=pathlib.Path(__file__).resolve().parent
OUT=ROOT/'results';OUT.mkdir(exist_ok=True);(OUT/'summary.json').unlink(missing_ok=True)
if not __debug__:raise SystemExit('Refusing -O')
DBDIR=pathlib.Path(tempfile.mkdtemp(prefix='database-',dir=OUT));DB=DBDIR/'ledger.db'
transcript=[];children=[];meta=None

def check(ok,msg):
    if not ok:raise RuntimeError(msg)
class Child:
    def __init__(self,role):
        self.role=role;self.command=[sys.executable,str(ROOT/'worker.py'),role,str(DB)]
        self.p=subprocess.Popen(self.command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
        self.q=queue.Queue();self.stdout=[];self.stderr=[];self.threads=[];children.append(self)
        def drain(stream,dest,signal):
            for line in stream:
                dest.append(line)
                if signal:self.q.put(line)
            if signal:self.q.put(None)
        for stream,dest,signal in [(self.p.stdout,self.stdout,True),(self.p.stderr,self.stderr,False)]:
            t=threading.Thread(target=drain,args=(stream,dest,signal),daemon=True);t.start();self.threads.append(t)
    def receive(self,prefix):
        line=self.q.get(timeout=5);check(line is not None and line.startswith(prefix),self.role+' expected '+prefix)
        data=json.loads(line[len(prefix):]);transcript.append({'direction':'receive','role':self.role,'data':data});return data
    def config(self):
        global meta
        c=self.receive('CONFIG=');check(c['config']=={'journal_mode':'delete','synchronous':3,'autocommit':-1,'isolation_level':None},'config')
        if meta is None:meta=c['metadata']
        check(c['metadata']==meta,'runtime identity')
    def event(self,phase):
        e=self.receive('EVENT=');check(e['role']==self.role and e['phase']==phase,'phase');return e
    def send(self,command):
        transcript.append({'direction':'send','role':self.role,'command':command});self.p.stdin.write(json.dumps({'command':command})+'\n');self.p.stdin.flush()
    def finish(self):
        check(self.p.wait(timeout=5)==0,'child exit')
        for t in self.threads:t.join(timeout=2)
        check(not self.stderr,'stderr');check(self.q.get(timeout=1) is None,'unexpected extra stdout')
    def save(self):
        (OUT/(self.role+'.stdout.txt')).write_text(''.join(self.stdout));(OUT/(self.role+'.stderr.txt')).write_text(''.join(self.stderr))
        (OUT/(self.role+'.command.json')).write_text(json.dumps({'command':self.command,'returncode':self.p.returncode},indent=2)+'\n')

def snap(data,balance,reward):
    check(data=={'balance':balance,'receipts':[['opening',100,'opening',100]]+([['reward-1',25,'quest',125]] if reward else []),'sum_delta':balance,'reward_count':int(reward),'integrity':[['ok']]},'exact snapshot')
ok=False
try:
    init=Child('init');init.config();snap(init.event('INITIALIZED')['snapshot'],100,False);init.finish()
    a=Child('A');b=Child('B')
    for child in [a,b]:
        child.config();e=child.event('READY');check(e['busy_timeout']==0 and not e['in_transaction'],'ready')
    a.send('APPLY_HOLD');e=a.event('HELD');check(e['in_transaction'],'A holds transaction');snap(e['snapshot'],125,True)
    b.send('TRY_BEGIN');e=b.event('BUSY_OBSERVED');check((e['code'],e['name'],e['at'],e['in_transaction'])==(5,'SQLITE_BUSY','BEGIN IMMEDIATE',False),'real begin busy');snap(e['snapshot'],100,False)
    a.send('COMMIT');check(not a.event('COMMITTED')['in_transaction'],'A committed')
    b.send('RETRY_SAME');e=b.event('DUPLICATE');check(e['outcome']=={'outcome':'duplicate','balance_after':125} and not e['in_transaction'],'retry outcome');snap(e['snapshot'],125,True)
    for child in [a,b]:child.send('CLOSE');check(not child.event('CLOSING')['in_transaction'],'closed transaction');child.finish()
    reader=Child('read');reader.config();snap(reader.event('FINAL')['snapshot'],125,True);reader.finish()
    ok=True
finally:
    for child in children:
        if child.p.poll() is None:
            child.p.terminate()
            try:child.p.wait(timeout=2)
            except subprocess.TimeoutExpired:child.p.kill();child.p.wait(timeout=2)
        for t in child.threads:t.join(timeout=2)
        child.save()
    (OUT/'transcript.json').write_text(json.dumps(transcript,indent=2)+'\n')
if ok:
    data=DB.read_bytes();(OUT/'ledger.db.base64').write_text(base64.encodebytes(data).decode('ascii'))
    summary={'status':'PASS','metadata':meta,'source_sha256':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ['ledger.py','worker.py','run.py']},'database_directory':str(DBDIR),'database':{'filename':'ledger.db','bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'encoded_file':'ledger.db.base64'},'processes':[{'role':c.role,'command':c.command,'returncode':c.p.returncode} for c in children]}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print('PASS deterministic writer handshake; four actual subprocesses')
