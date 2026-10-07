#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/main_backend"
/home/runner/ecommerce/.venv/bin/python manage.py test
