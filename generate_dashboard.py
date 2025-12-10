#!/usr/bin/env python3
"""
Enhanced Test Results Dashboard Generator

This script generates an interactive HTML dashboard from pytest JSON results.
Features: expandable test details, API responses, metrics, and interactive charts.
"""

import json
import os
import html
from datetime import datetime
from pathlib import Path


def load_test_results(json_path):
    """Load test results from pytest JSON report"""
    if not os.path.exists(json_path):
        print(f"❌ Error: Test results file not found: {json_path}")
        print("Run tests with: pytest tests/ --json-report --json-report-file=.test_report.json")
        return None

    with open(json_path, 'r') as f:
        return json.load(f)


def extract_entities_from_stdout(stdout):
    """Extract created entities from stdout"""
    entities = []
    if not stdout:
        return entities

    lines = stdout.split('\n')
    for line in lines:
        # Look for common patterns of created entities
        if 'created' in line.lower() or 'generated' in line.lower() or 'uploaded' in line.lower():
            entities.append(line.strip())
        elif ':' in line and any(keyword in line.lower() for keyword in ['id', 'type', 'hierarchy', 'file', 'process']):
            entities.append(line.strip())

    return entities


def calculate_metrics(data):
    """Calculate test metrics from results"""
    summary = data.get('summary', {})
    tests = data.get('tests', [])

    total = summary.get('total', 0)
    passed = summary.get('passed', 0)
    failed = summary.get('failed', 0)
    skipped = summary.get('skipped', 0)

    pass_rate = (passed / total * 100) if total > 0 else 0

    # Calculate execution time
    duration = data.get('duration', 0)

    # Group tests by marker/category
    categories = {
        'boundary': [],
        'localization': [],
        'generate': [],
        'file_operations': [],
        'process': [],
        'other': []
    }

    for test in tests:
        nodeid = test.get('nodeid', '')
        # Extract markers from nodeid or metadata
        categorized = False

        # Try to get from nodeid
        for cat in ['boundary', 'localization', 'generate', 'file_operations', 'process']:
            if cat in nodeid.lower():
                categories[cat].append(test)
                categorized = True
                break

        if not categorized:
            categories['other'].append(test)

    # Calculate average duration
    avg_duration = duration / total if total > 0 else 0

    # Get slowest tests
    sorted_tests = sorted(tests, key=lambda t: t.get('call', {}).get('duration', 0), reverse=True)
    slowest_tests = sorted_tests[:5]

    # Get failed tests with details
    failed_tests = [t for t in tests if t.get('outcome') == 'failed']

    return {
        'total': total,
        'passed': passed,
        'failed': failed,
        'skipped': skipped,
        'pass_rate': pass_rate,
        'duration': duration,
        'avg_duration': avg_duration,
        'categories': categories,
        'slowest_tests': slowest_tests,
        'failed_tests': failed_tests
    }


def get_test_details(tests):
    """Get detailed test information including stdout and entities"""
    details = []
    for test in tests:
        call_data = test.get('call', {})
        duration = call_data.get('duration', 0)
        stdout = call_data.get('stdout', '')

        # Extract entities from stdout
        entities = extract_entities_from_stdout(stdout)

        # Get error info for failed tests
        error_msg = ''
        if test.get('outcome') == 'failed':
            crash = call_data.get('crash', {})
            error_msg = crash.get('message', call_data.get('longrepr', ''))

        details.append({
            'name': test.get('nodeid', 'Unknown'),
            'outcome': test.get('outcome', 'unknown'),
            'duration': duration,
            'setup_duration': test.get('setup', {}).get('duration', 0),
            'teardown_duration': test.get('teardown', {}).get('duration', 0),
            'stdout': stdout,
            'entities': entities,
            'error_msg': error_msg
        })
    return details


