import json,sys,tempfile,sqlite3,hashlib
from pathlib import Path
if sys.flags.optimize:raise SystemExit('no -O')
p=Path(sys.argv[1]);source=p.read_text();ns={};exec(compile(source.split('check(len(sys.argv)==3')[0],str(p),'exec'),ns)
with tempfile.TemporaryDirectory() as t:
    db=ns['connect'](str(Path(t)/'supplement.db'))
    db.executescript('CREATE TABLE account(id INTEGER PRIMARY KEY CHECK(id=1),balance INTEGER NOT NULL CHECK(balance>=0)); CREATE TABLE receipt(event_id TEXT PRIMARY KEY NOT NULL,amount INTEGER NOT NULL,reason TEXT NOT NULL,balance_after INTEGER NOT NULL); INSERT INTO account VALUES(1,0);')
    post=ns['post'];snap=ns['snapshot'];post(db,'opening',100,'opening');baseline=snap(db); checks=[]
    for bad in [True,False,1.0,1000001,-1000001]:
        try:post(db,'bad',bad,'test')
        except RuntimeError:pass
        else:raise AssertionError('bad amount accepted')
        assert snap(db)==baseline and not db.in_transaction
        checks.append('reject '+repr(bad))
    for bad in [-101,1000000]:
        try:post(db,'bounds',bad,'test')
        except RuntimeError:pass
        else:raise AssertionError('balance bounds accepted')
        assert snap(db)==baseline and not db.in_transaction
        checks.append('balance rollback '+str(bad))
    post(db,'reward-1',25,'quest');old=snap(db)
    assert post(db,'reward-1',25,'other')=={'outcome':'payload_conflict'} and snap(db)==old and not db.in_transaction
    checks.append('reason conflict unchanged')
    post(db,'later',10,'later')
    assert post(db,'reward-1',25,'quest')=={'outcome':'duplicate','balance_after':125} and snap(db)['balance']==135
    checks.append('duplicate original receipt not current balance')
    db.execute("CREATE TRIGGER force_insert_failure BEFORE INSERT ON receipt WHEN NEW.event_id='trigger' BEGIN SELECT RAISE(ABORT,'injected'); END")
    old=snap(db)
    try:post(db,'trigger',5,'test')
    except sqlite3.IntegrityError:pass
    else:raise AssertionError('injection failed')
    assert snap(db)==old and not db.in_transaction
    checks.append('insert failure rolls back prior balance update')
    db.close()
print('SUPPLEMENT='+json.dumps({'checks':checks,'worker_sha256':hashlib.sha256(p.read_bytes()).hexdigest()}))
