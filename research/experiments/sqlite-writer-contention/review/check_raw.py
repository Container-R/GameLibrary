import json,sys,hashlib,base64
from pathlib import Path
if sys.flags.optimize:raise SystemExit('no -O')
r=Path(sys.argv[1]); transcript=json.loads((r/'transcript.json').read_text()); parsed={};events={};meta=[]
for role in ['init','A','B','read']:
    lines=(r/(role+'.stdout.txt')).read_text().splitlines();assert not (r/(role+'.stderr.txt')).read_text()
    assert json.loads((r/(role+'.command.json')).read_text())['returncode']==0
    decoded=[]
    for line in lines:
        key,value=line.split('=',1);assert key in ['CONFIG','EVENT'];d=json.loads(value);decoded.append(d)
        if key=='CONFIG':
            assert d['config']=={'journal_mode':'delete','synchronous':3,'autocommit':-1,'isolation_level':None};meta.append(d['metadata'])
        else:
            assert d['role']==role;events[(role,d['phase'])]=d
    assert decoded==[x['data'] for x in transcript if x['direction']=='receive' and x['role']==role]
    parsed[role]=decoded
assert len(meta)==4 and all(m==meta[0] for m in meta)
def at(role,phase):return next(i for i,x in enumerate(transcript) if x['direction']=='receive' and x['role']==role and x['data'].get('phase')==phase)
def sent(role,cmd):return next(i for i,x in enumerate(transcript) if x['direction']=='send' and x['role']==role and x['command']==cmd)
assert max(at('A','READY'),at('B','READY'))<sent('A','APPLY_HOLD')<at('A','HELD')<sent('B','TRY_BEGIN')<at('B','BUSY_OBSERVED')<sent('A','COMMIT')<at('A','COMMITTED')<sent('B','RETRY_SAME')<at('B','DUPLICATE')
for role in ['A','B']:
 assert events[(role,'READY')]['busy_timeout']==0 and not events[(role,'READY')]['in_transaction']
 assert at(role,'CLOSING')<at('read','FINAL')
assert events[('A','HELD')]['in_transaction'] and not events[('A','COMMITTED')]['in_transaction']
b=events[('B','BUSY_OBSERVED')];assert (b['code'],b['name'],b['at'],b['in_transaction'])==(5,'SQLITE_BUSY','BEGIN IMMEDIATE',False)
assert events[('B','DUPLICATE')]['outcome']=={'outcome':'duplicate','balance_after':125}
for key,balance in [(('init','INITIALIZED'),100),(('A','HELD'),125),(('B','BUSY_OBSERVED'),100),(('B','DUPLICATE'),125),(('read','FINAL'),125)]:
 s=events[key]['snapshot']; rows=[['opening',100,'opening',100]]+([['reward-1',25,'quest',125]] if balance==125 else [])
 assert s=={'balance':balance,'receipts':rows,'sum_delta':balance,'reward_count':int(balance==125),'integrity':[['ok']]}
summary=json.loads((r/'summary.json').read_text());d=summary['database'];raw=base64.decodebytes((r/d['encoded_file']).read_bytes());assert len(raw)==d['bytes'] and hashlib.sha256(raw).hexdigest()==d['sha256']
original=Path(summary['database_directory'])/d['filename']
original_compared=original.is_file()
if original_compared: assert raw==original.read_bytes()
print(json.dumps({'checks':'passed','events':list(events.values()),'database_verified':d,'original_runtime_file_compared':original_compared,'source_sha256':summary['source_sha256'],'metadata':meta[0]},indent=2))
