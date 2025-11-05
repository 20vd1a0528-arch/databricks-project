# Troubleshooting: Changes Not Reflected in Databricks

## Quick Checklist

### 1. Check GitHub Actions Status ✅

**Go to GitHub:**
1. Open your repository on GitHub
2. Click the **"Actions"** tab
3. Look for the most recent workflow run
4. Check if it:
   - ✅ Completed successfully (green checkmark)
   - ❌ Failed (red X)
   - ⏳ Is still running (yellow circle)

**If it failed:**
- Click on the failed run
- Check which step failed
- Look at the error logs

---

### 2. Verify GitHub Secrets Are Set ✅

**Check secrets:**
1. Go to repository **Settings** → **Secrets and variables** → **Actions**
2. Verify these secrets exist:
   - `DATABRICKS_HOST`
   - `DATABRICKS_TOKEN`

**If secrets are missing:**
- The workflow will fail at authentication step
- You'll see error: "DATABRICKS_HOST or DATABRICKS_TOKEN not set"

---

### 3. Check Deployment Step Ran ✅

In the GitHub Actions run, verify:
- ✅ Step "Deploy Bundle to Dev" ran
- ✅ No errors in deployment step

**If deployment step was skipped:**
- Check the condition: `if: github.event_name == 'push' && github.ref == 'refs/heads/main'`
- Make sure you pushed to `main` branch (not a feature branch)

---

### 4. Manual Deployment Test ✅

Test deployment locally:

```bash
cd databricks-project

# Validate first
databricks bundle validate --target dev

# Deploy manually
databricks bundle deploy --target dev
```

**If this works:**
- The issue is with GitHub Actions
- Check GitHub Actions logs

**If this fails:**
- The issue is with your configuration
- Check the error message

---

### 5. Verify File Path in Configuration ✅

Check that `databricks.yml` points to the correct file:

```yaml
sql_task:
  file:
    path: ./assets/notebooks/transform_data.sql  # ← Verify this path
```

**If you added a new file:**
- Update `databricks.yml` to point to the new file
- Or update the existing file that's referenced

---

### 6. Check Databricks Workspace ✅

**In Databricks:**
1. Go to **Workflows** → **Jobs**
2. Find your job: "Daily Sales Job (SQL Warehouse)"
3. Click on it
4. Check:
   - ✅ Job exists
   - ✅ Last updated time
   - ✅ SQL file content matches your local file

**If job doesn't exist:**
- Deployment didn't happen
- Check GitHub Actions logs

**If job exists but content is old:**
- Deployment happened but didn't update
- Try redeploying

---

## Common Issues & Solutions

### Issue 1: GitHub Actions Didn't Run

**Symptoms:**
- No workflow run in Actions tab
- Push happened but nothing triggered

**Solution:**
- Check workflow file exists: `.github/workflows/databricks-bundle.yml`
- Verify file is in `main` branch
- Check workflow syntax is valid

---

### Issue 2: Workflow Failed

**Symptoms:**
- Red X in Actions tab
- Error in logs

**Common errors:**

**Authentication failed:**
```
Error: DATABRICKS_HOST or DATABRICKS_TOKEN not set
```
**Solution:** Add secrets in GitHub repository settings

**Validation failed:**
```
Error: Bundle validation failed
```
**Solution:** Run `databricks bundle validate --target dev` locally to see error

**Deployment failed:**
```
Error: Failed to deploy bundle
```
**Solution:** Check Databricks workspace access and credentials

---

### Issue 3: Deployment Step Skipped

**Symptoms:**
- Workflow ran but deployment step was skipped
- All steps passed but nothing deployed

**Solution:**
- Check the condition in workflow
- Verify you pushed to `main` branch
- Not a PR or feature branch

---

### Issue 4: Wrong File Deployed

**Symptoms:**
- Deployment succeeded but wrong file content in Databricks

**Solution:**
- Check `databricks.yml` file path
- Verify local file matches what you want
- Redeploy if needed

---

## Step-by-Step Debugging

### Step 1: Check GitHub Actions
```bash
# Go to GitHub → Actions tab
# Look for your latest push
```

### Step 2: Check Workflow Logs
```bash
# Click on the workflow run
# Check each step
# Look for errors
```

### Step 3: Test Locally
```bash
cd databricks-project
databricks bundle validate --target dev
databricks bundle deploy --target dev
```

### Step 4: Verify in Databricks
```bash
# Go to Databricks workspace
# Check Workflows → Jobs
# Verify job content
```

---

## Quick Fix: Manual Deployment

If you need to deploy immediately:

```bash
cd databricks-project

# 1. Validate
databricks bundle validate --target dev

# 2. Deploy
databricks bundle deploy --target dev

# 3. Verify
databricks bundle resources list --target dev
```

---

## Still Not Working?

1. **Check GitHub Actions logs** - Most detailed error info
2. **Check Databricks workspace** - Verify job exists and is updated
3. **Test locally** - Isolate if it's a CI/CD issue or config issue
4. **Verify credentials** - Make sure GitHub Secrets are correct
5. **Check file paths** - Ensure databricks.yml points to correct files

