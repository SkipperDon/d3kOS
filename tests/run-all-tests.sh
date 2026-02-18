#!/bin/bash
# run-all-tests.sh - d3kOS Master Test Runner
# Part of Distribution Prep Session 3: Testing & QA
# Executes all test scripts and generates HTML + JSON reports

set -e

# Test configuration
SCRIPT_NAME="d3kOS Test Suite - Master Runner"
TEST_DIR="$(dirname "$(readlink -f "$0")")"
REPORT_DIR="${TEST_DIR}/reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
HTML_REPORT="${REPORT_DIR}/test-report-${TIMESTAMP}.html"
JSON_REPORT="${REPORT_DIR}/test-report-${TIMESTAMP}.json"
LATEST_HTML="${REPORT_DIR}/test-report-latest.html"
LATEST_JSON="${REPORT_DIR}/test-report-latest.json"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test suite definition (order matters)
TEST_SCRIPTS=(
    "test-services.sh"
    "test-configuration.sh"
    "test-hardware.sh"
    "test-web-interface.sh"
    "test-data-flow.sh"
    "test-performance.sh"
    "test-known-issues.sh"
    "pre-distribution-checklist.sh"
)

# Test results storage
declare -A TEST_RESULTS
declare -A TEST_OUTPUTS
declare -A TEST_DURATIONS

# Print header
print_header() {
    clear
    echo "========================================="
    echo "$SCRIPT_NAME"
    echo "========================================="
    echo "Timestamp: $(date)"
    echo "Test Directory: $TEST_DIR"
    echo "Report Directory: $REPORT_DIR"
    echo ""
    echo "Running ${#TEST_SCRIPTS[@]} test suites..."
    echo ""
}

# Create report directory
mkdir -p "$REPORT_DIR"

print_header

# Make all test scripts executable
echo "Preparing test scripts..."
for script in "${TEST_SCRIPTS[@]}"; do
    if [ -f "$TEST_DIR/$script" ]; then
        chmod +x "$TEST_DIR/$script"
        echo -e "  ${GREEN}✓${NC} $script"
    else
        echo -e "  ${RED}✗${NC} $script (not found)"
    fi
done
echo ""

# Run all tests
echo "========================================="
echo "Executing Test Suites"
echo "========================================="
echo ""

TOTAL_PASSED=0
TOTAL_FAILED=0
TOTAL_WARNINGS=0
SUITE_COUNT=0
SUITE_PASSED=0
SUITE_FAILED=0

for script in "${TEST_SCRIPTS[@]}"; do
    if [ ! -f "$TEST_DIR/$script" ]; then
        echo -e "${RED}SKIP${NC}: $script (not found)"
        TEST_RESULTS[$script]="SKIP"
        TEST_OUTPUTS[$script]="Script file not found"
        continue
    fi

    ((SUITE_COUNT++))

    echo ""
    echo "─────────────────────────────────────────"
    echo -e "${BLUE}Running:${NC} $script"
    echo "─────────────────────────────────────────"

    # Run test and capture output
    start_time=$(date +%s)
    output_file=$(mktemp)

    if "$TEST_DIR/$script" > "$output_file" 2>&1; then
        exit_code=0
    else
        exit_code=$?
    fi

    end_time=$(date +%s)
    duration=$((end_time - start_time))
    TEST_DURATIONS[$script]=$duration

    # Store output
    TEST_OUTPUTS[$script]=$(cat "$output_file")
    rm -f "$output_file"

    # Parse results from output
    passed=$(echo "${TEST_OUTPUTS[$script]}" | grep -oP 'Tests Passed:\s+\K\d+' | tail -1 || echo "0")
    failed=$(echo "${TEST_OUTPUTS[$script]}" | grep -oP 'Tests Failed:\s+\K\d+' | tail -1 || echo "0")
    warnings=$(echo "${TEST_OUTPUTS[$script]}" | grep -oP 'Warnings:\s+\K\d+' | tail -1 || echo "0")

    TOTAL_PASSED=$((TOTAL_PASSED + passed))
    TOTAL_FAILED=$((TOTAL_FAILED + failed))
    TOTAL_WARNINGS=$((TOTAL_WARNINGS + warnings))

    # Determine suite result
    if [ $exit_code -eq 0 ]; then
        TEST_RESULTS[$script]="PASS"
        ((SUITE_PASSED++))
        echo -e "${GREEN}✓ SUITE PASSED${NC} ($passed passed, $failed failed, $warnings warnings) [${duration}s]"
    else
        TEST_RESULTS[$script]="FAIL"
        ((SUITE_FAILED++))
        echo -e "${RED}✗ SUITE FAILED${NC} ($passed passed, $failed failed, $warnings warnings) [${duration}s]"
    fi
done

# Generate JSON report
echo ""
echo "========================================="
echo "Generating Reports"
echo "========================================="
echo ""

