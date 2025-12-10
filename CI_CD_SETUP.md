# CI/CD Setup Documentation

This document explains how to set up and use the CI/CD pipelines for the API Automation project.

## Table of Contents

- [Overview](#overview)
- [GitHub Actions Workflows](#github-actions-workflows)
- [Setup Instructions](#setup-instructions)
- [GitHub Secrets Configuration](#github-secrets-configuration)
- [Using the CI/CD Pipeline](#using-the-cicd-pipeline)
- [Test Reports](#test-reports)
- [Troubleshooting](#troubleshooting)

---

## Overview

The CI/CD pipeline is built using **GitHub Actions** and provides:

1. **Automated Testing**: Run pytest tests on push, PR, or manually
2. **Test Grouping**: Run specific test groups (boundary, localization, etc.)
3. **Multi-Python Support**: Tests run on Python 3.10, 3.11, and 3.12
4. **Test Reporting**: Generate HTML and Allure reports
5. **Code Quality**: Automated linting and security checks
6. **GitHub Pages**: Deploy Allure reports to GitHub Pages

---

## GitHub Actions Workflows

### 1. API Automation Tests (`.github/workflows/api-tests.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual trigger (workflow_dispatch)

**Features:**
- Runs tests on multiple Python versions (3.10, 3.11, 3.12)
- Supports test grouping (boundary, localization, generate, file_operations, process)
- Generates HTML and Allure test reports
- Uploads test artifacts (reports and outputs)
- Deploys Allure report to GitHub Pages (on main branch)

**Jobs:**
1. `test`: Run pytest tests on matrix of Python versions
2. `generate-allure-report`: Combine results and generate Allure report
3. `notify`: Create summary of pipeline results

### 2. Code Quality (`.github/workflows/code-quality.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual trigger (workflow_dispatch)

**Features:**
- **Linting**: flake8, pylint
- **Formatting**: black, isort
- **Security**: bandit security scan
- **Dependencies**: safety vulnerability check

**Jobs:**
1. `lint`: Code quality checks
2. `security`: Security vulnerability scan
3. `dependency-check`: Dependency vulnerability check

---

## Setup Instructions

### 1. Enable GitHub Actions

1. Go to your repository on GitHub
2. Click on **Settings** → **Actions** → **General**
3. Under "Actions permissions", select **Allow all actions and reusable workflows**
4. Click **Save**

### 2. Configure GitHub Secrets

GitHub Secrets are required to store sensitive credentials securely.

#### Steps:

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret from the table below

---

## GitHub Secrets Configuration

Add the following secrets to your repository:

| Secret Name | Description | Example Value |
|------------|-------------|---------------|
| `BASE_URL` | API base URL | `https://unified-qa.digit.org` |
| `API_USERNAME` | API username for authentication | `MDMSMZ` |
| `API_PASSWORD` | API password | `eGov@1234` |
| `TENANTID` | Tenant identifier | `mz` |
| `USERTYPE` | User type | `EMPLOYEE` |
| `CLIENT_AUTH_HEADER` | OAuth2 client auth header (base64) | `Basic ZWdvdi11c2VyLWNsaWVudDo=` |
| `LOCALE` | Default locale | `en_MZ` |
| `LOCALE_FRENCH` | French locale | `fr_MZ` |
| `LOCALE_PORTUGUESE` | Portuguese locale | `pt_MZ` |
| `SEARCH_LIMIT` | Search result limit | `200` |
| `SEARCH_OFFSET` | Search result offset | `0` |

**⚠️ Important:**
- Never commit secrets to the repository
- Use GitHub Secrets for CI/CD environments
- Keep `.env` file local only (it's in `.gitignore`)

---

## Using the CI/CD Pipeline

### Automatic Runs

The pipeline automatically runs on:

```bash
# Push to main or develop
git push origin main

# Create pull request to main or develop
gh pr create --base main
```

### Manual Trigger

You can manually trigger the test workflow with specific test groups:

1. Go to **Actions** tab on GitHub
2. Select **API Automation Tests** workflow
3. Click **Run workflow**
4. Select test group:
   - `all`: Run all tests (default)
   - `boundary`: Run boundary hierarchy tests
   - `localization`: Run localization tests
   - `generate`: Run data generation tests
   - `file_operations`: Run file upload/download tests
   - `process`: Run data processing tests
5. Click **Run workflow**

### Using GitHub CLI

```bash
# Trigger workflow manually
gh workflow run api-tests.yml

# Trigger with specific test group
gh workflow run api-tests.yml -f test_group=boundary

# View workflow runs
gh run list

# View logs for a specific run
gh run view <run-id>
```

---

## Test Reports

### 1. HTML Reports

**Location**: Available as workflow artifacts

**Access:**
1. Go to **Actions** tab
2. Click on the workflow run
3. Scroll to **Artifacts** section
4. Download `html-test-report-python-X.XX`

**Features:**
- Self-contained HTML file
- Pass/Fail summary
- Execution time
- Error details with stack traces

### 2. Allure Reports

**Location**: Deployed to GitHub Pages (main branch only)

**Access:**
- **URL**: `https://<username>.github.io/<repository>/`
- Example: `https://shreya-egov.github.io/API_Automation/`

**Setup GitHub Pages:**
1. Go to **Settings** → **Pages**
2. Under "Source", select **Deploy from a branch**
3. Select branch: `gh-pages`
4. Select folder: `/ (root)`
5. Click **Save**

**Features:**
- Interactive web-based report
- Test execution trends
- Historical data (last 20 reports)
- Detailed logs and attachments
- Test categorization

### 3. Test Outputs

**Location**: Available as workflow artifacts

**Access:**
1. Go to **Actions** tab
2. Click on the workflow run
3. Download `test-outputs-python-X.XX`

**Contents:**
- `output/ids.txt`: Generated hierarchy types and IDs
- `output/*.xlsx`: Generated templates and files

---

## Test Matrix

The pipeline runs tests on multiple Python versions:

| Python Version | Status |
|---------------|--------|
| 3.10 | ✅ Tested |
| 3.11 | ✅ Tested |
| 3.12 | ✅ Tested |

Each version generates separate test reports and artifacts.

---

## CI/CD Best Practices

### 1. Branch Protection

Protect your main branch with the following rules:

1. Go to **Settings** → **Branches**
2. Add branch protection rule for `main`
3. Enable:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
   - Select: `test (3.10)`, `test (3.11)`, `test (3.12)`
   - ✅ Require branches to be up to date before merging

### 2. Pull Request Workflow

```bash
# Create feature branch
git checkout -b feature/new-test

# Make changes
git add .
git commit -m "Add new test for X"

# Push branch
git push origin feature/new-test

# Create PR (tests run automatically)
gh pr create --base main --title "Add new test for X"

# After approval and tests pass, merge
gh pr merge --squash
```

### 3. Test Development

When developing tests:

1. Run tests locally first:
   ```bash
   pytest tests/ -v
   ```

2. Run specific test group:
   ```bash
   pytest -m boundary -v
   ```

3. Check code quality:
   ```bash
   flake8 tests/ utils/
   black --check tests/ utils/
   ```

4. Create PR to trigger CI/CD

---

## Troubleshooting

### Tests Failing in CI but Passing Locally

**Cause**: Environment differences or missing secrets

**Solution:**
1. Check GitHub Secrets are configured correctly
2. Verify `.env.example` matches required secrets
3. Check Python version compatibility
4. Review workflow logs for specific errors

### Allure Report Not Generating

**Cause**: Missing permissions or gh-pages branch

**Solution:**
1. Verify GitHub Pages is enabled
2. Check workflow has write permissions:
   - Go to **Settings** → **Actions** → **General**
   - Under "Workflow permissions", select **Read and write permissions**
3. Ensure `gh-pages` branch exists

### Secret Not Found Error

**Cause**: Missing or incorrect secret name

**Solution:**
1. Check secret names match exactly (case-sensitive)
2. Verify secrets are added to repository (not organization)
3. Re-add the secret if needed

### Workflow Not Triggering

**Cause**: Workflow file syntax error or branch protection

**Solution:**
1. Validate YAML syntax: `yamllint .github/workflows/*.yml`
2. Check workflow is enabled in Actions tab
3. Verify branch is not protected from running workflows

### Tests Timeout

**Cause**: API endpoint slowness or network issues

**Solution:**
1. Check API endpoint availability
2. Increase timeout in workflow (default: 360 minutes)
3. Review specific test logs for bottlenecks

---

## Monitoring and Notifications

### GitHub Actions Status Badge

Add to your README.md:

```markdown
![API Tests](https://github.com/<username>/<repository>/actions/workflows/api-tests.yml/badge.svg)
![Code Quality](https://github.com/<username>/<repository>/actions/workflows/code-quality.yml/badge.svg)
```

### Notifications

Configure notifications in GitHub:
1. **Settings** → **Notifications**
2. Under "Actions", select notification preferences
3. Options:
   - Email on workflow failure
   - Slack/Discord webhooks (requires additional setup)

---

## Advanced Configuration

### Custom Test Schedule

Add scheduled runs to `.github/workflows/api-tests.yml`:

```yaml
on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight UTC
    - cron: '0 9,17 * * 1-5'  # 9 AM and 5 PM on weekdays
```

### Conditional Test Execution

Run tests only on specific file changes:

```yaml
on:
  push:
    branches: [ main, develop ]
    paths:
      - 'tests/**'
      - 'utils/**'
      - 'payloads/**'
      - 'requirements.txt'
```

### Environment-Specific Tests

Create separate workflows for different environments:
- `api-tests-qa.yml` for QA environment
- `api-tests-staging.yml` for Staging environment
- `api-tests-prod.yml` for Production environment (manual trigger only)

---

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Pytest Documentation](https://docs.pytest.org/)
- [Allure Report Documentation](https://docs.qameta.io/allure/)
- [GitHub Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

---

## Support

For issues or questions:
- Create an issue: https://github.com/Shreya-egov/API_Automation/issues
- Review workflow logs in Actions tab
- Check this documentation

---

**Last Updated**: 2025-12-10
