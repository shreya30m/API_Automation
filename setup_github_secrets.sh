#!/bin/bash

# Helper script to add GitHub Actions secrets from .env file
# This script requires GitHub CLI (gh) to be installed and authenticated

set -e

echo "========================================"
echo "GitHub Actions Secrets Setup"
echo "========================================"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed."
    echo ""
    echo "To install GitHub CLI:"
    echo "  Ubuntu/Debian: sudo apt install gh"
    echo "  macOS: brew install gh"
    echo "  Or visit: https://cli.github.com/manual/installation"
    echo ""
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ GitHub CLI is not authenticated."
    echo ""
    echo "Please authenticate with:"
    echo "  gh auth login"
    echo ""
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found"
    echo ""
    echo "Please create a .env file with your configuration."
    echo "You can copy .env.example as a template."
    echo ""
    exit 1
fi

echo "✅ GitHub CLI is installed and authenticated"
echo "✅ .env file found"
echo ""

# Load .env file
source .env

# Mapping of environment variables to GitHub secret names
declare -A SECRET_MAP=(
    ["BASE_URL"]="BASE_URL"
    ["USERNAME"]="API_USERNAME"
    ["PASSWORD"]="API_PASSWORD"
    ["TENANTID"]="TENANTID"
    ["USERTYPE"]="USERTYPE"
    ["CLIENT_AUTH_HEADER"]="CLIENT_AUTH_HEADER"
    ["LOCALE"]="LOCALE"
    ["LOCALE_FRENCH"]="LOCALE_FRENCH"
    ["LOCALE_PORTUGUESE"]="LOCALE_PORTUGUESE"
    ["SEARCH_LIMIT"]="SEARCH_LIMIT"
    ["SEARCH_OFFSET"]="SEARCH_OFFSET"
)

echo "Adding secrets to GitHub Actions..."
echo ""

# Counter for tracking
total=0
success=0
failed=0

# Add each secret
for env_var in "${!SECRET_MAP[@]}"; do
    secret_name="${SECRET_MAP[$env_var]}"

    # Get value from environment variable
    value="${!env_var}"

    ((total++))

    if [ -z "$value" ]; then
        echo "⚠️  Skipping $secret_name (not set in .env)"
        ((failed++))
        continue
    fi

    # Add secret to GitHub
    if echo "$value" | gh secret set "$secret_name" 2>/dev/null; then
        echo "✅ Added secret: $secret_name"
        ((success++))
    else
        echo "❌ Failed to add secret: $secret_name"
        ((failed++))
    fi
done

echo ""
echo "========================================"
echo "Summary"
echo "========================================"
echo "Total secrets: $total"
echo "Successfully added: $success"
echo "Failed/Skipped: $failed"
echo ""

if [ $success -eq $total ]; then
    echo "🎉 All secrets added successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Commit and push your CI/CD changes"
    echo "2. The GitHub Actions workflows will run automatically"
    echo "3. View results in the Actions tab on GitHub"
else
    echo "⚠️  Some secrets were not added."
    echo ""
    echo "Please check:"
    echo "1. All required variables are set in .env"
    echo "2. You have admin access to the repository"
    echo "3. GitHub CLI has proper permissions"
fi

echo ""
