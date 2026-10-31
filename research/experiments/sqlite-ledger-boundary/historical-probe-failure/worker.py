#!/usr/bin/env python3
import hashlib,json,os,pathlib,platform,sqlite3,sys,_sqlite3
if not __debug__:raise SystemExit('Refusing -O')
def check(ok,msg):
    if not ok:raise RuntimeError(msg)
def metadata(db):
    paths={pathlib.Path(sys.executable).resolve(),pathlib.Path(_sqlite3.__file__).resolve()}
    for line in pathlib.Path('/proc/self/maps').read_text().splitlines():
        if 'libsqlite3' in line and line.split()[-1].startswith('/'):
            paths.add(pathlib.Path(line.split()[-1]).resolve())
    return {'python':platform.python_version(),'sqlite':sqlite3.sqlite_version,'source_id':db.execute('select sqlite_source_id()').fetchone()[0],'binaries':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}}
def connect(path):
    db=sqlite3.connect(path,isolation_level=None,autocommit=sqlite3.LEGACY_TRANSACTION_CONTROL,timeout=1)
    db.execute('PRAGMA journal_mode=DELETE');db.execute('PRAGMA synchronous=EXTRA')
    config={'journal_mode':db.execute('PRAGMA journal_mode').fetchone()[0],'synchronous':db.execute('PRAGMA synchronous').fetchone()[0],'autocommit':db.autocommit,'isolation_level':db.isolation_level}
    check(config['journal_mode']=='delete' and config['synchronous']==3,'pragma readback')
    print('CONFIG='+json.dumps({'config':config,'metadata':metadata(db)}),flush=True)
    return db

def post(db,event,amount,reason,checkpoint=None):
    check(isinstance(event,str) and bool(event.strip()),'event id')
    check(type(amount) is int and -1000000<=amount<=1000000,'bounded integer, not bool')
    check(isinstance(reason,str) and bool(reason.strip()),'reason')
    db.execute('BEGIN IMMEDIATE')
    try:
        old=db.execute('SELECT amount,reason,balance_after FROM receipt WHERE event_id=?',(event,)).fetchone()
        if old:
            if old[:2]!=(amount,reason):
                db.execute('ROLLBACK');return {'outcome':'payload_conflict'}
            db.execute('COMMIT');return {'outcome':'duplicate','balance_after':old[2]}
        balance=db.execute('SELECT balance FROM account WHERE id=1').fetchone()[0]
        check(0<=balance+amount<=1000000,'balance bounds')
        db.execute('UPDATE account SET balance=? WHERE id=1',(balance+amount,))
        db.execute('INSERT INTO receipt VALUES(?,?,?,?)',(event,amount,reason,balance+amount))
        if checkpoint=='before':
            print('CHECKPOINT='+json.dumps({'phase':'before_commit','in_transaction':db.in_transaction,'local_balance':balance+amount,'local_receipt':db.execute('SELECT count(*) FROM receipt WHERE event_id=?',(event,)).fetchone()[0]}),flush=True)
            os._exit(41)
        db.execute('COMMIT')
        if checkpoint=='after':
            print('CHECKPOINT='+json.dumps({'phase':'committed_before_ack','in_transaction':db.in_transaction}),flush=True)
            os._exit(42)
        return {'outcome':'applied','balance_after':balance+amount}
    except BaseException:
        if db.in_transaction:db.execute('ROLLBACK')
        raise

def snapshot(db):
    balance=db.execute('SELECT balance FROM account WHERE id=1').fetchone()[0]
    rows=db.execute('SELECT event_id,amount,reason,balance_after FROM receipt ORDER BY event_id').fetchall()
    return {'balance':balance,'receipts':rows,'sum_delta':db.execute('SELECT coalesce(sum(amount),0) FROM receipt').fetchone()[0],'reward_count':db.execute("SELECT count(*) FROM receipt WHERE event_id='reward-1'").fetchone()[0],'integrity':db.execute('PRAGMA integrity_check').fetchall()}
check(len(sys.argv)==3 and sys.argv[1] in ['init','before','after','retry_same','retry_changed','read'],'case whitelist')
mode,path=sys.argv[1:];db=connect(path)
try:
    outcome=None
    if mode=='init':
        db.execute('CREATE TABLE account(id INTEGER PRIMARY KEY CHECK(id=1),balance INTEGER NOT NULL CHECK(balance>=0))')
        db.execute('CREATE TABLE receipt(event_id TEXT PRIMARY KEY NOT NULL,amount INTEGER NOT NULL,reason TEXT NOT NULL,balance_after INTEGER NOT NULL)')
        db.execute('INSERT INTO account VALUES(1,0)');outcome=post(db,'opening',100,'opening')
    elif mode in ['before','after']:outcome=post(db,'reward-1',25,'quest',mode)
    elif mode=='retry_same':outcome=post(db,'reward-1',25,'quest')
    elif mode=='retry_changed':outcome=post(db,'reward-1',26,'quest')
    print('RESULT_JSON='+json.dumps({'mode':mode,'outcome':outcome,'snapshot':snapshot(db)}),flush=True)
finally:db.close()
