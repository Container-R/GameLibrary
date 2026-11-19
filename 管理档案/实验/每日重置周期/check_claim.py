"""Synthetic one-player progress journal; all tables here live in one SQLite DB."""
from datetime import datetime
from bisect import bisect_right
import json,sqlite3


def time(s):
    return int(datetime.fromisoformat(s).timestamp())


schedule=[(time("2026-03-07T13:00:00+00:00"),"2026-03-07"),
          (time("2026-03-08T12:00:00+00:00"),"2026-03-08"),
          (time("2026-03-09T12:00:00+00:00"),None)]
times=[t for t,k in schedule]
db=sqlite3.connect(":memory:",isolation_level=None)
db.executescript("""
CREATE TABLE claim(player TEXT NOT NULL, rule TEXT NOT NULL, period TEXT NOT NULL,
                    request TEXT NOT NULL, PRIMARY KEY(player,rule,period),
                    UNIQUE(player,rule,request));
CREATE TABLE progress(player TEXT PRIMARY KEY, points INT NOT NULL);
INSERT INTO progress VALUES ('P1',0);
""")

def claim(server_time, requested_period, request, fail_before_effect=False):
    db.execute("BEGIN IMMEDIATE")
    try:
        prev=db.execute("SELECT period FROM claim WHERE player='P1' AND rule='daily' AND request=?",
                        (request,)).fetchone()
        if prev:
            result="same_request_receipt:"+prev[0] if prev[0]==requested_period else "changed_request_payload"
        else:
            i=bisect_right(times,server_time)-1
            period=schedule[i][1] if i>=0 else None
            if period is None:
                result="unknown_schedule"
            elif requested_period!=period:
                result="stale_period"
            else:
                new=db.execute("""INSERT INTO claim VALUES ('P1','daily',?,?)
                                  ON CONFLICT(player,rule,period) DO NOTHING""",(period,request))
                if not new.rowcount:
                    result="already_claimed_this_period"
                else:
                    if fail_before_effect:
                        raise RuntimeError("synthetic fault before progress update")
                    db.execute("UPDATE progress SET points=points+1 WHERE player='P1'")
                    result="committed:"+period
        db.execute("COMMIT")
        return result
    except RuntimeError:
        db.execute("ROLLBACK")
        return "rolled_back"
    except BaseException:
        db.execute("ROLLBACK")
        raise


prior,nextday="2026-03-07","2026-03-08"
t=times[1]
tests=[
  (t-1,prior,"a",False,"committed:"+prior),
  (t,prior,"a",False,"same_request_receipt:"+prior),
  (t,nextday,"a",False,"changed_request_payload"),
  (t,prior,"b",False,"stale_period"),
  (t,nextday,"c",True,"rolled_back"),
  (t,nextday,"c",False,"committed:"+nextday),
  (t+1,nextday,"d",False,"already_claimed_this_period"),
  (times[2],nextday,"e",False,"unknown_schedule")]
trace=[]
for now,p,k,fail,want in tests:
    res=claim(now,p,k,fail)
    assert res==want,(res,want)
    trace.append([now-t,p,k,res])
assert db.execute("SELECT points FROM progress").fetchone()==(2,)
assert db.execute("SELECT count(*) FROM claim").fetchone()==(2,)
print(json.dumps({"scope":"actual SQLite local transactions over synthetic intents",
 "time_relative_to_boundary":trace,"points":2,"claims":2},indent=2))
