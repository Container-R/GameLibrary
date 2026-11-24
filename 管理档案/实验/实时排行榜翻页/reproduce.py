"""SQLite leaderboard membership, shared rank and snapshot fixtures."""
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE boards (
  epoch INTEGER NOT NULL,
  player_id TEXT COLLATE BINARY NOT NULL,
  score INTEGER NOT NULL,
  PRIMARY KEY (epoch, player_id)
);
INSERT INTO boards VALUES
  (1,'A',100),(1,'B',90),(1,'C',80),(1,'D',70),
  (2,'A',100),(2,'B',65),(2,'C',110),(2,'D',70),
  (3,'A',100),(3,'B',90),(3,'C',90),(3,'D',80),(3,'E',80);
""")

print("SQLite", sqlite3.sqlite_version)

def check(name, query, expected, args=()):
    actual = db.execute(query, args).fetchall()
    assert actual == expected, (name, actual, expected)
    print(name, actual)
    return actual

order_by = " ORDER BY score DESC, player_id ASC "
after = "(score < ? OR (score = ? AND player_id > ?))"
before = "(score > ? OR (score = ? AND player_id < ?))"
base = "SELECT player_id,score FROM boards WHERE epoch = ?"

first = check("movement page 1 @epoch 1:", base + order_by + "LIMIT 2",
              [("A",100),("B",90)], (1,))
player, score = first[-1]
anchor = (score, score, player)
check("movement live OFFSET @epoch 2:", base + order_by + "LIMIT 2 OFFSET 2",
      [("D",70),("B",65)], (2,))
check("movement live keyset @epoch 2:", base + " AND " + after + order_by + "LIMIT 2",
      [("D",70),("B",65)], (2,*anchor))
check("movement pinned keyset @epoch 1:", base + " AND " + after + order_by + "LIMIT 2",
      [("C",80),("D",70)], (1,*anchor))

def ranked(inner_extra="", window_tie=""):
    return f"""WITH ranked AS (
      SELECT player_id,score,RANK() OVER (ORDER BY score DESC {window_tie}) AS shared_rank
      FROM boards WHERE epoch = 3 {inner_extra}
    )
    SELECT player_id,score,shared_rank FROM ranked"""

first = check("tie page 1:", ranked() + order_by + "LIMIT 2",
              [("A",100,1),("B",90,2)])
player, score, _ = first[-1]
anchor = (score,score,player)
second = check("tie page 2, shared rank over snapshot:", ranked() + " WHERE " + after + order_by + "LIMIT 2",
               [("C",90,2),("D",80,4)], anchor)
check("tie BUG: cursor filter before window:", ranked("AND " + after) + order_by + "LIMIT 2",
      [("C",90,1),("D",80,2)], anchor)
check("tie BUG: ID inside rank window:", ranked(window_tie=", player_id ASC") + " WHERE " + after + order_by + "LIMIT 2",
      [("C",90,3),("D",80,4)], anchor)
player, score, _ = second[-1]
check("tie page 3:", ranked() + " WHERE " + after + order_by + "LIMIT 2",
      [("E",80,4)], (score,score,player))

player, score, _ = second[0]
raw = check("tie previous page in reverse query order:", ranked() + " WHERE " + before +
      " ORDER BY score ASC, player_id DESC LIMIT 2", [("B",90,2),("A",100,1)],
      (score,score,player))
restored = list(reversed(raw))
assert restored == first
print("tie previous page in display order:", restored)

# Small non-SQL client-side ordering control: capture generation on request.
page2 = (17, 1, ["C", "D"])
shown = (18, 2, ["X", "A"])
naive = shown[2] + page2[2]
guarded = shown[2] + (page2[2] if shown[:2] == page2[:2] else [])
assert naive == ["X","A","C","D"] and guarded == ["X","A"]
print("refresh race (Python, not SQL): append without guard =", naive, "; with epoch/generation guard =", guarded)
same_epoch_reopened = (17, 2, ["A","B"])
assert same_epoch_reopened[0] == page2[0] and same_epoch_reopened[:2] != page2[:2]
print("same epoch reopened (Python): older generation rejected")
