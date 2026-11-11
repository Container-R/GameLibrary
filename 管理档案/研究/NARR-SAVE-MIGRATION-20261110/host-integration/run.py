from pathlib import Path
import sqlite3,json,hashlib,subprocess,sys,os,shutil,datetime,platform
HERE=Path(__file__).resolve().parent
RESEARCH=HERE.parent
SDK=Path(os.environ['DOTNET_ROOT'])
def sha(b):return hashlib.sha256(b).hexdigest()
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def connect(db):
 c=sqlite3.connect(db);c.execute('PRAGMA synchronous=FULL');return c
# Package digest covers source/candidate bytes through their SHA256 and all identities/actions.
def migrate(db,p,crash=None):
 digest=sha(canon(p));c=connect(db)
 try:
  c.execute('BEGIN IMMEDIATE')
  prior=c.execute('SELECT digest,result FROM operations WHERE id=?',(p['operation_id'],)).fetchone()
  if prior:
   if prior[0]!=digest:raise ValueError('operation-package-conflict')
   c.rollback();return json.loads(prior[1])
  revision,host_revision,content,save=c.execute('SELECT revision,host_revision,content,save FROM active').fetchone()
  if (revision,host_revision,content,sha(save))!=(p['source_revision'],p['source_host_revision'],p['source_content'],p['source_save']):raise ValueError('stale-source')
  candidate=(Path(p['candidate_path'])).read_bytes()
  if sha(candidate)!=p['candidate_save']:raise ValueError('candidate-bytes-conflict')
  for action in p['actions']:
   payload=canon(action['payload']).decode();old=c.execute('SELECT payload FROM receipts WHERE event=?',(action['event'],)).fetchone()
   if old and old[0]!=payload:raise ValueError('event-payload-conflict')
   if not old:
    c.execute('UPDATE inventory SET amount=amount+?',(action['payload']['quantity'],))
    c.execute('INSERT INTO receipts VALUES(?,?,?)',(action['event'],payload,p['operation_id']))
  result={'operation_id':p['operation_id'],'committed_revision':revision+1,'candidate_save':p['candidate_save']}
  c.execute('UPDATE active SET revision=?,host_revision=?,content=?,save=?',(revision+1,host_revision+1,p['target_content'],candidate))
  c.execute('INSERT INTO operations VALUES(?,?,?)',(p['operation_id'],digest,json.dumps(result)))
  if crash=='before':os._exit(72)
  c.commit()
  if crash=='after':os._exit(73) # No response written, connection closed by process death.
  return result
 except: c.rollback();raise
 finally:c.close()
def state(db):
 with connect(db) as c:
  r,h,content,b=c.execute('SELECT * FROM active').fetchone()
  return dict(revision=r,host_revision=h,content=content,save_sha256=sha(b),inventory=c.execute('SELECT amount FROM inventory').fetchone()[0],receipts=c.execute('SELECT count(*) FROM receipts').fetchone()[0],operations=c.execute('SELECT count(*) FROM operations').fetchone()[0])
def init(db,src):
 with connect(db) as c:
  c.executescript('CREATE TABLE active(revision INTEGER,host_revision INTEGER,content TEXT,save BLOB);CREATE TABLE inventory(amount INTEGER);INSERT INTO inventory VALUES(0);CREATE TABLE receipts(event TEXT PRIMARY KEY,payload TEXT,operation TEXT);CREATE TABLE operations(id TEXT PRIMARY KEY,digest TEXT,result TEXT);')
  c.execute('INSERT INTO active VALUES(7,3,?,?)',(sha((src/'variables-old.story.json').read_bytes()),(src/'old.save.json').read_bytes()))
