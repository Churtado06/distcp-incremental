#!/bin/bash

RESULTS_DIR="quality-results"
REPORT_FILE="$RESULTS_DIR/test-report.txt"

echo "=== Unit Test Results ===" > "$REPORT_FILE"
echo "Tests started: $(date)" >> "$REPORT_FILE"

if [ -d "tests" ]; then
    pytest tests/ -v >> "$REPORT_FILE" 2>&1 || true
else
    echo "No tests directory found" >> "$REPORT_FILE"
fi

echo "Tests completed: $(date)" >> "$REPORT_FILE"