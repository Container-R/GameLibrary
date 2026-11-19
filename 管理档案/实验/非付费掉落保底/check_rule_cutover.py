"""Separate immutable attempt rules from an equivalent storage-only rename."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from check_qualified_progress import connect, misses, settle

def migrate_equivalent(db, migration_id, old, new):
    """Offline while no new writes can use the old storage format."""
    with db:
        seen = db.execute("SELECT source, target FROM migration WHERE id=?", (migration_id,)).fetchone()
        if seen is not None:
            if seen != (old, new):
                raise ValueError("migration identifier reused")
            return "already_applied"
        if db.execute("SELECT 1 FROM progress WHERE track=?", (new,)).fetchone():
            raise ValueError("destination already has progress")
        db.execute("UPDATE progress SET track=? WHERE track=?", (new, old))
        db.execute("INSERT INTO migration VALUES (?,?,?)", (migration_id, old, new))
    return "applied"

def open_case(path):
    db = connect(path)
    db.execute("CREATE TABLE IF NOT EXISTS migration(id TEXT PRIMARY KEY, source TEXT, target TEXT)")
    return db

def make_nine(db, track, prefix):
    for i in range(1, 10):
        assert settle(db, f"{prefix}{i}", track, qualified=True) == "progress"

def award_rows(db):
    return [list(row) for row in db.execute(
        "SELECT attempt_id,track,cause FROM award ORDER BY attempt_id")]

with TemporaryDirectory() as tmp:
    path = Path(tmp)
    db = open_case(path / "rules.sqlite")
    old, new = "amber:standard", "amber:expert"
    make_nine(db, old, "standard-")
    assert settle(db, "expert-1", new, qualified=True) == "progress"
    before_new = misses(db, new)
    # The trusted attempt was assigned the old rule before the cutover.
    assert settle(db, "standard-10", old, qualified=True) == "guarantee"
    db.close()
    db = open_case(path / "rules.sqlite")
    rules = {
        "new_rule_before_late_old_settlement": before_new,
        "identical_late_replay": settle(db, "standard-10", old, qualified=True),
        "replay_wrongly_reclassified": settle(db, "standard-10", new, qualified=True),
        "new_rule_after_both_replays": misses(db, new),
        "awards": award_rows(db),
    }
    db.close()

    db = open_case(path / "format.sqlite")
    make_nine(db, "formatA", "same-")
    assert migrate_equivalent(db, "A-to-B", "formatA", "formatB") == "applied"
    moved = misses(db, "formatB")
    db.close()
    db = open_case(path / "format.sqlite")
    assert settle(db, "same-9", "formatA", qualified=True) == "duplicate"
    assert settle(db, "same-10", "formatB", qualified=True) == "guarantee"
    fmt = {
        "moved_unconsumed": moved,
        "rerun_migration_after_award": migrate_equivalent(db, "A-to-B", "formatA", "formatB"),
        "counter_after_award_and_rerun": misses(db, "formatB"),
        "awards": award_rows(db),
    }
    db.close()

out = {"distinct_eligibility": rules, "equivalent_offline_format": fmt}
assert rules == {
    "new_rule_before_late_old_settlement": 1, "identical_late_replay": "duplicate",
    "replay_wrongly_reclassified": "conflict", "new_rule_after_both_replays": 1,
    "awards": [["standard-10", "amber:standard", "guarantee"]],
}
assert fmt == {
    "moved_unconsumed": 9, "rerun_migration_after_award": "already_applied",
    "counter_after_award_and_rerun": 0, "awards": [["same-10", "formatB", "guarantee"]],
}
print(json.dumps(out, indent=2))
