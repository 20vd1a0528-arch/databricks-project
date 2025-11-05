# GitHub Actions Conditional Examples

## Common `if` Conditions

### 1. Run only on push to main
```yaml
if: github.event_name == 'push' && github.ref == 'refs/heads/main'
```

### 2. Run only on pull requests
```yaml
if: github.event_name == 'pull_request'
```

### 3. Run only on specific branches
```yaml
if: github.ref == 'refs/heads/develop'
```

### 4. Run on push to main OR develop
```yaml
if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop')
```

### 5. Run only if previous step succeeded
```yaml
if: success()
```

### 6. Run only if previous step failed
```yaml
if: failure()
```

### 7. Run on tags (releases)
```yaml
if: startsWith(github.ref, 'refs/tags/')
```

### 8. Run on manual workflow dispatch
```yaml
if: github.event_name == 'workflow_dispatch'
```

### 9. Run on push to main AND previous step succeeded
```yaml
if: github.event_name == 'push' && github.ref == 'refs/heads/main' && success()
```

### 10. Skip on draft pull requests
```yaml
if: github.event_name == 'pull_request' && github.event.pull_request.draft == false
```

## Useful GitHub Context Variables

- `github.event_name` - The event that triggered the workflow (push, pull_request, etc.)
- `github.ref` - The Git reference (branch or tag) that triggered the workflow
- `github.ref_name` - Short branch/tag name (e.g., "main" instead of "refs/heads/main")
- `github.sha` - Commit SHA that triggered the workflow
- `github.actor` - Username of the person who triggered the workflow
- `github.repository` - Repository name (owner/repo)

## Common Patterns

### Deploy to dev on push to main, prod on tags
```yaml
- name: Deploy to Dev
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
  run: databricks bundle deploy --target dev

- name: Deploy to Prod
  if: startsWith(github.ref, 'refs/tags/v')
  run: databricks bundle deploy --target prod
```

### Different actions for different branches
```yaml
- name: Deploy Dev
  if: github.ref == 'refs/heads/develop'
  run: deploy-dev.sh

- name: Deploy Staging
  if: github.ref == 'refs/heads/staging'
  run: deploy-staging.sh

- name: Deploy Prod
  if: github.ref == 'refs/heads/main'
  run: deploy-prod.sh
```

