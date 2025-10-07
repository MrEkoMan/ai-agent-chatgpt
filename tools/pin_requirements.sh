#!/usr/bin/env bash
set -euo pipefail

# Generate a pinned requirements.lock file.
# Preferred: use pip-tools if installed. Fallback: pip freeze from current environment.
if command -v pip-compile >/dev/null 2>&1; then
  pip-compile --output-file=requirements.lock requirements.txt
else
  echo "pip-compile not found; falling back to pip freeze (ensure your venv has desired versions)"
  pip freeze > requirements.lock
fi
