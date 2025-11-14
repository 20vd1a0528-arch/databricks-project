# Databricks notebook source
# MAGIC %md
# MAGIC # Ring Central Call Analytics Visualization
# MAGIC 
# MAGIC This notebook visualizes call data with stack graphs for:
# MAGIC 1. Incoming vs Outgoing Calls
# MAGIC 2. Total Calls per Clinic
# MAGIC 3. Calls by Action/Result
# MAGIC 4. Calls per Day
# MAGIC 5. Calls per Day per Clinic

# COMMAND ----------

# Import required libraries
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Data from Combined Query

# COMMAND ----------

# Run the combined analytics query
query = """
SELECT
  DATE(r.start_time) AS call_date,
  LOWER(r.direction) AS direction,
  c.facilityName AS facility_name,
  CASE
    WHEN LOWER(r.direction) = 'inbound' THEN r.to_wellstreetId
    WHEN LOWER(r.direction) = 'outbound' THEN r.from_wellstreetId
  END AS wellstreetId,
  COALESCE(r.actions, r.action, 'Unknown') AS action,
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
  action
"""

df = spark.sql(query).toPandas()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Incoming vs Outgoing Calls (Stack Graph)

# COMMAND ----------

# Aggregate by direction
direction_df = df.groupby('direction')['call_count'].sum().reset_index()

# Create stacked bar chart
fig1 = px.bar(
    direction_df,
    x='direction',
    y='call_count',
    title='Incoming vs Outgoing Calls',
    labels={'direction': 'Call Direction', 'call_count': 'Total Calls'},
    color='direction',
    color_discrete_map={'inbound': '#1f77b4', 'outbound': '#ff7f0e'}
)
fig1.update_layout(
    xaxis_title='Call Direction',
    yaxis_title='Total Calls',
    showlegend=True,
    barmode='group'
)
fig1.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Total Calls per Clinic (Stack Graph)

# COMMAND ----------

# Aggregate by clinic
clinic_df = df.groupby('facility_name')['call_count'].sum().reset_index().sort_values('call_count', ascending=False)

# Create stacked bar chart
fig2 = px.bar(
    clinic_df.head(20),  # Top 20 clinics
    x='facility_name',
    y='call_count',
    title='Total Calls per Clinic (Top 20)',
    labels={'facility_name': 'Clinic Name', 'call_count': 'Total Calls'},
    color='call_count',
    color_continuous_scale='Viridis'
)
fig2.update_layout(
    xaxis_title='Clinic Name',
    yaxis_title='Total Calls',
    xaxis_tickangle=-45,
    showlegend=False
)
fig2.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Calls by Action/Result (Stack Graph)

# COMMAND ----------

# Aggregate by action
action_df = df.groupby('action')['call_count'].sum().reset_index().sort_values('call_count', ascending=False)

# Create stacked bar chart
fig3 = px.bar(
    action_df,
    x='action',
    y='call_count',
    title='Calls by Action/Result',
    labels={'action': 'Action', 'call_count': 'Total Calls'},
    color='action',
    color_discrete_sequence=px.colors.qualitative.Set3
)
fig3.update_layout(
    xaxis_title='Action',
    yaxis_title='Total Calls',
    showlegend=True,
    barmode='group'
)
fig3.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Calls per Day (Stack Graph)

# COMMAND ----------

# Aggregate by date
daily_df = df.groupby('call_date')['call_count'].sum().reset_index().sort_values('call_date')

# Create line/bar chart
fig4 = px.bar(
    daily_df,
    x='call_date',
    y='call_count',
    title='Calls per Day',
    labels={'call_date': 'Date', 'call_count': 'Total Calls'},
    color='call_count',
    color_continuous_scale='Blues'
)
fig4.update_layout(
    xaxis_title='Date',
    yaxis_title='Total Calls',
    xaxis_tickangle=-45,
    showlegend=False
)
fig4.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Calls per Day per Clinic (Stack Graph)

# COMMAND ----------

# Aggregate by date and clinic
daily_clinic_df = df.groupby(['call_date', 'facility_name'])['call_count'].sum().reset_index().sort_values('call_date')

# Get top clinics for better visualization
top_clinics = df.groupby('facility_name')['call_count'].sum().nlargest(10).index.tolist()
daily_clinic_filtered = daily_clinic_df[daily_clinic_df['facility_name'].isin(top_clinics)]

# Create stacked area chart
fig5 = px.area(
    daily_clinic_filtered,
    x='call_date',
    y='call_count',
    color='facility_name',
    title='Calls per Day per Clinic (Top 10 Clinics)',
    labels={'call_date': 'Date', 'call_count': 'Total Calls', 'facility_name': 'Clinic'},
    color_discrete_sequence=px.colors.qualitative.Set3
)
fig5.update_layout(
    xaxis_title='Date',
    yaxis_title='Total Calls',
    xaxis_tickangle=-45,
    showlegend=True
)
fig5.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Alternative: Stacked Bar Chart for Calls per Day per Clinic

# COMMAND ----------

# Create stacked bar chart version
fig6 = px.bar(
    daily_clinic_filtered,
    x='call_date',
    y='call_count',
    color='facility_name',
    title='Calls per Day per Clinic - Stacked Bar (Top 10 Clinics)',
    labels={'call_date': 'Date', 'call_count': 'Total Calls', 'facility_name': 'Clinic'},
    color_discrete_sequence=px.colors.qualitative.Set3
)
fig6.update_layout(
    xaxis_title='Date',
    yaxis_title='Total Calls',
    xaxis_tickangle=-45,
    barmode='stack',
    showlegend=True
)
fig6.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary Statistics

# COMMAND ----------

display(df.groupby('direction')['call_count'].sum())
display(df.groupby('action')['call_count'].sum())
display(df.groupby('facility_name')['call_count'].sum().sort_values(ascending=False).head(10))

