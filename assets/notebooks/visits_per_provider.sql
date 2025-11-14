-- Visits per Provider by Facility
-- Returns visit counts for each provider per facility

WITH filtered_visits AS (
    SELECT
        v.dfdVisitId,
        v.dfdCenterId,
        TO_DATE(v.appointmentDate, 'yyyy-MM-dd') AS appointmentDate,
        v.centerInfo.providerName AS providerName,
        c.facilityName
    FROM `dataplatform-prod`.wellstreet.dfd_visits v
    INNER JOIN `dataplatform-prod`.wellstreet.dfd_centers c
        ON v.dfdCenterId = c.centerId
    WHERE TO_DATE(v.appointmentDate, 'yyyy-MM-dd') >= '2025-01-01'
        AND v.centerInfo.providerName IS NOT NULL 
        AND v.centerInfo.providerName != ''
)

SELECT
    facilityName,
    providerName,
    COUNT(DISTINCT dfdVisitId) AS total_visits,
    ROUND(
        (COUNT(DISTINCT dfdVisitId) * 100.0) / SUM(COUNT(DISTINCT dfdVisitId)) OVER (PARTITION BY facilityName),
        2
    ) AS provider_percentage,
    ROW_NUMBER() OVER (PARTITION BY facilityName ORDER BY COUNT(DISTINCT dfdVisitId) DESC) AS provider_rank
FROM filtered_visits
GROUP BY facilityName, providerName
ORDER BY facilityName, total_visits DESC;

