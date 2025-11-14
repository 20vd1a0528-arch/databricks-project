-- Comprehensive Visits Analytics Query
-- All metrics in one query for visualization with VisitType as single column

WITH filtered_visits AS (
    SELECT
        v.dfdVisitId,
        v.dfdCenterId,
        TO_DATE(v.appointmentDate, 'yyyy-MM-dd') AS appointmentDate,
        v.startTimeInMins,
        v.appointmentType AS reasonForAppointment,
        CASE WHEN v.channel = 'Employee' THEN 'Walk-In' ELSE 'BookAhead' END AS appointmentChannel,
        v.isTelemedVisit,
        v.isFollowUpVisit,
        -- VisitType: Telemed or Other (in one column)
        CASE 
            WHEN LOWER(v.isTelemedVisit) = 'true' THEN 'Telemed'
            ELSE 'Other'
        END AS visitType,
        v.currentStatusCode AS currentStatus,
        v.patientWaitTime,
        v.delayTime.delayedByInMinutes AS delayedByInMinutes,
        v.isAttended,
        v.isNewVisit,
        v.centerInfo.providerName AS providerName,
        v.reasonForCancellation AS reasonForCancellation, 
        v.visitTime,
        v.timezone,
        c.facilityName,
        c.facilityType,
        c.orgName,
        c.isActive,
        c.isAvailableForPatient
    FROM `dataplatform-prod`.wellstreet.dfd_visits v
    INNER JOIN `dataplatform-prod`.wellstreet.dfd_centers c
        ON v.dfdCenterId = c.centerId
    WHERE TO_DATE(v.appointmentDate, 'yyyy-MM-dd') >= '2025-01-01'
),

-- Total Visits per Clinic
total_visits AS (
    SELECT 
        facilityName,
        COUNT(DISTINCT dfdVisitId) AS total_visits
    FROM filtered_visits
    GROUP BY facilityName
),

-- Visits by Type (Telemed or Other) - in one column
visits_by_type AS (
    SELECT
        facilityName,
        visitType,
        COUNT(DISTINCT dfdVisitId) AS visit_count
    FROM filtered_visits
    GROUP BY facilityName, visitType
),

-- Completed vs Cancelled Visits (in one column)
status_summary AS (
    SELECT
        facilityName,
        currentStatus AS status,
        COUNT(DISTINCT dfdVisitId) AS status_count
    FROM filtered_visits
    WHERE LOWER(currentStatus) IN ('completed', 'cancelled')
    GROUP BY facilityName, currentStatus
),

-- Cancellation Rate
cancellation_rate AS (
    SELECT
        facilityName,
        ROUND(
            (SUM(CASE WHEN LOWER(currentStatus) = 'cancelled' THEN 1 ELSE 0 END) * 100.0) / COUNT(*),
            2
        ) AS cancellation_rate
    FROM filtered_visits
    GROUP BY facilityName
),

-- Top Cancellation Reasons (aggregated - top 5 reasons per facility)
top_cancellation_reasons AS (
    SELECT
        facilityName,
        COLLECT_LIST(STRUCT(reasonForCancellation, reason_count)) AS top_reasons
    FROM (
        SELECT
            facilityName,
            reasonForCancellation,
            COUNT(*) AS reason_count,
            ROW_NUMBER() OVER (PARTITION BY facilityName ORDER BY COUNT(*) DESC) AS reason_rank
        FROM filtered_visits
        WHERE reasonForCancellation IS NOT NULL 
            AND reasonForCancellation != ''
            AND LOWER(currentStatus) = 'cancelled'
        GROUP BY facilityName, reasonForCancellation
    ) ranked
    WHERE reason_rank <= 5
    GROUP BY facilityName
),

-- Time from Scheduling to Completion (in minutes)
avg_time_completion AS (
    SELECT
        facilityName,
        ROUND(AVG(CAST(patientWaitTime AS DOUBLE)), 2) AS avg_wait_time_minutes
    FROM filtered_visits
    WHERE patientWaitTime IS NOT NULL
    GROUP BY facilityName
),

-- New vs Returning Patients (in one column)
patient_type AS (
    SELECT
        facilityName,
        CASE 
            WHEN LOWER(isNewVisit) = 'true' THEN 'New'
            ELSE 'Returning'
        END AS patient_category,
        COUNT(DISTINCT dfdVisitId) AS patient_count
    FROM filtered_visits
    GROUP BY facilityName, 
        CASE 
            WHEN LOWER(isNewVisit) = 'true' THEN 'New'
            ELSE 'Returning'
        END
),

-- Visits per Provider
visits_per_provider AS (
    SELECT
        facilityName,
        providerName,
        COUNT(DISTINCT dfdVisitId) AS total_visits_per_provider
    FROM filtered_visits
    WHERE providerName IS NOT NULL AND providerName != ''
    GROUP BY facilityName, providerName
),

-- PCP Involvement (commented out - uncomment if pcp field exists in schema)
-- pcp_involvement AS (
--     SELECT
--         facilityName,
--         SUM(CASE WHEN v.pcp IS NOT NULL AND v.pcp != '' THEN 1 ELSE 0 END) AS visits_with_pcp,
--         COUNT(*) AS total_visits,
--         ROUND(
--             (SUM(CASE WHEN v.pcp IS NOT NULL AND v.pcp != '' THEN 1 ELSE 0 END) * 100.0) / COUNT(*),
--             2
--         ) AS pcp_involvement_percent
--     FROM filtered_visits v
--     GROUP BY facilityName
-- )

-- Main query combining all metrics
SELECT
    t.facilityName,
    t.total_visits,
    v.visitType,
    v.visit_count,
    s.status,
    s.status_count,
    c.cancellation_rate,
    a.avg_wait_time_minutes,
    p.patient_category,
    p.patient_count,
    pp.providerName,
    pp.total_visits_per_provider
    -- pi.pcp_involvement_percent  -- Uncomment if pcp_involvement CTE is enabled
FROM total_visits t
LEFT JOIN visits_by_type v ON t.facilityName = v.facilityName
LEFT JOIN status_summary s ON t.facilityName = s.facilityName
LEFT JOIN cancellation_rate c ON t.facilityName = c.facilityName
LEFT JOIN top_cancellation_reasons tc ON t.facilityName = tc.facilityName
LEFT JOIN avg_time_completion a ON t.facilityName = a.facilityName
LEFT JOIN patient_type p ON t.facilityName = p.facilityName
LEFT JOIN visits_per_provider pp ON t.facilityName = pp.facilityName
-- LEFT JOIN pcp_involvement pi ON t.facilityName = pi.facilityName  -- Uncomment if pcp_involvement CTE is enabled
ORDER BY t.total_visits DESC, v.visitType, s.status, p.patient_category;
