# Databricks Asset Bundle Project

This project automates SQL transformations and table creation using Databricks Asset Bundles with CI/CD integration via GitHub Actions.

## Project Structure

```
databricks-project/
├── databricks.yml              # Main bundle configuration
├── assets/
│   ├── notebooks/
│   │   ├── create_employees.sql        # Creates employees table
│   │   ├── create_employees_table.py   # Python notebook for employees table
│   │   ├── query.sql                   # Creates date_table
│   │   └── transform_data.sql          # Creates daily_sales and date_table
│   ├── workflows/
│   │   └── jobs.yml                    # Additional job definitions
│   └── libraries/
│       └── requirements.txt             # Python dependencies
├── ci/
│   └── github-actions.yml              # GitHub Actions CI/CD workflow
├── tests/                               # Test directory (for future test files)
└── README.md
```

## Setup

### Prerequisites

1. **Databricks CLI** installed and authenticated
   ```bash
   pip install databricks-cli
   databricks configure --token
   ```

2. **GitHub repository** with secrets configured (for CI/CD)

3. **Access to Databricks workspace** with SQL warehouse

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
   databricks bundle run employees_job --target dev
   ```

## Jobs

### employees_job

The main job that creates the `default.employees` table with sample employee data.

**Configuration:** Defined in `databricks.yml`

**SQL File:** `assets/notebooks/create_employees.sql`

**Table Created:** `default.employees` with columns:
- `id` (integer)
- `name` (string)
- `salary` (integer)

**Sample Data:**
- alen (id: 1, salary: 10000)
- bob (id: 2, salary: 20000)
- charlie (id: 3, salary: 30000)
- ell (id: 4, salary: 50000)

## CI/CD Automation

### GitHub Actions Setup

The project includes automated CI/CD via GitHub Actions located in `ci/github-actions.yml` that:

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
  - Workspace: `https://dbc-3046d6f1-8d0b.cloud.databricks.com`
  - Root Path: `/Workspace/Users/pranathibts5117@gmail.com/bundles/notebooks_bundle`

- **prod**: Production environment (commented out in `databricks.yml`, configure as needed)

## Notebooks

### create_employees.sql
Creates the `default.employees` table with sample employee data.

### query.sql
Creates the `default.date_table` with current date.

### transform_data.sql
Creates both `default.daily_sales` and `default.date_table` tables.

### create_employees_table.py
Python notebook for creating employees table (alternative to SQL).

## Dependencies

Python dependencies are defined in `assets/libraries/requirements.txt`:
- pandas
- databricks-cli
- pytest>=7.0.0
- pytest-cov>=4.0.0
- pyyaml>=6.0

## Testing

The `tests/` directory is available for adding test files. Currently empty and ready for test implementations.

## Troubleshooting

- **Validation errors**: Run `databricks bundle validate --target dev` locally
- **Deployment issues**: Check GitHub Actions logs for detailed error messages
- **Job failures**: Verify SQL warehouse is running and accessible
- **Path issues**: Ensure file paths in YAML files are relative to the project root

## Additional Resources

- [Databricks Asset Bundles Documentation](https://docs.databricks.com/dev-tools/bundles/index.html)
- [Databricks CLI Documentation](https://docs.databricks.com/dev-tools/cli/index.html)
