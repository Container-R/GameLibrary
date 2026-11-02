"""One predetermined WAL observation. Do not launch before review approval."""
import hashlib
import json
from pathlib import Path
import platform
import sys
import traceback


def main():
    # No sqlite import or connection at module import time.
    report = {'schema': 1, 'status': 'FAILED', 'steps': [],
              'fixture_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'versions': {'python': platform.python_version()},
              'connections_opened': 0, 'connections_closed': 0}
    connections = []
    failed = False

    def require(condition):
        if not condition:
            raise ValueError('frozen observation mismatch')

    def emit(step, **values):
        report['steps'].append({'step': step, **values})

    def rows(conn, sql, args=()):
        cur = conn.execute(sql, args)
        try:
            return [list(row) for row in cur.fetchall()]
        finally:
            cur.close()

    def command(conn, sql, args=()):
        cur = conn.execute(sql, args)
        cur.close()

    def state(conn):
        return {'operations': rows(conn, 'SELECT account, request_id, result_amount FROM operations ORDER BY account, request_id'),
                'balances': rows(conn, 'SELECT account, amount FROM balance ORDER BY account'),
                'in_transaction': conn.in_transaction}

    def expected(amount, found, active):
        return {'balances': [['player-one', amount]],
                'operations': [['player-one', 'reward-one', 112]] if found else [],
                'in_transaction': active}

    def observe(name, conn, want):
        actual = state(conn)
        emit(name, **actual)
        require(actual == want)

    def connect():
        conn = sqlite3.connect(str(db), timeout=0, isolation_level=None,
                               autocommit=sqlite3.LEGACY_TRANSACTION_CONTROL)
        connections.append(conn)
        report['connections_opened'] += 1
        return conn

    def close(conn):
        conn.close()
        connections.remove(conn)
        report['connections_closed'] += 1

    try:
        if sys.version_info < (3, 12):
            raise RuntimeError('Python 3.12 or newer required')
        if sys.flags.optimize:
            raise RuntimeError('optimized child rejected')
        if len(sys.argv) != 2:
            raise ValueError('one owned database path required')
        db = Path(sys.argv[1])
        require(db.is_absolute() and db.parent.is_dir() and not db.exists() and not db.is_symlink())
        import sqlite3
        report['versions']['sqlite'] = sqlite3.sqlite_version
        a = connect()
        mode_a = rows(a, 'PRAGMA journal_mode=WAL')
        b = connect()
        for conn in (a, b):
            command(conn, 'PRAGMA busy_timeout=0')
            command(conn, 'PRAGMA read_uncommitted=0')
        config = {'set_mode': mode_a, 'A_mode': rows(a, 'PRAGMA journal_mode'), 'B_mode': rows(b, 'PRAGMA journal_mode'),
                  'A_busy_timeout': rows(a, 'PRAGMA busy_timeout'),
                  'B_busy_timeout': rows(b, 'PRAGMA busy_timeout'),
                  'A_read_uncommitted': rows(a, 'PRAGMA read_uncommitted'),
                  'B_read_uncommitted': rows(b, 'PRAGMA read_uncommitted'),
                  'A_autocommit': a.autocommit, 'B_autocommit': b.autocommit,
                  'A_isolation_level': a.isolation_level, 'B_isolation_level': b.isolation_level,
                  'distinct_connections': a is not b,
                  'A_in_transaction': a.in_transaction, 'B_in_transaction': b.in_transaction}
        emit('configuration', **config)
        require(config == {'set_mode': [['wal']], 'A_mode': [['wal']], 'B_mode': [['wal']],
                           'A_busy_timeout': [[0]], 'B_busy_timeout': [[0]],
                           'A_read_uncommitted': [[0]], 'B_read_uncommitted': [[0]],
                           'A_autocommit': -1, 'B_autocommit': -1,
                           'A_isolation_level': None, 'B_isolation_level': None,
                           'distinct_connections': True, 'A_in_transaction': False,
                           'B_in_transaction': False})
        command(a, 'BEGIN IMMEDIATE')
        command(a, 'CREATE TABLE balance(account TEXT PRIMARY KEY, amount INTEGER NOT NULL)')
        command(a, 'CREATE TABLE operations(account TEXT, request_id TEXT, result_amount INTEGER NOT NULL, PRIMARY KEY(account, request_id))')
        command(a, 'INSERT INTO balance VALUES (?, ?)', ('player-one', 100))
        command(a, 'COMMIT')
        observe('initialized', a, expected(100, False, False))
        command(a, 'BEGIN DEFERRED')
        observe('A_initial_read', a, expected(100, False, True))
        command(b, 'BEGIN IMMEDIATE')
        observe('B_before_write', b, expected(100, False, True))
        command(b, 'UPDATE balance SET amount=amount+12 WHERE account=?', ('player-one',))
        command(b, 'INSERT INTO operations VALUES (?, ?, ?)', ('player-one', 'reward-one', 112))
        command(b, 'COMMIT')
        observe('B_committed', b, expected(112, True, False))
        observe('A_old_snapshot', a, expected(100, False, True))
        for name in ('A_upgrade_attempt_1', 'A_upgrade_attempt_2'):
            try:
                command(a, 'UPDATE balance SET amount=amount+12 WHERE account=?', ('player-one',))
            except sqlite3.Error as exc:
                code = getattr(exc, 'sqlite_errorcode', None)
                error_name = getattr(exc, 'sqlite_errorname', None)
                emit(name, outcome='exception', code=code, name=error_name,
                     primary_code=(code & 255) if type(code) is int else None,
                     in_transaction=a.in_transaction)
                require(type(code) is int and code == 517 and error_name == 'SQLITE_BUSY_SNAPSHOT' and a.in_transaction is True)
            else:
                emit(name, outcome='unexpected_success', in_transaction=a.in_transaction)
                raise ValueError('upgrade unexpectedly succeeded')
        command(a, 'ROLLBACK')
        emit('A_rollback', in_transaction=a.in_transaction)
        require(a.in_transaction is False)
        command(a, 'BEGIN DEFERRED')
        observe('A_recheck', a, expected(112, True, True))
        # Duplicate branch: no UPDATE or INSERT after this point.
        command(a, 'COMMIT')
        emit('A_duplicate_committed', branch='duplicate_result', result_amount=112,
             in_transaction=a.in_transaction)
        require(a.in_transaction is False)
        close(a)
        close(b)
        fresh = connect()
        observe('fresh_connection', fresh, expected(112, True, False))
        close(fresh)
    except BaseException as exc:
        failed = True
        report['failure_type'] = type(exc).__name__
        traceback.print_exc(file=sys.stderr)  # INTERNAL ONLY: may contain local paths.
    finally:
        for conn in list(connections):
            try:
                close(conn)
            except BaseException:
                failed = True
                traceback.print_exc(file=sys.stderr)
        report['cleanup_complete'] = not connections
    if not failed and report['cleanup_complete']:
        report['status'] = 'OBSERVED'
    print(json.dumps(report, sort_keys=True, separators=(',', ':'), allow_nan=False))
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
