# Automation with Multiple Files - Explained

## ✅ Yes! Automation Works for Multiple Files

You can have:
- ✅ **Multiple SQL files** (as many as you want)
- ✅ **Multiple jobs** (each pointing to different files)
- ✅ **All deployed automatically** when you push to GitHub

---

## Current Setup

You have:
- `query.sql` - Creates `default.date_table`
- `transform_data.sql` - Creates `default.daily_sales`

But only **1 job** is configured pointing to `query.sql`.

---

## How to Add Multiple Jobs

### Example: Two Jobs, Two Files

```yaml
resources:
  jobs:
    # Job 1: Uses query.sql
    daily_sales_job:
      name: "Daily Sales Job (SQL Warehouse)"
      tasks:
        - task_key: run_transform
          sql_task:
            file:
              path: ./assets/notebooks/query.sql
            warehouse_id: "f68b5a932e3471dc"
    
    # Job 2: Uses transform_data.sql
    transform_data_job:
      name: "Transform Data Job"
      tasks:
        - task_key: run_transform
          sql_task:
            file:
              path: ./assets/notebooks/transform_data.sql
            warehouse_id: "f68b5a932e3471dc"
```

**Result:** When you push, **BOTH jobs** are deployed automatically!

---

## How Automation Works with Multiple Files

### When You Push to GitHub:

```
1. GitHub Actions triggers
   ↓
2. Deploys ALL jobs in databricks.yml
   ↓
3. Uploads ALL SQL files referenced
   ↓
4. Creates/updates ALL jobs in Databricks
   ↓
5. All jobs are ready to run
```

### Example Workflow:

```
Your Push:
  - query.sql (updated)
  - transform_data.sql (updated)
  - databricks.yml (has 2 jobs)
  
  ↓
  
GitHub Actions:
  ✅ Deploys query.sql → Job 1
  ✅ Deploys transform_data.sql → Job 2
  ✅ Both jobs updated in Databricks
```

---

## Real-World Example

### Scenario: You have 5 SQL files

```
assets/notebooks/
  ├── daily_sales.sql
  ├── weekly_report.sql
  ├── monthly_summary.sql
  ├── customer_analytics.sql
  └── inventory_check.sql
```

### Configure 5 Jobs:

```yaml
resources:
  jobs:
    daily_sales_job:
      name: "Daily Sales"
      tasks:
        - task_key: run_daily
          sql_task:
            file:
              path: ./assets/notebooks/daily_sales.sql
            warehouse_id: "f68b5a932e3471dc"
    
    weekly_report_job:
      name: "Weekly Report"
      tasks:
        - task_key: run_weekly
          sql_task:
            file:
              path: ./assets/notebooks/weekly_report.sql
            warehouse_id: "f68b5a932e3471dc"
    
    monthly_summary_job:
      name: "Monthly Summary"
      tasks:
        - task_key: run_monthly
          sql_task:
            file:
              path: ./assets/notebooks/monthly_summary.sql
            warehouse_id: "f68b5a932e3471dc"
    
    customer_analytics_job:
      name: "Customer Analytics"
      tasks:
        - task_key: run_analytics
          sql_task:
            file:
              path: ./assets/notebooks/customer_analytics.sql
            warehouse_id: "f68b5a932e3471dc"
    
    inventory_check_job:
      name: "Inventory Check"
      tasks:
        - task_key: run_inventory
          sql_task:
            file:
              path: ./assets/notebooks/inventory_check.sql
            warehouse_id: "f68b5a932e3471dc"
```

**Result:** Push once → **ALL 5 jobs** deployed automatically! 🎉

---

## Key Points

### ✅ What You Can Do:

1. **Multiple SQL files** - Create as many as you need
2. **Multiple jobs** - Each job can use a different file
3. **One push, all deploy** - All jobs deploy together
4. **Independent schedules** - Each job can have its own schedule
5. **Different warehouses** - Each job can use different SQL warehouse

### 📋 Rules:

- Each job needs a **unique name** (job key)
- Each job can reference **one SQL file**
- One job can have **multiple tasks** (each task can use different file)
- All files must be in your repository

---

## Example: One Job with Multiple Tasks

You can also have one job that runs multiple SQL files in sequence:

```yaml
resources:
  jobs:
    daily_pipeline_job:
      name: "Daily Pipeline"
      tasks:
        # Task 1: Run query.sql
        - task_key: step1_extract
          sql_task:
            file:
              path: ./assets/notebooks/query.sql
            warehouse_id: "f68b5a932e3471dc"
        
        # Task 2: Run transform_data.sql (runs after task 1)
        - task_key: step2_transform
          depends_on:
            - step1_extract
          sql_task:
            file:
              path: ./assets/notebooks/transform_data.sql
            warehouse_id: "f68b5a932e3471dc"
```

---

## Summary

**Automation is NOT limited to one file!**

- ✅ Add as many SQL files as you want
- ✅ Configure multiple jobs in `databricks.yml`
- ✅ Each job can point to a different file
- ✅ One push deploys everything automatically
- ✅ All jobs are managed together

**The automation scales with your needs!** 🚀

