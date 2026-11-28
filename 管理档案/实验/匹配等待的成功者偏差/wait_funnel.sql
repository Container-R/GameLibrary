WITH scoped AS (
  SELECT t.*, (@snapshot - t.entered >= @horizon) AS mature
  FROM tickets t
  WHERE t.entered >= @begin AND t.entered < @end AND t.entered <= @snapshot
), classified AS (
  SELECT s.variant, s.id, s.entered,
    CASE
      WHEN NOT s.mature THEN 'immature'
      WHEN e.at_s IS NOT NULL THEN e.outcome
      WHEN s.covered_through >= s.entered + @horizon
           AND s.coverage_observed_at <= @snapshot THEN 'pending_at_horizon'
      ELSE 'unknown'
    END AS status,
    e.at_s - s.entered AS elapsed
  FROM scoped s
  LEFT JOIN terminal e ON e.id = s.id
    AND e.at_s >= s.entered AND e.at_s <= s.entered + @horizon
    AND e.received_at <= @snapshot
), success_ranks AS (
  SELECT variant, elapsed,
         row_number() OVER (PARTITION BY variant ORDER BY elapsed, id) AS rank_no,
         count(*) OVER (PARTITION BY variant) AS n
  FROM classified WHERE status = 'ready'
), p95 AS (
  SELECT variant, elapsed AS p95_ready_seconds
  FROM success_ranks WHERE rank_no = (95 * n + 99) / 100
)
SELECT c.variant, count(*) AS entries,
       sum(status != 'immature') AS mature,
       sum(status = 'ready') AS ready,
       sum(status = 'cancel') AS cancel,
       sum(status = 'timeout') AS timeout,
       sum(status = 'failed') AS failed,
       sum(status = 'pending_at_horizon') AS pending_at_horizon,
       sum(status = 'unknown') AS unknown,
       sum(status = 'immature') AS immature,
       p95_ready_seconds
FROM classified c LEFT JOIN p95 p ON p.variant = c.variant
GROUP BY c.variant, p95_ready_seconds ORDER BY c.variant;