def generate_dashboard_html(metrics, test_details, output_path):
    """Generate enhanced HTML dashboard with expandable test details"""

    categories_data = []
    for cat, tests in metrics['categories'].items():
        if tests:  # Only include non-empty categories
            passed = sum(1 for t in tests if t.get('outcome') == 'passed')
            failed = sum(1 for t in tests if t.get('outcome') == 'failed')
            skipped = sum(1 for t in tests if t.get('outcome') == 'skipped')
            total_cat = len(tests)
            pass_rate_cat = (passed / total_cat * 100) if total_cat > 0 else 0
            categories_data.append({
                'name': cat.replace('_', ' ').title(),
                'total': total_cat,
                'passed': passed,
                'failed': failed,
                'skipped': skipped,
                'pass_rate': pass_rate_cat
            })

    # Prepare slowest tests data
    slowest_tests_html = ""
    for idx, test in enumerate(metrics['slowest_tests'], 1):
        test_name = test.get('nodeid', '').split('::')[-1]
        duration = test.get('call', {}).get('duration', 0)
        slowest_tests_html += f'''
            <tr>
                <td>{idx}</td>
                <td>{test_name}</td>
                <td>{duration:.2f}s</td>
            </tr>
        '''

    # Prepare failed tests details
    failed_tests_html = ""
    if metrics['failed_tests']:
        for test in metrics['failed_tests']:
            test_name = test.get('nodeid', '').split('::')[-1]
            error_msg = test.get('call', {}).get('longrepr', 'No error message available')
            # Truncate error message
            if len(error_msg) > 800:
                error_msg = error_msg[:800] + "..."
            failed_tests_html += f'''
                <div class="failure-item">
                    <h4>{test_name}</h4>
                    <pre class="error-message">{html.escape(error_msg)}</pre>
                </div>
            '''
    else:
        failed_tests_html = '<p class="no-failures">🎉 No test failures!</p>'

    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Automation Test Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1600px;
            margin: 0 auto;
        }}

        .header {{
            text-align: center;
            color: white;
            margin-bottom: 40px;
            animation: fadeInDown 0.6s ease;
        }}

        .header h1 {{
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
        }}

        .header p {{
            font-size: 1.2em;
            opacity: 0.95;
        }}

        @keyframes fadeInDown {{
            from {{
                opacity: 0;
                transform: translateY(-20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
            animation: fadeInUp 0.6s ease 0.2s both;
        }}

        .metric-card {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }}

        .metric-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, var(--card-color-1), var(--card-color-2));
        }}

        .metric-card:hover {{
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 20px 50px rgba(0,0,0,0.3);
        }}

        .metric-card h3 {{
            color: #666;
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 15px;
            font-weight: 600;
        }}

        .metric-card .value {{
            font-size: 3.5em;
            font-weight: 700;
            line-height: 1;
            color: #333;
        }}

        .metric-card .sub-value {{
            font-size: 0.9em;
            color: #999;
            margin-top: 8px;
        }}

        .metric-card.passed {{ --card-color-1: #10b981; --card-color-2: #34d399; }}
        .metric-card.passed .value {{ color: #10b981; }}

        .metric-card.failed {{ --card-color-1: #ef4444; --card-color-2: #f87171; }}
        .metric-card.failed .value {{ color: #ef4444; }}

        .metric-card.skipped {{ --card-color-1: #f59e0b; --card-color-2: #fbbf24; }}
        .metric-card.skipped .value {{ color: #f59e0b; }}

        .metric-card.total {{ --card-color-1: #3b82f6; --card-color-2: #60a5fa; }}
        .metric-card.total .value {{ color: #3b82f6; }}

        .metric-card.rate {{ --card-color-1: #8b5cf6; --card-color-2: #a78bfa; }}
        .metric-card.rate .value {{ color: #8b5cf6; }}

        .metric-card.avg {{ --card-color-1: #ec4899; --card-color-2: #f472b6; }}
        .metric-card.avg .value {{ color: #ec4899; font-size: 2.8em; }}

        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
            animation: fadeInUp 0.6s ease 0.4s both;
        }}

        .chart-card {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            transition: box-shadow 0.3s ease;
        }}

        .chart-card:hover {{
            box-shadow: 0 15px 50px rgba(0,0,0,0.25);
        }}

        .chart-card h2 {{
            color: #333;
            margin-bottom: 25px;
            font-size: 1.5em;
            font-weight: 600;
        }}

        .section {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            margin-bottom: 30px;
            animation: fadeInUp 0.6s ease 0.6s both;
        }}

        .section h2 {{
            color: #333;
            margin-bottom: 25px;
            font-size: 1.8em;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th, td {{
            padding: 14px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }}

        th {{
            background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
            font-weight: 700;
            color: #374151;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 1px;
        }}

        .test-row {{
            cursor: pointer;
            transition: background 0.2s ease;
        }}

        .test-row:hover {{
            background: #f9fafb;
        }}

        .test-row.clickable td:first-child {{
            color: #3b82f6;
            font-weight: 600;
        }}

        .test-row.clickable td:first-child:hover {{
            text-decoration: underline;
        }}

        .test-details-row {{
            display: none;
            background: #f8fafc;
        }}

        .test-details-row.visible {{
            display: table-row;
        }}

        .test-details-cell {{
            padding: 25px !important;
            border-left: 4px solid #3b82f6;
        }}

        .test-details-content {{
            display: grid;
            gap: 20px;
        }}

        .details-section {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #e5e7eb;
        }}

        .details-section h4 {{
            color: #374151;
            margin-bottom: 12px;
            font-size: 1.1em;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .entity-list {{
            list-style: none;
            padding: 0;
        }}

        .entity-list li {{
            padding: 8px 12px;
            background: #f0fdf4;
            border-left: 3px solid #10b981;
            margin-bottom: 8px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}

        .output-box {{
            background: #1e293b;
            color: #e2e8f0;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
            line-height: 1.6;
            overflow-x: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}

        .no-data {{
            color: #9ca3af;
            font-style: italic;
            text-align: center;
            padding: 20px;
        }}

        .status-badge {{
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .status-passed {{ background: #d1fae5; color: #065f46; }}
        .status-failed {{ background: #fee2e2; color: #991b1b; }}
        .status-skipped {{ background: #fef3c7; color: #92400e; }}

        .failure-item {{
            background: #fef2f2;
            border-left: 4px solid #ef4444;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}

        .failure-item h4 {{
            color: #991b1b;
            margin-bottom: 10px;
            font-size: 1.1em;
        }}

        .error-message {{
            background: #fff;
            padding: 15px;
            border-radius: 6px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
            color: #444;
            line-height: 1.5;
            border: 1px solid #fee2e2;
            white-space: pre-wrap;
        }}

        .no-failures {{
            text-align: center;
            color: #10b981;
            font-size: 1.2em;
            padding: 40px;
        }}

        .expand-icon {{
            transition: transform 0.3s ease;
            display: inline-block;
            margin-right: 8px;
            font-size: 0.8em;
        }}

        .test-row.expanded .expand-icon {{
            transform: rotate(90deg);
        }}

        .footer {{
            text-align: center;
            color: white;
            margin-top: 40px;
            opacity: 0.9;
            animation: fadeInUp 0.6s ease 0.8s both;
        }}

        @media (max-width: 768px) {{
            .header h1 {{ font-size: 2em; }}
            .charts-grid {{ grid-template-columns: 1fr; }}
            .metric-card .value {{ font-size: 2.5em; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 API Automation Test Dashboard</h1>
            <p>Generated on {datetime.now().strftime("%B %d, %Y at %I:%M:%S %p")}</p>
        </div>

        <div class="metrics-grid">
            <div class="metric-card total">
                <h3>Total Tests</h3>
                <div class="value">{metrics['total']}</div>
            </div>
            <div class="metric-card passed">
                <h3>Passed</h3>
                <div class="value">{metrics['passed']}</div>
                <div class="sub-value">{metrics['pass_rate']:.1f}% success rate</div>
            </div>
            <div class="metric-card failed">
                <h3>Failed</h3>
                <div class="value">{metrics['failed']}</div>
            </div>
            <div class="metric-card skipped">
                <h3>Skipped</h3>
                <div class="value">{metrics['skipped']}</div>
            </div>
            <div class="metric-card rate">
                <h3>Pass Rate</h3>
                <div class="value">{metrics['pass_rate']:.1f}%</div>
            </div>
            <div class="metric-card avg">
                <h3>Avg Duration</h3>
                <div class="value">{metrics['avg_duration']:.2f}s</div>
                <div class="sub-value">per test</div>
            </div>
        </div>

        <div class="section">
            <h2>🐌 Slowest Tests</h2>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Test Name</th>
                        <th>Duration</th>
                    </tr>
                </thead>
                <tbody>
                    {slowest_tests_html}
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>❌ Failed Tests Details</h2>
            {failed_tests_html}
        </div>

        <div class="section">
            <h2>📋 All Test Results <span style="font-size: 0.6em; font-weight: 400; color: #6b7280;">(Click test name to expand details)</span></h2>
            <table id="testResultsTable">
                <thead>
                    <tr>
                        <th>Test Name</th>
                        <th>Status</th>
                        <th>Entities Created</th>
                    </tr>
                </thead>
                <tbody>
'''

    for idx, test in enumerate(test_details):
        test_name = test['name'].split('::')[-1] if '::' in test['name'] else test['name']
        status_class = f"status-{test['outcome']}"

        # Get entities summary
        entities_summary = f"{len(test['entities'])} entities" if test['entities'] else "No entities"

        # Escape HTML in data
        stdout_escaped = html.escape(test['stdout']) if test['stdout'] else 'No output captured'
        error_escaped = html.escape(test['error_msg']) if test['error_msg'] else ''

        # Build entities HTML
        entities_html = ""
        if test['entities']:
            for entity in test['entities']:
                entities_html += f"<li>{html.escape(entity)}</li>"
        else:
            entities_html = '<p class="no-data">No entities created in this test</p>'

        html_content += f'''
                    <tr class="test-row clickable" data-test-id="{idx}">
                        <td><span class="expand-icon">▶</span>{test_name}</td>
                        <td><span class="status-badge {status_class}">{test['outcome']}</span></td>
                        <td>{entities_summary}</td>
                    </tr>
                    <tr class="test-details-row" id="details-{idx}">
                        <td colspan="3" class="test-details-cell">
                            <div class="test-details-content">
                                <div class="details-section">
                                    <h4>📦 Created Entities</h4>
                                    {"<ul class='entity-list'>" + entities_html + "</ul>" if test['entities'] else entities_html}
                                </div>
                                <div class="details-section">
                                    <h4>💬 Test Output</h4>
                                    <div class="output-box">{stdout_escaped}</div>
                                </div>
'''

        if test['outcome'] == 'failed' and error_escaped:
            html_content += f'''
                                <div class="details-section">
                                    <h4>🚨 Error Details</h4>
                                    <div class="error-message">{error_escaped}</div>
                                </div>
'''

        html_content += '''
                            </div>
                        </td>
                    </tr>
'''

    # Prepare categories data for JavaScript
    categories_json = json.dumps(categories_data)

    html_content += f'''
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p>✨ API Automation Framework - Enhanced Test Results Dashboard ✨</p>
            <p style="margin-top: 10px; opacity: 0.8;">Powered by Chart.js | Generated with Python</p>
        </div>
    </div>

    <script>
        // Test row click handler for expandable details
        document.querySelectorAll('.test-row.clickable').forEach(row => {{
            row.addEventListener('click', function() {{
                const testId = this.getAttribute('data-test-id');
                const detailsRow = document.getElementById('details-' + testId);

                // Toggle visibility
                detailsRow.classList.toggle('visible');
                this.classList.toggle('expanded');
            }});
        }});

    </script>
</body>
</html>
'''

    # Write HTML file
    with open(output_path, 'w') as f:
        f.write(html_content)

    print(f"✅ Dashboard generated successfully: {output_path}")


def main():
    """Main function"""
    # Paths
    json_path = ".test_report.json"
    output_path = "reports/dashboard.html"

    # Ensure reports directory exists
    os.makedirs("reports", exist_ok=True)

    print("=" * 70)
    print("Enhanced API Automation Test Dashboard Generator")
    print("=" * 70)
    print()

    # Load test results
    print(f"📄 Loading test results from: {json_path}")
    data = load_test_results(json_path)

    if not data:
        return 1

    # Calculate metrics
    print("📊 Calculating metrics...")
    metrics = calculate_metrics(data)

    # Get test details
    print("🔍 Extracting test details and entities...")
    test_details = get_test_details(data.get('tests', []))

    # Generate dashboard
    print(f"🎨 Generating enhanced dashboard with expandable details...")
    generate_dashboard_html(metrics, test_details, output_path)

    print()
    print("=" * 70)
    print("📈 Dashboard Statistics:")
    print(f"  Total Tests: {metrics['total']}")
    print(f"  ✅ Passed: {metrics['passed']}")
    print(f"  ❌ Failed: {metrics['failed']}")
    print(f"  ⏭️  Skipped: {metrics['skipped']}")
    print(f"  📊 Pass Rate: {metrics['pass_rate']:.1f}%")
    print(f"  ⌛ Avg Duration: {metrics['avg_duration']:.2f}s")
    print("=" * 70)
    print()
    print(f"🎉 Open the dashboard: file://{os.path.abspath(output_path)}")
    print(f"💡 Tip: Click on test names to expand and see created entities & responses!")
    print()

    return 0


if __name__ == "__main__":
    exit(main())
