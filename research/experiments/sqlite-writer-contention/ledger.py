#!/usr/bin/env python3
import hashlib,json,os,pathlib,platform,sqlite3,sys,_sqlite3
if not __debug__:raise SystemExit('Refusing -O')
def check(ok,msg):
    if not ok:raise RuntimeError(msg)
def metadata(db):
    paths={pathlib.Path(sys.executable).resolve()}
    extension_file=getattr(_sqlite3,'__file__',None)
    if extension_file:paths.add(pathlib.Path(extension_file).resolve())
    for line in pathlib.Path('/proc/self/maps').read_text().splitlines():
        if 'libsqlite3' in line and line.split()[-1].startswith('/'):
            paths.add(pathlib.Path(line.split()[-1]).resolve())
    return {'sqlite_module_origin':_sqlite3.__spec__.origin,'sqlite_extension_file':extension_file,'python':platform.python_version(),'sqlite':sqlite3.sqlite_version,'source_id':db.execute('select sqlite_source_id()').fetchone()[0],'binaries':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}}
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
    def rows(sql):
        cursor=db.execute(sql)
        try:return cursor.fetchall()
        finally:cursor.close()
    balance=rows('SELECT balance FROM account WHERE id=1')[0][0]
    return {'balance':balance,'receipts':rows('SELECT event_id,amount,reason,balance_after FROM receipt ORDER BY event_id'),'sum_delta':rows('SELECT coalesce(sum(amount),0) FROM receipt')[0][0],'reward_count':rows("SELECT count(*) FROM receipt WHERE event_id='reward-1'")[0][0],'integrity':rows('PRAGMA integrity_check')}
