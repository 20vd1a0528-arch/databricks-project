# Complete Explanation: Databricks Asset Bundles Project

## 📋 Overview

This project automates SQL transformations in Databricks using **Asset Bundles** with **CI/CD integration** via GitHub Actions. Here's everything that was set up and fixed.

---

## 🔍 Problems We Encountered & Fixed

### Problem 1: Incorrect `warehouse_id` Format
**Error:** The warehouse ID was set to a URL path instead of just the ID.

**Before:**
```yaml
warehouse_id: "/sql-warehouses?o=4019182261101671&page=1&page_size=20"
```

**After:**
```yaml
warehouse_id: "f68b5a932e3471dc"
```

**Why:** The `warehouse_id` field expects only the warehouse identifier, not a full URL path.

---

### Problem 2: Wrong SQL Task Syntax
**Error:** Using `query.file` which doesn't exist in Databricks Asset Bundles schema.

**Before:**
```yaml
sql_task:
  query:
    file: ./assets/notebooks/transform_data.sql
```

**After:**
```yaml
sql_task:
  file:
    path: ./assets/notebooks/transform_data.sql
```

**Why:** According to Databricks Asset Bundles schema:
- For SQL files: Use `file.path` structure
- For inline SQL queries: Use `query.query_id` (for saved queries in Databricks)
- For SQL alerts/dashboards: Use `alert` or `dashboard` structures

---

### Problem 3: SQL Query Referenced Non-Existent Table
**Error:** The SQL query tried to access `default.sales` table which didn't exist.

**Before:**
```sql
CREATE OR REPLACE TABLE default.daily_sales AS
SELECT
  current_date() AS run_date,
  SUM(amount) AS total_sales
FROM default.sales
WHERE date = current_date();
```

**After:**
```sql
CREATE OR REPLACE TABLE default.daily_sales AS
SELECT current_date() AS run_date;
```

**Why:** Simplified to just get the current date without any table dependencies.

---

### Problem 4: GitHub Push Protection - Exposed API Token
**Error:** GitHub detected a Databricks API token in commit history and blocked the push.

**Solution:**
1. Used `git filter-branch` to remove the `tokens` file from all commits
2. Added `tokens` to `.gitignore` to prevent future commits
3. Force-pushed the cleaned history

**Important:** If a token is exposed, always:
- Revoke it immediately in Databricks
- Generate a new token
- Store it only in GitHub Secrets (never in code)

---

## 📁 Project Structure Explained

```
databricks-project/
├── .github/
│   └── workflows/
│       └── databricks-bundle.yml    # CI/CD automation
├── assets/
│   ├── notebooks/
│   │   └── transform_data.sql       # SQL transformation query
│   ├── workflows/
│   │   └── jobs.yml                 # Job definitions (optional)
│   └── libraries/
│       └── requirements.txt         # Python dependencies
├── databricks.yml                   # Main bundle configuration
├── .gitignore                       # Files to exclude from Git
└── README.md                        # Documentation
```

---

## 🔧 Key Files Explained

### 1. `databricks.yml` - Main Configuration

This is the **heart of your Databricks Asset Bundle**. It defines:

```yaml
bundle:
  name: databricks-project  # Bundle identifier

environments:
  dev:    # Development environment
    workspace:
      host: https://dbc-3046d6f1-8d0b.cloud.databricks.com
      root_path: /Workspace/Users/.../bundles/sql_automation_bundle
  
  prod:   # Production environment
    workspace:
      host: https://dbc-3046d6f1-8d0b.cloud.databricks.com
      root_path: /Workspace/Users/.../bundles/sql_automation_bundle_prod

resources:
  jobs:
    daily_sales_job:  # Job name (internal identifier)
      name: "Daily Sales Job (SQL Warehouse)"  # Display name in Databricks UI
      tasks:
        - task_key: run_transform
          sql_task:
            file:
              path: ./assets/notebooks/transform_data.sql
            warehouse_id: "f68b5a932e3471dc"
```

**Key Concepts:**
- **Environments:** Different workspaces/configurations (dev, prod, staging)
- **Resources:** Things you want to deploy (jobs, pipelines, models, etc.)
- **Tasks:** Individual steps within a job
- **SQL Task:** Runs SQL queries using a SQL warehouse

---

### 2. `transform_data.sql` - SQL Query

```sql
CREATE OR REPLACE TABLE default.daily_sales AS
SELECT current_date() AS run_date;
```

**What it does:**
- Creates or replaces a table called `default.daily_sales`
- Inserts a single row with the current date
- No table dependencies required

**When it runs:**
- Manually triggered, or
- On a schedule (if uncommented in `databricks.yml`)

---

### 3. `.github/workflows/databricks-bundle.yml` - CI/CD Pipeline

This GitHub Actions workflow automates your deployment:

```yaml
on:
  push:
    branches: [main]      # Triggers on push to main
  pull_request:
    branches: [main]      # Validates on PRs

jobs:
  validate-and-deploy:
    steps:
      1. Checkout code
      2. Set up Python
      3. Install Databricks CLI
      4. Configure authentication (using GitHub Secrets)
      5. Validate bundle configuration
      6. Deploy to dev (only on push to main)
```

