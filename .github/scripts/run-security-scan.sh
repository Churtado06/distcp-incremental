#!/bin/bash

RESULTS_DIR="quality-results"
REPORT_FILE="$RESULTS_DIR/security-report.txt"

echo "=== Bandit Security Scan ===" | tee "$REPORT_FILE"
echo "Scan started: $(date)" | tee -a "$REPORT_FILE"

if [ -d "distcp-incremental-tech-talk/cloud_function_composer2/" ]; then
    bandit -r distcp-incremental-tech-talk/cloud_function_composer2/ -f txt 2>&1 | tee -a "$REPORT_FILE" || true
else
    echo "Directory not found for security scan" | tee -a "$REPORT_FILE"
fi

echo "Scan completed: $(date)" | tee -a "$REPORT_FILE"