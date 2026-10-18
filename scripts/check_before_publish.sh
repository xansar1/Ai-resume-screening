#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m py_compile app.py resume_explorer/engine.py api/main.py
python3 -m pytest -q
printf 'Syntax and unit/API tests passed.\n'
