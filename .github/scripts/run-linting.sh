#!/bin/bash

RESULTS_DIR="quality-results"
REPORT_FILE="$RESULTS_DIR/flake8-report.txt"

echo "=== Flake8 Linting Results ===" > "$REPORT_FILE"
echo "Scan started: $(date)" >> "$REPORT_FILE"

if [ -d "distcp-incremental-tech-talk/cloud_function_composer2/" ]; then
    flake8 distcp-incremental-tech-talk/cloud_function_composer2/ --max-line-length=88 --extend-ignore=E203,W503 >> "$REPORT_FILE" 2>&1 || true
else
    echo "Directory not found for linting" >> "$REPORT_FILE"
fi

echo "Scan completed: $(date)" >> "$REPORT_FILE"