cat > "$JSON_REPORT" <<EOF
{
  "test_run": {
    "timestamp": "$(date -Iseconds)",
    "hostname": "$(hostname)",
    "version": "$(cat /opt/d3kos/config/license.json 2>/dev/null | grep -oP '"version":\s*"\K[^"]+' || echo 'unknown')",
    "installation_id": "$(cat /opt/d3kos/config/license.json 2>/dev/null | grep -oP '"installation_id":\s*"\K[^"]+' || echo 'unknown')"
  },
  "summary": {
    "total_suites": $SUITE_COUNT,
    "suites_passed": $SUITE_PASSED,
    "suites_failed": $SUITE_FAILED,
    "total_tests": $((TOTAL_PASSED + TOTAL_FAILED)),
    "tests_passed": $TOTAL_PASSED,
    "tests_failed": $TOTAL_FAILED,
    "warnings": $TOTAL_WARNINGS
  },
  "test_suites": [
EOF

first=true
for script in "${TEST_SCRIPTS[@]}"; do
    if [ "$first" = true ]; then
        first=false
    else
        echo "," >> "$JSON_REPORT"
    fi

    result="${TEST_RESULTS[$script]}"
    duration="${TEST_DURATIONS[$script]:-0}"
    output=$(echo "${TEST_OUTPUTS[$script]}" | sed 's/"/\\"/g' | sed ':a;N;$!ba;s/\n/\\n/g')

    cat >> "$JSON_REPORT" <<EOF
    {
      "name": "$script",
      "result": "$result",
      "duration_seconds": $duration
    }
EOF
done

cat >> "$JSON_REPORT" <<EOF

  ]
}
EOF

echo -e "${GREEN}✓${NC} JSON report: $JSON_REPORT"

# Generate HTML report
cat > "$HTML_REPORT" <<'HTMLEOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>d3kOS Test Report</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #000000;
            color: #FFFFFF;
            padding: 20px;
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        header {
            background: #1a1a1a;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 30px;
            border-left: 5px solid #00CC00;
        }

        h1 {
            font-size: 32px;
            color: #00CC00;
            margin-bottom: 10px;
        }

        .meta {
            color: #888;
            font-size: 14px;
        }

        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .summary-card {
            background: #1a1a1a;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }

        .summary-card h3 {
            font-size: 14px;
            color: #888;
            margin-bottom: 10px;
            text-transform: uppercase;
        }

        .summary-card .value {
            font-size: 36px;
            font-weight: bold;
        }

        .summary-card.pass .value { color: #00CC00; }
        .summary-card.fail .value { color: #FF4444; }
        .summary-card.warn .value { color: #FFC107; }
        .summary-card.neutral .value { color: #FFFFFF; }

        .test-suites {
            background: #1a1a1a;
            padding: 30px;
            border-radius: 8px;
        }

        .test-suite {
            background: #0a0a0a;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 8px;
            border-left: 5px solid #555;
        }

        .test-suite.pass { border-left-color: #00CC00; }
        .test-suite.fail { border-left-color: #FF4444; }
        .test-suite.skip { border-left-color: #888; }

        .test-suite-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .test-suite-name {
            font-size: 18px;
            font-weight: bold;
        }

        .test-suite-result {
            padding: 5px 15px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 14px;
        }

        .test-suite-result.pass {
            background: #00CC00;
            color: #000;
        }

        .test-suite-result.fail {
            background: #FF4444;
            color: #FFF;
        }

        .test-suite-result.skip {
            background: #888;
            color: #FFF;
        }

        .test-suite-meta {
            font-size: 14px;
            color: #888;
        }

        .test-suite-output {
            background: #000000;
            padding: 15px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            color: #0F0;
            overflow-x: auto;
            white-space: pre-wrap;
            max-height: 400px;
            overflow-y: auto;
            margin-top: 15px;
            display: none;
        }

        .test-suite-output.visible {
            display: block;
        }

        .toggle-output {
            background: #333;
            color: #FFF;
            border: none;
            padding: 8px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            margin-top: 10px;
        }

        .toggle-output:hover {
            background: #444;
        }

        footer {
            text-align: center;
            color: #888;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #333;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>d3kOS Test Report</h1>
            <div class="meta">
                <strong>Timestamp:</strong> REPLACE_TIMESTAMP<br>
                <strong>Hostname:</strong> REPLACE_HOSTNAME<br>
                <strong>Version:</strong> REPLACE_VERSION<br>
                <strong>Installation ID:</strong> REPLACE_INSTALLATION_ID
            </div>
        </header>

        <div class="summary">
            <div class="summary-card neutral">
                <h3>Total Suites</h3>
                <div class="value">REPLACE_TOTAL_SUITES</div>
            </div>
            <div class="summary-card pass">
                <h3>Suites Passed</h3>
                <div class="value">REPLACE_SUITES_PASSED</div>
            </div>
            <div class="summary-card fail">
                <h3>Suites Failed</h3>
                <div class="value">REPLACE_SUITES_FAILED</div>
            </div>
            <div class="summary-card pass">
                <h3>Tests Passed</h3>
                <div class="value">REPLACE_TESTS_PASSED</div>
            </div>
            <div class="summary-card fail">
                <h3>Tests Failed</h3>
                <div class="value">REPLACE_TESTS_FAILED</div>
            </div>
            <div class="summary-card warn">
                <h3>Warnings</h3>
                <div class="value">REPLACE_WARNINGS</div>
            </div>
        </div>

        <div class="test-suites">
            <h2 style="margin-bottom: 20px;">Test Suite Results</h2>
            REPLACE_TEST_SUITES
        </div>

        <footer>
            <p>Generated by d3kOS Test Suite v1.0 | Distribution Prep Session 3</p>
        </footer>
    </div>

    <script>
        function toggleOutput(id) {
            const output = document.getElementById(id);
            const btn = event.target;
            if (output.classList.contains('visible')) {
                output.classList.remove('visible');
                btn.textContent = 'Show Output';
            } else {
                output.classList.add('visible');
                btn.textContent = 'Hide Output';
            }
        }
    </script>
</body>
</html>
HTMLEOF

# Replace placeholders in HTML
sed -i "s/REPLACE_TIMESTAMP/$(date)/" "$HTML_REPORT"
sed -i "s/REPLACE_HOSTNAME/$(hostname)/" "$HTML_REPORT"
sed -i "s/REPLACE_VERSION/$(cat /opt/d3kos/config/license.json 2>/dev/null | grep -oP '"version":\s*"\K[^"]+' || echo 'unknown')/" "$HTML_REPORT"
sed -i "s/REPLACE_INSTALLATION_ID/$(cat /opt/d3kos/config/license.json 2>/dev/null | grep -oP '"installation_id":\s*"\K[^"]+' || echo 'unknown')/" "$HTML_REPORT"
sed -i "s/REPLACE_TOTAL_SUITES/$SUITE_COUNT/" "$HTML_REPORT"
sed -i "s/REPLACE_SUITES_PASSED/$SUITE_PASSED/" "$HTML_REPORT"
sed -i "s/REPLACE_SUITES_FAILED/$SUITE_FAILED/" "$HTML_REPORT"
sed -i "s/REPLACE_TESTS_PASSED/$TOTAL_PASSED/" "$HTML_REPORT"
sed -i "s/REPLACE_TESTS_FAILED/$TOTAL_FAILED/" "$HTML_REPORT"
sed -i "s/REPLACE_WARNINGS/$TOTAL_WARNINGS/" "$HTML_REPORT"

# Generate test suite HTML blocks
suite_html=""
suite_id=0
for script in "${TEST_SCRIPTS[@]}"; do
    result="${TEST_RESULTS[$script]}"
    duration="${TEST_DURATIONS[$script]:-0}"
    output=$(echo "${TEST_OUTPUTS[$script]}" | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g')

    result_lower=$(echo "$result" | tr '[:upper:]' '[:lower:]')

    suite_html+="<div class=\"test-suite $result_lower\">"
    suite_html+="<div class=\"test-suite-header\">"
    suite_html+="<div class=\"test-suite-name\">$script</div>"
    suite_html+="<div class=\"test-suite-result $result_lower\">$result</div>"
    suite_html+="</div>"
    suite_html+="<div class=\"test-suite-meta\">Duration: ${duration}s</div>"
    suite_html+="<button class=\"toggle-output\" onclick=\"toggleOutput('output-$suite_id')\">Show Output</button>"
    suite_html+="<div class=\"test-suite-output\" id=\"output-$suite_id\">$output</div>"
    suite_html+="</div>"

    ((suite_id++))
done

sed -i "s|REPLACE_TEST_SUITES|$suite_html|" "$HTML_REPORT"

echo -e "${GREEN}✓${NC} HTML report: $HTML_REPORT"

# Create "latest" symlinks
ln -sf "$(basename "$HTML_REPORT")" "$LATEST_HTML"
ln -sf "$(basename "$JSON_REPORT")" "$LATEST_JSON"

echo -e "${GREEN}✓${NC} Latest HTML: $LATEST_HTML"
echo -e "${GREEN}✓${NC} Latest JSON: $LATEST_JSON"

# Print final summary
echo ""
echo "========================================="
echo "Test Run Complete"
echo "========================================="
echo ""
echo -e "Total Suites:   $SUITE_COUNT"
echo -e "Suites Passed:  ${GREEN}$SUITE_PASSED${NC}"
echo -e "Suites Failed:  ${RED}$SUITE_FAILED${NC}"
echo ""
echo -e "Total Tests:    $((TOTAL_PASSED + TOTAL_FAILED))"
echo -e "Tests Passed:   ${GREEN}$TOTAL_PASSED${NC}"
echo -e "Tests Failed:   ${RED}$TOTAL_FAILED${NC}"
echo -e "Warnings:       ${YELLOW}$TOTAL_WARNINGS${NC}"
echo ""

# Overall result
if [ $SUITE_FAILED -eq 0 ]; then
    echo -e "${GREEN}=========================================${NC}"
    echo -e "${GREEN}✓ ALL TEST SUITES PASSED${NC}"
    echo -e "${GREEN}=========================================${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}=========================================${NC}"
    echo -e "${RED}✗ SOME TEST SUITES FAILED${NC}"
    echo -e "${RED}=========================================${NC}"
    echo ""
    echo "Review the HTML report for details:"
    echo "  file://$HTML_REPORT"
    echo ""
    exit 1
fi
