# Databricks notebook source
# MAGIC %md
# MAGIC # Visits Analytics Visualization
# MAGIC 
# MAGIC This notebook creates stack bar graphs for:
# MAGIC 1. VisitType: Telemed vs Other
# MAGIC 2. Completed vs Cancelled visits
# MAGIC 3. New vs Returning patients
# MAGIC 4. Visits per Provider
# MAGIC 5. Top Cancellation Reasons
# MAGIC 6. PCP Involvement

# COMMAND ----------

# Import required libraries
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Data

# COMMAND ----------

# Run the visits analytics query
query = """
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

-- Top Cancellation Reasons
top_cancellation_reasons AS (
    SELECT
        facilityName,
        reasonForCancellation,
        COUNT(*) AS reason_count
    FROM filtered_visits
    WHERE reasonForCancellation IS NOT NULL 
        AND reasonForCancellation != ''
        AND LOWER(currentStatus) = 'cancelled'
    GROUP BY facilityName, reasonForCancellation
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
)

-- Main query for base metrics
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
    p.patient_count
FROM total_visits t
LEFT JOIN visits_by_type v ON t.facilityName = v.facilityName
LEFT JOIN status_summary s ON t.facilityName = s.facilityName
LEFT JOIN cancellation_rate c ON t.facilityName = c.facilityName
LEFT JOIN avg_time_completion a ON t.facilityName = a.facilityName
LEFT JOIN patient_type p ON t.facilityName = p.facilityName
ORDER BY t.total_visits DESC, v.visitType, s.status, p.patient_category
"""

df = spark.sql(query).toPandas()

# Fill NaN values with 0
df = df.fillna(0)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Additional Data for Provider and Cancellation Reasons

# COMMAND ----------

# Query for visits per provider
provider_query = """
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
    COUNT(DISTINCT dfdVisitId) AS total_visits_per_provider
FROM filtered_visits
GROUP BY facilityName, providerName
ORDER BY facilityName, total_visits_per_provider DESC
"""

df_providers = spark.sql(provider_query).toPandas()

# Query for top cancellation reasons
cancellation_query = """
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
    COUNT(*) AS reason_count
FROM filtered_visits
GROUP BY facilityName, reasonForCancellation
ORDER BY facilityName, reason_count DESC
"""

df_cancellations = spark.sql(cancellation_query).toPandas()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. VisitType: Telemed vs Other (Stack Bar)

# COMMAND ----------

# Prepare data for VisitType stack bar chart
df_visit_type = df[['facilityName', 'visitType', 'visit_count']].copy()
df_visit_type = df_visit_type[df_visit_type['visit_count'] > 0]

# Get top facilities by total visits
facility_totals = df_visit_type.groupby('facilityName')['visit_count'].sum().reset_index()
facility_totals = facility_totals.sort_values('visit_count', ascending=False).head(20)
top_facilities = facility_totals['facilityName'].tolist()
df_visit_type = df_visit_type[df_visit_type['facilityName'].isin(top_facilities)]

# Create stacked bar chart
fig1 = px.bar(
    df_visit_type,
    x='facilityName',
    y='visit_count',
    color='visitType',
    title='VisitType: Telemed vs Other (Top 20 Facilities)',
    labels={'facilityName': 'Facility Name', 'visit_count': 'Number of Visits', 'visitType': 'Visit Type'},
    color_discrete_map={'Telemed': '#1f77b4', 'Other': '#ff7f0e'}
)
fig1.update_layout(
    xaxis_title='Facility Name',
    yaxis_title='Number of Visits',
    xaxis_tickangle=-45,
    barmode='stack',
    showlegend=True,
    height=600
)
fig1.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Completed vs Cancelled Visits (Stack Bar)

# COMMAND ----------

# Prepare data for completed vs cancelled
df_status = df[['facilityName', 'status', 'status_count']].copy()
df_status = df_status[df_status['status_count'] > 0]

# Get top facilities
facility_totals = df_status.groupby('facilityName')['status_count'].sum().reset_index()
facility_totals = facility_totals.sort_values('status_count', ascending=False).head(20)
top_facilities = facility_totals['facilityName'].tolist()
df_status = df_status[df_status['facilityName'].isin(top_facilities)]

