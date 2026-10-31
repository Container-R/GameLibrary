import json,sys
from pathlib import Path
if sys.flags.optimize:raise SystemExit('no -O')
r=Path(sys.argv[1]); rows={}; metadata=[]
for label in ['init-before.db','init-after.db','before-exit','before-reopen','after-exit','after-reopen','retry-same','same-reopen','retry-changed','changed-reopen']:
    lines=(r/(label+'.stdout.txt')).read_text().splitlines()
    assert not (r/(label+'.stderr.txt')).read_text()
    cmd=json.loads((r/(label+'.command.json')).read_text())
    cfg=[json.loads(x[7:]) for x in lines if x.startswith('CONFIG=')];assert len(cfg)==1
    assert cfg[0]['config']=={'journal_mode':'delete','synchronous':3,'autocommit':-1,'isolation_level':None};metadata.append(cfg[0]['metadata'])
    payload=[json.loads(x[12:]) for x in lines if x.startswith('RESULT_JSON=')]
    marks=[json.loads(x[11:]) for x in lines if x.startswith('CHECKPOINT=')]
    if label in ['before-exit','after-exit']:
        before=label=='before-exit';assert cmd['returncode']==(41 if before else 42) and payload==[] and len(marks)==1
        assert marks[0]['in_transaction']==before
        assert marks[0]['phase']==('before_commit' if before else 'committed_before_ack')
        if before: assert marks[0]['local_receipt']==1 and marks[0]['local_balance']==125
        rows[label]=marks;continue
    assert cmd['returncode']==0 and len(payload)==1 and marks==[]
    s=payload[0]['snapshot'];has=label in ['after-reopen','retry-same','same-reopen','retry-changed','changed-reopen']
    expected=[['opening',100,'opening',100]]+([['reward-1',25,'quest',125]] if has else [])
    assert s['receipts']==expected and s['balance']==sum(x[1] for x in expected)==s['sum_delta']
    assert s['reward_count']==int(has) and s['integrity']==[['ok']]
    if label=='retry-same':assert payload[0]['outcome']=={'outcome':'duplicate','balance_after':125}
    if label=='retry-changed':assert payload[0]['outcome']=={'outcome':'payload_conflict'}
    rows[label]=payload[0]
assert all(m==metadata[0] for m in metadata)
print(json.dumps({'checks':'passed','observations':rows,'metadata':metadata[0]},indent=2))
