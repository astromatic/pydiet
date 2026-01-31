#!/bin/bash
set -e

# Activate the virtual environment
source venv_pydiet/bin/activate

# Execute the main command passed to the container (e.g., "python your_app_script.py")
exec "$@"