# Create stacked bar chart
fig2 = px.bar(
    df_status,
    x='facilityName',
    y='status_count',
    color='status',
    title='Completed vs Cancelled Visits (Top 20 Facilities)',
    labels={'facilityName': 'Facility Name', 'status_count': 'Number of Visits', 'status': 'Status'},
    color_discrete_map={'Completed': '#2ca02c', 'Cancelled': '#d62728', 'completed': '#2ca02c', 'cancelled': '#d62728'}
)
fig2.update_layout(
    xaxis_title='Facility Name',
    yaxis_title='Number of Visits',
    xaxis_tickangle=-45,
    barmode='stack',
    showlegend=True,
    height=600
)
fig2.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. New vs Returning Patients (Stack Bar)

# COMMAND ----------

# Prepare data for new vs returning patients
df_patients = df[['facilityName', 'patient_category', 'patient_count']].copy()
df_patients = df_patients[df_patients['patient_count'] > 0]

# Get top facilities
facility_totals = df_patients.groupby('facilityName')['patient_count'].sum().reset_index()
facility_totals = facility_totals.sort_values('patient_count', ascending=False).head(20)
top_facilities = facility_totals['facilityName'].tolist()
df_patients = df_patients[df_patients['facilityName'].isin(top_facilities)]

# Create stacked bar chart
fig3 = px.bar(
    df_patients,
    x='facilityName',
    y='patient_count',
    color='patient_category',
    title='New vs Returning Patients (Top 20 Facilities)',
    labels={'facilityName': 'Facility Name', 'patient_count': 'Number of Patients', 'patient_category': 'Patient Type'},
    color_discrete_map={'New': '#9467bd', 'Returning': '#8c564b'}
)
fig3.update_layout(
    xaxis_title='Facility Name',
    yaxis_title='Number of Patients',
    xaxis_tickangle=-45,
    barmode='stack',
    showlegend=True,
    height=600
)
fig3.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Visits per Provider (Stack Bar)

# COMMAND ----------

# Prepare data for visits per provider
# Get top facilities first
top_facilities = df_providers.groupby('facilityName')['total_visits_per_provider'].sum().reset_index()
top_facilities = top_facilities.sort_values('total_visits_per_provider', ascending=False).head(10)
top_facility_names = top_facilities['facilityName'].tolist()

df_providers_filtered = df_providers[df_providers['facilityName'].isin(top_facility_names)].copy()

# For each facility, get top 10 providers
df_providers_top = df_providers_filtered.groupby('facilityName').head(10)

# Create stacked bar chart
fig4 = px.bar(
    df_providers_top,
    x='facilityName',
    y='total_visits_per_provider',
    color='providerName',
    title='Visits per Provider (Top 10 Facilities, Top 10 Providers per Facility)',
    labels={'facilityName': 'Facility Name', 'total_visits_per_provider': 'Number of Visits', 'providerName': 'Provider'},
    color_discrete_sequence=px.colors.qualitative.Set3
)
fig4.update_layout(
    xaxis_title='Facility Name',
    yaxis_title='Number of Visits',
    xaxis_tickangle=-45,
    barmode='stack',
    showlegend=True,
    height=600
)
fig4.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Top Cancellation Reasons (Stack Bar)

# COMMAND ----------

# Prepare data for top cancellation reasons
# Get top facilities first
top_facilities = df_cancellations.groupby('facilityName')['reason_count'].sum().reset_index()
top_facilities = top_facilities.sort_values('reason_count', ascending=False).head(10)
top_facility_names = top_facilities['facilityName'].tolist()

df_cancellations_filtered = df_cancellations[df_cancellations['facilityName'].isin(top_facility_names)].copy()

# For each facility, get top 5 cancellation reasons
df_cancellations_top = df_cancellations_filtered.groupby('facilityName').head(5)

