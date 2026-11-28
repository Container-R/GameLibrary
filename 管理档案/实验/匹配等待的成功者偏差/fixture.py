import json
from pathlib import Path
import sqlite3

con = sqlite3.connect(':memory:')
con.row_factory = sqlite3.Row
con.executescript("""
CREATE TABLE tickets(
    id TEXT PRIMARY KEY, variant TEXT NOT NULL, entered INTEGER NOT NULL,
    covered_through INTEGER, coverage_observed_at INTEGER
);
CREATE TABLE terminal(
    id TEXT PRIMARY KEY REFERENCES tickets(id),
    outcome TEXT CHECK(outcome IN ('ready','cancel','timeout','failed')) NOT NULL,
    at_s INTEGER NOT NULL, received_at INTEGER NOT NULL CHECK(received_at >= at_s)
);
""")
sql = Path(__file__).with_name('wait_funnel.sql').read_text()
def put(var, i, outcome, duration, entered=0, covered=None,
        coverage_observed=None, received=None):
    key = var + str(i)
    con.execute("INSERT INTO tickets VALUES(?,?,?,?,?)",
                (key, var, entered, covered, coverage_observed))
    if outcome:
        at = entered + duration
        con.execute("INSERT INTO terminal VALUES(?,?,?,?)",
                    (key, outcome, at, at if received is None else received))

def report(start, end, at):
    rows = [dict(r) for r in con.execute(sql, {'begin':start,'end':end,
                                               'snapshot':at,'horizon':60})]
    for r in rows:
        parts = ('ready','cancel','timeout','failed','pending_at_horizon','unknown')
        assert sum(r[k] for k in parts) == r['mature']
        assert r['mature'] + r['immature'] == r['entries']
    return rows

for var, batches in (
    ('A', ((70,'ready',20),(10,'ready',45),(10,'ready',75),(5,'cancel',40),(5,'timeout',60))),
    ('B', ((70,'ready',20),(20,'cancel',40),(10,'timeout',60))),
):
    i = 0
    for count, outcome, duration in batches:
        for _ in range(count):
            put(var,i,outcome,duration,covered=60,coverage_observed=80)
            i += 1
rows = report(0,1,100)
a,b = rows
assert (a['p95_ready_seconds'],b['p95_ready_seconds']) == (45,20)
assert (a['ready'],b['ready']) == (80,70)
assert (a['pending_at_horizon'],b['pending_at_horizon']) == (10,0)
print(json.dumps({'main':rows}, sort_keys=True))

# Events exactly at W count, but event time and arrival are different.
put('edge', 1, 'ready', 60, entered=100, received=190)
put('edge', 2, None, None, entered=100, covered=160, coverage_observed=170)
put('edge', 3, 'ready', 10, entered=155)
put('edge', 4, 'failed', 18, entered=100)
put('edge', 5, 'ready', 61, entered=100, covered=160, coverage_observed=170)
put('edge', 6, 'ready', 1, entered=200)  # cohort endpoint excluded
frozen = report(100,200,170)[0]
mature = report(100,200,220)[0]
assert (frozen['entries'], frozen['ready'], frozen['failed'],
        frozen['pending_at_horizon'], frozen['unknown'], frozen['immature']) == (5,0,1,2,1,1)
assert frozen['p95_ready_seconds'] is None
assert (mature['ready'],mature['failed'],mature['pending_at_horizon'],
        mature['unknown'],mature['immature'],mature['p95_ready_seconds']) == (2,1,2,0,0,60)
print(json.dumps({'edge_170':frozen,'edge_220':mature}, sort_keys=True))
