-- Toy ledger: times are integer UTC hours; event type and ID were cleaned upstream.
-- Here the cutoff is inclusive; D7 is eligibility + 168 elapsed hours.
-- :covered_through is the authoritative ledger watermark, not MAX(event_time).
WITH entrants AS (
    SELECT player_id, first_eligible, first_eligible + 168 AS deadline
    FROM eligible
    WHERE first_eligible <= :covered_through
),
observed AS (
    SELECT e.player_id, e.deadline,
           MIN(CASE WHEN u.event_hour BETWEEN e.first_eligible AND MIN(e.deadline,:covered_through)
                    AND u.ingest_hour <= :report_as_of
                    THEN u.event_hour END) AS unlock_hour
    FROM entrants AS e
    LEFT JOIN unlock_log AS u ON u.player_id=e.player_id
    GROUP BY e.player_id,e.deadline
)
SELECT COUNT(*) AS enrolled,
       SUM(CASE WHEN unlock_hour IS NOT NULL THEN 1 ELSE 0 END) AS known_unlocks,
       SUM(CASE WHEN deadline <= :covered_through THEN 1 ELSE 0 END) AS d7_mature,
       SUM(CASE WHEN deadline <= :covered_through AND unlock_hour IS NOT NULL THEN 1 ELSE 0 END) AS d7_unlocks
FROM observed
