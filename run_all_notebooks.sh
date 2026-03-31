#!/bin/bash

# Script to run all Jupyter notebooks in order

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CODE_DIR="$SCRIPT_DIR/code"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_DIR="$SCRIPT_DIR/notebook_runs"
LOG_FILE="$LOG_DIR/run_$TIMESTAMP.log"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

echo "Starting notebook execution at $(date)" | tee "$LOG_FILE"
echo "Log file: $LOG_FILE" | tee -a "$LOG_FILE"
echo "---" | tee -a "$LOG_FILE"

# List of notebooks to run (in order)
NOTEBOOKS=(
    "1 Set up data.ipynb"
    "2 Generate oncogenic-activation signature.ipynb"
    "3 Decompose oncogenic-activation signature and define transcriptional components.ipynb"
    "4 Annotate transcriptional components.ipynb"
    "5 Define cellular states and make Onco-GPS map.ipynb"
    "6 Annotate cellular states.ipynb"
    "7 Display genomic features on Onco-GPS map.ipynb"
    "8 Define global cellular states and make global Onco-GPS map.ipynb"
    "9 Display genomic features on global Onco-GPS map.ipynb"
)

TOTAL=${#NOTEBOOKS[@]}
COMPLETED=0
FAILED=0

# Run each notebook
for notebook in "${NOTEBOOKS[@]}"; do
    COMPLETED=$((COMPLETED + 1))
    NOTEBOOK_PATH="$CODE_DIR/$notebook"
    OUTPUT_FILE="$CODE_DIR/${notebook%.*}_executed_$TIMESTAMP.ipynb"

    if [ ! -f "$NOTEBOOK_PATH" ]; then
        echo "[$COMPLETED/$TOTAL] ERROR: Notebook not found: $NOTEBOOK_PATH" | tee -a "$LOG_FILE"
        FAILED=$((FAILED + 1))
        continue
    fi

    echo "[$COMPLETED/$TOTAL] Running: $notebook" | tee -a "$LOG_FILE"

    if jupyter nbconvert --to notebook --execute --output "$OUTPUT_FILE" "$NOTEBOOK_PATH" >> "$LOG_FILE" 2>&1; then
        echo "  ✓ Completed successfully" | tee -a "$LOG_FILE"
    else
        echo "  ✗ FAILED" | tee -a "$LOG_FILE"
        FAILED=$((FAILED + 1))
    fi
    echo "" | tee -a "$LOG_FILE"
done

# Summary
echo "---" | tee -a "$LOG_FILE"
echo "Execution completed at $(date)" | tee -a "$LOG_FILE"
echo "Summary: $((TOTAL - FAILED))/$TOTAL notebooks completed successfully" | tee -a "$LOG_FILE"

if [ $FAILED -eq 0 ]; then
    echo "All notebooks executed successfully!" | tee -a "$LOG_FILE"
    exit 0
else
    echo "WARNING: $FAILED notebook(s) failed!" | tee -a "$LOG_FILE"
    exit 1
fi
