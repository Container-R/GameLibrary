"""Read-only literal archive acceptance; does not execute SQLite or archived code."""
import base64,hashlib,json,sys
from pathlib import Path

def require(ok,message):
    if not ok:raise ValueError(message)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main(root):
    reports=[]
    for side,folder,sources in [('author',root/'results',root),('review',root/'review/evidence',root/'review/fixture')]:
        summaries=list(folder.glob('*/summary.json'));require(len(summaries)==1,'one retained invocation')
        p=summaries[0];d=p.parent;s=json.loads(p.read_text())
        require(s['status']=='PASS' and s['invocation_id']==d.name,'terminal UUID')
        require(len(s['processes'])==2 and all(x['exit_code']==0 and x['timed_out'] is False for x in s['processes']),'two successful processes')
        for name,h in s['source_sha256'].items():require(digest(sources/name)==h,'source '+name)
        for name,h in s['outputs_sha256'].items():require(digest(d/name)==h,'output '+name)
        a=[json.loads(line) for line in (d/'scenario.stdout').read_text().splitlines()]
        kinds=['config','config','reader_held','writer_applied','commit_busy','writer_after_busy','reader_after_busy','reader_released','writer_committed','reader_new_view','writer_sql_trace','scenario_pass']
        require([x['kind'] for x in a]==kinds,'event ordering')
        for x in a[:2]:require(x['values']=={'journal_mode':'delete','synchronous':3,'busy_timeout':0},'configuration')
        opening=[['opening',100,100]];final=opening+[['reward-1',25,125]]
        for i,b,rows,active in [(2,100,opening,True),(3,125,final,True),(5,125,final,True),(6,100,opening,True),(8,125,final,False),(9,125,final,False)]:
            require(a[i]['snapshot']=={'balance':b,'receipts':rows,'in_transaction':active},'snapshot '+str(i))
        require(a[4]['code']==5 and a[4]['name']=='SQLITE_BUSY' and a[4]['in_transaction'] is True,'busy retains transaction')
        require(a[7]['in_transaction'] is False,'reader released')
        sql=[x for x in a[10]['statements'] if not x.startswith('SELECT ')]
        require(sql==['BEGIN IMMEDIATE','UPDATE account SET balance=balance+25',"INSERT INTO receipt VALUES('reward-1',25,125)",'COMMIT','COMMIT'],'no mutation replay')
        b=[json.loads(line) for line in (d/'observe.stdout').read_text().splitlines()]
        require(b==[{'kind':'independent_read_pass','snapshot':{'balance':125,'receipts':final,'in_transaction':False},'integrity':[['ok']]}],'fresh reader')
        for role,expected in [('scenario',a),('observe',b)]:
            require(json.loads((d/(role+'.json')).read_text())==expected,'raw parsed association')
            require(not (d/(role+'.stderr')).read_bytes(),'empty stderr')
        raw=base64.b64decode((d/'ledger.db.base64').read_text().strip(),validate=True)
        require(len(raw)==s['database']['bytes'] and hashlib.sha256(raw).hexdigest()==s['database']['sha256'],'database bytes/hash')
        reports.append({'side':side,'invocation':d.name,'status':'PASS','database_bytes':len(raw),'archived_processes':2,'new_process_executions':0})
    print(json.dumps({'scope':'Read-only retained archive semantics and consistency, no SQLite execution','results':reports},indent=2))
if __name__=='__main__':main(Path(sys.argv[1]).resolve())
