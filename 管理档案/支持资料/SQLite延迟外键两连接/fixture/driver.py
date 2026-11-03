"""Frozen deferred-FK observations. Preparation only; no execution yet."""
import sys
if sys.version_info[:2] != (3, 12):
    raise RuntimeError('requires Python 3.12 series')
import json
import sqlite3
from pathlib import Path

records = []

def sql(conn, statement):
    cur = conn.cursor()
    try:
        cur.execute(statement)
        return cur.fetchall()
    finally:
        cur.close()

def checkpoint(case, phase, w, r, error=None):
    records.append(dict(case=case, phase=phase,
        writer_owners=sql(w, 'SELECT id FROM owner ORDER BY id'),
        writer_items=sql(w, 'SELECT id, owner_id FROM inventory ORDER BY id'),
        reader_owners=sql(r, 'SELECT id FROM owner ORDER BY id'),
        reader_items=sql(r, 'SELECT id, owner_id FROM inventory ORDER BY id'),
        writer_in_transaction=w.in_transaction,
        reader_in_transaction=r.in_transaction, error=error))

def expect_fk(conn, statement):
    try:
        sql(conn, statement)
    except sqlite3.IntegrityError as exc:
        code = getattr(exc, 'sqlite_errorcode', None)
        name = getattr(exc, 'sqlite_errorname', None)
        if type(code) is not int or code != 787 or name != 'SQLITE_CONSTRAINT_FOREIGNKEY':
            raise
        return dict(code=code, name=name)
    raise RuntimeError('expected foreign-key rejection did not occur')

def run_case(case):
    path = Path(case + '.sqlite')
    if path.exists() or path.is_symlink():
        raise RuntimeError('database must be fresh')
    w = r = None
    failures = []
    try:
        opts = dict(uri=True, timeout=1.0, isolation_level=None,
                    autocommit=sqlite3.LEGACY_TRANSACTION_CONTROL)
        uri = 'file:' + path.name + '?cache=private'
        w = sqlite3.connect(uri, **opts)
        if sql(w, 'PRAGMA journal_mode=DELETE') != [('delete',)]:
            raise RuntimeError('DELETE mode not established')
        sql(w, 'PRAGMA foreign_keys=ON')
        sql(w, 'PRAGMA read_uncommitted=0')
        if sql(w, 'PRAGMA foreign_keys') != [(1,)]:
            raise RuntimeError('foreign keys unavailable')
        sql(w, 'CREATE TABLE owner(id INTEGER PRIMARY KEY)')
        clause = 'NOT DEFERRABLE INITIALLY IMMEDIATE' if case == 'C' else 'DEFERRABLE INITIALLY DEFERRED'
        sql(w, 'CREATE TABLE inventory(id INTEGER PRIMARY KEY, owner_id INTEGER NOT NULL REFERENCES owner(id) ' + clause + ')')
        r = sqlite3.connect(uri, **opts)
        sql(r, 'PRAGMA foreign_keys=ON')
        sql(r, 'PRAGMA read_uncommitted=0')
        for conn in (w, r):
            if conn.autocommit != sqlite3.LEGACY_TRANSACTION_CONTROL or conn.isolation_level is not None:
                raise RuntimeError('transaction mode mismatch')
            if conn.in_transaction:
                raise RuntimeError('unexpected setup transaction')
            if sql(conn, 'PRAGMA foreign_keys') != [(1,)] or sql(conn, 'PRAGMA journal_mode') != [('delete',)] or sql(conn, 'PRAGMA read_uncommitted') != [(0,)]:
                raise RuntimeError('connection settings mismatch')
        checkpoint(case, 'baseline', w, r)
        if case == 'A':
            sql(w, 'BEGIN')
            sql(w, 'SAVEPOINT helper')
            sql(w, 'INSERT INTO inventory VALUES(1,7)')
            sql(w, 'RELEASE helper')
            checkpoint(case, 'nested_release', w, r)
            error = expect_fk(w, 'COMMIT')
            checkpoint(case, 'commit_rejected', w, r, error)
            sql(w, 'INSERT INTO owner VALUES(7)')
            checkpoint(case, 'parent_inserted', w, r)
            sql(w, 'COMMIT')
            checkpoint(case, 'committed', w, r)
        elif case == 'B':
            sql(w, 'SAVEPOINT helper')
            sql(w, 'INSERT INTO inventory VALUES(1,7)')
            checkpoint(case, 'outermost_insert', w, r)
            error = expect_fk(w, 'RELEASE helper')
            checkpoint(case, 'release_rejected', w, r, error)
            sql(w, 'ROLLBACK TO helper')
            checkpoint(case, 'rollback_to', w, r)
            sql(w, 'RELEASE helper')
            checkpoint(case, 'released_empty', w, r)
        else:
            sql(w, 'BEGIN')
            error = expect_fk(w, 'INSERT INTO inventory VALUES(1,7)')
            checkpoint(case, 'insert_rejected', w, r, error)
            sql(w, 'ROLLBACK')
            checkpoint(case, 'rolled_back', w, r)
    except BaseException as exc:
        exc.add_note('case ' + case + ': SQL/setup/checkpoint failure')
        failures.append(exc)
    finally:
        for label, conn in (('reader', r), ('writer', w)):
            if conn is not None:
                try:
                    conn.close()
                except BaseException as exc:
                    exc.add_note('case ' + case + ': ' + label + ' close failure')
                    failures.append(exc)
    if failures:
        raise BaseExceptionGroup('case failed', failures)

try:
    for case in ('A', 'B', 'C'):
        run_case(case)
except BaseException:
    print(json.dumps({'partial_checkpoints': records}, sort_keys=True), flush=True)
    raise
print(json.dumps({'python_version': '.'.join(map(str, sys.version_info[:3])),
                  'sqlite_version': sqlite3.sqlite_version,
                  'checkpoints': records}, sort_keys=True))
