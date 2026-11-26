"""SQLite diagnostic: assign a finish by its occurrence time, not receipt time."""
import sqlite3

cx=sqlite3.connect(':memory:')
cx.execute("""CREATE TABLE delivery(
 event_id TEXT, match_id TEXT, occurred_utc TEXT, received_utc TEXT
)""")
# UTC text is canonical and fixed width in this probe; real pipelines should use
# typed timestamps and record trusted server vs. client provenance.
rows=[
 ('e-01','m-01','2026-11-24T23:56:00Z','2026-11-24T23:56:01Z'),
 ('e-02','m-02','2026-11-24T23:59:00Z','2026-11-25T00:07:00Z'),
 ('e-02','m-02','2026-11-24T23:59:00Z','2026-11-25T00:10:00Z'),
 ('e-03','m-03','2026-11-25T00:01:00Z','2026-11-25T00:01:02Z'),
 ('e-04','m-04','2026-11-24T23:58:00Z','2026-11-26T02:00:00Z'),
]
cx.executemany("INSERT INTO delivery VALUES (?,?,?,?)",rows)
assert not cx.execute("""SELECT event_id FROM delivery GROUP BY event_id
 HAVING COUNT(DISTINCT match_id)>1 OR COUNT(DISTINCT occurred_utc)>1""").fetchall()

before="2026-11-25T00:05:00Z"
refresh="2026-11-25T00:15:00Z"
backfill="2026-11-26T02:01:00Z"
days=("2026-11-24","2026-11-25")
def finish_counts(as_of, clock, dedupe):
    assert clock in ("occurred_utc","received_utc")
    # Use first receipt. Delivery retries share source ID and immutable payload.
    data=("SELECT event_id,MIN(occurred_utc) AS occurred_utc,"
          "MIN(received_utc) AS received_utc FROM delivery WHERE received_utc<=? GROUP BY event_id"
          if dedupe else "SELECT * FROM delivery WHERE received_utc<=?")
    rows=cx.execute(f"""WITH scoped AS ({data})
      SELECT substr({clock},1,10),count(*) FROM scoped GROUP BY 1""",(as_of,))
    real=dict(rows)
    return tuple(real.get(day,0) for day in days)

print("SQLite",sqlite3.sqlite_version,"days",days)
for label, t in (('initial',before),('refresh',refresh),('backfill',backfill)):
    print(label,t,"event day dedup",finish_counts(t,'occurred_utc',True),
          "receipt day dedup",finish_counts(t,'received_utc',True),
          "event day raw",finish_counts(t,'occurred_utc',False))
assert finish_counts(before,'occurred_utc',True)==(1,1)
assert finish_counts(refresh,'occurred_utc',True)==(2,1)
assert finish_counts(refresh,'received_utc',True)==(1,2)
assert finish_counts(refresh,'occurred_utc',False)==(3,1)
assert finish_counts(backfill,'occurred_utc',True)==(3,1)

cx.executescript("""
CREATE TABLE report_history (
  day TEXT, revision INTEGER, as_of TEXT, metric_version TEXT,
  matches INTEGER, status TEXT, reason TEXT,
  PRIMARY KEY(day,revision)
);
CREATE TABLE report_current (
  day TEXT PRIMARY KEY, revision INTEGER, as_of TEXT,
  FOREIGN KEY(day,revision) REFERENCES report_history(day,revision)
);
PRAGMA foreign_keys=ON;
""")
pday=days[0]
# Synthetic upstream checkpoints, not MAX(event_time) nor a streaming watermark.
# The release producer reports how far it has exported included data.
exports={
 before: ("2026-11-25T00:04:00Z","2026-11-24T23:55:00Z"),
 refresh: ("2026-11-25T00:12:00Z","2026-11-24T23:58:00Z"),
 "2026-11-25T01:00:00Z": ("2026-11-25T00:51:00Z","2026-11-25T00:17:00Z"),
}
boundary="2026-11-25T00:00:00Z"
seal="2026-11-25T01:00:00Z"
def status_at(t, visible_checkpoints=None):
    ready = exports[t] if visible_checkpoints is None else visible_checkpoints
    return 'sealed' if t>=seal and min(ready)>=boundary else 'provisional'
assert status_at(seal,(exports[seal][0],exports[refresh][1]))=='provisional'
print('seal time but one visible checkpoint behind:',status_at(seal,(exports[seal][0],exports[refresh][1])))

def publish(rev,t,n,status,reason):
    expected=(t,"finish-v1",n,status,reason)
    with cx:
        found=cx.execute("""SELECT as_of,metric_version,matches,status,reason
          FROM report_history WHERE day=? AND revision=?""",(pday,rev)).fetchone()
        if found is not None:
            if found!=expected:
                raise ValueError("changed payload under same version")
            return
        current=cx.execute("SELECT revision,as_of FROM report_current WHERE day=?",(pday,)).fetchone()
        if current and (rev<=current[0] or t<=current[1]):
            raise ValueError("new version must advance revision and data cutoff")
        cx.execute("""INSERT INTO report_history VALUES (?,?,?,?,?,?,?)
          ON CONFLICT(day,revision) DO NOTHING""",(pday,rev,*expected))
        actual=cx.execute("""SELECT as_of,metric_version,matches,status,reason
          FROM report_history WHERE day=? AND revision=?""",(pday,rev)).fetchone()
        if actual!=expected:
            raise ValueError("changed payload under same version")
        cx.execute("""INSERT INTO report_current VALUES (?,?,?)
          ON CONFLICT(day) DO UPDATE SET revision=excluded.revision, as_of=excluded.as_of
          WHERE excluded.revision>report_current.revision
          AND excluded.as_of>report_current.as_of""",(pday,rev,t))

publish(1,before,finish_counts(before,'occurred_utc',True)[0],status_at(before),'initial')
publish(2,refresh,finish_counts(refresh,'occurred_utc',True)[0],status_at(refresh),'late event + 1 retry')
publish(3,seal,finish_counts(seal,'occurred_utc',True)[0],status_at(seal),'cutoff and exports ready')
assert status_at(before)==status_at(refresh)=='provisional' and status_at(seal)=='sealed'
print("after seal and later receipt (before approved backfill):",
      cx.execute("SELECT revision FROM report_current").fetchone()[0])
publish(4,backfill,finish_counts(backfill,'occurred_utc',True)[0],'revised','tracked late backfill')
publish(2,refresh,2,'provisional','late event + 1 retry') # stale job delivery
publish(4,backfill,3,'revised','tracked late backfill') # idempotent retry
try:
    publish(4,backfill,4,'revised','bad payload under same revision')
except ValueError as exc:
    print("conflicting retry rejected:",exc)
else:
    raise AssertionError('expected conflicting retry rejection')
try:
    publish(5,refresh,2,'provisional','late job with fresh revision but stale data')
except ValueError as exc:
    print("stale input rejected:",exc)
else:
    raise AssertionError('expected stale input rejection')
got=cx.execute("""SELECT revision,matches,status,reason FROM report_history
                  ORDER BY revision""").fetchall()
print('historical snapshots:',got)
print('current:',cx.execute("SELECT revision,as_of FROM report_current").fetchone())
assert [i[:3] for i in got]==[(1,1,'provisional'),(2,2,'provisional'),
                             (3,2,'sealed'),(4,3,'revised')]
assert cx.execute("SELECT revision FROM report_current").fetchone()==(4,)
