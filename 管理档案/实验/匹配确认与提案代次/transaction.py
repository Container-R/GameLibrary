import json, sqlite3, tempfile
from pathlib import Path

def row(db, stmt, args=()):
    return db.execute(stmt,args).fetchone()

with tempfile.TemporaryDirectory() as temp:
    p=Path(temp)/"demo.sqlite"
    db=sqlite3.connect(p,isolation_level=None,timeout=0)
    peer=sqlite3.connect(p,isolation_level=None,timeout=0)
    db.executescript("""
      CREATE TABLE proposal(id TEXT PRIMARY KEY, phase TEXT, deadline INTEGER);
      CREATE TABLE roster(proposal TEXT, player TEXT, ticket TEXT, PRIMARY KEY(proposal,player));
      CREATE TABLE active(ticket TEXT PRIMARY KEY, proposal TEXT);
      CREATE TABLE acceptance(proposal TEXT, player TEXT, PRIMARY KEY(proposal,player));
      CREATE TABLE outbox(proposal TEXT PRIMARY KEY);
      CREATE TABLE receipt(proposal TEXT, player TEXT, ticket TEXT, op TEXT,
        PRIMARY KEY(proposal,player,ticket,op));
      INSERT INTO receipt VALUES ('P1','A','TA','a1');
      INSERT INTO proposal VALUES ('P1','expired',100),('P2','confirming',200);
      INSERT INTO active VALUES ('TA','P2'),('TC','P2');
      INSERT INTO roster VALUES ('P1','A','TA'),('P1','B','TB'),('P2','A','TA'),('P2','C','TC');
      INSERT INTO acceptance VALUES ('P1','A');
    """)
    def accept_conn(con,ticket,player,pid,t,op,*,rollback=False):
        con.execute("BEGIN IMMEDIATE")
        receipt = row(con,"SELECT 1 FROM receipt WHERE proposal=? AND player=? AND ticket=? AND op=?", (pid,player,ticket,op))
        if receipt:
            con.commit()
            return "replay:"+pid
        valid=row(con, """SELECT 1 FROM proposal p JOIN active a ON a.proposal=p.id
          JOIN roster r ON r.proposal=p.id AND r.ticket=a.ticket
          WHERE a.ticket=? AND r.player=? AND p.id=? AND p.phase='confirming' AND ?<p.deadline""",
          (ticket,player,pid,t))
        if valid:
            con.execute("INSERT OR IGNORE INTO acceptance VALUES (?,?)",(pid,player))
            ready = row(con,"""UPDATE proposal SET phase='ready'
              WHERE id=? AND phase='confirming' AND NOT EXISTS(
                SELECT 1 FROM roster r WHERE r.proposal=proposal.id AND NOT EXISTS(
                  SELECT 1 FROM acceptance a WHERE a.proposal=r.proposal AND a.player=r.player))
              RETURNING id""",(pid,))
            if ready:
                con.execute("INSERT INTO outbox VALUES (?)",(pid,))
        if valid:
            con.execute("INSERT INTO receipt VALUES (?,?,?,?)",(pid,player,ticket,op))
        if rollback:
            con.rollback()
        else:
            con.commit()
        return ("accepted:" if valid else "rejected:")+pid
    out=[]
    def snap(label):
        out.append([label,row(db,"SELECT phase FROM proposal WHERE id='P2'")[0],
            [r[0] for r in db.execute("SELECT player FROM acceptance WHERE proposal='P2' ORDER BY player")],
            [r[0] for r in db.execute("SELECT proposal FROM outbox ORDER BY proposal")],
            [r[0] for r in db.execute("SELECT op FROM receipt WHERE proposal='P2' ORDER BY op")]])
    assert accept_conn(db,"TA","A","P1",130,"a1") == "replay:P1"
    assert accept_conn(db,"TA","A","P1",131,"a1-new") == "rejected:P1"
    assert accept_conn(db,"TC","C","P2",150,"c2") == "accepted:P2"
    assert accept_conn(db,"TC","C","P2",151,"c2") == "replay:P2"
    snap("old P1 did not count for P2; duplicate C counts once")
    assert accept_conn(db,"TA","A","P2",160,"a2",rollback=True) == "accepted:P2"
    snap("rollback removes final accept AND allocation intent")
    db.execute("BEGIN IMMEDIATE")
    busy = None
    try:
        accept_conn(peer,"TA","A","P2",160,"a2")
    except sqlite3.OperationalError as e:
        busy=e.sqlite_errorname
    finally:
        db.rollback()
    assert busy=="SQLITE_BUSY",busy
    assert accept_conn(peer,"TA","A","P2",161,"a2") == "accepted:P2"
    assert accept_conn(db,"TA","A","P2",162,"a2") == "replay:P2"
    snap("one allocation intent after committed final decision")
    expected=[
      ["old P1 did not count for P2; duplicate C counts once","confirming",["C"],[],["c2"]],
      ["rollback removes final accept AND allocation intent","confirming",["C"],[],["c2"]],
      ["one allocation intent after committed final decision","ready",["A","C"],["P2"],["a2","c2"]]]
    assert out==expected,out
    print(json.dumps({"sqlite":sqlite3.sqlite_version,"writer_conflict":busy,"steps":out},indent=2))
