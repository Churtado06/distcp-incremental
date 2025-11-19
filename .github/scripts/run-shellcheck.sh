#!/bin/bash

RESULTS_DIR="quality-results"
REPORT_FILE="$RESULTS_DIR/shellcheck-report.txt"

echo "=== ShellCheck Results ===" > "$REPORT_FILE"
echo "Scan started: $(date)" >> "$REPORT_FILE"

if ls distcp-incremental-tech-talk/*.sh 1> /dev/null 2>&1; then
    shellcheck distcp-incremental-tech-talk/*.sh >> "$REPORT_FILE" 2>&1 || true
else
    echo "No shell scripts found" >> "$REPORT_FILE"
fi

echo "Scan completed: $(date)" >> "$REPORT_FILE"