-- Question 2: Total Calls per Clinic
-- Stack graph showing calls grouped by clinic/facility

SELECT
  c.facilityName AS facility_name,
  CASE
    WHEN LOWER(r.direction) = 'inbound' THEN r.to_wellstreetId
    WHEN LOWER(r.direction) = 'outbound' THEN r.from_wellstreetId
  END AS wellstreetId,
  COUNT(*) AS total_calls
FROM `dataplatform-prod`.thub_ai.ring_central_call_log AS r
INNER JOIN `dataplatform-prod`.wellstreet.dfd_centers AS c
  ON c.centerId = CASE
                    WHEN LOWER(r.direction) = 'inbound' THEN r.to_wellstreetId
                    WHEN LOWER(r.direction) = 'outbound' THEN r.from_wellstreetId
                  END
WHERE ((LOWER(r.direction) = 'inbound' AND r.to_wellstreetId IS NOT NULL)
    OR (LOWER(r.direction) = 'outbound' AND r.from_wellstreetId IS NOT NULL))
GROUP BY
  c.facilityName,
  CASE
    WHEN LOWER(r.direction) = 'inbound' THEN r.to_wellstreetId
    WHEN LOWER(r.direction) = 'outbound' THEN r.from_wellstreetId
  END
ORDER BY total_calls DESC, facility_name;

