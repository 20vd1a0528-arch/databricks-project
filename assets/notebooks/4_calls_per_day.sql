-- Question 4: Calls per Day
-- Stack graph showing calls grouped by date

SELECT
  DATE(r.start_time) AS call_date,
  COUNT(*) AS total_calls
FROM `dataplatform-prod`.thub_ai.ring_central_call_log AS r
WHERE ((LOWER(r.direction) = 'inbound' AND r.to_wellstreetId IS NOT NULL)
    OR (LOWER(r.direction) = 'outbound' AND r.from_wellstreetId IS NOT NULL))
  AND r.start_time IS NOT NULL
GROUP BY DATE(r.start_time)
ORDER BY call_date DESC;

