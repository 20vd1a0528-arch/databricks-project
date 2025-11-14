-- Question 1: Incoming vs Outgoing Calls
-- Stack graph showing inbound vs outbound calls

SELECT
  LOWER(r.direction) AS direction,
  COUNT(*) AS total_calls
FROM `dataplatform-prod`.thub_ai.ring_central_call_log AS r
WHERE (LOWER(r.direction) = 'inbound' AND r.to_wellstreetId IS NOT NULL)
   OR (LOWER(r.direction) = 'outbound' AND r.from_wellstreetId IS NOT NULL)
GROUP BY LOWER(r.direction)
ORDER BY direction;

