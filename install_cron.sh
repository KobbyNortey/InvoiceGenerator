#!/bin/bash

# Absolute paths (adjust these paths as needed)
PYTHON_PATH="/path/to/your/project/.venv/bin/python"
SCRIPT_PATH="/path/to/your/project/main.py"
LOG_FILE="/path/to/your/project/LOG_FILE.txt"

# Escape spaces for cron
PYTHON_ESCAPED=$(printf '%q' "$PYTHON_PATH")
SCRIPT_ESCAPED=$(printf '%q' "$SCRIPT_PATH")
LOG_ESCAPED=$(printf '%q' "$LOG_FILE")

# Cron job command
CRON_JOB="*/5 * * * * $PYTHON_ESCAPED $SCRIPT_ESCAPED >> $LOG_ESCAPED 2>&1"

# Install the cron job if it's not already present
(crontab -l 2>/dev/null | grep -v -F "$SCRIPT_PATH"; echo "$CRON_JOB") | crontab -

echo "Cron job installed to run main.py every 5 minutes."