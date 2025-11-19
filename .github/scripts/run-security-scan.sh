#!/bin/bash

RESULTS_DIR="quality-results"
REPORT_FILE="$RESULTS_DIR/security-report.txt"

echo "=== Bandit Security Scan ===" > "$REPORT_FILE"
echo "Scan started: $(date)" >> "$REPORT_FILE"

if [ -d "distcp-incremental-tech-talk/cloud_function_composer2/" ]; then
    bandit -r distcp-incremental-tech-talk/cloud_function_composer2/ -f txt >> "$REPORT_FILE" 2>&1 || true
else
    echo "Directory not found for security scan" >> "$REPORT_FILE"
fi

echo "Scan completed: $(date)" >> "$REPORT_FILE"