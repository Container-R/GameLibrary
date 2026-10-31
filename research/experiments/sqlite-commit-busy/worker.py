import json
import sqlite3
import sys
from pathlib import Path


def require(value, message):
    if not value:
        raise RuntimeError(message)


def query(c, sql):
    cur = c.execute(sql)
    try:
        return cur.fetchall()
    finally:
        cur.close()


def emit(kind, **fields):
    print(json.dumps(dict(kind=kind, **fields), sort_keys=True), flush=True)


def snapshot(c):
    return dict(balance=query(c, 'SELECT balance FROM account')[0][0],
                receipts=query(c, 'SELECT id,amount,balance_after FROM receipt ORDER BY id'),
                in_transaction=c.in_transaction)


def check(s, final, active):
    expected = [('opening', 100, 100)] + ([('reward-1', 25, 125)] if final else [])
    require(s == dict(balance=125 if final else 100, receipts=expected,
                      in_transaction=active), 'snapshot mismatch')


def connect(path):
    c = sqlite3.connect(path, timeout=0, isolation_level=None,
                        autocommit=sqlite3.LEGACY_TRANSACTION_CONTROL)
    for sql in ('PRAGMA journal_mode=DELETE', 'PRAGMA synchronous=EXTRA', 'PRAGMA busy_timeout=0'):
        query(c, sql)
    config = {k: query(c, 'PRAGMA ' + k)[0][0]
              for k in ('journal_mode', 'synchronous', 'busy_timeout')}
    require(config == dict(journal_mode='delete', synchronous=3, busy_timeout=0), 'config mismatch')
    emit('config', values=config)
    return c


def scenario(path):
    w = connect(path)
    r = None
    try:
        for sql in ('CREATE TABLE account(balance INTEGER NOT NULL)',
                    'CREATE TABLE receipt(id TEXT PRIMARY KEY, amount INTEGER, balance_after INTEGER)',
                    'BEGIN IMMEDIATE', 'INSERT INTO account VALUES(100)',
                    "INSERT INTO receipt VALUES('opening',100,100)", 'COMMIT'):
            w.execute(sql).close()
        r = connect(path)
        trace = []
        w.set_trace_callback(trace.append)
        r.execute('BEGIN').close()
        s = snapshot(r); check(s, False, True); emit('reader_held', snapshot=s)
        w.execute('BEGIN IMMEDIATE').close()
        w.execute('UPDATE account SET balance=balance+25').close()
        w.execute("INSERT INTO receipt VALUES('reward-1',25,125)").close()
        s = snapshot(w); check(s, True, True); emit('writer_applied', snapshot=s)
        try:
            w.execute('COMMIT').close()
        except sqlite3.OperationalError as e:
            require(e.sqlite_errorcode == 5 and e.sqlite_errorname == 'SQLITE_BUSY', 'unexpected SQL error')
            emit('commit_busy', code=e.sqlite_errorcode, name=e.sqlite_errorname,
                 message=str(e), in_transaction=w.in_transaction)
        else:
            raise RuntimeError('COMMIT unexpectedly succeeded')
        s = snapshot(w); check(s, True, True); emit('writer_after_busy', snapshot=s)
        s = snapshot(r); check(s, False, True); emit('reader_after_busy', snapshot=s)
        r.execute('COMMIT').close()
        require(not r.in_transaction, 'reader not released')
        emit('reader_released', in_transaction=r.in_transaction)
        w.execute('COMMIT').close()
        s = snapshot(w); check(s, True, False); emit('writer_committed', snapshot=s)
        s = snapshot(r); check(s, True, False); emit('reader_new_view', snapshot=s)
        for sql, count in [('BEGIN IMMEDIATE', 1), ('UPDATE account SET balance=balance+25', 1),
                           ("INSERT INTO receipt VALUES('reward-1',25,125)", 1), ('COMMIT', 2)]:
            require(trace.count(sql) == count, 'unexpected SQL execution count: ' + sql)
        emit('writer_sql_trace', statements=trace)
        emit('scenario_pass', sqlite_version=sqlite3.sqlite_version,
             sqlite_source_id=query(w, 'SELECT sqlite_source_id()')[0][0], python=sys.version)
    finally:
        if r is not None:
            r.close()
        w.close()


def observe(path):
    c = sqlite3.connect(Path(path).resolve().as_uri() + '?mode=ro', uri=True,
                        isolation_level=None, timeout=0, autocommit=sqlite3.LEGACY_TRANSACTION_CONTROL)
    try:
        s = snapshot(c); check(s, True, False)
        require(sum(row[1] for row in s['receipts']) == s['balance'], 'ledger conservation')
        integrity = query(c, 'PRAGMA integrity_check')
        require(integrity == [('ok',)], 'integrity failed')
        emit('independent_read_pass', snapshot=s, integrity=integrity)
    finally:
        c.close()


if __name__ == '__main__':
    if len(sys.argv) != 3 or sys.argv[1] not in ('scenario', 'observe'):
        raise SystemExit('usage: worker.py scenario|observe DATABASE')
    (scenario if sys.argv[1] == 'scenario' else observe)(sys.argv[2])
