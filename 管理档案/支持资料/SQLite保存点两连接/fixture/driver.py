"""Frozen three-case SQL observation. Preparation only; not yet executed."""
import sys
if sys.version_info[:2] != (3, 12):
    raise RuntimeError("requires Python 3.12 series")
import json
import sqlite3
from pathlib import Path

records = []

def sql(conn, statement):
    cur = conn.execute(statement)
    try:
        return cur.fetchall()
    finally:
        cur.close()

def checkpoint(case, phase, w, r):
    # Both SELECT cursors have been exhausted and closed before returning.
    wr = sql(w, "SELECT id, qty FROM inventory ORDER BY id")
    rr = sql(r, "SELECT id, qty FROM inventory ORDER BY id")
    if len(wr) != 1 or len(rr) != 1 or wr[0][0] != 1 or rr[0][0] != 1:
        raise RuntimeError("unexpected business row shape")
    records.append(dict(case=case, phase=phase, writer_qty=wr[0][1],
                        reader_qty=rr[0][1], writer_in_transaction=w.in_transaction,
                        reader_in_transaction=r.in_transaction))

def run_case(case):
    path = Path(case + ".sqlite")
    if path.exists() or path.is_symlink():
        raise RuntimeError("database must be fresh")
    w = r = None
    failures = []
    try:
        # cache=private explicitly excludes a shared-cache connection.
        uri = "file:" + path.name + "?cache=private"
        opts = dict(uri=True, timeout=1.0, isolation_level=None,
                    autocommit=sqlite3.LEGACY_TRANSACTION_CONTROL)
        w = sqlite3.connect(uri, **opts)
        if sql(w, "PRAGMA journal_mode=DELETE") != [("delete",)]:
            raise RuntimeError("DELETE mode not established")
        sql(w, "PRAGMA read_uncommitted=0")
        sql(w, "CREATE TABLE inventory(id INTEGER PRIMARY KEY, qty INTEGER NOT NULL)")
        sql(w, "INSERT INTO inventory VALUES(1, 10)")
        r = sqlite3.connect(uri, **opts)
        sql(r, "PRAGMA read_uncommitted=0")
        for conn in (w, r):
            if sql(conn, "PRAGMA journal_mode") != [("delete",)]:
                raise RuntimeError("journal mode mismatch")
            if sql(conn, "PRAGMA read_uncommitted") != [(0,)]:
                raise RuntimeError("read isolation mismatch")
            if conn.in_transaction:
                raise RuntimeError("unexpected setup transaction")
        checkpoint(case, "baseline", w, r)
        if case in ("A", "B"):
            sql(w, "BEGIN")
            sql(w, "UPDATE inventory SET qty=20 WHERE id=1")
            checkpoint(case, "outer_update", w, r)
            sql(w, "SAVEPOINT helper")
            sql(w, "UPDATE inventory SET qty=30 WHERE id=1")
            checkpoint(case, "inner_update", w, r)
            if case == "B":
                sql(w, "ROLLBACK TO helper")
                checkpoint(case, "rollback_to", w, r)
            sql(w, "RELEASE helper")
            checkpoint(case, "inner_release", w, r)
            sql(w, "ROLLBACK" if case == "A" else "COMMIT")
            checkpoint(case, "outer_rollback" if case == "A" else "outer_commit", w, r)
        else:
            sql(w, "SAVEPOINT helper")
            sql(w, "UPDATE inventory SET qty=40 WHERE id=1")
            checkpoint(case, "before_outermost_release", w, r)
            sql(w, "RELEASE helper")
            checkpoint(case, "outermost_release", w, r)
    except BaseException as exc:
        exc.add_note("case " + case + ": SQL/setup/checkpoint failure")
        failures.append(exc)
    finally:
        for label, conn in (("reader", r), ("writer", w)):
            if conn is not None:
                try:
                    conn.close()
                except BaseException as exc:
                    exc.add_note("case " + case + ": " + label + " close failure")
                    failures.append(exc)
    if failures:
        # Preserve the original failure and every cleanup failure in local stderr.
        raise BaseExceptionGroup("case failed", failures)

try:
    for case in ("A", "B", "C"):
        run_case(case)
except BaseException:
    print(json.dumps({"partial_checkpoints": records}, sort_keys=True), flush=True)
    raise
print(json.dumps({"python_version": ".".join(map(str, sys.version_info[:3])),
                  "sqlite_version": sqlite3.sqlite_version,
                  "checkpoints": records}, sort_keys=True))
