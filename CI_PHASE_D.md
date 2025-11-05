# Phase D - CI: Build and Validation

This document explains the CI (Continuous Integration) pipeline that runs on every pull request and push.

## Overview

The CI pipeline ensures code quality and prevents issues before deployment. It runs automatically on:
- ✅ **Pull Requests** - Validates changes before merging
- ✅ **Pushes to main** - Validates before deployment

## CI Pipeline Steps

### 1. Trigger CI on Pull Request ✅

The workflow automatically triggers on:
```yaml
on:
  pull_request:
    branches:
      - main
```

**What happens:**
- When a PR is created or updated
- GitHub Actions automatically starts the CI job
- All validation steps run
- Deployment is **skipped** (only runs on push to main)

---

### 2. Lint Notebooks and SQL Files ✅

**Step:** `Lint SQL files`

**What it does:**
- Finds all `.sql` files in the repository
- Checks for common issues:
  - ❌ Hardcoded credentials (passwords, secrets, tokens)
  - ⚠️ Potential SQL injection patterns
  - ✅ Valid SQL syntax structure

**Examples of what it catches:**
```sql
-- ❌ Will fail CI
password = 'secret123'
token = 'dapi123...'

-- ✅ Will pass CI
SELECT current_date() AS run_date;
```

**If linting fails:**
- ❌ CI fails
- ❌ PR cannot be merged (if branch protection is enabled)
- Error message shows which file and line

---

### 3. Run Unit Tests ✅

**Step:** `Run Unit Tests`

**What it does:**
- Runs pytest on all tests in `tests/` directory
- Tests cover:
  - ✅ `databricks.yml` exists and is valid YAML
  - ✅ Bundle configuration structure
  - ✅ SQL files exist
  - ✅ Warehouse ID format is correct
  - ✅ SQL task configuration is valid

**Test files:**
- `tests/test_bundle_config.py` - Configuration tests

**Adding more tests:**
Create new test files in `tests/` directory:
```python
# tests/test_your_feature.py
def test_your_feature():
    assert True
```

**If tests fail:**
- ❌ CI fails
- ❌ Deployment is blocked
- Test output shows what failed

---

### 4. Scan for Secret Exposure ✅

**Step:** `Scan for secrets`

**What it does:**
- Scans all files for exposed secrets/credentials
- Checks for common patterns:
  - Databricks API tokens (`dapi...`)
  - AWS keys (`AKIA...`)
  - GitHub tokens (`ghp_...`)
  - Generic passwords/secrets/tokens

**Patterns detected:**
```python
# ❌ Will fail CI
DATABRICKS_TOKEN = "dapi1234567890..."
password: "secret123"
token = "ghp_abc123..."

# ✅ Will pass CI
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")  # Using environment variable
```

**If secrets are found:**
- ❌ CI fails immediately
- ❌ Error shows which file contains the secret
- ⚠️ **CRITICAL:** Remove the secret and rotate it if exposed

**Best practices:**
- ✅ Use environment variables
- ✅ Use GitHub Secrets for CI/CD
- ✅ Never commit secrets to code
- ✅ Use `.gitignore` for local config files

---

### 5. Validate Bundle Using Databricks CLI ✅

**Step:** `Validate Bundle Configuration`

**What it does:**
- Validates `databricks.yml` syntax
- Checks bundle configuration structure
- Verifies all required fields are present
- Validates file paths and references

**Validation checks:**
- ✅ YAML syntax is valid
- ✅ Bundle structure is correct
- ✅ Environment configurations
- ✅ Resource definitions
- ✅ Task configurations

**If validation fails:**
- ❌ CI fails
- ❌ Error message shows what's wrong
- Example: "required field 'warehouse_id' is not set"

---

### 6. Verify Compute Profiles ✅

**Step:** `Verify Compute Profiles`

**What it does:**
- Checks that SQL warehouse ID exists
- Verifies warehouse is accessible
- Validates compute resources (if any)

