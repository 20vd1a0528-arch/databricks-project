-- Top Cancellation Reasons by Facility
-- Returns all cancellation reasons ranked by frequency per facility

WITH filtered_visits AS (
    SELECT
        v.dfdVisitId,
        v.dfdCenterId,
        TO_DATE(v.appointmentDate, 'yyyy-MM-dd') AS appointmentDate,
        v.reasonForCancellation,
        v.currentStatusCode AS currentStatus,
        c.facilityName
    FROM `dataplatform-prod`.wellstreet.dfd_visits v
    INNER JOIN `dataplatform-prod`.wellstreet.dfd_centers c
        ON v.dfdCenterId = c.centerId
    WHERE TO_DATE(v.appointmentDate, 'yyyy-MM-dd') >= '2025-01-01'
        AND LOWER(v.currentStatusCode) = 'cancelled'
        AND v.reasonForCancellation IS NOT NULL 
        AND v.reasonForCancellation != ''
)

SELECT
    facilityName,
    reasonForCancellation,
    COUNT(*) AS reason_count,
    ROUND(
        (COUNT(*) * 100.0) / SUM(COUNT(*)) OVER (PARTITION BY facilityName),
        2
    ) AS reason_percentage,
    ROW_NUMBER() OVER (PARTITION BY facilityName ORDER BY COUNT(*) DESC) AS reason_rank
FROM filtered_visits
GROUP BY facilityName, reasonForCancellation
ORDER BY facilityName, reason_count DESC;