# Create stacked bar chart
fig5 = px.bar(
    df_cancellations_top,
    x='facilityName',
    y='reason_count',
    color='reasonForCancellation',
    title='Top Cancellation Reasons (Top 10 Facilities, Top 5 Reasons per Facility)',
    labels={'facilityName': 'Facility Name', 'reason_count': 'Number of Cancellations', 'reasonForCancellation': 'Cancellation Reason'},
    color_discrete_sequence=px.colors.qualitative.Pastel
)
fig5.update_layout(
    xaxis_title='Facility Name',
    yaxis_title='Number of Cancellations',
    xaxis_tickangle=-45,
    barmode='stack',
    showlegend=True,
    height=600
)
fig5.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Cancellation Rate (Bar Chart)

# COMMAND ----------

# Prepare cancellation rate data
df_cancel_rate = df[['facilityName', 'cancellation_rate']].drop_duplicates()
df_cancel_rate = df_cancel_rate[df_cancel_rate['cancellation_rate'] > 0]
df_cancel_rate = df_cancel_rate.sort_values('cancellation_rate', ascending=False).head(20)

# Create bar chart
fig6 = px.bar(
    df_cancel_rate,
    x='facilityName',
    y='cancellation_rate',
    title='Cancellation Rate % (Top 20 Facilities)',
    labels={'facilityName': 'Facility Name', 'cancellation_rate': 'Cancellation Rate (%)'},
    color='cancellation_rate',
    color_continuous_scale='Reds'
)
fig6.update_layout(
    xaxis_title='Facility Name',
    yaxis_title='Cancellation Rate (%)',
    xaxis_tickangle=-45,
    height=600
)
fig6.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Average Wait Time (Bar Chart)

# COMMAND ----------

# Prepare average wait time data
df_wait_time = df[['facilityName', 'avg_wait_time_minutes']].drop_duplicates()
df_wait_time = df_wait_time[df_wait_time['avg_wait_time_minutes'] > 0]
df_wait_time = df_wait_time.sort_values('avg_wait_time_minutes', ascending=False).head(20)

# Create bar chart
fig7 = px.bar(
    df_wait_time,
    x='facilityName',
    y='avg_wait_time_minutes',
    title='Average Wait Time (Top 20 Facilities)',
    labels={'facilityName': 'Facility Name', 'avg_wait_time_minutes': 'Average Wait Time (minutes)'},
    color='avg_wait_time_minutes',
    color_continuous_scale='Blues'
)
fig7.update_layout(
    xaxis_title='Facility Name',
    yaxis_title='Average Wait Time (minutes)',
    xaxis_tickangle=-45,
    height=600
)
fig7.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. PCP Involvement (Stack Bar) - If Available
# MAGIC 
# MAGIC Note: Uncomment this section if PCP field exists in the schema

# COMMAND ----------

# Uncomment and modify if PCP field exists:
# pcp_query = """
# WITH filtered_visits AS (
#     SELECT
#         v.dfdVisitId,
#         v.dfdCenterId,
#         TO_DATE(v.appointmentDate, 'yyyy-MM-dd') AS appointmentDate,
#         v.pcp,
#         c.facilityName
#     FROM `dataplatform-prod`.wellstreet.dfd_visits v
#     INNER JOIN `dataplatform-prod`.wellstreet.dfd_centers c
#         ON v.dfdCenterId = c.centerId
#     WHERE TO_DATE(v.appointmentDate, 'yyyy-MM-dd') >= '2025-01-01'
# )
# SELECT
#     facilityName,
#     CASE 
#         WHEN pcp IS NOT NULL AND pcp != '' THEN 'With PCP'
#         ELSE 'Without PCP'
#     END AS pcp_status,
#     COUNT(DISTINCT dfdVisitId) AS visit_count
# FROM filtered_visits
# GROUP BY facilityName, 
#     CASE 
#         WHEN pcp IS NOT NULL AND pcp != '' THEN 'With PCP'
#         ELSE 'Without PCP'
#     END
# ORDER BY facilityName, pcp_status
# """
# 
# df_pcp = spark.sql(pcp_query).toPandas()
# 
# # Get top facilities
# top_facilities = df_pcp.groupby('facilityName')['visit_count'].sum().reset_index()
# top_facilities = top_facilities.sort_values('visit_count', ascending=False).head(20)
# top_facility_names = top_facilities['facilityName'].tolist()
# df_pcp_filtered = df_pcp[df_pcp['facilityName'].isin(top_facility_names)]
# 
# # Create stacked bar chart
# fig_pcp = px.bar(
#     df_pcp_filtered,
#     x='facilityName',
#     y='visit_count',
#     color='pcp_status',
#     title='PCP Involvement: With PCP vs Without PCP (Top 20 Facilities)',
#     labels={'facilityName': 'Facility Name', 'visit_count': 'Number of Visits', 'pcp_status': 'PCP Status'},
#     color_discrete_map={'With PCP': '#17becf', 'Without PCP': '#bcbd22'}
# )
# fig_pcp.update_layout(
#     xaxis_title='Facility Name',
#     yaxis_title='Number of Visits',
#     xaxis_tickangle=-45,
#     barmode='stack',
#     showlegend=True,
#     height=600
# )
# fig_pcp.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9. Combined Dashboard View