**What it checks:**
- ✅ Warehouse ID is valid format (not a URL)
- ✅ Warehouse exists in Databricks workspace
- ✅ Warehouse is accessible with current credentials
- ✅ No invalid compute configurations

**If verification fails:**
- ❌ CI fails
- ❌ Error: "Warehouse not found or not accessible"

---

### 7. Fail CI if Validation or Tests Fail ✅

**How it works:**
- Each step has `continue-on-error: false` (default)
- If any step fails, the entire CI job fails
- GitHub shows ❌ status on the PR/workflow

**Result:**
- ❌ PR cannot be merged (if branch protection enabled)
- ❌ Deployment is blocked
- ✅ All checks must pass before deployment

---

## CI Workflow Structure

```
┌─────────────────────────────────────┐
│  Pull Request Created/Updated       │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  CI Job Starts                      │
│  (ci-validation)                    │
└──────────────┬──────────────────────┘
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
┌──────────────┐  ┌──────────────┐
│ Step 1:      │  │ Step 2:      │
│ Lint SQL     │  │ Scan Secrets │
└──────┬───────┘  └──────┬───────┘
       │                 │
       └────────┬────────┘
                │
                ▼
       ┌─────────────────┐
       │ Step 3:         │
       │ Install CLI     │
       └────────┬────────┘
                │
                ▼
       ┌─────────────────┐
       │ Step 4:         │
       │ Authenticate    │
       └────────┬────────┘
                │
                ▼
       ┌─────────────────┐
       │ Step 5:         │
       │ Validate Bundle │
       └────────┬────────┘
                │
                ▼
       ┌─────────────────┐
       │ Step 6:         │
       │ Verify Compute  │
       └────────┬────────┘
                │
                ▼
       ┌─────────────────┐
       │ Step 7:         │
       │ Run Unit Tests  │
       └────────┬────────┘
                │
        ┌───────┴───────┐
        │               │
        ▼               ▼
   ┌─────────┐    ┌─────────┐
   │ All ✅  │    │ Any ❌  │
   │ Pass    │    │ Fail    │
   └────┬────┘    └────┬────┘
        │              │
        ▼              ▼
   CI Success      CI Failure
   (Can merge)    (Blocked)
```

---

## Running CI Locally

You can run CI checks locally before pushing:

### 1. Lint SQL files
```bash
# Manual check
find . -name "*.sql" -exec echo "Checking: {}" \;
```

### 2. Scan for secrets
```bash
# Install and use detect-secrets
pip install detect-secrets
detect-secrets scan
```

### 3. Validate bundle
```bash
databricks bundle validate --target dev
```

### 4. Run unit tests
```bash
pytest tests/ -v
```

---

## CI Status in GitHub

### On Pull Request:
- ✅ **Green checkmark** - All CI checks passed
- ❌ **Red X** - CI checks failed
- ⏳ **Yellow circle** - CI is running

### Branch Protection:
You can configure branch protection rules to:
- Require CI to pass before merging
- Require PR reviews
- Prevent force pushes

**Settings → Branches → Add rule**

---

## Troubleshooting CI Failures

### Common Issues:

1. **Secret scanning fails**
   - Remove the secret from code
   - Rotate the exposed secret
   - Use environment variables instead

2. **Bundle validation fails**
   - Check YAML syntax
   - Verify required fields are present
   - Run `databricks bundle validate` locally

3. **Unit tests fail**
   - Run tests locally: `pytest tests/ -v`
   - Fix failing tests
   - Check test output for details

4. **Compute verification fails**
   - Verify warehouse ID is correct
   - Check credentials have access
   - Ensure warehouse exists in workspace

---

## Summary

✅ **CI triggers automatically** on PRs and pushes  
✅ **Lints SQL files** for common issues  
✅ **Runs unit tests** to verify functionality  
✅ **Scans for secrets** to prevent exposure  
✅ **Validates bundle** configuration  
✅ **Verifies compute** profiles  
✅ **Fails CI** if any check fails  

**Result:** Only validated, tested code can be deployed! 🎉

