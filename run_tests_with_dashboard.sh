#!/bin/bash

# Run tests and generate dashboard
# This script runs pytest with all reporting options and generates the dashboard

set -e

echo "========================================"
echo "API Automation Tests with Dashboard"
echo "========================================"
echo ""

# Ensure reports directory exists
mkdir -p reports output

# Parse arguments
TEST_GROUP="${1:-all}"

echo "Running tests..."
echo "Test group: $TEST_GROUP"
echo ""

# Run tests with all reporting options
if [ "$TEST_GROUP" = "all" ]; then
    pytest tests/ -v \
        --html=reports/report.html --self-contained-html \
        --alluredir=allure-results \
        --json-report --json-report-file=.test_report.json
else
    pytest -m "$TEST_GROUP" -v \
        --html=reports/report.html --self-contained-html \
        --alluredir=allure-results \
        --json-report --json-report-file=.test_report.json
fi

TEST_EXIT_CODE=$?

echo ""
echo "Generating dashboard..."
python3 generate_dashboard.py

echo ""
echo "========================================"
echo "Reports Generated:"
echo "========================================"
echo "  📊 Dashboard:    reports/dashboard.html"
echo "  📄 HTML Report:  reports/report.html"
echo "  📈 Allure:       allure-results/"
echo ""
echo "To open dashboard:"
echo "  xdg-open reports/dashboard.html    # Linux"
echo "  open reports/dashboard.html        # macOS"
echo "  start reports/dashboard.html       # Windows"
echo ""

# Exit with test exit code
exit $TEST_EXIT_CODE
