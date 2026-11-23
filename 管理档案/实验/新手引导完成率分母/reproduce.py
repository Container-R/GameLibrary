#!/usr/bin/env python3
"""SQLite reproduction of a tutorial-entry selection reversal; no dependencies."""
import sqlite3

WINDOW = 100
FIRST_REPORT = 120
MATURE_REPORT = 150

PLAYER_STATE = """
WITH
  visible_events AS (
    SELECT a.player_id, e.kind, e.event_ts
    FROM assignment a JOIN event e USING (player_id)
    WHERE e.event_ts >= a.assigned_ts
      AND e.event_ts < a.assigned_ts + :window
      AND e.received_ts <= :as_of
  ),
  entry AS (
    SELECT player_id, MIN(event_ts) AS first_ts FROM visible_events
    WHERE kind='enter' GROUP BY player_id
  ),
  completion AS (
    SELECT v.player_id, MIN(v.event_ts) AS first_ts
    FROM visible_events v JOIN entry t USING (player_id)
    WHERE v.kind='complete' AND t.first_ts <= v.event_ts
    GROUP BY v.player_id
  ),
  per_player AS (
    SELECT a.player_id, a.arm, a.skill, a.pre_eligible,
           CASE WHEN o.first_ts IS NOT NULL THEN 1
                WHEN a.assigned_ts + :window > :as_of
                     OR c.complete_through IS NULL
                     OR c.complete_through < a.assigned_ts + :window
                     OR c.certified_at > :as_of THEN NULL
                ELSE 0 END AS completed,
           CASE WHEN t.first_ts IS NOT NULL THEN 1
                WHEN a.assigned_ts + :window > :as_of
                     OR c.complete_through IS NULL
                     OR c.complete_through < a.assigned_ts + :window
                     OR c.certified_at > :as_of THEN NULL
                ELSE 0 END AS entered
    FROM assignment a
    LEFT JOIN entry t USING (player_id)
    LEFT JOIN completion o USING (player_id)
    LEFT JOIN event_coverage c ON c.player_id=a.player_id
  )
"""

SUMMARY = """
SELECT arm, COUNT(*) AS assigned,
       COALESCE(SUM(entered=1),0) AS entered,
       COALESCE(SUM(completed=1),0) AS completed,
       COUNT(*)-COUNT(completed) AS completion_unknown
FROM per_player
GROUP BY arm ORDER BY arm
"""

def read(db, query, as_of=FIRST_REPORT):
    return db.execute(PLAYER_STATE + query, {"window": WINDOW, "as_of": as_of}).fetchall()

def populate(db):
    db.executescript("""
      CREATE TABLE assignment(
        player_id TEXT PRIMARY KEY, arm TEXT, skill TEXT,
        pre_eligible INTEGER, assigned_ts INTEGER);
      CREATE TABLE event(
        player_id TEXT, delivery_event_id TEXT, kind TEXT,
        event_ts INTEGER, received_ts INTEGER);
      CREATE TABLE event_coverage(
        player_id TEXT PRIMARY KEY, complete_through INTEGER, certified_at INTEGER);
    """)
    for arm in ("A", "B"):
        for skill in ("experienced", "new"):
            for i in range(50):
                player = f"{arm}/{skill}/{i:02d}"
                # Established before assignment, defined identically in both arms.
                # Only pre-eligible newcomers are gated away from entry in B.
                eligible = skill == "experienced" or i >= 10
                db.execute("INSERT INTO assignment VALUES (?,?,?,?,0)", (player, arm, skill, eligible))
                db.execute("INSERT INTO event_coverage VALUES (?,?,?)", (player, WINDOW, WINDOW))
                entered = arm == "A" or skill == "experienced" or not eligible
                completed = i < 40 if skill == "experienced" else i % 5 == 0
                if entered:
                    db.execute("INSERT INTO event VALUES (?,?,'enter',20,21)", (player, player + "/e"))
                if entered and completed:
                    db.execute("INSERT INTO event VALUES (?,?,'complete',90,91)", (player, player + "/c"))
    # A retry plus duplicate completion delivery: a raw join now counts 2×3 rows for one B player.
    for kind, n in (("enter", 1), ("complete", 2)):
        for _ in range(n):
            db.execute("""
              INSERT INTO event SELECT * FROM event
              WHERE player_id='B/experienced/00' AND kind=? LIMIT 1
            """, (kind,))

