"""One-room SQLite capacity fixture; not a distributed room service."""
import sqlite3

def trial(guarded):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE room(id INTEGER PRIMARY KEY, used INTEGER, capacity INTEGER)")
    db.execute("INSERT INTO room VALUES (1, 3, 4)")
    # Both callers observed the same stale listing before either arrived.
    seen = [db.execute("SELECT capacity-used FROM room").fetchone()[0] for _ in range(2)]
    accepted = []
    for remaining in seen:
        if guarded:
            accepted.append(db.execute("UPDATE room SET used=used+1 WHERE id=1 AND used<capacity").rowcount == 1)
        else:
            accepted.append(remaining>0)
            if remaining>0: db.execute("UPDATE room SET used=used+1 WHERE id=1")
    return seen,accepted,db.execute("SELECT used FROM room").fetchone()[0]

a,b=trial(False),trial(True)
assert a==([1,1],[True,True],5) and b==([1,1],[True,False],4)
print("listing used as authorization:",a)
print("authoritative conditional admission:",b)
