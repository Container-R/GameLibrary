"""Single-period, non-paid, one SQLite writer, synthetic accepted run results."""
import sqlite3

conn = sqlite3.connect(":memory:")
conn.executescript("""
CREATE TABLE rule(activity TEXT, revision INTEGER, metric TEXT, goal INTEGER,
                  PRIMARY KEY(activity, revision));
INSERT INTO rule VALUES ('event-11',1,'kills',3),('event-11',2,'successes',2);
CREATE TABLE accepted_run(
  activity TEXT, player TEXT, run TEXT, seq INTEGER UNIQUE, kills INTEGER,
  success INTEGER CHECK(success IN(0,1)), PRIMARY KEY(activity, player, run));
CREATE TABLE history(activity TEXT, player TEXT, complete_from_start INTEGER,
                     PRIMARY KEY(activity, player));
CREATE TABLE old_counter(activity TEXT, player TEXT, kills INTEGER,
                         PRIMARY KEY(activity, player));
CREATE TABLE entitlement(
  activity TEXT, player TEXT, milestone TEXT, granted_under INTEGER,
  PRIMARY KEY(activity,player,milestone));
CREATE TABLE claim(
  activity TEXT, player TEXT, milestone TEXT,
  PRIMARY KEY(activity,player,milestone));
CREATE TABLE balance(player TEXT PRIMARY KEY, tokens INTEGER NOT NULL);
""")
ACT, SLOT, CUT = "event-11", "one-reward", 100

def emit(player, run, seq, kills, success):
    existing = conn.execute(
        "SELECT kills,success FROM accepted_run WHERE activity=? AND player=? AND run=?",
        (ACT, player, run)).fetchone()
    if existing is not None:
        if existing != (kills, success):
            raise ValueError("same run, conflicting accepted result")
        return False
    conn.execute("INSERT INTO accepted_run VALUES(?,?,?,?,?,?)",
                 (ACT, player, run, seq, kills, success))
    return True

def qualify(player, revision):
    conn.execute("INSERT INTO entitlement VALUES(?,?,?,?) ON CONFLICT DO NOTHING",
                 (ACT, player, SLOT, revision))

def claim(player, fail_after_insert=False):
    with conn:
        cur = conn.execute("""
          INSERT INTO claim SELECT activity,player,milestone FROM entitlement
          WHERE activity=? AND player=? AND milestone=? ON CONFLICT DO NOTHING
          """, (ACT, player, SLOT))
        if cur.rowcount:
            if fail_after_insert:
                raise RuntimeError("injected failure before credit")
            conn.execute("""
              INSERT INTO balance VALUES(?,10) ON CONFLICT(player)
              DO UPDATE SET tokens=tokens+10
              """, (player,))
        return bool(cur.rowcount)

def count_wins(player, through):
    complete = conn.execute(
        "SELECT complete_from_start FROM history WHERE activity=? AND player=?",
        (ACT, player)).fetchone()[0]
    if not complete:
        return None
    return conn.execute(
        """SELECT COALESCE(SUM(success),0) FROM accepted_run
           WHERE activity=? AND player=? AND seq<=?""",
        (ACT, player, through)).fetchone()[0]

def qualified(player):
    row = conn.execute(
        """SELECT granted_under FROM entitlement
           WHERE activity=? AND player=? AND milestone=?""",
        (ACT, player, SLOT)).fetchone()
    return row[0] if row else None

with conn:
    for player, kills, complete in (("A",4,1),("B",4,1),("C",2,1),("D",2,1),("E",2,0)):
        conn.execute("INSERT INTO old_counter VALUES(?,?,?)", (ACT,player,kills))
        conn.execute("INSERT INTO history VALUES(?,?,?)", (ACT,player,complete))
        if kills >= 3:
            qualify(player, 1)
    for spec in (("A","a1",1,4,1),("B","b1",2,2,1),("B","b2",3,2,1),
                 ("C","c1",4,2,1),("D","d1",5,1,1),("D","d2",6,1,1),
                 ("E","e-known",7,1,1)):
        assert emit(*spec)
    assert not emit("D","d2",8,1,1)
    try:
        emit("D","d2",9,1,0)
    except ValueError:
        print("conflicting retry rejected")
    else:
        raise AssertionError("conflicting retry accepted")

assert claim("A")
print("database SQLite", sqlite3.sqlite_version)
new_goal = conn.execute("SELECT goal FROM rule WHERE activity=? AND revision=2",
                        (ACT,)).fetchone()[0]
print("readonly preflight, cut=100:")
expected = dict(A=1,B=2,C=1,D=2,E=None)
for player, old_kills in conn.execute("SELECT player,kills FROM old_counter ORDER BY player"):
    wins = count_wins(player, CUT)
    assert wins == expected[player]
    old_rev = qualified(player)
    decision = ("keep_v1" if old_rev else "hold_for_review" if wins is None
                else "grant_v2" if wins >= new_goal else "continue_v2")
    print(f"{player}: old={old_kills} v2={wins} {decision}")
assert conn.execute("SELECT COUNT(*) FROM entitlement").fetchone()[0] == 2

with conn:
    for player in expected:
        wins = count_wins(player, CUT)
        if wins is not None and wins >= new_goal:
            qualify(player, 2)
assert [qualified(p) for p in expected] == [1,1,None,2,None]

# One result written after the captured ledger mark. Re-read over the prefix
# plus accepted catch-up before claiming, instead of guessing from old totals.
with conn:
    assert emit("C","c2",101,0,1)
    assert count_wins("C", CUT)==1 and count_wins("C", 101)==2
    qualify("C",2)
print("catch-up at seq=101: C 1 -> 2")
try:
    claim("D", fail_after_insert=True)
except RuntimeError:
    pass
else:
    raise AssertionError("injected failure did not run")
assert conn.execute("SELECT 1 FROM claim WHERE player='D'").fetchone() is None
assert conn.execute("SELECT 1 FROM balance WHERE player='D'").fetchone() is None
print("injected failure rolled back the claim before credit")
assert [claim(p) for p in expected] == [False, True, True, True, False]
assert [claim(p) for p in expected] == [False]*len(expected)
print("final budgets:", conn.execute("SELECT player,tokens FROM balance ORDER BY player").fetchall())
print("E missing coverage -> unresolved (not zero), A paid under v1 -> not sent again")
