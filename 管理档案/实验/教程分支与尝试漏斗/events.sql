CREATE TABLE raw (
  arrival INTEGER PRIMARY KEY, player TEXT NOT NULL, attempt TEXT NOT NULL,
  version INTEGER NOT NULL, session TEXT NOT NULL, seq INTEGER NOT NULL,
  kind TEXT NOT NULL
);
INSERT INTO raw(player,attempt,version,session,seq,kind) VALUES
  ('A','a1',1,'s1',1,'begin'),('A','a1',1,'s1',2,'move'),('A','a1',1,'s1',3,'confirm'),
  ('B','b1',1,'s1',1,'begin'),('B','b1',1,'s1',2,'move_access'),('B','b1',1,'s1',3,'confirm'),
  ('C','c1',1,'s1',1,'begin'),('C','c1',1,'s2',4,'confirm'),('C','c1',1,'s1',2,'move'),
  ('C','c1',1,'s1',3,'back'),('C','c1',1,'s1',2,'move'),
  ('D','d1',1,'s1',1,'begin'),('D','d1',1,'s1',2,'move'),('D','d1',1,'s1',3,'restart_closed'),
  ('D','d2',1,'s1',1,'begin'),('D','d2',1,'s1',2,'confirm'),
  ('E','e1',1,'s1',1,'begin'),('E','e1',1,'s1',2,'confirm'),('E','e1',1,'s1',3,'move'),
  ('F','f1',1,'s1',1,'begin'),('F','f1',1,'s1',2,'skip'),
  ('G','g1',1,'s1',1,'begin'),('G','g1',1,'s1',2,'move'),('G','g1',1,'s1',2,'skip'),
  ('H','h1',1,'s1',1,'begin'),('H','h1',2,'s2',2,'move'),('H','h1',2,'s2',3,'confirm'),
  ('I','i1',1,'s1',1,'begin'),('I','i1',1,'s1',2,'move'),('I','i1',1,'s1',4,'confirm');

CREATE VIEW per_attempt AS
WITH RECURSIVE
 bad AS (
   SELECT player,attempt FROM raw GROUP BY player,attempt HAVING count(DISTINCT version)>1
   UNION
   SELECT player,attempt FROM raw GROUP BY player,attempt,seq HAVING count(DISTINCT kind)>1
   UNION
   SELECT player,attempt FROM raw GROUP BY player,attempt
     HAVING min(seq)<>1 OR max(seq)<>count(DISTINCT seq)
 ),
 clean AS (
   SELECT DISTINCT r.player,r.attempt,r.seq,r.kind
   FROM raw r WHERE NOT EXISTS (
     SELECT 1 FROM bad b WHERE b.player=r.player AND b.attempt=r.attempt)
 ),
 ordered AS (
   SELECT *,row_number() OVER (PARTITION BY player,attempt ORDER BY seq) AS n
   FROM clean
 ),
 walks(player,attempt,n,last_n,state) AS (
   SELECT player,attempt,0,max(n),'unstarted' FROM ordered GROUP BY player,attempt
   UNION ALL
   SELECT w.player,w.attempt,e.n,w.last_n,CASE
      WHEN w.state IN ('completed','skipped','closed') THEN w.state
      WHEN w.state='unstarted' AND e.kind='begin' THEN 'waiting_move'
      WHEN w.state<>'unstarted' AND e.kind='skip' THEN 'skipped'
      WHEN w.state<>'unstarted' AND e.kind='restart_closed' THEN 'closed'
      WHEN w.state='waiting_move' AND e.kind IN ('move','move_access') THEN 'waiting_confirm'
      WHEN w.state='waiting_confirm' AND e.kind='confirm' THEN 'completed'
      ELSE w.state END
   FROM walks w JOIN ordered e
     ON e.player=w.player AND e.attempt=w.attempt AND e.n=w.n+1
 )
 SELECT player,attempt,CASE WHEN state LIKE 'waiting_%' THEN 'open' ELSE state END AS outcome
 FROM walks WHERE n=last_n
 UNION ALL
 SELECT player,attempt,'unknown' AS outcome FROM bad;

-- These simplified comparators use synthetic global receive order that is correct
-- for A,B,D,E,F but not for delayed C. Their occurred order is supplied below by
-- a small fixture mapping, not inferred from per-attempt sequence across attempts.
CREATE VIEW observed_order AS
 SELECT *,CASE arrival WHEN 8 THEN 11 WHEN 9 THEN 8 WHEN 10 THEN 9 WHEN 11 THEN 10 ELSE arrival END AS logical
 FROM raw WHERE player IN ('A','B','C','D','E','F');
CREATE VIEW by_account AS
 SELECT DISTINCT b.player FROM observed_order b
 JOIN observed_order m ON b.player=m.player AND b.logical<m.logical AND m.kind IN ('move','move_access')
 JOIN observed_order c ON m.player=c.player AND m.logical<c.logical AND c.kind='confirm'
 WHERE b.kind='begin';
CREATE VIEW by_session AS
 SELECT DISTINCT b.player FROM observed_order b
 JOIN observed_order m ON b.player=m.player AND b.session=m.session AND b.logical<m.logical
                    AND m.kind IN ('move','move_access')
 JOIN observed_order c ON m.player=c.player AND m.session=c.session AND m.logical<c.logical
                    AND c.kind='confirm'
 WHERE b.kind='begin';
