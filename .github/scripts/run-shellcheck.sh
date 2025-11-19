#!/bin/bash

RESULTS_DIR="quality-results"
REPORT_FILE="$RESULTS_DIR/shellcheck-report.txt"

echo "=== ShellCheck Results ===" | tee "$REPORT_FILE"
echo "Scan started: $(date)" | tee -a "$REPORT_FILE"

if ls distcp-incremental-tech-talk/*.sh 1> /dev/null 2>&1; then
    shellcheck distcp-incremental-tech-talk/*.sh 2>&1 | tee -a "$REPORT_FILE" || true
else
    echo "No shell scripts found" | tee -a "$REPORT_FILE"
fi

echo "Scan completed: $(date)" | tee -a "$REPORT_FILE"