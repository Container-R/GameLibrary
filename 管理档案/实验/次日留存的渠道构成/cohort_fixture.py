import sqlite3
from fractions import Fraction as F
c=sqlite3.connect(':memory:')
c.executescript("""CREATE TABLE installs(id INTEGER PRIMARY KEY, version TEXT, channel TEXT, t0 INT);
CREATE TABLE opens(id INT, t INT); CREATE INDEX lookup ON opens(id,t);""")

def add(v,ch,t0,n,y):
    for i in range(n):
        id=c.execute("INSERT INTO installs(version,channel,t0) VALUES(?,?,?)",(v,ch,t0)).lastrowid
        offsets=(23,24,27,48) if i<y else (23,48)
        c.executemany("INSERT INTO opens VALUES(?,?)",((id,t0+k) for k in offsets))

for v,ch,n,y in [('A','organic',100,60),('A','campaign',900,180),
                 ('B','organic',900,495),('B','campaign',100,15)]:
    add(v,ch,100,n,y)
add('B','organic',470,10,10)
query="""WITH eligible AS (
  SELECT version, COALESCE(channel,'unknown') ch,
  EXISTS(SELECT 1 FROM opens o WHERE o.id=i.id AND o.t>=i.t0+24 AND o.t<i.t0+48) y
  FROM installs i WHERE i.t0+48<=:watermark
)
SELECT version,ch,SUM(y),COUNT(*) FROM eligible GROUP BY version,ch ORDER BY version,ch"""
def results(): return list(c.execute(query,{'watermark':500}))
expected=[('A','campaign',180,900),('A','organic',60,100),('B','campaign',15,100),('B','organic',495,900)]
baseline=results()
assert baseline==expected
print('SQLite',sqlite3.sqlite_version)
for row in baseline: print(*row)
for name,weights in [('A_mix',(F(9,10),F(1,10))),('even',(F(1,2),)*2)]:
    print(name, *(sum(w*F(y,n) for w,(_,_,y,n) in zip(weights,baseline[k:k+2])) for k in (0,2)))
add('B',None,100,20,17)
with_unknown=results()
assert with_unknown[-1]==('B','unknown',17,20)
a_channels={ch for v,ch,_,_ in with_unknown if v=='A'}
b_channels={ch for v,ch,_,_ in with_unknown if v=='B'}
common=a_channels & b_channels
assert common=={'organic','campaign'} and b_channels-a_channels=={'unknown'}
b_counts=[(ch,n) for v,ch,_,n in with_unknown if v=='B']
covered,total=sum(n for ch,n in b_counts if ch in common),sum(n for _,n in b_counts)
assert (covered,total)==(1000,1020)
print(f'B unknown=17/20; no A counterpart; common support is {covered}/{total} B accounts')
