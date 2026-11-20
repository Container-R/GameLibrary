"""SQLite save-fencing test. Runs only in an isolated temporary directory."""
import json
import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory

def trial(file, guarded):
    a = sqlite3.connect(file, isolation_level=None, timeout=0)
    b = sqlite3.connect(file, isolation_level=None, timeout=0)
    try:
        assert a.execute("PRAGMA journal_mode=WAL").fetchone() == ("wal",)
        a.executescript("""
            CREATE TABLE saves(id TEXT PRIMARY KEY, writer TEXT NOT NULL, epoch INTEGER NOT NULL CHECK(typeof(epoch)='integer' AND epoch>=0), body TEXT NOT NULL);
            CREATE TABLE receipts(id TEXT PRIMARY KEY);
            INSERT INTO saves VALUES ('player','A',17,'before');
        """)
        def read(conn):
            return {
                "save": list(conn.execute("SELECT writer,epoch,body FROM saves WHERE id='player'").fetchone()),
                "receipts": [x[0] for x in conn.execute("SELECT id FROM receipts ORDER BY id")],
            }
        def take(conn, writer, expected):
            assert conn.execute("UPDATE saves SET writer=?,epoch=epoch+1 WHERE id='player' AND epoch=? AND epoch<9223372036854775807", (writer,expected)).rowcount == 1
        def write(conn, writer, epoch, body, guard):
            if guard == "epoch":
                return conn.execute("UPDATE saves SET body=? WHERE id='player' AND writer=? AND epoch=?", (body,writer,epoch)).rowcount
            if guard == "writer":
                return conn.execute("UPDATE saves SET body=? WHERE id='player' AND writer=?", (body,writer)).rowcount
            return conn.execute("UPDATE saves SET body=? WHERE id='player'", (body,)).rowcount
        early = read(a)
        assert early["save"] == ["A",17,"before"]
        b.execute("BEGIN IMMEDIATE")
        take(b,"B",17)
        b.rollback()
        aborted = read(a)
        assert aborted == early
        b.execute("BEGIN IMMEDIATE")
        take(b,"B",17)
        try:
            a.execute("BEGIN IMMEDIATE")
        except sqlite3.OperationalError as ex:
            busy = ex.sqlite_errorname
        else:
            raise AssertionError("writer exclusion not observed")
        assert busy == "SQLITE_BUSY"
        b.commit()
        after_takeover = read(a)
        assert after_takeover["save"] == ["B",18,"before"]
        a.execute("BEGIN IMMEDIATE")
        a.execute("INSERT INTO receipts VALUES ('old-A')")
        a_rows = write(a,"A",17,"late-A","epoch" if guarded else "")
        if a_rows == 1:
            a.commit()
        else:
            a.rollback()
        after_old = read(b)
        assert after_old == ({"save":["B",18,"before"],"receipts":[]} if guarded else {"save":["B",18,"late-A"],"receipts":["old-A"]})
        b.execute("BEGIN IMMEDIATE")
        b_rows = write(b,"B",18,"current-B","epoch")
        assert b_rows == 1
        b.execute("INSERT INTO receipts VALUES ('new-B')")
        b.commit()
        after_new = read(a)
        assert after_new["save"] == ["B",18,"current-B"]
        take(b,"A",18)
        again = read(a)
        results = []
        for writer, epoch, guard in [("A",17,"writer"),("A",17,"epoch"),("A",19,"epoch")]:
            a.execute("BEGIN IMMEDIATE")
            rows = write(a,writer,epoch,f"request-{epoch}",guard)
            results.append({"guard":guard,"submitted_epoch":epoch,"rows":rows,"within_save":read(a)["save"]})
            a.rollback()
            assert read(b) == again
        assert [r["rows"] for r in results] == [1,0,1]
        return {"precheck":early,"aborted_takeover":aborted,"concurrent_writer":busy,
                "after_takeover_before_new_save":after_takeover,"old_rows":a_rows,"after_old":after_old,
                "new_rows":b_rows,"after_new":after_new,"writer_reused":again,"reused_writer_controls":results}
    finally:
        a.close()
        b.close()

def epoch_limit():
    max_epoch = 2**63 - 1
    with sqlite3.connect(":memory:", isolation_level=None) as db:
        db.execute("CREATE TABLE unchecked(epoch INTEGER NOT NULL)")
        db.execute("INSERT INTO unchecked VALUES (?)", (max_epoch,))
        db.execute("UPDATE unchecked SET epoch=epoch+1")
        unsafe_value, unsafe_type = db.execute("SELECT epoch, typeof(epoch) FROM unchecked").fetchone()
        assert unsafe_type == "real"
        db.execute("UPDATE unchecked SET epoch=epoch+1")
        assert db.execute("SELECT epoch FROM unchecked").fetchone()[0] == unsafe_value
        db.execute("CREATE TABLE checked(epoch INTEGER NOT NULL CHECK(typeof(epoch)='integer'))")
        db.execute("INSERT INTO checked VALUES (?)", (max_epoch - 1,))
        guards = [db.execute("UPDATE checked SET epoch=epoch+1 WHERE epoch<?", (max_epoch,)).rowcount
                  for _ in range(2)]
        assert guards == [1,0]
        final = list(db.execute("SELECT epoch,typeof(epoch) FROM checked").fetchone())
        assert final == [max_epoch,"integer"]
        return {"unchecked_overflow_type":unsafe_type,"unchecked_next_increment_stalls":True,
                "bounded_claim_rows":guards,"bounded_final":final}

with TemporaryDirectory() as tmp:
    result = {"sqlite":sqlite3.sqlite_version, "epoch_limit":epoch_limit()}
    for label, guarded in [("precheck_only",False),("epoch_guard",True)]:
        result[label] = trial(Path(tmp)/(label+".sqlite"), guarded)
print(json.dumps(result,indent=2))
