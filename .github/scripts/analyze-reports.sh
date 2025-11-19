#!/bin/bash

REPORTS_DIR="downloaded-reports"

echo "=== Downloaded Quality Reports ==="
ls -la "$REPORTS_DIR/"

echo -e "\n=== Summary Report ==="
cat "$REPORTS_DIR/summary.txt"

echo -e "\n=== Security Issues ==="
if grep -q "Issue" "$REPORTS_DIR/security-report.txt"; then
    echo "Security issues found!"
    grep "Issue" "$REPORTS_DIR/security-report.txt" || true
else
    echo "No security issues detected"
fi

echo -e "\n=== Linting Issues ==="
if grep -E ":[0-9]+:[0-9]+:" "$REPORTS_DIR/flake8-report.txt"; then
    echo "Linting issues found!"
else
    echo "No linting issues detected"
fi