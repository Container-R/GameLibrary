"""Review draft. Run only through launcher.py after separate authorization."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import traceback

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('local_isolation', HERE / 'isolation.py')
isolation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(isolation)
SEQ = 0


def emit(event, **data):
    global SEQ
    SEQ += 1
    print(json.dumps(dict(seq=SEQ, event=event, data=data), sort_keys=True), flush=True)


def require(ok, code):
    if not ok:
        raise RuntimeError(code)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    root = Path.cwd()
    isolation.validate_environment(os.environ, root)
    # The launcher must have prepared the five locations before this import.
    import sqlite3
    connections = []
    failure = None

    def connect(path):
        c = sqlite3.connect(path, timeout=0, isolation_level=None,
                            autocommit=sqlite3.LEGACY_TRANSACTION_CONTROL)
        connections.append(c)
        require(c.autocommit == sqlite3.LEGACY_TRANSACTION_CONTROL and
                c.isolation_level is None and not c.in_transaction, 'connection_transaction')
        query(c, 'PRAGMA busy_timeout=0')
        require(query(c, 'PRAGMA busy_timeout') == [(0,)], 'busy_timeout')
        return c

    def query(c, sql):
        cursor = c.execute(sql)
        try:
            return cursor.fetchall()
        finally:
            cursor.close()

    def rows(c):
        schema = query(c, 'PRAGMA table_info(save_item)')
        require(schema == [(0, 'id', 'INTEGER', 0, None, 1),
                           (1, 'qty', 'INTEGER', 1, None, 0)], 'schema')
        return query(c, 'SELECT id, qty FROM save_item ORDER BY id')

    def close(c, role):
        c.close()
        connections.remove(c)
        emit('closed', role=role)

    try:
        emit('begin', python=sys.version.split()[0], sqlite=sqlite3.sqlite_version)
        for name in ('source', 'plain', 'backup'):
            Path(name).mkdir(exist_ok=False)
        srcpath = Path('source/save.db')
        src = connect(srcpath)
        mode = query(src, 'PRAGMA journal_mode=WAL')
        require(mode == [('wal',)], 'wal_unsupported')
        query(src, 'PRAGMA wal_autocheckpoint=0')
        auto = query(src, 'PRAGMA wal_autocheckpoint')
        require(auto == [(0,)], 'autocheckpoint')
        emit('settings', journal_mode=mode, wal_autocheckpoint=auto,
             isolation_level=src.isolation_level, autocommit=src.autocommit, busy_timeout=0)
        query(src, 'BEGIN')
        query(src, 'CREATE TABLE save_item(id INTEGER PRIMARY KEY, qty INTEGER NOT NULL)')
        query(src, 'COMMIT')
        require(not src.in_transaction, 'schema_transaction_open')
        checkpoint = query(src, 'PRAGMA wal_checkpoint(TRUNCATE)')
        require(len(checkpoint) == 1 and len(checkpoint[0]) == 3 and
                all(type(x) is int for x in checkpoint[0]) and
                checkpoint[0][0] == 0 and checkpoint[0][1] >= 0 and
                checkpoint[0][1] == checkpoint[0][2], 'checkpoint')
        wal = Path('source/save.db-wal')
        require(wal.is_file() and wal.stat().st_size == 0, 'checkpoint_wal_not_empty')
        require(rows(src) == [], 'baseline_not_empty')
        baseline = digest(srcpath)
        emit('baseline', checkpoint=checkpoint, rows=[], main_sha256=baseline, wal_bytes=0)
        query(src, 'BEGIN')
        query(src, 'INSERT INTO save_item(id, qty) VALUES(1, 7)')
        query(src, 'COMMIT')
        require(not src.in_transaction, 'insert_transaction_open')
        actual = rows(src)
        require(actual == [(1, 7)], 'source_commit_rows')
        require(digest(srcpath) == baseline and wal.stat().st_size > 0, 'wal_only_condition')
        emit('committed', rows=actual, in_transaction=src.in_transaction,
             main_sha256=digest(srcpath), wal_bytes=wal.stat().st_size)
        plainpath = Path('plain/save.db')
        with plainpath.open('xb') as f:
            f.write(srcpath.read_bytes())
        require(digest(plainpath) == baseline and digest(srcpath) == baseline, 'copy_identity')
        emit('main_copy', path=plainpath.as_posix(), sha256=digest(plainpath))
        plain = connect(plainpath)
        plainrows = rows(plain)
        require(plainrows == [], 'plain_rows')
        emit('plain_read', rows=plainrows)
        close(plain, 'plain')
        dest = connect(Path('backup/save.db'))
        require(not src.in_transaction and not dest.in_transaction, 'backup_transaction')
        progress = []

        def on_progress(status, remaining, total):
            progress.append([status, remaining, total])
            emit('backup_progress', status=status, remaining=remaining, total=total)
            require(len(progress) <= 16, 'backup_progress_limit')
            require(status in (sqlite3.SQLITE_OK, sqlite3.SQLITE_DONE), 'backup_status')
            require(0 <= remaining <= total, 'backup_counts')
            require(status != sqlite3.SQLITE_DONE or remaining == 0, 'backup_done_remaining')

        emit('backup_attempt', pages=1, name='main', sleep=0.0)
        src.backup(dest, pages=1, progress=on_progress, name='main', sleep=0.0)
        require(progress and progress[-1][0] == sqlite3.SQLITE_DONE and
                progress[-1][1] == 0 and not dest.in_transaction, 'backup_incomplete')
        emit('backup_return', progress_calls=len(progress))
        close(dest, 'backup_writer')
        reopened = connect(Path('backup/save.db'))
        backed = rows(reopened)
        require(backed == [(1, 7)], 'backup_rows')
        emit('backup_read', rows=backed)
        close(reopened, 'backup_reader')
        final = rows(src)
        require(final == [(1, 7)] and digest(srcpath) == baseline, 'source_final')
        emit('source_final', rows=final, main_sha256=digest(srcpath))
    except BaseException as exc:
        failure = exc
        Path('private-error.txt').write_text(traceback.format_exc(), encoding='utf-8')
        emit('failure', category=type(exc).__name__)
    finally:
        for c in list(reversed(connections)):
            try:
                close(c, 'remaining')
            except BaseException as exc:
                if failure is None:
                    failure = exc
                with Path('private-error.txt').open('a', encoding='utf-8') as f:
                    f.write(traceback.format_exc())
                emit('cleanup_failure', category=type(exc).__name__)
    if failure is not None:
        return 1
    emit('success', plain_rows=[], backup_rows=[[1, 7]], source_rows=[[1, 7]])
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        Path('private-error.txt').write_text(traceback.format_exc(), encoding='utf-8')
        emit('startup_failure', category=type(exc).__name__)
        sys.exit(1)
