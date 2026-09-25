#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
source .venv/bin/activate
engiproof doctor
engiproof verify-all
python -m unittest discover -s tests -v
python tools/build_report.py
