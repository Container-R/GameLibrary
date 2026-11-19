"""Single-writer SQLite fixture: one player, one earned-material goal."""
import json
import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory

CAP = 10

def connect(path):
    db = sqlite3.connect(path)
    db.executescript("""
      CREATE TABLE IF NOT EXISTS receipt(
        attempt_id TEXT PRIMARY KEY, track TEXT NOT NULL,
        qualified INTEGER NOT NULL, natural INTEGER NOT NULL);
      CREATE TABLE IF NOT EXISTS progress(
        track TEXT PRIMARY KEY, misses INTEGER NOT NULL CHECK(misses BETWEEN 0 AND 9));
      CREATE TABLE IF NOT EXISTS award(
        attempt_id TEXT PRIMARY KEY, track TEXT NOT NULL, cause TEXT NOT NULL);
    """)
    return db

def misses(db, track):
    row = db.execute("SELECT misses FROM progress WHERE track=?", (track,)).fetchone()
    return 0 if row is None else row[0]

def settle(db, attempt, track, *, qualified, natural=False):
    # Pending is not a settlement. The trusted verifier may confirm it later.
    if qualified is None:
        return "pending"
    if natural and not qualified:
        raise ValueError("an ineligible attempt cannot award the material")
    with db:
        record = (track, int(qualified), int(natural))
        previous = db.execute(
            "SELECT track,qualified,natural FROM receipt WHERE attempt_id=?", (attempt,)
        ).fetchone()
        if previous is not None:
            if previous != record:
                return "conflict"
            return "duplicate"
        db.execute("INSERT INTO receipt VALUES(?,?,?,?)", (attempt, *record))
        if not qualified:
            return "ineligible"
        count = misses(db, track) + 1
        cause = "natural" if natural else "guarantee" if count == CAP else None
        if cause is not None:
            db.execute("INSERT INTO award VALUES(?,?,?)", (attempt, track, cause))
        db.execute(
            "INSERT INTO progress VALUES(?,?) ON CONFLICT(track) DO UPDATE SET misses=excluded.misses",
            (track, 0 if cause else count),
        )
        return cause or "progress"

if __name__ == "__main__":
    with TemporaryDirectory() as d:
        path = Path(d) / "reward.sqlite3"
        a, b = "map-material:v1", "map-material:v2"
        db = connect(path)
        assert all(settle(db, f"try{i}", a, qualified=True) == "progress" for i in range(1, 10))
        db.close()
        db = connect(path)
        observed = {"after_reopen": misses(db,a)}
        observed["duplicate_ninth"] = settle(db, "try9", a, qualified=True)
        observed["conflicting_replay"] = settle(db, "try9", b, qualified=True)
        observed["final_ineligible"] = settle(db, "final-rejected", a, qualified=False)
        observed["disconnected_pending"] = settle(db, "try10", a, qualified=None)
        observed["before_pending_confirms"] = misses(db,a)
        observed["new_track_starts_at"] = misses(db,b)
        observed["tenth_qualified"] = settle(db, "try10", a, qualified=True)
        db.close()
        db = connect(path)
        observed["duplicate_tenth_after_reopen"] = settle(db, "try10", a, qualified=True)
        observed["award_rows"] = db.execute("SELECT count(*) FROM award").fetchone()[0]
        observed["after_award"] = misses(db,a)
        assert settle(db,"new-track-1",b,qualified=True) == "progress"
        observed["early_natural"] = settle(db,"new-track-2",b,qualified=True,natural=True)
        observed["new_track_after_natural"] = misses(db,b)
        db.close()
    assert observed == {
        "after_reopen": 9, "duplicate_ninth": "duplicate", "conflicting_replay": "conflict",
        "final_ineligible": "ineligible", "disconnected_pending": "pending",
        "before_pending_confirms": 9, "new_track_starts_at": 0,
        "tenth_qualified": "guarantee", "duplicate_tenth_after_reopen": "duplicate",
        "award_rows": 1, "after_award": 0, "early_natural": "natural", "new_track_after_natural": 0,
    }
    print(json.dumps(observed, indent=2))
