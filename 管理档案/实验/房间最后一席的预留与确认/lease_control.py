"""Synthetic authority clock; SQLite transactions on two real connections."""
from contextlib import contextmanager
import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory

CAPACITY = 4

@contextmanager
def write(db):
    db.execute("BEGIN IMMEDIATE")
    try:
        yield
        db.execute("COMMIT")
    except BaseException:
        db.execute("ROLLBACK")
        raise

def counts(db, now):
    return db.execute("""SELECT
      COUNT(*) FILTER(WHERE state='active'),
      COUNT(*) FILTER(WHERE state='reserved' AND deadline>?)
      FROM seats""", (now,)).fetchone()

def reserve_locked(db, player, lease_id, now):
    db.execute("""UPDATE seats SET state='expired'
                  WHERE state='reserved' AND deadline<=?""", (now,))
    exact = db.execute("SELECT player,state FROM seats WHERE id=?", (lease_id,)).fetchone()
    if exact:
        return exact[1] if exact[0] == player else "wrong_player"
    existing = db.execute("SELECT id FROM seats WHERE player=? AND state IN ('reserved','active')",
                          (player,)).fetchone()
    if existing:
        return "different_live_request"
    if sum(counts(db, now)) >= CAPACITY:
        return "full"
    db.execute("INSERT INTO seats VALUES(?,?,?,?)", (lease_id, player, "reserved", now+10))
    return "reserved"

def reserve(db, player, lease_id, now):
    with write(db):
        return reserve_locked(db, player, lease_id, now)

def confirm(db, player, lease_id, now):
    with write(db):
        if db.execute("""UPDATE seats SET state='active'
          WHERE id=? AND player=? AND state='reserved' AND deadline>?""",
                      (lease_id, player, now)).rowcount:
            return "joined"
        exact = db.execute("SELECT player,state FROM seats WHERE id=?", (lease_id,)).fetchone()
        return "already_active" if exact == (player, "active") else "invalid"

def expire(db, player, lease_id, now):
    with write(db):
        return db.execute("""UPDATE seats SET state='expired'
          WHERE id=? AND player=? AND state='reserved' AND deadline<=?""",
                          (lease_id, player, now)).rowcount

def open_pair(name):
    with TemporaryDirectory() as path:
        file = Path(path, name + ".db")
        a,b = (sqlite3.connect(file, timeout=0, isolation_level=None) for _ in range(2))
        try:
            a.executescript("""
              CREATE TABLE seats(id TEXT PRIMARY KEY, player TEXT NOT NULL,
                state TEXT NOT NULL CHECK(state IN ('reserved','active','expired')),
                deadline INTEGER);
              CREATE UNIQUE INDEX one_seat_per_player ON seats(player)
                WHERE state IN ('reserved','active');
              INSERT INTO seats VALUES ('p1','p1','active',NULL),
                       ('p2','p2','active',NULL),('p3','p3','active',NULL);
            """)
            yield a,b
        finally:
            a.close()
            b.close()

case = contextmanager(open_pair)

print("SQLite", sqlite3.sqlite_version, "two connections, deterministic overlap")
with case("race") as (a,b):
    assert counts(a,0) == counts(b,0) == (3,0)
    with write(a):
        assert reserve_locked(a,"A","A1",0) == "reserved"
        try:
            reserve(b,"B","B1",0)
        except sqlite3.OperationalError as exc:
            assert exc.sqlite_errorcode == sqlite3.SQLITE_BUSY
            print("two stale reads of 3; B sees BUSY during A's write (not full)")
        else:
            raise AssertionError("B should contend with A")
    assert reserve(b,"B","B1",0) == "full"
    assert reserve(a,"A","A1",1) == "reserved" and counts(b,1) == (3,1)
    assert confirm(a,"A","A1",9) == "joined" and counts(b,9) == (4,0)
    assert expire(b,"A","A1",11) == 0 and counts(b,11) == (4,0)
    assert confirm(a,"A","A1",30) == "already_active"
    print("B retry full; A retry keeps one seat; confirm (3,1)->(4,0); old timeout changes 0 rows; repeat confirm stays active")

with case("renew") as (a,b):
    assert reserve(a,"A","A1",0) == "reserved"
    assert confirm(a,"A","A1",10) == "invalid"   # exactly expired
    assert reserve(a,"A","A2",10) == "reserved"
    assert expire(b,"A","A1",11) == 0
    assert counts(b,11) == (3,1)
    assert confirm(a,"A","A2",12) == "joined"
    print("A1 invalid at deadline; replacement A2 survives old cleanup and admits A")

with case("reassign") as (a,b):
    assert reserve(a,"A","A1",0) == "reserved"
    assert reserve(b,"B","B1",9) == "full"
    assert reserve(b,"B","B1",10) == "reserved"   # eligibility not tied to callback delivery
    assert confirm(a,"A","A1",11) == "invalid"
    assert confirm(b,"B","B1",11) == "joined" and counts(b,11) == (4,0)
    print("old hold ceases at boundary even if timer is late; B admitted, late A rejected")