# COMMAND ----------

# Create subplots with multiple charts
fig8 = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        'VisitType: Telemed vs Other (Top 10)',
        'Completed vs Cancelled (Top 10)',
        'New vs Returning Patients (Top 10)',
        'Cancellation Rate % (Top 10)'
    ),
    specs=[[{"type": "bar"}, {"type": "bar"}],
           [{"type": "bar"}, {"type": "bar"}]]
)

# Get top 10 facilities
top_10_facilities = df.groupby('facilityName')['visit_count'].sum().reset_index()
top_10_facilities = top_10_facilities.sort_values('visit_count', ascending=False).head(10)['facilityName'].tolist()

# Chart 1: VisitType
df_visit_type_top10 = df_visit_type[df_visit_type['facilityName'].isin(top_10_facilities)]
for visit_type in ['Telemed', 'Other']:
    df_subset = df_visit_type_top10[df_visit_type_top10['visitType'] == visit_type]
    if not df_subset.empty:
        fig8.add_trace(
        go.Bar(
                name=visit_type,
                x=df_subset['facilityName'],
                y=df_subset['visit_count'],
                marker_color='#1f77b4' if visit_type == 'Telemed' else '#ff7f0e'
        ),
        row=1, col=1
    )

# Chart 2: Completed vs Cancelled
df_status_top10 = df_status[df_status['facilityName'].isin(top_10_facilities)]
for status in ['Completed', 'Cancelled', 'completed', 'cancelled']:
    df_subset = df_status_top10[df_status_top10['status'].str.lower() == status.lower()]
    if not df_subset.empty:
        fig8.add_trace(
        go.Bar(
                name=status.title(),
                x=df_subset['facilityName'],
                y=df_subset['status_count'],
                marker_color='#2ca02c' if status.lower() == 'completed' else '#d62728'
        ),
        row=1, col=2
    )

# Chart 3: New vs Returning
df_patients_top10 = df_patients[df_patients['facilityName'].isin(top_10_facilities)]
for patient_type in ['New', 'Returning']:
    df_subset = df_patients_top10[df_patients_top10['patient_category'] == patient_type]
    if not df_subset.empty:
        fig8.add_trace(
        go.Bar(
                name=patient_type,
                x=df_subset['facilityName'],
                y=df_subset['patient_count'],
                marker_color='#9467bd' if patient_type == 'New' else '#8c564b'
        ),
        row=2, col=1
    )

# Chart 4: Cancellation Rate
df_cancel_rate_top10 = df_cancel_rate[df_cancel_rate['facilityName'].isin(top_10_facilities)]
if not df_cancel_rate_top10.empty:
    fig8.add_trace(
    go.Bar(
        name='Cancellation Rate %',
            x=df_cancel_rate_top10['facilityName'],
            y=df_cancel_rate_top10['cancellation_rate'],
        marker_color='#e377c2'
    ),
    row=2, col=2
)

# Update layout
fig8.update_layout(
    height=800,
    showlegend=True,
    title_text="Visits Analytics Dashboard - Top 10 Facilities",
    barmode='stack'
)

# Update x-axis labels
for i in range(1, 3):
    for j in range(1, 3):
        fig8.update_xaxes(tickangle=-45, row=i, col=j)

fig8.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary Statistics

# COMMAND ----------

display(df.head(50))
