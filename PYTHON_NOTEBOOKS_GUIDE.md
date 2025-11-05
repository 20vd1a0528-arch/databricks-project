# Using Python Files with Databricks Asset Bundles

## Important: SQL Warehouse vs Compute Clusters

### ❌ SQL Warehouse Limitations:
- **SQL warehouses can ONLY run SQL queries**
- They **CANNOT run Python files**
- They are optimized for SQL queries only

### ✅ For Python, You Need:
- **Notebook tasks** (not SQL tasks)
- **Compute clusters** (not SQL warehouses)
- Python files saved as Databricks notebooks

---

## How to Add Python Support

### Option 1: Notebook Task (Recommended)

**Step 1:** Create a Python notebook file (`.py`)

**Step 2:** Add notebook task to `databricks.yml`:

```yaml
resources:
  jobs:
    python_job:
      name: "Python Table Creation Job"
      tasks:
        - task_key: run_python
          notebook_task:
            notebook_path: ./assets/notebooks/create_table_python
          new_cluster:
            spark_version: "13.3.x-scala2.12"
            node_type_id: "i3.xlarge"
            num_workers: 1
```

**Key Differences:**
- Uses `notebook_task` (not `sql_task`)
- Uses `new_cluster` (not `warehouse_id`)
- Requires compute cluster configuration

---

## Complete Example Configuration

### Mixed Job: SQL + Python

```yaml
resources:
  jobs:
    # SQL Job (uses SQL warehouse)
    sql_job:
      name: "SQL Job"
      tasks:
        - task_key: create_sql_table
          sql_task:
            file:
              path: ./assets/notebooks/query.sql
            warehouse_id: "f68b5a932e3471dc"
    
    # Python Job (uses compute cluster)
    python_job:
      name: "Python Job"
      tasks:
        - task_key: create_python_table
          notebook_task:
            notebook_path: ./assets/notebooks/create_table_python
          new_cluster:
            spark_version: "13.3.x-scala2.12"
            node_type_id: "i3.xlarge"
            num_workers: 1
    
    # Combined Job: SQL first, then Python
    combined_job:
      name: "Combined SQL + Python Job"
      tasks:
        # Task 1: Run SQL (uses warehouse)
        - task_key: sql_step
          sql_task:
            file:
              path: ./assets/notebooks/query.sql
            warehouse_id: "f68b5a932e3471dc"
        
        # Task 2: Run Python (uses cluster)
        - task_key: python_step
          depends_on:
            - sql_step
          notebook_task:
            notebook_path: ./assets/notebooks/create_table_python
          new_cluster:
            spark_version: "13.3.x-scala2.12"
            node_type_id: "i3.xlarge"
            num_workers: 1
```

---

## Compute Cluster Configuration

### Required Fields:

```yaml
new_cluster:
  spark_version: "13.3.x-scala2.12"  # Databricks runtime version
  node_type_id: "i3.xlarge"          # Instance type
  num_workers: 1                      # Number of worker nodes
```

### Optional Fields:

```yaml
new_cluster:
  spark_version: "13.3.x-scala2.12"
  node_type_id: "i3.xlarge"
  num_workers: 1
  spark_conf:
    "spark.databricks.cluster.profile": "singleNode"
    "spark.master": "local[*]"
  custom_tags:
    ResourceClass: "SingleNode"
```

---

## Python Notebook Format

Python files for Databricks need to be in Databricks notebook format:

```python
# Databricks notebook source
# MAGIC %md
# MAGIC # My Python Notebook

# COMMAND ----------

# Your Python code here
from pyspark.sql import SparkSession
spark = SparkSession.builder.getOrCreate()

# COMMAND ----------

# More code
df = spark.createDataFrame([(1, "test")], ["id", "name"])
df.write.saveAsTable("default.my_table")
```

**Key Format Elements:**
- `# Databricks notebook source` - First line
- `# MAGIC %md` - For markdown cells
- `# COMMAND ----------` - Separates cells

---

## Alternative: Use Existing Cluster

Instead of creating a new cluster each time, you can use an existing cluster:

```yaml
tasks:
  - task_key: run_python
    notebook_task:
      notebook_path: ./assets/notebooks/create_table_python
    existing_cluster_id: "1234-567890-abc123"  # Your cluster ID
```

---

## Cost Considerations

### SQL Warehouse:
- ✅ Pay per query (serverless)
- ✅ Fast startup
- ✅ Good for SQL workloads

### Compute Cluster:
- ⚠️ Pay per cluster runtime
- ⚠️ Takes time to start
- ✅ Required for Python/Spark workloads

---

## Summary

| Feature | SQL Warehouse | Compute Cluster |
|---------|--------------|-----------------|
| SQL Queries | ✅ Yes | ✅ Yes |
| Python Code | ❌ No | ✅ Yes |
| Spark | ❌ No | ✅ Yes |
| Cost Model | Pay per query | Pay per runtime |
| Startup Time | Fast | Slower |

**To use Python:**
1. Create Python notebook (`.py` file in Databricks format)
2. Use `notebook_task` instead of `sql_task`
3. Use `new_cluster` or `existing_cluster_id` instead of `warehouse_id`
4. Configure compute cluster settings

---

## Example: Adding Python Job to Your Bundle

I've created a sample Python notebook: `assets/notebooks/create_table_python.py`

You can add it to your `databricks.yml` like this:

```yaml
python_table_job:
  name: "Python Table Creation"
  tasks:
    - task_key: create_python_table
      notebook_task:
        notebook_path: ./assets/notebooks/create_table_python
      new_cluster:
        spark_version: "13.3.x-scala2.12"
        node_type_id: "i3.xlarge"
        num_workers: 1
```

Then push to GitHub and it will deploy automatically! 🚀

