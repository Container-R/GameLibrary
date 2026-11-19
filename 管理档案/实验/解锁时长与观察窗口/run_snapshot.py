from pathlib import Path
import sqlite3
import json

con = sqlite3.connect(':memory:')
con.row_factory = sqlite3.Row
con.executescript('''
CREATE TABLE eligible(player_id TEXT PRIMARY KEY, first_eligible INT NOT NULL);
CREATE TABLE unlock_log(player_id TEXT, event_hour INT NOT NULL, ingest_hour INT NOT NULL);
INSERT INTO eligible VALUES
  ('a',0),('b',0),('c',0),('d',0),
  ('e',120),('f',120),('g',120),('h',120);
INSERT INTO unlock_log VALUES
  ('a',96,99),('b',144,146),('c',168,190),('d',169,170),
  ('a',96,105),('h',119,120);
''')
sql = Path(__file__).with_name('snapshot.sql').read_text()

def query(asof, cover):
    assert asof >= cover
    return dict(con.execute(sql,dict(report_as_of=asof, covered_through=cover)).fetchone())

rows = {
    # Watermark cannot pass an unreconciled hour 168 at issue time.
    "draft_before_partition_reconciliation": query(175,167),
    "reconciled_at_same_event_window": query(200,168),
}
assert rows["draft_before_partition_reconciliation"] == {
    "enrolled":8,"known_unlocks":2,"d7_mature":0,"d7_unlocks":0}
assert rows["reconciled_at_same_event_window"] == {
    "enrolled":8,"known_unlocks":3,"d7_mature":4,"d7_unlocks":3}
print(json.dumps(rows,indent=2))
