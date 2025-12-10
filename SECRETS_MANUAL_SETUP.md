# Manual GitHub Secrets Setup Guide

If you prefer to add secrets manually through the GitHub web interface, or if the automated script doesn't work, follow these instructions.

## Step-by-Step Instructions

### 1. Navigate to Repository Settings

1. Go to your repository on GitHub: `https://github.com/Shreya-egov/API_Automation`
2. Click on **Settings** (top menu)
3. In the left sidebar, click **Secrets and variables** → **Actions**

### 2. Add Each Secret

For each secret below, click **New repository secret** and enter:

---

#### Secret 1: BASE_URL

- **Name:** `BASE_URL`
- **Value:** `https://unified-qa.digit.org` (or your API base URL)
- Click **Add secret**

---

#### Secret 2: API_USERNAME

- **Name:** `API_USERNAME`
- **Value:** Your API username (e.g., `MDMSMZ`)
- Click **Add secret**

---

#### Secret 3: API_PASSWORD

- **Name:** `API_PASSWORD`
- **Value:** Your API password
- Click **Add secret**

---

#### Secret 4: TENANTID

- **Name:** `TENANTID`
- **Value:** `mz` (or your tenant ID)
- Click **Add secret**

---

#### Secret 5: USERTYPE

- **Name:** `USERTYPE`
- **Value:** `EMPLOYEE`
- Click **Add secret**

---

#### Secret 6: CLIENT_AUTH_HEADER

- **Name:** `CLIENT_AUTH_HEADER`
- **Value:** Your base64-encoded client credentials (e.g., `Basic ZWdvdi11c2VyLWNsaWVudDo=`)
- Click **Add secret**

---

#### Secret 7: LOCALE

- **Name:** `LOCALE`
- **Value:** `en_MZ` (or your default locale)
- Click **Add secret**

---

#### Secret 8: LOCALE_FRENCH

- **Name:** `LOCALE_FRENCH`
- **Value:** `fr_MZ` (or your French locale)
- Click **Add secret**

---

#### Secret 9: LOCALE_PORTUGUESE

- **Name:** `LOCALE_PORTUGUESE`
- **Value:** `pt_MZ` (or your Portuguese locale)
- Click **Add secret**

---

#### Secret 10: SEARCH_LIMIT

- **Name:** `SEARCH_LIMIT`
- **Value:** `200` (or your preferred limit)
- Click **Add secret**

---

#### Secret 11: SEARCH_OFFSET

- **Name:** `SEARCH_OFFSET`
- **Value:** `0` (or your preferred offset)
- Click **Add secret**

---

## Verification

After adding all secrets, you should see 11 secrets listed on the Actions secrets page:

```
✅ BASE_URL
✅ API_USERNAME
✅ API_PASSWORD
✅ TENANTID
✅ USERTYPE
✅ CLIENT_AUTH_HEADER
✅ LOCALE
✅ LOCALE_FRENCH
✅ LOCALE_PORTUGUESE
✅ SEARCH_LIMIT
✅ SEARCH_OFFSET
```

## Getting Values from .env File

If you have a `.env` file locally, you can view the values to copy:

```bash
# View your .env file (be careful - contains sensitive data!)
cat .env

# Or view specific variable
grep "BASE_URL" .env
grep "USERNAME" .env
```

**⚠️ Security Warning:**
- Never commit the `.env` file to git
- Never share screenshots of your secrets
- Keep the GitHub secrets page secure

## Testing the Setup

After adding secrets:

1. Go to **Actions** tab
2. Select **API Automation Tests** workflow
3. Click **Run workflow**
4. Select branch: `main`
5. Test group: `all`
6. Click **Run workflow**

The workflow should start and create a `.env` file from your secrets automatically.

## Troubleshooting

### Secret Not Showing Up

- Secrets are encrypted and hidden after creation
- You can update them by clicking **Update** next to the secret name
- You cannot view secret values after creation

### Workflow Still Failing

Check the workflow logs:
1. Go to **Actions** tab
2. Click on the failed workflow run
3. Click on the failed job
4. Expand the "Create .env file from secrets" step
5. Check if secrets are being loaded correctly

### Common Issues

**Issue:** "secret not found"
**Solution:** Check secret name matches exactly (case-sensitive)

**Issue:** "BASE_URL not found in .env"
**Solution:** Verify BASE_URL secret is set in GitHub

**Issue:** Authentication failures
**Solution:** Verify USERNAME, PASSWORD, and CLIENT_AUTH_HEADER are correct

---

## Alternative: Using GitHub CLI

If you have GitHub CLI installed, you can add secrets from command line:

```bash
# Install GitHub CLI first
# Ubuntu/Debian: sudo apt install gh
# macOS: brew install gh

# Authenticate
gh auth login

# Add secrets one by one
gh secret set BASE_URL
# Paste value when prompted

# Or from .env file (automated script)
./setup_github_secrets.sh
```

---

**Last Updated:** 2025-12-10
