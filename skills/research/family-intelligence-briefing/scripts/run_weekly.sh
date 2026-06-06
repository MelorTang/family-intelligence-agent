#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${FAMILY_INTELLIGENCE_PROJECT_PATH:-$(pwd)}"
cd "$PROJECT_DIR"

if [ -x ".venv/bin/python" ]; then
  exec .venv/bin/python main.py run-weekly
fi

exec python3 main.py run-weekly
