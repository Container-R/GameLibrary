import base64, hashlib, json, pathlib, sys
root=pathlib.Path(__file__).resolve().parent
out=pathlib.Path(json.loads((root/'run.stdout').read_text())['output'])
def req(ok, msg):
    if not ok: raise RuntimeError(msg)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((out/'summary.json').read_text())
req(s['status']=='PASS' and s['invocation_id']==out.name,'terminal')
req(len(s['processes'])==2 and all(x['exit_code']==0 and x['timed_out'] is False for x in s['processes']),'processes')
for name,h in s['source_sha256'].items(): req(sha(root/'fixture'/name)==h,'source '+name)
req(sha(pathlib.Path(s['executable']))==s['executable_sha256'],'interpreter')
for name,h in s['outputs_sha256'].items(): req(sha(out/name)==h,'output '+name)
a=[json.loads(x) for x in (out/'scenario.stdout').read_text().splitlines()]
req([x['kind'] for x in a]==['config','config','reader_held','writer_applied','commit_busy','writer_after_busy','reader_after_busy','reader_released','writer_committed','reader_new_view','writer_sql_trace','scenario_pass'],'sequence')
for x in a[:2]: req(x['values']=={'journal_mode':'delete','synchronous':3,'busy_timeout':0},'config')
opening=[['opening',100,100]]; final=opening+[['reward-1',25,125]]
for i,b,rows,active in [(2,100,opening,True),(3,125,final,True),(5,125,final,True),(6,100,opening,True),(8,125,final,False),(9,125,final,False)]:
    req(a[i]['snapshot']=={'balance':b,'receipts':rows,'in_transaction':active},'snapshot '+str(i))
req(a[4]['code']==5 and a[4]['name']=='SQLITE_BUSY' and a[4]['in_transaction'] is True,'busy')
req(a[7]['in_transaction'] is False,'release')
nonselect=[q for q in a[10]['statements'] if not q.startswith('SELECT ')]
req(nonselect==['BEGIN IMMEDIATE','UPDATE account SET balance=balance+25',"INSERT INTO receipt VALUES('reward-1',25,125)",'COMMIT','COMMIT'],'literal DML/commit sequence')
b=[json.loads(x) for x in (out/'observe.stdout').read_text().splitlines()]
req(b==[{'kind':'independent_read_pass','snapshot':{'balance':125,'receipts':final,'in_transaction':False},'integrity':[['ok']]}],'fresh reader')
for role in ['scenario','observe']:
    req(not (out/(role+'.stderr')).read_bytes(),'stderr')
    req(json.loads((out/(role+'.json')).read_text())==(a if role=='scenario' else b),'raw equality')
raw=base64.b64decode((out/'ledger.db.base64').read_text().strip(),validate=True)
req(len(raw)==s['database']['bytes'] and hashlib.sha256(raw).hexdigest()==s['database']['sha256'],'database archive')
print(json.dumps({'status':'PASS','invocation':out.name,'actual_child_processes':2,'database_bytes':len(raw),'sqlite_version':a[-1]['sqlite_version'],'sqlite_source_id':a[-1]['sqlite_source_id'],'source_sha256':s['source_sha256']},indent=2))
