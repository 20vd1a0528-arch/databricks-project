# Databricks SQL Automation using Asset Bundles

This project automates SQL transformations using Databricks Asset Bundles with CI/CD integration via GitHub Actions.

## Project Structure

```
databricks-project/
├── assets/
│   ├── notebooks/
│   │   └── transform_data.sql      # SQL transformation query
│   ├── workflows/
│   │   └── jobs.yml                 # Job definitions
│   └── libraries/
│       └── requirements.txt         # Python dependencies
├── .github/
│   └── workflows/
│       └── databricks-bundle.yml    # GitHub Actions CI/CD
├── databricks.yml                   # Main bundle configuration
└── README.md
```

## Setup

### Prerequisites

1. Databricks CLI installed and authenticated
2. GitHub repository with secrets configured
3. Access to Databricks workspace with SQL warehouse

### Local Development

1. **Validate the bundle:**
   ```bash
   databricks bundle validate --target dev
   ```

2. **Deploy to dev environment:**
   ```bash
   databricks bundle deploy --target dev
   ```

3. **Run the job manually:**
   ```bash
   databricks bundle run daily_sales_job --target dev
   ```

## CI/CD Automation

### GitHub Actions Setup

The project includes automated CI/CD via GitHub Actions that:

- **On Pull Requests**: Validates the bundle configuration
- **On Push to Main**: Validates and automatically deploys to dev environment

### Required GitHub Secrets

Configure these secrets in your GitHub repository settings:

1. `DATABRICKS_HOST` - Your Databricks workspace URL
   - Example: `https://dbc-3046d6f1-8d0b.cloud.databricks.com`

2. `DATABRICKS_TOKEN` - Your Databricks personal access token
   - Generate from: User Settings → Access Tokens → Generate new token

### Setting up GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add `DATABRICKS_HOST` and `DATABRICKS_TOKEN`

## Workflow

1. **Make changes** to SQL files or configuration
2. **Commit and push** to GitHub
3. **GitHub Actions** automatically:
   - Validates the bundle configuration
   - Deploys to dev environment (on main branch)
   - Updates the job in Databricks workspace

## Environments

- **dev**: Development environment
- **prod**: Production environment (configure as needed)

## Job Configuration

The `daily_sales_job` runs a SQL query that creates a table with the current date.

### Schedule

To enable automatic scheduling, uncomment the schedule section in `databricks.yml`:

```yaml
schedule:
  quartz_cron_expression: "0 0 6 ? * *"  # every day at 6 AM UTC
  timezone_id: "Asia/Kolkata"
```

## Troubleshooting

- **Validation errors**: Run `databricks bundle validate --target dev` locally
- **Deployment issues**: Check GitHub Actions logs for detailed error messages
- **Job failures**: Verify SQL warehouse is running and accessible
