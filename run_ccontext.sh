#!/bin/bash

# Determine the script's directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Add the script directory to PYTHONPATH
export PYTHONPATH="$SCRIPT_DIR"

# Activate the virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Run the main script with the provided arguments
python3 "$SCRIPT_DIR/ccontext/main.py" "$@"