def main():
 out=HERE/('run-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'));out.mkdir()
 shutil.copy2(__file__,out/'run.py');shutil.copy2(HERE/'Continue.cs',out/'Continue.cs')
 (out/'environment.json').write_text(json.dumps({'platform':platform.platform(),'python':sys.version,'sqlite':sqlite3.sqlite_version,'sdk':'8.0.428','runtime':'8.0.34','ink_commit':'35c63e52f1d36060930dc7ed3cfba38ea224b528','method':'existing direct Roslyn net8 runtime assembly; original csproj not retried'},indent=2))
 native=Path(os.environ['NATIVE_RESULTS_DIR']); old=native/'direct-roslyn-20261111T030108Z'
 shutil.copy2(old/'ink-engine-runtime.dll',out/'ink-engine-runtime.dll')
 refs=sorted((SDK/'packs/Microsoft.NETCore.App.Ref/8.0.34/ref/net8.0').glob('*.dll'))
 cmd=[str(SDK/'dotnet'),str(SDK/'sdk/8.0.428/Roslyn/bincore/csc.dll'),'-nologo','-noconfig','-nostdlib+','-target:exe','-out:'+str(out/'Continue.dll'),'-r:'+str(out/'ink-engine-runtime.dll')]+['-r:'+str(f) for f in refs]+[str(out/'Continue.cs')]
 (out/'build-command.json').write_text(json.dumps(cmd,indent=2));p=subprocess.run(cmd,capture_output=True,text=True);(out/'build.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stdout+p.stderr
 (out/'Continue.runtimeconfig.json').write_text(json.dumps({'runtimeOptions':{'tfm':'net8.0','framework':{'name':'Microsoft.NETCore.App','version':'8.0.34'}}}))
 log=[]
 for branch,dirname,score in [('true','030108',10),('false','025948',0)]:
  src=native/f'direct-roslyn-20261111T{dirname}Z'
  case=out/branch;case.mkdir();inp=case/'inputs';inp.mkdir()
  for name in ['candidate.save.json','old.save.json','variables-old.story.json','variables-new.story.json']:shutil.copy2(src/'artifacts'/name,inp/name)
  shutil.copy2(src/'inputs/mapping.json',inp/'mapping.json')
  package={'operation_id':'lineage-A:migrate-v1','lineage':'lineage-A','source_revision':7,'source_host_revision':3,'source_content':sha((inp/'variables-old.story.json').read_bytes()),'target_content':sha((inp/'variables-new.story.json').read_bytes()),'mapping':sha((inp/'mapping.json').read_bytes()),'runtime_assembly':sha((out/'ink-engine-runtime.dll').read_bytes()),'ink_commit':'35c63e52f1d36060930dc7ed3cfba38ea224b528','source_save':sha((inp/'old.save.json').read_bytes()),'candidate_save':sha((inp/'candidate.save.json').read_bytes()),'candidate_path':str(inp/'candidate.save.json'),'actions':[{'event':'lineage-A:fixture-compensation:1','payload':{'quantity':10,'kind':'synthetic-coin','rule':'explicit-test-compensation-v1'}}]}
  pkg=case/'package.json';pkg.write_bytes(canon(package));(case/'package.sha256').write_text(sha(canon(package))+'\n')
  for route in ['bridge','road']:
   db=case/(route+'.sqlite');init(db,inp);initial=state(db)
   # Both before-COMMIT rollback and lost acknowledgement use separate real processes.
   for fault,exitcode in [('before',72),('after',73)]:
    cmd=[sys.executable,str(out/'run.py'),'--worker',str(db),str(pkg),fault]
    (case/(route+'-'+fault+'-command.json')).write_text(json.dumps(cmd));p=subprocess.run(cmd,capture_output=True,text=True)
    (case/(route+'-'+fault+'-process.json')).write_text(json.dumps({'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr}));assert p.returncode==exitcode
    if fault=='before':assert state(db)==initial
   committed=state(db);assert committed['revision']==8 and committed['inventory']==10 and committed['operations']==1 and committed['receipts']==1 and committed['save_sha256']==package['candidate_save']
   first=migrate(db,package);assert state(db)==committed
   # Fetch the active bytes from SQLite, not from the original candidate path.
   with connect(db) as c: stored=c.execute('SELECT save FROM active').fetchone()[0]
   save=case/(route+'-db-loaded.save.json');save.write_bytes(stored)
   advanced=case/(route+'-advanced.save.json')
   cmd=[str(SDK/'dotnet'),str(out/'Continue.dll'),str(inp/'variables-new.story.json'),str(save),route+'_route',str(advanced),str(score)]
   (case/(route+'-native-command.json')).write_text(json.dumps(cmd));p=subprocess.run(cmd,capture_output=True,text=True)
   (case/(route+'-native.stdout.json')).write_text(p.stdout);(case/(route+'-native.stderr.txt')).write_text(p.stderr);assert p.returncode==0,p.stderr
   with connect(db) as c:
    q=c.execute('UPDATE active SET revision=9,host_revision=5,save=? WHERE revision=8 AND host_revision=4',(advanced.read_bytes(),));assert q.rowcount==1
   progressed=state(db);assert progressed['save_sha256']!=committed['save_sha256']
   repeated=migrate(db,package);assert repeated==first and state(db)==progressed
   conflicts=[]
   for change in [{'mapping':'changed-mapping'}, {'actions':[{'event':'other','payload':{'quantity':999}}]}, {'operation_id':'new-operation'}]:
    try:migrate(db,dict(package,**change));raise AssertionError('Expected rejection')
    except ValueError as e:conflicts.append(str(e))
    assert state(db)==progressed
   assert conflicts==['operation-package-conflict','operation-package-conflict','stale-source']
   log.append({'branch':branch,'route':route,'initial':initial,'committed':committed,'progressed':progressed,'retry_result':repeated,'conflicts':conflicts,'native':json.loads(p.stdout),'checks':'passed'})
 (out/'results.json').write_text(json.dumps(log,indent=2))
 (out/'sha256.txt').write_text(''.join(sha(f.read_bytes())+'  '+str(f.relative_to(out))+'\n' for f in sorted(out.rglob('*')) if f.is_file()))
 print(str(out));print('PASS: 2 source branches x 2 routes; rollback/lost acknowledgement/advance/retry/conflicts')
if __name__=='__main__':
 if len(sys.argv)>1 and sys.argv[1]=='--worker':migrate(sys.argv[2],json.loads(Path(sys.argv[3]).read_bytes()),sys.argv[4])
 else:main()
