#!/usr/bin/env python3
import json,sqlite3,sys
from ledger import connect,check,post,snapshot
check(len(sys.argv)==3 and sys.argv[1] in ['init','read','A','B'],'role')
role,path=sys.argv[1:];db=connect(path)
def emit(phase,**data):print('EVENT='+json.dumps({'role':role,'phase':phase,**data}),flush=True)
try:
    if role=='init':
        db.execute('CREATE TABLE account(id INTEGER PRIMARY KEY CHECK(id=1),balance INTEGER NOT NULL CHECK(balance>=0))')
        db.execute('CREATE TABLE receipt(event_id TEXT PRIMARY KEY NOT NULL,amount INTEGER NOT NULL,reason TEXT NOT NULL,balance_after INTEGER NOT NULL)')
        db.execute('INSERT INTO account VALUES(1,0)');post(db,'opening',100,'opening');emit('INITIALIZED',snapshot=snapshot(db))
    elif role=='read':emit('FINAL',snapshot=snapshot(db))
    else:
        db.execute('PRAGMA busy_timeout=0')
        emit('READY',busy_timeout=db.execute('PRAGMA busy_timeout').fetchone()[0],in_transaction=db.in_transaction)
        state='ready'
        for line in sys.stdin:
            cmd=json.loads(line)['command']
            if role=='A' and cmd=='APPLY_HOLD' and state=='ready':
                db.execute('BEGIN IMMEDIATE')
                check(db.execute("SELECT count(*) FROM receipt WHERE event_id='reward-1'").fetchone()[0]==0,'no existing reward')
                db.execute('UPDATE account SET balance=balance+25 WHERE id=1')
                db.execute('INSERT INTO receipt VALUES(?,?,?,?)',('reward-1',25,'quest',125))
                state='held';emit('HELD',in_transaction=db.in_transaction,snapshot=snapshot(db))
            elif role=='B' and cmd=='TRY_BEGIN' and state=='ready':
                try:db.execute('BEGIN IMMEDIATE')
                except sqlite3.OperationalError as e:
                    code=e.sqlite_errorcode;name=e.sqlite_errorname
                    check(code==sqlite3.SQLITE_BUSY and name=='SQLITE_BUSY','unexpected error')
                    check(not db.in_transaction,'BEGIN busy unexpectedly active')
                    view=snapshot(db)
                    state='busy';emit('BUSY_OBSERVED',code=code,name=name,message=str(e),at='BEGIN IMMEDIATE',in_transaction=db.in_transaction,snapshot=view)
                else:raise RuntimeError('B acquired writer while A should hold it')
            elif role=='A' and cmd=='COMMIT' and state=='held':
                db.execute('COMMIT');state='committed';emit('COMMITTED',in_transaction=db.in_transaction)
            elif role=='B' and cmd=='RETRY_SAME' and state=='busy':
                result=post(db,'reward-1',25,'quest');state='retried';emit('DUPLICATE',outcome=result,in_transaction=db.in_transaction,snapshot=snapshot(db))
            elif cmd=='CLOSE' and state in ['committed','retried']:
                emit('CLOSING',in_transaction=db.in_transaction);break
            else:raise RuntimeError('invalid protocol transition')
        else:raise RuntimeError('unexpected protocol EOF')
finally:db.close()
