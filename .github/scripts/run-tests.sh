#!/bin/bash

RESULTS_DIR="quality-results"
REPORT_FILE="$RESULTS_DIR/test-report.txt"

echo "=== Unit Test Results ===" | tee "$REPORT_FILE"
echo "Tests started: $(date)" | tee -a "$REPORT_FILE"

if [ -d "tests" ]; then
    pytest tests/ -v 2>&1 | tee -a "$REPORT_FILE" || true
else
    echo "No tests directory found" | tee -a "$REPORT_FILE"
fi

echo "Tests completed: $(date)" | tee -a "$REPORT_FILE"