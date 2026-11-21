"""Run a fully synthetic tutorial fixture in the standard library's real SQLite."""
from pathlib import Path
import json, sqlite3
here=Path(__file__).resolve().parent
with sqlite3.connect(":memory:") as db:
    db.executescript((here/"events.sql").read_text(encoding="utf-8"))
    actual=db.execute("SELECT * FROM per_attempt ORDER BY player,attempt").fetchall()
    assert actual == [
        ("A","a1","completed"),("B","b1","completed"),("C","c1","completed"),
        ("D","d1","closed"),("D","d2","open"),("E","e1","open"),("F","f1","skipped"),
        ("G","g1","unknown"),("H","h1","unknown"),("I","i1","unknown"),
    ], actual
    def players(view):
        return [p for (p,) in db.execute("SELECT player FROM "+view+" ORDER BY player")]
    account=players("by_account")
    session=players("by_session")
    authoritative=[p for p,a,status in actual if status=="completed"]
    assert account==["A","B","C","D"] and session==["A","B","D"] and authoritative==["A","B","C"]
    db.execute("INSERT INTO raw(player,attempt,version,session,seq,kind) VALUES ('I','i1',1,'s1',3,'skip')")
    after=db.execute("SELECT outcome FROM per_attempt WHERE player='I' AND attempt='i1'").fetchone()[0]
    assert after=="skipped"
    print(json.dumps(dict(sqlite=sqlite3.sqlite_version,attempts=actual,
        ordered_by_account=account,ordered_in_session=session,correct_players=authoritative, i_after_late_skip=after),indent=2))
