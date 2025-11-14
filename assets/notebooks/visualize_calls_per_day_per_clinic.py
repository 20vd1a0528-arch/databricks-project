# Databricks notebook source
# MAGIC %md
# MAGIC # Calls per Day per Clinic Visualization
# MAGIC 
# MAGIC This notebook specifically visualizes calls per day per clinic with stack graphs

# COMMAND ----------

# Import required libraries
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Data

# COMMAND ----------

# Run the calls per day per clinic query
query = """
SELECT
  DATE(r.start_time) AS call_date,
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
  AND r.start_time IS NOT NULL
GROUP BY
  DATE(r.start_time),
  c.facilityName,
  CASE
    WHEN LOWER(r.direction) = 'inbound' THEN r.to_wellstreetId
    WHEN LOWER(r.direction) = 'outbound' THEN r.from_wellstreetId
  END
ORDER BY
  call_date DESC,
  total_calls DESC,
  facility_name
"""

df = spark.sql(query).toPandas()
df['call_date'] = pd.to_datetime(df['call_date'])

# COMMAND ----------

# MAGIC %md
# MAGIC ## Stacked Area Chart - All Clinics

# COMMAND ----------

# Create stacked area chart
fig1 = px.area(
    df,
    x='call_date',
    y='total_calls',
    color='facility_name',
    title='Calls per Day per Clinic - Stacked Area Chart',
    labels={'call_date': 'Date', 'total_calls': 'Total Calls', 'facility_name': 'Clinic Name'},
    color_discrete_sequence=px.colors.qualitative.Set3
)
fig1.update_layout(
    xaxis_title='Date',
    yaxis_title='Total Calls',
    xaxis_tickangle=-45,
    showlegend=True,
    height=600
)
fig1.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Stacked Bar Chart - All Clinics

# COMMAND ----------

# Create stacked bar chart
fig2 = px.bar(
    df,
    x='call_date',
    y='total_calls',
    color='facility_name',
    title='Calls per Day per Clinic - Stacked Bar Chart',
    labels={'call_date': 'Date', 'total_calls': 'Total Calls', 'facility_name': 'Clinic Name'},
    color_discrete_sequence=px.colors.qualitative.Set3
)
fig2.update_layout(
    xaxis_title='Date',
    yaxis_title='Total Calls',
    xaxis_tickangle=-45,
    barmode='stack',
    showlegend=True,
    height=600
)
fig2.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Stacked Bar Chart - Top 10 Clinics Only

# COMMAND ----------

# Get top 10 clinics by total calls
top_clinics = df.groupby('facility_name')['total_calls'].sum().nlargest(10).index.tolist()
df_top10 = df[df['facility_name'].isin(top_clinics)]

# Create stacked bar chart for top 10
fig3 = px.bar(
    df_top10,
    x='call_date',
    y='total_calls',
    color='facility_name',
    title='Calls per Day per Clinic - Top 10 Clinics (Stacked Bar)',
    labels={'call_date': 'Date', 'total_calls': 'Total Calls', 'facility_name': 'Clinic Name'},
    color_discrete_sequence=px.colors.qualitative.Set3
)
fig3.update_layout(
    xaxis_title='Date',
    yaxis_title='Total Calls',
    xaxis_tickangle=-45,
    barmode='stack',
    showlegend=True,
    height=600
)
fig3.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Stacked Area Chart - Top 10 Clinics Only

# COMMAND ----------

# Create stacked area chart for top 10
fig4 = px.area(
    df_top10,
    x='call_date',
    y='total_calls',
    color='facility_name',
    title='Calls per Day per Clinic - Top 10 Clinics (Stacked Area)',
    labels={'call_date': 'Date', 'total_calls': 'Total Calls', 'facility_name': 'Clinic Name'},
    color_discrete_sequence=px.colors.qualitative.Set3
)
fig4.update_layout(
    xaxis_title='Date',
    yaxis_title='Total Calls',
    xaxis_tickangle=-45,
    showlegend=True,
    height=600
)
fig4.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Summary

# COMMAND ----------

display(df.groupby('facility_name')['total_calls'].sum().sort_values(ascending=False).head(20))
display(df.groupby('call_date')['total_calls'].sum().tail(30))

