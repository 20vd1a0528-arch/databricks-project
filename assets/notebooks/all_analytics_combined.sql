-- Combined Analytics Query
-- All 4 questions in one query for comprehensive analysis
-- Can be used to create multiple stack graphs from a single result set

SELECT
  -- Date dimension (for Calls per Day chart)
  DATE(r.start_time) AS call_date,
  
  -- Direction dimension (for Incoming vs Outgoing Calls chart)
  LOWER(r.direction) AS direction,
  
  -- Clinic dimension (for Total Calls per Clinic chart)
  c.facilityName AS facility_name,
  CASE
    WHEN LOWER(r.direction) = 'inbound' THEN r.to_wellstreetId
    WHEN LOWER(r.direction) = 'outbound' THEN r.from_wellstreetId
  END AS wellstreetId,
  
  -- Action dimension (for Calls by Action/Result chart - 3 values)
  COALESCE(r.actions, r.action, 'Unknown') AS action,
  
  -- Metric for stack graphs
  COUNT(*) AS call_count

FROM `dataplatform-prod`.thub_ai.ring_central_call_log AS r
INNER JOIN `dataplatform-prod`.wellstreet.dfd_centers AS c
  ON c.centerId = CASE
                    WHEN LOWER(r.direction) = 'inbound' THEN r.to_wellstreetId
                    WHEN LOWER(r.direction) = 'outbound' THEN r.from_wellstreetId
                  END

WHERE ((LOWER(r.direction) = 'inbound' AND r.to_wellstreetId IS NOT NULL)
    OR (LOWER(r.direction) = 'outbound' AND r.from_wellstreetId IS NOT NULL))
  AND r.start_time IS NOT NULL

GROUP BY
  DATE(r.start_time),
  LOWER(r.direction),
  c.facilityName,
  CASE
    WHEN LOWER(r.direction) = 'inbound' THEN r.to_wellstreetId
    WHEN LOWER(r.direction) = 'outbound' THEN r.from_wellstreetId
  END,
  COALESCE(r.actions, r.action)

ORDER BY
  call_date DESC,
  facility_name,
  direction,
  action;

