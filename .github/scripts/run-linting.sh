#!/bin/bash

RESULTS_DIR="quality-results"
REPORT_FILE="$RESULTS_DIR/flake8-report.txt"

echo "=== Flake8 Linting Results ===" | tee "$REPORT_FILE"
echo "Scan started: $(date)" | tee -a "$REPORT_FILE"

if [ -d "distcp-incremental-tech-talk/cloud_function_composer2/" ]; then
    flake8 distcp-incremental-tech-talk/cloud_function_composer2/ --max-line-length=88 --extend-ignore=E203,W503 2>&1 | tee -a "$REPORT_FILE" || true
else
    echo "Directory not found for linting" | tee -a "$REPORT_FILE"
fi

echo "Scan completed: $(date)" | tee -a "$REPORT_FILE"