def main():
    db = sqlite3.connect(":memory:")
    populate(db)
    print(f"SQLite {sqlite3.sqlite_version}")
    expected = [("A", 100, 100, 50, 0), ("B", 100, 60, 42, 0)]
    rows = read(db, SUMMARY)
    assert rows == expected
    for arm, assigned, entered, completed, unknown in rows:
        print(f"{arm}: {completed}/{assigned} assigned ({completed/assigned:.0%}), "
              f"{completed}/{entered} entrants ({completed/entered:.0%}), unknown={unknown}")
    strata = read(db, """
      SELECT arm, skill, SUM(entered=1), SUM(completed=1)
      FROM per_player GROUP BY arm, skill ORDER BY arm, skill
    """)
    assert strata == [("A","experienced",50,40),("A","new",50,10),
                      ("B","experienced",50,40),("B","new",10,2)]
    for arm, skill, entered, completed in strata:
        print(f"{arm}/{skill}: {completed}/{entered} ({completed/entered:.0%})")
    groups = read(db, """
      SELECT pre_eligible, arm, COUNT(*), SUM(completed=1)
      FROM per_player GROUP BY pre_eligible, arm ORDER BY pre_eligible DESC, arm
    """)
    assert groups == [(1,"A",90,48),(1,"B",90,40),(0,"A",10,2),(0,"B",10,2)]
    for eligible, arm, assigned, completed in groups:
        print(f"{arm} pre_eligible={eligible}: {completed}/{assigned} assigned")
    raw = db.execute("""
      SELECT COUNT(*), COUNT(c.delivery_event_id)
      FROM assignment a JOIN event e ON e.player_id=a.player_id AND e.kind='enter'
      LEFT JOIN event c ON c.player_id=a.player_id AND c.kind='complete'
      WHERE a.arm='B'
    """).fetchone()
    assert raw == (65,47)
    print(f"B naive event join: {raw[1]}/{raw[0]} rows; deduplicated: 42/60 players")

    db.execute("SAVEPOINT timestamp_controls")
    db.executemany("INSERT INTO event VALUES (?,?,?,?,?)", [
        ("A/experienced/00", "early-but-valid-later", "complete", 10, 11),
        ("B/new/11", "before-assignment", "enter", -1, 1),
        ("A/new/01", "outside-horizon", "complete", 100, 101),
        ("A/new/02", "before-entry-only", "complete", 10, 11),
        ("B/new/11", "within-horizon-but-no-entry", "complete", 20, 21),
    ])
    assert read(db, SUMMARY) == expected
    db.execute("ROLLBACK TO timestamp_controls")
    db.execute("RELEASE timestamp_controls")
    print("time/sequence controls: pre-assignment entry, pre-entry completion and horizon boundary excluded")

    # One previously known success is ingested after the first report cutoff;
    # one newly assigned account has not yet had the full follow-up window.
    db.execute("UPDATE event SET received_ts=130 WHERE player_id='B/new/00' AND kind='complete'")
    db.execute("UPDATE event_coverage SET certified_at=130 WHERE player_id='B/new/00'")
    db.execute("UPDATE assignment SET assigned_ts=40 WHERE player_id='B/new/49'")
    db.execute("UPDATE event_coverage SET complete_through=140, certified_at=150 WHERE player_id='B/new/49'")
    b = read(db, SUMMARY)[1]
    assert b == ("B",100,60,41,2)
    print("B at t=120: 41 confirmed completions, 57 known non-completions, 2 unknown; bounds 41–43%")
    assert read(db, SUMMARY, as_of=MATURE_REPORT) == expected
    print("B at t=150: 42 confirmed completions, 58 known non-completions, 0 unknown")

if __name__ == "__main__":
    main()
