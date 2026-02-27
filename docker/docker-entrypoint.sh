#!/bin/bash
set -e

# Activate the virtual environment
source venv_pydiet/bin/activate

# Execute the Docker fun command passed to the container (e.g., "pydiet --host 0.0.0.0")
exec "$@"
