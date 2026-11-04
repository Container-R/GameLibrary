"""Fixed synthetic SQL observation. Run only after independent acceptance."""
import json
import sys
import traceback


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def statement(connection, sql):
    """Completion means execute, fetchall and close all returned normally."""
    cursor = connection.cursor()
    primary = None
    rows = None
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    except BaseException as exc:
        primary = exc
    try:
        cursor.close()
    except BaseException as cleanup:
        if primary is not None:
            raise BaseExceptionGroup('statement and cursor cleanup', [primary, cleanup])
        raise
    if primary is not None:
        raise primary
    return rows


def observe(connection, branch, phase):
    parents = statement(connection, 'SELECT item_id,durability FROM inventory_item ORDER BY item_id')
    children = statement(connection, 'SELECT item_id,affix FROM item_affix ORDER BY item_id,affix')
    return {'branch': branch, 'phase': phase,
            'parents': parents, 'children': children,
            'in_transaction': connection.in_transaction}


def branch_run(sqlite3, branch, sql, checkpoints):
    connection = None
    primary = None
    try:
        connection = sqlite3.connect(':memory:', timeout=0, isolation_level=None,
                                     autocommit=sqlite3.LEGACY_TRANSACTION_CONTROL)
        require(connection.autocommit == sqlite3.LEGACY_TRANSACTION_CONTROL,
                'legacy control required')
        require(connection.isolation_level is None, 'isolation None required')
        require(not connection.in_transaction, 'unexpected initial transaction')
        statement(connection, 'PRAGMA foreign_keys=ON')
        foreign_keys = statement(connection, 'PRAGMA foreign_keys')
        statement(connection, 'PRAGMA recursive_triggers=OFF')
        recursive_triggers = statement(connection, 'PRAGMA recursive_triggers')
        require(foreign_keys == [(1,)], 'foreign key support/enabling required')
        require(recursive_triggers == [(0,)], 'recursive triggers must be off')
        checkpoints.append({'branch': branch, 'phase': 'configured',
                            'foreign_keys': foreign_keys,
                            'recursive_triggers': recursive_triggers,
                            'legacy_control': connection.autocommit == sqlite3.LEGACY_TRANSACTION_CONTROL,
                            'isolation_level': connection.isolation_level,
                            'in_transaction': connection.in_transaction})
        statement(connection, 'CREATE TABLE inventory_item(item_id INTEGER PRIMARY KEY,durability INTEGER NOT NULL)')
        statement(connection, 'CREATE TABLE item_affix(item_id INTEGER NOT NULL REFERENCES inventory_item(item_id) ON DELETE CASCADE,affix TEXT NOT NULL)')
        statement(connection, 'BEGIN')
        statement(connection, 'INSERT INTO inventory_item(item_id,durability) VALUES(41,8)')
        statement(connection, "INSERT INTO item_affix(item_id,affix) VALUES(41,'frost')")
        statement(connection, 'COMMIT')
        require(not connection.in_transaction, 'initialization did not finish')
        checkpoints.append(observe(connection, branch, 'baseline'))
        statement(connection, sql)
        checkpoints.append({'branch': branch, 'phase': 'save_completed',
                            'statement_completed': True,
                            'in_transaction': connection.in_transaction})
        require(not connection.in_transaction, 'save did not finish')
        checkpoints.append(observe(connection, branch, 'final'))
    except BaseException as exc:
        primary = exc
    cleanup = None
    if connection is not None:
        try:
            connection.close()
        except BaseException as exc:
            cleanup = exc
        else:
            checkpoints.append({'branch': branch, 'phase': 'closed', 'connection_closed': True})
    if primary is not None and cleanup is not None:
        raise BaseExceptionGroup('branch and connection cleanup', [primary, cleanup])
    if primary is not None:
        raise primary
    if cleanup is not None:
        raise cleanup


def main():
    output = {'python_version': '.'.join(map(str, sys.version_info[:3])),
              'sqlite_version': None, 'checkpoints': []}
    failed = False
    try:
        require(sys.version_info >= (3, 12), 'requires existing Python 3.12 or newer')
        import sqlite3
        output['sqlite_version'] = sqlite3.sqlite_version
        require(sqlite3.sqlite_version_info >= (3, 24, 0), 'requires SQLite UPSERT support')
        branch_run(sqlite3, 'replace',
                   'INSERT OR REPLACE INTO inventory_item(item_id,durability) VALUES(41,9)',
                   output['checkpoints'])
        branch_run(sqlite3, 'upsert',
                   'INSERT INTO inventory_item(item_id,durability) VALUES(41,9) ON CONFLICT(item_id) DO UPDATE SET durability=excluded.durability',
                   output['checkpoints'])
    except BaseException:
        failed = True
        traceback.print_exc(file=sys.stderr)
    # Preserve the observed prefix on failure. No PASS originates in the driver.
    print(json.dumps(output, ensure_ascii=True, allow_nan=False, sort_keys=True), flush=True)
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
