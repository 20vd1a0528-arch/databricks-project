# Serverless Compute Configuration Guide

## Issue: "Only serverless compute is supported in the workspace"

Your workspace only supports serverless compute, not traditional compute clusters. Here are your options:

---

## Option 1: Use Existing Serverless Compute Cluster (Recommended)

### Step 1: Create a Serverless Compute Cluster in Databricks

1. Go to your Databricks workspace
2. Navigate to **Compute** → **Compute** (or **Clusters**)
3. Click **Create Compute**
4. Select **Serverless** compute type
5. Configure and create the cluster
6. Copy the **Cluster ID**

### Step 2: Update databricks.yml

```yaml
employees_job:
  name: "Employees Table Creation Job"
  tasks:
    - task_key: create_employees_table
      notebook_task:
        notebook_path: ./assets/notebooks/create_employees_table.py
      existing_cluster_id: "your-serverless-cluster-id-here"
```

**Replace `your-serverless-cluster-id-here` with your actual cluster ID.**

---

## Option 2: Convert Python to SQL (If Possible)

If your Python code can be converted to SQL, you can use a SQL task instead:

### Original Python:
```python
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("Spark DataFrames").getOrCreate()
data = ([1, "alen", 10000], [2, "bob", 20000], [3, "charlie", 30000])
df = spark.createDataFrame(data, ["id", "name", "salary"])
df.write.mode("overwrite").saveAsTable("default.employees")
```

### Equivalent SQL:
```sql
CREATE OR REPLACE TABLE default.employees AS
SELECT 1 AS id, 'alen' AS name, 10000 AS salary
UNION ALL
SELECT 2 AS id, 'bob' AS name, 20000 AS salary
UNION ALL
SELECT 3 AS id, 'charlie' AS name, 30000 AS salary;
```

Then use SQL task:
```yaml
employees_job:
  name: "Employees Table Creation Job"
  tasks:
    - task_key: create_employees_table
      sql_task:
        file:
          path: ./assets/notebooks/create_employees.sql
        warehouse_id: "f68b5a932e3471dc"
```

---

## Option 3: Use SQL Warehouse for Simple Python Operations

If you need basic Python operations, some can be done with SQL warehouses. However, for jobs, notebook tasks typically require compute clusters.

For simple cases, consider converting to SQL or using SQL functions.

---

## Quick Fix: Get Your Serverless Compute Cluster ID

### Using Databricks CLI:

```bash
# List all compute clusters
databricks clusters list --output json | grep -i "cluster_id\|cluster_name\|cluster_source"

# Or list serverless clusters specifically
databricks clusters list --output json | grep -A 5 "serverless"
```

### Using Databricks UI:

1. Go to **Compute** → **Compute**
2. Find your serverless compute cluster
3. Click on it
4. Copy the **Cluster ID** from the URL or cluster details

---

## Example: Complete Configuration with Serverless Compute

```yaml
resources:
  jobs:
    employees_job:
      name: "Employees Table Creation Job"
      tasks:
        - task_key: create_employees_table
          notebook_task:
            notebook_path: ./assets/notebooks/create_employees_table.py
          existing_cluster_id: "1234-567890-serverless-cluster-id"
```

---

## Troubleshooting

### Error: "Only serverless compute is supported"
- ✅ Solution: Use `existing_cluster_id` with a serverless cluster
- ❌ Don't use: `new_cluster` (traditional compute not supported)

### Error: "Cluster not found"
- ✅ Solution: Verify the cluster ID is correct
- ✅ Solution: Ensure the cluster is serverless type
- ✅ Solution: Check cluster permissions

### Error: "Cluster not running"
- ✅ Solution: The cluster will start automatically when job runs
- ✅ Solution: Ensure you have permissions to use the cluster

---

## Next Steps

1. **Create a serverless compute cluster** in Databricks UI
2. **Get the cluster ID**
3. **Update `databricks.yml`** with `existing_cluster_id`
4. **Deploy again**

---

## Alternative: Convert to SQL Task

If you don't want to manage compute clusters, convert your Python code to SQL:

1. Create `assets/notebooks/create_employees.sql`
2. Use SQL syntax instead of Python
3. Use `sql_task` with `warehouse_id` (no compute cluster needed)

This is simpler for serverless-only workspaces!

