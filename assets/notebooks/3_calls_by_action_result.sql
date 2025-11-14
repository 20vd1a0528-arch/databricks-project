-- Question 3: Calls by Action/Result
-- Stack graph showing calls grouped by action (3 values)

SELECT
  COALESCE(r.action, 'Unknown') AS action,
  COUNT(*) AS total_calls
FROM `dataplatform-prod`.thub_ai.ring_central_call_log AS r
WHERE ((LOWER(r.direction) = 'inbound' AND r.to_wellstreetId IS NOT NULL)
    OR (LOWER(r.direction) = 'outbound' AND r.from_wellstreetId IS NOT NULL))
GROUP BY r.action
ORDER BY total_calls DESC, action;