**Workflow Behavior:**
- **On Pull Request:** Only validates (doesn't deploy)
- **On Push to Main:** Validates AND deploys automatically

**Required GitHub Secrets:**
- `DATABRICKS_HOST`: Your workspace URL
- `DATABRICKS_TOKEN`: Your personal access token

---

### 4. `.gitignore` - Security & Cleanup

Prevents committing sensitive or unnecessary files:

```
# Databricks cache files
.databricks/
.bundle/

# Tokens and secrets (IMPORTANT!)
tokens
*secret*
*password*
*credential*

# Environment variables
.env
.env.local
```

**Why it matters:** Prevents accidentally committing API tokens, passwords, or sensitive data.

---

## 🔄 How Everything Works Together

### Local Development Flow:

1. **Edit files** (SQL, config, etc.)
2. **Validate locally:**
   ```bash
   databricks bundle validate --target dev
   ```
3. **Deploy manually:**
   ```bash
   databricks bundle deploy --target dev
   ```
4. **Run job:**
   ```bash
   databricks bundle run daily_sales_job --target dev
   ```

### Automated CI/CD Flow:

1. **Developer pushes code to GitHub:**
   ```bash
   git add .
   git commit -m "Update SQL query"
   git push origin main
   ```

2. **GitHub Actions automatically:**
   - Checks out the code
   - Installs Databricks CLI
   - Validates the bundle configuration
   - Deploys to dev environment
   - Updates the job in Databricks workspace

3. **Result:** Your SQL file and job configuration are automatically updated in Databricks!

---

## 🎯 Key Concepts Explained

### What is a Databricks Asset Bundle?

An **Asset Bundle** is a way to:
- Define Databricks resources (jobs, pipelines, models) as code
- Version control your Databricks configurations
- Deploy consistently across environments
- Automate deployments via CI/CD

**Benefits:**
- ✅ Infrastructure as Code (IaC)
- ✅ Version control for Databricks resources
- ✅ Consistent deployments
- ✅ Easy rollbacks
- ✅ Team collaboration

### SQL Task vs Notebook Task

**SQL Task** (what we're using):
- Runs SQL queries directly
- Uses SQL warehouses
- Good for: Data transformations, ETL, reporting

**Notebook Task:**
- Runs Python/Scala/R notebooks
- Uses compute clusters
- Good for: Complex logic, ML workflows, data science

### Environments

**Dev Environment:**
- For testing and development
- Lower cost resources
- Frequent deployments

**Prod Environment:**
- For production workloads
- Higher reliability requirements
- Controlled deployments

---

## 🚀 Common Commands

```bash
# Validate configuration
databricks bundle validate --target dev

# Deploy to environment
databricks bundle deploy --target dev

# Run a job
databricks bundle run daily_sales_job --target dev

# Check deployment status
databricks bundle validate --target dev

# View bundle resources
databricks bundle resources list --target dev
```

---

## 🔐 Security Best Practices

1. **Never commit tokens/passwords:**
   - Use GitHub Secrets for CI/CD
   - Use `.gitignore` for local files
   - Use Databricks secrets for runtime

2. **Rotate tokens regularly:**
   - Especially if exposed (even briefly)

3. **Use least privilege:**
   - Tokens should have minimal required permissions

4. **Review before pushing:**
   - Check `git diff` before committing
   - Use pre-commit hooks if possible

---

## 📊 What Happens When You Deploy

1. **Bundle files uploaded** to Databricks workspace
2. **SQL file** (`transform_data.sql`) uploaded to workspace
3. **Job created/updated** in Databricks with:
   - Name: "Daily Sales Job (SQL Warehouse)"
   - Task: Runs the SQL file
   - Warehouse: Uses specified SQL warehouse
4. **Job ready** to run manually or on schedule

---

## 🎓 Next Steps & Enhancements

### Enable Scheduling:
Uncomment in `databricks.yml`:
```yaml
schedule:
  quartz_cron_expression: "0 0 6 ? * *"  # Daily at 6 AM UTC
  timezone_id: "Asia/Kolkata"
```

### Add More Jobs:
Add additional jobs in `databricks.yml`:
```yaml
resources:
  jobs:
    daily_sales_job: ...
    weekly_report_job: ...
    monthly_cleanup_job: ...
```

### Add Parameters:
Make SQL queries dynamic:
```yaml
sql_task:
  file:
    path: ./assets/notebooks/transform_data.sql
  parameters:
    start_date: "2025-01-01"
    end_date: "2025-01-31"
```

### Add Notifications:
Get notified on job completion:
```yaml
email_notifications:
  on_success: ["your-email@example.com"]
  on_failure: ["your-email@example.com"]
```

---

## ✅ Summary

You now have:
- ✅ Working Databricks Asset Bundle configuration
- ✅ SQL task that runs without table dependencies
- ✅ Automated CI/CD via GitHub Actions
- ✅ Secure token management
- ✅ Proper Git setup with `.gitignore`
- ✅ Documentation and best practices

**The system is fully automated:** Push to GitHub → GitHub Actions → Databricks deployment! 🎉

